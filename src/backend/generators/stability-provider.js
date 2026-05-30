'use strict';

const { ImageProvider } = require('./base-provider');

/**
 * Stability AI hosted provider (Stable Diffusion 3 / SD3.5 / SDXL, Stable Image
 * Core / Ultra). Uses the v2beta REST API which returns raw image bytes.
 *
 * Docs: https://platform.stability.ai/docs/api-reference
 * Requires STABILITY_API_KEY.
 */
class StabilityProvider extends ImageProvider {
  constructor(config = {}) {
    super({ name: 'stability', priority: 20, tier: 'diffusion', ...config });
    this.apiKey = config.apiKey || process.env.STABILITY_API_KEY;
    this.baseUrl = (config.baseUrl || 'https://api.stability.ai').replace(/\/$/, '');
    // 'core' (fast/cheap), 'ultra' (top quality), or 'sd3' family.
    this.model = config.model || process.env.STABILITY_MODEL || 'core';
  }

  async isAvailable() {
    return Boolean(this.apiKey) && Boolean(this._fetch);
  }

  _endpoint() {
    if (this.model === 'ultra') return `${this.baseUrl}/v2beta/stable-image/generate/ultra`;
    if (this.model.startsWith('sd3')) return `${this.baseUrl}/v2beta/stable-image/generate/sd3`;
    return `${this.baseUrl}/v2beta/stable-image/generate/core`;
  }

  async _generate(request) {
    if (!this.apiKey) throw new Error('stability: STABILITY_API_KEY not set');

    // The v2beta API expects multipart/form-data.
    const form = new FormData();
    form.append('prompt', request.prompt);
    if (request.negativePrompt) form.append('negative_prompt', request.negativePrompt);
    if (typeof request.seed === 'number') form.append('seed', String(request.seed % 4294967294));
    form.append('output_format', 'png');
    form.append('aspect_ratio', '1:1');
    if (this.model.startsWith('sd3')) form.append('model', this.model);

    const res = await this._httpFetch(this._endpoint(), {
      method: 'POST',
      headers: { Authorization: `Bearer ${this.apiKey}`, Accept: 'image/*' },
      body: form
    });

    const arrayBuffer = await res.arrayBuffer();
    return {
      buffer: Buffer.from(arrayBuffer),
      mimeType: 'image/png',
      seed: request.seed,
      meta: { model: this.model }
    };
  }
}

module.exports = { StabilityProvider };
