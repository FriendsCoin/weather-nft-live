# WeatherNFT Backend Services Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies for building)
RUN npm ci --ignore-scripts

# Copy source code
COPY . .

# Stage 2: Production stage
FROM node:18-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app user (non-root for security)
RUN addgroup -g 1001 -S weathernft && \
    adduser -S -u 1001 -G weathernft weathernft

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production --ignore-scripts && \
    npm cache clean --force

# Copy application code from builder
COPY --from=builder --chown=weathernft:weathernft /app/src ./src
COPY --from=builder --chown=weathernft:weathernft /app/.env.example ./.env.example

# Create logs directory
RUN mkdir -p /app/logs && \
    chown -R weathernft:weathernft /app

# Switch to non-root user
USER weathernft

# Expose ports (will be overridden by docker-compose)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3000) + '/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Default command (can be overridden by docker-compose)
CMD ["node", "src/backend/simple-server.js"]
