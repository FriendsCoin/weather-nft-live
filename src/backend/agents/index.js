'use strict';

/**
 * Autonomous agent subsystem.
 *
 * Adds genuine agency to WeatherNFT: agents that perceive the live weather,
 * reason with the detection ensemble, decide under an explicit policy, and act
 * (generate + mint + notify) on their own schedule.
 */
module.exports = {
  BaseAgent: require('./base-agent').BaseAgent,
  WeatherHunterAgent: require('./weather-hunter-agent').WeatherHunterAgent,
  DEFAULT_WATCHLIST: require('./weather-hunter-agent').DEFAULT_WATCHLIST,
  AgentOrchestrator: require('./orchestrator').AgentOrchestrator,
  DecisionPolicy: require('./policy').DecisionPolicy,
  AgentMemory: require('./memory').AgentMemory,
  Tool: require('./tools').Tool,
  Toolbox: require('./tools').Toolbox,
  buildDefaultToolbox: require('./tools').buildDefaultToolbox
};
