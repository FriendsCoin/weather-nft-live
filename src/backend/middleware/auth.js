/**
 * JWT Authentication Middleware
 * Validates JWT tokens for protected routes
 */

const jwt = require('jsonwebtoken');

// JWT Secret from environment (REQUIRED)
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRATION = process.env.JWT_EXPIRATION || '24h';

// Validate JWT_SECRET exists
if (!JWT_SECRET) {
  console.error('🔴 FATAL: JWT_SECRET environment variable is required!');
  console.error('   Set JWT_SECRET in .env file before starting the server.');
  console.error('   Example: JWT_SECRET=your-super-secret-key-here');

  if (process.env.NODE_ENV === 'production') {
    throw new Error('JWT_SECRET is required in production');
  } else {
    console.warn('⚠️  WARNING: Using temporary JWT_SECRET for development');
    console.warn('   This is INSECURE and should NEVER be used in production!');
  }
}

// Warn if using weak secret
if (JWT_SECRET && JWT_SECRET.length < 32) {
  console.warn('⚠️  WARNING: JWT_SECRET is too short (< 32 characters)');
  console.warn('   Use a strong secret key for production.');
}

/**
 * Generate JWT token for a user
 * @param {Object} payload - User data to encode in token
 * @returns {string} JWT token
 */
function generateToken(payload) {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRATION
  });
}

/**
 * Verify JWT token
 * @param {string} token - JWT token to verify
 * @returns {Object} Decoded token payload
 */
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    throw new Error('Invalid or expired token');
  }
}

/**
 * Authentication middleware
 * Checks for valid JWT token in Authorization header
 */
function authenticateToken(req, res, next) {
  // Get token from header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({
      success: false,
      error: 'Access denied. No token provided.'
    });
  }

  try {
    // Verify token
    const decoded = verifyToken(token);

    // Add user info to request
    req.user = decoded;

    next();
  } catch (error) {
    return res.status(403).json({
      success: false,
      error: 'Invalid or expired token',
      message: error.message
    });
  }
}

/**
 * Optional authentication middleware
 * Adds user info if token is present, but doesn't require it
 */
function optionalAuth(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token) {
    try {
      const decoded = verifyToken(token);
      req.user = decoded;
    } catch (error) {
      // Token invalid but we don't fail the request
      req.user = null;
    }
  }

  next();
}

/**
 * Role-based authorization middleware
 * @param {string[]} allowedRoles - Array of allowed roles
 */
function authorizeRoles(...allowedRoles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required'
      });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: 'Access denied. Insufficient permissions.',
        requiredRole: allowedRoles,
        yourRole: req.user.role
      });
    }

    next();
  };
}

/**
 * Wallet address verification middleware
 * Ensures the authenticated user matches the wallet address in params
 */
function verifyWalletOwnership(req, res, next) {
  if (!req.user) {
    return res.status(401).json({
      success: false,
      error: 'Authentication required'
    });
  }

  const walletAddress = req.params.walletAddress || req.params.userAddress || req.body.seller || req.body.owner;

  if (req.user.walletAddress !== walletAddress) {
    return res.status(403).json({
      success: false,
      error: 'Access denied. You can only access your own resources.',
      authenticated: req.user.walletAddress,
      requested: walletAddress
    });
  }

  next();
}

module.exports = {
  generateToken,
  verifyToken,
  authenticateToken,
  optionalAuth,
  authorizeRoles,
  verifyWalletOwnership,
  JWT_SECRET,
  JWT_EXPIRATION
};
