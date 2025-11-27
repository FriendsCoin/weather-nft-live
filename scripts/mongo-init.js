// MongoDB Initialization Script for WeatherNFT
// This script runs automatically when MongoDB container starts for the first time

// Get credentials from environment variables (set in docker-compose)
const appPassword = process.env.MONGO_APP_PASSWORD || 'app_password';

// Switch to weathernft database
db = db.getSiblingDB('weathernft');

// Create application user with read/write permissions
db.createUser({
  user: 'weathernft_app',
  pwd: appPassword,
  roles: [
    {
      role: 'readWrite',
      db: 'weathernft'
    }
  ]
});

print('✅ MongoDB weathernft database initialized');
print('✅ Application user "weathernft_app" created');
print('⚠️  Remember to change default passwords in production!');
