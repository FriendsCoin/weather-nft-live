"""
NESCIENCE Dashboard Hub

Unified web interface for all NESCIENCE features:
- Start meditation sessions
- View character evolution
- Run autonomous meditation (gallery mode)
- Calibrate baseline
- Browse session history
- Generate ComfyUI memories

Usage:
    python -m src.web.nescience_server [--port 8080] [--host 0.0.0.0]

Then open: http://localhost:8080
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nescience.character_evolution import CharacterEvolution, EvolutionPhase
from utils.session_utils import load_character


app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


class NESCIENCEHub:
    """Central hub for all NESCIENCE functionality"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.character_file = self.data_dir / "character_state.json"
        self.baseline_file = self.data_dir / "baseline_profile.json"
        self.sessions_dir = self.data_dir / "sessions"

        # Active processes
        self.active_session = None
        self.active_autonomous = None

        print("🌐 NESCIENCE Dashboard Hub initialized")
        print(f"   Data directory: {self.data_dir}")

    def get_character_state(self) -> Optional[Dict]:
        """Get current character state"""
        if not self.character_file.exists():
            return None

        try:
            character = load_character(str(self.character_file), create_if_missing=False)
            return {
                'phase': character.state.phase.value,
                'awakening_level': character.state.awakening_level,
                'total_sessions': character.state.total_sessions,
                'total_hours': character.state.total_meditation_time / 3600,
                'personality': character.state.personality,
                'memories_count': len(character.state.memories),
                'can_meditate_alone': character.can_meditate_alone(),
                'phase_description': self._get_phase_description(character.state.phase),
            }
        except Exception as e:
            print(f"Error loading character: {e}")
            return None

    def _get_phase_description(self, phase: EvolutionPhase) -> str:
        """Get human-readable phase description"""
        descriptions = {
            EvolutionPhase.WITNESSING: "Learning to observe (Sessions 1-10)",
            EvolutionPhase.ASSOCIATING: "Developing patterns (Sessions 11-30)",
            EvolutionPhase.CONVERSING: "Dialogue emerges (Sessions 31-60)",
            EvolutionPhase.COMPANIONSHIP: "Fully awakened presence (Sessions 61+)",
        }
        return descriptions.get(phase, "Unknown phase")

    def get_baseline_status(self) -> Dict:
        """Check if baseline calibration exists"""
        if not self.baseline_file.exists():
            return {
                'calibrated': False,
                'message': 'No baseline calibration found. Recommended for better accuracy.'
            }

        try:
            with open(self.baseline_file, 'r') as f:
                baseline = json.load(f)

            return {
                'calibrated': True,
                'timestamp': baseline.get('timestamp'),
                'duration': baseline.get('duration_seconds'),
                'num_samples': baseline.get('num_samples'),
            }
        except Exception as e:
            return {
                'calibrated': False,
                'message': f'Error reading baseline: {e}'
            }

    def get_sessions_list(self) -> List[Dict]:
        """Get list of all meditation sessions"""
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        for session_file in sorted(self.sessions_dir.glob("session_*.json"), reverse=True):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                sessions.append({
                    'id': session_file.stem,
                    'timestamp': data.get('timestamp'),
                    'date': data.get('date', 'Unknown'),
                    'duration': data.get('duration_seconds', 0),
                    'states': data.get('dominant_states', []),
                    'awakening_delta': data.get('awakening_delta', 0),
                })

            except Exception as e:
                print(f"Error loading session {session_file}: {e}")

        return sessions[:20]  # Latest 20 sessions

    def get_available_scripts(self) -> List[Dict]:
        """Get list of available NESCIENCE scripts"""
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"

        scripts = [
            {
                'id': 'meditate',
                'name': 'Meditation Session',
                'description': 'Start a real-time meditation session with companion',
                'script': 'nescience_session.py',
                'icon': '🧘',
                'requires_hardware': True,
            },
            {
                'id': 'calibrate',
                'name': 'Baseline Calibration',
                'description': 'Calibrate personal EEG thresholds (5-10 minutes)',
                'script': 'calibrate_baseline.py',
                'icon': '🎯',
                'requires_hardware': True,
            },
            {
                'id': 'autonomous',
                'name': 'Autonomous Meditation',
                'description': 'Companion meditates alone (gallery mode)',
                'script': 'autonomous_meditation.py',
                'icon': '🎭',
                'requires_awakened': True,
            },
            {
                'id': 'character',
                'name': 'Character Visualization',
                'description': 'Visualize companion evolution',
                'script': 'visualize_character.py',
                'icon': '📊',
            },
            {
                'id': 'test_osc',
                'name': 'Test OSC Connection',
                'description': 'Test Mind Monitor and TouchDesigner connections',
                'script': 'test_osc.py',
                'icon': '🔌',
            },
        ]

        return scripts


