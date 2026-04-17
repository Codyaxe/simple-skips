"""Editor panel component - main text editing area."""

from typing import Dict

import tkinter as tk
from tkinter import ttk

from ..core.theme_manager import ThemeManager


class EditorPanel:
    """Main text editor area with scrollbars and syntax highlighting."""

    def __init__(self, parent: ttk.Frame, theme: ThemeManager) -> None:
        """Initialize editor panel."""
        self.theme = theme

        # Main text widget
        self.editor = tk.Text(parent, wrap=tk.NONE, undo=True, font=("Consolas", 11))
        self.editor.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        self.editor_y_scroll = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=self.editor.yview,
            style="Minimal.Vertical.TScrollbar",
        )
        self.editor_y_scroll.grid(row=0, column=1, sticky="ns")

        self.editor_x_scroll = ttk.Scrollbar(
            parent,
            orient=tk.HORIZONTAL,
            command=self.editor.xview,
            style="Minimal.Horizontal.TScrollbar",
        )
        self.editor_x_scroll.grid(row=1, column=0, sticky="ew")

        # Corner fill
        self.scroll_corner = tk.Frame(parent, bd=0, highlightthickness=0)
        self.scroll_corner.grid(row=1, column=1, sticky="nsew")

        # Configure editor
        self.editor.configure(
            yscrollcommand=self.editor_y_scroll.set,
            xscrollcommand=self.editor_x_scroll.set,
        )

        # Configure highlight tags
        self.editor.tag_configure("match", background="#ffe8a3")
        self.editor.tag_configure("current_match", background="#ffbe55")
        self.editor.tag_configure("trace_align", background="#dbeafe")
        self.editor.tag_configure("trace_match", background="#bbf7d0")
        self.editor.tag_configure("trace_mismatch", background="#fecaca")

        # Grid configuration
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=0)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme colors to editor."""
        self.theme.apply_text_widget_theme(self.editor, colors)
        self.scroll_corner.configure(background=colors["scroll_trough"])

    def get_content(self) -> str:
        """Get all text from editor."""
        return self.editor.get("1.0", "end-1c")

    def set_content(self, content: str) -> None:
        """Set editor content and clear modified flag."""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.editor.edit_modified(False)

    def clear_highlights(self) -> None:
        """Clear all search and trace highlights."""
        self.editor.tag_remove("match", "1.0", tk.END)
        self.editor.tag_remove("current_match", "1.0", tk.END)
        self.clear_trace_highlights()

    def clear_trace_highlights(self) -> None:
        """Clear trace-specific highlights."""
        self.editor.tag_remove("trace_align", "1.0", tk.END)
        self.editor.tag_remove("trace_match", "1.0", tk.END)
        self.editor.tag_remove("trace_mismatch", "1.0", tk.END)

    def highlight_range(
        self, start_offset: int, end_offset: int, current: bool = False
    ) -> None:
        """Highlight a range in the editor."""
        start_index = f"1.0+{start_offset}c"
        end_index = f"1.0+{end_offset}c"
        tag = "current_match" if current else "match"
        self.editor.tag_add(tag, start_index, end_index)

    def mark_trace_highlight(self, text_index: int, tag: str) -> None:
        """Add a trace highlight tag at an index."""
        self.editor.tag_add(
            tag,
            f"1.0+{text_index}c",
            f"1.0+{text_index + 1}c",
        )

    def set_insertion_point(self, offset: int) -> None:
        """Move cursor to offset and ensure visible."""
        self.editor.mark_set("insert", f"1.0+{offset}c")
        self.editor.see(f"1.0+{offset}c")

    def get_cursor_offset(self) -> int:
        """Get current cursor position as character offset."""
        count = self.editor.count("1.0", "insert", "chars")
        if not count:
            return 0
        return int(count[0])
