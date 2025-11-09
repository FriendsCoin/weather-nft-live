#!/usr/bin/env python3
"""
Analyze meditation quality and learning progression.

Based on neurofeedback research showing:
- Fast learning (brain states modulate in ~1 minute)
- Alpha power = meditation marker
- Beta power = concentration marker
- Relative spectral power more informative

Usage:
    # Analyze single session
    python scripts/analyze_meditation.py --session data/sessions/session_001_features.h5

    # Track learning across all sessions
    python scripts/analyze_meditation.py --sessions-dir data/sessions --plot

    # Generate comprehensive report
    python scripts/analyze_meditation.py --sessions-dir data/sessions --report
"""

import sys
from pathlib import Path
from glob import glob

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.meditation_analysis import MeditationAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse


def plot_session_analysis(metrics: dict, output_path: Optional[str] = None):
    """Plot comprehensive session analysis."""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. Meditation depth over time
    ax1 = fig.add_subplot(gs[0, :])
    depths = metrics['depth_timeseries']
    time = np.arange(len(depths)) * 2 / 60  # Convert to minutes

    ax1.plot(time, depths, linewidth=2, alpha=0.7, color='#4CAF50')
    ax1.fill_between(time, 0, depths, alpha=0.2, color='#4CAF50')
    ax1.axhline(y=metrics['mean_depth'], color='white', linestyle='--', alpha=0.5, label=f"Mean: {metrics['mean_depth']:.1f}")
    ax1.set_xlabel('Time (minutes)')
    ax1.set_ylabel('Meditation Depth (0-100)')
    ax1.set_title('Meditation Depth Over Time', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_ylim(0, 100)

    # 2. Alpha vs Beta power
    ax2 = fig.add_subplot(gs[1, 0])
    alpha = metrics['alpha_timeseries']
    beta = metrics['beta_timeseries']

    ax2.plot(time, np.array(alpha) * 100, label='Alpha (Relaxation)', color='#2196F3', linewidth=2)
    ax2.plot(time, np.array(beta) * 100, label='Beta (Concentration)', color='#FF9800', linewidth=2)
    ax2.set_xlabel('Time (minutes)')
    ax2.set_ylabel('Relative Power (%)')
    ax2.set_title('Alpha vs Beta Power', fontsize=12)
    ax2.legend()
    ax2.grid(alpha=0.3)

    # 3. Session quality metrics
    ax3 = fig.add_subplot(gs[1, 1])
    quality_metrics = {
        'Depth': metrics['mean_depth'],
        'Stability': metrics['depth_stability'] * 10,  # Scale to 0-100
        'Quality': metrics['quality_score']
    }

    bars = ax3.bar(quality_metrics.keys(), quality_metrics.values(), color=['#4CAF50', '#2196F3', '#9C27B0'])
    ax3.set_ylabel('Score (0-100)')
    ax3.set_title('Session Quality Metrics', fontsize=12)
    ax3.set_ylim(0, 100)
    ax3.grid(alpha=0.3, axis='y')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom')

    # 4. Alpha/Beta ratio over time
    ax4 = fig.add_subplot(gs[1, 2])
    ratio = np.array(alpha) / (np.array(beta) + 1e-10)
    ax4.plot(time, ratio, linewidth=2, color='#9C27B0')
    ax4.axhline(y=metrics['alpha_beta_ratio'], color='white', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Time (minutes)')
    ax4.set_ylabel('Alpha/Beta Ratio')
    ax4.set_title('Relaxation vs Concentration', fontsize=12)
    ax4.grid(alpha=0.3)

    # 5. State transitions
    ax5 = fig.add_subplot(gs[2, :])

    # Detect transitions
    analyzer = MeditationAnalyzer()
    transitions = analyzer.detect_state_transitions(depths)

    ax5.plot(time, depths, linewidth=2, alpha=0.5, color='gray', label='Depth')

    # Mark transitions
    for trans in transitions:
        trans_time = trans['time_seconds'] / 60
        trans_type = trans['type']
        color = '#4CAF50' if trans_type == 'deepening' else '#FF5722'
        marker = '↑' if trans_type == 'deepening' else '↓'

        ax5.axvline(x=trans_time, color=color, alpha=0.3, linestyle='--')
        ax5.scatter([trans_time], [depths[trans['time_window']]], s=100, c=color, marker=marker, zorder=10)

    ax5.set_xlabel('Time (minutes)')
    ax5.set_ylabel('Depth')
    ax5.set_title(f'State Transitions ({len(transitions)} detected)', fontsize=12)
    ax5.legend(['Depth', 'Deepening', 'Surfacing'])
    ax5.grid(alpha=0.3)

    # Overall title
    fig.suptitle('Meditation Session Analysis', fontsize=16, fontweight='bold', y=0.98)

    plt.style.use('dark_background')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"📊 Plot saved: {output_path}")

    plt.show()


def plot_learning_curve(learning_df: pd.DataFrame, output_path: Optional[str] = None):
    """Plot learning progression across sessions."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.style.use('dark_background')

    # 1. Meditation depth progression
    ax1 = axes[0, 0]
    ax1.plot(learning_df['session_number'], learning_df['mean_depth'], 'o-', linewidth=2, markersize=8, color='#4CAF50')

    # Add trend line
    z = np.polyfit(learning_df['session_number'], learning_df['mean_depth'], 1)
    p = np.poly1d(z)
    ax1.plot(learning_df['session_number'], p(learning_df['session_number']), "--", alpha=0.5, color='white', label=f'Trend: {z[0]:+.2f}/session')

    ax1.set_xlabel('Session Number')
    ax1.set_ylabel('Mean Depth (0-100)')
    ax1.set_title('Meditation Depth Evolution', fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # 2. Quality score progression
    ax2 = axes[0, 1]
    ax2.plot(learning_df['session_number'], learning_df['quality_score'], 's-', linewidth=2, markersize=8, color='#2196F3')

    z = np.polyfit(learning_df['session_number'], learning_df['quality_score'], 1)
    p = np.poly1d(z)
    ax2.plot(learning_df['session_number'], p(learning_df['session_number']), "--", alpha=0.5, color='white', label=f'Trend: {z[0]:+.2f}/session')

    ax2.set_xlabel('Session Number')
    ax2.set_ylabel('Quality Score (0-100)')
    ax2.set_title('Overall Quality Evolution', fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)

    # 3. Alpha/Beta ratio
    ax3 = axes[1, 0]
    ax3.plot(learning_df['session_number'], learning_df['alpha_beta_ratio'], '^-', linewidth=2, markersize=8, color='#9C27B0')
    ax3.axhline(y=1.0, color='white', linestyle='--', alpha=0.3, label='Balance (1.0)')
    ax3.set_xlabel('Session Number')
    ax3.set_ylabel('Alpha/Beta Ratio')
    ax3.set_title('Relaxation vs Concentration Balance', fontweight='bold')
    ax3.legend()
    ax3.grid(alpha=0.3)

    # 4. Stability
    ax4 = axes[1, 1]
    ax4.plot(learning_df['session_number'], learning_df['stability'], 'd-', linewidth=2, markersize=8, color='#FF9800')
    ax4.set_xlabel('Session Number')
    ax4.set_ylabel('Stability Score')
    ax4.set_title('Meditation Stability Over Time', fontweight='bold')
    ax4.grid(alpha=0.3)

    fig.suptitle(f'Learning Progression ({len(learning_df)} Sessions)', fontsize=16, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"📈 Learning curve saved: {output_path}")

    plt.show()


def generate_report(learning_df: pd.DataFrame, output_path: str):
    """Generate comprehensive text report."""
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║         THE LISTENER - MEDITATION LEARNING REPORT            ║
╚══════════════════════════════════════════════════════════════╝

OVERVIEW
========
Total Sessions: {len(learning_df)}
Date Range: {learning_df['session_file'].iloc[0]} → {learning_df['session_file'].iloc[-1]}

OVERALL PROGRESS
================
Starting Depth: {learning_df['mean_depth'].iloc[0]:.1f}/100
Final Depth: {learning_df['mean_depth'].iloc[-1]:.1f}/100
Improvement: {learning_df['mean_depth'].iloc[-1] - learning_df['mean_depth'].iloc[0]:+.1f} points

Starting Quality: {learning_df['quality_score'].iloc[0]:.1f}/100
Final Quality: {learning_df['quality_score'].iloc[-1]:.1f}/100
Improvement: {learning_df['quality_score'].iloc[-1] - learning_df['quality_score'].iloc[0]:+.1f} points

LEARNING TRENDS
===============
Depth Trend: {np.polyfit(learning_df['session_number'], learning_df['mean_depth'], 1)[0]:+.3f} points/session
Quality Trend: {np.polyfit(learning_df['session_number'], learning_df['quality_score'], 1)[0]:+.3f} points/session
Stability Trend: {np.polyfit(learning_df['session_number'], learning_df['stability'], 1)[0]:+.3f}/session

BEST SESSIONS
=============
"""

    # Top 3 by depth
    top_depth = learning_df.nlargest(3, 'mean_depth')
    report += "\nHighest Meditation Depth:\n"
    for idx, row in top_depth.iterrows():
        report += f"  {row['session_number']:3d}. {row['session_file']:30s} - {row['mean_depth']:.1f}/100\n"

    # Top 3 by quality
    top_quality = learning_df.nlargest(3, 'quality_score')
    report += "\nBest Overall Quality:\n"
    for idx, row in top_quality.iterrows():
        report += f"  {row['session_number']:3d}. {row['session_file']:30s} - {row['quality_score']:.1f}/100\n"

    # Statistics
    report += f"""
STATISTICS
==========
Mean Depth: {learning_df['mean_depth'].mean():.1f} ± {learning_df['mean_depth'].std():.1f}
Mean Quality: {learning_df['quality_score'].mean():.1f} ± {learning_df['quality_score'].std():.1f}
Mean Alpha/Beta: {learning_df['alpha_beta_ratio'].mean():.2f} ± {learning_df['alpha_beta_ratio'].std():.2f}
Mean Stability: {learning_df['stability'].mean():.2f} ± {learning_df['stability'].std():.2f}

INTERPRETATION
==============
"""

    # Depth interpretation
    mean_depth = learning_df['mean_depth'].mean()
    if mean_depth > 70:
        depth_level = "EXPERT - Deep, consistent meditation practice"
    elif mean_depth > 50:
        depth_level = "ADVANCED - Strong meditation foundation"
    elif mean_depth > 30:
        depth_level = "INTERMEDIATE - Developing meditation skills"
    else:
        depth_level = "BEGINNER - Early meditation practice"

    report += f"Depth Level: {depth_level}\n"

    # Learning trend interpretation
    depth_slope = np.polyfit(learning_df['session_number'], learning_df['mean_depth'], 1)[0]
    if depth_slope > 0.5:
        learning_status = "STRONG IMPROVEMENT - Meditation deepening significantly"
    elif depth_slope > 0:
        learning_status = "GRADUAL IMPROVEMENT - Steady progress"
    elif depth_slope > -0.5:
        learning_status = "STABLE - Maintaining consistent practice"
    else:
        learning_status = "DECLINING - May need practice adjustment"

    report += f"Learning Status: {learning_status}\n"

    # Alpha/Beta interpretation
    mean_ratio = learning_df['alpha_beta_ratio'].mean()
    if mean_ratio > 1.5:
        state_type = "DEEP RELAXATION - High alpha dominance"
    elif mean_ratio > 1.0:
        state_type = "BALANCED MEDITATION - Relaxed awareness"
    elif mean_ratio > 0.7:
        state_type = "ACTIVE MEDITATION - Some mental activity"
    else:
        state_type = "CONCENTRATION - Beta dominance (not typical for meditation)"

    report += f"Meditation State: {state_type}\n"

    report += """
═══════════════════════════════════════════════════════════════
Generated by THE LISTENER - AI Meditation Witness
═══════════════════════════════════════════════════════════════
"""

    # Save report
    with open(output_path, 'w') as f:
        f.write(report)

    print(report)
    print(f"\n📄 Report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze meditation sessions")
    parser.add_argument("--session", help="Single session feature file (.h5)")
    parser.add_argument("--sessions-dir", default="data/sessions",
                       help="Directory with session features")
    parser.add_argument("--plot", action="store_true",
                       help="Generate plots")
    parser.add_argument("--report", action="store_true",
                       help="Generate text report")
    parser.add_argument("--output-dir", default="data/outputs/analysis",
                       help="Output directory for plots/reports")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer = MeditationAnalyzer()

    if args.session:
        # Single session analysis
        print("=" * 70)
        print("SINGLE SESSION ANALYSIS")
        print("=" * 70)

        features_df = pd.read_hdf(args.session, key='features')
        metrics = analyzer.analyze_session(features_df)

        if args.plot:
            plot_output = output_dir / f"{Path(args.session).stem}_analysis.png"
            plot_session_analysis(metrics, str(plot_output))

    elif args.sessions_dir:
        # Multi-session learning curve
        print("=" * 70)
        print("MULTI-SESSION LEARNING ANALYSIS")
        print("=" * 70)

        session_files = sorted(glob(f"{args.sessions_dir}/*.h5"))

        if not session_files:
            print(f"❌ No .h5 files found in {args.sessions_dir}")
            return

        learning_df = analyzer.track_learning_curve(session_files)

        # Save learning data
        csv_path = output_dir / "learning_curve.csv"
        learning_df.to_csv(csv_path, index=False)
        print(f"\n💾 Learning data saved: {csv_path}")

        if args.plot:
            plot_output = output_dir / "learning_progression.png"
            plot_learning_curve(learning_df, str(plot_output))

        if args.report:
            report_output = output_dir / "meditation_report.txt"
            generate_report(learning_df, str(report_output))

    else:
        print("Usage: Provide --session or --sessions-dir")


if __name__ == "__main__":
    main()
