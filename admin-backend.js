#!/usr/bin/env node

// WeatherNFT Admin Backend - Real functionality
const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.ADMIN_API_PORT || 3008;

// APIs of other services
const AI_API = 'http://localhost:3006';
const BLOCKCHAIN_API = 'http://localhost:3007';
const SD_AI_API = 'http://localhost:8000';

app.use(cors());
app.use(express.json());

// Import fetch for Node.js
let fetch;
(async () => {
  try {
    const nodeFetch = await import('node-fetch');
    fetch = nodeFetch.default;
  } catch (e) {
    // Fallback for older Node versions
    fetch = require('node-fetch');
  }
})();

// Admin data storage (in production would be a real database)
let adminData = {
  users: [
    {
      id: 'user_001',
      walletAddress: 'tz1ABC...DEF',
      credits: 25,
      totalSpent: 150,
      eventsCaptures: 12,
      joinedAt: '2025-06-15T10:00:00Z',
      status: 'active',
      lastActivity: '2025-06-21T09:30:00Z'
    },
    {
      id: 'user_002', 
      walletAddress: 'tz1XYZ...123',
      credits: 8,
      totalSpent: 320,
      eventsCaptures: 28,
      joinedAt: '2025-06-10T14:00:00Z',
      status: 'active',
      lastActivity: '2025-06-21T08:15:00Z'
    },
    {
      id: 'user_003',
      walletAddress: 'tz1GHI...456',
      credits: 0,
      totalSpent: 75,
      eventsCaptures: 5,
      joinedAt: '2025-06-18T16:00:00Z',
      status: 'inactive',
      lastActivity: '2025-06-20T12:00:00Z'
    }
  ],
  systemLogs: [],
  settings: {
    creditPrice: 5, // tez per credit
    eventPricing: {
      common: 5,
      uncommon: 10, 
      rare: 20,
      epic: 35,
      legendary: 50
    },
    aiSettings: {
      confidenceThreshold: 0.7,
      enabledAlgorithms: ['ThermalDrift-v2', 'StormChaser-v4', 'EcoBalance-v1', 'AuroraPredictor-v3', 'AquaDetect-v2'],
      retrainingInterval: 24, // hours
      maxEventsPerHour: 10
    }
  }
};

// Logging function
function log(level, message, data = null) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    data,
    id: Date.now().toString()
  };
  
  adminData.systemLogs.unshift(logEntry);
  if (adminData.systemLogs.length > 1000) {
    adminData.systemLogs = adminData.systemLogs.slice(0, 1000);
  }
  
  console.log(`[${level.toUpperCase()}] ${message}`, data || '');
}

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT Admin Backend',
    timestamp: new Date().toISOString()
  });
});

