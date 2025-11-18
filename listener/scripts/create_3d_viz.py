#!/usr/bin/env python3
"""
Create 3D Visualizations for Meditation Sessions

Generate interactive 3D visualizations for exploration and exhibition:
- 3D latent space journey
- 3D brain activity topography
- Animated meditation evolution
- VR-ready exports

Usage:
    # Generate all 3D visualizations
    python scripts/create_3d_viz.py --all

    # Latent space only
    python scripts/create_3d_viz.py --latent-space

    # Brain activity for specific session
    python scripts/create_3d_viz.py --brain-activity --session session_001

    # Journey animation
    python scripts/create_3d_viz.py --journey

    # VR export
    python scripts/create_3d_viz.py --vr-export

    # Custom parameters
    python scripts/create_3d_viz.py --latent-space --method tsne --color-by quality

    # Last N days only
    python scripts/create_3d_viz.py --all --days 30
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config

from src.database import SessionManager, QueryBuilder
from src.utils.visualization_3d import Visualization3D


def main():
    parser = argparse.ArgumentParser(
        description="Create 3D visualizations for meditation sessions"
    )

    # Visualization types
    parser.add_argument("--all", action="store_true",
                       help="Generate all 3D visualizations")
    parser.add_argument("--latent-space", action="store_true",
                       help="Generate 3D latent space visualization")
    parser.add_argument("--brain-activity", action="store_true",
                       help="Generate 3D brain activity visualization")
    parser.add_argument("--journey", action="store_true",
                       help="Generate animated meditation journey")
    parser.add_argument("--vr-export", action="store_true",
                       help="Export VR-ready data")

    # Parameters
    parser.add_argument("--method", default="umap",
                       choices=["umap", "tsne", "pca"],
                       help="Dimensionality reduction method (default: umap)")
    parser.add_argument("--color-by", default="depth",
                       choices=["depth", "quality", "alpha_plus", "date"],
                       help="Color points by metric (default: depth)")
    parser.add_argument("--size-by", default="quality",
                       choices=["quality", "depth", "duration"],
                       help="Size points by metric (default: quality)")
    parser.add_argument("--no-trajectory", action="store_true",
                       help="Don't show trajectory line in latent space")
    parser.add_argument("--session", default=None,
                       help="Session ID for brain activity visualization")

    # Filtering
    parser.add_argument("--days", type=int,
                       help="Only use sessions from last N days")
    parser.add_argument("--min-depth", type=float,
                       help="Minimum meditation depth")
    parser.add_argument("--min-quality", type=float,
                       help="Minimum signal quality")

    # Output
    parser.add_argument("--output-dir", default="exports/3d",
                       help="Output directory (default: exports/3d)")
    parser.add_argument("--theme", default="dark",
                       choices=["dark", "light"],
                       help="Visual theme (default: dark)")

    # Database
    parser.add_argument("--database", default=config.database_url,
                       help="Database URL")

    args = parser.parse_args()

    # If --all, enable all visualization types
    if args.all:
        args.latent_space = True
        args.brain_activity = True
        args.journey = True
        args.vr_export = True

    # If no type specified, show help
    if not any([args.latent_space, args.brain_activity, args.journey, args.vr_export]):
        parser.print_help()
        return

    print("=" * 60)
    print("  🌌 THE LISTENER - 3D Visualization Generator")
    print("=" * 60)
    print()

    # Load sessions from database
    print("📊 Loading sessions from database...")
    manager = SessionManager(args.database)

    with manager.session_scope() as db_session:
        query = QueryBuilder(db_session)

        if args.days:
            query = query.last_n_days(args.days)

        if args.min_depth:
            query = query.min_depth(args.min_depth)

        if args.min_quality:
            query = query.min_quality(args.min_quality)

        query = query.order_by('recorded_at', desc=False)
        sessions_db = query.execute()

        # Convert to dictionaries
        sessions = [s.to_dict() for s in sessions_db]

    if not sessions:
        print("❌ No sessions found in database")
        print("   Run migration first: python src/database/migration.py --sessions-dir data/sessions")
        return

    # Validate minimum session count for 3D visualizations
    if (args.latent_space or args.journey or args.vr_export) and len(sessions) < 2:
        print(f"❌ Need at least 2 sessions for 3D visualization (found {len(sessions)})")
        print("   Record more meditation sessions first")
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

    # Create visualization object
    viz = Visualization3D(sessions, theme=args.theme)

    # ============================================================
    # GENERATE VISUALIZATIONS
    # ============================================================

    if args.latent_space:
        print("🌌 Generating 3D latent space...")
        output_name = f"latent_space_3d_{timestamp}.html"
        if args.days:
            output_name = f"latent_space_3d_{args.days}days_{timestamp}.html"

        viz.create_latent_space_3d(
            output_path=str(output_dir / output_name),
            method=args.method,
            color_by=args.color_by,
            size_by=args.size_by,
            show_trajectory=not args.no_trajectory
        )
        print()

    if args.brain_activity:
        print("🧠 Generating 3D brain activity...")

        # If specific session specified
        if args.session:
            session_data = next((s for s in sessions if s['session_id'] == args.session), None)
            if session_data:
                output_name = f"brain_activity_3d_{args.session}_{timestamp}.html"
                viz.create_brain_activity_3d(
                    session_data=session_data,
                    output_path=str(output_dir / output_name)
                )
            else:
                print(f"❌ Session not found: {args.session}")
        else:
            # Use most recent session
            if sessions:
                session_data = sessions[-1]
                session_id = session_data.get('session_id', 'latest')
                output_name = f"brain_activity_3d_{session_id}_{timestamp}.html"
                viz.create_brain_activity_3d(
                    session_data=session_data,
                    output_path=str(output_dir / output_name)
                )
                print(f"   (Used most recent session: {session_id})")
            else:
                print("❌ No sessions available")

        print()

    if args.journey:
        print("🌠 Generating meditation journey animation...")
        output_name = f"meditation_journey_{timestamp}.html"
        if args.days:
            output_name = f"meditation_journey_{args.days}days_{timestamp}.html"

        viz.create_meditation_journey(
            output_path=str(output_dir / output_name),
            method=args.method
        )
        print()

    if args.vr_export:
        print("🥽 Exporting VR-ready data...")
        vr_dir = output_dir / f"vr_export_{timestamp}"
        if args.days:
            vr_dir = output_dir / f"vr_export_{args.days}days_{timestamp}"

        viz.export_for_vr(
            output_dir=str(vr_dir),
            method=args.method
        )
        print()

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 60)
    print("  ✅ 3D Visualization Complete!")
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
    print("📖 How to view:")
    print("   1. Open HTML files in web browser")
    print("   2. Interact with 3D visualizations:")
    print("      - Drag to rotate")
    print("      - Scroll to zoom")
    print("      - Hover for details")
    print("   3. Use slider in journey animation to explore evolution")
    print()
    print("🥽 VR export can be imported into:")
    print("   - Unity (import JSON + OBJ files)")
    print("   - Blender (File → Import → Wavefront OBJ)")
    print("   - Three.js / A-Frame (load JSON for positions)")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
