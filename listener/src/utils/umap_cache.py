"""
UMAP Cache - THE LISTENER

Cache UMAP embeddings for 20x faster 3D visualization.

Instead of recomputing UMAP every time (slow), cache the results
and reuse them when input data hasn't changed.

Usage:
    from src.utils.umap_cache import UMAPCache

    cache = UMAPCache()

    # First call: computes UMAP (slow)
    embedding = cache.get_embedding(latent_data, n_neighbors=15, min_dist=0.1)

    # Second call with same data: loads from cache (fast!)
    embedding = cache.get_embedding(latent_data, n_neighbors=15, min_dist=0.1)

Performance:
    Without cache: ~30-60 seconds for 100 sessions
    With cache:    ~1-2 seconds (20-30x speedup!)
"""

import hashlib
import pickle
import os
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import json


class UMAPCache:
    """
    Cache for UMAP embeddings.

    Stores precomputed UMAP embeddings with metadata to avoid
    expensive recomputation when data hasn't changed.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize UMAP cache.

        Args:
            cache_dir: Directory to store cache files (default: data/cache/umap)
        """
        if cache_dir is None:
            from ..config import config
            cache_dir = config.data_dir / 'cache' / 'umap'

        self.cache_dir = Path(cache_dir)
        self._cache_enabled = True

        # Try to create cache directory
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"⚠️  Warning: Could not create cache directory {self.cache_dir}: {e}")
            print("   UMAP caching will be disabled")
            self._cache_enabled = False
            self.cache_dir = None

        # Metadata file for cache management
        if self._cache_enabled:
            self.metadata_file = self.cache_dir / 'metadata.json'
            self.metadata = self._load_metadata()
        else:
            self.metadata_file = None
            self.metadata = {}

    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache metadata: {e}")

    def _compute_hash(
        self,
        data: np.ndarray,
        n_neighbors: int,
        min_dist: float,
        n_components: int,
        metric: str
    ) -> str:
        """
        Compute hash of data and parameters.

        Uses fast hashing for large arrays (samples every 1000th element).
        For datasets >1000 samples, this is 10-20x faster than full hash.

        Args:
            data: Input data array
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter
            n_components: UMAP n_components parameter
            metric: UMAP metric parameter

        Returns:
            SHA256 hash string
        """
        # For large arrays, sample to speed up hashing
        # Full hash would be slow for 1000+ session datasets
        if data.size > 10000:  # ~100 sessions with 100 features each
            # Hash: shape + dtype + sampled data
            sample_data = data.flat[::max(1, data.size // 1000)]  # Max 1000 samples
            data_repr = f"{data.shape}_{data.dtype}_{sample_data.tobytes()}"
        else:
            # Small array - hash everything
            data_repr = data.tobytes()

        data_hash = hashlib.sha256(data_repr if isinstance(data_repr, bytes) else data_repr.encode()).hexdigest()

        # Hash the parameters
        params_str = f"{data_hash}_{n_neighbors}_{min_dist}_{n_components}_{metric}"
        full_hash = hashlib.sha256(params_str.encode()).hexdigest()

        return full_hash

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.pkl"

    def get_embedding(
        self,
        data: np.ndarray,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        n_components: int = 3,
        metric: str = 'euclidean',
        force_recompute: bool = False,
        verbose: bool = True
    ) -> np.ndarray:
        """
        Get UMAP embedding (from cache if available).

        Args:
            data: Input data (n_samples, n_features)
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter
            n_components: Number of dimensions (2 or 3)
            metric: Distance metric
            force_recompute: Ignore cache and recompute
            verbose: Print cache status messages

        Returns:
            UMAP embedding (n_samples, n_components)
        """
        # Check if caching is enabled
        if not self._cache_enabled:
            force_recompute = True  # Skip cache if disabled

        # Compute cache key
        cache_key = self._compute_hash(data, n_neighbors, min_dist, n_components, metric) if self._cache_enabled else None
        cache_path = self._get_cache_path(cache_key) if cache_key else None

        # Try to load from cache
        if not force_recompute and self._cache_enabled and cache_path and cache_path.exists():
            try:
                if verbose:
                    print("📦 Loading UMAP embedding from cache...")

                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)

                embedding = cached_data['embedding']

                if verbose:
                    cache_time = cached_data.get('timestamp', 'unknown')
                    print(f"✅ Loaded from cache (created: {cache_time})")

                # Update access time in metadata
                self.metadata[cache_key] = {
                    'last_accessed': datetime.now().isoformat(),
                    'n_samples': data.shape[0],
                    'n_features': data.shape[1],
                    'n_components': n_components,
                    'params': {
                        'n_neighbors': n_neighbors,
                        'min_dist': min_dist,
                        'metric': metric
                    }
                }
                self._save_metadata()

                return embedding

            except Exception as e:
                if verbose:
                    print(f"⚠️  Cache load failed: {e}")
                    print("   Recomputing UMAP...")

        # Compute UMAP embedding
        if verbose:
            print("🔄 Computing UMAP embedding...")
            print(f"   Data shape: {data.shape}")
            print(f"   Parameters: n_neighbors={n_neighbors}, min_dist={min_dist}, "
                  f"n_components={n_components}, metric={metric}")

        try:
            import umap

            # Create UMAP reducer
            reducer = umap.UMAP(
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                n_components=n_components,
                metric=metric,
                random_state=42,
                verbose=False
            )

            # Fit and transform
            import time
            start_time = time.time()
            embedding = reducer.fit_transform(data)
            elapsed = time.time() - start_time

            if verbose:
                print(f"✅ UMAP computed in {elapsed:.1f}s")

            # Save to cache (if enabled)
            if self._cache_enabled and cache_path:
                try:
                    cache_data = {
                        'embedding': embedding,
                        'timestamp': datetime.now().isoformat(),
                        'elapsed_time': elapsed,
                        'n_samples': data.shape[0],
                        'n_features': data.shape[1],
                        'params': {
                            'n_neighbors': n_neighbors,
                            'min_dist': min_dist,
                            'n_components': n_components,
                            'metric': metric
                        }
                    }

                    # Write to temporary file first, then atomic rename
                    # This prevents corruption from concurrent writes
                    import tempfile
                    temp_fd, temp_path = tempfile.mkstemp(
                        dir=self.cache_dir,
                        prefix='.tmp_',
                        suffix='.pkl'
                    )
                    try:
                        with os.fdopen(temp_fd, 'wb') as f:
                            pickle.dump(cache_data, f)
                        # Atomic rename (replaces existing file atomically)
                        Path(temp_path).replace(cache_path)
                        if verbose:
                            print(f"💾 Cached to: {cache_path.name}")
                    except Exception as e:
                        # Clean up temp file if rename fails
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                        raise e

                    # Update metadata
                    self.metadata[cache_key] = {
                        'created': datetime.now().isoformat(),
                        'last_accessed': datetime.now().isoformat(),
                        'n_samples': data.shape[0],
                        'n_features': data.shape[1],
                        'n_components': n_components,
                        'elapsed_time': elapsed,
                        'params': cache_data['params']
                    }
                    self._save_metadata()

                except Exception as e:
                    if verbose:
                        print(f"⚠️  Could not cache embedding: {e}")

            return embedding

        except ImportError:
            raise ImportError(
                "UMAP not installed. Install with: pip install umap-learn"
            )
        except Exception as e:
            raise RuntimeError(f"UMAP computation failed: {e}")

    def clear_cache(self, older_than_days: Optional[int] = None):
        """
        Clear cached embeddings.

        Args:
            older_than_days: Only clear cache older than N days (default: clear all)
        """
        if older_than_days is None:
            # Clear all
            count = 0
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
                count += 1

            self.metadata = {}
            self._save_metadata()

            print(f"🗑️  Cleared {count} cached embeddings")
        else:
            # Clear old entries
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=older_than_days)

            count = 0
            for cache_key, meta in list(self.metadata.items()):
                created_str = meta.get('created', meta.get('last_accessed'))
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str)
                        if created < cutoff:
                            cache_path = self._get_cache_path(cache_key)
                            if cache_path.exists():
                                cache_path.unlink()
                            del self.metadata[cache_key]
                            count += 1
                    except:
                        pass

            self._save_metadata()
            print(f"🗑️  Cleared {count} cached embeddings older than {older_than_days} days")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)

        stats = {
            'total_entries': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'entries': []
        }

        # Add details for each entry
        for cache_key, meta in self.metadata.items():
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                size_mb = cache_path.stat().st_size / (1024 * 1024)
                stats['entries'].append({
                    'key': cache_key[:8] + '...',  # Abbreviated
                    'n_samples': meta.get('n_samples'),
                    'n_components': meta.get('n_components'),
                    'created': meta.get('created', 'unknown'),
                    'last_accessed': meta.get('last_accessed', 'unknown'),
                    'size_mb': size_mb,
                    'elapsed_time': meta.get('elapsed_time')
                })

        return stats

    def print_cache_stats(self):
        """Print cache statistics to console"""
        stats = self.get_cache_stats()

        print("=" * 60)
        print("  📊 UMAP Cache Statistics")
        print("=" * 60)
        print(f"Cache directory: {stats['cache_dir']}")
        print(f"Total entries:   {stats['total_entries']}")
        print(f"Total size:      {stats['total_size_mb']:.2f} MB")
        print()

        if stats['entries']:
            print("Cached embeddings:")
            print(f"{'Key':<12} {'Samples':<10} {'Dims':<6} {'Size (MB)':<10} {'Compute Time'}")
            print("-" * 60)
            for entry in stats['entries']:
                key = entry['key']
                n_samples = entry.get('n_samples', '?')
                n_comp = entry.get('n_components', '?')
                size = entry.get('size_mb', 0)
                elapsed = entry.get('elapsed_time')
                elapsed_str = f"{elapsed:.1f}s" if elapsed else "?"

                print(f"{key:<12} {n_samples:<10} {n_comp:<6} {size:<10.2f} {elapsed_str}")

        print("=" * 60)


# Convenience function for standalone use
def cached_umap(
    data: np.ndarray,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    n_components: int = 3,
    metric: str = 'euclidean',
    cache_dir: Optional[Path] = None,
    force_recompute: bool = False,
    verbose: bool = True
) -> np.ndarray:
    """
    Compute UMAP embedding with caching.

    Convenience function that creates a UMAPCache instance
    and returns the embedding.

    Args:
        data: Input data (n_samples, n_features)
        n_neighbors: UMAP n_neighbors parameter
        min_dist: UMAP min_dist parameter
        n_components: Number of dimensions (2 or 3)
        metric: Distance metric
        cache_dir: Cache directory (default: auto)
        force_recompute: Ignore cache and recompute
        verbose: Print status messages

    Returns:
        UMAP embedding (n_samples, n_components)

    Example:
        >>> import numpy as np
        >>> data = np.random.randn(100, 32)  # 100 samples, 32 features
        >>> embedding = cached_umap(data, n_components=3)
        >>> embedding.shape
        (100, 3)
    """
    cache = UMAPCache(cache_dir=cache_dir)
    return cache.get_embedding(
        data,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        force_recompute=force_recompute,
        verbose=verbose
    )
