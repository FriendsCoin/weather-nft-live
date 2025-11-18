"""
Rich CLI Utilities - THE LISTENER

Beautiful command-line interface components using Rich library.

Usage:
    from src.utils.rich_cli import console, create_progress, create_table

    console.print("[bold green]✓[/bold green] Success!")

    with create_progress() as progress:
        task = progress.add_task("Processing...", total=100)
        for i in range(100):
            progress.update(task, advance=1)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import sys

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
        MofNCompleteColumn
    )
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Global console instance
if RICH_AVAILABLE:
    console = Console()
else:
    # Fallback console for when Rich is not installed
    class FallbackConsole:
        """Fallback console when Rich is not available"""

        def print(self, *args, **kwargs):
            """Print without Rich formatting"""
            # Strip Rich markup
            text = ' '.join(str(arg) for arg in args)
            # Remove Rich tags
            import re
            text = re.sub(r'\[.*?\]', '', text)
            print(text)

        def log(self, *args, **kwargs):
            """Log without Rich formatting"""
            self.print(*args, **kwargs)

        def rule(self, title="", **kwargs):
            """Print a horizontal rule"""
            print("=" * 70)
            if title:
                print(f"  {title}")
                print("=" * 70)

    console = FallbackConsole()


def create_progress(description: str = "Processing") -> Optional[Progress]:
    """
    Create a Rich progress bar.

    Args:
        description: Default task description

    Returns:
        Progress object or None if Rich not available

    Example:
        with create_progress() as progress:
            task = progress.add_task("Loading...", total=100)
            for i in range(100):
                progress.update(task, advance=1)
    """
    if not RICH_AVAILABLE:
        return None

    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console
    )


def create_table(
    title: str,
    columns: List[str],
    rows: List[List[Any]],
    show_header: bool = True,
    show_lines: bool = False,
    box_style: str = "rounded"
) -> Optional[Table]:
    """
    Create a Rich table.

    Args:
        title: Table title
        columns: Column headers
        rows: Table rows (list of lists)
        show_header: Show column headers
        show_lines: Show lines between rows
        box_style: Box style (rounded, simple, heavy, etc.)

    Returns:
        Table object or None if Rich not available

    Example:
        table = create_table(
            "Sessions",
            ["ID", "Duration", "Depth"],
            [
                ["session_001", "600s", "85.2"],
                ["session_002", "720s", "92.1"]
            ]
        )
        console.print(table)
    """
    if not RICH_AVAILABLE:
        return None

    # Map box style names
    box_styles = {
        'rounded': box.ROUNDED,
        'simple': box.SIMPLE,
        'heavy': box.HEAVY,
        'double': box.DOUBLE,
        'minimal': box.MINIMAL
    }

    table = Table(
        title=title,
        show_header=show_header,
        show_lines=show_lines,
        box=box_styles.get(box_style, box.ROUNDED)
    )

    # Add columns
    for col in columns:
        table.add_column(col, style="cyan")

    # Add rows
    for row in rows:
        table.add_row(*[str(cell) for cell in row])

    return table


def print_header(text: str, style: str = "bold blue"):
    """
    Print a section header.

    Args:
        text: Header text
        style: Rich style string

    Example:
        print_header("Loading Sessions")
    """
    if RICH_AVAILABLE:
        console.rule(f"[{style}]{text}[/{style}]")
    else:
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)


def print_success(text: str):
    """Print success message"""
    if RICH_AVAILABLE:
        console.print(f"[bold green]✓[/bold green] {text}")
    else:
        print(f"✓ {text}")


def print_error(text: str):
    """Print error message"""
    if RICH_AVAILABLE:
        console.print(f"[bold red]✗[/bold red] {text}")
    else:
        print(f"✗ {text}")


def print_warning(text: str):
    """Print warning message"""
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠[/bold yellow] {text}")
    else:
        print(f"⚠ {text}")


def print_info(text: str):
    """Print info message"""
    if RICH_AVAILABLE:
        console.print(f"[bold cyan]ℹ[/bold cyan] {text}")
    else:
        print(f"ℹ {text}")


def create_panel(
    content: str,
    title: str = "",
    border_style: str = "blue",
    padding: int = 1
) -> Optional[Panel]:
    """
    Create a Rich panel.

    Args:
        content: Panel content
        title: Panel title
        border_style: Border color/style
        padding: Padding inside panel

    Returns:
        Panel object or None if Rich not available

    Example:
        panel = create_panel(
            "System is healthy!",
            title="Health Check",
            border_style="green"
        )
        console.print(panel)
    """
    if not RICH_AVAILABLE:
        return None

    return Panel(
        content,
        title=title,
        border_style=border_style,
        padding=(padding, padding * 2)
    )


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "5m 30s", "1h 15m")
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        mins = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds / 3600)
        mins = int((seconds % 3600) / 60)
        return f"{hours}h {mins}m"


def format_timestamp(dt: datetime) -> str:
    """
    Format timestamp in human-readable form.

    Args:
        dt: Datetime object

    Returns:
        Formatted string (e.g., "2024-01-15 14:30")
    """
    return dt.strftime("%Y-%m-%d %H:%M")


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with appropriate precision.

    Args:
        value: Number to format
        decimals: Decimal places

    Returns:
        Formatted string
    """
    if value >= 1000:
        return f"{value/1000:.1f}k"
    else:
        return f"{value:.{decimals}f}"


def is_rich_available() -> bool:
    """Check if Rich library is available"""
    return RICH_AVAILABLE


# Fallback progress for when Rich is not available
class FallbackProgress:
    """Simple progress indicator when Rich is not available"""

    def __init__(self, description: str = "Processing"):
        self.description = description
        self.tasks = {}
        self.task_counter = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        print()  # New line after progress

    def add_task(self, description: str, total: int = 100) -> int:
        """Add a task and return task ID"""
        task_id = self.task_counter
        self.tasks[task_id] = {
            'description': description,
            'completed': 0,
            'total': total
        }
        self.task_counter += 1
        print(f"{description}... ", end='', flush=True)
        return task_id

    def update(self, task_id: int, advance: int = 1):
        """Update task progress"""
        if task_id in self.tasks:
            self.tasks[task_id]['completed'] += advance
            task = self.tasks[task_id]
            if task['completed'] >= task['total']:
                print("✓")

    def console(self):
        """Return fallback console"""
        return console


def get_progress(description: str = "Processing"):
    """
    Get progress bar (Rich if available, fallback otherwise).

    Args:
        description: Default task description

    Returns:
        Progress object

    Example:
        with get_progress() as progress:
            task = progress.add_task("Loading...", total=100)
            for i in range(100):
                progress.update(task, advance=1)
    """
    if RICH_AVAILABLE:
        return create_progress(description)
    else:
        return FallbackProgress(description)
