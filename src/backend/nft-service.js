#!/usr/bin/env node

/**
 * NFT Service for WeatherNFT
 * Coordinates NFT creation: AI art generation -> IPFS upload -> Blockchain minting
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const IPFSService = require('./ipfs-service');
const AIArtGenerator = require('./ai-art-generator');
const DatabaseService = require('./database');
const { NFT } = require('./models');
const { authenticateToken } = require('./middleware/auth');
const {
  securityHeaders,
  generalLimiter,
  createLimiter,
  expensiveLimiter,
  corsOptions
} = require('./middleware/security');
const { requestLogger, errorLogger } = require('./middleware/logger');

const app = express();
const PORT = process.env.NFT_SERVICE_PORT || 3009;

// Configure multer for memory storage
const upload = multer({ storage: multer.memoryStorage() });

// Security middleware
app.use(securityHeaders());
app.use(cors(corsOptions()));
app.use(express.json({ limit: '50mb' })); // Increase limit for base64 images
app.use(requestLogger);
app.use(generalLimiter);

// Initialize services
const ipfsService = new IPFSService({
  provider: process.env.IPFS_PROVIDER || 'pinata'
});

const artGenerator = new AIArtGenerator({
  sdApiUrl: process.env.SD_AI_URL,
  useRealSD: process.env.USE_REAL_AI === 'true'
});

// Initialize database
const db = new DatabaseService();

// Health check
app.get('/health', async (req, res) => {
  try {
    const isDbConnected = await db.healthCheck();
    const nftCount = await NFT.countDocuments();
    const pendingMints = await NFT.countDocuments({ status: 'pending_mint' });

    res.json({
      status: 'OK',
      service: 'WeatherNFT NFT Service',
      database: isDbConnected ? 'connected' : 'disconnected',
      ipfs_provider: ipfsService.config.provider,
      ai_art_enabled: artGenerator.config.useRealSD,
      stats: {
        total_nfts: nftCount,
        pending_mints: pendingMints
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

// Test IPFS connection
app.get('/api/ipfs/test', async (req, res) => {
  try {
    const connected = await ipfsService.testConnection();
    res.json({
      success: connected,
      provider: ipfsService.config.provider,
      message: connected ? 'IPFS connection successful' : 'IPFS connection failed'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Generate AI art from weather data
 * POST /api/art/generate
 * Rate limited: 10 AI generations per hour
 */
