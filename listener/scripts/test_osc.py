#!/usr/bin/env python3
"""
Test OSC Connection

Simple script to test OSC sending and receiving.

Usage:
    # Test receiver (Mind Monitor simulation)
    python scripts/test_osc.py --receive --port 5000

    # Test sender (TouchDesigner simulation)
    python scripts/test_osc.py --send --host localhost --port 9000
"""

import sys
import time
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_receiver(port: int):
    """Test OSC receiver (simulate Mind Monitor)"""
    from integrations.osc_bridge import MindMonitorReceiver

    print(f"\n{'='*60}")
    print("Testing OSC Receiver")
    print(f"{'='*60}\n")
    print(f"Listening on port {port}")
    print("Send test messages from Mind Monitor or use:")
    print(f"  python scripts/test_osc.py --send --port {port}\n")

    def on_data(data):
        print(f"✓ Received: Alpha={data.alpha}, Beta={data.beta}")

    receiver = MindMonitorReceiver(port=port, callback=on_data)
    receiver.start()

    print("Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        receiver.stop()


def test_sender(host: str, port: int):
    """Test OSC sender (simulate TouchDesigner)"""
    from integrations.osc_bridge import TouchDesignerSender
    import random

    print(f"\n{'='*60}")
    print("Testing OSC Sender")
    print(f"{'='*60}\n")
    print(f"Sending to {host}:{port}")
    print("Make sure TouchDesigner (or receiver) is listening\n")

    sender = TouchDesignerSender(host=host, port=port)

    states = ['SETTLING', 'FLOW', 'DEEP', 'LIMINAL', 'PRESENT']

    try:
        for i in range(10):
            state = random.choice(states)
            intensity = random.random()
            alpha = random.random()
            beta = random.random()
            theta = random.random()
            delta = random.random()
            awakening = i / 10.0

            sender.send_meditation_state(
                state=state,
                intensity=intensity,
                alpha=alpha,
                beta=beta,
                theta=theta,
                delta=delta,
                awakening_level=awakening
            )

            sender.send_poetic_message(f"Test message {i}: {state}")

            print(f"✓ Sent: {state} (awakening: {awakening*100:.0f}%)")
            time.sleep(1)

        print("\n✓ Test complete!")

    except KeyboardInterrupt:
        print("\nStopped")


def main():
    parser = argparse.ArgumentParser(description="Test OSC Connection")
    parser.add_argument('--receive', action='store_true', help='Test receiver')
    parser.add_argument('--send', action='store_true', help='Test sender')
    parser.add_argument('--host', default='localhost', help='Host (for sender)')
    parser.add_argument('--port', type=int, default=5000, help='Port')

    args = parser.parse_args()

    if args.receive:
        test_receiver(args.port)
    elif args.send:
        test_sender(args.host, args.port)
    else:
        print("Use --receive or --send")
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
