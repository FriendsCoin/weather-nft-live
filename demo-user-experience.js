#!/usr/bin/env node

/**
 * WeatherNFT Complete User Experience Simulation
 * Demonstrates the entire workflow from weather detection to NFT minting
 */

require('dotenv').config();
const axios = require('axios');

// Configuration
const BASE_URL = 'http://localhost';
const PORTS = {
  ai: 3006,
  blockchain: 3007,
  admin: 3008,
  nft: 3009,
  guild: 3010
};

// Color output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  blue: '\x1b[34m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

const log = {
  header: (msg) => console.log(`\n${colors.bright}${colors.cyan}${'='.repeat(60)}${colors.reset}`),
  title: (msg) => console.log(`${colors.bright}${colors.blue}🌦️  ${msg}${colors.reset}`),
  step: (num, msg) => console.log(`\n${colors.bright}${colors.yellow}[STEP ${num}] ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  info: (msg) => console.log(`${colors.cyan}ℹ️  ${msg}${colors.reset}`),
  data: (msg) => console.log(`${colors.magenta}   ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  divider: () => console.log(`${colors.cyan}${'─'.repeat(60)}${colors.reset}`)
};

// Simulated user data
const DEMO_USER = {
  address: 'tz1DemoUser123ABC456DEF789GHI',
  name: 'Alice (Weather Hunter)'
};

// Simulated weather event
const DEMO_EVENT = {
  eventId: `evt_${Date.now()}`,
  weatherData: {
    temperature: 28,
    humidity: 85,
    pressure: 1002,
    windSpeed: 65,
    visibility: 5,
    conditions: 'stormy'
  },
  eventData: {
    id: `evt_${Date.now()}`,
    type: 'severe_thunderstorm',
    timestamp: Date.now(),
    severity: 'high',
    duration: 120
  },
  location: {
    city: 'Miami',
    country: 'USA',
    lat: 25.7617,
    lng: -80.1918
  },
  rarity: 'epic',
  algorithm: 'Storm Hunter'
};

// Helper function to make API calls
async function apiCall(service, endpoint, method = 'GET', data = null) {
  const url = `${BASE_URL}:${PORTS[service]}${endpoint}`;
  try {
    const config = {
      method,
      url,
      headers: { 'Content-Type': 'application/json' }
    };
    if (data) config.data = data;

    const response = await axios(config);
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.error || error.message
    };
  }
}

