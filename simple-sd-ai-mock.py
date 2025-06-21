#!/usr/bin/env python3
"""
Simple SD AI Mock Server for Testing
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class SDMockHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "model_status": "ready",
                "sd_environment": False,
                "pytorch_available": False,
                "algorithms_count": 5,
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/model/info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "ready",
                "sd_environment": False,
                "pytorch_available": False,
                "algorithms": {
                    "ThermalDrift-v2": {"accuracy": 94.2, "model_type": "LSTM", "status": "ready"},
                    "StormChaser-v4": {"accuracy": 97.8, "model_type": "CNN-LSTM", "status": "ready"},
                    "EcoBalance-v1": {"accuracy": 91.5, "model_type": "Transformer", "status": "ready"},
                    "AuroraPredictor-v3": {"accuracy": 89.3, "model_type": "RNN", "status": "ready"},
                    "AquaDetect-v2": {"accuracy": 96.1, "model_type": "GRU", "status": "ready"}
                },
                "algorithms_count": 5,
                "python_version": "3.8.10 (default, Nov 14 2022, 12:59:47)",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                weather_data = json.loads(post_data.decode('utf-8'))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Mock prediction
                response = {
                    "success": True,
                    "algorithm": "StormChaser-v4",
                    "confidence": 0.87,
                    "event_type": "thunderstorm",
                    "rarity": "rare",
                    "all_predictions": {
                        "ThermalDrift-v2": {"confidence": 0.72, "event_type": "heat_wave", "rarity": "rare"},
                        "StormChaser-v4": {"confidence": 0.87, "event_type": "thunderstorm", "rarity": "rare"},
                        "EcoBalance-v1": {"confidence": 0.65, "event_type": "climate_shift", "rarity": "uncommon"}
                    },
                    "model_type": "fallback"
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "success": False,
                    "error": str(e),
                    "model_type": "error"
                }
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), SDMockHandler) as httpd:
        print("🌦️ Simple SD AI Mock Server")
        print("=" * 30)
        print(f"✅ Server running on http://localhost:{PORT}")
        print("📊 Endpoints:")
        print("   • GET  /health      - Health check")
        print("   • GET  /model/info  - Model information")
        print("   • POST /predict     - Weather prediction")
        print("")
        print("🧪 Mock mode for testing admin panel integration")
        httpd.serve_forever()