app.post('/api/art/generate', expensiveLimiter, async (req, res) => {
  try {
    const { weatherData, eventData, location, rarity } = req.body;

    if (!weatherData || !eventData) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: weatherData, eventData'
      });
    }

    console.log(`🎨 Generating AI art for ${eventData.type}...`);

    const imageBuffer = await artGenerator.generateArt({
      weatherData,
      eventData,
      location: location || { city: 'Unknown', country: 'Unknown', lat: 0, lng: 0 },
      rarity: rarity || 'common'
    });

    // Convert buffer to base64
    const imageBase64 = imageBuffer.toString('base64');

    res.json({
      success: true,
      message: 'AI art generated successfully',
      data: {
        imageBase64: imageBase64,
        format: 'image/png',
        size: imageBuffer.length
      }
    });

  } catch (error) {
    console.error('❌ Art generation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Create complete NFT with AI art generation (PROTECTED)
 * POST /api/nft/create-with-art
 * Generates art automatically from weather data
 * Rate limited: 10 AI generations per hour
 */
app.post('/api/nft/create-with-art', authenticateToken, expensiveLimiter, async (req, res) => {
  try {
    const {
      eventId,
      weatherData,
      eventData,
      location,
      rarity,
      algorithm
    } = req.body;

    // Get owner from authenticated user
    const owner = req.user.walletAddress;

    if (!eventId || !weatherData || !eventData) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: eventId, weatherData, eventData'
      });
    }

    console.log(`🎨 Creating NFT with AI art for event ${eventId}...`);

    // Step 1: Generate AI art
    console.log('🖼️  Generating AI art...');
    const imageBuffer = await artGenerator.generateArt({
      weatherData,
      eventData,
      location: location || { city: 'Unknown', country: 'Unknown', lat: 0, lng: 0 },
      rarity: rarity || 'common'
    });
    console.log(`✅ Art generated (${imageBuffer.length} bytes)`);

    // Step 2: Upload image to IPFS
    console.log('📤 Uploading image to IPFS...');
    const imageUpload = await ipfsService.uploadImage(
      imageBuffer,
      `weather-nft-${eventId}.png`
    );
    console.log(`✅ Image uploaded: ${imageUpload.hash}`);

    // Step 3: Generate metadata
    console.log('📝 Generating NFT metadata...');
    const metadata = ipfsService.generateMetadata({
      name: `WeatherNFT #${eventId}`,
      description: null,
      imageHash: imageUpload.hash,
      weatherData,
      eventData,
      location: location || { city: 'Unknown', country: 'Unknown', lat: 0, lng: 0 },
      captureTimestamp: Date.now(),
      rarity: rarity || 'common',
      algorithm: algorithm || 'Unknown'
    });

    // Step 4: Upload metadata to IPFS
    console.log('📤 Uploading metadata to IPFS...');
    const metadataUpload = await ipfsService.uploadMetadata(metadata);
    console.log(`✅ Metadata uploaded: ${metadataUpload.hash}`);

    // Step 5: Save to database
    const nftData = {
      eventId: eventId,
      owner: owner || 'pending',
      imageHash: imageUpload.hash,
      imageUrl: imageUpload.url,
      metadataHash: metadataUpload.hash,
      metadataUrl: metadataUpload.url,
      metadata: metadata,
      status: 'pending_mint',
      rarity: rarity || 'common',
      algorithm: algorithm || 'Unknown',
      weatherData: weatherData,
      location: location || { city: 'Unknown', country: 'Unknown', lat: 0, lng: 0 }
    };

    const nft = await NFT.create(nftData);
    console.log(`✅ NFT ${eventId} saved to database and ready for minting`);

    res.json({
      success: true,
      message: 'NFT created with AI-generated art',
      data: {
        eventId: eventId,
        imageHash: imageUpload.hash,
        imageUrl: imageUpload.url,
        metadataHash: metadataUpload.hash,
        metadataUrl: metadataUpload.url,
        imagePreview: imageBuffer.toString('base64'),
        status: 'ready_to_mint'
      }
    });

  } catch (error) {
    console.error('❌ NFT creation with art failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Create complete NFT from weather event (PROTECTED)
 * POST /api/nft/create
 * Body: {
 *   eventId: string,
 *   weatherData: object,
 *   eventData: object,
 *   location: object,
 *   imageBase64: base64 string
 * }
 * Rate limited: 20 creations per hour
 */
app.post('/api/nft/create', authenticateToken, createLimiter, async (req, res) => {
  try {
    const {
      eventId,
      weatherData,
      eventData,
      location,
      imageBase64,
      rarity,
      algorithm
    } = req.body;

    // Get owner from authenticated user
    const owner = req.user.walletAddress;

    // Validate required fields
    if (!eventId || !weatherData || !eventData || !imageBase64) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: eventId, weatherData, eventData, imageBase64'
      });
    }

    console.log(`🎨 Creating NFT for event ${eventId}...`);

    // Convert base64 image to buffer
    const imageBuffer = Buffer.from(imageBase64, 'base64');

    // Step 1: Upload image to IPFS
    console.log('📤 Uploading image to IPFS...');
    const imageUpload = await ipfsService.uploadImage(
      imageBuffer,
      `weather-nft-${eventId}.png`
    );
    console.log(`✅ Image uploaded: ${imageUpload.hash}`);

    // Step 2: Generate metadata
    console.log('📝 Generating NFT metadata...');
    const metadata = ipfsService.generateMetadata({
      name: `WeatherNFT #${eventId}`,
      description: null, // Will auto-generate
      imageHash: imageUpload.hash,
      weatherData,
      eventData,
      location,
      captureTimestamp: Date.now(),
      rarity: rarity || 'common',
      algorithm: algorithm || 'Unknown'
    });

    // Step 3: Upload metadata to IPFS
    console.log('📤 Uploading metadata to IPFS...');
    const metadataUpload = await ipfsService.uploadMetadata(metadata);
    console.log(`✅ Metadata uploaded: ${metadataUpload.hash}`);

    // Step 4: Save to database
    const nftData = {
      eventId: eventId,
      owner: owner,
      imageHash: imageUpload.hash,
      imageUrl: imageUpload.url,
      metadataHash: metadataUpload.hash,
      metadataUrl: metadataUpload.url,
      metadata: metadata,
      status: 'pending_mint',
      rarity: rarity || 'common',
      algorithm: algorithm || 'Unknown',
      weatherData: weatherData,
      location: location || { city: 'Unknown', country: 'Unknown', lat: 0, lng: 0 }
    };

    const nft = await NFT.create(nftData);
    console.log(`✅ NFT ${eventId} saved to database and ready for minting`);

    res.json({
      success: true,
      message: 'NFT created and uploaded to IPFS',
      data: {
        eventId: eventId,
        imageHash: imageUpload.hash,
        imageUrl: imageUpload.url,
        metadataHash: metadataUpload.hash,
        metadataUrl: metadataUpload.url,
        ipfsGateway: imageUpload.pinataUrl || imageUpload.url,
        status: 'ready_to_mint'
      }
    });

  } catch (error) {
    console.error('❌ NFT creation failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Upload image file to IPFS
 * POST /api/ipfs/upload/image
 * Multipart form with 'image' file field
 */
app.post('/api/ipfs/upload/image', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No image file provided'
      });
    }

    console.log(`📤 Uploading image: ${req.file.originalname}`);

    const result = await ipfsService.uploadImage(
      req.file.buffer,
      req.file.originalname
    );

    res.json({
      success: true,
      message: 'Image uploaded to IPFS',
      data: result
    });

  } catch (error) {
    console.error('❌ Image upload failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Upload metadata to IPFS
 * POST /api/ipfs/upload/metadata
 * Body: { metadata: object }
 */
app.post('/api/ipfs/upload/metadata', async (req, res) => {
  try {
    const { metadata } = req.body;

    if (!metadata) {
      return res.status(400).json({
        success: false,
        error: 'No metadata provided'
      });
    }

    console.log('📤 Uploading metadata to IPFS...');

    const result = await ipfsService.uploadMetadata(metadata);

    res.json({
      success: true,
      message: 'Metadata uploaded to IPFS',
      data: result
    });

  } catch (error) {
    console.error('❌ Metadata upload failed:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get NFT by event ID
 * GET /api/nft/:eventId
 */
app.get('/api/nft/:eventId', async (req, res) => {
  try {
    const { eventId } = req.params;

    const nft = await NFT.findOne({ eventId }).lean();

    if (!nft) {
      return res.status(404).json({
        success: false,
        error: 'NFT not found'
      });
    }

    res.json({
      success: true,
      data: nft
    });
  } catch (error) {
    console.error('Error fetching NFT:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get all NFTs with filtering and pagination
 * GET /api/nfts
 */
app.get('/api/nfts', async (req, res) => {
  try {
    const {
      status,
      owner,
      rarity,
      algorithm,
      limit = 50,
      offset = 0,
      sortBy = 'createdAt',
      sortOrder = 'desc'
    } = req.query;

    // Build query
    const query = {};
    if (status) query.status = status;
    if (owner) query.owner = owner;
    if (rarity) query.rarity = rarity;
    if (algorithm) query.algorithm = algorithm;

    // Build sort
    const sort = {};
    sort[sortBy] = sortOrder === 'asc' ? 1 : -1;

    // Execute query with pagination
    const [nfts, total] = await Promise.all([
      NFT.find(query)
        .sort(sort)
        .skip(parseInt(offset))
        .limit(parseInt(limit))
        .lean(),
      NFT.countDocuments(query)
    ]);

    res.json({
      success: true,
      count: nfts.length,
      total: total,
      data: nfts,
      pagination: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: (parseInt(offset) + nfts.length) < total
      }
    });
  } catch (error) {
    console.error('Error fetching NFTs:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Update NFT status (after blockchain minting) (PROTECTED)
 * PUT /api/nft/:eventId/status
 * Body: { status: string, txHash?: string, tokenId?: string }
 */
app.put('/api/nft/:eventId/status', authenticateToken, async (req, res) => {
  try {
    const { eventId } = req.params;
    const { status, txHash, tokenId } = req.body;

    const updateData = { status };
    if (txHash) updateData.txHash = txHash;
    if (tokenId) updateData.tokenId = tokenId;

    const nft = await NFT.findOneAndUpdate(
      { eventId },
      { $set: updateData },
      { new: true }
    );

    if (!nft) {
      return res.status(404).json({
        success: false,
        error: 'NFT not found'
      });
    }

    console.log(`✅ NFT ${eventId} status updated to ${status}`);

    res.json({
      success: true,
      message: 'NFT status updated',
      data: nft
    });
  } catch (error) {
    console.error('Error updating NFT status:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Generate metadata preview
 * POST /api/metadata/preview
 */
app.post('/api/metadata/preview', (req, res) => {
  try {
    const {
      eventId,
      weatherData,
      eventData,
      location,
      rarity,
      algorithm
    } = req.body;

    const metadata = ipfsService.generateMetadata({
      name: `WeatherNFT #${eventId}`,
      description: null,
      imageHash: 'QmPreviewHash...',
      weatherData,
      eventData,
      location,
      captureTimestamp: Date.now(),
      rarity: rarity || 'common',
      algorithm: algorithm || 'Unknown'
    });

    res.json({
      success: true,
      data: metadata
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error logger middleware (must be after routes)
app.use(errorLogger);

// Start server with database connection
async function startServer() {
  try {
    console.log('');
    console.log('🎨 WeatherNFT NFT Service');
    console.log('='.repeat(50));

    // Connect to MongoDB
    console.log('📊 Connecting to MongoDB...');
    await db.connect();
    console.log('✅ MongoDB connected');

    // Initialize indexes
    console.log('📝 Initializing database indexes...');
    await NFT.createIndexes();
    console.log('✅ Database indexes initialized');

    // Start Express server
    app.listen(PORT, () => {
      console.log(`✅ Server running on http://localhost:${PORT}`);
      console.log(`📦 IPFS Provider: ${ipfsService.config.provider}`);
      console.log(`🤖 AI Art: ${artGenerator.config.useRealSD ? 'Enabled' : 'Mock Mode'}`);
      console.log('');
      console.log('📊 Endpoints:');
      console.log('   • GET  /health                    - Health check');
      console.log('   • GET  /api/ipfs/test             - Test IPFS connection');
      console.log('   • POST /api/nft/create-with-art   - Create NFT with AI art');
      console.log('   • POST /api/nft/create            - Create complete NFT');
      console.log('   • POST /api/art/generate          - Generate AI art only');
      console.log('   • POST /api/ipfs/upload/image     - Upload image to IPFS');
      console.log('   • POST /api/ipfs/upload/metadata  - Upload metadata to IPFS');
      console.log('   • GET  /api/nft/:eventId          - Get NFT by event ID');
      console.log('   • GET  /api/nfts                  - Get all NFTs (with filters)');
      console.log('   • PUT  /api/nft/:eventId/status   - Update NFT status');
      console.log('   • POST /api/metadata/preview      - Preview metadata');
      console.log('');
      console.log('✅ Ready to mint NFTs!');
      console.log('📦 MongoDB collection ready: NFT');
      console.log('');
    });

  } catch (error) {
    console.error('❌ Failed to start NFT service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⚠️  Shutting down NFT service...');
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
