"""
Logging Configuration for THE LISTENER

Centralized logging setup with:
- Structured logging to files and console
- Log rotation
- Different log levels for different components
- Performance tracking
- Error tracking with stack traces

Usage:
    from src.utils.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("Processing session", session_id="session_001", depth=75.3)
    logger.error("Failed to generate image", exc_info=True)
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'depth'):
            log_data['depth'] = record.depth
        if hasattr(record, 'quality'):
            log_data['quality'] = record.quality

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output
    """

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Color the level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # Format the message
        formatted = super().format(record)

        return formatted


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    console_output: bool = True,
    json_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for THE LISTENER

    Args:
        log_dir: Directory for log files
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console logging
        json_output: Enable JSON file logging
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # ============================================================
    # CONSOLE HANDLER (colored, human-readable)
    # ============================================================
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        console_formatter = ColoredFormatter(
            '%(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # ============================================================
    # FILE HANDLER - JSON (structured, for analysis)
    # ============================================================
    if json_output:
        json_file = log_path / f"listener_{datetime.now().strftime('%Y%m%d')}.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        json_handler.setLevel(logging.DEBUG)  # Log everything to file
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)

    # ============================================================
    # FILE HANDLER - TEXT (human-readable, for debugging)
    # ============================================================
    text_file = log_path / f"listener_{datetime.now().strftime('%Y%m%d')}.log"
    text_handler = logging.handlers.RotatingFileHandler(
        text_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    text_handler.setLevel(logging.DEBUG)

    text_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    text_handler.setFormatter(text_formatter)
    root_logger.addHandler(text_handler)

    # ============================================================
    # ERROR FILE HANDLER (errors only)
    # ============================================================
    error_file = log_path / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(text_formatter)
    root_logger.addHandler(error_handler)

    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized",
        extra={
            'log_dir': str(log_path.absolute()),
            'log_level': log_level,
            'console_output': console_output,
            'json_output': json_output
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing started")
        logger.error("Failed", exc_info=True)
    """
    return logging.getLogger(name)


def log_session_metrics(
    logger: logging.Logger,
    session_id: str,
    depth: float,
    quality: float,
    duration: float,
    level: str = "INFO"
):
    """
    Log session metrics in a structured way

    Args:
        logger: Logger instance
        session_id: Session identifier
        depth: Meditation depth score
        quality: Signal quality score
        duration: Session duration in seconds
        level: Log level
    """
    log_level = getattr(logging, level.upper())
    logger.log(
        log_level,
        f"Session completed: {session_id}",
        extra={
            'session_id': session_id,
            'depth': depth,
            'quality': quality,
            'duration': duration
        }
    )


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    success: bool = True
):
    """
    Log performance metrics

    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        success: Whether operation succeeded
    """
    logger.info(
        f"Performance: {operation}",
        extra={
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success
        }
    )


# ============================================================
# CONTEXT MANAGER FOR TIMING
# ============================================================

class LogTimer:
    """
    Context manager for timing and logging operations

    Usage:
        with LogTimer(logger, "VAE encoding"):
            latent = vae.encode(features)
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: str = "DEBUG"
    ):
        self.logger = logger
        self.operation = operation
        self.level = getattr(logging, level.upper())
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (datetime.now() - self.start_time).total_seconds() * 1000

        if exc_type is None:
            self.logger.log(
                self.level,
                f"Completed: {self.operation} ({duration_ms:.1f}ms)"
            )
        else:
            self.logger.error(
                f"Failed: {self.operation} ({duration_ms:.1f}ms)",
                exc_info=(exc_type, exc_val, exc_tb)
            )

        return False  # Don't suppress exceptions


# ============================================================
# DECORATOR FOR AUTOMATIC LOGGING
# ============================================================

def log_function_call(logger: Optional[logging.Logger] = None):
    """
    Decorator to automatically log function calls

    Usage:
        @log_function_call()
        def process_session(session_id):
            ...
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)

        def wrapper(*args, **kwargs):
            logger.debug(
                f"Calling {func.__name__}",
                extra={
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate long args
                    'kwargs': str(kwargs)[:100]
                }
            )

            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result

            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    """
    Test logging configuration
    """
    print("=" * 60)
    print("  🪵 Logging Configuration Test")
    print("=" * 60)
    print()

    # Setup logging
    setup_logging(
        log_dir="logs",
        log_level="DEBUG",
        console_output=True,
        json_output=True
    )

    # Test different loggers
    logger = get_logger(__name__)

    logger.debug("This is a debug message")
    logger.info("Session started successfully")
    logger.warning("Signal quality is low")
    logger.error("Failed to generate image")

    # Test structured logging
    log_session_metrics(
        logger,
        session_id="session_001",
        depth=75.3,
        quality=92.1,
        duration=600
    )

    # Test performance logging
    log_performance(
        logger,
        operation="VAE encoding",
        duration_ms=123.4,
        success=True
    )

    # Test timer context manager
    with LogTimer(logger, "Test operation"):
        import time
        time.sleep(0.1)

    # Test function decorator
    @log_function_call()
    def test_function(x, y):
        return x + y

    result = test_function(5, 3)

    # Test error logging
    try:
        1 / 0
    except Exception:
        logger.error("Division by zero", exc_info=True)

    print()
    print("✅ Logging test complete!")
    print()
    print("Check logs/ directory for output files:")
    print("  - listener_YYYYMMDD.log (human-readable)")
    print("  - listener_YYYYMMDD.json (structured)")
    print("  - errors_YYYYMMDD.log (errors only)")
