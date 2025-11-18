"""
Video Compiler for THE LISTENER

Creates video compilations:
- Timelapse of all sessions
- Progress evolution video
- Gallery slideshow
- Exhibition loop

Uses opencv for video creation.
"""

from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import cv2
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


class VideoCompiler:
    """
    Compile videos from meditation sessions.

    Usage:
        compiler = VideoCompiler()

        # Create progress timelapse
        compiler.create_progress_video(
            sessions,
            output_path="videos/progress_30days.mp4"
        )

        # Create gallery slideshow
        compiler.create_gallery_video(
            image_paths,
            output_path="videos/gallery.mp4"
        )
    """

    def __init__(
        self,
        fps: int = 30,
        resolution: tuple = (1920, 1080),
        codec: str = 'mp4v'
    ):
        """
        Initialize video compiler.

        Args:
            fps: Frames per second
            resolution: Video resolution (width, height)
            codec: Video codec ('mp4v', 'H264', etc.)
        """
        self.fps = fps
        self.resolution = resolution
        self.codec = codec

        print(f"🎬 Video Compiler initialized")
        print(f"   Resolution: {resolution[0]}x{resolution[1]}")
        print(f"   FPS: {fps}")

    def create_progress_video(
        self,
        sessions: List[Dict],
        output_path: str,
        duration_per_session: float = 2.0,
        show_stats: bool = True
    ):
        """
        Create progress timelapse video.

        Each session shows depth visualization + statistics.

        Args:
            sessions: List of session dictionaries
            output_path: Output video path
            duration_per_session: Seconds per session
            show_stats: Show statistics overlay
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            self.fps,
            self.resolution
        )

        print(f"\n🎬 Creating progress video...")
        print(f"   Sessions: {len(sessions)}")
        print(f"   Duration: {len(sessions) * duration_per_session:.1f}s")

        frames_per_session = int(self.fps * duration_per_session)

        for i, session in enumerate(sessions):
            print(f"   Processing session {i+1}/{len(sessions)}", end='\r')

            # Create frame for this session
            frame = self._create_session_frame(session, show_stats)

            # Write frame multiple times for duration
            for _ in range(frames_per_session):
                out.write(frame)

        out.release()
        print(f"\n✅ Video created: {output_path}")
        return output_path

    def _create_session_frame(
        self,
        session: Dict,
        show_stats: bool = True
    ) -> np.ndarray:
        """
        Create single frame for a session.

        Args:
            session: Session data
            show_stats: Show statistics overlay

        Returns:
            Frame as numpy array (BGR)
        """
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor='#0a0e27')
        ax.set_facecolor('#0a0e27')

        # Draw circle for meditation depth
        depth = session.get('mean_depth', 0)
        quality = session.get('quality_score', 0)

        # Circle size based on depth
        circle_size = 0.3 + (depth / 100) * 0.6

        # Color based on quality
        hue = depth / 100  # 0 to 1
        color = plt.cm.viridis(hue)

        circle = plt.Circle((0.5, 0.5), circle_size, color=color, alpha=0.8)
        ax.add_patch(circle)

        # Add stats overlay
        if show_stats:
            stats_text = f"""
Session: {session.get('session_id', 'Unknown')}
Date: {session.get('recorded_at', 'Unknown')[:10] if session.get('recorded_at') else 'Unknown'}

