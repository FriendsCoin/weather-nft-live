#!/usr/bin/env node

/**
 * Guild Management Service for WeatherNFT
 * Handles guild creation, membership, algorithm rentals, and revenue sharing
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const DatabaseService = require('./database');
const { Guild, GuildMembership, AlgorithmRental, RevenueShare } = require('./models');

const app = express();
const PORT = process.env.GUILD_SERVICE_PORT || 3010;

app.use(cors());
app.use(express.json());

// Initialize database
const db = new DatabaseService();

// AI Algorithms available for rental
const AI_ALGORITHMS = {
  'storm-hunter': {
    id: 'storm-hunter',
    name: 'Storm Hunter',
    description: 'Detects severe weather formation',
    monthlyPrice: 4, // XTZ
    specialization: 'thunderstorms, hurricanes, tornadoes',
    accuracy: 97.8
  },
  'aurora-predictor': {
    id: 'aurora-predictor',
    name: 'Aurora Predictor',
    description: 'Identifies northern lights probability',
    monthlyPrice: 3, // XTZ
    specialization: 'aurora borealis, solar activity',
    accuracy: 89.3
  },
  'micro-climate': {
    id: 'micro-climate',
    name: 'Micro Climate',
    description: 'Finds unusual local conditions',
    monthlyPrice: 2, // XTZ
    specialization: 'microclimates, local anomalies',
    accuracy: 91.5
  },
  'extreme-weather': {
    id: 'extreme-weather',
    name: 'Extreme Weather',
    description: 'Tracks dangerous conditions',
    monthlyPrice: 4, // XTZ
    specialization: 'extreme temperatures, severe storms',
    accuracy: 96.1
  },
  'temperature-anomaly': {
    id: 'temperature-anomaly',
    name: 'Temperature Anomaly',
    description: 'Spots unusual temperature patterns',
    monthlyPrice: 1, // XTZ
    specialization: 'heat waves, cold snaps',
    accuracy: 94.2
  }
};

// Health check
app.get('/health', async (req, res) => {
  try {
    const isDbConnected = await db.healthCheck();
    const [guildsCount, membersCount, rentalsCount] = await Promise.all([
      Guild.countDocuments(),
      GuildMembership.countDocuments(),
      AlgorithmRental.countDocuments({ status: 'active' })
    ]);

    res.json({
      status: 'OK',
      service: 'WeatherNFT Guild Service',
      database: isDbConnected ? 'connected' : 'disconnected',
      stats: {
        guilds_count: guildsCount,
        total_members: membersCount,
        active_rentals: rentalsCount
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      status: 'ERROR',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Get all available AI algorithms
 * GET /api/algorithms
 */
app.get('/api/algorithms', (req, res) => {
  res.json({
    success: true,
    count: Object.keys(AI_ALGORITHMS).length,
    data: Object.values(AI_ALGORITHMS)
  });
});

/**
 * Get algorithm details
 * GET /api/algorithms/:algorithmId
 */
app.get('/api/algorithms/:algorithmId', (req, res) => {
  const { algorithmId } = req.params;
  const algorithm = AI_ALGORITHMS[algorithmId];

  if (!algorithm) {
    return res.status(404).json({
      success: false,
      error: 'Algorithm not found'
    });
  }

  // Find guilds renting this algorithm
  const rentingGuildsData = await AlgorithmRental.find({
    algorithmId,
    status: 'active'
  }).limit(5).lean();

  const guildIds = rentingGuildsData.map(r => r.guildId);
  const rentingGuilds = await Guild.find({ guildId: { $in: guildIds } }).lean();

  const totalRenting = await AlgorithmRental.countDocuments({
    algorithmId,
    status: 'active'
  });

  res.json({
    success: true,
    data: {
      ...algorithm,
      renting_guilds_count: totalRenting,
      renting_guilds: rentingGuilds.slice(0, 5) // Top 5
    }
  });
});

/**
 * Create a new guild
 * POST /api/guilds/create
 */
