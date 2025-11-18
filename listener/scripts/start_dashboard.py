#!/usr/bin/env python3
"""
Start THE LISTENER Web Dashboard

Launches FastAPI backend and opens browser to dashboard.

Usage:
    python scripts/start_dashboard.py
    python scripts/start_dashboard.py --port 8000
    python scripts/start_dashboard.py --no-browser  # Don't auto-open browser
"""

import sys
from pathlib import Path
import argparse
import webbrowser
import time
from threading import Timer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def open_browser(port: int, delay: float = 1.5):
    """Open browser after delay."""
    def _open():
        url = f"http://localhost:{port}/web/"
        print(f"\n🌐 Opening dashboard: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Could not open browser: {e}")
            print(f"Please open manually: {url}")

    timer = Timer(delay, _open)
    timer.daemon = True
    timer.start()


def main():
    parser = argparse.ArgumentParser(
        description="Start THE LISTENER Web Dashboard"
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Port for API server (default: 8000)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--no-browser", action="store_true",
        help="Don't automatically open browser"
    )
    parser.add_argument(
        "--database", default="sqlite:///data/listener.db",
        help="Database URL (default: sqlite:///data/listener.db)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  🧘 THE LISTENER - Web Dashboard")
    print("=" * 60)
    print()
    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"Database: {args.database}")
    print()
    print("Available at:")
    print(f"  Dashboard: http://localhost:{args.port}/web/")
    print(f"  API Docs:  http://localhost:{args.port}/docs")
    print(f"  Health:    http://localhost:{args.port}/api/health")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Open browser automatically
    if not args.no_browser:
        open_browser(args.port)

    # Start FastAPI server
    import uvicorn
    from src.api.server import app

    # Update database connection in app
    from src.api import server
    server.db_manager.database_url = args.database

    # Mount static files for web dashboard
    from fastapi.staticfiles import StaticFiles
    app.mount("/web", StaticFiles(directory="web", html=True), name="web")

    # Run server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
