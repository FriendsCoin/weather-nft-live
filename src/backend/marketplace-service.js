#!/usr/bin/env node

/**
 * WeatherNFT Marketplace Service
 * Advanced marketplace features for NFT trading
 *
 * Features:
 * - NFT listing/delisting
 * - Buy/sell functionality
 * - Offer/bid system
 * - Price history tracking
 * - Transaction management
 * - Advanced search and filtering
 * - Marketplace statistics
 *
 * Port: 3013
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const DatabaseService = require('./database');
const { Listing, Offer, MarketplaceTransaction } = require('./models');
const { authenticateToken, verifyWalletOwnership } = require('./middleware/auth');
const {
  securityHeaders,
  generalLimiter,
  createLimiter,
  corsOptions
} = require('./middleware/security');
const { requestLogger, errorLogger } = require('./middleware/logger');

const app = express();
const PORT = process.env.MARKETPLACE_PORT || 3013;

// Initialize database
const db = new DatabaseService();

// Security middleware
app.use(securityHeaders());
app.use(cors(corsOptions()));
app.use(express.json());
app.use(requestLogger);
app.use(generalLimiter);

// Service URLs
const SERVICES = {
  nft: `http://localhost:${process.env.NFT_SERVICE_PORT || 3009}`,
  guild: `http://localhost:${process.env.GUILD_SERVICE_PORT || 3010}`,
  analytics: `http://localhost:${process.env.ANALYTICS_PORT || 3011}`,
  websocket: `http://localhost:${process.env.WEBSOCKET_PORT || 8080}`
};

// Listing status
const LISTING_STATUS = {
  ACTIVE: 'active',
  SOLD: 'sold',
  CANCELLED: 'cancelled',
  EXPIRED: 'expired'
};

// Offer status
const OFFER_STATUS = {
  PENDING: 'pending',
  ACCEPTED: 'accepted',
  REJECTED: 'rejected',
  CANCELLED: 'cancelled',
  EXPIRED: 'expired'
};

// Transaction types
const TRANSACTION_TYPE = {
  DIRECT_SALE: 'direct_sale',
  OFFER_ACCEPTED: 'offer_accepted',
  AUCTION_WIN: 'auction_win'
};

// ============================================
// LISTING ENDPOINTS
// ============================================

/**
 * Create NFT listing (PROTECTED)
 * POST /api/marketplace/listings
 * Rate limited: 20 creations per hour
 */