app.post('/api/guilds/create', async (req, res) => {
  try {
    const { name, description, founder, logo, algorithms } = req.body;

    if (!name || !founder) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, founder'
      });
    }

    const guildId = `guild_${Date.now()}_${Math.random().toString(36).substring(7)}`;

    const guildData = {
      guildId: guildId,
      name: name,
      description: description || '',
      founder: founder, // Wallet address
      logo: logo || null,
      members: [founder], // Founder is first member
      rentedAlgorithms: algorithms || [],
      totalRevenue: 0,
      totalCaptures: 0,
      status: 'active'
    };

    const guild = await Guild.create(guildData);

    // Add founder membership
    const membershipData = {
      guildId: guildId,
      userAddress: founder,
      role: 'founder',
      captures: 0,
      revenue: 0
    };

    const membership = await GuildMembership.create(membershipData);

    console.log(`✅ Guild created: ${name} (${guildId})`);

    res.json({
      success: true,
      message: 'Guild created successfully',
      data: {
        ...guild.toObject(),
        membership: membership
      }
    });

  } catch (error) {
    console.error('❌ Guild creation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get all guilds
 * GET /api/guilds
 */
app.get('/api/guilds', async (req, res) => {
  try {
    const {
      limit = 50,
      offset = 0,
      sortBy = 'totalRevenue',
      sortOrder = 'desc'
    } = req.query;

    const sort = {};
    sort[sortBy] = sortOrder === 'asc' ? 1 : -1;

    const [guildList, total] = await Promise.all([
      Guild.find()
        .sort(sort)
        .skip(parseInt(offset))
        .limit(parseInt(limit))
        .lean(),
      Guild.countDocuments()
    ]);

    // Add member and algorithm counts
    const enrichedGuilds = guildList.map(guild => ({
      ...guild,
      memberCount: guild.members.length,
      algorithmCount: guild.rentedAlgorithms.length
    }));

    res.json({
      success: true,
      count: enrichedGuilds.length,
      total: total,
      data: enrichedGuilds,
      pagination: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: (parseInt(offset) + enrichedGuilds.length) < total
      }
    });
  } catch (error) {
    console.error('Error fetching guilds:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get guild details
 * GET /api/guilds/:guildId
 */
app.get('/api/guilds/:guildId', async (req, res) => {
  try {
    const { guildId } = req.params;
    const guild = await Guild.findOne({ guildId }).lean();

    if (!guild) {
      return res.status(404).json({
        success: false,
        error: 'Guild not found'
      });
    }

    // Get member details
    const memberDetails = await GuildMembership.find({ guildId }).lean();

    // Get rented algorithms details
    const rentals = await AlgorithmRental.find({
      guildId,
      status: 'active'
    }).lean();

    const rentedAlgorithmsDetails = guild.rentedAlgorithms.map(algId => {
      const rental = rentals.find(r => r.algorithmId === algId);
      return {
        ...AI_ALGORITHMS[algId],
        rental: rental
      };
    }).filter(alg => alg.id); // Filter out algorithms that don't exist

    res.json({
      success: true,
      data: {
        ...guild,
        members: memberDetails,
        algorithms: rentedAlgorithmsDetails
      }
    });
  } catch (error) {
    console.error('Error fetching guild:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Join a guild
 * POST /api/guilds/:guildId/join
 */
app.post('/api/guilds/:guildId/join', async (req, res) => {
  try {
    const { guildId } = req.params;
    const { userAddress } = req.body;

    if (!userAddress) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: userAddress'
      });
    }

    const guild = await Guild.findOne({ guildId });

    if (!guild) {
      return res.status(404).json({
        success: false,
        error: 'Guild not found'
      });
    }

    // Check if already a member
    const existingMembership = await GuildMembership.findOne({ guildId, userAddress });
    if (existingMembership) {
      return res.status(400).json({
        success: false,
        error: 'Already a member of this guild'
      });
    }

    // Add member to guild
    guild.members.push(userAddress);
    await guild.save();

    // Create membership record
    const membershipData = {
      guildId: guildId,
      userAddress: userAddress,
      role: 'member',
      captures: 0,
      revenue: 0
    };

    const membership = await GuildMembership.create(membershipData);

    console.log(`✅ ${userAddress} joined guild ${guild.name}`);

    res.json({
      success: true,
      message: 'Joined guild successfully',
      data: {
        guild: guild,
        membership: membership
      }
    });

  } catch (error) {
    console.error('❌ Join guild failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Rent an algorithm for a guild
 * POST /api/guilds/:guildId/rent-algorithm
 */
app.post('/api/guilds/:guildId/rent-algorithm', async (req, res) => {
  try {
    const { guildId } = req.params;
    const { algorithmId, txHash } = req.body;

    if (!algorithmId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: algorithmId'
      });
    }

    const guild = await Guild.findOne({ guildId });
    const algorithm = AI_ALGORITHMS[algorithmId];

    if (!guild) {
      return res.status(404).json({ success: false, error: 'Guild not found' });
    }

    if (!algorithm) {
      return res.status(404).json({ success: false, error: 'Algorithm not found' });
    }

    // Check if already renting
    const existingRental = await AlgorithmRental.findOne({
      guildId,
      algorithmId,
      status: 'active'
    });

    if (existingRental) {
      return res.status(400).json({
        success: false,
        error: 'Already renting this algorithm'
      });
    }

    // Create rental record
    const rentalId = `rental_${Date.now()}`;
    const startDate = new Date();
    const endDate = new Date(startDate.getTime() + (30 * 24 * 60 * 60 * 1000)); // 30 days

    const rentalData = {
      rentalId: rentalId,
      guildId: guildId,
      algorithmId: algorithmId,
      startDate: startDate,
      endDate: endDate,
      monthlyPrice: algorithm.monthlyPrice,
      txHash: txHash || null,
      status: 'active'
    };

    const rental = await AlgorithmRental.create(rentalData);

    // Update guild
    if (!guild.rentedAlgorithms.includes(algorithmId)) {
      guild.rentedAlgorithms.push(algorithmId);
      await guild.save();
    }

    console.log(`✅ Guild ${guild.name} rented ${algorithm.name}`);

    res.json({
      success: true,
      message: 'Algorithm rented successfully',
      data: {
        rental: rental,
        algorithm: algorithm
      }
    });

  } catch (error) {
    console.error('❌ Algorithm rental failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Record a capture and distribute revenue
 * POST /api/guilds/capture-event
 */
app.post('/api/guilds/capture-event', async (req, res) => {
  try {
    const { guildId, userAddress, algorithmId, eventId, capturePrice } = req.body;

    if (!guildId || !userAddress || !capturePrice) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }

    const guild = await Guild.findOne({ guildId });
    if (!guild) {
      return res.status(404).json({ success: false, error: 'Guild not found' });
    }

    const membership = await GuildMembership.findOne({ guildId, userAddress });

    if (!membership) {
      return res.status(404).json({ success: false, error: 'Not a guild member' });
    }

    // Calculate revenue share (15% to guild)
    const guildShare = capturePrice * 0.15;
    const userShare = capturePrice * 0.85;

    // Update guild stats
    guild.totalRevenue += guildShare;
    guild.totalCaptures += 1;
    await guild.save();

    // Update member stats
    membership.captures += 1;
    membership.revenue += userShare;
    await membership.save();

    // Record revenue share
    const shareId = `share_${Date.now()}`;
    const revenueShareData = {
      shareId: shareId,
      guildId: guildId,
      userAddress: userAddress,
      algorithmId: algorithmId,
      eventId: eventId,
      capturePrice: capturePrice,
      guildShare: guildShare,
      userShare: userShare
    };

    await RevenueShare.create(revenueShareData);

    console.log(`💰 Revenue distributed: ${guildShare} XTZ to guild, ${userShare} XTZ to user`);

    res.json({
      success: true,
      message: 'Capture recorded and revenue distributed',
      data: {
        guildShare: guildShare,
        userShare: userShare,
        totalGuildRevenue: guild.totalRevenue,
        memberCaptures: membership.captures
      }
    });

  } catch (error) {
    console.error('❌ Capture recording failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get user's guild memberships
 * GET /api/user/:userAddress/guilds
 */
app.get('/api/user/:userAddress/guilds', async (req, res) => {
  try {
    const { userAddress } = req.params;

    const userMemberships = await GuildMembership.find({ userAddress }).lean();

    // Get guild details for each membership
    const guildIds = userMemberships.map(m => m.guildId);
    const guilds = await Guild.find({ guildId: { $in: guildIds } }).lean();

    // Create a map for quick lookup
    const guildMap = new Map(guilds.map(g => [g.guildId, g]));

    const enrichedMemberships = userMemberships
      .map(m => ({
        ...m,
        guild: guildMap.get(m.guildId)
      }))
      .filter(m => m.guild);

    res.json({
      success: true,
      count: enrichedMemberships.length,
      data: enrichedMemberships
    });
  } catch (error) {
    console.error('Error fetching user guilds:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get guild revenue history
 * GET /api/guilds/:guildId/revenue
 */
app.get('/api/guilds/:guildId/revenue', async (req, res) => {
  try {
    const { guildId } = req.params;
    const { limit = 50, offset = 0 } = req.query;

    const [guildRevenue, totalCount] = await Promise.all([
      RevenueShare.find({ guildId })
        .sort({ timestamp: -1 })
        .skip(parseInt(offset))
        .limit(parseInt(limit))
        .lean(),
      RevenueShare.countDocuments({ guildId })
    ]);

    const totalRevenue = guildRevenue.reduce((sum, share) => sum + share.guildShare, 0);

    res.json({
      success: true,
      totalRevenue: totalRevenue,
      transactionCount: totalCount,
      data: guildRevenue,
      pagination: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: (parseInt(offset) + guildRevenue.length) < totalCount
      }
    });
  } catch (error) {
    console.error('Error fetching guild revenue:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get guild leaderboard
 * GET /api/leaderboard
 */
app.get('/api/leaderboard', async (req, res) => {
  try {
    const { limit = 100, sortBy = 'totalRevenue' } = req.query;

    const sort = {};
    sort[sortBy] = -1; // Descending order

    const leaderboard = await Guild.find()
      .sort(sort)
      .limit(parseInt(limit))
      .lean();

    const enrichedLeaderboard = leaderboard.map(guild => ({
      id: guild.guildId,
      name: guild.name,
      totalRevenue: guild.totalRevenue,
      totalCaptures: guild.totalCaptures,
      memberCount: guild.members.length,
      algorithmCount: guild.rentedAlgorithms.length
    }));

    res.json({
      success: true,
      count: enrichedLeaderboard.length,
      data: enrichedLeaderboard
    });
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start server with database connection
async function startServer() {
  try {
    console.log('');
    console.log('🏛️  WeatherNFT Guild Management Service');
    console.log('='.repeat(50));

    // Connect to MongoDB
    console.log('📊 Connecting to MongoDB...');
    await db.connect();
    console.log('✅ MongoDB connected');

    // Initialize indexes
    console.log('📝 Initializing database indexes...');
    await Promise.all([
      Guild.createIndexes(),
      GuildMembership.createIndexes(),
      AlgorithmRental.createIndexes(),
      RevenueShare.createIndexes()
    ]);
    console.log('✅ Database indexes initialized');

    // Start Express server
    app.listen(PORT, () => {
      console.log(`✅ Server running on http://localhost:${PORT}`);
      console.log(`🎯 Available Algorithms: ${Object.keys(AI_ALGORITHMS).length}`);
      console.log('');
      console.log('📊 Endpoints:');
      console.log('   • GET  /health                         - Health check');
      console.log('   • GET  /api/algorithms                 - List all algorithms');
      console.log('   • GET  /api/algorithms/:id             - Algorithm details');
      console.log('   • POST /api/guilds/create              - Create new guild');
      console.log('   • GET  /api/guilds                     - List all guilds');
      console.log('   • GET  /api/guilds/:id                 - Guild details');
      console.log('   • POST /api/guilds/:id/join            - Join guild');
      console.log('   • POST /api/guilds/:id/rent-algorithm  - Rent algorithm');
      console.log('   • POST /api/guilds/capture-event       - Record capture');
      console.log('   • GET  /api/user/:address/guilds       - User memberships');
      console.log('   • GET  /api/guilds/:id/revenue         - Revenue history');
      console.log('   • GET  /api/leaderboard                - Guild leaderboard');
      console.log('');
      console.log('✅ Ready to manage guilds!');
      console.log('📦 MongoDB collections ready: Guild, GuildMembership, AlgorithmRental, RevenueShare');
      console.log('');
    });

  } catch (error) {
    console.error('❌ Failed to start guild service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⚠️  Shutting down guild service...');
  try {
    await db.disconnect();
    console.log('✅ Database connection closed');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
});

process.on('SIGTERM', async () => {
  console.log('\n⚠️  Received SIGTERM signal...');
  try {
    await db.disconnect();
    console.log('✅ Database connection closed');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
});

// Start the server
startServer();

module.exports = app;
