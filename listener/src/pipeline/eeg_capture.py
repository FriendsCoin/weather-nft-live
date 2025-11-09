"""
EEG Data Capture - Muse S Connection & Recording

This module handles:
- Bluetooth connection to Muse S headband
- Real-time EEG data streaming via LSL (Lab Streaming Layer)
- Recording sessions to CSV files
- Mock EEG generator for development/testing

Channels: TP9, AF7, AF8, TP10 (4 channels @ 256 Hz)
"""

import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import numpy as np


class MuseRecorder:
    """
    Real-time EEG recording from Muse S headband via LSL.

    Usage:
        recorder = MuseRecorder(output_dir="data/raw")
        recorder.connect()
        recorder.record(duration=300, session_name="session_001")
    """

    def __init__(
        self,
        output_dir: str = "data/raw",
        channels: Optional[List[str]] = None,
        sampling_rate: int = 256
    ):
        """
        Initialize Muse S recorder.

        Args:
            output_dir: Directory to save recordings
            channels: List of channel names (default: ["TP9", "AF7", "AF8", "TP10"])
            sampling_rate: Sampling rate in Hz (Muse S = 256 Hz)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.channels = channels or ["TP9", "AF7", "AF8", "TP10"]
        self.sampling_rate = sampling_rate

        self.inlet = None
        self.is_connected = False

    def connect(self, timeout: int = 30) -> bool:
        """
        Connect to Muse S headband via LSL.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully

        Note:
            Requires muselsl to be running:
            $ muselsl stream --name "Muse-S"
        """
        try:
            from pylsl import StreamInlet, resolve_byprop

            print(f"🔍 Searching for Muse S stream (timeout: {timeout}s)...")
            streams = resolve_byprop('type', 'EEG', timeout=timeout)

            if not streams:
                print("❌ No EEG stream found!")
                print("💡 Make sure muselsl is running:")
                print("   $ muselsl stream --name 'Muse-S'")
                return False

            print(f"✅ Found {len(streams)} EEG stream(s)")
            self.inlet = StreamInlet(streams[0])
            self.is_connected = True

            # Get stream info
            info = self.inlet.info()
            print(f"📡 Connected to: {info.name()}")
            print(f"   Channels: {info.channel_count()}")
            print(f"   Sampling rate: {info.nominal_srate()} Hz")

            return True

        except ImportError:
            print("❌ pylsl not installed!")
            print("   Install with: pip install pylsl")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def record(
        self,
        duration: int,
        session_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Record EEG session to CSV file.

        Args:
            duration: Recording duration in seconds
            session_name: Custom session name (default: timestamp)

        Returns:
            Path to saved CSV file, or None if recording failed
        """
        if not self.is_connected:
            print("❌ Not connected to Muse S. Call connect() first.")
            return None

        # Generate filename
        if session_name is None:
            session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        output_file = self.output_dir / f"{session_name}.csv"

        print(f"\n🎙️  Recording session: {session_name}")
        print(f"   Duration: {duration} seconds")
        print(f"   Output: {output_file}")
        print(f"   Press Ctrl+C to stop early\n")

        # Record data
        samples = []
        timestamps = []
        start_time = time.time()

        try:
            while (time.time() - start_time) < duration:
                sample, timestamp = self.inlet.pull_sample(timeout=1.0)

                if sample:
                    samples.append(sample)
                    timestamps.append(timestamp)

                    # Progress indicator
                    elapsed = time.time() - start_time
                    if int(elapsed) % 10 == 0 and elapsed > 0:
                        progress = (elapsed / duration) * 100
                        print(f"   Progress: {progress:.1f}% ({int(elapsed)}s / {duration}s)")

        except KeyboardInterrupt:
            print("\n⚠️  Recording stopped by user")

        # Save to CSV
        print(f"\n💾 Saving {len(samples)} samples...")

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['timestamp'] + self.channels)

            # Data
            for ts, sample in zip(timestamps, samples):
                writer.writerow([ts] + sample[:len(self.channels)])

        print(f"✅ Recording saved: {output_file}")
        print(f"   Samples: {len(samples)}")
        print(f"   Duration: {len(samples) / self.sampling_rate:.2f} seconds")

        return output_file


