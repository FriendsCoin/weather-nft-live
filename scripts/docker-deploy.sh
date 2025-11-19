#!/bin/bash

# WeatherNFT Docker Deployment Script
# Usage: ./scripts/docker-deploy.sh [dev|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if environment argument is provided
if [ -z "$1" ]; then
    print_error "Usage: ./scripts/docker-deploy.sh [dev|prod]"
    exit 1
fi

ENV=$1

# Validate environment
if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    print_error "Invalid environment. Use 'dev' or 'prod'"
    exit 1
fi

print_info "Deploying WeatherNFT in ${ENV} environment"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ "$ENV" = "prod" ]; then
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        print_info "Copying .env.docker template..."
        cp .env.docker .env
        print_warning "Please edit .env file with your production credentials before deploying!"
        exit 1
    fi
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

print_info "Using compose file: $COMPOSE_FILE"
echo ""

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down
print_success "Containers stopped"
echo ""

# Build images
print_info "Building Docker images..."
docker-compose -f $COMPOSE_FILE build --no-cache
print_success "Images built successfully"
echo ""

# Start services
print_info "Starting services..."
docker-compose -f $COMPOSE_FILE up -d
print_success "Services started"
echo ""

# Wait for services to be healthy
print_info "Waiting for services to become healthy..."
sleep 10

# Check service health
print_info "Checking service health..."
echo ""

services=("mongodb" "redis" "auth-service" "nft-service" "marketplace-service" "guild-service" "analytics-service" "weather-service")

for service in "${services[@]}"; do
    health_status=$(docker inspect --format='{{.State.Health.Status}}' weathernft-${service}-${ENV} 2>/dev/null || echo "no-health-check")

    if [ "$health_status" = "healthy" ]; then
        print_success "$service is healthy"
    elif [ "$health_status" = "no-health-check" ]; then
        print_warning "$service has no health check configured"
    else
        print_warning "$service status: $health_status"
    fi
done

echo ""

# Show running containers
print_info "Running containers:"
docker-compose -f $COMPOSE_FILE ps
echo ""

# Show logs
print_info "Recent logs (last 20 lines):"
docker-compose -f $COMPOSE_FILE logs --tail=20
echo ""

# Print access URLs
print_success "Deployment complete!"
echo ""
print_info "Access URLs:"
if [ "$ENV" = "dev" ]; then
    echo "  Frontend:     http://localhost:8081"
    echo "  Auth API:     http://localhost:3014/health"
    echo "  NFT API:      http://localhost:3009/health"
    echo "  Marketplace:  http://localhost:3013/health"
    echo "  Guild API:    http://localhost:3010/health"
    echo "  Analytics:    http://localhost:3011/health"
    echo "  Weather API:  http://localhost:3012/health"
    echo "  WebSocket:    ws://localhost:8080"
else
    echo "  Frontend:     https://weathernft.com"
    echo "  Health Check: https://weathernft.com/health"
fi

echo ""
print_info "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
print_info "To stop: docker-compose -f $COMPOSE_FILE down"
echo ""
