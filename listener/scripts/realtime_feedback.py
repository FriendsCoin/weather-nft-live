#!/usr/bin/env python3
"""
Real-time Neurofeedback Session

Provides live feedback during meditation using EEG analysis.

Features:
- Real-time state detection (alpha+/-, beta+/-, combined, drowsy)
- Audio and visual feedback cues
- Performance tracking
- Session recording for later analysis

Usage:
    # Basic session (5 minutes with mock data)
    python scripts/realtime_feedback.py --duration 300

    # With Muse headband (when supported)
    python scripts/realtime_feedback.py --device muse --duration 600

    # Quiet mode (visual only, no audio)
    python scripts/realtime_feedback.py --no-audio --duration 300

    # With personalized baseline
    python scripts/realtime_feedback.py --baseline data/baselines/baseline_001.pkl

    # Save session for analysis
    python scripts/realtime_feedback.py --duration 300 --output data/sessions/rt_session_001.pkl
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from realtime.neurofeedback import RealtimeNeurofeedback, FeedbackEvent
from realtime.feedback_cues import FeedbackController


def feedback_callback(event: FeedbackEvent, controller: FeedbackController):
    """
    Callback function for feedback events

    Args:
        event: Feedback event
        controller: Feedback controller
    """
    controller.provide_feedback(
        state_name=event.state.value,
        alpha=event.alpha_power,
        beta=event.beta_power,
        depth=event.meditation_depth
    )


def main():
    parser = argparse.ArgumentParser(
        description="Real-time Neurofeedback Session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 5-minute session with mock data
  python scripts/realtime_feedback.py --duration 300

  # 10-minute session with visual-only feedback
  python scripts/realtime_feedback.py --duration 600 --no-audio

  # Save session for analysis
  python scripts/realtime_feedback.py --duration 300 --output data/sessions/session.pkl

State Guide:
  [alpha+] = Deep relaxation (success)
  [alpha-] = Need more relaxation
  [beta+]  = Calm focus (success)
  [beta-]  = Too much mental activity
  [a+b+]   = Perfect meditation state
  [drowsy] = Stay alert (avoiding sleep)
        """
    )

    parser.add_argument(
        "--device",
        choices=["mock", "muse"],
        default="mock",
        help="EEG device to use (default: mock for testing)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Session duration in seconds (default: 300 = 5 minutes)"
    )

    parser.add_argument(
        "--window-size",
        type=float,
        default=2.0,
        help="Processing window size in seconds (default: 2.0)"
    )

    parser.add_argument(
        "--update-interval",
        type=float,
        default=0.5,
        help="Feedback update interval in seconds (default: 0.5)"
    )

    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio feedback (visual only)"
    )

    parser.add_argument(
        "--no-visual",
        action="store_true",
        help="Disable visual feedback (audio only)"
    )

    parser.add_argument(
        "--volume",
        type=float,
        default=0.5,
        help="Audio volume (0.0 to 1.0, default: 0.5)"
    )

    parser.add_argument(
        "--baseline",
        type=str,
        help="Path to baseline session for personalized thresholds"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Save session data to file (e.g., data/sessions/rt_session_001.pkl)"
    )

    parser.add_argument(
        "--smoothing",
        type=int,
        default=3,
        help="Number of states to smooth over (default: 3)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.no_audio and args.no_visual:
        print("Error: Cannot disable both audio and visual feedback")
        return 1

    if args.duration <= 0:
        print("Error: Duration must be positive")
        return 1

    if args.volume < 0 or args.volume > 1:
        print("Error: Volume must be between 0.0 and 1.0")
        return 1

    # Create feedback controller
    controller = FeedbackController(
        audio_enabled=not args.no_audio,
        visual_enabled=not args.no_visual,
        audio_volume=args.volume
    )

    # Create neurofeedback system
    feedback_system = RealtimeNeurofeedback(
        device=args.device,
        window_size=args.window_size,
        update_interval=args.update_interval,
        smoothing_window=args.smoothing,
        feedback_callback=lambda event: feedback_callback(event, controller),
        baseline_path=args.baseline
    )

    # Show welcome message
    print("\n" + "=" * 70)
    print("THE LISTENER - Real-time Neurofeedback")
    print("=" * 70)
    print(f"\nDevice: {args.device}")
    print(f"Duration: {args.duration}s ({args.duration / 60:.1f} minutes)")
    print(f"Window: {args.window_size}s, Update: {args.update_interval}s")
    print(f"Audio: {'Enabled' if not args.no_audio else 'Disabled'}")
    print(f"Visual: {'Enabled' if not args.no_visual else 'Disabled'}")

    if args.baseline:
        print(f"Baseline: {args.baseline}")

    print("\nPress Ctrl+C to stop early")
    print("=" * 70)

    # Wait for user to be ready
    try:
        input("\nPress Enter to begin meditation session...")
    except KeyboardInterrupt:
        print("\nSession cancelled")
        return 0

    # Start session
    controller.session_start(args.duration)

    try:
        feedback_system.start_session(duration=args.duration)
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user")
        feedback_system.is_running = False

    controller.session_end()

    # Save session if requested
    if args.output:
        feedback_system.save_session(args.output)

        # Also print where data was saved
        print(f"\nSession data saved to: {args.output}")
        print("You can analyze this session later with:")
        print(f"  python scripts/analyze_meditation.py {args.output}")

    # Print tips for improvement
    session_data = feedback_system.get_session_data()
    stats = session_data['performance_stats']

    print("\n" + "=" * 70)
    print("Tips for Next Session")
    print("=" * 70)

    alpha_total = stats['alpha_success_count'] + stats['alpha_fail_count']
    beta_total = stats['beta_success_count'] + stats['beta_fail_count']

    if alpha_total > 0:
        alpha_ratio = stats['alpha_success_count'] / alpha_total
        if alpha_ratio < 0.5:
            print("\n🔵 To improve alpha (relaxation):")
            print("  - Focus on slow, deep breathing")
            print("  - Relax facial muscles and shoulders")
            print("  - Let thoughts pass without engaging")

    if beta_total > 0:
        beta_ratio = stats['beta_success_count'] / beta_total
        if beta_ratio < 0.5:
            print("\n🔷 To reduce beta (mental activity):")
            print("  - Avoid analyzing or planning")
            print("  - Use a simple anchor (breath, mantra)")
            print("  - When mind wanders, gently return to anchor")

    if stats['drowsy_count'] > 5:
        print("\n🟡 To avoid drowsiness:")
        print("  - Sit upright with good posture")
        print("  - Keep eyes slightly open (soft gaze)")
        print("  - Meditate earlier in the day")

    if stats['combined_success_count'] > 0:
        print(f"\n⭐ Great job! You achieved perfect state {stats['combined_success_count']} times!")
        print("   Keep practicing to increase this number.")

    print("\n" + "=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
