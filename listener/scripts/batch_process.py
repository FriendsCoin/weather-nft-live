#!/usr/bin/env python3
"""
Batch Process Sessions - THE LISTENER

Process multiple meditation sessions in parallel for 10x speedup.

Usage:
    # Process all sessions in directory
    python scripts/batch_process.py --sessions-dir data/sessions

    # Process with VAE encoding
    python scripts/batch_process.py --sessions-dir data/sessions --vae-model models/vae_model.pt

    # Custom worker count
    python scripts/batch_process.py --sessions-dir data/sessions --workers 8

    # Process specific pattern
    python scripts/batch_process.py --sessions-dir data/sessions --pattern "session_2024*.h5"
"""

import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.pipeline.batch_processor import batch_process_directory


def main():
    parser = argparse.ArgumentParser(
        description="Batch process meditation sessions in parallel"
    )

    parser.add_argument(
        "--sessions-dir",
        type=str,
        required=True,
        help="Directory containing .h5 session files"
    )

    parser.add_argument(
        "--pattern",
        type=str,
        default="*.h5",
        help="File pattern to match (default: *.h5)"
    )

    parser.add_argument(
        "--vae-model",
        type=str,
        help="Path to VAE model for latent encoding (optional)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        help="Number of worker processes (default: CPU count - 1)"
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bars"
    )

    args = parser.parse_args()

    # Validate sessions directory
    sessions_dir = Path(args.sessions_dir)
    if not sessions_dir.exists():
        print(f"❌ Directory not found: {sessions_dir}")
        sys.exit(1)

    # Validate VAE model if provided
    vae_model_path = None
    if args.vae_model:
        vae_model_path = Path(args.vae_model)
        if not vae_model_path.exists():
            print(f"❌ VAE model not found: {vae_model_path}")
            sys.exit(1)

    print("=" * 70)
    print("  🚀 THE LISTENER - Batch Processor")
    print("=" * 70)
    print()

    # Run batch processing
    results = batch_process_directory(
        sessions_dir=sessions_dir,
        pattern=args.pattern,
        n_workers=args.workers,
        vae_model_path=vae_model_path,
        show_progress=not args.no_progress
    )

    # Print detailed results
    print()
    print("=" * 70)
    print("  📊 Processing Results")
    print("=" * 70)
    print()

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed:     {len(failed)}")
    print()

    if failed:
        print("Failed sessions:")
        for result in failed:
            print(f"   - {result.session_id}: {result.error}")
        print()

    # Performance stats
    if successful:
        total_time = sum(r.processing_time for r in results)
        avg_time = total_time / len(results)
        min_time = min(r.processing_time for r in successful)
        max_time = max(r.processing_time for r in successful)

        print("Performance:")
        print(f"   Total time:   {total_time:.1f}s")
        print(f"   Average time: {avg_time:.2f}s per session")
        print(f"   Min time:     {min_time:.2f}s")
        print(f"   Max time:     {max_time:.2f}s")
        print()

        # Speedup estimate
        sequential_time = len(results) * avg_time
        speedup = sequential_time / total_time if total_time > 0 else 1
        print(f"💨 Estimated speedup: {speedup:.1f}x vs sequential processing")
        print()

    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing cancelled\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
