'use strict';

/**
 * Shared scoring utilities: map model confidence to rarity, combine multiple
 * signal scores, and assemble normalised detection records.
 */

const RARITY_ORDER = ['common', 'uncommon', 'rare', 'epic', 'legendary'];

const RARITY_MULTIPLIERS = {
  common: 1,
  uncommon: 2,
  rare: 5,
  epic: 10,
  legendary: 30
};

/**
 * Confidence (0..1) -> rarity tier. Tuned so only genuinely extreme, high
 * certainty events reach legendary.
 * @param {number} confidence
 * @returns {string}
 */
function confidenceToRarity(confidence) {
  const c = clamp01(confidence);
  if (c >= 0.95) return 'legendary';
  if (c >= 0.85) return 'epic';
  if (c >= 0.70) return 'rare';
  if (c >= 0.50) return 'uncommon';
  return 'common';
}

/**
 * Combine several independent 0..1 signal scores into one confidence using a
 * "noisy-OR" — multiple weak-but-aligned signals reinforce each other, which is
 * exactly how real severe-weather detection works (low pressure AND high wind
 * AND heavy rain => far more confident than any single factor).
 * @param {number[]} signals
 * @returns {number}
 */
function noisyOr(signals) {
  const valid = (signals || []).map(clamp01).filter((s) => s > 0);
  if (valid.length === 0) return 0;
  let complement = 1;
  for (const s of valid) complement *= 1 - s;
  return 1 - complement;
}

/**
 * Weighted mean of 0..1 signals.
 * @param {Array<[number, number]>} weightedSignals [score, weight] pairs.
 * @returns {number}
 */
function weightedScore(weightedSignals) {
  let num = 0;
  let den = 0;
  for (const [score, weight] of weightedSignals || []) {
    if (typeof score !== 'number') continue;
    num += clamp01(score) * weight;
    den += weight;
  }
  return den > 0 ? num / den : 0;
}

/**
 * Build a normalised detection record shared across all algorithms.
 * @param {Object} d
 * @returns {Object}
 */
function makeDetection(d) {
  const confidence = clamp01(d.confidence);
  const rarity = d.rarity || confidenceToRarity(confidence);
  return {
    type: d.type,
    rarity,
    confidence: round(confidence, 4),
    score: round(d.score ?? confidence, 4),
    value: d.value,
    description: d.description,
    algorithm: d.algorithm,
    signals: d.signals || {},
    valueMultiplier: RARITY_MULTIPLIERS[rarity] || 1
  };
}

function clamp01(x) {
  if (typeof x !== 'number' || Number.isNaN(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

function round(x, dp = 2) {
  const f = Math.pow(10, dp);
  return Math.round(x * f) / f;
}

function compareRarity(a, b) {
  return RARITY_ORDER.indexOf(b) - RARITY_ORDER.indexOf(a);
}

module.exports = {
  RARITY_ORDER,
  RARITY_MULTIPLIERS,
  confidenceToRarity,
  noisyOr,
  weightedScore,
  makeDetection,
  compareRarity,
  clamp01,
  round
};
