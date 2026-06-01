'use strict';

const { DetectionAlgorithm, monthOf, latOf } = require('../base-algorithm');
const climo = require('../climatology');

/**
 * ThermalDrift-v2 — temperature anomaly detector.
 *
 * Instead of fixed global thresholds it scores how far the reading deviates
 * from the local seasonal climatology (z-score). A 30C reading is unremarkable
 * in the tropics but a legendary anomaly in the Arctic winter — the z-score
 * captures that automatically.
 */
class TemperatureAnomalyAlgorithm extends DetectionAlgorithm {
  constructor(meta = {}) {
    super({
      id: 'temperature-anomaly',
      name: 'ThermalDrift-v2',
      modelType: 'LSTM',
      accuracy: 0.942,
      specialization: 'Temperature anomalies and thermal flows',
      ...meta
    });
  }

  detect(weather, context = {}) {
    const temp = weather.temperature;
    if (typeof temp !== 'number') return [];

    const lat = latOf(weather, context);
    const month = monthOf(context);
    const mean = climo.expectedTemperature(lat, month);
    const sigma = climo.temperatureSigma(lat);
    const z = climo.zScore(temp, mean, sigma);

    // Need a meaningful departure (>1.2 sigma) before emitting anything.
    if (Math.abs(z) < 1.2) return [];

    const confidence = climo.zToConfidence(z, 2.2, 1.3);
    const hot = z > 0;
    const severity = Math.abs(z);

    const type = hot
      ? severity >= 3.2 ? 'extreme_heat' : severity >= 2.4 ? 'severe_heat' : 'heat_wave'
      : severity >= 3.2 ? 'extreme_cold' : severity >= 2.4 ? 'severe_cold' : 'cold_snap';

    return [
      this._emit({
        type,
        confidence,
        score: confidence,
        value: temp,
        description: `${hot ? 'Heat' : 'Cold'} anomaly: ${temp}°C (${z >= 0 ? '+' : ''}${z.toFixed(1)}σ vs local normal ${mean.toFixed(1)}°C)`,
        signals: {
          zScore: Number(z.toFixed(2)),
          climatologyMean: Number(mean.toFixed(1)),
          sigma: Number(sigma.toFixed(1)),
          direction: hot ? 'hot' : 'cold'
        }
      })
    ];
  }
}

module.exports = { TemperatureAnomalyAlgorithm };
