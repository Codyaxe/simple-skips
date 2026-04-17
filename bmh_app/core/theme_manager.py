"""Centralized theme and styling management."""

from typing import Any, Dict

import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """Manages all color schemes and ttk widget styling."""

    def __init__(self, style: ttk.Style) -> None:
        self.style = style
        self.colors: Dict[str, str] = {}

    def get_colors(self, dark: bool) -> Dict[str, str]:
        """Return color palette for dark or light mode."""
        if dark:
            return {
                "bg": "#1e1e1e",
                "panel": "#252526",
                "fg": "#e8e8e8",
                "muted": "#bcbcbc",
                "active": "#303033",
                "border": "#3c3c3c",
                "text_bg": "#1b1b1b",
                "text_fg": "#f2f2f2",
                "insert": "#f2f2f2",
                "select_bg": "#264f78",
                "select_fg": "#ffffff",
                "scroll_bg": "#343434",
                "scroll_trough": "#1e1e1e",
                "scroll_active": "#4a4a4a",
                "scroll_fg": "#d0d0d0",
                "button_border": "#4d4d4d",
                "button_active_border": "#6b6b6b",
                "input_border": "#575b63",
                "input_focus": "#7a818f",
                "box_border": "#4b4f56",
                "text_border": "#575b63",
            }
        else:
            return {
                "bg": "#f5f5f5",
                "panel": "#ffffff",
                "fg": "#1f1f1f",
                "muted": "#666666",
                "active": "#ececec",
                "border": "#d9d9d9",
                "text_bg": "#ffffff",
                "text_fg": "#000000",
                "insert": "#000000",
                "select_bg": "#cfe3ff",
                "select_fg": "#000000",
                "scroll_bg": "#dddddd",
                "scroll_trough": "#f8f8f8",
                "scroll_active": "#cfcfcf",
                "scroll_fg": "#6e6e6e",
                "button_border": "#d8d8d8",
                "button_active_border": "#c6c6c6",
                "input_border": "#dcdcdc",
                "input_focus": "#c6c6c6",
                "box_border": "#d6d6d6",
                "text_border": "#dddddd",
            }

    def apply_theme(self, root: tk.Tk, colors: Dict[str, str]) -> None:
        """Apply theme colors to all ttk widgets."""
        self.colors = colors
        self.style.theme_use("clam")

        # Base styles
        self.style.configure(
            ".",
            background=colors["bg"],
            foreground=colors["fg"],
            fieldbackground=colors["panel"],
            bordercolor=colors["border"],
        )
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        self.style.configure(
            "TButton",
            background=colors["panel"],
            foreground=colors["fg"],
            bordercolor=colors["button_border"],
            lightcolor=colors["panel"],
            darkcolor=colors["panel"],
            focuscolor=colors["active"],
            relief="flat",
            borderwidth=1,
        )
        self.style.configure(
            "TCheckbutton",
            background=colors["bg"],
            foreground=colors["fg"],
        )
        self.style.configure(
            "TLabelframe",
            background=colors["bg"],
            foreground=colors["fg"],
            bordercolor=colors["box_border"],
            lightcolor=colors["box_border"],
            darkcolor=colors["box_border"],
        )
        self.style.configure(
            "TLabelframe.Label",
            background=colors["bg"],
            foreground=colors["fg"],
        )
        self.style.configure(
            "TEntry",
            fieldbackground=colors["panel"],
            foreground=colors["fg"],
            bordercolor=colors["input_border"],
            lightcolor=colors["input_border"],
            darkcolor=colors["input_border"],
            insertcolor=colors["fg"],
            relief="flat",
        )
        self.style.configure(
            "TSpinbox",
            fieldbackground=colors["panel"],
            foreground=colors["fg"],
            bordercolor=colors["input_border"],
            lightcolor=colors["input_border"],
            darkcolor=colors["input_border"],
            insertcolor=colors["fg"],
            relief="flat",
        )
        self.style.configure(
            "Status.TLabel",
            background=colors["panel"],
            foreground=colors["fg"],
        )

        # Style maps for interactive states
        self.style.map(
            "TButton",
            background=[("active", colors["active"])],
            foreground=[("disabled", colors["muted"])],
            bordercolor=[("active", colors["button_active_border"])],
        )
        self.style.map(
            "TCheckbutton",
            background=[("active", colors["bg"])],
            foreground=[("disabled", colors["muted"])],
        )
        self.style.map(
            "TEntry",
            bordercolor=[
                ("focus", colors["input_focus"]),
                ("!focus", colors["input_border"]),
            ],
            lightcolor=[
                ("focus", colors["input_focus"]),
                ("!focus", colors["input_border"]),
            ],
            darkcolor=[
                ("focus", colors["input_focus"]),
                ("!focus", colors["input_border"]),
            ],
        )
        self.style.map(
            "TSpinbox",
            bordercolor=[
                ("focus", colors["input_focus"]),
                ("!focus", colors["input_border"]),
            ],
            lightcolor=[
                ("focus", colors["input_focus"]),
                ("!focus", colors["input_border"]),
            ],
            darkcolor=[
                ("focus", colors["input_focus"]),
                ("!focus", colors["input_border"]),
            ],
        )

        self._configure_scrollbars(colors)
        self._configure_performance_styles(colors)

    def _configure_scrollbars(self, colors: Dict[str, str]) -> None:
        """Configure scrollbar styles."""
        self.style.configure(
            "Minimal.Vertical.TScrollbar",
            gripcount=0,
            background=colors["scroll_bg"],
            darkcolor=colors["scroll_bg"],
            lightcolor=colors["scroll_bg"],
            troughcolor=colors["scroll_trough"],
            bordercolor=colors["scroll_trough"],
            arrowcolor=colors["scroll_fg"],
            relief="flat",
            borderwidth=0,
            arrowsize=12,
            width=12,
        )
        self.style.map(
            "Minimal.Vertical.TScrollbar",
            background=[("active", colors["scroll_active"])],
            darkcolor=[("active", colors["scroll_active"])],
            lightcolor=[("active", colors["scroll_active"])],
            arrowcolor=[("active", colors["scroll_fg"])],
        )

        self.style.configure(
            "Minimal.Horizontal.TScrollbar",
            gripcount=0,
            background=colors["scroll_bg"],
            darkcolor=colors["scroll_bg"],
            lightcolor=colors["scroll_bg"],
            troughcolor=colors["scroll_trough"],
            bordercolor=colors["scroll_trough"],
            arrowcolor=colors["scroll_fg"],
            relief="flat",
            borderwidth=0,
            arrowsize=12,
            width=12,
        )
        self.style.map(
            "Minimal.Horizontal.TScrollbar",
            background=[("active", colors["scroll_active"])],
            darkcolor=[("active", colors["scroll_active"])],
            lightcolor=[("active", colors["scroll_active"])],
            arrowcolor=[("active", colors["scroll_fg"])],
        )

    def _configure_performance_styles(self, colors: Dict[str, str]) -> None:
        """Configure performance window specific styles."""
        self.style.configure(
            "PerfSummary.TLabel",
            background=colors["bg"],
            foreground=colors["fg"],
        )
        self.style.configure("Perf.TFrame", background=colors["panel"])

        self.style.configure(
            "Perf.Treeview",
            background=colors["text_bg"],
            fieldbackground=colors["text_bg"],
            foreground=colors["text_fg"],
            rowheight=24,
            borderwidth=0,
            relief="flat",
            bordercolor=colors["panel"],
            lightcolor=colors["panel"],
            darkcolor=colors["panel"],
        )
        self.style.layout("Perf.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        self.style.map(
            "Perf.Treeview",
            background=[("selected", colors["select_bg"])],
            foreground=[("selected", colors["select_fg"])],
        )
        self.style.configure(
            "Perf.Treeview.Heading",
            background=colors["active"],
            foreground=colors["fg"],
            relief="flat",
            borderwidth=0,
            bordercolor=colors["active"],
            lightcolor=colors["active"],
            darkcolor=colors["active"],
        )
        self.style.map(
            "Perf.Treeview.Heading",
            background=[("active", colors["active"])],
            foreground=[("active", colors["fg"])],
        )

    def apply_text_widget_theme(
        self,
        widget: tk.Text,
        colors: Dict[str, str],
    ) -> None:
        """Apply theme to a Text widget."""
        widget.configure(
            background=colors["text_bg"],
            foreground=colors["text_fg"],
            insertbackground=colors["insert"],
            selectbackground=colors["select_bg"],
            selectforeground=colors["select_fg"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=colors["text_border"],
            highlightcolor=colors["input_focus"],
        )

    def configure_highlight_tags(self, root: Any, dark: bool) -> None:
        """Configure editor highlight tags based on theme."""
        if dark:
            root.editor.tag_configure(
                "match", background="#6f5a12", foreground="#fff2bf"
            )
            root.editor.tag_configure(
                "current_match", background="#a06c00", foreground="#fff2bf"
            )
            root.editor.tag_configure(
                "trace_align", background="#1f3550", foreground="#e8f1ff"
            )
            root.editor.tag_configure(
                "trace_match", background="#23523a", foreground="#dcfce7"
            )
            root.editor.tag_configure(
                "trace_mismatch", background="#6a2c2c", foreground="#ffe4e6"
            )

            root.visual_text.tag_configure(
                "viz_align", background="#26364a", foreground="#e8f1ff"
            )
            root.visual_text.tag_configure(
                "viz_match", background="#1f5a3f", foreground="#dcfce7"
            )
            root.visual_text.tag_configure(
                "viz_mismatch", background="#6a2b2b", foreground="#ffe4e6"
            )
            root.visual_text.tag_configure("viz_result_match", foreground="#86efac")
            root.visual_text.tag_configure("viz_result_mismatch", foreground="#fca5a5")
        else:
            root.editor.tag_configure(
                "match", background="#ffe8a3", foreground="#000000"
            )
            root.editor.tag_configure(
                "current_match", background="#ffbe55", foreground="#000000"
            )
            root.editor.tag_configure(
                "trace_align", background="#dbeafe", foreground="#000000"
            )
            root.editor.tag_configure(
                "trace_match", background="#bbf7d0", foreground="#000000"
            )
            root.editor.tag_configure(
                "trace_mismatch", background="#fecaca", foreground="#000000"
            )

            root.visual_text.tag_configure(
                "viz_align", background="#e8eefc", foreground="#000000"
            )
            root.visual_text.tag_configure(
                "viz_match", background="#dcfce7", foreground="#166534"
            )
            root.visual_text.tag_configure(
                "viz_mismatch", background="#fee2e2", foreground="#991b1b"
            )
            root.visual_text.tag_configure("viz_result_match", foreground="#166534")
            root.visual_text.tag_configure("viz_result_mismatch", foreground="#991b1b")
