'use strict';

const { DetectionAlgorithm, latOf } = require('../base-algorithm');
const climo = require('../climatology');
const { noisyOr, clamp01 } = require('../scoring');

/**
 * StormChaser-v4 — multi-factor storm detector.
 *
 * Real storms light up several variables at once: deep low pressure, high wind,
 * and heavy precipitation. This detector fuses those signals with a noisy-OR so
 * that a coherent multi-signal storm scores far higher (and rarer) than any
 * single isolated reading — the key weakness of the old per-variable ladder.
 */
class StormHunterAlgorithm extends DetectionAlgorithm {
  constructor(meta = {}) {
    super({
      id: 'storm-hunter',
      name: 'StormChaser-v4',
      modelType: 'CNN-LSTM',
      accuracy: 0.978,
      specialization: 'Storm prediction and extreme weather',
      ...meta
    });
  }

  detect(weather, context = {}) {
    const wind = num(weather.windSpeed);
    const pressure = num(weather.pressure);
    const rain = num(weather.rain) || num(weather.precipitation);
    const lat = latOf(weather, context);

    // Individual normalised 0..1 signal strengths.
    const windSignal = ramp(wind, 35, 130); // 35 km/h breezy -> 130 hurricane
    const pressureSignal = pressure
      ? ramp(climo.pressureModel(lat).mean - pressure, 13, 70) // 13 hPa drop -> 70 hPa = catastrophic
      : 0;
    const rainSignal = ramp(rain, 5, 60); // 5mm/h -> 60mm/h torrential

    const confidence = noisyOr([windSignal, pressureSignal * 0.95, rainSignal * 0.7]);
    if (confidence < 0.45) return [];

    const activeSignals = [windSignal, pressureSignal, rainSignal].filter((s) => s > 0.25).length;
    const type =
      activeSignals >= 3 ? 'severe_thunderstorm'
        : windSignal >= 0.85 ? 'hurricane_force_winds'
          : pressureSignal >= 0.7 ? 'severe_storm'
            : windSignal >= 0.55 ? 'severe_winds'
              : 'storm';

    return [
      this._emit({
        type,
        confidence,
        score: confidence,
        value: { windSpeed: wind, pressure, rain },
        description: `Storm system: ${wind} km/h winds, ${pressure || '—'} hPa, ${rain} mm/h precipitation`,
        signals: {
          windSignal: r(windSignal),
          pressureSignal: r(pressureSignal),
          rainSignal: r(rainSignal),
          activeSignals
        }
      })
    ];
  }
}

function num(x) {
  return typeof x === 'number' && !Number.isNaN(x) ? x : 0;
}

// Linear ramp from `lo` (0) to `hi` (1), clamped.
function ramp(value, lo, hi) {
  if (value <= lo) return 0;
  if (value >= hi) return 1;
  return clamp01((value - lo) / (hi - lo));
}

function r(x) {
  return Math.round(x * 100) / 100;
}

module.exports = { StormHunterAlgorithm };
