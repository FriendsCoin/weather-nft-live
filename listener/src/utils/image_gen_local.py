"""
Local GPU Image Generation with Low-Memory Optimizations

Optimized for RTX 2080 8GB VRAM using Stable Diffusion 1.5
with attention slicing, VAE tiling, and fp16 precision.

This is an alternative to the cloud-based Replicate API for
users who want to run everything locally on their GPU.
"""

import os
import torch
import yaml
from typing import Optional, List, Dict
from pathlib import Path
import time
import gc

try:
    from diffusers import (
        StableDiffusionPipeline,
        DPMSolverMultistepScheduler,
        EulerAncestralDiscreteScheduler
    )
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("⚠️  diffusers package not installed.")
    print("   Install with: pip install diffusers transformers accelerate")


class LocalImageGenerator:
    """
    Generate images locally on GPU with memory optimizations.

    Optimized for 8GB VRAM (RTX 2080, RTX 3070, etc.)

    Features:
    - Automatic memory management
    - fp16 precision (50% VRAM savings)
    - Attention slicing
    - VAE tiling for large images
    - xformers support (if installed)
    - VRAM monitoring

    Usage:
        # Load with low-memory config
        generator = LocalImageGenerator(config_path="configs/lowmem_gpu.yaml")

        # Generate image
        image = generator.generate(
            prompt="Waves of stillness dissolving into formless attention",
            session_number=25
        )

        # Save
        image.save("outputs/images/session_25.png")
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        device: str = "cuda",
        enable_optimizations: bool = True
    ):
        """
        Initialize local image generator.

        Args:
            config_path: Path to YAML config (e.g., configs/lowmem_gpu.yaml)
            model_id: HuggingFace model ID
            device: "cuda" or "cpu"
            enable_optimizations: Enable memory optimizations
        """
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("diffusers package required. Install with: pip install diffusers transformers accelerate")

        # Load config
        self.config = self._load_config(config_path) if config_path else {}

        # Get settings from config or use defaults
        sd_config = self.config.get("stable_diffusion", {})
        self.model_id = sd_config.get("model", model_id)
        self.device = device if torch.cuda.is_available() else "cpu"
        self.precision = sd_config.get("precision", "fp16")

        # Memory optimization flags
        self.enable_attention_slicing = sd_config.get("enable_attention_slicing", True)
        self.attention_slice_size = sd_config.get("attention_slice_size", "auto")
        self.enable_vae_tiling = sd_config.get("enable_vae_tiling", True)
        self.enable_vae_slicing = sd_config.get("enable_vae_slicing", True)
        self.enable_xformers = sd_config.get("enable_xformers", True)
        self.enable_cpu_offload = sd_config.get("enable_cpu_offload", False)

        # Default generation parameters
        self.default_size = sd_config.get("image_size", 512)
        self.default_steps = sd_config.get("num_inference_steps", 30)

        # VRAM monitoring
        monitoring = self.config.get("monitoring", {})
        self.log_vram = monitoring.get("log_vram_usage", True)
        self.warn_threshold = monitoring.get("warn_threshold_gb", 7.0)

        # Meditation style prompts
        self.base_style = "contemplative abstract art, minimal, ethereal, soft colors, meditation, peaceful"
        self.negative_prompt = "text, words, letters, numbers, faces, people, recognizable objects, photorealistic, busy, chaotic"

        print(f"🎨 Initializing Local Image Generator")
        print(f"   Model: {self.model_id}")
        print(f"   Device: {self.device}")
        print(f"   Precision: {self.precision}")

        # Load pipeline
        self._load_pipeline()

        print(f"✅ Pipeline loaded successfully")
        if self.log_vram and self.device == "cuda":
            self._log_vram_usage("After initialization")

    def _load_config(self, config_path: str) -> dict:
        """Load YAML configuration."""
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"⚠️  Config not found: {config_path}")
            return {}

        with open(config_file) as f:
            return yaml.safe_load(f)

    def _load_pipeline(self):
        """Load Stable Diffusion pipeline with optimizations."""
        # Determine dtype
        torch_dtype = torch.float16 if self.precision == "fp16" and self.device == "cuda" else torch.float32

        print(f"📥 Loading model from HuggingFace...")

        # Load pipeline
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch_dtype,
            safety_checker=None,  # Disable for speed (art project, not public)
            requires_safety_checker=False
        )

        # Use better scheduler (faster, same quality)
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )

        # Move to device
        self.pipe = self.pipe.to(self.device)

        # Apply optimizations
        if self.enable_attention_slicing and self.device == "cuda":
            print(f"   ✓ Enabling attention slicing")
            if self.attention_slice_size == "auto":
                self.pipe.enable_attention_slicing()
            else:
                self.pipe.enable_attention_slicing(self.attention_slice_size)

        if self.enable_vae_slicing and hasattr(self.pipe, 'enable_vae_slicing'):
            print(f"   ✓ Enabling VAE slicing")
            self.pipe.enable_vae_slicing()

        if self.enable_vae_tiling and hasattr(self.pipe, 'enable_vae_tiling'):
            print(f"   ✓ Enabling VAE tiling")
            self.pipe.enable_vae_tiling()

        # Try to enable xformers (significant speedup + memory savings)
        if self.enable_xformers and self.device == "cuda":
            try:
                self.pipe.enable_xformers_memory_efficient_attention()
                print(f"   ✓ Enabled xformers (20-30% VRAM savings)")
            except Exception as e:
                print(f"   ⚠️  xformers not available: {e}")
                print(f"      Install with: pip install xformers")

        # CPU offload (only if really needed - makes it slower)
        if self.enable_cpu_offload and self.device == "cuda":
            print(f"   ✓ Enabling CPU offload (slower but saves VRAM)")
            self.pipe.enable_model_cpu_offload()

    def _log_vram_usage(self, context: str = ""):
        """Log current VRAM usage."""
        if not torch.cuda.is_available():
            return

        allocated_gb = torch.cuda.memory_allocated() / 1024**3
        reserved_gb = torch.cuda.memory_reserved() / 1024**3

        print(f"   📊 VRAM {context}: {allocated_gb:.2f}GB allocated, {reserved_gb:.2f}GB reserved")

        if allocated_gb > self.warn_threshold:
            print(f"   ⚠️  VRAM usage high! Consider enabling more optimizations.")

    def clear_memory(self):
        """Clear GPU memory cache."""
        if self.device == "cuda":
            gc.collect()
            torch.cuda.empty_cache()
            if self.log_vram:
                self._log_vram_usage("After clearing cache")

    def generate(
        self,
        prompt: str,
        session_number: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        save_path: Optional[str] = None
    ):
        """
        Generate image from text prompt.

        Args:
            prompt: Poetic description from LLM
            session_number: Session number (for metadata)
            width: Image width (default: 512)
            height: Image height (default: 512)
            num_inference_steps: Quality (default: 30)
            guidance_scale: How closely to follow prompt
            seed: Random seed for reproducibility
            save_path: Optional path to save image

        Returns:
            PIL Image
        """
        # Use defaults from config
        width = width or self.default_size
        height = height or self.default_size
        num_inference_steps = num_inference_steps or self.default_steps

        # Validate size for 8GB VRAM
        if self.device == "cuda" and (width > 512 or height > 512):
            print(f"⚠️  Warning: {width}x{height} may exceed 8GB VRAM. Recommended max: 512x512")

        # Build full prompt
        full_prompt = f"{prompt}, {self.base_style}"

        print(f"\n🎨 Generating image...")
        print(f"   Prompt: {prompt[:60]}...")
        print(f"   Size: {width}x{height}")
        print(f"   Steps: {num_inference_steps}")

        if self.log_vram and self.device == "cuda":
            self._log_vram_usage("Before generation")

        # Set seed for reproducibility
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)

        # Generate
        start_time = time.time()

        with torch.inference_mode():
            result = self.pipe(
                prompt=full_prompt,
                negative_prompt=self.negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )

        image = result.images[0]
        elapsed = time.time() - start_time

        print(f"✅ Generated in {elapsed:.1f}s")

        if self.log_vram and self.device == "cuda":
            self._log_vram_usage("After generation")

        # Save if requested
        if save_path:
            save_file = Path(save_path)
            save_file.parent.mkdir(parents=True, exist_ok=True)
            image.save(save_file)
            print(f"💾 Saved to {save_path}")

        return image

    def generate_batch(
        self,
        prompts: List[str],
        base_output_dir: str = "outputs/images",
        session_numbers: Optional[List[int]] = None,
        clear_cache_between: bool = True,
        **kwargs
    ) -> List[str]:
        """
        Generate multiple images sequentially (safer for 8GB VRAM).

        Args:
            prompts: List of text prompts
            base_output_dir: Directory to save images
            session_numbers: Optional list of session numbers
            clear_cache_between: Clear VRAM between generations
            **kwargs: Additional args for generate()

        Returns:
            List of output paths
        """
        output_paths = []

        for i, prompt in enumerate(prompts):
            session_num = session_numbers[i] if session_numbers else i
            output_path = Path(base_output_dir) / f"session_{session_num:03d}.png"

            print(f"\n[{i+1}/{len(prompts)}] Session {session_num}")

            image = self.generate(
                prompt=prompt,
                session_number=session_num,
                save_path=str(output_path),
                **kwargs
            )

            output_paths.append(str(output_path))

            # Clear cache between generations
            if clear_cache_between and i < len(prompts) - 1:
                self.clear_memory()

        return output_paths


# Convenience function
def create_generator(use_local: bool = True, config_path: str = "configs/lowmem_gpu.yaml"):
    """
    Create image generator (local or cloud).

    Args:
        use_local: If True, use local GPU. If False, use Replicate API
        config_path: Path to config for local generation

    Returns:
        ImageGenerator instance
    """
    if use_local:
        return LocalImageGenerator(config_path=config_path)
    else:
        from .image_gen import ImageGenerator
        return ImageGenerator()


if __name__ == "__main__":
    # Test script
    print("Testing Local Image Generator with Low-Memory Config\n")

    # Create generator
    gen = LocalImageGenerator(
        config_path="../../../configs/lowmem_gpu.yaml"
    )

    # Test prompt
    test_prompt = "Waves of stillness dissolving into formless attention, gentle ripples of awareness"

    # Generate
    image = gen.generate(
        prompt=test_prompt,
        session_number=1,
        save_path="test_output.png",
        seed=42
    )

    print("\n✅ Test complete! Check test_output.png")

    # Memory check
    gen._log_vram_usage("Final")
