"""
PyTorch Lightning wrapper for VAE model

Simplifies training with:
- Automatic optimization
- Built-in logging
- Easy callbacks
- Multi-GPU support
- Gradient clipping
- Learning rate scheduling

Usage:
    from models.vae_lightning import VAELightningModule
    from pytorch_lightning import Trainer

    # Create model
    model = VAELightningModule(config, learning_rate=1e-3)

    # Create trainer
    trainer = Trainer(max_epochs=100, gpus=1)

    # Train
    trainer.fit(model, train_loader, val_loader)
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import pytorch_lightning as pl

from .vae import VAE, VAEConfig


class VAELightningModule(pl.LightningModule):
    """PyTorch Lightning wrapper for VAE"""

    def __init__(
        self,
        config: VAEConfig,
        learning_rate: float = 1e-3,
        optimizer_type: str = 'adam',
        scheduler_type: Optional[str] = None,
        warmup_epochs: int = 5,
        gradient_clip_val: float = 1.0
    ):
        """
        Initialize Lightning VAE module

        Args:
            config: VAE configuration
            learning_rate: Learning rate
            optimizer_type: 'adam', 'adamw', or 'sgd'
            scheduler_type: 'cosine', 'plateau', or None
            warmup_epochs: Number of warmup epochs
            gradient_clip_val: Gradient clipping value
        """
        super().__init__()

        self.config = config
        self.learning_rate = learning_rate
        self.optimizer_type = optimizer_type
        self.scheduler_type = scheduler_type
        self.warmup_epochs = warmup_epochs
        self.gradient_clip_val = gradient_clip_val

        # Create VAE model
        self.vae = VAE(config)

        # Save hyperparameters
        self.save_hyperparameters()

    def forward(self, x):
        """Forward pass"""
        return self.vae(x)

    def training_step(self, batch, batch_idx):
        """Training step"""
        x = batch

        # Forward pass
        recon_x, mu, logvar = self(x)

        # Compute loss
        loss, loss_dict = self._compute_loss(recon_x, x, mu, logvar)

        # Log metrics
        self.log('train_loss', loss, prog_bar=True)
        self.log('train_recon_loss', loss_dict['recon_loss'])
        self.log('train_kl_loss', loss_dict['kl_loss'])

        return loss

    def validation_step(self, batch, batch_idx):
        """Validation step"""
        x = batch

        # Forward pass
        recon_x, mu, logvar = self(x)

        # Compute loss
        loss, loss_dict = self._compute_loss(recon_x, x, mu, logvar)

        # Log metrics
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_recon_loss', loss_dict['recon_loss'])
        self.log('val_kl_loss', loss_dict['kl_loss'])

        return loss

    def _compute_loss(self, recon_x, x, mu, logvar):
        """Compute VAE loss"""
        # Reconstruction loss
        recon_loss = nn.functional.mse_loss(recon_x, x, reduction='mean')

        # KL divergence
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / x.size(0)

        # Total loss with beta weighting
        total_loss = recon_loss + self.config.beta * kl_loss

        loss_dict = {
            'recon_loss': recon_loss,
            'kl_loss': kl_loss
        }

        return total_loss, loss_dict

    def configure_optimizers(self):
        """Configure optimizers and learning rate schedulers"""
        # Optimizer
        if self.optimizer_type.lower() == 'adam':
            optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        elif self.optimizer_type.lower() == 'adamw':
            optimizer = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        elif self.optimizer_type.lower() == 'sgd':
            optimizer = torch.optim.SGD(self.parameters(), lr=self.learning_rate, momentum=0.9)
        else:
            raise ValueError(f"Unknown optimizer: {self.optimizer_type}")

        # Scheduler
        if self.scheduler_type is None:
            return optimizer

        if self.scheduler_type.lower() == 'cosine':
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=self.trainer.max_epochs,
                eta_min=self.learning_rate * 0.01
            )
            return [optimizer], [scheduler]

        elif self.scheduler_type.lower() == 'plateau':
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode='min',
                factor=0.5,
                patience=10,
                verbose=True
            )
            return {
                'optimizer': optimizer,
                'lr_scheduler': {
                    'scheduler': scheduler,
                    'monitor': 'val_loss'
                }
            }

        return optimizer

    def on_train_epoch_end(self):
        """Called at the end of training epoch"""
        # Log learning rate
        current_lr = self.optimizers().param_groups[0]['lr']
        self.log('learning_rate', current_lr)


def train_with_lightning(
    config: VAEConfig,
    train_loader,
    val_loader,
    max_epochs: int = 100,
    learning_rate: float = 1e-3,
    device: str = 'cuda',
    checkpoint_dir: str = 'data/checkpoints',
    experiment_name: str = 'vae_training',
    early_stopping_patience: int = 15,
    **trainer_kwargs
):
    """
    Train VAE using PyTorch Lightning

    Args:
        config: VAE configuration
        train_loader: Training data loader
        val_loader: Validation data loader
        max_epochs: Maximum number of epochs
        learning_rate: Learning rate
        device: Device to train on
        checkpoint_dir: Directory for checkpoints
        experiment_name: Name of experiment
        early_stopping_patience: Patience for early stopping
        **trainer_kwargs: Additional arguments for Trainer

    Returns:
        Trained model
    """
    from pytorch_lightning import Trainer
    from pytorch_lightning.callbacks import (
        ModelCheckpoint,
        EarlyStopping,
        LearningRateMonitor
    )
    from pytorch_lightning.loggers import TensorBoardLogger

    # Create model
    model = VAELightningModule(
        config=config,
        learning_rate=learning_rate
    )

    # Callbacks
    callbacks = [
        # Checkpoint callback
        ModelCheckpoint(
            dirpath=checkpoint_dir,
            filename=f'{experiment_name}-{{epoch:02d}}-{{val_loss:.4f}}',
            monitor='val_loss',
            mode='min',
            save_top_k=3,
            verbose=True
        ),

        # Early stopping
        EarlyStopping(
            monitor='val_loss',
            patience=early_stopping_patience,
            mode='min',
            verbose=True
        ),

        # Learning rate monitor
        LearningRateMonitor(logging_interval='epoch')
    ]

    # Logger
    logger = TensorBoardLogger(
        save_dir='runs',
        name=experiment_name
    )

    # Trainer
    trainer = Trainer(
        max_epochs=max_epochs,
        accelerator='gpu' if device == 'cuda' and torch.cuda.is_available() else 'cpu',
        devices=1,
        callbacks=callbacks,
        logger=logger,
        gradient_clip_val=1.0,
        log_every_n_steps=10,
        **trainer_kwargs
    )

    # Train
    trainer.fit(model, train_loader, val_loader)

    print("\n✓ Training complete!")
    print(f"Best checkpoint: {trainer.checkpoint_callback.best_model_path}")

    return model


def load_from_checkpoint(checkpoint_path: str) -> VAELightningModule:
    """
    Load model from checkpoint

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Loaded model
    """
    model = VAELightningModule.load_from_checkpoint(checkpoint_path)
    print(f"✓ Loaded model from: {checkpoint_path}")
    return model
