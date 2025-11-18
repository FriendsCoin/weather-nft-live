#!/usr/bin/env python3
"""
Quick Stats - One-command overview of meditation progress

Usage:
    python scripts/quick_stats.py
    python scripts/quick_stats.py --sessions-dir data/sessions
    python scripts/quick_stats.py --last 7  # Last 7 sessions
"""

import sys
from pathlib import Path
from glob import glob
from typing import List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.meditation_analysis import MeditationAnalyzer
import argparse


def print_header():
    """Print colorful header."""
    print("\n" + "═" * 60)
    print("  🧘 THE LISTENER - Quick Stats")
    print("═" * 60 + "\n")


def quick_overview(sessions_dir: str, last_n: int = None):
    """
    Show quick overview of meditation progress.

    Args:
        sessions_dir: Directory with session files
        last_n: Only show last N sessions
    """
    print_header()

    # Find all sessions
    session_files = sorted(glob(f"{sessions_dir}/*.h5"))

    if not session_files:
        print(f"❌ No sessions found in {sessions_dir}")
        return

    if last_n:
        session_files = session_files[-last_n:]

    total_sessions = len(session_files)

    print(f"📊 Overview")
    print(f"{'─' * 60}")
    print(f"Total sessions:  {total_sessions}")
    print(f"Date range:      {Path(session_files[0]).stem} → {Path(session_files[-1]).stem}")
    print()

    # Analyze all sessions (quick version)
    analyzer = MeditationAnalyzer()
    metrics_list = []

    print("📈 Progress")
    print(f"{'─' * 60}")

    for i, session_file in enumerate(session_files):
        try:
            features_df = pd.read_hdf(session_file, key='features')
            metrics = analyzer.analyze_session(features_df)
            metrics_list.append(metrics)
        except Exception as e:
            print(f"⚠️  Skipped {session_file}: {e}")

    if not metrics_list:
        print("❌ No valid sessions")
        return

    # Compute statistics
    depths = [m['mean_depth'] for m in metrics_list]
    qualities = [m['quality_score'] for m in metrics_list]
    alpha_perfs = [m.get('alpha_performance', 0) for m in metrics_list]

    mean_depth = np.mean(depths)
    mean_quality = np.mean(qualities)
    mean_alpha_perf = np.mean(alpha_perfs)

    # Trends
    if len(depths) > 1:
        depth_trend = np.polyfit(range(len(depths)), depths, 1)[0]
        quality_trend = np.polyfit(range(len(qualities)), qualities, 1)[0]
    else:
        depth_trend = 0
        quality_trend = 0

    # Display
    print(f"Average depth:      {mean_depth:.1f}/100  {_trend_symbol(depth_trend)}")
    print(f"Average quality:    {mean_quality:.1f}/100  {_trend_symbol(quality_trend)}")
    print(f"Alpha performance:  {mean_alpha_perf:.2f}")
    print()

    # Best/Worst sessions
    print("🌟 Best Sessions")
    print(f"{'─' * 60}")

    best_idx = np.argmax(depths)
    print(f"Deepest:  Session {best_idx + 1} - {depths[best_idx]:.1f} depth")

    best_quality_idx = np.argmax(qualities)
    print(f"Quality:  Session {best_quality_idx + 1} - {qualities[best_quality_idx]:.1f} quality")
    print()

    # Recent trend
    if len(depths) >= 5:
        recent_depths = depths[-5:]
        recent_avg = np.mean(recent_depths)
        overall_avg = np.mean(depths[:-5]) if len(depths) > 5 else mean_depth

        print("📅 Recent Performance (last 5 sessions)")
        print(f"{'─' * 60}")
        print(f"Recent average:   {recent_avg:.1f}")
        print(f"Overall average:  {overall_avg:.1f}")

        if recent_avg > overall_avg + 5:
            print("✨ You're improving! Recent sessions are better")
        elif recent_avg < overall_avg - 5:
            print("🤔 Recent dip. Consider rest or different approach")
        else:
            print("😌 Maintaining consistent practice")
        print()

    # Learning stage
    print("🎯 Learning Stage")
    print(f"{'─' * 60}")

    if total_sessions < 5:
        stage = "🌱 Beginner - Building foundation"
        advice = "Focus on consistency. Aim for daily practice."
    elif total_sessions < 20:
        stage = "🌿 Developing - Learning patterns"
        advice = "Notice what works. Track mood before/after."
    elif total_sessions < 50:
        stage = "🌳 Intermediate - Deepening practice"
        advice = "Experiment with duration and techniques."
    else:
        stage = "🏔️  Advanced - Established practice"
        advice = "Refine and explore subtle states."

    print(stage)
    print(f"💡 {advice}")
    print()

    # Quick recommendations
    print("💪 Recommendations")
    print(f"{'─' * 60}")

    if mean_alpha_perf < 1.0:
        print("• Work on relaxation - alpha performance is low")

    if mean_depth < 30:
        print("• Try longer sessions (15-20 min)")

    if depth_trend < 0:
        print("• Consider rest day - may be overtraining")

    if total_sessions < 10:
        print("• Keep going! Brain needs ~10 sessions to adapt")

    # Consistency check
    if len(session_files) >= 7:
        # Check if sessions are regular
        dates = [datetime.strptime(Path(f).stem.split('_')[1], '%Y%m%d')
                for f in session_files if '_' in Path(f).stem]

        if dates:
            gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_gap = np.mean(gaps) if gaps else 0

            if avg_gap <= 1.5:
                print("✅ Excellent consistency! Daily practice is key")
            elif avg_gap <= 3:
                print("✨ Good consistency. Try for daily practice")
            else:
                print("🎯 Aim for more regular practice. Consistency > intensity")

    print()
    print("═" * 60)
    print("Run 'python scripts/analyze_meditation.py --sessions-dir data/sessions --plot'")
    print("for detailed analysis and visualizations")
    print("═" * 60 + "\n")


