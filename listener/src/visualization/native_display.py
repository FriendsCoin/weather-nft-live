"""
Native Visualization for NESCIENCE (No TouchDesigner Required)

Real-time visualization using Python native libraries (matplotlib).
Useful for testing without TouchDesigner, development, and simple installations.

Usage:
    from visualization.native_display import NativeDisplay

    display = NativeDisplay()
    display.start()
    display.update_state('FLOW', intensity=0.75, alpha=0.6, awakening=0.15)
    display.stop()

Features:
- Real-time state visualization
- Band power meters (alpha, beta, theta, delta)
- Character awakening progress
- Poetry display
- Matplotlib-based (no external dependencies)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from typing import Optional, Dict
from collections import deque
from datetime import datetime
import threading


class NativeDisplay:
    """
    Real-time visualization using matplotlib

    Alternative to TouchDesigner for testing and development.
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize native display

        Args:
            window_size: Number of samples to show in history (default: 100)
        """
        self.window_size = window_size

        # Data buffers
        self.state_history = deque(maxlen=window_size)
        self.alpha_history = deque(maxlen=window_size)
        self.beta_history = deque(maxlen=window_size)
        self.theta_history = deque(maxlen=window_size)
        self.delta_history = deque(maxlen=window_size)
        self.intensity_history = deque(maxlen=window_size)

        # Current values
        self.current_state = "SETTLING"
        self.current_intensity = 0.5
        self.current_bands = {'alpha': 0.5, 'beta': 0.5, 'theta': 0.5, 'delta': 0.5}
        self.current_awakening = 0.0
        self.current_poetry = "Awaiting first state..."

        # State colors (contemplative palette)
        self.state_colors = {
            'SETTLING': '#8B7355',  # Brown/earth
            'FLOW': '#4A90A4',      # Water blue
            'DEEP': '#2C3E50',      # Deep blue-gray
            'LIMINAL': '#7B68A6',   # Purple/twilight
            'PRESENT': '#E8DCC4',   # Warm white
        }

        # Figure and axes
        self.fig = None
        self.axes = {}
        self.animation = None
        self.is_running = False

    def start(self):
        """Start the visualization window"""
        if self.is_running:
            return

        self.is_running = True

        # Create figure with dark background
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.canvas.manager.set_window_title('NESCIENCE - Native Visualization')

        # Create layout
        gs = self.fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. Current state (large, top center)
        self.axes['state'] = self.fig.add_subplot(gs[0, :])

        # 2. Band power history (middle left, 2 cols)
        self.axes['bands'] = self.fig.add_subplot(gs[1, :2])

        # 3. Band power meters (middle right)
        self.axes['meters'] = self.fig.add_subplot(gs[1, 2])

        # 4. Character awakening (bottom left)
        self.axes['awakening'] = self.fig.add_subplot(gs[2, 0])

        # 5. Intensity history (bottom middle)
        self.axes['intensity'] = self.fig.add_subplot(gs[2, 1])

        # 6. Poetry/description (bottom right)
        self.axes['poetry'] = self.fig.add_subplot(gs[2, 2])

        # Start animation
        self.animation = FuncAnimation(
            self.fig,
            self._update_plots,
            interval=100,  # 10 FPS
            blit=False
        )

        plt.show(block=False)
        plt.pause(0.1)

    def stop(self):
        """Stop the visualization"""
        self.is_running = False
        if self.fig:
            plt.close(self.fig)

    def update_state(
        self,
        state: str,
        intensity: float,
        alpha: float,
        beta: float = None,
        theta: float = None,
        delta: float = None,
        awakening: float = 0.0,
        poetry: Optional[str] = None
    ):
        """
        Update visualization with new state

        Args:
            state: Meditation state (SETTLING, FLOW, DEEP, LIMINAL, PRESENT)
            intensity: State intensity (0-1)
            alpha: Alpha band power (0-1)
            beta: Beta band power (0-1, optional)
            theta: Theta band power (0-1, optional)
            delta: Delta band power (0-1, optional)
            awakening: Character awakening level (0-1)
            poetry: Poetic description (optional)
        """
        # Update current values
        self.current_state = state
        self.current_intensity = intensity
        self.current_bands['alpha'] = alpha
        if beta is not None:
            self.current_bands['beta'] = beta
        if theta is not None:
            self.current_bands['theta'] = theta
        if delta is not None:
            self.current_bands['delta'] = delta
        self.current_awakening = awakening

        if poetry:
            self.current_poetry = poetry

        # Append to history
        self.state_history.append(state)
        self.alpha_history.append(alpha)
        self.beta_history.append(beta if beta is not None else 0.5)
        self.theta_history.append(theta if theta is not None else 0.5)
        self.delta_history.append(delta if delta is not None else 0.5)
        self.intensity_history.append(intensity)

    def _update_plots(self, frame):
        """Update all plots (called by animation)"""
        if not self.is_running or not self.axes:
            return

        # Clear all axes
        for ax in self.axes.values():
            ax.clear()

        self._plot_current_state()
        self._plot_band_history()
        self._plot_band_meters()
        self._plot_awakening()
        self._plot_intensity()
        self._plot_poetry()

    def _plot_current_state(self):
        """Plot current meditation state (large display)"""
        ax = self.axes['state']
        ax.axis('off')

        # Get state color
        color = self.state_colors.get(self.current_state, '#FFFFFF')

        # Draw state rectangle
        rect = patches.Rectangle(
            (0.1, 0.2), 0.8, 0.6,
            facecolor=color,
            alpha=self.current_intensity,
            edgecolor='white',
            linewidth=2
        )
        ax.add_patch(rect)

        # State text
        ax.text(
            0.5, 0.5,
            self.current_state,
            fontsize=48,
            fontweight='bold',
            ha='center',
            va='center',
            color='white'
        )

        # Intensity bar
        ax.text(
            0.5, 0.1,
            f"Intensity: {self.current_intensity:.2f}",
            fontsize=16,
            ha='center',
            color='white',
            alpha=0.7
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    def _plot_band_history(self):
        """Plot band power history over time"""
        ax = self.axes['bands']

        if len(self.alpha_history) == 0:
            return

        x = np.arange(len(self.alpha_history))

        ax.plot(x, list(self.alpha_history), label='Alpha', color='#3498db', linewidth=2)
        ax.plot(x, list(self.beta_history), label='Beta', color='#e74c3c', linewidth=2)
        ax.plot(x, list(self.theta_history), label='Theta', color='#9b59b6', linewidth=2)
        ax.plot(x, list(self.delta_history), label='Delta', color='#1abc9c', linewidth=2)

        ax.set_xlabel('Time (samples)', fontsize=10)
        ax.set_ylabel('Relative Power', fontsize=10)
        ax.set_title('Band Power History', fontsize=12)
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(alpha=0.3)

    def _plot_band_meters(self):
        """Plot current band powers as meters"""
        ax = self.axes['meters']
        ax.axis('off')

        bands = ['Alpha', 'Beta', 'Theta', 'Delta']
        values = [
            self.current_bands['alpha'],
            self.current_bands['beta'],
            self.current_bands['theta'],
            self.current_bands['delta']
        ]
        colors = ['#3498db', '#e74c3c', '#9b59b6', '#1abc9c']

        y_positions = [0.8, 0.6, 0.4, 0.2]

        for i, (band, value, color, y) in enumerate(zip(bands, values, colors, y_positions)):
            # Label
            ax.text(0.05, y, band, fontsize=10, va='center', color='white')

            # Bar background
            ax.add_patch(patches.Rectangle(
                (0.25, y-0.05), 0.7, 0.1,
                facecolor='#2c3e50',
                edgecolor='white',
                linewidth=0.5
            ))

            # Bar fill
            ax.add_patch(patches.Rectangle(
                (0.25, y-0.05), 0.7 * value, 0.1,
                facecolor=color,
                alpha=0.8
            ))

            # Value text
            ax.text(0.97, y, f"{value:.2f}", fontsize=9, va='center', ha='right', color='white')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('Current Band Powers', fontsize=12, pad=10)

    def _plot_awakening(self):
        """Plot character awakening progress"""
        ax = self.axes['awakening']
        ax.axis('off')

        # Title
        ax.text(0.5, 0.9, 'Awakening', fontsize=12, ha='center', fontweight='bold')

        # Progress circle
        circle_bg = patches.Circle(
            (0.5, 0.45), 0.35,
            facecolor='#2c3e50',
            edgecolor='white',
            linewidth=2
        )
        ax.add_patch(circle_bg)

        # Fill based on awakening level
        if self.current_awakening > 0:
            theta = np.linspace(0, 2 * np.pi * self.current_awakening, 100)
            x = 0.5 + 0.35 * np.cos(theta - np.pi/2)
            y = 0.45 + 0.35 * np.sin(theta - np.pi/2)
            ax.fill(x, y, color='#f39c12', alpha=0.8)

        # Percentage text
        pct = self.current_awakening * 100
        ax.text(
            0.5, 0.45,
            f"{pct:.1f}%",
            fontsize=24,
            ha='center',
            va='center',
            color='white',
            fontweight='bold'
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    def _plot_intensity(self):
        """Plot intensity history"""
        ax = self.axes['intensity']

        if len(self.intensity_history) == 0:
            return

        x = np.arange(len(self.intensity_history))
        y = list(self.intensity_history)

        ax.fill_between(x, 0, y, alpha=0.5, color='#95a5a6')
        ax.plot(x, y, color='white', linewidth=2)

        ax.set_xlabel('Time (samples)', fontsize=10)
        ax.set_ylabel('Intensity', fontsize=10)
        ax.set_title('State Intensity History', fontsize=12)
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)

    def _plot_poetry(self):
        """Plot poetic description"""
        ax = self.axes['poetry']
        ax.axis('off')

        # Wrap text
        wrapped_text = self._wrap_text(self.current_poetry, 25)

        ax.text(
            0.5, 0.5,
            wrapped_text,
            fontsize=11,
            ha='center',
            va='center',
            color='#ecf0f1',
            style='italic',
            wrap=True
        )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)


# Example usage
if __name__ == "__main__":
    import time
    import random

    display = NativeDisplay()
    display.start()

    states = ['SETTLING', 'FLOW', 'DEEP', 'LIMINAL', 'PRESENT']
    poetries = [
        "Ripples across a dark pond",
        "Natural movement of breath",
        "Profound stillness emerges",
        "Between sleep and waking",
        "Pure presence without object"
    ]

    try:
        for i in range(200):
            state = random.choice(states)
            intensity = 0.3 + random.random() * 0.7
            alpha = 0.3 + random.random() * 0.6
            beta = 0.2 + random.random() * 0.4
            theta = 0.3 + random.random() * 0.5
            delta = 0.2 + random.random() * 0.4
            awakening = min(1.0, i / 200.0)
            poetry = random.choice(poetries)

            display.update_state(
                state=state,
                intensity=intensity,
                alpha=alpha,
                beta=beta,
                theta=theta,
                delta=delta,
                awakening=awakening,
                poetry=poetry
            )

            plt.pause(0.1)

    except KeyboardInterrupt:
        print("Stopping...")

    display.stop()
    print("Done!")
