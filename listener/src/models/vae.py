"""
Variational Autoencoder for Meditation EEG Patterns

This VAE learns to:
1. ENCODE: Compress EEG features into latent space (meditation "essence")
2. DECODE: Reconstruct features from latent space
3. GENERATE: Sample latent space to create "memories" of meditation

Architecture:
- Encoder: Features (34D) → Hidden layers → Latent space (32D)
- Decoder: Latent space (32D) → Hidden layers → Reconstructed features (34D)

The latent space captures the "character" of this person's meditation practice.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class VAEConfig:
    """Configuration for Meditation VAE."""

    # Input/output dimensions
    input_dim: int = 34  # Number of features extracted
    latent_dim: int = 32  # Compressed representation size

    # Architecture
    encoder_layers: list = None  # Hidden layer sizes [128, 64, 32]
    decoder_layers: list = None  # Mirror of encoder
    activation: str = "relu"
    dropout: float = 0.2
    batch_norm: bool = True

    # VAE-specific
    beta: float = 1.0  # KL divergence weight (β-VAE)

    def __post_init__(self):
        """Set default layer sizes if not provided."""
        if self.encoder_layers is None:
            self.encoder_layers = [128, 64, 32]
        if self.decoder_layers is None:
            self.decoder_layers = [32, 64, 128]


class MeditationVAE(nn.Module):
    """
    Variational Autoencoder for meditation EEG patterns.

    Unlike standard classification models, this VAE learns the DISTRIBUTION
    of meditation states, allowing it to:
    - Reconstruct patterns (how well it "understands" the meditation)
    - Generate new patterns (AI's "imagination" of meditation states)
    - Interpolate between states (transitions during meditation)

    This is witnessing, not optimizing.
    """

    def __init__(self, config: VAEConfig):
        """
        Initialize VAE.

        Args:
            config: VAE configuration
        """
        super().__init__()
        self.config = config

        # Activation function
        if config.activation == "relu":
            self.activation = nn.ReLU()
        elif config.activation == "leaky_relu":
            self.activation = nn.LeakyReLU(0.2)
        elif config.activation == "elu":
            self.activation = nn.ELU()
        else:
            self.activation = nn.ReLU()

        # Build encoder
        self.encoder = self._build_encoder()

        # Latent space projection
        last_encoder_dim = config.encoder_layers[-1]
        self.fc_mu = nn.Linear(last_encoder_dim, config.latent_dim)
        self.fc_logvar = nn.Linear(last_encoder_dim, config.latent_dim)

        # Build decoder
        self.decoder = self._build_decoder()

    def _build_encoder(self) -> nn.Sequential:
        """Build encoder network."""
        layers = []
        input_dim = self.config.input_dim

        for hidden_dim in self.config.encoder_layers:
            layers.append(nn.Linear(input_dim, hidden_dim))

            if self.config.batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))

            layers.append(self.activation)

            if self.config.dropout > 0:
                layers.append(nn.Dropout(self.config.dropout))

            input_dim = hidden_dim

        return nn.Sequential(*layers)

    def _build_decoder(self) -> nn.Sequential:
        """Build decoder network."""
        layers = []

        # Start from latent dimension
        decoder_dims = [self.config.latent_dim] + self.config.decoder_layers

        for i in range(len(decoder_dims) - 1):
            layers.append(nn.Linear(decoder_dims[i], decoder_dims[i + 1]))

            if self.config.batch_norm:
                layers.append(nn.BatchNorm1d(decoder_dims[i + 1]))

            layers.append(self.activation)

            if self.config.dropout > 0:
                layers.append(nn.Dropout(self.config.dropout))

        # Final layer (reconstruction)
        layers.append(nn.Linear(decoder_dims[-1], self.config.input_dim))

        return nn.Sequential(*layers)

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode input to latent distribution parameters.

        Args:
            x: Input features, shape (batch_size, input_dim)

        Returns:
            mu: Mean of latent distribution, shape (batch_size, latent_dim)
            logvar: Log variance of latent distribution
        """
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """
        Reparameterization trick: z = mu + sigma * epsilon

        This allows backpropagation through sampling.

        Args:
            mu: Mean of latent distribution
            logvar: Log variance of latent distribution

        Returns:
            z: Sampled latent vector
        """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """
        Decode latent vector to reconstructed features.

        Args:
            z: Latent vector, shape (batch_size, latent_dim)

        Returns:
            Reconstructed features, shape (batch_size, input_dim)
        """
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through VAE.

        Args:
            x: Input features, shape (batch_size, input_dim)

        Returns:
            recon: Reconstructed features
            mu: Latent mean
            logvar: Latent log variance
        """
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar

    def sample(self, num_samples: int, device: str = "cpu") -> torch.Tensor:
        """
        Sample from latent space to generate "memories".

        This is where the AI creates its own meditation patterns
        based on what it has learned.

        Args:
            num_samples: Number of samples to generate
            device: Device to generate on

        Returns:
            Generated features, shape (num_samples, input_dim)
        """
        # Sample from standard normal
        z = torch.randn(num_samples, self.config.latent_dim).to(device)

        # Decode to features
        with torch.no_grad():
            samples = self.decode(z)

        return samples

    def interpolate(
        self,
        x1: torch.Tensor,
        x2: torch.Tensor,
        num_steps: int = 10
    ) -> torch.Tensor:
        """
        Interpolate between two meditation states.

        Useful for visualizing transitions and generating
        "in-between" states.

        Args:
            x1: First state features
            x2: Second state features
            num_steps: Number of interpolation steps

        Returns:
            Interpolated features, shape (num_steps, input_dim)
        """
        # Encode both states
        mu1, _ = self.encode(x1)
        mu2, _ = self.encode(x2)

        # Linear interpolation in latent space
        alphas = torch.linspace(0, 1, num_steps).to(x1.device)
        z_interp = torch.stack([
            (1 - alpha) * mu1 + alpha * mu2
            for alpha in alphas
        ])

        # Decode interpolated latents
        with torch.no_grad():
            interp_features = self.decode(z_interp)

        return interp_features


def vae_loss(
    recon_x: torch.Tensor,
    x: torch.Tensor,
    mu: torch.Tensor,
    logvar: torch.Tensor,
    beta: float = 1.0
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    VAE loss function: Reconstruction + KL divergence.

    Loss = MSE(reconstruction) + β * KL(latent || N(0,1))

    Args:
        recon_x: Reconstructed features
        x: Original features
        mu: Latent mean
        logvar: Latent log variance
        beta: KL divergence weight (β-VAE parameter)

    Returns:
        total_loss: Combined loss
        recon_loss: Reconstruction loss (MSE)
        kl_loss: KL divergence loss
    """
    # Reconstruction loss (Mean Squared Error)
    recon_loss = F.mse_loss(recon_x, x, reduction='mean')

    # KL divergence: KL(N(mu, sigma) || N(0, 1))
    # = -0.5 * sum(1 + logvar - mu^2 - exp(logvar))
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    kl_loss = kl_loss / x.size(0)  # Average over batch

    # Total loss
    total_loss = recon_loss + beta * kl_loss

    return total_loss, recon_loss, kl_loss


# Example usage
if __name__ == "__main__":
    # Create config
    config = VAEConfig(
        input_dim=34,
        latent_dim=32,
        encoder_layers=[128, 64, 32],
        decoder_layers=[32, 64, 128],
        beta=1.0
    )

    # Create model
    model = MeditationVAE(config)

    print("🧠 Meditation VAE Architecture:")
    print(f"   Input dim: {config.input_dim}")
    print(f"   Latent dim: {config.latent_dim}")
    print(f"   Encoder: {config.encoder_layers}")
    print(f"   Decoder: {config.decoder_layers}")
    print(f"\n   Total parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Test forward pass
    batch_size = 16
    x = torch.randn(batch_size, config.input_dim)

    recon, mu, logvar = model(x)
    total_loss, recon_loss, kl_loss = vae_loss(recon, x, mu, logvar, beta=config.beta)

    print(f"\n🧪 Test forward pass (batch_size={batch_size}):")
    print(f"   Reconstruction shape: {recon.shape}")
    print(f"   Latent mean shape: {mu.shape}")
    print(f"   Total loss: {total_loss.item():.4f}")
    print(f"   Reconstruction loss: {recon_loss.item():.4f}")
    print(f"   KL divergence: {kl_loss.item():.4f}")

    # Test sampling
    samples = model.sample(num_samples=5)
    print(f"\n🎲 Generated samples shape: {samples.shape}")

    print("\n✅ VAE model working correctly!")
