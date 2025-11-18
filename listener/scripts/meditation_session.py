#!/usr/bin/env python3
"""
Integrated Meditation Session Workflow

Complete workflow integrating all quick win features:
- Mood tracking (before/after)
- Session journaling
- Quick stats overview

Usage:
    # Before meditation
    python scripts/meditation_session.py --before

    # After meditation (with session file)
    python scripts/meditation_session.py --after --session data/sessions/session_20241118_001.h5

    # View recent progress
    python scripts/meditation_session.py --stats
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import MoodTracker, SessionJournal, MeditationAnalyzer


class MeditationSessionWorkflow:
    """
    Integrated workflow for complete meditation session.

    Combines mood tracking, journaling, and analysis.
    """

    def __init__(self):
        """Initialize all components."""
        self.mood_tracker = MoodTracker()
        self.journal = SessionJournal()
        self.analyzer = MeditationAnalyzer()

        print("\n" + "═" * 60)
        print("  🧘 THE LISTENER - Meditation Session")
        print("═" * 60 + "\n")

    def before_meditation(self):
        """
        Pre-meditation routine.

        Logs mood and optionally intention.
        """
        print("📋 Pre-Meditation Check-in")
        print("─" * 60 + "\n")

        # Get mood inputs
        print("Rate your current state (1-5):")
        print("  1 = Low/Poor, 5 = High/Excellent\n")

        try:
            stress = int(input("Stress (1=calm, 5=stressed): "))
            energy = int(input("Energy (1=tired, 5=energized): "))
            happiness = int(input("Happiness (1=sad, 5=happy): "))
            focus = int(input("Focus (1=scattered, 5=focused): "))

            # Validate
            if not all(1 <= x <= 5 for x in [stress, energy, happiness, focus]):
                print("❌ Values must be between 1-5")
                return

            # Optional notes
            print("\nOptional:")
            notes = input("Any notes? (press Enter to skip): ").strip()
            intention = input("Set intention for this session? (press Enter to skip): ").strip()

            # Log mood
            entry_id = self.mood_tracker.log_before(
                stress=stress,
                energy=energy,
                happiness=happiness,
                focus=focus,
                notes=notes
            )

            print(f"\n✅ Pre-meditation check-in complete")
            print(f"   Entry ID: {entry_id}")

            if intention:
                print(f"\n🎯 Intention set: {intention}")
                print("   (Add to journal after meditation)")

            print("\n" + "─" * 60)
            print("🧘 Begin your meditation practice...")
            print("   When finished, run:")
            print(f"   python scripts/meditation_session.py --after --session <session_file>")
            print("─" * 60 + "\n")

        except ValueError:
            print("❌ Please enter numbers 1-5")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled")

    def after_meditation(self, session_file: str = None):
        """
        Post-meditation routine.

        Logs mood, analyzes session, creates journal entry.

        Args:
            session_file: Path to session .h5 file (optional)
        """
        print("📝 Post-Meditation Reflection")
        print("─" * 60 + "\n")

        # Get mood inputs
        print("Rate your current state (1-5):\n")

        try:
            stress = int(input("Stress (1=calm, 5=stressed): "))
            energy = int(input("Energy (1=tired, 5=energized): "))
            happiness = int(input("Happiness (1=sad, 5=happy): "))
            focus = int(input("Focus (1=scattered, 5=focused): "))

            # Validate
            if not all(1 <= x <= 5 for x in [stress, energy, happiness, focus]):
                print("❌ Values must be between 1-5")
                return

            # Log mood after
            self.mood_tracker.log_after(
                stress=stress,
                energy=energy,
                happiness=happiness,
                focus=focus
            )

            # Analyze session if provided
            session_metrics = None
            if session_file:
                try:
                    print(f"\n📊 Analyzing session: {Path(session_file).name}")
                    features_df = pd.read_hdf(session_file, key='features')
                    session_metrics = self.analyzer.analyze_session(features_df)

                    print(f"\n   Meditation depth:    {session_metrics['mean_depth']:.1f}/100")
                    print(f"   Quality score:       {session_metrics['quality_score']:.1f}/100")
                    print(f"   Alpha performance:   {session_metrics.get('alpha_performance', 0):.2f}")

                    # Correlate with mood
                    self.mood_tracker.correlate_with_eeg(session_metrics)

                except Exception as e:
                    print(f"⚠️  Could not analyze session: {e}")

            # Journal entry
            print("\n📔 Add to journal? (optional)")
            add_journal = input("Add notes/insights? (y/n): ").strip().lower()

            if add_journal == 'y':
                print("\nJournal entry:")
                notes = input("  Notes: ").strip()
                insights = input("  Insights: ").strip()
                challenges = input("  Challenges: ").strip()
                intentions = input("  Intention (if set before): ").strip()
                tags_input = input("  Tags (comma-separated): ").strip()
                rating_input = input("  Rating (1-5): ").strip()

                tags = [t.strip() for t in tags_input.split(',')] if tags_input else []
                rating = int(rating_input) if rating_input and rating_input.isdigit() else None

                # Generate session ID
                session_id = Path(session_file).stem if session_file else datetime.now().strftime("session_%Y%m%d_%H%M%S")

                self.journal.add_entry(
                    session_id=session_id,
                    notes=notes,
                    insights=insights,
                    challenges=challenges,
                    intentions=intentions,
                    tags=tags,
                    rating=rating
                )

            print("\n" + "═" * 60)
            print("✨ Session complete! Well done.")
            print("═" * 60 + "\n")

        except ValueError:
            print("❌ Please enter valid numbers")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled")

    def show_stats(self, sessions_dir: str = "data/sessions", last_n: int = None):
        """
        Show quick stats overview.

        Args:
            sessions_dir: Directory with session files
            last_n: Only show last N sessions
        """
        from glob import glob
        import numpy as np

        print("📊 Quick Progress Overview")
        print("─" * 60 + "\n")

        # Find sessions
        session_files = sorted(glob(f"{sessions_dir}/*.h5"))

        if not session_files:
            print(f"❌ No sessions found in {sessions_dir}")
            return

        if last_n:
            session_files = session_files[-last_n:]

        # Analyze
        metrics_list = []
        for session_file in session_files:
            try:
                features_df = pd.read_hdf(session_file, key='features')
                metrics = self.analyzer.analyze_session(features_df)
                metrics_list.append(metrics)
            except Exception as e:
                pass

        if not metrics_list:
            print("❌ No valid sessions")
            return

        # Stats
        depths = [m['mean_depth'] for m in metrics_list]
        qualities = [m['quality_score'] for m in metrics_list]

        print(f"Total sessions:     {len(metrics_list)}")
        print(f"Average depth:      {np.mean(depths):.1f}/100")
        print(f"Average quality:    {np.mean(qualities):.1f}/100")
        print(f"Best depth:         {np.max(depths):.1f}/100")
        print()

        # Mood stats
        mood_stats = self.mood_tracker.get_statistics()
        if mood_stats:
            print("Mood tracking:")
            print(f"  Sessions tracked: {mood_stats['total_sessions']}")
            avg_changes = mood_stats.get('average_changes', {})
            if avg_changes:
                print("  Average improvements:")
                for metric, change in avg_changes.items():
                    symbol = '📈' if change > 0 else '📉' if change < 0 else '➡️'
                    print(f"    {metric.capitalize():12s}: {change:+.1f} {symbol}")

        print()

        # Journal summary
        self.journal.show_summary()

        print("─" * 60)
        print("For detailed analysis run:")
        print("  python scripts/quick_stats.py")
        print("─" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Integrated meditation session workflow")
    parser.add_argument("--before", action="store_true",
                       help="Pre-meditation check-in")
    parser.add_argument("--after", action="store_true",
                       help="Post-meditation reflection")
    parser.add_argument("--stats", action="store_true",
                       help="Show quick stats")
    parser.add_argument("--session", type=str,
                       help="Session file to analyze (for --after)")
    parser.add_argument("--sessions-dir", default="data/sessions",
                       help="Directory with session files")
    parser.add_argument("--last", type=int,
                       help="Only show last N sessions (for --stats)")

    args = parser.parse_args()

    workflow = MeditationSessionWorkflow()

    if args.before:
        workflow.before_meditation()

    elif args.after:
        workflow.after_meditation(args.session)

    elif args.stats:
        workflow.show_stats(args.sessions_dir, args.last)

    else:
        print("Usage:")
        print("  Before meditation:")
        print("    python scripts/meditation_session.py --before")
        print()
        print("  After meditation:")
        print("    python scripts/meditation_session.py --after --session data/sessions/session_001.h5")
        print()
        print("  View stats:")
        print("    python scripts/meditation_session.py --stats")
        print("    python scripts/meditation_session.py --stats --last 7")
        print()


if __name__ == "__main__":
    main()
