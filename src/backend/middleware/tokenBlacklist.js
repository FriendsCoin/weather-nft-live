/**
 * Token Blacklist Service using Redis
 * Allows secure logout by blacklisting JWT tokens
 */

const Redis = require('ioredis');
const { logSecurityEvent } = require('./logger');

// Redis client (singleton)
let redisClient = null;

/**
 * Initialize Redis client
 * @param {string} redisUrl - Redis connection URL
 * @returns {Redis} Redis client instance
 */
function initRedis(redisUrl = process.env.REDIS_URL) {
  if (redisClient) {
    return redisClient;
  }

  try {
    // If Redis URL not provided, use in-memory fallback (development only)
    if (!redisUrl) {
      console.warn('⚠️  WARNING: No REDIS_URL provided. Token blacklist disabled.');
      console.warn('   Tokens will remain valid even after logout (development only!)');
      return null;
    }

    redisClient = new Redis(redisUrl, {
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: 3,
      enableOfflineQueue: false,
      lazyConnect: true
    });

    redisClient.on('connect', () => {
      console.log('✅ Redis connected for token blacklist');
    });

    redisClient.on('error', (err) => {
      console.error('❌ Redis connection error:', err.message);
      logSecurityEvent('redis_connection_error', { error: err.message });
    });

    redisClient.on('close', () => {
      console.warn('⚠️  Redis connection closed');
    });

    // Connect to Redis
    redisClient.connect().catch((err) => {
      console.error('❌ Failed to connect to Redis:', err.message);
      redisClient = null;
    });

    return redisClient;
  } catch (error) {
    console.error('❌ Redis initialization failed:', error.message);
    logSecurityEvent('redis_init_error', { error: error.message });
    return null;
  }
}

/**
 * Add token to blacklist
 * @param {string} token - JWT token to blacklist
 * @param {number} expiresIn - Token expiration time in seconds
 * @returns {Promise<boolean>} True if successfully blacklisted
 */
async function blacklistToken(token, expiresIn = 86400) {
  if (!redisClient) {
    console.warn('⚠️  Redis not available. Token blacklist skipped.');
    return false;
  }

  try {
    // Store token with expiration matching JWT expiration
    // Key format: "blacklist:token:<token>"
    const key = `blacklist:token:${token}`;
    await redisClient.setex(key, expiresIn, '1');

    logSecurityEvent('token_blacklisted', {
      tokenPrefix: token.substring(0, 20) + '...',
      expiresIn
    });

    return true;
  } catch (error) {
    console.error('❌ Failed to blacklist token:', error.message);
    logSecurityEvent('token_blacklist_error', { error: error.message });
    return false;
  }
}

/**
 * Check if token is blacklisted
 * @param {string} token - JWT token to check
 * @returns {Promise<boolean>} True if token is blacklisted
 */
async function isTokenBlacklisted(token) {
  if (!redisClient) {
    // If Redis is not available, assume token is not blacklisted
    // This maintains functionality in development without Redis
    return false;
  }

  try {
    const key = `blacklist:token:${token}`;
    const result = await redisClient.get(key);
    return result === '1';
  } catch (error) {
    console.error('❌ Failed to check token blacklist:', error.message);
    logSecurityEvent('token_blacklist_check_error', { error: error.message });
    // Fail open - allow request to proceed if Redis is down
    return false;
  }
}

/**
 * Blacklist all tokens for a specific user (logout from all devices)
 * @param {string} userId - User ID
 * @param {number} expiresIn - Expiration time in seconds
 * @returns {Promise<boolean>} True if successfully blacklisted
 */
async function blacklistAllUserTokens(userId, expiresIn = 86400) {
  if (!redisClient) {
    console.warn('⚠️  Redis not available. User token blacklist skipped.');
    return false;
  }

  try {
    // Store user ID with timestamp
    const key = `blacklist:user:${userId}`;
    const timestamp = Date.now();
    await redisClient.setex(key, expiresIn, timestamp.toString());

    logSecurityEvent('user_tokens_blacklisted', { userId, expiresIn });

    return true;
  } catch (error) {
    console.error('❌ Failed to blacklist user tokens:', error.message);
    logSecurityEvent('user_token_blacklist_error', {
      userId,
      error: error.message
    });
    return false;
  }
}

/**
 * Check if user has been logged out from all devices
 * @param {string} userId - User ID
 * @param {number} tokenIssuedAt - Token issued timestamp (iat claim)
 * @returns {Promise<boolean>} True if all user tokens are blacklisted
 */
async function areAllUserTokensBlacklisted(userId, tokenIssuedAt) {
  if (!redisClient) {
    return false;
  }

  try {
    const key = `blacklist:user:${userId}`;
    const blacklistTimestamp = await redisClient.get(key);

    if (!blacklistTimestamp) {
      return false;
    }

    // If token was issued before the blacklist timestamp, it's invalid
    const tokenTime = tokenIssuedAt * 1000; // Convert to milliseconds
    const blacklistTime = parseInt(blacklistTimestamp, 10);

    return tokenTime < blacklistTime;
  } catch (error) {
    console.error('❌ Failed to check user token blacklist:', error.message);
    return false;
  }
}

/**
 * Middleware to check if token is blacklisted
 * Must be used AFTER authenticateToken middleware
 */
async function checkTokenBlacklist(req, res, next) {
  try {
    // Extract token from header
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return next(); // No token, let authenticateToken handle it
    }

    // Check if specific token is blacklisted
    const isBlacklisted = await isTokenBlacklisted(token);
    if (isBlacklisted) {
      logSecurityEvent('blacklisted_token_used', {
        userId: req.user?.userId,
        tokenPrefix: token.substring(0, 20) + '...'
      });

      return res.status(401).json({
        success: false,
        error: 'Token has been revoked. Please login again.',
        code: 'TOKEN_REVOKED'
      });
    }

    // Check if all user tokens are blacklisted (logout from all devices)
    if (req.user && req.user.userId && req.user.iat) {
      const allBlacklisted = await areAllUserTokensBlacklisted(
        req.user.userId,
        req.user.iat
      );

      if (allBlacklisted) {
        logSecurityEvent('revoked_user_session_used', {
          userId: req.user.userId
        });

        return res.status(401).json({
          success: false,
          error: 'Session has been revoked. Please login again.',
          code: 'SESSION_REVOKED'
        });
      }
    }

    next();
  } catch (error) {
    console.error('❌ Token blacklist check failed:', error);
    // Fail open - allow request to proceed if check fails
    next();
  }
}

/**
 * Clean up Redis connection
 */
async function disconnectRedis() {
  if (redisClient) {
    await redisClient.quit();
    redisClient = null;
    console.log('✅ Redis disconnected');
  }
}

/**
 * Get Redis connection status
 */
function getRedisStatus() {
  if (!redisClient) {
    return { connected: false, message: 'Redis not initialized' };
  }

  return {
    connected: redisClient.status === 'ready',
    status: redisClient.status,
    message: redisClient.status === 'ready' ? 'Connected' : `Status: ${redisClient.status}`
  };
}

module.exports = {
  initRedis,
  blacklistToken,
  isTokenBlacklisted,
  blacklistAllUserTokens,
  areAllUserTokensBlacklisted,
  checkTokenBlacklist,
  disconnectRedis,
  getRedisStatus
};
