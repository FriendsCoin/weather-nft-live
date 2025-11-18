#!/usr/bin/env python3
"""
Migration Tool - THE LISTENER

Convert existing .h5 session files to database format.

Maintains backward compatibility while enabling
structured querying and analysis.

Usage:
    # Migrate all sessions
    python migration.py --sessions-dir data/sessions --database data/listener.db

    # Migrate specific session
    python migration.py --session data/sessions/session_001.h5

    # Dry run (preview without writing)
    python migration.py --sessions-dir data/sessions --dry-run
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from glob import glob

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import SessionManager, Session
from src.utils.meditation_analysis import MeditationAnalyzer


class MigrationTool:
    """
    Migrate .h5 session files to database.

    Extracts metadata and statistics from .h5 files
    and stores in structured database.
    """

    def __init__(self, database_url: str = "sqlite:///data/listener.db"):
        """
        Initialize migration tool.

        Args:
            database_url: Database URL
        """
        self.database_url = database_url
        self.manager = SessionManager(database_url)
        self.analyzer = MeditationAnalyzer()

        print("🔄 Migration tool initialized")
        print(f"   Database: {database_url}")

    def migrate_session(
        self,
        h5_path: str,
        dry_run: bool = False
    ) -> Optional[Dict]:
        """
        Migrate single session from .h5 to database.

        Args:
            h5_path: Path to .h5 file
            dry_run: Preview without writing

        Returns:
            Session data dict or None if failed
        """
        h5_path = Path(h5_path)

        if not h5_path.exists():
            print(f"❌ File not found: {h5_path}")
            return None

        try:
            # Extract session ID from filename
            session_id = h5_path.stem

            # Check if already migrated
            existing = self.manager.get_session(session_id)
            if existing and not dry_run:
                print(f"⚠️  Already migrated: {session_id}")
                return existing.to_dict()

            # Load features
            features_df = pd.read_hdf(h5_path, key='features')

            # Analyze session
            print(f"📊 Analyzing {session_id}...")
            metrics = self.analyzer.analyze_session(features_df)

            # Extract timestamp from session_id or file mtime
            try:
                # Try parsing from session_id (format: session_YYYYMMDD_HHMMSS)
                date_str = session_id.split('_')[1] if '_' in session_id else None
                time_str = session_id.split('_')[2] if '_' in session_id else None

                if date_str and time_str:
                    recorded_at = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                else:
                    # Fall back to file modification time
                    recorded_at = datetime.fromtimestamp(h5_path.stat().st_mtime)
            except:
                recorded_at = datetime.fromtimestamp(h5_path.stat().st_mtime)

            # Compute duration from features
            duration_seconds = len(features_df) * 1.0  # Assuming 1 Hz sampling

            # Extract band power statistics
            alpha_cols = [c for c in features_df.columns if 'alpha' in c.lower() and 'mean' in c.lower()]
            beta_cols = [c for c in features_df.columns if 'beta' in c.lower() and 'mean' in c.lower()]
            theta_cols = [c for c in features_df.columns if 'theta' in c.lower() and 'mean' in c.lower()]
            delta_cols = [c for c in features_df.columns if 'delta' in c.lower() and 'mean' in c.lower()]
            gamma_cols = [c for c in features_df.columns if 'gamma' in c.lower() and 'mean' in c.lower()]

            # Prepare session data
            session_data = {
                'session_id': session_id,
                'recorded_at': recorded_at,
                'duration_seconds': duration_seconds,

                # Meditation metrics
                'mean_depth': metrics.get('mean_depth', 0),
                'max_depth': metrics.get('max_depth', 0),
                'quality_score': metrics.get('quality_score', 0),

                # Band powers
                'alpha_mean': features_df[alpha_cols].mean().mean() if alpha_cols else None,
                'alpha_std': features_df[alpha_cols].std().mean() if alpha_cols else None,
                'beta_mean': features_df[beta_cols].mean().mean() if beta_cols else None,
                'beta_std': features_df[beta_cols].std().mean() if beta_cols else None,
                'theta_mean': features_df[theta_cols].mean().mean() if theta_cols else None,
                'theta_std': features_df[theta_cols].std().mean() if theta_cols else None,
                'delta_mean': features_df[delta_cols].mean().mean() if delta_cols else None,
                'delta_std': features_df[delta_cols].std().mean() if delta_cols else None,
                'gamma_mean': features_df[gamma_cols].mean().mean() if gamma_cols else None,
                'gamma_std': features_df[gamma_cols].std().mean() if gamma_cols else None,

                # Performance metrics
                'alpha_performance': metrics.get('alpha_performance', 0),
                'beta_performance': metrics.get('beta_performance', 0),
                'alpha_beta_ratio': metrics.get('alpha_beta_ratio', 0),

                # Advanced metrics
                'learning_stage': metrics.get('learning_stage'),
                'training_effect': metrics.get('training_effect'),
                'delta_reduction': metrics.get('delta_reduction'),

                # Personal thresholds
                'thresholds': metrics.get('personal_thresholds', {}),

                # File paths
                'features_path': str(h5_path),

                # Quality indicators
                'signal_quality': 100.0  # Assume good if processed
            }

            if dry_run:
                print(f"✅ Would migrate: {session_id}")
                print(f"   Depth: {session_data['mean_depth']:.1f}")
                print(f"   Quality: {session_data['quality_score']:.1f}")
                print(f"   Duration: {session_data['duration_seconds']:.0f}s")
                return session_data

            # Add to database
            session = self.manager.add_meditation_session(**session_data)

            print(f"✅ Migrated: {session_id}")
            return session.to_dict()

        except Exception as e:
            print(f"❌ Error migrating {h5_path}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def migrate_directory(
        self,
        sessions_dir: str,
        pattern: str = "*.h5",
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Migrate all sessions in directory.

        Args:
            sessions_dir: Directory with .h5 files
            pattern: File pattern to match
            dry_run: Preview without writing

        Returns:
            Statistics dict
        """
        sessions_dir = Path(sessions_dir)

        if not sessions_dir.exists():
            print(f"❌ Directory not found: {sessions_dir}")
            return {}

        # Find all .h5 files
        h5_files = sorted(sessions_dir.glob(pattern))

        if not h5_files:
            print(f"❌ No .h5 files found in {sessions_dir}")
            return {}

        print(f"\n📂 Found {len(h5_files)} session files")
        print(f"   Directory: {sessions_dir}")
        print()

        # Migrate each session
        migrated = 0
        skipped = 0
        failed = 0

        for h5_file in h5_files:
            result = self.migrate_session(str(h5_file), dry_run=dry_run)

            if result:
                migrated += 1
            elif result is None:
                failed += 1
            else:
                skipped += 1

        # Summary
        print()
        print("=" * 60)
        print(f"  📊 Migration {'Preview' if dry_run else 'Complete'}")
        print("=" * 60)
        print(f"Migrated:  {migrated}")
        print(f"Skipped:   {skipped}")
        print(f"Failed:    {failed}")
        print("=" * 60)

        if dry_run:
            print()
            print("Run without --dry-run to actually migrate")

        return {
            'migrated': migrated,
            'skipped': skipped,
            'failed': failed,
            'total': len(h5_files)
        }

    def migrate_mood_logs(self, mood_log_file: str = "data/mood_logs/mood_log.json"):
        """
        Migrate mood logs from JSON to database.

        Args:
            mood_log_file: Path to mood_log.json
        """
        import json

        mood_log_file = Path(mood_log_file)

        if not mood_log_file.exists():
            print(f"⚠️  Mood log not found: {mood_log_file}")
            return

        print(f"🎭 Migrating mood logs from {mood_log_file}")

        with open(mood_log_file, 'r') as f:
            logs = json.load(f)

        migrated = 0
        for log in logs:
            # Find matching session
            # Mood logs use entry_id format YYYYMMDD_HHMMSS
            # Sessions use session_YYYYMMDD_HHMMSS
            entry_id = log.get('id', '')
            session_id = f"session_{entry_id}"

            session = self.manager.get_session(session_id)
            if not session:
                continue

            # Add mood log
            try:
                self.manager.add_mood_log(
                    session_id=session.id,
                    log_type=log.get('type'),
                    stress=log.get('stress'),
                    energy=log.get('energy'),
                    happiness=log.get('happiness'),
                    focus=log.get('focus'),
                    anxiety=log.get('anxiety'),
                    notes=log.get('notes', '')
                )
                migrated += 1
            except Exception as e:
                print(f"⚠️  Error migrating mood log: {e}")

        print(f"✅ Migrated {migrated} mood logs")

    def migrate_journal_entries(self, journal_file: str = "data/journal.json"):
        """
        Migrate journal entries from JSON to database.

        Args:
            journal_file: Path to journal.json
        """
        import json

        journal_file = Path(journal_file)

        if not journal_file.exists():
            print(f"⚠️  Journal not found: {journal_file}")
            return

        print(f"📔 Migrating journal entries from {journal_file}")

        with open(journal_file, 'r') as f:
            entries = json.load(f)

        migrated = 0
        for entry in entries:
            session_id = entry.get('session_id')
            session = self.manager.get_session(session_id)

            if not session:
                continue

            try:
                self.manager.add_journal_entry(
                    session_id=session.id,
                    notes=entry.get('notes', ''),
                    insights=entry.get('insights', ''),
                    challenges=entry.get('challenges', ''),
                    intentions=entry.get('intentions', ''),
                    rating=entry.get('rating')
                )

                # Add tags
                tags = entry.get('tags', [])
                if tags:
                    self.manager.tag_session(session_id, tags)

                migrated += 1
            except Exception as e:
                print(f"⚠️  Error migrating journal entry: {e}")

        print(f"✅ Migrated {migrated} journal entries")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate .h5 session files to database"
    )
    parser.add_argument(
        "--sessions-dir", type=str,
        help="Directory with .h5 session files"
    )
    parser.add_argument(
        "--session", type=str,
        help="Single session file to migrate"
    )
    parser.add_argument(
        "--database", default="sqlite:///data/listener.db",
        help="Database URL (default: sqlite:///data/listener.db)"
    )
    parser.add_argument(
        "--pattern", default="*.h5",
        help="File pattern to match (default: *.h5)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview migration without writing to database"
    )
    parser.add_argument(
        "--mood-logs", type=str,
        help="Migrate mood logs from JSON file"
    )
    parser.add_argument(
        "--journal", type=str,
        help="Migrate journal entries from JSON file"
    )

    args = parser.parse_args()

    # Create migration tool
    tool = MigrationTool(args.database)

    # Migrate sessions
    if args.sessions_dir:
        tool.migrate_directory(args.sessions_dir, args.pattern, args.dry_run)

    elif args.session:
        tool.migrate_session(args.session, args.dry_run)

    # Migrate mood logs
    if args.mood_logs:
        tool.migrate_mood_logs(args.mood_logs)

    # Migrate journal
    if args.journal:
        tool.migrate_journal_entries(args.journal)

    # Show stats
    if not args.dry_run:
        stats = tool.manager.get_statistics()
        print()
        print("📊 Database Statistics:")
        print(f"   Total sessions: {stats['total_sessions']}")
        print(f"   Average depth: {stats.get('avg_depth', 0):.1f}")
        print(f"   Average quality: {stats.get('avg_quality', 0):.1f}")
        print(f"   Total time: {stats.get('total_minutes', 0):.1f} minutes")


if __name__ == "__main__":
    main()
