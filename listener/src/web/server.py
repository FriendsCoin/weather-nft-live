"""
Web Server for THE LISTENER Dashboard

Provides real-time visualization of neurofeedback sessions via WebSocket
and historical session analytics.

Features:
- Real-time EEG data streaming via WebSocket
- Live neurofeedback state display
- Historical session browser
- Interactive charts and visualizations
- Session comparison and analytics

Usage:
    python -m src.web.server [--port 5000] [--debug]
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
from pathlib import Path
from typing import Dict, List, Optional
import threading
import time
from datetime import datetime
import numpy as np


app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


class DashboardServer:
    """Web dashboard server for real-time neurofeedback"""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize dashboard server

        Args:
            data_dir: Root data directory
        """
        self.data_dir = Path(data_dir)
        self.sessions_dir = self.data_dir / "raw" / "sessions"
        self.outputs_dir = self.data_dir / "outputs"

        # Real-time session tracking
        self.active_session = None
        self.is_streaming = False
        self.stream_thread = None

        print("🌐 Dashboard server initialized")
        print(f"   Data directory: {self.data_dir}")

    def get_session_list(self) -> List[Dict]:
        """
        Get list of all recorded sessions

        Returns:
            List of session metadata dictionaries
        """
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        for session_file in sorted(self.sessions_dir.glob("*.pkl")):
            try:
                import pickle
                with open(session_file, 'rb') as f:
                    data = pickle.load(f)

                # Extract metadata
                metadata = {
                    'id': session_file.stem,
                    'filename': session_file.name,
                    'path': str(session_file),
                    'timestamp': session_file.stat().st_mtime,
                    'date': datetime.fromtimestamp(session_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'duration': len(data.get('raw_eeg', [])) / data.get('sampling_rate', 256),
                    'channels': len(data.get('channels', [])),
                }

                sessions.append(metadata)

            except Exception as e:
                print(f"Error loading {session_file}: {e}")

        return sessions

    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """
        Load session data for visualization

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary or None
        """
        session_file = self.sessions_dir / f"{session_id}.pkl"

        if not session_file.exists():
            return None

        try:
            import pickle
            with open(session_file, 'rb') as f:
                data = pickle.load(f)

            # Process for web display
            return self._process_session_for_web(data, session_id)

        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def _process_session_for_web(self, data: Dict, session_id: str) -> Dict:
        """Process session data for web visualization"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from utils.meditation_analysis import MeditationAnalyzer
        from pipeline.feature_extraction import FeatureExtractor

        # Extract features if not already done
        if 'features' not in data:
            # Extract features
            extractor = FeatureExtractor(sampling_rate=data['sampling_rate'])
            features_df = extractor.extract_features(data['raw_eeg'])
            data['features'] = features_df

        # Analyze meditation quality
        analyzer = MeditationAnalyzer()

        # Get time series of band powers
        features_df = data['features']

        # Compute metrics
        metrics = analyzer.analyze_session(features_df)

        # Prepare time series data
        time_series = {
            'time': list(range(len(features_df))),
            'alpha': features_df['alpha_power'].tolist() if 'alpha_power' in features_df.columns else [],
            'beta': features_df['beta_power'].tolist() if 'beta_power' in features_df.columns else [],
            'theta': features_df['theta_power'].tolist() if 'theta_power' in features_df.columns else [],
            'delta': features_df['delta_power'].tolist() if 'delta_power' in features_df.columns else [],
        }

        return {
            'id': session_id,
            'metadata': {
                'duration': len(data['raw_eeg']) / data['sampling_rate'],
                'channels': data['channels'],
                'sampling_rate': data['sampling_rate'],
            },
            'metrics': metrics,
            'time_series': time_series,
        }

    def start_realtime_stream(self):
        """Start real-time data streaming to connected clients"""
        self.is_streaming = True

        def stream_worker():
            """Worker thread for streaming data"""
            from realtime.neurofeedback import RealtimeNeurofeedback, FeedbackEvent

            def broadcast_event(event: FeedbackEvent):
                """Broadcast event to all connected clients"""
                socketio.emit('neurofeedback_update', {
                    'timestamp': event.timestamp,
                    'state': event.state.value,
                    'alpha': event.alpha_power,
                    'beta': event.beta_power,
                    'theta': event.theta_power,
                    'delta': event.delta_power,
                    'depth': event.meditation_depth,
                    'message': event.message,
                }, namespace='/realtime')

            # Create neurofeedback system
            feedback = RealtimeNeurofeedback(
                device='mock',
                feedback_callback=broadcast_event
            )

            # Start session (infinite duration)
            feedback.start_session(duration=None)

        self.stream_thread = threading.Thread(target=stream_worker)
        self.stream_thread.daemon = True
        self.stream_thread.start()

    def stop_realtime_stream(self):
        """Stop real-time streaming"""
        self.is_streaming = False


# Global dashboard instance
dashboard = DashboardServer()


# ============================================================
# Web Routes
# ============================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/realtime')
def realtime():
    """Real-time neurofeedback page"""
    return render_template('realtime.html')


@app.route('/history')
def history():
    """Historical sessions page"""
    return render_template('history.html')


@app.route('/api/sessions')
def api_sessions():
    """API: Get list of all sessions"""
    sessions = dashboard.get_session_list()
    return jsonify(sessions)


@app.route('/api/session/<session_id>')
def api_session(session_id):
    """API: Get specific session data"""
    session_data = dashboard.get_session_data(session_id)

    if session_data is None:
        return jsonify({'error': 'Session not found'}), 404

    return jsonify(session_data)


@app.route('/api/stats')
def api_stats():
    """API: Get overall statistics"""
    sessions = dashboard.get_session_list()

    stats = {
        'total_sessions': len(sessions),
        'total_duration': sum(s.get('duration', 0) for s in sessions),
        'latest_session': sessions[-1] if sessions else None,
    }

    return jsonify(stats)


# ============================================================
# WebSocket Events
# ============================================================

@socketio.on('connect', namespace='/realtime')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to real-time neurofeedback'})


@socketio.on('disconnect', namespace='/realtime')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('start_session', namespace='/realtime')
def handle_start_session(data):
    """Start real-time neurofeedback session"""
    print("Starting real-time session...")

    # Start streaming
    if not dashboard.is_streaming:
        dashboard.start_realtime_stream()

    emit('session_started', {'message': 'Session started'})


@socketio.on('stop_session', namespace='/realtime')
def handle_stop_session():
    """Stop real-time neurofeedback session"""
    print("Stopping real-time session...")

    dashboard.stop_realtime_stream()

    emit('session_stopped', {'message': 'Session stopped'})


# ============================================================
# Server Control
# ============================================================

def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the dashboard server

    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    print("\n" + "=" * 70)
    print("THE LISTENER - Web Dashboard")
    print("=" * 70)
    print(f"\nServer starting on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nOpen in your browser:")
    print(f"  - Dashboard: http://localhost:{port}/")
    print(f"  - Real-time: http://localhost:{port}/realtime")
    print(f"  - History:   http://localhost:{port}/history")
    print("\nPress Ctrl+C to stop")
    print("=" * 70 + "\n")

    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="THE LISTENER Web Dashboard")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    run_server(host=args.host, port=args.port, debug=args.debug)
