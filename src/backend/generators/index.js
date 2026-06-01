'use strict';

/**
 * Modern multi-provider image generation subsystem.
 *
 * Public surface for the rest of the platform. Prefer `GeneratorRegistry` for
 * new code; the individual providers are exported for advanced wiring/testing.
 */
module.exports = {
  GeneratorRegistry: require('./generator-registry').GeneratorRegistry,
  stepsForRarity: require('./generator-registry').stepsForRarity,
  promptBuilder: require('./prompt-builder'),
  ImageProvider: require('./base-provider').ImageProvider,
  ProceduralProvider: require('./procedural-provider').ProceduralProvider,
  StableDiffusionProvider: require('./stable-diffusion-provider').StableDiffusionProvider,
  StabilityProvider: require('./stability-provider').StabilityProvider,
  OpenAIImageProvider: require('./openai-provider').OpenAIImageProvider,
  ReplicateProvider: require('./replicate-provider').ReplicateProvider,
  FalProvider: require('./fal-provider').FalProvider
};
