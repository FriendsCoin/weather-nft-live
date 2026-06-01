'use strict';

const { ImageProvider } = require('./base-provider');

let createCanvas = null;
try {
  // `canvas` is a declared dependency but optional at runtime (native build).
  ({ createCanvas } = require('canvas'));
} catch (_) {
  createCanvas = null;
}

/**
 * Always-available local generator. Renders weather art procedurally on a
 * node-canvas surface — zero network, zero credentials. Acts as the terminal
 * fallback in every generation chain so the platform always produces *an*
 * image even with no AI backend configured.
 */
class ProceduralProvider extends ImageProvider {
  constructor(config = {}) {
    super({ name: 'procedural', priority: 1000, tier: 'procedural', timeoutMs: 0, ...config });
    this.width = config.width || 512;
    this.height = config.height || 512;
    this.styles = {
      clear: ['#87CEEB', '#FFD700', '#FFA500'],
      cloudy: ['#778899', '#C0C0C0', '#696969'],
      rainy: ['#4682B4', '#5F9EA0', '#708090'],
      stormy: ['#2F4F4F', '#483D8B', '#191970'],
      thunderstorm: ['#2F4F4F', '#483D8B', '#191970'],
      snowy: ['#F0F8FF', '#E0FFFF', '#B0E0E6'],
      snow: ['#F0F8FF', '#E0FFFF', '#B0E0E6'],
      foggy: ['#DCDCDC', '#D3D3D3', '#C0C0C0'],
      fog: ['#DCDCDC', '#D3D3D3', '#C0C0C0'],
      aurora: ['#0B3D2E', '#1B9A6E', '#3A1078']
    };
  }

  async isAvailable() {
    return createCanvas !== null;
  }

  async _generate(request) {
    if (!createCanvas) {
      throw new Error('procedural: node-canvas is not installed');
    }
    const { context = {} } = request;
    const weatherData = context.weatherData || {};
    const eventData = context.eventData || { type: 'weather' };
    const location = context.location || { city: 'Unknown', country: '' };

    const canvas = createCanvas(this.width, this.height);
    const ctx = canvas.getContext('2d');

    const condition = (weatherData.conditions || 'clear').toLowerCase();
    const colors = this.styles[condition] || this.styles.clear;

    const gradient = ctx.createLinearGradient(0, 0, 0, this.height);
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(0.5, colors[1]);
    gradient.addColorStop(1, colors[2]);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, this.width, this.height);

    this._drawEffects(ctx, weatherData, condition);
    this._drawDataPanel(ctx, weatherData, eventData);
    this._drawHeader(ctx, location, eventData);

