'use strict';

/**
 * Modern prompt engineering for weather-driven generative art.
 *
 * Turns structured weather + event data into rich prompts tuned for current
 * diffusion models (SDXL, SD3, Flux, gpt-image). Centralised here so every
 * provider shares the same creative direction and so prompts can be unit-tested
 * independently of any network backend.
 */

const CONDITION_STYLES = {
  clear: { palette: 'golden hour blues and warm gold', mood: 'serene, luminous', motif: 'crisp sunlight, lens flare, soft volumetric rays' },
  cloudy: { palette: 'muted silver-grey gradients', mood: 'calm, contemplative', motif: 'layered cumulus, soft diffused light' },
  rainy: { palette: 'steel blue and slate teal', mood: 'moody, reflective', motif: 'rain streaks, wet reflections, bokeh droplets' },
  stormy: { palette: 'deep indigo and stormcloud charcoal', mood: 'dramatic, powerful, ominous', motif: 'forked lightning, turbulent supercell clouds' },
  thunderstorm: { palette: 'electric violet and ink-black', mood: 'intense, electric, foreboding', motif: 'lightning bolts, anvil clouds, sheets of rain' },
  snow: { palette: 'alice-blue, frost white and pale cyan', mood: 'hushed, crystalline', motif: 'falling snow, frost crystals, drifting flakes' },
  snowy: { palette: 'alice-blue, frost white and pale cyan', mood: 'hushed, crystalline', motif: 'falling snow, frost crystals, drifting flakes' },
  fog: { palette: 'gainsboro and desaturated greys', mood: 'mysterious, ethereal', motif: 'rolling mist, soft silhouettes, low visibility haze' },
  foggy: { palette: 'gainsboro and desaturated greys', mood: 'mysterious, ethereal', motif: 'rolling mist, soft silhouettes, low visibility haze' },
  aurora: { palette: 'emerald green, violet and deep night blue', mood: 'transcendent, otherworldly', motif: 'shimmering aurora borealis curtains, star field' }
};

const RARITY_DIRECTION = {
  common: { quality: 'clean digital illustration', detail: 'balanced composition' },
  uncommon: { quality: 'detailed digital painting', detail: 'rich texture, depth of field' },
  rare: { quality: 'masterpiece concept art, highly detailed', detail: 'cinematic composition, intricate detail' },
  epic: { quality: 'epic award-winning concept art, ultra detailed', detail: 'dramatic cinematic lighting, hyper-detailed, 4k' },
  legendary: { quality: 'legendary masterpiece, ultra-detailed, 8k, award-winning', detail: 'breathtaking cinematic lighting, god rays, photorealistic detail, trending on ArtStation' }
};

const DEFAULT_NEGATIVE =
  'low quality, blurry, jpeg artifacts, watermark, text, signature, logo, ' +
  'deformed, distorted, oversaturated, frame, border, ugly, duplicate';

/**
 * Pick the closest known style bucket for an arbitrary condition string.
 * @param {string} condition
 * @returns {{palette: string, mood: string, motif: string}}
 */
function resolveStyle(condition) {
  const key = String(condition || 'clear').toLowerCase();
  if (CONDITION_STYLES[key]) return CONDITION_STYLES[key];
  // Heuristic fuzzy matching for provider-specific condition vocabularies.
  if (/storm|thunder|squall/.test(key)) return CONDITION_STYLES.stormy;
  // Check snow before rain so "snow showers" isn't captured by /shower/.
  if (/snow|sleet|blizzard|ice/.test(key)) return CONDITION_STYLES.snow;
  if (/rain|drizzle|shower/.test(key)) return CONDITION_STYLES.rainy;
  if (/fog|mist|haze/.test(key)) return CONDITION_STYLES.fog;
  if (/cloud|overcast/.test(key)) return CONDITION_STYLES.cloudy;
  if (/aurora|borealis/.test(key)) return CONDITION_STYLES.aurora;
  return CONDITION_STYLES.clear;
}

/**
 * Build a positive + negative prompt pair from weather/event context.
 *
 * @param {Object} params
 * @param {Object} params.weatherData  { temperature, windSpeed, humidity, conditions, pressure }
 * @param {Object} [params.eventData]  { type }
 * @param {Object} [params.location]   { city, country }
 * @param {string} [params.rarity]
 * @returns {{prompt: string, negativePrompt: string, style: Object}}
 */
function buildPrompt(params = {}) {
  const { weatherData = {}, eventData = {}, location = {}, rarity = 'common' } = params;
  const condition = weatherData.conditions || eventData.type || 'clear';
  const style = resolveStyle(condition);
  const direction = RARITY_DIRECTION[rarity] || RARITY_DIRECTION.common;

  const subject = eventData.type
    ? humanizeEvent(eventData.type)
    : `${condition} weather phenomenon`;

  const place = location.city
    ? `over the landscape of ${location.city}${location.country ? ', ' + location.country : ''}`
    : 'over a sweeping natural landscape';

  const physical = describePhysical(weatherData);

  const prompt = [
    direction.quality,
    `${subject} ${place}`,
    `${style.mood} atmosphere`,
    style.motif,
    `color palette of ${style.palette}`,
    physical,
    direction.detail,
    'atmospheric, volumetric, environment art'
  ]
    .filter(Boolean)
    .join(', ');

  return { prompt, negativePrompt: DEFAULT_NEGATIVE, style };
}

/**
 * Translate physical readings into evocative phrasing the model can use.
 * @param {Object} w
 * @returns {string}
 */
function describePhysical(w = {}) {
  const parts = [];
  if (typeof w.temperature === 'number') {
    if (w.temperature >= 38) parts.push('shimmering heat haze, scorched air');
    else if (w.temperature <= -15) parts.push('biting frozen air, ice fog');
    else if (w.temperature <= 0) parts.push('cold crisp air');
  }
  if (typeof w.windSpeed === 'number' && w.windSpeed >= 40) {
    parts.push('powerful wind, motion-blurred debris, bending trees');
  }
  if (typeof w.humidity === 'number' && w.humidity >= 85) {
    parts.push('heavy humid air, dense moisture');
  }
  return parts.join(', ');
}

/**
 * "heat_wave" -> "a dramatic heat wave".
 * @param {string} type
 * @returns {string}
 */
function humanizeEvent(type) {
  const words = String(type).replace(/[_-]+/g, ' ').trim();
  return `a dramatic ${words}`;
}

/**
 * Deterministic seed derived from weather so identical conditions yield
 * reproducible art across runs and providers.
 * @param {Object} weatherData
 * @returns {number}
 */
function seedFromWeather(weatherData = {}) {
  const { temperature = 0, humidity = 0, pressure = 0, windSpeed = 0 } = weatherData;
  const raw = Math.abs(Math.floor(temperature * 1000 + humidity * 100 + pressure * 10 + windSpeed));
  // Keep within the 32-bit range most diffusion backends accept.
  return raw % 2147483647;
}

module.exports = {
  buildPrompt,
  resolveStyle,
  seedFromWeather,
  humanizeEvent,
  CONDITION_STYLES,
  RARITY_DIRECTION,
  DEFAULT_NEGATIVE
};