def _trend_symbol(trend: float) -> str:
    """Get trend symbol."""
    if trend > 0.5:
        return "📈 Improving"
    elif trend < -0.5:
        return "📉 Declining"
    else:
        return "➡️  Stable"


def compare_sessions(session1: str, session2: str):
    """
    Compare two sessions side by side.

    Args:
        session1: Path to first session
        session2: Path to second session
    """
    print_header()
    print("🔄 Session Comparison\n")

    analyzer = MeditationAnalyzer()

    # Analyze both
    try:
        features1 = pd.read_hdf(session1, key='features')
        metrics1 = analyzer.analyze_session(features1)

        features2 = pd.read_hdf(session2, key='features')
        metrics2 = analyzer.analyze_session(features2)
    except Exception as e:
        print(f"❌ Error loading sessions: {e}")
        return

    # Compare
    print(f"Session 1: {Path(session1).name}")
    print(f"Session 2: {Path(session2).name}")
    print()

    comparison_metrics = [
        ('mean_depth', 'Meditation Depth'),
        ('quality_score', 'Quality Score'),
        ('alpha_performance', 'Alpha Performance'),
        ('beta_performance', 'Beta Performance'),
        ('alpha_beta_ratio', 'Alpha/Beta Ratio'),
    ]

    for key, label in comparison_metrics:
        val1 = metrics1.get(key, 0)
        val2 = metrics2.get(key, 0)
        diff = val2 - val1

        symbol = '↗' if diff > 0 else '↘' if diff < 0 else '→'
        color = '🟢' if diff > 0 else '🔴' if diff < 0 else '🟡'

        print(f"{label:20s}: {val1:6.2f} → {val2:6.2f}  {symbol} {color} ({diff:+.2f})")

    print()

    # Interpretation
    if metrics2['mean_depth'] > metrics1['mean_depth'] + 5:
        print("✨ Session 2 was significantly deeper!")
    elif metrics2['mean_depth'] < metrics1['mean_depth'] - 5:
        print("🤔 Session 1 was deeper. What was different?")
    else:
        print("😌 Similar depth in both sessions")

    print()


def main():
    parser = argparse.ArgumentParser(description="Quick meditation stats")
    parser.add_argument("--sessions-dir", default="data/sessions",
                       help="Directory with session files")
    parser.add_argument("--last", type=int, help="Only show last N sessions")
    parser.add_argument("--compare", nargs=2, metavar=('SESSION1', 'SESSION2'),
                       help="Compare two sessions")

    args = parser.parse_args()

    if args.compare:
        compare_sessions(args.compare[0], args.compare[1])
    else:
        quick_overview(args.sessions_dir, args.last)


if __name__ == "__main__":
    main()
