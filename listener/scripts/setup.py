#!/usr/bin/env python3
"""
THE LISTENER - Interactive Setup Wizard

Automates initial project setup:
- Creates directory structure
- Generates config file from template
- Validates dependencies
- Tests GPU setup (if available)
- Generates sample data for testing

Usage:
    python scripts/setup.py [--quick] [--skip-api-keys]

Options:
    --quick          Skip interactive prompts, use defaults
    --skip-api-keys  Skip API key configuration (for local-only setup)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def create_directory_structure(base_dir: Path):
    """Create all necessary directories for the project"""
    print_header("Creating Directory Structure")

    directories = [
        "data/raw/eeg",
        "data/raw/sessions",
        "data/processed/features",
        "data/processed/vae_latents",
        "data/checkpoints",
        "data/outputs/images",
        "data/outputs/videos",
        "data/outputs/audio",
        "data/outputs/gallery",
        "data/baselines",
        "data/cache",
        "logs",
    ]

    created_count = 0
    existing_count = 0

    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {directory}")
            created_count += 1
        else:
            print_info(f"Already exists: {directory}")
            existing_count += 1

    # Create .gitkeep files in data directories (but not in logs)
    for directory in directories:
        if directory.startswith("data"):
            gitkeep_path = base_dir / directory / ".gitkeep"
            gitkeep_path.touch(exist_ok=True)

    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC} Created {created_count} new directories, {existing_count} already existed")
    return True

def check_dependencies() -> Dict[str, Any]:
    """Check for required Python packages and system dependencies"""
    print_header("Checking Dependencies")

    results = {
        "python_packages": {},
        "system": {},
        "optional": {}
    }

    # Required Python packages
    required_packages = {
        "numpy": "numpy",
        "torch": "torch",
        "mne": "mne",
        "anthropic": "anthropic",
        "replicate": "replicate",
        "PyYAML": "yaml",
        "matplotlib": "matplotlib",
        "scipy": "scipy",
    }

    print(f"{Colors.BOLD}Required Python packages:{Colors.ENDC}")
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print_success(f"{package_name} installed")
            results["python_packages"][package_name] = True
        except ImportError:
            print_error(f"{package_name} NOT installed")
            results["python_packages"][package_name] = False

    # Optional packages
    optional_packages = {
        "TTS": "TTS (Coqui)",
        "diffusers": "diffusers (local Stable Diffusion)",
        "transformers": "transformers",
        "accelerate": "accelerate",
    }

    print(f"\n{Colors.BOLD}Optional Python packages:{Colors.ENDC}")
    for import_name, display_name in optional_packages.items():
        try:
            __import__(import_name)
            print_success(f"{display_name} installed")
            results["optional"][display_name] = True
        except ImportError:
            print_warning(f"{display_name} NOT installed (optional)")
            results["optional"][display_name] = False

    # Check for CUDA
    print(f"\n{Colors.BOLD}GPU Support:{Colors.ENDC}")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            print_success(f"CUDA available: {gpu_name} ({vram_gb:.1f} GB VRAM)")
            results["system"]["cuda"] = True
            results["system"]["gpu_name"] = gpu_name
            results["system"]["vram_gb"] = vram_gb
        else:
            print_warning("CUDA not available - will use CPU")
            results["system"]["cuda"] = False
    except:
        print_warning("Could not check CUDA availability")
        results["system"]["cuda"] = False

    # Summary
    missing_required = [pkg for pkg, installed in results["python_packages"].items() if not installed]
    if missing_required:
        print_error(f"\n{len(missing_required)} required packages missing: {', '.join(missing_required)}")
        print_info("Install with: pip install -r requirements.txt")
        return results
    else:
        print_success(f"\nAll required packages installed!")

    return results

def create_config_file(base_dir: Path, quick_mode: bool = False, skip_api_keys: bool = False):
    """Create config.yaml from template with user inputs"""
    print_header("Creating Configuration File")

    config_path = base_dir / "config.yaml"
    example_path = base_dir / "config.example.yaml"

    if config_path.exists():
        overwrite = "y" if quick_mode else get_input(
            "config.yaml already exists. Overwrite? (y/N)",
            default="N"
        )
        if overwrite.lower() != "y":
            print_info("Keeping existing config.yaml")
            return True

    # Load template
    with open(example_path, 'r') as f:
        config = yaml.safe_load(f)

    if not quick_mode and not skip_api_keys:
        print(f"\n{Colors.BOLD}API Configuration{Colors.ENDC}")
        print("You can get API keys from:")
        print("  - Anthropic Claude: https://console.anthropic.com/")
        print("  - Replicate: https://replicate.com/account")
        print("\nPress Enter to skip (you can add them later)")

        # Anthropic API key
        anthropic_key = get_input("\nAnthropic API key", default="")
        if anthropic_key:
            config["anthropic"]["api_key"] = anthropic_key

        # Replicate API key
        replicate_key = get_input("Replicate API key", default="")
        if replicate_key:
            config["replicate"]["api_key"] = replicate_key

        # Project settings
        print(f"\n{Colors.BOLD}Project Settings{Colors.ENDC}")
        practitioner = get_input("Your name (for single-subject training)", default="Practitioner")
        if practitioner:
            config["project"]["practitioner"] = practitioner

        # Powerline frequency
        print(f"\n{Colors.BOLD}Signal Processing{Colors.ENDC}")
        region = get_input("Region (US/EU) for powerline noise removal", default="US")
        if region.upper() == "EU":
            config["preprocessing"]["notch_freq"] = 50
        else:
            config["preprocessing"]["notch_freq"] = 60

    # Save config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print_success(f"Created config.yaml")

    if skip_api_keys or (not quick_mode and not (anthropic_key or replicate_key)):
        print_warning("API keys not configured - you can add them later to config.yaml")
        print_info("The project will work in local-only mode without API keys")

    return True

def test_gpu_setup(base_dir: Path):
    """Test GPU setup if available"""
    print_header("Testing GPU Setup")

    try:
        import torch

        if not torch.cuda.is_available():
            print_warning("No GPU available - skipping GPU tests")
            return True

        # Run GPU test script
        test_script = base_dir / "scripts" / "test_gpu_setup.py"
        if test_script.exists():
            print_info("Running GPU validation tests...")
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(base_dir),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print_success("GPU tests passed!")
                print(result.stdout)
            else:
                print_warning("GPU tests completed with warnings")
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
        else:
            print_warning("GPU test script not found")

        return True

    except Exception as e:
        print_error(f"GPU test failed: {e}")
        return False

def generate_sample_data(base_dir: Path, quick_mode: bool = False):
    """Generate sample mock data for testing"""
    print_header("Generating Sample Data")

    if not quick_mode:
        generate = get_input(
            "Generate sample EEG data for testing? (Y/n)",
            default="Y"
        )
        if generate.lower() == "n":
            print_info("Skipping sample data generation")
            return True

    try:
        # Generate one mock session
        print_info("Generating mock EEG session...")
        mock_script = base_dir / "scripts" / "generate_mock_data.py"

        if not mock_script.exists():
            print_warning("Mock data generation script not found")
            return False

        result = subprocess.run(
            [sys.executable, str(mock_script), "--num-sessions", "1", "--duration", "60"],
            cwd=str(base_dir),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_success("Generated 1 minute of sample EEG data")
            print_info("You can generate more with: python scripts/generate_mock_data.py")
        else:
            print_warning("Sample data generation completed with warnings")
            if result.stderr:
                print(result.stderr)

        return True

    except Exception as e:
        print_error(f"Failed to generate sample data: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete!")

    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}\n")

    print(f"{Colors.OKCYAN}1. Configure API keys (if not done):{Colors.ENDC}")
    print("   Edit config.yaml and add your Anthropic and Replicate API keys")
    print("   (Optional - only needed for text/image generation)\n")

    print(f"{Colors.OKCYAN}2. Generate test data:{Colors.ENDC}")
    print("   python scripts/generate_mock_data.py --num-sessions 5 --duration 300\n")

    print(f"{Colors.OKCYAN}3. Train the VAE model:{Colors.ENDC}")
    print("   python scripts/train.py\n")

    print(f"{Colors.OKCYAN}4. Analyze meditation quality:{Colors.ENDC}")
    print("   python scripts/analyze_meditation.py data/raw/sessions/session_001.pkl\n")

    print(f"{Colors.OKCYAN}5. Generate memories (text + images):{Colors.ENDC}")
    print("   python scripts/generate_memories.py --num-memories 3\n")

    print(f"{Colors.BOLD}Documentation:{Colors.ENDC}")
    print("   - Quick Start: docs/QUICK_START.md")
    print("   - Technical Details: docs/TECHNICAL.md")
    print("   - Meditation Science: docs/MEDITATION_SCIENCE.md\n")

    print(f"{Colors.OKGREEN}Setup complete! You're ready to start using THE LISTENER{Colors.ENDC}\n")

def main():
    """Main setup wizard"""
    import argparse

    parser = argparse.ArgumentParser(description="THE LISTENER - Interactive Setup Wizard")
    parser.add_argument("--quick", action="store_true", help="Quick setup with defaults")
    parser.add_argument("--skip-api-keys", action="store_true", help="Skip API key configuration")
    args = parser.parse_args()

    # Get base directory (listener/)
    base_dir = Path(__file__).parent.parent.resolve()

    # Welcome message
    print_header("THE LISTENER - Setup Wizard")
    print("This wizard will help you set up THE LISTENER project.")
    print("It will create directories, configure settings, and validate your environment.\n")

    if args.quick:
        print_info("Running in quick mode with defaults\n")

    # Step 1: Create directories
    if not create_directory_structure(base_dir):
        print_error("Failed to create directory structure")
        return 1

    # Step 2: Check dependencies
    dep_results = check_dependencies()
    missing_required = [pkg for pkg, installed in dep_results["python_packages"].items() if not installed]
    if missing_required:
        print_error("\nCannot proceed without required packages")
        print_info("Install with: pip install -r requirements.txt")
        return 1

    # Step 3: Create config file
    if not create_config_file(base_dir, args.quick, args.skip_api_keys):
        print_error("Failed to create config file")
        return 1

    # Step 4: Test GPU (if available)
    if dep_results["system"].get("cuda"):
        test_gpu_setup(base_dir)

    # Step 5: Generate sample data
    generate_sample_data(base_dir, args.quick)

    # Step 6: Print next steps
    print_next_steps()

    return 0

if __name__ == "__main__":
    sys.exit(main())
