#!/usr/bin/env node

/**
 * Weather API Service for WeatherNFT
 * Integrates with multiple weather data providers to detect real weather events
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.WEATHER_API_PORT || 3012;

app.use(cors());
app.use(express.json());

// API Configuration
const APIS = {
  openweather: {
    key: process.env.OPENWEATHER_API_KEY,
    baseUrl: 'https://api.openweathermap.org/data/2.5',
    enabled: !!process.env.OPENWEATHER_API_KEY
  },
  weatherapi: {
    key: process.env.WEATHERAPI_KEY,
    baseUrl: 'https://api.weatherapi.com/v1',
    enabled: !!process.env.WEATHERAPI_KEY
  }
};

// Rarity thresholds for weather events
const RARITY_THRESHOLDS = {
  temperature: {
    extreme_hot: { min: 45, rarity: 'legendary' },    // 45°C+
    very_hot: { min: 40, rarity: 'epic' },            // 40-45°C
    hot: { min: 35, rarity: 'rare' },                 // 35-40°C
    extreme_cold: { max: -30, rarity: 'legendary' },  // -30°C-
    very_cold: { max: -20, rarity: 'epic' },          // -30 to -20°C
    cold: { max: -10, rarity: 'rare' }                // -20 to -10°C
  },
  wind: {
    hurricane: { min: 120, rarity: 'legendary' },     // 120+ km/h
    very_strong: { min: 90, rarity: 'epic' },         // 90-120 km/h
    strong: { min: 60, rarity: 'rare' },              // 60-90 km/h
    moderate: { min: 40, rarity: 'uncommon' }         // 40-60 km/h
  },
  pressure: {
    extreme_low: { max: 950, rarity: 'legendary' },   // <950 hPa
    very_low: { max: 980, rarity: 'epic' },           // 950-980 hPa
    low: { max: 1000, rarity: 'rare' }                // 980-1000 hPa
  },
  visibility: {
    zero: { max: 0.1, rarity: 'epic' },               // <100m
    very_low: { max: 1, rarity: 'rare' },             // <1km
    low: { max: 5, rarity: 'uncommon' }               // <5km
  }
};

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'WeatherNFT Weather API Service',
    apis: {
      openweather: APIS.openweather.enabled,
      weatherapi: APIS.weatherapi.enabled
    },
    timestamp: new Date().toISOString()
  });
});

/**
 * Get current weather for a location
 * GET /api/weather/current
 */
