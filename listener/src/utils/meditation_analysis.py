"""
Enhanced EEG Analysis for THE LISTENER

Improvements based on neurofeedback research:
- Relative spectral power (RSP) instead of absolute
- Meditation depth scoring (alpha/beta ratios)
- Learning curve tracking across sessions
- State transition detection
- Temporal dynamics analysis
- Performance ratios (alpha+/alpha-, beta+/beta-)
- Dynamic personal thresholds (individualized targets)
- Baseline prediction of learning potential
- Delta reduction tracking during concentration
- Real-time state feedback messages

References:
- Kovacevic et al. (2015) "My Virtual Dream" neurofeedback study
  * ~1 minute learning speed for brain state modulation
  * Alpha (8-12 Hz) = relaxation marker
  * Beta (18-30 Hz) = concentration marker
  * Personalized thresholds: lower=0.9×mean, upper=1.1×(alpha) or 1.2×(beta)
  * Performance = (success states) / (failure states)
  * Baseline delta/beta predicts learning trajectory
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

    def __init__(self, sampling_rate: int = 256, baseline_session: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            sampling_rate: EEG sampling rate (Hz)
            baseline_session: Path to first session for personalized thresholds
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

        # Personal thresholds (set from baseline session)
        self.personal_thresholds = None
        self.baseline_metrics = None

        if baseline_session:
            self._compute_personal_thresholds(baseline_session)

        print("🧘 Meditation Analyzer initialized")
        print(f"   Bands: {list(self.bands.keys())}")
        if self.personal_thresholds:
            print(f"   ✓ Personal thresholds loaded from baseline")

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

        # Compute performance ratios (new from paper)
        performance = self.compute_performance_ratios(
            alpha_arr,
            beta_arr,
            use_personal_thresholds=self.personal_thresholds is not None
        )

        # Compute delta reduction (new from paper)
        delta_reduction = self.compute_delta_reduction(delta_arr)

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
            'mean_delta_rsp': np.mean(delta_arr),  # Added delta
            'mean_gamma_rsp': np.mean([r.get('gamma', 0.1) for r in rsps]),  # Added gamma

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

            # NEW: Performance ratios from Kovacevic et al. (2015)
            'alpha_performance': performance['alpha_performance'],
            'beta_performance': performance['beta_performance'],
            'alpha_plus_count': performance['alpha_plus'],
            'alpha_minus_count': performance['alpha_minus'],
            'beta_plus_count': performance['beta_plus'],
            'beta_minus_count': performance['beta_minus'],
            'alpha_success_pct': performance['alpha_success_pct'],
            'beta_success_pct': performance['beta_success_pct'],

            # NEW: Delta reduction tracking
            'delta_reduction': delta_reduction['delta_reduction'],
            'delta_reduction_pct': delta_reduction['delta_reduction_pct'],
            'delta_reduction_interpretation': delta_reduction['interpretation'],

            # Time series
            'depth_timeseries': depths,
            'alpha_timeseries': alpha_arr.tolist(),
            'beta_timeseries': beta_arr.tolist(),
            'delta_timeseries': delta_arr.tolist()
        }

        print(f"\n📊 Session Metrics:")
        print(f"   Meditation depth: {metrics['mean_depth']:.1f}/100")
        print(f"   Alpha/Beta ratio: {metrics['alpha_beta_ratio']:.2f}")
        print(f"   Alpha Performance (aP): {metrics['alpha_performance']:.2f} ({metrics['alpha_success_pct']:.0f}% success)")
        print(f"   Beta Performance (bP): {metrics['beta_performance']:.2f} ({metrics['beta_success_pct']:.0f}% success)")
        print(f"   Stability: {metrics['depth_stability']:.2f}")
        print(f"   Quality score: {metrics['quality_score']:.1f}/100")
        print(f"   Delta reduction: {metrics['delta_reduction_interpretation']}")

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

    def _compute_personal_thresholds(self, baseline_session: str):
        """
        Compute personalized thresholds from baseline (first) session.

        Based on Kovacevic et al. (2015):
        - Lower threshold = 0.9 × mean RSP
        - Upper threshold = 1.1 × mean RSP (alpha) or 1.2 × mean RSP (beta)

        Args:
            baseline_session: Path to baseline session features
        """
        print(f"\n📊 Computing personal thresholds from baseline...")

        # Load baseline
        baseline_df = pd.read_hdf(baseline_session, key='features')
        self.baseline_metrics = self.analyze_session(baseline_df)

        # Get mean RSP values
        mean_alpha = self.baseline_metrics['mean_alpha_rsp']
        mean_beta = self.baseline_metrics['mean_beta_rsp']
        mean_theta = self.baseline_metrics['mean_theta_rsp']
        mean_delta = self.baseline_metrics.get('mean_delta_rsp', 0.2)  # fallback

        self.personal_thresholds = {
            'alpha': {
                'lower': 0.9 * mean_alpha,
                'upper': 1.1 * mean_alpha
            },
            'beta': {
                'lower': 0.9 * mean_beta,
                'upper': 1.2 * mean_beta  # Higher multiplier for beta
            },
            'theta': {
                'lower': 0.9 * mean_theta,
                'upper': 1.1 * mean_theta
            },
            'delta': {
                'lower': 0.9 * mean_delta,
                'upper': 1.1 * mean_delta
            }
        }

        print(f"   ✓ Alpha thresholds: {self.personal_thresholds['alpha']['lower']:.3f} - {self.personal_thresholds['alpha']['upper']:.3f}")
        print(f"   ✓ Beta thresholds: {self.personal_thresholds['beta']['lower']:.3f} - {self.personal_thresholds['beta']['upper']:.3f}")

    def compute_performance_ratios(
        self,
        alpha_timeseries: np.ndarray,
        beta_timeseries: np.ndarray,
        use_personal_thresholds: bool = True
    ) -> Dict:
        """
        Compute performance ratios based on Kovacevic et al. (2015).

        Performance metrics:
        - Alpha Performance (aP) = (alpha+ states) / (alpha- states)
        - Beta Performance (bP) = (beta+ states) / (beta- states)

        Where:
        - alpha+ = RSP above upper threshold (good relaxation)
        - alpha- = RSP below lower threshold (too tense)
        - beta+ = RSP above upper threshold (good concentration)
        - beta- = RSP below lower threshold (mind wandering)

        Args:
            alpha_timeseries: Alpha RSP values over time
            beta_timeseries: Beta RSP values over time
            use_personal_thresholds: Use personalized thresholds (default: True)

        Returns:
            Dict with performance metrics and state counts
        """
        # Get thresholds
        if use_personal_thresholds and self.personal_thresholds:
            alpha_lower = self.personal_thresholds['alpha']['lower']
            alpha_upper = self.personal_thresholds['alpha']['upper']
            beta_lower = self.personal_thresholds['beta']['lower']
            beta_upper = self.personal_thresholds['beta']['upper']
        else:
            # Generic thresholds (based on typical RSP values ~0.15-0.35)
            alpha_mean = np.mean(alpha_timeseries)
            beta_mean = np.mean(beta_timeseries)
            alpha_lower, alpha_upper = 0.9 * alpha_mean, 1.1 * alpha_mean
            beta_lower, beta_upper = 0.9 * beta_mean, 1.2 * beta_mean

        # Count states
        alpha_plus = np.sum(alpha_timeseries > alpha_upper)
        alpha_minus = np.sum(alpha_timeseries < alpha_lower)
        beta_plus = np.sum(beta_timeseries > beta_upper)
        beta_minus = np.sum(beta_timeseries < beta_lower)

        # Compute performance ratios
        # Add 1 to denominator to avoid division by zero
        alpha_performance = alpha_plus / (alpha_minus + 1)
        beta_performance = beta_plus / (beta_minus + 1)

        # Success percentages
        total_windows = len(alpha_timeseries)
        alpha_success_pct = (alpha_plus / total_windows) * 100
        beta_success_pct = (beta_plus / total_windows) * 100

        return {
            'alpha_performance': alpha_performance,
            'beta_performance': beta_performance,
            'alpha_plus': int(alpha_plus),
            'alpha_minus': int(alpha_minus),
            'beta_plus': int(beta_plus),
            'beta_minus': int(beta_minus),
            'alpha_success_pct': alpha_success_pct,
            'beta_success_pct': beta_success_pct,
            'thresholds': {
                'alpha_lower': alpha_lower,
                'alpha_upper': alpha_upper,
                'beta_lower': beta_lower,
                'beta_upper': beta_upper
            }
        }

    def compute_training_effect(
        self,
        baseline_performance: Dict,
        current_performance: Dict,
        metric: str = 'beta_performance'
    ) -> float:
        """
        Compute training effect (% improvement from baseline).

        Based on Kovacevic et al. (2015):
        Training Effect = ((current - baseline) / baseline) × 100

        Args:
            baseline_performance: Performance dict from first session
            current_performance: Performance dict from current session
            metric: Which performance metric to track

        Returns:
            Training effect percentage (e.g., 169% = major improvement)
        """
        baseline_value = baseline_performance[metric]
        current_value = current_performance[metric]

        if baseline_value == 0:
            return 0.0

        training_effect = ((current_value - baseline_value) / baseline_value) * 100

        return training_effect

    def predict_learning_potential(self, first_session_metrics: Dict) -> Dict:
        """
        Predict learning potential from first session.

        Based on Kovacevic et al. (2015) finding:
        - High delta + low beta/gamma at baseline → 169% improvement (fast learner)
        - Low delta + high beta/gamma at baseline → -44% improvement (slow learner)

        This helps identify if someone is naturally predisposed to
        neurofeedback learning or needs a different approach.

        Args:
            first_session_metrics: Metrics from analyze_session() on first session

        Returns:
            Dict with prediction and recommendations
        """
        # Extract baseline RSP values
        delta_rsp = first_session_metrics.get('mean_delta_rsp',
                                                first_session_metrics.get('delta_rsp', 0.2))
        beta_rsp = first_session_metrics['mean_beta_rsp']
        gamma_rsp = first_session_metrics.get('mean_gamma_rsp', 0.1)

        # Compute predictor score
        # High delta + low beta/gamma = good predictor
        predictor_score = delta_rsp - (beta_rsp + gamma_rsp)

        # Classify learning potential
        if predictor_score > 0.05:
            category = "fast_learner"
            expected_improvement = "+100% to +200%"
            description = "High learning potential! Your baseline brain patterns suggest you'll respond very well to meditation practice."
            recommendations = [
                "You're naturally suited for meditation practice",
                "Expect to see rapid improvements (weeks, not months)",
                "Focus on consistency - even short daily sessions will compound",
                "Track your progress to see the rapid gains"
            ]
        elif predictor_score > -0.05:
            category = "moderate_learner"
            expected_improvement = "+20% to +80%"
            description = "Good learning potential. You'll likely see steady, consistent progress with regular practice."
            recommendations = [
                "Steady, consistent practice is key",
                "Expect gradual improvements over 4-8 weeks",
                "Don't get discouraged - your gains will be steady and sustainable",
                "Consider longer sessions (15-20 minutes) for best results"
            ]
        else:
            category = "slow_learner"
            expected_improvement = "-20% to +40%"
            description = "Your baseline patterns suggest meditation may be initially challenging. Consider complementary approaches."
            recommendations = [
                "Don't be discouraged - you may need a different approach",
                "Try body-scan meditation or guided practices first",
                "Consider combining with breathwork or movement (yoga, tai chi)",
                "Longer sessions (20-30 min) may work better than short ones",
                "Your brain may need more time to 'unlearn' active patterns"
            ]

        return {
            'category': category,
            'predictor_score': predictor_score,
            'expected_improvement': expected_improvement,
            'description': description,
            'recommendations': recommendations,
            'baseline_features': {
                'delta_rsp': delta_rsp,
                'beta_rsp': beta_rsp,
                'gamma_rsp': gamma_rsp
            }
        }

    def get_state_message(
        self,
        alpha_rsp: float,
        beta_rsp: float,
        use_personal_thresholds: bool = True
    ) -> Dict:
        """
        Get real-time state feedback message.

        Based on Kovacevic et al. (2015) feedback system:
        - a+ = "Good relaxation!" (alpha above upper threshold)
        - a- = "Too tense" (alpha below lower threshold)
        - b+ = "Good concentration!" (beta above upper threshold)
        - b- = "Mind wandering" (beta below lower threshold)

        Args:
            alpha_rsp: Current alpha RSP value
            beta_rsp: Current beta RSP value
            use_personal_thresholds: Use personalized thresholds

        Returns:
            Dict with state codes and messages
        """
        # Get thresholds
        if use_personal_thresholds and self.personal_thresholds:
            alpha_lower = self.personal_thresholds['alpha']['lower']
            alpha_upper = self.personal_thresholds['alpha']['upper']
            beta_lower = self.personal_thresholds['beta']['lower']
            beta_upper = self.personal_thresholds['beta']['upper']
        else:
            # Generic thresholds
            alpha_lower, alpha_upper = 0.18, 0.26
            beta_lower, beta_upper = 0.15, 0.24

        # Determine alpha state
        if alpha_rsp > alpha_upper:
            alpha_state = "a+"
            alpha_message = "Good relaxation! Deep meditative state."
        elif alpha_rsp < alpha_lower:
            alpha_state = "a-"
            alpha_message = "Too tense. Try to release tension and relax."
        else:
            alpha_state = "a="
            alpha_message = "Moderate relaxation. Baseline state."

        # Determine beta state
        if beta_rsp > beta_upper:
            beta_state = "b+"
            beta_message = "Strong concentration! Mind is active and focused."
        elif beta_rsp < beta_lower:
            beta_state = "b-"
            beta_message = "Mind wandering. Gently return attention to breath."
        else:
            beta_state = "b="
            beta_message = "Moderate concentration. Baseline state."

        # Combined interpretation
        if alpha_state == "a+" and beta_state == "b-":
            combined = "🧘 Perfect meditation state: Relaxed yet aware"
        elif alpha_state == "a+" and beta_state == "b+":
            combined = "🎯 Focused relaxation: Calm concentration"
        elif alpha_state == "a-" and beta_state == "b+":
            combined = "😤 Tense concentration: Try to relax while focusing"
        elif alpha_state == "a-" and beta_state == "b-":
            combined = "😴 Low engagement: May be drowsy or distracted"
        else:
            combined = "😌 Neutral state: Baseline meditation"

        return {
            'alpha_state': alpha_state,
            'alpha_message': alpha_message,
            'beta_state': beta_state,
            'beta_message': beta_message,
            'combined_state': combined,
            'values': {
                'alpha_rsp': alpha_rsp,
                'beta_rsp': beta_rsp
            },
            'thresholds': {
                'alpha_lower': alpha_lower,
                'alpha_upper': alpha_upper,
                'beta_lower': beta_lower,
                'beta_upper': beta_upper
            }
        }

    def compute_delta_reduction(
        self,
        delta_timeseries: np.ndarray,
        window_size: int = 30
    ) -> Dict:
        """
        Track delta reduction during meditation.

        Kovacevic et al. (2015) found that during concentration tasks,
        delta power (<3 Hz) should decrease (staying awake, not drowsy).

        This is a complementary metric to beta increase.

        Args:
            delta_timeseries: Delta RSP values over time
            window_size: Windows to compare (default: 30 = ~1 minute)

        Returns:
            Dict with delta reduction metrics
        """
        if len(delta_timeseries) < window_size * 2:
            return {
                'delta_reduction': 0.0,
                'early_mean': np.mean(delta_timeseries),
                'late_mean': np.mean(delta_timeseries),
                'sufficient_data': False
            }

        # Compare early vs late session
        early_delta = np.mean(delta_timeseries[:window_size])
        late_delta = np.mean(delta_timeseries[-window_size:])

        # Reduction (positive = good, delta decreased)
        delta_reduction = early_delta - late_delta
        delta_reduction_pct = (delta_reduction / early_delta) * 100 if early_delta > 0 else 0

        # Interpret
        if delta_reduction_pct > 10:
            interpretation = "Excellent: Maintained alertness throughout session"
        elif delta_reduction_pct > 0:
            interpretation = "Good: Slight improvement in alertness"
        elif delta_reduction_pct > -10:
            interpretation = "Stable: Maintained consistent alertness"
        else:
            interpretation = "Caution: Increasing drowsiness, may need shorter sessions"

        return {
            'delta_reduction': delta_reduction,
            'delta_reduction_pct': delta_reduction_pct,
            'early_mean': early_delta,
            'late_mean': late_delta,
            'interpretation': interpretation,
            'sufficient_data': True
        }


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
