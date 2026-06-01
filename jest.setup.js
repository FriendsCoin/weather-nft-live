/**
 * Jest setup file
 * Runs before all tests
 */

// Set test environment variables
process.env.NODE_ENV = 'test';
// Deterministic test-only secret so auth/JWT tests can sign & verify tokens
// without depending on a developer's local .env.
process.env.JWT_SECRET = process.env.JWT_SECRET || 'test-jwt-secret-deterministic-0123456789abcdef';
process.env.MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/weathernft_test';
process.env.PORT = process.env.PORT || '3000';
process.env.NFT_SERVICE_PORT = process.env.NFT_SERVICE_PORT || '3009';
process.env.GUILD_SERVICE_PORT = process.env.GUILD_SERVICE_PORT || '3010';
process.env.MARKETPLACE_PORT = process.env.MARKETPLACE_PORT || '3013';

// Increase test timeout for database operations
jest.setTimeout(10000);

// Global teardown
afterAll(async () => {
  // Close any open connections
  await new Promise(resolve => setTimeout(resolve, 500));
});