app.get('/api/weather/current', async (req, res) => {
  try {
    const { lat, lon, city } = req.query;

    if (!lat && !lon && !city) {
      return res.status(400).json({
        success: false,
        error: 'Location required (lat/lon or city)'
      });
    }

    let weatherData;

    if (APIS.openweather.enabled) {
      weatherData = await fetchOpenWeatherMap({ lat, lon, city });
    } else if (APIS.weatherapi.enabled) {
      weatherData = await fetchWeatherAPI({ lat, lon, city });
    } else {
      return res.status(503).json({
        success: false,
        error: 'No weather API configured'
      });
    }

    res.json({
      success: true,
      data: weatherData,
      source: weatherData.source
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Detect weather events (anomalies)
 * GET /api/weather/detect-events
 */
app.get('/api/weather/detect-events', async (req, res) => {
  try {
    const { lat, lon, city } = req.query;

    // Get current weather
    const weatherData = await getCurrentWeather({ lat, lon, city });

    // Analyze for events
    const events = analyzeWeatherForEvents(weatherData);

    res.json({
      success: true,
      location: weatherData.location,
      weather: weatherData,
      events: events,
      timestamp: Date.now()
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get weather for multiple locations (for scanning)
 * POST /api/weather/batch
 */
app.post('/api/weather/batch', async (req, res) => {
  try {
    const { locations } = req.body;

    if (!locations || !Array.isArray(locations)) {
      return res.status(400).json({
        success: false,
        error: 'locations array required'
      });
    }

    const results = [];

    for (const location of locations) {
      try {
        const weather = await getCurrentWeather(location);
        const events = analyzeWeatherForEvents(weather);

        results.push({
          location: weather.location,
          weather: weather,
          events: events,
          hasEvents: events.length > 0
        });

        // Rate limiting
        await sleep(100);
      } catch (error) {
        results.push({
          location: location,
          error: error.message
        });
      }
    }

    // Filter locations with events
    const withEvents = results.filter(r => r.hasEvents);

    res.json({
      success: true,
      total: results.length,
      withEvents: withEvents.length,
      results: withEvents,
      allResults: results
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Search for weather events globally
 * GET /api/weather/scan
 */
app.get('/api/weather/scan', async (req, res) => {
  try {
    // Major cities around the world for scanning
    const majorCities = [
      { name: 'New York', lat: 40.7128, lon: -74.0060, country: 'USA' },
      { name: 'London', lat: 51.5074, lon: -0.1278, country: 'UK' },
      { name: 'Tokyo', lat: 35.6762, lon: 139.6503, country: 'Japan' },
      { name: 'Sydney', lat: -33.8688, lon: 151.2093, country: 'Australia' },
      { name: 'Mumbai', lat: 19.0760, lon: 72.8777, country: 'India' },
      { name: 'São Paulo', lat: -23.5505, lon: -46.6333, country: 'Brazil' },
      { name: 'Dubai', lat: 25.2048, lon: 55.2708, country: 'UAE' },
      { name: 'Singapore', lat: 1.3521, lon: 103.8198, country: 'Singapore' },
      { name: 'Moscow', lat: 55.7558, lon: 37.6173, country: 'Russia' },
      { name: 'Reykjavik', lat: 64.1466, lon: -21.9426, country: 'Iceland' }
    ];

    const detectedEvents = [];

    for (const city of majorCities) {
      try {
        const weather = await getCurrentWeather({ lat: city.lat, lon: city.lon });
        const events = analyzeWeatherForEvents(weather);

        if (events.length > 0) {
          detectedEvents.push({
            city: city.name,
            country: city.country,
            location: { lat: city.lat, lng: city.lon, city: city.name, country: city.country },
            weather: weather,
            events: events
          });
        }

        await sleep(200); // Rate limiting
      } catch (error) {
        console.error(`Error scanning ${city.name}:`, error.message);
      }
    }

    res.json({
      success: true,
      scannedLocations: majorCities.length,
      eventsDetected: detectedEvents.length,
      events: detectedEvents,
      timestamp: Date.now()
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Helper Functions

async function getCurrentWeather({ lat, lon, city }) {
  if (APIS.openweather.enabled) {
    return await fetchOpenWeatherMap({ lat, lon, city });
  } else if (APIS.weatherapi.enabled) {
    return await fetchWeatherAPI({ lat, lon, city });
  } else {
    throw new Error('No weather API configured');
  }
}

async function fetchOpenWeatherMap({ lat, lon, city }) {
  const params = {
    appid: APIS.openweather.key,
    units: 'metric'
  };

  if (lat && lon) {
    params.lat = lat;
    params.lon = lon;
  } else if (city) {
    params.q = city;
  }

  const response = await axios.get(`${APIS.openweather.baseUrl}/weather`, { params });
  const data = response.data;

  return {
    source: 'openweathermap',
    location: {
      city: data.name,
      country: data.sys.country,
      lat: data.coord.lat,
      lng: data.coord.lon
    },
    temperature: data.main.temp,
    feelsLike: data.main.feels_like,
    humidity: data.main.humidity,
    pressure: data.main.pressure,
    windSpeed: data.wind.speed * 3.6, // m/s to km/h
    windDirection: data.wind.deg,
    visibility: data.visibility / 1000, // meters to km
    conditions: data.weather[0].main.toLowerCase(),
    description: data.weather[0].description,
    clouds: data.clouds?.all || 0,
    rain: data.rain?.['1h'] || 0,
    snow: data.snow?.['1h'] || 0,
    timestamp: data.dt * 1000
  };
}

async function fetchWeatherAPI({ lat, lon, city }) {
  const params = {
    key: APIS.weatherapi.key,
    q: city || `${lat},${lon}`,
    aqi: 'no'
  };

  const response = await axios.get(`${APIS.weatherapi.baseUrl}/current.json`, { params });
  const data = response.data;

  return {
    source: 'weatherapi',
    location: {
      city: data.location.name,
      country: data.location.country,
      lat: data.location.lat,
      lng: data.location.lon
    },
    temperature: data.current.temp_c,
    feelsLike: data.current.feelslike_c,
    humidity: data.current.humidity,
    pressure: data.current.pressure_mb,
    windSpeed: data.current.wind_kph,
    windDirection: data.current.wind_degree,
    visibility: data.current.vis_km,
    conditions: data.current.condition.text.toLowerCase(),
    description: data.current.condition.text,
    clouds: data.current.cloud,
    uv: data.current.uv,
    timestamp: data.location.localtime_epoch * 1000
  };
}

function analyzeWeatherForEvents(weather) {
  const events = [];

  // Temperature events
  if (weather.temperature >= RARITY_THRESHOLDS.temperature.extreme_hot.min) {
    events.push({
      type: 'extreme_heat',
      rarity: 'legendary',
      value: weather.temperature,
      description: `Extreme heat: ${weather.temperature}°C`,
      algorithm: 'temperature-anomaly'
    });
  } else if (weather.temperature >= RARITY_THRESHOLDS.temperature.very_hot.min) {
    events.push({
      type: 'severe_heat',
      rarity: 'epic',
      value: weather.temperature,
      description: `Severe heat: ${weather.temperature}°C`,
      algorithm: 'temperature-anomaly'
    });
  } else if (weather.temperature >= RARITY_THRESHOLDS.temperature.hot.min) {
    events.push({
      type: 'heat_wave',
      rarity: 'rare',
      value: weather.temperature,
      description: `Heat wave: ${weather.temperature}°C`,
      algorithm: 'temperature-anomaly'
    });
  }

  if (weather.temperature <= RARITY_THRESHOLDS.temperature.extreme_cold.max) {
    events.push({
      type: 'extreme_cold',
      rarity: 'legendary',
      value: weather.temperature,
      description: `Extreme cold: ${weather.temperature}°C`,
      algorithm: 'temperature-anomaly'
    });
  } else if (weather.temperature <= RARITY_THRESHOLDS.temperature.very_cold.max) {
    events.push({
      type: 'severe_cold',
      rarity: 'epic',
      value: weather.temperature,
      description: `Severe cold: ${weather.temperature}°C`,
      algorithm: 'temperature-anomaly'
    });
  } else if (weather.temperature <= RARITY_THRESHOLDS.temperature.cold.max) {
    events.push({
      type: 'cold_snap',
      rarity: 'rare',
      value: weather.temperature,
      description: `Cold snap: ${weather.temperature}°C`,
      algorithm: 'temperature-anomaly'
    });
  }

  // Wind events
  if (weather.windSpeed >= RARITY_THRESHOLDS.wind.hurricane.min) {
    events.push({
      type: 'hurricane_force_winds',
      rarity: 'legendary',
      value: weather.windSpeed,
      description: `Hurricane force winds: ${weather.windSpeed} km/h`,
      algorithm: 'storm-hunter'
    });
  } else if (weather.windSpeed >= RARITY_THRESHOLDS.wind.very_strong.min) {
    events.push({
      type: 'severe_winds',
      rarity: 'epic',
      value: weather.windSpeed,
      description: `Severe winds: ${weather.windSpeed} km/h`,
      algorithm: 'storm-hunter'
    });
  } else if (weather.windSpeed >= RARITY_THRESHOLDS.wind.strong.min) {
    events.push({
      type: 'strong_winds',
      rarity: 'rare',
      value: weather.windSpeed,
      description: `Strong winds: ${weather.windSpeed} km/h`,
      algorithm: 'extreme-weather'
    });
  } else if (weather.windSpeed >= RARITY_THRESHOLDS.wind.moderate.min) {
    events.push({
      type: 'moderate_winds',
      rarity: 'uncommon',
      value: weather.windSpeed,
      description: `Moderate winds: ${weather.windSpeed} km/h`,
      algorithm: 'extreme-weather'
    });
  }

  // Pressure events (storms)
  if (weather.pressure <= RARITY_THRESHOLDS.pressure.extreme_low.max) {
    events.push({
      type: 'extreme_low_pressure',
      rarity: 'legendary',
      value: weather.pressure,
      description: `Extreme low pressure: ${weather.pressure} hPa`,
      algorithm: 'storm-hunter'
    });
  } else if (weather.pressure <= RARITY_THRESHOLDS.pressure.very_low.max) {
    events.push({
      type: 'severe_storm',
      rarity: 'epic',
      value: weather.pressure,
      description: `Severe storm: ${weather.pressure} hPa`,
      algorithm: 'storm-hunter'
    });
  } else if (weather.pressure <= RARITY_THRESHOLDS.pressure.low.max) {
    events.push({
      type: 'storm',
      rarity: 'rare',
      value: weather.pressure,
      description: `Storm conditions: ${weather.pressure} hPa`,
      algorithm: 'storm-hunter'
    });
  }

  // Visibility events (fog)
  if (weather.visibility <= RARITY_THRESHOLDS.visibility.zero.max) {
    events.push({
      type: 'zero_visibility',
      rarity: 'epic',
      value: weather.visibility,
      description: `Zero visibility: ${weather.visibility} km`,
      algorithm: 'micro-climate'
    });
  } else if (weather.visibility <= RARITY_THRESHOLDS.visibility.very_low.max) {
    events.push({
      type: 'dense_fog',
      rarity: 'rare',
      value: weather.visibility,
      description: `Dense fog: ${weather.visibility} km`,
      algorithm: 'micro-climate'
    });
  } else if (weather.visibility <= RARITY_THRESHOLDS.visibility.low.max) {
    events.push({
      type: 'fog',
      rarity: 'uncommon',
      value: weather.visibility,
      description: `Fog: ${weather.visibility} km`,
      algorithm: 'micro-climate'
    });
  }

  // Combined events
  if (weather.windSpeed > 60 && weather.pressure < 990 && weather.rain > 10) {
    events.push({
      type: 'severe_thunderstorm',
      rarity: 'epic',
      value: { wind: weather.windSpeed, pressure: weather.pressure, rain: weather.rain },
      description: `Severe thunderstorm detected`,
      algorithm: 'storm-hunter'
    });
  }

  return events;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('🌦️  WeatherNFT Weather API Service');
  console.log('=' .repeat(50));
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log('');
  console.log('🌍 Weather APIs:');
  console.log(`   • OpenWeatherMap: ${APIS.openweather.enabled ? '✅ Enabled' : '❌ Disabled'}`);
  console.log(`   • WeatherAPI: ${APIS.weatherapi.enabled ? '✅ Enabled' : '❌ Disabled'}`);
  console.log('');
  console.log('📊 Endpoints:');
  console.log('   • GET  /health                     - Health check');
  console.log('   • GET  /api/weather/current        - Get current weather');
  console.log('   • GET  /api/weather/detect-events  - Detect weather events');
  console.log('   • POST /api/weather/batch          - Batch locations');
  console.log('   • GET  /api/weather/scan           - Scan global events');
  console.log('');

  if (!APIS.openweather.enabled && !APIS.weatherapi.enabled) {
    console.log('⚠️  WARNING: No weather APIs configured!');
    console.log('   Add OPENWEATHER_API_KEY or WEATHERAPI_KEY to .env');
    console.log('');
  }
});

module.exports = app;
