"""
Centralized Configuration for THE LISTENER

Manages all configuration settings including:
- Database connection
- API keys
- File paths
- Application settings

Loads from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional


# ============================================================
# PATHS
# ============================================================

def get_project_root() -> Path:
    """Get project root directory"""
    # Assumes this file is in src/
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Get data directory"""
    data_dir = Path(os.getenv('LISTENER_DATA_DIR', get_project_root() / 'data'))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_models_dir() -> Path:
    """Get models directory"""
    models_dir = Path(os.getenv('LISTENER_MODELS_DIR', get_project_root() / 'models'))
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def get_exports_dir() -> Path:
    """Get exports directory"""
    exports_dir = Path(os.getenv('LISTENER_EXPORTS_DIR', get_project_root() / 'exports'))
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir


def get_logs_dir() -> Path:
    """Get logs directory"""
    logs_dir = Path(os.getenv('LISTENER_LOGS_DIR', get_project_root() / 'logs'))
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


# ============================================================
# DATABASE
# ============================================================

def get_database_url() -> str:
    """
    Get database connection URL

    Priority:
    1. LISTENER_DATABASE_URL environment variable
    2. Default: SQLite in data directory

    Examples:
        sqlite:///path/to/listener.db
        postgresql://user:pass@localhost/listener
        mysql://user:pass@localhost/listener
    """
    default_db = f"sqlite:///{get_data_dir() / 'listener.db'}"
    return os.getenv('LISTENER_DATABASE_URL', default_db)


# ============================================================
# API KEYS
# ============================================================

def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key for Claude"""
    return os.getenv('ANTHROPIC_API_KEY')


def get_replicate_api_token() -> Optional[str]:
    """Get Replicate API token for image generation"""
    return os.getenv('REPLICATE_API_TOKEN')


# ============================================================
# EEG SETTINGS
# ============================================================

def get_eeg_sampling_rate() -> float:
    """Get EEG sampling rate (Hz)"""
    return float(os.getenv('LISTENER_EEG_SAMPLING_RATE', '256.0'))


def get_eeg_channels() -> list:
    """Get EEG channel names"""
    default_channels = 'TP9,AF7,AF8,TP10'
    channels_str = os.getenv('LISTENER_EEG_CHANNELS', default_channels)
    return [ch.strip() for ch in channels_str.split(',')]


def get_lsl_stream_name() -> str:
    """Get LSL stream name for EEG device"""
    return os.getenv('LISTENER_LSL_STREAM_NAME', 'Muse')


# ============================================================
# MODEL SETTINGS
# ============================================================

def get_vae_input_dim() -> int:
    """Get VAE input dimension (number of features)"""
    return int(os.getenv('LISTENER_VAE_INPUT_DIM', '34'))


def get_vae_latent_dim() -> int:
    """Get VAE latent dimension"""
    return int(os.getenv('LISTENER_VAE_LATENT_DIM', '32'))


def get_default_model_path() -> Path:
    """Get default VAE model path"""
    default_model = get_models_dir() / 'vae_best.pt'
    model_str = os.getenv('LISTENER_DEFAULT_MODEL', str(default_model))
    return Path(model_str)


# ============================================================
# WEB DASHBOARD
# ============================================================

def get_api_host() -> str:
    """Get API server host"""
    return os.getenv('LISTENER_API_HOST', '0.0.0.0')


def get_api_port() -> int:
    """Get API server port"""
    return int(os.getenv('LISTENER_API_PORT', '8080'))


def get_web_dir() -> Path:
    """Get web dashboard directory"""
    return get_project_root() / 'web'


# ============================================================
# LOGGING
# ============================================================

def get_log_level() -> str:
    """Get logging level"""
    return os.getenv('LISTENER_LOG_LEVEL', 'INFO').upper()


# ============================================================
# GPU SETTINGS
# ============================================================

def use_gpu() -> bool:
    """Check if GPU should be used"""
    return os.getenv('LISTENER_USE_GPU', 'true').lower() in ('true', '1', 'yes')


def get_gpu_device() -> str:
    """Get GPU device"""
    return os.getenv('LISTENER_GPU_DEVICE', 'cuda:0')


# ============================================================
# CONFIGURATION CLASS
# ============================================================

class Config:
    """
    Configuration singleton

    Usage:
        from src.config import config

        db_url = config.database_url
        api_key = config.anthropic_api_key
    """

    def __init__(self):
        # Paths
        self.project_root = get_project_root()
        self.data_dir = get_data_dir()
        self.models_dir = get_models_dir()
        self.exports_dir = get_exports_dir()
        self.logs_dir = get_logs_dir()
        self.web_dir = get_web_dir()

        # Database
        self.database_url = get_database_url()

        # API Keys
        self.anthropic_api_key = get_anthropic_api_key()
        self.replicate_api_token = get_replicate_api_token()

        # EEG
        self.eeg_sampling_rate = get_eeg_sampling_rate()
        self.eeg_channels = get_eeg_channels()
        self.lsl_stream_name = get_lsl_stream_name()

        # Model
        self.vae_input_dim = get_vae_input_dim()
        self.vae_latent_dim = get_vae_latent_dim()
        self.default_model_path = get_default_model_path()

        # Web
        self.api_host = get_api_host()
        self.api_port = get_api_port()

        # Logging
        self.log_level = get_log_level()

        # GPU
        self.use_gpu = use_gpu()
        self.gpu_device = get_gpu_device()

    def __repr__(self):
        return (
            f"Config(\n"
            f"  database_url='{self.database_url}',\n"
            f"  data_dir='{self.data_dir}',\n"
            f"  models_dir='{self.models_dir}',\n"
            f"  eeg_sampling_rate={self.eeg_sampling_rate},\n"
            f"  log_level='{self.log_level}'\n"
            f")"
        )


# Singleton instance
config = Config()


if __name__ == "__main__":
    """Print current configuration"""
    print("=" * 60)
    print("  THE LISTENER - Configuration")
    print("=" * 60)
    print()
    print(f"Project Root:    {config.project_root}")
    print(f"Data Directory:  {config.data_dir}")
    print(f"Models Directory: {config.models_dir}")
    print(f"Exports Directory: {config.exports_dir}")
    print(f"Logs Directory:  {config.logs_dir}")
    print()
    print(f"Database URL:    {config.database_url}")
    print()
    print(f"EEG Sampling Rate: {config.eeg_sampling_rate} Hz")
    print(f"EEG Channels:    {', '.join(config.eeg_channels)}")
    print(f"LSL Stream Name: {config.lsl_stream_name}")
    print()
    print(f"VAE Input Dim:   {config.vae_input_dim}")
    print(f"VAE Latent Dim:  {config.vae_latent_dim}")
    print(f"Default Model:   {config.default_model_path}")
    print()
    print(f"API Host:        {config.api_host}")
    print(f"API Port:        {config.api_port}")
    print()
    print(f"Log Level:       {config.log_level}")
    print()
    print(f"Use GPU:         {config.use_gpu}")
    if config.use_gpu:
        print(f"GPU Device:      {config.gpu_device}")
    print()
    print(f"Anthropic API:   {'✅ Set' if config.anthropic_api_key else '❌ Not set'}")
    print(f"Replicate API:   {'✅ Set' if config.replicate_api_token else '❌ Not set'}")
    print()
