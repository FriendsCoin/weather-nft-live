'use strict';

const { ImageProvider } = require('./base-provider');

/**
 * OpenAI Images provider (gpt-image-1 / DALL·E 3).
 *
 * Uses the `/v1/images/generations` REST endpoint and returns base64 PNG.
 * Requires OPENAI_API_KEY. Note: OpenAI ignores explicit seeds / negative
 * prompts, so those are folded into the positive prompt where useful.
 *
 * Docs: https://platform.openai.com/docs/api-reference/images
 */
class OpenAIImageProvider extends ImageProvider {
  constructor(config = {}) {
    super({ name: 'openai', priority: 30, tier: 'diffusion', ...config });
    this.apiKey = config.apiKey || process.env.OPENAI_API_KEY;
    this.baseUrl = (config.baseUrl || process.env.OPENAI_BASE_URL || 'https://api.openai.com').replace(/\/$/, '');
    this.model = config.model || process.env.OPENAI_IMAGE_MODEL || 'gpt-image-1';
  }

  async isAvailable() {
    return Boolean(this.apiKey) && Boolean(this._fetch);
  }

  async _generate(request) {
    if (!this.apiKey) throw new Error('openai: OPENAI_API_KEY not set');

    // Fold the negative prompt into a natural-language exclusion clause.
    const prompt = request.negativePrompt
      ? `${request.prompt}. Avoid: ${request.negativePrompt}.`
      : request.prompt;

    const size = this._closestSize(request.width || 1024, request.height || 1024);
    const body = { model: this.model, prompt, n: 1, size };
    // gpt-image-1 returns b64 by default; dall-e-3 needs explicit response_format.
    if (this.model.startsWith('dall-e')) body.response_format = 'b64_json';

    const res = await this._httpFetch(`${this.baseUrl}/v1/images/generations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.apiKey}` },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    const b64 = data?.data?.[0]?.b64_json;
    if (!b64) throw new Error('openai: response did not include b64_json image');
    return { buffer: Buffer.from(b64, 'base64'), mimeType: 'image/png', meta: { model: this.model, size } };
  }

  _closestSize(w, h) {
    if (w > h) return '1536x1024';
    if (h > w) return '1024x1536';
    return '1024x1024';
  }
}

module.exports = { OpenAIImageProvider };
