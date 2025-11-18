#!/usr/bin/env python3
"""
OSC Server for TouchDesigner Integration

Streams real-time EEG metrics to TouchDesigner (or any OSC-compatible software)
for live visual feedback during meditation sessions.

OSC Messages sent:
    /meditation/depth       - Float 0-100 (meditation depth)
    /meditation/quality     - Float 0-100 (signal quality)
    /meditation/alpha_plus  - Float (alpha+ performance ratio)
    /meditation/alpha_minus - Float (alpha- performance ratio)
    /meditation/beta_plus   - Float (beta+ performance ratio)
    /meditation/beta_minus  - Float (beta- performance ratio)
    /meditation/theta       - Float (theta power)
    /meditation/delta       - Float (delta power)
    /meditation/state       - String ("deep", "focused", "calm", "distracted")
    /meditation/message     - String (poetic state description)

Usage:
    # In your script
    from src.pipeline.osc_server import OSCServer

    server = OSCServer(host="127.0.0.1", port=8000)
    server.start()

    # Send updates
    server.send_meditation_state({
        'depth': 75.3,
        'quality': 92.1,
        'alpha_plus': 1.2,
        'state': 'deep',
        'message': 'You are descending into stillness'
    })

    server.stop()

TouchDesigner Setup:
    1. Create OSC In CHOP
    2. Set Network Port to 8000
    3. Map incoming addresses to parameters
    4. Example: /meditation/depth → Circle size
               /meditation/alpha_plus → Color hue
               /meditation/state → Visual style
"""

import time
from typing import Dict, Any, Optional
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading


