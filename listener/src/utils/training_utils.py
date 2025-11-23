"""
Advanced Training Utilities for Custom Model Training

Provides tools for:
- Hyperparameter optimization (Optuna)
- Experiment tracking (TensorBoard)
- Custom loss functions
- Advanced callbacks
- Model architecture search
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import json


class ExperimentTracker:
    """Track experiments with TensorBoard and JSON logs"""

    def __init__(self, experiment_name: str, log_dir: str = "runs"):
        """
        Initialize experiment tracker

        Args:
            experiment_name: Name of the experiment
            log_dir: Directory for logs
        """
        self.experiment_name = experiment_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # TensorBoard writer
        try:
            from torch.utils.tensorboard import SummaryWriter
            self.writer = SummaryWriter(log_dir=str(self.log_dir / experiment_name))
            self.tensorboard_available = True
        except ImportError:
            print("⚠ TensorBoard not available - install with: pip install tensorboard")
            self.writer = None
            self.tensorboard_available = False

        # JSON log file
        self.json_log_path = self.log_dir / f"{experiment_name}_log.json"
        self.metrics_history = []

    def log_metrics(self, metrics: Dict[str, float], step: int):
        """
        Log metrics to TensorBoard and JSON

        Args:
            metrics: Dictionary of metric names and values
            step: Training step/epoch
        """
        # TensorBoard
        if self.tensorboard_available and self.writer:
            for name, value in metrics.items():
                self.writer.add_scalar(name, value, step)

        # JSON log
        log_entry = {"step": step, **metrics}
        self.metrics_history.append(log_entry)

        # Save to file
        with open(self.json_log_path, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)

    def log_hyperparameters(self, hparams: Dict[str, Any], metrics: Dict[str, float]):
        """
        Log hyperparameters and final metrics

        Args:
            hparams: Hyperparameters dictionary
            metrics: Final metrics
        """
        if self.tensorboard_available and self.writer:
            self.writer.add_hparams(hparams, metrics)

    def log_model_graph(self, model: nn.Module, input_size: tuple):
        """
        Log model architecture to TensorBoard

        Args:
            model: PyTorch model
            input_size: Input tensor size (batch_size, ...)
        """
        if self.tensorboard_available and self.writer:
            dummy_input = torch.randn(input_size)
            try:
                self.writer.add_graph(model, dummy_input)
            except Exception as e:
                print(f"Could not log model graph: {e}")

    def close(self):
        """Close TensorBoard writer"""
        if self.writer:
            self.writer.close()


class CustomLosses:
    """Collection of custom loss functions for EEG/VAE training"""

    @staticmethod
    def weighted_mse_loss(
        output: torch.Tensor,
        target: torch.Tensor,
        weights: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Weighted MSE loss - emphasize certain features

        Args:
            output: Model output
            target: Target values
            weights: Feature weights (same shape as output)

        Returns:
            Weighted MSE loss
        """
        mse = (output - target) ** 2

        if weights is not None:
            mse = mse * weights

        return mse.mean()

    @staticmethod
    def beta_vae_loss(
        recon_x: torch.Tensor,
        x: torch.Tensor,
        mu: torch.Tensor,
        logvar: torch.Tensor,
        beta: float = 1.0
    ) -> tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        β-VAE loss with reconstruction and KL divergence

        Args:
            recon_x: Reconstructed input
            x: Original input
            mu: Latent mean
            logvar: Latent log variance
            beta: KL divergence weight

        Returns:
            Total loss and dictionary of loss components
        """
        # Reconstruction loss
        recon_loss = nn.functional.mse_loss(recon_x, x, reduction='mean')

        # KL divergence
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / x.size(0)

        # Total loss
        total_loss = recon_loss + beta * kl_loss

        losses = {
            'total_loss': total_loss,
            'recon_loss': recon_loss,
            'kl_loss': kl_loss
        }

        return total_loss, losses

    @staticmethod
    def focal_loss(
        inputs: torch.Tensor,
        targets: torch.Tensor,
        alpha: float = 0.25,
        gamma: float = 2.0
    ) -> torch.Tensor:
        """
        Focal loss for imbalanced classification

        Args:
            inputs: Model predictions
            targets: Ground truth labels
            alpha: Weighting factor
            gamma: Focusing parameter

        Returns:
            Focal loss
        """
        bce_loss = nn.functional.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )

        pt = torch.exp(-bce_loss)
        focal_loss = alpha * (1 - pt) ** gamma * bce_loss

        return focal_loss.mean()


class EarlyStopping:
    """Early stopping to prevent overfitting"""

    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 0.0,
        mode: str = 'min'
    ):
        """
        Initialize early stopping

        Args:
            patience: Number of epochs with no improvement to wait
            min_delta: Minimum change to qualify as improvement
            mode: 'min' or 'max' (minimize or maximize metric)
        """
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_score = None
        self.early_stop = False

        self.comparison_op = torch.lt if mode == 'min' else torch.gt

    def __call__(self, metric: float) -> bool:
        """
        Check if training should stop

        Args:
            metric: Validation metric to monitor

        Returns:
            True if training should stop
        """
        if self.best_score is None:
            self.best_score = metric
            return False

        # Check if improved
        if self.mode == 'min':
            improved = metric < (self.best_score - self.min_delta)
        else:
            improved = metric > (self.best_score + self.min_delta)

        if improved:
            self.best_score = metric
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
                print(f"\n⚠ Early stopping triggered after {self.counter} epochs without improvement")
                return True

        return False


class LearningRateScheduler:
    """Custom learning rate scheduling strategies"""

    @staticmethod
    def warmup_cosine_schedule(
        optimizer: torch.optim.Optimizer,
        warmup_epochs: int,
        total_epochs: int,
        min_lr: float = 1e-6
    ):
        """
        Warmup + Cosine annealing learning rate schedule

        Args:
            optimizer: PyTorch optimizer
            warmup_epochs: Number of warmup epochs
            total_epochs: Total training epochs
            min_lr: Minimum learning rate

        Returns:
            Learning rate scheduler
        """
        def lr_lambda(epoch):
            if epoch < warmup_epochs:
                # Linear warmup
                return epoch / warmup_epochs
            else:
                # Cosine annealing
                progress = (epoch - warmup_epochs) / (total_epochs - warmup_epochs)
                return min_lr + 0.5 * (1 - min_lr) * (1 + torch.cos(torch.tensor(progress * 3.14159)))

        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    @staticmethod
    def one_cycle_schedule(
        optimizer: torch.optim.Optimizer,
        max_lr: float,
        total_steps: int,
        pct_start: float = 0.3
    ):
        """
        One Cycle learning rate policy

        Args:
            optimizer: PyTorch optimizer
            max_lr: Maximum learning rate
            total_steps: Total training steps
            pct_start: Percentage of cycle spent increasing LR

        Returns:
            One cycle scheduler
        """
        return torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=max_lr,
            total_steps=total_steps,
            pct_start=pct_start
        )


class GradientClipping:
    """Gradient clipping utilities"""

    @staticmethod
    def clip_grad_norm(
        model: nn.Module,
        max_norm: float = 1.0
    ) -> float:
        """
        Clip gradients by norm

        Args:
            model: PyTorch model
            max_norm: Maximum gradient norm

        Returns:
            Total gradient norm before clipping
        """
        return torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)

    @staticmethod
    def clip_grad_value(
        model: nn.Module,
        clip_value: float = 0.5
    ):
        """
        Clip gradients by value

        Args:
            model: PyTorch model
            clip_value: Maximum absolute gradient value
        """
        torch.nn.utils.clip_grad_value_(model.parameters(), clip_value)


class ModelCheckpoint:
    """Save best models during training"""

    def __init__(
        self,
        checkpoint_dir: str,
        model_name: str,
        mode: str = 'min',
        save_top_k: int = 3
    ):
        """
        Initialize model checkpoint

        Args:
            checkpoint_dir: Directory to save checkpoints
            model_name: Base name for checkpoint files
            mode: 'min' or 'max' (save best based on minimizing or maximizing)
            save_top_k: Number of best checkpoints to keep
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.mode = mode
        self.save_top_k = save_top_k

        self.best_scores = []
        self.checkpoint_files = []

    def save(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        metric: float,
        metadata: Optional[Dict] = None
    ):
        """
        Save checkpoint if it's among the best

        Args:
            model: PyTorch model
            optimizer: Optimizer
            epoch: Current epoch
            metric: Metric to compare
            metadata: Additional metadata to save
        """
        # Check if this is a top-k checkpoint
        should_save = False

        if len(self.best_scores) < self.save_top_k:
            should_save = True
        else:
            if self.mode == 'min':
                worst_score = max(self.best_scores)
                if metric < worst_score:
                    should_save = True
                    # Remove worst checkpoint
                    worst_idx = self.best_scores.index(worst_score)
                    worst_file = self.checkpoint_files[worst_idx]
                    if worst_file.exists():
                        worst_file.unlink()
                    self.best_scores.pop(worst_idx)
                    self.checkpoint_files.pop(worst_idx)
            else:
                worst_score = min(self.best_scores)
                if metric > worst_score:
                    should_save = True
                    worst_idx = self.best_scores.index(worst_score)
                    worst_file = self.checkpoint_files[worst_idx]
                    if worst_file.exists():
                        worst_file.unlink()
                    self.best_scores.pop(worst_idx)
                    self.checkpoint_files.pop(worst_idx)

        if should_save:
            checkpoint_path = self.checkpoint_dir / f"{self.model_name}_epoch{epoch}_metric{metric:.4f}.pt"

            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'metric': metric,
                'metadata': metadata or {}
            }

            torch.save(checkpoint, checkpoint_path)

            self.best_scores.append(metric)
            self.checkpoint_files.append(checkpoint_path)

            print(f"✓ Saved checkpoint: {checkpoint_path.name}")


def print_model_summary(model: nn.Module, input_size: tuple):
    """
    Print detailed model summary

    Args:
        model: PyTorch model
        input_size: Input tensor size (batch_size, ...)
    """
    try:
        from torchinfo import summary
        summary(model, input_size=input_size, device='cpu')
    except ImportError:
        print("⚠ torchinfo not installed - install with: pip install torchinfo")
        print(model)


def count_parameters(model: nn.Module) -> Dict[str, int]:
    """
    Count model parameters

    Args:
        model: PyTorch model

    Returns:
        Dictionary with parameter counts
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        'total': total_params,
        'trainable': trainable_params,
        'non_trainable': total_params - trainable_params
    }
