'use strict';

const { BaseAgent } = require('./base-agent');
const { DecisionPolicy } = require('./policy');
const { AgentMemory } = require('./memory');
const { DetectionEngine } = require('../algorithms');
const { buildDefaultToolbox } = require('./tools');

/**
 * WeatherHunterAgent — the platform's first truly autonomous actor.
 *
 * It continuously hunts the globe for rare weather: it perceives (scans a
 * watchlist of regions), reasons (runs the modern detection ensemble), decides
 * (applies an explicit policy with budget, cooldowns and dedupe), and acts
 * (generates art + mints an NFT + notifies subscribers) — all without a human
 * in the loop. Every step is injectable, so the agent is fully testable offline.
 */
class WeatherHunterAgent extends BaseAgent {
  /**
   * @param {Object} [config]
   * @param {Array} [config.watchlist]        [{ lat, lon, name, country }]
   * @param {DetectionEngine} [config.detectionEngine]
   * @param {Object} [config.generator]       { generate(params) }
   * @param {Object} [config.toolbox]         Pre-built Toolbox (else default)
   * @param {Object} [config.http]            HTTP client for default tools
   * @param {DecisionPolicy} [config.policy]
   * @param {string} [config.authToken]       Bearer token for minting
   * @param {boolean} [config.dryRun]         Decide but never mint
   */
  constructor(config = {}) {
    super({ name: config.name || 'WeatherHunter', intervalMs: config.intervalMs ?? 5 * 60 * 1000, memory: config.memory || new AgentMemory(), logger: config.logger });

    this.watchlist = config.watchlist || DEFAULT_WATCHLIST;
    this.detectionEngine = config.detectionEngine || new DetectionEngine();
    this.generator = config.generator || null;
    this.policy = config.policy || new DecisionPolicy();
    this.authToken = config.authToken || process.env.AGENT_AUTH_TOKEN || null;
    this.dryRun = config.dryRun ?? (process.env.AGENT_DRY_RUN === 'true');

    this.toolbox =
      config.toolbox ||
      buildDefaultToolbox({
        detectionEngine: this.detectionEngine,
        generator: this.generator,
        http: config.http,
        endpoints: config.endpoints
      });

    this._dayWindowStart = Date.now();
    this._actionsToday = 0;
  }

  // ----- PERCEIVE: scan the watchlist --------------------------------------
  async perceive() {
    const readings = await this.toolbox.run('scan_region', { locations: this.watchlist });
    return { readings: (readings || []).filter((r) => r && r.weather && !r.error) };
  }

  // ----- REASON: run the detection ensemble over every reading -------------
  async reason(perception) {
    const findings = [];
    for (const reading of perception.readings) {
      const context = { location: reading.location, timestamp: reading.weather.timestamp || Date.now() };
      const detections = await this.toolbox.run('detect_events', { weather: reading.weather, context });
      for (const detection of detections) {
        findings.push({ detection, weather: reading.weather, location: reading.location });
      }
    }
    // Highest-value first so the per-cycle cap spends budget on the best events.
    findings.sort((a, b) => this.policy.estimateValue(b.detection) - this.policy.estimateValue(a.detection));
    return findings;
  }

  // ----- DECIDE: apply the policy ------------------------------------------
  async decide(findings) {
    this._rollDailyWindow();
    const approved = [];
    let actionsThisCycle = 0;

    for (const finding of findings) {
      const signature = AgentMemory.signature(finding.detection, finding.location);
      const verdict = this.policy.decide(finding.detection, {
        memory: this.memory,
        location: finding.location,
        actionsThisCycle,
        actionsToday: this._actionsToday,
        signature
      });

      if (verdict.act) {
        actionsThisCycle += 1;
        approved.push({ ...finding, signature, value: verdict.value });
      } else {
        this.memory.record({ outcome: 'skipped', reason: verdict.reason, type: finding.detection.type, location: finding.location });
        this.memory.counters.skipped += 1;
      }
    }
    return approved;
  }

  // ----- ACT: generate art, mint, notify -----------------------------------
  async act(decisions) {
    const actions = [];
    for (const decision of decisions) {
      const { detection, weather, location, signature, value } = decision;
      const eventId = makeEventId(detection, location);
      try {
        // Mark seen immediately so concurrent cycles can't double-fire.
        this.memory.markSeen(signature);

        let art = null;
        if (this.generator && this.toolbox.has('generate_art')) {
          art = await this.toolbox.run('generate_art', {
            weatherData: weather,
            eventData: { type: detection.type, timestamp: Date.now() },
            location,
            rarity: detection.rarity
          });
        }

        let mint = { dryRun: true };
        if (!this.dryRun) {
          mint = await this.toolbox.run('mint_nft', {
            eventId,
            weatherData: weather,
            eventData: { type: detection.type, confidence: detection.confidence },
            location,
            rarity: detection.rarity,
            algorithm: detection.algorithm
          }, { authToken: this.authToken });
        }

        await this.toolbox.run('notify', {
          channel: 'weather_events',
          event: { type: 'autonomous_capture', eventId, detection, location, value, agent: this.name }
        }).catch(() => {});

        this._actionsToday += 1;
        const action = {
          outcome: 'acted',
          eventId,
          type: detection.type,
          rarity: detection.rarity,
          confidence: detection.confidence,
          value,
          location,
          provider: art?.provider || null,
          dryRun: this.dryRun,
          mint
        };
        this.memory.record(action);
        this.emit('action', action);
        this._log(`captured ${detection.rarity} ${detection.type} @ ${location.city || 'unknown'} (conf ${detection.confidence})`);
        actions.push(action);
      } catch (err) {
        this.memory.record({ outcome: 'failed', eventId, type: detection.type, error: err.message, location });
        this.memory.counters.failed += 1;
        this.emit('error', err);
        this._log(`action failed for ${detection.type}: ${err.message}`);
        actions.push({ outcome: 'failed', eventId, error: err.message });
      }
    }
    return actions;
  }

  _rollDailyWindow() {
    const DAY = 24 * 60 * 60 * 1000;
    if (Date.now() - this._dayWindowStart >= DAY) {
      this._dayWindowStart = Date.now();
      this._actionsToday = 0;
    }
  }

  status() {
    return {
      ...super.status(),
      dryRun: this.dryRun,
      watchlistSize: this.watchlist.length,
      actionsToday: this._actionsToday,
      policy: this.policy.describe(),
      algorithms: this.detectionEngine.describe().map((a) => a.id)
    };
  }
}

function makeEventId(detection, location) {
  const loc = (location.city || 'loc').toLowerCase().replace(/[^a-z0-9]+/g, '-');
  return `auto-${loc}-${detection.type}-${Date.now().toString(36)}`;
}

const DEFAULT_WATCHLIST = [
  { name: 'New York', lat: 40.7128, lon: -74.006, country: 'USA' },
  { name: 'London', lat: 51.5074, lon: -0.1278, country: 'UK' },
  { name: 'Tokyo', lat: 35.6762, lon: 139.6503, country: 'Japan' },
  { name: 'Sydney', lat: -33.8688, lon: 151.2093, country: 'Australia' },
  { name: 'Reykjavik', lat: 64.1466, lon: -21.9426, country: 'Iceland' },
  { name: 'Dubai', lat: 25.2048, lon: 55.2708, country: 'UAE' },
  { name: 'Mumbai', lat: 19.076, lon: 72.8777, country: 'India' },
  { name: 'Tromsø', lat: 69.6492, lon: 18.9553, country: 'Norway' }
];

module.exports = { WeatherHunterAgent, DEFAULT_WATCHLIST };