app.post('/api/marketplace/listings', authenticateToken, createLimiter, async (req, res) => {
  try {
    const {
      nftId,
      price,
      currency = 'XTZ',
      duration = 30, // days
      auctionMode = false,
      minimumBid,
      buyNowPrice
    } = req.body;

    // Get seller from authenticated user
    const seller = req.user.walletAddress;

    // Validate required fields
    if (!nftId || !price) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: nftId, price'
      });
    }

    // Check if NFT is already listed in marketplace
    const existingListing = await Listing.findOne({
      nftId,
      status: LISTING_STATUS.ACTIVE
    });

    if (existingListing) {
      return res.status(400).json({
        success: false,
        error: 'NFT is already listed in marketplace'
      });
    }

    // Check if NFT exists and verify ownership
    try {
      const nftResponse = await axios.get(`${SERVICES.nft}/api/nfts/${nftId}`);
      const nft = nftResponse.data;

      if (!nft) {
        return res.status(404).json({
          success: false,
          error: 'NFT not found'
        });
      }

      // Verify seller owns the NFT (check owner field, not capturedBy)
      const nftOwner = nft.owner || nft.capturedBy;
      if (!nftOwner) {
        return res.status(400).json({
          success: false,
          error: 'NFT has no owner assigned'
        });
      }

      if (nftOwner !== seller) {
        return res.status(403).json({
          success: false,
          error: 'Only the NFT owner can list it',
          nftOwner: nftOwner,
          yourAddress: seller
        });
      }
    } catch (error) {
      if (error.response && error.response.status === 404) {
        return res.status(404).json({
          success: false,
          error: 'NFT not found'
        });
      }
      return res.status(500).json({
        success: false,
        error: 'Failed to verify NFT ownership',
        message: error.message
      });
    }

    const listingId = `listing_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + duration);

    const listingData = {
      listingId,
      nftId,
      seller,
      price: parseFloat(price),
      currency,
      auctionMode,
      minimumBid: auctionMode ? parseFloat(minimumBid || price) : null,
      buyNowPrice: auctionMode && buyNowPrice ? parseFloat(buyNowPrice) : null,
      currentBid: auctionMode ? 0 : null,
      highestBidder: null,
      status: LISTING_STATUS.ACTIVE,
      views: 0,
      favorites: 0,
      expiresAt
    };

    // Create listing in MongoDB
    const listing = await Listing.create(listingData);

    console.log(`✅ NFT listed: ${nftId} for ${price} ${currency}`);

    res.json({
      success: true,
      listing
    });

    // Broadcast listing event
    broadcastToWebSocket('marketplace_listing', 'new_listing', { listing });

  } catch (error) {
    console.error('Error creating listing:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create listing'
    });
  }
});

/**
 * Get all active listings
 * GET /api/marketplace/listings
 */
app.get('/api/marketplace/listings', async (req, res) => {
  try {
    const {
      status = LISTING_STATUS.ACTIVE,
      seller,
      minPrice,
      maxPrice,
      currency,
      auctionMode,
      sortBy = 'createdAt',
      sortOrder = 'desc',
      page = 1,
      limit = 20
    } = req.query;

    // Build MongoDB query
    const query = {};

    if (status) {
      query.status = status;
    }

    if (seller) {
      query.seller = seller;
    }

    if (minPrice || maxPrice) {
      query.price = {};
      if (minPrice) query.price.$gte = parseFloat(minPrice);
      if (maxPrice) query.price.$lte = parseFloat(maxPrice);
    }

    if (currency) {
      query.currency = currency;
    }

    if (auctionMode !== undefined) {
      query.auctionMode = auctionMode === 'true';
    }

    // Update expired listings
    const now = new Date();
    await Listing.updateMany(
      { status: LISTING_STATUS.ACTIVE, expiresAt: { $lt: now } },
      { $set: { status: LISTING_STATUS.EXPIRED } }
    );

    // Build sort object
    const sort = {};
    sort[sortBy] = sortOrder === 'asc' ? 1 : -1;

    // Execute query with pagination
    const pageNum = parseInt(page);
    const limitNum = parseInt(limit);
    const skip = (pageNum - 1) * limitNum;

    const [filteredListings, total] = await Promise.all([
      Listing.find(query).sort(sort).skip(skip).limit(limitNum).lean(),
      Listing.countDocuments(query)
    ]);

    res.json({
      success: true,
      data: filteredListings,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total,
        pages: Math.ceil(total / limitNum)
      }
    });

  } catch (error) {
    console.error('Error fetching listings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch listings'
    });
  }
});

/**
 * Get single listing
 * GET /api/marketplace/listings/:listingId
 */
app.get('/api/marketplace/listings/:listingId', async (req, res) => {
  try {
    const { listingId } = req.params;

    // Find and increment view count atomically
    const listing = await Listing.findOneAndUpdate(
      { listingId },
      { $inc: { views: 1 } },
      { new: true }
    );

    if (!listing) {
      return res.status(404).json({
        success: false,
        error: 'Listing not found'
      });
    }

    res.json({
      success: true,
      listing
    });

  } catch (error) {
    console.error('Error fetching listing:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch listing'
    });
  }
});

/**
 * Cancel listing (PROTECTED)
 * DELETE /api/marketplace/listings/:listingId
 */
app.delete('/api/marketplace/listings/:listingId', authenticateToken, async (req, res) => {
  try {
    const { listingId } = req.params;
    const seller = req.user.walletAddress;

    const listing = await Listing.findOne({ listingId });

    if (!listing) {
      return res.status(404).json({
        success: false,
        error: 'Listing not found'
      });
    }

    if (listing.seller !== seller) {
      return res.status(403).json({
        success: false,
        error: 'Only the seller can cancel the listing'
      });
    }

    if (listing.status !== LISTING_STATUS.ACTIVE) {
      return res.status(400).json({
        success: false,
        error: 'Only active listings can be cancelled'
      });
    }

    listing.status = LISTING_STATUS.CANCELLED;
    await listing.save();

    console.log(`❌ Listing cancelled: ${listingId}`);

    res.json({
      success: true,
      message: 'Listing cancelled successfully',
      listing
    });

    // Broadcast cancellation
    broadcastToWebSocket('marketplace_listing', 'listing_cancelled', {
      listingId,
      nftId: listing.nftId
    });

  } catch (error) {
    console.error('Error cancelling listing:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to cancel listing'
    });
  }
});

// ============================================
// BUY/SELL ENDPOINTS
// ============================================

/**
 * Buy NFT (direct purchase) (PROTECTED)
 * POST /api/marketplace/buy
 */
app.post('/api/marketplace/buy', authenticateToken, async (req, res) => {
  try {
    const { listingId, paymentMethod = 'wallet' } = req.body;
    const buyer = req.user.walletAddress;

    if (!listingId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: listingId'
      });
    }

    const listing = await Listing.findOne({ listingId });

    if (!listing) {
      return res.status(404).json({
        success: false,
        error: 'Listing not found'
      });
    }

    if (listing.status !== LISTING_STATUS.ACTIVE) {
      return res.status(400).json({
        success: false,
        error: 'This listing is not available'
      });
    }

    if (listing.seller === buyer) {
      return res.status(400).json({
        success: false,
        error: 'You cannot buy your own NFT'
      });
    }

    if (listing.auctionMode && !listing.buyNowPrice) {
      return res.status(400).json({
        success: false,
        error: 'This is an auction. Please place a bid instead'
      });
    }

    const salePrice = listing.auctionMode ? listing.buyNowPrice : listing.price;

    // Create transaction record
    const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const transactionData = {
      transactionId,
      type: TRANSACTION_TYPE.DIRECT_SALE,
      listingId,
      nftId: listing.nftId,
      seller: listing.seller,
      buyer,
      price: salePrice,
      currency: listing.currency,
      paymentMethod,
      platformFee: salePrice * 0.025, // 2.5% platform fee
      sellerReceives: salePrice * 0.975,
      status: 'completed',
      timestamp: new Date()
    };

    const transaction = await MarketplaceTransaction.create(transactionData);

    // Update listing status
    listing.status = LISTING_STATUS.SOLD;
    listing.soldTo = buyer;
    listing.soldAt = new Date();
    listing.soldPrice = salePrice;
    await listing.save();

    console.log(`💰 NFT sold: ${listing.nftId} for ${salePrice} ${listing.currency}`);

    res.json({
      success: true,
      message: 'NFT purchased successfully',
      transaction
    });

    // Broadcast sale event
    broadcastToWebSocket('marketplace_sale', 'nft_sold', {
      transaction,
      nftId: listing.nftId
    });

  } catch (error) {
    console.error('Error processing purchase:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process purchase'
    });
  }
});

// ============================================
// OFFER/BID ENDPOINTS
// ============================================

/**
 * Create offer/bid on NFT (PROTECTED)
 * POST /api/marketplace/offers
 */
app.post('/api/marketplace/offers', authenticateToken, async (req, res) => {
  try {
    const {
      listingId,
      nftId,
      amount,
      currency = 'XTZ',
      duration = 7 // days
    } = req.body;

    const offerer = req.user.walletAddress;

    if ((!listingId && !nftId) || !amount) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }

    let listing = null;
    if (listingId) {
      listing = await Listing.findOne({ listingId });
      if (!listing) {
        return res.status(404).json({
          success: false,
          error: 'Listing not found'
        });
      }
    }

    const offerId = `offer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + duration);

    const offerData = {
      offerId,
      listingId,
      nftId: listing ? listing.nftId : nftId,
      offerer,
      amount: parseFloat(amount),
      currency,
      status: OFFER_STATUS.PENDING,
      expiresAt
    };

    // For auction listings, update highest bid atomically (fixes race condition)
    if (listing && listing.auctionMode) {
      if (amount < listing.minimumBid) {
        return res.status(400).json({
          success: false,
          error: `Bid must be at least ${listing.minimumBid} ${listing.currency}`
        });
      }

      if (amount <= listing.currentBid) {
        return res.status(400).json({
          success: false,
          error: `Bid must be higher than current bid of ${listing.currentBid} ${listing.currency}`
        });
      }

      // Atomic update to prevent race condition
      const updatedListing = await Listing.findOneAndUpdate(
        {
          listingId,
          status: LISTING_STATUS.ACTIVE,
          currentBid: { $lt: amount } // Ensure bid is still valid
        },
        {
          $set: {
            currentBid: parseFloat(amount),
            highestBidder: offerer
          }
        },
        { new: true }
      );

      if (!updatedListing) {
        return res.status(400).json({
          success: false,
          error: 'Bid was outbid by another user. Please try again with a higher amount.'
        });
      }

      console.log(`📈 New bid on ${updatedListing.nftId}: ${amount} ${currency} by ${offerer}`);
    }

    const offer = await Offer.create(offerData);

    res.json({
      success: true,
      offer
    });

    // Broadcast offer event
    const eventType = listing?.auctionMode ? 'new_bid' : 'new_offer';
    broadcastToWebSocket('marketplace_offer', eventType, {
      offer,
      listing
    });

  } catch (error) {
    console.error('Error creating offer:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create offer'
    });
  }
});

