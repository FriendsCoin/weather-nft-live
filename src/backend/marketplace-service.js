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

const app = express();
const PORT = process.env.MARKETPLACE_PORT || 3013;

// Middleware
app.use(cors());
app.use(express.json());

// Service URLs
const SERVICES = {
  nft: `http://localhost:${process.env.NFT_SERVICE_PORT || 3009}`,
  guild: `http://localhost:${process.env.GUILD_SERVICE_PORT || 3010}`,
  analytics: `http://localhost:${process.env.ANALYTICS_PORT || 3011}`,
  websocket: `http://localhost:${process.env.WEBSOCKET_PORT || 8080}`
};

// In-memory storage (в продакшене использовать MongoDB)
const listings = new Map(); // NFT listings
const offers = new Map(); // Offers/bids on NFTs
const priceHistory = new Map(); // Price history for each NFT
const transactions = new Map(); // Transaction history
const watchlist = new Map(); // User watchlists

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
 * Create NFT listing
 * POST /api/marketplace/listings
 */
app.post('/api/marketplace/listings', async (req, res) => {
  try {
    const {
      nftId,
      seller,
      price,
      currency = 'XTZ',
      duration = 30, // days
      auctionMode = false,
      minimumBid,
      buyNowPrice
    } = req.body;

    // Validate required fields
    if (!nftId || !seller || !price) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: nftId, seller, price'
      });
    }

    // Check if NFT exists
    try {
      const nftResponse = await axios.get(`${SERVICES.nft}/api/nfts/${nftId}`);
      const nft = nftResponse.data;

      if (nft.status === 'listed') {
        return res.status(400).json({
          success: false,
          error: 'NFT is already listed'
        });
      }

      // Verify seller owns the NFT
      if (nft.capturedBy !== seller) {
        return res.status(403).json({
          success: false,
          error: 'Only the NFT owner can list it'
        });
      }
    } catch (error) {
      return res.status(404).json({
        success: false,
        error: 'NFT not found'
      });
    }

    const listingId = `listing_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + duration);

    const listing = {
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
      createdAt: new Date(),
      expiresAt,
      updatedAt: new Date()
    };

    listings.set(listingId, listing);

    // Record price history
    recordPriceHistory(nftId, {
      type: 'listed',
      price,
      currency,
      timestamp: new Date()
    });

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
app.get('/api/marketplace/listings', (req, res) => {
  try {
    const {
      status = LISTING_STATUS.ACTIVE,
      seller,
      minPrice,
      maxPrice,
      currency,
      auctionMode,
      rarity,
      weatherCondition,
      sortBy = 'createdAt',
      sortOrder = 'desc',
      page = 1,
      limit = 20
    } = req.query;

    let filteredListings = Array.from(listings.values());

    // Apply filters
    if (status) {
      filteredListings = filteredListings.filter(l => l.status === status);
    }

    if (seller) {
      filteredListings = filteredListings.filter(l => l.seller === seller);
    }

    if (minPrice) {
      filteredListings = filteredListings.filter(l => l.price >= parseFloat(minPrice));
    }

    if (maxPrice) {
      filteredListings = filteredListings.filter(l => l.price <= parseFloat(maxPrice));
    }

    if (currency) {
      filteredListings = filteredListings.filter(l => l.currency === currency);
    }

    if (auctionMode !== undefined) {
      const isAuction = auctionMode === 'true';
      filteredListings = filteredListings.filter(l => l.auctionMode === isAuction);
    }

    // Check for expired listings
    const now = new Date();
    filteredListings.forEach(listing => {
      if (listing.status === LISTING_STATUS.ACTIVE && listing.expiresAt < now) {
        listing.status = LISTING_STATUS.EXPIRED;
        listings.set(listing.listingId, listing);
      }
    });

    // Sorting
    filteredListings.sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];

      if (sortBy === 'price' || sortBy === 'currentBid') {
        aVal = parseFloat(aVal) || 0;
        bVal = parseFloat(bVal) || 0;
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    // Pagination
    const startIndex = (parseInt(page) - 1) * parseInt(limit);
    const endIndex = startIndex + parseInt(limit);
    const paginatedListings = filteredListings.slice(startIndex, endIndex);

    res.json({
      success: true,
      data: paginatedListings,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: filteredListings.length,
        pages: Math.ceil(filteredListings.length / parseInt(limit))
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
app.get('/api/marketplace/listings/:listingId', (req, res) => {
  try {
    const { listingId } = req.params;
    const listing = listings.get(listingId);

    if (!listing) {
      return res.status(404).json({
        success: false,
        error: 'Listing not found'
      });
    }

    // Increment view count
    listing.views += 1;
    listings.set(listingId, listing);

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
 * Cancel listing
 * DELETE /api/marketplace/listings/:listingId
 */
app.delete('/api/marketplace/listings/:listingId', (req, res) => {
  try {
    const { listingId } = req.params;
    const { seller } = req.body;

    const listing = listings.get(listingId);

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
    listing.updatedAt = new Date();
    listings.set(listingId, listing);

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
 * Buy NFT (direct purchase)
 * POST /api/marketplace/buy
 */
app.post('/api/marketplace/buy', async (req, res) => {
  try {
    const { listingId, buyer, paymentMethod = 'wallet' } = req.body;

    if (!listingId || !buyer) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: listingId, buyer'
      });
    }

    const listing = listings.get(listingId);

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
    const transaction = {
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

    transactions.set(transactionId, transaction);

    // Update listing status
    listing.status = LISTING_STATUS.SOLD;
    listing.soldTo = buyer;
    listing.soldAt = new Date();
    listing.soldPrice = salePrice;
    listing.updatedAt = new Date();
    listings.set(listingId, listing);

    // Record price history
    recordPriceHistory(listing.nftId, {
      type: 'sold',
      price: salePrice,
      currency: listing.currency,
      buyer,
      seller: listing.seller,
      timestamp: new Date()
    });

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
 * Create offer/bid on NFT
 * POST /api/marketplace/offers
 */
app.post('/api/marketplace/offers', (req, res) => {
  try {
    const {
      listingId,
      nftId,
      offerer,
      amount,
      currency = 'XTZ',
      duration = 7 // days
    } = req.body;

    if ((!listingId && !nftId) || !offerer || !amount) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }

    let listing = null;
    if (listingId) {
      listing = listings.get(listingId);
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

    const offer = {
      offerId,
      listingId,
      nftId: listing ? listing.nftId : nftId,
      offerer,
      amount: parseFloat(amount),
      currency,
      status: OFFER_STATUS.PENDING,
      createdAt: new Date(),
      expiresAt,
      updatedAt: new Date()
    };

    // For auction listings, update highest bid
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

      listing.currentBid = parseFloat(amount);
      listing.highestBidder = offerer;
      listing.updatedAt = new Date();
      listings.set(listingId, listing);

      console.log(`📈 New bid on ${listing.nftId}: ${amount} ${currency} by ${offerer}`);
    }

    offers.set(offerId, offer);

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
app.get('/api/marketplace/offers', (req, res) => {
  try {
    const { listingId, nftId, offerer, status } = req.query;

    let filteredOffers = Array.from(offers.values());

    if (listingId) {
      filteredOffers = filteredOffers.filter(o => o.listingId === listingId);
    }

    if (nftId) {
      filteredOffers = filteredOffers.filter(o => o.nftId === nftId);
    }

    if (offerer) {
      filteredOffers = filteredOffers.filter(o => o.offerer === offerer);
    }

    if (status) {
      filteredOffers = filteredOffers.filter(o => o.status === status);
    }

    // Check for expired offers
    const now = new Date();
    filteredOffers.forEach(offer => {
      if (offer.status === OFFER_STATUS.PENDING && offer.expiresAt < now) {
        offer.status = OFFER_STATUS.EXPIRED;
        offers.set(offer.offerId, offer);
      }
    });

    // Sort by amount (highest first)
    filteredOffers.sort((a, b) => b.amount - a.amount);

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
 * Accept offer
 * POST /api/marketplace/offers/:offerId/accept
 */
app.post('/api/marketplace/offers/:offerId/accept', (req, res) => {
  try {
    const { offerId } = req.params;
    const { seller } = req.body;

    const offer = offers.get(offerId);

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
      const listing = listings.get(offer.listingId);
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
    offer.updatedAt = new Date();
    offers.set(offerId, offer);

    // Create transaction
    const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const transaction = {
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

    transactions.set(transactionId, transaction);

    // Update listing if exists
    if (offer.listingId) {
      const listing = listings.get(offer.listingId);
      if (listing) {
        listing.status = LISTING_STATUS.SOLD;
        listing.soldTo = offer.offerer;
        listing.soldAt = new Date();
        listing.soldPrice = offer.amount;
        listings.set(offer.listingId, listing);
      }
    }

    // Record price history
    recordPriceHistory(offer.nftId, {
      type: 'offer_accepted',
      price: offer.amount,
      currency: offer.currency,
      buyer: offer.offerer,
      seller,
      timestamp: new Date()
    });

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
 * Reject offer
 * POST /api/marketplace/offers/:offerId/reject
 */
app.post('/api/marketplace/offers/:offerId/reject', (req, res) => {
  try {
    const { offerId } = req.params;
    const offer = offers.get(offerId);

    if (!offer) {
      return res.status(404).json({
        success: false,
        error: 'Offer not found'
      });
    }

    offer.status = OFFER_STATUS.REJECTED;
    offer.rejectedAt = new Date();
    offer.updatedAt = new Date();
    offers.set(offerId, offer);

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
 * Cancel offer
 * DELETE /api/marketplace/offers/:offerId
 */
app.delete('/api/marketplace/offers/:offerId', (req, res) => {
  try {
    const { offerId } = req.params;
    const { offerer } = req.body;

    const offer = offers.get(offerId);

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
    offer.updatedAt = new Date();
    offers.set(offerId, offer);

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
// PRICE HISTORY ENDPOINTS
// ============================================

/**
 * Get price history for NFT
 * GET /api/marketplace/price-history/:nftId
 */
app.get('/api/marketplace/price-history/:nftId', (req, res) => {
  try {
    const { nftId } = req.params;
    const history = priceHistory.get(nftId) || [];

    // Calculate statistics
    const prices = history.filter(h => h.price).map(h => h.price);
    const stats = {
      count: prices.length,
      averagePrice: prices.length > 0 ? prices.reduce((a, b) => a + b, 0) / prices.length : 0,
      minPrice: prices.length > 0 ? Math.min(...prices) : 0,
      maxPrice: prices.length > 0 ? Math.max(...prices) : 0,
      lastPrice: prices.length > 0 ? prices[prices.length - 1] : 0
    };

    res.json({
      success: true,
      nftId,
      history,
      stats
    });

  } catch (error) {
    console.error('Error fetching price history:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch price history'
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
app.get('/api/marketplace/transactions', (req, res) => {
  try {
    const { user, nftId, type, limit = 50 } = req.query;

    let filteredTransactions = Array.from(transactions.values());

    if (user) {
      filteredTransactions = filteredTransactions.filter(
        t => t.seller === user || t.buyer === user
      );
    }

    if (nftId) {
      filteredTransactions = filteredTransactions.filter(t => t.nftId === nftId);
    }

    if (type) {
      filteredTransactions = filteredTransactions.filter(t => t.type === type);
    }

    // Sort by timestamp (newest first)
    filteredTransactions.sort((a, b) => b.timestamp - a.timestamp);

    // Limit results
    filteredTransactions = filteredTransactions.slice(0, parseInt(limit));

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
app.get('/api/marketplace/stats', (req, res) => {
  try {
    const allListings = Array.from(listings.values());
    const allOffers = Array.from(offers.values());
    const allTransactions = Array.from(transactions.values());

    // Calculate statistics
    const stats = {
      listings: {
        total: allListings.length,
        active: allListings.filter(l => l.status === LISTING_STATUS.ACTIVE).length,
        sold: allListings.filter(l => l.status === LISTING_STATUS.SOLD).length,
        cancelled: allListings.filter(l => l.status === LISTING_STATUS.CANCELLED).length,
        auctions: allListings.filter(l => l.auctionMode).length
      },
      offers: {
        total: allOffers.length,
        pending: allOffers.filter(o => o.status === OFFER_STATUS.PENDING).length,
        accepted: allOffers.filter(o => o.status === OFFER_STATUS.ACCEPTED).length,
        rejected: allOffers.filter(o => o.status === OFFER_STATUS.REJECTED).length
      },
      transactions: {
        total: allTransactions.length,
        volume: allTransactions.reduce((sum, t) => sum + t.price, 0),
        platformFees: allTransactions.reduce((sum, t) => sum + t.platformFee, 0),
        averagePrice: allTransactions.length > 0
          ? allTransactions.reduce((sum, t) => sum + t.price, 0) / allTransactions.length
          : 0
      },
      trending: {
        topSellers: getTopSellers(allTransactions, 5),
        topBuyers: getTopBuyers(allTransactions, 5),
        recentSales: allTransactions.slice(0, 10),
        mostViewed: getMostViewed(allListings, 10)
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
app.get('/api/marketplace/floor-prices', (req, res) => {
  try {
    const activeListings = Array.from(listings.values())
      .filter(l => l.status === LISTING_STATUS.ACTIVE);

    // Group by rarity and find floor prices
    const floorPrices = {
      overall: activeListings.length > 0 ? Math.min(...activeListings.map(l => l.price)) : 0,
      byRarity: {}
    };

    const rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary'];
    rarities.forEach(rarity => {
      const rarityListings = activeListings.filter(l => l.rarity === rarity);
      floorPrices.byRarity[rarity] = rarityListings.length > 0
        ? Math.min(...rarityListings.map(l => l.price))
        : 0;
    });

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
// WATCHLIST ENDPOINTS
// ============================================

/**
 * Add NFT to watchlist
 * POST /api/marketplace/watchlist
 */
app.post('/api/marketplace/watchlist', (req, res) => {
  try {
    const { userId, nftId } = req.body;

    if (!userId || !nftId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: userId, nftId'
      });
    }

    let userWatchlist = watchlist.get(userId) || [];
    if (!userWatchlist.includes(nftId)) {
      userWatchlist.push(nftId);
      watchlist.set(userId, userWatchlist);
    }

    res.json({
      success: true,
      message: 'Added to watchlist',
      watchlist: userWatchlist
    });

  } catch (error) {
    console.error('Error adding to watchlist:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to add to watchlist'
    });
  }
});

/**
 * Get user watchlist
 * GET /api/marketplace/watchlist/:userId
 */
app.get('/api/marketplace/watchlist/:userId', (req, res) => {
  try {
    const { userId } = req.params;
    const userWatchlist = watchlist.get(userId) || [];

    res.json({
      success: true,
      watchlist: userWatchlist,
      count: userWatchlist.length
    });

  } catch (error) {
    console.error('Error fetching watchlist:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch watchlist'
    });
  }
});

/**
 * Remove from watchlist
 * DELETE /api/marketplace/watchlist
 */
app.delete('/api/marketplace/watchlist', (req, res) => {
  try {
    const { userId, nftId } = req.body;

    let userWatchlist = watchlist.get(userId) || [];
    userWatchlist = userWatchlist.filter(id => id !== nftId);
    watchlist.set(userId, userWatchlist);

    res.json({
      success: true,
      message: 'Removed from watchlist',
      watchlist: userWatchlist
    });

  } catch (error) {
    console.error('Error removing from watchlist:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to remove from watchlist'
    });
  }
});

// ============================================
// HELPER FUNCTIONS
// ============================================

function recordPriceHistory(nftId, entry) {
  let history = priceHistory.get(nftId) || [];
  history.push(entry);
  priceHistory.set(nftId, history);
}

function getTopSellers(transactions, limit) {
  const sellerStats = new Map();

  transactions.forEach(t => {
    const current = sellerStats.get(t.seller) || { sales: 0, volume: 0 };
    current.sales += 1;
    current.volume += t.price;
    sellerStats.set(t.seller, current);
  });

  return Array.from(sellerStats.entries())
    .map(([seller, stats]) => ({ seller, ...stats }))
    .sort((a, b) => b.volume - a.volume)
    .slice(0, limit);
}

function getTopBuyers(transactions, limit) {
  const buyerStats = new Map();

  transactions.forEach(t => {
    const current = buyerStats.get(t.buyer) || { purchases: 0, spent: 0 };
    current.purchases += 1;
    current.spent += t.price;
    buyerStats.set(t.buyer, current);
  });

  return Array.from(buyerStats.entries())
    .map(([buyer, stats]) => ({ buyer, ...stats }))
    .sort((a, b) => b.spent - a.spent)
    .slice(0, limit);
}

function getMostViewed(listings, limit) {
  return listings
    .sort((a, b) => b.views - a.views)
    .slice(0, limit)
    .map(l => ({
      listingId: l.listingId,
      nftId: l.nftId,
      views: l.views,
      price: l.price
    }));
}

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

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date(),
    service: 'marketplace-service',
    uptime: process.uptime(),
    stats: {
      listings: listings.size,
      offers: offers.size,
      transactions: transactions.size,
      priceHistory: priceHistory.size
    }
  });
});

// ============================================
// START SERVER
// ============================================

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
  console.log('  GET    /api/marketplace/price-history/:id   - Get price history');
  console.log('  GET    /api/marketplace/transactions        - Get transactions');
  console.log('  GET    /api/marketplace/stats               - Marketplace stats');
  console.log('  GET    /api/marketplace/floor-prices        - Floor prices');
  console.log('  POST   /api/marketplace/watchlist           - Add to watchlist');
  console.log('  GET    /api/marketplace/watchlist/:userId   - Get watchlist');
  console.log('  DELETE /api/marketplace/watchlist           - Remove from watchlist');
  console.log('  GET    /health                              - Health check');
  console.log('');
  console.log('✅ Ready to handle marketplace operations!');
});

module.exports = app;
