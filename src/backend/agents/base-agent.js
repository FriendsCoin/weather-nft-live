'use strict';

const EventEmitter = require('events');
const { AgentMemory } = require('./memory');

/**
 * Base autonomous agent.
 *
 * Implements the lifecycle and the perceive -> reason -> decide -> act loop,
 * plus scheduling (run once, or on an interval), pause/resume, structured
 * status, and an event stream for observability. Concrete agents implement the
 * four cognitive phases.
 *
 * Emits: 'cycle:start', 'cycle:end', 'action', 'error', 'log'.
 */
class BaseAgent extends EventEmitter {
  /**
   * @param {Object} [config]
   * @param {string} [config.name]
   * @param {number} [config.intervalMs] Default loop interval.
   * @param {AgentMemory} [config.memory]
   * @param {Function} [config.logger]
   */
  constructor(config = {}) {
    super();
    this.name = config.name || this.constructor.name;
    this.intervalMs = config.intervalMs ?? 60000;
    this.memory = config.memory || new AgentMemory(config.memoryOptions);
    this.logger = config.logger || (() => {});
    this.state = 'idle'; // idle | running | paused | stopped
    this._timer = null;
    this._running = false;
    this.cycles = 0;
    this.startedAt = null;
    this.lastCycle = null;
    this.lastError = null;
  }

  // ----- cognitive phases (override in subclasses) -------------------------
  /** Gather observations from the world. @returns {Promise<Object>} */
  async perceive() { return {}; }
  /** Interpret observations into candidate findings. @returns {Promise<Object[]>} */
  async reason(_perception) { return []; }
  /** Choose which findings to act on. @returns {Promise<Object[]>} */
  async decide(_findings) { return []; }
  /** Execute the chosen decisions. @returns {Promise<Object[]>} */
  async act(_decisions) { return []; }

  /**
   * Run a single perceive->reason->decide->act cycle.
   * @returns {Promise<Object>} cycle summary
   */
  async runCycle() {
    if (this._running) {
      return { skipped: true, reason: 'previous cycle still running' };
    }
    this._running = true;
    const startedAt = Date.now();
    this.emit('cycle:start', { agent: this.name, cycle: this.cycles + 1 });
    const summary = {
      agent: this.name,
      cycle: this.cycles + 1,
      perceived: 0,
      findings: 0,
      decisions: 0,
      actions: [],
      errors: []
    };

    try {
      const perception = await this.perceive();
      summary.perceived = countPerception(perception);
      this.memory.counters.perceived += summary.perceived;

      const findings = await this.reason(perception);
      summary.findings = findings.length;
      this.memory.counters.detected += findings.length;

      const decisions = await this.decide(findings);
      summary.decisions = decisions.length;

      const actions = await this.act(decisions);
      summary.actions = actions;
    } catch (err) {
      this.lastError = err.message;
      summary.errors.push(err.message);
      this.memory.counters.failed += 1;
      this.emit('error', err);
      this._log(`cycle error: ${err.message}`);
    } finally {
      this.cycles += 1;
      summary.durationMs = Date.now() - startedAt;
      this.lastCycle = summary;
      this._running = false;
      this.emit('cycle:end', summary);
    }
    return summary;
  }

  /**
   * Start the autonomous loop.
   * @param {Object} [opts]
   * @param {number} [opts.intervalMs]
   * @param {boolean} [opts.immediate] Run a cycle right away.
   */
  start(opts = {}) {
    if (this.state === 'running') return this;
    this.intervalMs = opts.intervalMs ?? this.intervalMs;
    this.state = 'running';
    this.startedAt = this.startedAt || Date.now();
    this._log(`started (interval ${this.intervalMs}ms)`);

    const tick = () => {
      if (this.state !== 'running') return;
      this.runCycle().catch((e) => this.emit('error', e));
    };
    if (opts.immediate !== false) tick();
    this._timer = setInterval(tick, this.intervalMs);
    if (this._timer.unref) this._timer.unref();
    return this;
  }

  pause() {
    if (this.state === 'running') {
      this.state = 'paused';
      this._clearTimer();
      this._log('paused');
    }
    return this;
  }

  resume() {
    if (this.state === 'paused') this.start({ immediate: false });
    return this;
  }

  stop() {
    this.state = 'stopped';
    this._clearTimer();
    this._log('stopped');
    return this;
  }

  status() {
    return {
      name: this.name,
      state: this.state,
      cycles: this.cycles,
      intervalMs: this.intervalMs,
      startedAt: this.startedAt,
      uptimeMs: this.startedAt ? Date.now() - this.startedAt : 0,
      lastError: this.lastError,
      lastCycle: this.lastCycle,
      memory: this.memory.stats()
    };
  }

  _clearTimer() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
  }

  _log(message) {
    const line = `[agent:${this.name}] ${message}`;
    this.logger(line);
    this.emit('log', line);
  }
}

function countPerception(p) {
  if (Array.isArray(p)) return p.length;
  if (p && Array.isArray(p.readings)) return p.readings.length;
  return p ? 1 : 0;
}

module.exports = { BaseAgent };