class OSCServer:
    """
    OSC Server for streaming meditation metrics to visual software
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        send_port: int = 8000,
        receive_port: Optional[int] = None,
        verbose: bool = True
    ):
        """
        Initialize OSC server

        Args:
            host: Target host (usually localhost for TouchDesigner)
            send_port: Port to send OSC messages to
            receive_port: Port to receive OSC messages (optional, for bidirectional)
            verbose: Print sent messages
        """
        self.host = host
        self.send_port = send_port
        self.receive_port = receive_port
        self.verbose = verbose

        # Create OSC client for sending
        self.client = udp_client.SimpleUDPClient(host, send_port)

        # Create OSC server for receiving (if bidirectional)
        self.server = None
        self.server_thread = None
        if receive_port:
            self._setup_receiver(receive_port)

        # State tracking
        self.is_running = False
        self.last_update = None

        if self.verbose:
            print(f"🎨 OSC Server initialized")
            print(f"   Sending to: {host}:{send_port}")
            if receive_port:
                print(f"   Receiving on: {receive_port}")

    def _setup_receiver(self, port: int):
        """Setup OSC server for receiving messages"""
        dispatcher = Dispatcher()
        dispatcher.map("/control/*", self._handle_control_message)
        dispatcher.set_default_handler(self._handle_default_message)

        self.server = BlockingOSCUDPServer(("0.0.0.0", port), dispatcher)

    def _handle_control_message(self, address: str, *args):
        """Handle control messages from TouchDesigner"""
        if self.verbose:
            print(f"📨 Received control: {address} {args}")

        # Example: /control/reset, /control/save_screenshot, etc.
        if address == "/control/reset":
            print("🔄 Reset requested")
        elif address == "/control/screenshot":
            print("📸 Screenshot requested")

    def _handle_default_message(self, address: str, *args):
        """Handle any other OSC messages"""
        if self.verbose:
            print(f"📨 Received: {address} {args}")

    def start(self):
        """Start the OSC server (if receiving)"""
        if self.server and not self.is_running:
            self.is_running = True
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True
            )
            self.server_thread.start()
            if self.verbose:
                print("✅ OSC receiver started")

    def stop(self):
        """Stop the OSC server"""
        if self.server and self.is_running:
            self.is_running = False
            self.server.shutdown()
            if self.verbose:
                print("⏹️  OSC receiver stopped")

    # ============================================================
    # SEND METHODS
    # ============================================================

    def send_meditation_state(self, state: Dict[str, Any]):
        """
        Send complete meditation state via OSC

        Args:
            state: Dictionary with meditation metrics
                   Keys: depth, quality, alpha_plus, alpha_minus,
                         beta_plus, beta_minus, theta, delta,
                         state, message
        """
        # Core metrics
        if 'depth' in state:
            self.send_float('/meditation/depth', state['depth'])

        if 'quality' in state:
            self.send_float('/meditation/quality', state['quality'])

        # Performance ratios
        if 'alpha_plus' in state:
            self.send_float('/meditation/alpha_plus', state['alpha_plus'])

        if 'alpha_minus' in state:
            self.send_float('/meditation/alpha_minus', state['alpha_minus'])

        if 'beta_plus' in state:
            self.send_float('/meditation/beta_plus', state['beta_plus'])

        if 'beta_minus' in state:
            self.send_float('/meditation/beta_minus', state['beta_minus'])

        # Raw band powers
        if 'theta' in state:
            self.send_float('/meditation/theta', state['theta'])

        if 'delta' in state:
            self.send_float('/meditation/delta', state['delta'])

        # Categorical state
        if 'state' in state:
            self.send_string('/meditation/state', state['state'])

        # Poetic message
        if 'message' in state:
            self.send_string('/meditation/message', state['message'])

        # Timestamp
        self.send_float('/meditation/timestamp', time.time())

        self.last_update = time.time()

    def send_float(self, address: str, value: float):
        """Send a float value via OSC"""
        self.client.send_message(address, float(value))
        if self.verbose:
            print(f"📤 {address}: {value:.2f}")

    def send_int(self, address: str, value: int):
        """Send an integer value via OSC"""
        self.client.send_message(address, int(value))
        if self.verbose:
            print(f"📤 {address}: {value}")

    def send_string(self, address: str, value: str):
        """Send a string value via OSC"""
        self.client.send_message(address, str(value))
        if self.verbose:
            print(f"📤 {address}: '{value}'")

    def send_bool(self, address: str, value: bool):
        """Send a boolean value via OSC"""
        self.client.send_message(address, 1 if value else 0)
        if self.verbose:
            print(f"📤 {address}: {value}")

    # ============================================================
    # VISUAL CONTROL METHODS
    # ============================================================

    def send_visual_params(
        self,
        size: float = 1.0,
        hue: float = 0.5,
        brightness: float = 1.0,
        saturation: float = 1.0,
        speed: float = 1.0,
        intensity: float = 1.0
    ):
        """
        Send visual parameters to control TouchDesigner visuals

        Args:
            size: Visual size (0-2, 1=normal)
            hue: Color hue (0-1)
            brightness: Brightness (0-1)
            saturation: Color saturation (0-1)
            speed: Animation speed (0-2)
            intensity: Effect intensity (0-1)
        """
        self.send_float('/visual/size', size)
        self.send_float('/visual/hue', hue)
        self.send_float('/visual/brightness', brightness)
        self.send_float('/visual/saturation', saturation)
        self.send_float('/visual/speed', speed)
        self.send_float('/visual/intensity', intensity)

    def send_trigger(self, trigger_name: str):
        """
        Send a trigger/bang to TouchDesigner

        Args:
            trigger_name: Name of trigger (e.g., "bloom", "pulse", "sparkle")
        """
        self.send_int(f'/trigger/{trigger_name}', 1)

    # ============================================================
    # HELPER METHODS
    # ============================================================

    def map_to_visual_params(
        self,
        depth: float,
        quality: float,
        alpha_plus: float,
        state: str
    ) -> Dict[str, float]:
        """
        Map meditation metrics to visual parameters

        Args:
            depth: Meditation depth (0-100)
            quality: Signal quality (0-100)
            alpha_plus: Alpha+ performance ratio
            state: Meditation state string

        Returns:
            Dictionary of visual parameters
        """
        # Size: Based on meditation depth
        size = 0.5 + (depth / 100.0) * 1.5  # Range: 0.5 to 2.0

        # Hue: Based on alpha performance (blue → purple → pink)
        hue = 0.6 + (min(alpha_plus, 2.0) / 2.0) * 0.2  # Range: 0.6-0.8

        # Brightness: Based on quality
        brightness = 0.3 + (quality / 100.0) * 0.7  # Range: 0.3-1.0

        # Saturation: Higher in deep states
        saturation = 0.5 + (depth / 100.0) * 0.5  # Range: 0.5-1.0

        # Speed: Slower in deep states
        speed = 2.0 - (depth / 100.0) * 1.5  # Range: 0.5-2.0

        # Intensity: Based on depth
        intensity = depth / 100.0  # Range: 0-1

        return {
            'size': size,
            'hue': hue,
            'brightness': brightness,
            'saturation': saturation,
            'speed': speed,
            'intensity': intensity
        }

    def send_mapped_visuals(
        self,
        depth: float,
        quality: float,
        alpha_plus: float,
        state: str
    ):
        """
        Automatically map meditation metrics to visual parameters and send

        Args:
            depth: Meditation depth (0-100)
            quality: Signal quality (0-100)
            alpha_plus: Alpha+ performance ratio
            state: Meditation state string
        """
        params = self.map_to_visual_params(depth, quality, alpha_plus, state)
        self.send_visual_params(**params)

        # Send triggers based on state
        if state == "deep" and depth > 80:
            self.send_trigger("bloom")
        elif state == "focused" and alpha_plus > 1.3:
            self.send_trigger("sparkle")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_osc_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    verbose: bool = True
) -> OSCServer:
    """
    Convenience function to create and start OSC server

    Args:
        host: Target host
        port: Target port
        verbose: Print debug messages

    Returns:
        Initialized OSCServer instance
    """
    server = OSCServer(host=host, send_port=port, verbose=verbose)
    return server


if __name__ == "__main__":
    """
    Test the OSC server with simulated data
    """
    import random

    print("=" * 60)
    print("  🎨 OSC Server Test")
    print("=" * 60)
    print()
    print("Make sure TouchDesigner is running with OSC In CHOP")
    print("Set Network Port to 8000")
    print()
    print("Press Ctrl+C to stop")
    print()

    # Create server
    server = create_osc_server(host="127.0.0.1", port=8000, verbose=True)

    try:
        # Simulate meditation session
        states = ["distracted", "calm", "focused", "deep"]
        messages = {
            "distracted": "Your mind wanders through familiar paths",
            "calm": "Stillness begins to settle",
            "focused": "You are finding your center",
            "deep": "You are descending into infinite space"
        }

        depth = 20.0
        quality = 85.0
        alpha_plus = 0.8

        print("🎬 Starting simulation...\n")

        for i in range(100):
            # Simulate gradual deepening
            depth = min(95, depth + random.uniform(-5, 7))
            quality = 85 + random.uniform(-10, 10)
            alpha_plus = max(0.5, min(2.0, alpha_plus + random.uniform(-0.1, 0.2)))

            # Determine state
            if depth > 75:
                state = "deep"
            elif depth > 50:
                state = "focused"
            elif depth > 30:
                state = "calm"
            else:
                state = "distracted"

            # Send meditation state
            server.send_meditation_state({
                'depth': depth,
                'quality': quality,
                'alpha_plus': alpha_plus,
                'alpha_minus': 1.0 / alpha_plus if alpha_plus > 0 else 1.0,
                'beta_plus': random.uniform(0.8, 1.2),
                'beta_minus': random.uniform(0.8, 1.2),
                'theta': random.uniform(5, 15),
                'delta': random.uniform(2, 8),
                'state': state,
                'message': messages[state]
            })

            # Send visual parameters
            server.send_mapped_visuals(depth, quality, alpha_plus, state)

            print()
            time.sleep(1)  # 1 Hz update rate

    except KeyboardInterrupt:
        print("\n\n⏹️  Simulation stopped\n")

    server.stop()
