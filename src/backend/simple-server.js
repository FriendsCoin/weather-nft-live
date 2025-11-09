#!/usr/bin/env node

// Упрощенный standalone сервер WeatherNFT без внешних зависимостей
const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

const PORT = 3002;
const WS_PORT = 8080;

// Mock данные для демонстрации
const mockWeatherEvents = [
  {
    id: '1',
    type: 'storm',
    location: { lat: 40.7128, lng: -74.0060, city: 'New York', country: 'USA' },
    severity: 'moderate',
    rarity: 'uncommon',
    timestamp: new Date().toISOString(),
    captureSlots: 5,
    capturedCount: 2,
    active: true,
    description: 'Thunderstorm with moderate precipitation',
    windSpeed: 45,
    temperature: 18,
    humidity: 85
  },
  {
    id: '2', 
    type: 'aurora',
    location: { lat: 64.2008, lng: -149.4937, city: 'Fairbanks', country: 'USA' },
    severity: 'high',
    rarity: 'rare',
    timestamp: new Date().toISOString(),
    captureSlots: 3,
    capturedCount: 0,
    active: true,
    description: 'Northern Lights activity detected',
    kpIndex: 6.2,
    visibility: 'excellent'
  },
  {
    id: '3',
    type: 'extreme_temperature',
    location: { lat: 25.7617, lng: -80.1918, city: 'Miami', country: 'USA' },
    severity: 'high',
    rarity: 'uncommon',
    timestamp: new Date().toISOString(),
    captureSlots: 8,
    capturedCount: 3,
    active: true,
    description: 'Extreme heat wave conditions',
    temperature: 42,
    heatIndex: 48,
    humidity: 78
  }
];

const mockGuilds = [
  {
    id: '1',
    name: 'Storm Hunters',
    members: 15,
    algorithm: 'storm_hunter',
    monthlyFee: 2,
    active: true,
    description: 'Elite weather trackers focusing on severe storms'
  },
  {
    id: '2',
    name: 'Aurora Watchers',
    members: 8,
    algorithm: 'aurora_predictor',
    monthlyFee: 3,
    active: true,
    description: 'Northern lights enthusiasts and researchers'
  }
];

const monitoredLocations = [
  { city: 'New York', country: 'USA', lat: 40.7128, lng: -74.0060 },
  { city: 'Tokyo', country: 'Japan', lat: 35.6762, lng: 139.6503 },
  { city: 'London', country: 'UK', lat: 51.5074, lng: -0.1278 },
  { city: 'Sydney', country: 'Australia', lat: -33.8688, lng: 151.2093 },
  { city: 'Fairbanks', country: 'USA', lat: 64.2008, lng: -149.4937 },
  { city: 'Miami', country: 'USA', lat: 25.7617, lng: -80.1918 }
];

// Утилиты для погодных расчетов
const weatherUtils = {
  calculateDewPoint: (temperature, humidity) => {
    const a = 17.27;
    const b = 237.7;
    const alpha = ((a * temperature) / (b + temperature)) + Math.log(humidity / 100);
    return (b * alpha) / (a - alpha);
  },

  calculateHeatIndex: (temperature, humidity) => {
    const T = temperature;
    const RH = humidity;
    
    if (T < 27) return T;
    
    const c1 = -8.78469475556;
    const c2 = 1.61139411;
    const c3 = 2.33854883889;
    const c4 = -0.14611605;
    const c5 = -0.012308094;
    const c6 = -0.0164248277778;
    const c7 = 0.002211732;
    const c8 = 0.00072546;
    const c9 = -0.000003582;
    
    return c1 + (c2 * T) + (c3 * RH) + (c4 * T * RH) + (c5 * T * T) + 
           (c6 * RH * RH) + (c7 * T * T * RH) + (c8 * T * RH * RH) + (c9 * T * T * RH * RH);
  },

  generateWeatherData: (lat, lon) => {
    const location = monitoredLocations.find(loc => 
      Math.abs(loc.lat - lat) < 0.1 && Math.abs(loc.lng - lon) < 0.1
    ) || { city: 'Unknown', country: 'Unknown', lat, lng: lon };

    return {
      location,
      temperature: Math.round(Math.random() * 40 - 10),
      humidity: Math.round(Math.random() * 100),
      windSpeed: Math.round(Math.random() * 50),
      pressure: Math.round(1000 + Math.random() * 50),
      visibility: Math.round(Math.random() * 20),
      conditions: ['clear', 'cloudy', 'rainy', 'stormy', 'snowy'][Math.floor(Math.random() * 5)],
      timestamp: new Date().toISOString()
    };
  }
};

// Простой CORS middleware
const setCORSHeaders = (res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
};

// JSON response helper
const sendJSON = (res, data, status = 200) => {
  setCORSHeaders(res);
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data, null, 2));
};

