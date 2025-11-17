# Web Dashboard Guide

Beautiful browser-based interface for THE LISTENER neurofeedback system.

## Quick Start

```bash
# Start the server
python -m src.web.server --port 5000

# Open in browser
http://localhost:5000
```

## Features

### 🏠 Main Dashboard (`/`)
- **Session statistics**: Total sessions and practice time
- **Recent sessions**: Last 5 sessions with quick access
- **Quick actions**: Start real-time session or view history

### ⚡ Real-time Page (`/realtime`)
- **Live neurofeedback**: Real-time state detection and feedback
- **Interactive charts**: Band powers and meditation depth over time
- **Power meters**: Visual bars for alpha, beta, theta, delta
- **Session stats**: Success counts and duration timer
- **Color-coded states**: Instant visual feedback on meditation quality

### 📚 History Page (`/history`)
- **All sessions**: Grid view of recorded sessions
- **Session details**: Click to view full analysis
- **Time series charts**: Band power evolution
- **Meditation metrics**: Depth scores and statistics

## Architecture

### Frontend Stack
- **HTML5/CSS3**: Modern, responsive design
- **Chart.js**: Real-time data visualization
- **Socket.IO Client**: WebSocket communication
- **Vanilla JavaScript**: No heavy frameworks

### Backend Stack
- **Flask**: Lightweight web framework
- **Flask-SocketIO**: WebSocket support
- **Python Threading**: Background EEG processing
- **RESTful API**: Session data endpoints

### Real-time Communication

```
Browser ←──WebSocket──→ Flask-SocketIO ←──Threading──→ Neurofeedback Engine
   │                           │                              │
   │                           │                              │
Charts, UI              Session Management            EEG Processing
```

## API Endpoints

### REST API

```python
GET /                          # Main dashboard page
GET /realtime                  # Real-time feedback page
GET /history                   # Session history page

GET /api/sessions              # List all sessions
GET /api/session/<id>          # Get session details
GET /api/stats                 # Overall statistics
```

### WebSocket Events

```javascript
// Client → Server
socket.emit('start_session', {})
socket.emit('stop_session')

// Server → Client
socket.on('connected', {message: '...'})
socket.on('session_started', {message: '...'})
socket.on('session_stopped', {message: '...'})
socket.on('neurofeedback_update', {
    timestamp: 12.5,
    state: 'alpha+',
    alpha: 0.25,
    beta: 0.15,
    theta: 0.20,
    delta: 0.10,
    depth: 65.3,
    message: '🟢 Deep relaxation - excellent!'
})
```

## Server Configuration

### Command Line Options

```bash
# Default (localhost:5000)
python -m src.web.server

# Custom host and port
python -m src.web.server --host 0.0.0.0 --port 8080

# Debug mode (auto-reload, detailed errors)
python -m src.web.server --debug
```

### Environment Variables

```bash
# Optional: Set via environment
export LISTENER_DATA_DIR="path/to/data"
export LISTENER_PORT=8080
```

### Remote Access

To access from other devices on your network:

```bash
# 1. Start server on all interfaces
python -m src.web.server --host 0.0.0.0 --port 5000

# 2. Find your IP address
# Linux/Mac:
ifconfig | grep "inet "

# Windows:
ipconfig

# 3. Open in browser on other device
http://<your-ip>:5000
```

**Security Note**: Only expose on trusted networks (home WiFi). For internet access, use SSH tunneling or HTTPS.

## Customization

### Styling

Edit `src/web/templates/base.html` for global styles:

