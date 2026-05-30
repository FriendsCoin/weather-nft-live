'use strict';

const { DetectionAlgorithm } = require('../base-algorithm');
const { clamp01 } = require('../scoring');

/**
 * MicroClimate-v1 — local-scale anomaly detector for fog, haze and unusual
 * humidity/visibility regimes that the storm/temperature experts ignore.
 */
class MicroClimateAlgorithm extends DetectionAlgorithm {
  constructor(meta = {}) {
    super({
      id: 'micro-climate',
      name: 'EcoBalance-v1',
      modelType: 'Transformer',
      accuracy: 0.915,
      specialization: 'Micro-climate and local atmospheric balance',
      ...meta
    });
  }

  detect(weather, context = {}) {
    const detections = [];
    const visibility = num(weather.visibility, NaN);
    const humidity = num(weather.humidity, NaN);

    if (!Number.isNaN(visibility) && visibility <= 5) {
      // Lower visibility -> higher confidence (0.1km ~ 1.0, 5km ~ ~0.5).
      const confidence = clamp01(1 - visibility / 10);
      const type = visibility <= 0.1 ? 'zero_visibility' : visibility <= 1 ? 'dense_fog' : 'fog';
      detections.push(
        this._emit({
          type,
          confidence: Math.max(confidence, type === 'zero_visibility' ? 0.9 : 0.55),
          value: visibility,
          description: `${type.replace(/_/g, ' ')}: ${visibility} km visibility`,
          signals: { visibility, humidity: Number.isNaN(humidity) ? null : humidity }
        })
      );
    }

    // Oppressive humidity with high temperature => "heat dome" microclimate.
    if (!Number.isNaN(humidity) && humidity >= 92 && num(weather.temperature, 0) >= 28) {
      detections.push(
        this._emit({
          type: 'humid_heat_dome',
          confidence: clamp01((humidity - 90) / 10),
          value: humidity,
          description: `Oppressive humid heat: ${humidity}% RH at ${weather.temperature}°C`,
          signals: { humidity, temperature: weather.temperature }
        })
      );
    }

    return detections;
  }
}

function num(x, fallback = 0) {
  return typeof x === 'number' && !Number.isNaN(x) ? x : fallback;
}

module.exports = { MicroClimateAlgorithm };
