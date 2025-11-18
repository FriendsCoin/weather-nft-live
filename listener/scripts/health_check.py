#!/usr/bin/env python3
"""
Health Check - THE LISTENER

Verifies system is correctly configured.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --verbose
    python scripts/health_check.py --fix-dirs  # Create missing directories
"""

import sys
from pathlib import Path
import argparse
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_python_version() -> Tuple[bool, str]:
    """Check Python version >= 3.8"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (Need >= 3.8)"


def check_dependencies() -> Tuple[bool, List[str]]:
    """Check required Python packages are installed"""
    required = {
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'pandas': 'Pandas',
        'torch': 'PyTorch',
        'sklearn': 'scikit-learn',
        'sqlalchemy': 'SQLAlchemy',
        'fastapi': 'FastAPI',
        'pylsl': 'pylsl (Lab Streaming Layer)',
        'mne': 'MNE-Python',
        'plotly': 'Plotly',
        'anthropic': 'Anthropic SDK',
    }

    missing = []
    installed = []

    for module, name in required.items():
        try:
            __import__(module)
            installed.append(name)
        except ImportError:
            missing.append(name)

    all_installed = len(missing) == 0
    return all_installed, missing


def check_optional_dependencies() -> List[str]:
    """Check optional packages"""
    optional = {
        'pygame': 'Pygame (for biofeedback game)',
        'replicate': 'Replicate (for cloud image generation)',
        'umap': 'UMAP (for 3D visualization)',
        'cv2': 'OpenCV (for video generation)',
    }

    installed = []
    for module, name in optional.items():
        try:
            __import__(module)
            installed.append(name)
        except ImportError:
            pass

    return installed


def check_config() -> Tuple[bool, str]:
    """Check configuration loads correctly"""
    try:
        from src.config import config
        return True, f"Loaded from {config.project_root}"
    except Exception as e:
        return False, f"Error: {e}"


def check_directories() -> Tuple[bool, List[str]]:
    """Check required directories exist"""
    try:
        from src.config import config

        dirs_to_check = [
            ('Data', config.data_dir),
            ('Models', config.models_dir),
            ('Exports', config.exports_dir),
            ('Logs', config.logs_dir),
            ('Web', config.web_dir),
        ]

        missing = []
        for name, path in dirs_to_check:
            if not path.exists():
                missing.append(f"{name}: {path}")

        return len(missing) == 0, missing
    except Exception as e:
        return False, [f"Error checking directories: {e}"]


def check_database() -> Tuple[bool, str]:
    """Check database connection"""
    try:
        from src.config import config
        from src.database.session_manager import SessionManager

        # Try to connect
        db_manager = SessionManager()

        # Try a simple query
        with db_manager.get_session() as session:
            from src.database.schema import Session as DBSession
            count = session.query(DBSession).count()

        return True, f"Connected ({count} sessions in database)"
    except Exception as e:
        return False, f"Error: {e}"


def check_api_keys() -> List[Tuple[str, bool]]:
    """Check API keys are configured"""
    try:
        from src.config import config

        keys = [
            ('Anthropic API', config.anthropic_api_key),
            ('Replicate API', config.replicate_api_token),
        ]

        return [(name, key is not None and len(key) > 0) for name, key in keys]
    except:
        return []


def check_muse_connection(timeout: float = 2.0) -> Tuple[bool, str]:
    """Check Muse S LSL stream is available"""
    try:
        import pylsl

        # Try to find EEG stream (short timeout)
        streams = pylsl.resolve_byprop('type', 'EEG', timeout=timeout)

        if streams:
            info = streams[0]
            name = info.name()
            channels = info.channel_count()
            srate = info.nominal_srate()
            return True, f"Found: {name} ({channels} ch, {srate} Hz)"
        else:
            return False, "No EEG stream found (is muselsl running?)"
    except Exception as e:
        return False, f"Error: {e}"


def check_gpu() -> Tuple[bool, str]:
    """Check GPU availability"""
    try:
        import torch

        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return True, f"{device_name} ({memory:.1f} GB)"
        else:
            return False, "CUDA not available (CPU mode)"
    except Exception as e:
        return False, f"Error: {e}"


def check_model_files() -> Tuple[bool, List[str]]:
    """Check VAE model files exist"""
    try:
        from src.config import config

        model_files = [
            config.default_model_path,
            config.models_dir / 'vae_checkpoint.pt',
        ]

        found = []
        missing = []

        for model_path in model_files:
            if model_path.exists():
                size_mb = model_path.stat().st_size / 1024**2
                found.append(f"{model_path.name} ({size_mb:.1f} MB)")
            else:
                missing.append(str(model_path))

        return len(found) > 0, missing
    except Exception as e:
        return False, [f"Error: {e}"]


def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(name: str, passed: bool, details: str = ""):
    """Print check result"""
    status = "✅" if passed else "❌"
    print(f"{status} {name:<30} {details}")


def fix_directories():
    """Create missing directories"""
    try:
        from src.config import config

        dirs_to_create = [
            config.data_dir,
            config.models_dir,
            config.exports_dir,
            config.logs_dir,
        ]

        for path in dirs_to_create:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created: {path}")
            else:
                print(f"⏭️  Exists: {path}")

        return True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Health check for THE LISTENER"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--fix-dirs",
        action="store_true",
        help="Create missing directories"
    )
    parser.add_argument(
        "--skip-muse",
        action="store_true",
        help="Skip Muse S connection check"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  🏥 THE LISTENER - Health Check")
    print("=" * 60)

    # Fix directories if requested
    if args.fix_dirs:
        print_header("Creating Directories")
        fix_directories()
        return

    # Track overall health
    all_critical_passed = True
    warnings = []

    # 1. Python version
    print_header("System")
    passed, details = check_python_version()
    print_check("Python Version", passed, details)
    if not passed:
        all_critical_passed = False

    # 2. Dependencies
    print_header("Dependencies")
    passed, missing = check_dependencies()
    if passed:
        print_check("Required Packages", True, "All installed")
    else:
        print_check("Required Packages", False, f"{len(missing)} missing")
        if args.verbose:
            for pkg in missing:
                print(f"   - {pkg}")
        all_critical_passed = False

    # Optional dependencies
    installed_optional = check_optional_dependencies()
    if installed_optional:
        print_check("Optional Packages", True, f"{len(installed_optional)} installed")
        if args.verbose:
            for pkg in installed_optional:
                print(f"   - {pkg}")

    # 3. Configuration
    print_header("Configuration")
    passed, details = check_config()
    print_check("Config Module", passed, details)
    if not passed:
        all_critical_passed = False

    # 4. Directories
    passed, missing = check_directories()
    if passed:
        print_check("Directories", True, "All exist")
    else:
        print_check("Directories", False, f"{len(missing)} missing")
        if args.verbose:
            for d in missing:
                print(f"   - {d}")
        warnings.append("Run with --fix-dirs to create missing directories")

    # 5. Database
    passed, details = check_database()
    print_check("Database", passed, details)
    if not passed:
        all_critical_passed = False

    # 6. API Keys
    print_header("API Keys")
    api_keys = check_api_keys()
    for name, configured in api_keys:
        print_check(name, configured, "Configured" if configured else "Not set")
        if not configured:
            warnings.append(f"{name} not configured (some features unavailable)")

    # 7. GPU
    print_header("Hardware")
    passed, details = check_gpu()
    print_check("GPU", passed, details)
    if not passed:
        warnings.append("GPU not available - will use CPU (slower)")

    # 8. Model Files
    passed, missing = check_model_files()
    if passed:
        print_check("VAE Models", True, "Found")
    else:
        print_check("VAE Models", False, "Not found")
        warnings.append("No VAE model found - train one first with scripts/train.py")

    # 9. Muse Connection (optional check)
    if not args.skip_muse:
        print_header("EEG Device")
        passed, details = check_muse_connection(timeout=2.0)
        print_check("Muse S Stream", passed, details)
        if not passed:
            warnings.append("No Muse S stream - start with: muselsl stream")

    # Summary
    print_header("Summary")

    if all_critical_passed and len(warnings) == 0:
        print("\n🎉 All checks passed! System is ready.\n")
        sys.exit(0)
    elif all_critical_passed:
        print("\n⚠️  System is functional but has warnings:\n")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
        sys.exit(0)
    else:
        print("\n❌ Critical issues found. Please fix before using THE LISTENER.\n")
        if warnings:
            print("Warnings:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
            print()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
        sys.exit(0)
