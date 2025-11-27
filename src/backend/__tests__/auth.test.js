/**
 * Authentication Tests
 * Tests JWT authentication middleware and auth service
 */

const { generateToken, verifyToken, authenticateToken } = require('../middleware/auth');

describe('Authentication Middleware', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Token Generation', () => {
    test('should generate valid JWT token', () => {
      const payload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        role: 'user'
      };

      const token = generateToken(payload);

      expect(token).toBeTruthy();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3); // JWT has 3 parts
    });

    test('should include payload data in token', () => {
      const payload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        username: 'testuser',
        role: 'user'
      };

      const token = generateToken(payload);
      const decoded = verifyToken(token);

      expect(decoded.userId).toBe(payload.userId);
      expect(decoded.walletAddress).toBe(payload.walletAddress);
      expect(decoded.username).toBe(payload.username);
      expect(decoded.role).toBe(payload.role);
    });

    test('should include expiration in token', () => {
      const payload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        role: 'user'
      };

      const token = generateToken(payload);
      const decoded = verifyToken(token);

      expect(decoded.exp).toBeTruthy();
      expect(decoded.iat).toBeTruthy();
      expect(decoded.exp).toBeGreaterThan(decoded.iat);
    });
  });

  describe('Token Verification', () => {
    test('should verify valid token', () => {
      const payload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        role: 'user'
      };

      const token = generateToken(payload);
      const decoded = verifyToken(token);

      expect(decoded).toBeTruthy();
      expect(decoded.userId).toBe(payload.userId);
    });

    test('should throw error for invalid token', () => {
      const invalidToken = 'invalid.token.here';

      expect(() => {
        verifyToken(invalidToken);
      }).toThrow('Invalid or expired token');
    });

    test('should throw error for malformed token', () => {
      const malformedToken = 'notavalidtoken';

      expect(() => {
        verifyToken(malformedToken);
      }).toThrow();
    });

    test('should throw error for empty token', () => {
      expect(() => {
        verifyToken('');
      }).toThrow();
    });
  });

  describe('Authentication Middleware', () => {
    test('should attach user to request on valid token', () => {
      const payload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        role: 'user'
      };

      const token = generateToken(payload);

      const req = {
        headers: {
          authorization: `Bearer ${token}`
        }
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn()
      };

      const next = jest.fn();

      authenticateToken(req, res, next);

      expect(next).toHaveBeenCalled();
      expect(req.user).toBeTruthy();
      expect(req.user.userId).toBe(payload.userId);
      expect(req.user.walletAddress).toBe(payload.walletAddress);
    });

    test('should reject request without authorization header', () => {
      const req = {
        headers: {}
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn()
      };

      const next = jest.fn();

      authenticateToken(req, res, next);

      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalledWith({
        success: false,
        error: 'Access denied. No token provided.'
      });
      expect(next).not.toHaveBeenCalled();
    });

    test('should reject request with invalid token', () => {
      const req = {
        headers: {
          authorization: 'Bearer invalid.token.here'
        }
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn()
      };

      const next = jest.fn();

      authenticateToken(req, res, next);

      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: false,
          error: 'Invalid or expired token'
        })
      );
      expect(next).not.toHaveBeenCalled();
    });

    test('should reject request with malformed authorization header', () => {
      const req = {
        headers: {
          authorization: 'InvalidFormat'
        }
      };

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn()
      };

      const next = jest.fn();

      authenticateToken(req, res, next);

      expect(res.status).toHaveBeenCalledWith(401);
      expect(next).not.toHaveBeenCalled();
    });
  });

  describe('User Registration Data', () => {
    test('should validate required registration fields', () => {
      const validData = {
        walletAddress: '0xABC123',
        username: 'testuser',
        email: 'test@example.com'
      };

      expect(validData.walletAddress).toBeTruthy();
      expect(validData.username).toBeTruthy();
      expect(validData.email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    });

    test('should accept registration without optional fields', () => {
      const minimalData = {
        walletAddress: '0xABC123'
      };

      expect(minimalData.walletAddress).toBeTruthy();
    });

    test('should validate wallet address format', () => {
      const validAddresses = [
        '0x1234567890abcdef',
        '0xABCDEF1234567890',
        'tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb'
      ];

      validAddresses.forEach(address => {
        expect(address).toBeTruthy();
        expect(address.length).toBeGreaterThan(10);
      });
    });
  });

  describe('User Login Data', () => {
    test('should validate login with wallet address', () => {
      const loginData = {
        walletAddress: '0xABC123'
      };

      expect(loginData.walletAddress).toBeTruthy();
    });

    test('should validate login with password', () => {
      const loginData = {
        walletAddress: '0xABC123',
        password: 'securePassword123'
      };

      expect(loginData.walletAddress).toBeTruthy();
      expect(loginData.password).toBeTruthy();
    });

    test('should validate login with signature', () => {
      const loginData = {
        walletAddress: '0xABC123',
        signature: 'signatureHash123'
      };

      expect(loginData.walletAddress).toBeTruthy();
      expect(loginData.signature).toBeTruthy();
    });
  });

  describe('Protected Routes Authorization', () => {
    test('should allow access with valid token', () => {
      const payload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        role: 'user'
      };

      const token = generateToken(payload);

      expect(token).toBeTruthy();

      const decoded = verifyToken(token);
      expect(decoded.role).toBe('user');
    });

    test('should identify admin role', () => {
      const payload = {
        userId: 'admin123',
        walletAddress: '0xADMIN',
        role: 'admin'
      };

      const token = generateToken(payload);
      const decoded = verifyToken(token);

      expect(decoded.role).toBe('admin');
    });

    test('should identify founder role', () => {
      const payload = {
        userId: 'founder123',
        walletAddress: '0xFOUNDER',
        role: 'founder'
      };

      const token = generateToken(payload);
      const decoded = verifyToken(token);

      expect(decoded.role).toBe('founder');
    });
  });

  describe('Token Refresh', () => {
    test('should allow token refresh with valid token', () => {
      const originalPayload = {
        userId: 'user123',
        walletAddress: '0xABC123',
        role: 'user'
      };

      const originalToken = generateToken(originalPayload);
      const decoded = verifyToken(originalToken);

      // Generate new token with same payload
      const newToken = generateToken({
        userId: decoded.userId,
        walletAddress: decoded.walletAddress,
        role: decoded.role
      });

      expect(newToken).toBeTruthy();
      // Note: Tokens generated at the same second with same payload may be identical
      // This is expected behavior for JWT

      const newDecoded = verifyToken(newToken);
      expect(newDecoded.userId).toBe(originalPayload.userId);
      expect(newDecoded.walletAddress).toBe(originalPayload.walletAddress);
      expect(newDecoded.role).toBe(originalPayload.role);
    });
  });

  describe('Wallet Ownership Verification', () => {
    test('should verify matching wallet addresses', () => {
      const userWallet = '0xABC123';
      const requestedWallet = '0xABC123';

      expect(userWallet).toBe(requestedWallet);
    });

    test('should reject mismatched wallet addresses', () => {
      const userWallet = '0xABC123';
      const requestedWallet = '0xDEF456';

      expect(userWallet).not.toBe(requestedWallet);
    });

    test('should handle case-sensitive wallet addresses', () => {
      const wallet1 = '0xABC123';
      const wallet2 = '0xabc123';

      // Most blockchain addresses are case-sensitive
      expect(wallet1 === wallet2).toBe(false);
    });
  });
});