Depth: {depth:.1f}/100
Quality: {quality:.1f}/100
Alpha: {session.get('alpha_performance', 0):.2f}
            """

            ax.text(0.02, 0.98, stats_text.strip(),
                   transform=ax.transAxes,
                   verticalalignment='top',
                   fontsize=14,
                   color='white',
                   family='monospace',
                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

        # Title
        ax.text(0.5, 0.95, 'THE LISTENER - Meditation Progress',
               transform=ax.transAxes,
               ha='center',
               fontsize=20,
               color='#7c4dff',
               fontweight='bold')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Convert to image
        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)

        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Resize to target resolution
        img_bgr = cv2.resize(img_bgr, self.resolution)

        return img_bgr

    def create_gallery_video(
        self,
        image_paths: List[str],
        output_path: str,
        duration_per_image: float = 3.0,
        transition: str = 'fade'
    ):
        """
        Create slideshow video from images.

        Args:
            image_paths: List of image file paths
            output_path: Output video path
            duration_per_image: Seconds per image
            transition: 'fade', 'cut', or 'slide'
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            self.fps,
            self.resolution
        )

        print(f"\n🎬 Creating gallery video...")
        print(f"   Images: {len(image_paths)}")
        print(f"   Duration: {len(image_paths) * duration_per_image:.1f}s")

        frames_per_image = int(self.fps * duration_per_image)
        transition_frames = int(self.fps * 0.5) if transition == 'fade' else 0

        for i, img_path in enumerate(image_paths):
            print(f"   Processing image {i+1}/{len(image_paths)}", end='\r')

            # Load and resize image
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"\n⚠️  Could not load: {img_path}")
                continue

            img = self._resize_and_pad(img, self.resolution)

            # Write frames
            if transition == 'fade' and i < len(image_paths) - 1:
                # Write image frames
                for _ in range(frames_per_image - transition_frames):
                    out.write(img)

                # Fade transition to next image
                next_img = cv2.imread(str(image_paths[i + 1]))
                if next_img is not None:
                    next_img = self._resize_and_pad(next_img, self.resolution)

                    for t in range(transition_frames):
                        alpha = t / transition_frames
                        blended = cv2.addWeighted(img, 1 - alpha, next_img, alpha, 0)
                        out.write(blended)
            else:
                # No transition, just write frames
                for _ in range(frames_per_image):
                    out.write(img)

        out.release()
        print(f"\n✅ Gallery video created: {output_path}")
        return output_path

    def _resize_and_pad(
        self,
        img: np.ndarray,
        target_size: tuple,
        bg_color: tuple = (10, 14, 39)  # Dark background
    ) -> np.ndarray:
        """
        Resize image to fit target size with padding.

        Args:
            img: Input image
            target_size: (width, height)
            bg_color: Background color (BGR)

        Returns:
            Resized and padded image
        """
        h, w = img.shape[:2]
        target_w, target_h = target_size

        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize
        resized = cv2.resize(img, (new_w, new_h))

        # Create canvas
        canvas = np.full((target_h, target_w, 3), bg_color, dtype=np.uint8)

        # Center image on canvas
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2

        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

        return canvas

    def create_evolution_video(
        self,
        sessions: List[Dict],
        output_path: str,
        style: str = 'line_graph'
    ):
        """
        Create evolution video showing progress over time.

        Args:
            sessions: List of session dictionaries
            output_path: Output video path
            style: 'line_graph', 'bar_race', or 'circle_grow'
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            self.fps,
            self.resolution
        )

        print(f"\n🎬 Creating evolution video ({style})...")

        depths = [s.get('mean_depth', 0) for s in sessions]
        qualities = [s.get('quality_score', 0) for s in sessions]

        # Create frames showing gradual reveal
        for i in range(1, len(sessions) + 1):
            frame = self._create_evolution_frame(
                sessions[:i],
                depths[:i],
                qualities[:i],
                style
            )

            # Write frame (hold for 0.5 seconds each)
            for _ in range(int(self.fps * 0.5)):
                out.write(frame)

        # Hold final frame for 2 seconds
        for _ in range(int(self.fps * 2)):
            out.write(frame)

        out.release()
        print(f"✅ Evolution video created: {output_path}")
        return output_path

    def _create_evolution_frame(
        self,
        sessions: List[Dict],
        depths: List[float],
        qualities: List[float],
        style: str
    ) -> np.ndarray:
        """Create single frame of evolution animation."""
        fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor='#0a0e27')

        if style == 'line_graph':
            # Line graph revealing over time
            x = list(range(len(depths)))
            ax.plot(x, depths, marker='o', linewidth=3, markersize=8,
                   color='#7c4dff', label='Depth')
            ax.plot(x, qualities, marker='s', linewidth=3, markersize=8,
                   color='#00e676', label='Quality')

            ax.set_ylim(0, 100)
            ax.set_xlabel('Session', fontsize=14, color='white')
            ax.set_ylabel('Score', fontsize=14, color='white')
            ax.set_title(f'Meditation Progress - Session {len(depths)}',
                        fontsize=20, color='#7c4dff', fontweight='bold', pad=20)
            ax.legend(fontsize=14)
            ax.grid(True, alpha=0.3, color='white')
            ax.set_facecolor('#0a0e27')

        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')

        # Convert to image
        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)

        # Convert RGB to BGR
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img_bgr = cv2.resize(img_bgr, self.resolution)

        return img_bgr


# Example usage
if __name__ == "__main__":
    print("Video Compiler Example")
    print()
    print("Usage:")
    print("  from src.utils.video_compiler import VideoCompiler")
    print("  ")
    print("  compiler = VideoCompiler()")
    print("  compiler.create_progress_video(sessions, 'progress.mp4')")
    print("  compiler.create_gallery_video(images, 'gallery.mp4')")
