#!/usr/bin/env python3
"""
Generate Exports for THE LISTENER

Creates comprehensive exports:
- PDF reports with charts
- Video compilations
- Data exports (CSV, JSON, R, MATLAB)
- Complete archive backup

Usage:
    # Generate all exports
    python scripts/generate_exports.py --all

    # Generate specific exports
    python scripts/generate_exports.py --report --video
    python scripts/generate_exports.py --csv --json

    # Specify time range
    python scripts/generate_exports.py --all --days 30
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionManager, QueryBuilder
from src.utils import ReportGenerator, VideoCompiler, DataExporter
from glob import glob


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive exports for THE LISTENER"
    )

    # Export types
    parser.add_argument("--all", action="store_true",
                       help="Generate all exports")
    parser.add_argument("--report", action="store_true",
                       help="Generate PDF report")
    parser.add_argument("--video", action="store_true",
                       help="Generate video compilation")
    parser.add_argument("--csv", action="store_true",
                       help="Export to CSV")
    parser.add_argument("--json", action="store_true",
                       help="Export to JSON")
    parser.add_argument("--stats", action="store_true",
                       help="Export statistics")
    parser.add_argument("--archive", action="store_true",
                       help="Create complete archive")
    parser.add_argument("--r", action="store_true",
                       help="Export for R analysis")
    parser.add_argument("--matlab", action="store_true",
                       help="Export for MATLAB analysis")

    # Options
    parser.add_argument("--days", type=int,
                       help="Last N days (default: all time)")
    parser.add_argument("--output-dir", default="exports",
                       help="Output directory (default: exports)")
    parser.add_argument("--database", default="sqlite:///data/listener.db",
                       help="Database URL")

    args = parser.parse_args()

    # If --all, enable all export types
    if args.all:
        args.report = True
        args.video = True
        args.csv = True
        args.json = True
        args.stats = True
        args.archive = True

    # If no export type specified, show help
    if not any([args.report, args.video, args.csv, args.json,
                args.stats, args.archive, args.r, args.matlab]):
        parser.print_help()
        return

    print("=" * 60)
    print("  📦 THE LISTENER - Export Generator")
    print("=" * 60)
    print()

    # Load sessions from database
    print("📊 Loading sessions from database...")
    manager = SessionManager(args.database)

    with manager.session_scope() as db_session:
        query = QueryBuilder(db_session)

        if args.days:
            query = query.last_n_days(args.days)

        query = query.order_by('recorded_at', desc=False)
        sessions_db = query.execute()

        # Convert to dictionaries
        sessions = [s.to_dict() for s in sessions_db]

    if not sessions:
        print("❌ No sessions found in database")
        print("   Run migration first: python src/database/migration.py --sessions-dir data/sessions")
        return

    print(f"✅ Loaded {len(sessions)} sessions")
    if args.days:
        print(f"   Time range: Last {args.days} days")
    print()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ============================================================
    # GENERATE EXPORTS
    # ============================================================

    if args.report:
        print("📄 Generating PDF report...")
        generator = ReportGenerator(theme='dark')
        report_name = f"meditation_report_{timestamp}.pdf"
        if args.days:
            report_name = f"meditation_report_{args.days}days_{timestamp}.pdf"

        generator.generate_progress_report(
            sessions,
            str(output_dir / report_name),
            days=args.days
        )
        print()

    if args.video:
        print("🎬 Generating video compilation...")
        compiler = VideoCompiler(fps=30)

        # Progress video
        video_name = f"meditation_progress_{timestamp}.mp4"
        if args.days:
            video_name = f"meditation_progress_{args.days}days_{timestamp}.mp4"

        compiler.create_progress_video(
            sessions,
            str(output_dir / video_name),
            duration_per_session=2.0
        )

        # Evolution video
        evolution_name = f"meditation_evolution_{timestamp}.mp4"
        if args.days:
            evolution_name = f"meditation_evolution_{args.days}days_{timestamp}.mp4"

        compiler.create_evolution_video(
            sessions,
            str(output_dir / evolution_name),
            style='line_graph'
        )

        # Gallery video (if images exist)
        image_paths = glob("data/outputs/**/*.png", recursive=True)
        if image_paths:
            gallery_name = f"meditation_gallery_{timestamp}.mp4"
            compiler.create_gallery_video(
                image_paths[:50],  # Limit to 50 images
                str(output_dir / gallery_name),
                duration_per_image=3.0
            )
        print()

    if args.csv:
        print("📊 Exporting to CSV...")
        exporter = DataExporter()
        csv_name = f"sessions_{timestamp}.csv"
        if args.days:
            csv_name = f"sessions_{args.days}days_{timestamp}.csv"

        exporter.export_to_csv(
            sessions,
            str(output_dir / csv_name)
        )
        print()

    if args.json:
        print("📋 Exporting to JSON...")
        exporter = DataExporter()
        json_name = f"sessions_{timestamp}.json"
        if args.days:
            json_name = f"sessions_{args.days}days_{timestamp}.json"

        exporter.export_to_json(
            sessions,
            str(output_dir / json_name)
        )
        print()

    if args.stats:
        print("📈 Exporting statistics...")
        exporter = DataExporter()
        stats_name = f"statistics_{timestamp}.json"
        if args.days:
            stats_name = f"statistics_{args.days}days_{timestamp}.json"

        exporter.export_statistics(
            sessions,
            str(output_dir / stats_name)
        )
        print()

    if args.archive:
        print("📦 Creating complete archive...")
        exporter = DataExporter()
        archive_name = f"listener_backup_{timestamp}.tar.gz"

        exporter.create_archive(
            str(output_dir / archive_name)
        )
        print()

    if args.r:
        print("📊 Exporting for R...")
        exporter = DataExporter()
        r_dir = output_dir / f"r_export_{timestamp}"

        exporter.export_for_r(
            sessions,
            str(r_dir)
        )
        print()

    if args.matlab:
        print("📊 Exporting for MATLAB...")
        exporter = DataExporter()
        matlab_dir = output_dir / f"matlab_export_{timestamp}"

        exporter.export_for_matlab(
            sessions,
            str(matlab_dir)
        )
        print()

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 60)
    print("  ✅ Export Complete!")
    print("=" * 60)
    print()
    print(f"📁 Output directory: {output_dir.absolute()}")
    print()
    print("Generated files:")
    for file in sorted(output_dir.rglob("*")):
        if file.is_file():
            size = file.stat().st_size / 1024  # KB
            if size > 1024:
                size_str = f"{size/1024:.2f} MB"
            else:
                size_str = f"{size:.2f} KB"
            print(f"   {file.relative_to(output_dir)} ({size_str})")

    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Export cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
