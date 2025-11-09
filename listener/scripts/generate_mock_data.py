#!/usr/bin/env python3
"""
Generate mock EEG data for testing THE LISTENER pipeline.

Creates realistic synthetic meditation sessions so you can test
the entire system before connecting real Muse S hardware.

Usage:
    python scripts/generate_mock_data.py --num-sessions 10 --duration 300
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.eeg_capture import MockEEGGenerator
from pipeline.preprocessing import EEGPreprocessor
from pipeline.feature_extraction import FeatureExtractor
import argparse


def main():
    parser = argparse.ArgumentParser(description="Generate mock EEG sessions")
    parser.add_argument("--num-sessions", type=int, default=10,
                       help="Number of sessions to generate")
    parser.add_argument("--duration", type=int, default=300,
                       help="Duration per session (seconds)")
    parser.add_argument("--output-dir", default="data",
                       help="Output directory")

    args = parser.parse_args()

    print("=" * 60)
    print("THE LISTENER - Mock Data Generation")
    print("=" * 60)

    # Initialize components
    generator = MockEEGGenerator(output_dir=f"{args.output_dir}/raw")
    preprocessor = EEGPreprocessor()
    extractor = FeatureExtractor(window_size=4.0, overlap=0.5)

    # Quality progression (simulate getting deeper into meditation over time)
    qualities = ["restless", "restless", "medium", "medium", "medium",
                "medium", "deep", "deep", "deep", "deep"]

    for i in range(args.num_sessions):
        session_num = i + 1
        quality = qualities[min(i, len(qualities)-1)]

        print(f"\n{'='*60}")
        print(f"Session {session_num}/{args.num_sessions}")
        print(f"{'='*60}")

        # 1. Generate raw EEG
        raw_file = generator.generate_session(
            duration=args.duration,
            session_name=f"session_{session_num:03d}",
            meditation_quality=quality
        )

        # 2. Preprocess
        preprocessor.load_session(str(raw_file))
        preprocessor.apply_filters(use_mne=False)  # Use scipy for portability
        preprocessor.remove_artifacts(method="simple")
        preprocessor.normalize(method="z-score")

        clean_file = Path(args.output_dir) / "processed" / f"session_{session_num:03d}_clean.csv"
        preprocessor.save(str(clean_file))

        # 3. Extract features
        features = extractor.extract_from_file(str(clean_file))
        extractor.summarize_features(features)

        features_file = Path(args.output_dir) / "sessions" / f"session_{session_num:03d}_features.h5"
        extractor.save_features(features, str(features_file))

        print(f"\n✅ Session {session_num} complete!")

    print(f"\n{'='*60}")
    print(f"✅ All {args.num_sessions} sessions generated!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("  1. Train VAE: python scripts/train.py")
    print("  2. Generate memories: python scripts/generate_memories.py")


if __name__ == "__main__":
    main()
