"""
Latent Space Sampling & Generation

This module allows the trained VAE to:
1. Sample from latent space (generate "memories")
2. Reconstruct specific sessions
3. Interpolate between states
4. Explore latent space systematically

This is where the AI companion creates its interpretations
of meditation states it has witnessed.
"""

import torch
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import json

from .vae import MeditationVAE, VAEConfig


class LatentSampler:
    """
    Sample from trained VAE's latent space.

    Use cases:
    - Generate "memories" for interpretation by LLM
    - Reconstruct past sessions
    - Interpolate between meditation states
    - Explore what the AI has "learned"

    Usage:
        sampler = LatentSampler.from_checkpoint("checkpoints/best_model.pt")
        memories = sampler.generate_random_samples(n=10)
        sampler.save_samples(memories, "outputs/memories.json")
    """

    def __init__(self, model: MeditationVAE, device: str = "cpu"):
        """
        Initialize sampler.

        Args:
            model: Trained VAE model
            device: Device to run on
        """
        self.model = model.to(device)
        self.model.eval()  # Evaluation mode
        self.device = device
        self.config = model.config

        # Feature names (for interpretation)
        self.feature_names = self._get_feature_names()

    def _get_feature_names(self) -> List[str]:
        """Generate feature names based on standard extraction."""
        names = []

        # Channels
        channels = ["TP9", "AF7", "AF8", "TP10"]
        bands = ["delta", "theta", "alpha", "beta", "gamma"]

        # Band powers (20)
        for band in bands:
            for ch in channels:
                names.append(f"{band}_{ch}")

        # Asymmetry (2)
        names.extend(["alpha_asymmetry", "beta_asymmetry"])

        # Connectivity (6)
        for i, ch1 in enumerate(channels):
            for ch2 in channels[i+1:]:
                names.append(f"conn_{ch1}_{ch2}")

        # Entropy (4)
        for ch in channels:
            names.append(f"entropy_{ch}")

        # Temporal (2)
        names.extend(["mean_absolute_derivative", "spatial_variance"])

        return names

    @classmethod
    def from_checkpoint(cls, checkpoint_path: str, device: Optional[str] = None):
        """
        Load sampler from checkpoint.

        Args:
            checkpoint_path: Path to checkpoint .pt file
            device: Device to load on (auto-detect if None)

        Returns:
            LatentSampler instance
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=device)

        # Reconstruct config
        config_dict = checkpoint['config']
        config = VAEConfig(**config_dict)

        # Create model
        model = MeditationVAE(config)
        model.load_state_dict(checkpoint['model_state_dict'])

        print(f"✅ Loaded model from {checkpoint_path}")
        print(f"   Epoch: {checkpoint['epoch']}")
        print(f"   Val loss: {checkpoint['val_loss']:.4f}")

        return cls(model, device=device)

    @torch.no_grad()
    def generate_random_samples(self, n: int = 10) -> List[Dict]:
        """
        Generate random samples from latent space.

        These are the AI's "imagined" meditation states based
        on what it has learned.

        Args:
            n: Number of samples to generate

        Returns:
            List of feature dictionaries
        """
        print(f"\n🎲 Generating {n} random samples from latent space...")

        # Sample latent vectors from standard normal
        z = torch.randn(n, self.config.latent_dim).to(self.device)

        # Decode to features
        features = self.model.decode(z)
        features = features.cpu().numpy()

        # Convert to list of dicts
        samples = []
        for i in range(n):
            sample = {
                'sample_id': i,
                'latent_vector': z[i].cpu().numpy().tolist(),
                'features': {
                    name: float(features[i, j])
                    for j, name in enumerate(self.feature_names[:features.shape[1]])
                }
            }
            samples.append(sample)

        print(f"✅ Generated {n} samples")

        return samples

    @torch.no_grad()
    def reconstruct_session(self, session_features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reconstruct features from a real session.

        Useful for seeing how well the model "understands" a session.

        Args:
            session_features: Original features, shape (n_windows, n_features)

        Returns:
            Tuple of (reconstructions, latent_vectors)
        """
        # Convert to tensor
        features_tensor = torch.from_numpy(session_features).float().to(self.device)

        # Encode and decode
        mu, logvar = self.model.encode(features_tensor)
        z = self.model.reparameterize(mu, logvar)
        reconstructions = self.model.decode(z)

        return reconstructions.cpu().numpy(), z.cpu().numpy()

    @torch.no_grad()
    def interpolate_between_sessions(
        self,
        session1_features: np.ndarray,
        session2_features: np.ndarray,
        num_steps: int = 10
    ) -> np.ndarray:
        """
        Interpolate between two sessions in latent space.

        Creates a smooth transition showing how the AI might
        "imagine" the journey between two meditation states.

        Args:
            session1_features: First session features (mean across windows)
            session2_features: Second session features
            num_steps: Number of interpolation steps

        Returns:
            Interpolated features, shape (num_steps, n_features)
        """
        # Take mean of each session (represent session by single point)
        feat1 = torch.from_numpy(session1_features.mean(axis=0, keepdims=True)).float().to(self.device)
        feat2 = torch.from_numpy(session2_features.mean(axis=0, keepdims=True)).float().to(self.device)

        # Encode both
        mu1, _ = self.model.encode(feat1)
        mu2, _ = self.model.encode(feat2)

        # Linear interpolation in latent space
        alphas = torch.linspace(0, 1, num_steps).to(self.device)
        z_interp = torch.stack([
            (1 - alpha) * mu1 + alpha * mu2
            for alpha in alphas
        ]).squeeze(1)

        # Decode
        interp_features = self.model.decode(z_interp)

        return interp_features.cpu().numpy()

    @torch.no_grad()
    def explore_latent_dimension(
        self,
        dimension: int,
        num_samples: int = 10,
        range_std: float = 2.0
    ) -> List[Dict]:
        """
        Explore a single latent dimension systematically.

        Useful for understanding what each dimension represents.

        Args:
            dimension: Which latent dimension to explore (0 to latent_dim-1)
            num_samples: Number of samples along dimension
            range_std: Range in standard deviations to explore

        Returns:
            List of samples with varying latent dimension
        """
        print(f"\n🔍 Exploring latent dimension {dimension}...")

        # Create base latent vector (all zeros = mean)
        z_base = torch.zeros(1, self.config.latent_dim).to(self.device)

        # Vary one dimension
        values = torch.linspace(-range_std, range_std, num_samples).to(self.device)

        samples = []
        for i, val in enumerate(values):
            z = z_base.clone()
            z[0, dimension] = val

            # Decode
            features = self.model.decode(z)
            features = features.cpu().numpy()[0]

            sample = {
                'sample_id': i,
                'dimension': dimension,
                'value': float(val),
                'features': {
                    name: float(features[j])
                    for j, name in enumerate(self.feature_names[:len(features)])
                }
            }
            samples.append(sample)

        return samples

    def get_latent_statistics(self, session_features_list: List[np.ndarray]) -> Dict:
        """
        Get statistics of latent space for multiple sessions.

        Useful for understanding the "spread" of meditation states.

        Args:
            session_features_list: List of feature arrays from different sessions

        Returns:
            Dict with latent space statistics
        """
        print(f"\n📊 Computing latent space statistics for {len(session_features_list)} sessions...")

        all_latents = []

        for session_features in session_features_list:
            features_tensor = torch.from_numpy(session_features).float().to(self.device)
            mu, logvar = self.model.encode(features_tensor)
            all_latents.append(mu.cpu().numpy())

        # Concatenate all latents
        all_latents = np.vstack(all_latents)

        stats = {
            'mean': all_latents.mean(axis=0).tolist(),
            'std': all_latents.std(axis=0).tolist(),
            'min': all_latents.min(axis=0).tolist(),
            'max': all_latents.max(axis=0).tolist(),
            'n_samples': len(all_latents)
        }

        print(f"✅ Statistics computed for {len(all_latents)} latent vectors")

        return stats

    def save_samples(self, samples: List[Dict], output_path: str):
        """
        Save generated samples to JSON.

        Args:
            samples: List of sample dictionaries
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(samples, f, indent=2)

        print(f"\n💾 Saved {len(samples)} samples to {output_path}")

    def summarize_sample(self, sample: Dict) -> str:
        """
        Create human-readable summary of a sample.

        This summary will be fed to the LLM for poetic interpretation.

        Args:
            sample: Sample dictionary with features

        Returns:
            Text summary
        """
        features = sample['features']

        # Extract key meditation indicators
        alpha_power = np.mean([
            features.get(f'alpha_{ch}', 0)
            for ch in ['TP9', 'AF7', 'AF8', 'TP10']
        ])

        theta_power = np.mean([
            features.get(f'theta_{ch}', 0)
            for ch in ['TP9', 'AF7', 'AF8', 'TP10']
        ])

        beta_power = np.mean([
            features.get(f'beta_{ch}', 0)
            for ch in ['TP9', 'AF7', 'AF8', 'TP10']
        ])

        alpha_asym = features.get('alpha_asymmetry', 0)

        # Connectivity (average)
        conn_features = [v for k, v in features.items() if 'conn_' in k]
        avg_connectivity = np.mean(conn_features) if conn_features else 0

        # Entropy (average)
        entropy_features = [v for k, v in features.items() if 'entropy_' in k]
        avg_entropy = np.mean(entropy_features) if entropy_features else 0

        # Create summary
        summary = f"""Sample {sample['sample_id']}:
- Alpha rhythm: {alpha_power:.3f} (relaxation)
- Theta rhythm: {theta_power:.3f} (deep meditation)
- Beta rhythm: {beta_power:.3f} (mental activity)
- Hemispheric balance: {alpha_asym:.3f} (negative=left, positive=right)
- Brain connectivity: {avg_connectivity:.3f}
- Signal complexity: {avg_entropy:.3f}"""

        return summary


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sample from Meditation VAE")
    parser.add_argument("checkpoint", help="Path to model checkpoint")
    parser.add_argument("--num-samples", type=int, default=10,
                       help="Number of samples to generate")
    parser.add_argument("--output", default="outputs/samples.json",
                       help="Output JSON file")

    args = parser.parse_args()

    # Load sampler
    sampler = LatentSampler.from_checkpoint(args.checkpoint)

    # Generate samples
    samples = sampler.generate_random_samples(n=args.num_samples)

    # Save
    sampler.save_samples(samples, args.output)

    # Print summaries
    print("\n📝 Sample summaries:")
    for sample in samples[:3]:  # Show first 3
        print(sampler.summarize_sample(sample))
        print()

    print("✅ Done!")
