"""
Database module for THE LISTENER.

Provides structured storage for meditation sessions,
replacing scattered .h5 files with proper database.
"""

from .schema import (
    Base,
    Session,
    MoodLog,
    JournalEntry,
    Tag,
    LatentRepresentation,
    Checkpoint,
    GeneratedOutput,
    User,
    create_database,
    get_session_maker
)

from .session_manager import SessionManager
from .queries import QueryBuilder

__all__ = [
    'Base',
    'Session',
    'MoodLog',
    'JournalEntry',
    'Tag',
    'LatentRepresentation',
    'Checkpoint',
    'GeneratedOutput',
    'User',
    'create_database',
    'get_session_maker',
    'SessionManager',
    'QueryBuilder'
]
