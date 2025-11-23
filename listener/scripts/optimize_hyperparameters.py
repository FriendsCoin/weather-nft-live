"""
Hyperparameter Optimization using Optuna

Automatically finds best hyperparameters for VAE training.

Usage:
    python scripts/optimize_hyperparameters.py --trials 50 --data-dir data/sessions
"""

import sys
from pathlib import Path
from typing import Dict, Any
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import optuna
from optuna.visualization import (
    plot_optimization_history,
    plot_param_importances,
    plot_slice
)
import torch
from glob import glob

from models.vae import VAEConfig, VAE
from models.trainer import VAETrainer


def objective(trial: optuna.Trial, data_files: list, device: str) -> float:
    """
    Optuna objective function for VAE hyperparameter optimization

    Args:
        trial: Optuna trial object
        data_files: List of training data files
        device: Device to train on ('cuda' or 'cpu')

    Returns:
        Validation loss (to minimize)
    """
    # Suggest hyperparameters
    latent_dim = trial.suggest_int('latent_dim', 16, 64, step=16)
    learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical('batch_size', [16, 32, 64])
    beta = trial.suggest_float('beta', 0.5, 2.0)
    dropout = trial.suggest_float('dropout', 0.0, 0.5)

    # Hidden layer sizes
    encoder_size = trial.suggest_categorical('encoder_size', [64, 128, 256])
    encoder_layers = [encoder_size, encoder_size // 2, encoder_size // 4]

    print(f"\n{'='*60}")
    print(f"Trial {trial.number}")
    print(f"{'='*60}")
    print(f"Hyperparameters:")
    print(f"  latent_dim: {latent_dim}")
    print(f"  learning_rate: {learning_rate:.6f}")
    print(f"  batch_size: {batch_size}")
    print(f"  beta: {beta:.2f}")
    print(f"  dropout: {dropout:.2f}")
    print(f"  encoder_layers: {encoder_layers}")

    # Create VAE config
    config = VAEConfig(
        input_dim=34,
        latent_dim=latent_dim,
        encoder_layers=encoder_layers,
        decoder_layers=encoder_layers[::-1],
        activation="relu",
        dropout=dropout,
        batch_norm=True,
        beta=beta
    )

    # Create trainer
    trainer = VAETrainer(
        config=config,
        checkpoint_dir=f"data/optuna/trial_{trial.number}"
    )

    # Load data
    trainer.load_data(
        feature_files=data_files,
        train_ratio=0.8,
        batch_size=batch_size,
        shuffle=True
    )

    # Configure optimizer
    trainer.configure_optimizer(
        learning_rate=learning_rate,
        optimizer_type="adam"
    )

    # Train for fewer epochs (fast evaluation)
    num_epochs = 30

    try:
        history = trainer.train(
            num_epochs=num_epochs,
            save_every_n_epochs=None,  # Don't save checkpoints
            device=device
        )

        # Get best validation loss
        val_losses = [epoch['val_loss'] for epoch in history]
        best_val_loss = min(val_losses)

        print(f"Best validation loss: {best_val_loss:.4f}")

        # Report intermediate values for pruning
        for epoch, val_loss in enumerate(val_losses):
            trial.report(val_loss, epoch)

            # Prune unpromising trials
            if trial.should_prune():
                raise optuna.TrialPruned()

        return best_val_loss

    except Exception as e:
        print(f"Trial failed: {e}")
        return float('inf')


def main():
    parser = argparse.ArgumentParser(description="Optimize VAE Hyperparameters")
    parser.add_argument(
        "--data-dir",
        default="data/sessions",
        help="Directory containing feature files"
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=50,
        help="Number of optimization trials"
    )
    parser.add_argument(
        "--study-name",
        default="vae_optimization",
        help="Name of the Optuna study"
    )
    parser.add_argument(
        "--device",
        choices=["cuda", "cpu"],
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to train on"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Create visualization plots"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("THE LISTENER - Hyperparameter Optimization")
    print("=" * 60)

    # Find feature files
    feature_files = sorted(glob(f"{args.data_dir}/*.h5"))

    if len(feature_files) == 0:
        print(f"\n❌ No feature files found in {args.data_dir}")
        print("\nGenerate data first:")
        print("  python scripts/generate_mock_data.py --num-sessions 20")
        return 1

    print(f"\nFound {len(feature_files)} sessions")
    print(f"Device: {args.device}")
    print(f"Number of trials: {args.trials}")
    print(f"Study name: {args.study_name}\n")

    # Create Optuna study
    study = optuna.create_study(
        study_name=args.study_name,
        direction="minimize",  # Minimize validation loss
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=5,
            n_warmup_steps=10
        )
    )

    # Optimize
    study.optimize(
        lambda trial: objective(trial, feature_files, args.device),
        n_trials=args.trials,
        show_progress_bar=True
    )

    # Print results
    print("\n" + "=" * 60)
    print("Optimization Complete!")
    print("=" * 60)

    print(f"\nBest trial: {study.best_trial.number}")
    print(f"Best validation loss: {study.best_trial.value:.4f}")
    print("\nBest hyperparameters:")
    for key, value in study.best_trial.params.items():
        print(f"  {key}: {value}")

    # Save best config
    best_config_path = Path("data/optuna") / "best_config.yaml"
    best_config_path.parent.mkdir(parents=True, exist_ok=True)

    import yaml
    with open(best_config_path, 'w') as f:
        yaml.dump(study.best_trial.params, f)

    print(f"\n✓ Best config saved to: {best_config_path}")

    # Visualizations
    if args.visualize:
        print("\nGenerating visualizations...")

        vis_dir = Path("data/optuna/visualizations")
        vis_dir.mkdir(parents=True, exist_ok=True)

        # Optimization history
        fig = plot_optimization_history(study)
        fig.write_html(str(vis_dir / "optimization_history.html"))
        print(f"  - {vis_dir}/optimization_history.html")

        # Parameter importances
        fig = plot_param_importances(study)
        fig.write_html(str(vis_dir / "param_importances.html"))
        print(f"  - {vis_dir}/param_importances.html")

        # Slice plot
        fig = plot_slice(study)
        fig.write_html(str(vis_dir / "param_slices.html"))
        print(f"  - {vis_dir}/param_slices.html")

        print("\n✓ Open visualizations in your browser")

    # Print command to train with best params
    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("\nTrain with best hyperparameters:")
    print(f"  python scripts/train.py \\")
    print(f"    --latent-dim {study.best_trial.params['latent_dim']} \\")
    print(f"    --lr {study.best_trial.params['learning_rate']:.6f} \\")
    print(f"    --batch-size {study.best_trial.params['batch_size']} \\")
    print(f"    --beta {study.best_trial.params['beta']:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
