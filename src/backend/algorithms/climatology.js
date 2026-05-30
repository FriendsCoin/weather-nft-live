'use strict';

/**
 * Lightweight climatological baseline model.
 *
 * The legacy detector used fixed global thresholds (e.g. "35C = rare heat").
 * That ignores context: 30C in Reykjavik in January is a far rarer anomaly than
 * 38C in Dubai in July. This module provides season- and latitude-aware
 * expected values plus a standard-deviation so algorithms can compute proper
 * z-scores (how many sigma a reading is from its local normal).
 *
 * The model is deliberately compact and dependency-free — a smooth analytic
 * approximation rather than a giant lookup table — but captures the dominant
 * effects: latitude (equator warm, poles cold), seasonality (hemisphere-aware),
 * and continentality (variance grows away from the equator).
 */

const DEG2RAD = Math.PI / 180;

/**
 * Expected mean temperature (C) for a latitude/month.
 * @param {number} lat   Latitude in degrees (-90..90).
 * @param {number} month 0-11 (Jan..Dec).
 * @returns {number}
 */
function expectedTemperature(lat, month) {
  const absLat = Math.min(Math.abs(lat || 0), 90);
  // Base annual-mean temperature: ~27C at equator down to ~-25C at the poles.
  const annualMean = 27 - 0.58 * absLat;
  // Seasonal swing grows with latitude; flips sign in the southern hemisphere.
  const amplitude = 2 + 0.35 * absLat;
  // Northern hemisphere peaks in July (month 6); southern hemisphere in January.
  const phase = (lat || 0) >= 0 ? 6 : 0;
  const seasonal = amplitude * Math.cos(((month - phase) / 12) * 2 * Math.PI);
  return annualMean - Math.abs(seasonal) * 0 + seasonal;
}

/**
 * Expected temperature variability (sigma, C) for a latitude.
 * Tropics are stable; mid/high latitudes swing wildly.
 * @param {number} lat
 * @returns {number}
 */
function temperatureSigma(lat) {
  const absLat = Math.min(Math.abs(lat || 0), 90);
  return 3 + 0.12 * absLat; // ~3C tropics, ~14C poles
}

/**
 * Typical sea-level pressure is ~1013 hPa everywhere; storms are deep negative
 * departures. Sigma is fairly uniform (~7 hPa) but a touch higher at high lat.
 * @param {number} lat
 * @returns {{mean: number, sigma: number}}
 */
function pressureModel(lat) {
  const absLat = Math.min(Math.abs(lat || 0), 90);
  return { mean: 1013, sigma: 6 + 0.04 * absLat };
}

/**
 * Aurora visibility potential (0..1) as a function of geomagnetic latitude.
 * Sharply rises above ~55deg; near-zero in the tropics.
 * @param {number} lat
 * @returns {number}
 */
function auroraPotential(lat) {
  const absLat = Math.min(Math.abs(lat || 0), 90);
  if (absLat < 45) return Math.max(0, (absLat - 30) / 60); // faint chance 30-45
  // Logistic ramp centred on ~62deg.
  return 1 / (1 + Math.exp(-(absLat - 62) / 4));
}

/**
 * Standard score (z): how many sigma `value` is from `mean`.
 * @param {number} value
 * @param {number} mean
 * @param {number} sigma
 * @returns {number}
 */
function zScore(value, mean, sigma) {
  if (!sigma || sigma <= 0) return 0;
  return (value - mean) / sigma;
}

/**
 * Smooth 0..1 confidence from an absolute z-score using a logistic curve
 * centred at `midpoint` sigma. |z|>=midpoint+ -> high confidence.
 * @param {number} z
 * @param {number} [midpoint]
 * @param {number} [steepness]
 * @returns {number}
 */
function zToConfidence(z, midpoint = 2, steepness = 1.4) {
  const a = Math.abs(z);
  return 1 / (1 + Math.exp(-steepness * (a - midpoint)));
}

/**
 * Day-of-year sun elevation proxy (0..1) — used by aurora (needs darkness) and
 * heat algorithms. Crude but adequate: longer days near the summer solstice.
 * @param {number} lat
 * @param {number} month
 * @returns {number} fraction of the day that is dark (0..1)
 */
function darknessFraction(lat, month) {
  const phase = (lat || 0) >= 0 ? 6 : 0;
  const seasonal = Math.cos(((month - phase) / 12) * 2 * Math.PI); // +1 summer
  const absLat = Math.min(Math.abs(lat || 0), 90);
  const daylight = 0.5 + 0.45 * (seasonal * (absLat / 90));
  return Math.max(0.05, Math.min(0.95, 1 - daylight));
}

module.exports = {
  expectedTemperature,
  temperatureSigma,
  pressureModel,
  auroraPotential,
  darknessFraction,
  zScore,
  zToConfidence,
  DEG2RAD
};
