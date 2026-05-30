'use strict';

const scoring = require('./scoring');

/**
 * Base class for weather event detection algorithms.
 *
 * Each algorithm is a small, self-contained "expert" that inspects a weather
 * reading and emits zero or more detections, every one carrying a calibrated
 * confidence (0..1) and a derived rarity. This replaces the old monolithic
 * threshold `if`-ladder with composable, individually testable detectors that
 * mirror the platform's branded ML model names.
 */
class DetectionAlgorithm {
  /**
   * @param {Object} meta
   * @param {string} meta.id           Stable slug used in events (e.g. 'storm-hunter').
   * @param {string} meta.name         Branded model name (e.g. 'StormChaser-v4').
   * @param {string} meta.modelType    e.g. 'CNN-LSTM'.
   * @param {number} meta.accuracy     Reported accuracy 0..1.
   * @param {string} meta.specialization
   */
  constructor(meta = {}) {
    this.id = meta.id;
    this.name = meta.name;
    this.modelType = meta.modelType || 'heuristic';
    this.accuracy = meta.accuracy ?? 0.9;
    this.specialization = meta.specialization || '';
    this.enabled = meta.enabled !== false;
  }

  /**
   * Inspect a weather reading and return detections.
   * @param {Object} weather  Normalised weather object.
   * @param {Object} [context] { location, timestamp, month, ... }
   * @returns {Object[]} detection records (see scoring.makeDetection)
   */
  detect(weather, context = {}) {
    return [];
  }

  /**
   * Helper subclasses use to emit a normalised detection tagged with this
   * algorithm's id and reliability.
   * @protected
   */
  _emit(fields) {
    return scoring.makeDetection({ algorithm: this.id, ...fields });
  }

  /** Public metadata describing this algorithm. */
  info() {
    return {
      id: this.id,
      name: this.name,
      modelType: this.modelType,
      accuracy: this.accuracy,
      specialization: this.specialization,
      enabled: this.enabled
    };
  }
}

/**
 * Resolve the month index from a context or timestamp, defaulting to "now".
 * @param {Object} context
 * @returns {number} 0-11
 */
function monthOf(context = {}) {
  if (typeof context.month === 'number') return context.month;
  const ts = context.timestamp || Date.now();
  return new Date(ts).getUTCMonth();
}

/**
 * Best-effort latitude extraction from a weather/context object.
 * @param {Object} weather
 * @param {Object} context
 * @returns {number}
 */
function latOf(weather = {}, context = {}) {
  return (
    context.location?.lat ??
    weather.location?.lat ??
    weather.lat ??
    0
  );
}

module.exports = { DetectionAlgorithm, monthOf, latOf };