    return {
      buffer: canvas.toBuffer('image/png'),
      mimeType: 'image/png',
      seed: request.seed ?? null,
      meta: { renderer: 'node-canvas', condition }
    };
  }

  _drawEffects(ctx, w, condition) {
    ctx.save();
    switch (condition) {
      case 'rainy': this._rain(ctx, w.humidity || 50); break;
      case 'stormy':
      case 'thunderstorm': this._lightning(ctx); this._rain(ctx, 80); break;
      case 'snow':
      case 'snowy': this._snow(ctx, w.temperature || 0); break;
      case 'cloudy': this._clouds(ctx); break;
      case 'fog':
      case 'foggy': this._fog(ctx); break;
      case 'aurora': this._aurora(ctx); break;
      default: this._sun(ctx);
    }
    if ((w.windSpeed || 0) > 20) this._wind(ctx, w.windSpeed);
    ctx.restore();
  }

  _rain(ctx, intensity) {
    const drops = Math.floor((intensity / 100) * 200);
    ctx.strokeStyle = 'rgba(200, 200, 255, 0.3)';
    ctx.lineWidth = 2;
    for (let i = 0; i < drops; i++) {
      const x = Math.random() * this.width;
      const y = Math.random() * this.height;
      const len = 10 + Math.random() * 20;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x - 2, y + len);
      ctx.stroke();
    }
  }

  _lightning(ctx) {
    const bolts = 2 + Math.floor(Math.random() * 3);
    for (let i = 0; i < bolts; i++) {
      ctx.strokeStyle = 'rgba(255, 255, 200, 0.8)';
      ctx.lineWidth = 3;
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#FFFF00';
      let x = Math.random() * this.width;
      let y = 0;
      ctx.beginPath();
      ctx.moveTo(x, y);
      while (y < this.height) {
        x += (Math.random() - 0.5) * 50;
        y += 30 + Math.random() * 40;
        ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }
  }

  _snow(ctx, temperature) {
    const flakes = 100 + Math.abs(temperature) * 5;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    for (let i = 0; i < flakes; i++) {
      ctx.beginPath();
      ctx.arc(Math.random() * this.width, Math.random() * this.height, 2 + Math.random() * 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  _clouds(ctx) {
    const count = 3 + Math.floor(Math.random() * 4);
    for (let i = 0; i < count; i++) {
      const x = Math.random() * this.width;
      const y = Math.random() * (this.height / 2);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      for (let j = 0; j < 5; j++) {
        ctx.beginPath();
        ctx.arc(x + (Math.random() - 0.5) * 80, y + (Math.random() - 0.5) * 30, 20 + Math.random() * 40, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  _sun(ctx) {
    const cx = this.width * 0.8;
    const cy = this.height * 0.2;
    const r = 60;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 2);
    g.addColorStop(0, 'rgba(255, 255, 100, 0.8)');
    g.addColorStop(0.5, 'rgba(255, 200, 0, 0.3)');
    g.addColorStop(1, 'rgba(255, 200, 0, 0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, this.width, this.height);
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
  }

  _fog(ctx) {
    for (let i = 0; i < 5; i++) {
      const y = (i / 5) * this.height;
      ctx.fillStyle = `rgba(220, 220, 220, ${0.1 + Math.random() * 0.2})`;
      ctx.fillRect(0, y, this.width, this.height / 5);
    }
  }

  _aurora(ctx) {
    for (let i = 0; i < 4; i++) {
      const y = this.height * 0.15 + i * 30;
      const grad = ctx.createLinearGradient(0, y, this.width, y);
      grad.addColorStop(0, 'rgba(27, 154, 110, 0)');
      grad.addColorStop(0.5, `rgba(${50 + i * 30}, 220, ${120 + i * 20}, 0.5)`);
      grad.addColorStop(1, 'rgba(58, 16, 120, 0)');
      ctx.strokeStyle = grad;
      ctx.lineWidth = 18;
      ctx.beginPath();
      ctx.moveTo(0, y);
      for (let x = 0; x <= this.width; x += 20) {
        ctx.lineTo(x, y + Math.sin(x / 50 + i) * 25);
      }
      ctx.stroke();
    }
  }

  _wind(ctx, windSpeed) {
    const lines = Math.floor(windSpeed / 5);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2;
    for (let i = 0; i < lines; i++) {
      const y = Math.random() * this.height;
      const len = 50 + Math.random() * 100;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.quadraticCurveTo(len / 2, y - 10, len, y);
      ctx.stroke();
    }
  }

  _drawDataPanel(ctx, w, eventData) {
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(10, this.height - 120, 220, 110);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(String(eventData.type || 'WEATHER').toUpperCase(), 20, this.height - 95);
    ctx.font = '14px Arial';
    ctx.fillText(`temp ${w.temperature ?? '?'}C`, 20, this.height - 70);
    ctx.fillText(`wind ${w.windSpeed ?? '?'} km/h`, 20, this.height - 50);
    ctx.fillText(`humidity ${w.humidity ?? '?'}%`, 20, this.height - 30);
    ctx.restore();
  }

  _drawHeader(ctx, location, eventData) {
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, this.width, 40);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 14px Arial';
    ctx.fillText(`${location.city || 'Unknown'}${location.country ? ', ' + location.country : ''}`, 15, 25);
    if (eventData.timestamp) {
      ctx.textAlign = 'right';
      ctx.fillText(new Date(eventData.timestamp).toLocaleDateString(), this.width - 15, 25);
    }
    ctx.restore();
  }
}

module.exports = { ProceduralProvider };
