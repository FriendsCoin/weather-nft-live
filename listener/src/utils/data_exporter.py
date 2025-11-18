"""
Data Exporter for THE LISTENER

Export meditation data in various formats:
- CSV for Excel/R/MATLAB
- JSON for web/JavaScript
- Archive packages (complete backup)
"""

from pathlib import Path
from typing import List, Dict, Optional
import json
import csv
from datetime import datetime
import pandas as pd
import shutil
import tarfile


class DataExporter:
    """
    Export meditation data in various formats.

    Usage:
        exporter = DataExporter()

        # Export to CSV
        exporter.export_to_csv(sessions, "exports/sessions.csv")

        # Export to JSON
        exporter.export_to_json(sessions, "exports/sessions.json")

        # Create complete archive
        exporter.create_archive("exports/complete_backup.tar.gz")
    """

    def __init__(self):
        """Initialize data exporter."""
        print("📦 Data Exporter initialized")

    def export_to_csv(
        self,
        sessions: List[Dict],
        output_path: str,
        include_all_fields: bool = True
    ):
        """
        Export sessions to CSV format.

        Args:
            sessions: List of session dictionaries
            output_path: Output CSV path
            include_all_fields: Include all fields or just summary
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame(sessions)

        if not include_all_fields:
            # Export only summary fields
            columns = [
                'session_id', 'recorded_at', 'duration_seconds',
                'mean_depth', 'quality_score',
                'alpha_performance', 'beta_performance',
                'alpha_beta_ratio', 'rating', 'notes'
            ]
            df = df[[col for col in columns if col in df.columns]]

        df.to_csv(output_path, index=False)
        print(f"✅ CSV exported: {output_path}")
        print(f"   Rows: {len(df)}, Columns: {len(df.columns)}")
        return output_path

    def export_to_json(
        self,
        sessions: List[Dict],
        output_path: str,
        pretty: bool = True
    ):
        """
        Export sessions to JSON format.

        Args:
            sessions: List of session dictionaries
            output_path: Output JSON path
            pretty: Pretty-print with indentation
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert datetime objects to strings
        sessions_json = []
        for session in sessions:
            session_copy = session.copy()
            if 'recorded_at' in session_copy and isinstance(session_copy['recorded_at'], datetime):
                session_copy['recorded_at'] = session_copy['recorded_at'].isoformat()
            sessions_json.append(session_copy)

        with open(output_path, 'w') as f:
            if pretty:
                json.dump(sessions_json, f, indent=2, default=str)
            else:
                json.dump(sessions_json, f, default=str)

        print(f"✅ JSON exported: {output_path}")
        print(f"   Sessions: {len(sessions_json)}")
        return output_path

    def export_statistics(
        self,
        sessions: List[Dict],
        output_path: str
    ):
        """
        Export statistics summary to JSON.

        Args:
            sessions: List of session dictionaries
            output_path: Output JSON path
        """
        import numpy as np

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Compute statistics
        depths = [s.get('mean_depth', 0) for s in sessions]
        qualities = [s.get('quality_score', 0) for s in sessions]
        alphas = [s.get('alpha_performance', 0) for s in sessions]
        betas = [s.get('beta_performance', 0) for s in sessions]
        durations = [s.get('duration_seconds', 0) for s in sessions]

        stats = {
            'summary': {
                'total_sessions': len(sessions),
                'total_time_hours': sum(durations) / 3600,
                'date_range': {
                    'first': sessions[0].get('recorded_at') if sessions else None,
                    'last': sessions[-1].get('recorded_at') if sessions else None
                }
            },
            'depth': {
                'mean': float(np.mean(depths)),
                'median': float(np.median(depths)),
                'std': float(np.std(depths)),
                'min': float(np.min(depths)),
                'max': float(np.max(depths)),
                'percentiles': {
                    '25': float(np.percentile(depths, 25)),
                    '50': float(np.percentile(depths, 50)),
                    '75': float(np.percentile(depths, 75))
                }
            },
            'quality': {
                'mean': float(np.mean(qualities)),
                'median': float(np.median(qualities)),
                'std': float(np.std(qualities)),
                'min': float(np.min(qualities)),
                'max': float(np.max(qualities))
            },
            'alpha_performance': {
                'mean': float(np.mean(alphas)),
                'std': float(np.std(alphas))
            },
            'beta_performance': {
                'mean': float(np.mean(betas)),
                'std': float(np.std(betas))
            },
            'duration': {
                'mean_minutes': float(np.mean(durations) / 60),
                'median_minutes': float(np.median(durations) / 60),
                'total_hours': float(sum(durations) / 3600)
            },
            'progress': {
                'first_5_avg_depth': float(np.mean(depths[:5])) if len(depths) >= 5 else None,
                'last_5_avg_depth': float(np.mean(depths[-5:])) if len(depths) >= 5 else None,
                'improvement': float(np.mean(depths[-5:]) - np.mean(depths[:5])) if len(depths) >= 5 else None
            },
            'generated_at': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"✅ Statistics exported: {output_path}")
        return output_path

    def create_archive(
        self,
        output_path: str,
        include_patterns: Optional[List[str]] = None
    ):
        """
        Create complete archive of all data.

        Args:
            output_path: Output tar.gz path
            include_patterns: Patterns to include (default: all data)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if include_patterns is None:
            include_patterns = [
                'data/sessions/*.h5',
                'data/outputs/**/*',
                'data/checkpoints/*.pt',
                'data/listener.db',
                'data/mood_logs/**/*',
                'config.yaml'
            ]

        print(f"\n📦 Creating archive...")
        print(f"   Output: {output_path}")

        with tarfile.open(output_path, 'w:gz') as tar:
            for pattern in include_patterns:
                for file_path in Path('.').glob(pattern):
                    if file_path.is_file():
                        tar.add(file_path)
                        print(f"   + {file_path}")

        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Archive created: {output_path}")
        print(f"   Size: {file_size:.2f} MB")
        return output_path

    def export_for_r(
        self,
        sessions: List[Dict],
        output_dir: str
    ):
        """
        Export data in R-friendly format.

        Creates CSV with proper column names and metadata.

        Args:
            sessions: List of session dictionaries
            output_dir: Output directory
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Main data CSV
        df = pd.DataFrame(sessions)

        # Rename columns to R-friendly names
        df.columns = [col.replace('_', '.') for col in df.columns]

        # Export
        data_path = output_dir / 'sessions_data.csv'
        df.to_csv(data_path, index=False)

        # Create R script for loading
        r_script = f"""
# THE LISTENER - R Analysis Script
# Generated: {datetime.now().isoformat()}

# Load data
data <- read.csv("sessions_data.csv")

# Basic statistics
summary(data$mean.depth)
summary(data$quality.score)

# Plot depth over time
plot(data$mean.depth, type='l', main='Meditation Depth Over Time',
     xlab='Session', ylab='Depth', col='blue', lwd=2)

# Correlation analysis
cor(data$mean.depth, data$quality.score, use='complete.obs')

# Linear trend
model <- lm(mean.depth ~ seq_along(mean.depth), data=data)
summary(model)
abline(model, col='red', lwd=2)

print("Data loaded successfully!")
print(paste("Total sessions:", nrow(data)))
"""

        script_path = output_dir / 'analysis.R'
        with open(script_path, 'w') as f:
            f.write(r_script)

        print(f"✅ R export complete: {output_dir}")
        print(f"   Data: {data_path}")
        print(f"   Script: {script_path}")
        return output_dir

    def export_for_matlab(
        self,
        sessions: List[Dict],
        output_dir: str
    ):
        """
        Export data in MATLAB-friendly format.

        Creates CSV and .mat file.

        Args:
            sessions: List of session dictionaries
            output_dir: Output directory
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export CSV
        csv_path = output_dir / 'sessions_data.csv'
        self.export_to_csv(sessions, str(csv_path))

        # Create MATLAB script
        matlab_script = f"""
