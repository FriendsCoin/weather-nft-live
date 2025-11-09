#!/usr/bin/env node

// WeatherNFT.live Admin Dashboard
require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

// Polyfill for fetch if not available
if (!global.fetch) {
  global.fetch = require('node-fetch');
}

const app = express();
const PORT = process.env.ADMIN_PORT || 3005;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.static('admin-public'));

// Database Models (reuse from main server)
const weatherEventSchema = new mongoose.Schema({
  eventId: { type: String, unique: true, required: true },
  type: { type: String, required: true },
  aiAlgorithm: { type: String, required: true },
  uniqueName: { type: String, required: true },
  location: {
    city: String,
    country: String,
    lat: Number,
    lng: Number
  },
  severity: { type: String, enum: ['low', 'moderate', 'high', 'extreme'] },
  rarity: { type: String, enum: ['common', 'uncommon', 'rare', 'epic', 'legendary'] },
  captureSlots: Number,
  capturedCount: { type: Number, default: 0 },
  active: { type: Boolean, default: true },
  expiresAt: Date,
  weatherData: {
    temperature: Number,
    humidity: Number,
    pressure: Number,
    windSpeed: Number,
    visibility: Number,
    conditions: String
  },
  aiPrediction: {
    confidence: Number,
    detectedAt: Date,
    algorithm: String,
    accuracy: Number
  },
  verification: {
    verified: { type: Boolean, default: false },
    verifiedAt: Date,
    provenance: String,
    apiSources: [String]
  },
  price: { type: Number, required: true },
  createdAt: { type: Date, default: Date.now }
});

const userSchema = new mongoose.Schema({
  walletAddress: { type: String, unique: true },
  credits: { type: Number, default: 12 },
  guildMemberships: [String],
  capturedEvents: [String],
  stats: {
    totalCaptures: { type: Number, default: 0 },
    totalSpent: { type: Number, default: 0 },
    successRate: { type: Number, default: 0 }
  },
  createdAt: { type: Date, default: Date.now }
});

const apiKeySchema = new mongoose.Schema({
  service: { type: String, required: true },
  keyName: { type: String, required: true },
  keyValue: { type: String, required: true },
  active: { type: Boolean, default: true },
  lastUsed: Date,
  usageCount: { type: Number, default: 0 },
  rateLimit: {
    requestsPerHour: Number,
    currentUsage: { type: Number, default: 0 },
    resetTime: Date
  },
  createdAt: { type: Date, default: Date.now }
});

const WeatherEvent = mongoose.model('WeatherEvent', weatherEventSchema);
const User = mongoose.model('User', userSchema);
const ApiKey = mongoose.model('ApiKey', apiKeySchema);

// MongoDB Connection
async function connectDB() {
  try {
    const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/weather-nft';
    await mongoose.connect(mongoURI);
    console.log('✅ Admin Dashboard connected to MongoDB');
  } catch (error) {
    console.error('❌ MongoDB connection failed:', error);
    process.exit(1);
  }
}

// Utility Functions
const sendJSON = (res, data, status = 200) => {
  res.status(status).json(data);
};

// Admin API Routes

// Main dashboard stats
app.get('/api/dashboard/stats', async (req, res) => {
  try {
    const [
      totalEvents,
      activeEvents,
      totalUsers,
      totalCaptures,
      recentEvents,
      topAlgorithms
    ] = await Promise.all([
      WeatherEvent.countDocuments(),
      WeatherEvent.countDocuments({ active: true }),
      User.countDocuments(),
      WeatherEvent.aggregate([{ $group: { _id: null, total: { $sum: '$capturedCount' } } }]),
      WeatherEvent.find().sort({ createdAt: -1 }).limit(10),
      WeatherEvent.aggregate([
        { $group: { _id: '$aiAlgorithm', count: { $sum: 1 }, avgAccuracy: { $avg: '$aiPrediction.accuracy' } } },
        { $sort: { count: -1 } },
        { $limit: 5 }
      ])
    ]);

    sendJSON(res, {
      success: true,
      stats: {
        totalEvents,
        activeEvents,
        totalUsers,
        totalCaptures: totalCaptures[0]?.total || 0,
        recentEvents,
        topAlgorithms
      }
    });
  } catch (error) {
    console.error('Dashboard stats error:', error);
    sendJSON(res, { error: 'Failed to fetch dashboard stats' }, 500);
  }
});

