"""
OSC Bridge for Mind Monitor and TouchDesigner Integration

Handles bidirectional OSC communication:
- Receives EEG data from Mind Monitor (phone app)
- Sends processed states to TouchDesigner (visuals)
- Controls LED mask via OSC/Serial

NESCIENCE Architecture:
- Mind Monitor → Python (this module) → TouchDesigner
- Real-time, low latency (<100ms)
- Poetic interpretation, not diagnostic

Usage:
    # Receive from Mind Monitor
    receiver = MindMonitorReceiver(port=5000)
    receiver.start()

    # Send to TouchDesigner
    sender = TouchDesignerSender(host='localhost', port=9000)
    sender.send_state('SETTLING', alpha=0.3, theta=0.5)

Mind Monitor OSC Messages:
    /muse/eeg - Raw EEG (4 channels: TP9, AF7, AF8, TP10)
    /muse/alpha_relative - Alpha band power
    /muse/beta_relative - Beta band power
    /muse/theta_relative - Theta band power
    /muse/delta_relative - Delta band power
    /muse/gamma_relative - Gamma band power
"""

import time
import threading
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass
from collections import deque
import numpy as np

from pythonosc import dispatcher, osc_server, udp_client
from pythonosc.osc_message_builder import OscMessageBuilder


@dataclass
class MuseData:
    """EEG data from Muse S headband via Mind Monitor"""
    timestamp: float

    # Raw EEG (microvolts)
    eeg_tp9: float  # Left ear
    eeg_af7: float  # Left forehead
    eeg_af8: float  # Right forehead
    eeg_tp10: float # Right ear

    # Relative band powers (0-1)
    alpha: Optional[float] = None
    beta: Optional[float] = None
    theta: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None

    # Auxiliary sensors
    ppg: Optional[float] = None  # Heart rate
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None


class MindMonitorReceiver:
    """
    Receives OSC data from Mind Monitor app

    Mind Monitor sends EEG data from Muse S at ~10-12 Hz
    """

    def __init__(
        self,
        port: int = 5000,
        callback: Optional[Callable[[MuseData], None]] = None,
        buffer_size: int = 100
    ):
        """
        Initialize Mind Monitor receiver

        Args:
            port: OSC port to listen on (default: 5000)
            callback: Function to call with new data
            buffer_size: Number of samples to buffer
        """
        self.port = port
        self.callback = callback
        self.buffer_size = buffer_size

        # Data buffers
        self.data_buffer = deque(maxlen=buffer_size)
        self.latest_data = None

        # Server
        self.server = None
        self.server_thread = None
        self.is_running = False

        # Setup dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        self._setup_handlers()

        print(f"🎧 Mind Monitor receiver initialized on port {port}")

    def _setup_handlers(self):
        """Setup OSC message handlers"""

        # Raw EEG
        self.dispatcher.map("/muse/eeg", self._handle_eeg)

        # Relative band powers
        self.dispatcher.map("/muse/elements/alpha_relative", self._handle_alpha)
        self.dispatcher.map("/muse/elements/beta_relative", self._handle_beta)
        self.dispatcher.map("/muse/elements/theta_relative", self._handle_theta)
        self.dispatcher.map("/muse/elements/delta_relative", self._handle_delta)
        self.dispatcher.map("/muse/elements/gamma_relative", self._handle_gamma)

        # Auxiliary
        self.dispatcher.map("/muse/ppg", self._handle_ppg)
        self.dispatcher.map("/muse/gyro", self._handle_gyro)
        self.dispatcher.map("/muse/acc", self._handle_accel)

    def _handle_eeg(self, address, *args):
        """Handle raw EEG data"""
        if len(args) >= 4:
            data = MuseData(
                timestamp=time.time(),
                eeg_tp9=args[0],
                eeg_af7=args[1],
                eeg_af8=args[2],
                eeg_tp10=args[3]
            )

            self.latest_data = data
            self.data_buffer.append(data)

            if self.callback:
                self.callback(data)

    def _handle_alpha(self, address, *args):
        """Handle alpha band power"""
        if self.latest_data and len(args) >= 4:
            self.latest_data.alpha = np.mean(args[:4])

    def _handle_beta(self, address, *args):
        """Handle beta band power"""
        if self.latest_data and len(args) >= 4:
            self.latest_data.beta = np.mean(args[:4])

    def _handle_theta(self, address, *args):
        """Handle theta band power"""
        if self.latest_data and len(args) >= 4:
            self.latest_data.theta = np.mean(args[:4])

    def _handle_delta(self, address, *args):
        """Handle delta band power"""
        if self.latest_data and len(args) >= 4:
            self.latest_data.delta = np.mean(args[:4])

    def _handle_gamma(self, address, *args):
        """Handle gamma band power"""
        if self.latest_data and len(args) >= 4:
            self.latest_data.gamma = np.mean(args[:4])

    def _handle_ppg(self, address, *args):
        """Handle heart rate (PPG) data"""
        if self.latest_data and len(args) >= 1:
            self.latest_data.ppg = args[0]

    def _handle_gyro(self, address, *args):
        """Handle gyroscope data"""
        if self.latest_data and len(args) >= 3:
            self.latest_data.gyro_x = args[0]
            self.latest_data.gyro_y = args[1]
            self.latest_data.gyro_z = args[2]

    def _handle_accel(self, address, *args):
        """Handle accelerometer data"""
        if self.latest_data and len(args) >= 3:
            self.latest_data.accel_x = args[0]
            self.latest_data.accel_y = args[1]
            self.latest_data.accel_z = args[2]

    def start(self):
        """Start receiving OSC messages"""
        if self.is_running:
            print("⚠ Receiver already running")
            return

        print(f"\n{'='*60}")
        print("Mind Monitor OSC Receiver Starting")
        print(f"{'='*60}")
        print(f"Listening on port {self.port}")
        print("Waiting for Mind Monitor data...")
        print("(Start meditation in Mind Monitor app)")
        print(f"{'='*60}\n")

        self.server = osc_server.ThreadingOSCUDPServer(
            ("0.0.0.0", self.port),
            self.dispatcher
        )

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.is_running = True

    def stop(self):
        """Stop receiving"""
        if self.server:
            self.server.shutdown()
            self.is_running = False
            print("✓ Mind Monitor receiver stopped")

    def get_latest_data(self) -> Optional[MuseData]:
        """Get most recent data"""
        return self.latest_data

    def get_buffer(self) -> List[MuseData]:
        """Get buffered data"""
        return list(self.data_buffer)


