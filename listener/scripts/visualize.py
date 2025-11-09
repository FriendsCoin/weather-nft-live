#!/usr/bin/env python3
"""
Visualize THE LISTENER training and latent space.

Usage:
    python scripts/visualize.py --history data/checkpoints/training_history.json
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.visualization import Visualizer
import argparse


def main():
    parser = argparse.ArgumentParser(description="Visualize THE LISTENER")
    parser.add_argument("--history", help="Path to training_history.json")
    parser.add_argument("--output", help="Output path for figure")

    args = parser.parse_args()

    viz = Visualizer(style="dark_background", dpi=150)

    if args.history:
        if not Path(args.history).exists():
            print(f"❌ History file not found: {args.history}")
            sys.exit(1)

        viz.plot_training_history(args.history, save_path=args.output)

    else:
        print("Usage: python scripts/visualize.py --history <path-to-history.json>")


if __name__ == "__main__":
    main()
