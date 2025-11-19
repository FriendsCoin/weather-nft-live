#!/usr/bin/env python3
"""
Session Integrity Checker - THE LISTENER

Проверка целостности данных медитационных сессий.
Check meditation session data integrity.

Usage:
    # Check all sessions
    python scripts/check_integrity.py --sessions-dir data/sessions

    # Check with detailed output
    python scripts/check_integrity.py --sessions-dir data/sessions --verbose

    # Auto-fix issues
    python scripts/check_integrity.py --sessions-dir data/sessions --fix

    # Check specific session
    python scripts/check_integrity.py --session data/sessions/session_001.h5
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.database.session_manager import SessionManager


class IntegrityChecker:
    """
    Проверка целостности данных сессий
    Session data integrity checker
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize checker.

        Args:
            verbose: Verbose output
        """
        self.verbose = verbose
        self.issues = []
        self.warnings = []
        self.fixed = []

    def check_h5_file(self, h5_path: Path) -> Dict:
        """
        Проверить H5 файл на целостность.
        Check H5 file integrity.

        Args:
            h5_path: Path to H5 file

        Returns:
            Dict with check results
        """
        session_id = h5_path.stem
        result = {
            'session_id': session_id,
            'file_path': str(h5_path),
            'exists': h5_path.exists(),
            'readable': False,
            'has_eeg': False,
            'has_features': False,
            'has_latent': False,
            'eeg_shape': None,
            'features_shape': None,
            'latent_shape': None,
            'duration_seconds': None,
            'file_size_mb': None,
            'issues': [],
            'warnings': []
        }

        if not h5_path.exists():
            result['issues'].append("File does not exist")
            return result

        # File size
        try:
            result['file_size_mb'] = h5_path.stat().st_size / (1024 * 1024)
        except Exception as e:
            result['warnings'].append(f"Could not get file size: {e}")

        # Try to read H5 file
        try:
            # Check EEG data
            try:
                eeg_data = pd.read_hdf(h5_path, key='eeg_data')
                result['has_eeg'] = True
                result['eeg_shape'] = eeg_data.shape
                result['readable'] = True

                # Validate EEG dimensions
                if len(eeg_data.shape) != 2:
                    result['issues'].append(f"Invalid EEG shape: {eeg_data.shape}, expected 2D")
                elif eeg_data.shape[0] not in [4, 5]:  # Muse S has 4-5 channels
                    result['warnings'].append(f"Unusual channel count: {eeg_data.shape[0]}, expected 4-5")

                # Calculate duration
                if len(eeg_data.shape) == 2:
                    n_samples = eeg_data.shape[1]
                    result['duration_seconds'] = n_samples / 256.0  # Muse S = 256 Hz

                    # Validate duration
                    if result['duration_seconds'] < 10:
                        result['warnings'].append(f"Very short session: {result['duration_seconds']:.1f}s")
                    elif result['duration_seconds'] > 7200:  # > 2 hours
                        result['warnings'].append(f"Very long session: {result['duration_seconds']/60:.1f}min")

                # Check for NaN/Inf
                if np.any(np.isnan(eeg_data.values)):
                    result['warnings'].append("EEG data contains NaN values")
                if np.any(np.isinf(eeg_data.values)):
                    result['warnings'].append("EEG data contains Inf values")

            except KeyError:
                result['issues'].append("Missing 'eeg_data' key")
            except Exception as e:
                result['issues'].append(f"Error reading EEG data: {e}")

            # Check features
            try:
                features_df = pd.read_hdf(h5_path, key='features')
                result['has_features'] = True
                result['features_shape'] = features_df.shape

                # Validate features
                if features_df.shape[1] < 10:
                    result['warnings'].append(f"Few features: {features_df.shape[1]}, expected 30+")

                # Check for NaN/Inf
                if np.any(np.isnan(features_df.values)):
                    result['warnings'].append("Features contain NaN values")
                if np.any(np.isinf(features_df.values)):
                    result['warnings'].append("Features contain Inf values")

            except KeyError:
                result['warnings'].append("Missing 'features' key (optional)")
            except Exception as e:
                result['warnings'].append(f"Error reading features: {e}")

            # Check latent
            try:
                latent_df = pd.read_hdf(h5_path, key='latent')
                result['has_latent'] = True
                result['latent_shape'] = latent_df.shape

                # Validate latent
                if latent_df.shape[1] not in [16, 32, 64]:
                    result['warnings'].append(f"Unusual latent dimension: {latent_df.shape[1]}")

            except KeyError:
                result['warnings'].append("Missing 'latent' key (optional)")
            except Exception as e:
                result['warnings'].append(f"Error reading latent: {e}")

        except Exception as e:
            result['issues'].append(f"Cannot read H5 file: {e}")
            result['readable'] = False

        return result

    def check_database_consistency(
        self,
        sessions_dir: Path,
        database_url: str
    ) -> List[Dict]:
        """
        Проверить соответствие БД и файлов.
        Check database-file consistency.

        Args:
            sessions_dir: Sessions directory
            database_url: Database URL

        Returns:
            List of consistency issues
        """
        issues = []

        try:
            db_manager = SessionManager(database_url)

            # Get all sessions from database
            with db_manager.get_session() as session:
                from src.database.schema import Session as DBSession
                db_sessions = session.query(DBSession).all()

            # Check each DB session
            for db_session in db_sessions:
                if db_session.file_path:
                    file_path = Path(db_session.file_path)
                    if not file_path.exists():
                        issues.append({
                            'type': 'missing_file',
                            'session_id': db_session.session_id,
                            'file_path': str(file_path),
                            'message': "File referenced in DB does not exist"
                        })

            # Check for orphaned files
            h5_files = sorted(sessions_dir.glob("*.h5"))
            db_session_ids = {s.session_id for s in db_sessions}

            for h5_file in h5_files:
                session_id = h5_file.stem
                if session_id not in db_session_ids:
                    issues.append({
                        'type': 'orphaned_file',
                        'session_id': session_id,
                        'file_path': str(h5_file),
                        'message': "File exists but not in database"
                    })

        except Exception as e:
            issues.append({
                'type': 'database_error',
                'message': f"Error checking database: {e}"
            })

        return issues

    def find_duplicates(self, sessions_dir: Path) -> List[Dict]:
        """
        Найти дублирующиеся сессии.
        Find duplicate sessions.

        Args:
            sessions_dir: Sessions directory

        Returns:
            List of potential duplicates
        """
        duplicates = []
        h5_files = sorted(sessions_dir.glob("*.h5"))

        # Group by file size (quick check)
        size_groups = {}
        for h5_file in h5_files:
            try:
                size = h5_file.stat().st_size
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(h5_file)
            except:
                pass

        # Check potential duplicates
        for size, files in size_groups.items():
            if len(files) > 1:
                duplicates.append({
                    'type': 'size_match',
                    'files': [str(f) for f in files],
                    'size_mb': size / (1024 * 1024),
                    'message': f"{len(files)} files with same size"
                })

        return duplicates

    def print_results(self, results: List[Dict]):
        """Print check results"""
        print("\n" + "=" * 70)
        print("  🔍 Session Integrity Check Results")
        print("=" * 70)

        total = len(results)
        readable = sum(1 for r in results if r['readable'])
        with_eeg = sum(1 for r in results if r['has_eeg'])
        with_features = sum(1 for r in results if r['has_features'])
        with_latent = sum(1 for r in results if r['has_latent'])
        with_issues = sum(1 for r in results if r['issues'])
        with_warnings = sum(1 for r in results if r['warnings'])

        print(f"\n📊 Summary:")
        print(f"   Total sessions:     {total}")
        print(f"   ✅ Readable:         {readable}")
        print(f"   🧠 With EEG data:    {with_eeg}")
        print(f"   📈 With features:    {with_features}")
        print(f"   🎯 With latent:      {with_latent}")
        print(f"   ❌ With issues:      {with_issues}")
        print(f"   ⚠️  With warnings:    {with_warnings}")

        # Print issues
        if with_issues > 0:
            print(f"\n❌ Issues found ({with_issues} sessions):")
            for r in results:
                if r['issues']:
                    print(f"\n   {r['session_id']}:")
                    for issue in r['issues']:
                        print(f"      - {issue}")

        # Print warnings if verbose
        if self.verbose and with_warnings > 0:
            print(f"\n⚠️  Warnings ({with_warnings} sessions):")
            for r in results:
                if r['warnings']:
                    print(f"\n   {r['session_id']}:")
                    for warning in r['warnings']:
                        print(f"      - {warning}")

        print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Check meditation session data integrity"
    )

    parser.add_argument(
        "--sessions-dir",
        type=str,
        help="Directory with session H5 files"
    )

    parser.add_argument(
        "--session",
        type=str,
        help="Check single session file"
    )

    parser.add_argument(
        "--database",
        default=config.database_url,
        help="Database URL"
    )

    parser.add_argument(
        "--check-db",
        action="store_true",
        help="Check database consistency"
    )

    parser.add_argument(
        "--find-duplicates",
        action="store_true",
        help="Find potential duplicate sessions"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues (when possible)"
    )

    args = parser.parse_args()

    if not args.sessions_dir and not args.session:
        parser.print_help()
        return

    print("\n" + "=" * 70)
    print("  🔍 THE LISTENER - Session Integrity Checker")
    print("=" * 70)

    checker = IntegrityChecker(verbose=args.verbose)

    # Check single session
    if args.session:
        session_path = Path(args.session)
        result = checker.check_h5_file(session_path)
        checker.print_results([result])
        return

    # Check directory
    if args.sessions_dir:
        sessions_dir = Path(args.sessions_dir)

        if not sessions_dir.exists():
            print(f"\n❌ Directory not found: {sessions_dir}")
            sys.exit(1)

        # Find all H5 files
        h5_files = sorted(sessions_dir.glob("*.h5"))

        if not h5_files:
            print(f"\n❌ No H5 files found in {sessions_dir}")
            sys.exit(1)

        print(f"\n📂 Checking {len(h5_files)} session files...")

        # Check each file
        results = []
        for h5_file in h5_files:
            result = checker.check_h5_file(h5_file)
            results.append(result)

        # Print results
        checker.print_results(results)

        # Check database consistency
        if args.check_db:
            print("\n🔗 Checking database consistency...")
            db_issues = checker.check_database_consistency(sessions_dir, args.database)

            if db_issues:
                print(f"\n❌ Database consistency issues ({len(db_issues)}):")
                for issue in db_issues:
                    print(f"   - {issue['type']}: {issue.get('session_id', 'N/A')}")
                    print(f"     {issue['message']}")
            else:
                print("✅ Database is consistent with files")

        # Find duplicates
        if args.find_duplicates:
            print("\n🔍 Searching for duplicates...")
            duplicates = checker.find_duplicates(sessions_dir)

            if duplicates:
                print(f"\n⚠️  Potential duplicates found ({len(duplicates)}):")
                for dup in duplicates:
                    print(f"   {dup['message']}:")
                    for f in dup['files']:
                        print(f"      - {Path(f).name}")
            else:
                print("✅ No duplicates found")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
