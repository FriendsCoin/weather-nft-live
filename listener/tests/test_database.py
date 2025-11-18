"""
Tests for Database Operations
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionManager, QueryBuilder, Session


class TestDatabaseOperations:
    """Test suite for database operations"""

    def test_session_manager_initialization(self, temp_database):
        """Test SessionManager initialization"""
        manager = SessionManager(temp_database)
        assert manager is not None

    def test_create_session(self, temp_database, sample_session_dict):
        """Test creating a session in database"""
        manager = SessionManager(temp_database)

        with manager.session_scope() as db_session:
            session = Session(
                session_id=sample_session_dict['session_id'],
                recorded_at=datetime.fromisoformat(sample_session_dict['recorded_at']),
                duration_seconds=sample_session_dict['duration_seconds'],
                depth_score=sample_session_dict['depth_score'],
                quality_score=sample_session_dict['quality_score']
            )
            db_session.add(session)
            db_session.commit()

            # Verify it was created
            retrieved = db_session.query(Session).filter_by(
                session_id=sample_session_dict['session_id']
            ).first()

            assert retrieved is not None
            assert retrieved.session_id == sample_session_dict['session_id']
            assert retrieved.depth_score == sample_session_dict['depth_score']

    def test_query_all_sessions(self, temp_database):
        """Test querying all sessions"""
        manager = SessionManager(temp_database)

        # Create multiple sessions
        with manager.session_scope() as db_session:
            for i in range(5):
                session = Session(
                    session_id=f'test_session_{i:03d}',
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=50.0 + i * 10,
                    quality_score=80.0
                )
                db_session.add(session)
            db_session.commit()

        # Query all
        with manager.session_scope() as db_session:
            query = QueryBuilder(db_session)
            sessions = query.execute()

            assert len(sessions) == 5

    def test_query_filter_by_depth(self, temp_database):
        """Test filtering sessions by depth"""
        manager = SessionManager(temp_database)

        # Create sessions with varying depths
        with manager.session_scope() as db_session:
            for i in range(10):
                session = Session(
                    session_id=f'test_session_{i:03d}',
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=i * 10.0,  # 0, 10, 20, ..., 90
                    quality_score=80.0
                )
                db_session.add(session)
            db_session.commit()

        # Query sessions with depth > 50
        with manager.session_scope() as db_session:
            query = QueryBuilder(db_session).min_depth(50)
            sessions = query.execute()

            assert len(sessions) == 5  # 60, 70, 80, 90, 100
            assert all(s.depth_score >= 50 for s in sessions)

    def test_query_filter_by_quality(self, temp_database):
        """Test filtering sessions by quality"""
        manager = SessionManager(temp_database)

        # Create sessions with varying quality
        with manager.session_scope() as db_session:
            for i in range(10):
                session = Session(
                    session_id=f'test_session_{i:03d}',
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=75.0,
                    quality_score=i * 10.0  # 0, 10, 20, ..., 90
                )
                db_session.add(session)
            db_session.commit()

        # Query sessions with quality > 70
        with manager.session_scope() as db_session:
            query = QueryBuilder(db_session).min_quality(70)
            sessions = query.execute()

            assert len(sessions) == 3  # 80, 90
            assert all(s.quality_score >= 70 for s in sessions)

    def test_query_order_by(self, temp_database):
        """Test ordering query results"""
        manager = SessionManager(temp_database)

        # Create sessions
        with manager.session_scope() as db_session:
            for i in range(5):
                session = Session(
                    session_id=f'test_session_{i:03d}',
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=50.0 + i * 10,
                    quality_score=80.0
                )
                db_session.add(session)
            db_session.commit()

        # Query ordered by depth descending
        with manager.session_scope() as db_session:
            query = QueryBuilder(db_session).order_by('depth_score', desc=True)
            sessions = query.execute()

            depths = [s.depth_score for s in sessions]
            assert depths == sorted(depths, reverse=True)

    def test_query_limit(self, temp_database):
        """Test limiting query results"""
        manager = SessionManager(temp_database)

        # Create 10 sessions
        with manager.session_scope() as db_session:
            for i in range(10):
                session = Session(
                    session_id=f'test_session_{i:03d}',
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=75.0,
                    quality_score=80.0
                )
                db_session.add(session)
            db_session.commit()

        # Query with limit
        with manager.session_scope() as db_session:
            query = QueryBuilder(db_session).limit(5)
            sessions = query.execute()

            assert len(sessions) == 5

    def test_session_to_dict(self, temp_database, sample_session_dict):
        """Test Session.to_dict() method"""
        manager = SessionManager(temp_database)

        with manager.session_scope() as db_session:
            session = Session(
                session_id=sample_session_dict['session_id'],
                recorded_at=datetime.fromisoformat(sample_session_dict['recorded_at']),
                duration_seconds=sample_session_dict['duration_seconds'],
                depth_score=sample_session_dict['depth_score'],
                quality_score=sample_session_dict['quality_score']
            )
            db_session.add(session)
            db_session.commit()

            # Convert to dict
            session_dict = session.to_dict()

            assert isinstance(session_dict, dict)
            assert session_dict['session_id'] == sample_session_dict['session_id']
            assert session_dict['depth_score'] == sample_session_dict['depth_score']
            assert session_dict['quality_score'] == sample_session_dict['quality_score']

    def test_session_scope_rollback_on_error(self, temp_database):
        """Test that session_scope rolls back on error"""
        manager = SessionManager(temp_database)

        try:
            with manager.session_scope() as db_session:
                session = Session(
                    session_id='test_session',
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=75.0,
                    quality_score=80.0
                )
                db_session.add(session)
                db_session.commit()

                # Cause an error
                raise ValueError("Test error")
        except ValueError:
            pass

        # Session should still exist (commit happened before error)
        with manager.session_scope() as db_session:
            count = db_session.query(Session).count()
            assert count == 1

    def test_duplicate_session_id(self, temp_database):
        """Test handling of duplicate session IDs"""
        manager = SessionManager(temp_database)

        with manager.session_scope() as db_session:
            # Create first session
            session1 = Session(
                session_id='duplicate_test',
                recorded_at=datetime.now(),
                duration_seconds=600,
                depth_score=75.0,
                quality_score=80.0
            )
            db_session.add(session1)
            db_session.commit()

        # Try to create duplicate
        with pytest.raises(Exception):  # Should raise IntegrityError
            with manager.session_scope() as db_session:
                session2 = Session(
                    session_id='duplicate_test',  # Same ID
                    recorded_at=datetime.now(),
                    duration_seconds=600,
                    depth_score=85.0,
                    quality_score=90.0
                )
                db_session.add(session2)
                db_session.commit()
