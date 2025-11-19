/**
 * MongoDB Models for WeatherNFT
 * Mongoose schemas for all platform entities
 */

const mongoose = require('mongoose');

// Guild Schema
const guildSchema = new mongoose.Schema({
  guildId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    default: ''
  },
  founder: {
    type: String,
    required: true,
    index: true
  },
  logo: {
    type: String,
    default: null
  },
  members: [{
    type: String,
    index: true
  }],
  rentedAlgorithms: [{
    type: String
  }],
  totalRevenue: {
    type: Number,
    default: 0,
    min: 0
  },
  totalCaptures: {
    type: Number,
    default: 0,
    min: 0
  },
  status: {
    type: String,
    enum: ['active', 'inactive', 'suspended'],
    default: 'active'
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Indexes
guildSchema.index({ totalRevenue: -1 });
guildSchema.index({ totalCaptures: -1 });
guildSchema.index({ createdAt: -1 });

// NFT Schema
const nftSchema = new mongoose.Schema({
  eventId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  owner: {
    type: String,
    required: true,
    index: true
  },
  imageHash: {
    type: String,
    required: true
  },
  imageUrl: {
    type: String,
    required: true
  },
  metadataHash: {
    type: String,
    required: true
  },
  metadataUrl: {
    type: String,
    required: true
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  status: {
    type: String,
    enum: ['pending_mint', 'minted', 'listed', 'sold'],
    default: 'pending_mint',
    index: true
  },
  tokenId: {
    type: String,
    default: null,
    sparse: true,
    index: true
  },
  txHash: {
    type: String,
    default: null,
    sparse: true
  },
  price: {
    type: Number,
    min: 0
  },
  rarity: {
    type: String,
    enum: ['common', 'uncommon', 'rare', 'epic', 'legendary'],
    required: true,
    index: true
  },
  algorithm: {
    type: String,
    required: true,
    index: true
  },
  weatherData: {
    type: mongoose.Schema.Types.Mixed
  },
  location: {
    type: mongoose.Schema.Types.Mixed
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Indexes
nftSchema.index({ rarity: 1, createdAt: -1 });
nftSchema.index({ owner: 1, status: 1 });

// User Schema
const userSchema = new mongoose.Schema({
  address: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  username: {
    type: String,
    sparse: true,
    unique: true
  },
  email: {
    type: String,
    sparse: true,
    lowercase: true
  },
  guilds: [{
    guildId: String,
    role: {
      type: String,
      enum: ['founder', 'member', 'admin']
    },
    joinedAt: Date
  }],
  nfts: [{
    type: String
  }],
  totalCaptures: {
    type: Number,
    default: 0,
    min: 0
  },
  totalEarned: {
    type: Number,
    default: 0,
    min: 0
  },
  stats: {
    nftsCreated: { type: Number, default: 0 },
    nftsSold: { type: Number, default: 0 },
    guildsJoined: { type: Number, default: 0 },
    guildsFounded: { type: Number, default: 0 }
  },
  settings: {
    notifications: { type: Boolean, default: true },
    publicProfile: { type: Boolean, default: true }
  },
  lastActive: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: true
});

// Event Schema
const eventSchema = new mongoose.Schema({
  eventId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  type: {
    type: String,
    required: true,
    index: true
  },
  location: {
    city: String,
    country: String,
    lat: Number,
    lng: Number
  },
  weatherData: {
    temperature: Number,
    humidity: Number,
    pressure: Number,
    windSpeed: Number,
    visibility: Number,
    conditions: String
  },
  rarity: {
    type: String,
    enum: ['common', 'uncommon', 'rare', 'epic', 'legendary'],
    required: true,
    index: true
  },
  algorithm: {
    type: String,
    required: true,
    index: true
  },
  capturedBy: {
    type: String,
    default: null,
    index: true
  },
  capturedAt: {
    type: Date,
    default: null
  },
  capturePrice: {
    type: Number,
    min: 0
  },
  status: {
    type: String,
    enum: ['available', 'captured', 'expired'],
    default: 'available',
    index: true
  },
  expiresAt: {
    type: Date,
    index: true
  },
  detectedAt: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: true
});

// Indexes
eventSchema.index({ status: 1, expiresAt: 1 });
eventSchema.index({ type: 1, rarity: 1 });
eventSchema.index({ 'location.city': 1 });

// Transaction Schema
const transactionSchema = new mongoose.Schema({
  txId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  type: {
    type: String,
    enum: ['capture', 'mint', 'sale', 'transfer', 'guild_rental', 'revenue_share'],
    required: true,
    index: true
  },
  from: {
    type: String,
    index: true
  },
  to: {
    type: String,
    index: true
  },
  amount: {
    type: Number,
    required: true,
    min: 0
  },
  currency: {
    type: String,
    default: 'XTZ'
  },
  relatedEntity: {
    entityType: {
      type: String,
      enum: ['nft', 'event', 'guild', 'algorithm']
    },
    entityId: String
  },
  blockchainTxHash: {
    type: String,
    sparse: true,
    index: true
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'failed'],
    default: 'pending',
    index: true
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: true
});

// Indexes
transactionSchema.index({ type: 1, createdAt: -1 });
transactionSchema.index({ from: 1, type: 1 });
transactionSchema.index({ to: 1, type: 1 });

// Algorithm Rental Schema
const algorithmRentalSchema = new mongoose.Schema({
  rentalId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  guildId: {
    type: String,
    required: true,
    index: true
  },
  algorithmId: {
    type: String,
    required: true,
    index: true
  },
  startDate: {
    type: Date,
    required: true,
    index: true
  },
  endDate: {
    type: Date,
    required: true,
    index: true
  },
  monthlyPrice: {
    type: Number,
    required: true,
    min: 0
  },
  txHash: {
    type: String,
    default: null
  },
  status: {
    type: String,
    enum: ['active', 'expired', 'cancelled'],
    default: 'active',
    index: true
  },
  autoRenew: {
    type: Boolean,
    default: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Indexes
algorithmRentalSchema.index({ guildId: 1, status: 1 });
algorithmRentalSchema.index({ endDate: 1, status: 1 });

// Revenue Share Schema
const revenueShareSchema = new mongoose.Schema({
  shareId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  guildId: {
    type: String,
    required: true,
    index: true
  },
  userAddress: {
    type: String,
    required: true,
    index: true
  },
  algorithmId: {
    type: String,
    index: true
  },
  eventId: {
    type: String,
    required: true,
    index: true
  },
  capturePrice: {
    type: Number,
    required: true,
    min: 0
  },
  guildShare: {
    type: Number,
    required: true,
    min: 0
  },
  userShare: {
    type: Number,
    required: true,
    min: 0
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: false
});

// Indexes
revenueShareSchema.index({ guildId: 1, timestamp: -1 });
revenueShareSchema.index({ userAddress: 1, timestamp: -1 });

// Analytics Schema (for caching)
const analyticsSchema = new mongoose.Schema({
  type: {
    type: String,
    required: true,
    index: true
  },
  period: {
    type: String, // 'daily', 'weekly', 'monthly'
    required: true
  },
  date: {
    type: Date,
    required: true,
    index: true
  },
  data: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true,
    expires: 604800 // TTL: 7 days
  }
}, {
  timestamps: false
});

// Compound indexes
analyticsSchema.index({ type: 1, period: 1, date: -1 });

// Listing Schema (for marketplace listings)
const listingSchema = new mongoose.Schema({
  listingId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  nftId: {
    type: String,
    required: true,
    index: true
  },
  seller: {
    type: String,
    required: true,
    index: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  currency: {
    type: String,
    default: 'XTZ'
  },
  auctionMode: {
    type: Boolean,
    default: false
  },
  minimumBid: {
    type: Number,
    min: 0,
    default: null
  },
  buyNowPrice: {
    type: Number,
    min: 0,
    default: null
  },
  currentBid: {
    type: Number,
    min: 0,
    default: 0
  },
  highestBidder: {
    type: String,
    default: null
  },
  status: {
    type: String,
    enum: ['active', 'sold', 'cancelled', 'expired'],
    default: 'active',
    index: true
  },
  views: {
    type: Number,
    default: 0
  },
  favorites: {
    type: Number,
    default: 0
  },
  soldTo: {
    type: String,
    default: null
  },
  soldAt: {
    type: Date,
    default: null
  },
  soldPrice: {
    type: Number,
    default: null
  },
  expiresAt: {
    type: Date,
    required: true,
    index: true
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Indexes
listingSchema.index({ seller: 1, status: 1 });
listingSchema.index({ price: 1, status: 1 });
listingSchema.index({ createdAt: -1, status: 1 });
listingSchema.index({ expiresAt: 1, status: 1 });

// Offer Schema (for bids and offers)
const offerSchema = new mongoose.Schema({
  offerId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  listingId: {
    type: String,
    index: true,
    default: null
  },
  nftId: {
    type: String,
    required: true,
    index: true
  },
  offerer: {
    type: String,
    required: true,
    index: true
  },
  amount: {
    type: Number,
    required: true,
    min: 0
  },
  currency: {
    type: String,
    default: 'XTZ'
  },
  status: {
    type: String,
    enum: ['pending', 'accepted', 'rejected', 'cancelled', 'expired'],
    default: 'pending',
    index: true
  },
  acceptedAt: {
    type: Date,
    default: null
  },
  rejectedAt: {
    type: Date,
    default: null
  },
  expiresAt: {
    type: Date,
    required: true,
    index: true
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Indexes
offerSchema.index({ nftId: 1, status: 1 });
offerSchema.index({ offerer: 1, status: 1 });
offerSchema.index({ amount: -1 });
offerSchema.index({ expiresAt: 1, status: 1 });

// Marketplace Transaction Schema
const marketplaceTransactionSchema = new mongoose.Schema({
  transactionId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  type: {
    type: String,
    enum: ['direct_sale', 'offer_accepted', 'auction_win'],
    required: true,
    index: true
  },
  listingId: {
    type: String,
    index: true
  },
  offerId: {
    type: String,
    index: true,
    default: null
  },
  nftId: {
    type: String,
    required: true,
    index: true
  },
  seller: {
    type: String,
    required: true,
    index: true
  },
  buyer: {
    type: String,
    required: true,
    index: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  currency: {
    type: String,
    default: 'XTZ'
  },
  paymentMethod: {
    type: String,
    default: 'wallet'
  },
  platformFee: {
    type: Number,
    required: true,
    min: 0
  },
  sellerReceives: {
    type: Number,
    required: true,
    min: 0
  },
  status: {
    type: String,
    enum: ['pending', 'completed', 'failed', 'refunded'],
    default: 'completed',
    index: true
  },
  txHash: {
    type: String,
    default: null,
    sparse: true
  },
  timestamp: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: false
});

// Indexes
marketplaceTransactionSchema.index({ seller: 1, timestamp: -1 });
marketplaceTransactionSchema.index({ buyer: 1, timestamp: -1 });
marketplaceTransactionSchema.index({ nftId: 1, timestamp: -1 });
marketplaceTransactionSchema.index({ type: 1, timestamp: -1 });

// Guild Membership Schema (for tracking member stats per guild)
const guildMembershipSchema = new mongoose.Schema({
  guildId: {
    type: String,
    required: true,
    index: true
  },
  userAddress: {
    type: String,
    required: true,
    index: true
  },
  role: {
    type: String,
    enum: ['founder', 'admin', 'member'],
    default: 'member',
    index: true
  },
  captures: {
    type: Number,
    default: 0,
    min: 0
  },
  revenue: {
    type: Number,
    default: 0,
    min: 0
  },
  joinedAt: {
    type: Date,
    default: Date.now,
    index: true
  }
}, {
  timestamps: true
});

// Indexes
guildMembershipSchema.index({ guildId: 1, userAddress: 1 }, { unique: true });
guildMembershipSchema.index({ userAddress: 1, joinedAt: -1 });
guildMembershipSchema.index({ captures: -1 });
guildMembershipSchema.index({ revenue: -1 });

// Create models
const Guild = mongoose.model('Guild', guildSchema);
const NFT = mongoose.model('NFT', nftSchema);
const User = mongoose.model('User', userSchema);
const Event = mongoose.model('Event', eventSchema);
const Transaction = mongoose.model('Transaction', transactionSchema);
const AlgorithmRental = mongoose.model('AlgorithmRental', algorithmRentalSchema);
const RevenueShare = mongoose.model('RevenueShare', revenueShareSchema);
const Analytics = mongoose.model('Analytics', analyticsSchema);
const Listing = mongoose.model('Listing', listingSchema);
const Offer = mongoose.model('Offer', offerSchema);
const MarketplaceTransaction = mongoose.model('MarketplaceTransaction', marketplaceTransactionSchema);
const GuildMembership = mongoose.model('GuildMembership', guildMembershipSchema);

module.exports = {
  Guild,
  NFT,
  User,
  Event,
  Transaction,
  AlgorithmRental,
  RevenueShare,
  Analytics,
  Listing,
  Offer,
  MarketplaceTransaction,
  GuildMembership
};
