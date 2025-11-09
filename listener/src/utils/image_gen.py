"""
Image Generation from Poetic Interpretations

This module uses Stable Diffusion (via Replicate API) to generate
visual "memories" from the LLM's poetic interpretations.

The images become part of the gallery showing the AI companion's
evolution through the meditation journey.
"""

import os
from typing import Optional, List, Dict
from pathlib import Path
import time
import json
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    print("⚠️  replicate package not installed. Image generation will not work.")
    print("   Install with: pip install replicate")


class ImageGenerator:
    """
    Generate images from poetic text prompts.

    Uses Stable Diffusion XL via Replicate API to create
    contemplative visual representations of meditation states.

    Usage:
        generator = ImageGenerator(api_key="your-key")
        image_url = generator.generate(
            prompt="Waves of stillness dissolving into formless attention",
            session_number=25
        )
        generator.download_image(image_url, "outputs/images/session_25.png")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "stability-ai/sdxl:latest",
        base_style: str = "contemplative abstract art, minimal, ethereal, soft colors",
        negative_prompt: str = "text, words, letters, numbers, faces, people, recognizable objects, photorealistic"
    ):
        """
        Initialize image generator.

        Args:
            api_key: Replicate API key (or set REPLICATE_API_TOKEN env var)
            model: Replicate model to use
            base_style: Style keywords added to all prompts
            negative_prompt: What to avoid in images
        """
        if not REPLICATE_AVAILABLE:
            print("❌ Replicate not available. Install with: pip install replicate")
            self.client = None
            return

        # Get API key
        if api_key is not None:
            os.environ["REPLICATE_API_TOKEN"] = api_key
        elif "REPLICATE_API_TOKEN" not in os.environ:
            print("⚠️  No Replicate API key found.")
            print("   Set REPLICATE_API_TOKEN environment variable or pass api_key parameter.")
            self.client = None
            return

        self.model = model
        self.base_style = base_style
        self.negative_prompt = negative_prompt

        print(f"🎨 Image Generator initialized")
        print(f"   Model: {self.model}")
        print(f"   Style: {self.base_style}")

    def generate(
        self,
        prompt: str,
        session_number: Optional[int] = None,
        width: int = 768,
        height: int = 768,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate image from text prompt.

        Args:
            prompt: Poetic description from LLM
            session_number: Optional session number (for metadata)
            width: Image width
            height: Image height
            num_inference_steps: Quality (higher = better but slower)
            guidance_scale: How closely to follow prompt
            seed: Random seed (for reproducibility)

        Returns:
            URL of generated image, or None if error
        """
        if not REPLICATE_AVAILABLE or self.client is None:
            print("❌ Replicate not configured")
            return None

        # Construct full prompt with style
        full_prompt = f"{prompt}, {self.base_style}"

        print(f"\n🎨 Generating image...")
        if session_number is not None:
            print(f"   Session: {session_number}")
        print(f"   Prompt: {prompt}")

        try:
            # Run Stable Diffusion
            output = replicate.run(
                self.model,
                input={
                    "prompt": full_prompt,
                    "negative_prompt": self.negative_prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed
                }
            )

            # Get image URL (SDXL returns list of URLs)
            if isinstance(output, list):
                image_url = output[0]
            else:
                image_url = output

            print(f"✅ Image generated: {image_url}")

            return image_url

        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None

    def download_image(
        self,
        image_url: str,
        save_path: str,
        session_number: Optional[int] = None
    ) -> Optional[Path]:
        """
        Download generated image to local file.

        Args:
            image_url: URL of generated image
            save_path: Local path to save image
            session_number: Optional session number (for metadata)

        Returns:
            Path to saved image, or None if error
        """
        import requests
        from PIL import Image
        from io import BytesIO

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Download image
            response = requests.get(image_url)
            response.raise_for_status()

            # Open and save
            img = Image.open(BytesIO(response.content))
            img.save(save_path)

            print(f"💾 Image saved: {save_path}")

            # Save metadata
            metadata_path = save_path.with_suffix('.json')
            metadata = {
                'image_url': image_url,
                'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'session_number': session_number,
                'file_size': save_path.stat().st_size
            }

            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            return save_path

        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return None

    def generate_batch(
        self,
        interpretations: List[Dict],
        output_dir: str = "data/outputs/images",
        delay: float = 1.0
    ) -> List[Dict]:
        """
        Generate images for multiple interpretations.

        Args:
            interpretations: List of interpretation dicts with 'text' field
            output_dir: Directory to save images
            delay: Delay between API calls (avoid rate limiting)

        Returns:
            List of results with image paths
        """
        if not REPLICATE_AVAILABLE or self.client is None:
            print("❌ Replicate not configured")
            return []

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🎨 Generating {len(interpretations)} images...")

        results = []

        for i, interp in enumerate(interpretations):
            print(f"\n[{i+1}/{len(interpretations)}]")

            prompt = interp['text']
            session_num = interp.get('session_number')
            sample_id = interp.get('sample_id', i)

            # Generate filename
            if session_num is not None:
                filename = f"session_{session_num:03d}_memory.png"
            else:
                filename = f"sample_{sample_id:03d}_memory.png"

            save_path = output_dir / filename

            # Skip if already exists
            if save_path.exists():
                print(f"⏭️  Skipping (already exists): {filename}")
                results.append({
                    'sample_id': sample_id,
                    'session_number': session_num,
                    'image_path': str(save_path),
                    'skipped': True
                })
                continue

            # Generate image
            image_url = self.generate(
                prompt=prompt,
                session_number=session_num
            )

            if image_url:
                # Download
                local_path = self.download_image(
                    image_url,
                    str(save_path),
                    session_number=session_num
                )

                results.append({
                    'sample_id': sample_id,
                    'session_number': session_num,
                    'prompt': prompt,
                    'image_url': image_url,
                    'image_path': str(local_path) if local_path else None,
                    'success': local_path is not None
                })
            else:
                results.append({
                    'sample_id': sample_id,
                    'session_number': session_num,
                    'prompt': prompt,
                    'success': False,
                    'error': 'Generation failed'
                })

            # Delay to avoid rate limiting
            if i < len(interpretations) - 1:
                time.sleep(delay)

        # Save batch results
        results_path = output_dir / "generation_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)

        successful = sum(1 for r in results if r.get('success', False))
        print(f"\n✅ Batch complete: {successful}/{len(interpretations)} images generated")
        print(f"💾 Results saved: {results_path}")

        return results

    def create_gallery_html(
        self,
        results: List[Dict],
        interpretations: List[Dict],
        output_path: str = "data/outputs/gallery.html"
    ):
        """
        Create simple HTML gallery of generated images.

        Args:
            results: Generation results from generate_batch
            interpretations: Original interpretations
            output_path: Path to save HTML file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build HTML
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>THE LISTENER - AI Meditation Memories</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 40px;
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            font-weight: 300;
            letter-spacing: 2px;
            margin-bottom: 60px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 40px;
        }
        .memory {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
        }
        .memory img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .session-number {
            font-size: 0.9em;
            color: #888;
            margin-bottom: 10px;
        }
        .interpretation {
            font-style: italic;
            line-height: 1.6;
            color: #ccc;
        }
    </style>
</head>
<body>
    <h1>THE LISTENER</h1>
    <p style="text-align: center; color: #888; margin-bottom: 60px;">
        AI-generated memories of witnessed meditation states
    </p>
    <div class="gallery">
"""

        # Add each memory
        for result in results:
            if not result.get('success', False):
                continue

            sample_id = result.get('sample_id', 0)
            session_num = result.get('session_number')
            image_path = result.get('image_path', '')

            # Find corresponding interpretation
            interp_text = ""
            for interp in interpretations:
                if interp.get('sample_id') == sample_id:
                    interp_text = interp.get('text', '')
                    break

            # Make image path relative
            image_rel = Path(image_path).name

            session_label = f"Session {session_num}" if session_num else f"Sample {sample_id}"

            html += f"""
        <div class="memory">
            <div class="session-number">{session_label}</div>
            <img src="{image_rel}" alt="{session_label}">
            <div class="interpretation">{interp_text}</div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        # Save
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"\n🖼️  Gallery created: {output_path}")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate images from interpretations")
    parser.add_argument("--prompt", help="Text prompt for single image")
    parser.add_argument("--api-key", help="Replicate API key")
    parser.add_argument("--output", default="output.png", help="Output image path")

    args = parser.parse_args()

    # Initialize generator
    generator = ImageGenerator(api_key=args.api_key)

    if args.prompt:
        # Generate single image
        image_url = generator.generate(prompt=args.prompt)

        if image_url:
            generator.download_image(image_url, args.output)
            print(f"\n✅ Image saved to {args.output}")
    else:
        print("❌ No prompt provided. Use --prompt 'your text here'")
