#!/usr/bin/env python3
"""
Biofeedback Game - Real-Time Meditation Visualization

Combines real-time EEG processing with immersive visual feedback.
Displays meditation state as an interactive, responsive visualization.

Features:
- Live EEG processing from Muse S
- Real-time VAE encoding
- Pygame visualization with particles and smooth animations
- Optional TouchDesigner integration via OSC
- Automatic state detection and poetic messages
- Screenshot capture

Usage:
    # Run with pygame visualization
    python scripts/biofeedback_game.py

    # Run with TouchDesigner integration
    python scripts/biofeedback_game.py --osc --osc-port 8000

    # Run fullscreen
    python scripts/biofeedback_game.py --fullscreen

    # Run with custom model
    python scripts/biofeedback_game.py --model models/vae_epoch_100.pt

Prerequisites:
    1. Muse S headband connected via bluetooth
    2. Run: muselsl stream (in separate terminal)
    3. Trained VAE model (from training)

Controls:
    - ESC: Exit
    - F: Toggle fullscreen
    - S: Save screenshot
"""

import sys
from pathlib import Path
import argparse
import time
import numpy as np
from threading import Thread, Event
from queue import Queue
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.realtime_feedback import RealtimeFeedback
from src.pipeline.feature_extraction import FeatureExtractor
from src.models.vae import MeditationVAE
from src.utils.meditation_analysis import MeditationAnalyzer
from src.pipeline.visual_feedback import VisualFeedback
from src.pipeline.osc_server import OSCServer
import pylsl


# ============================================================
# POETIC STATE MESSAGES
# ============================================================

STATE_MESSAGES = {
    "deep": [
        "You are descending into infinite space",
        "Stillness blooms like a lotus in darkness",
        "You have found the eye of the storm",
        "Time dissolves at the edges of awareness",
        "You are becoming the silence",
    ],
    "focused": [
        "You are finding your center",
        "The mind sharpens like a beam of light",
        "Clarity emerges from the fog",
        "You are gathering scattered attention",
        "Focus crystallizes into presence",
    ],
    "calm": [
        "Stillness begins to settle",
        "The waters of the mind grow clear",
        "You are releasing what does not serve",
        "Peace ripples outward from your core",
        "Tension melts like snow in spring",
    ],
    "distracted": [
        "Your mind wanders through familiar paths",
        "Thoughts drift like clouds across the sky",
        "The journey begins with gentle awareness",
        "Notice without judgment, return without force",
        "Every beginning is a new opportunity",
    ]
}


