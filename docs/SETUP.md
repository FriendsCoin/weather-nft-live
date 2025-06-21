# WeatherNFT.live Setup Guide

## Prerequisites

- Node.js 16+ 
- MongoDB
- Redis
- Tezos wallet with Ghostnet XTZ

## API Keys Required

1. **OpenWeatherMap API** - https://openweathermap.org/api
2. **WeatherAPI** - https://www.weatherapi.com/
3. **NOAA API** (optional) - https://www.weather.gov/documentation/services-web-api
4. **NASA API** (optional) - https://api.nasa.gov/

## Quick Setup

### 1. Backend Setup

```bash
cd backend
npm install
cp .env.example .env
```

Edit `.env` with your API keys:
```
MONGODB_URI=mongodb://localhost:27017/weather-nft
REDIS_URL=redis://localhost:6379
OPENWEATHER_API_KEY=your_key_here
WEATHERAPI_KEY=your_key_here
```

Start the backend:
```bash
npm run dev
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

### 3. Smart Contracts (Optional)

```bash
cd smart-contracts
# Deploy using SmartPy CLI or Tezos node
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│  React/Next.js + WebSocket + Taquito (Tezos integration)       │
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

## Key Components

### Weather AI System
- **5 Specialized Algorithms**: Storm Hunter, Aurora Predictor, Micro Climate, Extreme Weather, Temperature Anomaly
- **Real-time Detection**: Scans global weather data every 5 minutes
- **Confidence Scoring**: Each event rated 0-100% confidence
- **Rarity Classification**: Common → Legendary based on uniqueness

### Blockchain Integration
- **Tezos Network**: Low-cost, eco-friendly blockchain
- **FA2 NFT Standard**: Compatible with all Tezos wallets/marketplaces
- **Smart Contracts**: Automated event capture and NFT minting

### Guild System
- **Algorithm Rental**: Guilds rent AI algorithms monthly
- **Revenue Sharing**: 15% of captures go to relevant guild
- **Collaborative**: Members get priority access to events

## Development Status

✅ **Completed:**
- Backend API with weather aggregation
- AI event detection algorithms
- WebSocket real-time streaming
- Tezos smart contracts (FA2 NFT + Event Manager)
- React frontend with wallet integration

🔄 **In Progress:**
- AI art generation pipeline
- IPFS integration for NFT storage

📋 **Planned:**
- Guild management system
- Advanced analytics dashboard
- Mobile app
- Marketplace integration

## Testing

1. **Start Services**:
   ```bash
   # Terminal 1 - Backend
   cd backend && npm run dev
   
   # Terminal 2 - Frontend  
   cd frontend && npm start
   ```

2. **Connect Wallet**: Use Temple/Kukai wallet on Ghostnet

3. **Monitor Events**: AI should detect and display weather events

## API Endpoints

- `GET /api/events/active` - Get current weather events
- `GET /api/weather/current/:lat/:lon` - Get weather data
- `POST /api/events/:id/capture` - Capture weather event
- WebSocket: `ws://localhost:8080/ws` - Real-time events

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Discord: [WeatherNFT Community]

## License

MIT License - See LICENSE file for details