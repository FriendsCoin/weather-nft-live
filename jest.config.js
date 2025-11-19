module.exports = {
  // Test environment
  testEnvironment: 'node',

  // Coverage configuration
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/backend/**/*.js',
    '!src/backend/**/*.test.js',
    '!src/backend/simple-test-server.js',
    '!src/backend/simple-sd-ai-mock.py'
  ],

  // Test match patterns
  testMatch: [
    '**/__tests__/**/*.js',
    '**/*.test.js'
  ],

  // Coverage thresholds (start low, increase over time)
  coverageThreshold: {
    global: {
      branches: 30,
      functions: 30,
      lines: 30,
      statements: 30
    }
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  // Test timeout
  testTimeout: 10000,

  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/coverage/'
  ],

  // Module paths
  moduleDirectories: ['node_modules', 'src'],

  // Verbose output
  verbose: true
};
