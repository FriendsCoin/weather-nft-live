'use strict';

/**
 * Agent tool layer.
 *
 * Agents act on the world exclusively through Tools — small, named, schema-
 * described capabilities with a single `execute()` entry point. Each tool wraps
 * a concrete effect (scan weather, generate art, mint an NFT, broadcast a
 * notification) behind an injectable executor, so the same agent runs against
 * real HTTP microservices in production and against in-memory fakes in tests.
 */

class Tool {
  /**
   * @param {Object} def
   * @param {string} def.name
   * @param {string} def.description
   * @param {Object} [def.schema]   Documented parameter shape.
   * @param {Function} def.execute  async (params, ctx) => result
   */
  constructor(def) {
    if (!def?.name || typeof def.execute !== 'function') {
      throw new Error('Tool requires a name and an execute() function');
    }
    this.name = def.name;
    this.description = def.description || '';
    this.schema = def.schema || {};
    this._execute = def.execute;
  }

  async execute(params = {}, ctx = {}) {
    return this._execute(params, ctx);
  }

  describe() {
    return { name: this.name, description: this.description, schema: this.schema };
  }
}

/**
 * Named collection of tools an agent is allowed to use.
 */
class Toolbox {
  constructor(tools = []) {
    this.tools = new Map();
    for (const t of tools) this.add(t);
  }

  add(tool) {
    const t = tool instanceof Tool ? tool : new Tool(tool);
    this.tools.set(t.name, t);
    return this;
  }

  has(name) {
    return this.tools.has(name);
  }

  get(name) {
    const t = this.tools.get(name);
    if (!t) throw new Error(`Toolbox: unknown tool "${name}"`);
    return t;
  }

  async run(name, params, ctx) {
    return this.get(name).execute(params, ctx);
  }

  list() {
    return Array.from(this.tools.values()).map((t) => t.describe());
  }
}

/**
 * Build the standard WeatherNFT toolbox.
 *
 * Every effect is overridable via `impls` so tests can inject fakes. The
 * default implementations talk to the platform's services through an injected
 * `http` client ({ get, post }) and the in-process detection/generation
 * subsystems.
 *
 * @param {Object} deps
 * @param {Object} [deps.detectionEngine]   algorithms/DetectionEngine
 * @param {Object} [deps.generator]         { generate(params) } (registry/facade)
 * @param {Object} [deps.http]              { get(url), post(url, body) }
 * @param {Object} [deps.endpoints]         service base URLs
 * @param {Object} [deps.impls]             per-tool override functions
 * @returns {Toolbox}
 */
function buildDefaultToolbox(deps = {}) {
  const {
    detectionEngine,
    generator,
    http,
    endpoints = {},
    impls = {}
  } = deps;

  const weatherUrl = endpoints.weather || process.env.WEATHER_API_URL || 'http://localhost:3012';
  const nftUrl = endpoints.nft || process.env.NFT_SERVICE_URL || 'http://localhost:3009';
  const wsUrl = endpoints.websocket || process.env.WEBSOCKET_URL || 'http://localhost:8080';

  const toolbox = new Toolbox();

  // --- scan_region: pull live weather for a set of locations ---------------
  toolbox.add(new Tool({
    name: 'scan_region',
    description: 'Fetch current weather for one or more locations.',
    schema: { locations: 'Array<{lat,lon,name?}>' },
    execute: impls.scan_region || (async ({ locations }) => {
      if (!http) throw new Error('scan_region: no http client configured');
      const res = await http.post(`${weatherUrl}/api/weather/batch`, { locations });
      const body = res.data || res;
      // Normalise to a flat list of weather readings.
      return (body.allResults || body.results || []).map((r) => ({
        location: r.location,
        weather: r.weather,
        error: r.error
      }));
    })
  }));

  // --- detect_events: run the modern ensemble over a reading ---------------
  toolbox.add(new Tool({
    name: 'detect_events',
    description: 'Run the detection-algorithm ensemble over a weather reading.',
    schema: { weather: 'Object', context: 'Object' },
    execute: impls.detect_events || (async ({ weather, context }) => {
      if (!detectionEngine) throw new Error('detect_events: no detection engine');
      return detectionEngine.analyze(weather, context || {});
    })
  }));

  // --- generate_art: produce an image for a detection ----------------------
  toolbox.add(new Tool({
    name: 'generate_art',
    description: 'Generate NFT artwork for a detected weather event.',
    schema: { weatherData: 'Object', eventData: 'Object', location: 'Object', rarity: 'string' },
    execute: impls.generate_art || (async (params) => {
      if (!generator) throw new Error('generate_art: no generator configured');
      return generator.generate(params);
    })
  }));

  // --- mint_nft: persist/mint an NFT via the NFT service -------------------
  toolbox.add(new Tool({
    name: 'mint_nft',
    description: 'Create an NFT record from a detected event and generated art.',
    schema: { eventId: 'string', weatherData: 'Object', eventData: 'Object', location: 'Object', rarity: 'string', algorithm: 'string' },
    execute: impls.mint_nft || (async (payload, ctx) => {
      if (!http) throw new Error('mint_nft: no http client configured');
      const headers = ctx?.authToken ? { Authorization: `Bearer ${ctx.authToken}` } : {};
      const res = await http.post(`${nftUrl}/api/nft/create-with-art`, payload, { headers });
      return res.data || res;
    })
  }));

  // --- notify: broadcast an event to connected clients ---------------------
  toolbox.add(new Tool({
    name: 'notify',
    description: 'Broadcast a real-time notification over the websocket bridge.',
    schema: { channel: 'string', event: 'Object' },
    execute: impls.notify || (async ({ channel, event }) => {
      if (!http) return { delivered: false, reason: 'no http client' };
      try {
        const res = await http.post(`${wsUrl}/broadcast`, { channel, event });
        return { delivered: true, response: res.data || res };
      } catch (err) {
        return { delivered: false, reason: err.message };
      }
    })
  }));

  return toolbox;
}

module.exports = { Tool, Toolbox, buildDefaultToolbox };
