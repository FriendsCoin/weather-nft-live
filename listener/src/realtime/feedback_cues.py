"""
Audio and Visual Feedback Cues for Real-time Neurofeedback

Provides immediate sensory feedback during meditation:
- Audio tones for different states
- Visual indicators (terminal-based and GUI)
- Haptic feedback (future)
"""

import numpy as np
import sys
import time
from typing import Optional
from enum import Enum


class AudioCue:
    """Generate audio cues for different meditation states"""

    def __init__(self, enabled: bool = True, volume: float = 0.5):
        """
        Initialize audio cue generator

        Args:
            enabled: Whether audio is enabled
            volume: Volume level (0.0 to 1.0)
        """
        self.enabled = enabled
        self.volume = volume
        self.sample_rate = 44100

        # Check for audio libraries
        try:
            import sounddevice as sd
            self.sd = sd
            self.audio_available = True
        except ImportError:
            self.sd = None
            self.audio_available = False
            if enabled:
                print("⚠ sounddevice not installed - audio feedback disabled")
                print("  Install with: pip install sounddevice")

    def generate_tone(self, frequency: float, duration: float = 0.2) -> np.ndarray:
        """
        Generate a pure tone

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds

        Returns:
            Audio samples
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Generate tone with envelope to avoid clicks
        tone = np.sin(2 * np.pi * frequency * t)

        # Apply fade in/out envelope
        envelope_len = int(0.01 * self.sample_rate)  # 10ms fade
        envelope = np.ones_like(tone)
        envelope[:envelope_len] = np.linspace(0, 1, envelope_len)
        envelope[-envelope_len:] = np.linspace(1, 0, envelope_len)

        tone = tone * envelope * self.volume

        return tone

    def play_tone(self, frequency: float, duration: float = 0.2):
        """
        Play a tone

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
        """
        if not self.enabled or not self.audio_available:
            return

        tone = self.generate_tone(frequency, duration)

        try:
            self.sd.play(tone, self.sample_rate)
            self.sd.wait()
        except Exception as e:
            # Silently fail if audio can't play
            pass

    def play_success_cue(self):
        """Play success/positive feedback cue (pleasant ascending tone)"""
        if not self.enabled or not self.audio_available:
            return

        # Ascending chord (C major: C-E-G)
        frequencies = [523.25, 659.25, 783.99]  # C5, E5, G5
        duration = 0.15

        for freq in frequencies:
            self.play_tone(freq, duration)
            time.sleep(0.05)

    def play_fail_cue(self):
        """Play failure/needs improvement cue (gentle low tone)"""
        if not self.enabled or not self.audio_available:
            return

        # Low gentle tone
        self.play_tone(220.0, 0.3)  # A3

    def play_drowsy_cue(self):
        """Play drowsiness alert (attention-grabbing but not harsh)"""
        if not self.enabled or not self.audio_available:
            return

        # Two quick beeps
        for _ in range(2):
            self.play_tone(440.0, 0.1)  # A4
            time.sleep(0.1)

    def play_perfect_cue(self):
        """Play perfect meditation state cue (harmonious chord)"""
        if not self.enabled or not self.audio_available:
            return

        # Beautiful ascending arpeggio
        frequencies = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        for freq in frequencies:
            self.play_tone(freq, 0.12)
            time.sleep(0.04)

    def play_baseline_cue(self):
        """Play neutral baseline cue (single soft tone)"""
        if not self.enabled or not self.audio_available:
            return

        self.play_tone(440.0, 0.15)  # A4

    def play_state_cue(self, state_name: str):
        """
        Play appropriate cue for a given state

        Args:
            state_name: Name of the feedback state
        """
        cue_map = {
            'alpha+': self.play_success_cue,
            'alpha-': self.play_fail_cue,
            'beta+': self.play_success_cue,
            'beta-': self.play_fail_cue,
            'a+b+': self.play_perfect_cue,
            'drowsy': self.play_drowsy_cue,
            'baseline': self.play_baseline_cue,
        }

        cue_func = cue_map.get(state_name, self.play_baseline_cue)
        cue_func()


class VisualCue:
    """Terminal-based visual feedback"""

    def __init__(self, enabled: bool = True, use_colors: bool = True):
        """
        Initialize visual cue display

        Args:
            enabled: Whether visual feedback is enabled
            use_colors: Whether to use terminal colors
        """
        self.enabled = enabled
        self.use_colors = use_colors and sys.stdout.isatty()

        # ANSI color codes
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m',
        }

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text"""
        if not self.use_colors:
            return text

        return f"{self.colors.get(color, '')}{text}{self.colors['reset']}"

    def show_state(self, state_name: str, alpha: float, beta: float, depth: float):
        """
        Display current state visually

        Args:
            state_name: Name of the state
            alpha: Alpha power
            beta: Beta power
            depth: Meditation depth score
        """
        if not self.enabled:
            return

        # Clear line and move cursor to beginning
        print('\r' + ' ' * 100, end='')
        print('\r', end='')

        # State indicator
        state_colors = {
            'alpha+': 'green',
            'alpha-': 'red',
            'beta+': 'green',
            'beta-': 'red',
            'a+b+': 'magenta',
            'drowsy': 'yellow',
            'baseline': 'white',
        }

        color = state_colors.get(state_name, 'white')
        state_display = self._colorize(f"[{state_name:^8}]", color)

        # Power bars
        alpha_bar = self._make_bar(alpha, 0.4, 'blue')
        beta_bar = self._make_bar(beta, 0.4, 'cyan')
        depth_bar = self._make_bar(depth / 100, 1.0, 'green')

        # Combine display
        display = (
            f"{state_display} "
            f"α:{alpha_bar} "
            f"β:{beta_bar} "
            f"depth:{depth_bar}"
        )

        print(display, end='', flush=True)

    def _make_bar(self, value: float, max_value: float, color: str, width: int = 10) -> str:
        """
        Create a text-based progress bar

        Args:
            value: Current value
            max_value: Maximum value
            color: Bar color
            width: Bar width in characters

        Returns:
            Formatted bar string
        """
        percentage = min(value / max_value, 1.0)
        filled = int(percentage * width)
        empty = width - filled

        bar = "█" * filled + "░" * empty
        bar = self._colorize(bar, color)

        return f"{bar} {value:.2f}"

    def show_session_start(self, duration: Optional[float] = None):
        """Display session start message"""
        if not self.enabled:
            return

        print("\n" + "=" * 70)
        print(self._colorize("🧘 MEDITATION SESSION STARTED", 'bold'))
        if duration:
            print(f"Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")
        print("=" * 70 + "\n")

        print("State Guide:")
        print(f"  {self._colorize('[alpha+]', 'green')} = Deep relaxation ✓")
        print(f"  {self._colorize('[alpha-]', 'red')} = Need more relaxation")
        print(f"  {self._colorize('[beta+]', 'green')} = Calm focus ✓")
        print(f"  {self._colorize('[beta-]', 'red')} = Too much mental activity")
        print(f"  {self._colorize('[a+b+]', 'magenta')} = Perfect state ⭐")
        print(f"  {self._colorize('[drowsy]', 'yellow')} = Stay alert!")
        print("\n")

    def show_session_end(self):
        """Display session end message"""
        if not self.enabled:
            return

        print("\n\n" + "=" * 70)
        print(self._colorize("✓ MEDITATION SESSION COMPLETE", 'bold'))
        print("=" * 70 + "\n")

    def clear_line(self):
        """Clear current line"""
        print('\r' + ' ' * 100 + '\r', end='', flush=True)


