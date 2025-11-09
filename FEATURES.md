# 🚀 WeatherNFT New Features

## Summary of Implemented Features (Phase 2)

All features have been implemented, tested, and pushed to the repository.

---

## 1. IPFS Integration for NFT Storage ✅

### Overview
Complete IPFS integration supporting multiple providers for decentralized NFT storage.

### Features Implemented
- ✅ Multi-provider support (Pinata, Infura, Local IPFS node)
- ✅ Image upload to IPFS with automatic hashing
- ✅ Metadata upload in standard NFT format
- ✅ Configurable IPFS gateways
- ✅ Connection testing and validation

### API Endpoints
```
POST /api/ipfs/upload/image     - Upload image to IPFS
POST /api/ipfs/upload/metadata  - Upload metadata to IPFS
GET  /api/ipfs/test             - Test IPFS connection
```

### Configuration
```env
IPFS_PROVIDER=pinata
PINATA_API_KEY=your_key
PINATA_SECRET_KEY=your_secret
```

### Usage Example
```bash
npm run nft
# Server starts on http://localhost:3009
```

---

## 2. AI Art Generation with Weather Data ✅

### Overview
Intelligent art generation system that creates unique visual NFTs based on real-time weather conditions.

### Features Implemented
- ✅ Procedural art generation from weather data
- ✅ Weather-specific visual effects:
  - Rain with dynamic droplets
  - Snow with animated flakes
  - Lightning with electric bolts
  - Sun with radiant glow
  - Clouds with realistic formations
  - Fog with atmospheric layers
  - Wind visualization
- ✅ Stable Diffusion integration support
- ✅ Dynamic prompt generation
- ✅ Rarity-based quality levels
- ✅ Data visualization overlays

### API Endpoints
```
POST /api/art/generate            - Generate AI art from weather data
POST /api/nft/create-with-art     - Create complete NFT with auto-generated art
```

### Weather Effects
| Condition | Effects |
|-----------|---------|
| Clear | Sun with glow, blue sky gradient |
| Rainy | Rain drops, water effects |
| Stormy | Lightning bolts, dark clouds, heavy rain |
| Snowy | Falling snowflakes, white gradient |
| Cloudy | Cloud formations, gray tones |
| Foggy | Mist layers, atmospheric effects |

### Generation Parameters
- **Temperature**: Affects color palette
- **Wind Speed**: Adds motion blur and wind lines
- **Humidity**: Controls particle density
- **Rarity**: Determines generation quality
  - Common: Basic 30 steps
  - Rare: Enhanced 40 steps
  - Legendary: Premium 50 steps

### Usage Example
```bash
# Generate art only
curl -X POST http://localhost:3009/api/art/generate \
  -H "Content-Type: application/json" \
  -d '{
    "weatherData": {"temperature": 25, "conditions": "stormy"},
    "eventData": {"type": "thunderstorm", "timestamp": 1699564800000},
    "location": {"city": "NewYork", "country": "USA"},
    "rarity": "rare"
  }'

# Create NFT with auto-generated art
curl -X POST http://localhost:3009/api/nft/create-with-art \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "evt_001",
    "weatherData": {...},
    "eventData": {...},
    "location": {...}
  }'
```

---

## 3. NFT Metadata Generation System ✅

### Overview
Standard-compliant NFT metadata generation following OpenSea and Tezos FA2 specifications.

### Features Implemented
- ✅ OpenSea metadata standard compliance
- ✅ Attribute generation from weather data
- ✅ IPFS URI format support
- ✅ Rarity system integration
- ✅ Location and timestamp tracking
- ✅ AI algorithm attribution

### Metadata Structure
```json
{
  "name": "WeatherNFT #001",
  "description": "A unique weather NFT capturing a thunderstorm...",
  "image": "ipfs://QmHash...",
  "external_url": "https://weathernft.live/nft/001",
  "attributes": [
    {"trait_type": "Event Type", "value": "Thunderstorm"},
    {"trait_type": "Rarity", "value": "Rare"},
    {"trait_type": "Temperature", "value": 25, "display_type": "number"},
    {"trait_type": "Wind Speed", "value": 45, "display_type": "number"},
    {"trait_type": "Humidity", "value": 85, "display_type": "number"},
    {"trait_type": "Location", "value": "New York, USA"},
    {"trait_type": "AI Algorithm", "value": "Storm Hunter"}
  ],
  "properties": {
    "weather": {...},
    "event": {...},
    "location": {...}
  }
}
```

