"""
Enhanced error handling utilities for THE LISTENER

Provides helpful error messages with actionable solutions
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import importlib.util


class ListenerError(Exception):
    """Base exception for THE LISTENER with helpful error messages"""

    def __init__(self, message: str, solution: Optional[str] = None, error_type: str = "Error"):
        self.message = message
        self.solution = solution
        self.error_type = error_type
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message with solution"""
        msg = f"\n{'='*60}\n"
        msg += f"❌ {self.error_type}: {self.message}\n"
        msg += f"{'='*60}\n"

        if self.solution:
            msg += f"\n💡 Solution:\n{self.solution}\n"
            msg += f"{'='*60}\n"

        return msg


class DependencyError(ListenerError):
    """Error for missing dependencies"""

    def __init__(self, package: str, import_name: Optional[str] = None, install_name: Optional[str] = None):
        import_name = import_name or package
        install_name = install_name or package

        message = f"Required package '{package}' is not installed"
        solution = f"""Install the missing package:

    pip install {install_name}

Or install all requirements:

    pip install -r requirements.txt
"""
        super().__init__(message, solution, "Dependency Error")


class ConfigurationError(ListenerError):
    """Error for configuration issues"""

    def __init__(self, message: str, solution: Optional[str] = None):
        if solution is None:
            solution = """Check your config.yaml file or run setup:

    python scripts/setup.py
"""
        super().__init__(message, solution, "Configuration Error")


class DataNotFoundError(ListenerError):
    """Error for missing data files"""

    def __init__(self, path: str, data_type: str = "data"):
        message = f"Required {data_type} not found: {path}"
        solution = f"""The {data_type} file does not exist.

If this is your first time running:
    python scripts/setup.py

To generate sample data:
    python scripts/generate_mock_data.py --num-sessions 5 --duration 300

Or check the path and try again.
"""
        super().__init__(message, solution, "Data Not Found")


class GPUError(ListenerError):
    """Error for GPU-related issues"""

    def __init__(self, message: str):
        solution = """GPU issues detected. Try these solutions:

1. Check GPU availability:
    python scripts/test_gpu_setup.py

2. Use CPU mode instead:
    Add --device cpu to your command

3. Check CUDA installation:
    nvidia-smi

4. Reduce memory usage:
    - Use smaller batch size: --batch-size 16
    - Use smaller latent dimension: --latent-dim 16
"""
        super().__init__(message, solution, "GPU Error")


class APIError(ListenerError):
    """Error for API-related issues"""

    def __init__(self, api_name: str, message: str):
        solution = f"""Check your API configuration:

1. Verify API key in config.yaml
2. Check API key is valid at:
    - Anthropic: https://console.anthropic.com/
    - Replicate: https://replicate.com/account

3. Check network connection
4. Verify API quota/credits

To skip API calls and work locally:
    python scripts/setup.py --skip-api-keys
"""
        super().__init__(f"{api_name} API error: {message}", solution, "API Error")


def check_dependency(package: str, import_name: Optional[str] = None, install_name: Optional[str] = None) -> bool:
    """
    Check if a Python package is installed

    Args:
        package: Display name of the package
        import_name: Name to use for import (defaults to package)
        install_name: Name to use for pip install (defaults to package)

    Returns:
        True if package is installed, False otherwise

    Raises:
        DependencyError: If package is not installed
    """
    import_name = import_name or package

    try:
        __import__(import_name)
        return True
    except ImportError:
        raise DependencyError(package, import_name, install_name)


def check_dependencies(required: List[str], optional: Optional[List[str]] = None) -> Dict[str, bool]:
    """
    Check multiple dependencies at once

    Args:
        required: List of required package names
        optional: List of optional package names

    Returns:
        Dictionary with package availability status

    Raises:
        DependencyError: If any required package is missing
    """
    results = {}

    # Check required packages
    for package in required:
        try:
            check_dependency(package)
            results[package] = True
        except DependencyError:
            results[package] = False
            raise

    # Check optional packages (don't raise)
    if optional:
        for package in optional:
            try:
                __import__(package)
                results[package] = True
            except ImportError:
                results[package] = False

    return results


def check_file_exists(path: str, data_type: str = "file") -> Path:
    """
    Check if a file exists and return Path object

    Args:
        path: Path to check
        data_type: Description of the data type (for error message)

    Returns:
        Path object if file exists

    Raises:
        DataNotFoundError: If file does not exist
    """
    file_path = Path(path)

    if not file_path.exists():
        raise DataNotFoundError(str(path), data_type)

    return file_path


def check_directory_exists(path: str, create: bool = False) -> Path:
    """
    Check if a directory exists, optionally create it

    Args:
        path: Directory path to check
        create: If True, create directory if it doesn't exist

    Returns:
        Path object

    Raises:
        DataNotFoundError: If directory doesn't exist and create=False
    """
    dir_path = Path(path)

    if not dir_path.exists():
        if create:
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            raise DataNotFoundError(str(path), "directory")

    return dir_path


