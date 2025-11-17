/**
 * MongoDB Database Connection Service
 * Handles database connection, initialization, and health checks
 */

const mongoose = require('mongoose');

class DatabaseService {
  constructor() {
    this.isConnected = false;
    this.connectionString = process.env.MONGODB_URI || 'mongodb://localhost:27017/weathernft';
    this.options = {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    };
  }

  /**
   * Connect to MongoDB
   */
  async connect() {
    if (this.isConnected) {
      console.log('📦 Already connected to MongoDB');
      return;
    }

    try {
      await mongoose.connect(this.connectionString, this.options);
      this.isConnected = true;

      console.log('');
      console.log('✅ MongoDB connected successfully');
      console.log(`   Database: ${mongoose.connection.name}`);
      console.log(`   Host: ${mongoose.connection.host}`);
      console.log('');

      // Handle connection events
      mongoose.connection.on('error', (err) => {
        console.error('❌ MongoDB connection error:', err);
        this.isConnected = false;
      });

      mongoose.connection.on('disconnected', () => {
        console.log('⚠️  MongoDB disconnected');
        this.isConnected = false;
      });

      mongoose.connection.on('reconnected', () => {
        console.log('✅ MongoDB reconnected');
        this.isConnected = true;
      });

      // Graceful shutdown
      process.on('SIGINT', async () => {
        await this.disconnect();
        process.exit(0);
      });

    } catch (error) {
      console.error('❌ MongoDB connection failed:', error.message);
      console.log('');
      console.log('💡 Make sure MongoDB is running:');
      console.log('   brew services start mongodb-community  # macOS');
      console.log('   sudo systemctl start mongod            # Linux');
      console.log('   net start MongoDB                      # Windows');
      console.log('');
      throw error;
    }
  }

  /**
   * Disconnect from MongoDB
   */
  async disconnect() {
    if (!this.isConnected) {
      return;
    }

    try {
      await mongoose.connection.close();
      this.isConnected = false;
      console.log('👋 MongoDB disconnected');
    } catch (error) {
      console.error('❌ Error disconnecting from MongoDB:', error);
      throw error;
    }
  }

  /**
   * Check database health
   */
  async healthCheck() {
    try {
      if (!this.isConnected) {
        return {
          status: 'disconnected',
          message: 'Not connected to database'
        };
      }

      // Ping database
      await mongoose.connection.db.admin().ping();

      // Get database stats
      const stats = await mongoose.connection.db.stats();

      return {
        status: 'healthy',
        database: mongoose.connection.name,
        collections: stats.collections,
        dataSize: `${(stats.dataSize / 1024 / 1024).toFixed(2)} MB`,
        indexSize: `${(stats.indexSize / 1024 / 1024).toFixed(2)} MB`,
        connected: this.isConnected
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        connected: false
      };
    }
  }

  /**
   * Initialize database with indexes
   */
  async initializeIndexes() {
    try {
      console.log('🔧 Creating database indexes...');

      const models = mongoose.modelNames();

      for (const modelName of models) {
        const model = mongoose.model(modelName);
        await model.createIndexes();
        console.log(`   ✓ ${modelName} indexes created`);
      }

      console.log('✅ All indexes created successfully');
    } catch (error) {
      console.error('❌ Error creating indexes:', error);
      throw error;
    }
  }

  /**
   * Clear all collections (for testing)
   */
  async clearDatabase() {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('Cannot clear database in production!');
    }

    try {
      const collections = await mongoose.connection.db.collections();

      for (const collection of collections) {
        await collection.deleteMany({});
      }

      console.log('🗑️  Database cleared');
    } catch (error) {
      console.error('❌ Error clearing database:', error);
      throw error;
    }
  }

  /**
   * Get collection statistics
   */
  async getCollectionStats() {
    try {
      const collections = await mongoose.connection.db.listCollections().toArray();
      const stats = {};

      for (const collection of collections) {
        const collStats = await mongoose.connection.db.collection(collection.name).stats();
        stats[collection.name] = {
          count: collStats.count,
          size: `${(collStats.size / 1024).toFixed(2)} KB`,
          avgObjSize: `${(collStats.avgObjSize || 0).toFixed(2)} bytes`,
          indexes: collStats.nindexes
        };
      }

      return stats;
    } catch (error) {
      console.error('❌ Error getting collection stats:', error);
      return {};
    }
  }

  /**
   * Seed database with sample data (for development)
   */
  async seedDatabase() {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('Cannot seed database in production!');
    }

    try {
      const { Guild, User, NFT, Event } = require('./models');

      console.log('🌱 Seeding database...');

      // Create sample users
      const sampleUsers = [
        {
          address: 'tz1SampleUser1ABC123',
          username: 'alice_weather',
          totalCaptures: 0,
          totalEarned: 0
        },
        {
          address: 'tz1SampleUser2DEF456',
          username: 'bob_hunter',
          totalCaptures: 0,
          totalEarned: 0
        }
      ];

      for (const userData of sampleUsers) {
        await User.findOneAndUpdate(
          { address: userData.address },
          userData,
          { upsert: true, new: true }
        );
      }

      console.log('   ✓ Sample users created');

      // Create sample guild
      const sampleGuild = {
        guildId: `guild_${Date.now()}_sample`,
        name: 'Weather Pioneers',
        description: 'First weather hunting guild',
        founder: sampleUsers[0].address,
        members: [sampleUsers[0].address],
        rentedAlgorithms: ['storm-hunter'],
        totalRevenue: 0,
        totalCaptures: 0,
        status: 'active'
      };

      await Guild.findOneAndUpdate(
        { guildId: sampleGuild.guildId },
        sampleGuild,
        { upsert: true, new: true }
      );

      console.log('   ✓ Sample guild created');

      console.log('✅ Database seeded successfully');
    } catch (error) {
      console.error('❌ Error seeding database:', error);
      throw error;
    }
  }
}

// Create singleton instance
const dbService = new DatabaseService();

module.exports = dbService;
