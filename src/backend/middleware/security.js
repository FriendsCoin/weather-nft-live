/**
 * Security Middleware
 * Rate limiting, helmet, and security headers for all services
 */

const rateLimit = require('express-rate-limit');
const helmet = require('helmet');

/**
 * Helmet security headers configuration
 */
function securityHeaders() {
  return helmet({
    // Content Security Policy
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'"],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    // Prevent clickjacking
    frameguard: { action: 'deny' },
    // Hide X-Powered-By header
    hidePoweredBy: true,
    // Prevent MIME type sniffing
    noSniff: true,
    // Force HTTPS
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    },
    // Prevent IE from executing downloads in your site's context
    ieNoOpen: true,
    // Don't allow your site to be used in an iframe
    xssFilter: true
  });
}

/**
 * General rate limiter for all routes
 * 100 requests per 15 minutes
 */
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    success: false,
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
  // Skip rate limiting for health checks
  skip: (req) => req.path === '/health'
});

/**
 * Strict rate limiter for authentication endpoints
 * 5 requests per 15 minutes (prevent brute-force)
 */
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 login/register requests per windowMs
  message: {
    success: false,
    error: 'Too many authentication attempts from this IP, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Slow down instead of blocking
  skipSuccessfulRequests: true // Don't count successful requests
});

/**
 * Rate limiter for creating resources (listings, NFTs, guilds)
 * 20 requests per hour
 */
const createLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 20, // Limit each IP to 20 create requests per hour
  message: {
    success: false,
    error: 'Too many creation requests, please slow down.',
    retryAfter: '1 hour'
  },
  standardHeaders: true,
  legacyHeaders: false
});

/**
 * Rate limiter for expensive operations (AI art generation)
 * 10 requests per hour
 */
const expensiveLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 10, // Limit each IP to 10 expensive requests per hour
  message: {
    success: false,
    error: 'AI art generation rate limit exceeded. Please try again later.',
    retryAfter: '1 hour'
  },
  standardHeaders: true,
  legacyHeaders: false
});

/**
 * CORS configuration
 * Restrict to specific domains in production
 */
function corsOptions() {
  const allowedOrigins = process.env.NODE_ENV === 'production'
    ? (process.env.ALLOWED_ORIGINS || '').split(',').filter(Boolean)
    : ['http://localhost:8081', 'http://localhost:3000'];

  return {
    origin: (origin, callback) => {
      // Allow requests with no origin (mobile apps, Postman, etc.)
      if (!origin) return callback(null, true);

      if (process.env.NODE_ENV !== 'production') {
        // Allow all origins in development
        return callback(null, true);
      }

      if (allowedOrigins.indexOf(origin) !== -1) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization']
  };
}

/**
 * Sanitize error messages for production
 * Don't leak sensitive information
 */
function sanitizeError(error, req, res) {
  if (process.env.NODE_ENV === 'production') {
    // Generic error message in production
    return {
      success: false,
      error: 'An error occurred',
      requestId: req.id || Date.now()
    };
  } else {
    // Detailed error in development
    return {
      success: false,
      error: error.message,
      stack: error.stack,
      requestId: req.id || Date.now()
    };
  }
}

module.exports = {
  securityHeaders,
  generalLimiter,
  authLimiter,
  createLimiter,
  expensiveLimiter,
  corsOptions,
  sanitizeError
};
