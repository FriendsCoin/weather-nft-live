"""
EEG Signal Preprocessing

This module handles:
- Bandpass filtering (0.5-50 Hz)
- Notch filtering (powerline noise removal)
- Artifact removal (eye blinks, movement)
- Normalization (z-score, robust)

Uses MNE-Python for professional EEG processing.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import warnings


class EEGPreprocessor:
    """
    Preprocess raw EEG data for meditation analysis.

    Pipeline:
    1. Load raw CSV data
    2. Bandpass filter (0.5-50 Hz)
    3. Notch filter (remove 60 Hz powerline noise)
    4. Artifact removal (optional ICA for eye blinks)
    5. Normalization

    Usage:
        preprocessor = EEGPreprocessor()
        preprocessor.load_session("data/raw/session_001.csv")
        preprocessor.apply_filters()
        preprocessor.remove_artifacts()
        clean_data = preprocessor.get_clean_data()
        preprocessor.save("data/processed/session_001_clean.csv")
    """

    def __init__(
        self,
        channels: Optional[list] = None,
        sampling_rate: int = 256,
        bandpass_low: float = 0.5,
        bandpass_high: float = 50.0,
        notch_freq: int = 60
    ):
        """
        Initialize preprocessor.

        Args:
            channels: Channel names (default: Muse S channels)
            sampling_rate: Sampling rate in Hz
            bandpass_low: High-pass cutoff (remove slow drifts)
            bandpass_high: Low-pass cutoff (remove high-frequency noise)
            notch_freq: Powerline noise frequency (60 Hz US, 50 Hz EU)
        """
        self.channels = channels or ["TP9", "AF7", "AF8", "TP10"]
        self.sampling_rate = sampling_rate
        self.bandpass_low = bandpass_low
        self.bandpass_high = bandpass_high
        self.notch_freq = notch_freq

        self.raw_data = None
        self.clean_data = None
        self.timestamps = None

    def load_session(self, csv_path: str) -> None:
        """
        Load raw EEG session from CSV.

        Args:
            csv_path: Path to CSV file with columns: timestamp, TP9, AF7, AF8, TP10
        """
        print(f"\n📂 Loading session: {csv_path}")

        df = pd.read_csv(csv_path)

        # Extract data
        self.timestamps = df['timestamp'].values
        self.raw_data = df[self.channels].values.T  # Shape: (n_channels, n_samples)

        print(f"   Channels: {len(self.channels)}")
        print(f"   Samples: {len(self.timestamps)}")
        print(f"   Duration: {len(self.timestamps) / self.sampling_rate:.2f} seconds")

        # Basic statistics
        print(f"\n📊 Signal statistics:")
        for i, ch in enumerate(self.channels):
            mean = np.mean(self.raw_data[i])
            std = np.std(self.raw_data[i])
            min_val = np.min(self.raw_data[i])
            max_val = np.max(self.raw_data[i])
            print(f"   {ch}: mean={mean:.2f}, std={std:.2f}, range=[{min_val:.2f}, {max_val:.2f}]")

    def apply_filters(self, use_mne: bool = True) -> None:
        """
        Apply bandpass and notch filters.

        Args:
            use_mne: Use MNE-Python (recommended) or scipy fallback
        """
        if self.raw_data is None:
            raise ValueError("No data loaded. Call load_session() first.")

        print(f"\n🔧 Applying filters...")
        print(f"   Bandpass: {self.bandpass_low}-{self.bandpass_high} Hz")
        print(f"   Notch: {self.notch_freq} Hz (powerline noise)")

        if use_mne:
            self._apply_filters_mne()
        else:
            self._apply_filters_scipy()

        print(f"✅ Filtering complete")

    def _apply_filters_mne(self) -> None:
        """Apply filters using MNE-Python (professional EEG processing)."""
        try:
            import mne

            # Suppress MNE info messages
            mne.set_log_level('WARNING')

            # Create MNE RawArray
            info = mne.create_info(
                ch_names=self.channels,
                sfreq=self.sampling_rate,
                ch_types='eeg'
            )

            raw = mne.io.RawArray(self.raw_data.copy(), info, verbose=False)

            # Bandpass filter
            raw.filter(
                l_freq=self.bandpass_low,
                h_freq=self.bandpass_high,
                fir_design='firwin',
                verbose=False
            )

            # Notch filter (powerline noise)
            raw.notch_filter(
                freqs=self.notch_freq,
                verbose=False
            )

            # Get filtered data
            self.clean_data = raw.get_data()

        except ImportError:
            print("⚠️  MNE-Python not available, using scipy fallback")
            self._apply_filters_scipy()

    def _apply_filters_scipy(self) -> None:
        """Apply filters using scipy (fallback if MNE not available)."""
        from scipy import signal

        self.clean_data = self.raw_data.copy()

        # Design bandpass filter
        sos_bandpass = signal.butter(
            4,  # Filter order
            [self.bandpass_low, self.bandpass_high],
            btype='bandpass',
            fs=self.sampling_rate,
            output='sos'
        )

        # Design notch filter
        sos_notch = signal.iirnotch(
            self.notch_freq,
            Q=30,
            fs=self.sampling_rate
        )

        # Apply to each channel
        for i in range(len(self.channels)):
            # Bandpass
            self.clean_data[i] = signal.sosfiltfilt(sos_bandpass, self.clean_data[i])
            # Notch
            self.clean_data[i] = signal.filtfilt(sos_notch[0], sos_notch[1], self.clean_data[i])

    def remove_artifacts(self, method: str = "simple") -> None:
        """
        Remove artifacts (eye blinks, movement).

        Args:
            method: "simple" (threshold-based) or "ica" (Independent Component Analysis)
        """
        if self.clean_data is None:
            raise ValueError("No filtered data. Call apply_filters() first.")

        print(f"\n🧹 Removing artifacts (method: {method})...")

        if method == "ica":
            self._remove_artifacts_ica()
        else:
            self._remove_artifacts_simple()

        print(f"✅ Artifact removal complete")

    def _remove_artifacts_simple(self) -> None:
        """Simple threshold-based artifact removal."""
        # Detect large spikes (likely artifacts)
        threshold = 5.0  # Standard deviations

        for i in range(len(self.channels)):
            mean = np.mean(self.clean_data[i])
            std = np.std(self.clean_data[i])

            # Find outliers
            outliers = np.abs(self.clean_data[i] - mean) > (threshold * std)
            n_outliers = np.sum(outliers)

            if n_outliers > 0:
                # Replace outliers with interpolated values
                outlier_indices = np.where(outliers)[0]

                for idx in outlier_indices:
                    # Linear interpolation between surrounding points
                    start_idx = max(0, idx - 5)
                    end_idx = min(len(self.clean_data[i]) - 1, idx + 5)

                    if start_idx < idx < end_idx:
                        self.clean_data[i][idx] = np.mean([
                            self.clean_data[i][start_idx],
                            self.clean_data[i][end_idx]
                        ])

                print(f"   {self.channels[i]}: Removed {n_outliers} artifacts")

    def _remove_artifacts_ica(self) -> None:
        """ICA-based artifact removal (eye blinks, muscle activity)."""
        try:
            import mne
            from sklearn.decomposition import FastICA

            mne.set_log_level('WARNING')

            # Create MNE RawArray
            info = mne.create_info(
                ch_names=self.channels,
                sfreq=self.sampling_rate,
                ch_types='eeg'
            )

            raw = mne.io.RawArray(self.clean_data.copy(), info, verbose=False)

            # Apply ICA
            ica = mne.preprocessing.ICA(
                n_components=min(4, len(self.channels)),
                random_state=42,
                verbose=False
            )

            ica.fit(raw)

            # Auto-detect eye blink components (typically have frontal topography)
            # For Muse S: AF7, AF8 are frontal channels
            eog_indices, eog_scores = ica.find_bads_eog(
                raw,
                ch_name=['AF7', 'AF8'],
                verbose=False
            )

            if len(eog_indices) > 0:
                print(f"   Found {len(eog_indices)} eye blink components")
                ica.exclude = eog_indices

                # Apply ICA removal
                raw_corrected = ica.apply(raw.copy(), verbose=False)
                self.clean_data = raw_corrected.get_data()
            else:
                print(f"   No eye blink components detected")

        except ImportError:
            print("⚠️  MNE or sklearn not available for ICA, using simple method")
            self._remove_artifacts_simple()

    def normalize(self, method: str = "z-score") -> None:
        """
        Normalize data.

        Args:
            method: "z-score", "min-max", or "robust"
        """
        if self.clean_data is None:
            raise ValueError("No data to normalize. Run preprocessing first.")

        print(f"\n📏 Normalizing data (method: {method})...")

        for i in range(len(self.channels)):
            if method == "z-score":
                # Zero mean, unit variance
                mean = np.mean(self.clean_data[i])
                std = np.std(self.clean_data[i])
                self.clean_data[i] = (self.clean_data[i] - mean) / (std + 1e-8)

            elif method == "min-max":
                # Scale to [0, 1]
                min_val = np.min(self.clean_data[i])
                max_val = np.max(self.clean_data[i])
                self.clean_data[i] = (self.clean_data[i] - min_val) / (max_val - min_val + 1e-8)

            elif method == "robust":
                # Use median and IQR (robust to outliers)
                median = np.median(self.clean_data[i])
                q75, q25 = np.percentile(self.clean_data[i], [75, 25])
                iqr = q75 - q25
                self.clean_data[i] = (self.clean_data[i] - median) / (iqr + 1e-8)

        print(f"✅ Normalization complete")

    def get_clean_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get preprocessed data.

        Returns:
            Tuple of (timestamps, clean_data)
            clean_data shape: (n_channels, n_samples)
        """
        if self.clean_data is None:
            raise ValueError("No clean data available. Run preprocessing first.")

        return self.timestamps, self.clean_data

    def save(self, output_path: str) -> None:
        """
        Save preprocessed data to CSV.

        Args:
            output_path: Path to save cleaned data
        """
        if self.clean_data is None:
            raise ValueError("No clean data to save.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create DataFrame
        df = pd.DataFrame(
            self.clean_data.T,
            columns=self.channels
        )
        df.insert(0, 'timestamp', self.timestamps)

        # Save
        df.to_csv(output_path, index=False)

        print(f"\n💾 Saved preprocessed data: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.2f} KB")


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EEG Preprocessing CLI")
    parser.add_argument("input", help="Input CSV file (raw EEG)")
    parser.add_argument("--output", help="Output CSV file (cleaned)")
    parser.add_argument("--artifact-method", default="simple",
                       choices=["simple", "ica"],
                       help="Artifact removal method")
    parser.add_argument("--normalize", default="z-score",
                       choices=["z-score", "min-max", "robust"],
                       help="Normalization method")

    args = parser.parse_args()

    # Default output path
    if args.output is None:
        input_path = Path(args.input)
        args.output = input_path.parent.parent / "processed" / f"{input_path.stem}_clean.csv"

    # Preprocess
    preprocessor = EEGPreprocessor()
    preprocessor.load_session(args.input)
    preprocessor.apply_filters()
    preprocessor.remove_artifacts(method=args.artifact_method)
    preprocessor.normalize(method=args.normalize)
    preprocessor.save(args.output)

    print("\n✅ Preprocessing complete!")
