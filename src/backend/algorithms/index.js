'use strict';

/**
 * Modern weather event detection subsystem.
 *
 * Replaces fixed global thresholds with a calibrated, climatology-aware
 * ensemble. Prefer `DetectionEngine` for new code.
 */
module.exports = {
  DetectionEngine: require('./detection-engine').DetectionEngine,
  DetectionAlgorithm: require('./base-algorithm').DetectionAlgorithm,
  climatology: require('./climatology'),
  scoring: require('./scoring'),
  TemperatureAnomalyAlgorithm: require('./detectors/temperature-anomaly').TemperatureAnomalyAlgorithm,
  StormHunterAlgorithm: require('./detectors/storm-hunter').StormHunterAlgorithm,
  MicroClimateAlgorithm: require('./detectors/micro-climate').MicroClimateAlgorithm,
  AuroraPredictorAlgorithm: require('./detectors/aurora-predictor').AuroraPredictorAlgorithm,
  AquaDetectAlgorithm: require('./detectors/aqua-detect').AquaDetectAlgorithm
};