/**
 * Get offers for NFT or listing
 * GET /api/marketplace/offers
 */
app.get('/api/marketplace/offers', async (req, res) => {
  try {
    const { listingId, nftId, offerer, status } = req.query;

    // Build query
    const query = {};
    if (listingId) query.listingId = listingId;
    if (nftId) query.nftId = nftId;
    if (offerer) query.offerer = offerer;
    if (status) query.status = status;

    // Update expired offers
    const now = new Date();
    await Offer.updateMany(
      { status: OFFER_STATUS.PENDING, expiresAt: { $lt: now } },
      { $set: { status: OFFER_STATUS.EXPIRED } }
    );

    // Get offers sorted by amount (highest first)
    const filteredOffers = await Offer.find(query).sort({ amount: -1 }).lean();

    res.json({
      success: true,
      data: filteredOffers,
      count: filteredOffers.length
    });

  } catch (error) {
    console.error('Error fetching offers:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch offers'
    });
  }
});

/**
 * Accept offer (PROTECTED)
 * POST /api/marketplace/offers/:offerId/accept
 */
app.post('/api/marketplace/offers/:offerId/accept', authenticateToken, async (req, res) => {
  try {
    const { offerId } = req.params;
    const seller = req.user.walletAddress;

    const offer = await Offer.findOne({ offerId });

    if (!offer) {
      return res.status(404).json({
        success: false,
        error: 'Offer not found'
      });
    }

    if (offer.status !== OFFER_STATUS.PENDING) {
      return res.status(400).json({
        success: false,
        error: 'This offer is no longer available'
      });
    }

    // Verify seller owns the NFT
    if (offer.listingId) {
      const listing = await Listing.findOne({ listingId: offer.listingId });
      if (listing && listing.seller !== seller) {
        return res.status(403).json({
          success: false,
          error: 'Only the seller can accept offers'
        });
      }
    }

    // Accept offer
    offer.status = OFFER_STATUS.ACCEPTED;
    offer.acceptedAt = new Date();
    await offer.save();

    // Create transaction
    const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const transactionData = {
      transactionId,
      type: TRANSACTION_TYPE.OFFER_ACCEPTED,
      offerId,
      nftId: offer.nftId,
      seller,
      buyer: offer.offerer,
      price: offer.amount,
      currency: offer.currency,
      platformFee: offer.amount * 0.025,
      sellerReceives: offer.amount * 0.975,
      status: 'completed',
      timestamp: new Date()
    };

    const transaction = await MarketplaceTransaction.create(transactionData);

    // Update listing if exists
    if (offer.listingId) {
      await Listing.updateOne(
        { listingId: offer.listingId },
        {
          $set: {
            status: LISTING_STATUS.SOLD,
            soldTo: offer.offerer,
            soldAt: new Date(),
            soldPrice: offer.amount
          }
        }
      );
    }

    console.log(`✅ Offer accepted: ${offerId} for ${offer.amount} ${offer.currency}`);

    res.json({
      success: true,
      message: 'Offer accepted successfully',
      transaction
    });

    broadcastToWebSocket('marketplace_sale', 'offer_accepted', {
      transaction,
      offer
    });

  } catch (error) {
    console.error('Error accepting offer:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to accept offer'
    });
  }
});