class BiofeedbackGame:
    """
    Real-time biofeedback visualization for meditation
    """

    def __init__(
        self,
        model_path: str,
        use_osc: bool = False,
        osc_host: str = "127.0.0.1",
        osc_port: int = 8000,
        window_size: tuple = (1280, 720),
        fullscreen: bool = False,
        fps: int = 60,
        update_rate: float = 0.5  # seconds between EEG updates
    ):
        """
        Initialize biofeedback game

        Args:
            model_path: Path to trained VAE model
            use_osc: Enable OSC output to TouchDesigner
            osc_host: OSC target host
            osc_port: OSC target port
            window_size: Window dimensions (width, height)
            fullscreen: Run in fullscreen mode
            fps: Target frame rate for visualization
            update_rate: Seconds between EEG metric updates
        """
        self.model_path = model_path
        self.use_osc = use_osc
        self.update_rate = update_rate

        # Components
        self.realtime_feedback = None
        self.feature_extractor = None
        self.vae = None
        self.analyzer = None
        self.visual = None
        self.osc = None
        self.lsl_inlet = None

        # State
        self.running = False
        self.stop_event = Event()
        self.metric_queue = Queue(maxsize=10)

        # Message rotation
        self.message_index = {state: 0 for state in STATE_MESSAGES}

        print("=" * 60)
        print("  🎮 THE LISTENER - Biofeedback Game")
        print("=" * 60)
        print()

        # Initialize components
        self._init_eeg_pipeline()
        self._init_vae_model()
        self._init_analyzer()
        self._init_visualization(window_size, fullscreen, fps)

        if use_osc:
            self._init_osc(osc_host, osc_port)

        print("\n✅ Initialization complete!")
        print()

    def _init_eeg_pipeline(self):
        """Initialize EEG processing pipeline"""
        print("📊 Initializing EEG pipeline...")

        try:
            # Initialize real-time feedback system
            self.realtime_feedback = RealtimeFeedback(
                window_size=10.0,  # 10 second windows
                update_rate=self.update_rate,
                sfreq=256.0,
                channels=['TP9', 'AF7', 'AF8', 'TP10']
            )

            # Connect to LSL stream
            print("   Searching for Muse stream...")
            streams = pylsl.resolve_byprop('type', 'EEG', timeout=5.0)
            if not streams:
                raise RuntimeError("No EEG stream found. Is 'muselsl stream' running?")

            self.lsl_inlet = pylsl.StreamInlet(streams[0])
            print(f"   ✅ Connected to {streams[0].name()}")

            self.feature_extractor = FeatureExtractor()
            print("   ✅ EEG pipeline ready")

        except Exception as e:
            print(f"   ⚠️  EEG pipeline initialization failed: {e}")
            print("   Make sure 'muselsl stream' is running!")
            raise

    def _init_vae_model(self):
        """Load trained VAE model"""
        print(f"🧠 Loading VAE model: {self.model_path}")

        import torch

        # Load model
        checkpoint = torch.load(self.model_path, map_location='cpu')

        # Create VAE
        input_dim = checkpoint.get('input_dim', 34)
        latent_dim = checkpoint.get('latent_dim', 32)

        self.vae = MeditationVAE(input_dim=input_dim, latent_dim=latent_dim)
        self.vae.load_state_dict(checkpoint['model_state_dict'])
        self.vae.eval()

        print(f"   ✅ Model loaded (epoch {checkpoint.get('epoch', '?')})")

    def _init_analyzer(self):
        """Initialize meditation analyzer"""
        print("🧘 Initializing meditation analyzer...")

        self.analyzer = MeditationAnalyzer()
        print("   ✅ Analyzer ready")

    def _init_visualization(self, window_size: tuple, fullscreen: bool, fps: int):
        """Initialize pygame visualization"""
        print(f"🎨 Initializing visualization ({window_size[0]}x{window_size[1]})...")

        self.visual = VisualFeedback(
            width=window_size[0],
            height=window_size[1],
            fullscreen=fullscreen,
            fps=fps,
            theme='dark'
        )
        print("   ✅ Visualization ready")

    def _init_osc(self, host: str, port: int):
        """Initialize OSC server for TouchDesigner"""
        print(f"🎨 Initializing OSC ({host}:{port})...")

        self.osc = OSCServer(
            host=host,
            send_port=port,
            verbose=False  # Reduce spam
        )
        print("   ✅ OSC server ready")

    def _get_poetic_message(self, state: str) -> str:
        """Get rotating poetic message for state"""
        messages = STATE_MESSAGES.get(state, STATE_MESSAGES['calm'])
        idx = self.message_index[state]
        message = messages[idx]

        # Rotate to next message
        self.message_index[state] = (idx + 1) % len(messages)

        return message

    def _eeg_processing_loop(self):
        """
        Background thread for EEG processing
        Continuously reads from LSL stream and updates metrics
        """
        print("\n🎬 Starting EEG processing loop...")

        import torch

        try:
            last_analysis_time = time.time()

            while not self.stop_event.is_set():
                # Pull sample from LSL stream (non-blocking)
                sample, timestamp = self.lsl_inlet.pull_sample(timeout=0.1)

                if sample is None:
                    continue  # No data yet, try again

                # Add sample to real-time feedback buffer
                self.realtime_feedback.add_sample(timestamp, np.array(sample))

                # Check if we should analyze (based on update_rate)
                current_time = time.time()
                if (current_time - last_analysis_time) >= self.update_rate:
                    # Get current state from realtime feedback
                    rt_state = self.realtime_feedback.get_current_state()

                    if rt_state is None:
                        continue  # Not enough data yet

                    # Extract features for VAE encoding
                    # Get buffered EEG data
                    eeg_buffer = np.array(self.realtime_feedback.eeg_buffer).T  # [channels, samples]

                    # Only process if we have enough data
                    if eeg_buffer.shape[1] >= 256:  # At least 1 second of data
                        features = self.feature_extractor.extract_features(eeg_buffer)

                        # Encode to latent space
                        with torch.no_grad():
                            features_tensor = torch.tensor(
                                features,
                                dtype=torch.float32
                            ).unsqueeze(0)
                            mu, logvar = self.vae.encode(features_tensor)
                            latent = mu.numpy()[0]  # Use mean, not sampled

                        # Analyze meditation state
                        analysis = self.analyzer.analyze_session(
                            features=features,
                            latent_vector=latent
                        )

                        # Create state dict
                        state = {
                            'depth': analysis['depth_score'],
                            'quality': analysis['quality_score'],
                            'alpha_plus': analysis['performance_ratios']['alpha_plus'],
                            'alpha_minus': analysis['performance_ratios']['alpha_minus'],
                            'beta_plus': analysis['performance_ratios']['beta_plus'],
                            'beta_minus': analysis['performance_ratios']['beta_minus'],
                            'theta': features[5],  # Theta power
                            'delta': features[4],  # Delta power
                            'state': analysis['state'],
                            'message': self._get_poetic_message(analysis['state'])
                        }

                        # Send to main thread via queue
                        if not self.metric_queue.full():
                            self.metric_queue.put(state)

                        last_analysis_time = current_time

        except Exception as e:
            print(f"\n❌ EEG processing error: {e}")
            import traceback
            traceback.print_exc()

        print("\n⏹️  EEG processing loop stopped")

    def run(self):
        """
        Run the biofeedback game
        """
        print("\n" + "=" * 60)
        print("  🚀 Starting Biofeedback Game")
        print("=" * 60)
        print()
        print("Controls:")
        print("  - ESC: Exit")
        print("  - F: Toggle fullscreen")
        print("  - S: Save screenshot")
        print()
        print("Make sure Muse S is connected and 'muselsl stream' is running!")
        print()
        print("=" * 60)
        print()

        # Start EEG processing thread
        self.running = True
        eeg_thread = Thread(
            target=self._eeg_processing_loop,
            daemon=True
        )
        eeg_thread.start()

        # Give EEG thread time to start
        time.sleep(2)

        # Main visualization loop
        try:
            last_update = time.time()

            while self.visual.running:
                # Check for new metrics from EEG thread
                if not self.metric_queue.empty():
                    metrics = self.metric_queue.get()

                    # Update visualization
                    self.visual.update(metrics)

                    # Send to OSC if enabled
                    if self.use_osc and self.osc:
                        self.osc.send_meditation_state(metrics)
                        self.osc.send_mapped_visuals(
                            metrics['depth'],
                            metrics['quality'],
                            metrics['alpha_plus'],
                            metrics['state']
                        )

                    last_update = time.time()

                    # Print status
                    print(
                        f"📊 Depth: {metrics['depth']:5.1f} | "
                        f"Quality: {metrics['quality']:5.1f} | "
                        f"State: {metrics['state']:12s} | "
                        f"α+: {metrics['alpha_plus']:.2f}"
                    )

                # Render frame
                self.visual.render()

                # Check if too long since last update
                if time.time() - last_update > 5:
                    print("⚠️  No EEG updates for 5 seconds...")

        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")

        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            self.running = False
            self.stop_event.set()

            if self.osc:
                self.osc.stop()

            self.visual.close()

            print("\n✅ Biofeedback game stopped\n")


