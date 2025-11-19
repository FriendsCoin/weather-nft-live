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

const app = express();
const PORT = process.env.AUTH_SERVICE_PORT || 3014;

app.use(cors());
app.use(express.json());

// Initialize database
const db = new DatabaseService();

/**
 * Health check
 */
app.get('/health', async (req, res) => {
  try {
    const isDbConnected = await db.healthCheck();
    const userCount = await User.countDocuments();

    res.json({
      status: 'OK',
      service: 'WeatherNFT Authentication Service',
      database: isDbConnected ? 'connected' : 'disconnected',
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
 */
app.post('/api/auth/register', async (req, res) => {
  try {
    const { walletAddress, username, email, password } = req.body;

    // Validate required fields
    if (!walletAddress) {
      return res.status(400).json({
        success: false,
        error: 'Wallet address is required'
      });
    }

    // Check if user already exists
    const existingUser = await User.findOne({ address: walletAddress });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        error: 'User with this wallet address already exists'
      });
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
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Login with wallet address (signature verification)
 * POST /api/auth/login
 */
app.post('/api/auth/login', async (req, res) => {
  try {
    const { walletAddress, password, signature } = req.body;

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
        return res.status(401).json({
          success: false,
          error: 'Invalid password'
        });
      }
    }

    // TODO: Verify wallet signature in production
    // For now, we trust the wallet address

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
app.get('/api/auth/me', authenticateToken, async (req, res) => {
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
app.post('/api/auth/verify', authenticateToken, (req, res) => {
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
app.post('/api/auth/refresh', authenticateToken, async (req, res) => {
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

    // Start Express server
    app.listen(PORT, () => {
      console.log(`✅ Server running on http://localhost:${PORT}`);
      console.log('');
      console.log('📊 Endpoints:');
      console.log('   • GET  /health              - Health check');
      console.log('   • POST /api/auth/register   - Register new user');
      console.log('   • POST /api/auth/login      - Login user');
      console.log('   • GET  /api/auth/me         - Get current user (protected)');
      console.log('   • POST /api/auth/verify     - Verify token (protected)');
      console.log('   • POST /api/auth/refresh    - Refresh token (protected)');
      console.log('');
      console.log('✅ Ready to authenticate users!');
      console.log('📦 MongoDB collection ready: User');
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
