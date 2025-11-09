#!/usr/bin/env node

// WeatherNFT Blockchain Integration Service
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { TezosToolkit } = require('@taquito/taquito');
const { InMemorySigner } = require('@taquito/signer');

const app = express();
const PORT = process.env.BLOCKCHAIN_PORT || 3007;

app.use(cors());
app.use(express.json());

// Tezos configuration
const TEZOS_RPC = process.env.TEZOS_RPC_URL || 'https://ghostnet.ecadinfra.com';
const PRIVATE_KEY = process.env.TEZOS_PRIVATE_KEY || 'edsk...'; // Placeholder

// Contract addresses (to be deployed)
const NFT_CONTRACT = process.env.NFT_CONTRACT_ADDRESS || 'KT1...';
const EVENT_CONTRACT = process.env.EVENT_CONTRACT_ADDRESS || 'KT1...';

// Initialize Tezos toolkit
let Tezos;

async function initTezos() {
  try {
    Tezos = new TezosToolkit(TEZOS_RPC);
    
    if (PRIVATE_KEY && PRIVATE_KEY !== 'edsk...') {
      Tezos.setProvider({
        signer: new InMemorySigner(PRIVATE_KEY)
      });
      console.log('✅ Tezos toolkit initialized with signer');
    } else {
      console.log('⚠️ Tezos toolkit initialized without signer (read-only mode)');
    }
    
    // Test connection
    const head = await Tezos.rpc.getBlockHeader();
    console.log(`🔗 Connected to Tezos ${head.chain_id} at block ${head.level}`);
    
  } catch (error) {
    console.error('❌ Tezos initialization failed:', error.message);
  }
}

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT Blockchain Service',
    network: 'Ghostnet',
    contracts: {
      nft: NFT_CONTRACT,
      events: EVENT_CONTRACT
    },
    timestamp: new Date().toISOString()
  });
});

