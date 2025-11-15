# 📁 Project Structure

## Clean Directory Organization

```
weather-nft-live/
├── 📂 src/                          # Source code
│   ├── backend/                     # Backend services
│   │   ├── simple-test-server.js    # AI Backend (Port 3006)
│   │   ├── blockchain-service.js    # Blockchain Service (Port 3007)
│   │   ├── admin-backend.js         # Admin API (Port 3008)
│   │   ├── admin-dashboard.js       # Admin Dashboard Logic
│   │   ├── simple-server.js         # Simple Backend Server
│   │   ├── sd-pytorch-integration.py # Real SD AI (Port 8000)
│   │   └── simple-sd-ai-mock.py     # Mock SD AI (Port 8000)
│   │
│   └── frontend/                    # Frontend services
│       └── simple-frontend-server.js # Frontend Server (Port 8081)
│
├── 📂 public/                       # Web interface files
│   ├── index.html                   # Landing page
│   ├── marketplace-inspired.html    # Main marketplace
│   ├── admin-futuristic.html       # Admin panel
│   ├── admin-test.html             # Admin test interface
│   └── test-purchase.html          # Purchase flow test
│
├── 📂 scripts/                      # Management scripts
│   ├── restart-all.sh              # Start all services
│   ├── stop-all.sh                 # Stop all services
│   ├── status.sh                   # Check service status
│   ├── start-pytorch-ai.sh         # Start PyTorch AI
│   ├── start-sd-ai.sh              # Start SD AI
│   ├── switch-to-real-sd.sh        # Switch to real SD
│   └── test-real-sd.sh             # Test real SD integration
│
├── 📂 docs/                         # Documentation
│   ├── SETUP.md                     # Main setup guide
│   ├── deployment/                  # Deployment guides
│   │   ├── DOCKER_QUICK_START.md
│   │   ├── HYBRID_DEPLOYMENT_GUIDE.md
│   │   ├── VERCEL_DEPLOY_GUIDE.md
│   │   └── ...
│   ├── guides/                      # Integration guides
│   │   ├── SD_AI_INTEGRATION_GUIDE.md
│   │   ├── MANAGEMENT_SCRIPTS.md
│   │   ├── CONNECT_REAL_SD.md
│   │   └── ...
│   └── archive/                     # Archived documentation
│       └── ...
│
├── 📂 api/                          # API routes
│   └── test.js                      # API test endpoints
│
├── 📂 archive/                      # Archived/unused files
│   ├── windows-scripts/             # Windows batch files
│   └── nft-market-place.animaapp.io.mhtml
│
├── 📄 package.json                  # Node.js dependencies
├── 📄 requirements.txt              # Python dependencies
├── 📄 requirements-pytorch.txt      # PyTorch dependencies
├── 📄 docker-compose.dev.yml        # Docker development config
├── 📄 Dockerfile.railway            # Railway deployment
├── 📄 Dockerfile.sd-dev             # SD AI Docker config
├── 📄 railway.toml                  # Railway config
├── 📄 render.yaml                   # Render config
├── 📄 vercel.json                   # Vercel config
└── 📄 README.md                     # Project documentation
```

## NPM Scripts

All services can be started using npm scripts:

```bash
# Start frontend server (Port 8081)
npm start

# Start all services (development mode)
npm run dev

# Individual services
npm run backend      # Backend API server
npm run test         # AI Backend server
npm run admin        # Admin backend
npm run blockchain   # Blockchain service

# AI services
npm run ai:mock      # Mock SD AI (for testing)
npm run ai:real      # Real SD AI (requires PyTorch)
```

## Service Ports

| Service | Port | Script |
|---------|------|--------|
| Frontend Server | 8081 | `npm start` |
| AI Backend | 3006 | `npm run test` |
| Blockchain Service | 3007 | `npm run blockchain` |
| Admin Backend | 3008 | `npm run admin` |
| SD AI (Mock/Real) | 8000 | `npm run ai:mock` or `ai:real` |

## Quick Start

```bash
# Install dependencies
npm install
pip3 install -r requirements.txt

# Start all services
npm run dev

# Access the application
# Frontend: http://localhost:8081
# Admin Panel: http://localhost:8081/admin-futuristic.html
```

## Cleanup Benefits

✅ **Removed:**
- 4 duplicate HTML files from root
- 8 Windows batch files (archived)
- 22MB binary archive file (archived)
- Empty/broken files
- 18 scattered documentation files

✅ **Organized:**
- Source code in `src/backend` and `src/frontend`
- Management scripts in `scripts/`
- Documentation in `docs/` with proper categorization
- Web files in `public/`

✅ **Improved:**
- Clear directory structure
- Updated package.json with all service scripts
- Fixed script paths in restart-all.sh
- Better separation of concerns
- Easier navigation and maintenance