def main():
    parser = argparse.ArgumentParser(
        description="Real-time biofeedback visualization for meditation"
    )

    # Model
    parser.add_argument(
        "--model",
        default="models/vae_best.pt",
        help="Path to trained VAE model"
    )

    # OSC
    parser.add_argument(
        "--osc",
        action="store_true",
        help="Enable OSC output to TouchDesigner"
    )
    parser.add_argument(
        "--osc-host",
        default="127.0.0.1",
        help="OSC target host"
    )
    parser.add_argument(
        "--osc-port",
        type=int,
        default=8000,
        help="OSC target port"
    )

    # Visualization
    parser.add_argument(
        "--width",
        type=int,
        default=1280,
        help="Window width"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=720,
        help="Window height"
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Run in fullscreen mode"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Target frame rate"
    )

    # Processing
    parser.add_argument(
        "--update-rate",
        type=float,
        default=0.5,
        help="Seconds between EEG metric updates"
    )

    args = parser.parse_args()

    # Check if model exists
    if not Path(args.model).exists():
        print(f"❌ Model not found: {args.model}")
        print()
        print("Available models:")
        models_dir = Path("models")
        if models_dir.exists():
            for model_file in sorted(models_dir.glob("*.pt")):
                print(f"   - {model_file}")
        else:
            print("   (no models found)")
        print()
        print("Train a model first: python scripts/train_vae.py")
        return

    # Create and run game
    try:
        game = BiofeedbackGame(
            model_path=args.model,
            use_osc=args.osc,
            osc_host=args.osc_host,
            osc_port=args.osc_port,
            window_size=(args.width, args.height),
            fullscreen=args.fullscreen,
            fps=args.fps,
            update_rate=args.update_rate
        )

        game.run()

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
        sys.exit(0)
