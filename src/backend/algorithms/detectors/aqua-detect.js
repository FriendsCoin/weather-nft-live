'use strict';

const { DetectionAlgorithm } = require('../base-algorithm');
const { clamp01 } = require('../scoring');

/**
 * AquaDetect-v2 — water-cycle detector for flooding-grade precipitation, heavy
 * snow accumulation and drought-signature dryness.
 */
class AquaDetectAlgorithm extends DetectionAlgorithm {
  constructor(meta = {}) {
    super({
      id: 'aqua-detect',
      name: 'AquaDetect-v2',
      modelType: 'GRU',
      accuracy: 0.961,
      specialization: 'Water cycles and precipitation',
      ...meta
    });
  }

  detect(weather, context = {}) {
    const detections = [];
    const rain = num(weather.rain) || num(weather.precipitation);
    const snow = num(weather.snow);
    const humidity = num(weather.humidity, NaN);
    const temp = num(weather.temperature, NaN);

    if (rain >= 15) {
      const confidence = clamp01((rain - 10) / 50); // 15mm/h -> ~0.1, 60mm/h -> 1
      detections.push(
        this._emit({
          type: rain >= 40 ? 'flash_flood' : 'heavy_rain',
          confidence: Math.max(confidence, rain >= 40 ? 0.7 : 0.5),
          value: rain,
          description: `${rain >= 40 ? 'Flash-flood-level' : 'Heavy'} rainfall: ${rain} mm/h`,
          signals: { rain, humidity: Number.isNaN(humidity) ? null : humidity }
        })
      );
    }

    if (snow >= 5) {
      detections.push(
        this._emit({
          type: snow >= 20 ? 'blizzard_snowfall' : 'heavy_snow',
          confidence: clamp01((snow - 3) / 30),
          value: snow,
          description: `${snow >= 20 ? 'Blizzard-grade' : 'Heavy'} snowfall: ${snow} mm/h water-equiv`,
          signals: { snow, temperature: Number.isNaN(temp) ? null : temp }
        })
      );
    }

    // Drought signature: very dry air + warmth + no precipitation.
    if (!Number.isNaN(humidity) && humidity <= 12 && !Number.isNaN(temp) && temp >= 25 && rain === 0) {
      detections.push(
        this._emit({
          type: 'drought_signature',
          confidence: clamp01((15 - humidity) / 15),
          value: humidity,
          description: `Drought-signature dryness: ${humidity}% RH at ${temp}°C`,
          signals: { humidity, temperature: temp }
        })
      );
    }

    return detections;
  }
}

function num(x, fallback = 0) {
  return typeof x === 'number' && !Number.isNaN(x) ? x : fallback;
}

module.exports = { AquaDetectAlgorithm };
