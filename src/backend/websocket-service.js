#!/usr/bin/env node

/**
 * WebSocket Service for WeatherNFT
 * Provides real-time updates for weather events, NFT creation, and guild activity
 */

require('dotenv').config();
const WebSocket = require('ws');
const http = require('http');
const express = require('express');

const app = express();
const server = http.createServer(app);
const PORT = process.env.WEBSOCKET_PORT || 8080;

// WebSocket server
const wss = new WebSocket.Server({ server });

// Connected clients storage
const clients = new Map();
const subscriptions = new Map(); // user subscriptions to channels

// Channel types
const CHANNELS = {
  WEATHER_EVENTS: 'weather_events',
  NFT_CREATED: 'nft_created',
  GUILD_ACTIVITY: 'guild_activity',
  USER_NOTIFICATIONS: 'user_notifications',
  CAPTURES: 'captures',
  LEADERBOARD: 'leaderboard'
};

// Event types
const EVENT_TYPES = {
  WEATHER_DETECTED: 'weather_detected',
  NFT_MINTED: 'nft_minted',
  GUILD_CREATED: 'guild_created',
  GUILD_JOINED: 'guild_joined',
  ALGORITHM_RENTED: 'algorithm_rented',
  CAPTURE_EVENT: 'capture_event',
  REVENUE_DISTRIBUTED: 'revenue_distributed',
  LEADERBOARD_UPDATED: 'leaderboard_updated'
};

app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT WebSocket Service',
    connected_clients: clients.size,
    subscriptions: Array.from(subscriptions.keys()).length,
    timestamp: new Date().toISOString()
  });
});

// Broadcast event via HTTP POST
app.post('/broadcast', (req, res) => {
  try {
    const { channel, event, data } = req.body;

    if (!channel || !event) {
      return res.status(400).json({
        success: false,
        error: 'Missing channel or event'
      });
    }

    const message = {
      type: event,
      channel: channel,
      data: data,
      timestamp: Date.now()
    };

    broadcastToChannel(channel, message);

    res.json({
      success: true,
      message: 'Event broadcasted',
      recipients: getChannelSubscribers(channel).length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get connected clients stats
app.get('/stats', (req, res) => {
  const stats = {
    total_clients: clients.size,
    channels: {}
  };

  Object.values(CHANNELS).forEach(channel => {
    stats.channels[channel] = getChannelSubscribers(channel).length;
  });

  res.json({
    success: true,
    data: stats
  });
});

// WebSocket connection handler
wss.on('connection', (ws, req) => {
  const clientId = generateClientId();
  clients.set(clientId, {
    ws: ws,
    subscriptions: new Set(),
    userAddress: null,
    connectedAt: Date.now()
  });

  console.log(`✅ Client connected: ${clientId} (Total: ${clients.size})`);

  // Send welcome message
  sendToClient(ws, {
    type: 'connected',
    clientId: clientId,
    message: 'Connected to WeatherNFT real-time updates',
    channels: Object.values(CHANNELS)
  });

  // Handle incoming messages
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      handleClientMessage(clientId, data);
    } catch (error) {
      sendToClient(ws, {
        type: 'error',
        message: 'Invalid message format'
      });
    }
  });

  // Handle client disconnect
  ws.on('close', () => {
    const client = clients.get(clientId);
    if (client) {
      // Remove subscriptions
      client.subscriptions.forEach(channel => {
        const subs = subscriptions.get(channel) || new Set();
        subs.delete(clientId);
        if (subs.size === 0) {
          subscriptions.delete(channel);
        } else {
          subscriptions.set(channel, subs);
        }
      });
    }
    clients.delete(clientId);
    console.log(`❌ Client disconnected: ${clientId} (Total: ${clients.size})`);
  });

  // Handle errors
  ws.on('error', (error) => {
    console.error(`⚠️  Client error ${clientId}:`, error.message);
  });

  // Ping/pong for keepalive
  ws.isAlive = true;
  ws.on('pong', () => {
    ws.isAlive = true;
  });
});

// Keepalive ping
const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) {
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000); // 30 seconds

wss.on('close', () => {
  clearInterval(interval);
});

// Handle client messages
function handleClientMessage(clientId, data) {
  const client = clients.get(clientId);
  if (!client) return;

  const { action, payload } = data;

  switch (action) {
    case 'subscribe':
      subscribeToChannel(clientId, payload.channel);
      break;

    case 'unsubscribe':
      unsubscribeFromChannel(clientId, payload.channel);
      break;

    case 'identify':
      client.userAddress = payload.userAddress;
      sendToClient(client.ws, {
        type: 'identified',
        userAddress: payload.userAddress,
        message: 'User identified successfully'
      });
      break;

    case 'ping':
      sendToClient(client.ws, { type: 'pong', timestamp: Date.now() });
      break;

    default:
      sendToClient(client.ws, {
        type: 'error',
        message: `Unknown action: ${action}`
      });
  }
}

// Subscribe client to channel
function subscribeToChannel(clientId, channel) {
  const client = clients.get(clientId);
  if (!client) return;

  if (!Object.values(CHANNELS).includes(channel)) {
    sendToClient(client.ws, {
      type: 'error',
      message: `Invalid channel: ${channel}`
    });
    return;
  }

  client.subscriptions.add(channel);

  let subs = subscriptions.get(channel) || new Set();
  subs.add(clientId);
  subscriptions.set(channel, subs);

  sendToClient(client.ws, {
    type: 'subscribed',
    channel: channel,
    message: `Subscribed to ${channel}`,
    subscribers: subs.size
  });

  console.log(`📡 Client ${clientId} subscribed to ${channel} (${subs.size} subscribers)`);
}

// Unsubscribe client from channel
function unsubscribeFromChannel(clientId, channel) {
  const client = clients.get(clientId);
  if (!client) return;

  client.subscriptions.delete(channel);

  const subs = subscriptions.get(channel);
  if (subs) {
    subs.delete(clientId);
    if (subs.size === 0) {
      subscriptions.delete(channel);
    }
  }

  sendToClient(client.ws, {
    type: 'unsubscribed',
    channel: channel,
    message: `Unsubscribed from ${channel}`
  });

  console.log(`📡 Client ${clientId} unsubscribed from ${channel}`);
}

// Send message to specific client
function sendToClient(ws, message) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  }
}