// AI Algorithms monitoring
app.get('/api/ai/performance', async (req, res) => {
  try {
    const algorithms = await WeatherEvent.aggregate([
      {
        $group: {
          _id: '$aiAlgorithm',
          totalEvents: { $sum: 1 },
          avgConfidence: { $avg: '$aiPrediction.confidence' },
          avgAccuracy: { $avg: '$aiPrediction.accuracy' },
          totalCaptures: { $sum: '$capturedCount' },
          successRate: { 
            $avg: { 
              $cond: [{ $gt: ['$capturedCount', 0] }, 1, 0] 
            } 
          },
          recentEvents: { $push: { name: '$uniqueName', date: '$createdAt', confidence: '$aiPrediction.confidence' } }
        }
      },
      { $sort: { totalEvents: -1 } }
    ]);

    sendJSON(res, {
      success: true,
      algorithms: algorithms.map(algo => ({
        ...algo,
        recentEvents: algo.recentEvents.slice(-5) // Last 5 events
      }))
    });
  } catch (error) {
    console.error('AI performance error:', error);
    sendJSON(res, { error: 'Failed to fetch AI performance' }, 500);
  }
});

// Events management
app.get('/api/events/manage', async (req, res) => {
  try {
    const { page = 1, limit = 20, algorithm, active } = req.query;
    const filter = {};
    
    if (algorithm) filter.aiAlgorithm = algorithm;
    if (active !== undefined) filter.active = active === 'true';

    const events = await WeatherEvent.find(filter)
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);

    const total = await WeatherEvent.countDocuments(filter);

    sendJSON(res, {
      success: true,
      events,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Events management error:', error);
    sendJSON(res, { error: 'Failed to fetch events' }, 500);
  }
});

// Update event
app.put('/api/events/:eventId', async (req, res) => {
  try {
    const { eventId } = req.params;
    const updates = req.body;

    const event = await WeatherEvent.findOneAndUpdate(
      { eventId },
      updates,
      { new: true }
    );

    if (!event) {
      return sendJSON(res, { error: 'Event not found' }, 404);
    }

    sendJSON(res, { success: true, event });
  } catch (error) {
    console.error('Update event error:', error);
    sendJSON(res, { error: 'Failed to update event' }, 500);
  }
});

// Users management
app.get('/api/users/manage', async (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query;

    const users = await User.find()
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);

    const total = await User.countDocuments();

    sendJSON(res, {
      success: true,
      users,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Users management error:', error);
    sendJSON(res, { error: 'Failed to fetch users' }, 500);
  }
});

// Update user credits
app.put('/api/users/:walletAddress/credits', async (req, res) => {
  try {
    const { walletAddress } = req.params;
    const { credits } = req.body;

    const user = await User.findOneAndUpdate(
      { walletAddress },
      { credits: parseInt(credits) },
      { new: true, upsert: true }
    );

    sendJSON(res, { success: true, user });
  } catch (error) {
    console.error('Update credits error:', error);
    sendJSON(res, { error: 'Failed to update credits' }, 500);
  }
});

// API Keys management
app.get('/api/keys', async (req, res) => {
  try {
    const keys = await ApiKey.find().select('-keyValue');
    sendJSON(res, { success: true, keys });
  } catch (error) {
    console.error('API keys error:', error);
    sendJSON(res, { error: 'Failed to fetch API keys' }, 500);
  }
});

// Add/Update API key
app.post('/api/keys', async (req, res) => {
  try {
    const { service, keyName, keyValue, requestsPerHour } = req.body;

    const apiKey = await ApiKey.findOneAndUpdate(
      { service, keyName },
      {
        service,
        keyName,
        keyValue,
        rateLimit: { requestsPerHour: requestsPerHour || 1000 }
      },
      { new: true, upsert: true }
    );

    // Update environment file
    updateEnvFile(keyName, keyValue);

    sendJSON(res, { success: true, message: 'API key updated', keyId: apiKey._id });
  } catch (error) {
    console.error('API key update error:', error);
    sendJSON(res, { error: 'Failed to update API key' }, 500);
  }
});

// System health
app.get('/api/system/health', async (req, res) => {
  try {
    const health = {
      admin: 'healthy',
      database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
      aiServer: 'unknown',
      backend: 'unknown',
      frontend: 'unknown'
    };

    // Check AI server (using Docker container name)
    try {
      const aiResponse = await fetch('http://weather-nft-ai-server:3004/health');
      health.aiServer = aiResponse.ok ? 'healthy' : 'error';
    } catch (e) {
      health.aiServer = 'offline';
    }

    // Check backend (using Docker container name)
    try {
      const backendResponse = await fetch('http://weather-nft-backend:3001/health');
      health.backend = backendResponse.ok ? 'healthy' : 'error';
    } catch (e) {
      health.backend = 'offline';
    }

    // Check frontend (using Docker container name)
    try {
      const frontendResponse = await fetch('http://weather-nft-frontend:3000');
      health.frontend = frontendResponse.ok ? 'healthy' : 'error';
    } catch (e) {
      health.frontend = 'offline';
    }

    sendJSON(res, { success: true, health });
  } catch (error) {
    console.error('System health error:', error);
    sendJSON(res, { error: 'Failed to check system health' }, 500);
  }
});

// Force generate events (for testing)
app.post('/api/ai/force-generate', async (req, res) => {
  try {
    const { count = 5 } = req.body;
    
    // Call AI server to generate events (using Docker container name)
    const response = await fetch('http://weather-nft-ai-server:3004/api/events/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat: 40.7128, lng: -74.0060 })
    });

    const result = await response.json();
    
    sendJSON(res, { 
      success: true, 
      message: `Generated ${result.generated || 0} events`,
      events: result.events || []
    });
  } catch (error) {
    console.error('Force generate error:', error);
    sendJSON(res, { error: 'Failed to generate events' }, 500);
  }
});

