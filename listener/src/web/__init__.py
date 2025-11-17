"""Web dashboard module"""

from .server import app, socketio, run_server

__all__ = ['app', 'socketio', 'run_server']
