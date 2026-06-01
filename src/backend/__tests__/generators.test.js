'use strict';

const {
  GeneratorRegistry,
  promptBuilder,
  ImageProvider
} = require('../generators');

/** Minimal in-memory provider for deterministic, offline tests. */
class FakeProvider extends ImageProvider {
  constructor(name, { available = true, fail = false, priority = 10 } = {}) {
    super({ name, priority, timeoutMs: 0 });
    this._available = available;
    this._fail = fail;
    this.calls = 0;
  }
  async isAvailable() { return this._available; }
  async _generate() {
    this.calls += 1;
    if (this._fail) throw new Error(`${this.name} boom`);
    return { buffer: Buffer.from(`img-${this.name}`), seed: 42, meta: { fake: true } };
  }
}

describe('promptBuilder', () => {
  test('builds a rich prompt from weather + event context', () => {
    const { prompt, negativePrompt } = promptBuilder.buildPrompt({
      weatherData: { conditions: 'stormy', temperature: 41, windSpeed: 80, humidity: 90 },
      eventData: { type: 'severe_thunderstorm' },
      location: { city: 'Tokyo', country: 'Japan' },
      rarity: 'legendary'
    });
    expect(prompt).toMatch(/legendary masterpiece/i);
    expect(prompt).toMatch(/severe thunderstorm/i);
    expect(prompt).toMatch(/Tokyo/);
    expect(prompt).toMatch(/lightning/i); // from stormy motif
    expect(negativePrompt).toMatch(/watermark/);
  });

  test('fuzzy-matches unknown conditions to a known style', () => {
    expect(promptBuilder.resolveStyle('light drizzle')).toBe(promptBuilder.CONDITION_STYLES.rainy);
    expect(promptBuilder.resolveStyle('heavy snow showers')).toBe(promptBuilder.CONDITION_STYLES.snow);
    expect(promptBuilder.resolveStyle('totally-unknown')).toBe(promptBuilder.CONDITION_STYLES.clear);
  });

  test('seedFromWeather is deterministic and bounded', () => {
    const w = { temperature: 25.5, humidity: 60, pressure: 1008, windSpeed: 12 };
    const a = promptBuilder.seedFromWeather(w);
    const b = promptBuilder.seedFromWeather({ ...w });
    expect(a).toBe(b);
    expect(a).toBeGreaterThanOrEqual(0);
    expect(a).toBeLessThan(2147483647);
  });
});

describe('GeneratorRegistry', () => {
  test('selects the highest-priority available provider', async () => {
    const high = new FakeProvider('high', { priority: 1 });
    const low = new FakeProvider('low', { priority: 100 });
    const reg = new GeneratorRegistry({ includeDefaults: false, providers: [low, high] });

    const result = await reg.generate({ weatherData: { conditions: 'clear', temperature: 20 } });
    expect(result.provider).toBe('high');
    expect(result.prompt).toEqual(expect.any(String));
    expect(high.calls).toBe(1);
    expect(low.calls).toBe(0);
  });

  test('falls back when the preferred provider fails', async () => {
    const broken = new FakeProvider('broken', { priority: 1, fail: true });
    const good = new FakeProvider('good', { priority: 2 });
    const reg = new GeneratorRegistry({ includeDefaults: false, providers: [broken, good] });

    const result = await reg.generate({ weatherData: { conditions: 'clear', temperature: 20 } });
    expect(result.provider).toBe('good');
    expect(result.fallbacksTried).toEqual([{ provider: 'broken', error: expect.stringMatching(/boom/) }]);
  });

  test('honours an explicitly preferred provider', async () => {
    const a = new FakeProvider('a', { priority: 1 });
    const b = new FakeProvider('b', { priority: 2 });
    const reg = new GeneratorRegistry({ includeDefaults: false, providers: [a, b] });

    const result = await reg.generate({ provider: 'b', weatherData: { conditions: 'clear', temperature: 20 } });
    expect(result.provider).toBe('b');
  });

  test('skips unavailable providers', async () => {
    const off = new FakeProvider('off', { priority: 1, available: false });
    const on = new FakeProvider('on', { priority: 2 });
    const reg = new GeneratorRegistry({ includeDefaults: false, providers: [off, on] });

    const names = (await reg.availableProviders()).map((p) => p.name);
    expect(names).toEqual(['on']);
    const result = await reg.generate({ weatherData: { conditions: 'clear', temperature: 20 } });
    expect(result.provider).toBe('on');
  });

  test('throws a clear error when every provider fails', async () => {
    const reg = new GeneratorRegistry({
      includeDefaults: false,
      providers: [new FakeProvider('x', { fail: true }), new FakeProvider('y', { fail: true })]
    });
    await expect(reg.generate({ weatherData: { conditions: 'clear', temperature: 20 } }))
      .rejects.toThrow(/all providers failed/);
  });

  test('default registry registers the modern provider chain', () => {
    const reg = new GeneratorRegistry();
    const names = reg.list();
    expect(names).toEqual(expect.arrayContaining([
      'stability', 'fal', 'replicate', 'openai', 'stable-diffusion', 'procedural'
    ]));
    // procedural is the guaranteed terminal fallback (highest priority number).
    expect(names[names.length - 1]).toBe('procedural');
  });
});
