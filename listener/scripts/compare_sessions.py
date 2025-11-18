#!/usr/bin/env python3
"""
Session Comparison Tool - THE LISTENER

Compare two meditation sessions side-by-side.

Usage:
    # Compare by session ID
    python scripts/compare_sessions.py session_001 session_030

    # Compare with detailed analysis
    python scripts/compare_sessions.py session_001 session_030 --detailed

    # Compare and show latent space distance
    python scripts/compare_sessions.py session_001 session_030 --latent

    # Export comparison report
    python scripts/compare_sessions.py session_001 session_030 --export comparison.txt
"""

import sys
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.database.session_manager import SessionManager
from src.database.schema import Session


def load_session_data(session_id: str, db_manager: SessionManager) -> Optional[Dict]:
    """
    Load session from database with all data.

    Args:
        session_id: Session identifier
        db_manager: Database manager

    Returns:
        Dict with session data or None if not found
    """
    with db_manager.get_session() as session:
        db_session = session.query(Session).filter(
            Session.session_id == session_id
        ).first()

        if not db_session:
            return None

        # Load HDF5 data if available
        h5_path = Path(db_session.file_path) if db_session.file_path else None
        features_data = None
        eeg_data = None
        latent_data = None

        if h5_path and h5_path.exists():
            try:
                features_data = pd.read_hdf(h5_path, key='features')
            except (KeyError, IOError, OSError, ValueError) as e:
                # Key doesn't exist, file corrupted, or permission issue
                pass

            try:
                eeg_data = pd.read_hdf(h5_path, key='eeg_data')
            except (KeyError, IOError, OSError, ValueError) as e:
                pass

            try:
                latent_data = pd.read_hdf(h5_path, key='latent')
            except (KeyError, IOError, OSError, ValueError) as e:
                pass

        return {
            'session': db_session,
            'features': features_data,
            'eeg': eeg_data,
            'latent': latent_data
        }


def calculate_latent_distance(latent1: Optional[pd.DataFrame],
                               latent2: Optional[pd.DataFrame]) -> Optional[float]:
    """
    Calculate distance between latent representations.

    Args:
        latent1: First session latent vectors
        latent2: Second session latent vectors

    Returns:
        Mean Euclidean distance or None
    """
    if latent1 is None or latent2 is None:
        return None

    try:
        # Get mean latent vectors
        mean1 = latent1.mean(axis=0).values
        mean2 = latent2.mean(axis=0).values

        # Calculate Euclidean distance
        distance = np.linalg.norm(mean1 - mean2)
        return float(distance)
    except Exception as e:
        print(f"   Warning: Could not calculate latent distance: {e}")
        return None


def compare_features(features1: Optional[pd.DataFrame],
                     features2: Optional[pd.DataFrame]) -> Optional[Dict]:
    """
    Compare feature distributions between sessions.

    Args:
        features1: First session features
        features2: Second session features

    Returns:
        Dict with feature comparison stats
    """
    if features1 is None or features2 is None:
        return None

    try:
        # Find common columns
        common_cols = list(set(features1.columns) & set(features2.columns))

        if not common_cols:
            return None

        # Compare key features
        comparison = {}

        # Alpha power
        alpha_cols = [c for c in common_cols if 'alpha' in c.lower()]
        if alpha_cols:
            alpha1 = features1[alpha_cols].mean().mean()
            alpha2 = features2[alpha_cols].mean().mean()
            comparison['alpha_mean'] = (alpha1, alpha2, alpha2 - alpha1)

        # Beta power
        beta_cols = [c for c in common_cols if 'beta' in c.lower()]
        if beta_cols:
            beta1 = features1[beta_cols].mean().mean()
            beta2 = features2[beta_cols].mean().mean()
            comparison['beta_mean'] = (beta1, beta2, beta2 - beta1)

        # Theta power
        theta_cols = [c for c in common_cols if 'theta' in c.lower()]
        if theta_cols:
            theta1 = features1[theta_cols].mean().mean()
            theta2 = features2[theta_cols].mean().mean()
            comparison['theta_mean'] = (theta1, theta2, theta2 - theta1)

        return comparison
    except Exception as e:
        print(f"   Warning: Could not compare features: {e}")
        return None


