"""
Session Journaling for THE LISTENER

Add notes, reflections, and observations to meditation sessions.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List


class SessionJournal:
    """
    Add journal entries to meditation sessions.

    Usage:
        journal = SessionJournal()

        # Add entry
        journal.add_entry(
            session_id="session_001",
            notes="Very deep session today. Mind was calm.",
            insights="Noticed breath awareness improves with time",
            challenges="Itchy nose for first 5 minutes",
            tags=["deep", "calm", "morning"]
        )

        # View entry
        entry = journal.get_entry("session_001")

        # Search by tag
        sessions = journal.find_by_tag("deep")
    """

    def __init__(self, journal_file: str = "data/session_journal.json"):
        """
        Initialize session journal.

        Args:
            journal_file: Path to journal file
        """
        self.journal_file = Path(journal_file)
        self.journal_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing journal
        self.entries = self._load_journal()

        print(f"📔 Session Journal initialized")
        print(f"   Entries: {len(self.entries)}")

    def _load_journal(self) -> Dict:
        """Load journal from file."""
        if self.journal_file.exists():
            with open(self.journal_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_journal(self):
        """Save journal to file."""
        with open(self.journal_file, 'w') as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def add_entry(
        self,
        session_id: str,
        notes: str = "",
        insights: str = "",
        challenges: str = "",
        intentions: str = "",
        tags: Optional[List[str]] = None,
        rating: Optional[int] = None
    ):
        """
        Add or update journal entry for session.

        Args:
            session_id: Session identifier
            notes: General notes/observations
            insights: Insights or realizations
            challenges: Difficulties encountered
            intentions: Intention set before meditation
            tags: List of tags (e.g., ["deep", "calm", "morning"])
            rating: Subjective rating 1-5
        """
        entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "insights": insights,
            "challenges": challenges,
            "intentions": intentions,
            "tags": tags or [],
            "rating": rating
        }

        self.entries[session_id] = entry
        self._save_journal()

        print(f"\n📝 Journal entry added: {session_id}")
        if notes:
            print(f"   Notes: {notes[:60]}...")
        if tags:
            print(f"   Tags: {', '.join(tags)}")
        if rating:
            print(f"   Rating: {'⭐' * rating}")

    def get_entry(self, session_id: str) -> Optional[Dict]:
        """Get journal entry for session."""
        return self.entries.get(session_id)

    def find_by_tag(self, tag: str) -> List[Dict]:
        """Find all sessions with specific tag."""
        return [
            entry for entry in self.entries.values()
            if tag in entry.get('tags', [])
        ]

    def find_by_rating(self, min_rating: int = 4) -> List[Dict]:
        """Find sessions with high ratings."""
        return [
            entry for entry in self.entries.values()
            if entry.get('rating', 0) >= min_rating
        ]

    def get_insights_summary(self) -> List[str]:
        """Get all insights collected."""
        insights = []
        for entry in self.entries.values():
            if entry.get('insights'):
                insights.append(f"{entry['session_id']}: {entry['insights']}")
        return insights

    def export_to_markdown(self, output_file: str = "meditation_journal.md"):
        """
        Export journal to markdown file.

        Args:
            output_file: Output markdown file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Meditation Journal\n\n")
            f.write(f"**Total entries:** {len(self.entries)}\n\n")
            f.write("---\n\n")

            # Sort by date
            sorted_entries = sorted(
                self.entries.values(),
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )

            for entry in sorted_entries:
                f.write(f"## {entry['session_id']}\n\n")
                f.write(f"**Date:** {entry['timestamp'][:10]}\n\n")

                if entry.get('rating'):
                    f.write(f"**Rating:** {'⭐' * entry['rating']}\n\n")

                if entry.get('tags'):
                    f.write(f"**Tags:** {', '.join(entry['tags'])}\n\n")

                if entry.get('intentions'):
                    f.write(f"**Intention:** {entry['intentions']}\n\n")

                if entry.get('notes'):
                    f.write(f"**Notes:**\n{entry['notes']}\n\n")

                if entry.get('insights'):
                    f.write(f"**Insights:**\n{entry['insights']}\n\n")

                if entry.get('challenges'):
                    f.write(f"**Challenges:**\n{entry['challenges']}\n\n")

                f.write("---\n\n")

        print(f"📄 Journal exported to: {output_file}")

    def show_summary(self):
        """Show journal summary."""
        print(f"\n📔 Journal Summary")
        print(f"{'─' * 60}")
        print(f"Total entries: {len(self.entries)}")

        # Count tags
        all_tags = []
        for entry in self.entries.values():
            all_tags.extend(entry.get('tags', []))

        if all_tags:
            from collections import Counter
            tag_counts = Counter(all_tags)
            print(f"\nMost common tags:")
            for tag, count in tag_counts.most_common(5):
                print(f"  {tag}: {count}")

        # Average rating
        ratings = [e.get('rating', 0) for e in self.entries.values() if e.get('rating')]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"\nAverage rating: {'⭐' * int(avg_rating)} ({avg_rating:.1f}/5)")

        print(f"{'─' * 60}\n")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Session journaling")
    parser.add_argument("--session", help="Session ID")
    parser.add_argument("--notes", help="Notes")
    parser.add_argument("--insights", help="Insights")
    parser.add_argument("--challenges", help="Challenges")
    parser.add_argument("--tags", help="Tags (comma-separated)")
    parser.add_argument("--rating", type=int, choices=[1,2,3,4,5], help="Rating 1-5")
    parser.add_argument("--view", help="View entry for session")
    parser.add_argument("--tag", help="Find sessions by tag")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--export", help="Export to markdown file")

    args = parser.parse_args()

    journal = SessionJournal()

    if args.summary:
        journal.show_summary()

    elif args.export:
        journal.export_to_markdown(args.export)

    elif args.view:
        entry = journal.get_entry(args.view)
        if entry:
            print(f"\n📝 {args.view}")
            print(f"{'─' * 60}")
            for key, value in entry.items():
                if value and key != 'session_id':
                    print(f"{key.capitalize()}: {value}")
        else:
            print(f"❌ No entry found for {args.view}")

    elif args.tag:
        entries = journal.find_by_tag(args.tag)
        print(f"\n🏷️  Sessions tagged '{args.tag}': {len(entries)}")
        for entry in entries:
            print(f"  - {entry['session_id']}")

    elif args.session:
        tags = args.tags.split(',') if args.tags else None
        journal.add_entry(
            session_id=args.session,
            notes=args.notes or "",
            insights=args.insights or "",
            challenges=args.challenges or "",
            tags=tags,
            rating=args.rating
        )

    else:
        print("Usage:")
        print("  python session_journal.py --session session_001 --notes 'Deep session' --rating 5")
        print("  python session_journal.py --view session_001")
        print("  python session_journal.py --tag deep")
        print("  python session_journal.py --summary")
        print("  python session_journal.py --export journal.md")
