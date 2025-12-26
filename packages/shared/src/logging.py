"""
Logging utilities for BLACKICE.

Provides structured logging with rich output.
"""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


# BLACKICE theme - cyberpunk aesthetic
blackice_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "ice": "bold blue",
    "synth": "magenta",
})

# Global console for rich output
console = Console(theme=blackice_theme)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Use RichHandler for pretty output
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    if level is not None:
        logger.setLevel(level)
    elif logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)

    return logger


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Setup logging for the entire application.

    Args:
        verbose: Enable verbose output
        debug: Enable debug output
    """
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            RichHandler(
                console=console,
                show_time=True,
                show_path=debug,
                rich_tracebacks=True,
                markup=True,
            )
        ],
    )

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def ice_print(message: str, style: str = "ice") -> None:
    """Print a styled message to console."""
    console.print(f"[{style}]{message}[/{style}]")


def success(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]{message}[/success]")


def error(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]{message}[/error]")


def warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]{message}[/warning]")


def banner() -> None:
    """Print the BLACKICE banner."""
    console.print("""
[bold blue]
 ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██╗ ██████╗███████╗
 ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██║██╔════╝██╔════╝
 ██████╔╝██║     ███████║██║     █████╔╝ ██║██║     █████╗
 ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║██║     ██╔══╝
 ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██║╚██████╗███████╗
 ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
[/bold blue]
[dim]Neuro-symbolic software factory[/dim]
""")
