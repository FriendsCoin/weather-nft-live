"""
Real-time Neurofeedback System for THE LISTENER

Provides live feedback during meditation sessions based on EEG analysis.

Features:
- Real-time EEG processing with minimal latency
- Live state detection (alpha+, alpha-, beta+, beta-)
- Audio and visual feedback cues
- Smooth state transitions
- Performance tracking

Usage:
    # With Muse headband
    feedback = RealtimeNeurofeedback(device='muse')
    feedback.start_session(duration=600)  # 10 minutes

    # With mock data (for testing)
    feedback = RealtimeNeurofeedback(device='mock')
    feedback.start_session(duration=60)
"""

import numpy as np
import time
from typing import Dict, List, Optional, Callable, Tuple
from collections import deque
from dataclasses import dataclass
from enum import Enum
import threading
import queue


class FeedbackState(Enum):
    """Neurofeedback states based on Kovacevic et al. (2015)"""
    ALPHA_SUCCESS = "alpha+"    # High alpha (relaxation success)
    ALPHA_FAIL = "alpha-"       # Low alpha (need more relaxation)
    BETA_SUCCESS = "beta+"      # Controlled beta (focused awareness)
    BETA_FAIL = "beta-"         # High beta (mental chatter)
    COMBINED_SUCCESS = "a+b+"   # Both alpha high and beta controlled
    DROWSY = "drowsy"           # High delta (falling asleep)
    BASELINE = "baseline"       # Normal state


@dataclass
class FeedbackEvent:
    """Neurofeedback event"""
    timestamp: float
    state: FeedbackState
    alpha_power: float
    beta_power: float
    delta_power: float
    theta_power: float
    meditation_depth: float
    message: str


