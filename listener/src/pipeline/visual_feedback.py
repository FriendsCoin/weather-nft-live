#!/usr/bin/env python3
"""
Visual Biofeedback System

Real-time visual feedback for meditation using pygame.
Creates an immersive, responsive visualization that reacts to EEG data.

Visualization Features:
- Pulsing circle that grows with meditation depth
- Color shifts based on alpha wave performance
- Particle effects for deep states
- Smooth animations and transitions
- Poetic text messages
- Optional fullscreen mode

Visual Mapping:
- Circle size → Meditation depth (bigger = deeper)
- Circle color → Alpha performance (blue → purple → pink)
- Glow intensity → Quality score
- Particle density → Theta waves (creative states)
- Background darkness → Delta reduction (alertness)
- Animation speed → Inverse of depth (slower = deeper)

Usage:
    from src.pipeline.visual_feedback import VisualFeedback

    viz = VisualFeedback(width=1920, height=1080, fullscreen=False)
    viz.update({
        'depth': 75.3,
        'quality': 92.1,
        'alpha_plus': 1.2,
        'state': 'deep',
        'message': 'You are descending into stillness'
    })

    # Run visualization loop
    viz.run()  # Blocks until window closed
"""

import pygame
import math
import time
import random
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class Particle:
    """Particle for visual effects"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    life: float
    color: Tuple[int, int, int]


class VisualFeedback:
    """
    Pygame-based visual biofeedback system
    """

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fullscreen: bool = False,
        fps: int = 60,
        theme: str = 'dark'
    ):
        """
        Initialize visual feedback system

        Args:
            width: Window width
            height: Window height
            fullscreen: Run in fullscreen mode
            fps: Target frame rate
            theme: Visual theme ('dark', 'light', 'cosmic')
        """
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.fps = fps
        self.theme = theme

        # Create window
        if fullscreen:
            self.screen = pygame.display.set_mode(
                (width, height),
                pygame.FULLSCREEN | pygame.DOUBLEBUF
            )
        else:
            self.screen = pygame.display.set_mode((width, height))

        pygame.display.set_caption("THE LISTENER - Biofeedback")

        # Clock for frame rate
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.SysFont('Arial', 72, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)

        # State
        self.running = True
        self.depth = 0.0
        self.quality = 0.0
        self.alpha_plus = 1.0
        self.state = "calm"
        self.message = "Begin your meditation"

        # Animation state
        self.circle_size = 100.0  # Current size (animated)
        self.target_size = 100.0  # Target size (from depth)
        self.circle_hue = 0.6  # HSV hue (0-1)
        self.glow_intensity = 0.5
        self.rotation = 0.0

        # Particles
        self.particles: List[Particle] = []
        self.max_particles = 200

        # History for smoothing
        self.depth_history = deque(maxlen=60)  # 1 second at 60fps

        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()

        print(f"🎨 Visual Feedback initialized ({width}x{height})")

    def update(self, state: Dict[str, Any]):
        """
        Update visualization with new meditation state

        Args:
            state: Dictionary with meditation metrics
        """
        # Update metrics
        self.depth = state.get('depth', self.depth)
        self.quality = state.get('quality', self.quality)
        self.alpha_plus = state.get('alpha_plus', self.alpha_plus)
        self.state = state.get('state', self.state)
        self.message = state.get('message', self.message)

        # Add to history
        self.depth_history.append(self.depth)

        # Calculate smoothed depth
        smoothed_depth = sum(self.depth_history) / len(self.depth_history)

        # Update visual parameters
        self._update_visual_params(smoothed_depth)

    def _update_visual_params(self, depth: float):
        """Update visual parameters based on meditation depth"""
        # Target circle size (50-400 pixels)
        self.target_size = 50 + (depth / 100.0) * 350

        # Hue: Blue (0.6) → Purple (0.75) → Pink (0.85)
        alpha_factor = min(self.alpha_plus, 2.0) / 2.0
        self.circle_hue = 0.6 + alpha_factor * 0.25

        # Glow intensity
        self.glow_intensity = 0.3 + (self.quality / 100.0) * 0.7

    def _smooth_animate(self, current: float, target: float, speed: float = 0.1) -> float:
        """Smooth animation using exponential interpolation"""
        return current + (target - current) * speed

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV color to RGB"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def _draw_background(self):
        """Draw animated background"""
        # Background color based on depth (darker = deeper)
        if self.theme == 'dark':
            darkness = 1.0 - (self.depth / 200.0)  # 0.5-1.0
            bg_color = (
                int(10 * darkness),
                int(14 * darkness),
                int(39 * darkness)
            )
        elif self.theme == 'cosmic':
            bg_color = (5, 5, 15)
        else:
            bg_color = (240, 240, 250)

        self.screen.fill(bg_color)

        # Subtle gradient circles in background
        if self.theme in ['dark', 'cosmic']:
            for i in range(3):
                offset_x = math.sin(self.rotation * 0.5 + i * 2) * 100
                offset_y = math.cos(self.rotation * 0.3 + i * 2) * 100
                x = self.width // 2 + int(offset_x)
                y = self.height // 2 + int(offset_y)
                radius = 200 + i * 100
                color = self._hsv_to_rgb(
                    self.circle_hue + i * 0.1,
                    0.3,
                    0.1
                )
                self._draw_glow_circle(x, y, radius, color, alpha=20)

    def _draw_glow_circle(
        self,
        x: int,
        y: int,
        radius: int,
        color: Tuple[int, int, int],
        alpha: int = 128
    ):
        """Draw a circle with glow effect"""
        # Create surface with alpha
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        # Draw multiple circles with decreasing alpha for glow
        for i in range(5):
            glow_radius = int(radius * (1.0 + i * 0.2))
            glow_alpha = int(alpha / (i + 1))
            glow_color = (*color, glow_alpha)
            pygame.draw.circle(
                surface,
                glow_color,
                (radius, radius),
                glow_radius
            )

        # Blit to screen
        self.screen.blit(surface, (x - radius, y - radius))

    def _draw_main_circle(self):
        """Draw main meditation circle"""
        # Animate size
        self.circle_size = self._smooth_animate(
            self.circle_size,
            self.target_size,
            speed=0.05
        )

        # Position
        x = self.width // 2
        y = self.height // 2

        # Color
        saturation = 0.6 + (self.depth / 100.0) * 0.4  # More saturated when deep
        value = 0.5 + (self.quality / 200.0)  # Brighter with good quality
        color = self._hsv_to_rgb(self.circle_hue, saturation, value)

        # Draw glow
        glow_alpha = int(100 * self.glow_intensity)
        self._draw_glow_circle(
            x, y,
            int(self.circle_size * 1.5),
            color,
            alpha=glow_alpha
        )

        # Draw main circle
        pygame.draw.circle(
            self.screen,
            color,
            (x, y),
            int(self.circle_size)
        )

        # Draw inner circle (breathing effect)
        breath_phase = math.sin(self.rotation * 2) * 0.5 + 0.5
        inner_size = int(self.circle_size * (0.6 + breath_phase * 0.2))
        inner_color = self._hsv_to_rgb(self.circle_hue, saturation * 0.5, value * 1.2)
        pygame.draw.circle(
            self.screen,
            inner_color,
            (x, y),
            inner_size
        )

    def _update_particles(self):
        """Update and spawn particles"""
        # Spawn new particles based on depth
        if self.depth > 50 and random.random() < 0.3:
            self._spawn_particle()

        # Update existing particles
        for particle in self.particles[:]:
            particle.x += particle.vx
            particle.y += particle.vy
            particle.life -= 0.02

            # Remove dead particles
            if particle.life <= 0:
                self.particles.remove(particle)

    def _spawn_particle(self):
        """Spawn a new particle"""
        if len(self.particles) >= self.max_particles:
            return

        # Spawn from circle edge
        angle = random.uniform(0, 2 * math.pi)
        spawn_radius = self.circle_size

        x = self.width // 2 + math.cos(angle) * spawn_radius
        y = self.height // 2 + math.sin(angle) * spawn_radius

        # Velocity (outward)
        speed = random.uniform(0.5, 2.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        # Color (similar to circle)
        color = self._hsv_to_rgb(
            self.circle_hue + random.uniform(-0.1, 0.1),
            0.8,
            0.9
        )

        particle = Particle(
            x=x, y=y,
            vx=vx, vy=vy,
            size=random.uniform(2, 6),
            life=1.0,
            color=color
        )

        self.particles.append(particle)

    def _draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            alpha = int(particle.life * 255)
            color = (*particle.color, alpha)

            # Create surface with alpha
            size = int(particle.size)
            surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (size, size), size)

            self.screen.blit(
                surface,
                (int(particle.x - size), int(particle.y - size))
            )

    def _draw_text(self):
        """Draw meditation state and message"""
        # State indicator
        state_text = self.font_medium.render(
            self.state.upper(),
            True,
            (200, 200, 255)
        )
        state_rect = state_text.get_rect(
            center=(self.width // 2, 100)
        )
        self.screen.blit(state_text, state_rect)

        # Poetic message
        message_text = self.font_small.render(
            self.message,
            True,
            (180, 180, 220)
        )
        message_rect = message_text.get_rect(
            center=(self.width // 2, self.height - 100)
        )
        self.screen.blit(message_text, message_rect)

        # Depth indicator
        depth_text = self.font_small.render(
            f"Depth: {self.depth:.1f}",
            True,
            (150, 150, 200)
        )
        self.screen.blit(depth_text, (50, 50))

        # Quality indicator
        quality_text = self.font_small.render(
            f"Quality: {self.quality:.1f}",
            True,
            (150, 150, 200)
        )
        self.screen.blit(quality_text, (50, 90))

    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    # Toggle fullscreen
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(
                            (self.width, self.height),
                            pygame.FULLSCREEN | pygame.DOUBLEBUF
                        )
                    else:
                        self.screen = pygame.display.set_mode(
                            (self.width, self.height)
                        )
                elif event.key == pygame.K_s:
                    # Save screenshot
                    self._save_screenshot()

    def _save_screenshot(self):
        """Save current visualization as screenshot"""
        from datetime import datetime
        from pathlib import Path

        output_dir = Path("data/screenshots")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meditation_{timestamp}.png"
        filepath = output_dir / filename

        pygame.image.save(self.screen, str(filepath))
        print(f"📸 Screenshot saved: {filepath}")

    def render(self):
        """Render single frame"""
        # Update rotation
        self.rotation += 0.01

        # Draw layers
        self._draw_background()
        self._update_particles()
        self._draw_particles()
        self._draw_main_circle()
        self._draw_text()

        # Update display
        pygame.display.flip()

        # Maintain frame rate
        self.clock.tick(self.fps)

        self.frame_count += 1

    def run(self):
        """
        Main visualization loop
        Blocks until window is closed
        """
        print("\n🎬 Starting visualization")
        print("   Press ESC to exit")
        print("   Press F to toggle fullscreen")
        print("   Press S to save screenshot\n")

        while self.running:
            self._handle_events()
            self.render()

        # Cleanup
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0

        print(f"\n⏹️  Visualization stopped")
        print(f"   Frames: {self.frame_count}")
        print(f"   Avg FPS: {avg_fps:.1f}\n")

        pygame.quit()

    def close(self):
        """Close the visualization"""
        self.running = False
        pygame.quit()


if __name__ == "__main__":
    """
    Test the visual feedback system with simulated data
    """
    import random

    print("=" * 60)
    print("  🎨 Visual Feedback Test")
    print("=" * 60)
    print()

    # Create visualization
    viz = VisualFeedback(
        width=1280,
        height=720,
        fullscreen=False,
        theme='dark'
    )

    # Simulate meditation session
    depth = 20.0
    quality = 85.0
    alpha_plus = 0.8

    states = ["distracted", "calm", "focused", "deep"]
    messages = {
        "distracted": "Your mind wanders through familiar paths",
        "calm": "Stillness begins to settle",
        "focused": "You are finding your center",
        "deep": "You are descending into infinite space"
    }

    # Update loop (separate from render loop)
    import threading

    def simulation_loop():
        nonlocal depth, quality, alpha_plus

        while viz.running:
            # Simulate gradual deepening
            depth = min(95, depth + random.uniform(-3, 5))
            quality = 85 + random.uniform(-10, 10)
            alpha_plus = max(0.5, min(2.0, alpha_plus + random.uniform(-0.1, 0.15)))

            # Determine state
            if depth > 70:
                state = "deep"
            elif depth > 50:
                state = "focused"
            elif depth > 30:
                state = "calm"
            else:
                state = "distracted"

            # Update visualization
            viz.update({
                'depth': depth,
                'quality': quality,
                'alpha_plus': alpha_plus,
                'state': state,
                'message': messages[state]
            })

            time.sleep(0.5)  # 2 Hz update rate

    # Start simulation thread
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()

    # Run visualization (blocking)
    viz.run()
