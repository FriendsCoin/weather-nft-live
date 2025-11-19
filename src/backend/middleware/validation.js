/**
 * Input Validation Middleware
 * Uses express-validator for comprehensive input validation
 */

const { body, param, query, validationResult } = require('express-validator');
const { logSecurityEvent } = require('./logger');

/**
 * Middleware to handle validation errors
 */
function handleValidationErrors(req, res, next) {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    // Log validation failure for security monitoring
    logSecurityEvent('validation_failed', {
      path: req.path,
      method: req.method,
      errors: errors.array(),
      ip: req.ip
    });

    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array().map(err => ({
        field: err.path,
        message: err.msg,
        value: err.value
      }))
    });
  }

  next();
}

/**
 * Wallet address validation rules
 */
const walletAddressRules = () => {
  return [
    body('walletAddress')
      .trim()
      .notEmpty()
      .withMessage('Wallet address is required')
      .isLength({ min: 35, max: 42 })
      .withMessage('Invalid wallet address length')
      .custom((value) => {
        // Check if it's Ethereum (0x + 40 hex chars)
        const isEthereum = /^0x[a-fA-F0-9]{40}$/.test(value);

        // Check if it's Tezos (tz1, tz2, tz3, or KT1 + 33 chars)
        const isTezos = /^(tz1|tz2|tz3|KT1)[a-zA-Z0-9]{33}$/.test(value);

        if (!isEthereum && !isTezos) {
          throw new Error('Invalid wallet address format. Must be Ethereum (0x...) or Tezos (tz1...)');
        }

        return true;
      })
  ];
};

/**
 * Password validation rules (strong password requirements)
 */
