'use strict';

const { TemperatureAnomalyAlgorithm } = require('./detectors/temperature-anomaly');
const { StormHunterAlgorithm } = require('./detectors/storm-hunter');
const { MicroClimateAlgorithm } = require('./detectors/micro-climate');
const { AuroraPredictorAlgorithm } = require('./detectors/aurora-predictor');
const { AquaDetectAlgorithm } = require('./detectors/aqua-detect');
const { compareRarity } = require('./scoring');

/**
 * Orchestrates the full ensemble of detection algorithms over a weather
 * reading, deduplicates overlapping detections, and ranks them by rarity then
 * confidence. This is the modern replacement for the monolithic
 * `analyzeWeatherForEvents()` threshold function.
 */
class DetectionEngine {
  /**
   * @param {Object} [options]
   * @param {DetectionAlgorithm[]} [options.algorithms] Custom ensemble.
   * @param {number} [options.minConfidence] Drop detections below this.
   */
  constructor(options = {}) {
    this.minConfidence = options.minConfidence ?? 0.45;
    this.algorithms =
      options.algorithms ||
      [
        new TemperatureAnomalyAlgorithm(),
        new StormHunterAlgorithm(),
        new MicroClimateAlgorithm(),
        new AuroraPredictorAlgorithm(),
        new AquaDetectAlgorithm()
      ];
  }

  /** @returns {Object[]} metadata for every registered algorithm. */
  describe() {
    return this.algorithms.map((a) => a.info());
  }

  register(algorithm) {
    this.algorithms.push(algorithm);
    return this;
  }

  /**
   * Run the ensemble.
   * @param {Object} weather  Normalised weather reading.
   * @param {Object} [context] { location, timestamp, kpIndex, ... }
   * @returns {Object[]} ranked detections.
   */
  analyze(weather, context = {}) {
    if (!weather || typeof weather !== 'object') return [];

    const raw = [];
    for (const algo of this.algorithms) {
      if (!algo.enabled) continue;
      try {
        const found = algo.detect(weather, context) || [];
        for (const d of found) raw.push(d);
      } catch (err) {
        // One faulty detector must never break the whole scan.
        // eslint-disable-next-line no-console
        console.error(`[detection-engine] ${algo.id} failed:`, err.message);
      }
    }

    const filtered = raw.filter((d) => d && d.confidence >= this.minConfidence);
    const deduped = this._dedupe(filtered);
    return deduped.sort(
      (a, b) => compareRarity(a.rarity, b.rarity) || b.confidence - a.confidence
    );
  }

  /**
   * Collapse duplicate event types, keeping the highest-confidence instance.
   * @private
   */
  _dedupe(detections) {
    const byType = new Map();
    for (const d of detections) {
      const existing = byType.get(d.type);
      if (!existing || d.confidence > existing.confidence) byType.set(d.type, d);
    }
    return Array.from(byType.values());
  }

  /**
   * Convenience: the single most significant detection, or null.
   * @param {Object} weather
   * @param {Object} [context]
   * @returns {Object|null}
   */
  topDetection(weather, context = {}) {
    return this.analyze(weather, context)[0] || null;
  }
}

module.exports = { DetectionEngine };