/**
 * Reject offer (PROTECTED)
 * POST /api/marketplace/offers/:offerId/reject
 */
app.post('/api/marketplace/offers/:offerId/reject', authenticateToken, async (req, res) => {
  try {
    const { offerId } = req.params;
    const offer = await Offer.findOne({ offerId });

    if (!offer) {
      return res.status(404).json({
        success: false,
        error: 'Offer not found'
      });
    }

    offer.status = OFFER_STATUS.REJECTED;
    offer.rejectedAt = new Date();
    await offer.save();

    res.json({
      success: true,
      message: 'Offer rejected',
      offer
    });

  } catch (error) {
    console.error('Error rejecting offer:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reject offer'
    });
  }
});

/**
 * Cancel offer (PROTECTED)
 * DELETE /api/marketplace/offers/:offerId
 */
app.delete('/api/marketplace/offers/:offerId', authenticateToken, async (req, res) => {
  try {
    const { offerId } = req.params;
    const offerer = req.user.walletAddress;

    const offer = await Offer.findOne({ offerId });

    if (!offer) {
      return res.status(404).json({
        success: false,
        error: 'Offer not found'
      });
    }

    if (offer.offerer !== offerer) {
      return res.status(403).json({
        success: false,
        error: 'Only the offerer can cancel the offer'
      });
    }

    offer.status = OFFER_STATUS.CANCELLED;
    await offer.save();

    res.json({
      success: true,
      message: 'Offer cancelled',
      offer
    });

  } catch (error) {
    console.error('Error cancelling offer:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to cancel offer'
    });
  }
});

