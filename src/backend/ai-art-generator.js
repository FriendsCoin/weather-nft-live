#!/usr/bin/env node

/**
 * AI Art Generator for WeatherNFT
 * Generates unique art from weather data using Stable Diffusion
 * Falls back to procedural generation if SD is unavailable
 */

const axios = require('axios');
const { createCanvas } = require('canvas');

class AIArtGenerator {
  constructor(config = {}) {
    this.config = {
      sdApiUrl: config.sdApiUrl || process.env.SD_AI_URL || 'http://localhost:8000',
      useRealSD: config.useRealSD || process.env.USE_REAL_AI === 'true',
      fallbackMode: config.fallbackMode || 'procedural', // 'procedural' or 'placeholder'
      imageWidth: config.imageWidth || 512,
      imageHeight: config.imageHeight || 512
    };

    this.weatherStyles = {
      clear: {
        colors: ['#87CEEB', '#FFD700', '#FFA500'],
        mood: 'bright and vibrant',
        style: 'ethereal sunlight'
      },
      cloudy: {
        colors: ['#778899', '#C0C0C0', '#696969'],
        mood: 'calm and peaceful',
        style: 'soft clouds'
      },
      rainy: {
        colors: ['#4682B4', '#5F9EA0', '#708090'],
        mood: 'dramatic and moody',
        style: 'rain streaks'
      },
      stormy: {
        colors: ['#2F4F4F', '#483D8B', '#191970'],
        mood: 'intense and powerful',
        style: 'lightning and storm clouds'
      },
      snowy: {
        colors: ['#F0F8FF', '#E0FFFF', '#B0E0E6'],
        mood: 'serene and cold',
        style: 'falling snow'
      },
      foggy: {
        colors: ['#DCDCDC', '#D3D3D3', '#C0C0C0'],
        mood: 'mysterious and ethereal',
        style: 'misty fog'
      }
    };
  }

  /**
   * Generate art from weather event
   * @param {Object} params - Generation parameters
   * @returns {Promise<Buffer>} Image buffer
   */
  async generateArt(params) {
    const {
      weatherData,
      eventData,
      location,
      rarity
    } = params;

    try {
      if (this.config.useRealSD) {
        return await this._generateWithStableDiffusion(params);
      } else {
        return await this._generateProceduralArt(params);
      }
    } catch (error) {
      console.error('❌ Art generation failed, falling back:', error.message);
      return await this._generateProceduralArt(params);
    }
  }

  /**
   * Generate art using Stable Diffusion API
   * @private
   */
  async _generateWithStableDiffusion(params) {
    const { weatherData, eventData, location, rarity } = params;

    console.log('🎨 Generating art with Stable Diffusion...');

    // Create detailed prompt from weather data
    const prompt = this._createSDPrompt(weatherData, eventData, location, rarity);
    const negativePrompt = 'ugly, blurry, low quality, distorted, text, watermark';

    try {
      const response = await axios.post(
        `${this.config.sdApiUrl}/generate`,
        {
          prompt: prompt,
          negative_prompt: negativePrompt,
          width: this.config.imageWidth,
          height: this.config.imageHeight,
          steps: rarity === 'legendary' ? 50 : rarity === 'epic' ? 40 : 30,
          cfg_scale: 7.5,
          seed: this._generateSeedFromWeather(weatherData)
        },
        { timeout: 120000 } // 2 minute timeout
      );

      if (response.data && response.data.image) {
        // Convert base64 to buffer
        return Buffer.from(response.data.image, 'base64');
      }

      throw new Error('Invalid response from SD API');

    } catch (error) {
      console.error('❌ Stable Diffusion generation failed:', error.message);
      throw error;
    }
  }

  /**
   * Generate procedural art (fallback)
   * @private
   */
  async _generateProceduralArt(params) {
    const { weatherData, eventData, location } = params;

    console.log('🎨 Generating procedural art...');

    const canvas = createCanvas(this.config.imageWidth, this.config.imageHeight);
    const ctx = canvas.getContext('2d');

    // Determine weather style
    const condition = weatherData.conditions || 'clear';
    const style = this.weatherStyles[condition] || this.weatherStyles.clear;

    // Background gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, this.config.imageHeight);
    gradient.addColorStop(0, style.colors[0]);
    gradient.addColorStop(0.5, style.colors[1]);
    gradient.addColorStop(1, style.colors[2]);

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, this.config.imageWidth, this.config.imageHeight);