class MockEEGGenerator:
    """
    Generate realistic synthetic EEG data for development/testing.

    Simulates:
    - Meditation-like patterns (increasing alpha, decreasing beta)
    - Realistic noise and artifacts
    - Natural frequency band variations

    Usage:
        generator = MockEEGGenerator(output_dir="data/raw")
        generator.generate_session(duration=300, session_name="mock_001")
    """

    def __init__(
        self,
        output_dir: str = "data/raw",
        channels: Optional[List[str]] = None,
        sampling_rate: int = 256
    ):
        """Initialize mock EEG generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.channels = channels or ["TP9", "AF7", "AF8", "TP10"]
        self.sampling_rate = sampling_rate

    def _generate_band(
        self,
        freq_range: tuple,
        n_samples: int,
        amplitude: float = 1.0
    ) -> np.ndarray:
        """Generate signal in specific frequency band."""
        t = np.arange(n_samples) / self.sampling_rate

        # Random frequency within band
        freq = np.random.uniform(freq_range[0], freq_range[1])

        # Generate sine wave with noise
        signal = amplitude * np.sin(2 * np.pi * freq * t)

        # Add pink noise (1/f)
        noise = np.random.randn(n_samples)
        noise = np.cumsum(noise)  # Simple pink noise approximation
        noise = noise / np.std(noise) * amplitude * 0.3

        return signal + noise

    def generate_session(
        self,
        duration: int = 300,
        session_name: Optional[str] = None,
        meditation_quality: str = "medium"
    ) -> Path:
        """
        Generate synthetic meditation session.

        Args:
            duration: Session duration in seconds
            session_name: Custom session name
            meditation_quality: "deep", "medium", "restless"
                - deep: high alpha, low beta
                - medium: balanced
                - restless: low alpha, high beta

        Returns:
            Path to generated CSV file
        """
        n_samples = duration * self.sampling_rate

        if session_name is None:
            session_name = f"mock_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n🎲 Generating mock EEG session: {session_name}")
        print(f"   Duration: {duration} seconds ({n_samples} samples)")
        print(f"   Quality: {meditation_quality}")

        # Quality parameters
        quality_params = {
            "deep": {"alpha": 2.0, "theta": 1.5, "beta": 0.5, "delta": 1.0},
            "medium": {"alpha": 1.2, "theta": 1.0, "beta": 1.0, "delta": 0.8},
            "restless": {"alpha": 0.6, "theta": 0.8, "beta": 1.8, "delta": 0.5}
        }
        params = quality_params.get(meditation_quality, quality_params["medium"])

        # Generate data for each channel
        data = {}
        for i, channel in enumerate(self.channels):
            # Mix frequency bands
            delta = self._generate_band((0.5, 4), n_samples, params["delta"] * 10)
            theta = self._generate_band((4, 8), n_samples, params["theta"] * 15)
            alpha = self._generate_band((8, 13), n_samples, params["alpha"] * 20)
            beta = self._generate_band((13, 30), n_samples, params["beta"] * 10)
            gamma = self._generate_band((30, 50), n_samples, 5)

            # Combine bands
            signal = delta + theta + alpha + beta + gamma

            # Add occasional artifacts (eye blinks, movement)
            n_artifacts = np.random.randint(5, 15)
            for _ in range(n_artifacts):
                artifact_pos = np.random.randint(0, n_samples - 100)
                artifact = np.random.randn(100) * 50  # Large spike
                signal[artifact_pos:artifact_pos+100] += artifact

            # Normalize to realistic EEG range (microvolts)
            signal = signal / np.std(signal) * 30  # ~30 uV typical

            data[channel] = signal

        # Create timestamps
        timestamps = np.arange(n_samples) / self.sampling_rate

        # Save to CSV
        output_file = self.output_dir / f"{session_name}.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp'] + self.channels)

            for i in range(n_samples):
                row = [timestamps[i]] + [data[ch][i] for ch in self.channels]
                writer.writerow(row)

        print(f"✅ Mock session generated: {output_file}")
        print(f"   Samples: {n_samples}")
        print(f"   File size: {output_file.stat().st_size / 1024:.2f} KB")

        return output_file


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EEG Recording CLI")
    parser.add_argument("--mock", action="store_true", help="Generate mock data")
    parser.add_argument("--duration", type=int, default=60, help="Recording duration (seconds)")
    parser.add_argument("--session", type=str, help="Session name")
    parser.add_argument("--quality", type=str, default="medium",
                       choices=["deep", "medium", "restless"],
                       help="Mock session quality")

    args = parser.parse_args()

    if args.mock:
        generator = MockEEGGenerator()
        generator.generate_session(
            duration=args.duration,
            session_name=args.session,
            meditation_quality=args.quality
        )
    else:
        recorder = MuseRecorder()
        if recorder.connect():
            recorder.record(duration=args.duration, session_name=args.session)