// ============================================
// TRANSACTION HISTORY
// ============================================

/**
 * Get transaction history
 * GET /api/marketplace/transactions
 */
app.get('/api/marketplace/transactions', async (req, res) => {
  try {
    const { user, nftId, type, limit = 50 } = req.query;

    // Build query
    const query = {};

    if (user) {
      query.$or = [{ seller: user }, { buyer: user }];
    }

    if (nftId) {
      query.nftId = nftId;
    }

    if (type) {
      query.type = type;
    }

    // Get transactions sorted by timestamp (newest first)
    const filteredTransactions = await MarketplaceTransaction.find(query)
      .sort({ timestamp: -1 })
      .limit(parseInt(limit))
      .lean();

    res.json({
      success: true,
      data: filteredTransactions,
      count: filteredTransactions.length
    });

  } catch (error) {
    console.error('Error fetching transactions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch transactions'
    });
  }
});

// ============================================
// MARKETPLACE STATISTICS
// ============================================

/**
 * Get marketplace statistics
 * GET /api/marketplace/stats
 */
app.get('/api/marketplace/stats', async (req, res) => {
  try {
    // Get counts from each collection using aggregation
    const [listingStats, offerStats, transactionStats] = await Promise.all([
      Listing.aggregate([
        {
          $group: {
            _id: null,
            total: { $sum: 1 },
            active: { $sum: { $cond: [{ $eq: ['$status', 'active'] }, 1, 0] } },
            sold: { $sum: { $cond: [{ $eq: ['$status', 'sold'] }, 1, 0] } },
            cancelled: { $sum: { $cond: [{ $eq: ['$status', 'cancelled'] }, 1, 0] } },
            auctions: { $sum: { $cond: ['$auctionMode', 1, 0] } }
          }
        }
      ]),
      Offer.aggregate([
        {
          $group: {
            _id: null,
            total: { $sum: 1 },
            pending: { $sum: { $cond: [{ $eq: ['$status', 'pending'] }, 1, 0] } },
            accepted: { $sum: { $cond: [{ $eq: ['$status', 'accepted'] }, 1, 0] } },
            rejected: { $sum: { $cond: [{ $eq: ['$status', 'rejected'] }, 1, 0] } }
          }
        }
      ]),
      MarketplaceTransaction.aggregate([
        {
          $group: {
            _id: null,
            total: { $sum: 1 },
            volume: { $sum: '$price' },
            platformFees: { $sum: '$platformFee' },
            averagePrice: { $avg: '$price' }
          }
        }
      ])
    ]);

    // Get trending data
    const [topSellers, topBuyers, recentSales, mostViewed] = await Promise.all([
      MarketplaceTransaction.aggregate([
        { $group: { _id: '$seller', sales: { $sum: 1 }, volume: { $sum: '$price' } } },
        { $sort: { volume: -1 } },
        { $limit: 5 },
        { $project: { seller: '$_id', sales: 1, volume: 1, _id: 0 } }
      ]),
      MarketplaceTransaction.aggregate([
        { $group: { _id: '$buyer', purchases: { $sum: 1 }, spent: { $sum: '$price' } } },
        { $sort: { spent: -1 } },
        { $limit: 5 },
        { $project: { buyer: '$_id', purchases: 1, spent: 1, _id: 0 } }
      ]),
      MarketplaceTransaction.find().sort({ timestamp: -1 }).limit(10).lean(),
      Listing.find({ status: 'active' }).sort({ views: -1 }).limit(10).select('listingId nftId views price').lean()
    ]);

    const stats = {
      listings: listingStats[0] || { total: 0, active: 0, sold: 0, cancelled: 0, auctions: 0 },
      offers: offerStats[0] || { total: 0, pending: 0, accepted: 0, rejected: 0 },
      transactions: transactionStats[0] || { total: 0, volume: 0, platformFees: 0, averagePrice: 0 },
      trending: {
        topSellers,
        topBuyers,
        recentSales,
        mostViewed
      }
    };

    res.json({
      success: true,
      stats,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('Error fetching marketplace stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch marketplace statistics'
    });
  }
});

/**
 * Get marketplace floor prices
 * GET /api/marketplace/floor-prices
 */
app.get('/api/marketplace/floor-prices', async (req, res) => {
  try {
    // Get overall floor price
    const overallFloor = await Listing.findOne({ status: LISTING_STATUS.ACTIVE })
      .sort({ price: 1 })
      .select('price')
      .lean();

    const floorPrices = {
      overall: overallFloor ? overallFloor.price : 0,
      byRarity: {}
    };

    res.json({
      success: true,
      floorPrices,
      timestamp: new Date()
    });

  } catch (error) {
    console.error('Error calculating floor prices:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to calculate floor prices'
    });
  }
});

