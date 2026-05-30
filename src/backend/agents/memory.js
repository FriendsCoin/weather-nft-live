'use strict';

/**
 * Bounded agent memory.
 *
 * Gives an agent short-term recall so it can avoid re-acting on the same event,
 * respect per-location cooldowns, and expose a recent-activity trail for
 * observability. Intentionally in-process and bounded — no external store.
 */
class AgentMemory {
  /**
   * @param {Object} [opts]
   * @param {number} [opts.maxEvents]   Max remembered action records.
   * @param {number} [opts.dedupeTtlMs] How long an event signature is "seen".
   */
  constructor(opts = {}) {
    this.maxEvents = opts.maxEvents ?? 500;
    this.dedupeTtlMs = opts.dedupeTtlMs ?? 6 * 60 * 60 * 1000; // 6h
    this.history = [];
    this.seen = new Map(); // signature -> timestamp
    this.lastActionByLocation = new Map(); // locationKey -> timestamp
    this.counters = { perceived: 0, detected: 0, acted: 0, skipped: 0, failed: 0 };
  }

  /**
   * Stable signature for an event so repeats are recognised.
   * @param {Object} detection
   * @param {Object} location
   * @returns {string}
   */
  static signature(detection, location = {}) {
    const loc = location.city || `${round(location.lat)},${round(location.lng ?? location.lon)}`;
    return `${loc}:${detection.type}:${detection.rarity}`;
  }

  hasSeen(signature) {
    const ts = this.seen.get(signature);
    if (!ts) return false;
    if (Date.now() - ts > this.dedupeTtlMs) {
      this.seen.delete(signature);
      return false;
    }
    return true;
  }

  markSeen(signature) {
    this.seen.set(signature, Date.now());
  }

  locationKey(location = {}) {
    return location.city || `${round(location.lat)},${round(location.lng ?? location.lon)}`;
  }

  lastActionAt(location) {
    return this.lastActionByLocation.get(this.locationKey(location)) || 0;
  }

  record(entry) {
    const record = { at: Date.now(), ...entry };
    this.history.push(record);
    if (this.history.length > this.maxEvents) this.history.shift();
    if (entry.outcome && this.counters[entry.outcome] !== undefined) {
      this.counters[entry.outcome] += 1;
    }
    if (entry.outcome === 'acted' && entry.location) {
      this.lastActionByLocation.set(this.locationKey(entry.location), record.at);
    }
    return record;
  }

  recent(n = 20) {
    return this.history.slice(-n);
  }

  stats() {
    return { ...this.counters, remembered: this.history.length, seenSignatures: this.seen.size };
  }
}

function round(x) {
  return typeof x === 'number' ? Math.round(x * 100) / 100 : x;
}

module.exports = { AgentMemory };