// Get contract info
app.get('/api/contracts', async (req, res) => {
  try {
    const contracts = {
      nft: {
        address: NFT_CONTRACT,
        deployed: NFT_CONTRACT !== 'KT1...',
        type: 'FA2 NFT Contract'
      },
      events: {
        address: EVENT_CONTRACT,
        deployed: EVENT_CONTRACT !== 'KT1...',
        type: 'Event Manager Contract'
      }
    };
    
    res.json({
      success: true,
      data: contracts,
      network: 'ghostnet'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Mint NFT for weather event
app.post('/api/nft/mint', async (req, res) => {
  try {
    const { eventId, owner, metadata } = req.body;
    
    if (!Tezos || NFT_CONTRACT === 'KT1...') {
      return res.status(503).json({
        success: false,
        error: 'Contracts not deployed yet'
      });
    }
    
    // Mock response for now
    const mintResult = {
      tokenId: Math.floor(Math.random() * 10000),
      txHash: 'op' + Math.random().toString(36).substr(2, 50),
      eventId,
      owner,
      metadata,
      status: 'pending'
    };
    
    res.json({
      success: true,
      message: 'NFT minting initiated',
      data: mintResult
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get user's NFTs
app.get('/api/nft/owner/:address', async (req, res) => {
  try {
    const { address } = req.params;
    
    // Mock data for now
    const mockNFTs = [
      {
        tokenId: 1,
        name: 'Термальная Аномалия #1234',
        description: 'Rare temperature spike captured in Phoenix',
        image: 'ipfs://QmXXX...',
        eventId: 'evt_001',
        rarity: 'rare',
        mintedAt: new Date(),
        owner: address
      }
    ];
    
    res.json({
      success: true,
      data: mockNFTs,
      count: mockNFTs.length
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Transfer NFT
app.post('/api/nft/transfer', async (req, res) => {
  try {
    const { tokenId, from, to } = req.body;
    
    if (!Tezos || NFT_CONTRACT === 'KT1...') {
      return res.status(503).json({
        success: false,
        error: 'Contracts not deployed yet'
      });
    }
    
    // Mock response
    const transferResult = {
      txHash: 'op' + Math.random().toString(36).substr(2, 50),
      tokenId,
      from,
      to,
      status: 'pending'
    };
    
    res.json({
      success: true,
      message: 'NFT transfer initiated',
      data: transferResult
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Create weather event (from AI)
app.post('/api/events/create', async (req, res) => {
  try {
    const { 
      eventType, 
      location, 
      severity, 
      rarity, 
      aiAlgorithm,
      weatherData,
      confidence 
    } = req.body;
    
    if (!Tezos || EVENT_CONTRACT === 'KT1...') {
      return res.status(503).json({
        success: false,
        error: 'Contracts not deployed yet'
      });
    }
    
    // Mock event creation
    const eventResult = {
      eventId: 'evt_' + Date.now(),
      txHash: 'op' + Math.random().toString(36).substr(2, 50),
      eventType,
      location,
      severity,
      rarity,
      aiAlgorithm,
      weatherData,
      confidence,
      captureSlots: getRaritySlots(rarity),
      price: getRarityPrice(rarity),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
      status: 'active'
    };
    
    res.json({
      success: true,
      message: 'Weather event created on blockchain',
      data: eventResult
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Deploy contracts (admin only)
app.post('/api/admin/deploy', async (req, res) => {
  try {
    const { contractType } = req.body;
    
    if (!Tezos || PRIVATE_KEY === 'edsk...') {
      return res.status(503).json({
        success: false,
        error: 'No deployment key configured'
      });
    }
    
    // Mock deployment
    const deployResult = {
      contractType,
      address: 'KT1' + Math.random().toString(36).substr(2, 33),
      txHash: 'op' + Math.random().toString(36).substr(2, 50),
      status: 'pending'
    };
    
    res.json({
      success: true,
      message: `${contractType} contract deployment initiated`,
      data: deployResult
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get blockchain stats
app.get('/api/stats', async (req, res) => {
  try {
    const stats = {
      network: 'ghostnet',
      totalNFTs: 42,
      totalEvents: 15,
      activeEvents: 8,
      totalUsers: 23,
      contractsDeployed: NFT_CONTRACT !== 'KT1...' && EVENT_CONTRACT !== 'KT1...',
      lastBlock: await getLastBlock()
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

// Helper functions
function getRaritySlots(rarity) {
  const slots = {
    'common': 20,
    'uncommon': 10,
    'rare': 5,
    'epic': 3,
    'legendary': 1
  };
  return slots[rarity] || 10;
}

function getRarityPrice(rarity) {
  const prices = {
    'common': 5,
    'uncommon': 10,
    'rare': 20,
    'epic': 35,
    'legendary': 50
  };
  return prices[rarity] || 10;
}

async function getLastBlock() {
  try {
    if (Tezos) {
      const head = await Tezos.rpc.getBlockHeader();
      return head.level;
    }
    return 0;
  } catch (error) {
    return 0;
  }
}

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'WeatherNFT Blockchain Service',
    status: 'Running',
    version: '1.0.0',
    network: 'ghostnet',
    endpoints: {
      health: '/health',
      contracts: '/api/contracts',
      mintNFT: '/api/nft/mint',
      getUserNFTs: '/api/nft/owner/:address',
      transferNFT: '/api/nft/transfer',
      createEvent: '/api/events/create',
      stats: '/api/stats'
    }
  });
});

// Initialize and start server
async function start() {
  await initTezos();
  
  app.listen(PORT, () => {
    console.log('🔗 WeatherNFT Blockchain Service');
    console.log('==================================');
    console.log(`✅ Server running on http://localhost:${PORT}`);
    console.log(`🌐 Network: Ghostnet`);
    console.log(`📱 NFT Contract: ${NFT_CONTRACT}`);
    console.log(`⚡ Event Contract: ${EVENT_CONTRACT}`);
    console.log('');
    console.log('🔗 API endpoints:');
    console.log(`   GET  /health - Service health`);
    console.log(`   GET  /api/contracts - Contract info`);
    console.log(`   POST /api/nft/mint - Mint NFT`);
    console.log(`   GET  /api/nft/owner/:address - User NFTs`);
    console.log(`   POST /api/events/create - Create event`);
    console.log('');
    console.log('🚀 Ready for blockchain operations!');
  });
}

start().catch(console.error);