// ============================================
// HELPER FUNCTIONS
// ============================================

async function broadcastToWebSocket(channel, event, data) {
  try {
    await axios.post(`${SERVICES.websocket}/broadcast`, {
      channel,
      event,
      data
    });
  } catch (error) {
    console.log('WebSocket broadcast failed (service may not be running)');
  }
}

// Error logger middleware (must be after routes)
app.use(errorLogger);

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', async (req, res) => {
  try {
    const isDbConnected = await db.healthCheck();
    const [listingCount, offerCount, transactionCount] = await Promise.all([
      Listing.countDocuments(),
      Offer.countDocuments(),
      MarketplaceTransaction.countDocuments()
    ]);

    res.json({
      status: 'ok',
      timestamp: new Date(),
      service: 'marketplace-service',
      uptime: process.uptime(),
      database: isDbConnected ? 'connected' : 'disconnected',
      stats: {
        listings: listingCount,
        offers: offerCount,
        transactions: transactionCount
      }
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error: error.message
    });
  }
});

// ============================================
// START SERVER
// ============================================

async function startServer() {
  try {
    // Connect to MongoDB
    console.log('📊 Connecting to MongoDB...');
    await db.connect();
    console.log('✅ MongoDB connected');

    // Initialize indexes
    await Promise.all([
      Listing.createIndexes(),
      Offer.createIndexes(),
      MarketplaceTransaction.createIndexes()
    ]);
    console.log('✅ Database indexes initialized');

    // Start server
    app.listen(PORT, () => {
      console.log('╔════════════════════════════════════════════════╗');
      console.log('║   WeatherNFT Marketplace Service Started      ║');
      console.log('╚════════════════════════════════════════════════╝');
  console.log(`🏪 Marketplace Service: http://localhost:${PORT}`);
  console.log('');
  console.log('Available endpoints:');
  console.log('  POST   /api/marketplace/listings            - Create listing');
  console.log('  GET    /api/marketplace/listings            - Get all listings');
  console.log('  GET    /api/marketplace/listings/:id        - Get single listing');
  console.log('  DELETE /api/marketplace/listings/:id        - Cancel listing');
  console.log('  POST   /api/marketplace/buy                 - Buy NFT');
  console.log('  POST   /api/marketplace/offers              - Create offer/bid');
  console.log('  GET    /api/marketplace/offers              - Get offers');
  console.log('  POST   /api/marketplace/offers/:id/accept   - Accept offer');
      console.log('  POST   /api/marketplace/offers/:id/reject   - Reject offer');
      console.log('  DELETE /api/marketplace/offers/:id          - Cancel offer');
      console.log('  GET    /api/marketplace/transactions        - Get transactions');
      console.log('  GET    /api/marketplace/stats               - Marketplace stats');
      console.log('  GET    /api/marketplace/floor-prices        - Floor prices');
      console.log('  GET    /health                              - Health check');
      console.log('');
      console.log('✅ Ready to handle marketplace operations!');
      console.log('📦 MongoDB collections ready: Listing, Offer, MarketplaceTransaction');
    });

  } catch (error) {
    console.error('❌ Failed to start marketplace service:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⚠️  Shutting down marketplace service...');
  await db.disconnect();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n⚠️  Shutting down marketplace service...');
  await db.disconnect();
  process.exit(0);
});

// Start the server
startServer();

module.exports = app;
