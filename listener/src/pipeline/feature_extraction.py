"""
EEG Feature Extraction

Extract meditation-relevant features from preprocessed EEG:
- Frequency band powers (delta, theta, alpha, beta, gamma)
- Temporal features (smoothness, transitions)
- Asymmetry (left vs right hemisphere)
- Connectivity (channel correlations)
- Entropy (signal complexity)

These features become the input to the VAE model.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scipy import signal
from scipy.stats import entropy


class FeatureExtractor:
    """
    Extract features from preprocessed EEG data.

    Features per window:
    - Band powers: delta, theta, alpha, beta, gamma (5 × 4 channels = 20)
    - Asymmetry: alpha asymmetry, beta asymmetry (2)
    - Connectivity: channel correlations (6 pairs)
    - Entropy: spectral entropy per channel (4)
    Total: ~32 features per time window

    Usage:
        extractor = FeatureExtractor(window_size=4.0, overlap=0.5)
        features = extractor.extract_from_file("data/processed/session_001_clean.csv")
        extractor.save_features(features, "data/sessions/session_001_features.h5")
    """

    def __init__(
        self,
        window_size: float = 4.0,
        overlap: float = 0.5,
        sampling_rate: int = 256,
        channels: Optional[List[str]] = None
    ):
        """
        Initialize feature extractor.

        Args:
            window_size: Window size in seconds (e.g., 4.0 = 4 seconds)
            overlap: Overlap ratio (0.5 = 50% overlap)
            sampling_rate: Sampling rate in Hz
            channels: Channel names
        """
        self.window_size = window_size
        self.overlap = overlap
        self.sampling_rate = sampling_rate
        self.channels = channels or ["TP9", "AF7", "AF8", "TP10"]

        # Window parameters
        self.window_samples = int(window_size * sampling_rate)
        self.step_samples = int(self.window_samples * (1 - overlap))

        # Frequency bands (Hz)
        self.bands = {
            'delta': (0.5, 4.0),    # Deep sleep
            'theta': (4.0, 8.0),    # Meditation, drowsiness
            'alpha': (8.0, 13.0),   # Relaxation, eyes closed
            'beta': (13.0, 30.0),   # Active thinking
            'gamma': (30.0, 50.0)   # Concentration
        }

        print(f"🔍 Feature Extractor initialized:")
        print(f"   Window: {window_size}s ({self.window_samples} samples)")
        print(f"   Step: {self.step_samples} samples ({overlap*100}% overlap)")
        print(f"   Bands: {list(self.bands.keys())}")

    def extract_from_file(self, csv_path: str) -> pd.DataFrame:
        """
        Extract features from preprocessed CSV file.

        Args:
            csv_path: Path to cleaned EEG CSV

        Returns:
            DataFrame with features (rows = time windows, columns = features)
        """
        print(f"\n📂 Loading preprocessed data: {csv_path}")

        # Load data
        df = pd.read_csv(csv_path)
        timestamps = df['timestamp'].values
        data = df[self.channels].values.T  # Shape: (n_channels, n_samples)

        print(f"   Samples: {data.shape[1]}")
        print(f"   Duration: {data.shape[1] / self.sampling_rate:.2f} seconds")

        # Extract features
        return self.extract_features(data, timestamps)

    def extract_features(
        self,
        data: np.ndarray,
        timestamps: np.ndarray
    ) -> pd.DataFrame:
        """
        Extract features from EEG data array.

        Args:
            data: EEG data, shape (n_channels, n_samples)
            timestamps: Timestamp array

        Returns:
            DataFrame with features per window
        """
        n_samples = data.shape[1]
        n_windows = (n_samples - self.window_samples) // self.step_samples + 1

        print(f"\n🔧 Extracting features...")
        print(f"   Number of windows: {n_windows}")

        features_list = []

        for i in range(n_windows):
            start_idx = i * self.step_samples
            end_idx = start_idx + self.window_samples

            if end_idx > n_samples:
                break

            # Window data
            window = data[:, start_idx:end_idx]
            window_time = timestamps[start_idx]

            # Extract features for this window
            window_features = self._extract_window_features(window)
            window_features['timestamp'] = window_time
            window_features['window_idx'] = i

            features_list.append(window_features)

            # Progress
            if (i + 1) % 50 == 0:
                print(f"   Progress: {i+1}/{n_windows} windows")

        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)

        print(f"✅ Feature extraction complete")
        print(f"   Windows: {len(features_df)}")
        print(f"   Features per window: {len(features_df.columns) - 2}")  # -2 for timestamp and window_idx

        return features_df

    def _extract_window_features(self, window: np.ndarray) -> Dict:
        """Extract all features from a single window."""
        features = {}

        # 1. Band powers (20 features: 5 bands × 4 channels)
        band_powers = self._compute_band_powers(window)
        features.update(band_powers)

        # 2. Asymmetry features (2 features)
        asymmetry = self._compute_asymmetry(band_powers)
        features.update(asymmetry)

        # 3. Connectivity features (6 features: pairwise correlations)
        connectivity = self._compute_connectivity(window)
        features.update(connectivity)

        # 4. Entropy features (4 features: one per channel)
        entropy_features = self._compute_entropy(window)
        features.update(entropy_features)

        # 5. Temporal features (2 features)
        temporal = self._compute_temporal_features(window)
        features.update(temporal)

        return features

    def _compute_band_powers(self, window: np.ndarray) -> Dict:
        """
        Compute power in each frequency band using Welch's method.

        Args:
            window: EEG data, shape (n_channels, window_samples)

        Returns:
            Dict with keys like "delta_TP9", "theta_AF7", etc.
        """
        features = {}

        for i, channel in enumerate(self.channels):
            # Compute power spectral density using Welch's method
            freqs, psd = signal.welch(
                window[i],
                fs=self.sampling_rate,
                nperseg=min(256, len(window[i]))
            )

            # Compute power in each band
            for band_name, (low, high) in self.bands.items():
                # Find frequencies in this band
                band_mask = (freqs >= low) & (freqs <= high)

                # Integrate PSD over band (approximation of band power)
                band_power = np.trapz(psd[band_mask], freqs[band_mask])

                # Log transform (EEG power is log-normally distributed)
                band_power_log = np.log10(band_power + 1e-10)

                features[f"{band_name}_{channel}"] = band_power_log

        return features

    def _compute_asymmetry(self, band_powers: Dict) -> Dict:
        """
        Compute hemispheric asymmetry.

        For Muse S:
        - Left hemisphere: TP9, AF7
        - Right hemisphere: TP10, AF8

        Asymmetry = log(Right/Left)
        Positive = more right activity
        Negative = more left activity
        """
        features = {}

        # Alpha asymmetry (important for meditation/emotion)
        alpha_left = (band_powers['alpha_TP9'] + band_powers['alpha_AF7']) / 2
        alpha_right = (band_powers['alpha_TP10'] + band_powers['alpha_AF8']) / 2
        features['alpha_asymmetry'] = alpha_right - alpha_left  # Already log scale

        # Beta asymmetry
        beta_left = (band_powers['beta_TP9'] + band_powers['beta_AF7']) / 2
        beta_right = (band_powers['beta_TP10'] + band_powers['beta_AF8']) / 2
        features['beta_asymmetry'] = beta_right - beta_left

        return features

    def _compute_connectivity(self, window: np.ndarray) -> Dict:
        """
        Compute channel connectivity (correlations).

        Measures how synchronized different brain regions are.
        """
        features = {}

        # All pairwise correlations
        n_channels = len(self.channels)
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                # Pearson correlation
                corr = np.corrcoef(window[i], window[j])[0, 1]
                features[f"conn_{self.channels[i]}_{self.channels[j]}"] = corr

        return features

    def _compute_entropy(self, window: np.ndarray) -> Dict:
        """
        Compute spectral entropy (measure of signal complexity).

        Lower entropy = more regular/rhythmic
        Higher entropy = more complex/irregular
        """
        features = {}

        for i, channel in enumerate(self.channels):
            # Power spectral density
            freqs, psd = signal.welch(
                window[i],
                fs=self.sampling_rate,
                nperseg=min(256, len(window[i]))
            )

            # Normalize PSD to probability distribution
            psd_norm = psd / np.sum(psd)

            # Shannon entropy
            spectral_entropy = entropy(psd_norm)

            features[f"entropy_{channel}"] = spectral_entropy

        return features

    def _compute_temporal_features(self, window: np.ndarray) -> Dict:
        """
        Compute temporal features (how signal changes over time).
        """
        features = {}

        # Mean absolute derivative (smoothness)
        # Lower = smoother signal
        derivatives = np.diff(window, axis=1)
        mad = np.mean(np.abs(derivatives))
        features['mean_absolute_derivative'] = mad

        # Standard deviation across channels (spatial variance)
        spatial_std = np.mean(np.std(window, axis=0))
        features['spatial_variance'] = spatial_std

        return features

    def save_features(self, features_df: pd.DataFrame, output_path: str) -> None:
        """
        Save features to HDF5 file (efficient for numerical data).

        Args:
            features_df: Feature DataFrame
            output_path: Path to save (should end in .h5)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as HDF5
        features_df.to_hdf(
            output_path,
            key='features',
            mode='w',
            complevel=9  # Compression
        )

        print(f"\n💾 Saved features: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.2f} KB")
        print(f"   Shape: {features_df.shape}")

    @staticmethod
    def load_features(h5_path: str) -> pd.DataFrame:
        """Load features from HDF5 file."""
        return pd.read_hdf(h5_path, key='features')

    def summarize_features(self, features_df: pd.DataFrame) -> None:
        """Print summary statistics of extracted features."""
        print("\n📊 Feature Summary:")
        print(f"   Total windows: {len(features_df)}")
        print(f"   Features per window: {len(features_df.columns) - 2}")
        print(f"\n   Feature statistics:")

        # Group by feature type
        band_features = [c for c in features_df.columns if any(b in c for b in self.bands.keys())]
        asymmetry_features = [c for c in features_df.columns if 'asymmetry' in c]
        connectivity_features = [c for c in features_df.columns if 'conn_' in c]
        entropy_features = [c for c in features_df.columns if 'entropy' in c]

        print(f"      Band powers: {len(band_features)}")
        print(f"      Asymmetry: {len(asymmetry_features)}")
        print(f"      Connectivity: {len(connectivity_features)}")
        print(f"      Entropy: {len(entropy_features)}")

        # Show mean alpha power (important for meditation)
        alpha_cols = [c for c in features_df.columns if 'alpha_' in c and 'asymmetry' not in c]
        if alpha_cols:
            mean_alpha = features_df[alpha_cols].mean().mean()
            print(f"\n   Mean alpha power: {mean_alpha:.3f} (higher = more relaxed)")


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EEG Feature Extraction CLI")
    parser.add_argument("input", help="Input CSV file (preprocessed EEG)")
    parser.add_argument("--output", help="Output HDF5 file (features)")
    parser.add_argument("--window-size", type=float, default=4.0,
                       help="Window size in seconds")
    parser.add_argument("--overlap", type=float, default=0.5,
                       help="Window overlap ratio (0-1)")

    args = parser.parse_args()

    # Default output path
    if args.output is None:
        input_path = Path(args.input)
        args.output = input_path.parent.parent / "sessions" / f"{input_path.stem.replace('_clean', '')}_features.h5"

    # Extract features
    extractor = FeatureExtractor(
        window_size=args.window_size,
        overlap=args.overlap
    )

    features = extractor.extract_from_file(args.input)
    extractor.summarize_features(features)
    extractor.save_features(features, args.output)

    print("\n✅ Feature extraction complete!")
