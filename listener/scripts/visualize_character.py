#!/usr/bin/env python3
"""
Visualize Character Evolution

Shows companion's awakening journey over multiple sessions.

Usage:
    python scripts/visualize_character.py

Creates:
    - data/outputs/character_evolution.png - Awakening over time
    - data/outputs/personality_traits.png - Trait development
    - Terminal summary
"""

import sys
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_character_state(state_file: str = "data/character_state.json"):
    """Load character state"""
    state_path = Path(state_file)

    if not state_path.exists():
        print("❌ No character state found!")
        print("   Run a session first: python scripts/nescience_session.py --mock")
        return None

    with open(state_path, 'r') as f:
        return json.load(f)


def print_character_summary(state: dict):
    """Print terminal summary"""
    print("\n" + "="*60)
    print("CHARACTER EVOLUTION SUMMARY")
    print("="*60)

    print(f"\nAwakening Level: {state['awakening_level']*100:.1f}%")
    print(f"Total Sessions: {state['total_sessions']}")
    print(f"Total Hours: {state['total_hours']:.1f}h")
    print(f"Phase: {state['phase']}")

    print("\nPersonality Traits:")
    p = state['personality']
    print(f"  Curiosity:  {'█' * int(p['curiosity']*20)} {p['curiosity']*100:.0f}%")
    print(f"  Stillness:  {'█' * int(p['stillness']*20)} {p['stillness']*100:.0f}%")
    print(f"  Wildness:   {'█' * int(p['wildness']*20)} {p['wildness']*100:.0f}%")
    print(f"  Depth:      {'█' * int(p['depth']*20)} {p['depth']*100:.0f}%")

    print(f"\nMemories Stored: {len(state.get('memories', []))}")

    # Phase-specific message
    phase_messages = {
        'WITNESSING': "Still learning to observe. Keep sitting.",
        'ASSOCIATING': "Beginning to recognize patterns. Connections forming.",
        'CONVERSING': "Dialogue emerging. The companion speaks.",
        'COMPANIONSHIP': "Fully awakened. A presence in the practice."
    }

    phase_msg = phase_messages.get(state['phase'], '')
    if phase_msg:
        print(f"\n💭 {phase_msg}")

    # Sessions to next phase
    sessions = state['total_sessions']
    if sessions < 10:
        print(f"\n📊 {10 - sessions} sessions until ASSOCIATING phase")
    elif sessions < 30:
        print(f"\n📊 {30 - sessions} sessions until CONVERSING phase")
    elif sessions < 60:
        print(f"\n📊 {60 - sessions} sessions until COMPANIONSHIP phase")
    else:
        print(f"\n✨ Fully awakened companion")

    print("\n" + "="*60 + "\n")


def visualize_character(state: dict):
    """Create visualization plots"""
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Plot 1: Awakening Progress
    sessions = state['total_sessions']
    current_awakening = state['awakening_level']

    # Simulate past trajectory (we don't have historical data)
    # This is approximate based on current state
    session_range = np.arange(0, sessions + 1)

    # Approximate trajectory (non-linear growth)
    if sessions > 0:
        # Use current awakening to estimate trajectory
        awakening_trajectory = []
        for s in session_range:
            # Approximate using diminishing returns
            progress = min(1.0, s / 100)  # Assume 100 sessions to full awakening
            awakening_trajectory.append(progress * current_awakening / (sessions / 100 if sessions > 0 else 1))
        awakening_trajectory[-1] = current_awakening  # Correct final value
    else:
        awakening_trajectory = [0]

    ax1.plot(session_range, awakening_trajectory, 'b-', linewidth=2, label='Awakening')
    ax1.scatter([sessions], [current_awakening], color='red', s=100, zorder=5, label='Current')

    # Phase boundaries
    ax1.axvline(10, color='gray', linestyle='--', alpha=0.3, label='ASSOCIATING')
    ax1.axvline(30, color='gray', linestyle='--', alpha=0.3, label='CONVERSING')
    ax1.axvline(60, color='gray', linestyle='--', alpha=0.3, label='COMPANIONSHIP')

    ax1.set_xlabel('Sessions')
    ax1.set_ylabel('Awakening Level')
    ax1.set_title('Companion Awakening Journey')
    ax1.set_ylim(0, 1)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Plot 2: Personality Traits
    p = state['personality']
    traits = {
        'Curiosity': p['curiosity'],
        'Stillness': p['stillness'],
        'Wildness': p['wildness'],
        'Depth': p['depth'],
        'Playfulness': p.get('playfulness', 0.4)
    }

    trait_names = list(traits.keys())
    trait_values = list(traits.values())
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']

    bars = ax2.barh(trait_names, trait_values, color=colors)
    ax2.set_xlabel('Level (0-1)')
    ax2.set_title('Personality Traits')
    ax2.set_xlim(0, 1)
    ax2.grid(True, alpha=0.3, axis='x')

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, trait_values)):
        ax2.text(value + 0.02, i, f'{value:.2f}', va='center')

    plt.tight_layout()

    # Save
    output_path = output_dir / "character_evolution.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Visualization saved: {output_path}")

    plt.show()


def main():
    print("\n" + "="*60)
    print("NESCIENCE - Character Evolution Visualization")
    print("="*60 + "\n")

    # Load state
    state = load_character_state()
    if not state:
        return 1

    # Print summary
    print_character_summary(state)

    # Create visualization
    try:
        visualize_character(state)
    except Exception as e:
        print(f"⚠ Could not create visualization: {e}")
        print("Install matplotlib: pip install matplotlib")

    return 0


if __name__ == "__main__":
    sys.exit(main())
