#!/usr/bin/env node

/**
 * Authentication Service for WeatherNFT
 * Handles user registration, login, and token management
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const DatabaseService = require('./database');
const { User } = require('./models');
const { generateToken, authenticateToken } = require('./middleware/auth');
const {
  securityHeaders,
  generalLimiter,
  authLimiter,
  corsOptions
} = require('./middleware/security');
const { requestLogger, errorLogger, logAuthEvent } = require('./middleware/logger');
const {
  generateChallengeMessage,
  verifyWalletSignature,
  verifyTimestamp
} = require('./middleware/walletVerification');
const {
  validateRegistration,
  validateLogin,
  sanitizeInput
} = require('./middleware/validation');
const {
  initRedis,
  blacklistToken,
  blacklistAllUserTokens,
  checkTokenBlacklist,
  getRedisStatus,
  disconnectRedis
} = require('./middleware/tokenBlacklist');

const app = express();
const PORT = process.env.AUTH_SERVICE_PORT || 3014;

// Security middleware
app.use(securityHeaders());
app.use(cors(corsOptions()));
app.use(express.json());
app.use(sanitizeInput); // Sanitize input to prevent XSS
app.use(requestLogger); // Log all requests
app.use(generalLimiter); // Rate limit all routes

// Initialize database
const db = new DatabaseService();

/**
 * Get challenge message for wallet signing
 * GET /api/auth/challenge/:walletAddress
 * Returns a message to sign for authentication
 */
app.get('/api/auth/challenge/:walletAddress', (req, res) => {
  const { walletAddress } = req.params;
  const timestamp = Date.now();

  if (!walletAddress) {
    return res.status(400).json({
      success: false,
      error: 'Wallet address is required'
    });
  }

  const message = generateChallengeMessage(walletAddress, timestamp);

  res.json({
    success: true,
    message,
    timestamp,
    expiresIn: '5 minutes',
    instructions: 'Sign this message with your wallet to authenticate'
  });
});

/**
 * Health check
 */
