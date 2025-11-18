"""
Emotion and Mood Tracking for THE LISTENER

Log subjective emotional state before/after meditation
to correlate with objective EEG metrics.

Based on research showing meditation impacts:
- Stress levels
- Energy
- Mood/happiness
- Focus
- Anxiety
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd
import numpy as np


class MoodTracker:
    """
    Track emotional state before/after meditation sessions.

    Provides correlation analysis between subjective mood
    and objective EEG metrics.

    Usage:
        tracker = MoodTracker()

        # Before meditation
        tracker.log_before(
            stress=4,
            energy=2,
            happiness=3,
            focus=2,
            notes="Tough day at work"
        )

        # After meditation (auto-links to before entry)
        tracker.log_after(
            stress=2,
            energy=4,
            happiness=4,
            focus=4,
            notes="Feeling much calmer"
        )

        # Analyze
        tracker.show_changes()
        tracker.correlate_with_eeg(session_metrics)
    """

    def __init__(self, data_dir: str = "data/mood_logs"):
        """
        Initialize mood tracker.

        Args:
            data_dir: Directory to store mood logs
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / "mood_log.json"

        # Load existing logs
        self.logs = self._load_logs()

        print("🎭 Mood Tracker initialized")
        print(f"   Logs: {len(self.logs)} entries")

    def _load_logs(self) -> List[Dict]:
        """Load mood logs from file."""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_logs(self):
        """Save mood logs to file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)

    def log_before(
        self,
        stress: int,
        energy: int,
        happiness: int,
        focus: int,
        anxiety: Optional[int] = None,
        notes: str = ""
    ) -> str:
        """
        Log mood BEFORE meditation.

        Args:
            stress: 1-5 scale (1=calm, 5=very stressed)
            energy: 1-5 scale (1=exhausted, 5=energized)
            happiness: 1-5 scale (1=sad, 5=very happy)
            focus: 1-5 scale (1=scattered, 5=focused)
            anxiety: 1-5 scale (optional)
            notes: Free text notes

        Returns:
            Entry ID
        """
        entry_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        entry = {
            "id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "type": "before",
            "stress": stress,
            "energy": energy,
            "happiness": happiness,
            "focus": focus,
            "anxiety": anxiety,
            "notes": notes
        }

        self.logs.append(entry)
        self._save_logs()

        print(f"\n📝 Mood logged (before meditation)")
        print(f"   Stress:    {self._bar(stress)}")
        print(f"   Energy:    {self._bar(energy)}")
        print(f"   Happiness: {self._bar(happiness)}")
        print(f"   Focus:     {self._bar(focus)}")
        if notes:
            print(f"   Notes: {notes}")

        return entry_id

    def log_after(
        self,
        stress: int,
        energy: int,
        happiness: int,
        focus: int,
        anxiety: Optional[int] = None,
        notes: str = "",
        session_id: Optional[str] = None
    ):
        """
        Log mood AFTER meditation.

        Automatically links to most recent 'before' entry.

        Args:
            stress: 1-5 scale
            energy: 1-5 scale
            happiness: 1-5 scale
            focus: 1-5 scale
            anxiety: 1-5 scale (optional)
            notes: Free text notes
            session_id: Link to specific session (optional)
        """
        # Find most recent 'before' entry
        before_entry = None
        for entry in reversed(self.logs):
            if entry['type'] == 'before':
                before_entry = entry
                break

        entry = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "type": "after",
            "stress": stress,
            "energy": energy,
            "happiness": happiness,
            "focus": focus,
            "anxiety": anxiety,
            "notes": notes,
            "session_id": session_id,
            "before_id": before_entry['id'] if before_entry else None
        }

        self.logs.append(entry)
        self._save_logs()

        # Show changes
        if before_entry:
            self.show_changes(before_entry, entry)
        else:
            print("\n📝 Mood logged (after meditation)")
            print(f"   Stress:    {self._bar(stress)}")
            print(f"   Energy:    {self._bar(energy)}")
            print(f"   Happiness: {self._bar(happiness)}")
            print(f"   Focus:     {self._bar(focus)}")

    def show_changes(self, before: Optional[Dict] = None, after: Optional[Dict] = None):
        """
        Show mood changes from before to after.

        Args:
            before: Before entry (or use most recent)
            after: After entry (or use most recent)
        """
        if before is None or after is None:
            # Find most recent pair
            for i in range(len(self.logs) - 1, 0, -1):
                if self.logs[i]['type'] == 'after':
                    after = self.logs[i]
                    # Find linked before
                    before_id = after.get('before_id')
                    if before_id:
                        before = next((e for e in self.logs if e['id'] == before_id), None)
                    break

        if not before or not after:
            print("⚠️  No mood pair found")
            return

        print(f"\n🎭 Mood Changes")
        print(f"{'─' * 50}")

        metrics = ['stress', 'energy', 'happiness', 'focus']
        for metric in metrics:
            b = before.get(metric, 0)
            a = after.get(metric, 0)
            change = a - b

            # Stress is inverse (lower is better)
            if metric == 'stress':
                change = -change

            symbol = '↗' if change > 0 else '↘' if change < 0 else '→'
            color = '🟢' if change > 0 else '🔴' if change < 0 else '🟡'

            print(f"{metric.capitalize():12s}: {self._bar(b)} → {self._bar(a)} {symbol} {color}")
            print(f"              Change: {change:+d}")

        print(f"{'─' * 50}")

        # Overall assessment
        total_improvement = sum([
            -(after.get('stress', 0) - before.get('stress', 0)),
            after.get('energy', 0) - before.get('energy', 0),
            after.get('happiness', 0) - before.get('happiness', 0),
            after.get('focus', 0) - before.get('focus', 0)
        ])

        if total_improvement > 3:
            assessment = "🌟 Excellent meditation! Major mood improvement"
        elif total_improvement > 0:
            assessment = "✨ Good meditation. Positive changes"
        elif total_improvement == 0:
            assessment = "😌 Neutral meditation. Maintained baseline"
        else:
            assessment = "🤔 Challenging session. Consider shorter practice"

        print(f"\n{assessment}")
        print()

    def _bar(self, value: int, max_val: int = 5) -> str:
        """Create visual bar for value."""
        filled = '█' * value
        empty = '░' * (max_val - value)
        return f"{filled}{empty} ({value}/{max_val})"

    def get_statistics(self) -> Dict:
        """
        Get mood tracking statistics.

        Returns:
            Dict with statistics
        """
        if not self.logs:
            return {}

        # Separate before/after
        befores = [e for e in self.logs if e['type'] == 'before']
        afters = [e for e in self.logs if e['type'] == 'after']

        # Compute average changes
        changes = {
            'stress': [],
            'energy': [],
            'happiness': [],
            'focus': []
        }

        for after in afters:
            before_id = after.get('before_id')
            if before_id:
                before = next((e for e in befores if e['id'] == before_id), None)
                if before:
                    for metric in changes.keys():
                        b = before.get(metric, 0)
                        a = after.get(metric, 0)
                        # Stress is inverse
                        if metric == 'stress':
                            changes[metric].append(b - a)
                        else:
                            changes[metric].append(a - b)

        stats = {
            'total_sessions': len(afters),
            'average_changes': {
                metric: np.mean(vals) if vals else 0
                for metric, vals in changes.items()
            },
            'best_improvement': max(
                (sum(vals) for vals in changes.values() if vals),
                default=0
            )
        }

        return stats

    def correlate_with_eeg(self, session_metrics: Dict) -> Dict:
        """
        Correlate mood changes with EEG metrics.

        Args:
            session_metrics: Dict from analyze_session()

        Returns:
            Correlation results
        """
        # Find most recent mood pair
        after = None
        before = None

        for i in range(len(self.logs) - 1, 0, -1):
            if self.logs[i]['type'] == 'after':
                after = self.logs[i]
                before_id = after.get('before_id')
                if before_id:
                    before = next((e for e in self.logs if e['id'] == before_id), None)
                break

        if not before or not after:
            print("⚠️  No mood pair found for correlation")
            return {}

        # Compute mood improvement
        mood_improvement = sum([
            -(after.get('stress', 0) - before.get('stress', 0)),
            after.get('energy', 0) - before.get('energy', 0),
            after.get('happiness', 0) - before.get('happiness', 0),
            after.get('focus', 0) - before.get('focus', 0)
        ])

        # Correlate with EEG
        correlations = {
            'mood_improvement': mood_improvement,
            'meditation_depth': session_metrics.get('mean_depth', 0),
            'alpha_performance': session_metrics.get('alpha_performance', 0),
            'quality_score': session_metrics.get('quality_score', 0)
        }

        print(f"\n🔗 Mood-EEG Correlation")
        print(f"{'─' * 50}")
        print(f"Mood improvement:    {mood_improvement:+d}")
        print(f"Meditation depth:    {correlations['meditation_depth']:.1f}/100")
        print(f"Alpha performance:   {correlations['alpha_performance']:.2f}")
        print(f"Quality score:       {correlations['quality_score']:.1f}/100")
        print(f"{'─' * 50}")

        # Interpretation
        if mood_improvement > 0 and correlations['meditation_depth'] > 50:
            print("✅ Strong positive correlation: deep meditation → better mood")
        elif mood_improvement > 0:
            print("✨ Mood improved despite moderate meditation depth")
        else:
            print("🤔 Limited mood improvement. Try different approach?")

        return correlations

    def export_to_csv(self, output_path: str = "mood_log.csv"):
        """Export mood logs to CSV."""
        df = pd.DataFrame(self.logs)
        df.to_csv(output_path, index=False)
        print(f"💾 Mood logs exported: {output_path}")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Track mood before/after meditation")
    parser.add_argument("--before", action="store_true", help="Log before meditation")
    parser.add_argument("--after", action="store_true", help="Log after meditation")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--stress", type=int, help="Stress level (1-5)")
    parser.add_argument("--energy", type=int, help="Energy level (1-5)")
    parser.add_argument("--happiness", type=int, help="Happiness level (1-5)")
    parser.add_argument("--focus", type=int, help="Focus level (1-5)")
    parser.add_argument("--notes", type=str, default="", help="Notes")

    args = parser.parse_args()

    tracker = MoodTracker()

    if args.stats:
        stats = tracker.get_statistics()
        print(f"\n📊 Mood Tracking Statistics")
        print(f"   Total sessions: {stats.get('total_sessions', 0)}")
        print(f"\n   Average changes:")
        for metric, change in stats.get('average_changes', {}).items():
            print(f"   {metric.capitalize():12s}: {change:+.1f}")

    elif args.before:
        if not all([args.stress, args.energy, args.happiness, args.focus]):
            print("❌ Please provide all mood values: --stress --energy --happiness --focus")
        else:
            tracker.log_before(
                stress=args.stress,
                energy=args.energy,
                happiness=args.happiness,
                focus=args.focus,
                notes=args.notes
            )

    elif args.after:
        if not all([args.stress, args.energy, args.happiness, args.focus]):
            print("❌ Please provide all mood values: --stress --energy --happiness --focus")
        else:
            tracker.log_after(
                stress=args.stress,
                energy=args.energy,
                happiness=args.happiness,
                focus=args.focus,
                notes=args.notes
            )

    else:
        print("Usage:")
        print("  python mood_tracker.py --before --stress 4 --energy 2 --happiness 3 --focus 2")
        print("  python mood_tracker.py --after --stress 2 --energy 4 --happiness 4 --focus 4")
        print("  python mood_tracker.py --stats")