def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_comparison_row(metric: str, val1, val2, unit: str = "", show_diff: bool = True):
    """Print a comparison row"""
    if isinstance(val1, float):
        s1 = f"{val1:.2f}"
        s2 = f"{val2:.2f}"
        if show_diff:
            diff = val2 - val1
            if diff > 0:
                arrow = "↑"
                sign = "+"
            elif diff < 0:
                arrow = "↓"
                sign = ""
            else:
                arrow = "→"
                sign = " "
            diff_str = f"  {arrow} {sign}{diff:.2f} {unit}"
        else:
            diff_str = ""
    else:
        s1 = str(val1)
        s2 = str(val2)
        diff_str = ""

    print(f"{metric:<25} {s1:>12} {unit:<8} │ {s2:>12} {unit:<8} {diff_str}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare two meditation sessions"
    )
    parser.add_argument(
        "session1",
        help="First session ID"
    )
    parser.add_argument(
        "session2",
        help="Second session ID"
    )
    parser.add_argument(
        "--database",
        default=config.database_url,
        help="Database URL"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed feature comparison"
    )
    parser.add_argument(
        "--latent",
        action="store_true",
        help="Calculate latent space distance (requires VAE)"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export comparison to text file"
    )

    args = parser.parse_args()

    # Validate sessions are different
    if args.session1 == args.session2:
        print("\n❌ Cannot compare a session to itself")
        print(f"   Both arguments are: {args.session1}")
        print("\nUsage: compare_sessions.py <session_id_1> <session_id_2>")
        sys.exit(1)

    # Redirect output if exporting
    if args.export:
        original_stdout = sys.stdout
        sys.stdout = open(args.export, 'w')

    try:
        # Connect to database
        db_manager = SessionManager(args.database)

        print("\n" + "=" * 70)
        print("  📊 THE LISTENER - Session Comparison")
        print("=" * 70)
        print(f"\n  Session 1: {args.session1}")
        print(f"  Session 2: {args.session2}")

        # Load sessions
        print("\n🔍 Loading sessions...")
        data1 = load_session_data(args.session1, db_manager)
        data2 = load_session_data(args.session2, db_manager)

        if not data1:
            print(f"\n❌ Session not found: {args.session1}")
            sys.exit(1)

        if not data2:
            print(f"\n❌ Session not found: {args.session2}")
            sys.exit(1)

        s1 = data1['session']
        s2 = data2['session']

        print("✅ Both sessions loaded")

        # Basic Information
        print_header("Basic Information")
        print(f"\n{'Metric':<25} {'Session 1':>12} {'Unit':<8} │ {'Session 2':>12} {'Unit':<8} {'Change'}")
        print("-" * 70)

        # Date
        date1 = s1.recorded_at.strftime("%Y-%m-%d %H:%M") if s1.recorded_at else "Unknown"
        date2 = s2.recorded_at.strftime("%Y-%m-%d %H:%M") if s2.recorded_at else "Unknown"
        print(f"{'Date':<25} {date1:>12} {'':<8} │ {date2:>12} {'':<8}")

        # Duration
        print_comparison_row("Duration", s1.duration_seconds or 0, s2.duration_seconds or 0, "sec")

        # Session Metrics
        print_header("Meditation Metrics")
        print(f"\n{'Metric':<25} {'Session 1':>12} {'Unit':<8} │ {'Session 2':>12} {'Unit':<8} {'Change'}")
        print("-" * 70)

        # Depth scores
        if s1.mean_depth is not None and s2.mean_depth is not None:
            print_comparison_row("Mean Depth", s1.mean_depth, s2.mean_depth, "/100")

        if s1.max_depth is not None and s2.max_depth is not None:
            print_comparison_row("Max Depth", s1.max_depth, s2.max_depth, "/100")

        # Quality
        if s1.quality_score is not None and s2.quality_score is not None:
            print_comparison_row("Quality Score", s1.quality_score, s2.quality_score, "/100")

        # Interpretation
        print_header("Interpretation")

        # Depth analysis
        if s1.mean_depth is not None and s2.mean_depth is not None:
            depth_change = s2.mean_depth - s1.mean_depth

            if depth_change > 10:
                print("\n🎉 Significant improvement in meditation depth!")
                print(f"   Your meditation depth increased by {depth_change:.1f} points.")
            elif depth_change > 5:
                print("\n✅ Good progress in meditation depth.")
                print(f"   Your meditation depth increased by {depth_change:.1f} points.")
            elif depth_change > -5:
                print("\n→  Meditation depth remained stable.")
                print(f"   Change: {depth_change:+.1f} points.")
            elif depth_change > -10:
                print("\n⚠️  Slight decrease in meditation depth.")
                print(f"   Your meditation depth decreased by {abs(depth_change):.1f} points.")
            else:
                print("\n⚠️  Significant decrease in meditation depth.")
                print(f"   Your meditation depth decreased by {abs(depth_change):.1f} points.")

        # Quality analysis
        if s1.quality_score is not None and s2.quality_score is not None:
            quality_change = s2.quality_score - s1.quality_score

            if quality_change > 10:
                print("\n✨ Signal quality improved significantly.")
            elif quality_change < -10:
                print("\n⚠️  Signal quality decreased. Check headband fit.")

        # Detailed feature comparison
        if args.detailed:
            print_header("Detailed Feature Comparison")

            feature_comp = compare_features(data1['features'], data2['features'])

            if feature_comp:
                print(f"\n{'Band':<15} {'Session 1':>12} {'Session 2':>12} {'Change':>12}")
                print("-" * 55)

                if 'alpha_mean' in feature_comp:
                    v1, v2, diff = feature_comp['alpha_mean']
                    print(f"{'Alpha':<15} {v1:>12.4f} {v2:>12.4f} {diff:>+12.4f}")

                if 'beta_mean' in feature_comp:
                    v1, v2, diff = feature_comp['beta_mean']
                    print(f"{'Beta':<15} {v1:>12.4f} {v2:>12.4f} {diff:>+12.4f}")

                if 'theta_mean' in feature_comp:
                    v1, v2, diff = feature_comp['theta_mean']
                    print(f"{'Theta':<15} {v1:>12.4f} {v2:>12.4f} {diff:>+12.4f}")

                # Band interpretation
                if 'alpha_mean' in feature_comp and 'beta_mean' in feature_comp:
                    alpha_diff = feature_comp['alpha_mean'][2]
                    beta_diff = feature_comp['beta_mean'][2]

                    print("\nBand Analysis:")
                    if alpha_diff > 0 and beta_diff < 0:
                        print("  ✅ Ideal pattern: Alpha increased, Beta decreased")
                        print("     This indicates deeper relaxation and reduced mental chatter.")
                    elif alpha_diff > 0:
                        print("  ✅ Alpha increased - good relaxation")
                    elif beta_diff < 0:
                        print("  ✅ Beta decreased - reduced mental activity")
            else:
                print("\n⚠️  Feature data not available for comparison")

        # Latent space distance
        if args.latent:
            print_header("Latent Space Analysis")

            distance = calculate_latent_distance(data1['latent'], data2['latent'])

            if distance is not None:
                print(f"\nLatent Space Distance: {distance:.4f}")

                if distance < 1.0:
                    print("  → Very similar meditation states")
                elif distance < 3.0:
                    print("  → Similar meditation states")
                elif distance < 5.0:
                    print("  → Moderately different meditation states")
                else:
                    print("  → Very different meditation states")

                print("\nInterpretation:")
                print("  Lower distance = more similar brain states during meditation")
                print("  Higher distance = exploring new meditation territories")
            else:
                print("\n⚠️  Latent data not available for comparison")
                print("   Run sessions through VAE first with scripts/generate_exports.py")

        # Time between sessions
        if s1.recorded_at and s2.recorded_at:
            time_diff = abs((s2.recorded_at - s1.recorded_at).days)
            print_header("Timeline")
            print(f"\nTime between sessions: {time_diff} days")

            if time_diff == 0:
                print("  Same day comparison")
            elif time_diff <= 7:
                print("  Short-term comparison (within 1 week)")
            elif time_diff <= 30:
                print("  Medium-term comparison (within 1 month)")
            else:
                print(f"  Long-term comparison ({time_diff // 30} months)")

        # Summary
        print_header("Summary")

        improvements = []
        regressions = []

        if s1.mean_depth is not None and s2.mean_depth is not None:
            if s2.mean_depth > s1.mean_depth + 5:
                improvements.append("meditation depth")
            elif s2.mean_depth < s1.mean_depth - 5:
                regressions.append("meditation depth")

        if s1.quality_score is not None and s2.quality_score is not None:
            if s2.quality_score > s1.quality_score + 10:
                improvements.append("signal quality")
            elif s2.quality_score < s1.quality_score - 10:
                regressions.append("signal quality")

        if improvements:
            print(f"\n✅ Improvements: {', '.join(improvements)}")

        if regressions:
            print(f"\n⚠️  Regressions: {', '.join(regressions)}")

        if not improvements and not regressions:
            print("\n→  Overall performance remained stable between sessions")

        print("\n" + "=" * 70 + "\n")

    finally:
        # Restore stdout if exporting
        if args.export:
            sys.stdout.close()
            sys.stdout = original_stdout
            print(f"\n✅ Comparison exported to: {args.export}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
        sys.exit(0)