// Broadcast to all clients in a channel
function broadcastToChannel(channel, message) {
  const subscribers = getChannelSubscribers(channel);

  subscribers.forEach(clientId => {
    const client = clients.get(clientId);
    if (client && client.ws.readyState === WebSocket.OPEN) {
      sendToClient(client.ws, message);
    }
  });

  console.log(`📢 Broadcasted to ${channel}: ${subscribers.length} recipients`);
}

// Get all subscribers of a channel
function getChannelSubscribers(channel) {
  const subs = subscriptions.get(channel);
  return subs ? Array.from(subs) : [];
}

// Broadcast to specific user
function broadcastToUser(userAddress, message) {
  clients.forEach((client, clientId) => {
    if (client.userAddress === userAddress) {
      sendToClient(client.ws, message);
    }
  });
}

// Broadcast to all connected clients
function broadcastToAll(message) {
  clients.forEach((client) => {
    sendToClient(client.ws, message);
  });
  console.log(`📢 Broadcasted to all: ${clients.size} recipients`);
}

// Generate unique client ID
function generateClientId() {
  return `client_${Date.now()}_${Math.random().toString(36).substring(7)}`;
}

// Helper functions to send specific event types

function broadcastWeatherEvent(eventData) {
  broadcastToChannel(CHANNELS.WEATHER_EVENTS, {
    type: EVENT_TYPES.WEATHER_DETECTED,
    channel: CHANNELS.WEATHER_EVENTS,
    data: eventData,
    timestamp: Date.now()
  });
}

function broadcastNFTCreated(nftData) {
  broadcastToChannel(CHANNELS.NFT_CREATED, {
    type: EVENT_TYPES.NFT_MINTED,
    channel: CHANNELS.NFT_CREATED,
    data: nftData,
    timestamp: Date.now()
  });
}

function broadcastGuildActivity(activityData) {
  broadcastToChannel(CHANNELS.GUILD_ACTIVITY, {
    type: activityData.type,
    channel: CHANNELS.GUILD_ACTIVITY,
    data: activityData,
    timestamp: Date.now()
  });
}

function broadcastCapture(captureData) {
  broadcastToChannel(CHANNELS.CAPTURES, {
    type: EVENT_TYPES.CAPTURE_EVENT,
    channel: CHANNELS.CAPTURES,
    data: captureData,
    timestamp: Date.now()
  });
}

function broadcastLeaderboardUpdate(leaderboardData) {
  broadcastToChannel(CHANNELS.LEADERBOARD, {
    type: EVENT_TYPES.LEADERBOARD_UPDATED,
    channel: CHANNELS.LEADERBOARD,
    data: leaderboardData,
    timestamp: Date.now()
  });
}

// Export broadcast functions for use in other services
module.exports = {
  broadcastWeatherEvent,
  broadcastNFTCreated,
  broadcastGuildActivity,
  broadcastCapture,
  broadcastLeaderboardUpdate,
  broadcastToUser,
  broadcastToAll,
  CHANNELS,
  EVENT_TYPES
};

// Start server
server.listen(PORT, () => {
  console.log('');
  console.log('⚡ WeatherNFT WebSocket Service');
  console.log('=' .repeat(50));
  console.log(`✅ WebSocket server running on ws://localhost:${PORT}`);
  console.log(`✅ HTTP server running on http://localhost:${PORT}`);
  console.log('');
  console.log('📡 Available Channels:');
  Object.entries(CHANNELS).forEach(([key, value]) => {
    console.log(`   • ${value}`);
  });
  console.log('');
  console.log('📊 HTTP Endpoints:');
  console.log('   • GET  /health     - Health check');
  console.log('   • GET  /stats      - Connection statistics');
  console.log('   • POST /broadcast  - Broadcast event to channel');
  console.log('');
  console.log('🔌 Client Commands:');
  console.log('   • {"action": "subscribe", "payload": {"channel": "weather_events"}}');
  console.log('   • {"action": "unsubscribe", "payload": {"channel": "weather_events"}}');
  console.log('   • {"action": "identify", "payload": {"userAddress": "tz1..."}}');
  console.log('   • {"action": "ping"}');
  console.log('');
});
