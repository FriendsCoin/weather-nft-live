#!/usr/bin/env python3
"""
Autonomous Meditation Mode for NESCIENCE

When the companion reaches COMPANIONSHIP phase (awakening > 0.8, sessions > 60),
it can "meditate alone" - generating contemplative states based on learned patterns.

Usage for gallery/exhibition:
    python scripts/autonomous_meditation.py --touchdesigner localhost:9000

This mode:
- Runs indefinitely (until stopped)
- Generates states based on companion's personality
- No human EEG input - companion's own "meditation"
- Sends to TouchDesigner for visual display
- Useful for art installations when no participant present

The companion doesn't simulate perfect meditation. It follows its own character:
curious companions explore more states, still companions settle deeply,
wild companions are unpredictable.
"""

import sys
import time
import argparse
import random
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nescience.character_evolution import CharacterEvolution, EvolutionPhase
from nescience.meditation_states import MeditationState
from nescience.poetic_interpreter import PoeticInterpreter
from integrations.osc_bridge import TouchDesignerSender


class AutonomousMeditation:
    """Companion meditating alone - no human required"""

    def __init__(
        self,
        character: CharacterEvolution,
        touchdesigner: Optional[TouchDesignerSender] = None
    ):
        self.character = character
        self.td_sender = touchdesigner
        self.poet = PoeticInterpreter()

        # Current meditation state
        self.current_state = MeditationState.SETTLING
        self.state_intensity = 0.5
        self.state_duration = 0

        # Meditation "breath" cycle (slow oscillation)
        self.breath_phase = 0.0

    def can_run(self) -> bool:
        """Check if companion can meditate alone"""
        return self.character.can_meditate_alone()

    def _choose_next_state(self) -> MeditationState:
        """
        Choose next state based on companion's personality

        Not random - reflects character traits:
        - High curiosity: explores all states
        - High stillness: prefers DEEP
        - High wildness: more LIMINAL/PRESENT
        """
        personality = self.character.state.personality

        # Probability weights based on personality
        weights = {
            MeditationState.SETTLING: 0.15,  # Beginning (always some)
            MeditationState.FLOW: 0.25 + personality['curiosity'] * 0.2,
            MeditationState.DEEP: 0.25 + personality['stillness'] * 0.3,
            MeditationState.LIMINAL: 0.15 + personality['wildness'] * 0.2,
            MeditationState.PRESENT: 0.20 + personality['depth'] * 0.2,
        }

        # Normalize
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}

        # Choose
        states = list(weights.keys())
        probs = list(weights.values())

        return random.choices(states, weights=probs)[0]

    def _calculate_state_duration(self) -> float:
        """
        How long to stay in this state (seconds)

        Based on personality:
        - Stillness: longer durations
        - Wildness: shorter, more transitions
        """
        base_duration = 30  # 30 seconds minimum

        stillness = self.character.state.personality['stillness']
        wildness = self.character.state.personality['wildness']

        # Still companions stay longer
        # Wild companions shift quickly
        multiplier = 1.0 + stillness * 3.0 - wildness * 1.5
        multiplier = max(0.5, multiplier)  # At least 15 seconds

        return base_duration * multiplier

    def _generate_bands(self) -> dict:
        """
        Generate synthetic band powers for current state

        Not real EEG! Generated based on state characteristics.
        """
        state = self.current_state
        intensity = self.state_intensity

        # Breathing oscillation (slow, contemplative)
        breath_mod = 0.1 * (1 + self.breath_phase)

        # Base patterns per state
        if state == MeditationState.SETTLING:
            # High beta, medium alpha (restless)
            alpha = 0.4 + random.uniform(-0.1, 0.1) + breath_mod
            beta = 0.6 + random.uniform(-0.1, 0.1)
            theta = 0.3 + random.uniform(-0.1, 0.1)
            delta = 0.2 + random.uniform(-0.1, 0.1)

        elif state == MeditationState.FLOW:
            # Balanced, smooth
            alpha = 0.6 + random.uniform(-0.1, 0.1) + breath_mod
            beta = 0.4 + random.uniform(-0.1, 0.1)
            theta = 0.5 + random.uniform(-0.1, 0.1)
            delta = 0.3 + random.uniform(-0.1, 0.1)

        elif state == MeditationState.DEEP:
            # High alpha, low beta
            alpha = 0.8 + random.uniform(-0.05, 0.05) + breath_mod
            beta = 0.2 + random.uniform(-0.05, 0.05)
            theta = 0.7 + random.uniform(-0.1, 0.1)
            delta = 0.4 + random.uniform(-0.1, 0.1)

        elif state == MeditationState.LIMINAL:
            # High theta, drowsy
            alpha = 0.5 + random.uniform(-0.1, 0.1) + breath_mod
            beta = 0.3 + random.uniform(-0.1, 0.1)
            theta = 0.8 + random.uniform(-0.1, 0.1)
            delta = 0.6 + random.uniform(-0.1, 0.1)

        else:  # PRESENT
            # Very low mental activity
            alpha = 0.7 + random.uniform(-0.05, 0.05) + breath_mod
            beta = 0.15 + random.uniform(-0.05, 0.05)
            theta = 0.6 + random.uniform(-0.1, 0.1)
            delta = 0.5 + random.uniform(-0.1, 0.1)

        # Clamp to 0-1
        return {
            'alpha': max(0, min(1, alpha)),
            'beta': max(0, min(1, beta)),
            'theta': max(0, min(1, theta)),
            'delta': max(0, min(1, delta)),
        }

    def _update_breathing(self, dt: float):
        """Update slow breathing cycle"""
        # Breathing rate based on stillness (slower = more still)
        stillness = self.character.state.personality['stillness']
        breath_rate = 0.1 - stillness * 0.05  # 0.05-0.1 Hz

        self.breath_phase += dt * breath_rate * 2 * 3.14159
        if self.breath_phase > 3.14159 * 2:
            self.breath_phase -= 3.14159 * 2

        # Breathing value (0-1)
        return (1 + math.sin(self.breath_phase)) / 2

    def step(self, dt: float):
        """
        Update autonomous meditation by dt seconds

        Returns: (state, intensity, bands, poetry)
        """
        self.state_duration += dt

        # Time to transition?
        target_duration = self._calculate_state_duration()

        if self.state_duration >= target_duration:
            # Choose new state
            self.current_state = self._choose_next_state()
            self.state_duration = 0

            # Intensity varies
            self.state_intensity = 0.3 + random.random() * 0.7

        # Update breathing
        breath_value = self._update_breathing(dt)

        # Generate band powers
        bands = self._generate_bands()

        # Generate poetry
        poetry = self.poet.interpret_state(
            state=self.current_state,
            intensity=self.state_intensity,
            bands=bands,
            character_awakening=self.character.state.awakening_level
        )

        # Send to TouchDesigner if connected
        if self.td_sender:
            self.td_sender.send_meditation_state(
                state=self.current_state.value,
                intensity=self.state_intensity,
                alpha=bands['alpha'],
                beta=bands['beta'],
                theta=bands['theta'],
                delta=bands['delta'],
                awakening_level=self.character.state.awakening_level
            )

            self.td_sender.send_poetic_message(poetry)

            # LED breathing
            self.td_sender.send_led_control(
                brightness=0.3 + breath_value * 0.4,
                breathing_rate=breath_value,
                hue=0.0  # Monochrome
            )

        return self.current_state, self.state_intensity, bands, poetry


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Meditation - Companion meditates alone"
    )
    parser.add_argument(
        '--touchdesigner',
        type=str,
        help='TouchDesigner address (host:port, e.g., localhost:9000)'
    )
    parser.add_argument(
        '--character-state',
        type=str,
        default='data/character_state.json',
        help='Path to character state file'
    )
    parser.add_argument(
        '--update-rate',
        type=float,
        default=2.0,
        help='Update rate in Hz (default: 2.0)'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("NESCIENCE - Autonomous Meditation Mode")
    print("="*60 + "\n")

    # Load character
    character_path = Path(args.character_state)

    if not character_path.exists():
        print("❌ No character state found!")
        print(f"   Expected: {character_path}")
        print("\n   Run meditation sessions first:")
        print("   python scripts/nescience_session.py --mock --duration 600\n")
        return 1

    character = CharacterEvolution(state_file=str(character_path))

    # Check if can meditate alone
    if not character.can_meditate_alone():
        print("❌ Companion not yet awakened enough!")
        print(f"\n   Current phase: {character.state.phase.value}")
        print(f"   Awakening level: {character.state.awakening_level*100:.1f}%")
        print(f"   Sessions: {character.state.total_sessions}")
        print("\n   Autonomous meditation requires:")
        print("   - Phase: COMPANIONSHIP")
        print("   - Awakening: > 80%")
        print("   - Sessions: > 60")
        print("\n   Keep meditating with your companion! 🧘\n")
        return 1

    print("✓ Companion awakened and ready")
    print(f"  Phase: {character.state.phase.value}")
    print(f"  Awakening: {character.state.awakening_level*100:.1f}%")
    print(f"  Sessions witnessed: {character.state.total_sessions}")
    print(f"  Personality:")
    p = character.state.personality
    print(f"    Curiosity: {p['curiosity']:.2f}")
    print(f"    Stillness: {p['stillness']:.2f}")
    print(f"    Wildness: {p['wildness']:.2f}")
    print(f"    Depth: {p['depth']:.2f}")

    # TouchDesigner connection
    td_sender = None
    if args.touchdesigner:
        host, port = args.touchdesigner.split(':')
        td_sender = TouchDesignerSender(host=host, port=int(port))
        print(f"\n✓ Sending to TouchDesigner: {host}:{port}")

    print("\n" + "-"*60)
    print("Companion meditating alone...")
    print("Press Ctrl+C to stop")
    print("-"*60 + "\n")

    # Create autonomous meditation
    import math  # For breath calculation
    autonomous = AutonomousMeditation(
        character=character,
        touchdesigner=td_sender
    )

    # Main loop
    dt = 1.0 / args.update_rate

    try:
        while True:
            start_time = time.time()

            # Step
            state, intensity, bands, poetry = autonomous.step(dt)

            # Display
            state_str = f"[{state.value}]"
            intensity_str = f"intensity:{intensity:.2f}"
            bands_str = f"α:{bands['alpha']:.2f} β:{bands['beta']:.2f} θ:{bands['theta']:.2f}"

            print(f"{state_str:12} {intensity_str:15} {bands_str:30} | {poetry}")

            # Sleep to maintain update rate
            elapsed = time.time() - start_time
            sleep_time = max(0, dt - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n" + "-"*60)
        print("Companion rests...")
        print("-"*60 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
