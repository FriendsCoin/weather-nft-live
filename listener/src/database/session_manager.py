"""
Session Manager for THE LISTENER Database

Handles database sessions and provides convenient
methods for creating, reading, updating, deleting records.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import json
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession

from .schema import (
    Base, Session, MoodLog, JournalEntry, Tag,
    LatentRepresentation, Checkpoint, GeneratedOutput, User
)


class SessionManager:
    """
    Manages database connections and operations.

    Provides high-level API for working with THE LISTENER database.

    Usage:
        manager = SessionManager("sqlite:///data/listener.db")

        # Add session
        session = manager.add_meditation_session(
            session_id="session_20241118_001",
            recorded_at=datetime.now(),
            duration_seconds=1800,
            mean_depth=65.3,
            quality_score=72.1
        )

        # Query sessions
        sessions = manager.get_sessions(min_depth=50, limit=10)

        # Add mood log
        manager.add_mood_log(
            session_id=session.id,
            log_type="before",
            stress=4, energy=2, happiness=3, focus=2
        )
    """

    def __init__(self, database_url: str = "sqlite:///data/listener.db", echo: bool = False):
        """
        Initialize session manager.

        Args:
            database_url: SQLAlchemy database URL
            echo: Print SQL statements (for debugging)
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=echo)
        self.SessionMaker = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

        print(f"📊 Database connected: {database_url}")

    @contextmanager
    def session_scope(self):
        """
        Provide transactional scope for database operations.

        Usage:
            with manager.session_scope() as session:
                session.add(obj)
        """
        session = self.SessionMaker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ===== Meditation Session Methods =====

    def add_meditation_session(
        self,
        session_id: str,
        recorded_at: datetime,
        duration_seconds: Optional[float] = None,
        mean_depth: Optional[float] = None,
        quality_score: Optional[float] = None,
        **kwargs
    ) -> Session:
        """
        Add new meditation session.

        Args:
            session_id: Unique session identifier
            recorded_at: Session timestamp
            duration_seconds: Session duration
            mean_depth: Average meditation depth
            quality_score: Session quality score
            **kwargs: Additional session attributes

        Returns:
            Session object
        """
        with self.session_scope() as db_session:
            session = Session(
                session_id=session_id,
                recorded_at=recorded_at,
                duration_seconds=duration_seconds,
                mean_depth=mean_depth,
                quality_score=quality_score,
                **kwargs
            )
            db_session.add(session)
            db_session.flush()  # Get ID
            db_session.refresh(session)
            return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object or None
        """
        with self.session_scope() as db_session:
            return db_session.query(Session).filter_by(session_id=session_id).first()

    def get_session_by_pk(self, pk: int) -> Optional[Session]:
        """
        Get session by primary key.

        Args:
            pk: Primary key ID

        Returns:
            Session object or None
        """
        with self.session_scope() as db_session:
            return db_session.query(Session).get(pk)

    def get_sessions(
        self,
        min_depth: Optional[float] = None,
        min_quality: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        order_by: str = 'recorded_at'
    ) -> List[Session]:
        """
        Query sessions with filters.

        Args:
            min_depth: Minimum meditation depth
            min_quality: Minimum quality score
            start_date: Start date filter
            end_date: End date filter
            tags: Filter by tags
            limit: Maximum number of results
            order_by: Sort field (default: 'recorded_at')

        Returns:
            List of Session objects
        """
        with self.session_scope() as db_session:
            query = db_session.query(Session)

            # Apply filters
            if min_depth is not None:
                query = query.filter(Session.mean_depth >= min_depth)
            if min_quality is not None:
                query = query.filter(Session.quality_score >= min_quality)
            if start_date:
                query = query.filter(Session.recorded_at >= start_date)
            if end_date:
                query = query.filter(Session.recorded_at <= end_date)
            if tags:
                query = query.join(Session.tags).filter(Tag.name.in_(tags))

            # Order and limit
            if hasattr(Session, order_by):
                query = query.order_by(getattr(Session, order_by).desc())
            if limit:
                query = query.limit(limit)

            return query.all()

    def update_session(self, session_id: str, **kwargs) -> Optional[Session]:
        """
        Update session attributes.

        Args:
            session_id: Session identifier
            **kwargs: Attributes to update

        Returns:
            Updated Session object or None
        """
        with self.session_scope() as db_session:
            session = db_session.query(Session).filter_by(session_id=session_id).first()
            if session:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                session.updated_at = datetime.utcnow()
            return session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        with self.session_scope() as db_session:
            session = db_session.query(Session).filter_by(session_id=session_id).first()
            if session:
                db_session.delete(session)
                return True
            return False

    # ===== Mood Log Methods =====

    def add_mood_log(
        self,
        session_id: int,
        log_type: str,
        stress: int,
        energy: int,
        happiness: int,
        focus: int,
        anxiety: Optional[int] = None,
        notes: str = ""
    ) -> MoodLog:
        """
        Add mood log.

        Args:
            session_id: Session primary key
            log_type: 'before' or 'after'
            stress: 1-5 scale
            energy: 1-5 scale
            happiness: 1-5 scale
            focus: 1-5 scale
            anxiety: 1-5 scale (optional)
            notes: Free text notes

        Returns:
            MoodLog object
        """
        with self.session_scope() as db_session:
            mood_log = MoodLog(
                session_id=session_id,
                log_type=log_type,
                stress=stress,
                energy=energy,
                happiness=happiness,
                focus=focus,
                anxiety=anxiety,
                notes=notes
            )
            db_session.add(mood_log)
            db_session.flush()
            db_session.refresh(mood_log)
            return mood_log

    # ===== Journal Entry Methods =====

    def add_journal_entry(
        self,
        session_id: int,
        notes: str = "",
        insights: str = "",
        challenges: str = "",
        intentions: str = "",
        rating: Optional[int] = None
    ) -> JournalEntry:
        """
        Add journal entry.

        Args:
            session_id: Session primary key
            notes: Session notes
            insights: Insights gained
            challenges: Challenges faced
            intentions: Intentions set
            rating: 1-5 star rating

        Returns:
            JournalEntry object
        """
        with self.session_scope() as db_session:
            entry = JournalEntry(
                session_id=session_id,
                notes=notes,
                insights=insights,
                challenges=challenges,
                intentions=intentions,
                rating=rating
            )
            db_session.add(entry)
            db_session.flush()
            db_session.refresh(entry)
            return entry

    # ===== Tag Methods =====

    def add_tag(self, name: str, color: Optional[str] = None) -> Tag:
        """
        Add or get tag.

        Args:
            name: Tag name
            color: Hex color code

        Returns:
            Tag object
        """
        with self.session_scope() as db_session:
            # Check if exists
            tag = db_session.query(Tag).filter_by(name=name).first()
            if tag:
                return tag

            # Create new
            tag = Tag(name=name, color=color)
            db_session.add(tag)
            db_session.flush()
            db_session.refresh(tag)
            return tag

    def tag_session(self, session_id: str, tag_names: List[str]):
        """
        Add tags to session.

        Args:
            session_id: Session identifier
            tag_names: List of tag names
        """
        with self.session_scope() as db_session:
            session = db_session.query(Session).filter_by(session_id=session_id).first()
            if not session:
                return

            for tag_name in tag_names:
                tag = db_session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db_session.add(tag)
                if tag not in session.tags:
                    session.tags.append(tag)

    def get_sessions_by_tag(self, tag_name: str) -> List[Session]:
        """
        Get sessions with specific tag.

        Args:
            tag_name: Tag name

        Returns:
            List of Session objects
        """
        with self.session_scope() as db_session:
            return db_session.query(Session).join(Session.tags).filter(Tag.name == tag_name).all()

    # ===== Latent Representation Methods =====

    def add_latent_representation(
        self,
        session_id: int,
        latent_vector: List[float],
        reconstruction_loss: Optional[float] = None,
        kl_divergence: Optional[float] = None,
        checkpoint_id: Optional[int] = None
    ) -> LatentRepresentation:
        """
        Add latent representation.

        Args:
            session_id: Session primary key
            latent_vector: 32-dimensional latent vector
            reconstruction_loss: Reconstruction loss
            kl_divergence: KL divergence
            checkpoint_id: Model checkpoint ID

        Returns:
            LatentRepresentation object
        """
        with self.session_scope() as db_session:
            latent = LatentRepresentation(
                session_id=session_id,
                latent_vector=latent_vector,
                reconstruction_loss=reconstruction_loss,
                kl_divergence=kl_divergence,
                checkpoint_id=checkpoint_id
            )
            db_session.add(latent)
            db_session.flush()
            db_session.refresh(latent)
            return latent

    # ===== Checkpoint Methods =====

    def add_checkpoint(
        self,
        name: str,
        checkpoint_path: str,
        epoch: int,
        session_count: int,
        train_loss: Optional[float] = None,
        **kwargs
    ) -> Checkpoint:
        """
        Add training checkpoint.

        Args:
            name: Checkpoint name
            checkpoint_path: Path to .pt file
            epoch: Training epoch
            session_count: Number of sessions trained on
            train_loss: Training loss
            **kwargs: Additional checkpoint attributes

        Returns:
            Checkpoint object
        """
        with self.session_scope() as db_session:
            checkpoint = Checkpoint(
                name=name,
                checkpoint_path=checkpoint_path,
                epoch=epoch,
                session_count=session_count,
                train_loss=train_loss,
                **kwargs
            )
            db_session.add(checkpoint)
            db_session.flush()
            db_session.refresh(checkpoint)
            return checkpoint

    # ===== Generated Output Methods =====

    def add_generated_output(
        self,
        session_id: int,
        output_type: str,
        file_path: str,
        prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> GeneratedOutput:
        """
        Add generated output.

        Args:
            session_id: Session primary key
            output_type: 'image', 'video', 'audio', 'text'
            file_path: Path to generated file
            prompt: Generation prompt
            model_name: Model used
            **kwargs: Additional attributes

        Returns:
            GeneratedOutput object
        """
        with self.session_scope() as db_session:
            output = GeneratedOutput(
                session_id=session_id,
                output_type=output_type,
                file_path=file_path,
                prompt=prompt,
                model_name=model_name,
                **kwargs
            )
            db_session.add(output)
            db_session.flush()
            db_session.refresh(output)
            return output

    # ===== Statistics Methods =====

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics.

        Returns:
            Dict with statistics
        """
        with self.session_scope() as db_session:
            total_sessions = db_session.query(Session).count()
            if total_sessions == 0:
                return {'total_sessions': 0}

            from sqlalchemy import func

            stats = db_session.query(
                func.count(Session.id).label('count'),
                func.avg(Session.mean_depth).label('avg_depth'),
                func.avg(Session.quality_score).label('avg_quality'),
                func.sum(Session.duration_seconds).label('total_duration')
            ).first()

            return {
                'total_sessions': stats.count,
                'avg_depth': stats.avg_depth,
                'avg_quality': stats.avg_quality,
                'total_minutes': stats.total_duration / 60 if stats.total_duration else 0
            }

    def get_recent_sessions(self, limit: int = 10) -> List[Session]:
        """
        Get most recent sessions.

        Args:
            limit: Number of sessions

        Returns:
            List of Session objects
        """
        with self.session_scope() as db_session:
            return db_session.query(Session).order_by(Session.recorded_at.desc()).limit(limit).all()


# Example usage
if __name__ == "__main__":
    manager = SessionManager("sqlite:///test_listener.db")

    print("\n📊 Database initialized")
    print(f"   Tables created")
    print(f"   Ready to use!\n")

    print("Example usage:")
    print("  from database import SessionManager")
    print("  manager = SessionManager('sqlite:///data/listener.db')")
    print("  sessions = manager.get_recent_sessions(10)")
