"""Main application window - orchestrator for all UI components."""

import time
import tracemalloc
from typing import Any, Callable, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from bmh_logic import (
    BMHStep,
    bmh_find_all,
    bmh_search,
    bmh_trace,
    build_skip_table,
    display_char,
    visual_char,
)

from .core.theme_manager import ThemeManager
from .ui_utils.dropdown_menu import DropdownMenu
from .ui_utils.custom_menu_bar import CustomMenuBar
from .components.editor_panel import EditorPanel
from .components.search_bar import SearchBar
from .components.visualization_panel import VisualizationPanel
from .components.performance_window import PerformanceWindow


class BMHTextEditor(tk.Tk):
    """Main application window - coordinates all components."""

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()

        self.title("BMH Text Editor")
        self.geometry("1200x760")
        self.minsize(980, 620)

        # File management
        self.current_file: Optional[str] = None
        self.is_dirty = False

        # Trace state
        self.trace_steps: List[BMHStep] = []
        self.trace_step_index = 0
        self.trace_text = ""
        self.trace_pattern = ""
        self.animation_job: Optional[str] = None
        self.is_animating = False

        # Variables
        self.status_var = tk.StringVar(value="Ready")
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.show_visualization_var = tk.BooleanVar(value=True)

        # Theme
        self.style = ttk.Style(self)
        self.theme_manager = ThemeManager(self.style)

        # Performance window
        self.performance_window: Optional[tk.Toplevel] = None

        # Components (will be initialized in _build_ui)
        self.search_bar: SearchBar
        self.editor_panel: EditorPanel
        self.viz_panel: VisualizationPanel
        self.editor: tk.Text
        self.visual_text: tk.Text
        self.skip_text: tk.Text

        # Build UI
        self._build_ui()
        self._build_menu()
        self._apply_theme()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ========================================================================
    # UI CONSTRUCTION
    # ========================================================================

    def _build_ui(self) -> None:
        """Build main UI layout."""
        self.container = ttk.Frame(self, padding=10)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Search bar
        self.search_bar = SearchBar(self.container, self.find_var, self.replace_var)
        self.search_bar.set_callback("find_next", self.find_next)
        self.search_bar.set_callback("find_all", self.find_all)
        self.search_bar.set_callback("replace_next", self.replace_next)
        self.search_bar.set_callback("replace_all", self.replace_all)
        self.search_bar.set_callback("clear_marks", self.clear_highlights)

        # Horizontal split: editor + visualization
        self.split = ttk.Panedwindow(self.container, orient=tk.HORIZONTAL)
        self.split.pack(fill=tk.BOTH, expand=True)

        # Editor panel
        editor_frame = ttk.Frame(self.split)
        self.split.add(editor_frame, weight=3)
        self.editor_panel = EditorPanel(editor_frame, self.theme_manager)
        self.editor = self.editor_panel.editor

        # Visualization panel
        self.viz_frame = ttk.LabelFrame(self.split, text="BMH Visualization", padding=8)
        self.split.add(self.viz_frame, weight=2)
        self.viz_panel = VisualizationPanel(self.viz_frame, self.theme_manager)
        self.visual_text = self.viz_panel.visual_text
        self.skip_text = self.viz_panel.skip_text

        # Wire visualization callbacks
        self.viz_panel.set_callback("build_trace", self.build_trace)
        self.viz_panel.set_callback("prev", self.prev_trace_step)
        self.viz_panel.set_callback("next", self.next_trace_step)
        self.viz_panel.set_callback("toggle_animation", self.toggle_animation)

        # Status bar
        self.status_frame = tk.Frame(
            self.container,
            bd=0,
            highlightthickness=1,
        )
        self.status_frame.pack(fill=tk.X, pady=(8, 0))

        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            anchor="w",
            padding=(6, 2),
        )
        self.status_label.pack(fill=tk.X)

        # Bind modifications
        self.editor.bind("<<Modified>>", self._on_text_modified)

    def _build_menu(self) -> None:
        """Build menu bar with dropdowns."""
        self.menu_bar = CustomMenuBar(self)
        self.menu_bar.pack(fill=tk.X, side=tk.TOP, before=self.container)

        # File menu
        self.file_menu = DropdownMenu(self)
        self.file_menu.add_command(
            label="New",
            accelerator="Ctrl+N",
            command=self.new_file,
        )
        self.file_menu.add_command(
            label="Open",
            accelerator="Ctrl+O",
            command=self.open_file,
        )
        self.file_menu.add_command(
            label="Save",
            accelerator="Ctrl+S",
            command=self.save_file,
        )
        self.file_menu.add_command(
            label="Save As",
            accelerator="Ctrl+Shift+S",
            command=self.save_as_file,
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._on_close)

        # View menu
        self.view_menu = DropdownMenu(self)
        self.view_menu.add_checkbutton(
            label="Dark Mode",
            variable=self.dark_mode_var,
            command=self.toggle_dark_mode,
        )
        self.view_menu.add_checkbutton(
            label="Show Visualization",
            variable=self.show_visualization_var,
            command=self.toggle_visualization,
        )

        # Performance menu
        self.performance_menu = DropdownMenu(self)
        self.performance_menu.add_command(
            label="Run Evaluation",
            command=self.run_performance_evaluation,
        )

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.menu_bar.add_cascade(label="Performance", menu=self.performance_menu)

        self._bind_shortcuts()

    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        self.bind_all("<Control-n>", self._on_shortcut_new)
        self.bind_all("<Control-o>", self._on_shortcut_open)
        self.bind_all("<Control-s>", self._on_shortcut_save)
        self.bind_all("<Control-S>", self._on_shortcut_save_as)

    # ========================================================================
    # THEME MANAGEMENT
    # ========================================================================

    def toggle_dark_mode(self) -> None:
        """Toggle dark/light mode."""
        self._apply_theme()

    def toggle_visualization(self) -> None:
        """Toggle visualization panel visibility."""
        if self.show_visualization_var.get():
            if str(self.viz_frame) not in self.split.panes():
                self.split.add(self.viz_frame, weight=2)
        else:
            if str(self.viz_frame) in self.split.panes():
                self._cancel_animation()
                self.split.forget(self.viz_frame)

    def _apply_theme(self) -> None:
        """Apply current theme to all components."""
        dark = self.dark_mode_var.get()
        colors = self.theme_manager.get_colors(dark)

        self.configure(bg=colors["bg"])
        self.theme_manager.apply_theme(self, colors)

        # Apply to components
        self.editor_panel.apply_theme(colors)
        self.viz_panel.apply_theme(colors)

        # Status bar
        self.status_label.configure(style="Status.TLabel")
        self.status_frame.configure(
            background=colors["panel"],
            highlightbackground=colors["box_border"],
            highlightcolor=colors["box_border"],
        )
        self.menu_bar.update_colors(colors)

        # Highlight tags
        self.theme_manager.configure_highlight_tags(self, dark)

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def new_file(self) -> None:
        """Create a new file."""
        if not self._confirm_discard_if_needed():
            return

        self.current_file = None
        self.editor_panel.set_content("")
        self.is_dirty = False
        self._update_window_title()
        self.clear_highlights()
        self._set_status("Started a new file.")

    def open_file(self) -> None:
        """Open an existing file."""
        if not self._confirm_discard_if_needed():
            return

        path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except OSError as exc:
            messagebox.showerror("Open Failed", str(exc))
            return

        self.current_file = path
        self.editor_panel.set_content(content)
        self.is_dirty = False
        self._update_window_title()
        self.clear_highlights()
        self._set_status(f"Opened {path}")

    def save_file(self) -> bool:
        """Save current file."""
        if not self.current_file:
            return self.save_as_file()

        try:
            with open(self.current_file, "w", encoding="utf-8") as handle:
                handle.write(self.editor_panel.get_content())
        except OSError as exc:
            messagebox.showerror("Save Failed", str(exc))
            return False

        self.is_dirty = False
        self._update_window_title()
        self._set_status(f"Saved {self.current_file}")
        return True

    def save_as_file(self) -> bool:
        """Save file with new name."""
        path = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return False

        self.current_file = path
        return self.save_file()

    def _confirm_discard_if_needed(self) -> bool:
        """Ask to save if file has unsaved changes."""
        if not self.is_dirty:
            return True

        choice = messagebox.askyesnocancel(
            "Unsaved Changes", "Save your changes first?"
        )
        if choice is None:
            return False
        if choice:
            return self.save_file()
        return True

    def _on_text_modified(self, _event: tk.Event) -> None:
        """Handle text modification."""
        if self.editor.edit_modified():
            self.is_dirty = True
            self._update_window_title()
            self.editor.edit_modified(False)

    def _update_window_title(self) -> None:
        """Update window title with filename and dirty indicator."""
        name = self.current_file if self.current_file else "Untitled"
        dirty = " *" if self.is_dirty else ""
        self.title(f"Simple Skips Text Editor - {name}{dirty}")

    # ========================================================================
    # SEARCH OPERATIONS
    # ========================================================================

    def find_next(self) -> None:
        """Find next occurrence of search pattern."""
        pattern = self.find_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        self.clear_highlights()
        start = self.editor_panel.get_cursor_offset()
        index, wrapped = self._find_next_from(pattern, start)

        if index == -1:
            self._set_status("No match found.")
            return

        self.editor_panel.highlight_range(index, index + len(pattern), current=True)
        self.editor_panel.set_insertion_point(index + len(pattern))

        if wrapped:
            self._set_status(f"Found at index {index} (wrapped to start).")
        else:
            self._set_status(f"Found at index {index}.")

    def find_all(self) -> None:
        """Find and highlight all occurrences."""
        pattern = self.find_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        self.clear_highlights()
        content = self.editor_panel.get_content()
        matches = bmh_find_all(content, pattern, allow_overlap=True)

        for index in matches:
            self.editor_panel.highlight_range(
                index, index + len(pattern), current=False
            )

        if matches:
            self._set_status(f"Highlighted {len(matches)} match(es).")
        else:
            self._set_status("No matches found.")

    def replace_next(self) -> None:
        """Replace next occurrence."""
        pattern = self.find_var.get()
        replacement = self.replace_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        start = self.editor_panel.get_cursor_offset()
        index, wrapped = self._find_next_from(pattern, start)

        if index == -1:
            self._set_status("No match found to replace.")
            return

        start_index = f"1.0+{index}c"
        end_index = f"1.0+{index + len(pattern)}c"
        self.editor.delete(start_index, end_index)
        self.editor.insert(start_index, replacement)

        self.clear_highlights()
        replacement_end = index + len(replacement)
        self.editor_panel.highlight_range(index, replacement_end, current=True)
        self.editor_panel.set_insertion_point(replacement_end)

        self.is_dirty = True
        self._update_window_title()

        if wrapped:
            self._set_status(f"Replaced at index {index} (wrapped to start).")
        else:
            self._set_status(f"Replaced at index {index}.")

    def replace_all(self) -> None:
        """Replace all occurrences."""
        pattern = self.find_var.get()
        replacement = self.replace_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        original = self.editor_panel.get_content()
        matches = bmh_find_all(original, pattern, allow_overlap=False)

        if not matches:
            self._set_status("No matches found to replace.")
            return

        pieces: List[str] = []
        cursor = 0
        pattern_len = len(pattern)

        for index in matches:
            pieces.append(original[cursor:index])
            pieces.append(replacement)
            cursor = index + pattern_len

        pieces.append(original[cursor:])
        updated = "".join(pieces)

        self.editor_panel.set_content(updated)
        self.clear_highlights()
        self.is_dirty = True
        self._update_window_title()
        self._set_status(f"Replaced {len(matches)} occurrence(s).")

    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.editor_panel.clear_highlights()

    def _find_next_from(self, pattern: str, start_offset: int) -> Tuple[int, bool]:
        """Find next occurrence from offset."""
        content = self.editor_panel.get_content()
        index = bmh_search(content, pattern, start_offset)
        wrapped = False

        if index == -1 and start_offset > 0:
            index = bmh_search(content, pattern, 0)
            wrapped = index != -1

        return index, wrapped

    # ========================================================================
    # TRACE & VISUALIZATION
    # ========================================================================

    def build_trace(self) -> None:
        """Build trace from current text and pattern."""
        self._cancel_animation()
        pattern = self.find_var.get()
        if not pattern:
            self._set_status("Find text is empty. Enter pattern first.")
            return

        text = self.editor_panel.get_content()
        if not text:
            self._set_status("Editor is empty. Add text to visualize BMH.")
            return

        cursor_start = self.editor_panel.get_cursor_offset()
        stop_on_match = not self.viz_panel.full_scan_var.get()

        fallback_to_start = (
            cursor_start > 0
            and len(pattern) <= len(text)
            and cursor_start > len(text) - len(pattern)
        )
        trace_start = 0 if fallback_to_start else cursor_start

        steps, first_match, _skip = bmh_trace(
            text=text,
            pattern=pattern,
            start=trace_start,
            stop_on_first_match=stop_on_match,
        )

        if not steps:
            self.trace_steps = []
            self.trace_step_index = 0
            self.trace_text = text
            self.trace_pattern = pattern
            self.viz_panel.set_step_text(0, 0)
            self._render_skip_table(pattern)
            self.viz_panel.set_visual_content("No steps available for this input.")
            self._set_status("Trace could not be generated.")
            return

        self.trace_steps = steps
        self.trace_step_index = 0
        self.trace_text = text
        self.trace_pattern = pattern
        self._render_skip_table(pattern)
        self._render_trace_step()

        if first_match == -1:
            if fallback_to_start:
                self._set_status(
                    "Trace built from start (cursor was past the last alignment). "
                    "No match found."
                )
            else:
                self._set_status("Trace built. No match found.")
        else:
            if fallback_to_start:
                self._set_status(
                    "Trace built from start (cursor was past the last alignment). "
                    f"First match at index {first_match}."
                )
            else:
                self._set_status(f"Trace built. First match at index {first_match}.")

    def prev_trace_step(self) -> None:
        """Go to previous trace step."""
        self._cancel_animation()
        if not self.trace_steps:
            self._set_status("Build a trace first.")
            return

        if self.trace_step_index > 0:
            self.trace_step_index -= 1
            self._render_trace_step()

    def next_trace_step(self) -> None:
        """Go to next trace step."""
        self._cancel_animation()
        if not self.trace_steps:
            self._set_status("Build a trace first.")
            return

        if self.trace_step_index < len(self.trace_steps) - 1:
            self.trace_step_index += 1
            self._render_trace_step()

    def toggle_animation(self) -> None:
        """Toggle trace animation."""
        if self.is_animating:
            self._cancel_animation(update_status=True)
            return

        if not self.trace_steps:
            self._set_status("Build a trace first.")
            return

        self.is_animating = True
        self.viz_panel.update_play_button(True)
        self._set_status("Animation started.")
        self._animate_trace_step()

    def _animate_trace_step(self) -> None:
        """Execute animation step."""
        if not self.is_animating:
            return

        self._render_trace_step()

        if self.trace_step_index >= len(self.trace_steps) - 1:
            self._cancel_animation(update_status=True, message="Animation completed.")
            return

        self.trace_step_index += 1
        delay = max(80, int(self.viz_panel.animation_delay_var.get()))
        self.animation_job = self.after(delay, self._animate_trace_step)

    def _cancel_animation(
        self,
        update_status: bool = False,
        message: str = "Animation stopped.",
    ) -> None:
        """Stop animation."""
        if self.animation_job is not None:
            self.after_cancel(self.animation_job)
            self.animation_job = None

        was_animating = self.is_animating
        self.is_animating = False
        self.viz_panel.update_play_button(False)

        if update_status and was_animating:
            self._set_status(message)

    def _render_trace_step(self) -> None:
        """Render current trace step."""
        if not self.trace_steps:
            return

        step = self.trace_steps[self.trace_step_index]
        text = self.trace_text
        pattern = self.trace_pattern

        window_radius = 20
        start = max(0, step.alignment - window_radius)
        end = min(len(text), step.alignment + len(pattern) + window_radius)

        window_raw = text[start:end]
        window_display = "".join(visual_char(ch) for ch in window_raw)
        pattern_display = "".join(visual_char(ch) for ch in pattern)

        index_line = "".join(str((start + i) % 10) for i in range(len(window_raw)))
        pattern_offset = max(0, step.alignment - start)
        pattern_line = (" " * pattern_offset) + pattern_display

        markers = [" "] * len(window_raw)
        checks: List[str] = []

        for (
            text_index,
            pattern_index,
            text_char,
            pattern_char,
            matched,
        ) in step.comparisons:
            local_index = text_index - start
            if 0 <= local_index < len(markers):
                markers[local_index] = "^" if matched else "x"

            operator = "==" if matched else "!="
            checks.append(
                f"T[{text_index}] '{display_char(text_char)}' {operator} "
                f"P[{pattern_index}] '{display_char(pattern_char)}'"
            )

        marker_line = "".join(markers)
        checks_text = (
            ", ".join(checks) if checks else "No character comparisons in this step."
        )
        result_text = "MATCH" if step.is_match else "MISMATCH"
        text_prefix = "Text   : "
        pattern_prefix = "Pattern: "
        compare_prefix = "Compare: "

        self.visual_text.configure(state=tk.NORMAL)
        self.visual_text.delete("1.0", tk.END)

        self.visual_text.insert(tk.END, f"Window [{start}:{end}]\n")
        self.visual_text.insert(tk.END, f"Index  : {index_line}\n")

        text_line_start = self.visual_text.index(tk.END)
        self.visual_text.insert(tk.END, f"{text_prefix}{window_display}\n")

        pattern_line_start = self.visual_text.index(tk.END)
        self.visual_text.insert(tk.END, f"{pattern_prefix}{pattern_line}\n")

        compare_line_start = self.visual_text.index(tk.END)
        self.visual_text.insert(tk.END, f"{compare_prefix}{marker_line}\n\n")

        self.visual_text.insert(tk.END, f"Checks : {checks_text}\n")

        result_line_start = self.visual_text.index(tk.END)
        self.visual_text.insert(tk.END, f"Result : {result_text}\n")

        self.visual_text.insert(tk.END, f"Shift  : {step.shift}\n")
        self.visual_text.insert(tk.END, f"Why    : {step.reason}\n")

        alignment_display_start = max(0, step.alignment - start)
        alignment_display_end = min(
            len(window_display), alignment_display_start + len(pattern)
        )
        text_prefix_len = len(text_prefix)
        pattern_prefix_len = len(pattern_prefix)

        if alignment_display_end > alignment_display_start:
            self.visual_text.tag_add(
                "viz_align",
                f"{text_line_start}+{text_prefix_len + alignment_display_start}c",
                f"{text_line_start}+{text_prefix_len + alignment_display_end}c",
            )
            self.visual_text.tag_add(
                "viz_align",
                f"{pattern_line_start}+{pattern_prefix_len + pattern_offset}c",
                f"{pattern_line_start}+{pattern_prefix_len + pattern_offset + len(pattern)}c",
            )

        compare_prefix_len = len(compare_prefix)
        for (
            text_index,
            pattern_index,
            _text_char,
            _pattern_char,
            matched,
        ) in step.comparisons:
            local_index = text_index - start
            if local_index < 0 or local_index >= len(window_display):
                continue

            tag_name = "viz_match" if matched else "viz_mismatch"

            self.visual_text.tag_add(
                tag_name,
                f"{text_line_start}+{text_prefix_len + local_index}c",
                f"{text_line_start}+{text_prefix_len + local_index + 1}c",
            )

            pattern_local = pattern_offset + pattern_index
            self.visual_text.tag_add(
                tag_name,
                f"{pattern_line_start}+{pattern_prefix_len + pattern_local}c",
                f"{pattern_line_start}+{pattern_prefix_len + pattern_local + 1}c",
            )

            self.visual_text.tag_add(
                tag_name,
                f"{compare_line_start}+{compare_prefix_len + local_index}c",
                f"{compare_line_start}+{compare_prefix_len + local_index + 1}c",
            )

        result_tag = "viz_result_match" if step.is_match else "viz_result_mismatch"
        self.visual_text.tag_add(
            result_tag,
            f"{result_line_start}+9c",
            f"{result_line_start}+{9 + len(result_text)}c",
        )

        self.visual_text.configure(state=tk.DISABLED)

        self.editor_panel.clear_trace_highlights()
        if len(pattern) > 0:
            align_start_idx = step.alignment
            align_end_idx = step.alignment + len(pattern)
            self.editor_panel.editor.tag_add(
                "trace_align",
                f"1.0+{align_start_idx}c",
                f"1.0+{align_end_idx}c",
            )

        for (
            text_index,
            _pattern_index,
            _text_char,
            _pattern_char,
            matched,
        ) in step.comparisons:
            tag_name = "trace_match" if matched else "trace_mismatch"
            self.editor_panel.mark_trace_highlight(text_index, tag_name)

        self.editor.see(f"1.0+{step.alignment}c")

        self.viz_panel.set_step_text(self.trace_step_index + 1, len(self.trace_steps))

    def _render_skip_table(self, pattern: str) -> None:
        """Render skip table visualization."""
        if not pattern:
            self.viz_panel.set_skip_table("No pattern set.")
            return

        table = build_skip_table(pattern)
        rows = [f"Default shift: {len(pattern)}"]

        if table:
            rows.append("Custom shifts:")
            for char in sorted(table.keys()):
                rows.append(f"  '{display_char(char)}' -> {table[char]}")
        else:
            rows.append("Pattern length is 1, so only default shift is used.")

        self.viz_panel.set_skip_table("\n".join(rows))

    # ========================================================================
    # PERFORMANCE EVALUATION
    # ========================================================================

    def run_performance_evaluation(self) -> None:
        """Run performance evaluation."""
        text = self.editor_panel.get_content()
        pattern = self.find_var.get()

        if not text:
            self._set_status("Performance evaluation requires text in the editor.")
            messagebox.showinfo(
                "Performance Evaluation",
                "Add some text first before running performance evaluation.",
            )
            return

        if not pattern:
            self._set_status("Performance evaluation requires a pattern in Find.")
            messagebox.showinfo(
                "Performance Evaluation",
                "Enter a pattern in the Find box before running evaluation.",
            )
            return

        iterations = self._select_benchmark_iterations(len(text), len(pattern))

        operations: List[Tuple[str, Callable[[], Any]]] = [
            ("BMH Search", lambda: bmh_search(text, pattern, 0)),
            (
                "BMH Find All",
                lambda: bmh_find_all(text, pattern, allow_overlap=True),
            ),
        ]

        results: List[Dict[str, Any]] = []
        for operation_name, callback in operations:
            runtime_ms, peak_kb, result = self._measure_operation(callback, iterations)
            results.append(
                {
                    "operation": operation_name,
                    "runtime_ms": runtime_ms,
                    "memory_kb": peak_kb,
                    "result": self._format_performance_result(result),
                }
            )

        colors = self.theme_manager.colors or self.theme_manager.get_colors(
            self.dark_mode_var.get()
        )
        if self.performance_window and self.performance_window.winfo_exists():
            self.performance_window.destroy()

        perf_window = PerformanceWindow(
            self,
            results,
            len(text),
            len(pattern),
            iterations,
            colors,
            self.style,
            self.theme_manager,
        )
        self.performance_window = perf_window.window
        self._set_status("Performance evaluation complete.")

    def _select_benchmark_iterations(self, text_len: int, pattern_len: int) -> int:
        """Select appropriate benchmark iterations."""
        scale = text_len + pattern_len
        if scale <= 1_000:
            return 500
        if scale <= 10_000:
            return 150
        if scale <= 100_000:
            return 35
        return 10

    def _measure_operation(
        self,
        callback: Callable[[], Any],
        iterations: int,
    ) -> Tuple[float, float, Any]:
        """Measure operation performance."""
        iterations = max(1, iterations)
        result: Any = None

        tracemalloc.start()
        start = time.perf_counter()
        for _ in range(iterations):
            result = callback()
        elapsed = time.perf_counter() - start
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        avg_runtime_ms = (elapsed / iterations) * 1000.0
        peak_kb = peak / 1024.0
        return avg_runtime_ms, peak_kb, result

    def _format_performance_result(self, result: Any) -> str:
        """Format performance result for display."""
        if isinstance(result, list):
            return f"{len(result)} matches"
        return str(result)

    # ========================================================================
    # SHORTCUTS & UTILITIES
    # ========================================================================

    def _on_shortcut_new(self, _event: tk.Event) -> str:
        self.new_file()
        return "break"

    def _on_shortcut_open(self, _event: tk.Event) -> str:
        self.open_file()
        return "break"

    def _on_shortcut_save(self, _event: tk.Event) -> str:
        self.save_file()
        return "break"

    def _on_shortcut_save_as(self, _event: tk.Event) -> str:
        self.save_as_file()
        return "break"

    def _on_close(self) -> None:
        """Handle window close."""
        self._cancel_animation()
        if self._confirm_discard_if_needed():
            self.destroy()

    def _set_status(self, message: str) -> None:
        """Set status bar message."""
        self.status_var.set(message)