// Обработка маршрутов
const handleRequest = (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // Handle OPTIONS requests for CORS
  if (method === 'OPTIONS') {
    setCORSHeaders(res);
    res.writeHead(200);
    res.end();
    return;
  }

  console.log(`${method} ${pathname}`);

  try {
    // Health check
    if (pathname === '/health') {
      return sendJSON(res, {
        status: 'OK',
        timestamp: new Date().toISOString(),
        service: 'WeatherNFT Backend (Standalone)',
        version: '1.0.0'
      });
    }

    // Weather routes
    if (pathname.startsWith('/api/weather/current/')) {
      const parts = pathname.split('/');
      const lat = parseFloat(parts[4]);
      const lng = parseFloat(parts[5]);
      
      if (isNaN(lat) || isNaN(lng)) {
        return sendJSON(res, { error: 'Invalid coordinates' }, 400);
      }

      const weatherData = weatherUtils.generateWeatherData(lat, lng);
      return sendJSON(res, { success: true, data: weatherData });
    }

    if (pathname === '/api/weather/locations/monitored') {
      return sendJSON(res, {
        success: true,
        data: monitoredLocations,
        count: monitoredLocations.length
      });
    }

    if (pathname === '/api/weather/locations/all') {
      const allData = monitoredLocations.map(loc => 
        weatherUtils.generateWeatherData(loc.lat, loc.lng)
      );
      return sendJSON(res, {
        success: true,
        data: allData,
        count: allData.length
      });
    }

    // Events routes
    if (pathname === '/api/events') {
      return sendJSON(res, {
        success: true,
        data: mockWeatherEvents,
        count: mockWeatherEvents.length
      });
    }

    if (pathname === '/api/events/active') {
      const activeEvents = mockWeatherEvents.filter(event => event.active);
      return sendJSON(res, {
        success: true,
        data: activeEvents,
        count: activeEvents.length
      });
    }

    // Guild routes
    if (pathname === '/api/guild') {
      return sendJSON(res, {
        success: true,
        data: mockGuilds,
        count: mockGuilds.length
      });
    }

    // POST routes
    if (method === 'POST') {
      let body = '';
      req.on('data', chunk => { body += chunk; });
      req.on('end', () => {
        try {
          const data = JSON.parse(body);

          if (pathname === '/api/weather/calculate/dew-point') {
            const { temperature, humidity } = data;
            if (temperature === undefined || humidity === undefined) {
              return sendJSON(res, { error: 'Temperature and humidity required' }, 400);
            }
            const dewPoint = weatherUtils.calculateDewPoint(temperature, humidity);
            return sendJSON(res, {
              success: true,
              data: { temperature, humidity, dewPoint: Math.round(dewPoint * 100) / 100 }
            });
          }

          if (pathname === '/api/weather/calculate/heat-index') {
            const { temperature, humidity } = data;
            if (temperature === undefined || humidity === undefined) {
              return sendJSON(res, { error: 'Temperature and humidity required' }, 400);
            }
            const heatIndex = weatherUtils.calculateHeatIndex(temperature, humidity);
            return sendJSON(res, {
              success: true,
              data: { temperature, humidity, heatIndex: Math.round(heatIndex * 100) / 100 }
            });
          }

        } catch (error) {
          return sendJSON(res, { error: 'Invalid JSON data' }, 400);
        }
      });
      return;
    }

    // 404 for unmatched routes
    sendJSON(res, { error: 'Route not found' }, 404);

  } catch (error) {
    console.error('Request error:', error);
    sendJSON(res, { error: 'Internal server error' }, 500);
  }
};

// Создаем HTTP сервер
const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log('🌦️  WeatherNFT Standalone Server');
  console.log('================================');
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📡 WebSocket ready on ws://localhost:${WS_PORT}`);
  console.log('');
  console.log('Available endpoints:');
  console.log(`   GET  /health - Health check`);
  console.log(`   GET  /api/events - All weather events`);
  console.log(`   GET  /api/events/active - Active events only`);
  console.log(`   GET  /api/guild - All guilds`);
  console.log(`   GET  /api/weather/current/:lat/:lng - Weather data`);
  console.log(`   GET  /api/weather/locations/monitored - Monitored locations`);
  console.log(`   POST /api/weather/calculate/dew-point - Calculate dew point`);
  console.log(`   POST /api/weather/calculate/heat-index - Calculate heat index`);
  console.log('');
  console.log('💡 Test the API:');
  console.log(`   curl http://localhost:${PORT}/health`);
  console.log(`   node test-backend.js`);
});

server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use!`);
    console.log('💡 Try closing other applications or use a different port.');
  } else {
    console.error('❌ Server error:', error);
  }
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\\n🛑 Shutting down server...');
  server.close(() => {
    console.log('✅ Server closed successfully');
    process.exit(0);
  });
});

console.log('⏳ Starting WeatherNFT server...');