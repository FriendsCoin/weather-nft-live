"""
Real-Time Neurofeedback for THE LISTENER

Processes live EEG stream and provides real-time feedback
on meditation depth, alpha performance, and state quality.

For live performance, museum exhibition, and personal practice.
"""

import numpy as np
from collections import deque
from typing import Dict, Optional, Callable, List
import time
from datetime import datetime
import mne
from scipy import signal as sp_signal

# Import EEG processing utilities
from .preprocessing import preprocess_eeg
from .feature_extraction import extract_features


class RealtimeFeedback:
    """
    Real-time EEG processing and neurofeedback.

    Processes live EEG stream with rolling window,
    extracts features, and provides instant feedback
    on meditation state.

    Usage:
        feedback = RealtimeFeedback(
            window_size=5.0,  # 5-second rolling window
            update_rate=0.5   # Update every 0.5 seconds
        )

        # In LSL callback
        def on_eeg_sample(timestamp, sample):
            feedback.add_sample(timestamp, sample)

        # Get current state
        state = feedback.get_current_state()
        print(f"Depth: {state['depth']:.1f}/100")
        print(f"Alpha: {state['alpha_performance']:.2f}")
    """

    def __init__(
        self,
        window_size: float = 5.0,
        update_rate: float = 0.5,
        sfreq: float = 256.0,
        channels: List[str] = ['TP9', 'AF7', 'AF8', 'TP10'],
        reference_data: Optional[Dict] = None
    ):
        """
        Initialize real-time feedback system.

        Args:
            window_size: Rolling window size in seconds
            update_rate: Update interval in seconds
            sfreq: Sampling frequency (Hz)
            channels: EEG channel names
            reference_data: Personal thresholds from previous sessions
        """
        self.window_size = window_size
        self.update_rate = update_rate
        self.sfreq = sfreq
        self.channels = channels
        self.n_channels = len(channels)

        # Calculate buffer sizes
        self.window_samples = int(window_size * sfreq)
        self.update_samples = int(update_rate * sfreq)

        # Initialize buffers (deque for efficient rolling window)
        self.timestamp_buffer = deque(maxlen=self.window_samples)
        self.eeg_buffer = deque(maxlen=self.window_samples)

        # State tracking
        self.current_state = None
        self.last_update_time = 0
        self.sample_count = 0

        # Personal thresholds (from training data)
        self.thresholds = reference_data or self._default_thresholds()

        # State history for smoothing
        self.depth_history = deque(maxlen=10)
        self.alpha_history = deque(maxlen=10)

        # Callbacks
        self.state_callbacks = []

        print(f"🔴 Real-time feedback initialized")
        print(f"   Window: {window_size}s ({self.window_samples} samples)")
        print(f"   Update rate: {update_rate}s")
        print(f"   Channels: {', '.join(channels)}")

    def _default_thresholds(self) -> Dict:
        """Default thresholds (updated by calibration)."""
        return {
            'alpha_upper': 0.3,  # Upper threshold for alpha+
            'alpha_lower': -0.3,  # Lower threshold for alpha-
            'beta_upper': 0.3,
            'beta_lower': -0.3,
            'theta_baseline': 0.0,
            'depth_threshold': 30.0  # Minimum depth for "meditation state"
        }

    def add_sample(self, timestamp: float, sample: np.ndarray):
        """
        Add new EEG sample to buffer.

        Args:
            timestamp: Sample timestamp (seconds)
            sample: EEG data [n_channels]
        """
        self.timestamp_buffer.append(timestamp)
        self.eeg_buffer.append(sample)
        self.sample_count += 1

        # Check if it's time to update
        current_time = time.time()
        if (current_time - self.last_update_time) >= self.update_rate:
            if len(self.eeg_buffer) >= self.window_samples:
                self._update_state()
                self.last_update_time = current_time

    def _update_state(self):
        """
        Compute current meditation state from buffer.

        Called automatically when update interval is reached.
        """
        # Convert buffer to numpy array
        eeg_data = np.array(self.eeg_buffer).T  # [n_channels, n_samples]

        # Create MNE Raw object for processing
        info = mne.create_info(
            ch_names=self.channels,
            sfreq=self.sfreq,
            ch_types='eeg'
        )
        raw = mne.io.RawArray(eeg_data, info, verbose=False)

        try:
            # Preprocess (bandpass filter, artifact removal)
            raw_clean = preprocess_eeg(
                raw,
                l_freq=1.0,
                h_freq=50.0,
                notch_freq=60.0
            )

            # Extract features
            features = extract_features(raw_clean)

            # Compute meditation metrics
            state = self._compute_meditation_state(features)

            # Smooth with history
            state = self._smooth_state(state)

            # Update current state
            self.current_state = state

            # Trigger callbacks
            for callback in self.state_callbacks:
                callback(state)

        except Exception as e:
            print(f"⚠️  Error updating state: {e}")

    def _compute_meditation_state(self, features: Dict) -> Dict:
        """
        Compute meditation state from features.

        Args:
            features: Feature dictionary from extract_features()

        Returns:
            State dict with meditation metrics
        """
        # Get band powers (averaged across channels)
        alpha_power = features.get('alpha_mean', 0)
        beta_power = features.get('beta_mean', 0)
        theta_power = features.get('theta_mean', 0)
        delta_power = features.get('delta_mean', 0)
        gamma_power = features.get('gamma_mean', 0)

        # Compute relative powers
        total_power = alpha_power + beta_power + theta_power + delta_power + gamma_power
        if total_power > 0:
            alpha_rel = alpha_power / total_power
            beta_rel = beta_power / total_power
            theta_rel = theta_power / total_power
        else:
            alpha_rel = beta_rel = theta_rel = 0

        # Alpha/beta ratio (relaxation indicator)
        alpha_beta_ratio = alpha_power / (beta_power + 1e-6)

        # Meditation depth (based on alpha, theta, low beta)
        depth = 100 * (
            0.4 * alpha_rel +
            0.3 * theta_rel +
            0.3 * (1.0 - beta_rel)
        )
        depth = np.clip(depth, 0, 100)

        # Alpha performance (relative to personal thresholds)
        alpha_z = (alpha_rel - 0.2) / 0.1  # Z-score approximation
        if alpha_z > self.thresholds['alpha_upper']:
            alpha_state = 'alpha+'
            alpha_performance = 1.0 + (alpha_z - self.thresholds['alpha_upper'])
        elif alpha_z < self.thresholds['alpha_lower']:
            alpha_state = 'alpha-'
            alpha_performance = alpha_z  # Negative
        else:
            alpha_state = 'alpha_neutral'
            alpha_performance = alpha_z

        # Beta performance (inverse - lower is better for meditation)
        beta_z = (beta_rel - 0.2) / 0.1
        if beta_z > self.thresholds['beta_upper']:
            beta_state = 'beta+'  # High beta = active mind
            beta_performance = -(beta_z - self.thresholds['beta_upper'])
        elif beta_z < self.thresholds['beta_lower']:
            beta_state = 'beta-'  # Low beta = calm
            beta_performance = 1.0 - beta_z
        else:
            beta_state = 'beta_neutral'
            beta_performance = 0.5

        # Quality score (0-100)
        quality = 100 * (
            0.4 * (alpha_performance / 2.0 + 0.5) +  # Normalize to 0-1
            0.3 * (beta_performance / 2.0 + 0.5) +
            0.3 * (depth / 100)
        )
        quality = np.clip(quality, 0, 100)

        # State message (for visual feedback)
        if depth > self.thresholds['depth_threshold']:
            if alpha_state == 'alpha+':
                state_message = "🌟 Deep relaxation"
                state_level = 4
            elif beta_state == 'beta-':
                state_message = "✨ Calm and focused"
                state_level = 3
            else:
                state_message = "😌 Meditating"
                state_level = 2
        else:
            if beta_state == 'beta+':
                state_message = "🤔 Active mind"
                state_level = 1
            else:
                state_message = "🌱 Settling in"
                state_level = 1

        return {
            'timestamp': datetime.now().isoformat(),
            'depth': depth,
            'quality': quality,
            'alpha_power': alpha_power,
            'beta_power': beta_power,
            'theta_power': theta_power,
            'alpha_rel': alpha_rel,
            'beta_rel': beta_rel,
            'theta_rel': theta_rel,
            'alpha_beta_ratio': alpha_beta_ratio,
            'alpha_state': alpha_state,
            'beta_state': beta_state,
            'alpha_performance': alpha_performance,
            'beta_performance': beta_performance,
            'state_message': state_message,
            'state_level': state_level,
            'raw_features': features
        }

    def _smooth_state(self, state: Dict) -> Dict:
        """
        Smooth state with exponential moving average.

        Prevents jittery visual feedback.

        Args:
            state: Current state dict

        Returns:
            Smoothed state dict
        """
        # Add to history
        self.depth_history.append(state['depth'])
        self.alpha_history.append(state['alpha_performance'])

        # Compute smoothed values (EMA)
        if len(self.depth_history) > 1:
            state['depth_smooth'] = np.mean(list(self.depth_history))
            state['alpha_smooth'] = np.mean(list(self.alpha_history))
        else:
            state['depth_smooth'] = state['depth']
            state['alpha_smooth'] = state['alpha_performance']

        return state

    def get_current_state(self) -> Optional[Dict]:
        """
        Get current meditation state.

        Returns:
            State dict or None if not enough data yet
        """
        return self.current_state

    def register_callback(self, callback: Callable[[Dict], None]):
        """
        Register callback for state updates.

        Args:
            callback: Function that receives state dict
        """
        self.state_callbacks.append(callback)

    def calibrate(self, baseline_session_features: Dict):
        """
        Calibrate personal thresholds from baseline session.

        Args:
            baseline_session_features: Features from a baseline session
        """
        # Extract alpha/beta timeseries
        alpha_ts = baseline_session_features.get('alpha_timeseries', [])
        beta_ts = baseline_session_features.get('beta_timeseries', [])

        if alpha_ts and beta_ts:
            # Compute percentile-based thresholds
            self.thresholds['alpha_upper'] = np.percentile(alpha_ts, 75)
            self.thresholds['alpha_lower'] = np.percentile(alpha_ts, 25)
            self.thresholds['beta_upper'] = np.percentile(beta_ts, 75)
            self.thresholds['beta_lower'] = np.percentile(beta_ts, 25)

            print(f"✅ Calibration complete")
            print(f"   Alpha thresholds: {self.thresholds['alpha_lower']:.2f} - {self.thresholds['alpha_upper']:.2f}")
            print(f"   Beta thresholds: {self.thresholds['beta_lower']:.2f} - {self.thresholds['beta_upper']:.2f}")
        else:
            print("⚠️  Calibration failed: no timeseries data")

    def reset(self):
        """Reset buffers and state."""
        self.timestamp_buffer.clear()
        self.eeg_buffer.clear()
        self.depth_history.clear()
        self.alpha_history.clear()
        self.current_state = None
        self.sample_count = 0
        print("🔄 Real-time feedback reset")

    def get_statistics(self) -> Dict:
        """
        Get session statistics.

        Returns:
            Dict with running statistics
        """
        if not self.depth_history:
            return {}

        return {
            'samples_processed': self.sample_count,
            'mean_depth': np.mean(list(self.depth_history)),
            'max_depth': np.max(list(self.depth_history)),
            'mean_alpha': np.mean(list(self.alpha_history)),
            'duration_seconds': self.sample_count / self.sfreq
        }


