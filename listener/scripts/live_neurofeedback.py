#!/usr/bin/env python3
"""
Live Neurofeedback - THE LISTENER

Real-time EEG processing with visual feedback.

Usage:
    # Basic usage (connects to Muse S, starts WebSocket server)
    python scripts/live_neurofeedback.py

    # Custom options
    python scripts/live_neurofeedback.py --port 8765 --window 5.0 --calibrate baseline_session.h5

    # Save test visualization client
    python scripts/live_neurofeedback.py --save-client

    # Then open test_client.html in browser
"""

import sys
from pathlib import Path
import argparse
import asyncio
import numpy as np
from pylsl import StreamInlet, resolve_byprop
import time
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.realtime_feedback import RealtimeFeedback, VisualFeedback
from pipeline.websocket_server import NeurofeedbackServer, save_test_client


class LiveNeurofeedback:
    """
    Live neurofeedback system.

    Connects to Muse S, processes EEG in real-time,
    and streams feedback to visualization clients.
    """

    def __init__(
        self,
        window_size: float = 5.0,
        update_rate: float = 0.5,
        websocket_port: int = 8765,
        calibration_file: str = None
    ):
        """
        Initialize live neurofeedback.

        Args:
            window_size: Rolling window size (seconds)
            update_rate: Update interval (seconds)
            websocket_port: WebSocket server port
            calibration_file: Path to baseline session for calibration
        """
        self.window_size = window_size
        self.update_rate = update_rate
        self.websocket_port = websocket_port

        # Initialize components
        print("\n" + "═" * 60)
        print("  🧘 THE LISTENER - Live Neurofeedback")
        print("═" * 60 + "\n")

        # Load calibration data if provided
        reference_data = None
        if calibration_file:
            reference_data = self._load_calibration(calibration_file)

        # Initialize feedback processor
        self.feedback = RealtimeFeedback(
            window_size=window_size,
            update_rate=update_rate,
            reference_data=reference_data
        )

        # Initialize WebSocket server
        self.server = NeurofeedbackServer(port=websocket_port)

        # Register callback
        self.feedback.register_callback(self._on_state_update)

        # LSL stream
        self.inlet = None
        self.is_running = False

        # Statistics
        self.session_start_time = None
        self.total_samples = 0

    def _load_calibration(self, calibration_file: str):
        """
        Load calibration data from baseline session.

        Args:
            calibration_file: Path to .h5 session file

        Returns:
            Reference data dict
        """
        import pandas as pd

        try:
            print(f"📊 Loading calibration: {calibration_file}")
            features_df = pd.read_hdf(calibration_file, key='features')

            # Extract alpha/beta timeseries for thresholds
            alpha_cols = [c for c in features_df.columns if 'alpha' in c.lower()]
            beta_cols = [c for c in features_df.columns if 'beta' in c.lower()]

            if alpha_cols and beta_cols:
                alpha_ts = features_df[alpha_cols].mean(axis=1).values
                beta_ts = features_df[beta_cols].mean(axis=1).values

                # Compute thresholds
                reference_data = {
                    'alpha_upper': np.percentile(alpha_ts, 75),
                    'alpha_lower': np.percentile(alpha_ts, 25),
                    'beta_upper': np.percentile(beta_ts, 75),
                    'beta_lower': np.percentile(beta_ts, 25)
                }

                print(f"✅ Calibration loaded")
                return reference_data
            else:
                print("⚠️  No alpha/beta data in calibration file")
                return None

        except Exception as e:
            print(f"⚠️  Could not load calibration: {e}")
            return None

    def _on_state_update(self, state: dict):
        """
        Callback when meditation state is updated.

        Args:
            state: State dict from RealtimeFeedback
        """
        # Print to console
        print(f"\r{state['state_message']} | "
              f"Depth: {state['depth_smooth']:5.1f} | "
              f"Quality: {state['quality']:5.1f} | "
              f"Alpha: {state['alpha_performance']:+.2f}",
              end='', flush=True)

        # Broadcast to WebSocket clients (async-safe)
        # Server will handle broadcasting in its event loop
        self.server.latest_state = state

    async def connect_muse(self):
        """
        Connect to Muse S via LSL.

        Returns:
            StreamInlet or None
        """
        print("🔍 Searching for Muse S EEG stream...")

        # Look for Muse stream
        streams = resolve_byprop('type', 'EEG', timeout=10)

        if not streams:
            print("❌ No EEG stream found")
            print("   Make sure Muse S is paired and muselsl is streaming:")
            print("   muselsl stream")
            return None

        # Connect to first stream
        inlet = StreamInlet(streams[0])
        info = inlet.info()

        print(f"✅ Connected to: {info.name()}")
        print(f"   Channels: {info.channel_count()}")
        print(f"   Sample rate: {info.nominal_srate()} Hz")

        return inlet

    async def run(self):
        """
        Run live neurofeedback session.

        Main loop: receive EEG samples, process, broadcast.
        """
        # Start WebSocket server in background
        asyncio.create_task(self.server.start())
        await asyncio.sleep(1)  # Let server start

        # Connect to Muse S
        self.inlet = await self.connect_muse()
        if not self.inlet:
            return

        print("\n" + "─" * 60)
        print("🔴 LIVE SESSION STARTED")
        print("   Open test_client.html in browser to see visualization")
        print("   Press Ctrl+C to stop")
        print("─" * 60 + "\n")

        self.is_running = True
        self.session_start_time = time.time()

        try:
            # Main processing loop
            while self.is_running:
                # Pull sample from LSL stream
                sample, timestamp = self.inlet.pull_sample(timeout=1.0)

                if sample:
                    # Add to feedback processor
                    self.feedback.add_sample(timestamp, np.array(sample))
                    self.total_samples += 1

                    # Broadcast latest state if available
                    if self.feedback.current_state:
                        await self.server.broadcast_state(self.feedback.current_state)

                # Small delay to prevent busy loop
                await asyncio.sleep(0.001)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping session...")

        finally:
            await self.stop()

    async def stop(self):
        """Stop neurofeedback session."""
        self.is_running = False

        # Print statistics
        if self.session_start_time:
            duration = time.time() - self.session_start_time
            stats = self.feedback.get_statistics()

            print("\n" + "═" * 60)
            print("  📊 Session Statistics")
            print("═" * 60)
            print(f"Duration:       {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f"Samples:        {self.total_samples}")
            print(f"Mean depth:     {stats.get('mean_depth', 0):.1f}/100")
            print(f"Max depth:      {stats.get('max_depth', 0):.1f}/100")
            print(f"Mean alpha:     {stats.get('mean_alpha', 0):.2f}")
            print("═" * 60 + "\n")

        # Stop server
        await self.server.stop()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Live neurofeedback for THE LISTENER"
    )
    parser.add_argument(
        "--window", type=float, default=5.0,
        help="Rolling window size in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--update-rate", type=float, default=0.5,
        help="Update interval in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--port", type=int, default=8765,
        help="WebSocket server port (default: 8765)"
    )
    parser.add_argument(
        "--calibrate", type=str,
        help="Baseline session file for calibration (.h5)"
    )
    parser.add_argument(
        "--save-client", action="store_true",
        help="Save test HTML client and exit"
    )

    args = parser.parse_args()

    # Save test client if requested
    if args.save_client:
        save_test_client()
        print("\nUsage:")
        print("  1. Start neurofeedback: python scripts/live_neurofeedback.py")
        print("  2. Open test_client.html in browser")
        return

    # Create and run neurofeedback
    nf = LiveNeurofeedback(
        window_size=args.window,
        update_rate=args.update_rate,
        websocket_port=args.port,
        calibration_file=args.calibrate
    )

    await nf.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
