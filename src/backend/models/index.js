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

// Create models
const Guild = mongoose.model('Guild', guildSchema);
const NFT = mongoose.model('NFT', nftSchema);
const User = mongoose.model('User', userSchema);
const Event = mongoose.model('Event', eventSchema);
const Transaction = mongoose.model('Transaction', transactionSchema);
const AlgorithmRental = mongoose.model('AlgorithmRental', algorithmRentalSchema);
const RevenueShare = mongoose.model('RevenueShare', revenueShareSchema);
const Analytics = mongoose.model('Analytics', analyticsSchema);

module.exports = {
  Guild,
  NFT,
  User,
  Event,
  Transaction,
  AlgorithmRental,
  RevenueShare,
  Analytics
};
