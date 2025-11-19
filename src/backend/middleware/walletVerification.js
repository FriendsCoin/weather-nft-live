/**
 * Wallet Signature Verification
 * Supports both Tezos and Ethereum wallet signatures
 */

const { ethers } = require('ethers');
const { verifySignature: verifyTezosSignature } = require('@taquito/utils');
const { logSecurityEvent } = require('./logger');

/**
 * Verify Ethereum wallet signature
 * @param {string} message - Original message that was signed
 * @param {string} signature - Signature from wallet
 * @param {string} walletAddress - Expected wallet address
 * @returns {boolean} - True if signature is valid
 */
function verifyEthereumSignature(message, signature, walletAddress) {
  try {
    // Recover the address from the signature
    const recoveredAddress = ethers.verifyMessage(message, signature);

    // Compare recovered address with expected address (case-insensitive)
    const isValid = recoveredAddress.toLowerCase() === walletAddress.toLowerCase();

    if (!isValid) {
      logSecurityEvent('ethereum_signature_mismatch', {
        expected: walletAddress,
        recovered: recoveredAddress
      });
    }

    return isValid;
  } catch (error) {
    logSecurityEvent('ethereum_signature_error', {
      walletAddress,
      error: error.message
    });
    return false;
  }
}

/**
 * Verify Tezos wallet signature
 * @param {string} message - Original message that was signed
 * @param {string} signature - Signature from wallet
 * @param {string} walletAddress - Expected wallet address (tz1...)
 * @returns {boolean} - True if signature is valid
 */
function verifyTezosSignatureWrapper(message, signature, walletAddress) {
  try {
    // Convert message to hex format for Tezos
    const messageBytes = Buffer.from(message, 'utf8').toString('hex');

    // Verify signature using @taquito/utils
    const isValid = verifyTezosSignature(
      messageBytes,
      walletAddress,
      signature
    );

    if (!isValid) {
      logSecurityEvent('tezos_signature_mismatch', {
        walletAddress
      });
    }

    return isValid;
  } catch (error) {
    logSecurityEvent('tezos_signature_error', {
      walletAddress,
      error: error.message
    });
    return false;
  }
}

/**
 * Detect wallet type from address
 * @param {string} walletAddress - Wallet address
 * @returns {string} - 'ethereum', 'tezos', or 'unknown'
 */
function detectWalletType(walletAddress) {
  if (!walletAddress) return 'unknown';

  // Ethereum: starts with 0x, 42 characters (0x + 40 hex chars)
  if (walletAddress.startsWith('0x') && walletAddress.length === 42) {
    return 'ethereum';
  }

  // Tezos: starts with tz1, tz2, tz3, or KT1
  if (/^(tz1|tz2|tz3|KT1)[a-zA-Z0-9]{33}$/.test(walletAddress)) {
    return 'tezos';
  }

  return 'unknown';
}

/**
 * Verify wallet signature (auto-detects Ethereum or Tezos)
 * @param {string} message - Original message that was signed
 * @param {string} signature - Signature from wallet
 * @param {string} walletAddress - Wallet address
 * @returns {Object} - { valid: boolean, walletType: string, error?: string }
 */
function verifyWalletSignature(message, signature, walletAddress) {
  const walletType = detectWalletType(walletAddress);

  if (walletType === 'unknown') {
    logSecurityEvent('unknown_wallet_type', { walletAddress });
    return {
      valid: false,
      walletType: 'unknown',
      error: 'Unknown wallet address format'
    };
  }

  try {
    let isValid = false;

    if (walletType === 'ethereum') {
      isValid = verifyEthereumSignature(message, signature, walletAddress);
    } else if (walletType === 'tezos') {
      isValid = verifyTezosSignatureWrapper(message, signature, walletAddress);
    }

    if (isValid) {
      logSecurityEvent('wallet_signature_verified', {
        walletType,
        walletAddress
      });
    } else {
      logSecurityEvent('wallet_signature_failed', {
        walletType,
        walletAddress
      });
    }

    return {
      valid: isValid,
      walletType
    };
  } catch (error) {
    logSecurityEvent('wallet_verification_error', {
      walletType,
      walletAddress,
      error: error.message
    });

    return {
      valid: false,
      walletType,
      error: error.message
    };
  }
}

/**
 * Generate a challenge message for wallet signing
 * @param {string} walletAddress - Wallet address
 * @param {number} timestamp - Unix timestamp (milliseconds)
 * @returns {string} - Challenge message to sign
 */
function generateChallengeMessage(walletAddress, timestamp) {
  return `Sign this message to authenticate with WeatherNFT\n\nWallet: ${walletAddress}\nTimestamp: ${timestamp}\n\nThis request will not trigger a blockchain transaction or cost any gas fees.`;
}

/**
 * Verify challenge message timestamp (prevent replay attacks)
 * @param {number} timestamp - Timestamp from the challenge
 * @param {number} maxAgeMs - Maximum age in milliseconds (default: 5 minutes)
 * @returns {boolean} - True if timestamp is recent enough
 */
function verifyTimestamp(timestamp, maxAgeMs = 5 * 60 * 1000) {
  const now = Date.now();
  const age = now - timestamp;

  // Timestamp must be in the past but not too old
  if (age < 0) {
    logSecurityEvent('future_timestamp', { timestamp, now });
    return false;
  }

  if (age > maxAgeMs) {
    logSecurityEvent('expired_timestamp', {
      timestamp,
      now,
      ageMinutes: Math.floor(age / 60000)
    });
    return false;
  }

  return true;
}

/**
 * Express middleware for wallet signature verification
 * Requires: req.body.signature, req.body.timestamp, req.body.walletAddress
 */
function requireWalletSignature(req, res, next) {
  const { walletAddress, signature, timestamp } = req.body;

  if (!walletAddress || !signature || !timestamp) {
    logSecurityEvent('missing_signature_data', {
      hasWallet: !!walletAddress,
      hasSignature: !!signature,
      hasTimestamp: !!timestamp
    });

    return res.status(400).json({
      success: false,
      error: 'Missing required fields: walletAddress, signature, timestamp'
    });
  }

  // Verify timestamp (prevent replay attacks)
  if (!verifyTimestamp(timestamp)) {
    return res.status(401).json({
      success: false,
      error: 'Challenge expired or invalid timestamp. Please request a new challenge.'
    });
  }

  // Generate the expected message
  const message = generateChallengeMessage(walletAddress, timestamp);

  // Verify signature
  const result = verifyWalletSignature(message, signature, walletAddress);

  if (!result.valid) {
    return res.status(401).json({
      success: false,
      error: 'Invalid wallet signature',
      details: result.error
    });
  }

  // Attach wallet info to request
  req.verifiedWallet = {
    address: walletAddress,
    type: result.walletType
  };

  next();
}

module.exports = {
  verifyEthereumSignature,
  verifyTezosSignatureWrapper,
  detectWalletType,
  verifyWalletSignature,
  generateChallengeMessage,
  verifyTimestamp,
  requireWalletSignature
};