app.get('/health', async (req, res) => {
  try {
    const isDbConnected = await db.healthCheck();
    const userCount = await User.countDocuments();
    const redisStatus = getRedisStatus();

    res.json({
      status: 'OK',
      service: 'WeatherNFT Authentication Service',
      database: isDbConnected ? 'connected' : 'disconnected',
      redis: redisStatus.connected ? 'connected' : 'disconnected',
      features: {
        token_blacklist: redisStatus.connected ? 'enabled' : 'disabled'
      },
      stats: {
        total_users: userCount
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      status: 'ERROR',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Register new user with wallet address
 * POST /api/auth/register
 * Rate limited: 5 attempts per 15 minutes
 */
app.post('/api/auth/register', authLimiter, validateRegistration, async (req, res) => {
  try {
    const { walletAddress, username, email, password } = req.body;

    // Validate required fields
    if (!walletAddress) {
      return res.status(400).json({
        success: false,
        error: 'Wallet address is required'
      });
    }

    // Check if user already exists by wallet address
    const existingUser = await User.findOne({ address: walletAddress });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        error: 'User with this wallet address already exists'
      });
    }

    // Check if username is already taken (if provided)
    if (username) {
      const existingUsername = await User.findOne({ username: username });
      if (existingUsername) {
        return res.status(400).json({
          success: false,
          error: 'Username is already taken'
        });
      }
    }

    // Check if email is already registered (if provided)
    if (email) {
      const existingEmail = await User.findOne({ email: email });
      if (existingEmail) {
        return res.status(400).json({
          success: false,
          error: 'Email is already registered'
        });
      }
    }

    // Hash password if provided (optional for wallet-only auth)
    let hashedPassword = null;
    if (password) {
      const salt = await bcrypt.genSalt(10);
      hashedPassword = await bcrypt.hash(password, salt);
    }

    // Create user
    const userData = {
      address: walletAddress,
      username: username || null,
      email: email || null,
      password: hashedPassword,
      totalCaptures: 0,
      totalEarned: 0,
      stats: {
        nftsCreated: 0,
        nftsSold: 0,
        guildsJoined: 0,
        guildsFounded: 0
      }
    };

    const user = await User.create(userData);

    // Generate JWT token
    const token = generateToken({
      userId: user._id,
      walletAddress: user.address,
      role: 'user'
    });

    console.log(`✅ User registered: ${walletAddress}`);
    logAuthEvent('register', walletAddress, true, { username });

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      token: token,
      user: {
        id: user._id,
        walletAddress: user.address,
        username: user.username
      }
    });

  } catch (error) {
    console.error('❌ Registration failed:', error);
    logAuthEvent('register', req.body.walletAddress, false, { error: error.message });
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Login with wallet address (signature verification)
 * POST /api/auth/login
 * Rate limited: 5 attempts per 15 minutes
 */
app.post('/api/auth/login', authLimiter, validateLogin, async (req, res) => {
  try {
    const { walletAddress, password, signature, timestamp } = req.body;

    if (!walletAddress) {
      return res.status(400).json({
        success: false,
        error: 'Wallet address is required'
      });
    }

    // Find user
    const user = await User.findOne({ address: walletAddress });
    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found. Please register first.'
      });
    }

    // Verify password if provided
    if (password && user.password) {
      const validPassword = await bcrypt.compare(password, user.password);
      if (!validPassword) {
        logAuthEvent('login', walletAddress, false, { reason: 'invalid_password' });
        return res.status(401).json({
          success: false,
          error: 'Invalid password'
        });
      }
    }

    // Verify wallet signature if provided (recommended for production)
    if (signature && timestamp) {
      // Verify timestamp first (prevent replay attacks)
      if (!verifyTimestamp(timestamp)) {
        logAuthEvent('login', walletAddress, false, { reason: 'expired_timestamp' });
        return res.status(401).json({
          success: false,
          error: 'Challenge expired. Please request a new challenge.'
        });
      }

      // Generate expected message
      const message = generateChallengeMessage(walletAddress, timestamp);

      // Verify signature
      const verification = verifyWalletSignature(message, signature, walletAddress);

      if (!verification.valid) {
        logAuthEvent('login', walletAddress, false, {
          reason: 'invalid_signature',
          walletType: verification.walletType,
          error: verification.error
        });
        return res.status(401).json({
          success: false,
          error: 'Invalid wallet signature',
          details: verification.error
        });
      }

      // Signature verified successfully
      logAuthEvent('login', walletAddress, true, {
        method: 'wallet_signature',
        walletType: verification.walletType
      });
    } else if (!password) {
      // No password and no signature - not secure!
      logAuthEvent('login', walletAddress, false, { reason: 'no_authentication' });
      return res.status(400).json({
        success: false,
        error: 'Please provide either password or wallet signature for authentication'
      });
    }

    // Update last active
    user.lastActive = new Date();
    await user.save();

    // Generate JWT token
    const token = generateToken({
      userId: user._id,
      walletAddress: user.address,
      username: user.username,
      role: 'user'
    });

    console.log(`✅ User logged in: ${walletAddress}`);
    logAuthEvent('login', walletAddress, true, {
      username: user.username,
      method: password ? 'password' : 'wallet'
    });

    res.json({
      success: true,
      message: 'Login successful',
      token: token,
      user: {
        id: user._id,
        walletAddress: user.address,
        username: user.username,
        totalCaptures: user.totalCaptures,
        totalEarned: user.totalEarned
      }
    });

  } catch (error) {
    console.error('❌ Login failed:', error);
    logAuthEvent('login', req.body.walletAddress, false, { error: error.message });
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get current user profile (protected route)
 * GET /api/auth/me
 */
app.get('/api/auth/me', authenticateToken, checkTokenBlacklist, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId).select('-password');

    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    res.json({
      success: true,
      user: user
    });

  } catch (error) {
    console.error('❌ Get profile failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Verify token validity
 * POST /api/auth/verify
 */
app.post('/api/auth/verify', authenticateToken, checkTokenBlacklist, (req, res) => {
  res.json({
    success: true,
    valid: true,
    user: req.user
  });
});

/**
 * Refresh token
 * POST /api/auth/refresh
 */
app.post('/api/auth/refresh', authenticateToken, checkTokenBlacklist, async (req, res) => {
  try {
    // Generate new token with same payload
    const newToken = generateToken({
      userId: req.user.userId,
      walletAddress: req.user.walletAddress,
      username: req.user.username,
      role: req.user.role
    });

    res.json({
      success: true,
      token: newToken
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Logout (blacklist current token)
 * POST /api/auth/logout
 */
app.post('/api/auth/logout', authenticateToken, async (req, res) => {
  try {
    // Extract token from header
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      // Blacklist token for 24 hours (default JWT expiration)
      const success = await blacklistToken(token, 86400);

      if (success) {
        logAuthEvent('logout', req.user.walletAddress, true, {
          userId: req.user.userId
        });

        res.json({
          success: true,
          message: 'Logged out successfully'
        });
      } else {
        // Redis not available, but we still log out client-side
        logAuthEvent('logout', req.user.walletAddress, true, {
          userId: req.user.userId,
          warning: 'Token blacklist unavailable'
        });

        res.json({
          success: true,
          message: 'Logged out successfully (client-side only)',
          warning: 'Token revocation unavailable. Token will remain valid until expiration.'
        });
      }
    } else {
      res.status(400).json({
        success: false,
        error: 'No token provided'
      });
    }
  } catch (error) {
    console.error('❌ Logout failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Logout from all devices (blacklist all user tokens)
 * POST /api/auth/logout-all
 */
app.post('/api/auth/logout-all', authenticateToken, async (req, res) => {
  try {
    const success = await blacklistAllUserTokens(req.user.userId, 86400);

    if (success) {
      logAuthEvent('logout_all_devices', req.user.walletAddress, true, {
        userId: req.user.userId
      });

      res.json({
        success: true,
        message: 'Logged out from all devices successfully'
      });
    } else {
      logAuthEvent('logout_all_devices', req.user.walletAddress, false, {
        userId: req.user.userId,
        error: 'Redis unavailable'
      });

      res.json({
        success: false,
        error: 'Token revocation unavailable. Please try again later.',
        warning: 'Ensure Redis is running for logout functionality.'
      });
    }
  } catch (error) {
    console.error('❌ Logout all failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error logger middleware (must be after routes)
app.use(errorLogger);

// Start server with database connection
async function startServer() {
  try {
    console.log('');
    console.log('🔐 WeatherNFT Authentication Service');
    console.log('='.repeat(50));

    // Connect to MongoDB
    console.log('📊 Connecting to MongoDB...');
    await db.connect();
    console.log('✅ MongoDB connected');

    // Initialize indexes
    console.log('📝 Initializing database indexes...');
    await User.createIndexes();
    console.log('✅ Database indexes initialized');

    // Initialize Redis for token blacklist (optional)
    console.log('🔴 Initializing Redis for token blacklist...');
    const redis = initRedis();
    if (redis) {
      console.log('✅ Redis initialized (token blacklist enabled)');
    } else {
      console.warn('⚠️  Redis not available (token blacklist disabled)');
    }

    // Start Express server
    app.listen(PORT, () => {
      console.log(`✅ Server running on http://localhost:${PORT}`);
      console.log('');
      console.log('📊 Endpoints:');
      console.log('   • GET  /health                          - Health check');
      console.log('   • GET  /api/auth/challenge/:wallet      - Get challenge for wallet signing');
      console.log('   • POST /api/auth/register               - Register new user');
      console.log('   • POST /api/auth/login                  - Login (password or wallet signature)');
      console.log('   • GET  /api/auth/me                     - Get current user (protected)');
      console.log('   • POST /api/auth/verify                 - Verify token (protected)');
      console.log('   • POST /api/auth/refresh                - Refresh token (protected)');
      console.log('   • POST /api/auth/logout                 - Logout (revoke token)');
      console.log('   • POST /api/auth/logout-all             - Logout from all devices');
      console.log('');
      console.log('✅ Ready to authenticate users!');
      console.log('📦 MongoDB collection ready: User');
      console.log('🔐 Wallet signature verification: Tezos & Ethereum supported');
      console.log('');
    });

  } catch (error) {
    console.error('❌ Failed to start auth service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⚠️  Shutting down auth service...');
  try {
    await disconnectRedis();
    await db.disconnect();
    console.log('✅ Database connection closed');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
});

process.on('SIGTERM', async () => {
  console.log('\n⚠️  Received SIGTERM signal...');
  try {
    await disconnectRedis();
    await db.disconnect();
    console.log('✅ Database connection closed');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
});

// Start the server
startServer();

module.exports = app;