```css
/* Change color scheme */
body {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}

.btn {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

### Chart Colors

Edit real-time visualization colors in `templates/realtime.html`:

```javascript
datasets: [
    {
        label: 'Alpha',
        borderColor: '#YOUR_COLOR',  // Change this
        // ...
    }
]
```

### State Indicators

Customize state colors in `templates/realtime.html`:

```css
.state-alpha-success {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

## Advanced Usage

### Custom Data Processing

Add custom metrics to session analysis in `src/web/server.py`:

```python
def _process_session_for_web(self, data: Dict, session_id: str) -> Dict:
    # Add your custom analysis here
    custom_metric = compute_my_metric(data)

    return {
        'metrics': {
            'my_metric': custom_metric,
            # ...
        }
    }
```

### Additional Pages

Create new pages:

1. **Add route** in `src/web/server.py`:
```python
@app.route('/my-page')
def my_page():
    return render_template('my_page.html')
```

2. **Create template** in `src/web/templates/my_page.html`:
```html
{% extends "base.html" %}
{% block content %}
  <!-- Your content -->
{% endblock %}
```

### Real-time Data Export

Export live data to CSV:

```javascript
// In realtime.html
socket.on('neurofeedback_update', (data) => {
    // Collect data
    csvData.push([data.timestamp, data.alpha, data.beta, ...]);

    // Download when done
    downloadCSV(csvData);
});
```

## Performance Optimization

### Client-Side

**Reduce Chart Updates**:
```javascript
// Update every N data points instead of every point
if (dataPoints.length % 5 === 0) {
    chart.update();
}
```

**Limit Data Points**:
```javascript
// Keep only last 100 points
if (timeData.length > 100) {
    timeData.shift();
    alphaData.shift();
    // ...
}
```

### Server-Side

**Reduce Processing Load**:
```python
# In neurofeedback.py
update_interval=1.0  # Less frequent updates (default: 0.5)
```

**Use Caching**:
```python
from src.utils.caching import SessionCache
cache = SessionCache()
# Automatically caches processed sessions
```

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
lsof -i :5000

# Use different port
python -m src.web.server --port 8080
```

### WebSocket Not Connecting

1. **Check browser console** (F12) for errors
2. **Verify Socket.IO version** matches server
3. **Check CORS settings** if accessing remotely
4. **Try different browser** (Chrome recommended)

### Slow Performance

1. **Reduce update rate**:
```bash
python scripts/realtime_feedback.py --update-interval 1.0
```

2. **Limit chart data points** (see Performance section)

3. **Close other applications** using GPU/CPU

### Session Data Not Loading

1. **Check data directory structure**:
```bash
ls data/raw/sessions/
```

2. **Verify session files are valid**:
```bash
python -c "
import pickle
with open('data/raw/sessions/session_001.pkl', 'rb') as f:
    data = pickle.load(f)
    print(list(data.keys()))
"
```

3. **Check server logs** for errors

## Deployment

### Production Deployment

For production use, use a proper WSGI server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    -w 1 \
    -b 0.0.0.0:5000 \
    src.web.server:app
```

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "-m", "src.web.server", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t listener-dashboard .
docker run -p 5000:5000 -v $(pwd)/data:/app/data listener-dashboard
```

### Reverse Proxy (Nginx)

For HTTPS and domain routing:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Security Considerations

### Production Checklist

- [ ] Disable debug mode (`--debug` off)
- [ ] Use HTTPS (via reverse proxy)
- [ ] Add authentication (see below)
- [ ] Limit CORS origins
- [ ] Run as non-root user
- [ ] Keep dependencies updated

### Adding Authentication

Simple token-based auth:

```python
# In src/web/server.py
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != 'YOUR_SECRET_TOKEN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/sessions')
@require_auth
def api_sessions():
    # ...
```

For production, use proper authentication (OAuth, JWT, etc.).

## Browser Compatibility

**Recommended**:
- Chrome/Chromium (best performance)
- Firefox
- Safari
- Edge

**Required Features**:
- WebSocket support
- ES6 JavaScript
- HTML5 Canvas (for charts)

## Future Enhancements

Planned features:

- [ ] User accounts and authentication
- [ ] Session comparison tools
- [ ] Goal setting and tracking
- [ ] Social features (share progress)
- [ ] Mobile app (React Native)
- [ ] Offline mode (PWA)
- [ ] Export to PDF reports
- [ ] Integration with wearables

---

**Need help?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [REALTIME_NEUROFEEDBACK.md](REALTIME_NEUROFEEDBACK.md)
