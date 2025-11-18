"""
Query Builder for THE LISTENER Database

Advanced querying capabilities with fluent interface.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_, or_, func

from .schema import Session, MoodLog, JournalEntry, Tag, LatentRepresentation


class QueryBuilder:
    """
    Fluent query builder for meditation sessions.

    Usage:
        # Simple query
        sessions = QueryBuilder(db_session).min_depth(50).last_n_days(7).execute()

        # Complex query
        sessions = (QueryBuilder(db_session)
                   .min_depth(60)
                   .min_quality(70)
                   .has_tag('morning')
                   .has_mood_improvement()
                   .order_by('mean_depth', desc=True)
                   .limit(10)
                   .execute())

        # Statistics
        stats = QueryBuilder(db_session).min_depth(50).statistics()
    """

    def __init__(self, db_session: DBSession):
        """
        Initialize query builder.

        Args:
            db_session: SQLAlchemy session
        """
        self.db_session = db_session
        self.query = db_session.query(Session)
        self._filters = []

    def min_depth(self, depth: float) -> 'QueryBuilder':
        """Filter by minimum depth."""
        self._filters.append(Session.mean_depth >= depth)
        return self

    def max_depth(self, depth: float) -> 'QueryBuilder':
        """Filter by maximum depth."""
        self._filters.append(Session.mean_depth <= depth)
        return self

    def min_quality(self, quality: float) -> 'QueryBuilder':
        """Filter by minimum quality score."""
        self._filters.append(Session.quality_score >= quality)
        return self

    def max_quality(self, quality: float) -> 'QueryBuilder':
        """Filter by maximum quality score."""
        self._filters.append(Session.quality_score <= quality)
        return self

    def date_range(self, start: datetime, end: datetime) -> 'QueryBuilder':
        """Filter by date range."""
        self._filters.append(and_(
            Session.recorded_at >= start,
            Session.recorded_at <= end
        ))
        return self

    def last_n_days(self, days: int) -> 'QueryBuilder':
        """Filter to last N days."""
        start_date = datetime.now() - timedelta(days=days)
        self._filters.append(Session.recorded_at >= start_date)
        return self

    def this_week(self) -> 'QueryBuilder':
        """Filter to this week."""
        return self.last_n_days(7)

    def this_month(self) -> 'QueryBuilder':
        """Filter to this month."""
        return self.last_n_days(30)

    def has_tag(self, tag_name: str) -> 'QueryBuilder':
        """Filter by tag."""
        self.query = self.query.join(Session.tags).filter(Tag.name == tag_name)
        return self

    def has_any_tag(self, tag_names: List[str]) -> 'QueryBuilder':
        """Filter by any of the tags."""
        self.query = self.query.join(Session.tags).filter(Tag.name.in_(tag_names))
        return self

    def has_rating(self, min_rating: int = 1, max_rating: int = 5) -> 'QueryBuilder':
        """Filter by rating range."""
        self._filters.append(and_(
            Session.rating >= min_rating,
            Session.rating <= max_rating
        ))
        return self

    def min_duration(self, minutes: float) -> 'QueryBuilder':
        """Filter by minimum duration."""
        self._filters.append(Session.duration_seconds >= minutes * 60)
        return self

    def max_duration(self, minutes: float) -> 'QueryBuilder':
        """Filter by maximum duration."""
        self._filters.append(Session.duration_seconds <= minutes * 60)
        return self

    def has_journal(self) -> 'QueryBuilder':
        """Filter sessions with journal entries."""
        self.query = self.query.join(Session.journal_entry)
        return self

    def has_mood_logs(self) -> 'QueryBuilder':
        """Filter sessions with mood logs."""
        self.query = self.query.filter(Session.mood_before.has())
        return self

    def has_mood_improvement(self, min_improvement: int = 1) -> 'QueryBuilder':
        """
        Filter sessions with mood improvement.

        Args:
            min_improvement: Minimum total improvement score
        """
        # This requires subquery - simplified version
        self.query = self.query.filter(
            and_(Session.mood_before.has(), Session.mood_after.has())
        )
        return self

    def alpha_performance_range(self, min_perf: float, max_perf: float) -> 'QueryBuilder':
        """Filter by alpha performance range."""
        self._filters.append(and_(
            Session.alpha_performance >= min_perf,
            Session.alpha_performance <= max_perf
        ))
        return self

    def good_alpha(self) -> 'QueryBuilder':
        """Filter sessions with good alpha performance (>1.0)."""
        return self.alpha_performance_range(1.0, 10.0)

    def high_beta(self) -> 'QueryBuilder':
        """Filter sessions with high beta (active mind)."""
        self._filters.append(Session.beta_mean > Session.alpha_mean)
        return self

    def deep_meditation(self) -> 'QueryBuilder':
        """Filter deep meditation sessions (depth >70)."""
        return self.min_depth(70)

    def order_by(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """
        Order results.

        Args:
            field: Field name to order by
            desc: Descending order
        """
        if hasattr(Session, field):
            attr = getattr(Session, field)
            self.query = self.query.order_by(attr.desc() if desc else attr.asc())
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        """Limit number of results."""
        self.query = self.query.limit(n)
        return self

    def offset(self, n: int) -> 'QueryBuilder':
        """Offset results."""
        self.query = self.query.offset(n)
        return self

    def execute(self) -> List[Session]:
        """
        Execute query and return results.

        Returns:
            List of Session objects
        """
        # Apply all filters
        if self._filters:
            self.query = self.query.filter(and_(*self._filters))

        return self.query.all()

    def count(self) -> int:
        """
        Count matching sessions.

        Returns:
            Number of sessions
        """
        if self._filters:
            self.query = self.query.filter(and_(*self._filters))
        return self.query.count()

    def first(self) -> Optional[Session]:
        """
        Get first matching session.

        Returns:
            Session object or None
        """
        if self._filters:
            self.query = self.query.filter(and_(*self._filters))
        return self.query.first()

    def statistics(self) -> Dict[str, Any]:
        """
        Compute statistics for matching sessions.

        Returns:
            Dict with statistics
        """
        if self._filters:
            self.query = self.query.filter(and_(*self._filters))

        stats = self.query.with_entities(
            func.count(Session.id).label('count'),
            func.avg(Session.mean_depth).label('avg_depth'),
            func.max(Session.mean_depth).label('max_depth'),
            func.avg(Session.quality_score).label('avg_quality'),
            func.avg(Session.alpha_performance).label('avg_alpha'),
            func.sum(Session.duration_seconds).label('total_duration')
        ).first()

        return {
            'count': stats.count or 0,
            'avg_depth': stats.avg_depth or 0,
            'max_depth': stats.max_depth or 0,
            'avg_quality': stats.avg_quality or 0,
            'avg_alpha': stats.avg_alpha or 0,
            'total_minutes': (stats.total_duration or 0) / 60
        }

    def to_dataframe(self):
        """
        Convert results to pandas DataFrame.

        Returns:
            pandas DataFrame
        """
        import pandas as pd

        sessions = self.execute()
        return pd.DataFrame([s.to_dict() for s in sessions])


# Convenience functions

def find_best_sessions(db_session: DBSession, n: int = 10, metric: str = 'mean_depth') -> List[Session]:
    """
    Find best sessions by metric.

    Args:
        db_session: SQLAlchemy session
        n: Number of sessions
        metric: Metric to sort by

    Returns:
        List of Session objects
    """
    return (QueryBuilder(db_session)
            .order_by(metric, desc=True)
            .limit(n)
            .execute())


def find_recent_deep_sessions(db_session: DBSession, days: int = 30, min_depth: float = 70) -> List[Session]:
    """
    Find recent deep meditation sessions.

    Args:
        db_session: SQLAlchemy session
        days: Look back days
        min_depth: Minimum depth threshold

    Returns:
        List of Session objects
    """
    return (QueryBuilder(db_session)
            .last_n_days(days)
            .min_depth(min_depth)
            .order_by('recorded_at', desc=True)
            .execute())


def find_sessions_by_pattern(
    db_session: DBSession,
    depth_range: tuple = None,
    quality_range: tuple = None,
    tags: List[str] = None
) -> List[Session]:
    """
    Find sessions matching pattern.

    Args:
        db_session: SQLAlchemy session
        depth_range: (min, max) depth
        quality_range: (min, max) quality
        tags: List of tags

    Returns:
        List of Session objects
    """
    builder = QueryBuilder(db_session)

    if depth_range:
        builder = builder.min_depth(depth_range[0]).max_depth(depth_range[1])
    if quality_range:
        builder = builder.min_quality(quality_range[0]).max_quality(quality_range[1])
    if tags:
        builder = builder.has_any_tag(tags)

    return builder.execute()


# Example usage
if __name__ == "__main__":
    print("Query Builder Examples:")
    print()
    print("# Simple query")
    print("sessions = QueryBuilder(db_session).min_depth(50).execute()")
    print()
    print("# Complex query")
    print("sessions = (QueryBuilder(db_session)")
    print("           .min_depth(60)")
    print("           .min_quality(70)")
    print("           .has_tag('morning')")
    print("           .last_n_days(7)")
    print("           .order_by('mean_depth', desc=True)")
    print("           .execute())")
    print()
    print("# Statistics")
    print("stats = QueryBuilder(db_session).this_month().statistics()")
    print("print(f'This month: {stats['count']} sessions, avg depth: {stats['avg_depth']:.1f}')")
