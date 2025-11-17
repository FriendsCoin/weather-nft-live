#!/usr/bin/env node

/**
 * Database Manager CLI
 * Tool for managing MongoDB database operations
 */

require('dotenv').config();
const dbService = require('./database');
const models = require('./models');

const commands = {
  connect: 'Connect to database',
  init: 'Initialize database with indexes',
  seed: 'Seed database with sample data',
  clear: 'Clear all collections (dev only)',
  stats: 'Show database statistics',
  health: 'Check database health',
  collections: 'List all collections with stats'
};

async function main() {
  const command = process.argv[2];

  if (!command || command === 'help') {
    console.log('\n📦 WeatherNFT Database Manager\n');
    console.log('Available commands:');
    Object.entries(commands).forEach(([cmd, desc]) => {
      console.log(`  ${cmd.padEnd(15)} - ${desc}`);
    });
    console.log('\nUsage:');
    console.log('  node src/backend/db-manager.js <command>\n');
    process.exit(0);
  }

  try {
    await dbService.connect();

    switch (command) {
      case 'init':
        await dbService.initializeIndexes();
        break;

      case 'seed':
        await dbService.seedDatabase();
        break;

      case 'clear':
        console.log('⚠️  This will delete ALL data!');
        await dbService.clearDatabase();
        break;

      case 'stats':
        const dbStats = await dbService.healthCheck();
        console.log('\n📊 Database Statistics:');
        console.log(JSON.stringify(dbStats, null, 2));
        break;

      case 'health':
        const health = await dbService.healthCheck();
        console.log('\n💊 Database Health:');
        console.log(`Status: ${health.status}`);
        console.log(`Database: ${health.database}`);
        console.log(`Collections: ${health.collections}`);
        console.log(`Data Size: ${health.dataSize}`);
        console.log(`Index Size: ${health.indexSize}`);
        break;

      case 'collections':
        const collStats = await dbService.getCollectionStats();
        console.log('\n📚 Collections:');
        Object.entries(collStats).forEach(([name, stats]) => {
          console.log(`\n${name}:`);
          console.log(`  Documents: ${stats.count}`);
          console.log(`  Size: ${stats.size}`);
          console.log(`  Avg Size: ${stats.avgObjSize}`);
          console.log(`  Indexes: ${stats.indexes}`);
        });
        break;

      case 'connect':
        console.log('✅ Connected successfully');
        break;

      default:
        console.log(`❌ Unknown command: ${command}`);
        console.log('Run "node src/backend/db-manager.js help" for available commands');
        process.exit(1);
    }

    await dbService.disconnect();
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main };
