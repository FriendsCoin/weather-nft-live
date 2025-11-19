/**
 * Logging Middleware
 * Winston logger with rotation and structured logging
 */

const winston = require('winston');
const expressWinston = require('express-winston');
const path = require('path');
const fs = require('fs');

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

/**
 * Winston logger instance
 */
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'weathernft',
    environment: process.env.NODE_ENV || 'development'
  },
  transports: [
    // Write all logs to combined.log
    new winston.transports.File({
      filename: path.join(logsDir, 'combined.log'),
      maxsize: 10485760, // 10MB
      maxFiles: 5
    }),
    // Write all errors to error.log
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 10485760,
      maxFiles: 5
    })
  ]
});

// Also log to console in development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    )
  }));
}

/**
 * Express middleware for request logging
 */
const requestLogger = expressWinston.logger({
  winstonInstance: logger,
  meta: true,
  msg: 'HTTP {{req.method}} {{req.url}} {{res.statusCode}} {{res.responseTime}}ms',
  expressFormat: false,
  colorize: false,
  ignoreRoute: (req) => {
    // Don't log health checks
    return req.path === '/health';
  },
  requestWhitelist: ['url', 'method', 'httpVersion', 'originalUrl', 'query'],
  responseWhitelist: ['statusCode'],
  dynamicMeta: (req, res) => {
    return {
      user: req.user ? req.user.walletAddress : 'anonymous',
      ip: req.ip,
      userAgent: req.get('user-agent')
    };
  }
});

/**
 * Express middleware for error logging
 */
const errorLogger = expressWinston.errorLogger({
  winstonInstance: logger,
  meta: true,
  msg: 'ERROR {{err.message}}',
  requestWhitelist: ['url', 'method', 'httpVersion', 'originalUrl', 'query'],
  blacklistedMetaFields: ['trace', 'process', 'os']
});

/**
 * Log security events
 */
function logSecurityEvent(event, details) {
  logger.warn('SECURITY_EVENT', {
    event,
    ...details,
    timestamp: new Date().toISOString()
  });
}

/**
 * Log authentication events
 */
function logAuthEvent(event, walletAddress, success, details = {}) {
  logger.info('AUTH_EVENT', {
    event,
    walletAddress,
    success,
    ...details,
    timestamp: new Date().toISOString()
  });
}

/**
 * Log database operations
 */
function logDatabaseEvent(operation, collection, success, details = {}) {
  logger.info('DATABASE_EVENT', {
    operation,
    collection,
    success,
    ...details,
    timestamp: new Date().toISOString()
  });
}

/**
 * Log blockchain transactions
 */
function logBlockchainEvent(event, txHash, details = {}) {
  logger.info('BLOCKCHAIN_EVENT', {
    event,
    txHash,
    ...details,
    timestamp: new Date().toISOString()
  });
}

module.exports = {
  logger,
  requestLogger,
  errorLogger,
  logSecurityEvent,
  logAuthEvent,
  logDatabaseEvent,
  logBlockchainEvent
};
