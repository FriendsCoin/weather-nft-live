#!/usr/bin/env node

'use strict';

/**
 * WeatherNFT Autonomous Agent Runner.
 *
 * Boots the WeatherHunter agent under an orchestrator and exposes a tiny
 * read-only control/status HTTP endpoint. Designed to run as its own process /
 * container alongside the other microservices.
 *
 * Usage:
 *   node src/backend/agent-runner.js                 # run the loop + status API
 *   node src/backend/agent-runner.js --once          # single cycle then exit
 *   node src/backend/agent-runner.js --once --dry-run # no minting, no network deps
 *   AGENT_DRY_RUN=true AGENT_INTERVAL_MS=300000 node src/backend/agent-runner.js
 */

require('dotenv').config();
const http = require('http');
const axios = require('axios');

const { GeneratorRegistry } = require('./generators');
const { DetectionEngine } = require('./algorithms');
const { WeatherHunterAgent, AgentOrchestrator, DecisionPolicy } = require('./agents');

const argv = process.argv.slice(2);
const runOnce = argv.includes('--once');
const dryRun = argv.includes('--dry-run') || process.env.AGENT_DRY_RUN === 'true';
const PORT = process.env.AGENT_PORT || 3013;
const intervalMs = Number(process.env.AGENT_INTERVAL_MS || 5 * 60 * 1000);

// Minimal axios-based HTTP client shaped for the agent toolbox.
const httpClient = {
  get: (url, opts) => axios.get(url, opts),
  post: (url, body, opts) => axios.post(url, body, opts)
};

function buildAgent() {
  const detectionEngine = new DetectionEngine();
  const generator = new GeneratorRegistry({ logger: (m) => console.log(m) });

  const policy = new DecisionPolicy({
    minConfidence: Number(process.env.AGENT_MIN_CONFIDENCE || 0.6),
    allowedRarities: (process.env.AGENT_RARITIES || 'rare,epic,legendary').split(','),
    maxActionsPerCycle: Number(process.env.AGENT_MAX_PER_CYCLE || 5),
    dailyBudget: Number(process.env.AGENT_DAILY_BUDGET || 50)
  });

  return new WeatherHunterAgent({
    detectionEngine,
    generator,
    policy,
    http: httpClient,
    dryRun,
    intervalMs,
    logger: (m) => console.log(m),
    endpoints: {
      weather: process.env.WEATHER_API_URL,
      nft: process.env.NFT_SERVICE_URL,
      websocket: process.env.WEBSOCKET_URL
    }
  });
}

async function main() {
  console.log('');
  console.log('🤖 WeatherNFT Autonomous Agent Runner');
  console.log('='.repeat(50));
  console.log(`   mode:      ${runOnce ? 'single-cycle' : 'continuous'}`);
  console.log(`   dry-run:   ${dryRun}`);
  console.log(`   interval:  ${intervalMs}ms`);
  console.log('');

  const agent = buildAgent();
  const orchestrator = new AgentOrchestrator({ logger: (m) => console.log(m) });
  orchestrator.register(agent);

  orchestrator.on('agent:action', ({ action }) =>
    console.log(`   ⚡ ${action.outcome} ${action.rarity || ''} ${action.type || ''} -> ${action.eventId || ''}`));

  if (runOnce) {
    const results = await orchestrator.runOnce();
    console.log('\n📊 Cycle summary:');
    console.log(JSON.stringify(results, null, 2));
    console.log('\n📈 Status:');
    console.log(JSON.stringify(orchestrator.status(), null, 2));
    return;
  }

  // Continuous mode: start the loop and a status endpoint.
  orchestrator.startAll();

  const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    if (req.url === '/health') {
      return res.end(JSON.stringify({ status: 'OK', service: 'WeatherNFT Agent Runner', dryRun }));
    }
    if (req.url === '/status' || req.url === '/') {
      return res.end(JSON.stringify(orchestrator.status(), null, 2));
    }
    res.statusCode = 404;
    res.end(JSON.stringify({ error: 'not found' }));
  });

  server.listen(PORT, () => {
    console.log(`✅ Agent status API on http://localhost:${PORT}/status`);
  });

  const shutdown = () => {
    console.log('\n🛑 Shutting down agents...');
    orchestrator.stopAll();
    server.close(() => process.exit(0));
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

if (require.main === module) {
  main().catch((err) => {
    console.error('Agent runner fatal error:', err);
    process.exit(1);
  });
}

module.exports = { buildAgent };
