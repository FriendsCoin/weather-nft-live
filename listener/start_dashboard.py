#!/usr/bin/env python3
"""
NESCIENCE Dashboard Launcher

Simple launcher for the unified NESCIENCE dashboard hub.

Usage:
    python start_dashboard.py [--port 8080]

Then open: http://localhost:8080
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web.nescience_server import main

if __name__ == "__main__":
    main()
