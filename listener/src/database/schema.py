"""
Database Schema for THE LISTENER

SQLAlchemy models for storing meditation sessions,
features, outputs, and metadata.

Replaces scattered .h5 files with structured database.
"""

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import (
    create_engine,
    Column, Integer, Float, String, DateTime,
    Boolean, Text, JSON, ForeignKey, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session as DBSession
import json

Base = declarative_base()


# Association table for session tags
session_tags = Table(
    'session_tags',
    Base.metadata,
    Column('session_id', Integer, ForeignKey('sessions.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Session(Base):
    """
    Meditation session record.

    Stores metadata and aggregated statistics for each session.
    Links to full timeseries data in .h5 files.
    """
    __tablename__ = 'sessions'

    # Primary key
    id = Column(Integer, primary_key=True)

    # Session identification
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    recorded_at = Column(DateTime, nullable=False, index=True)
    duration_seconds = Column(Float)

    # File paths
    raw_data_path = Column(String(500))  # Path to raw .h5
    features_path = Column(String(500))  # Path to features .h5
    processed_data_path = Column(String(500))  # Path to processed .h5

    # Aggregated meditation metrics
    mean_depth = Column(Float)
    max_depth = Column(Float)
    quality_score = Column(Float)

    # Band power statistics (averaged across channels and time)
    alpha_mean = Column(Float)
    alpha_std = Column(Float)
    beta_mean = Column(Float)
    beta_std = Column(Float)
    theta_mean = Column(Float)
    theta_std = Column(Float)
    delta_mean = Column(Float)
    delta_std = Column(Float)
    gamma_mean = Column(Float)
    gamma_std = Column(Float)

    # Performance metrics
    alpha_performance = Column(Float)
    beta_performance = Column(Float)
    alpha_beta_ratio = Column(Float)

    # Advanced neurofeedback metrics
    learning_stage = Column(String(50))  # fast_learner, moderate, slow
    training_effect = Column(Float)
    delta_reduction = Column(Float)

    # Personal thresholds (JSON)
    thresholds = Column(JSON)  # {alpha_upper, alpha_lower, beta_upper, beta_lower}

    # Session quality indicators
    artifact_percentage = Column(Float)  # % of data removed as artifacts
    signal_quality = Column(Float)  # Overall signal quality (0-100)

    # User notes and ratings
    notes = Column(Text)
    rating = Column(Integer)  # 1-5 stars

    # Relationships
    mood_before = relationship("MoodLog",
                              foreign_keys="MoodLog.session_id",
                              primaryjoin="and_(Session.id==MoodLog.session_id, MoodLog.log_type=='before')",
                              uselist=False)
    mood_after = relationship("MoodLog",
                             foreign_keys="MoodLog.session_id",
                             primaryjoin="and_(Session.id==MoodLog.session_id, MoodLog.log_type=='after')",
                             uselist=False)
    journal_entry = relationship("JournalEntry", back_populates="session", uselist=False)
    generated_outputs = relationship("GeneratedOutput", back_populates="session")
    latent_vector = relationship("LatentRepresentation", back_populates="session", uselist=False)
    tags = relationship("Tag", secondary=session_tags, back_populates="sessions")

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Session(id={self.session_id}, date={self.recorded_at}, depth={self.mean_depth:.1f})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'duration_seconds': self.duration_seconds,
            'mean_depth': self.mean_depth,
            'quality_score': self.quality_score,
            'alpha_performance': self.alpha_performance,
            'rating': self.rating,
            'notes': self.notes
        }


class MoodLog(Base):
    """
    Mood log before/after meditation.

    Tracks subjective emotional state.
    """
    __tablename__ = 'mood_logs'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), index=True)
    log_type = Column(String(10), nullable=False)  # 'before' or 'after'

    # Mood metrics (1-5 scale)
    stress = Column(Integer)
    energy = Column(Integer)
    happiness = Column(Integer)
    focus = Column(Integer)
    anxiety = Column(Integer)

    # Timestamp
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Notes
    notes = Column(Text)

    # Relationship
    session = relationship("Session", foreign_keys=[session_id])

    def __repr__(self):
        return f"<MoodLog(session={self.session_id}, type={self.log_type})>"


class JournalEntry(Base):
    """
    Session journal entry.

    Qualitative reflections and insights.
    """
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), unique=True, index=True)

    # Journal fields
    notes = Column(Text)
    insights = Column(Text)
    challenges = Column(Text)
    intentions = Column(Text)

    # Rating
    rating = Column(Integer)  # 1-5 stars

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    session = relationship("Session", back_populates="journal_entry")

    def __repr__(self):
        return f"<JournalEntry(session={self.session_id}, rating={self.rating})>"


