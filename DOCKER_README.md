# WeatherNFT Docker Deployment Guide

Complete guide for deploying WeatherNFT platform using Docker and Docker Compose.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Docker Architecture](#docker-architecture)
6. [Environment Variables](#environment-variables)
7. [Health Checks](#health-checks)
8. [Scaling Services](#scaling-services)
9. [Monitoring & Logs](#monitoring--logs)
10. [Troubleshooting](#troubleshooting)
11. [CI/CD Pipeline](#cicd-pipeline)

---

## Quick Start

### Development (Local)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/weather-nft-live.git
cd weather-nft-live

# 2. Deploy with Docker
./scripts/docker-deploy.sh dev

# 3. Access the application
# Frontend: http://localhost:8081
# Auth API: http://localhost:3014/health
```

### Production

```bash
# 1. Copy environment template
cp .env.docker .env

# 2. Edit .env with production credentials
nano .env

# 3. Deploy
./scripts/docker-deploy.sh prod
```

---

## Prerequisites

### Required Software

- **Docker**: v20.10 or later
- **Docker Compose**: v2.0 or later
- **Git**: v2.0 or later

### Installation

#### Ubuntu/Debian

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose version
```

#### macOS

```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose version
```

---

## Development Deployment

### Using Helper Script (Recommended)

```bash
# Deploy all services
./scripts/docker-deploy.sh dev

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f auth-service
```

### Development Features

- ✅ **Hot Reload**: Source code mounted as volumes
- ✅ **Debug Logging**: LOG_LEVEL=debug
- ✅ **Development Databases**: MongoDB and Redis included
- ✅ **Port Mapping**: All services exposed to localhost

### Accessing Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:8081 | Main application |
| Auth API | http://localhost:3014/health | Authentication service |
| NFT API | http://localhost:3009/health | NFT management |
| Marketplace | http://localhost:3013/health | NFT marketplace |
| Guild API | http://localhost:3010/health | Guild management |
| Analytics | http://localhost:3011/health | Analytics service |
| Weather API | http://localhost:3012/health | Weather data |
| WebSocket | ws://localhost:8080 | Real-time updates |
| MongoDB | mongodb://localhost:27017 | Database |
| Redis | redis://localhost:6379 | Cache |

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Domain configured with DNS records
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Strong passwords generated for all services
- [ ] API keys configured (IPFS, Weather APIs)
- [ ] Firewall rules configured
- [ ] Backup strategy in place

### Step-by-Step Production Deployment

#### 1. Prepare Environment

```bash
# Create .env from template
cp .env.docker .env

# Generate strong secrets
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# Edit .env file
nano .env
```

**Required Variables**:
```bash
# MongoDB
MONGO_ROOT_PASSWORD=<strong-password>
MONGO_APP_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# JWT
JWT_SECRET=<64-character-hex-string>
SESSION_SECRET=<64-character-hex-string>

# CORS
ALLOWED_ORIGINS=https://weathernft.com,https://www.weathernft.com

# IPFS
PINATA_API_KEY=<your-api-key>
PINATA_SECRET_KEY=<your-secret-key>

# Weather APIs
OPENWEATHER_API_KEY=<your-api-key>
WEATHERAPI_KEY=<your-api-key>
```

#### 2. Create Required Directories

```bash
# Data directories
sudo mkdir -p /var/lib/weathernft/{mongodb,mongodb-config,redis}
sudo mkdir -p /var/log/weathernft

# Set permissions
sudo chown -R 1001:1001 /var/lib/weathernft
sudo chown -R $USER:$USER /var/log/weathernft
```

#### 3. Deploy Services

```bash
# Using helper script
./scripts/docker-deploy.sh prod

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. Verify Deployment

```bash
# Check service health
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs

# Test health endpoints
curl https://weathernft.com/health
curl https://weathernft.com/api/auth/health
```

### Production Features

- ✅ **Multi-Stage Builds**: Optimized image sizes
- ✅ **Health Checks**: Automatic container health monitoring
- ✅ **Resource Limits**: CPU and memory constraints
- ✅ **Non-Root User**: Security-hardened containers
- ✅ **Separate Networks**: Internal vs public network isolation
- ✅ **Persistent Storage**: Bind mounts for data persistence
- ✅ **Service Replicas**: Multiple instances for high availability

---

## Docker Architecture

### Network Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    Public Network                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Nginx   │  │ Frontend │  │   Auth   │  │   NFT    │    │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│        │            │             │              │           │
└────────┼────────────┼─────────────┼──────────────┼───────────┘
         │            │             │              │
┌────────┼────────────┼─────────────┼──────────────┼───────────┐
│        │            │             │              │           │
│  ┌─────▼────┐  ┌───▼──────┐  ┌──▼───────┐  ┌───▼──────┐    │
│  │ MongoDB  │  │  Redis   │  │ Guilds   │  │ Weather  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                    Internal Network                          │
└─────────────────────────────────────────────────────────────┘
```

### Service Dependencies

```
MongoDB + Redis
    ↓
Auth Service
    ↓
NFT Service → Marketplace Service
    ↓              ↓
  Guilds      Analytics
    ↓              ↓
  Weather     WebSocket
    ↓              ↓
      Frontend
```

### Container Images

| Service | Base Image | Size | Purpose |
|---------|------------|------|---------|
| Backend Services | node:18-alpine | ~200MB | Lightweight Node.js runtime |
| MongoDB | mongo:6.0 | ~700MB | Database |
| Redis | redis:7-alpine | ~30MB | Cache & session store |
| Nginx | nginx:alpine | ~40MB | Reverse proxy |

---

## Environment Variables

### MongoDB Configuration

```bash
# Root credentials (admin access)
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=strong_password_here

# Application credentials
MONGO_APP_PASSWORD=another_strong_password
```

### Security Configuration

```bash
# Generate with: node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
JWT_SECRET=64_character_hex_string
SESSION_SECRET=64_character_hex_string
JWT_EXPIRATION=24h
```

### External Services

```bash
# IPFS (Pinata recommended)
IPFS_PROVIDER=pinata
PINATA_API_KEY=your_api_key
PINATA_SECRET_KEY=your_secret_key

# Weather APIs
OPENWEATHER_API_KEY=your_key
WEATHERAPI_KEY=your_key
```

### Full Example

See `.env.docker` for complete template with all variables.

---

## Health Checks

### Built-in Health Checks

All services include Docker health checks that automatically monitor:

- HTTP endpoint availability (`/health`)
- Response time (10s timeout)
- Retry logic (3 retries with 30s interval)
- Startup grace period (40-60s)

### Manual Health Check

```bash
# Check all service health
docker-compose ps

# Check specific service
docker inspect --format='{{.State.Health.Status}}' weathernft-auth-dev

# Test health endpoint
curl http://localhost:3014/health
```

### Health Check Response

```json
{
  "status": "OK",
  "service": "WeatherNFT Authentication Service",
  "database": "connected",
  "redis": "connected",
  "features": {
    "token_blacklist": "enabled"
  },
  "stats": {
    "total_users": 1234
  },
  "timestamp": "2025-11-19T12:00:00.000Z"
}
```

---

## Scaling Services

### Horizontal Scaling (Multiple Instances)

```bash
# Scale auth service to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale auth-service=3

# Scale frontend to 4 instances
docker-compose -f docker-compose.prod.yml up -d --scale frontend=4
```

### Resource Allocation

Configure in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Load Balancing

Nginx automatically load balances across multiple instances:

```nginx
upstream auth_service {
    least_conn;
    server auth-service-1:3014;
    server auth-service-2:3014;
    server auth-service-3:3014;
}
```

---

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs auth-service

# Follow logs (real-time)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Filter by time
docker-compose logs --since=1h
```

### Log Files

Production logs stored in `/var/log/weathernft/`:

```
/var/log/weathernft/
├── combined.log        # All services
├── error.log           # Errors only
├── auth-error.log      # Auth service errors
├── nft-error.log       # NFT service errors
└── ...
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Service-specific stats
docker stats weathernft-auth-prod

# Disk usage
docker system df

# Network usage
docker network inspect weathernft-internal
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check container status
docker inspect weathernft-service-name

# Restart service
docker-compose restart service-name
```

### Database Connection Issues

```bash
# Check MongoDB logs
docker-compose logs mongodb

# Test MongoDB connection
docker exec -it weathernft-mongodb-dev mongosh \
  mongodb://weathernft_app:password@localhost:27017/weathernft

# Check Redis connection
docker exec -it weathernft-redis-dev redis-cli -a password ping
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :3014

# Stop all containers
docker-compose down

# Remove all containers
docker-compose down -v
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove stopped containers
docker container prune

# Remove unused volumes
docker volume prune

# Clean everything
docker system prune -a --volumes
```

### Reset Everything

```bash
# Stop and remove all containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Fresh start
./scripts/docker-deploy.sh dev
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes automated CI/CD pipeline (`.github/workflows/ci-cd.yml`):

#### Triggers

- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop`
- **Manual** workflow dispatch

#### Jobs

1. **Test** (Node.js 18.x, 20.x)
   - Install dependencies
   - Run linter
   - Run unit tests
   - Upload coverage reports

2. **Security Scan**
   - npm audit
   - Trivy vulnerability scanner
   - Upload results to GitHub Security

3. **Build** (on push to main/develop)
   - Build Docker images
   - Push to GitHub Container Registry
   - Multi-platform builds (amd64, arm64)

4. **Deploy to Staging** (develop branch)
   - SSH to staging server
   - Pull latest images
   - Restart services
   - Run health checks

5. **Deploy to Production** (main branch)
   - SSH to production server
   - Pull latest images
   - Restart services
   - Run health checks
   - Rollback on failure

### Required GitHub Secrets

Configure in GitHub repository settings:

```
STAGING_HOST          # Staging server IP/hostname
STAGING_USER          # SSH username
STAGING_SSH_KEY       # Private SSH key

PRODUCTION_HOST       # Production server IP/hostname
PRODUCTION_USER       # SSH username
PRODUCTION_SSH_KEY    # Private SSH key
```

### Manual Deployment Trigger

```bash
# Trigger via GitHub CLI
gh workflow run ci-cd.yml

# Or via GitHub UI:
# Actions → WeatherNFT CI/CD → Run workflow
```

---

## Best Practices

### Security

- ✅ Always use `.env` files (never commit secrets)
- ✅ Generate strong passwords (64+ characters)
- ✅ Run containers as non-root user
- ✅ Use separate networks (internal vs public)
- ✅ Enable resource limits
- ✅ Regular security scans (Trivy)
- ✅ Keep images updated

### Performance

- ✅ Use multi-stage builds
- ✅ Minimize image layers
- ✅ Cache dependencies
- ✅ Use Alpine-based images
- ✅ Enable health checks
- ✅ Configure resource limits

### Monitoring

- ✅ Centralized logging
- ✅ Health check endpoints
- ✅ Container metrics
- ✅ Automated alerts
- ✅ Regular backups

---

## Additional Commands

### Database Backup

```bash
# Backup MongoDB
docker exec weathernft-mongodb-prod mongodump \
  --uri="mongodb://user:pass@localhost:27017/weathernft" \
  --out=/backup/$(date +%Y%m%d)

# Backup Redis
docker exec weathernft-redis-prod redis-cli \
  -a password BGSAVE
```

### Update Images

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Clean Logs

```bash
# Truncate log files
docker-compose exec auth-service truncate -s 0 /app/logs/combined.log

# Or rotate logs
docker-compose restart
```

---

## Support

- **Documentation**: See `DEPLOYMENT_GUIDE.md` for detailed deployment instructions
- **Issues**: https://github.com/YOUR_USERNAME/weather-nft-live/issues
- **Docker Hub**: https://hub.docker.com/r/weathernft/
- **GitHub Packages**: https://github.com/YOUR_USERNAME/weather-nft-live/packages

---

## License

MIT License - See LICENSE file for details
