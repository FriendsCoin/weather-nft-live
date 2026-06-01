#!/usr/bin/env node

'use strict';

/**
 * AI Art Generator for WeatherNFT (facade).
 *
 * Historically this class hard-coded a single Stable Diffusion endpoint with a
 * procedural canvas fallback. It now delegates to the modern multi-provider
 * `GeneratorRegistry` (Stability AI, fal.ai, Replicate/FLUX, OpenAI gpt-image,
 * self-hosted SD, procedural), while preserving its original public API so all
 * existing callers (nft-service, tests) keep working unchanged.
 *
 *   generateArt(params)        -> Promise<Buffer>     (unchanged contract)
 *   generateArtDetailed(params)-> Promise<GenerationResult> (new, richer)
 *   testSDConnection()         -> Promise<boolean>    (unchanged)
 */

const { GeneratorRegistry } = require('./generators');
const promptBuilder = require('./generators/prompt-builder');

class AIArtGenerator {
  constructor(config = {}) {
    this.config = {
      sdApiUrl: config.sdApiUrl || process.env.SD_AI_URL || 'http://localhost:8000',
      useRealSD: config.useRealSD ?? (process.env.USE_REAL_AI === 'true'),
      fallbackMode: config.fallbackMode || 'procedural',
      imageWidth: config.imageWidth || 512,
      imageHeight: config.imageHeight || 512,
      preferredProvider: config.preferredProvider || process.env.IMAGE_PROVIDER || null
    };

    // Allow callers/tests to inject a pre-built registry; otherwise build the
    // default chain. The SD provider honours `useRealSD` via env.
    this.registry =
      config.registry ||
      new GeneratorRegistry({
        fetchImpl: config.fetchImpl,
        logger: config.logger || ((m) => console.log(m))
      });
  }

  /**
   * Generate art and return raw PNG bytes (backwards-compatible).
   * @param {Object} params
   * @returns {Promise<Buffer>}
   */
  async generateArt(params) {
    const result = await this.generateArtDetailed(params);
    return result.buffer;
  }

  /**
   * Generate art and return the full provider result (provider name, seed,
   * prompt, latency, fallback chain, ...).
   * @param {Object} params
   * @returns {Promise<import('./generators/base-provider').GenerationResult>}
   */
  async generateArtDetailed(params) {
    return this.registry.generate({
      ...params,
      provider: params.provider || this.config.preferredProvider,
      overrides: {
        width: this.config.imageWidth,
        height: this.config.imageHeight,
        ...(params.overrides || {})
      }
    });
  }

  /**
   * Build the prompt that would be used for the given params (no generation).
   * @param {Object} params
   * @returns {{prompt: string, negativePrompt: string}}
   */
  buildPrompt(params) {
    return promptBuilder.buildPrompt(params);
  }

  /**
   * Which providers are currently usable, in selection order.
   * @returns {Promise<string[]>}
   */
  async availableProviders() {
    const providers = await this.registry.availableProviders(this.config.preferredProvider);
    return providers.map((p) => p.name);
  }

  /**
   * Backwards-compatible health probe for the self-hosted SD backend.
   * @returns {Promise<boolean>}
   */
  async testSDConnection() {
    const sd = this.registry.providers.find((p) => p.name === 'stable-diffusion');
    if (!sd) return false;
    const ok = await sd.isAvailable();
    console.log(ok ? '✅ Stable Diffusion provider available' : '⚠️  Stable Diffusion provider unavailable, using fallback');
    return ok;
  }
}

module.exports = AIArtGenerator;
