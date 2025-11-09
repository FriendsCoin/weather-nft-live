#!/usr/bin/env python3
"""
Generate complete multimedia memories for THE LISTENER.

Creates immersive meditation memories with:
- Poetic text interpretations (Claude)
- Animated visuals (video)
- Voice narration (Coqui TTS)
- Combined audio/video output

This is Phase 2.5: Enhanced multimedia interpretation.

Usage:
    python scripts/generate_multimedia.py --checkpoint checkpoints/best_model.pt --num-samples 5
"""

import sys
from pathlib import Path
import os
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.sampler import LatentSampler
from utils.llm_interface import LLMInterpreter
from utils.image_gen import ImageGenerator
from utils.video_gen import VideoGenerator
from utils.audio_gen import VoiceGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate multimedia meditation memories")
    parser.add_argument("--checkpoint", default="data/checkpoints/best_model.pt",
                       help="Path to trained model checkpoint")
    parser.add_argument("--num-samples", type=int, default=5,
                       help="Number of memories to generate")

    # API keys
    parser.add_argument("--anthropic-key", help="Anthropic API key")
    parser.add_argument("--replicate-key", help="Replicate API key")

    # Output options
    parser.add_argument("--output-dir", default="data/outputs",
                       help="Output directory")

    # Media options
    parser.add_argument("--skip-images", action="store_true",
                       help="Skip image generation")
    parser.add_argument("--skip-video", action="store_true",
                       help="Skip video generation")
    parser.add_argument("--skip-voice", action="store_true",
                       help="Skip voice generation")

    # Video settings
    parser.add_argument("--video-mode", default="breathing",
                       choices=["breathing", "interpolation", "animated"],
                       help="Video generation mode")
    parser.add_argument("--video-duration", type=float, default=6.0,
                       help="Video duration (seconds)")

    # Voice settings
    parser.add_argument("--voice-style", default="calm",
                       choices=["calm", "whispered", "deep"],
                       help="Voice narration style")

    args = parser.parse_args()

    print("=" * 70)
    print("THE LISTENER - Multimedia Memory Generation")
    print("=" * 70)

    # Check checkpoint
    if not Path(args.checkpoint).exists():
        print(f"\n❌ Checkpoint not found: {args.checkpoint}")
        print("\nTrain model first: python scripts/train.py")
        sys.exit(1)

    # Setup output directories
    output_dir = Path(args.output_dir)
    images_dir = output_dir / "images"
    videos_dir = output_dir / "videos"
    audio_dir = output_dir / "audio"

    for d in [images_dir, videos_dir, audio_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # =================================================================
    # Step 1: Sample from latent space
    # =================================================================
    print(f"\n[Step 1/6] Loading trained model...")
    sampler = LatentSampler.from_checkpoint(args.checkpoint)

    print(f"\n[Step 2/6] Generating {args.num_samples} samples from latent space...")
    samples = sampler.generate_random_samples(n=args.num_samples)

    # Save samples
    samples_path = output_dir / "multimedia_samples.json"
    sampler.save_samples(samples, str(samples_path))

    # Create summaries for LLM
    summaries = [sampler.summarize_sample(s) for s in samples]

    print("\n📝 Sample summaries:")
    for i, summary in enumerate(summaries[:2]):  # Show first 2
        print(f"\n{summary}")

    # =================================================================
    # Step 3: Generate text interpretations
    # =================================================================
    print(f"\n[Step 3/6] Generating poetic interpretations with Claude...")

    try:
        interpreter = LLMInterpreter(
            api_key=args.anthropic_key,
            temperature=0.8
        )

        interpretations = interpreter.interpret_batch(
            sample_summaries=summaries,
            save_path=str(output_dir / "multimedia_interpretations.json")
        )

        print("\n🎨 Interpretations:")
        for i, interp in enumerate(interpretations[:3]):  # Show first 3
            print(f"\n{i+1}. {interp['text']}")

    except Exception as e:
        print(f"\n⚠️  Could not generate interpretations: {e}")
        print("Set ANTHROPIC_API_KEY or use --anthropic-key")
        interpretations = []

    if not interpretations:
        print("\n❌ Cannot continue without interpretations")
        sys.exit(1)

    # =================================================================
    # Step 4: Generate images
    # =================================================================
    if not args.skip_images:
        print(f"\n[Step 4/6] Generating images with Stable Diffusion...")

        try:
            image_gen = ImageGenerator(api_key=args.replicate_key)

            image_results = image_gen.generate_batch(
                interpretations=interpretations,
                output_dir=str(images_dir),
                delay=2.0
            )

            successful_images = [r for r in image_results if r.get('success')]
            print(f"\n✅ Generated {len(successful_images)}/{args.num_samples} images")

        except Exception as e:
            print(f"\n⚠️  Image generation failed: {e}")
            image_results = []
    else:
        print(f"\n[Step 4/6] Skipping image generation")
        image_results = []

    # =================================================================
    # Step 5: Generate videos
    # =================================================================
    if not args.skip_video and image_results:
        print(f"\n[Step 5/6] Generating videos...")

        video_gen = VideoGenerator(
            output_dir=str(videos_dir),
            fps=30
        )

        video_paths = []

        for i, result in enumerate(image_results):
            if not result.get('success'):
                continue

            image_path = result['image_path']
            sample_id = result['sample_id']

            print(f"\n   Video {i+1}/{len(image_results)}...")

            if args.video_mode == "breathing":
                # Breathing animation from single image
                video_path = video_gen.create_breathing_loop(
                    base_image=image_path,
                    breath_cycles=3,
                    cycle_duration=args.video_duration,
                    output_name=f"memory_{sample_id:03d}_breathing.mp4"
                )

            elif args.video_mode == "animated":
                # AnimateDiff animation
                prompt = interpretations[i].get('text', '')
                video_path = video_gen.create_animated_video(
                    prompt=prompt,
                    duration=args.video_duration,
                    motion_style="breathing",
                    output_name=f"memory_{sample_id:03d}_animated.mp4"
                )

            elif args.video_mode == "interpolation" and i > 0:
                # Interpolation between consecutive images
                prev_image = image_results[i-1]['image_path']
                video_path = video_gen.create_interpolation_video(
                    images=[prev_image, image_path],
                    duration_per_transition=args.video_duration,
                    output_name=f"memory_{i-1:03d}_to_{sample_id:03d}_interp.mp4"
                )
            else:
                video_path = None

            if video_path:
                video_paths.append((sample_id, str(video_path), interpretations[i]['text']))

        print(f"\n✅ Generated {len(video_paths)} videos")

    else:
        print(f"\n[Step 5/6] Skipping video generation")
        video_paths = []

    # =================================================================
    # Step 6: Generate voice narration and combine
    # =================================================================
    if not args.skip_voice and (video_paths or interpretations):
        print(f"\n[Step 6/6] Generating voice narration...")

        voice_gen = VoiceGenerator(output_dir=str(audio_dir))

        final_outputs = []

        if video_paths:
            # Add voice to videos
            for sample_id, video_path, text in video_paths:
                print(f"\n   Adding voice to video {sample_id}...")

                final_video = voice_gen.add_voice_to_video(
                    video_path=video_path,
                    text=text,
                    voice_style=args.voice_style,
                    output_name=f"memory_{sample_id:03d}_final.mp4"
                )

                if final_video:
                    final_outputs.append({
                        'type': 'video_with_voice',
                        'sample_id': sample_id,
                        'path': str(final_video),
                        'text': text
                    })

        else:
            # Generate standalone audio
            for i, interp in enumerate(interpretations):
                print(f"\n   Voice {i+1}/{len(interpretations)}...")

                audio_path = voice_gen.generate_voice(
                    text=interp['text'],
                    voice_style=args.voice_style,
                    output_name=f"memory_{i:03d}_voice.wav"
                )

                if audio_path:
                    final_outputs.append({
                        'type': 'audio',
                        'sample_id': i,
                        'path': str(audio_path),
                        'text': interp['text']
                    })

        print(f"\n✅ Generated {len(final_outputs)} final outputs with voice")

        # Save manifest
        import json
        manifest_path = output_dir / "multimedia_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(final_outputs, f, indent=2)

        print(f"\n📋 Manifest saved: {manifest_path}")

    else:
        print(f"\n[Step 6/6] Skipping voice generation")

    # =================================================================
    # Create multimedia gallery
    # =================================================================
    print(f"\n[Final] Creating multimedia gallery...")

    if video_paths or image_results:
        create_multimedia_gallery(
            output_dir=output_dir,
            interpretations=interpretations,
            image_results=image_results,
            video_paths=video_paths
        )

    print("\n" + "=" * 70)
    print("✅ Multimedia generation complete!")
    print("=" * 70)
    print(f"\nOutputs:")
    print(f"  📝 Text: {output_dir}/multimedia_interpretations.json")
    if not args.skip_images:
        print(f"  🖼️  Images: {images_dir}/")
    if not args.skip_video:
        print(f"  🎬 Videos: {videos_dir}/")
    if not args.skip_voice:
        print(f"  🎙️  Audio: {audio_dir}/")
    print(f"  🌐 Gallery: {output_dir}/multimedia_gallery.html")


def create_multimedia_gallery(
    output_dir: Path,
    interpretations: list,
    image_results: list,
    video_paths: list
):
    """Create HTML gallery with images, videos, and text."""

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>THE LISTENER - Multimedia Memories</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 40px;
            max-width: 1600px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            font-weight: 300;
            letter-spacing: 3px;
            margin-bottom: 20px;
        }
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 0.9em;
            margin-bottom: 60px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 50px;
        }
        .memory {
            background: #1a1a1a;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .memory video {
            width: 100%;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .memory img {
            width: 100%;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .sample-id {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 12px;
        }
        .interpretation {
            font-style: italic;
            line-height: 1.7;
            color: #ccc;
            font-size: 1.05em;
        }
        .media-type {
            display: inline-block;
            background: #2a2a2a;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.75em;
            color: #888;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>THE LISTENER</h1>
    <div class="subtitle">
        AI-generated multimedia memories of witnessed meditation states
    </div>
    <div class="gallery">
"""

    # Add each memory
    for i, interp in enumerate(interpretations):
        sample_id = interp.get('sample_id', i)

        # Find video if exists
        video_file = None
        for vid_id, vid_path, _ in video_paths:
            if vid_id == sample_id:
                video_file = Path(vid_path).name
                break

        # Find image if exists
        image_file = None
        for result in image_results:
            if result.get('sample_id') == sample_id and result.get('success'):
                image_file = Path(result['image_path']).name
                break

        if not video_file and not image_file:
            continue

        media_type = "Video + Voice" if video_file else "Image"

        html += f"""
        <div class="memory">
            <div class="sample-id">Memory {sample_id}</div>
            <div class="media-type">{media_type}</div>
"""

        if video_file:
            html += f"""
            <video controls loop>
                <source src="videos/{video_file}" type="video/mp4">
            </video>
"""
        elif image_file:
            html += f"""
            <img src="images/{image_file}" alt="Memory {sample_id}">
"""

        html += f"""
            <div class="interpretation">{interp.get('text', '')}</div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    # Save
    gallery_path = output_dir / "multimedia_gallery.html"
    with open(gallery_path, 'w') as f:
        f.write(html)

    print(f"   Gallery: {gallery_path}")


if __name__ == "__main__":
    main()
