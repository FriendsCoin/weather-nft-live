#!/usr/bin/env python3
"""
Generate "memories" from trained VAE.

This is Phase 2: The AI creates poetic interpretations and
visual representations of meditation states it has witnessed.

Usage:
    python scripts/generate_memories.py --checkpoint checkpoints/best_model.pt --num-samples 10
"""

import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.sampler import LatentSampler
from utils.llm_interface import LLMInterpreter
from utils.image_gen import ImageGenerator
import argparse


def main():
    parser = argparse.ArgumentParser(description="Generate AI meditation memories")
    parser.add_argument("--checkpoint", default="data/checkpoints/best_model.pt",
                       help="Path to trained model checkpoint")
    parser.add_argument("--num-samples", type=int, default=10,
                       help="Number of memories to generate")
    parser.add_argument("--anthropic-key", help="Anthropic API key")
    parser.add_argument("--replicate-key", help="Replicate API key")
    parser.add_argument("--output-dir", default="data/outputs",
                       help="Output directory")
    parser.add_argument("--skip-images", action="store_true",
                       help="Skip image generation (only text)")

    args = parser.parse_args()

    print("=" * 60)
    print("THE LISTENER - Memory Generation")
    print("=" * 60)

    # Check for checkpoint
    if not Path(args.checkpoint).exists():
        print(f"\n❌ Checkpoint not found: {args.checkpoint}")
        print("\nDid you train the model?")
        print("  python scripts/train.py")
        sys.exit(1)

    # 1. Load VAE sampler
    print("\n[Step 1/3] Loading trained model...")
    sampler = LatentSampler.from_checkpoint(args.checkpoint)

    # 2. Generate samples from latent space
    print(f"\n[Step 2/3] Generating {args.num_samples} samples from latent space...")
    samples = sampler.generate_random_samples(n=args.num_samples)

    # Save samples
    samples_path = Path(args.output_dir) / "samples.json"
    sampler.save_samples(samples, str(samples_path))

    # Create summaries for LLM
    summaries = [sampler.summarize_sample(s) for s in samples]

    print("\n📝 Sample summaries created:")
    for i, summary in enumerate(summaries[:3]):  # Show first 3
        print(f"\n{summary}")

    # 3. Generate poetic interpretations with LLM
    print(f"\n[Step 3/3] Generating poetic interpretations with Claude...")

    try:
        interpreter = LLMInterpreter(
            api_key=args.anthropic_key,
            temperature=0.8
        )

        interpretations = interpreter.interpret_batch(
            sample_summaries=summaries,
            session_numbers=None,
            save_path=str(Path(args.output_dir) / "interpretations.json")
        )

        print("\n🎨 Interpretations generated:")
        for i, interp in enumerate(interpretations[:5]):  # Show first 5
            print(f"\n{i+1}. {interp['text']}")

    except Exception as e:
        print(f"\n⚠️  Could not generate interpretations: {e}")
        print("Set ANTHROPIC_API_KEY environment variable or use --anthropic-key")
        interpretations = []

    # 4. Generate images (optional)
    if not args.skip_images and len(interpretations) > 0:
        print("\n[Step 4/4] Generating visual memories with Stable Diffusion...")

        try:
            generator = ImageGenerator(api_key=args.replicate_key)

            results = generator.generate_batch(
                interpretations=interpretations,
                output_dir=str(Path(args.output_dir) / "images"),
                delay=2.0  # Avoid rate limiting
            )

            # Create gallery
            generator.create_gallery_html(
                results=results,
                interpretations=interpretations,
                output_path=str(Path(args.output_dir) / "gallery.html")
            )

            print(f"\n🖼️  Gallery created! Open: {args.output_dir}/gallery.html")

        except Exception as e:
            print(f"\n⚠️  Could not generate images: {e}")
            print("Set REPLICATE_API_TOKEN environment variable or use --replicate-key")

    print("\n" + "=" * 60)
    print("✅ Memory generation complete!")
    print("=" * 60)
    print(f"\nOutputs saved to: {args.output_dir}/")
    print("  - samples.json: Latent space samples")
    print("  - interpretations.json: Poetic descriptions")
    if not args.skip_images:
        print("  - images/: Generated visual memories")
        print("  - gallery.html: Visual gallery")


if __name__ == "__main__":
    main()
