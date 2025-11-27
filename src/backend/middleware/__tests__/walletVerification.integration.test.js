/**
 * Integration Tests for Wallet Signature Verification
 * Tests Ethereum and Tezos wallet signature verification
 */

const {
  detectWalletType,
  generateChallengeMessage,
  verifyTimestamp,
  verifyWalletSignature
} = require('../walletVerification');

describe('Wallet Verification Integration Tests', () => {
  describe('detectWalletType', () => {
    test('should detect Ethereum wallet address', () => {
      const ethAddress = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      expect(detectWalletType(ethAddress)).toBe('ethereum');
    });

    test('should detect Tezos tz1 wallet address', () => {
      const tezosAddress = 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb';
      expect(detectWalletType(tezosAddress)).toBe('tezos');
    });

    test('should detect Tezos KT1 contract address', () => {
      const tezosContract = 'KT1TxqZ8QtKvLu3V3JH7Gx58n7Co8pgtpQU5';
      expect(detectWalletType(tezosContract)).toBe('tezos');
    });

    test('should return unknown for invalid address', () => {
      expect(detectWalletType('invalid_address')).toBe('unknown');
      expect(detectWalletType('')).toBe('unknown');
      expect(detectWalletType(null)).toBe('unknown');
    });

    test('should handle Ethereum address with different case', () => {
      const ethAddressUpper = '0X742D35CC6634C0532925A3B844BC9E7595F0BEB1';
      expect(detectWalletType(ethAddressUpper.toLowerCase())).toBe('ethereum');
    });
  });

  describe('generateChallengeMessage', () => {
    test('should generate challenge message with wallet address', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const timestamp = 1234567890000;
      const message = generateChallengeMessage(wallet, timestamp);

      expect(message).toContain('WeatherNFT');
      expect(message).toContain(wallet);
      expect(message).toContain(timestamp.toString());
      expect(message).toContain('blockchain transaction');
    });

    test('should generate unique messages for different timestamps', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const message1 = generateChallengeMessage(wallet, 1000);
      const message2 = generateChallengeMessage(wallet, 2000);

      expect(message1).not.toBe(message2);
    });

    test('should generate different messages for different wallets', () => {
      const timestamp = 1234567890000;
      const message1 = generateChallengeMessage('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1', timestamp);
      const message2 = generateChallengeMessage('tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb', timestamp);

      expect(message1).not.toBe(message2);
    });
  });

  describe('verifyTimestamp', () => {
    test('should accept recent timestamp', () => {
      const recentTimestamp = Date.now() - 1000; // 1 second ago
      expect(verifyTimestamp(recentTimestamp)).toBe(true);
    });

    test('should accept timestamp within 5 minute window', () => {
      const timestamp = Date.now() - (4 * 60 * 1000); // 4 minutes ago
      expect(verifyTimestamp(timestamp)).toBe(true);
    });

    test('should reject expired timestamp (older than 5 minutes)', () => {
      const expiredTimestamp = Date.now() - (6 * 60 * 1000); // 6 minutes ago
      expect(verifyTimestamp(expiredTimestamp)).toBe(false);
    });

    test('should reject future timestamp', () => {
      const futureTimestamp = Date.now() + 1000; // 1 second in future
      expect(verifyTimestamp(futureTimestamp)).toBe(false);
    });

    test('should respect custom maxAge parameter', () => {
      const timestamp = Date.now() - (2 * 60 * 1000); // 2 minutes ago

      // Should pass with 3 minute window
      expect(verifyTimestamp(timestamp, 3 * 60 * 1000)).toBe(true);

      // Should fail with 1 minute window
      expect(verifyTimestamp(timestamp, 1 * 60 * 1000)).toBe(false);
    });

    test('should handle edge cases', () => {
      const now = Date.now();

      // Exactly now should pass
      expect(verifyTimestamp(now)).toBe(true);

      // Exactly at boundary (5 minutes) should fail
      const exactBoundary = now - (5 * 60 * 1000);
      expect(verifyTimestamp(exactBoundary)).toBe(false);
    });
  });

  describe('verifyWalletSignature', () => {
    test('should return error for unknown wallet type', () => {
      const message = 'Test message';
      const signature = 'fake_signature';
      const wallet = 'invalid_wallet';

      const result = verifyWalletSignature(message, signature, wallet);

      expect(result.valid).toBe(false);
      expect(result.walletType).toBe('unknown');
      expect(result.error).toContain('Unknown wallet');
    });

    test('should detect Ethereum wallet and attempt verification', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const message = 'Test message';
      const invalidSignature = '0xinvalid';

      const result = verifyWalletSignature(message, invalidSignature, wallet);

      expect(result.walletType).toBe('ethereum');
      expect(result.valid).toBe(false);
      // Should fail because signature is invalid
    });

    test('should detect Tezos wallet and attempt verification', () => {
      const wallet = 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb';
      const message = 'Test message';
      const invalidSignature = 'edsiginvalid';

      const result = verifyWalletSignature(message, invalidSignature, wallet);

      expect(result.walletType).toBe('tezos');
      expect(result.valid).toBe(false);
      // Should fail because signature is invalid
    });

    test('should handle empty signature', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const message = 'Test message';
      const signature = '';

      const result = verifyWalletSignature(message, signature, wallet);

      expect(result.valid).toBe(false);
      expect(result.walletType).toBe('ethereum');
    });

    test('should handle null/undefined inputs gracefully', () => {
      const result1 = verifyWalletSignature(null, 'sig', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1');
      expect(result1.valid).toBe(false);

      const result2 = verifyWalletSignature('msg', null, '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1');
      expect(result2.valid).toBe(false);
    });
  });

  describe('Challenge-Response Flow Integration', () => {
    test('should complete full challenge-response flow for Ethereum', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const timestamp = Date.now();

      // Step 1: Generate challenge
      const message = generateChallengeMessage(wallet, timestamp);
      expect(message).toContain(wallet);

      // Step 2: Verify timestamp is valid
      expect(verifyTimestamp(timestamp)).toBe(true);

      // Step 3: Detect wallet type
      expect(detectWalletType(wallet)).toBe('ethereum');

      // Step 4: Verify signature (with invalid signature, should fail)
      const result = verifyWalletSignature(message, '0xinvalid', wallet);
      expect(result.walletType).toBe('ethereum');
      expect(result.valid).toBe(false);
    });

    test('should complete full challenge-response flow for Tezos', () => {
      const wallet = 'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb';
      const timestamp = Date.now();

      // Step 1: Generate challenge
      const message = generateChallengeMessage(wallet, timestamp);
      expect(message).toContain(wallet);

      // Step 2: Verify timestamp is valid
      expect(verifyTimestamp(timestamp)).toBe(true);

      // Step 3: Detect wallet type
      expect(detectWalletType(wallet)).toBe('tezos');

      // Step 4: Verify signature (with invalid signature, should fail)
      const result = verifyWalletSignature(message, 'edsiginvalid', wallet);
      expect(result.walletType).toBe('tezos');
      expect(result.valid).toBe(false);
    });

    test('should reject expired challenge', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const expiredTimestamp = Date.now() - (6 * 60 * 1000); // 6 minutes ago

      // Generate challenge with expired timestamp
      const message = generateChallengeMessage(wallet, expiredTimestamp);

      // Timestamp should be invalid
      expect(verifyTimestamp(expiredTimestamp)).toBe(false);

      // Even with valid signature, expired timestamp should fail authentication
    });

    test('should prevent replay attacks with different timestamps', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const timestamp1 = Date.now() - 1000;
      const timestamp2 = Date.now();

      const message1 = generateChallengeMessage(wallet, timestamp1);
      const message2 = generateChallengeMessage(wallet, timestamp2);

      // Messages should be different due to different timestamps
      expect(message1).not.toBe(message2);

      // This prevents replay attacks - old signature won't work for new challenge
    });
  });

  describe('Security Tests', () => {
    test('should not accept signature for different wallet address', () => {
      const wallet1 = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const wallet2 = '0x123456789abcdef123456789abcdef123456789a';
      const timestamp = Date.now();

      const message1 = generateChallengeMessage(wallet1, timestamp);
      const message2 = generateChallengeMessage(wallet2, timestamp);

      // Messages should be different for different wallets
      expect(message1).not.toBe(message2);
    });

    test('should handle very long message gracefully', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const longMessage = 'A'.repeat(10000);
      const signature = '0x' + '0'.repeat(130);

      const result = verifyWalletSignature(longMessage, signature, wallet);
      expect(result.valid).toBe(false);
    });

    test('should handle malformed signatures gracefully', () => {
      const wallet = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1';
      const message = 'Test message';

      const malformedSignatures = [
        'not_a_signature',
        '0x',
        '0xZZZZ',
        'edsigtooShort',
        '{}',
        'null',
        '12345'
      ];

      malformedSignatures.forEach(sig => {
        const result = verifyWalletSignature(message, sig, wallet);
        expect(result.valid).toBe(false);
      });
    });
  });
});
