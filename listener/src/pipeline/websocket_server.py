"""
WebSocket Server for Real-Time Neurofeedback Streaming

Streams meditation state data to visualization clients
(web browsers, TouchDesigner, Processing, etc.)

Based on websockets library with asyncio.
"""

import asyncio
import websockets
import json
from typing import Set, Dict, Optional
from datetime import datetime
import threading


class NeurofeedbackServer:
    """
    WebSocket server for streaming neurofeedback data.

    Broadcasts meditation state to all connected clients.

    Usage:
        server = NeurofeedbackServer(port=8765)
        await server.start()

        # From feedback callback
        feedback.register_callback(server.broadcast_state)

        # Server will broadcast to all connected clients
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize WebSocket server.

        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.is_running = False
        self.latest_state = None

        print(f"🌐 WebSocket server initialized")
        print(f"   Address: ws://{host}:{port}")

    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """Register new client connection."""
        self.clients.add(websocket)
        print(f"✅ Client connected: {websocket.remote_address}")
        print(f"   Total clients: {len(self.clients)}")

        # Send latest state immediately if available
        if self.latest_state:
            await websocket.send(json.dumps(self.latest_state))

    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister client disconnection."""
        self.clients.remove(websocket)
        print(f"❌ Client disconnected: {websocket.remote_address}")
        print(f"   Total clients: {len(self.clients)}")

    async def handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """
        Handle WebSocket connection.

        Args:
            websocket: WebSocket connection
            path: Request path
        """
        await self.register(websocket)
        try:
            # Keep connection alive and handle incoming messages
            async for message in websocket:
                # Echo back or handle commands
                data = json.loads(message)
                command = data.get('command')

                if command == 'ping':
                    await websocket.send(json.dumps({'response': 'pong'}))
                elif command == 'get_state':
                    if self.latest_state:
                        await websocket.send(json.dumps(self.latest_state))
                    else:
                        await websocket.send(json.dumps({'error': 'No state available'}))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def broadcast_state(self, state: Dict):
        """
        Broadcast meditation state to all connected clients.

        Args:
            state: State dict from RealtimeFeedback

        Can be called from any thread (thread-safe).
        """
        self.latest_state = state

        if self.clients:
            # Prepare JSON message
            message = json.dumps(state, default=str)  # default=str for datetime

            # Broadcast to all clients
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Clean up disconnected clients
            self.clients -= disconnected

    def broadcast_state_sync(self, state: Dict):
        """
        Synchronous version of broadcast_state.

        For use with RealtimeFeedback callbacks (non-async).

        Args:
            state: State dict from RealtimeFeedback
        """
        # Update latest state
        self.latest_state = state

        # Create task in event loop if running
        if self.is_running and self.clients:
            # Schedule coroutine in the server's event loop
            asyncio.create_task(self.broadcast_state(state))

    async def start(self):
        """Start WebSocket server."""
        self.server = await websockets.serve(
            self.handler,
            self.host,
            self.port
        )
        self.is_running = True

        print(f"🚀 WebSocket server started")
        print(f"   Listening on ws://{self.host}:{self.port}")
        print(f"   Waiting for connections...")

        # Keep server running
        await asyncio.Future()  # Run forever

    async def stop(self):
        """Stop WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            print("🛑 WebSocket server stopped")

    def run_threaded(self):
        """
        Run server in background thread.

        Useful for running alongside EEG capture.

        Returns:
            Thread object
        """
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start())

        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()

        print("🧵 WebSocket server running in background thread")
        return thread


# Example client HTML for testing
HTML_CLIENT = """
<!DOCTYPE html>
<html>
<head>
    <title>THE LISTENER - Live Feedback</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #000;
            color: #fff;
            font-family: monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        #container {
            text-align: center;
        }
        #circle {
            margin: 50px auto;
            border-radius: 50%;
            transition: all 0.5s ease;
            box-shadow: 0 0 50px rgba(255, 255, 255, 0.3);
        }
        #stats {
            font-size: 18px;
            line-height: 1.8;
        }
        .label {
            color: #888;
        }
        #message {
            font-size: 32px;
            margin: 30px 0;
        }
    </style>
</head>
<body>
    <div id="container">
        <h1>THE LISTENER</h1>
        <div id="message">Connecting...</div>
        <div id="circle"></div>
        <div id="stats">
            <div><span class="label">Depth:</span> <span id="depth">--</span>/100</div>
            <div><span class="label">Quality:</span> <span id="quality">--</span>/100</div>
            <div><span class="label">Alpha:</span> <span id="alpha">--</span></div>
            <div><span class="label">Beta:</span> <span id="beta">--</span></div>
        </div>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:8765');

        ws.onopen = () => {
            console.log('Connected to neurofeedback server');
            document.getElementById('message').textContent = 'Waiting for data...';
        };

        ws.onmessage = (event) => {
            const state = JSON.parse(event.data);
            updateVisualization(state);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            document.getElementById('message').textContent = 'Connection error';
        };

        ws.onclose = () => {
            console.log('Disconnected from server');
            document.getElementById('message').textContent = 'Disconnected';
        };

        function updateVisualization(state) {
            // Update stats
            document.getElementById('depth').textContent = state.depth_smooth.toFixed(1);
            document.getElementById('quality').textContent = state.quality.toFixed(1);
            document.getElementById('alpha').textContent = state.alpha_performance.toFixed(2);
            document.getElementById('beta').textContent = state.beta_performance.toFixed(2);
            document.getElementById('message').textContent = state.state_message;

            // Update circle
            const circle = document.getElementById('circle');
            const size = 50 + (state.depth_smooth / 100) * 400;  // 50-450px
            const hue = 240 - ((state.alpha_smooth + 2) / 4) * 180;  // Blue to yellow
            const brightness = 30 + (state.quality / 100) * 70;  // 30-100%

            circle.style.width = size + 'px';
            circle.style.height = size + 'px';
            circle.style.backgroundColor = `hsl(${hue}, 80%, ${brightness}%)`;
            circle.style.boxShadow = `0 0 ${size/3}px hsl(${hue}, 80%, ${brightness}%)`;
        }
    </script>
</body>
</html>
"""


def save_test_client(filename: str = "test_client.html"):
    """
    Save test client HTML file.

    Args:
        filename: Output filename
    """
    with open(filename, 'w') as f:
        f.write(HTML_CLIENT)

    print(f"✅ Test client saved: {filename}")
    print(f"   Open in browser after starting server")


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WebSocket server for neurofeedback")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--save-client", action="store_true",
                       help="Save test HTML client")

    args = parser.parse_args()

    if args.save_client:
        save_test_client()
        print("\nStart server and open test_client.html in browser")
    else:
        server = NeurofeedbackServer(host=args.host, port=args.port)
        asyncio.run(server.start())
