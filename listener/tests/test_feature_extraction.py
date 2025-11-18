"""
Tests for Feature Extraction
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.feature_extraction import FeatureExtractor


class TestFeatureExtractor:
    """Test suite for FeatureExtractor"""

    def test_initialization(self):
        """Test FeatureExtractor initialization"""
        extractor = FeatureExtractor()
        assert extractor is not None

    def test_extract_features_shape(self, sample_eeg_data):
        """Test that extracted features have correct shape"""
        extractor = FeatureExtractor()
        features = extractor.extract_features(sample_eeg_data)

        assert isinstance(features, np.ndarray)
        assert features.shape == (34,), f"Expected shape (34,), got {features.shape}"

    def test_extract_features_no_nan(self, sample_eeg_data):
        """Test that extracted features don't contain NaN values"""
        extractor = FeatureExtractor()
        features = extractor.extract_features(sample_eeg_data)

        assert not np.isnan(features).any(), "Features contain NaN values"

    def test_extract_features_no_inf(self, sample_eeg_data):
        """Test that extracted features don't contain Inf values"""
        extractor = FeatureExtractor()
        features = extractor.extract_features(sample_eeg_data)

        assert not np.isinf(features).any(), "Features contain Inf values"

    def test_extract_features_deterministic(self, sample_eeg_data):
        """Test that feature extraction is deterministic"""
        extractor = FeatureExtractor()

        features1 = extractor.extract_features(sample_eeg_data)
        features2 = extractor.extract_features(sample_eeg_data)

        np.testing.assert_array_equal(features1, features2,
                                     err_msg="Feature extraction is not deterministic")

    def test_band_powers_positive(self, sample_eeg_data):
        """Test that band powers are positive"""
        extractor = FeatureExtractor()
        features = extractor.extract_features(sample_eeg_data)

        # First 20 features are band powers (5 bands × 4 channels)
        band_powers = features[:20]
        assert np.all(band_powers >= 0), "Band powers should be non-negative"

    def test_different_inputs_different_outputs(self):
        """Test that different EEG data produces different features"""
        extractor = FeatureExtractor()

        # Generate two different EEG signals
        np.random.seed(42)
        eeg1 = np.random.randn(4, 2560)

        np.random.seed(123)
        eeg2 = np.random.randn(4, 2560)

        features1 = extractor.extract_features(eeg1)
        features2 = extractor.extract_features(eeg2)

        assert not np.array_equal(features1, features2), \
            "Different EEG data should produce different features"

    def test_zero_input(self):
        """Test behavior with zero EEG data"""
        extractor = FeatureExtractor()
        eeg_zeros = np.zeros((4, 2560))

        features = extractor.extract_features(eeg_zeros)

        assert isinstance(features, np.ndarray)
        assert features.shape == (34,)
        # Most features should be zero or very small for zero input
        assert np.all(np.abs(features) < 1e-6), "Zero input should produce near-zero features"

    def test_invalid_shape(self):
        """Test error handling for invalid EEG shape"""
        extractor = FeatureExtractor()

        # Wrong number of channels
        with pytest.raises((ValueError, IndexError, AssertionError)):
            extractor.extract_features(np.random.randn(3, 2560))

        # Too few samples
        with pytest.raises((ValueError, IndexError)):
            extractor.extract_features(np.random.randn(4, 100))

    def test_feature_ranges(self, sample_eeg_data):
        """Test that features are within reasonable ranges"""
        extractor = FeatureExtractor()
        features = extractor.extract_features(sample_eeg_data)

        # Band powers should be positive and not too large
        band_powers = features[:20]
        assert np.all(band_powers >= 0)
        assert np.all(band_powers < 1000), "Band powers seem unusually large"

        # Ratios should be positive
        ratios = features[20:28]
        assert np.all(ratios >= 0), "Ratios should be non-negative"

        # Coherence should be between 0 and 1
        coherence = features[28:34]
        assert np.all(coherence >= 0) and np.all(coherence <= 1.1), \
            "Coherence should be between 0 and 1 (with small tolerance)"
