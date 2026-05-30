'use strict';

const { ProceduralProvider } = require('./procedural-provider');
const { StableDiffusionProvider } = require('./stable-diffusion-provider');
const { StabilityProvider } = require('./stability-provider');
const { OpenAIImageProvider } = require('./openai-provider');
const { ReplicateProvider } = require('./replicate-provider');
const { FalProvider } = require('./fal-provider');
const promptBuilder = require('./prompt-builder');

/**
 * Central registry that owns every image provider and turns a structured
 * weather/event request into an image, transparently falling back along a
 * priority-ordered chain until one provider succeeds.
 *
 * Selection order:
 *   1. Explicitly requested provider (if available), else
 *   2. Providers sorted by ascending `priority`, filtered by availability,
 *   3. The procedural renderer as the guaranteed terminal fallback.
 */
class GeneratorRegistry {
  /**
   * @param {Object} [options]
   * @param {ImageProvider[]} [options.providers] Custom provider set (testing).
   * @param {boolean} [options.includeDefaults]   Register built-in providers.
   * @param {Function} [options.fetchImpl]         Injected fetch for network providers.
   * @param {Function} [options.logger]            Optional log sink.
   */
  constructor(options = {}) {
    this.providers = [];
    this.logger = options.logger || (() => {});
    this._availabilityCache = new Map();
    this._availabilityTtlMs = options.availabilityTtlMs ?? 60000;

    if (options.includeDefaults !== false) {
      this._registerDefaults(options.fetchImpl);
    }
    for (const provider of options.providers || []) {
      this.register(provider);
    }
  }

  _registerDefaults(fetchImpl) {
    const shared = fetchImpl ? { fetchImpl } : {};
    this.register(new StabilityProvider(shared));
    this.register(new FalProvider(shared));
    this.register(new ReplicateProvider(shared));
    this.register(new OpenAIImageProvider(shared));
    this.register(new StableDiffusionProvider(shared));
    this.register(new ProceduralProvider(shared)); // always last-resort
  }

  /**
   * Register (or replace, by name) a provider.
   * @param {ImageProvider} provider
   * @returns {GeneratorRegistry}
   */
  register(provider) {
    if (!provider || typeof provider.generate !== 'function') {
      throw new Error('GeneratorRegistry.register: provider must implement generate()');
    }
    this.providers = this.providers.filter((p) => p.name !== provider.name);
    this.providers.push(provider);
    this.providers.sort((a, b) => a.priority - b.priority);
    return this;
  }

  /** @returns {string[]} provider names in selection order. */
  list() {
    return this.providers.map((p) => p.name);
  }

  /**
   * Resolve the ordered list of providers that are currently available.
   * @param {string} [preferred] Name to try first.
   * @returns {Promise<ImageProvider[]>}
   */
  async availableProviders(preferred) {
    const checks = await Promise.all(
      this.providers.map(async (p) => ({ provider: p, ok: await this._isAvailable(p) }))
    );
    let available = checks.filter((c) => c.ok).map((c) => c.provider);
    if (preferred) {
      available = available.sort((a, b) => {
        if (a.name === preferred) return -1;
        if (b.name === preferred) return 1;
        return a.priority - b.priority;
      });
    }
    return available;
  }

  async _isAvailable(provider) {
    const cached = this._availabilityCache.get(provider.name);
    const now = Date.now();
    if (cached && now - cached.at < this._availabilityTtlMs) return cached.ok;
    let ok = false;
    try {
      ok = await provider.isAvailable();
    } catch (_) {
      ok = false;
    }
    this._availabilityCache.set(provider.name, { ok, at: now });
    return ok;
  }

  /**
   * Generate art from a weather/event context, with automatic fallback.
   *
   * @param {Object} params
   * @param {Object} params.weatherData
   * @param {Object} [params.eventData]
   * @param {Object} [params.location]
   * @param {string} [params.rarity]
   * @param {string} [params.provider]   Preferred provider name.
   * @param {Object} [params.overrides]  Raw request overrides (width, steps...).
   * @returns {Promise<GenerationResult>}
   */
  async generate(params = {}) {
    const { weatherData = {}, eventData = {}, location = {}, rarity = 'common' } = params;
    const { prompt, negativePrompt } = promptBuilder.buildPrompt({ weatherData, eventData, location, rarity });
    const seed = promptBuilder.seedFromWeather(weatherData);

    const request = {
      prompt,
      negativePrompt,
      seed,
      width: params.overrides?.width || 1024,
      height: params.overrides?.height || 1024,
      steps: params.overrides?.steps || stepsForRarity(rarity),
      cfgScale: params.overrides?.cfgScale || 7.5,
      // Procedural renderer needs the raw context to draw the scene.
      context: { weatherData, eventData, location, rarity },
      ...params.overrides
    };

    const candidates = await this.availableProviders(params.provider);
    if (candidates.length === 0) {
      throw new Error('GeneratorRegistry: no available image providers');
    }

    const attempts = [];
    for (const provider of candidates) {
      try {
        const result = await provider.generate(request);
        result.prompt = prompt;
        result.fallbacksTried = attempts;
        return result;
      } catch (err) {
        attempts.push({ provider: provider.name, error: err.message });
        this.logger(`[generator] ${provider.name} failed: ${err.message}`);
      }
    }
    throw new Error(`GeneratorRegistry: all providers failed -> ${JSON.stringify(attempts)}`);
  }
}

function stepsForRarity(rarity) {
  switch (rarity) {
    case 'legendary': return 50;
    case 'epic': return 40;
    case 'rare': return 35;
    default: return 30;
  }
}

module.exports = { GeneratorRegistry, stepsForRarity };
