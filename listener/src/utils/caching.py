"""
Caching utilities for THE LISTENER

Improves performance by caching expensive operations like:
- Feature extraction
- Model predictions
- Preprocessing results
"""

import os
import pickle
import hashlib
import json
from pathlib import Path
from typing import Any, Optional, Callable, Dict
from functools import wraps
import time


class Cache:
    """Simple file-based cache for expensive operations"""

    def __init__(self, cache_dir: str = "data/cache", enabled: bool = True):
        """
        Initialize cache

        Args:
            cache_dir: Directory to store cache files
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        # Create a string representation of args and kwargs
        key_data = {
            'args': [str(arg) for arg in args],
            'kwargs': {k: str(v) for k, v in sorted(kwargs.items())}
        }
        key_string = json.dumps(key_data, sort_keys=True)

        # Hash it for consistent filename
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_path(self, func_name: str, cache_key: str) -> Path:
        """Get path to cache file"""
        return self.cache_dir / f"{func_name}_{cache_key}.pkl"

    def get(self, func_name: str, *args, **kwargs) -> Optional[Any]:
        """
        Get cached result

        Args:
            func_name: Name of the function
            *args, **kwargs: Function arguments

        Returns:
            Cached result if found, None otherwise
        """
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(*args, **kwargs)
        cache_path = self._get_cache_path(func_name, cache_key)

        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)

                # Check if cache has expired (24 hours by default)
                cache_age = time.time() - cache_path.stat().st_mtime
                if cache_age < 24 * 3600:  # 24 hours
                    return cached_data['result']

            except Exception as e:
                # If cache is corrupted, delete it
                cache_path.unlink()

        return None

    def set(self, func_name: str, result: Any, *args, **kwargs):
        """
        Store result in cache

        Args:
            func_name: Name of the function
            result: Result to cache
            *args, **kwargs: Function arguments
        """
        if not self.enabled:
            return

        cache_key = self._get_cache_key(*args, **kwargs)
        cache_path = self._get_cache_path(func_name, cache_key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'result': result,
                    'timestamp': time.time()
                }, f)
        except Exception:
            # If we can't cache, just continue
            pass

    def clear(self, func_name: Optional[str] = None):
        """
        Clear cache

        Args:
            func_name: If provided, only clear cache for this function
        """
        if not self.enabled:
            return

        if func_name:
            # Clear specific function cache
            pattern = f"{func_name}_*.pkl"
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()

    def info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {'enabled': False}

        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'enabled': True,
            'num_entries': len(cache_files),
            'total_size_mb': total_size / 1024 / 1024,
            'cache_dir': str(self.cache_dir)
        }


# Global cache instance
_global_cache = Cache()


def cached(func: Optional[Callable] = None, *, cache_instance: Optional[Cache] = None, ttl: int = 24 * 3600):
    """
    Decorator to cache function results

    Args:
        func: Function to cache
        cache_instance: Cache instance to use (default: global cache)
        ttl: Time to live in seconds (default: 24 hours)

    Usage:
        @cached
        def expensive_function(x, y):
            return x + y

        # Or with custom cache
        my_cache = Cache("custom_cache")

        @cached(cache_instance=my_cache)
        def another_function(x):
            return x * 2
    """
    def decorator(f):
        cache = cache_instance or _global_cache

        @wraps(f)
        def wrapper(*args, **kwargs):
            # Try to get from cache
            result = cache.get(f.__name__, *args, **kwargs)

            if result is not None:
                return result

            # Compute result
            result = f(*args, **kwargs)

            # Store in cache
            cache.set(f.__name__, result, *args, **kwargs)

            return result

        # Add cache control methods
        wrapper.clear_cache = lambda: cache.clear(f.__name__)
        wrapper.cache_info = lambda: cache.info()

        return wrapper

    # Handle both @cached and @cached()
    if func is None:
        return decorator
    else:
        return decorator(func)


class SessionCache:
    """Specialized cache for EEG session data"""

    def __init__(self, cache_dir: str = "data/cache/sessions"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file contents for cache invalidation"""
        path = Path(file_path)
        # Use file size and modification time as quick hash
        stat = path.stat()
        return hashlib.md5(f"{stat.st_size}_{stat.st_mtime}".encode()).hexdigest()

    def get_processed_session(self, session_path: str, processing_stage: str) -> Optional[Any]:
        """
        Get cached processed session data

        Args:
            session_path: Path to original session file
            processing_stage: Stage of processing (e.g., "preprocessed", "features")

        Returns:
            Cached data if available and valid, None otherwise
        """
        file_hash = self._get_file_hash(session_path)
        session_name = Path(session_path).stem
        cache_file = self.cache_dir / f"{session_name}_{processing_stage}_{file_hash}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                # Corrupted cache, delete it
                cache_file.unlink()

        return None

    def set_processed_session(self, session_path: str, processing_stage: str, data: Any):
        """
        Cache processed session data

        Args:
            session_path: Path to original session file
            processing_stage: Stage of processing
            data: Data to cache
        """
        file_hash = self._get_file_hash(session_path)
        session_name = Path(session_path).stem
        cache_file = self.cache_dir / f"{session_name}_{processing_stage}_{file_hash}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except:
            pass

    def clear_session(self, session_path: str):
        """Clear all cached data for a session"""
        session_name = Path(session_path).stem
        for cache_file in self.cache_dir.glob(f"{session_name}_*.pkl"):
            cache_file.unlink()

    def clear_all(self):
        """Clear all session cache"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()


class ModelCache:
    """Cache for model predictions and embeddings"""

    def __init__(self, cache_dir: str = "data/cache/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_model_hash(self, model_path: str) -> str:
        """Get hash of model file"""
        path = Path(model_path)
        if not path.exists():
            return "no_model"
        stat = path.stat()
        return hashlib.md5(f"{stat.st_size}_{stat.st_mtime}".encode()).hexdigest()

    def get_embeddings(self, model_path: str, session_id: str) -> Optional[Any]:
        """Get cached embeddings for a session"""
        model_hash = self._get_model_hash(model_path)
        cache_file = self.cache_dir / f"embeddings_{session_id}_{model_hash}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                cache_file.unlink()

        return None

    def set_embeddings(self, model_path: str, session_id: str, embeddings: Any):
        """Cache embeddings for a session"""
        model_hash = self._get_model_hash(model_path)
        cache_file = self.cache_dir / f"embeddings_{session_id}_{model_hash}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embeddings, f)
        except:
            pass


# Convenience function
def clear_all_caches():
    """Clear all caches"""
    _global_cache.clear()
    SessionCache().clear_all()
    ModelCache().clear_all()
    print("✓ All caches cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about all caches"""
    stats = {
        'global': _global_cache.info(),
        'sessions': {},
        'models': {}
    }

    # Session cache stats
    session_cache_dir = Path("data/cache/sessions")
    if session_cache_dir.exists():
        files = list(session_cache_dir.glob("*.pkl"))
        size = sum(f.stat().st_size for f in files)
        stats['sessions'] = {
            'num_entries': len(files),
            'total_size_mb': size / 1024 / 1024
        }

    # Model cache stats
    model_cache_dir = Path("data/cache/models")
    if model_cache_dir.exists():
        files = list(model_cache_dir.glob("*.pkl"))
        size = sum(f.stat().st_size for f in files)
        stats['models'] = {
            'num_entries': len(files),
            'total_size_mb': size / 1024 / 1024
        }

    return stats