% THE LISTENER - MATLAB Analysis Script
% Generated: {datetime.now().isoformat()}

% Load data
data = readtable('sessions_data.csv');

% Basic statistics
mean_depth = data.mean_depth;
quality = data.quality_score;

fprintf('Total sessions: %d\\n', height(data));
fprintf('Mean depth: %.2f\\n', mean(mean_depth, 'omitnan'));
fprintf('Mean quality: %.2f\\n', mean(quality, 'omitnan'));

% Plot
figure;
subplot(2,1,1);
plot(mean_depth, 'LineWidth', 2);
title('Meditation Depth Over Time');
xlabel('Session');
ylabel('Depth');
grid on;

subplot(2,1,2);
plot(quality, 'LineWidth', 2, 'Color', [0, 0.8, 0.2]);
title('Quality Score Over Time');
xlabel('Session');
ylabel('Quality');
grid on;

% Correlation
corr_val = corr(mean_depth, quality, 'rows', 'complete');
fprintf('Depth-Quality correlation: %.3f\\n', corr_val);

% Trend analysis
x = (1:length(mean_depth))';
p = polyfit(x, mean_depth, 1);
trend = polyval(p, x);

figure;
plot(x, mean_depth, 'o', x, trend, '-', 'LineWidth', 2);
legend('Actual', 'Trend');
title('Meditation Progress Trend');
xlabel('Session');
ylabel('Depth');
grid on;

fprintf('Trend slope: %.3f per session\\n', p(1));
"""

        script_path = output_dir / 'analysis.m'
        with open(script_path, 'w') as f:
            f.write(matlab_script)

        print(f"✅ MATLAB export complete: {output_dir}")
        print(f"   Data: {csv_path}")
        print(f"   Script: {script_path}")
        return output_dir


# Example usage
if __name__ == "__main__":
    print("Data Exporter Example")
    print()
    print("Usage:")
    print("  from src.utils.data_exporter import DataExporter")
    print("  ")
    print("  exporter = DataExporter()")
    print("  exporter.export_to_csv(sessions, 'sessions.csv')")
    print("  exporter.export_to_json(sessions, 'sessions.json')")
    print("  exporter.create_archive('backup.tar.gz')")
