#!/usr/bin/env python3
"""
Database Upgrade Script

Adds indexes to existing databases for better query performance.

Usage:
    python scripts/upgrade_database.py
    python scripts/upgrade_database.py --database sqlite:///path/to/db.db
"""

import sys
from pathlib import Path
import argparse
from sqlalchemy import create_engine, inspect, Index

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Session


def add_indexes(database_url: str, dry_run: bool = False):
    """
    Add performance indexes to database

    Args:
        database_url: Database URL
        dry_run: Print actions without executing
    """
    print("=" * 60)
    print("  📈 Database Upgrade - Adding Indexes")
    print("=" * 60)
    print()
    print(f"Database: {database_url}")
    print(f"Dry run: {dry_run}")
    print()

    # Connect to database
    engine = create_engine(database_url)
    inspector = inspect(engine)

    # Get existing indexes
    existing_indexes = inspector.get_indexes('sessions')
    existing_index_names = {idx['name'] for idx in existing_indexes}

    print("Existing indexes:")
    for idx in existing_indexes:
        print(f"  - {idx['name']}: {idx['column_names']}")
    print()

    # Define indexes to add
    indexes_to_add = [
        ('idx_mean_depth', 'mean_depth'),
        ('idx_max_depth', 'max_depth'),
        ('idx_quality_score', 'quality_score'),
    ]

    # Add indexes
    added = 0
    skipped = 0

    for idx_name, column_name in indexes_to_add:
        if idx_name in existing_index_names:
            print(f"⏭️  Skipping {idx_name} (already exists)")
            skipped += 1
            continue

        if dry_run:
            print(f"Would create index: {idx_name} on {column_name}")
        else:
            print(f"Creating index: {idx_name} on {column_name}...")
            try:
                # Create index using raw SQL (more reliable)
                with engine.connect() as conn:
                    conn.execute(f"CREATE INDEX {idx_name} ON sessions ({column_name})")
                    conn.commit()
                print(f"  ✅ Created {idx_name}")
                added += 1
            except Exception as e:
                print(f"  ❌ Failed to create {idx_name}: {e}")

    # Summary
    print()
    print("=" * 60)
    print("  Summary")
    print("=" * 60)
    if dry_run:
        print(f"Would add: {len(indexes_to_add) - skipped} indexes")
    else:
        print(f"Added: {added} indexes")
    print(f"Skipped: {skipped} indexes (already exist)")
    print()

    # Show final indexes
    if not dry_run:
        final_indexes = inspector.get_indexes('sessions')
        print("Final indexes:")
        for idx in final_indexes:
            print(f"  - {idx['name']}: {idx['column_names']}")
        print()

    print("✅ Database upgrade complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade database with performance indexes"
    )

    parser.add_argument(
        "--database",
        default="sqlite:///data/listener.db",
        help="Database URL (default: sqlite:///data/listener.db)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )

    args = parser.parse_args()

    try:
        add_indexes(args.database, dry_run=args.dry_run)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
        sys.exit(0)
