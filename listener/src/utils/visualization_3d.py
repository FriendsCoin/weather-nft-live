#!/usr/bin/env python3
"""
3D Visualization for Meditation Sessions

Creates interactive 3D visualizations for exploration and exhibition:
- 3D latent space with UMAP/t-SNE dimensionality reduction
- 3D brain activity topography
- Journey through meditation evolution
- VR-ready exports
- Blender-compatible mesh exports

Usage:
    from src.utils.visualization_3d import Visualization3D

    viz = Visualization3D(sessions)
    viz.create_latent_space_3d(output_path="latent_space_3d.html")
    viz.create_brain_activity_3d(session_id, output_path="brain_3d.html")
    viz.create_meditation_journey(output_path="journey_3d.html")
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json


class Visualization3D:
    """
    3D visualization for meditation sessions
    """

    def __init__(
        self,
        sessions: Optional[List[Dict[str, Any]]] = None,
        theme: str = 'dark'
    ):
        """
        Initialize 3D visualization

        Args:
            sessions: List of session dictionaries
            theme: Visual theme ('dark', 'light')
        """
        self.sessions = sessions or []
        self.theme = theme

        # Theme colors
        if theme == 'dark':
            self.bg_color = '#0a0e27'
            self.paper_color = '#1a1f3a'
            self.text_color = '#e8eaf6'
            self.grid_color = '#2a3050'
        else:
            self.bg_color = '#ffffff'
            self.paper_color = '#f8f9fa'
            self.text_color = '#212529'
            self.grid_color = '#dee2e6'

        print(f"🎨 3D Visualization initialized with {len(self.sessions)} sessions")

    # ============================================================
    # 3D LATENT SPACE
    # ============================================================

    def create_latent_space_3d(
        self,
        output_path: str,
        method: str = 'umap',
        color_by: str = 'depth',
        size_by: str = 'quality',
        show_trajectory: bool = True,
        n_neighbors: int = 15,
        min_dist: float = 0.1
    ):
        """
        Create interactive 3D latent space visualization

        Args:
            output_path: Output HTML file path
            method: Dimensionality reduction ('umap', 'tsne', 'pca')
            color_by: Metric to color points ('depth', 'quality', 'alpha_plus', 'date')
            size_by: Metric to size points ('quality', 'depth', 'duration')
            show_trajectory: Show chronological trajectory lines
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter
        """
        print(f"\n🌌 Creating 3D latent space visualization ({method.upper()})...")

        if not self.sessions:
            print("❌ No sessions loaded")
            return

        # Extract latent vectors
        latent_vectors = []
        metadata = []

        for session in self.sessions:
            if 'latent_mean' in session and session['latent_mean'] is not None:
                latent_vectors.append(session['latent_mean'])
                metadata.append(session)

        if len(latent_vectors) < 2:
            print("❌ Need at least 2 sessions with latent vectors")
            return

        latent_vectors = np.array(latent_vectors)
        print(f"   Loaded {len(latent_vectors)} latent vectors (dim={latent_vectors.shape[1]})")

        # Reduce to 3D
        coords_3d = self._reduce_to_3d(latent_vectors, method, n_neighbors, min_dist)

        # Extract metrics for visualization
        depths = [m.get('depth_score', 50) for m in metadata]
        qualities = [m.get('quality_score', 50) for m in metadata]
        alpha_plus = [m.get('performance_ratios', {}).get('alpha_plus', 1.0) for m in metadata]
        dates = [m.get('recorded_at', '') for m in metadata]
        session_ids = [m.get('session_id', f"session_{i}") for m in metadata]

        # Prepare color and size data
        if color_by == 'depth':
            colors = depths
            colorscale = [[0, '#3949ab'], [0.5, '#5e35b1'], [1, '#7c4dff']]
            colorbar_title = 'Meditation Depth'
        elif color_by == 'quality':
            colors = qualities
            colorscale = 'viridis'
            colorbar_title = 'Signal Quality'
        elif color_by == 'alpha_plus':
            colors = alpha_plus
            colorscale = 'plasma'
            colorbar_title = 'Alpha+ Performance'
        else:  # date
            colors = list(range(len(metadata)))
            colorscale = 'rainbow'
            colorbar_title = 'Session Order'

        if size_by == 'quality':
            sizes = qualities
        elif size_by == 'depth':
            sizes = depths
        else:  # duration
            sizes = [m.get('duration_seconds', 600) / 60 for m in metadata]  # minutes

        # Normalize sizes for visualization
        sizes = np.array(sizes)
        sizes = 5 + (sizes - sizes.min()) / (sizes.max() - sizes.min() + 1e-6) * 15

        # Create hover text
        hover_texts = []
        for i, m in enumerate(metadata):
            text = (
                f"<b>{session_ids[i]}</b><br>"
                f"Depth: {depths[i]:.1f}<br>"
                f"Quality: {qualities[i]:.1f}<br>"
                f"Alpha+: {alpha_plus[i]:.2f}<br>"
                f"Date: {dates[i][:10]}"
            )
            hover_texts.append(text)

        # Create 3D scatter plot
        fig = go.Figure()

        # Add scatter points
        fig.add_trace(go.Scatter3d(
            x=coords_3d[:, 0],
            y=coords_3d[:, 1],
            z=coords_3d[:, 2],
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors,
                colorscale=colorscale,
                showscale=True,
                colorbar=dict(
                    title=colorbar_title,
                    thickness=20,
                    len=0.7
                ),
                line=dict(color='white', width=0.5)
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            name='Sessions'
        ))

        # Add trajectory line if requested
        if show_trajectory:
            fig.add_trace(go.Scatter3d(
                x=coords_3d[:, 0],
                y=coords_3d[:, 1],
                z=coords_3d[:, 2],
                mode='lines',
                line=dict(color='rgba(124, 77, 255, 0.3)', width=2),
                hoverinfo='skip',
                showlegend=False,
                name='Trajectory'
            ))

        # Update layout
        fig.update_layout(
            title=f'3D Latent Space - Meditation Journey ({method.upper()})',
            scene=dict(
                xaxis=dict(
                    title=f'{method.upper()} 1',
                    backgroundcolor=self.bg_color,
                    gridcolor=self.grid_color,
                    showbackground=True,
                ),
                yaxis=dict(
                    title=f'{method.upper()} 2',
                    backgroundcolor=self.bg_color,
                    gridcolor=self.grid_color,
                    showbackground=True,
                ),
                zaxis=dict(
                    title=f'{method.upper()} 3',
                    backgroundcolor=self.bg_color,
                    gridcolor=self.grid_color,
                    showbackground=True,
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            paper_bgcolor=self.paper_color,
            plot_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            hovermode='closest',
            width=1200,
            height=800
        )

        # Save
        fig.write_html(output_path)
        print(f"   ✅ Saved: {output_path}")

        return fig

    def _reduce_to_3d(
        self,
        vectors: np.ndarray,
        method: str = 'umap',
        n_neighbors: int = 15,
        min_dist: float = 0.1
    ) -> np.ndarray:
        """
        Reduce high-dimensional vectors to 3D

        Args:
            vectors: Input vectors (n_samples, n_features)
            method: Reduction method ('umap', 'tsne', 'pca')
            n_neighbors: UMAP n_neighbors
            min_dist: UMAP min_dist

        Returns:
            3D coordinates (n_samples, 3)
        """
        print(f"   Reducing {vectors.shape[1]}D → 3D using {method.upper()}...")

        if method == 'umap':
            from umap import UMAP
            reducer = UMAP(
                n_components=3,
                n_neighbors=min(n_neighbors, len(vectors) - 1),
                min_dist=min_dist,
                metric='euclidean',
                random_state=42
            )
            coords_3d = reducer.fit_transform(vectors)

        elif method == 'tsne':
            from sklearn.manifold import TSNE
            reducer = TSNE(
                n_components=3,
                perplexity=min(30, len(vectors) - 1),
                random_state=42,
                n_iter=1000
            )
            coords_3d = reducer.fit_transform(vectors)

        elif method == 'pca':
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=3)
            coords_3d = reducer.fit_transform(vectors)
            print(f"   PCA explained variance: {reducer.explained_variance_ratio_.sum():.2%}")

        else:
            raise ValueError(f"Unknown method: {method}")

        return coords_3d

    # ============================================================
    # 3D BRAIN ACTIVITY
    # ============================================================

    def create_brain_activity_3d(
        self,
        session_data: Dict[str, Any],
        output_path: str,
        time_point: Optional[int] = None
    ):
        """
        Create 3D brain activity visualization

        Args:
            session_data: Session dictionary with EEG data
            output_path: Output HTML file path
            time_point: Specific time point (seconds), or None for average
        """
        print("\n🧠 Creating 3D brain activity visualization...")

        # Get EEG data
        if 'eeg_data' not in session_data or session_data['eeg_data'] is None:
            print("❌ No EEG data in session")
            return

        eeg_data = session_data['eeg_data']  # (n_channels, n_samples)

        # Muse S electrode positions (approximate, in 3D)
        # AF7, AF8, TP9, TP10 (frontal and temporal)
        electrode_positions = {
            'AF7': np.array([-0.3, 0.6, 0.3]),   # Left frontal
            'AF8': np.array([0.3, 0.6, 0.3]),    # Right frontal
            'TP9': np.array([-0.6, -0.2, 0.1]),  # Left temporal
            'TP10': np.array([0.6, -0.2, 0.1]),  # Right temporal
        }

        # Calculate average power at each electrode
        if time_point is not None:
            # Specific time point
            sample_idx = int(time_point * 256)  # 256 Hz sampling
            powers = np.abs(eeg_data[:, sample_idx])
        else:
            # Average over entire session
            powers = np.mean(np.abs(eeg_data), axis=1)

        # Normalize powers
        powers = (powers - powers.min()) / (powers.max() - powers.min() + 1e-6)

        # Create figure
        fig = go.Figure()

        # Add head sphere (wireframe)
        self._add_head_sphere(fig)

        # Add electrodes
        electrode_names = list(electrode_positions.keys())
        for i, name in enumerate(electrode_names):
            pos = electrode_positions[name]
            power = powers[i] if i < len(powers) else 0

            # Electrode marker
            fig.add_trace(go.Scatter3d(
                x=[pos[0]],
                y=[pos[1]],
                z=[pos[2]],
                mode='markers+text',
                marker=dict(
                    size=15 + power * 20,
                    color=power,
                    colorscale='Hot',
                    cmin=0,
                    cmax=1,
                    showscale=False,
                    line=dict(color='white', width=2)
                ),
                text=[name],
                textposition='top center',
                textfont=dict(size=10, color=self.text_color),
                hovertemplate=f'<b>{name}</b><br>Power: {power:.2f}<extra></extra>',
                showlegend=False
            ))

        # Add interpolated surface for topography
        self._add_topographic_surface(fig, electrode_positions, powers)

        # Update layout
        fig.update_layout(
            title='3D Brain Activity - EEG Topography',
            scene=dict(
                xaxis=dict(
                    title='Left-Right',
                    backgroundcolor=self.bg_color,
                    gridcolor=self.grid_color,
                    showbackground=True,
                    range=[-1, 1]
                ),
                yaxis=dict(
                    title='Front-Back',
                    backgroundcolor=self.bg_color,
                    gridcolor=self.grid_color,
                    showbackground=True,
                    range=[-1, 1]
                ),
                zaxis=dict(
                    title='Top-Bottom',
                    backgroundcolor=self.bg_color,
                    gridcolor=self.grid_color,
                    showbackground=True,
                    range=[-0.5, 1]
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                ),
                aspectmode='cube'
            ),
            paper_bgcolor=self.paper_color,
            plot_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            width=1000,
            height=800
        )

        # Save
        fig.write_html(output_path)
        print(f"   ✅ Saved: {output_path}")

        return fig

    def _add_head_sphere(self, fig: go.Figure):
        """Add wireframe sphere representing head"""
        # Create sphere mesh
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = 0.7 * np.outer(np.cos(u), np.sin(v))
        y = 0.7 * np.outer(np.sin(u), np.sin(v))
        z = 0.7 * np.outer(np.ones(np.size(u)), np.cos(v))

        # Add as surface
        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            opacity=0.1,
            colorscale=[[0, 'rgba(200, 200, 200, 0.1)'], [1, 'rgba(200, 200, 200, 0.1)']],
            showscale=False,
            hoverinfo='skip',
            name='Head'
        ))

    def _add_topographic_surface(
        self,
        fig: go.Figure,
        electrode_positions: Dict[str, np.ndarray],
        powers: np.ndarray
    ):
        """Add interpolated topographic surface"""
        from scipy.interpolate import griddata

        # Extract positions and values
        positions = np.array(list(electrode_positions.values()))
        values = powers[:len(positions)]

        # Create interpolation grid on sphere surface
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi / 2, 25)  # Top hemisphere only
        x_grid = 0.75 * np.outer(np.cos(u), np.sin(v))
        y_grid = 0.75 * np.outer(np.sin(u), np.sin(v))
        z_grid = 0.75 * np.outer(np.ones(np.size(u)), np.cos(v))

        # Flatten grid
        points_grid = np.column_stack([x_grid.ravel(), y_grid.ravel(), z_grid.ravel()])

        # Interpolate (using 2D projection for simplicity)
        values_interp = griddata(
            positions[:, :2],  # XY positions only
            values,
            points_grid[:, :2],  # XY grid only
            method='cubic',
            fill_value=0
        )

        # Reshape
        values_interp = values_interp.reshape(x_grid.shape)

        # Add surface
        fig.add_trace(go.Surface(
            x=x_grid,
            y=y_grid,
            z=z_grid,
            surfacecolor=values_interp,
            colorscale='Hot',
            opacity=0.6,
            showscale=True,
            colorbar=dict(
                title='Power',
                thickness=20,
                len=0.7,
                x=1.1
            ),
            hoverinfo='skip',
            name='Topography'
        ))

    # ============================================================
    # MEDITATION JOURNEY
    # ============================================================

    def create_meditation_journey(
        self,
        output_path: str,
        method: str = 'umap'
    ):
        """
        Create animated 3D journey through meditation evolution

        Args:
            output_path: Output HTML file path
            method: Dimensionality reduction method
        """
        print("\n🌠 Creating meditation journey animation...")

        if not self.sessions:
            print("❌ No sessions loaded")
            return

        # Extract data
        latent_vectors = []
        depths = []
        dates = []
        session_ids = []

        for session in self.sessions:
            if 'latent_mean' in session and session['latent_mean'] is not None:
                latent_vectors.append(session['latent_mean'])
                depths.append(session.get('depth_score', 50))
                dates.append(session.get('recorded_at', ''))
                session_ids.append(session.get('session_id', ''))

        if len(latent_vectors) < 2:
            print("❌ Need at least 2 sessions")
            return

        latent_vectors = np.array(latent_vectors)

        # Reduce to 3D
        coords_3d = self._reduce_to_3d(latent_vectors, method)

        # Create animated figure
        fig = go.Figure()

        # Add traces for each frame (cumulative sessions)
        for i in range(1, len(coords_3d) + 1):
            # Points up to frame i
            fig.add_trace(go.Scatter3d(
                x=coords_3d[:i, 0],
                y=coords_3d[:i, 1],
                z=coords_3d[:i, 2],
                mode='markers+lines',
                marker=dict(
                    size=8,
                    color=depths[:i],
                    colorscale=[[0, '#3949ab'], [0.5, '#5e35b1'], [1, '#7c4dff']],
                    showscale=True,
                    colorbar=dict(title='Depth'),
                    line=dict(color='white', width=1)
                ),
                line=dict(color='rgba(124, 77, 255, 0.5)', width=2),
                text=session_ids[:i],
                hovertemplate='<b>%{text}</b><br>Depth: %{marker.color:.1f}<extra></extra>',
                visible=(i == len(coords_3d))  # Only last frame visible initially
            ))

        # Create slider steps
        steps = []
        for i in range(len(fig.data)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)},
                      {"title": f"Meditation Journey - Session {i + 1}/{len(coords_3d)}"}],
                label=str(i + 1)
            )
            step["args"][0]["visible"][i] = True
            steps.append(step)

        # Create slider
        sliders = [dict(
            active=len(coords_3d) - 1,
            yanchor="top",
            y=0.1,
            xanchor="left",
            x=0.1,
            currentvalue=dict(
                prefix="Session: ",
                visible=True,
                xanchor="right"
            ),
            pad=dict(b=10, t=50),
            len=0.9,
            steps=steps
        )]

        # Update layout
        fig.update_layout(
            title=f'Meditation Journey - Session {len(coords_3d)}/{len(coords_3d)}',
            scene=dict(
                xaxis=dict(title=f'{method.upper()} 1', backgroundcolor=self.bg_color, gridcolor=self.grid_color),
                yaxis=dict(title=f'{method.upper()} 2', backgroundcolor=self.bg_color, gridcolor=self.grid_color),
                zaxis=dict(title=f'{method.upper()} 3', backgroundcolor=self.bg_color, gridcolor=self.grid_color),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            sliders=sliders,
            paper_bgcolor=self.paper_color,
            plot_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            width=1200,
            height=900
        )

        # Save
        fig.write_html(output_path)
        print(f"   ✅ Saved: {output_path}")

        return fig

    # ============================================================
    # EXPORT FOR VR / BLENDER
    # ============================================================

    def export_for_vr(
        self,
        output_dir: str,
        method: str = 'umap'
    ):
        """
        Export VR-ready data (JSON + OBJ meshes)

        Args:
            output_dir: Output directory
            method: Dimensionality reduction method
        """
        print("\n🥽 Exporting for VR...")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract data
        latent_vectors = []
        session_metadata = []

        for session in self.sessions:
            if 'latent_mean' in session and session['latent_mean'] is not None:
                latent_vectors.append(session['latent_mean'])
                session_metadata.append({
                    'session_id': session.get('session_id', ''),
                    'depth': session.get('depth_score', 50),
                    'quality': session.get('quality_score', 50),
                    'date': session.get('recorded_at', '')
                })

        if len(latent_vectors) < 2:
            print("❌ Need at least 2 sessions")
            return

        latent_vectors = np.array(latent_vectors)

        # Reduce to 3D
        coords_3d = self._reduce_to_3d(latent_vectors, method)

        # Save as JSON
        vr_data = {
            'method': method,
            'n_sessions': len(coords_3d),
            'positions': coords_3d.tolist(),
            'sessions': session_metadata
        }

        json_path = output_dir / 'vr_meditation_space.json'
        with open(json_path, 'w') as f:
            json.dump(vr_data, f, indent=2)

        print(f"   ✅ Saved VR data: {json_path}")

        # Create simple OBJ sphere meshes for each point
        for i, pos in enumerate(coords_3d):
            self._export_sphere_obj(
                output_dir / f'session_{i:03d}.obj',
                center=pos,
                radius=0.1
            )

        print(f"   ✅ Saved {len(coords_3d)} OBJ meshes")
        print(f"\n📁 VR export complete: {output_dir.absolute()}")

    def _export_sphere_obj(self, filepath: Path, center: np.ndarray, radius: float):
        """Export simple sphere as OBJ file"""
        # Create sphere vertices
        u = np.linspace(0, 2 * np.pi, 10)
        v = np.linspace(0, np.pi, 10)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]

        # Write OBJ
        with open(filepath, 'w') as f:
            f.write(f"# Meditation session sphere\n")
            # Vertices
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    f.write(f"v {x[i,j]:.6f} {y[i,j]:.6f} {z[i,j]:.6f}\n")


if __name__ == "__main__":
    """
    Test 3D visualization
    """
    print("=" * 60)
    print("  🌌 3D Visualization Test")
    print("=" * 60)
    print()

    # Create mock sessions
    np.random.seed(42)
    n_sessions = 30
    sessions = []

    for i in range(n_sessions):
        # Simulate gradual improvement
        base_depth = 30 + i * 1.5 + np.random.randn() * 10
        base_depth = np.clip(base_depth, 0, 100)

        sessions.append({
            'session_id': f'session_{i:03d}',
            'latent_mean': np.random.randn(32),
            'depth_score': base_depth,
            'quality_score': 80 + np.random.randn() * 10,
            'performance_ratios': {'alpha_plus': 0.8 + i * 0.02},
            'recorded_at': f'2025-01-{i+1:02d}',
            'eeg_data': np.random.randn(4, 2560)  # 4 channels, 10 seconds @ 256Hz
        })

    # Create visualization
    viz = Visualization3D(sessions, theme='dark')

    # Test latent space
    viz.create_latent_space_3d(
        'test_latent_3d.html',
        method='umap',
        color_by='depth',
        show_trajectory=True
    )

    # Test brain activity
    viz.create_brain_activity_3d(
        sessions[0],
        'test_brain_3d.html'
    )

    # Test journey
    viz.create_meditation_journey(
        'test_journey_3d.html',
        method='umap'
    )

    # Test VR export
    viz.export_for_vr('test_vr_export', method='umap')

    print("\n✅ Test complete!")
    print("\nGenerated files:")
    print("  - test_latent_3d.html")
    print("  - test_brain_3d.html")
    print("  - test_journey_3d.html")
    print("  - test_vr_export/")