class Tag(Base):
    """
    Tag for categorizing sessions.

    Examples: 'morning', 'deep', 'restless', 'breakthrough'
    """
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7))  # Hex color code

    # Relationships
    sessions = relationship("Session", secondary=session_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(name={self.name})>"


class LatentRepresentation(Base):
    """
    VAE latent vector for a session.

    32-dimensional latent space representation.
    """
    __tablename__ = 'latent_representations'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), unique=True, index=True)

    # Latent vector (stored as JSON array)
    latent_vector = Column(JSON, nullable=False)  # [32 floats]

    # Reconstruction metrics
    reconstruction_loss = Column(Float)
    kl_divergence = Column(Float)

    # Model checkpoint used
    checkpoint_id = Column(Integer, ForeignKey('checkpoints.id'))

    # Timestamp
    computed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="latent_vector")
    checkpoint = relationship("Checkpoint")

    def __repr__(self):
        return f"<LatentRepresentation(session={self.session_id})>"


class Checkpoint(Base):
    """
    VAE model checkpoint.

    Tracks training progress and model evolution.
    """
    __tablename__ = 'checkpoints'

    id = Column(Integer, primary_key=True)

    # Checkpoint identification
    name = Column(String(100), unique=True, nullable=False)
    epoch = Column(Integer)
    session_count = Column(Integer)  # Number of sessions trained on

    # File path
    checkpoint_path = Column(String(500), nullable=False)

    # Training metrics
    train_loss = Column(Float)
    val_loss = Column(Float)
    reconstruction_loss = Column(Float)
    kl_loss = Column(Float)

    # Model configuration (JSON)
    config = Column(JSON)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Checkpoint(name={self.name}, epoch={self.epoch})>"


class GeneratedOutput(Base):
    """
    Generated multimedia output (image, video, audio).

    Tracks all AI-generated content from sessions.
    """
    __tablename__ = 'generated_outputs'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), index=True)

    # Output type
    output_type = Column(String(20), nullable=False)  # 'image', 'video', 'audio', 'text'

    # File path
    file_path = Column(String(500), nullable=False)

    # Generation parameters
    prompt = Column(Text)  # LLM prompt or description
    model_name = Column(String(100))  # Model used (e.g., 'stable-diffusion-v1-5')
    generation_params = Column(JSON)  # Model parameters

    # Quality metrics
    generation_time_seconds = Column(Float)
    file_size_bytes = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    session = relationship("Session", back_populates="generated_outputs")

    def __repr__(self):
        return f"<GeneratedOutput(type={self.output_type}, session={self.session_id})>"


class User(Base):
    """
    User/practitioner information.

    Single-user system but tracks metadata.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    # User info
    name = Column(String(100))
    email = Column(String(200))

    # Practice metadata
    first_session_date = Column(DateTime)
    total_sessions = Column(Integer, default=0)
    total_meditation_minutes = Column(Float, default=0.0)

    # Baseline thresholds (JSON)
    baseline_thresholds = Column(JSON)

    # Learning profile
    learning_stage = Column(String(50))  # From first session analysis
    expected_improvement = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(name={self.name}, sessions={self.total_sessions})>"


# Database initialization utilities

def create_database(database_url: str = "sqlite:///listener.db"):
    """
    Create database with all tables.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        Engine instance
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    print(f"✅ Database created: {database_url}")
    return engine


def get_session_maker(database_url: str = "sqlite:///listener.db"):
    """
    Get SQLAlchemy session maker.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        SessionMaker instance
    """
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(database_url, echo=False)
    SessionMaker = sessionmaker(bind=engine)
    return SessionMaker


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize THE LISTENER database")
    parser.add_argument("--database", default="sqlite:///data/listener.db",
                       help="Database URL (default: sqlite:///data/listener.db)")
    parser.add_argument("--create", action="store_true",
                       help="Create database tables")

    args = parser.parse_args()

    if args.create:
        engine = create_database(args.database)
        print(f"\n📊 Database structure:")
        print(f"   Sessions: meditation session records")
        print(f"   MoodLogs: before/after mood tracking")
        print(f"   JournalEntries: session notes and insights")
        print(f"   Tags: session categorization")
        print(f"   LatentRepresentations: VAE latent vectors")
        print(f"   Checkpoints: model training checkpoints")
        print(f"   GeneratedOutputs: images, videos, audio")
        print(f"   Users: practitioner metadata")
        print(f"\n✨ Ready to use!")
    else:
        print("Usage:")
        print("  python schema.py --create")
        print("  python schema.py --database postgresql://user:pass@localhost/listener --create")
