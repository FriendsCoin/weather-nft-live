"""
Enhanced EEG Analysis for THE LISTENER

Improvements based on neurofeedback research:
- Relative spectral power (RSP) instead of absolute
- Meditation depth scoring (alpha/beta ratios)
- Learning curve tracking across sessions
- State transition detection
- Temporal dynamics analysis

References:
- Kovacevic et al. (2015) "My Virtual Dream" neurofeedback study
- Shows ~1 minute learning speed for brain state modulation
- Alpha (8-12 Hz) = relaxation, Beta (18-30 Hz) = concentration
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scipy import signal, stats


class MeditationAnalyzer:
    """
    Advanced meditation state analysis.

    Based on neurofeedback research showing:
    - Fast learning (~1 min to modulate states)
    - Alpha power = relaxation/meditation
    - Beta power = concentration/mental activity
    - Relative power more informative than absolute

    Usage:
        analyzer = MeditationAnalyzer()

        # Analyze single session
        metrics = analyzer.analyze_session(features_df)
        print(f"Meditation depth: {metrics['depth_score']:.2f}")

        # Track learning across sessions
        learning = analyzer.track_learning_curve(session_files)
        analyzer.plot_learning_progression(learning)
    """

    def __init__(self, sampling_rate: int = 256):
        """
        Initialize analyzer.

        Args:
            sampling_rate: EEG sampling rate (Hz)
        """
        self.sampling_rate = sampling_rate

        # Frequency bands (refined based on research)
        self.bands = {
            'delta': (0.5, 4.0),
            'theta': (4.0, 8.0),
            'alpha': (8.0, 12.0),    # Meditation marker
            'beta': (18.0, 30.0),    # Concentration marker (shifted from 13-30)
            'low_beta': (13.0, 18.0),  # Separate low beta
            'gamma': (30.0, 50.0)
        }

        print("🧘 Meditation Analyzer initialized")
        print(f"   Bands: {list(self.bands.keys())}")

    def compute_relative_spectral_power(
        self,
        psd: np.ndarray,
        freqs: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute Relative Spectral Power (RSP) for each band.

        RSP = band_power / total_power
        More robust than absolute power across sessions/individuals.

        Args:
            psd: Power spectral density
            freqs: Frequency array

        Returns:
            Dict of band_name: RSP value
        """
        # Total power across all frequencies
        total_power = np.trapz(psd, freqs)

        rsp = {}
        for band_name, (low, high) in self.bands.items():
            # Find frequencies in this band
            band_mask = (freqs >= low) & (freqs <= high)

            # Band power
            band_power = np.trapz(psd[band_mask], freqs[band_mask])

            # Relative power
            rsp[band_name] = band_power / (total_power + 1e-10)

        return rsp

    def compute_meditation_depth(
        self,
        alpha_power: float,
        beta_power: float,
        theta_power: float,
        delta_power: float
    ) -> float:
        """
        Compute meditation depth score (0-100).

        Based on research showing:
        - High alpha = relaxed awareness (meditation)
        - Low beta = reduced mental chatter
        - Moderate theta = deep meditation (not drowsiness)
        - Low delta = awake (not sleep)

        Formula:
        depth = (alpha_weight * alpha + theta_weight * theta
                - beta_weight * beta - delta_weight * delta) * 100

        Args:
            alpha_power: Alpha relative power
            beta_power: Beta relative power
            theta_power: Theta relative power
            delta_power: Delta relative power

        Returns:
            Meditation depth score (0-100, higher = deeper)
        """
        # Weights based on meditation markers
        alpha_weight = 0.5    # Primary meditation marker
        theta_weight = 0.3    # Deep meditation
        beta_weight = -0.3    # Mental activity (subtract)
        delta_weight = -0.2   # Drowsiness (subtract)

        # Compute weighted sum
        depth = (
            alpha_weight * alpha_power +
            theta_weight * theta_power +
            beta_weight * beta_power +
            delta_weight * delta_power
        )

        # Normalize to 0-100 scale
        # (assuming RSP values are 0-1, depth will be roughly -0.5 to 0.8)
        depth_normalized = (depth + 0.5) / 1.3 * 100
        depth_normalized = np.clip(depth_normalized, 0, 100)

        return depth_normalized

    def analyze_session(
        self,
        features_df: pd.DataFrame,
        channels: Optional[List[str]] = None
    ) -> Dict:
        """
        Comprehensive session analysis.

        Returns metrics:
        - Meditation depth (0-100)
        - Alpha/beta ratio (relaxation vs concentration)
        - State stability (consistency across time)
        - Transition count (state changes)
        - Quality score (overall meditation quality)

        Args:
            features_df: Feature DataFrame from feature extraction
            channels: Channels to analyze (default: all)

        Returns:
            Dict with analysis results
        """
        if channels is None:
            channels = ["TP9", "AF7", "AF8", "TP10"]

        print(f"\n🔍 Analyzing session...")
        print(f"   Windows: {len(features_df)}")
        print(f"   Duration: {len(features_df) * 2:.0f} seconds")  # 2s per window (4s window, 50% overlap)

        # Extract relative band powers
        rsp_data = {band: [] for band in self.bands.keys()}

        for idx, row in features_df.iterrows():
            # Average across channels for each band
            for band in self.bands.keys():
                band_cols = [c for c in features_df.columns if band in c and any(ch in c for ch in channels)]
                if band_cols:
                    # Convert from log power to linear for RSP calculation
                    powers = [10**row[c] for c in band_cols]
                    rsp_data[band].append(np.mean(powers))

        # Compute RSP per window
        rsps = []
        for i in range(len(features_df)):
            total = sum(rsp_data[band][i] for band in self.bands.keys())
            window_rsp = {
                band: rsp_data[band][i] / (total + 1e-10)
                for band in self.bands.keys()
            }
            rsps.append(window_rsp)

        # Convert to arrays for analysis
        alpha_arr = np.array([r['alpha'] for r in rsps])
        beta_arr = np.array([r['beta'] for r in rsps])
        theta_arr = np.array([r['theta'] for r in rsps])
        delta_arr = np.array([r['delta'] for r in rsps])

        # Compute depth per window
        depths = [
            self.compute_meditation_depth(
                rsps[i]['alpha'],
                rsps[i]['beta'],
                rsps[i]['theta'],
                rsps[i]['delta']
            )
            for i in range(len(rsps))
        ]

        # Session-level metrics
        metrics = {
            # Primary metrics
            'mean_depth': np.mean(depths),
            'max_depth': np.max(depths),
            'depth_std': np.std(depths),

            # Band powers (mean RSP)
            'mean_alpha_rsp': np.mean(alpha_arr),
            'mean_beta_rsp': np.mean(beta_arr),
            'mean_theta_rsp': np.mean(theta_arr),

            # Ratios
            'alpha_beta_ratio': np.mean(alpha_arr) / (np.mean(beta_arr) + 1e-10),
            'alpha_theta_ratio': np.mean(alpha_arr) / (np.mean(theta_arr) + 1e-10),

            # Stability
            'depth_stability': 1.0 / (np.std(depths) + 1.0),  # Higher = more stable

            # Temporal dynamics
            'num_transitions': self._count_state_transitions(depths, threshold=10),
            'learning_slope': self._compute_learning_slope(depths),

            # Quality score (composite)
            'quality_score': self._compute_quality_score(depths, alpha_arr, beta_arr),

            # Time series
            'depth_timeseries': depths,
            'alpha_timeseries': alpha_arr.tolist(),
            'beta_timeseries': beta_arr.tolist()
        }

        print(f"\n📊 Session Metrics:")
        print(f"   Meditation depth: {metrics['mean_depth']:.1f}/100")
        print(f"   Alpha/Beta ratio: {metrics['alpha_beta_ratio']:.2f}")
        print(f"   Stability: {metrics['depth_stability']:.2f}")
        print(f"   Quality score: {metrics['quality_score']:.1f}/100")

        return metrics

    def _count_state_transitions(self, depths: List[float], threshold: float = 10) -> int:
        """Count significant depth transitions."""
        transitions = 0
        for i in range(1, len(depths)):
            if abs(depths[i] - depths[i-1]) > threshold:
                transitions += 1
        return transitions

    def _compute_learning_slope(self, depths: List[float]) -> float:
        """
        Compute learning slope (depth increase over time).

        Positive = deepening meditation
        Negative = deteriorating attention
        """
        if len(depths) < 2:
            return 0.0

        x = np.arange(len(depths))
        slope, _ = np.polyfit(x, depths, 1)
        return slope

    def _compute_quality_score(
        self,
        depths: List[float],
        alpha: np.ndarray,
        beta: np.ndarray
    ) -> float:
        """
        Composite quality score (0-100).

        Factors:
        - Mean depth (50%)
        - Stability (25%)
        - Alpha dominance (15%)
        - Positive learning slope (10%)
        """
        mean_depth = np.mean(depths)
        stability = 1.0 / (np.std(depths) + 1.0)
        alpha_dominance = np.mean(alpha) / (np.mean(beta) + np.mean(alpha))
        slope = self._compute_learning_slope(depths)

        quality = (
            0.50 * mean_depth +
            0.25 * (stability * 20) +  # Normalize stability to ~0-100
            0.15 * (alpha_dominance * 100) +
            0.10 * (max(0, slope) * 10)  # Positive slope only
        )

        return np.clip(quality, 0, 100)

    def track_learning_curve(
        self,
        session_files: List[str],
        metric: str = "mean_depth"
    ) -> pd.DataFrame:
        """
        Track learning progression across multiple sessions.

        Args:
            session_files: List of feature file paths
            metric: Metric to track ('mean_depth', 'quality_score', etc.)

        Returns:
            DataFrame with session number and metric values
        """
        print(f"\n📈 Tracking learning curve across {len(session_files)} sessions...")

        learning_data = []

        for i, session_file in enumerate(sorted(session_files)):
            print(f"   Session {i+1}/{len(session_files)}...", end=" ")

            # Load features
            features_df = pd.read_hdf(session_file, key='features')

            # Analyze
            metrics = self.analyze_session(features_df)

            learning_data.append({
                'session_number': i + 1,
                'session_file': Path(session_file).name,
                metric: metrics[metric],
                'mean_depth': metrics['mean_depth'],
                'quality_score': metrics['quality_score'],
                'alpha_beta_ratio': metrics['alpha_beta_ratio'],
                'stability': metrics['depth_stability']
            })

            print(f"{metric}={metrics[metric]:.1f}")

        learning_df = pd.DataFrame(learning_data)

        # Compute overall learning trend
        slope, _ = np.polyfit(learning_df['session_number'], learning_df[metric], 1)

        print(f"\n✅ Learning analysis complete")
        print(f"   Overall trend: {'+' if slope > 0 else ''}{slope:.2f} {metric}/session")

        return learning_df

    def detect_state_transitions(
        self,
        depths: List[float],
        window_size: int = 10,
        threshold: float = 15
    ) -> List[Dict]:
        """
        Detect significant meditation state transitions.

        Args:
            depths: Depth timeseries
            window_size: Windows to compare
            threshold: Minimum depth change to count as transition

        Returns:
            List of transition events with timestamps and types
        """
        transitions = []

        for i in range(window_size, len(depths) - window_size):
            before = np.mean(depths[i-window_size:i])
            after = np.mean(depths[i:i+window_size])

            change = after - before

            if abs(change) > threshold:
                transition_type = "deepening" if change > 0 else "surfacing"
                transitions.append({
                    'time_window': i,
                    'time_seconds': i * 2,  # 2s per window
                    'type': transition_type,
                    'magnitude': abs(change),
                    'depth_before': before,
                    'depth_after': after
                })

        return transitions


