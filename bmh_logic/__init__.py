"""Boyer-Moore-Horspool algorithm package."""

from .core import (
    BMHStep,
    bmh_find_all,
    bmh_search,
    bmh_trace,
    build_skip_table,
    display_char,
    visual_char,
)

__all__ = [
    "BMHStep",
    "bmh_find_all",
    "bmh_search",
    "bmh_trace",
    "build_skip_table",
    "display_char",
    "visual_char",
]

__version__ = "1.0.0"
