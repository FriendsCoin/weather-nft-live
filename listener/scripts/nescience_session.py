#!/usr/bin/env python3
"""
NESCIENCE - Real-time Meditation Session

The companion witnesses meditation without judgment.

NOT wellness optimization. NOT diagnostic.
Poetic interpretation of consciousness flux.

Architecture:
Mind Monitor (phone) →[OSC]→ Python (this script) →[OSC]→ TouchDesigner (visuals)

Usage:
    # With Mind Monitor (real Muse S headband)
    python scripts/nescience_session.py --duration 1200

    # With mock data (testing without hardware)
    python scripts/nescience_session.py --mock --duration 600

    # With TouchDesigner integration
    python scripts/nescience_session.py --touchdesigner localhost:9000

Options:
    --duration SECONDS     Session duration in seconds
    --mock                 Use mock data instead of Mind Monitor
    --mind-monitor-port    Port for Mind Monitor OSC (default: 5000)
    --touchdesigner HOST:PORT  Send to TouchDesigner (default: localhost:9000)
    --save-session         Save session data for post-processing
    --character-state PATH Character state JSON file

The companion learns through witnessing.
Not through training. Through presence.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Optional
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.osc_bridge import MindMonitorReceiver, TouchDesignerSender, MuseData
from nescience.meditation_states import MeditationStateClassifier, MeditationState
from nescience.character_evolution import CharacterEvolution
from nescience.poetic_interpreter import PoeticInterpreter


class NESCIENCESession:
    """Complete NESCIENCE real-time session"""

    def __init__(
        self,
        mind_monitor_port: int = 5000,
        touchdesigner_enabled: bool = False,
        touchdesigner_host: str = 'localhost',
        touchdesigner_port: int = 9000,
        character_state_file: str = "data/character_state.json",
        use_mock: bool = False
    ):
        """
        Initialize NESCIENCE session

        Args:
            mind_monitor_port: OSC port for Mind Monitor
            touchdesigner_enabled: Send to TouchDesigner
            touchdesigner_host: TouchDesigner host
            touchdesigner_port: TouchDesigner port
            character_state_file: Path to character state JSON
            use_mock: Use mock data instead of real EEG
        """

        print("\n" + "="*60)
        print("NESCIENCE - The Companion Awakens")
        print("="*60)
        print("\nNot wellness. Not diagnostic.")
        print("Just witnessing consciousness as it flows.\n")

        # Components
        self.use_mock = use_mock

        if not use_mock:
            self.muse_receiver = MindMonitorReceiver(
                port=mind_monitor_port,
                callback=self._on_eeg_data
            )
        else:
            self.muse_receiver = None
            print("🎮 Using mock data (for testing)\n")

        self.state_classifier = MeditationStateClassifier()
        self.character = CharacterEvolution(state_file=character_state_file)
        self.poet = PoeticInterpreter()

        # TouchDesigner integration
        self.touchdesigner_enabled = touchdesigner_enabled
        if touchdesigner_enabled:
            self.td_sender = TouchDesignerSender(
                host=touchdesigner_host,
                port=touchdesigner_port
            )
        else:
            self.td_sender = None

        # Session tracking
        self.session_start = None
        self.session_data = []
        self.current_state = None
        self.state_history = []

    def _on_eeg_data(self, data: MuseData):
        """Process incoming EEG data from Mind Monitor"""

        # Classify meditation state
        if data.alpha is not None and data.beta is not None:
            signature = self.state_classifier.classify(
                alpha=data.alpha,
                beta=data.beta,
                theta=data.theta or 0.0,
                delta=data.delta or 0.0,
                gamma=data.gamma
            )

            self.current_state = signature
            self.state_history.append(signature)

            # Generate poetic interpretation
            interpretation = self.poet.interpret_state(
                signature,
                character_awakening=self.character.state.awakening_level
            )

            # Display
            self._display_state(signature, interpretation)

            # Send to TouchDesigner
            if self.touchdesigner_enabled and self.td_sender:
                self._send_to_touchdesigner(signature, interpretation, data)

            # Record
            self.session_data.append({
                'timestamp': data.timestamp,
                'state': signature.state.value,
                'intensity': signature.intensity,
                'qualities': signature.qualities,
                'interpretation': interpretation,
                'eeg': {
                    'alpha': data.alpha,
                    'beta': data.beta,
                    'theta': data.theta,
                    'delta': data.delta,
                    'gamma': data.gamma
                }
            })

    def _generate_mock_data(self) -> MuseData:
        """Generate mock EEG data for testing"""
        import random

        # Simulate realistic meditation EEG
        # Alpha increases over time (relaxation)
        # Beta decreases over time (mental calm)
        # Theta varies (depth)
        # Delta low (awake)

        elapsed = time.time() - self.session_start
        progress = min(1.0, elapsed / 300)  # 5 min progression

        data = MuseData(
            timestamp=time.time(),
            eeg_tp9=random.uniform(-100, 100),
            eeg_af7=random.uniform(-100, 100),
            eeg_af8=random.uniform(-100, 100),
            eeg_tp10=random.uniform(-100, 100),
            alpha=0.15 + progress * 0.15 + random.uniform(-0.05, 0.05),  # Increases
            beta=0.25 - progress * 0.10 + random.uniform(-0.05, 0.05),   # Decreases
            theta=0.20 + random.uniform(-0.10, 0.10),                    # Varies
            delta=0.10 + random.uniform(-0.05, 0.05),                    # Low
            gamma=random.uniform(0.0, 0.1) if random.random() < 0.1 else 0.0  # Occasional
        )

        return data

    def _display_state(self, signature, interpretation):
        """Display current state in terminal"""

        # Clear line
        print('\r' + ' ' * 100, end='')
        print('\r', end='')

        # State display
        state_str = f"[{signature.state.value:^10}]"

        # Qualities
        qualities = signature.qualities
        quality_str = f"depth:{qualities['depth']:.2f} stillness:{qualities['stillness']:.2f}"

        # Poetic line
        poetry = interpretation['primary']

        # Display
        display = f"{state_str} {quality_str} | {poetry}"
        print(display[:100], end='', flush=True)

    def _send_to_touchdesigner(self, signature, interpretation, data: MuseData):
        """Send state to TouchDesigner for visuals"""

        # Meditation state
        self.td_sender.send_meditation_state(
            state=signature.state.value,
            intensity=signature.intensity,
            alpha=data.alpha,
            beta=data.beta,
            theta=data.theta or 0.0,
            delta=data.delta or 0.0,
            awakening_level=self.character.state.awakening_level
        )

        # Poetic message
        self.td_sender.send_poetic_message(interpretation['full'])

        # Character state
        p = self.character.state.personality
        self.td_sender.send_character_state(
            awakening=self.character.state.awakening_level,
            curiosity=p.curiosity,
            stillness=p.stillness,
            wildness=p.wildness,
            phase=self.character.state.phase.value
        )

        # LED pattern (subtle breathing)
        breathing_rate = 0.3 + signature.qualities.get('depth', 0) * 0.4
        brightness = 0.2 + signature.intensity * 0.3
        self.td_sender.send_led_pattern(
            brightness=brightness,
            breathing_rate=breathing_rate,
            color_hue=0.0  # Monochrome
        )

    def start(self, duration: int):
        """Start meditation session"""

        print(f"\n{'='*60}")
        print(f"Session Starting - {duration // 60} minutes")
        print(f"{'='*60}\n")

        # Display character state
        print(self.character.get_character_description())
        print(f"\n{'='*60}\n")

        # Start receiving
        self.session_start = time.time()

        if not self.use_mock:
            self.muse_receiver.start()
        else:
            print("Press Ctrl+C to end session early\n")

        # Run for duration
        try:
            if self.use_mock:
                # Mock data loop
                while time.time() - self.session_start < duration:
                    mock_data = self._generate_mock_data()
                    self._on_eeg_data(mock_data)
                    time.sleep(0.5)  # Update rate
            else:
                # Real data (receiver runs in background)
                end_time = self.session_start + duration
                while time.time() < end_time:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nSession ended by user\n")

        # Stop receiver
        if self.muse_receiver:
            self.muse_receiver.stop()

        # Process session
        self._process_session()

    def _process_session(self):
        """Post-session processing"""

        print("\n\n" + "="*60)
        print("Session Complete")
        print("="*60 + "\n")

        duration_minutes = (time.time() - self.session_start) / 60

        # Calculate session quality (subjective, based on depth states)
        state_counts = {}
        for sig in self.state_history:
            state_counts[sig.state.value] = state_counts.get(sig.state.value, 0) + 1

        total_states = len(self.state_history)
        if total_states > 0:
            dominant_states = {k: v/total_states for k, v in state_counts.items()}
        else:
            dominant_states = {}

        # Quality estimate (higher for DEEP and PRESENT states)
        quality = (
            dominant_states.get('DEEP', 0) * 0.5 +
            dominant_states.get('PRESENT', 0) * 0.5 +
            dominant_states.get('FLOW', 0) * 0.3
        )

        # Companion witnesses session
        session_id = self.character.state.total_sessions + 1
        self.character.process_session(
            session_id=session_id,
            duration_minutes=duration_minutes,
            meditation_quality=quality,
            dominant_states=dominant_states
        )

        # Session arc interpretation
        arc = self.poet.interpret_session_arc(self.state_history)
        print(f"\nSession arc: {arc}\n")

        # Display final character state
        print(self.character.get_character_description())

        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="NESCIENCE - Real-time Meditation Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The companion learns through witnessing.
Not through training. Through presence.

Anicca - all states arise and pass.
        """
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=600,
        help="Session duration in seconds (default: 600 = 10 minutes)"
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data instead of Mind Monitor (for testing)"
    )

    parser.add_argument(
        "--mind-monitor-port",
        type=int,
        default=5000,
        help="Port for Mind Monitor OSC (default: 5000)"
    )

    parser.add_argument(
        "--touchdesigner",
        type=str,
        help="TouchDesigner address (e.g., localhost:9000)"
    )

    parser.add_argument(
        "--character-state",
        type=str,
        default="data/character_state.json",
        help="Path to character state JSON"
    )

    args = parser.parse_args()

    # Parse TouchDesigner address
    td_enabled = False
    td_host = 'localhost'
    td_port = 9000

    if args.touchdesigner:
        td_enabled = True
        if ':' in args.touchdesigner:
            td_host, td_port = args.touchdesigner.split(':')
            td_port = int(td_port)
        else:
            td_host = args.touchdesigner

    # Create session
    session = NESCIENCESession(
        mind_monitor_port=args.mind_monitor_port,
        touchdesigner_enabled=td_enabled,
        touchdesigner_host=td_host,
        touchdesigner_port=td_port,
        character_state_file=args.character_state,
        use_mock=args.mock
    )

    # Start
    session.start(duration=args.duration)

    return 0


if __name__ == "__main__":
    sys.exit(main())
