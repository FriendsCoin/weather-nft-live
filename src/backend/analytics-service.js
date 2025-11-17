#!/usr/bin/env node

/**
 * Analytics Dashboard API for WeatherNFT
 * Provides comprehensive statistics and metrics for the platform
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.ANALYTICS_PORT || 3011;

app.use(cors());
app.use(express.json());

// Service URLs
const SERVICES = {
  nft: process.env.NFT_SERVICE_URL || 'http://localhost:3009',
  guild: process.env.GUILD_SERVICE_URL || 'http://localhost:3010'
};

// In-memory analytics data (will be replaced with MongoDB)
const analyticsData = {
  totalNFTsCreated: 0,
  totalRevenue: 0,
  totalCaptures: 0,
  eventsByType: {},
  eventsByRarity: {},
  eventsByLocation: {},
  topGuilds: [],
  recentActivity: [],
  dailyStats: [],
  algorithmUsage: {}
};

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT Analytics Service',
    timestamp: new Date().toISOString()
  });
});

/**
 * Get platform overview statistics
 * GET /api/analytics/overview
 */
app.get('/api/analytics/overview', async (req, res) => {
  try {
    // Fetch data from other services
    const [nftData, guildData] = await Promise.all([
      fetchNFTStats(),
      fetchGuildStats()
    ]);

    const overview = {
      totalNFTs: nftData.total,
      totalGuilds: guildData.total,
      totalRevenue: calculateTotalRevenue(guildData.guilds),
      totalMembers: calculateTotalMembers(guildData.guilds),
      activeAlgorithms: countActiveAlgorithms(guildData.guilds),
      averageNFTPrice: calculateAveragePrice(nftData.nfts),
      topRarity: getMostCommonRarity(nftData.nfts),
      platformGrowth: calculateGrowthRate()
    };

    res.json({
      success: true,
      data: overview,
      timestamp: Date.now()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get NFT statistics
 * GET /api/analytics/nfts
 */
app.get('/api/analytics/nfts', async (req, res) => {
  try {
    const nftData = await fetchNFTStats();

    const stats = {
      total: nftData.total,
      byRarity: groupByRarity(nftData.nfts),
      byStatus: groupByStatus(nftData.nfts),
      recentlyCreated: nftData.nfts.slice(0, 10),
      totalValue: calculateTotalValue(nftData.nfts),
      averageCreationTime: calculateAverageTime(nftData.nfts)
    };

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Guild statistics
 * GET /api/analytics/guilds
 */
app.get('/api/analytics/guilds', async (req, res) => {
  try {
    const guildData = await fetchGuildStats();

    const stats = {
      total: guildData.total,
      topByRevenue: guildData.guilds
        .sort((a, b) => b.totalRevenue - a.totalRevenue)
        .slice(0, 10),
      topByMembers: guildData.guilds
        .sort((a, b) => b.members.length - a.members.length)
        .slice(0, 10),
      topByCaptures: guildData.guilds
        .sort((a, b) => b.totalCaptures - a.totalCaptures)
        .slice(0, 10),
      algorithmDistribution: analyzeAlgorithmDistribution(guildData.guilds),
      membershipGrowth: calculateMembershipGrowth(guildData.guilds)
    };

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Event statistics
 * GET /api/analytics/events
 */
app.get('/api/analytics/events', (req, res) => {
  try {
    const stats = {
      totalEvents: analyticsData.totalCaptures,
      byType: analyticsData.eventsByType,
      byRarity: analyticsData.eventsByRarity,
      byLocation: analyticsData.eventsByLocation,
      recentEvents: analyticsData.recentActivity.slice(0, 20),
      averageValue: analyticsData.totalRevenue / (analyticsData.totalCaptures || 1)
    };

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Algorithm usage statistics
 * GET /api/analytics/algorithms
 */
app.get('/api/analytics/algorithms', async (req, res) => {
  try {
    const guildData = await fetchGuildStats();

    const algorithmStats = {
      'storm-hunter': {
        name: 'Storm Hunter',
        rentals: 0,
        revenue: 0,
        captures: 0,
        avgAccuracy: 97.8
      },
      'aurora-predictor': {
        name: 'Aurora Predictor',
        rentals: 0,
        revenue: 0,
        captures: 0,
        avgAccuracy: 89.3
      },
      'micro-climate': {
        name: 'Micro Climate',
        rentals: 0,
        revenue: 0,
        captures: 0,
        avgAccuracy: 91.5
      },
      'extreme-weather': {
        name: 'Extreme Weather',
        rentals: 0,
        revenue: 0,
        captures: 0,
        avgAccuracy: 96.1
      },
      'temperature-anomaly': {
        name: 'Temperature Anomaly',
        rentals: 0,
        revenue: 0,
        captures: 0,
        avgAccuracy: 94.2
      }
    };

    // Count algorithm usage
    guildData.guilds.forEach(guild => {
      guild.rentedAlgorithms.forEach(algId => {
        if (algorithmStats[algId]) {
          algorithmStats[algId].rentals++;
          algorithmStats[algId].captures += guild.totalCaptures;
          algorithmStats[algId].revenue += guild.totalRevenue;
        }
      });
    });

    res.json({
      success: true,
      data: Object.values(algorithmStats).sort((a, b) => b.rentals - a.rentals)
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Time-based statistics (daily/weekly/monthly)
 * GET /api/analytics/timeline
 */
app.get('/api/analytics/timeline', (req, res) => {
  try {
    const { period = 'daily', days = 7 } = req.query;

    const timeline = generateTimeline(period, parseInt(days));

    res.json({
      success: true,
      data: {
        period: period,
        days: parseInt(days),
        data: timeline
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get User statistics
 * GET /api/analytics/users/:address
 */
app.get('/api/analytics/users/:address', async (req, res) => {
  try {
    const { address } = req.params;

    const guildData = await fetchGuildStats();
    const nftData = await fetchNFTStats();

    // Find user's guilds
    const userGuilds = [];
    guildData.guilds.forEach(guild => {
      if (guild.members.includes(address)) {
        userGuilds.push(guild);
      }
    });

    // Find user's NFTs
    const userNFTs = nftData.nfts.filter(nft => nft.owner === address);

    const stats = {
      address: address,
      guilds: {
        total: userGuilds.length,
        founded: userGuilds.filter(g => g.founder === address).length,
        totalRevenue: userGuilds.reduce((sum, g) => sum + g.totalRevenue, 0)
      },
      nfts: {
        total: userNFTs.length,
        byRarity: groupByRarity(userNFTs),
        totalValue: calculateTotalValue(userNFTs)
      },
      activity: {
        totalCaptures: calculateUserCaptures(address, guildData.guilds),
        totalEarned: calculateUserEarnings(address, guildData.guilds),
        joinDate: findEarliestJoinDate(address, guildData.guilds)
      }
    };

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Leaderboards
 * GET /api/analytics/leaderboard
 */
app.get('/api/analytics/leaderboard', async (req, res) => {
  try {
    const { type = 'revenue', limit = 10 } = req.query;

    const guildData = await fetchGuildStats();

    let leaderboard = [];

    switch (type) {
      case 'revenue':
        leaderboard = guildData.guilds
          .sort((a, b) => b.totalRevenue - a.totalRevenue)
          .slice(0, parseInt(limit));
        break;
      case 'captures':
        leaderboard = guildData.guilds
          .sort((a, b) => b.totalCaptures - a.totalCaptures)
          .slice(0, parseInt(limit));
        break;
      case 'members':
        leaderboard = guildData.guilds
          .sort((a, b) => b.members.length - a.members.length)
          .slice(0, parseInt(limit));
        break;
      default:
        leaderboard = guildData.guilds.slice(0, parseInt(limit));
    }

    res.json({
      success: true,
      data: {
        type: type,
        limit: parseInt(limit),
        leaderboard: leaderboard.map((guild, index) => ({
          rank: index + 1,
          guildId: guild.id,
          name: guild.name,
          value: type === 'revenue' ? guild.totalRevenue :
                 type === 'captures' ? guild.totalCaptures :
                 guild.members.length,
          members: guild.members.length
        }))
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Record an event (for analytics tracking)
 * POST /api/analytics/track
 */
app.post('/api/analytics/track', (req, res) => {
  try {
    const { event, data } = req.body;

    // Track event
    const activity = {
      event: event,
      data: data,
      timestamp: Date.now()
    };

    analyticsData.recentActivity.unshift(activity);

    // Keep only last 100 activities
    if (analyticsData.recentActivity.length > 100) {
      analyticsData.recentActivity = analyticsData.recentActivity.slice(0, 100);
    }

    // Update counters based on event type
    switch (event) {
      case 'nft_created':
        analyticsData.totalNFTsCreated++;
        updateEventStats(data);
        break;
      case 'capture':
        analyticsData.totalCaptures++;
        analyticsData.totalRevenue += data.price || 0;
        break;
    }

    res.json({
      success: true,
      message: 'Event tracked'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Helper functions

async function fetchNFTStats() {
  try {
    const response = await axios.get(`${SERVICES.nft}/api/nfts`);
    return {
      total: response.data.count || 0,
      nfts: response.data.data || []
    };
  } catch (error) {
    return { total: 0, nfts: [] };
  }
}

async function fetchGuildStats() {
  try {
    const response = await axios.get(`${SERVICES.guild}/api/guilds`);
    return {
      total: response.data.count || 0,
      guilds: response.data.data || []
    };
  } catch (error) {
    return { total: 0, guilds: [] };
  }
}

function groupByRarity(nfts) {
  const grouped = {};
  nfts.forEach(nft => {
    const rarity = nft.metadata?.properties?.event?.rarity || 'common';
    grouped[rarity] = (grouped[rarity] || 0) + 1;
  });
  return grouped;
}

function groupByStatus(nfts) {
  const grouped = {};
  nfts.forEach(nft => {
    grouped[nft.status] = (grouped[nft.status] || 0) + 1;
  });
  return grouped;
}

function calculateTotalValue(nfts) {
  // Estimate value based on rarity multipliers
  const rarityMultipliers = {
    common: 1,
    uncommon: 2,
    rare: 5,
    epic: 10,
    legendary: 30
  };

  return nfts.reduce((sum, nft) => {
    const rarity = nft.metadata?.properties?.event?.rarity || 'common';
    return sum + (rarityMultipliers[rarity] * 0.5); // Base price 0.5 XTZ
  }, 0);
}

function calculateAverageTime(nfts) {
  if (nfts.length === 0) return 0;
  const times = nfts.map(nft => nft.createdAt || Date.now());
  return times.reduce((sum, time) => sum + time, 0) / times.length;
}

function calculateTotalRevenue(guilds) {
  return guilds.reduce((sum, guild) => sum + (guild.totalRevenue || 0), 0);
}

function calculateTotalMembers(guilds) {
  const uniqueMembers = new Set();
  guilds.forEach(guild => {
    guild.members.forEach(member => uniqueMembers.add(member));
  });
  return uniqueMembers.size;
}

function countActiveAlgorithms(guilds) {
  const algorithms = new Set();
  guilds.forEach(guild => {
    guild.rentedAlgorithms.forEach(alg => algorithms.add(alg));
  });
  return algorithms.size;
}

function calculateAveragePrice(nfts) {
  if (nfts.length === 0) return 0;
  return calculateTotalValue(nfts) / nfts.length;
}

function getMostCommonRarity(nfts) {
  const rarities = groupByRarity(nfts);
  let maxRarity = 'common';
  let maxCount = 0;

  Object.entries(rarities).forEach(([rarity, count]) => {
    if (count > maxCount) {
      maxCount = count;
      maxRarity = rarity;
    }
  });

  return maxRarity;
}

function calculateGrowthRate() {
  // Simulate growth rate (would be real with MongoDB)
  return {
    daily: Math.random() * 10,
    weekly: Math.random() * 20,
    monthly: Math.random() * 50
  };
}

function analyzeAlgorithmDistribution(guilds) {
  const distribution = {};
  guilds.forEach(guild => {
    guild.rentedAlgorithms.forEach(alg => {
      distribution[alg] = (distribution[alg] || 0) + 1;
    });
  });
  return distribution;
}

function calculateMembershipGrowth(guilds) {
  // Simplified - would be more sophisticated with MongoDB
  return {
    new_members_today: Math.floor(Math.random() * 10),
    new_members_week: Math.floor(Math.random() * 50),
    average_guild_size: guilds.length > 0
      ? guilds.reduce((sum, g) => sum + g.members.length, 0) / guilds.length
      : 0
  };
}

function generateTimeline(period, days) {
  const data = [];
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now - (i * dayMs));
    data.push({
      date: date.toISOString().split('T')[0],
      nfts_created: Math.floor(Math.random() * 20),
      captures: Math.floor(Math.random() * 50),
      revenue: (Math.random() * 100).toFixed(2),
      new_guilds: Math.floor(Math.random() * 5),
      new_members: Math.floor(Math.random() * 30)
    });
  }

  return data;
}

function calculateUserCaptures(address, guilds) {
  // Would query actual membership data with MongoDB
  return Math.floor(Math.random() * 20);
}

function calculateUserEarnings(address, guilds) {
  // Would calculate from actual transaction history
  return (Math.random() * 100).toFixed(2);
}

function findEarliestJoinDate(address, guilds) {
  // Would query membership timestamps
  return Date.now() - (Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000);
}

function updateEventStats(data) {
  // Update event type stats
  const eventType = data.eventType || 'unknown';
  analyticsData.eventsByType[eventType] = (analyticsData.eventsByType[eventType] || 0) + 1;

  // Update rarity stats
  const rarity = data.rarity || 'common';
  analyticsData.eventsByRarity[rarity] = (analyticsData.eventsByRarity[rarity] || 0) + 1;

  // Update location stats
  const location = data.location || 'unknown';
  analyticsData.eventsByLocation[location] = (analyticsData.eventsByLocation[location] || 0) + 1;
}

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('📊 WeatherNFT Analytics Dashboard');
  console.log('=' .repeat(50));
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log('');
  console.log('📈 Endpoints:');
  console.log('   • GET  /health                      - Health check');
  console.log('   • GET  /api/analytics/overview      - Platform overview');
  console.log('   • GET  /api/analytics/nfts          - NFT statistics');
  console.log('   • GET  /api/analytics/guilds        - Guild statistics');
  console.log('   • GET  /api/analytics/events        - Event statistics');
  console.log('   • GET  /api/analytics/algorithms    - Algorithm usage');
  console.log('   • GET  /api/analytics/timeline      - Time-based stats');
  console.log('   • GET  /api/analytics/users/:addr   - User statistics');
  console.log('   • GET  /api/analytics/leaderboard   - Leaderboards');
  console.log('   • POST /api/analytics/track         - Track events');
  console.log('');
});

module.exports = app;
