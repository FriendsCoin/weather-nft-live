'use strict';

const { ImageProvider } = require('./base-provider');

/**
 * fal.ai provider — low-latency hosted FLUX / SDXL endpoints.
 *
 * Uses the synchronous `fal.run` endpoint which returns a JSON payload with an
 * `images[]` array of URLs. Requires FAL_KEY.
 *
 * Docs: https://docs.fal.ai/
 */
class FalProvider extends ImageProvider {
  constructor(config = {}) {
    super({ name: 'fal', priority: 22, tier: 'diffusion', ...config });
    this.apiKey = config.apiKey || process.env.FAL_KEY;
    this.baseUrl = (config.baseUrl || 'https://fal.run').replace(/\/$/, '');
    this.model = config.model || process.env.FAL_MODEL || 'fal-ai/flux/schnell';
  }

  async isAvailable() {
    return Boolean(this.apiKey) && Boolean(this._fetch);
  }

  async _generate(request) {
    if (!this.apiKey) throw new Error('fal: FAL_KEY not set');

    const res = await this._httpFetch(`${this.baseUrl}/${this.model}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Key ${this.apiKey}` },
      body: JSON.stringify({
        prompt: request.prompt,
        image_size: 'square_hd',
        num_images: 1,
        ...(typeof request.seed === 'number' ? { seed: request.seed } : {})
      })
    });

    const data = await res.json();
    const url = data?.images?.[0]?.url;
    if (!url) throw new Error('fal: response did not include an image url');

    const imgRes = await this._httpFetch(url, { method: 'GET' });
    const arrayBuffer = await imgRes.arrayBuffer();
    return {
      buffer: Buffer.from(arrayBuffer),
      mimeType: data.images[0].content_type || 'image/png',
      seed: data.seed ?? request.seed,
      meta: { model: this.model }
    };
  }
}

module.exports = { FalProvider };
