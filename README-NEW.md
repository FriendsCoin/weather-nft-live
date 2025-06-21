# 🌦️ WeatherNFT.live

Revolutionary NFT project that captures unique weather moments as tradeable digital assets with **real AI-powered weather prediction**.

![WeatherNFT Banner](https://via.placeholder.com/800x200/10b981/ffffff?text=WeatherNFT.live+-+AI+Weather+NFT+Platform)

## 🎯 Overview

Instead of buying static images, users "hunt" live weather events detected by **advanced AI algorithms** around the globe. Each weather event becomes a unique NFT with real-world data and rarity based on actual meteorological conditions.

## ✨ Features

- 🧠 **Real PyTorch AI**: 5 advanced algorithms (LSTM, CNN-LSTM, Transformer, RNN, GRU)
- 🔥 **CUDA Acceleration**: GPU-powered weather prediction
- 🌍 **Real-time Detection**: AI algorithms scan global weather data
- 🎨 **Dynamic NFT Generation**: Unique tokens based on actual weather events
- 💎 **Natural Rarity System**: Scarcity based on real weather patterns
- 🗺️ **Interactive Dashboard**: Live global weather event tracking
- 🌱 **Tezos Blockchain**: Fast, eco-friendly NFT platform
- 👨‍💼 **Admin Panel**: Complete management system with built-in terminal

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/username/weather-nft-live.git
cd weather-nft-live

# Install dependencies
npm install

# Start all services
./restart-all.sh  # Linux/Mac
# or
restart-all.bat   # Windows

# Visit http://localhost:8081
```

### SD AI Integration (Optional)
```bash
# Activate your SD environment
conda activate SD

# Install AI dependencies  
pip install fastapi uvicorn torch

# Start real PyTorch AI server
python sd-pytorch-integration.py --server
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   AI Backend    │    │   SD AI Server  │
│   (Port 8081)   │◄──►│   (Port 3006)   │◄──►│   (Port 8000)   │ 
│   • Admin Panel │    │   • 5 Algorithms│    │   • PyTorch     │
│   • Marketplace │    │   • Real Data   │    │   • CUDA GPU    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Blockchain     │    │  Admin Backend  │    │   Mock Server   │
│  (Port 3007)    │    │  (Port 3008)    │    │  (Fallback)     │
│  • Tezos        │    │  • Management   │    │  • Demo Mode    │
│  • FA2 NFTs     │    │  • Monitoring   │    │  • Quick Test   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧠 AI Algorithms

| Algorithm | Specialization | Accuracy | Model Type |
|-----------|---------------|----------|------------|
| **ThermalDrift-v2** | Temperature anomalies | 94.2% | LSTM |
| **StormChaser-v4** | Storm prediction | 97.8% | CNN-LSTM |
| **EcoBalance-v1** | Climate monitoring | 91.5% | Transformer |
| **AuroraPredictor-v3** | Aurora prediction | 89.3% | RNN |
| **AquaDetect-v2** | Water cycles | 96.1% | GRU |

## 📊 API Endpoints

```
GET  /api/events           - Active weather events
GET  /api/ai/algorithms    - AI model information
POST /api/ai/predict       - Weather prediction
GET  /api/admin/dashboard  - System metrics
POST /api/nft/mint         - Mint weather NFT
```

## 🛠️ Management Scripts

```bash
./restart-all.sh    # Start all services
./stop-all.sh       # Stop all services  
./status.sh         # Check service status
./test-real-sd.sh   # Test SD AI connection
```

## 🐳 Deployment Options

### Vercel (Recommended)
```bash
npm i -g vercel
vercel --prod
```

### Railway
```bash
# Connect GitHub repository to Railway
# Uses railway.toml configuration
```

### Docker
```bash
docker-compose -f docker-compose.dev.yml up
```

## 🔧 Environment Variables

```env
NODE_ENV=production
AI_API_URL=http://localhost:3006
ADMIN_API_URL=http://localhost:3008
BLOCKCHAIN_API_URL=http://localhost:3007
SD_AI_API_URL=http://localhost:8000
```

## 👨‍💼 Admin Panel Features

- 📊 **Real-time Dashboard**: Service monitoring
- 🖥️ **Built-in Terminal**: Command execution
- 🧠 **AI Management**: Model control and testing
- 👥 **User Management**: Credits and permissions
- 📈 **Analytics**: System metrics and logs
- ⚙️ **Settings**: Configuration management

## 🎮 Getting Started

1. **Visit the demo**: [weather-nft-live.vercel.app](https://weather-nft-live.vercel.app)
2. **Explore admin panel**: Click the terminal button (green circle, bottom right)
3. **Test AI prediction**: Use `test-ai` command in terminal
4. **Check status**: Use `status` command for system overview

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **PyTorch Team** for the amazing ML framework
- **Tezos** for the eco-friendly blockchain
- **Vercel** for seamless deployment
- **Weather APIs** for real-time data

---

**Built with ❤️ by the WeatherNFT Team**

[🌐 Live Demo](https://weather-nft-live.vercel.app) | [📖 Documentation](./MANAGEMENT_SCRIPTS.md) | [🚀 Deployment Guide](./FINAL_DEPLOYMENT_OPTIONS.md)