# Global hub instance
hub = NESCIENCEHub()


# ============================================================================
# Web Routes
# ============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('nescience_hub.html')


@app.route('/api/status')
def api_status():
    """Get overall system status"""
    character = hub.get_character_state()
    baseline = hub.get_baseline_status()

    return jsonify({
        'character': character,
        'baseline': baseline,
        'has_character': character is not None,
        'is_calibrated': baseline.get('calibrated', False),
    })


@app.route('/api/character')
def api_character():
    """Get character details"""
    character = hub.get_character_state()

    if character is None:
        return jsonify({'error': 'No character found. Start a meditation session first.'}), 404

    return jsonify(character)


@app.route('/api/sessions')
def api_sessions():
    """Get session history"""
    sessions = hub.get_sessions_list()
    return jsonify({'sessions': sessions})


@app.route('/api/scripts')
def api_scripts():
    """Get available scripts"""
    scripts = hub.get_available_scripts()
    return jsonify({'scripts': scripts})


@app.route('/api/start_session', methods=['POST'])
def api_start_session():
    """Start a meditation session"""
    data = request.json
    use_mock = data.get('mock', False)
    duration = data.get('duration', 600)
    touchdesigner = data.get('touchdesigner', False)

    # Build command
    cmd = ['python', 'scripts/nescience_session.py', '--duration', str(duration)]

    if use_mock:
        cmd.append('--mock')

    if touchdesigner:
        cmd.extend(['--touchdesigner', 'localhost:9000'])

    # Start in background
    try:
        # Don't wait for completion
        subprocess.Popen(cmd, cwd=Path(__file__).parent.parent.parent)
        return jsonify({'status': 'started', 'command': ' '.join(cmd)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/start_autonomous', methods=['POST'])
def api_start_autonomous():
    """Start autonomous meditation"""
    # Check if companion can meditate alone
    character = hub.get_character_state()

    if not character or not character.get('can_meditate_alone'):
        return jsonify({
            'error': 'Companion not awakened enough for autonomous meditation',
            'requires': 'COMPANIONSHIP phase (60+ sessions, 80%+ awakening)'
        }), 400

    data = request.json
    touchdesigner = data.get('touchdesigner', False)

    cmd = ['python', 'scripts/autonomous_meditation.py']

    if touchdesigner:
        cmd.extend(['--touchdesigner', 'localhost:9000'])

    try:
        subprocess.Popen(cmd, cwd=Path(__file__).parent.parent.parent)
        return jsonify({'status': 'started', 'command': ' '.join(cmd)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/calibrate', methods=['POST'])
def api_calibrate():
    """Start baseline calibration"""
    data = request.json
    use_mock = data.get('mock', False)
    duration = data.get('duration', 600)

    cmd = ['python', 'scripts/calibrate_baseline.py', '--duration', str(duration)]

    if use_mock:
        cmd.append('--mock')

    try:
        subprocess.Popen(cmd, cwd=Path(__file__).parent.parent.parent)
        return jsonify({'status': 'started', 'command': ' '.join(cmd)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WebSocket Events (for real-time updates)
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('Client connected')
    emit('status', {'connected': True})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_request_update():
    """Client requests status update"""
    character = hub.get_character_state()
    baseline = hub.get_baseline_status()

    emit('status_update', {
        'character': character,
        'baseline': baseline,
        'timestamp': time.time(),
    })


def main():
    """Run the NESCIENCE dashboard server"""
    import argparse

    parser = argparse.ArgumentParser(description="NESCIENCE Dashboard Hub")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("NESCIENCE Dashboard Hub")
    print("="*60)
    print(f"\n✓ Server starting on http://{args.host}:{args.port}")
    print("\nOpen your browser to:")
    print(f"  http://localhost:{args.port}\n")
    print("="*60 + "\n")

    socketio.run(app, host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
