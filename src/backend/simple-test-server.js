#!/usr/bin/env node

// Simple test server to verify AI is working
require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3006; // Different port to avoid conflicts

app.use(cors());
app.use(express.json());

// Import only legacy AI
const AdvancedWeatherAI = require('./legacy-algorithms/advanced-ai-engine');
const advancedAI = new AdvancedWeatherAI();

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT.live Simple Test',
    ai_engine: 'JavaScript ML',
    timestamp: new Date().toISOString()
  });
});

// Compatible API endpoints for frontend
// Event generation (POST)
app.post('/api/events/generate', async (req, res) => {
  try {
    const { lat, lng } = req.body;
    
    // Mock weather data
    const weatherData = {
      temperature: Math.round(Math.random() * 50 - 10), // -10 to 40°C
      humidity: Math.round(Math.random() * 100),
      pressure: Math.round(980 + Math.random() * 60),
      windSpeed: Math.round(Math.random() * 80),
      visibility: Math.round(Math.random() * 20),
      conditions: ['clear', 'cloudy', 'rainy', 'stormy'][Math.floor(Math.random() * 4)]
    };
    
    const location = {
      lat: parseFloat(lat) || 40.7128,
      lng: parseFloat(lng) || -74.0060,
      city: 'Test Location',
      country: 'Test'
    };
    
    console.log(`🧠 Testing AI with: ${weatherData.temperature}°C, ${weatherData.windSpeed} km/h wind`);
    
    // Analyze with AI
    const analysis = await advancedAI.analyzeWeatherData(weatherData, location);
    
    res.json({
      success: true,
      message: 'AI is working!',
      generated_events: analysis.events.length,
      events: analysis.events,
      weather_data: weatherData,
      ml_analysis: analysis.ml_analysis,
      total_predictions: analysis.total_predictions,
      active_models: analysis.active_models
    });
    
  } catch (error) {
    console.error('❌ AI Error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      message: 'AI test failed'
    });
  }
});

// AI algorithms info (GET) - compatible with frontend
app.get('/api/ai/algorithms', async (req, res) => {
  try {
    const modelStats = advancedAI.getModelStats();
    const analytics = advancedAI.getRealtimeAnalytics();
    
    // Format for frontend compatibility
    const algorithms = [];
    for (const [name, stats] of Object.entries(modelStats)) {
      algorithms.push({
        name: name,
        accuracy: stats.accuracy,
        specialization: stats.specialization,
        type: stats.type,
        version: stats.version,
        predictions: stats.predictions || 0,
        realtime_stats: {
          predictions: stats.predictions || 0,
          avg_confidence: stats.avgConfidence || 0.85,
          model_size: stats.modelComplexity,
          last_used: stats.lastUsed,
          status: 'ready'
        }
      });
    }
    
    res.json({
      success: true,
      data: algorithms,
      count: algorithms.length,
      ai_engine: 'JavaScript ML',
      total_predictions: analytics.totalPredictions
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get AI statistics (alternative endpoint)
app.get('/api/test/stats', async (req, res) => {
  try {
    const modelStats = advancedAI.getModelStats();
    const analytics = advancedAI.getRealtimeAnalytics();
    
    res.json({
      success: true,
      model_stats: modelStats,
      analytics: analytics,
      message: 'AI statistics retrieved successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Additional endpoints for frontend compatibility
app.get('/api/events', async (req, res) => {
  try {
    // Mock active events for frontend
    const mockEvents = [
      {
        eventId: 'evt_001',
        uniqueName: 'Термальная Аномалия #1234',
        type: 'extreme_temperature',
        aiAlgorithm: 'ThermalDrift-v2',
        severity: 'high',
        rarity: 'rare',
        confidence: 0.89,
        captureSlots: 5,
        capturedCount: 2,
        price: 15,
        location: { city: 'Phoenix', country: 'USA' },
        weatherData: { temperature: 45, humidity: 20, windSpeed: 8 },
        active: true,
        createdAt: new Date()
      },
      {
        eventId: 'evt_002', 
        uniqueName: 'Грозовая Симфония #5678',
        type: 'thunderstorm',
        aiAlgorithm: 'StormChaser-v4',
        severity: 'extreme',
        rarity: 'epic',
        confidence: 0.95,
        captureSlots: 3,
        capturedCount: 1,
        price: 25,
        location: { city: 'Miami', country: 'USA' },
        weatherData: { temperature: 28, humidity: 85, windSpeed: 75 },
        active: true,
        createdAt: new Date()
      }
    ];

    res.json({
      success: true,
      data: mockEvents,
      count: mockEvents.length,
      totalValue: mockEvents.reduce((sum, event) => sum + event.price, 0)
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/analytics/stats', async (req, res) => {
  try {
    const analytics = advancedAI.getRealtimeAnalytics();
    
    const stats = {
      totalEvents: 42,
      activeEvents: 8,
      totalUsers: 156,
      totalGuilds: 3,
      totalCreditsSpent: 1247,
      avgAIAccuracy: analytics.avgAccuracy,
      systemUptime: process.uptime(),
      aiAlgorithmsActive: analytics.activeModels
    };

    res.json({
      success: true,
      data: stats
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'WeatherNFT.live AI Server',
    status: 'Running',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      algorithms: '/api/ai/algorithms',
      generateEvents: '/api/events/generate',
      events: '/api/events',
      stats: '/api/analytics/stats'
    }
  });
});

// Start server
app.listen(PORT, () => {
  console.log('🧪 WeatherNFT.live Simple Test Server');
  console.log('=====================================');
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`🧠 AI Engine: JavaScript ML (Legacy)`);
  console.log('');
  console.log('🔗 Test endpoints:');
  console.log(`   GET  /health - Health check`);
  console.log(`   POST /api/test/generate - Test AI event generation`);
  console.log(`   GET  /api/test/stats - AI statistics`);
  console.log('');
  console.log('🧪 Quick tests:');
  console.log(`   GET  http://localhost:${PORT}/api/ai/algorithms`);
  console.log(`   POST http://localhost:${PORT}/api/events/generate -d '{"lat":40.7,"lng":-74}'`);
  console.log('');
  console.log('🎯 Ready for AI testing!');
});