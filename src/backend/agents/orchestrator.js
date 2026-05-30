'use strict';

const EventEmitter = require('events');

/**
 * AgentOrchestrator — supervises a fleet of autonomous agents.
 *
 * Provides one place to register, start, pause and stop many agents, aggregates
 * their status for a control dashboard, and re-emits their action/error streams
 * so an HTTP layer or websocket can surface live agent activity.
 *
 * Emits: 'agent:action', 'agent:error', 'agent:cycle', 'agent:log'.
 */
class AgentOrchestrator extends EventEmitter {
  constructor(config = {}) {
    super();
    this.agents = new Map();
    this.logger = config.logger || (() => {});
    this.startedAt = null;
  }

  /**
   * Register an agent and wire its event stream into the orchestrator.
   * @param {import('./base-agent').BaseAgent} agent
   * @returns {AgentOrchestrator}
   */
  register(agent) {
    if (this.agents.has(agent.name)) {
      throw new Error(`Orchestrator: agent "${agent.name}" already registered`);
    }
    this.agents.set(agent.name, agent);
    agent.on('action', (a) => this.emit('agent:action', { agent: agent.name, action: a }));
    agent.on('error', (e) => this.emit('agent:error', { agent: agent.name, error: e.message || String(e) }));
    agent.on('cycle:end', (s) => this.emit('agent:cycle', s));
    agent.on('log', (l) => this.emit('agent:log', l));
    return this;
  }

  get(name) {
    return this.agents.get(name);
  }

  /** Start all (or one) agents. */
  startAll(opts = {}) {
    this.startedAt = this.startedAt || Date.now();
    for (const agent of this.agents.values()) agent.start(opts);
    this.logger(`[orchestrator] started ${this.agents.size} agent(s)`);
    return this;
  }

  start(name, opts) {
    const agent = this.get(name);
    if (agent) agent.start(opts);
    return this;
  }

  pauseAll() {
    for (const agent of this.agents.values()) agent.pause();
    return this;
  }

  stopAll() {
    for (const agent of this.agents.values()) agent.stop();
    this.logger('[orchestrator] stopped all agents');
    return this;
  }

  /** Trigger one immediate cycle across all agents (e.g. manual "scan now"). */
  async runOnce() {
    const results = [];
    for (const agent of this.agents.values()) {
      results.push(await agent.runCycle());
    }
    return results;
  }

  /** Aggregate status for a control panel. */
  status() {
    const agents = {};
    let totalActions = 0;
    for (const [name, agent] of this.agents) {
      agents[name] = agent.status();
      totalActions += agent.memory.counters.acted || 0;
    }
    return {
      agents,
      count: this.agents.size,
      running: Array.from(this.agents.values()).filter((a) => a.state === 'running').length,
      totalActions,
      startedAt: this.startedAt,
      uptimeMs: this.startedAt ? Date.now() - this.startedAt : 0
    };
  }
}

module.exports = { AgentOrchestrator };