// Update .env file
function updateEnvFile(keyName, keyValue) {
  try {
    const envPath = path.join(__dirname, '.env');
    let envContent = fs.readFileSync(envPath, 'utf8');
    
    const keyPattern = new RegExp(`^${keyName}=.*$`, 'm');
    const newLine = `${keyName}=${keyValue}`;
    
    if (keyPattern.test(envContent)) {
      envContent = envContent.replace(keyPattern, newLine);
    } else {
      envContent += `\n${newLine}`;
    }
    
    fs.writeFileSync(envPath, envContent);
    console.log(`✅ Updated ${keyName} in .env file`);
  } catch (error) {
    console.error('Failed to update .env file:', error);
  }
}

// Serve admin dashboard HTML
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WeatherNFT.live - Admin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: white;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .admin-header {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(16px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(16, 185, 129, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .admin-header h1 {
            background: linear-gradient(135deg, #6ee7b7 0%, #67e8f9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-indicator {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .admin-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .admin-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .admin-card {
            background: rgba(16, 185, 129, 0.1);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 1rem;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        .admin-card:hover {
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.3);
            transform: translateY(-4px);
        }
        
        .card-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .card-title {
            color: #6ee7b7;
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .card-icon {
            font-size: 2rem;
            margin-right: 1rem;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #67e8f9;
            display: block;
        }
        
        .stat-label {
            color: #9ca3af;
            font-size: 0.875rem;
        }
        
        .btn {
            background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }
        
        .table-container {
            background: rgba(16, 185, 129, 0.05);
            border-radius: 0.75rem;
            padding: 1rem;
            overflow-x: auto;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .table th, .table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid rgba(16, 185, 129, 0.1);
        }
        
        .table th {
            color: #6ee7b7;
            font-weight: 600;
        }
        
        .input-group {
            margin-bottom: 1rem;
        }
        
        .input-label {
            display: block;
            color: #6ee7b7;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .input-field {
            width: 100%;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 0.5rem;
            padding: 0.75rem;
            color: white;
            font-size: 1rem;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #10b981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #67e8f9;
        }
        
        .status-healthy { color: #10b981; }
        .status-error { color: #ef4444; }
        .status-offline { color: #6b7280; }
        
        .section-title {
            color: #6ee7b7;
            font-size: 1.5rem;
            margin: 2rem 0 1rem 0;
            border-bottom: 2px solid rgba(16, 185, 129, 0.3);
            padding-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <div class="admin-header">
        <h1>🌦️ WeatherNFT.live Admin Dashboard</h1>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>System Online</span>
        </div>
    </div>

    <div class="admin-container">
        <!-- Dashboard Stats -->
        <div class="admin-grid">
            <div class="admin-card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <h3 class="card-title">System Stats</h3>
                </div>
                <div id="systemStats" class="loading">Загрузка...</div>
            </div>

            <div class="admin-card">
                <div class="card-header">
                    <span class="card-icon">🤖</span>
                    <h3 class="card-title">AI Performance</h3>
                </div>
                <div id="aiPerformance" class="loading">Загрузка...</div>
            </div>

            <div class="admin-card">
                <div class="card-header">
                    <span class="card-icon">🔧</span>
                    <h3 class="card-title">System Health</h3>
                </div>
                <div id="systemHealth" class="loading">Загрузка...</div>
            </div>

            <div class="admin-card">
                <div class="card-header">
                    <span class="card-icon">⚡</span>
                    <h3 class="card-title">Quick Actions</h3>
                </div>
                <button class="btn btn-small" onclick="forceGenerateEvents()">Generate Test Events</button>
                <button class="btn btn-small" onclick="refreshDashboard()">Refresh Dashboard</button>
            </div>
        </div>

        <!-- API Keys Management -->
        <h2 class="section-title">🔑 API Keys Management</h2>
        <div class="admin-card">
            <div class="input-group">
                <label class="input-label">Service</label>
                <select id="apiService" class="input-field">
                    <option value="OPENWEATHER_API_KEY">OpenWeatherMap</option>
                    <option value="NASA_API_KEY">NASA API</option>
                    <option value="WEATHERAPI_KEY">WeatherAPI</option>
                </select>
            </div>
            <div class="input-group">
                <label class="input-label">API Key</label>
                <input type="text" id="apiKeyValue" class="input-field" placeholder="Enter API key">
            </div>
            <button class="btn" onclick="updateApiKey()">Update API Key</button>
        </div>

        <!-- Recent Events -->
        <h2 class="section-title">🌩️ Recent Weather Events</h2>
        <div class="admin-card">
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Event Name</th>
                            <th>AI Algorithm</th>
                            <th>Confidence</th>
                            <th>Rarity</th>
                            <th>Captures</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="eventsTable">
                        <tr><td colspan="7" class="loading">Загрузка событий...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Users Management -->
        <h2 class="section-title">👥 Users Management</h2>
        <div class="admin-card">
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Wallet Address</th>
                            <th>Credits</th>
                            <th>Total Captures</th>
                            <th>Success Rate</th>
                            <th>Joined</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="usersTable">
                        <tr><td colspan="6" class="loading">Загрузка пользователей...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Dashboard functionality
        let dashboardData = {};

        async function fetchDashboardStats() {
            try {
                const response = await fetch('/api/dashboard/stats');
                const data = await response.json();
                
                if (data.success) {
                    dashboardData.stats = data.stats;
                    renderSystemStats(data.stats);
                    renderRecentEvents(data.stats.recentEvents);
                }
            } catch (error) {
                console.error('Failed to fetch dashboard stats:', error);
            }
        }

        async function fetchAIPerformance() {
            try {
                const response = await fetch('/api/ai/performance');
                const data = await response.json();
                
                if (data.success) {
                    renderAIPerformance(data.algorithms);
                }
            } catch (error) {
                console.error('Failed to fetch AI performance:', error);
            }
        }

        async function fetchSystemHealth() {
            try {
                const response = await fetch('/api/system/health');
                const data = await response.json();
                
                if (data.success) {
                    renderSystemHealth(data.health);
                }
            } catch (error) {
                console.error('Failed to fetch system health:', error);
            }
        }

        async function fetchUsers() {
            try {
                const response = await fetch('/api/users/manage');
                const data = await response.json();
                
                if (data.success) {
                    renderUsers(data.users);
                }
            } catch (error) {
                console.error('Failed to fetch users:', error);
            }
        }

        function renderSystemStats(stats) {
            document.getElementById('systemStats').innerHTML = \`
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <span class="stat-number">\${stats.totalEvents}</span>
                        <span class="stat-label">Total Events</span>
                    </div>
                    <div>
                        <span class="stat-number">\${stats.activeEvents}</span>
                        <span class="stat-label">Active Events</span>
                    </div>
                    <div>
                        <span class="stat-number">\${stats.totalUsers}</span>
                        <span class="stat-label">Total Users</span>
                    </div>
                    <div>
                        <span class="stat-number">\${stats.totalCaptures}</span>
                        <span class="stat-label">Total Captures</span>
                    </div>
                </div>
            \`;
        }

        function renderAIPerformance(algorithms) {
            const html = algorithms.map(algo => \`
                <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(6, 182, 212, 0.1); border-radius: 0.5rem;">
                    <div style="font-weight: 600; color: #67e8f9;">\${algo._id}</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">
                        <div>Events: \${algo.totalEvents}</div>
                        <div>Confidence: \${(algo.avgConfidence * 100).toFixed(1)}%</div>
                        <div>Accuracy: \${algo.avgAccuracy?.toFixed(1) || 'N/A'}%</div>
                        <div>Success: \${(algo.successRate * 100).toFixed(1)}%</div>
                    </div>
                </div>
            \`).join('');
            
            document.getElementById('aiPerformance').innerHTML = html;
        }

        function renderSystemHealth(health) {
            const statusClass = (status) => {
                switch(status) {
                    case 'healthy': case 'connected': return 'status-healthy';
                    case 'error': case 'disconnected': return 'status-error';
                    default: return 'status-offline';
                }
            };

            document.getElementById('systemHealth').innerHTML = \`
                <div style="display: grid; gap: 0.5rem;">
                    <div>Admin: <span class="\${statusClass(health.admin)}">\${health.admin}</span></div>
                    <div>Database: <span class="\${statusClass(health.database)}">\${health.database}</span></div>
                    <div>AI Server: <span class="\${statusClass(health.aiServer)}">\${health.aiServer}</span></div>
                    <div>Backend: <span class="\${statusClass(health.backend)}">\${health.backend}</span></div>
                    <div>Frontend: <span class="\${statusClass(health.frontend)}">\${health.frontend}</span></div>
                </div>
            \`;
        }

        function renderRecentEvents(events) {
            const html = events.map(event => \`
                <tr>
                    <td>\${event.uniqueName}</td>
                    <td>\${event.aiAlgorithm}</td>
                    <td>\${(event.aiPrediction?.confidence * 100 || 0).toFixed(1)}%</td>
                    <td>\${event.rarity}</td>
                    <td>\${event.capturedCount}/\${event.captureSlots}</td>
                    <td>\${new Date(event.createdAt).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-small" onclick="toggleEvent('\${event.eventId}', \${!event.active})">
                            \${event.active ? 'Deactivate' : 'Activate'}
                        </button>
                    </td>
                </tr>
            \`).join('');
            
            document.getElementById('eventsTable').innerHTML = html;
        }

        function renderUsers(users) {
            const html = users.map(user => \`
                <tr>
                    <td>\${user.walletAddress?.substring(0, 12)}...</td>
                    <td>\${user.credits}</td>
                    <td>\${user.stats?.totalCaptures || 0}</td>
                    <td>\${(user.stats?.successRate * 100 || 0).toFixed(1)}%</td>
                    <td>\${new Date(user.createdAt).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-small" onclick="editUser('\${user.walletAddress}')">Edit</button>
                    </td>
                </tr>
            \`).join('');
            
            document.getElementById('usersTable').innerHTML = html;
        }

        async function updateApiKey() {
            const service = document.getElementById('apiService').value;
            const keyValue = document.getElementById('apiKeyValue').value;
            
            if (!keyValue) {
                alert('Please enter an API key');
                return;
            }

            try {
                const response = await fetch('/api/keys', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service: service.toLowerCase(),
                        keyName: service,
                        keyValue: keyValue
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    alert('API key updated successfully!');
                    document.getElementById('apiKeyValue').value = '';
                } else {
                    alert('Failed to update API key: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Failed to update API key: ' + error.message);
            }
        }

        async function forceGenerateEvents() {
            try {
                const response = await fetch('/api/ai/force-generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ count: 5 })
                });

                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    refreshDashboard();
                } else {
                    alert('Failed to generate events: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Failed to generate events: ' + error.message);
            }
        }

        async function toggleEvent(eventId, active) {
            try {
                const response = await fetch(\`/api/events/\${eventId}\`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ active })
                });

                const data = await response.json();
                
                if (data.success) {
                    refreshDashboard();
                } else {
                    alert('Failed to update event');
                }
            } catch (error) {
                alert('Failed to update event: ' + error.message);
            }
        }

        function editUser(walletAddress) {
            const newCredits = prompt('Enter new credit amount:');
            if (newCredits && !isNaN(newCredits)) {
                updateUserCredits(walletAddress, parseInt(newCredits));
            }
        }

        async function updateUserCredits(walletAddress, credits) {
            try {
                const response = await fetch(\`/api/users/\${walletAddress}/credits\`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credits })
                });

                const data = await response.json();
                
                if (data.success) {
                    alert('User credits updated successfully!');
                    fetchUsers();
                } else {
                    alert('Failed to update credits');
                }
            } catch (error) {
                alert('Failed to update credits: ' + error.message);
            }
        }

        function refreshDashboard() {
            fetchDashboardStats();
            fetchAIPerformance();
            fetchSystemHealth();
            fetchUsers();
        }

        // Initialize dashboard
        window.addEventListener('load', () => {
            refreshDashboard();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshDashboard, 30000);
        });
    </script>
</body>
</html>
  `);
});

// Start server
async function startServer() {
  try {
    await connectDB();

    const server = app.listen(PORT, () => {
      console.log('');
      console.log('🔧  WeatherNFT.live Admin Dashboard');
      console.log('=====================================');
      console.log(`🚀 Admin panel running on http://localhost:${PORT}`);
      console.log('📊 Full system monitoring and management');
      console.log('🔑 API keys management');
      console.log('🤖 AI algorithms monitoring');
      console.log('👥 Users and events management');
      console.log('');
      console.log('🔗 Open http://localhost:3005 to access admin panel');
    });

    server.on('error', (error) => {
      if (error.code === 'EADDRINUSE') {
        console.error(`❌ Port ${PORT} is already in use!`);
      } else {
        console.error('❌ Admin server error:', error);
      }
    });

  } catch (error) {
    console.error('Failed to start admin server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down admin dashboard...');
  process.exit(0);
});

startServer();