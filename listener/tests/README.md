# THE LISTENER - Test Suite

Unit tests for core components.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_feature_extraction.py

# Run specific test
pytest tests/test_feature_extraction.py::TestFeatureExtractor::test_extract_features_shape

# Run tests matching pattern
pytest -k "test_depth"

# Show verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Test Organization

- `conftest.py` - Shared fixtures and configuration
- `test_feature_extraction.py` - Feature extraction tests
- `test_meditation_analyzer.py` - Meditation analysis tests
- `test_database.py` - Database operation tests

## Coverage

Generate HTML coverage report:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Writing Tests

Example test:

```python
def test_example(sample_eeg_data):
    # Arrange
    extractor = FeatureExtractor()

    # Act
    features = extractor.extract_features(sample_eeg_data)

    # Assert
    assert features.shape == (34,)
    assert not np.isnan(features).any()
```

## Fixtures

Available fixtures (from `conftest.py`):

- `sample_eeg_data` - Mock EEG data (4, 2560)
- `sample_features` - Mock feature vector (34,)
- `sample_latent` - Mock latent vector (32,)
- `sample_session_dict` - Mock session dictionary
- `temp_database` - Temporary SQLite database
- `temp_output_dir` - Temporary output directory
- `mock_vae_model` - Mock VAE model checkpoint

## Test Markers

Use markers to organize tests:

```python
@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.integration
def test_database_integration():
    ...
```

Run specific markers:

```bash
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```
