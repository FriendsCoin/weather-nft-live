# WeatherNFT.live

Revolutionary NFT project that captures unique weather moments as tradeable digital assets. Instead of buying static images, users "hunt" live weather events detected by AI algorithms around the globe.

## 🌩️ Concept

**Traditional NFTs**: Static Collection → Browse → Buy  
**WeatherNFT**: Live Weather Stream → AI Detection → Capture Moment → Unique NFT

## 🎯 Core Features

### Real-Time Weather Monitoring
- **5 AI Algorithms** continuously scan global weather patterns
- **Storm Hunter**: Detects severe weather formation
- **Aurora Predictor**: Identifies northern lights probability  
- **Micro Climate**: Finds unusual local conditions
- **Extreme Weather**: Tracks dangerous conditions
- **Temperature Anomaly**: Spots unusual temperature patterns

### Live Capture System
- Events appear for limited time (15-120 minutes)
- Limited capture slots per event (1-20 depending on rarity)
- Real-time bidding and FOMO mechanics
- WebSocket live stream for instant notifications

### Guild Economy
- Guilds rent AI algorithms monthly (1-4 XTZ/month)
- Members get priority access to events from their algorithms
- 15% revenue share from captures back to guild
- Collaborative weather hunting community

### Rarity & Economics
- **Common** (1x): Everyday weather patterns
- **Uncommon** (2x): Notable conditions  
- **Rare** (5x): Significant weather events
- **Epic** (10x): Extreme phenomena
- **Legendary** (30x): Once-in-a-lifetime events

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│  React + WebSocket + Taquito (Tezos integration)               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                       BACKEND API                               │
│  Node.js + Express + MongoDB + Redis (caching)                 │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Weather API │  │ AI Engine  │  │ NFT Manager │             │
│  │ Aggregator  │  │ (Event Det.)│  │ (IPFS+Meta) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    BLOCKCHAIN LAYER                             │
│  Tezos Smart Contracts (SmartPy)                              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ NFT Contract│  │Guild Manager│  │Event Manager│             │
│  │   (FA2)     │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
git clone <repository>
cd weather-nft-live

# Start all services
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:3001
# WebSocket: ws://localhost:8080/ws
```

### Manual Setup
```bash
# Backend
cd backend
npm install
cp .env.example .env  # Add your API keys
npm run dev

# Frontend (new terminal)
cd frontend
npm install
npm start

# MongoDB and Redis required
```

### Required API Keys
1. **OpenWeatherMap**: https://openweathermap.org/api
2. **WeatherAPI**: https://www.weatherapi.com/
3. **NOAA** (optional): https://www.weather.gov/documentation/services-web-api

## 💰 Business Model

### Revenue Streams
1. **Event Captures** (60%): Primary revenue from NFT sales
2. **Guild Subscriptions** (25%): Monthly AI algorithm rentals
3. **Marketplace Fees** (15%): Secondary market transactions

### Pricing Structure
- **Base Price**: 0.5 XTZ per capture
- **Rarity Multipliers**: 1x → 30x based on event uniqueness
- **Algorithm Rentals**: 1-4 XTZ/month per algorithm
- **Guild Revenue Share**: 15% of captures through guild algorithms

## 🎨 AI Art Generation

Each captured weather event generates unique visual NFT:
- **Multi-provider generators** — Stability AI (SD3/SDXL), FLUX via fal.ai &
  Replicate, OpenAI gpt-image, self-hosted SD, with automatic fallback to a
  procedural renderer (always available, zero keys)
- **Dynamic prompts** from temperature, humidity, wind, location
- **Deterministic seeding** so identical conditions reproduce the same art
- **IPFS storage** for decentralized metadata

## 🧠 Modern Detection & 🤖 Autonomous Agents

Recent modernization adds three subsystems (see
[docs/MODERN_GENERATORS_AND_AGENTS.md](./docs/MODERN_GENERATORS_AND_AGENTS.md)):

- **Modern generators** (`src/backend/generators/`) — pluggable image providers
  with a priority-ordered auto-fallback registry.
- **Modern algorithms** (`src/backend/algorithms/`) — a climatology-aware
  detection ensemble that scores anomalies by z-score and fuses multi-factor
  signals into a calibrated confidence (`GET /api/weather/detect-events?engine=v2`,
  `GET /api/algorithms`).
- **Agency** (`src/backend/agents/`) — the **WeatherHunter** agent autonomously
  perceives → reasons → decides → acts (scan, detect, generate, mint, notify)
  under an explicit budget/cooldown policy.

```bash
npm run agent        # run the autonomous hunter + status API (:3013)
npm run agent:once   # single dry-run cycle (no minting, no external deps)
```

## 📊 Current Status

✅ **Phase 1 Complete** (MVP Ready):
- ✅ Backend API with weather aggregation
- ✅ 5 AI weather detection algorithms
- ✅ WebSocket real-time event streaming
- ✅ Tezos smart contracts (FA2 NFT + Event Manager)
- ✅ React frontend with wallet integration
- ✅ MongoDB/Redis infrastructure
- ✅ Docker deployment setup

🔄 **Phase 2** (In Progress):
- 🔄 AI art generation pipeline
- 🔄 IPFS integration for NFT storage
- 📋 Guild management system
- 📋 Advanced analytics dashboard

📋 **Phase 3** (Planned):
- 📋 Mobile application
- 📋 Marketplace integration
- 📋 Advanced ML weather prediction
- 📋 Community governance features

## 🌍 Live Demo

Visit **WeatherNFT.live** to see the system in action:
- Real-time weather events from around the globe
- Connect Tezos wallet (Ghostnet testnet)
- Capture unique weather moments as NFTs
- Join weather hunting guilds

## 📚 Documentation

- [Setup Guide](./docs/SETUP.md) - Complete installation instructions
- [API Documentation](./docs/API.md) - Backend API reference
- [Smart Contracts](./smart-contracts/) - Tezos contract source code
- [Architecture](./docs/ARCHITECTURE.md) - Technical deep dive

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🔗 Links

- **Website**: https://weathernft.live
- **Discord**: [WeatherNFT Community]
- **Twitter**: [@WeatherNFT]
- **Documentation**: [GitBook Docs]

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for the future of weather data and NFTs*