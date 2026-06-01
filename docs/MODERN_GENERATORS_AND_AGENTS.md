# Modern Generators, Algorithms & Agents

This document describes the three subsystems added to modernise WeatherNFT:

1. **Modern Generators** — a pluggable, multi-provider image-generation layer
   (`src/backend/generators/`).
2. **Modern Algorithms** — a climatology-aware detection ensemble with
   calibrated confidence (`src/backend/algorithms/`).
3. **Agency** — autonomous agents that perceive, reason, decide and act on their
   own schedule (`src/backend/agents/`).

All three are **dependency-light**, **fully unit-tested offline** (no network or
API keys required for tests), and **backwards compatible** — existing services
and APIs keep working unchanged.

---

## 1. Modern Generators

### Why

The old `AIArtGenerator` hard-coded a single Stable Diffusion endpoint with a
procedural canvas fallback. Today's best results come from a spread of
backends (Stability AI SD3, FLUX via fal.ai / Replicate, OpenAI gpt-image).
The new layer treats every backend as an interchangeable **provider** behind a
uniform contract, and a **registry** that auto-selects the best available one
and transparently falls back on failure.

### Architecture

```
GeneratorRegistry
 ├─ StabilityProvider      (priority 20)  SD3 / SDXL / Ultra   [STABILITY_API_KEY]
 ├─ FalProvider            (priority 22)  FLUX / SDXL          [FAL_KEY]
 ├─ ReplicateProvider      (priority 25)  FLUX                 [REPLICATE_API_TOKEN]
 ├─ OpenAIImageProvider    (priority 30)  gpt-image-1 / DALL·E [OPENAI_API_KEY]
 ├─ StableDiffusionProvider(priority 50)  self-hosted A1111/simple
 └─ ProceduralProvider     (priority 1000) node-canvas — always available
```

Selection order: explicitly requested provider → lowest `priority` available →
**procedural** as the guaranteed terminal fallback. Availability is probed
(credentials present / host reachable) and cached for 60s.

### Usage

```js
const { GeneratorRegistry } = require('./src/backend/generators');

const registry = new GeneratorRegistry();           // builds the default chain
const result = await registry.generate({
  weatherData: { conditions: 'stormy', temperature: 41, windSpeed: 80, humidity: 90 },
  eventData:   { type: 'severe_thunderstorm' },
  location:    { city: 'Tokyo', country: 'Japan' },
  rarity:      'legendary',
  provider:    'stability'                           // optional preference
});

result.buffer;          // Buffer (PNG bytes)
result.provider;        // which backend actually produced it
result.prompt;          // the engineered prompt
result.fallbacksTried;  // [{ provider, error }] if any fell through
```

The legacy facade still works exactly as before:

```js
const AIArtGenerator = require('./src/backend/ai-art-generator');
const gen = new AIArtGenerator();
const pngBuffer = await gen.generateArt({ weatherData, eventData, location, rarity });
const detailed  = await gen.generateArtDetailed({ ... }); // new richer result
```

### Prompt engineering

`generators/prompt-builder.js` centralises creative direction: condition →
palette/mood/motif, rarity → quality tier, physical readings → evocative
phrasing, plus a deterministic `seedFromWeather()` so identical conditions
produce reproducible art across providers.

---

## 2. Modern Algorithms

### Why

