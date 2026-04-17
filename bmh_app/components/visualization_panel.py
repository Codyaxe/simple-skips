"""Visualization panel component - BMH trace rendering."""

from typing import Callable, Dict, List

import tkinter as tk
from tkinter import ttk

from ..core.theme_manager import ThemeManager


class VisualizationPanel:
    """BMH algorithm visualization and skip table display."""

    def __init__(self, parent: ttk.LabelFrame, theme: ThemeManager) -> None:
        """Initialize visualization panel."""
        self.theme = theme

        # Controls
        viz_controls = ttk.Frame(parent)
        viz_controls.pack(fill=tk.X, pady=(0, 8))

        self.full_scan_var = tk.BooleanVar(value=False)
        self.animation_delay_var = tk.IntVar(value=400)

        ttk.Checkbutton(
            viz_controls,
            text="Full scan (continue after match)",
            variable=self.full_scan_var,
        ).pack(side=tk.LEFT)

        self.callbacks: Dict[str, Callable[[], None]] = {}

        ttk.Button(viz_controls, text="Build Trace", command=self._on_build_trace).pack(
            side=tk.LEFT, padx=(10, 6)
        )
        ttk.Button(viz_controls, text="Prev", command=self._on_prev).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(viz_controls, text="Next", command=self._on_next).pack(side=tk.LEFT)
        self.play_button = ttk.Button(
            viz_controls, text="Play", command=self._on_toggle_animation
        )
        self.play_button.pack(side=tk.LEFT, padx=(6, 6))

        ttk.Label(viz_controls, text="Delay (ms)").pack(side=tk.LEFT, padx=(8, 4))
        ttk.Spinbox(
            viz_controls,
            from_=100,
            to=2000,
            increment=50,
            textvariable=self.animation_delay_var,
            width=6,
        ).pack(side=tk.LEFT)

        # Step display
        self.step_var = tk.StringVar(value="Step 0/0")
        ttk.Label(parent, textvariable=self.step_var).pack(anchor="w", pady=(0, 6))

        # Visualization text
        self.visual_text = tk.Text(
            parent, height=16, wrap=tk.NONE, font=("Consolas", 10)
        )
        self.visual_text.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.visual_text.tag_configure("viz_align", background="#e8eefc")
        self.visual_text.tag_configure(
            "viz_match", background="#dcfce7", foreground="#166534"
        )
        self.visual_text.tag_configure(
            "viz_mismatch", background="#fee2e2", foreground="#991b1b"
        )
        self.visual_text.tag_configure("viz_result_match", foreground="#166534")
        self.visual_text.tag_configure("viz_result_mismatch", foreground="#991b1b")
        self.visual_text.configure(state=tk.DISABLED)

        # Skip table
        ttk.Label(parent, text="Skip Table").pack(anchor="w")
        self.skip_text = tk.Text(parent, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.skip_text.pack(fill=tk.X)
        self.skip_text.configure(state=tk.DISABLED)

    def set_callback(self, name: str, callback: Callable[[], None]) -> None:
        """Register callback for button action."""
        self.callbacks[name] = callback

    def _on_build_trace(self) -> None:
        if "build_trace" in self.callbacks:
            self.callbacks["build_trace"]()

    def _on_prev(self) -> None:
        if "prev" in self.callbacks:
            self.callbacks["prev"]()

    def _on_next(self) -> None:
        if "next" in self.callbacks:
            self.callbacks["next"]()

    def _on_toggle_animation(self) -> None:
        if "toggle_animation" in self.callbacks:
            self.callbacks["toggle_animation"]()

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme to visualization."""
        self.theme.apply_text_widget_theme(self.visual_text, colors)
        self.theme.apply_text_widget_theme(self.skip_text, colors)

    def set_step_text(self, step_num: int, total: int) -> None:
        """Update step display."""
        self.step_var.set(f"Step {step_num}/{total}")

    def set_visual_content(self, content: str) -> None:
        """Update visualization text content."""
        self._set_readonly_text(self.visual_text, content)

    def set_skip_table(self, content: str) -> None:
        """Update skip table content."""
        self._set_readonly_text(self.skip_text, content)

    def update_play_button(self, is_animating: bool) -> None:
        """Update play button text based on animation state."""
        self.play_button.configure(text="Stop" if is_animating else "Play")

    def clear_trace_display(self) -> None:
        """Clear all trace visualization."""
        self._set_readonly_text(self.visual_text, "")
        self.set_step_text(0, 0)

    def _set_readonly_text(self, widget: tk.Text, content: str) -> None:
        """Set text in a read-only widget."""
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.configure(state=tk.DISABLED)