# CLI interface
if __name__ == "__main__":
    import argparse
    from glob import glob

    parser = argparse.ArgumentParser(description="Analyze meditation sessions")
    parser.add_argument("--session", help="Single session feature file")
    parser.add_argument("--sessions-dir", help="Directory with multiple sessions")
    parser.add_argument("--output", help="Output analysis file")

    args = parser.parse_args()

    analyzer = MeditationAnalyzer()

    if args.session:
        # Single session analysis
        features_df = pd.read_hdf(args.session, key='features')
        metrics = analyzer.analyze_session(features_df)

        # Save results
        if args.output:
            import json
            with open(args.output, 'w') as f:
                # Remove timeseries for JSON serialization
                metrics_clean = {k: v for k, v in metrics.items() if not isinstance(v, list)}
                json.dump(metrics_clean, f, indent=2)
            print(f"\n💾 Analysis saved: {args.output}")

    elif args.sessions_dir:
        # Multi-session learning curve
        session_files = sorted(glob(f"{args.sessions_dir}/*.h5"))

        if not session_files:
            print(f"❌ No .h5 files found in {args.sessions_dir}")
        else:
            learning_df = analyzer.track_learning_curve(session_files)

            if args.output:
                learning_df.to_csv(args.output, index=False)
                print(f"💾 Learning curve saved: {args.output}")

    else:
        print("Usage: Provide --session or --sessions-dir")