def check_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load and validate configuration file

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary

    Raises:
        ConfigurationError: If config file is missing or invalid
    """
    import yaml

    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}",
            """Create a configuration file:

    cp config.example.yaml config.yaml

Or run the setup wizard:

    python scripts/setup.py
"""
        )

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Invalid YAML in configuration file: {e}",
            "Check your config.yaml syntax"
        )

    # Validate required sections
    required_sections = ["anthropic", "project", "preprocessing", "features", "model", "training"]
    missing_sections = [s for s in required_sections if s not in config]

    if missing_sections:
        raise ConfigurationError(
            f"Missing required sections in config.yaml: {', '.join(missing_sections)}",
            "Use config.example.yaml as a template"
        )

    return config


def check_gpu_available(required: bool = False) -> bool:
    """
    Check if GPU is available

    Args:
        required: If True, raise error if GPU not available

    Returns:
        True if GPU is available, False otherwise

    Raises:
        GPUError: If GPU is required but not available
    """
    try:
        import torch
        available = torch.cuda.is_available()

        if required and not available:
            raise GPUError(
                "GPU required but CUDA is not available"
            )

        return available

    except ImportError:
        if required:
            raise DependencyError("torch", "torch", "torch")
        return False


def check_api_key(config: Dict[str, Any], api_name: str) -> Optional[str]:
    """
    Check if API key is configured

    Args:
        config: Configuration dictionary
        api_name: Name of the API (e.g., "anthropic", "replicate")

    Returns:
        API key if found, None otherwise

    Raises:
        ConfigurationError: If API key is missing or placeholder
    """
    if api_name not in config:
        raise ConfigurationError(
            f"API configuration missing: {api_name}",
            f"Add {api_name} section to config.yaml"
        )

    api_key = config[api_name].get("api_key", "")

    # Check for placeholder values
    placeholders = ["your-", "placeholder", "example", ""]
    if any(p in api_key.lower() for p in placeholders):
        return None

    return api_key


def validate_session_data(session_path: str) -> Dict[str, Any]:
    """
    Validate EEG session data file

    Args:
        session_path: Path to session file (.pkl or .h5)

    Returns:
        Dictionary with validation results

    Raises:
        DataNotFoundError: If file doesn't exist
        ListenerError: If file format is invalid
    """
    import pickle

    session_file = check_file_exists(session_path, "session data")

    # Check file extension
    if session_file.suffix not in ['.pkl', '.h5', '.hdf5']:
        raise ListenerError(
            f"Invalid session file format: {session_file.suffix}",
            "Session files must be .pkl or .h5 format"
        )

    # Try to load and validate
    try:
        if session_file.suffix == '.pkl':
            with open(session_file, 'rb') as f:
                data = pickle.load(f)

            # Check required fields
            required_fields = ['raw_eeg', 'sampling_rate', 'channels']
            missing = [f for f in required_fields if f not in data]

            if missing:
                raise ListenerError(
                    f"Invalid session data: missing fields {missing}",
                    "Session file may be corrupted. Try regenerating the data."
                )

            return {
                'valid': True,
                'format': 'pkl',
                'channels': data.get('channels', []),
                'sampling_rate': data.get('sampling_rate', 0),
                'duration': len(data.get('raw_eeg', [])) / data.get('sampling_rate', 1) if 'raw_eeg' in data else 0
            }

        elif session_file.suffix in ['.h5', '.hdf5']:
            import h5py

            with h5py.File(session_file, 'r') as f:
                return {
                    'valid': True,
                    'format': 'h5',
                    'keys': list(f.keys())
                }

    except Exception as e:
        raise ListenerError(
            f"Failed to validate session data: {e}",
            "File may be corrupted. Try regenerating the data."
        )


def print_system_info():
    """Print system information for debugging"""
    import platform
    import torch

    print("\n" + "="*60)
    print("System Information")
    print("="*60)

    print(f"\nPython: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")

    if torch.cuda.is_available():
        print(f"\nGPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA: {torch.version.cuda}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("\nGPU: Not available (using CPU)")

    print("="*60 + "\n")


# Context manager for better error handling
class ErrorContext:
    """Context manager for handling errors with helpful messages"""

    def __init__(self, operation: str, cleanup=None):
        self.operation = operation
        self.cleanup = cleanup

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Run cleanup if provided
            if self.cleanup:
                try:
                    self.cleanup()
                except:
                    pass

            # If it's already a ListenerError, just re-raise
            if isinstance(exc_val, ListenerError):
                return False

            # Wrap other exceptions
            raise ListenerError(
                f"Error during {self.operation}: {exc_val}",
                "Check the error message above for details"
            )

        return False
