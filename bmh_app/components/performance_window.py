"""Performance evaluation window component."""

from typing import Any, Dict, List

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from ..core.theme_manager import ThemeManager


class PerformanceWindow:
    """Standalone performance evaluation window."""

    def __init__(
        self,
        parent: tk.Tk,
        results: List[Dict[str, Any]],
        text_len: int,
        pattern_len: int,
        iterations: int,
        colors: Dict[str, str],
        style: ttk.Style,
        theme: ThemeManager,
    ) -> None:
        """Initialize performance window."""
        self.parent = parent
        self.colors = colors
        self.style = style
        self.theme = theme
        self.results = results

        self.window = tk.Toplevel(parent)
        self.window.title("Performance Evaluation")
        self.window.geometry("920x560")
        self.window.minsize(760, 480)
        self.window.configure(bg=colors["bg"])

        self.label_font = tkfont.Font(family="Segoe UI", size=8)

        self._configure_styles()
        self._build_ui(text_len, pattern_len, iterations)

    def _configure_styles(self) -> None:
        """Configure performance window styles."""
        self.style.configure(
            "PerfSummary.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["fg"],
        )
        self.style.configure(
            "Perf.TFrame",
            background=self.colors["panel"],
        )

    def _build_ui(self, text_len: int, pattern_len: int, iterations: int) -> None:
        """Build performance window UI."""
        # Summary
        summary = (
            f"Text length: {text_len}    Pattern length: {pattern_len}    "
            f"Iterations per operation: {iterations}"
        )
        ttk.Label(
            self.window,
            text=summary,
            anchor="w",
            style="PerfSummary.TLabel",
        ).pack(fill=tk.X, padx=12, pady=(10, 6))

        content_frame = ttk.Frame(self.window, style="Perf.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # Tab bar
        tab_bar = tk.Frame(
            content_frame,
            bd=0,
            highlightthickness=0,
            background=self.colors["bg"],
        )
        tab_bar.pack(fill=tk.X, pady=0)

        self.table_tab = tk.Label(
            tab_bar,
            text="Table",
            background=self.colors["panel"],
            foreground=self.colors["fg"],
            font=("Segoe UI", 9),
            padx=12,
            pady=6,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        self.table_tab.pack(side=tk.LEFT, padx=(0, 8))

        self.graph_tab = tk.Label(
            tab_bar,
            text="Graph",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
            padx=12,
            pady=6,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        self.graph_tab.pack(side=tk.LEFT, padx=(0, 8))

        # Content container
        view_container = ttk.Frame(content_frame, style="Perf.TFrame")
        view_container.pack(fill=tk.BOTH, expand=True, pady=0)

        self.table_frame = self._build_table(view_container)
        self.graph_frame = self._build_graph(view_container)

        def _show_view(name: str) -> None:
            if name == "table":
                self.graph_frame.pack_forget()
                self.table_frame.pack(fill=tk.BOTH, expand=True)
                self.table_tab.configure(foreground=self.colors["fg"])
                self.graph_tab.configure(foreground=self.colors["muted"])
            else:
                self.table_frame.pack_forget()
                self.graph_frame.pack(fill=tk.BOTH, expand=True)
                self.table_tab.configure(foreground=self.colors["muted"])
                self.graph_tab.configure(foreground=self.colors["fg"])

        self.table_tab.bind("<Button-1>", lambda _: _show_view("table"))
        self.graph_tab.bind("<Button-1>", lambda _: _show_view("graph"))

        _show_view("table")
        self._render_graph()

    def _build_table(self, parent: ttk.Frame) -> ttk.Frame:
        """Build results table view."""
        table_frame = ttk.Frame(parent, style="Perf.TFrame")

        columns = ("operation", "runtime", "memory", "result")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Perf.Treeview",
        )
        tree.heading("operation", text="Operation", anchor=tk.W)
        tree.heading("runtime", text="Avg Runtime (ms)", anchor=tk.W)
        tree.heading("memory", text="Peak Memory (KB)", anchor=tk.W)
        tree.heading("result", text="Result", anchor=tk.W)

        tree.column("operation", width=200, anchor=tk.W)
        tree.column("runtime", width=140, anchor=tk.W)
        tree.column("memory", width=140, anchor=tk.W)
        tree.column("result", width=220, anchor=tk.W)

        tree.tag_configure(
            "perf_even",
            background=self.colors["text_bg"],
            foreground=self.colors["text_fg"],
        )
        tree.tag_configure(
            "perf_odd",
            background=self.colors["panel"],
            foreground=self.colors["text_fg"],
        )

        for index, row in enumerate(self.results):
            row_tag = "perf_even" if index % 2 == 0 else "perf_odd"
            tree.insert(
                "",
                tk.END,
                values=(
                    row["operation"],
                    f"{row['runtime_ms']:.4f}",
                    f"{row['memory_kb']:.4f}",
                    row["result"],
                ),
                tags=(row_tag,),
            )

        table_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=tree.yview,
            style="Minimal.Vertical.TScrollbar",
        )
        tree.configure(yscrollcommand=table_scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)

        return table_frame

    def _build_graph(self, parent: ttk.Frame) -> ttk.Frame:
        """Build graph view."""
        graph_frame = ttk.Frame(parent, style="Perf.TFrame")

        graph_canvas = tk.Canvas(
            graph_frame,
            bd=0,
            highlightthickness=0,
            background=self.colors["text_bg"],
        )
        graph_canvas.pack(fill=tk.BOTH, expand=True)
        graph_canvas.bind("<Configure>", lambda _: self._render_graph())

        self.graph_canvas = graph_canvas
        return graph_frame

    def _render_graph(self) -> None:
        """Render performance comparison graph."""
        self.graph_canvas.delete("all")

        width = max(760, self.graph_canvas.winfo_width())
        height = max(320, self.graph_canvas.winfo_height())
        left_margin = 50
        right_margin = 28
        top_margin = 50
        bottom_margin = 70
        gap = 36
        chart_w = max(220, (width - left_margin - right_margin - gap) // 2)
        chart_h = max(160, height - top_margin - bottom_margin)

        runtime_x = left_margin
        memory_x = left_margin + chart_w + gap
        chart_y = top_margin

        runtime_color = self.colors.get("button_active_border", "#3b82f6")
        memory_color = self.colors.get("input_focus", "#f59e0b")

        self.graph_canvas.create_text(
            width / 2,
            24,
            text="Performance Comparison",
            fill=self.colors["fg"],
            font=("Segoe UI", 11, "bold"),
        )

        self._draw_chart(
            runtime_x,
            chart_y,
            chart_w,
            chart_h,
            "runtime_ms",
            "Avg Runtime (ms)",
            runtime_color,
        )
        self._draw_chart(
            memory_x,
            chart_y,
            chart_w,
            chart_h,
            "memory_kb",
            "Peak Memory (KB)",
            memory_color,
        )

    def _draw_chart(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        metric_key: str,
        title: str,
        bar_color: str,
    ) -> None:
        """Draw a single metric chart."""
        values = [float(item[metric_key]) for item in self.results]
        max_value = max(values) if values else 1.0
        max_value = max(max_value, 1e-9)

        self.graph_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=self.colors["panel"],
            outline=self.colors["border"],
            width=1,
        )

        for i in range(1, 5):
            y_line = y + int((height / 5) * i)
            self.graph_canvas.create_line(
                x + 1,
                y_line,
                x + width - 1,
                y_line,
                fill=self.colors["active"],
            )

        self.graph_canvas.create_text(
            x + width / 2,
            y - 18,
            text=title,
            fill=self.colors["fg"],
            font=("Segoe UI", 10, "bold"),
        )

        slot_w = width / max(1, len(self.results))
        bar_w = slot_w * 0.55

        for index, item in enumerate(self.results):
            value = float(item[metric_key])
            bar_h = (value / max_value) * (height - 28)
            left = x + index * slot_w + (slot_w - bar_w) / 2
            top = y + height - bar_h

            self.graph_canvas.create_rectangle(
                left,
                top,
                left + bar_w,
                y + height,
                fill=bar_color,
                outline="",
            )
            self.graph_canvas.create_text(
                left + bar_w / 2,
                top - 12,
                text=f"{value:.4f}",
                fill=self.colors["fg"],
                font=("Segoe UI", 8),
            )
            max_label_width = max(40, int(slot_w) - 8)
            label_text = item["operation"]

            if max_label_width < 70:
                label_text = self._truncate_label(label_text, max_label_width)
                self.graph_canvas.create_text(
                    left + bar_w / 2,
                    y + height + 14,
                    text=label_text,
                    fill=self.colors["fg"],
                    font=self.label_font,
                )
            else:
                self.graph_canvas.create_text(
                    left + bar_w / 2,
                    y + height + 14,
                    text=label_text,
                    fill=self.colors["fg"],
                    font=self.label_font,
                    width=max_label_width,
                )

    def _truncate_label(self, text: str, max_px: int) -> str:
        """Truncate labels when the bar slot is too narrow for wrapping."""
        if max_px <= 0:
            return ""

        ellipsis = "..."
        if self.label_font.measure(text) <= max_px:
            return text
        if self.label_font.measure(ellipsis) >= max_px:
            return ellipsis

        trimmed = text
        while trimmed and self.label_font.measure(trimmed + ellipsis) > max_px:
            trimmed = trimmed[:-1]

        return trimmed + ellipsis
