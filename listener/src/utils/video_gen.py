"""
Video Generation for THE LISTENER

Create animated visual memories from meditation states:
- Latent space interpolation (smooth transitions)
- AnimateDiff-style breathing/flowing animations
- ComfyUI API integration (alternative approach)

These videos show the AI's interpretation of meditation evolving over time.
"""

import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import json
import requests
from PIL import Image
import io

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  opencv-python not installed. Install with: pip install opencv-python")

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False


class VideoGenerator:
    """
    Generate animated videos from meditation states.

    Approaches:
    1. Latent interpolation: Smooth transitions between states
    2. AnimateDiff: Motion-guided animations via Replicate
    3. ComfyUI: Local workflow execution

    Usage:
        generator = VideoGenerator()

        # Interpolation video
        video_path = generator.create_interpolation_video(
            images=["img1.png", "img2.png", "img3.png"],
            duration_per_transition=3.0
        )

        # AnimateDiff animation
        video_path = generator.create_animated_video(
            prompt="Waves of stillness dissolving into space",
            duration=5.0
        )
    """

    def __init__(
        self,
        output_dir: str = "data/outputs/videos",
        fps: int = 30,
        resolution: Tuple[int, int] = (768, 768)
    ):
        """
        Initialize video generator.

        Args:
            output_dir: Directory to save videos
            fps: Frames per second
            resolution: Video resolution (width, height)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.fps = fps
        self.resolution = resolution

        print(f"🎬 Video Generator initialized")
        print(f"   Output: {self.output_dir}")
        print(f"   FPS: {self.fps}, Resolution: {self.resolution}")

    def create_interpolation_video(
        self,
        images: List[str],
        duration_per_transition: float = 3.0,
        interpolation_method: str = "linear",
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Create smooth interpolation video between meditation state images.

        Perfect for showing evolution across sessions or transitions
        within a single session.

        Args:
            images: List of image paths to interpolate between
            duration_per_transition: Seconds per transition
            interpolation_method: "linear", "ease_in_out", "sine"
            output_name: Custom output filename

        Returns:
            Path to generated video
        """
        if not CV2_AVAILABLE:
            print("❌ OpenCV required for video generation")
            return None

        print(f"\n🎬 Creating interpolation video...")
        print(f"   Images: {len(images)}")
        print(f"   Duration per transition: {duration_per_transition}s")

        # Load images
        frames_data = []
        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"⚠️  Could not load {img_path}, skipping")
                continue

            # Resize to target resolution
            img = cv2.resize(img, self.resolution)
            frames_data.append(img)

        if len(frames_data) < 2:
            print("❌ Need at least 2 valid images")
            return None

        # Generate output filename
        if output_name is None:
            output_name = f"interpolation_{len(images)}states.mp4"

        output_path = self.output_dir / output_name

        # Calculate frames needed
        frames_per_transition = int(duration_per_transition * self.fps)

        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            self.fps,
            self.resolution
        )

        # Interpolate between each pair of images
        for i in range(len(frames_data) - 1):
            img1 = frames_data[i].astype(np.float32)
            img2 = frames_data[i + 1].astype(np.float32)

            print(f"   Interpolating {i+1} → {i+2}...")

            for frame_idx in range(frames_per_transition):
                # Calculate interpolation weight
                t = frame_idx / frames_per_transition

                # Apply interpolation curve
                if interpolation_method == "ease_in_out":
                    t = self._ease_in_out(t)
                elif interpolation_method == "sine":
                    t = np.sin(t * np.pi / 2)

                # Interpolate
                frame = (1 - t) * img1 + t * img2
                frame = frame.astype(np.uint8)

                writer.write(frame)

        # Hold last frame for a moment
        for _ in range(self.fps):
            writer.write(frames_data[-1])

        writer.release()

        print(f"✅ Video created: {output_path}")
        print(f"   Duration: {len(frames_data) * duration_per_transition:.1f}s")
        print(f"   Total frames: {(len(frames_data) - 1) * frames_per_transition}")

        return output_path

    def _ease_in_out(self, t: float) -> float:
        """Smooth ease-in-out curve."""
        return 3 * t**2 - 2 * t**3

    def create_animated_video(
        self,
        prompt: str,
        duration: float = 5.0,
        motion_style: str = "breathing",
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Create animated video using AnimateDiff via Replicate.

        Adds breathing, flowing motion to meditation visualizations.

        Args:
            prompt: Text prompt for the video
            duration: Video duration in seconds
            motion_style: "breathing", "flowing", "dissolving"
            output_name: Custom output filename

        Returns:
            Path to downloaded video
        """
        if not REPLICATE_AVAILABLE:
            print("❌ Replicate package required")
            return None

        # Add motion descriptors based on style
        motion_prompts = {
            "breathing": "gentle pulsing, rhythmic expansion and contraction, breathing motion",
            "flowing": "slow flowing motion, liquid movement, gentle currents",
            "dissolving": "slowly dissolving, particles dispersing, fading edges"
        }

        motion_desc = motion_prompts.get(motion_style, motion_prompts["breathing"])
        full_prompt = f"{prompt}, {motion_desc}, smooth animation, contemplative"

        print(f"\n🎬 Creating animated video...")
        print(f"   Prompt: {prompt}")
        print(f"   Motion: {motion_style}")
        print(f"   Duration: {duration}s")

        try:
            # Use AnimateDiff via Replicate
            # Note: Model name may change, check Replicate for latest
            output = replicate.run(
                "lucataco/animate-diff:beecf59c4aee8d81bf04f0381033dfa10dc16e845b4ae00d281e2fa377e48a9f",
                input={
                    "prompt": full_prompt,
                    "num_frames": int(duration * 8),  # ~8 fps for AnimateDiff
                    "guidance_scale": 7.5,
                    "num_inference_steps": 25
                }
            )

            # Download video
            if output_name is None:
                output_name = f"animated_{motion_style}.mp4"

            output_path = self.output_dir / output_name

            # Download from URL
            if isinstance(output, str):
                video_url = output
            elif isinstance(output, list):
                video_url = output[0]
            else:
                video_url = str(output)

            response = requests.get(video_url)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Animated video created: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error creating animated video: {e}")
            return None

    def create_breathing_loop(
        self,
        base_image: str,
        breath_cycles: int = 3,
        cycle_duration: float = 6.0,
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Create breathing animation from a single image.

        Simulates meditative breathing by gently zooming in/out.

        Args:
            base_image: Path to base image
            breath_cycles: Number of breath cycles
            cycle_duration: Duration per breath cycle (seconds)
            output_name: Custom output filename

        Returns:
            Path to generated video
        """
        if not CV2_AVAILABLE:
            print("❌ OpenCV required")
            return None

        print(f"\n🌬️  Creating breathing animation...")
        print(f"   Cycles: {breath_cycles}")
        print(f"   Cycle duration: {cycle_duration}s")

        # Load base image
        img = cv2.imread(str(base_image))
        if img is None:
            print(f"❌ Could not load {base_image}")
            return None

        img = cv2.resize(img, self.resolution)

        # Generate output filename
        if output_name is None:
            output_name = f"breathing_{breath_cycles}cycles.mp4"

        output_path = self.output_dir / output_name

        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            self.fps,
            self.resolution
        )

        frames_per_cycle = int(cycle_duration * self.fps)
        total_frames = breath_cycles * frames_per_cycle

        for frame_idx in range(total_frames):
            # Calculate breath phase (0 to 2π per cycle)
            cycle_phase = (frame_idx % frames_per_cycle) / frames_per_cycle * 2 * np.pi

            # Breathing curve (sine wave)
            # 1.0 = exhale (normal size)
            # 1.05 = inhale (slightly larger)
            scale = 1.0 + 0.05 * np.sin(cycle_phase)

            # Apply zoom
            frame = self._zoom_image(img, scale)

            # Slight brightness modulation (very subtle)
            brightness = 1.0 + 0.03 * np.sin(cycle_phase)
            frame = np.clip(frame * brightness, 0, 255).astype(np.uint8)

            writer.write(frame)

            if (frame_idx + 1) % frames_per_cycle == 0:
                print(f"   Cycle {(frame_idx + 1) // frames_per_cycle}/{breath_cycles} complete")

        writer.release()

        print(f"✅ Breathing animation created: {output_path}")
        print(f"   Duration: {breath_cycles * cycle_duration:.1f}s")

        return output_path

    def _zoom_image(self, img: np.ndarray, scale: float) -> np.ndarray:
        """Apply zoom transform to image."""
        h, w = img.shape[:2]

        # Calculate new dimensions
        new_h = int(h * scale)
        new_w = int(w * scale)

        # Resize
        zoomed = cv2.resize(img, (new_w, new_h))

        # Crop to original size (center crop)
        y_offset = (new_h - h) // 2
        x_offset = (new_w - w) // 2

        cropped = zoomed[y_offset:y_offset + h, x_offset:x_offset + w]

        return cropped

    def create_comfyui_video(
        self,
        prompt: str,
        workflow_path: str,
        comfyui_url: str = "http://127.0.0.1:8188",
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Generate video using ComfyUI API.

        Requires ComfyUI running locally with API enabled.

        Args:
            prompt: Text prompt
            workflow_path: Path to ComfyUI workflow JSON
            comfyui_url: ComfyUI server URL
            output_name: Custom output filename

        Returns:
            Path to generated video
        """
        print(f"\n🎨 Generating video via ComfyUI...")
        print(f"   Server: {comfyui_url}")
        print(f"   Workflow: {workflow_path}")

        try:
            # Load workflow
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)

            # Update prompt in workflow (assumes specific node structure)
            # This is workflow-dependent - adjust for your ComfyUI setup
            for node_id, node in workflow.items():
                if node.get("class_type") == "CLIPTextEncode":
                    if "inputs" in node and "text" in node["inputs"]:
                        node["inputs"]["text"] = prompt

            # Queue prompt
            response = requests.post(
                f"{comfyui_url}/prompt",
                json={"prompt": workflow}
            )
            response.raise_for_status()

            prompt_id = response.json()["prompt_id"]
            print(f"   Prompt queued: {prompt_id}")

            # Poll for completion (simplified - real implementation needs better handling)
            import time
            for _ in range(60):  # 60 attempts, 2 seconds each = 2 min timeout
                time.sleep(2)

                history_response = requests.get(f"{comfyui_url}/history/{prompt_id}")
                history = history_response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})

                    # Find video output (workflow-dependent)
                    for node_outputs in outputs.values():
                        if "videos" in node_outputs:
                            video_info = node_outputs["videos"][0]

                            # Download video
                            video_url = f"{comfyui_url}/view?filename={video_info['filename']}&subfolder={video_info.get('subfolder', '')}"

                            if output_name is None:
                                output_name = f"comfyui_{prompt_id}.mp4"

                            output_path = self.output_dir / output_name

                            video_response = requests.get(video_url)
                            video_response.raise_for_status()

                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)

                            print(f"✅ Video created: {output_path}")
                            return output_path

            print("❌ ComfyUI generation timed out")
            return None

        except Exception as e:
            print(f"❌ ComfyUI error: {e}")
            return None


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate meditation videos")
    parser.add_argument("--mode", choices=["interpolate", "animate", "breathing"],
                       required=True, help="Generation mode")
    parser.add_argument("--images", nargs="+", help="Images for interpolation")
    parser.add_argument("--prompt", help="Text prompt for animation")
    parser.add_argument("--duration", type=float, default=5.0,
                       help="Video duration")
    parser.add_argument("--output", help="Output filename")

    args = parser.parse_args()

    generator = VideoGenerator()

    if args.mode == "interpolate":
        if not args.images:
            print("❌ --images required for interpolation mode")
        else:
            generator.create_interpolation_video(
                images=args.images,
                duration_per_transition=args.duration,
                output_name=args.output
            )

    elif args.mode == "animate":
        if not args.prompt:
            print("❌ --prompt required for animate mode")
        else:
            generator.create_animated_video(
                prompt=args.prompt,
                duration=args.duration,
                output_name=args.output
            )

    elif args.mode == "breathing":
        if not args.images or len(args.images) != 1:
            print("❌ Single image required for breathing mode")
        else:
            generator.create_breathing_loop(
                base_image=args.images[0],
                breath_cycles=3,
                cycle_duration=args.duration,
                output_name=args.output
            )