    // Add weather-specific effects
    this._drawWeatherEffects(ctx, weatherData, style);

    // Add data visualization
    this._drawDataVisualization(ctx, weatherData, eventData);

    // Add location and timestamp
    this._drawMetadata(ctx, location, eventData);

    return canvas.toBuffer('image/png');
  }

  /**
   * Draw weather-specific visual effects
   * @private
   */
  _drawWeatherEffects(ctx, weatherData, style) {
    const { temperature, windSpeed, humidity, conditions } = weatherData;

    ctx.save();

    switch (conditions) {
      case 'rainy':
        this._drawRain(ctx, humidity);
        break;
      case 'stormy':
        this._drawLightning(ctx);
        this._drawRain(ctx, 80);
        break;
      case 'snowy':
        this._drawSnow(ctx, temperature);
        break;
      case 'cloudy':
        this._drawClouds(ctx);
        break;
      case 'clear':
        this._drawSun(ctx);
        break;
      case 'foggy':
        this._drawFog(ctx);
        break;
    }

    // Wind visualization
    if (windSpeed > 20) {
      this._drawWind(ctx, windSpeed);
    }

    ctx.restore();
  }

  /**
   * Draw rain effect
   * @private
   */
  _drawRain(ctx, intensity) {
    const drops = Math.floor((intensity / 100) * 200);

    ctx.strokeStyle = 'rgba(200, 200, 255, 0.3)';
    ctx.lineWidth = 2;

    for (let i = 0; i < drops; i++) {
      const x = Math.random() * this.config.imageWidth;
      const y = Math.random() * this.config.imageHeight;
      const length = 10 + Math.random() * 20;

      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x - 2, y + length);
      ctx.stroke();
    }
  }

  /**
   * Draw lightning effect
   * @private
   */
  _drawLightning(ctx) {
    const bolts = 2 + Math.floor(Math.random() * 3);

    for (let i = 0; i < bolts; i++) {
      ctx.strokeStyle = 'rgba(255, 255, 200, 0.8)';
      ctx.lineWidth = 3;
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#FFFF00';

      const startX = Math.random() * this.config.imageWidth;
      let currentX = startX;
      let currentY = 0;

      ctx.beginPath();
      ctx.moveTo(currentX, currentY);

      while (currentY < this.config.imageHeight) {
        currentX += (Math.random() - 0.5) * 50;
        currentY += 30 + Math.random() * 40;
        ctx.lineTo(currentX, currentY);
      }

      ctx.stroke();
      ctx.shadowBlur = 0;
    }
  }

  /**
   * Draw snow effect
   * @private
   */
  _drawSnow(ctx, temperature) {
    const flakes = 100 + Math.abs(temperature) * 5;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';

    for (let i = 0; i < flakes; i++) {
      const x = Math.random() * this.config.imageWidth;
      const y = Math.random() * this.config.imageHeight;
      const size = 2 + Math.random() * 4;

      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  /**
   * Draw clouds
   * @private
   */
  _drawClouds(ctx) {
    const cloudCount = 3 + Math.floor(Math.random() * 4);

    for (let i = 0; i < cloudCount; i++) {
      const x = Math.random() * this.config.imageWidth;
      const y = Math.random() * (this.config.imageHeight / 2);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';

      for (let j = 0; j < 5; j++) {
        const offsetX = (Math.random() - 0.5) * 80;
        const offsetY = (Math.random() - 0.5) * 30;
        const radius = 20 + Math.random() * 40;

        ctx.beginPath();
        ctx.arc(x + offsetX, y + offsetY, radius, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  /**
   * Draw sun
   * @private
   */
  _drawSun(ctx) {
    const centerX = this.config.imageWidth * 0.8;
    const centerY = this.config.imageHeight * 0.2;
    const radius = 60;

    // Sun glow
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 2);
    gradient.addColorStop(0, 'rgba(255, 255, 100, 0.8)');
    gradient.addColorStop(0.5, 'rgba(255, 200, 0, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 200, 0, 0)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, this.config.imageWidth, this.config.imageHeight);

    // Sun core
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  /**
   * Draw fog effect
   * @private
   */
  _drawFog(ctx) {
    for (let i = 0; i < 5; i++) {
      const y = (i / 5) * this.config.imageHeight;
      ctx.fillStyle = `rgba(220, 220, 220, ${0.1 + Math.random() * 0.2})`;
      ctx.fillRect(0, y, this.config.imageWidth, this.config.imageHeight / 5);
    }
  }

  /**
   * Draw wind effect
   * @private
   */
  _drawWind(ctx, windSpeed) {
    const lines = Math.floor(windSpeed / 5);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2;

    for (let i = 0; i < lines; i++) {
      const y = Math.random() * this.config.imageHeight;
      const length = 50 + Math.random() * 100;

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.quadraticCurveTo(length / 2, y - 10, length, y);
      ctx.stroke();
    }
  }

  /**
   * Draw data visualization
   * @private
   */
  _drawDataVisualization(ctx, weatherData, eventData) {
    const { temperature, humidity, pressure, windSpeed } = weatherData;

    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(10, this.config.imageHeight - 120, 220, 110);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(eventData.type.toUpperCase(), 20, this.config.imageHeight - 95);

    ctx.font = '14px Arial';
    ctx.fillText(`🌡️  ${temperature}°C`, 20, this.config.imageHeight - 70);
    ctx.fillText(`💨 ${windSpeed} km/h`, 20, this.config.imageHeight - 50);
    ctx.fillText(`💧 ${humidity}%`, 20, this.config.imageHeight - 30);

    ctx.restore();
  }

  /**
   * Draw metadata overlay
   * @private
   */
  _drawMetadata(ctx, location, eventData) {
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, this.config.imageWidth, 40);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 14px Arial';
    ctx.fillText(`${location.city}, ${location.country}`, 15, 25);

    const date = new Date(eventData.timestamp).toLocaleDateString();
    ctx.textAlign = 'right';
    ctx.fillText(date, this.config.imageWidth - 15, 25);

    ctx.restore();
  }

  /**
   * Create Stable Diffusion prompt from weather data
   * @private
   */
  _createSDPrompt(weatherData, eventData, location, rarity) {
    const { temperature, humidity, windSpeed, conditions } = weatherData;

    const style = this.weatherStyles[conditions] || this.weatherStyles.clear;

    const rarityStyles = {
      common: 'digital art',
      uncommon: 'digital art, detailed',
      rare: 'masterpiece digital art, highly detailed',
      epic: 'epic masterpiece, ultra detailed, cinematic lighting',
      legendary: 'legendary masterpiece, ultra detailed, 8k, award winning, cinematic'
    };

    const basePrompt = `${rarityStyles[rarity] || rarityStyles.common}, `;
    const weatherPrompt = `${conditions} weather scene, ${style.mood}, ${style.style}, `;
    const detailsPrompt = `temperature ${temperature}°C, wind ${windSpeed} km/h, `;
    const locationPrompt = `landscape of ${location.city}, ${location.country}, `;
    const artisticPrompt = 'trending on artstation, concept art, atmospheric, dramatic lighting';

    return basePrompt + weatherPrompt + detailsPrompt + locationPrompt + artisticPrompt;
  }

  /**
   * Generate deterministic seed from weather data
   * @private
   */
  _generateSeedFromWeather(weatherData) {
    const { temperature, humidity, pressure, windSpeed } = weatherData;
    return Math.abs(
      Math.floor(temperature * 1000 + humidity * 100 + pressure * 10 + windSpeed)
    );
  }

  /**
   * Test SD API connection
   * @returns {Promise<boolean>}
   */
  async testSDConnection() {
    try {
      const response = await axios.get(`${this.config.sdApiUrl}/health`, {
        timeout: 5000
      });
      console.log('✅ Stable Diffusion API connected');
      return true;
    } catch (error) {
      console.log('⚠️  Stable Diffusion API not available, using fallback');
      return false;
    }
  }
}

module.exports = AIArtGenerator;
