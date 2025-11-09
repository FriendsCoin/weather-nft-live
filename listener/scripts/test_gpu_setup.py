#!/usr/bin/env python3
"""
Test GPU setup for THE LISTENER

Quick script to verify your RTX 2080 8GB is properly configured
for running Stable Diffusion locally with memory optimizations.

Usage:
    python scripts/test_gpu_setup.py
    python scripts/test_gpu_setup.py --generate-test-image
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import argparse


def check_cuda():
    """Check if CUDA is available."""
    print("\n" + "="*60)
    print("1. CHECKING CUDA AVAILABILITY")
    print("="*60)

    try:
        import torch
        print(f"✅ PyTorch installed: {torch.__version__}")

        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.version.cuda}")
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")

            # Get VRAM
            total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✅ Total VRAM: {total_vram:.1f} GB")

            if total_vram < 7.5:
                print(f"⚠️  Warning: {total_vram:.1f}GB may be tight for some features")
                print(f"   Recommended: Use low-memory config (configs/lowmem_gpu.yaml)")
            elif total_vram >= 8:
                print(f"✅ VRAM sufficient for all features with optimizations")

            return True
        else:
            print("❌ CUDA not available")
            print("   Check your PyTorch installation:")
            print("   pip install torch --index-url https://download.pytorch.org/whl/cu118")
            return False

    except ImportError:
        print("❌ PyTorch not installed")
        print("   Install with: pip install torch torchvision")
        return False


def check_diffusers():
    """Check if diffusers and dependencies are installed."""
    print("\n" + "="*60)
    print("2. CHECKING DIFFUSERS DEPENDENCIES")
    print("="*60)

    packages = {
        "diffusers": "pip install diffusers",
        "transformers": "pip install transformers",
        "accelerate": "pip install accelerate",
    }

    all_installed = True

    for package, install_cmd in packages.items():
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package} installed: {version}")
        except ImportError:
            print(f"❌ {package} not installed")
            print(f"   Install with: {install_cmd}")
            all_installed = False

    return all_installed


def check_xformers():
    """Check if xformers is installed (critical for 8GB VRAM)."""
    print("\n" + "="*60)
    print("3. CHECKING XFORMERS (Critical for 8GB VRAM!)")
    print("="*60)

    try:
        import xformers
        print(f"✅ xformers installed: {xformers.__version__}")
        print(f"   This will save 20-30% VRAM + speed up generation!")
        return True
    except ImportError:
        print("⚠️  xformers not installed (HIGHLY RECOMMENDED for 8GB VRAM)")
        print("   Install with: pip install xformers")
        print("   Or: pip install -r requirements-local-gpu.txt")
        return False


def check_local_generator():
    """Check if LocalImageGenerator can be imported."""
    print("\n" + "="*60)
    print("4. CHECKING LOCAL IMAGE GENERATOR")
    print("="*60)

    try:
        from utils.image_gen_local import LocalImageGenerator
        print("✅ LocalImageGenerator imported successfully")
        return True
    except ImportError as e:
        print(f"❌ LocalImageGenerator import failed: {e}")
        print("   Install missing dependencies with:")
        print("   pip install -r requirements-local-gpu.txt")
        return False


def test_generation(config_path: str = "configs/lowmem_gpu.yaml"):
    """Test actual image generation."""
    print("\n" + "="*60)
    print("5. TESTING IMAGE GENERATION")
    print("="*60)

    try:
        from utils.image_gen_local import LocalImageGenerator
        import torch

        # Show initial VRAM
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            print(f"Initial VRAM: {torch.cuda.memory_allocated()/1024**3:.2f} GB")

        # Initialize generator
        print(f"\nLoading model with config: {config_path}")
        print("This may take 30-60 seconds on first run (downloading model)...")

        gen = LocalImageGenerator(config_path=config_path)

        print("\nGenerating test image (512x512, 20 steps)...")

        # Generate
        image = gen.generate(
            prompt="Waves of stillness dissolving into formless attention, abstract meditation art",
            width=512,
            height=512,
            num_inference_steps=20,
            seed=42,
            save_path="test_gpu_output.png"
        )

        # Show peak VRAM
        if torch.cuda.is_available():
            peak_vram = torch.cuda.max_memory_allocated() / 1024**3
            print(f"\n✅ Generation successful!")
            print(f"   Peak VRAM usage: {peak_vram:.2f} GB")

            if peak_vram > 7.5:
                print(f"   ⚠️  High VRAM usage! Consider enabling more optimizations.")
            else:
                print(f"   ✅ VRAM usage is healthy for 8GB card")

            print(f"\n💾 Test image saved to: test_gpu_output.png")

        return True

    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Test GPU setup for THE LISTENER")
    parser.add_argument(
        "--generate-test-image",
        action="store_true",
        help="Generate a test image (downloads SD model on first run)"
    )
    parser.add_argument(
        "--config",
        default="configs/lowmem_gpu.yaml",
        help="Config file to use (default: configs/lowmem_gpu.yaml)"
    )
    args = parser.parse_args()

    print("\n" + "🔍 THE LISTENER - GPU Setup Test".center(60))
    print("Testing RTX 2080 8GB Configuration\n")

    # Run checks
    results = {
        "CUDA": check_cuda(),
        "Diffusers": check_diffusers(),
        "xformers": check_xformers(),
        "LocalImageGenerator": check_local_generator(),
    }

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    all_good = all(results.values())

    for component, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {component}")

    if all_good:
        print("\n✅ All checks passed! Your GPU is ready.")

        if args.generate_test_image:
            success = test_generation(args.config)
            if success:
                print("\n" + "="*60)
                print("🎉 SETUP COMPLETE - RTX 2080 8GB is fully configured!")
                print("="*60)
                print("\nNext steps:")
                print("1. Review the test image: test_gpu_output.png")
                print("2. Read the optimization guide: docs/LOW_MEMORY_GPU.md")
                print("3. Start generating meditation memories!")
                print("\nExample:")
                print("  python scripts/generate_multimedia.py \\")
                print("    --config configs/lowmem_gpu.yaml \\")
                print("    --use-local-gpu \\")
                print("    --num-samples 10")
        else:
            print("\nRun with --generate-test-image to test actual generation:")
            print("  python scripts/test_gpu_setup.py --generate-test-image")
    else:
        print("\n⚠️  Some components are missing or not configured.")
        print("\nFix missing components:")
        print("  pip install -r requirements-local-gpu.txt")
        print("\nSee full guide:")
        print("  docs/LOW_MEMORY_GPU.md")

    print()


if __name__ == "__main__":
    main()
