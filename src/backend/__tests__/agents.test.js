'use strict';

const {
  WeatherHunterAgent,
  AgentOrchestrator,
  DecisionPolicy,
  AgentMemory,
  Toolbox,
  Tool
} = require('../agents');
const { scoring } = require('../algorithms');

/** Build a fake HTTP client that routes by URL and records side effects. */
function fakeHttp({ readings }) {
  const mints = [];
  const notifies = [];
  const client = {
    get: async () => ({ data: {} }),
    post: async (url, body) => {
      if (url.includes('/api/weather/batch')) return { data: { allResults: readings } };
      if (url.includes('/api/nft/create-with-art')) {
        mints.push(body);
        return { data: { success: true, eventId: body.eventId } };
      }
      if (url.includes('/broadcast')) {
        notifies.push(body);
        return { data: { ok: true } };
      }
      throw new Error(`unexpected POST ${url}`);
    }
  };
  return { client, mints, notifies };
}

const fakeGenerator = {
  generate: async () => ({ provider: 'fake', tier: 'diffusion', buffer: Buffer.from('img'), seed: 1, meta: {} })
};

const STORMY_READING = {
  location: { city: 'Miami', country: 'USA', lat: 25.76, lng: -80.19 },
  weather: { temperature: 27, windSpeed: 100, pressure: 965, rain: 35, humidity: 85, visibility: 9, clouds: 90, timestamp: Date.now() }
};
const CALM_READING = {
  location: { city: 'San Diego', country: 'USA', lat: 32.7, lng: -117.16 },
  weather: { temperature: 22, windSpeed: 8, pressure: 1015, rain: 0, humidity: 50, visibility: 16, clouds: 5, timestamp: Date.now() }
};

describe('DecisionPolicy', () => {
  test('approves a confident allowed-rarity detection', () => {
    const policy = new DecisionPolicy();
    const v = policy.decide({ type: 'storm', rarity: 'epic', confidence: 0.9, algorithm: 'storm-hunter' }, {});
    expect(v.act).toBe(true);
    expect(v.value).toBeGreaterThan(0);
  });

  test('rejects low-confidence and disallowed rarity', () => {
    const policy = new DecisionPolicy();
    expect(policy.decide({ rarity: 'epic', confidence: 0.3, algorithm: 'x' }, {}).act).toBe(false);
    expect(policy.decide({ rarity: 'common', confidence: 0.99, algorithm: 'x' }, {}).act).toBe(false);
  });

  test('enforces the per-cycle cap and daily budget', () => {
    const policy = new DecisionPolicy({ maxActionsPerCycle: 1, dailyBudget: 1 });
    const d = { rarity: 'legendary', confidence: 0.99, algorithm: 'x' };
    expect(policy.decide(d, { actionsThisCycle: 1 }).act).toBe(false);
    expect(policy.decide(d, { actionsToday: 1 }).act).toBe(false);
  });

  test('estimateValue scales with rarity and confidence', () => {
    const policy = new DecisionPolicy();
    const legendary = policy.estimateValue({ rarity: 'legendary', confidence: 1 });
    const common = policy.estimateValue({ rarity: 'common', confidence: 0.5 });
    expect(legendary).toBeGreaterThan(common);
  });
});

describe('AgentMemory', () => {
  test('dedupe + cooldown bookkeeping', () => {
    const mem = new AgentMemory();
    const sig = AgentMemory.signature({ type: 'storm', rarity: 'epic' }, { city: 'Miami' });
    expect(mem.hasSeen(sig)).toBe(false);
    mem.markSeen(sig);
    expect(mem.hasSeen(sig)).toBe(true);
    mem.record({ outcome: 'acted', location: { city: 'Miami' } });
    expect(mem.lastActionAt({ city: 'Miami' })).toBeGreaterThan(0);
    expect(mem.stats().acted).toBe(1);
  });
});

describe('Toolbox', () => {
  test('runs a registered tool and rejects unknown tools', async () => {
    const box = new Toolbox([new Tool({ name: 'echo', execute: async (p) => p.msg })]);
    await expect(box.run('echo', { msg: 'hi' })).resolves.toBe('hi');
    expect(() => box.get('missing')).toThrow(/unknown tool/);
  });
});