const passwordRules = () => {
  return [
    body('password')
      .optional()
      .isLength({ min: 8 })
      .withMessage('Password must be at least 8 characters long')
      .matches(/[a-z]/)
      .withMessage('Password must contain at least one lowercase letter')
      .matches(/[A-Z]/)
      .withMessage('Password must contain at least one uppercase letter')
      .matches(/[0-9]/)
      .withMessage('Password must contain at least one number')
      .matches(/[!@#$%^&*(),.?":{}|<>]/)
      .withMessage('Password must contain at least one special character (!@#$%^&*...)')
      .not()
      .matches(/\s/)
      .withMessage('Password must not contain spaces')
  ];
};

/**
 * Username validation rules
 */
const usernameRules = () => {
  return [
    body('username')
      .optional()
      .trim()
      .isLength({ min: 3, max: 30 })
      .withMessage('Username must be between 3 and 30 characters')
      .matches(/^[a-zA-Z0-9_-]+$/)
      .withMessage('Username can only contain letters, numbers, hyphens, and underscores')
      .not()
      .matches(/^[0-9]+$/)
      .withMessage('Username cannot be only numbers')
  ];
};

/**
 * Email validation rules
 */
const emailRules = () => {
  return [
    body('email')
      .optional()
      .trim()
      .normalizeEmail()
      .isEmail()
      .withMessage('Invalid email address')
      .isLength({ max: 100 })
      .withMessage('Email must be less than 100 characters')
  ];
};

/**
 * Registration validation
 */
const validateRegistration = [
  ...walletAddressRules(),
  ...usernameRules(),
  ...emailRules(),
  ...passwordRules(),
  handleValidationErrors
];

/**
 * Login validation
 */
const validateLogin = [
  ...walletAddressRules(),
  body('signature')
    .optional()
    .isString()
    .withMessage('Signature must be a string')
    .notEmpty()
    .withMessage('Signature cannot be empty'),
  body('timestamp')
    .optional()
    .isInt({ min: 0 })
    .withMessage('Timestamp must be a positive integer')
    .custom((value) => {
      const now = Date.now();
      const age = now - value;

      // Must be within 5 minutes
      if (age < 0 || age > 5 * 60 * 1000) {
        throw new Error('Timestamp is expired or invalid');
      }

      return true;
    }),
  body('password')
    .optional()
    .isString()
    .withMessage('Password must be a string')
    .notEmpty()
    .withMessage('Password cannot be empty'),
  handleValidationErrors
];

/**
 * NFT creation validation
 */
const validateNFTCreation = [
  body('latitude')
    .isFloat({ min: -90, max: 90 })
    .withMessage('Latitude must be between -90 and 90'),
  body('longitude')
    .isFloat({ min: -180, max: 180 })
    .withMessage('Longitude must be between -180 and 180'),
  body('location')
    .optional()
    .trim()
    .isLength({ max: 200 })
    .withMessage('Location name must be less than 200 characters'),
  body('weatherCondition')
    .optional()
    .trim()
    .isLength({ max: 100 })
    .withMessage('Weather condition must be less than 100 characters'),
  body('temperature')
    .optional()
    .isFloat({ min: -100, max: 100 })
    .withMessage('Temperature must be between -100 and 100 degrees'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('Metadata must be an object'),
  handleValidationErrors
];

/**
 * Marketplace listing validation
 */
const validateMarketplaceListing = [
  body('nftId')
    .trim()
    .notEmpty()
    .withMessage('NFT ID is required')
    .isMongoId()
    .withMessage('Invalid NFT ID format'),
  body('price')
    .isFloat({ min: 0.01 })
    .withMessage('Price must be at least 0.01')
    .isFloat({ max: 1000000 })
    .withMessage('Price must be less than 1,000,000'),
  body('seller')
    .trim()
    .notEmpty()
    .withMessage('Seller wallet address is required'),
  handleValidationErrors
];

/**
 * Marketplace purchase validation
 */
const validateMarketplacePurchase = [
  body('listingId')
    .trim()
    .notEmpty()
    .withMessage('Listing ID is required')
    .isMongoId()
    .withMessage('Invalid listing ID format'),
  body('buyer')
    .trim()
    .notEmpty()
    .withMessage('Buyer wallet address is required'),
  handleValidationErrors
];

/**
 * Guild creation validation
 */
const validateGuildCreation = [
  body('name')
    .trim()
    .notEmpty()
    .withMessage('Guild name is required')
    .isLength({ min: 3, max: 50 })
    .withMessage('Guild name must be between 3 and 50 characters')
    .matches(/^[a-zA-Z0-9\s_-]+$/)
    .withMessage('Guild name can only contain letters, numbers, spaces, hyphens, and underscores'),
  body('description')
    .optional()
    .trim()
    .isLength({ max: 500 })
    .withMessage('Description must be less than 500 characters'),
  body('founder')
    .trim()
    .notEmpty()
    .withMessage('Founder wallet address is required'),
  body('entryFee')
    .optional()
    .isFloat({ min: 0 })
    .withMessage('Entry fee must be a positive number'),
  handleValidationErrors
];

/**
 * Guild join validation
 */
const validateGuildJoin = [
  param('guildId')
    .trim()
    .notEmpty()
    .withMessage('Guild ID is required')
    .isMongoId()
    .withMessage('Invalid guild ID format'),
  body('walletAddress')
    .trim()
    .notEmpty()
    .withMessage('Wallet address is required'),
  handleValidationErrors
];

/**
 * AI art generation validation
 */
const validateArtGeneration = [
  body('prompt')
    .trim()
    .notEmpty()
    .withMessage('Art prompt is required')
    .isLength({ min: 10, max: 500 })
    .withMessage('Prompt must be between 10 and 500 characters')
    .matches(/^[a-zA-Z0-9\s,.\-!?]+$/)
    .withMessage('Prompt contains invalid characters'),
  body('weatherData')
    .optional()
    .isObject()
    .withMessage('Weather data must be an object'),
  handleValidationErrors
];

/**
 * MongoDB ID parameter validation
 */
const validateMongoId = (paramName = 'id') => {
  return [
    param(paramName)
      .trim()
      .notEmpty()
      .withMessage(`${paramName} is required`)
      .isMongoId()
      .withMessage(`Invalid ${paramName} format`),
    handleValidationErrors
  ];
};

/**
 * Wallet address parameter validation
 */
const validateWalletParam = (paramName = 'walletAddress') => {
  return [
    param(paramName)
      .trim()
      .notEmpty()
      .withMessage('Wallet address is required')
      .custom((value) => {
        const isEthereum = /^0x[a-fA-F0-9]{40}$/.test(value);
        const isTezos = /^(tz1|tz2|tz3|KT1)[a-zA-Z0-9]{33}$/.test(value);

        if (!isEthereum && !isTezos) {
          throw new Error('Invalid wallet address format');
        }

        return true;
      }),
    handleValidationErrors
  ];
};

/**
 * Pagination query validation
 */
const validatePagination = [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Page must be a positive integer')
    .toInt(),
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('Limit must be between 1 and 100')
    .toInt(),
  handleValidationErrors
];

/**
 * Sanitize input to prevent XSS
 */
function sanitizeInput(req, res, next) {
  // Remove any HTML tags from string inputs
  const sanitize = (obj) => {
    for (let key in obj) {
      if (typeof obj[key] === 'string') {
        // Remove HTML tags
        obj[key] = obj[key].replace(/<[^>]*>/g, '');

        // Remove script tags (double check)
        obj[key] = obj[key].replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
      } else if (typeof obj[key] === 'object' && obj[key] !== null) {
        sanitize(obj[key]);
      }
    }
  };

  if (req.body) sanitize(req.body);
  if (req.query) sanitize(req.query);
  if (req.params) sanitize(req.params);

  next();
}

module.exports = {
  handleValidationErrors,
  validateRegistration,
  validateLogin,
  validateNFTCreation,
  validateMarketplaceListing,
  validateMarketplacePurchase,
  validateGuildCreation,
  validateGuildJoin,
  validateArtGeneration,
  validateMongoId,
  validateWalletParam,
  validatePagination,
  sanitizeInput
};
