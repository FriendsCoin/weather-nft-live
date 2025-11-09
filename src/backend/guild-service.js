#!/usr/bin/env node

/**
 * Guild Management Service for WeatherNFT
 * Handles guild creation, membership, algorithm rentals, and revenue sharing
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.GUILD_SERVICE_PORT || 3010;

app.use(cors());
app.use(express.json());

// In-memory storage (replace with MongoDB in production)
const guilds = new Map();
const memberships = new Map();
const algorithmRentals = new Map();
const revenueShares = new Map();

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
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT Guild Service',
    guilds_count: guilds.size,
    total_members: memberships.size,
    active_rentals: algorithmRentals.size,
    timestamp: new Date().toISOString()
  });
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
  const rentingGuilds = Array.from(algorithmRentals.values())
    .filter(rental => rental.algorithmId === algorithmId && rental.status === 'active')
    .map(rental => guilds.get(rental.guildId))
    .filter(Boolean);

  res.json({
    success: true,
    data: {
      ...algorithm,
      renting_guilds_count: rentingGuilds.length,
      renting_guilds: rentingGuilds.slice(0, 5) // Top 5
    }
  });
});

/**
 * Create a new guild
 * POST /api/guilds/create
 */
app.post('/api/guilds/create', (req, res) => {
  try {
    const { name, description, founder, logo, algorithms } = req.body;

    if (!name || !founder) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, founder'
      });
    }

    const guildId = `guild_${Date.now()}_${Math.random().toString(36).substring(7)}`;

    const guild = {
      id: guildId,
      name: name,
      description: description || '',
      founder: founder, // Wallet address
      logo: logo || null,
      members: [founder], // Founder is first member
      rentedAlgorithms: algorithms || [],
      totalRevenue: 0,
      totalCaptures: 0,
      createdAt: Date.now(),
      status: 'active'
    };

    guilds.set(guildId, guild);

    // Add founder membership
    const membershipId = `${guildId}_${founder}`;
    memberships.set(membershipId, {
      guildId: guildId,
      userAddress: founder,
      role: 'founder',
      joinedAt: Date.now(),
      captures: 0,
      revenue: 0
    });

    console.log(`✅ Guild created: ${name} (${guildId})`);

    res.json({
      success: true,
      message: 'Guild created successfully',
      data: guild
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
app.get('/api/guilds', (req, res) => {
  const guildList = Array.from(guilds.values())
    .map(guild => ({
      ...guild,
      memberCount: guild.members.length,
      algorithmCount: guild.rentedAlgorithms.length
    }))
    .sort((a, b) => b.totalRevenue - a.totalRevenue);

  res.json({
    success: true,
    count: guildList.length,
    data: guildList
  });
});

/**
 * Get guild details
 * GET /api/guilds/:guildId
 */
app.get('/api/guilds/:guildId', (req, res) => {
  const { guildId } = req.params;
  const guild = guilds.get(guildId);

  if (!guild) {
    return res.status(404).json({
      success: false,
      error: 'Guild not found'
    });
  }

  // Get member details
  const memberDetails = guild.members.map(address => {
    const membershipId = `${guildId}_${address}`;
    return memberships.get(membershipId);
  }).filter(Boolean);

  // Get rented algorithms details
  const rentedAlgorithmsDetails = guild.rentedAlgorithms.map(algId => {
    const rental = Array.from(algorithmRentals.values())
      .find(r => r.guildId === guildId && r.algorithmId === algId);
    return {
      ...AI_ALGORITHMS[algId],
      rental: rental
    };
  }).filter(Boolean);

  res.json({
    success: true,
    data: {
      ...guild,
      members: memberDetails,
      algorithms: rentedAlgorithmsDetails
    }
  });
});

/**
 * Join a guild
 * POST /api/guilds/:guildId/join
 */
app.post('/api/guilds/:guildId/join', (req, res) => {
  try {
    const { guildId } = req.params;
    const { userAddress } = req.body;

    if (!userAddress) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: userAddress'
      });
    }

    const guild = guilds.get(guildId);

    if (!guild) {
      return res.status(404).json({
        success: false,
        error: 'Guild not found'
      });
    }

    // Check if already a member
    if (guild.members.includes(userAddress)) {
      return res.status(400).json({
        success: false,
        error: 'Already a member of this guild'
      });
    }

    // Add member
    guild.members.push(userAddress);
    guilds.set(guildId, guild);

    // Create membership record
    const membershipId = `${guildId}_${userAddress}`;
    memberships.set(membershipId, {
      guildId: guildId,
      userAddress: userAddress,
      role: 'member',
      joinedAt: Date.now(),
      captures: 0,
      revenue: 0
    });

    console.log(`✅ ${userAddress} joined guild ${guild.name}`);

    res.json({
      success: true,
      message: 'Joined guild successfully',
      data: {
        guild: guild,
        membership: memberships.get(membershipId)
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
app.post('/api/guilds/:guildId/rent-algorithm', (req, res) => {
  try {
    const { guildId } = req.params;
    const { algorithmId, txHash } = req.body;

    if (!algorithmId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: algorithmId'
      });
    }

    const guild = guilds.get(guildId);
    const algorithm = AI_ALGORITHMS[algorithmId];

    if (!guild) {
      return res.status(404).json({ success: false, error: 'Guild not found' });
    }

    if (!algorithm) {
      return res.status(404).json({ success: false, error: 'Algorithm not found' });
    }

    // Check if already renting
    if (guild.rentedAlgorithms.includes(algorithmId)) {
      return res.status(400).json({
        success: false,
        error: 'Already renting this algorithm'
      });
    }

    // Create rental record
    const rentalId = `rental_${Date.now()}`;
    const rental = {
      id: rentalId,
      guildId: guildId,
      algorithmId: algorithmId,
      startDate: Date.now(),
      endDate: Date.now() + (30 * 24 * 60 * 60 * 1000), // 30 days
      monthlyPrice: algorithm.monthlyPrice,
      txHash: txHash || null,
      status: 'active'
    };

    algorithmRentals.set(rentalId, rental);

    // Update guild
    guild.rentedAlgorithms.push(algorithmId);
    guilds.set(guildId, guild);

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
app.post('/api/guilds/capture-event', (req, res) => {
  try {
    const { guildId, userAddress, algorithmId, eventId, capturePrice } = req.body;

    if (!guildId || !userAddress || !capturePrice) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }

    const guild = guilds.get(guildId);
    if (!guild) {
      return res.status(404).json({ success: false, error: 'Guild not found' });
    }

    const membershipId = `${guildId}_${userAddress}`;
    const membership = memberships.get(membershipId);

    if (!membership) {
      return res.status(404).json({ success: false, error: 'Not a guild member' });
    }

    // Calculate revenue share (15% to guild)
    const guildShare = capturePrice * 0.15;
    const userShare = capturePrice * 0.85;

    // Update guild stats
    guild.totalRevenue += guildShare;
    guild.totalCaptures += 1;
    guilds.set(guildId, guild);

    // Update member stats
    membership.captures += 1;
    membership.revenue += userShare;
    memberships.set(membershipId, membership);

    // Record revenue share
    const shareId = `share_${Date.now()}`;
    revenueShares.set(shareId, {
      id: shareId,
      guildId: guildId,
      userAddress: userAddress,
      algorithmId: algorithmId,
      eventId: eventId,
      capturePrice: capturePrice,
      guildShare: guildShare,
      userShare: userShare,
      timestamp: Date.now()
    });

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
app.get('/api/user/:userAddress/guilds', (req, res) => {
  const { userAddress } = req.params;

  const userMemberships = Array.from(memberships.values())
    .filter(m => m.userAddress === userAddress)
    .map(m => ({
      ...m,
      guild: guilds.get(m.guildId)
    }))
    .filter(m => m.guild);

  res.json({
    success: true,
    count: userMemberships.length,
    data: userMemberships
  });
});

/**
 * Get guild revenue history
 * GET /api/guilds/:guildId/revenue
 */
app.get('/api/guilds/:guildId/revenue', (req, res) => {
  const { guildId } = req.params;

  const guildRevenue = Array.from(revenueShares.values())
    .filter(share => share.guildId === guildId)
    .sort((a, b) => b.timestamp - a.timestamp);

  const totalRevenue = guildRevenue.reduce((sum, share) => sum + share.guildShare, 0);

  res.json({
    success: true,
    totalRevenue: totalRevenue,
    transactionCount: guildRevenue.length,
    data: guildRevenue
  });
});

/**
 * Get guild leaderboard
 * GET /api/leaderboard
 */
app.get('/api/leaderboard', (req, res) => {
  const leaderboard = Array.from(guilds.values())
    .map(guild => ({
      id: guild.id,
      name: guild.name,
      totalRevenue: guild.totalRevenue,
      totalCaptures: guild.totalCaptures,
      memberCount: guild.members.length,
      algorithmCount: guild.rentedAlgorithms.length
    }))
    .sort((a, b) => b.totalRevenue - a.totalRevenue)
    .slice(0, 100); // Top 100

  res.json({
    success: true,
    count: leaderboard.length,
    data: leaderboard
  });
});

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('🏛️  WeatherNFT Guild Management Service');
  console.log('=' .repeat(50));
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
});

module.exports = app;
