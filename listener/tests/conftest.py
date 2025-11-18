"""
Pytest configuration and shared fixtures for THE LISTENER tests
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path


@pytest.fixture
def sample_eeg_data():
    """
    Generate sample EEG data for testing

    Returns:
        np.ndarray: (4, 2560) - 4 channels, 10 seconds @ 256 Hz
    """
    np.random.seed(42)
    n_channels = 4
    n_samples = 2560  # 10 seconds @ 256 Hz

    # Generate realistic EEG-like data
    # Mix of frequencies: delta (1-4 Hz), theta (4-8 Hz), alpha (8-13 Hz), beta (13-30 Hz)
    time = np.linspace(0, 10, n_samples)
    eeg_data = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Add frequency components
        eeg_data[ch] += 5 * np.sin(2 * np.pi * 2 * time)    # Delta
        eeg_data[ch] += 3 * np.sin(2 * np.pi * 6 * time)    # Theta
        eeg_data[ch] += 4 * np.sin(2 * np.pi * 10 * time)   # Alpha
        eeg_data[ch] += 2 * np.sin(2 * np.pi * 20 * time)   # Beta
        eeg_data[ch] += np.random.randn(n_samples) * 0.5    # Noise

    return eeg_data


@pytest.fixture
def sample_features():
    """
    Generate sample feature vector for testing

    Returns:
        np.ndarray: (34,) - Feature vector
    """
    np.random.seed(42)
    return np.random.randn(34)


@pytest.fixture
def sample_latent():
    """
    Generate sample latent vector for testing

    Returns:
        np.ndarray: (32,) - Latent vector
    """
    np.random.seed(42)
    return np.random.randn(32)


@pytest.fixture
def sample_session_dict():
    """
    Generate sample session dictionary for testing

    Returns:
        dict: Session data
    """
    return {
        'session_id': 'test_session_001',
        'recorded_at': '2025-01-15 14:30:00',
        'duration_seconds': 600,
        'depth_score': 75.3,
        'quality_score': 92.1,
        'performance_ratios': {
            'alpha_plus': 1.2,
            'alpha_minus': 0.8,
            'beta_plus': 1.1,
            'beta_minus': 0.9
        },
        'state': 'deep',
        'latent_mean': np.random.randn(32).tolist()
    }


@pytest.fixture
def temp_database():
    """
    Create a temporary SQLite database for testing

    Returns:
        str: Database URL
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_url = f"sqlite:///{f.name}"
        yield db_url

    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_output_dir():
    """
    Create a temporary output directory for testing

    Returns:
        Path: Temporary directory path
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_vae_model():
    """
    Create a mock VAE model for testing

    Returns:
        dict: Model checkpoint dictionary
    """
    import torch

    # Create minimal VAE state dict
    state_dict = {
        'encoder.0.weight': torch.randn(128, 34),
        'encoder.0.bias': torch.randn(128),
        'encoder.2.weight': torch.randn(64, 128),
        'encoder.2.bias': torch.randn(64),
        'fc_mu.weight': torch.randn(32, 64),
        'fc_mu.bias': torch.randn(32),
        'fc_logvar.weight': torch.randn(32, 64),
        'fc_logvar.bias': torch.randn(32),
        'decoder.0.weight': torch.randn(64, 32),
        'decoder.0.bias': torch.randn(64),
        'decoder.2.weight': torch.randn(128, 64),
        'decoder.2.bias': torch.randn(128),
        'decoder.4.weight': torch.randn(34, 128),
        'decoder.4.bias': torch.randn(34),
    }

    checkpoint = {
        'model_state_dict': state_dict,
        'epoch': 10,
        'input_dim': 34,
        'latent_dim': 32,
        'train_loss': 0.5,
        'val_loss': 0.6
    }

    return checkpoint


@pytest.fixture(autouse=True)
def reset_random_seeds():
    """
    Reset random seeds before each test for reproducibility
    """
    np.random.seed(42)
    import random
    random.seed(42)

    try:
        import torch
        torch.manual_seed(42)
    except ImportError:
        pass
