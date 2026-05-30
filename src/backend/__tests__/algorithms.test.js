'use strict';

const {
  DetectionEngine,
  climatology,
  scoring,
  TemperatureAnomalyAlgorithm,
  StormHunterAlgorithm,
  AuroraPredictorAlgorithm,
  AquaDetectAlgorithm
} = require('../algorithms');

describe('climatology', () => {
  test('expected temperature falls from equator to poles', () => {
    const equatorJul = climatology.expectedTemperature(0, 6);
    const arcticJan = climatology.expectedTemperature(78, 0);
    expect(equatorJul).toBeGreaterThan(arcticJan);
    expect(arcticJan).toBeLessThan(0);
  });

  test('sigma grows with latitude', () => {
    expect(climatology.temperatureSigma(70)).toBeGreaterThan(climatology.temperatureSigma(5));
  });

  test('zScore and zToConfidence behave monotonically', () => {
    expect(climatology.zScore(10, 0, 5)).toBe(2);
    expect(climatology.zToConfidence(3)).toBeGreaterThan(climatology.zToConfidence(1));
  });

  test('aurora potential is high near the poles, ~zero at equator', () => {
    expect(climatology.auroraPotential(70)).toBeGreaterThan(0.8);
    expect(climatology.auroraPotential(5)).toBeLessThan(0.05);
  });
});

describe('scoring', () => {
  test('confidenceToRarity maps tiers', () => {
    expect(scoring.confidenceToRarity(0.97)).toBe('legendary');
    expect(scoring.confidenceToRarity(0.87)).toBe('epic');
    expect(scoring.confidenceToRarity(0.72)).toBe('rare');
    expect(scoring.confidenceToRarity(0.55)).toBe('uncommon');
    expect(scoring.confidenceToRarity(0.2)).toBe('common');
  });

  test('noisy-OR reinforces multiple aligned signals', () => {
    const single = scoring.noisyOr([0.5]);
    const triple = scoring.noisyOr([0.5, 0.5, 0.5]);
    expect(triple).toBeGreaterThan(single);
    expect(triple).toBeLessThanOrEqual(1);
  });
});

describe('TemperatureAnomalyAlgorithm', () => {
  const algo = new TemperatureAnomalyAlgorithm();

  test('flags a warm reading in the Arctic winter as a strong anomaly', () => {
    const out = algo.detect({ temperature: 12 }, { location: { lat: 78 }, month: 0 });
    expect(out).toHaveLength(1);
    expect(out[0].signals.direction).toBe('hot');
    expect(out[0].confidence).toBeGreaterThan(0.7);
    expect(out[0].algorithm).toBe('temperature-anomaly');
  });

  test('ignores an ordinary tropical reading', () => {
    const out = algo.detect({ temperature: 28 }, { location: { lat: 1 }, month: 6 });
    expect(out).toHaveLength(0);
  });
});

describe('StormHunterAlgorithm', () => {
  const algo = new StormHunterAlgorithm();

  test('fuses wind + low pressure + rain into a high-confidence storm', () => {
    const out = algo.detect(
      { windSpeed: 95, pressure: 968, rain: 30 },
      { location: { lat: 25 } }
    );
    expect(out).toHaveLength(1);
    expect(out[0].confidence).toBeGreaterThan(0.8);
    expect(out[0].signals.activeSignals).toBeGreaterThanOrEqual(3);
    expect(out[0].type).toBe('severe_thunderstorm');
  });

  test('a light breeze produces nothing', () => {
    expect(algo.detect({ windSpeed: 15, pressure: 1015, rain: 0 }, {})).toHaveLength(0);
  });
});

describe('AuroraPredictorAlgorithm', () => {
  const algo = new AuroraPredictorAlgorithm();

  test('surfaces an aurora opportunity at high latitude in winter', () => {
    const out = algo.detect({ clouds: 10 }, { location: { lat: 69 }, month: 0, kpIndex: 5 });
    expect(out.length).toBeGreaterThanOrEqual(1);
    expect(['aurora_borealis', 'geomagnetic_storm']).toContain(out[0].type);
  });

  test('never fires in the tropics', () => {
    expect(algo.detect({ clouds: 0 }, { location: { lat: 3 }, kpIndex: 9 })).toHaveLength(0);
  });
});

describe('AquaDetectAlgorithm', () => {
  const algo = new AquaDetectAlgorithm();

  test('detects flash-flood-level rainfall', () => {
    const out = algo.detect({ rain: 55, humidity: 99 }, {});
    expect(out.some((d) => d.type === 'flash_flood')).toBe(true);
  });

  test('detects a drought signature', () => {
    const out = algo.detect({ humidity: 8, temperature: 33, rain: 0 }, {});
    expect(out.some((d) => d.type === 'drought_signature')).toBe(true);
  });
});

describe('DetectionEngine', () => {
  test('runs the full ensemble and ranks by rarity then confidence', () => {
    const engine = new DetectionEngine();
    const detections = engine.analyze(
      { temperature: 14, windSpeed: 100, pressure: 965, rain: 35, humidity: 80, visibility: 8, clouds: 20 },
      { location: { lat: 78, city: 'Longyearbyen' }, month: 0 }
    );
    expect(detections.length).toBeGreaterThan(0);
    // Sorted: first item is at least as rare as the last.
    expect(scoring.RARITY_ORDER.indexOf(detections[0].rarity))
      .toBeGreaterThanOrEqual(scoring.RARITY_ORDER.indexOf(detections[detections.length - 1].rarity));
  });

  test('describe() exposes branded algorithm metadata', () => {
    const engine = new DetectionEngine();
    const ids = engine.describe().map((a) => a.id);
    expect(ids).toEqual(expect.arrayContaining([
      'temperature-anomaly', 'storm-hunter', 'micro-climate', 'aurora-predictor', 'aqua-detect'
    ]));
  });

  test('dedupes repeated event types keeping the most confident', () => {
    const engine = new DetectionEngine({
      algorithms: [
        { id: 'a', enabled: true, info: () => ({ id: 'a' }), detect: () => [scoring.makeDetection({ type: 'storm', confidence: 0.6, algorithm: 'a' })] },
        { id: 'b', enabled: true, info: () => ({ id: 'b' }), detect: () => [scoring.makeDetection({ type: 'storm', confidence: 0.9, algorithm: 'b' })] }
      ]
    });
    const out = engine.analyze({ temperature: 20 }, {});
    expect(out).toHaveLength(1);
    expect(out[0].confidence).toBe(0.9);
  });

  test('a throwing detector does not break the scan', () => {
    const engine = new DetectionEngine({
      algorithms: [
        { id: 'bad', enabled: true, info: () => ({ id: 'bad' }), detect: () => { throw new Error('nope'); } },
        { id: 'good', enabled: true, info: () => ({ id: 'good' }), detect: () => [scoring.makeDetection({ type: 'fog', confidence: 0.8, algorithm: 'good' })] }
      ]
    });
    const out = engine.analyze({ visibility: 0.5 }, {});
    expect(out).toHaveLength(1);
    expect(out[0].type).toBe('fog');
  });
});
