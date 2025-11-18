"""
FastAPI Backend for THE LISTENER Web Dashboard

Provides REST API for meditation sessions, statistics,
and real-time neurofeedback data.

Features:
- Session browsing with filtering
- Statistics and analytics
- Live EEG visualization
- Gallery view for generated content
- WebSocket integration for real-time data
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import SessionManager, QueryBuilder
from src.database.schema import Session

# Initialize FastAPI
app = FastAPI(
    title="THE LISTENER Dashboard API",
    description="REST API for meditation session data and real-time neurofeedback",
    version="1.0.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
db_manager = SessionManager("sqlite:///data/listener.db")

# WebSocket connection manager for live data
class ConnectionManager:
    """Manage WebSocket connections for live neurofeedback."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except (RuntimeError, ConnectionError) as e:
                # Connection closed or broken, will be cleaned up later
                print(f"Warning: Failed to send to connection: {e}")
            except Exception as e:
                # Unexpected error, log it
                print(f"Error broadcasting message: {e}")

manager = ConnectionManager()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
async def root():
    """API root - health check."""
    return {
        "status": "ok",
        "service": "THE LISTENER Dashboard API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = db_manager.get_statistics()
        return {
            "status": "healthy",
            "database": "connected",
            "total_sessions": stats.get('total_sessions', 0)
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# ============================================================
# SESSION ENDPOINTS
# ============================================================

@app.get("/api/sessions")
async def get_sessions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    min_depth: Optional[float] = Query(None, ge=0, le=100),
    min_quality: Optional[float] = Query(None, ge=0, le=100),
    days: Optional[int] = Query(None, ge=1),
    tag: Optional[str] = None
):
    """
    Get sessions with optional filtering.

    Query Parameters:
    - limit: Maximum number of sessions (1-500)
    - offset: Pagination offset
    - min_depth: Minimum meditation depth (0-100)
    - min_quality: Minimum quality score (0-100)
    - days: Last N days
    - tag: Filter by tag name
    """
    try:
        with db_manager.session_scope() as db_session:
            query = QueryBuilder(db_session)

            # Apply filters
            if min_depth:
                query = query.min_depth(min_depth)
            if min_quality:
                query = query.min_quality(min_quality)
            if days:
                query = query.last_n_days(days)
            if tag:
                query = query.has_tag(tag)

            # Pagination
            query = query.order_by('recorded_at', desc=True)
            query = query.offset(offset).limit(limit)

            sessions = query.execute()

            return {
                "sessions": [s.to_dict() for s in sessions],
                "count": len(sessions),
                "offset": offset,
                "limit": limit
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get single session by ID."""
    try:
        session = db_manager.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get related data
        result = session.to_dict()

        # Add mood logs
        if session.mood_before:
            result['mood_before'] = {
                'stress': session.mood_before.stress,
                'energy': session.mood_before.energy,
                'happiness': session.mood_before.happiness,
                'focus': session.mood_before.focus
            }

        if session.mood_after:
            result['mood_after'] = {
                'stress': session.mood_after.stress,
                'energy': session.mood_after.energy,
                'happiness': session.mood_after.happiness,
                'focus': session.mood_after.focus
            }

        # Add journal entry
        if session.journal_entry:
            result['journal'] = {
                'notes': session.journal_entry.notes,
                'insights': session.journal_entry.insights,
                'rating': session.journal_entry.rating
            }

        # Add tags
        result['tags'] = [tag.name for tag in session.tags]

        # Add generated outputs
        result['outputs'] = [
            {
                'type': output.output_type,
                'path': output.file_path,
                'prompt': output.prompt
            }
            for output in session.generated_outputs
        ]

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# STATISTICS ENDPOINTS
# ============================================================

@app.get("/api/statistics")
async def get_statistics(days: Optional[int] = None):
    """
    Get overall statistics.

    Query Parameters:
    - days: Last N days (optional, default: all time)
    """
    try:
        with db_manager.session_scope() as db_session:
            query = QueryBuilder(db_session)

            if days:
                query = query.last_n_days(days)

            stats = query.statistics()

            # Add time range info
            stats['time_range'] = f'Last {days} days' if days else 'All time'

            return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics/trends")
async def get_trends(days: int = Query(30, ge=7, le=365)):
    """
    Get trend data over time.

    Returns daily averages for depth, quality, and duration.
    """
    try:
        sessions = db_manager.get_sessions(
            start_date=datetime.now() - timedelta(days=days),
            order_by='recorded_at'
        )

        # Group by day
        daily_data = {}
        for session in sessions:
            day = session.recorded_at.date().isoformat()

            if day not in daily_data:
                daily_data[day] = {
                    'date': day,
                    'sessions': [],
                    'depths': [],
                    'qualities': []
                }

            daily_data[day]['sessions'].append(session.session_id)
            if session.mean_depth:
                daily_data[day]['depths'].append(session.mean_depth)
            if session.quality_score:
                daily_data[day]['qualities'].append(session.quality_score)

        # Compute daily averages
        trends = []
        for day, data in sorted(daily_data.items()):
            trends.append({
                'date': day,
                'session_count': len(data['sessions']),
                'avg_depth': sum(data['depths']) / len(data['depths']) if data['depths'] else 0,
                'avg_quality': sum(data['qualities']) / len(data['qualities']) if data['qualities'] else 0
            })

        return {
            'trends': trends,
            'days': days
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics/best")
async def get_best_sessions(
    metric: str = Query('mean_depth', regex='^(mean_depth|quality_score|alpha_performance)$'),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get best sessions by metric.

    Query Parameters:
    - metric: 'mean_depth', 'quality_score', or 'alpha_performance'
    - limit: Number of sessions (1-50)
    """
    try:
        with db_manager.session_scope() as db_session:
            sessions = (QueryBuilder(db_session)
                       .order_by(metric, desc=True)
                       .limit(limit)
                       .execute())

            return {
                "sessions": [s.to_dict() for s in sessions],
                "metric": metric,
                "count": len(sessions)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# TAGS ENDPOINTS
# ============================================================

@app.get("/api/tags")
async def get_tags():
    """Get all tags."""
    try:
        with db_manager.session_scope() as db_session:
            from src.database.schema import Tag
            tags = db_session.query(Tag).all()

            return {
                "tags": [
                    {
                        "name": tag.name,
                        "color": tag.color,
                        "session_count": len(tag.sessions)
                    }
                    for tag in tags
                ]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tags/{tag_name}/sessions")
async def get_sessions_by_tag(tag_name: str):
    """Get sessions with specific tag."""
    try:
        sessions = db_manager.get_sessions_by_tag(tag_name)

        return {
            "tag": tag_name,
            "sessions": [s.to_dict() for s in sessions],
            "count": len(sessions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# LIVE NEUROFEEDBACK WEBSOCKET
# ============================================================

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """
    WebSocket for live neurofeedback data.

    Connects to live_neurofeedback.py WebSocket server
    and relays data to dashboard clients.
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive data from client (heartbeat, commands)
            data = await websocket.receive_json()

            # Echo back for testing
            if data.get('type') == 'ping':
                await websocket.send_json({'type': 'pong'})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ============================================================
# FILE SERVING (for images, videos, etc.)
# ============================================================

@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str):
    """
    Serve generated files (images, videos, audio).

    Path Parameters:
    - file_path: Relative path to file in data/outputs/
    """
    try:
        full_path = Path("data/outputs") / file_path

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(full_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("  🌐 THE LISTENER Dashboard API")
    print("=" * 60)
    print()
    print("Starting server...")
    print("  API docs: http://localhost:8000/docs")
    print("  Health: http://localhost:8000/api/health")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
