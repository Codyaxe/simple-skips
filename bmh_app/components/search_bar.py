"""Search and replace bar component."""

from typing import Callable, Dict, Optional

import tkinter as tk
from tkinter import ttk


class SearchBar:
    """Search/find/replace control bar."""

    def __init__(
        self, parent: ttk.Frame, find_var: tk.StringVar, replace_var: tk.StringVar
    ) -> None:
        """Initialize search bar."""
        self.find_var = find_var
        self.replace_var = replace_var
        self.callbacks: Dict[str, Callable[[], None]] = {}

        search_row = ttk.Frame(parent)
        search_row.pack(fill=tk.X, pady=(0, 8))

        # Find section
        ttk.Label(search_row, text="Find").pack(side=tk.LEFT)
        ttk.Entry(search_row, textvariable=self.find_var, width=20).pack(
            side=tk.LEFT, padx=(6, 10)
        )

        # Replace section
        ttk.Label(search_row, text="Replace").pack(side=tk.LEFT)
        ttk.Entry(search_row, textvariable=self.replace_var, width=20).pack(
            side=tk.LEFT, padx=(6, 10)
        )

        # Buttons
        ttk.Button(search_row, text="Find Next", command=self._on_find_next).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Find All", command=self._on_find_all).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Replace Next", command=self._on_replace_next).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Replace All", command=self._on_replace_all).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Clear Marks", command=self._on_clear_marks).pack(
            side=tk.LEFT
        )

    def set_callback(self, name: str, callback: Callable[[], None]) -> None:
        """Register callback for button action."""
        self.callbacks[name] = callback

    def _on_find_next(self) -> None:
        if "find_next" in self.callbacks:
            self.callbacks["find_next"]()

    def _on_find_all(self) -> None:
        if "find_all" in self.callbacks:
            self.callbacks["find_all"]()

    def _on_replace_next(self) -> None:
        if "replace_next" in self.callbacks:
            self.callbacks["replace_next"]()

    def _on_replace_all(self) -> None:
        if "replace_all" in self.callbacks:
            self.callbacks["replace_all"]()

    def _on_clear_marks(self) -> None:
        if "clear_marks" in self.callbacks:
            self.callbacks["clear_marks"]()