// Delay helper
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function simulateCompleteUserExperience() {
  log.header();
  log.title('WEATHERNFT COMPLETE USER EXPERIENCE SIMULATION');
  log.header();

  console.log(`\n${colors.bright}Simulating user journey: Weather Detection → NFT Creation → Guild Participation${colors.reset}\n`);

  // ============================================================
  // PHASE 1: System Health Check
  // ============================================================
  log.step(1, 'SYSTEM HEALTH CHECK');
  log.info('Checking all services...');

  const services = ['nft', 'guild'];
  let allHealthy = true;

  for (const service of services) {
    const result = await apiCall(service, '/health');
    if (result.success) {
      log.success(`${service.toUpperCase()} Service: ${result.data.status}`);
      if (result.data.ipfs_provider) {
        log.data(`IPFS Provider: ${result.data.ipfs_provider}`);
      }
      if (result.data.guilds_count !== undefined) {
        log.data(`Active Guilds: ${result.data.guilds_count}`);
      }
    } else {
      log.error(`${service.toUpperCase()} Service: OFFLINE`);
      allHealthy = false;
    }
  }

  if (!allHealthy) {
    log.error('Some services are offline. Please start all services with: npm run dev');
    process.exit(1);
  }

  await sleep(1000);

  // ============================================================
  // PHASE 2: Weather Event Detection
  // ============================================================
  log.step(2, 'WEATHER EVENT DETECTION');
  log.info('Simulating real-time weather monitoring...');

  console.log(`\n${colors.bright}${colors.yellow}📡 AI Algorithm: ${DEMO_EVENT.algorithm}${colors.reset}`);
  log.data(`Location: ${DEMO_EVENT.location.city}, ${DEMO_EVENT.location.country}`);
  log.data(`Event Type: ${DEMO_EVENT.eventData.type.toUpperCase()}`);
  log.data(`Temperature: ${DEMO_EVENT.weatherData.temperature}°C`);
  log.data(`Wind Speed: ${DEMO_EVENT.weatherData.windSpeed} km/h`);
  log.data(`Humidity: ${DEMO_EVENT.weatherData.humidity}%`);
  log.data(`Pressure: ${DEMO_EVENT.weatherData.pressure} hPa`);
  log.data(`Conditions: ${DEMO_EVENT.weatherData.conditions}`);
  log.data(`Rarity: ${DEMO_EVENT.rarity.toUpperCase()}`);

  log.success('Severe weather event detected!');
  log.info('Event is now available for capture...');

  await sleep(1500);

  // ============================================================
  // PHASE 3: User Creates/Joins Guild
  // ============================================================
  log.step(3, 'GUILD PARTICIPATION');
  log.info('User creates a weather hunting guild...');

  const guildData = {
    name: 'Elite Storm Chasers',
    description: 'Professional weather hunters tracking severe storms worldwide',
    founder: DEMO_USER.address,
    algorithms: ['storm-hunter']
  };

  const guildResult = await apiCall('guild', '/api/guilds/create', 'POST', guildData);

  if (guildResult.success) {
    const guild = guildResult.data.data;
    log.success(`Guild created: "${guild.name}"`);
    log.data(`Guild ID: ${guild.id}`);
    log.data(`Founder: ${DEMO_USER.name}`);
    log.data(`Members: ${guild.members.length}`);

    // Rent algorithm
    await sleep(1000);
    log.info('Renting AI algorithm for guild...');

    const rentalResult = await apiCall(
      'guild',
      `/api/guilds/${guild.id}/rent-algorithm`,
      'POST',
      {
        algorithmId: 'storm-hunter',
        txHash: `op${Date.now()}`
      }
    );

    if (rentalResult.success) {
      const rental = rentalResult.data.data;
      log.success('Algorithm rented successfully!');
      log.data(`Algorithm: ${rental.algorithm.name}`);
      log.data(`Monthly Cost: ${rental.algorithm.monthlyPrice} XTZ`);
      log.data(`Accuracy: ${rental.algorithm.accuracy}%`);
      log.data(`Specialization: ${rental.algorithm.specialization}`);
      log.info('Guild members now have priority access to storm events!');
    }

    DEMO_EVENT.guildId = guild.id;
    await sleep(1500);
  }

  // ============================================================
  // PHASE 4: AI Art Generation
  // ============================================================
  log.step(4, 'AI ART GENERATION');
  log.info('Generating unique NFT art from weather data...');

  const artResult = await apiCall('nft', '/api/art/generate', 'POST', {
    weatherData: DEMO_EVENT.weatherData,
    eventData: DEMO_EVENT.eventData,
    location: DEMO_EVENT.location,
    rarity: DEMO_EVENT.rarity
  });

  if (artResult.success) {
    const art = artResult.data.data;
    log.success('AI art generated!');
    log.data(`Format: ${art.format}`);
    log.data(`Size: ${(art.size / 1024).toFixed(2)} KB`);
    log.data(`Weather effects applied: Stormy conditions with lightning`);
    log.info('Preview: [Base64 image data available]');
  } else {
    log.error(`Art generation failed: ${artResult.error}`);
  }

  await sleep(1500);

  // ============================================================
  // PHASE 5: NFT Creation & IPFS Upload
  // ============================================================
  log.step(5, 'NFT CREATION & IPFS UPLOAD');
  log.info('Creating NFT with AI-generated art...');

  const nftResult = await apiCall('nft', '/api/nft/create-with-art', 'POST', {
    eventId: DEMO_EVENT.eventId,
    weatherData: DEMO_EVENT.weatherData,
    eventData: DEMO_EVENT.eventData,
    location: DEMO_EVENT.location,
    owner: DEMO_USER.address,
    rarity: DEMO_EVENT.rarity,
    algorithm: DEMO_EVENT.algorithm
  });

  if (nftResult.success) {
    const nft = nftResult.data.data;
    log.success('NFT created successfully!');
    log.divider();
    console.log(`${colors.bright}NFT Details:${colors.reset}`);
    log.data(`Event ID: ${nft.eventId}`);
    log.data(`Image Hash: ${nft.imageHash}`);
    log.data(`Metadata Hash: ${nft.metadataHash}`);
    log.data(`Image URL: ${nft.imageUrl}`);
    log.data(`Metadata URL: ${nft.metadataUrl}`);
    log.data(`Status: ${nft.status}`);
    log.divider();
    log.info('NFT is ready for blockchain minting!');

    DEMO_EVENT.nftData = nft;
    await sleep(2000);
  } else {
    log.error(`NFT creation failed: ${nftResult.error}`);
    log.info('Note: IPFS service may need configuration (Pinata API keys)');
  }

  // ============================================================
  // PHASE 6: Revenue Distribution
  // ============================================================
  log.step(6, 'CAPTURE & REVENUE DISTRIBUTION');

  const capturePrice = 15; // XTZ
  log.info(`User captures the weather event for ${capturePrice} XTZ...`);

  if (DEMO_EVENT.guildId) {
    const revenueResult = await apiCall('guild', '/api/guilds/capture-event', 'POST', {
      guildId: DEMO_EVENT.guildId,
      userAddress: DEMO_USER.address,
      algorithmId: 'storm-hunter',
      eventId: DEMO_EVENT.eventId,
      capturePrice: capturePrice
    });

    if (revenueResult.success) {
      const revenue = revenueResult.data.data;
      log.success('Revenue distributed!');
      log.divider();
      console.log(`${colors.bright}Revenue Breakdown:${colors.reset}`);
      log.data(`Total Capture Price: ${capturePrice} XTZ`);
      log.data(`Guild Share (15%): ${revenue.guildShare.toFixed(2)} XTZ`);
      log.data(`User Share (85%): ${revenue.userShare.toFixed(2)} XTZ`);
      log.divider();
      log.info(`Total Guild Revenue: ${revenue.totalGuildRevenue.toFixed(2)} XTZ`);
      log.info(`User Total Captures: ${revenue.memberCaptures}`);
    }
  }

  await sleep(1500);

  // ============================================================
  // PHASE 7: Guild Statistics & Leaderboard
  // ============================================================
  log.step(7, 'GUILD STATISTICS & LEADERBOARD');
  log.info('Fetching guild performance data...');

  const leaderboardResult = await apiCall('guild', '/api/leaderboard');

  if (leaderboardResult.success) {
    const leaderboard = leaderboardResult.data.data;
    log.success('Guild leaderboard retrieved!');
    log.divider();
    console.log(`${colors.bright}Top Guilds:${colors.reset}`);

    leaderboard.slice(0, 5).forEach((guild, index) => {
      console.log(`\n${colors.yellow}#${index + 1} ${guild.name}${colors.reset}`);
      log.data(`Revenue: ${guild.totalRevenue.toFixed(2)} XTZ`);
      log.data(`Captures: ${guild.totalCaptures}`);
      log.data(`Members: ${guild.memberCount}`);
      log.data(`Algorithms: ${guild.algorithmCount}`);
    });
    log.divider();
  }

  await sleep(1500);

  // ============================================================
  // PHASE 8: Final Summary
  // ============================================================
  log.step(8, 'USER JOURNEY SUMMARY');
  log.divider();

  console.log(`\n${colors.bright}${colors.green}Complete User Experience Simulation${colors.reset}\n`);

  console.log(`${colors.bright}What Happened:${colors.reset}`);
  console.log(`\n1. 🌩️  AI detected severe thunderstorm in ${DEMO_EVENT.location.city}`);
  console.log(`2. 🏛️  User created guild "${guildData.name}"`);
  console.log(`3. 🤖 Guild rented "${DEMO_EVENT.algorithm}" algorithm`);
  console.log(`4. 🎨 AI generated unique art from weather conditions`);
  if (nftResult.success) {
    console.log(`5. 📦 NFT uploaded to IPFS with metadata`);
    console.log(`6. 💎 NFT ready for blockchain minting`);
  } else {
    console.log(`5. ⚠️  NFT creation simulated (IPFS offline)`);
  }
  console.log(`7. 💰 Revenue distributed: ${(capturePrice * 0.15).toFixed(2)} XTZ to guild, ${(capturePrice * 0.85).toFixed(2)} XTZ to user`);
  console.log(`8. 🏆 Guild statistics updated on leaderboard\n`);

  console.log(`${colors.bright}User Benefits:${colors.reset}`);
  console.log(`✅ Unique, one-of-a-kind weather NFT`);
  console.log(`✅ AI-generated art based on real weather data`);
  console.log(`✅ Decentralized storage on IPFS`);
  console.log(`✅ Guild collaboration and revenue sharing`);
  console.log(`✅ Priority access to weather events`);
  console.log(`✅ Competitive leaderboard ranking\n`);

  if (nftResult.success) {
    console.log(`${colors.bright}${colors.cyan}Next Steps:${colors.reset}`);
    console.log(`1. View NFT on IPFS: ${DEMO_EVENT.nftData.imageUrl}`);
    console.log(`2. Mint NFT on Tezos blockchain`);
    console.log(`3. List NFT on marketplace`);
    console.log(`4. Track weather events in real-time\n`);
  }

  log.divider();
  log.success('Simulation complete!');
  log.header();
}

// Run simulation
if (require.main === module) {
  console.log(`\n${colors.bright}${colors.blue}Starting WeatherNFT User Experience Simulation...${colors.reset}\n`);
  console.log(`${colors.yellow}Make sure all services are running: npm run dev${colors.reset}\n`);

  setTimeout(() => {
    simulateCompleteUserExperience().catch(error => {
      log.error(`Simulation failed: ${error.message}`);
      console.error(error);
      process.exit(1);
    });
  }, 1000);
}

module.exports = { simulateCompleteUserExperience };