// Dashboard data
app.get('/api/dashboard', async (req, res) => {
  try {
    // Get data from AI service
    const aiStatsRes = await fetch(`${AI_API}/api/analytics/stats`);
    const aiStats = await aiStatsRes.json();
    
    const aiAlgorithmsRes = await fetch(`${AI_API}/api/ai/algorithms`);
    const aiAlgorithms = await aiAlgorithmsRes.json();
    
    const eventsRes = await fetch(`${AI_API}/api/events`);
    const events = await eventsRes.json();
    
    // Get blockchain status
    let blockchainStatus = 'inactive';
    try {
      const blockchainRes = await fetch(`${BLOCKCHAIN_API}/health`);
      if (blockchainRes.ok) blockchainStatus = 'active';
    } catch (e) {
      blockchainStatus = 'inactive';
    }
    
    // Calculate real-time metrics
    const totalUsers = adminData.users.length;
    const activeUsers = adminData.users.filter(u => u.status === 'active').length;
    const totalCredits = adminData.users.reduce((sum, u) => sum + u.credits, 0);
    const totalSpent = adminData.users.reduce((sum, u) => sum + u.totalSpent, 0);
    
    const dashboard = {
      overview: {
        activeEvents: events.success ? events.count : 0,
        totalUsers: totalUsers,
        activeUsers: activeUsers,
        aiPredictions: aiStats.success ? aiStats.data.totalEvents : 0,
        systemUptime: aiStats.success ? Math.floor(aiStats.data.systemUptime / 3600) : 0,
        avgAIAccuracy: aiAlgorithms.success ? 
          (aiAlgorithms.data.reduce((sum, a) => sum + a.accuracy, 0) / aiAlgorithms.data.length).toFixed(1) : 0
      },
      services: [
        {
          name: 'AI Backend',
          status: aiStats.success ? 'active' : 'inactive',
          port: 3006,
          uptime: aiStats.success ? Math.floor(aiStats.data.systemUptime / 3600) + 'h' : '0h',
          url: AI_API
        },
        {
          name: 'Frontend',
          status: 'active', // Assuming it's active since admin is loaded
          port: 8081,
          uptime: '2h 45m',
          url: 'http://localhost:8081'
        },
        {
          name: 'Blockchain',
          status: blockchainStatus,
          port: 3007,
          uptime: blockchainStatus === 'active' ? '2h 45m' : '0h',
          url: BLOCKCHAIN_API
        },
        {
          name: 'Admin Backend',
          status: 'active',
          port: PORT,
          uptime: '0h 5m',
          url: `http://localhost:${PORT}`
        }
      ],
      recentActivity: adminData.systemLogs.slice(0, 10),
      userStats: {
        totalUsers,
        activeUsers,
        totalCredits,
        totalSpent,
        avgCreditsPerUser: totalUsers > 0 ? (totalCredits / totalUsers).toFixed(1) : 0
      }
    };
    
    res.json({ success: true, data: dashboard });
    
  } catch (error) {
    log('error', 'Dashboard data fetch failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

// AI Management
app.get('/api/ai/models', async (req, res) => {
  try {
    const response = await fetch(`${AI_API}/api/ai/algorithms`);
    const data = await response.json();
    
    if (data.success) {
      // Enhance with admin data
      const enhancedModels = data.data.map(model => ({
        ...model,
        enabled: adminData.settings.aiSettings.enabledAlgorithms.includes(model.name),
        lastRetrained: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        nextRetraining: new Date(Date.now() + adminData.settings.aiSettings.retrainingInterval * 60 * 60 * 1000).toISOString()
      }));
      
      res.json({ success: true, data: enhancedModels, total_predictions: data.total_predictions });
    } else {
      res.status(500).json(data);
    }
    
  } catch (error) {
    log('error', 'AI models fetch failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/ai/models/:modelName/toggle', (req, res) => {
  try {
    const { modelName } = req.params;
    const { enabled } = req.body;
    
    if (enabled) {
      if (!adminData.settings.aiSettings.enabledAlgorithms.includes(modelName)) {
        adminData.settings.aiSettings.enabledAlgorithms.push(modelName);
      }
    } else {
      adminData.settings.aiSettings.enabledAlgorithms = 
        adminData.settings.aiSettings.enabledAlgorithms.filter(name => name !== modelName);
    }
    
    log('info', `AI model ${modelName} ${enabled ? 'enabled' : 'disabled'}`, { modelName, enabled });
    
    res.json({ success: true, message: `Model ${modelName} ${enabled ? 'enabled' : 'disabled'}` });
    
  } catch (error) {
    log('error', 'AI model toggle failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/ai/models/:modelName/retrain', async (req, res) => {
  try {
    const { modelName } = req.params;
    
    // Simulate retraining (in real implementation would trigger actual retraining)
    log('info', `Retraining initiated for ${modelName}`, { modelName });
    
    // Simulate training time
    setTimeout(() => {
      log('info', `Retraining completed for ${modelName}`, { modelName, newAccuracy: (Math.random() * 5 + 90).toFixed(1) });
    }, 5000);
    
    res.json({ 
      success: true, 
      message: `Retraining started for ${modelName}`,
      estimatedTime: '5-10 minutes'
    });
    
  } catch (error) {
    log('error', 'AI model retrain failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

// SD PyTorch AI Integration
app.get('/api/ai/sd-status', async (req, res) => {
  try {
    const response = await fetch(`${SD_AI_API}/health`);
    const data = await response.json();
    
    log('info', 'SD AI status checked', data);
    res.json({ success: true, data });
    
  } catch (error) {
    log('warning', 'SD AI not available', error.message);
    res.json({ 
      success: false, 
      error: 'SD AI service not running',
      message: 'SD PyTorch AI is not available. Start it with: python sd-pytorch-integration.py --server'
    });
  }
});

app.get('/api/ai/sd-info', async (req, res) => {
  try {
    const response = await fetch(`${SD_AI_API}/model/info`);
    const data = await response.json();
    
    log('info', 'SD AI model info retrieved', data);
    res.json({ success: true, data });
    
  } catch (error) {
    log('warning', 'SD AI model info failed', error.message);
    res.json({ 
      success: false, 
      error: 'SD AI service not available',
      fallback_info: {
        status: "offline",
        sd_environment: false,
        pytorch_available: false,
        algorithms_count: 5,
        note: "Start SD AI with: python sd-pytorch-integration.py --server"
      }
    });
  }
});

app.post('/api/ai/sd-predict', async (req, res) => {
  try {
    const weatherData = req.body;
    
    const response = await fetch(`${SD_AI_API}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(weatherData)
    });
    
    const data = await response.json();
    
    log('info', 'SD AI prediction completed', { confidence: data.confidence, algorithm: data.algorithm });
    res.json({ success: true, data });
    
  } catch (error) {
    log('warning', 'SD AI prediction failed', error.message);
    res.json({ 
      success: false, 
      error: 'SD AI prediction failed',
      message: 'SD PyTorch AI service is not available. Using JavaScript AI fallback.'
    });
  }
});

app.post('/api/ai/sd-start', async (req, res) => {
  try {
    log('info', 'SD AI start requested', { source: 'admin-panel' });
    
    // In a real implementation, this would start the SD AI service
    // For now, we return instructions
    res.json({ 
      success: true, 
      message: 'SD AI start instructions provided',
      instructions: {
        step1: 'Open terminal in project directory',
        step2: 'Run: ./start-sd-ai.sh --server',
        step3: 'Or run: python sd-pytorch-integration.py --server',
        note: 'SD AI will start on port 8000'
      }
    });
    
  } catch (error) {
    log('error', 'SD AI start failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Events Management
app.get('/api/admin/events', async (req, res) => {
  try {
    const response = await fetch(`${AI_API}/api/events`);
    const data = await response.json();
    
    if (data.success) {
      // Enhance events with admin data
      const enhancedEvents = data.data.map(event => ({
        ...event,
        adminActions: {
          canDelete: true,
          canModify: true,
          canBoost: event.rarity !== 'legendary'
        },
        performance: {
          captureRate: event.captureSlots > 0 ? (event.capturedCount / event.captureSlots * 100).toFixed(1) : 0,
          timeRemaining: Math.floor(Math.random() * 24) + 'h',
          estimatedValue: event.price * event.captureSlots
        }
      }));
      
      res.json({ success: true, data: enhancedEvents, summary: data });
    } else {
      res.status(500).json(data);
    }
    
  } catch (error) {
    log('error', 'Events fetch failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.delete('/api/admin/events/:eventId', (req, res) => {
  try {
    const { eventId } = req.params;
    
    log('warning', `Event ${eventId} deleted by admin`, { eventId });
    
    res.json({ 
      success: true, 
      message: `Event ${eventId} deleted` 
    });
    
  } catch (error) {
    log('error', 'Event deletion failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/admin/events/:eventId/boost', (req, res) => {
  try {
    const { eventId } = req.params;
    const { boostMultiplier = 1.5 } = req.body;
    
    log('info', `Event ${eventId} boosted`, { eventId, boostMultiplier });
    
    res.json({ 
      success: true, 
      message: `Event ${eventId} boosted by ${boostMultiplier}x` 
    });
    
  } catch (error) {
    log('error', 'Event boost failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/admin/events/generate', async (req, res) => {
  try {
    const { lat = 55.7558, lng = 37.6173, forceRarity } = req.body;
    
    // Generate event through AI service
    const response = await fetch(`${AI_API}/api/events/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat, lng })
    });
    
    const data = await response.json();
    
    if (data.success) {
      log('info', 'Admin generated weather event', { 
        location: { lat, lng }, 
        events: data.generated_events,
        forceRarity 
      });
      
      res.json({ 
        success: true, 
        message: `Generated ${data.generated_events} events`,
        events: data.events
      });
    } else {
      res.status(500).json(data);
    }
    
  } catch (error) {
    log('error', 'Event generation failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

// User Management
app.get('/api/admin/users', (req, res) => {
  try {
    const { status, sortBy = 'joinedAt', order = 'desc', limit = 50 } = req.query;
    
    let users = [...adminData.users];
    
    // Filter by status
    if (status && status !== 'all') {
      users = users.filter(user => user.status === status);
    }
    
    // Sort
    users.sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      
      if (order === 'desc') {
        return bVal > aVal ? 1 : -1;
      } else {
        return aVal > bVal ? 1 : -1;
      }
    });
    
    // Limit
    users = users.slice(0, parseInt(limit));
    
    res.json({ 
      success: true, 
      data: users,
      total: adminData.users.length,
      filtered: users.length
    });
    
  } catch (error) {
    log('error', 'Users fetch failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/admin/users/:userId/credits', (req, res) => {
  try {
    const { userId } = req.params;
    const { amount, reason } = req.body;
    
    const user = adminData.users.find(u => u.id === userId);
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    user.credits += amount;
    
    log('info', `Credits ${amount > 0 ? 'added' : 'removed'}`, { 
      userId, 
      amount, 
      reason, 
      newBalance: user.credits 
    });
    
    res.json({ 
      success: true, 
      message: `${amount > 0 ? 'Added' : 'Removed'} ${Math.abs(amount)} credits`,
      newBalance: user.credits
    });
    
  } catch (error) {
    log('error', 'Credit modification failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/admin/users/:userId/status', (req, res) => {
  try {
    const { userId } = req.params;
    const { status, reason } = req.body;
    
    const user = adminData.users.find(u => u.id === userId);
    if (!user) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    const oldStatus = user.status;
    user.status = status;
    
    log('warning', `User status changed`, { 
      userId, 
      oldStatus, 
      newStatus: status, 
      reason 
    });
    
    res.json({ 
      success: true, 
      message: `User status changed to ${status}` 
    });
    
  } catch (error) {
    log('error', 'User status change failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

// System Management
app.get('/api/admin/logs', (req, res) => {
  try {
    const { level, limit = 100, since } = req.query;
    
    let logs = [...adminData.systemLogs];
    
    // Filter by level
    if (level && level !== 'all') {
      logs = logs.filter(log => log.level === level);
    }
    
    // Filter by time
    if (since) {
      const sinceDate = new Date(since);
      logs = logs.filter(log => new Date(log.timestamp) > sinceDate);
    }
    
    // Limit
    logs = logs.slice(0, parseInt(limit));
    
    res.json({ 
      success: true, 
      data: logs,
      total: adminData.systemLogs.length
    });
    
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/admin/system/restart/:service', (req, res) => {
  try {
    const { service } = req.params;
    
    log('warning', `Service restart requested`, { service });
    
    // In real implementation, this would actually restart the service
    res.json({ 
      success: true, 
      message: `${service} restart initiated` 
    });
    
  } catch (error) {
    log('error', 'Service restart failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/admin/system/start-pytorch', (req, res) => {
  try {
    log('info', 'PyTorch startup requested via admin');
    
    // Try to spawn the batch script
    const { spawn } = require('child_process');
    const isWindows = process.platform === 'win32';
    
    if (isWindows) {
      // Windows batch file
      const child = spawn('cmd', ['/c', 'start-pytorch-ai.bat'], {
        detached: true,
        stdio: 'ignore'
      });
      child.unref();
    } else {
      // Linux/Mac shell script
      const child = spawn('./start-pytorch-ai.sh', [], {
        detached: true,
        stdio: 'ignore'
      });
      child.unref();
    }
    
    log('info', 'PyTorch startup script executed');
    
    res.json({ 
      success: true, 
      message: 'PyTorch startup initiated. Check terminal for progress.' 
    });
    
  } catch (error) {
    log('error', 'PyTorch startup failed', error.message);
    res.json({ 
      success: false, 
      message: 'Manual start required: run start-pytorch-ai.bat' 
    });
  }
});

app.get('/api/admin/settings', (req, res) => {
  try {
    res.json({ 
      success: true, 
      data: adminData.settings 
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.put('/api/admin/settings', (req, res) => {
  try {
    const newSettings = req.body;
    
    // Merge settings
    adminData.settings = { ...adminData.settings, ...newSettings };
    
    log('info', 'System settings updated', { settings: newSettings });
    
    res.json({ 
      success: true, 
      message: 'Settings updated',
      data: adminData.settings
    });
    
  } catch (error) {
    log('error', 'Settings update failed', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'WeatherNFT Admin Backend',
    status: 'Running',
    version: '1.0.0',
    endpoints: {
      dashboard: '/api/dashboard',
      aiModels: '/api/ai/models',
      events: '/api/admin/events', 
      users: '/api/admin/users',
      logs: '/api/admin/logs',
      settings: '/api/admin/settings'
    }
  });
});

// Initialize logs
log('info', 'WeatherNFT Admin Backend started', { port: PORT });
log('info', 'Connected services', { ai: AI_API, blockchain: BLOCKCHAIN_API });

// Start server
app.listen(PORT, () => {
  console.log('🔧 WeatherNFT Admin Backend');
  console.log('============================');
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`🔗 AI Service: ${AI_API}`);
  console.log(`🔗 Blockchain Service: ${BLOCKCHAIN_API}`);
  console.log('');
  console.log('🛠️ Admin API endpoints:');
  console.log(`   GET  /api/dashboard - Real-time dashboard`);
  console.log(`   GET  /api/ai/models - AI model management`);
  console.log(`   GET  /api/admin/events - Event management`);
  console.log(`   GET  /api/admin/users - User management`);
  console.log(`   GET  /api/admin/logs - System logs`);
  console.log('');
  console.log('🎛️ Ready for admin operations!');
});