"""
VAE Training Pipeline

Handles:
- Loading features from multiple sessions
- Training loop with validation
- Checkpointing (save every N epochs to track evolution)
- Loss monitoring and visualization
- Early stopping

This is where the AI learns the unique meditation "signature".
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from tqdm import tqdm
import json
from datetime import datetime

from .vae import MeditationVAE, VAEConfig, vae_loss


class MeditationDataset(Dataset):
    """
    Dataset for meditation EEG features.

    Loads features from multiple session files (.h5) and
    creates a unified dataset for training.
    """

    def __init__(self, feature_files: List[str]):
        """
        Initialize dataset.

        Args:
            feature_files: List of paths to feature .h5 files
        """
        self.features = []
        self.session_ids = []

        print(f"📂 Loading {len(feature_files)} sessions...")

        for i, file_path in enumerate(feature_files):
            # Load features
            df = pd.read_hdf(file_path, key='features')

            # Remove metadata columns
            feature_cols = [c for c in df.columns if c not in ['timestamp', 'window_idx']]
            features = df[feature_cols].values

            # Store
            self.features.append(features)
            self.session_ids.extend([i] * len(features))

            print(f"   Session {i+1}: {len(features)} windows from {Path(file_path).name}")

        # Concatenate all sessions
        self.features = np.vstack(self.features).astype(np.float32)
        self.session_ids = np.array(self.session_ids)

        print(f"✅ Dataset loaded: {len(self.features)} total windows from {len(feature_files)} sessions")
        print(f"   Feature dimension: {self.features.shape[1]}")

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return torch.from_numpy(self.features[idx])

    def get_feature_stats(self) -> Dict:
        """Get dataset statistics."""
        return {
            'mean': np.mean(self.features, axis=0),
            'std': np.std(self.features, axis=0),
            'min': np.min(self.features, axis=0),
            'max': np.max(self.features, axis=0)
        }


class VAETrainer:
    """
    Train Meditation VAE on collected sessions.

    Features:
    - Automatic train/val split
    - Checkpointing every N epochs (track evolution)
    - Early stopping (prevent overfitting)
    - Loss monitoring and logging

    Usage:
        trainer = VAETrainer(config, checkpoint_dir="data/checkpoints")
        trainer.load_data(feature_files)
        trainer.train(num_epochs=100)
    """

    def __init__(
        self,
        config: VAEConfig,
        checkpoint_dir: str = "data/checkpoints",
        device: Optional[str] = None
    ):
        """
        Initialize trainer.

        Args:
            config: VAE configuration
            checkpoint_dir: Directory to save checkpoints
            device: Device to train on (auto-detect if None)
        """
        self.config = config
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"🎯 Training device: {self.device}")

        # Model
        self.model = MeditationVAE(config).to(self.device)
        self.optimizer = None
        self.scheduler = None

        # Training state
        self.train_loader = None
        self.val_loader = None
        self.history = {
            'train_loss': [],
            'train_recon': [],
            'train_kl': [],
            'val_loss': [],
            'val_recon': [],
            'val_kl': []
        }

        print(f"🧠 Model initialized with {sum(p.numel() for p in self.model.parameters()):,} parameters")

    def load_data(
        self,
        feature_files: List[str],
        train_ratio: float = 0.8,
        batch_size: int = 32,
        shuffle: bool = True
    ):
        """
        Load and prepare data for training.

        Args:
            feature_files: List of feature .h5 files
            train_ratio: Ratio of data for training (rest for validation)
            batch_size: Batch size for training
            shuffle: Shuffle data
        """
        # Create dataset
        dataset = MeditationDataset(feature_files)

        # Split train/val
        train_size = int(len(dataset) * train_ratio)
        val_size = len(dataset) - train_size

        train_dataset, val_dataset = random_split(
            dataset,
            [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )

        print(f"\n📊 Data split:")
        print(f"   Training: {train_size} windows ({train_ratio*100:.0f}%)")
        print(f"   Validation: {val_size} windows ({(1-train_ratio)*100:.0f}%)")

        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=0
        )

        self.val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )

        print(f"   Batch size: {batch_size}")
        print(f"   Training batches: {len(self.train_loader)}")

    def configure_optimizer(
        self,
        learning_rate: float = 0.001,
        optimizer_type: str = "adam"
    ):
        """Configure optimizer and learning rate scheduler."""
        if optimizer_type.lower() == "adam":
            self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        elif optimizer_type.lower() == "adamw":
            self.optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)
        else:
            self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        # Learning rate scheduler (reduce on plateau)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=10,
            verbose=True
        )

        print(f"⚙️  Optimizer: {optimizer_type}, LR: {learning_rate}")

    def train_epoch(self) -> Tuple[float, float, float]:
        """Train for one epoch."""
        self.model.train()

        total_loss = 0
        total_recon = 0
        total_kl = 0
        n_batches = 0

        for batch in self.train_loader:
            batch = batch.to(self.device)

            # Forward pass
            recon, mu, logvar = self.model(batch)
            loss, recon_loss, kl_loss = vae_loss(
                recon, batch, mu, logvar,
                beta=self.config.beta
            )

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Accumulate losses
            total_loss += loss.item()
            total_recon += recon_loss.item()
            total_kl += kl_loss.item()
            n_batches += 1

        # Average losses
        avg_loss = total_loss / n_batches
        avg_recon = total_recon / n_batches
        avg_kl = total_kl / n_batches

        return avg_loss, avg_recon, avg_kl

    @torch.no_grad()
    def validate(self) -> Tuple[float, float, float]:
        """Validate on validation set."""
        self.model.eval()

        total_loss = 0
        total_recon = 0
        total_kl = 0
        n_batches = 0

        for batch in self.val_loader:
            batch = batch.to(self.device)

            # Forward pass
            recon, mu, logvar = self.model(batch)
            loss, recon_loss, kl_loss = vae_loss(
                recon, batch, mu, logvar,
                beta=self.config.beta
            )

            # Accumulate losses
            total_loss += loss.item()
            total_recon += recon_loss.item()
            total_kl += kl_loss.item()
            n_batches += 1

        # Average losses
        avg_loss = total_loss / n_batches
        avg_recon = total_recon / n_batches
        avg_kl = total_kl / n_batches

        return avg_loss, avg_recon, avg_kl

    def save_checkpoint(self, epoch: int, val_loss: float, is_best: bool = False):
        """
        Save model checkpoint.

        Saves every N epochs to track evolution of AI companion.
        """
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config.__dict__,
            'history': self.history,
            'val_loss': val_loss
        }

        # Save regular checkpoint
        checkpoint_path = self.checkpoint_dir / f"checkpoint_epoch_{epoch:03d}.pt"
        torch.save(checkpoint, checkpoint_path)

        # Save best model
        if is_best:
            best_path = self.checkpoint_dir / "best_model.pt"
            torch.save(checkpoint, best_path)
            print(f"   💎 New best model saved (val_loss: {val_loss:.4f})")

    def train(
        self,
        num_epochs: int = 100,
        save_every: int = 10,
        patience: int = 20
    ):
        """
        Full training loop.

        Args:
            num_epochs: Number of epochs to train
            save_every: Save checkpoint every N epochs
            patience: Early stopping patience
        """
        if self.train_loader is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        if self.optimizer is None:
            self.configure_optimizer()

        print(f"\n🚀 Starting training...")
        print(f"   Epochs: {num_epochs}")
        print(f"   Save every: {save_every} epochs")
        print(f"   Early stopping patience: {patience}")
        print(f"   Beta (KL weight): {self.config.beta}")

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(1, num_epochs + 1):
            # Train
            train_loss, train_recon, train_kl = self.train_epoch()

            # Validate
            val_loss, val_recon, val_kl = self.validate()

            # Update scheduler
            self.scheduler.step(val_loss)

            # Record history
            self.history['train_loss'].append(train_loss)
            self.history['train_recon'].append(train_recon)
            self.history['train_kl'].append(train_kl)
            self.history['val_loss'].append(val_loss)
            self.history['val_recon'].append(val_recon)
            self.history['val_kl'].append(val_kl)

            # Print progress
            print(f"\nEpoch {epoch}/{num_epochs}")
            print(f"   Train - Loss: {train_loss:.4f}, Recon: {train_recon:.4f}, KL: {train_kl:.4f}")
            print(f"   Val   - Loss: {val_loss:.4f}, Recon: {val_recon:.4f}, KL: {val_kl:.4f}")

            # Check if best model
            is_best = val_loss < best_val_loss
            if is_best:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            # Save checkpoint
            if epoch % save_every == 0 or is_best:
                self.save_checkpoint(epoch, val_loss, is_best)
                print(f"   💾 Checkpoint saved: epoch_{epoch:03d}")

            # Early stopping
            if patience_counter >= patience:
                print(f"\n⚠️  Early stopping triggered (patience: {patience})")
                print(f"   Best val loss: {best_val_loss:.4f} at epoch {epoch - patience}")
                break

        print(f"\n✅ Training complete!")
        print(f"   Best validation loss: {best_val_loss:.4f}")

        # Save final training history
        history_path = self.checkpoint_dir / "training_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)

        print(f"   Training history saved: {history_path}")

    def load_checkpoint(self, checkpoint_path: str):
        """Load model from checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.history = checkpoint['history']

        print(f"✅ Checkpoint loaded: {checkpoint_path}")
        print(f"   Epoch: {checkpoint['epoch']}")
        print(f"   Val loss: {checkpoint['val_loss']:.4f}")


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    from glob import glob

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
                       help="Latent dimension")
    parser.add_argument("--beta", type=float, default=1.0,
                       help="Beta parameter for KL divergence")

    args = parser.parse_args()

    # Find all feature files
    feature_files = glob(f"{args.data_dir}/*.h5")

    if len(feature_files) == 0:
        print(f"❌ No feature files found in {args.data_dir}")
        print("   Run feature extraction first!")
        exit(1)

    print(f"Found {len(feature_files)} feature files")

    # Create config
    config = VAEConfig(
        input_dim=34,  # Will be auto-detected from data
        latent_dim=args.latent_dim,
        beta=args.beta
    )

    # Create trainer
    trainer = VAETrainer(config, checkpoint_dir=args.checkpoint_dir)

    # Load data
    trainer.load_data(feature_files, batch_size=args.batch_size)

    # Configure optimizer
    trainer.configure_optimizer(learning_rate=args.lr)

    # Train
    trainer.train(num_epochs=args.epochs, save_every=10)

    print("\n🎉 Training complete!")