### API Endpoints
```
POST /api/metadata/preview  - Preview metadata before minting
POST /api/nft/create        - Create NFT with custom image
GET  /api/nft/:eventId      - Get NFT from minting queue
GET  /api/nfts              - Get all NFTs in queue
PUT  /api/nft/:eventId/status - Update NFT minting status
```

---

## 4. Guild Management System ✅

### Overview
Complete guild economy system for collaborative weather hunting with algorithm rentals and revenue sharing.

### Features Implemented
- ✅ Guild creation and management
- ✅ Member management system
- ✅ AI algorithm rental marketplace
- ✅ Revenue sharing (15% guild / 85% user)
- ✅ Guild leaderboard
- ✅ Member statistics
- ✅ Revenue history tracking

### Available AI Algorithms

| Algorithm | Price/Month | Accuracy | Specialization |
|-----------|-------------|----------|----------------|
| Storm Hunter | 4 XTZ | 97.8% | Thunderstorms, hurricanes |
| Extreme Weather | 4 XTZ | 96.1% | Extreme temperatures |
| Aurora Predictor | 3 XTZ | 89.3% | Northern lights |
| Temperature Anomaly | 1 XTZ | 94.2% | Heat waves, cold snaps |
| Micro Climate | 2 XTZ | 91.5% | Local anomalies |

### Guild Features
- Create guilds with custom name and description
- Invite unlimited members
- Rent up to 5 different AI algorithms
- 15% revenue share on all member captures
- Priority access to events from rented algorithms
- Track total guild revenue and captures
- Member performance statistics

### API Endpoints
```
GET  /api/algorithms                - List all available algorithms
GET  /api/algorithms/:id            - Algorithm details
POST /api/guilds/create             - Create new guild
GET  /api/guilds                    - List all guilds
GET  /api/guilds/:id                - Guild details with members
POST /api/guilds/:id/join           - Join a guild
POST /api/guilds/:id/rent-algorithm - Rent algorithm for guild
POST /api/guilds/capture-event      - Record capture & distribute revenue
GET  /api/user/:address/guilds      - User's guild memberships
GET  /api/guilds/:id/revenue        - Guild revenue history
GET  /api/leaderboard               - Top guilds by revenue
```

### Revenue Sharing Example
```
Capture Price: 10 XTZ
├─ Guild Share (15%): 1.5 XTZ
└─ User Share (85%): 8.5 XTZ

Guild stats updated:
- Total revenue: +1.5 XTZ
- Total captures: +1

Member stats updated:
- Captures: +1
- Revenue: +8.5 XTZ
```

### Usage Example
```bash
npm run guild
# Server starts on http://localhost:3010

# Create a guild
curl -X POST http://localhost:3010/api/guilds/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Storm Chasers",
    "description": "Elite weather hunters",
    "founder": "tz1abc..."
  }'

# Rent an algorithm
curl -X POST http://localhost:3010/api/guilds/guild_123/rent-algorithm \
  -H "Content-Type: application/json" \
  -d '{
    "algorithmId": "storm-hunter",
    "txHash": "op123..."
  }'

# Join a guild
curl -X POST http://localhost:3010/api/guilds/guild_123/join \
  -H "Content-Type: application/json" \
  -d '{"userAddress": "tz1xyz..."}'
```

---

## 📊 Services Overview

### All Active Services

| Service | Port | Command | Purpose |
|---------|------|---------|---------|
| Frontend Server | 8081 | `npm start` | Main web interface |
| AI Backend | 3006 | `npm run test` | Weather AI algorithms |
| Blockchain Service | 3007 | `npm run blockchain` | Tezos integration |
| Admin Backend | 3008 | `npm run admin` | Admin panel API |
| **NFT Service** | **3009** | `npm run nft` | **NFT creation & IPFS** |
| **Guild Service** | **3010** | `npm run guild` | **Guild management** |
| SD AI Mock | 8000 | `npm run ai:mock` | AI mock server |

