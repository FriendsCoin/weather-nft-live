"""
Visualization Utilities

Tools for visualizing:
- Training progress (loss curves)
- Latent space structure (UMAP projections)
- Feature distributions
- Session evolution over time

These help understand what the AI companion has learned.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import json

# Try to import umap
try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    print("⚠️  umap-learn not installed. Install with: pip install umap-learn")


class Visualizer:
    """
    Visualization tools for THE LISTENER project.

    Usage:
        viz = Visualizer()
        viz.plot_training_history("checkpoints/training_history.json")
        viz.plot_latent_space(latent_vectors, session_ids)
    """

    def __init__(self, style: str = "dark_background", dpi: int = 150):
        """
        Initialize visualizer.

        Args:
            style: Matplotlib style
            dpi: Resolution for saved figures
        """
        plt.style.use(style)
        self.dpi = dpi

        # Color palette for sessions
        self.cmap = plt.cm.viridis

        print(f"📊 Visualizer initialized (style: {style}, dpi: {dpi})")

    def plot_training_history(
        self,
        history_path: str,
        save_path: Optional[str] = None
    ):
        """
        Plot training and validation losses over epochs.

        Args:
            history_path: Path to training_history.json
            save_path: Optional path to save figure
        """
        # Load history
        with open(history_path, 'r') as f:
            history = json.load(f)

        epochs = range(1, len(history['train_loss']) + 1)

        # Create figure
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        # Total loss
        axes[0].plot(epochs, history['train_loss'], label='Train', linewidth=2)
        axes[0].plot(epochs, history['val_loss'], label='Validation', linewidth=2)
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Total Loss')
        axes[0].set_title('Training Progress')
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        # Reconstruction loss
        axes[1].plot(epochs, history['train_recon'], label='Train', linewidth=2)
        axes[1].plot(epochs, history['val_recon'], label='Validation', linewidth=2)
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Reconstruction Loss (MSE)')
        axes[1].set_title('How Well AI Reconstructs Patterns')
        axes[1].legend()
        axes[1].grid(alpha=0.3)

        # KL divergence
        axes[2].plot(epochs, history['train_kl'], label='Train', linewidth=2)
        axes[2].plot(epochs, history['val_kl'], label='Validation', linewidth=2)
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('KL Divergence')
        axes[2].set_title('Latent Space Regularization')
        axes[2].legend()
        axes[2].grid(alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"💾 Training history plot saved: {save_path}")

        plt.show()

    def plot_latent_space(
        self,
        latent_vectors: np.ndarray,
        session_ids: Optional[np.ndarray] = None,
        save_path: Optional[str] = None
    ):
        """
        Visualize latent space using UMAP projection.

        Shows how different meditation sessions cluster in latent space.

        Args:
            latent_vectors: Latent vectors, shape (n_samples, latent_dim)
            session_ids: Session IDs for coloring, shape (n_samples,)
            save_path: Optional path to save figure
        """
        if not UMAP_AVAILABLE:
            print("❌ UMAP not available. Install with: pip install umap-learn")
            return

        print(f"\n🗺️  Computing UMAP projection...")
        print(f"   Input: {latent_vectors.shape[0]} vectors, {latent_vectors.shape[1]} dimensions")

        # Compute UMAP
        reducer = umap.UMAP(
            n_neighbors=15,
            min_dist=0.1,
            metric='euclidean',
            random_state=42
        )

        embedding = reducer.fit_transform(latent_vectors)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 8))

        if session_ids is not None:
            scatter = ax.scatter(
                embedding[:, 0],
                embedding[:, 1],
                c=session_ids,
                cmap=self.cmap,
                alpha=0.6,
                s=20
            )
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Session Number', rotation=270, labelpad=20)
        else:
            ax.scatter(
                embedding[:, 0],
                embedding[:, 1],
                alpha=0.6,
                s=20
            )

        ax.set_xlabel('UMAP Dimension 1')
        ax.set_ylabel('UMAP Dimension 2')
        ax.set_title('Latent Space Landscape\n(Each point = meditation moment)')
        ax.grid(alpha=0.2)

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"💾 Latent space plot saved: {save_path}")

        plt.show()

        print(f"✅ UMAP projection complete")

    def plot_session_evolution(
        self,
        session_features: List[np.ndarray],
        session_numbers: List[int],
        feature_names: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ):
        """
        Plot how key features evolve across sessions.

        Args:
            session_features: List of feature arrays per session
            session_numbers: Session numbers
            feature_names: Names of features
            save_path: Optional path to save
        """
        # Average features per session
        session_means = np.array([
            features.mean(axis=0)
            for features in session_features
        ])

        # Select key meditation features to plot
        if feature_names is not None:
            # Find alpha and theta features
            alpha_indices = [i for i, name in enumerate(feature_names) if 'alpha_' in name]
            theta_indices = [i for i, name in enumerate(feature_names) if 'theta_' in name]
            beta_indices = [i for i, name in enumerate(feature_names) if 'beta_' in name]
        else:
            # Use first few features as proxy
            alpha_indices = [2, 3, 4, 5]
            theta_indices = [6, 7, 8, 9]
            beta_indices = [10, 11, 12, 13]

        # Compute band averages
        alpha_avg = session_means[:, alpha_indices].mean(axis=1)
        theta_avg = session_means[:, theta_indices].mean(axis=1)
        beta_avg = session_means[:, beta_indices].mean(axis=1)

        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(session_numbers, alpha_avg, 'o-', label='Alpha (Relaxation)', linewidth=2, markersize=6)
        ax.plot(session_numbers, theta_avg, 's-', label='Theta (Deep Meditation)', linewidth=2, markersize=6)
        ax.plot(session_numbers, beta_avg, '^-', label='Beta (Mental Activity)', linewidth=2, markersize=6)

        ax.set_xlabel('Session Number')
        ax.set_ylabel('Average Power (log scale)')
        ax.set_title('Meditation Practice Evolution Over Time')
        ax.legend()
        ax.grid(alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"💾 Evolution plot saved: {save_path}")

        plt.show()

    def plot_feature_distribution(
        self,
        features: pd.DataFrame,
        feature_name: str,
        save_path: Optional[str] = None
    ):
        """
        Plot distribution of a specific feature.

        Args:
            features: Feature DataFrame
            feature_name: Name of feature to plot
            save_path: Optional path to save
        """
        if feature_name not in features.columns:
            print(f"❌ Feature '{feature_name}' not found")
            return

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Histogram
        axes[0].hist(features[feature_name], bins=50, alpha=0.7, edgecolor='black')
        axes[0].set_xlabel(feature_name)
        axes[0].set_ylabel('Frequency')
        axes[0].set_title(f'{feature_name} Distribution')
        axes[0].grid(alpha=0.3)

        # Time series
        axes[1].plot(features[feature_name], alpha=0.6, linewidth=0.5)
        axes[1].set_xlabel('Time Window')
        axes[1].set_ylabel(feature_name)
        axes[1].set_title(f'{feature_name} Over Time')
        axes[1].grid(alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"💾 Feature distribution saved: {save_path}")

        plt.show()

    def create_session_summary_plot(
        self,
        features_df: pd.DataFrame,
        session_name: str,
        save_path: Optional[str] = None
    ):
        """
        Create comprehensive summary plot for a single session.

        Args:
            features_df: Feature DataFrame for session
            session_name: Name of session
            save_path: Optional path to save
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Title
        fig.suptitle(f'Session Summary: {session_name}', fontsize=16, y=0.98)

        # 1. Alpha power over time
        ax1 = fig.add_subplot(gs[0, :])
        alpha_cols = [c for c in features_df.columns if 'alpha_' in c and 'asymmetry' not in c]
        for col in alpha_cols:
            ax1.plot(features_df[col], label=col, alpha=0.7)
        ax1.set_ylabel('Alpha Power')
        ax1.set_title('Relaxation (Alpha Rhythm)')
        ax1.legend(loc='upper right')
        ax1.grid(alpha=0.3)

        # 2. Theta power over time
        ax2 = fig.add_subplot(gs[1, :])
        theta_cols = [c for c in features_df.columns if 'theta_' in c]
        for col in theta_cols:
            ax2.plot(features_df[col], label=col, alpha=0.7)
        ax2.set_ylabel('Theta Power')
        ax2.set_title('Deep Meditation (Theta Rhythm)')
        ax2.legend(loc='upper right')
        ax2.grid(alpha=0.3)

        # 3. Asymmetry over time
        ax3 = fig.add_subplot(gs[2, 0])
        if 'alpha_asymmetry' in features_df.columns:
            ax3.plot(features_df['alpha_asymmetry'], linewidth=2)
            ax3.axhline(y=0, color='white', linestyle='--', alpha=0.5)
            ax3.set_ylabel('Asymmetry')
            ax3.set_title('Left/Right Balance')
            ax3.grid(alpha=0.3)

        # 4. Connectivity heatmap
        ax4 = fig.add_subplot(gs[2, 1])
        conn_cols = [c for c in features_df.columns if 'conn_' in c]
        if conn_cols:
            conn_data = features_df[conn_cols].mean().values
            # Create correlation matrix shape
            n_channels = 4
            corr_matrix = np.zeros((n_channels, n_channels))
            idx = 0
            for i in range(n_channels):
                for j in range(i+1, n_channels):
                    corr_matrix[i, j] = conn_data[idx]
                    corr_matrix[j, i] = conn_data[idx]
                    idx += 1

            im = ax4.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
            ax4.set_xticks(range(4))
            ax4.set_yticks(range(4))
            ax4.set_xticklabels(['TP9', 'AF7', 'AF8', 'TP10'])
            ax4.set_yticklabels(['TP9', 'AF7', 'AF8', 'TP10'])
            ax4.set_title('Brain Connectivity')
            plt.colorbar(im, ax=ax4)

        # 5. Summary statistics
        ax5 = fig.add_subplot(gs[2, 2])
        ax5.axis('off')

        # Compute stats
        mean_alpha = features_df[[c for c in features_df.columns if 'alpha_' in c and 'asymmetry' not in c]].mean().mean()
        mean_theta = features_df[[c for c in features_df.columns if 'theta_' in c]].mean().mean()
        duration = len(features_df) * 2  # Assuming 2s per window

        stats_text = f"""
Session Statistics:

Duration: {duration:.0f} seconds
Windows: {len(features_df)}

Average Powers:
  Alpha: {mean_alpha:.3f}
  Theta: {mean_theta:.3f}

Quality: {'Deep' if mean_theta > mean_alpha else 'Active'}
"""
        ax5.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                family='monospace')

        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"💾 Session summary saved: {save_path}")

        plt.show()


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize THE LISTENER data")
    parser.add_argument("--history", help="Path to training_history.json")
    parser.add_argument("--latent", help="Path to latent vectors .npy file")
    parser.add_argument("--output", help="Output path for figure")

    args = parser.parse_args()

    viz = Visualizer()

    if args.history:
        viz.plot_training_history(args.history, save_path=args.output)
    elif args.latent:
        latents = np.load(args.latent)
        viz.plot_latent_space(latents, save_path=args.output)
    else:
        print("❌ No data provided. Use --history or --latent")
