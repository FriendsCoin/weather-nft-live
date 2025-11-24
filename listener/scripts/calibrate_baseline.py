#!/usr/bin/env python3
"""
Baseline Calibration for NESCIENCE

Everyone's EEG is different. What's "high alpha" for one person
might be "low alpha" for another. This calibration session establishes
your personal baseline thresholds for better meditation state classification.

Usage:
    # Real Muse S headband (recommended)
    python scripts/calibrate_baseline.py --duration 600

    # Mock data (for testing)
    python scripts/calibrate_baseline.py --mock --duration 300

Process:
    1. 5-10 minute quiet sitting
    2. Collects your EEG patterns
    3. Calculates personalized thresholds
    4. Saves to data/baseline_profile.json

This is optional but recommended. Without it, NESCIENCE uses population averages.

NOT about getting "good" scores. Just establishing YOUR baseline.
"""

import sys
import time
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.osc_bridge import MindMonitorReceiver, MuseData


class BaselineCalibration:
    """Collect and analyze baseline EEG patterns"""

    def __init__(self):
        self.samples: List[MuseData] = []
        self.start_time = None

    def collect_sample(self, data: MuseData):
        """Add a sample to calibration data"""
        self.samples.append(data)

    def calculate_baseline(self) -> Dict:
        """
        Calculate personalized thresholds from collected data

        Returns:
        {
            'alpha': {'mean': ..., 'std': ..., 'min': ..., 'max': ...},
            'beta': {...},
            'theta': {...},
            'delta': {...},
            'timestamp': ...,
            'num_samples': ...
        }
        """
        if not self.samples:
            raise ValueError("No samples collected!")

        # Extract band powers
        alpha_values = [s.alpha for s in self.samples if s.alpha is not None]
        beta_values = [s.beta for s in self.samples if s.beta is not None]
        theta_values = [s.theta for s in self.samples if s.theta is not None]
        delta_values = [s.delta for s in self.samples if s.delta is not None]

        def band_stats(values):
            if not values:
                return None
            return {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'p25': float(np.percentile(values, 25)),
                'p75': float(np.percentile(values, 75)),
            }

        baseline = {
            'alpha': band_stats(alpha_values),
            'beta': band_stats(beta_values),
            'theta': band_stats(theta_values),
            'delta': band_stats(delta_values),
            'timestamp': datetime.now().isoformat(),
            'num_samples': len(self.samples),
            'duration_seconds': len(self.samples) / 10.0,  # ~10Hz sampling
        }

        return baseline

    def print_summary(self, baseline: Dict):
        """Print calibration summary"""
        print("\n" + "="*60)
        print("BASELINE CALIBRATION COMPLETE")
        print("="*60 + "\n")

        print(f"Samples collected: {baseline['num_samples']}")
        print(f"Duration: {baseline['duration_seconds']:.1f} seconds\n")

        print("Your Personal Thresholds:")
        print("-" * 60)

        for band in ['alpha', 'beta', 'theta', 'delta']:
            stats = baseline[band]
            if stats:
                print(f"\n{band.upper()}:")
                print(f"  Mean:   {stats['mean']:.3f}")
                print(f"  Std:    {stats['std']:.3f}")
                print(f"  Range:  {stats['min']:.3f} - {stats['max']:.3f}")
                print(f"  Median: {stats['median']:.3f}")

        print("\n" + "="*60)
        print("\nThese thresholds will be used in future sessions")
        print("for personalized meditation state classification.")
        print("\nSaved to: data/baseline_profile.json")
        print("="*60 + "\n")


def run_calibration_mock(duration: int, output_file: str):
    """Run calibration with mock data"""
    print("\n⚠️  Using MOCK data (for testing only)")
    print("    For real calibration, use Muse S headband\n")

    calibration = BaselineCalibration()

    print("Generating baseline samples...")
    print("(In real mode, this would be your actual EEG)\n")

    # Simulate samples at ~10 Hz
    num_samples = duration * 10

    for i in range(num_samples):
        # Generate realistic mock patterns
        # Most people have alpha around 0.5-0.7 during relaxed sitting
        mock_data = MuseData(
            timestamp=time.time(),
            eeg_tp9=np.random.randn() * 50,
            eeg_af7=np.random.randn() * 50,
            eeg_af8=np.random.randn() * 50,
            eeg_tp10=np.random.randn() * 50,
            alpha=0.6 + np.random.randn() * 0.15,
            beta=0.4 + np.random.randn() * 0.1,
            theta=0.5 + np.random.randn() * 0.12,
            delta=0.3 + np.random.randn() * 0.08,
        )

        calibration.collect_sample(mock_data)

        # Progress update
        if (i + 1) % 100 == 0:
            progress = (i + 1) / num_samples * 100
            print(f"Progress: {progress:.0f}% ({i+1}/{num_samples} samples)")

    # Calculate baseline
    baseline = calibration.calculate_baseline()

    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(baseline, f, indent=2)

    # Print summary
    calibration.print_summary(baseline)

    return 0


def run_calibration_real(duration: int, port: int, output_file: str):
    """Run calibration with real Muse S headband"""
    calibration = BaselineCalibration()

    print("Waiting for Mind Monitor to connect...")
    print(f"(Send OSC to localhost:{port})\n")

    # Setup receiver
    def on_data(data: MuseData):
        calibration.collect_sample(data)

        # Progress update (every 5 seconds)
        if len(calibration.samples) % 50 == 0:
            elapsed = len(calibration.samples) / 10.0
            remaining = duration - elapsed
            print(f"Collecting... {elapsed:.0f}s / {duration}s ({remaining:.0f}s remaining)")

    receiver = MindMonitorReceiver(port=port, callback=on_data)
    receiver.start()

    print("✓ Listening for EEG data")
    print(f"\nSit quietly for {duration} seconds")
    print("Eyes open or closed - whatever feels natural")
    print("Just be. No need to 'do' anything.\n")

    # Collect for duration
    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            time.sleep(0.5)

            # Check if we're getting data
            if len(calibration.samples) == 0 and time.time() - start_time > 10:
                print("\n⚠️  No data received after 10 seconds!")
                print("   Check Mind Monitor connection:")
                print("   1. OSC streaming enabled")
                print("   2. Correct IP address")
                print(f"   3. Port set to {port}")
                print("   4. Muse headband connected\n")

    except KeyboardInterrupt:
        print("\n\nCalibration interrupted by user")

    finally:
        receiver.stop()

    # Check if we got enough data
    if len(calibration.samples) < 100:
        print(f"\n❌ Not enough data collected ({len(calibration.samples)} samples)")
        print("   Need at least 100 samples (10 seconds)")
        return 1

    # Calculate baseline
    baseline = calibration.calculate_baseline()

    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(baseline, f, indent=2)

    # Print summary
    calibration.print_summary(baseline)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Baseline Calibration - Establish your personal EEG thresholds"
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=600,
        help='Calibration duration in seconds (default: 600 = 10 minutes)'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock data (for testing)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='OSC port for Mind Monitor (default: 5000)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/baseline_profile.json',
        help='Output file for baseline profile'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("NESCIENCE - Baseline Calibration")
    print("="*60 + "\n")

    print("This establishes YOUR personal EEG baseline.")
    print("Everyone's brain is different - this helps NESCIENCE")
    print("understand your unique patterns.\n")

    print(f"Duration: {args.duration} seconds ({args.duration/60:.1f} minutes)")
    print(f"Output: {args.output}\n")

    if args.mock:
        return run_calibration_mock(args.duration, args.output)
    else:
        return run_calibration_real(args.duration, args.port, args.output)


if __name__ == "__main__":
    sys.exit(main())