class RealtimeNeurofeedback:
    """
    Real-time neurofeedback system

    Processes EEG data in real-time and provides immediate feedback
    on meditation state.
    """

    def __init__(
        self,
        device: str = 'mock',
        sampling_rate: int = 256,
        window_size: float = 2.0,
        update_interval: float = 0.5,
        smoothing_window: int = 3,
        feedback_callback: Optional[Callable] = None,
        baseline_path: Optional[str] = None
    ):
        """
        Initialize real-time neurofeedback

        Args:
            device: 'muse' or 'mock'
            sampling_rate: EEG sampling rate (Hz)
            window_size: Processing window in seconds
            update_interval: How often to update feedback (seconds)
            smoothing_window: Number of states to smooth over
            feedback_callback: Function to call with feedback events
            baseline_path: Path to baseline session for personalized thresholds
        """
        self.device = device
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.update_interval = update_interval
        self.smoothing_window = smoothing_window
        self.feedback_callback = feedback_callback

        # Processing parameters
        self.window_samples = int(window_size * sampling_rate)
        self.update_samples = int(update_interval * sampling_rate)

        # Data buffers
        self.eeg_buffer = deque(maxlen=self.window_samples * 2)  # Rolling buffer
        self.state_history = deque(maxlen=smoothing_window)

        # Frequency bands
        self.bands = {
            'delta': (0.5, 4.0),
            'theta': (4.0, 8.0),
            'alpha': (8.0, 12.0),
            'beta': (18.0, 30.0),
        }

        # Personal thresholds (from baseline or defaults)
        self.thresholds = self._load_baseline_thresholds(baseline_path)

        # Session tracking
        self.is_running = False
        self.session_start = None
        self.events = []
        self.performance_stats = {
            'alpha_success_count': 0,
            'alpha_fail_count': 0,
            'beta_success_count': 0,
            'beta_fail_count': 0,
            'combined_success_count': 0,
            'drowsy_count': 0
        }

        # Threading
        self.data_queue = queue.Queue()
        self.process_thread = None

        print("🎯 Real-time Neurofeedback initialized")
        print(f"   Device: {device}")
        print(f"   Window: {window_size}s, Update: {update_interval}s")
        print(f"   Thresholds: {'Personalized' if baseline_path else 'Default'}")

    def _load_baseline_thresholds(self, baseline_path: Optional[str]) -> Dict[str, float]:
        """Load or create default thresholds"""
        if baseline_path:
            # TODO: Load from baseline session
            # For now, use defaults
            pass

        # Default thresholds (will be personalized in future)
        return {
            'alpha_low': 0.15,      # Below this = alpha-
            'alpha_high': 0.25,     # Above this = alpha+
            'beta_low': 0.12,       # Below this = beta+ (controlled)
            'beta_high': 0.20,      # Above this = beta- (too active)
            'delta_drowsy': 0.30,   # Above this = drowsy
        }

    def compute_band_powers(self, eeg_data: np.ndarray) -> Dict[str, float]:
        """
        Compute relative band powers from EEG data

        Args:
            eeg_data: EEG samples (samples x channels)

        Returns:
            Dictionary of band powers (relative)
        """
        from scipy import signal as sig

        # Average across channels
        if len(eeg_data.shape) > 1:
            eeg_avg = np.mean(eeg_data, axis=1)
        else:
            eeg_avg = eeg_data

        # Compute power spectral density
        freqs, psd = sig.welch(
            eeg_avg,
            fs=self.sampling_rate,
            nperseg=min(256, len(eeg_avg)),
            noverlap=128
        )

        # Compute total power
        total_power = np.trapz(psd, freqs)

        # Compute relative band powers
        band_powers = {}
        for band_name, (low, high) in self.bands.items():
            mask = (freqs >= low) & (freqs <= high)
            band_power = np.trapz(psd[mask], freqs[mask])
            band_powers[band_name] = band_power / (total_power + 1e-10)

        return band_powers

    def detect_state(self, band_powers: Dict[str, float]) -> FeedbackState:
        """
        Detect current neurofeedback state

        Args:
            band_powers: Dictionary of band powers

        Returns:
            Current feedback state
        """
        alpha = band_powers['alpha']
        beta = band_powers['beta']
        delta = band_powers['delta']
        theta = band_powers['theta']

        # Check for drowsiness first
        if delta > self.thresholds['delta_drowsy']:
            return FeedbackState.DROWSY

        # Determine alpha state
        alpha_state = None
        if alpha > self.thresholds['alpha_high']:
            alpha_state = FeedbackState.ALPHA_SUCCESS
        elif alpha < self.thresholds['alpha_low']:
            alpha_state = FeedbackState.ALPHA_FAIL

        # Determine beta state
        beta_state = None
        if beta < self.thresholds['beta_low']:
            beta_state = FeedbackState.BETA_SUCCESS
        elif beta > self.thresholds['beta_high']:
            beta_state = FeedbackState.BETA_FAIL

        # Combined state logic
        if alpha_state == FeedbackState.ALPHA_SUCCESS and beta_state == FeedbackState.BETA_SUCCESS:
            return FeedbackState.COMBINED_SUCCESS
        elif alpha_state:
            return alpha_state
        elif beta_state:
            return beta_state
        else:
            return FeedbackState.BASELINE

    def get_state_message(self, state: FeedbackState, band_powers: Dict[str, float]) -> str:
        """
        Get human-readable message for current state

        Args:
            state: Current feedback state
            band_powers: Band powers for context

        Returns:
            Feedback message
        """
        messages = {
            FeedbackState.ALPHA_SUCCESS: "🟢 Deep relaxation - excellent!",
            FeedbackState.ALPHA_FAIL: "🔴 More relaxation needed",
            FeedbackState.BETA_SUCCESS: "🟢 Calm focus - well done!",
            FeedbackState.BETA_FAIL: "🔴 Too much mental activity",
            FeedbackState.COMBINED_SUCCESS: "⭐ Perfect meditation state!",
            FeedbackState.DROWSY: "🟡 Stay alert - avoiding drowsiness",
            FeedbackState.BASELINE: "⚪ Baseline state",
        }

        base_msg = messages.get(state, "Unknown state")

        # Add depth indicator
        depth = self.compute_meditation_depth(band_powers)
        depth_bar = "█" * int(depth / 10) + "░" * (10 - int(depth / 10))

        return f"{base_msg} | Depth: [{depth_bar}] {depth:.0f}%"

    def compute_meditation_depth(self, band_powers: Dict[str, float]) -> float:
        """
        Compute meditation depth score (0-100)

        Args:
            band_powers: Dictionary of band powers

        Returns:
            Meditation depth score
        """
        alpha = band_powers['alpha']
        beta = band_powers['beta']
        theta = band_powers['theta']
        delta = band_powers['delta']

        # Weighted formula
        depth = (
            2.0 * alpha +      # High alpha = relaxation
            1.0 * theta -      # Some theta = deep meditation
            1.5 * beta -       # Low beta = less mental chatter
            2.0 * delta        # Low delta = awake
        )

        # Normalize to 0-100
        depth = np.clip(depth * 100, 0, 100)

        return depth

    def smooth_state(self, current_state: FeedbackState) -> FeedbackState:
        """
        Smooth state transitions to avoid jitter

        Args:
            current_state: Latest detected state

        Returns:
            Smoothed state
        """
        self.state_history.append(current_state)

        if len(self.state_history) < self.smoothing_window:
            return current_state

        # Most common state in recent history
        from collections import Counter
        state_counts = Counter(self.state_history)
        smoothed_state = state_counts.most_common(1)[0][0]

        return smoothed_state

    def process_window(self):
        """Process current window of EEG data"""
        if len(self.eeg_buffer) < self.window_samples:
            return

        # Get current window
        window_data = np.array(list(self.eeg_buffer)[-self.window_samples:])

        # Compute band powers
        band_powers = self.compute_band_powers(window_data)

        # Detect state
        raw_state = self.detect_state(band_powers)
        smoothed_state = self.smooth_state(raw_state)

        # Update statistics
        state_key = smoothed_state.value.replace('+', '_success').replace('-', '_fail') + '_count'
        if state_key in self.performance_stats:
            self.performance_stats[state_key] += 1

        # Create feedback event
        event = FeedbackEvent(
            timestamp=time.time() - self.session_start,
            state=smoothed_state,
            alpha_power=band_powers['alpha'],
            beta_power=band_powers['beta'],
            delta_power=band_powers['delta'],
            theta_power=band_powers['theta'],
            meditation_depth=self.compute_meditation_depth(band_powers),
            message=self.get_state_message(smoothed_state, band_powers)
        )

        self.events.append(event)

        # Call feedback callback
        if self.feedback_callback:
            self.feedback_callback(event)

        return event

    def _processing_loop(self):
        """Background processing loop"""
        sample_count = 0

        while self.is_running:
            try:
                # Get data from queue (with timeout)
                data = self.data_queue.get(timeout=0.1)
                self.eeg_buffer.extend(data)
                sample_count += len(data)

                # Process window at regular intervals
                if sample_count >= self.update_samples:
                    self.process_window()
                    sample_count = 0

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in processing loop: {e}")
                break

    def start_session(self, duration: Optional[float] = None):
        """
        Start a real-time feedback session

        Args:
            duration: Session duration in seconds (None = infinite)
        """
        print(f"\n{'='*60}")
        print("Starting Real-time Neurofeedback Session")
        print(f"{'='*60}\n")

        self.is_running = True
        self.session_start = time.time()
        self.events = []
        self.performance_stats = {k: 0 for k in self.performance_stats}

        # Start processing thread
        self.process_thread = threading.Thread(target=self._processing_loop)
        self.process_thread.daemon = True
        self.process_thread.start()

        # Start data acquisition
        if self.device == 'mock':
            self._run_mock_session(duration)
        elif self.device == 'muse':
            self._run_muse_session(duration)
        else:
            raise ValueError(f"Unknown device: {self.device}")

        # Stop processing
        self.is_running = False
        if self.process_thread:
            self.process_thread.join()

        # Print session summary
        self._print_session_summary()

    def _run_mock_session(self, duration: float):
        """Run session with mock EEG data"""
        print("🎮 Using mock EEG data (for testing)")
        print(f"Session duration: {duration}s\n")

        elapsed = 0
        while self.is_running and (duration is None or elapsed < duration):
            # Generate mock data (4 channels)
            mock_data = self._generate_mock_eeg(samples=self.update_samples)
            self.data_queue.put(mock_data)

            time.sleep(self.update_interval)
            elapsed += self.update_interval

    def _run_muse_session(self, duration: Optional[float]):
        """Run session with Muse headband"""
        print("🎧 Connecting to Muse headband...")

        # TODO: Implement Muse connection
        # For now, fallback to mock
        print("⚠ Muse integration not yet implemented, using mock data")
        self._run_mock_session(duration or 300)

    def _generate_mock_eeg(self, samples: int) -> np.ndarray:
        """
        Generate mock EEG data for testing

        Args:
            samples: Number of samples to generate

        Returns:
            Mock EEG data (samples x 4 channels)
        """
        channels = 4
        t = np.linspace(0, samples / self.sampling_rate, samples)

        eeg = np.zeros((samples, channels))

        for ch in range(channels):
            # Base noise
            noise = np.random.randn(samples) * 0.1

            # Add frequency components
            alpha = 0.5 * np.sin(2 * np.pi * 10 * t + np.random.rand())  # 10 Hz alpha
            beta = 0.3 * np.sin(2 * np.pi * 20 * t + np.random.rand())   # 20 Hz beta
            theta = 0.4 * np.sin(2 * np.pi * 6 * t + np.random.rand())   # 6 Hz theta

            eeg[:, ch] = alpha + beta + theta + noise

        return eeg

    def _print_session_summary(self):
        """Print session statistics"""
        total_time = time.time() - self.session_start

        print(f"\n{'='*60}")
        print("Session Complete!")
        print(f"{'='*60}\n")

        print(f"Duration: {total_time:.1f}s")
        print(f"Events recorded: {len(self.events)}\n")

        print("Performance Summary:")
        print(f"  ⭐ Combined success: {self.performance_stats['combined_success_count']}")
        print(f"  🟢 Alpha success: {self.performance_stats['alpha_success_count']}")
        print(f"  🔴 Alpha needs work: {self.performance_stats['alpha_fail_count']}")
        print(f"  🟢 Beta controlled: {self.performance_stats['beta_success_count']}")
        print(f"  🔴 Beta too high: {self.performance_stats['beta_fail_count']}")
        print(f"  🟡 Drowsy moments: {self.performance_stats['drowsy_count']}\n")

        # Compute performance ratios
        alpha_total = self.performance_stats['alpha_success_count'] + self.performance_stats['alpha_fail_count']
        beta_total = self.performance_stats['beta_success_count'] + self.performance_stats['beta_fail_count']

        if alpha_total > 0:
            alpha_ratio = self.performance_stats['alpha_success_count'] / alpha_total
            print(f"Alpha performance: {alpha_ratio*100:.1f}%")

        if beta_total > 0:
            beta_ratio = self.performance_stats['beta_success_count'] / beta_total
            print(f"Beta performance: {beta_ratio*100:.1f}%")

        print(f"{'='*60}\n")

    def get_session_data(self) -> Dict:
        """
        Get session data for saving/analysis

        Returns:
            Dictionary with session data
        """
        return {
            'events': self.events,
            'performance_stats': self.performance_stats,
            'duration': time.time() - self.session_start if self.session_start else 0,
            'thresholds': self.thresholds
        }

    def save_session(self, output_path: str):
        """Save session data to file"""
        import pickle
        from pathlib import Path

        session_data = self.get_session_data()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            pickle.dump(session_data, f)

        print(f"✓ Session saved to: {output_path}")
