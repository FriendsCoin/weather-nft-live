'use strict';

const { RARITY_MULTIPLIERS } = require('../algorithms/scoring');

/**
 * Decision policy for autonomous agents.
 *
 * Given a detection plus the agent's memory and budget, decides whether the
 * agent should act (mint), skip, or defer. This is where "agency" becomes
 * accountable: every autonomous action is justified by an explicit, inspectable
 * rule set rather than firing on anything that crosses a threshold.
 */
class DecisionPolicy {
  /**
   * @param {Object} [opts]
   * @param {number} [opts.minConfidence]      Floor to consider acting.
   * @param {string[]} [opts.allowedRarities]  Rarities the agent may mint.
   * @param {number} [opts.cooldownMs]         Per-location action cooldown.
   * @param {number} [opts.maxActionsPerCycle] Cap actions per perceive cycle.
   * @param {number} [opts.dailyBudget]        Max actions per rolling 24h.
   * @param {string[]} [opts.focusAlgorithms]  Restrict to these algorithm ids.
   */
  constructor(opts = {}) {
    this.minConfidence = opts.minConfidence ?? 0.6;
    this.allowedRarities = opts.allowedRarities || ['rare', 'epic', 'legendary'];
    this.cooldownMs = opts.cooldownMs ?? 30 * 60 * 1000; // 30 min
    this.maxActionsPerCycle = opts.maxActionsPerCycle ?? 5;
    this.dailyBudget = opts.dailyBudget ?? 50;
    this.focusAlgorithms = opts.focusAlgorithms || null;
  }

  /**
   * Estimate the economic value of acting on a detection. Drives prioritisation
   * when more candidates exist than the per-cycle cap allows.
   * @param {Object} detection
   * @returns {number}
   */
  estimateValue(detection, basePriceXtz = 0.5) {
    const multiplier = RARITY_MULTIPLIERS[detection.rarity] || 1;
    // Confidence sharpens or discounts the headline rarity value.
    return Number((basePriceXtz * multiplier * (0.5 + detection.confidence / 2)).toFixed(3));
  }

  /**
   * Decide on a single detection.
   * @param {Object} detection
   * @param {Object} ctx { memory, location, actionsThisCycle, actionsToday }
   * @returns {{act: boolean, reason: string, value: number}}
   */
  decide(detection, ctx = {}) {
    const { memory, location = {}, actionsThisCycle = 0, actionsToday = 0 } = ctx;
    const value = this.estimateValue(detection);

    if (this.focusAlgorithms && !this.focusAlgorithms.includes(detection.algorithm)) {
      return reject('outside agent focus', value);
    }
    if (detection.confidence < this.minConfidence) {
      return reject(`confidence ${detection.confidence} < ${this.minConfidence}`, value);
    }
    if (!this.allowedRarities.includes(detection.rarity)) {
      return reject(`rarity ${detection.rarity} not in allowlist`, value);
    }
    if (actionsThisCycle >= this.maxActionsPerCycle) {
      return reject('per-cycle action cap reached', value);
    }
    if (actionsToday >= this.dailyBudget) {
      return reject('daily budget exhausted', value);
    }
    if (memory) {
      const sig = ctx.signature;
      if (sig && memory.hasSeen(sig)) {
        return reject('event already acted on (dedupe)', value);
      }
      const since = Date.now() - memory.lastActionAt(location);
      if (since < this.cooldownMs) {
        return reject(`location cooling down (${Math.round(since / 1000)}s)`, value);
      }
    }
    return { act: true, reason: 'meets policy', value };
  }

  describe() {
    return {
      minConfidence: this.minConfidence,
      allowedRarities: this.allowedRarities,
      cooldownMs: this.cooldownMs,
      maxActionsPerCycle: this.maxActionsPerCycle,
      dailyBudget: this.dailyBudget,
      focusAlgorithms: this.focusAlgorithms
    };
  }
}

function reject(reason, value) {
  return { act: false, reason, value };
}

module.exports = { DecisionPolicy };
