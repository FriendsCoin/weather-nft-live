'use strict';

const { ImageProvider } = require('./base-provider');

/**
 * Replicate provider — runs modern open models such as Black Forest Labs FLUX
 * (flux-schnell / flux-dev / flux-1.1-pro) via the Replicate predictions API.
 *
 * Replicate is asynchronous: create a prediction, then poll until it succeeds,
 * then download the resulting image URL. Requires REPLICATE_API_TOKEN.
 *
 * Docs: https://replicate.com/docs/reference/http
 */
class ReplicateProvider extends ImageProvider {
  constructor(config = {}) {
    super({ name: 'replicate', priority: 25, tier: 'diffusion', ...config });
    this.apiKey = config.apiKey || process.env.REPLICATE_API_TOKEN;
    this.baseUrl = (config.baseUrl || 'https://api.replicate.com').replace(/\/$/, '');
    // Default to the fast FLUX schnell model.
    this.model = config.model || process.env.REPLICATE_MODEL || 'black-forest-labs/flux-schnell';
    this.pollIntervalMs = config.pollIntervalMs || 1500;
    this.maxPolls = config.maxPolls || 40;
  }

  async isAvailable() {
    return Boolean(this.apiKey) && Boolean(this._fetch);
  }

  async _generate(request) {
    if (!this.apiKey) throw new Error('replicate: REPLICATE_API_TOKEN not set');
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.apiKey}`,
      Prefer: 'wait' // ask Replicate to hold the connection when possible
    };

    const createRes = await this._httpFetch(`${this.baseUrl}/v1/models/${this.model}/predictions`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        input: {
          prompt: request.prompt,
          aspect_ratio: '1:1',
          output_format: 'png',
          ...(typeof request.seed === 'number' ? { seed: request.seed } : {})
        }
      })
    });

    let prediction = await createRes.json();
    prediction = await this._awaitCompletion(prediction, headers);

    const url = Array.isArray(prediction.output) ? prediction.output[0] : prediction.output;
    if (!url) throw new Error('replicate: prediction produced no output');

    const imgRes = await this._httpFetch(url, { method: 'GET' });
    const arrayBuffer = await imgRes.arrayBuffer();
    return { buffer: Buffer.from(arrayBuffer), mimeType: 'image/png', seed: request.seed, meta: { model: this.model } };
  }

  async _awaitCompletion(prediction, headers) {
    let current = prediction;
    let polls = 0;
    while (current && ['starting', 'processing'].includes(current.status)) {
      if (polls++ >= this.maxPolls) throw new Error('replicate: polling timed out');
      await new Promise((r) => setTimeout(r, this.pollIntervalMs));
      const url = current.urls?.get;
      if (!url) break;
      const res = await this._httpFetch(url, { method: 'GET', headers });
      current = await res.json();
    }
    if (current.status !== 'succeeded') {
      throw new Error(`replicate: prediction ${current.status}: ${current.error || 'unknown error'}`);
    }
    return current;
  }
}

module.exports = { ReplicateProvider };
