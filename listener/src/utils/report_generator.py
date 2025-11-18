"""
Report Generator for THE LISTENER

Creates beautiful PDF reports with:
- Session summary and statistics
- Charts and visualizations
- Progress tracking
- Meditation insights

Uses matplotlib for charts and reportlab for PDF generation.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  reportlab not installed. PDF reports will use matplotlib only.")


class ReportGenerator:
    """
    Generate PDF reports for meditation sessions.

    Usage:
        generator = ReportGenerator()

        # Single session report
        generator.generate_session_report(
            session_data,
            output_path="reports/session_001.pdf"
        )

        # Progress report
        generator.generate_progress_report(
            sessions,
            output_path="reports/progress_30days.pdf"
        )

        # Complete summary
        generator.generate_complete_summary(
            all_sessions,
            output_path="reports/meditation_summary.pdf"
        )
    """

    def __init__(self, theme: str = 'dark'):
        """
        Initialize report generator.

        Args:
            theme: 'dark' or 'light' for report aesthetics
        """
        self.theme = theme

        # Set matplotlib style
        if theme == 'dark':
            plt.style.use('dark_background')
            self.bg_color = '#0a0e27'
            self.text_color = '#e8eaf6'
            self.accent_color = '#7c4dff'
        else:
            plt.style.use('default')
            self.bg_color = '#ffffff'
            self.text_color = '#000000'
            self.accent_color = '#5e35b1'

        print(f"📄 Report Generator initialized ({theme} theme)")

    # ============================================================
    # MATPLOTLIB-BASED REPORTS (Always available)
    # ============================================================

    def generate_matplotlib_report(
        self,
        sessions: List[Dict],
        output_path: str,
        title: str = "Meditation Report"
    ):
        """
        Generate multi-page PDF report using matplotlib.

        Args:
            sessions: List of session dictionaries
            output_path: Output PDF path
            title: Report title
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with PdfPages(output_path) as pdf:
            # Page 1: Title and summary
            self._create_title_page(pdf, sessions, title)

            # Page 2: Depth trend
            self._create_depth_chart(pdf, sessions)

            # Page 3: Quality trend
            self._create_quality_chart(pdf, sessions)

            # Page 4: Distribution charts
            self._create_distribution_charts(pdf, sessions)

            # Page 5: Statistics table
            self._create_statistics_page(pdf, sessions)

            # Metadata
            d = pdf.infodict()
            d['Title'] = title
            d['Author'] = 'THE LISTENER'
            d['Subject'] = 'Meditation Session Report'
            d['Keywords'] = 'meditation, EEG, neurofeedback'
            d['CreationDate'] = datetime.now()

        print(f"✅ Report generated: {output_path}")
        return output_path

    def _create_title_page(self, pdf: PdfPages, sessions: List[Dict], title: str):
        """Create title page with summary statistics."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')

        # Title
        fig.text(0.5, 0.85, title, ha='center', fontsize=28, fontweight='bold',
                color=self.accent_color)
        fig.text(0.5, 0.80, 'THE LISTENER - AI Meditation Companion',
                ha='center', fontsize=14, color=self.text_color, alpha=0.7)

        # Summary statistics
        total_sessions = len(sessions)
        depths = [s.get('mean_depth', 0) for s in sessions]
        qualities = [s.get('quality_score', 0) for s in sessions]
        durations = [s.get('duration_seconds', 0) for s in sessions]

        avg_depth = np.mean(depths) if depths else 0
        avg_quality = np.mean(qualities) if qualities else 0
        total_time = sum(durations) / 3600 if durations else 0  # hours

        stats_text = f"""
        Summary Statistics
        ═══════════════════════════════════

        Total Sessions:        {total_sessions}
        Total Time:            {total_time:.1f} hours

        Average Depth:         {avg_depth:.1f}/100
        Average Quality:       {avg_quality:.1f}/100

        Best Depth:            {max(depths) if depths else 0:.1f}/100
        Best Quality:          {max(qualities) if qualities else 0:.1f}/100

        ═══════════════════════════════════

        Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """

        fig.text(0.5, 0.45, stats_text, ha='center', va='center',
                fontsize=12, color=self.text_color, family='monospace')

        pdf.savefig(fig, facecolor=self.bg_color)
        plt.close()

    def _create_depth_chart(self, pdf: PdfPages, sessions: List[Dict]):
        """Create meditation depth trend chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        dates = [datetime.fromisoformat(s['recorded_at']) if isinstance(s['recorded_at'], str)
                else s['recorded_at'] for s in sessions]
        depths = [s.get('mean_depth', 0) for s in sessions]

        # Sort by date
        sorted_data = sorted(zip(dates, depths))
        dates, depths = zip(*sorted_data) if sorted_data else ([], [])

        # Plot
        ax.plot(dates, depths, marker='o', linewidth=2, markersize=6,
               color=self.accent_color, label='Meditation Depth')

        # Moving average
        if len(depths) >= 7:
            window = min(7, len(depths))
            ma = np.convolve(depths, np.ones(window)/window, mode='valid')
            ma_dates = dates[window-1:]
            ax.plot(ma_dates, ma, '--', linewidth=2, alpha=0.7,
                   color='#00e676', label=f'{window}-session Moving Avg')

        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Meditation Depth', fontsize=12)
        ax.set_title('Meditation Depth Over Time', fontsize=16, fontweight='bold',
                    pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        ax.set_ylim(0, 100)

        # Format dates
        if len(dates) > 10:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)

        plt.tight_layout()
        pdf.savefig(fig, facecolor=self.bg_color)
        plt.close()

    def _create_quality_chart(self, pdf: PdfPages, sessions: List[Dict]):
        """Create quality score trend chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        dates = [datetime.fromisoformat(s['recorded_at']) if isinstance(s['recorded_at'], str)
                else s['recorded_at'] for s in sessions]
        qualities = [s.get('quality_score', 0) for s in sessions]

        # Sort by date
        sorted_data = sorted(zip(dates, qualities))
        dates, qualities = zip(*sorted_data) if sorted_data else ([], [])

        # Plot
        ax.plot(dates, qualities, marker='s', linewidth=2, markersize=6,
               color='#00e676', label='Quality Score')

        # Formatting
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Quality Score', fontsize=12)
        ax.set_title('Session Quality Over Time', fontsize=16, fontweight='bold',
                    pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        ax.set_ylim(0, 100)

        # Format dates
        if len(dates) > 10:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)

        plt.tight_layout()
        pdf.savefig(fig, facecolor=self.bg_color)
        plt.close()

    def _create_distribution_charts(self, pdf: PdfPages, sessions: List[Dict]):
        """Create distribution histograms."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))

        # Extract data
        depths = [s.get('mean_depth', 0) for s in sessions]
        qualities = [s.get('quality_score', 0) for s in sessions]
        alphas = [s.get('alpha_performance', 0) for s in sessions]
        durations = [s.get('duration_seconds', 0) / 60 for s in sessions]  # minutes

        # Depth distribution
        ax1.hist(depths, bins=15, color=self.accent_color, alpha=0.7, edgecolor='white')
        ax1.set_xlabel('Meditation Depth')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Depth Distribution')
        ax1.axvline(np.mean(depths), color='#00e676', linestyle='--', linewidth=2,
                   label=f'Mean: {np.mean(depths):.1f}')
        ax1.legend()

        # Quality distribution
        ax2.hist(qualities, bins=15, color='#00e676', alpha=0.7, edgecolor='white')
        ax2.set_xlabel('Quality Score')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Quality Distribution')
        ax2.axvline(np.mean(qualities), color=self.accent_color, linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(qualities):.1f}')
        ax2.legend()

        # Alpha performance distribution
        ax3.hist(alphas, bins=15, color='#ffd740', alpha=0.7, edgecolor='white')
        ax3.set_xlabel('Alpha Performance')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Alpha Performance Distribution')
        ax3.axvline(np.mean(alphas), color='#ff5252', linestyle='--', linewidth=2,
                   label=f'Mean: {np.mean(alphas):.2f}')
        ax3.legend()

        # Duration distribution
        ax4.hist(durations, bins=15, color='#536dfe', alpha=0.7, edgecolor='white')
        ax4.set_xlabel('Duration (minutes)')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Session Duration Distribution')
        ax4.axvline(np.mean(durations), color='#00e676', linestyle='--', linewidth=2,
                   label=f'Mean: {np.mean(durations):.1f} min')
        ax4.legend()

        plt.suptitle('Session Distributions', fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        pdf.savefig(fig, facecolor=self.bg_color)
        plt.close()

    def _create_statistics_page(self, pdf: PdfPages, sessions: List[Dict]):
        """Create detailed statistics page."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')

        # Compute statistics
        depths = [s.get('mean_depth', 0) for s in sessions]
        qualities = [s.get('quality_score', 0) for s in sessions]
        alphas = [s.get('alpha_performance', 0) for s in sessions]
        betas = [s.get('beta_performance', 0) for s in sessions]
        durations = [s.get('duration_seconds', 0) for s in sessions]

        stats_text = f"""
        Detailed Statistics
        ═══════════════════════════════════════════════════

        DEPTH METRICS
        ───────────────────────────────────────────────────
        Mean:                {np.mean(depths):.2f}
        Median:              {np.median(depths):.2f}
        Std Dev:             {np.std(depths):.2f}
        Min:                 {np.min(depths):.2f}
        Max:                 {np.max(depths):.2f}

        QUALITY METRICS
        ───────────────────────────────────────────────────
        Mean:                {np.mean(qualities):.2f}
        Median:              {np.median(qualities):.2f}
        Std Dev:             {np.std(qualities):.2f}
        Min:                 {np.min(qualities):.2f}
        Max:                 {np.max(qualities):.2f}

        PERFORMANCE METRICS
        ───────────────────────────────────────────────────
        Alpha Mean:          {np.mean(alphas):.3f}
        Alpha Std:           {np.std(alphas):.3f}
        Beta Mean:           {np.mean(betas):.3f}
        Beta Std:            {np.std(betas):.3f}

        DURATION
        ───────────────────────────────────────────────────
        Total Time:          {sum(durations)/3600:.2f} hours
        Mean Duration:       {np.mean(durations)/60:.1f} minutes
        Median Duration:     {np.median(durations)/60:.1f} minutes

        PROGRESS INDICATORS
        ───────────────────────────────────────────────────
        First 5 Avg Depth:   {np.mean(depths[:5]) if len(depths) >= 5 else 0:.2f}
        Last 5 Avg Depth:    {np.mean(depths[-5:]) if len(depths) >= 5 else 0:.2f}
        Improvement:         {np.mean(depths[-5:]) - np.mean(depths[:5]) if len(depths) >= 5 else 0:.2f}

        ═══════════════════════════════════════════════════
        """

        fig.text(0.5, 0.5, stats_text, ha='center', va='center',
                fontsize=10, color=self.text_color, family='monospace')

        fig.text(0.5, 0.95, 'Statistical Analysis', ha='center',
                fontsize=18, fontweight='bold', color=self.accent_color)

        pdf.savefig(fig, facecolor=self.bg_color)
        plt.close()

    # ============================================================
    # CONVENIENCE METHODS
    # ============================================================

    def generate_session_report(
        self,
        session: Dict,
        output_path: str
    ):
        """
        Generate report for single session.

        Args:
            session: Session data dictionary
            output_path: Output PDF path
        """
        return self.generate_matplotlib_report(
            [session],
            output_path,
            title=f"Session Report\n{session.get('session_id', 'Unknown')}"
        )

    def generate_progress_report(
        self,
        sessions: List[Dict],
        output_path: str,
        days: Optional[int] = None
    ):
        """
        Generate progress report for multiple sessions.

        Args:
            sessions: List of session dictionaries
            output_path: Output PDF path
            days: Last N days (optional)
        """
        title = "Meditation Progress Report"
        if days:
            title += f"\nLast {days} Days"

        return self.generate_matplotlib_report(
            sessions,
            output_path,
            title=title
        )

    def generate_complete_summary(
        self,
        sessions: List[Dict],
        output_path: str
    ):
        """
        Generate complete summary report.

        Args:
            sessions: All session dictionaries
            output_path: Output PDF path
        """
        return self.generate_matplotlib_report(
            sessions,
            output_path,
            title="Complete Meditation Summary"
        )


# Example usage
if __name__ == "__main__":
    print("Report Generator Example")
    print()
    print("Usage:")
    print("  from src.utils.report_generator import ReportGenerator")
    print("  ")
    print("  generator = ReportGenerator()")
    print("  generator.generate_progress_report(sessions, 'report.pdf')")