class TouchDesignerSender:
    """
    Sends processed meditation states to TouchDesigner

    For visual generation and LED control
    """

    def __init__(self, host: str = 'localhost', port: int = 9000):
        """
        Initialize TouchDesigner OSC sender

        Args:
            host: TouchDesigner host (default: localhost)
            port: TouchDesigner OSC port (default: 9000)
        """
        self.host = host
        self.port = port
        self.client = udp_client.SimpleUDPClient(host, port)

        print(f"📡 TouchDesigner sender initialized: {host}:{port}")

    def send_meditation_state(
        self,
        state: str,
        intensity: float,
        alpha: float,
        beta: float,
        theta: float,
        delta: float,
        awakening_level: float = 0.0
    ):
        """
        Send meditation state to TouchDesigner

        Args:
            state: Meditation state (SETTLING, FLOW, DEEP, LIMINAL, PRESENT)
            intensity: State intensity (0-1)
            alpha, beta, theta, delta: Band powers (0-1)
            awakening_level: Companion awakening (0-1)
        """
        # Main state
        self.client.send_message("/nescience/state", state)
        self.client.send_message("/nescience/intensity", intensity)

        # Band powers
        self.client.send_message("/nescience/alpha", alpha)
        self.client.send_message("/nescience/beta", beta)
        self.client.send_message("/nescience/theta", theta)
        self.client.send_message("/nescience/delta", delta)

        # Companion evolution
        self.client.send_message("/nescience/awakening", awakening_level)

    def send_poetic_message(self, text: str):
        """
        Send poetic interpretation to TouchDesigner

        Args:
            text: Poetic description of current state
        """
        self.client.send_message("/nescience/poetry", text)

    def send_character_state(
        self,
        awakening: float,
        curiosity: float,
        stillness: float,
        wildness: float,
        phase: str
    ):
        """
        Send character evolution state

        Args:
            awakening: Awakening level (0-1)
            curiosity: Curiosity trait (0-1)
            stillness: Stillness trait (0-1)
            wildness: Wildness trait (0-1)
            phase: Evolution phase (WITNESSING, ASSOCIATING, CONVERSING, COMPANIONSHIP)
        """
        self.client.send_message("/character/awakening", awakening)
        self.client.send_message("/character/curiosity", curiosity)
        self.client.send_message("/character/stillness", stillness)
        self.client.send_message("/character/wildness", wildness)
        self.client.send_message("/character/phase", phase)

    def send_led_pattern(
        self,
        brightness: float,
        breathing_rate: float,
        color_hue: float = 0.0
    ):
        """
        Send LED mask control parameters

        Args:
            brightness: Overall brightness (0-1)
            breathing_rate: Breathing effect speed (0-1)
            color_hue: Color hue (0-1, optional for subtle color)
        """
        self.client.send_message("/led/brightness", brightness)
        self.client.send_message("/led/breathing", breathing_rate)
        self.client.send_message("/led/hue", color_hue)


class OSCBridge:
    """
    Complete OSC bridge: Mind Monitor → Python → TouchDesigner

    Usage:
        bridge = OSCBridge()
        bridge.start()

        # Bridge automatically forwards processed data
        # to TouchDesigner
    """

    def __init__(
        self,
        mind_monitor_port: int = 5000,
        touchdesigner_host: str = 'localhost',
        touchdesigner_port: int = 9000,
        processing_callback: Optional[Callable] = None
    ):
        """
        Initialize complete OSC bridge

        Args:
            mind_monitor_port: Port for Mind Monitor (default: 5000)
            touchdesigner_host: TouchDesigner host
            touchdesigner_port: TouchDesigner port (default: 9000)
            processing_callback: Custom processing function
        """
        self.receiver = MindMonitorReceiver(
            port=mind_monitor_port,
            callback=self._on_data_received
        )

        self.sender = TouchDesignerSender(
            host=touchdesigner_host,
            port=touchdesigner_port
        )

        self.processing_callback = processing_callback

        print("\n🌉 OSC Bridge initialized")
        print(f"   Mind Monitor :{mind_monitor_port} → TouchDesigner {touchdesigner_host}:{touchdesigner_port}")

    def _on_data_received(self, data: MuseData):
        """Process received data and forward to TouchDesigner"""

        # Call custom processing if provided
        if self.processing_callback:
            result = self.processing_callback(data)

            if result and isinstance(result, dict):
                # Forward processed state to TouchDesigner
                self.sender.send_meditation_state(**result)

    def start(self):
        """Start bridge"""
        self.receiver.start()
        print("✓ OSC Bridge active")

    def stop(self):
        """Stop bridge"""
        self.receiver.stop()
        print("✓ OSC Bridge stopped")

    def get_latest_data(self) -> Optional[MuseData]:
        """Get latest Mind Monitor data"""
        return self.receiver.get_latest_data()
