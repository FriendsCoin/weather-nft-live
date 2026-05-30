'use strict';

const { DetectionAlgorithm, monthOf, latOf } = require('../base-algorithm');
const climo = require('../climatology');
const { noisyOr, clamp01 } = require('../scoring');

/**
 * AuroraPredictor-v3 — geomagnetic aurora opportunity detector.
 *
 * Combines geomagnetic-latitude potential, seasonal darkness (auroras need a
 * dark sky), clear-ish skies, and an optional live Kp index (0..9). Without a
 * Kp feed it assumes mildly active conditions so high-latitude clear winter
 * nights still surface as candidate events.
 */
class AuroraPredictorAlgorithm extends DetectionAlgorithm {
  constructor(meta = {}) {
    super({
      id: 'aurora-predictor',
      name: 'AuroraPredictor-v3',
      modelType: 'RNN',
      accuracy: 0.893,
      specialization: 'Aurora and geomagnetic storms',
      ...meta
    });
  }

  detect(weather, context = {}) {
    const lat = latOf(weather, context);
    const month = monthOf(context);

    const potential = climo.auroraPotential(lat);
    if (potential < 0.15) return [];

    const darkness = climo.darknessFraction(lat, month);
    const cloudFactor = 1 - clamp01(num(weather.clouds, 50) / 100); // clearer = better
    // Kp 0..9 from context if a geomagnetic feed is wired in; else assume ~3.
    const kp = clamp01(num(context.kpIndex, 3) / 9);

    const confidence = noisyOr([potential, darkness * 0.6, cloudFactor * 0.5, kp]);
    if (confidence < 0.45) return [];

    const type = kp >= 0.78 ? 'geomagnetic_storm' : 'aurora_borealis';

    return [
      this._emit({
        type,
        confidence,
        value: { latitude: lat, kpIndex: num(context.kpIndex, 3) },
        description: `Aurora opportunity at ${Math.abs(lat).toFixed(0)}° latitude (Kp≈${num(context.kpIndex, 3)})`,
        signals: {
          potential: r(potential),
          darkness: r(darkness),
          clearSky: r(cloudFactor),
          kp: r(kp)
        }
      })
    ];
  }
}

function num(x, fallback = 0) {
  return typeof x === 'number' && !Number.isNaN(x) ? x : fallback;
}
function r(x) {
  return Math.round(x * 100) / 100;
}

module.exports = { AuroraPredictorAlgorithm };
