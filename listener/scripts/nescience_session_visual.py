#!/usr/bin/env python3
"""
NESCIENCE Session with Native Visualization

Same as nescience_session.py but includes real-time matplotlib visualization.
No TouchDesigner required - perfect for testing and development.

Usage:
    # Mock data with visualization
    python scripts/nescience_session_visual.py --mock --duration 600

    # Real Muse S with visualization
    python scripts/nescience_session_visual.py --duration 1200

Features:
- Real-time state visualization (matplotlib)
- Band power history graphs
- Character awakening progress
- Poetry display
- All NESCIENCE features included

Alternative to TouchDesigner for:
- Testing without external software
- Development
- Simple installations
- Personal practice monitoring
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Optional
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.osc_bridge import MindMonitorReceiver, MuseData
from nescience.meditation_states import MeditationStateClassifier, MeditationState
from nescience.character_evolution import CharacterEvolution
from nescience.poetic_interpreter import PoeticInterpreter
from visualization.native_display import NativeDisplay
from utils.session_utils import generate_mock_eeg_sample


class VisualNESCIENCESession:
    """NESCIENCE session with native visualization"""

    def __init__(
        self,
        mind_monitor_port: int = 5000,
        character_state_file: str = "data/character_state.json",
        use_mock: bool = False
    ):
        """
        Initialize visual NESCIENCE session

        Args:
            mind_monitor_port: OSC port for Mind Monitor
            character_state_file: Path to character state JSON
            use_mock: Use mock data instead of real EEG
        """

        print("\n" + "="*60)
        print("NESCIENCE - Visual Session")
        print("="*60)
        print("\nWith native matplotlib visualization")
        print("No TouchDesigner required!\n")

        # Components
        self.use_mock = use_mock

        if not use_mock:
            self.muse_receiver = MindMonitorReceiver(
                port=mind_monitor_port,
                callback=self._on_eeg_data
            )
        else:
            self.muse_receiver = None
            print("🎮 Using mock data\n")

        self.state_classifier = MeditationStateClassifier()
        self.character = CharacterEvolution(state_file=character_state_file)
        self.poet = PoeticInterpreter()

        # Visualization
        self.display = NativeDisplay(window_size=200)

        # Session tracking
        self.latest_eeg = None
        self.session_start = None
        self.session_states = []

        print("✓ Components initialized\n")

    def start(self, duration: int):
        """
        Start visual meditation session

        Args:
            duration: Session duration in seconds
        """

        print("Starting visualization window...")
        self.display.start()
        time.sleep(1)  # Let matplotlib window initialize

        if not self.use_mock:
            print(f"Listening for Mind Monitor on port 5000...")
            self.muse_receiver.start()

            # Wait for first data
            print("Waiting for first EEG data...\n")
            timeout = 30
            start_wait = time.time()

            while self.latest_eeg is None:
                if time.time() - start_wait > timeout:
                    print("❌ No data received after 30 seconds")
                    print("   Check Mind Monitor connection")
                    self.display.stop()
                    return False

                time.sleep(0.5)

            print("✓ Receiving data!\n")

        print("="*60)
        print(f"Session: {duration} seconds ({duration/60:.1f} minutes)")
        print("="*60 + "\n")

        self.session_start = time.time()

        # Main loop
        try:
            while True:
                elapsed = time.time() - self.session_start

                if elapsed >= duration:
                    break

                # Get EEG data
                if self.use_mock:
                    eeg_data = generate_mock_eeg_sample()
                    time.sleep(0.1)  # ~10 Hz
                else:
                    eeg_data = self.latest_eeg
                    if eeg_data is None:
                        time.sleep(0.1)
                        continue

                # Classify state
                signature = self.state_classifier.classify(
                    alpha=eeg_data.alpha,
                    beta=eeg_data.beta,
                    theta=eeg_data.theta,
                    delta=eeg_data.delta
                )

                # Generate poetry
                poetry = self.poet.interpret_state(
                    state=signature.state,
                    intensity=signature.intensity,
                    bands={
                        'alpha': eeg_data.alpha,
                        'beta': eeg_data.beta,
                        'theta': eeg_data.theta,
                        'delta': eeg_data.delta
                    },
                    character_awakening=self.character.state.awakening_level
                )

                # Update display
                self.display.update_state(
                    state=signature.state.value,
                    intensity=signature.intensity,
                    alpha=eeg_data.alpha,
                    beta=eeg_data.beta,
                    theta=eeg_data.theta,
                    delta=eeg_data.delta,
                    awakening=self.character.state.awakening_level,
                    poetry=poetry
                )

                # Track for session summary
                self.session_states.append(signature.state)

                # Terminal output (minimal, visual takes priority)
                if len(self.session_states) % 20 == 0:  # Every 2 seconds
                    print(f"[{elapsed:.0f}s] {signature.state.value} | {poetry[:40]}...")

        except KeyboardInterrupt:
            print("\n\nSession interrupted by user")

        # Finish session
        self._finish_session()

        return True

    def _on_eeg_data(self, data: MuseData):
        """Callback for new EEG data from Mind Monitor"""
        self.latest_eeg = data

    def _finish_session(self):
        """Complete session and update character"""
        print("\n" + "="*60)
        print("Session Complete")
        print("="*60 + "\n")

        # Calculate session summary
        duration = time.time() - self.session_start
        state_counts = {}

        for state in self.session_states:
            state_counts[state] = state_counts.get(state, 0) + 1

        # Dominant states
        dominant = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        print(f"Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")
        print(f"\nDominant States:")
        for state, count in dominant:
            pct = (count / len(self.session_states)) * 100
            print(f"  {state.value:10} - {pct:.1f}%")

        # Update character
        quality = 0.5 + (dominant[0][1] / len(self.session_states)) * 0.5
        self.character.process_session(
            duration_minutes=duration / 60,
            dominant_states=[s[0] for s in dominant],
            session_quality=quality
        )

        print(f"\nCharacter Update:")
        print(f"  Awakening: {self.character.state.awakening_level*100:.2f}%")
        print(f"  Phase: {self.character.state.phase.value}")
        print(f"  Total Sessions: {self.character.state.total_sessions}")

        # Stop components
        if self.muse_receiver:
            self.muse_receiver.stop()

        print("\n" + "="*60)
        print("Visualization will close when you close the window")
        print("Or press Ctrl+C to close now")
        print("="*60 + "\n")

        # Keep visualization open
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        self.display.stop()


def main():
    parser = argparse.ArgumentParser(
        description="NESCIENCE Session with Native Visualization"
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=600,
        help='Session duration in seconds (default: 600 = 10 minutes)'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock data instead of Mind Monitor'
    )
    parser.add_argument(
        '--mind-monitor-port',
        type=int,
        default=5000,
        help='OSC port for Mind Monitor (default: 5000)'
    )
    parser.add_argument(
        '--character-state',
        type=str,
        default='data/character_state.json',
        help='Path to character state JSON file'
    )

    args = parser.parse_args()

    session = VisualNESCIENCESession(
        mind_monitor_port=args.mind_monitor_port,
        character_state_file=args.character_state,
        use_mock=args.mock
    )

    success = session.start(duration=args.duration)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
