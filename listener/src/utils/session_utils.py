"""
Common utilities for NESCIENCE sessions

Reduces code duplication across scripts.
"""

import time
import numpy as np
from pathlib import Path
from typing import Optional, Callable
import sys

# Handle imports
try:
    from integrations.osc_bridge import MindMonitorReceiver, MuseData
    from nescience.character_evolution import CharacterEvolution
except ImportError:
    # Add src to path if not already there
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from integrations.osc_bridge import MindMonitorReceiver, MuseData
    from nescience.character_evolution import CharacterEvolution


def load_character(
    state_file: str = "data/character_state.json",
    create_if_missing: bool = True
) -> CharacterEvolution:
    """
    Load character state with consistent error handling

    Args:
        state_file: Path to character state JSON
        create_if_missing: Create new character if file doesn't exist

    Returns:
        CharacterEvolution instance
    """
    character_path = Path(state_file)

    if not character_path.exists() and not create_if_missing:
        raise FileNotFoundError(
            f"Character state not found: {state_file}\n"
            f"Run a meditation session first to create one."
        )

    character = CharacterEvolution(state_file=state_file)

    print(f"✓ Character loaded")
    print(f"  Phase: {character.state.phase.value}")
    print(f"  Awakening: {character.state.awakening_level*100:.1f}%")
    print(f"  Sessions: {character.state.total_sessions}")

    return character


def setup_osc_receiver(
    port: int = 5000,
    callback: Optional[Callable] = None,
    timeout: float = 10.0
) -> MindMonitorReceiver:
    """
    Setup Mind Monitor OSC receiver with consistent error handling

    Args:
        port: OSC port to listen on
        callback: Callback function for EEG data
        timeout: Seconds to wait for first data

    Returns:
        MindMonitorReceiver instance
    """
    print(f"\nListening for Mind Monitor on port {port}...")
    print("Make sure:")
    print("  1. Muse headband is connected to Mind Monitor app")
    print("  2. OSC streaming is enabled in Mind Monitor")
    print(f"  3. OSC target is set to this device (port {port})")

    receiver = MindMonitorReceiver(port=port, callback=callback)
    receiver.start()

    return receiver


def generate_mock_eeg_sample() -> MuseData:
    """
    Generate a single mock EEG sample

    Useful for testing without hardware.
    Returns realistic-looking EEG data.
    """
    # Realistic EEG voltage ranges (-100 to 100 µV)
    eeg_tp9 = np.random.randn() * 50
    eeg_af7 = np.random.randn() * 50
    eeg_af8 = np.random.randn() * 50
    eeg_tp10 = np.random.randn() * 50

    # Realistic band power ranges (0-1, normalized)
    # Most people have alpha around 0.5-0.7 during relaxed states
    alpha = np.clip(0.6 + np.random.randn() * 0.15, 0, 1)
    beta = np.clip(0.4 + np.random.randn() * 0.1, 0, 1)
    theta = np.clip(0.5 + np.random.randn() * 0.12, 0, 1)
    delta = np.clip(0.3 + np.random.randn() * 0.08, 0, 1)

    return MuseData(
        timestamp=time.time(),
        eeg_tp9=eeg_tp9,
        eeg_af7=eeg_af7,
        eeg_af8=eeg_af8,
        eeg_tp10=eeg_tp10,
        alpha=alpha,
        beta=beta,
        theta=theta,
        delta=delta,
    )


def print_session_header(title: str, subtitle: Optional[str] = None):
    """Print consistent session header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)
    if subtitle:
        print(f"\n{subtitle}\n")


def print_session_footer():
    """Print consistent session footer"""
    print("\n" + "="*60 + "\n")


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        mins = seconds / 60
        return f"{mins:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp as human-readable string"""
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
