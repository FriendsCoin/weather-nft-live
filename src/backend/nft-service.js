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

const app = express();
const PORT = process.env.NFT_SERVICE_PORT || 3009;

// Configure multer for memory storage
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors());
app.use(express.json());

// Initialize IPFS service
const ipfsService = new IPFSService({
  provider: process.env.IPFS_PROVIDER || 'pinata'
});

// In-memory storage for NFT minting queue
const mintingQueue = new Map();

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT NFT Service',
    ipfs_provider: ipfsService.config.provider,
    queue_size: mintingQueue.size,
    timestamp: new Date().toISOString()
  });
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
 * Create complete NFT from weather event
 * POST /api/nft/create
 * Body: {
 *   eventId: string,
 *   weatherData: object,
 *   eventData: object,
 *   location: object,
 *   imageBuffer: base64 string,
 *   owner: string (wallet address)
 * }
 */
app.post('/api/nft/create', async (req, res) => {
  try {
    const {
      eventId,
      weatherData,
      eventData,
      location,
      imageBase64,
      owner,
      rarity,
      algorithm
    } = req.body;

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

    // Step 4: Add to minting queue
    const nftData = {
      id: eventId,
      owner: owner,
      imageHash: imageUpload.hash,
      imageUrl: imageUpload.url,
      metadataHash: metadataUpload.hash,
      metadataUrl: metadataUpload.url,
      metadata: metadata,
      status: 'pending_mint',
      createdAt: Date.now()
    };

    mintingQueue.set(eventId, nftData);
    console.log(`✅ NFT ${eventId} ready for minting`);

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
 * Get NFT from minting queue
 * GET /api/nft/:eventId
 */
app.get('/api/nft/:eventId', (req, res) => {
  const { eventId } = req.params;

  const nft = mintingQueue.get(eventId);

  if (!nft) {
    return res.status(404).json({
      success: false,
      error: 'NFT not found in queue'
    });
  }

  res.json({
    success: true,
    data: nft
  });
});

/**
 * Get all NFTs in minting queue
 * GET /api/nfts
 */
app.get('/api/nfts', (req, res) => {
  const nfts = Array.from(mintingQueue.values());

  res.json({
    success: true,
    count: nfts.length,
    data: nfts
  });
});

/**
 * Update NFT status (after blockchain minting)
 * PUT /api/nft/:eventId/status
 * Body: { status: string, txHash?: string }
 */
app.put('/api/nft/:eventId/status', (req, res) => {
  const { eventId } = req.params;
  const { status, txHash, tokenId } = req.body;

  const nft = mintingQueue.get(eventId);

  if (!nft) {
    return res.status(404).json({
      success: false,
      error: 'NFT not found'
    });
  }

  nft.status = status;
  if (txHash) nft.txHash = txHash;
  if (tokenId) nft.tokenId = tokenId;
  nft.updatedAt = Date.now();

  mintingQueue.set(eventId, nft);

  res.json({
    success: true,
    message: 'NFT status updated',
    data: nft
  });
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

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('🎨 WeatherNFT NFT Service');
  console.log('=' .repeat(50));
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`📦 IPFS Provider: ${ipfsService.config.provider}`);
  console.log('');
  console.log('📊 Endpoints:');
  console.log('   • GET  /health                    - Health check');
  console.log('   • GET  /api/ipfs/test             - Test IPFS connection');
  console.log('   • POST /api/nft/create            - Create complete NFT');
  console.log('   • POST /api/ipfs/upload/image     - Upload image to IPFS');
  console.log('   • POST /api/ipfs/upload/metadata  - Upload metadata to IPFS');
  console.log('   • GET  /api/nft/:eventId          - Get NFT from queue');
  console.log('   • GET  /api/nfts                  - Get all NFTs');
  console.log('   • PUT  /api/nft/:eventId/status   - Update NFT status');
  console.log('   • POST /api/metadata/preview      - Preview metadata');
  console.log('');
});

module.exports = app;
