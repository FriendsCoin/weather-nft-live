#!/usr/bin/env python3
"""
Train the Meditation VAE on collected sessions.

This is where the AI companion learns the unique meditation signature.

Usage:
    python scripts/train.py --epochs 100 --latent-dim 32
"""

import sys
from pathlib import Path
from glob import glob

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.vae import VAEConfig
from models.trainer import VAETrainer
import argparse


def main():
    parser = argparse.ArgumentParser(description="Train Meditation VAE")
    parser.add_argument("--data-dir", default="data/sessions",
                       help="Directory containing feature .h5 files")
    parser.add_argument("--checkpoint-dir", default="data/checkpoints",
                       help="Directory to save checkpoints")
    parser.add_argument("--epochs", type=int, default=100,
                       help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32,
                       help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001,
                       help="Learning rate")
    parser.add_argument("--latent-dim", type=int, default=32,
                       help="Latent space dimension")
    parser.add_argument("--beta", type=float, default=1.0,
                       help="Beta parameter for VAE (KL weight)")
    parser.add_argument("--save-every", type=int, default=10,
                       help="Save checkpoint every N epochs")

    args = parser.parse_args()

    print("=" * 60)
    print("THE LISTENER - VAE Training")
    print("=" * 60)

    # Find feature files
    feature_files = sorted(glob(f"{args.data_dir}/*.h5"))

    if len(feature_files) == 0:
        print(f"\n❌ No feature files found in {args.data_dir}")
        print("\nDid you run feature extraction?")
        print("  For real data: python scripts/process_session.py <session.csv>")
        print("  For mock data: python scripts/generate_mock_data.py")
        sys.exit(1)

    print(f"\n📂 Found {len(feature_files)} sessions:")
    for f in feature_files:
        print(f"   - {Path(f).name}")

    # Create VAE config
    config = VAEConfig(
        input_dim=34,  # Standard feature count
        latent_dim=args.latent_dim,
        encoder_layers=[128, 64, 32],
        decoder_layers=[32, 64, 128],
        activation="relu",
        dropout=0.2,
        batch_norm=True,
        beta=args.beta
    )

    print(f"\n🧠 VAE Configuration:")
    print(f"   Latent dimension: {config.latent_dim}")
    print(f"   Beta (KL weight): {config.beta}")
    print(f"   Encoder: {config.encoder_layers}")
    print(f"   Decoder: {config.decoder_layers}")

    # Create trainer
    trainer = VAETrainer(
        config=config,
        checkpoint_dir=args.checkpoint_dir
    )

    # Load data
    trainer.load_data(
        feature_files=feature_files,
        train_ratio=0.8,
        batch_size=args.batch_size,
        shuffle=True
    )

    # Configure optimizer
    trainer.configure_optimizer(
        learning_rate=args.lr,
        optimizer_type="adam"
    )

    # Train
    trainer.train(
        num_epochs=args.epochs,
        save_every=args.save_every,
        patience=20
    )

    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"  1. View training: python scripts/visualize.py --history {args.checkpoint_dir}/training_history.json")
    print(f"  2. Generate memories: python scripts/generate_memories.py")


if __name__ == "__main__":
    main()