The original detector used **fixed global thresholds** (e.g. "35 °C = rare
heat"). That ignores context — 12 °C in the Arctic winter is a far rarer
anomaly than 38 °C in Dubai in July. The new ensemble scores deviations against
a **local seasonal climatology** (z-scores) and fuses multiple signals into a
calibrated **confidence (0–1)** that maps to rarity.

### Architecture

```
DetectionEngine (ensemble + dedupe + ranking)
 ├─ ThermalDrift-v2     temperature-anomaly   z-score vs climatology
 ├─ StormChaser-v4      storm-hunter          noisy-OR(wind, pressure, rain)
 ├─ EcoBalance-v1       micro-climate         fog / visibility / humid-heat
 ├─ AuroraPredictor-v3  aurora-predictor      geo-lat × darkness × Kp × clear-sky
 └─ AquaDetect-v2       aqua-detect           flood / heavy-snow / drought
```

- `climatology.js` — analytic, dependency-free seasonal/latitude model
  (expected temperature, sigma, pressure model, aurora potential, darkness).
- `scoring.js` — `confidenceToRarity`, `noisyOr`, weighted scoring, normalised
  detection records.
- Each detector is an independently testable `DetectionAlgorithm` subclass.

### Usage

```js
const { DetectionEngine } = require('./src/backend/algorithms');
const engine = new DetectionEngine();

const detections = engine.analyze(weather, { location, timestamp, kpIndex });
// → ranked [{ type, rarity, confidence, score, value, description,
//             algorithm, signals, valueMultiplier }]
```

Each detection now carries **why** it fired (`signals`, e.g. `zScore`,
`activeSignals`, `potential`) for transparent, auditable rarity.

### Live API

`weather-api-service.js` exposes the ensemble without breaking the old endpoint:

| Endpoint | Behaviour |
|---|---|
| `GET /api/weather/detect-events` | legacy thresholds (unchanged) |
| `GET /api/weather/detect-events?engine=v2` | modern ensemble |
| `GET /api/algorithms` | metadata for every algorithm in the ensemble |

---

## 3. Agency (Autonomous Agents)

### Why

Everything in the platform was previously **reactive** — nothing happened
without an HTTP request. The agent layer adds genuine **agency**: an actor that
hunts the globe for rare weather and acts on its own.

### The loop

```
perceive  → scan a watchlist of regions (scan_region tool)
reason    → run the detection ensemble over every reading (detect_events tool)
decide    → apply an explicit DecisionPolicy (confidence, rarity, budget,
            cooldown, dedupe, per-cycle cap)
act       → generate art + mint NFT + broadcast notification
            (generate_art / mint_nft / notify tools)
```

### Components

- `BaseAgent` — lifecycle (`start`/`pause`/`resume`/`stop`), scheduling, the
  perceive→reason→decide→act cycle, structured `status()`, and an event stream
  (`action`, `cycle:end`, `error`, `log`).
- `WeatherHunterAgent` — the concrete autonomous hunter.
- `DecisionPolicy` — accountable, inspectable rules; every autonomous action is
  justified (`{ act, reason, value }`). Includes economic value estimation so
  budget is spent on the highest-value events first.
- `AgentMemory` — bounded recall: dedupe signatures, per-location cooldowns,
  recent-activity trail, counters.
- `Tool` / `Toolbox` — every effect is a named, schema-described, **injectable**
  capability, so the agent runs against real microservices in production and
  in-memory fakes in tests.
- `AgentOrchestrator` — supervises a fleet of agents, aggregates status, re-emits
  their event streams for a control dashboard.

### Running the agent

```bash
# Continuous autonomous loop + status API on :3013
npm run agent

# One cycle, no minting, no external deps (great for demos/CI)
npm run agent:once
```

Status endpoint (continuous mode):

```bash
curl http://localhost:3013/status
```

### Safety & control

- **`AGENT_DRY_RUN=true`** — the agent perceives, reasons and decides but never
  mints. Ideal for observing behaviour before going live.
- **Budgets & cooldowns** — `AGENT_MAX_PER_CYCLE`, `AGENT_DAILY_BUDGET`,
  per-location cooldown, and event dedupe prevent runaway minting.
- **Rarity allowlist** — `AGENT_RARITIES` restricts what the agent will act on.
- **Resilience** — a failing detector, provider or tool never crashes a cycle;
  errors are recorded and the loop continues.

---

## Configuration

See `.env.example` for the full set of variables (generator API keys, agent
budgets/intervals, service URLs). Everything degrades gracefully: with **no**
keys configured, generation falls back to procedural art and the agent runs in
detect-only mode.

## Testing

```bash
npm test                                   # full suite (127 tests)
npx jest src/backend/__tests__/generators.test.js
npx jest src/backend/__tests__/algorithms.test.js
npx jest src/backend/__tests__/agents.test.js
```

The new modules are covered by 40 focused tests that run **entirely offline** —
network providers and HTTP effects are exercised through injected fakes.