### Start All Services
```bash
npm run dev
# or
./scripts/restart-all.sh
```

---

## 🎯 Complete Workflow Example

### Create Weather NFT with Guild

```javascript
// 1. Generate AI art from weather event
const artResponse = await fetch('http://localhost:3009/api/art/generate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    weatherData: {
      temperature: 28,
      humidity: 75,
      windSpeed: 55,
      pressure: 1005,
      conditions: 'stormy'
    },
    eventData: {
      type: 'severe_thunderstorm',
      timestamp: Date.now()
    },
    location: {
      city: 'Miami',
      country: 'USA',
      lat: 25.7617,
      lng: -80.1918
    },
    rarity: 'epic'
  })
});

// 2. Create NFT with generated art and upload to IPFS
const nftResponse = await fetch('http://localhost:3009/api/nft/create-with-art', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    eventId: 'evt_miami_001',
    weatherData: {...},
    eventData: {...},
    location: {...},
    owner: 'tz1abc123...',
    rarity: 'epic',
    algorithm: 'Storm Hunter'
  })
});

// 3. Record capture in guild and distribute revenue
const guildResponse = await fetch('http://localhost:3010/api/guilds/capture-event', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    guildId: 'guild_stormchasers',
    userAddress: 'tz1abc123...',
    algorithmId: 'storm-hunter',
    eventId: 'evt_miami_001',
    capturePrice: 10 // XTZ
  })
});

// Result:
// - NFT created with AI-generated art
// - Uploaded to IPFS (image + metadata)
// - Guild receives 1.5 XTZ (15%)
// - User receives 8.5 XTZ (85%)
// - Ready for blockchain minting
```

---

## 📦 Installation & Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - PINATA_API_KEY
# - PINATA_SECRET_KEY
# - TEZOS_RPC_URL
# - etc.
```

### 3. Start Services
```bash
# All services
npm run dev

# Individual services
npm run nft      # NFT service
npm run guild    # Guild service
npm run blockchain # Blockchain service
```

### 4. Test Endpoints
```bash
# Health checks
curl http://localhost:3009/health  # NFT service
curl http://localhost:3010/health  # Guild service

# Test IPFS connection
curl http://localhost:3009/api/ipfs/test
```

---

## 🔧 Development Notes

### Dependencies Added
- `ipfs-http-client` - IPFS uploads
- `canvas` - Procedural art generation
- `multer` - File upload handling
- `form-data` - Multipart requests

### Environment Variables
All configuration in `.env.example`. Key variables:
- `IPFS_PROVIDER` - Choose: pinata, infura, or local
- `PINATA_API_KEY` & `PINATA_SECRET_KEY` - For Pinata
- `SD_AI_URL` - Stable Diffusion API endpoint
- `USE_REAL_AI` - Enable real SD (default: false)
- `NFT_SERVICE_PORT` - NFT service port (default: 3009)
- `GUILD_SERVICE_PORT` - Guild service port (default: 3010)

### Testing Tips
1. Start with mock AI for development
2. Test IPFS connection before creating NFTs
3. Use Pinata for reliable IPFS hosting
4. Monitor logs directory for service output
5. Check health endpoints for service status

---

## 🚀 Next Steps

### Phase 3 Features (Future)
- [ ] MongoDB integration for persistent storage
- [ ] Analytics dashboard with real-time stats
- [ ] Marketplace integration
- [ ] Mobile application
- [ ] Advanced ML weather prediction
- [ ] Community governance

### Immediate Improvements
- [ ] Add MongoDB models for guilds and NFTs
- [ ] Implement blockchain minting integration
- [ ] Create admin dashboard for guild management
- [ ] Add WebSocket support for real-time updates
- [ ] Implement caching layer with Redis

---

## 📄 License
MIT License - See LICENSE file for details

---

**Built with ❤️ for the future of weather data and NFTs**