# Visual feedback helpers
class VisualFeedback:
    """
    Generate visual feedback parameters from meditation state.

    For use with visualization systems (TouchDesigner, etc.)
    """

    @staticmethod
    def circle_size(depth: float, min_size: float = 50, max_size: float = 500) -> float:
        """
        Map meditation depth to circle size.

        Args:
            depth: Meditation depth (0-100)
            min_size: Minimum circle radius
            max_size: Maximum circle radius

        Returns:
            Circle radius
        """
        return min_size + (depth / 100.0) * (max_size - min_size)

    @staticmethod
    def color_hue(alpha_performance: float) -> float:
        """
        Map alpha performance to color hue.

        Args:
            alpha_performance: Alpha performance (-2 to +2)

        Returns:
            Hue value (0-360 degrees)
        """
        # Map to blue (calm) → green (balanced) → yellow (active)
        # -2 → 240° (blue), 0 → 180° (cyan/green), +2 → 60° (yellow)
        normalized = (alpha_performance + 2) / 4.0  # 0 to 1
        hue = 240 - (normalized * 180)  # 240 to 60
        return hue

    @staticmethod
    def particle_density(quality: float, max_particles: int = 100) -> int:
        """
        Map quality score to particle density.

        Args:
            quality: Quality score (0-100)
            max_particles: Maximum number of particles

        Returns:
            Number of particles to display
        """
        return int((quality / 100.0) * max_particles)

    @staticmethod
    def glow_intensity(state_level: int) -> float:
        """
        Map state level to glow intensity.

        Args:
            state_level: State level (1-4)

        Returns:
            Glow intensity (0-1)
        """
        return state_level / 4.0

    @staticmethod
    def get_visual_params(state: Dict) -> Dict:
        """
        Convert state to visual parameters.

        Args:
            state: State dict from RealtimeFeedback

        Returns:
            Dict of visual parameters
        """
        return {
            'circle_size': VisualFeedback.circle_size(state['depth_smooth']),
            'color_hue': VisualFeedback.color_hue(state['alpha_smooth']),
            'particle_count': VisualFeedback.particle_density(state['quality']),
            'glow_intensity': VisualFeedback.glow_intensity(state['state_level']),
            'depth_percent': state['depth_smooth'],
            'quality_percent': state['quality'],
            'state_message': state['state_message']
        }
