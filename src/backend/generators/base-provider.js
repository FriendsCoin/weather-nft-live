'use strict';

/**
 * Base class for all image generation providers.
 *
 * A provider is a thin, uniform adapter around a single image-generation
 * backend (Stable Diffusion / SDXL, Stability AI, OpenAI gpt-image, Replicate
 * Flux, fal.ai, a local procedural renderer, ...). Every provider exposes the
 * same contract so the GeneratorRegistry can treat them interchangeably and
 * build automatic fallback chains.
 *
 * Subclasses MUST implement `_generate(request)` and SHOULD override
 * `isAvailable()` when availability depends on credentials or a reachable host.
 */
class ImageProvider {
  /**
   * @param {Object} [config]
   * @param {string} [config.name]      Stable identifier (e.g. "stability").
   * @param {number} [config.priority]  Lower = preferred. Used for ordering.
   * @param {string} [config.tier]      Quality tier: 'diffusion' | 'procedural'.
   * @param {number} [config.timeoutMs] Per-request timeout.
   * @param {Function} [config.fetchImpl] Injectable fetch (testing/runtime).
   */
  constructor(config = {}) {
    this.name = config.name || this.constructor.name;
    this.priority = config.priority ?? 100;
    this.tier = config.tier || 'diffusion';
    this.timeoutMs = config.timeoutMs ?? 120000;
    this.config = config;
    // Node 18+/22 ships a global fetch; allow injection for tests.
    this._fetch = config.fetchImpl || (typeof fetch === 'function' ? fetch.bind(globalThis) : null);
  }

  /**
   * Whether this provider can currently be used (credentials present, etc.).
   * Cheap, synchronous-ish check — must never throw.
   * @returns {Promise<boolean>}
   */
  async isAvailable() {
    return true;
  }

  /**
   * Generate an image.
   * @param {Object} request
   * @param {string} request.prompt
   * @param {string} [request.negativePrompt]
   * @param {number} [request.width]
   * @param {number} [request.height]
   * @param {number} [request.steps]
   * @param {number} [request.cfgScale]
   * @param {number} [request.seed]
   * @returns {Promise<GenerationResult>}
   */
  async generate(request) {
    if (typeof request?.prompt !== 'string' || request.prompt.trim() === '') {
      throw new Error(`${this.name}: prompt is required`);
    }
    const started = Date.now();
    const result = await this._withTimeout(this._generate(request));
    return {
      provider: this.name,
      tier: this.tier,
      mimeType: result.mimeType || 'image/png',
      buffer: result.buffer,
      seed: result.seed ?? request.seed ?? null,
      meta: { ...result.meta, latencyMs: Date.now() - started }
    };
  }

  /**
   * Provider-specific implementation. Must return `{ buffer, mimeType?, seed?, meta? }`.
   * @abstract
   * @param {Object} request
   * @returns {Promise<{buffer: Buffer, mimeType?: string, seed?: number, meta?: Object}>}
   */
  async _generate(request) {
    throw new Error(`${this.name}: _generate() not implemented`);
  }

  /**
   * Wrap a promise with this provider's timeout.
   * @protected
   */
  async _withTimeout(promise) {
    if (!this.timeoutMs || this.timeoutMs <= 0) return promise;
    let timer;
    const timeout = new Promise((_, reject) => {
      timer = setTimeout(
        () => reject(new Error(`${this.name}: generation timed out after ${this.timeoutMs}ms`)),
        this.timeoutMs
      );
    });
    try {
      return await Promise.race([promise, timeout]);
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * Minimal fetch helper with timeout + non-2xx detection.
   * @protected
   */
  async _httpFetch(url, options = {}) {
    if (!this._fetch) {
      throw new Error(`${this.name}: no fetch implementation available`);
    }
    const controller = typeof AbortController === 'function' ? new AbortController() : null;
    let timer;
    if (controller && this.timeoutMs > 0) {
      timer = setTimeout(() => controller.abort(), this.timeoutMs);
    }
    try {
      const res = await this._fetch(url, {
        ...options,
        signal: controller ? controller.signal : undefined
      });
      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error(`${this.name}: HTTP ${res.status} ${res.statusText} ${body.slice(0, 200)}`);
      }
      return res;
    } finally {
      clearTimeout(timer);
    }
  }
}

/**
 * @typedef {Object} GenerationResult
 * @property {string} provider  Provider name that produced the image.
 * @property {string} tier      'diffusion' | 'procedural'.
 * @property {string} mimeType  e.g. 'image/png'.
 * @property {Buffer} buffer    Raw image bytes.
 * @property {?number} seed     Seed used, if deterministic.
 * @property {Object} meta      Free-form metadata (latency, model, ...).
 */

module.exports = { ImageProvider };
