#!/usr/bin/env python3
"""
NESCIENCE Validation Script

Checks that everything is ready to run NESCIENCE dashboard and sessions.

Usage:
    python validate_setup.py
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version >= 3.8"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ✗ Python 3.8+ required")
        return False

    print("  ✓ Python version OK")
    return True


def check_dependencies():
    """Check critical dependencies are installed"""
    print("\nChecking dependencies...")

    required = {
        # Core
        'numpy': 'Numerical computing',
        'scipy': 'Signal processing',

        # Web dashboard
        'flask': 'Web server',
        'flask_socketio': 'WebSocket support',
        'flask_cors': 'CORS support',

        # OSC integration
        'pythonosc': 'OSC protocol (Mind Monitor)',

        # ML (optional but recommended)
        'torch': 'PyTorch (for VAE)',

        # API
        'anthropic': 'Claude API (for interpretations)',
    }

    missing = []
    optional_missing = []

    for module, description in required.items():
        try:
            __import__(module)
            print(f"  ✓ {module:20} - {description}")
        except ImportError:
            if module in ['torch', 'anthropic']:
                optional_missing.append((module, description))
                print(f"  ⚠ {module:20} - {description} (optional)")
            else:
                missing.append((module, description))
                print(f"  ✗ {module:20} - {description} (REQUIRED)")

    if missing:
        print(f"\n✗ Missing {len(missing)} required dependencies")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False

    if optional_missing:
        print(f"\n⚠ {len(optional_missing)} optional dependencies missing")
        print("  (Install later if needed)")

    print("\n✓ All required dependencies installed")
    return True


def check_directory_structure():
    """Check that directory structure exists"""
    print("\nChecking directory structure...")

    base_dir = Path(__file__).parent

    required_dirs = [
        'src/nescience',
        'src/integrations',
        'src/web',
        'src/web/templates',
        'src/utils',
        'scripts',
        'docs',
    ]

    required_files = [
        'start_dashboard.py',
        'src/web/nescience_server.py',
        'src/web/templates/nescience_hub.html',
        'src/nescience/character_evolution.py',
        'src/nescience/meditation_states.py',
        'src/integrations/osc_bridge.py',
        'scripts/nescience_session.py',
        'scripts/test_osc.py',
    ]

    all_ok = True

    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (MISSING)")
            all_ok = False

    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (MISSING)")
            all_ok = False

    if all_ok:
        print("\n✓ Directory structure OK")
    else:
        print("\n✗ Some files/directories missing")

    return all_ok


def check_data_directories():
    """Check/create data directories"""
    print("\nChecking data directories...")

    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'

    data_dirs = [
        'data',
        'data/sessions',
        'data/checkpoints',
        'data/outputs',
    ]

    for dir_path in data_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  + Created {dir_path}")
            except Exception as e:
                print(f"  ✗ Could not create {dir_path}: {e}")
                return False

    print("\n✓ Data directories OK")
    return True


def check_imports():
    """Try importing key modules"""
    print("\nChecking NESCIENCE modules...")

    sys.path.insert(0, str(Path(__file__).parent / 'src'))

    modules = [
        ('nescience.character_evolution', 'Character evolution system'),
        ('nescience.meditation_states', 'Meditation states classifier'),
        ('nescience.poetic_interpreter', 'Poetic interpreter'),
        ('integrations.osc_bridge', 'OSC bridge (Mind Monitor)'),
        ('utils.session_utils', 'Session utilities'),
        ('web.nescience_server', 'Dashboard server'),
    ]

    all_ok = True

    for module, description in modules:
        try:
            __import__(module)
            print(f"  ✓ {module:35} - {description}")
        except ImportError as e:
            print(f"  ✗ {module:35} - {description}")
            print(f"    Error: {e}")
            all_ok = False

    if all_ok:
        print("\n✓ All NESCIENCE modules import successfully")
    else:
        print("\n✗ Some modules failed to import")
        print("  Make sure dependencies are installed:")
        print("  pip install -r requirements.txt")

    return all_ok


def print_summary(results):
    """Print validation summary"""
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60 + "\n")

    all_ok = all(results.values())

    for check, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {check}")

    print("\n" + "="*60)

    if all_ok:
        print("✓ ALL CHECKS PASSED")
        print("\nReady to run NESCIENCE!")
        print("\nNext steps:")
        print("  1. Start dashboard:    python start_dashboard.py")
        print("  2. Test OSC:           python scripts/test_osc.py --receive")
        print("  3. First session:      python scripts/nescience_session.py --mock --duration 600")
        print("="*60)
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nFix issues above, then run again:")
        print("  python validate_setup.py")
        print("="*60)
        return 1


def main():
    print("="*60)
    print("NESCIENCE - Validation Script")
    print("="*60 + "\n")

    results = {
        'Python version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Directory structure': check_directory_structure(),
        'Data directories': check_data_directories(),
        'Module imports': check_imports(),
    }

    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
