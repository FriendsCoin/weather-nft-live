# 🎮 WeatherNFT Demo Guide

## Complete User Experience Simulation

This guide will walk you through experiencing the entire WeatherNFT platform in two different ways:
1. **Interactive Web Demo** - Visual browser-based simulation
2. **CLI Demo** - Terminal-based complete workflow

---

## 🌐 Method 1: Interactive Web Demo (Recommended)

### Quick Start

1. **Start all services:**
```bash
npm run dev
```

2. **Open the demo page:**
```
http://localhost:8081/demo-ux.html
```

3. **Configure your weather event:**
   - Choose weather condition (stormy, rainy, snowy, etc.)
   - Select rarity level (common → legendary)
   - Pick a location
   - Choose AI algorithm

4. **Click "Start User Experience Simulation"**

5. **Watch the magic happen:**
   - ✅ Weather event detection
   - ✅ Guild creation & algorithm rental
   - ✅ AI art generation from weather data
   - ✅ NFT creation & IPFS upload
   - ✅ Revenue distribution

### What You'll See

The demo shows a real-time simulation with:
- **Live progress tracking** through each step
- **Visual feedback** with color-coded status
- **NFT preview** with generated art
- **Revenue statistics** showing guild/user split
- **Console logs** showing API calls
- **Final results** with all metadata

### Customization Options

#### Weather Conditions
- ⚡ **Stormy** - Lightning, dark clouds, heavy rain
- 🌧️ **Rainy** - Rain drops, water effects
- ❄️ **Snowy** - Snowflakes, white gradient
- ☀️ **Clear** - Sun with glow, blue sky
- ☁️ **Cloudy** - Cloud formations
- 🌫️ **Foggy** - Mist layers

#### Rarity Levels
- **Common** (1x) - Basic quality, everyday events
- **Uncommon** (2x) - Notable conditions
- **Rare** (5x) - Significant weather events
- **Epic** (10x) - Extreme phenomena
- **Legendary** (30x) - Once-in-a-lifetime events

Higher rarity = Better art quality + Higher value

#### Locations
- Miami, USA
- Tokyo, Japan
- London, UK
- Sydney, Australia
- Reykjavik, Iceland

#### AI Algorithms
- **Storm Hunter** (4 XTZ/mo) - 97.8% accuracy
- **Aurora Predictor** (3 XTZ/mo) - 89.3% accuracy
- **Micro Climate** (2 XTZ/mo) - 91.5% accuracy
- **Extreme Weather** (4 XTZ/mo) - 96.1% accuracy
- **Temperature Anomaly** (1 XTZ/mo) - 94.2% accuracy

---

## 💻 Method 2: CLI Demo Script

### Quick Start

1. **Start all services:**
```bash
npm run dev
```

2. **In a new terminal, run the demo:**
```bash
npm run demo
```

### What It Does

The CLI demo simulates a complete user journey:

#### Phase 1: System Health Check ✅
```
✅ NFT Service: OK
✅ Guild Service: OK
ℹ️  IPFS Provider: pinata
ℹ️  Active Guilds: 1
```

#### Phase 2: Weather Event Detection 🌩️
```
📡 AI Algorithm: Storm Hunter
   Location: Miami, USA
   Event Type: SEVERE_THUNDERSTORM
   Temperature: 28°C
   Wind Speed: 65 km/h
   Humidity: 85%
   Rarity: EPIC
✅ Severe weather event detected!
```

#### Phase 3: Guild Creation 🏛️
```
✅ Guild created: "Elite Storm Chasers"
   Guild ID: guild_1699564800123_abc
   Founder: Alice (Weather Hunter)
   Members: 1

✅ Algorithm rented successfully!
   Algorithm: Storm Hunter
   Monthly Cost: 4 XTZ
   Accuracy: 97.8%
   Specialization: thunderstorms, hurricanes
```

#### Phase 4: AI Art Generation 🎨
```
✅ AI art generated!
   Format: image/png
   Size: 45.67 KB
   Weather effects applied: Stormy conditions with lightning
```

#### Phase 5: NFT Creation & IPFS Upload 📦
```
✅ NFT created successfully!
──────────────────────────────────────────────────────────
NFT Details:
   Event ID: evt_1699564800123
   Image Hash: QmXyZ123...
   Metadata Hash: QmAbc456...
   Image URL: https://gateway.pinata.cloud/ipfs/QmXyZ123...
   Metadata URL: https://gateway.pinata.cloud/ipfs/QmAbc456...
   Status: ready_to_mint
──────────────────────────────────────────────────────────
ℹ️  NFT is ready for blockchain minting!
```

#### Phase 6: Revenue Distribution 💰
```
✅ Revenue distributed!
──────────────────────────────────────────────────────────
Revenue Breakdown:
   Total Capture Price: 15 XTZ
   Guild Share (15%): 2.25 XTZ
   User Share (85%): 12.75 XTZ
──────────────────────────────────────────────────────────
ℹ️  Total Guild Revenue: 2.25 XTZ
ℹ️  User Total Captures: 1
```

#### Phase 7: Guild Leaderboard 🏆
```
✅ Guild leaderboard retrieved!
──────────────────────────────────────────────────────────
Top Guilds:

#1 Elite Storm Chasers
   Revenue: 2.25 XTZ
   Captures: 1
   Members: 1
   Algorithms: 1
──────────────────────────────────────────────────────────
```

