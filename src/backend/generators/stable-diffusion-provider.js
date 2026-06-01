'use strict';

const { ImageProvider } = require('./base-provider');

/**
 * Self-hosted Stable Diffusion / SDXL provider.
 *
 * Supports two common server shapes:
 *  - The project's lightweight `/generate` endpoint (base64 `image` field).
 *  - The AUTOMATIC1111 `/sdapi/v1/txt2img` endpoint (`images[]` base64 array).
 *
 * Auto-detected from `apiStyle` config ('simple' | 'a1111').
 */
class StableDiffusionProvider extends ImageProvider {
  constructor(config = {}) {
    super({ name: 'stable-diffusion', priority: 50, tier: 'diffusion', ...config });
    this.baseUrl = (config.baseUrl || process.env.SD_AI_URL || 'http://localhost:8000').replace(/\/$/, '');
    this.apiStyle = config.apiStyle || process.env.SD_API_STYLE || 'simple';
    this.enabled = config.enabled ?? (process.env.USE_REAL_AI === 'true');
  }

  async isAvailable() {
    if (!this.enabled) return false;
    try {
      const res = await this._httpFetch(`${this.baseUrl}/health`, { method: 'GET' });
      await res.text().catch(() => '');
      return true;
    } catch (_) {
      return false;
    }
  }

  async _generate(request) {
    return this.apiStyle === 'a1111'
      ? this._generateA1111(request)
      : this._generateSimple(request);
  }

  async _generateSimple(request) {
    const res = await this._httpFetch(`${this.baseUrl}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: request.prompt,
        negative_prompt: request.negativePrompt,
        width: request.width || 512,
        height: request.height || 512,
        steps: request.steps || 30,
        cfg_scale: request.cfgScale || 7.5,
        seed: request.seed
      })
    });
    const data = await res.json();
    if (!data || !data.image) throw new Error('stable-diffusion: invalid /generate response');
    return { buffer: Buffer.from(data.image, 'base64'), seed: data.seed ?? request.seed, meta: { apiStyle: 'simple' } };
  }

  async _generateA1111(request) {
    const res = await this._httpFetch(`${this.baseUrl}/sdapi/v1/txt2img`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: request.prompt,
        negative_prompt: request.negativePrompt,
        width: request.width || 1024,
        height: request.height || 1024,
        steps: request.steps || 30,
        cfg_scale: request.cfgScale || 7.5,
        seed: request.seed ?? -1
      })
    });
    const data = await res.json();
    const b64 = data?.images?.[0];
    if (!b64) throw new Error('stable-diffusion: empty images[] from /sdapi/v1/txt2img');
    return { buffer: Buffer.from(b64, 'base64'), seed: request.seed, meta: { apiStyle: 'a1111' } };
  }
}

module.exports = { StableDiffusionProvider };