describe('WeatherHunterAgent', () => {
  function buildAgent(overrides = {}) {
    const { client, mints, notifies } = fakeHttp({ readings: [STORMY_READING, CALM_READING] });
    const agent = new WeatherHunterAgent({
      generator: fakeGenerator,
      http: client,
      logger: () => {},
      policy: new DecisionPolicy({ cooldownMs: 60 * 60 * 1000 }),
      ...overrides
    });
    return { agent, mints, notifies };
  }

  test('runs a full perceive→reason→decide→act cycle and mints a rare event', async () => {
    const { agent, mints, notifies } = buildAgent();
    const summary = await agent.runCycle();

    expect(summary.perceived).toBe(2);
    expect(summary.findings).toBeGreaterThan(0);
    expect(summary.actions.length).toBeGreaterThanOrEqual(1);

    const acted = summary.actions.filter((a) => a.outcome === 'acted');
    expect(acted.length).toBeGreaterThanOrEqual(1);
    expect(acted[0].location.city).toBe('Miami'); // the stormy one, not calm
    expect(['rare', 'epic', 'legendary']).toContain(acted[0].rarity);

    expect(mints.length).toBeGreaterThanOrEqual(1);
    expect(mints[0].eventId).toMatch(/^auto-miami-/);
    expect(notifies.length).toBeGreaterThanOrEqual(1);
    expect(agent.memory.stats().acted).toBeGreaterThanOrEqual(1);
  });

  test('does not re-act on the same event (dedupe + cooldown)', async () => {
    const { agent, mints } = buildAgent();
    await agent.runCycle();
    const afterFirst = mints.length;
    await agent.runCycle();
    expect(mints.length).toBe(afterFirst); // nothing new minted
  });

  test('dry-run decides but never mints', async () => {
    const { agent, mints } = buildAgent({ dryRun: true });
    const summary = await agent.runCycle();
    const acted = summary.actions.filter((a) => a.outcome === 'acted');
    expect(acted.length).toBeGreaterThanOrEqual(1);
    expect(acted[0].dryRun).toBe(true);
    expect(mints.length).toBe(0);
  });

  test('status() reports policy, watchlist and algorithm ids', async () => {
    const { agent } = buildAgent();
    const status = agent.status();
    expect(status.name).toBe('WeatherHunter');
    expect(status.watchlistSize).toBeGreaterThan(0);
    expect(status.algorithms).toEqual(expect.arrayContaining(['storm-hunter']));
    expect(status.policy.allowedRarities).toBeDefined();
  });

  test('a calm-only world produces no actions', async () => {
    const { client, mints } = fakeHttp({ readings: [CALM_READING] });
    const agent = new WeatherHunterAgent({ generator: fakeGenerator, http: client, logger: () => {} });
    const summary = await agent.runCycle();
    expect(summary.actions.filter((a) => a.outcome === 'acted')).toHaveLength(0);
    expect(mints).toHaveLength(0);
  });
});

describe('AgentOrchestrator', () => {
  test('supervises agents and aggregates status', async () => {
    const { client } = fakeHttp({ readings: [STORMY_READING] });
    const agent = new WeatherHunterAgent({ name: 'Hunter-1', generator: fakeGenerator, http: client, logger: () => {} });
    const orch = new AgentOrchestrator();

    const actions = [];
    orch.on('agent:action', (e) => actions.push(e));
    orch.register(agent);

    await orch.runOnce();
    const status = orch.status();
    expect(status.count).toBe(1);
    expect(status.agents['Hunter-1']).toBeDefined();
    expect(actions.length).toBeGreaterThanOrEqual(1);
  });

  test('rejects duplicate agent names', () => {
    const orch = new AgentOrchestrator();
    const a1 = new WeatherHunterAgent({ name: 'dup', generator: fakeGenerator, http: { get: async () => ({}), post: async () => ({}) } });
    const a2 = new WeatherHunterAgent({ name: 'dup', generator: fakeGenerator, http: { get: async () => ({}), post: async () => ({}) } });
    orch.register(a1);
    expect(() => orch.register(a2)).toThrow(/already registered/);
  });
});