#### Phase 8: Summary 📊
```
Complete User Experience Simulation

What Happened:

1. 🌩️  AI detected severe thunderstorm in Miami
2. 🏛️  User created guild "Elite Storm Chasers"
3. 🤖 Guild rented "Storm Hunter" algorithm
4. 🎨 AI generated unique art from weather conditions
5. 📦 NFT uploaded to IPFS with metadata
6. 💎 NFT ready for blockchain minting
7. 💰 Revenue distributed: 2.25 XTZ to guild, 12.75 XTZ to user
8. 🏆 Guild statistics updated on leaderboard

User Benefits:
✅ Unique, one-of-a-kind weather NFT
✅ AI-generated art based on real weather data
✅ Decentralized storage on IPFS
✅ Guild collaboration and revenue sharing
✅ Priority access to weather events
✅ Competitive leaderboard ranking

Next Steps:
1. View NFT on IPFS: https://gateway.pinata.cloud/ipfs/...
2. Mint NFT on Tezos blockchain
3. List NFT on marketplace
4. Track weather events in real-time
```

---

## 🔧 Configuration for Full Demo

### IPFS Setup (For NFT Upload)

To see actual IPFS uploads in the demo:

1. **Sign up for Pinata** (recommended):
   - Visit https://pinata.cloud
   - Create free account
   - Get API keys from dashboard

2. **Configure environment:**
```bash
cp .env.example .env
```

3. **Add your Pinata keys to `.env`:**
```env
IPFS_PROVIDER=pinata
PINATA_API_KEY=your_actual_api_key
PINATA_SECRET_KEY=your_actual_secret_key
```

4. **Restart services:**
```bash
npm run dev
```

Now the demo will upload real images and metadata to IPFS!

### Without IPFS (Simulation Only)

If you don't configure IPFS:
- Demo will still work
- Art generation happens normally
- IPFS upload will be simulated
- You'll see helpful messages explaining setup

---

## 🎯 What Each Demo Shows

### Web Demo Features
- ✅ Visual step-by-step progress
- ✅ Interactive configuration
- ✅ Real-time status updates
- ✅ NFT art preview
- ✅ Revenue statistics
- ✅ Console logging
- ✅ Error handling with friendly messages

### CLI Demo Features
- ✅ Complete workflow automation
- ✅ Colored console output
- ✅ Detailed logging
- ✅ API call tracking
- ✅ Guild leaderboard
- ✅ Final summary with next steps

---

## 🧪 Testing Different Scenarios

### Scenario 1: Epic Storm Event
```
Condition: Stormy
Rarity: Epic
Location: Miami
Algorithm: Storm Hunter
Expected Revenue: ~15 XTZ capture price
```

### Scenario 2: Legendary Aurora
```
Condition: Clear (for northern lights)
Rarity: Legendary
Location: Reykjavik
Algorithm: Aurora Predictor
Expected Revenue: ~45 XTZ capture price (30x multiplier)
```

### Scenario 3: Rare Snowstorm
```
Condition: Snowy
Rarity: Rare
Location: Tokyo
Algorithm: Extreme Weather
Expected Revenue: ~7.5 XTZ capture price (5x multiplier)
```

---

## 📊 Understanding the Results

### Revenue Split
```
Capture Price: X XTZ
├─ Guild (15%): 0.15X XTZ
└─ User (85%): 0.85X XTZ
```

Example with 15 XTZ capture:
- Guild gets: 2.25 XTZ
- User gets: 12.75 XTZ

### NFT Metadata
Every generated NFT includes:
- Unique AI-generated art
- Weather data (temp, wind, humidity, etc.)
- Location coordinates
- Capture timestamp
- Rarity level
- AI algorithm used
- IPFS hashes for image & metadata

### Guild Benefits
- 15% passive income from member captures
- Access to rented AI algorithms
- Leaderboard ranking
- Community collaboration
- Priority event access

---

## 🚨 Troubleshooting

### Services Not Running
```bash
# Check if services are running
curl http://localhost:3009/health  # NFT Service
curl http://localhost:3010/health  # Guild Service

# If not running, start them:
npm run dev
```

### IPFS Errors
```
Error: "IPFS upload failed"
```
**Solution**: Either configure Pinata API keys or ignore - demo works in simulation mode

### Port Already in Use
```
Error: Port 3009 already in use
```
**Solution**:
```bash
./scripts/stop-all.sh
npm run dev
```

---

## 🎁 Demo Tips

1. **Try Different Weather Conditions**
   - Each condition creates unique visual art
   - Stormy events have lightning effects
   - Snowy events have falling flakes
   - Clear events have sun visualization

2. **Experiment with Rarity**
   - Higher rarity = better art quality
   - Legendary events are 30x more valuable
   - Epic events have enhanced effects

3. **Compare Algorithms**
   - Each algorithm has different pricing
   - Higher cost = better accuracy
   - Choose based on event type

4. **Watch the Console**
   - Web demo: Browser console (F12)
   - CLI demo: Terminal output
   - See actual API calls and responses

---

## 📚 Next Steps After Demo

1. **Explore the Code**
   - Check `src/backend/nft-service.js` for NFT logic
   - Review `src/backend/ai-art-generator.js` for art generation
   - See `src/backend/guild-service.js` for guild management

2. **Test Individual Services**
   ```bash
   npm run nft      # NFT service only
   npm run guild    # Guild service only
   ```

3. **Read Full Documentation**
   - `FEATURES.md` - Complete feature documentation
   - `README.md` - Project overview
   - `STRUCTURE.md` - Project structure

4. **Deploy to Production**
   - Review `docs/deployment/` guides
   - Configure production IPFS
   - Set up Tezos blockchain integration

---

## 🎉 Enjoy the Demo!

The demo showcases the complete WeatherNFT experience:
- Real-time weather detection
- AI-powered art generation
- Decentralized NFT storage
- Guild-based collaboration
- Fair revenue sharing
- Competitive leaderboards

**Try it now:**
```bash
npm run dev              # Start services
npm run demo             # CLI demo
# or visit http://localhost:8081/demo-ux.html
```

Happy weather hunting! 🌦️⚡🎨