class FeedbackController:
    """
    Unified feedback controller for audio and visual cues

    Coordinates all feedback modalities
    """

    def __init__(
        self,
        audio_enabled: bool = True,
        visual_enabled: bool = True,
        audio_volume: float = 0.5,
        visual_colors: bool = True
    ):
        """
        Initialize feedback controller

        Args:
            audio_enabled: Enable audio cues
            visual_enabled: Enable visual display
            audio_volume: Audio volume (0.0 to 1.0)
            visual_colors: Use colors in terminal
        """
        self.audio = AudioCue(enabled=audio_enabled, volume=audio_volume)
        self.visual = VisualCue(enabled=visual_enabled, use_colors=visual_colors)

        self.last_state = None
        self.state_change_count = 0

    def provide_feedback(self, state_name: str, alpha: float, beta: float, depth: float):
        """
        Provide multimodal feedback

        Args:
            state_name: Current state name
            alpha: Alpha power
            beta: Beta power
            depth: Meditation depth
        """
        # Visual feedback (continuous)
        self.visual.show_state(state_name, alpha, beta, depth)

        # Audio feedback (only on state change)
        if state_name != self.last_state:
            self.audio.play_state_cue(state_name)
            self.last_state = state_name
            self.state_change_count += 1

    def session_start(self, duration: Optional[float] = None):
        """Signal session start"""
        self.visual.show_session_start(duration)
        self.last_state = None
        self.state_change_count = 0

    def session_end(self):
        """Signal session end"""
        self.visual.show_session_end()
        print(f"State changes during session: {self.state_change_count}\n")


# Convenience function for use in scripts
def create_feedback_controller(
    audio: bool = True,
    visual: bool = True,
    volume: float = 0.5
) -> FeedbackController:
    """
    Create a feedback controller with sensible defaults

    Args:
        audio: Enable audio feedback
        visual: Enable visual feedback
        volume: Audio volume

    Returns:
        Configured FeedbackController
    """
    return FeedbackController(
        audio_enabled=audio,
        visual_enabled=visual,
        audio_volume=volume
    )
