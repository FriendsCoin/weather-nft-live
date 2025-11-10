"""EEG data pipeline - capture, preprocess, extract features."""

from .eeg_capture import MuseRecorder, MockEEGGenerator
from .preprocessing import EEGPreprocessor
from .feature_extraction import FeatureExtractor

__all__ = [
    "MuseRecorder",
    "MockEEGGenerator",
    "EEGPreprocessor",
    "FeatureExtractor",
]
