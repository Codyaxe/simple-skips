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


class _DropdownMenu:
    """Borderless themed dropdown that replaces native tk.Menu popups."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._items: List[Dict[str, Any]] = []
        self._win: Optional[tk.Toplevel] = None

    def add_command(
        self,
        label: str,
        command: Optional[Callable[[], Any]] = None,
        accelerator: str = "",
    ) -> None:
        self._items.append(
            {
                "type": "command",
                "label": label,
                "command": command,
                "accelerator": accelerator,
            }
        )

    def add_checkbutton(
        self,
        label: str,
        variable: Optional[tk.BooleanVar] = None,
        command: Optional[Callable[[], Any]] = None,
    ) -> None:
        self._items.append(
            {
                "type": "checkbutton",
                "label": label,
                "variable": variable,
                "command": command,
            }
        )

    def add_separator(self) -> None:
        self._items.append({"type": "separator"})

    def show(self, x: int, y: int, colors: Dict[str, str]) -> None:
        self._close()
        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.configure(bg=colors["border"])

        inner = tk.Frame(win, bg=colors["panel"], bd=0, highlightthickness=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        for item in self._items:
            if item["type"] == "separator":
                tk.Frame(inner, height=1, bg=colors["border"]).pack(
                    fill=tk.X,
                    padx=6,
                    pady=2,
                )
                continue
            self._build_row(inner, item, colors, win)

        win.update_idletasks()
        win.geometry(f"+{x}+{y}")
        win.lift()
        self._win = win

    def _build_row(
        self,
        parent: tk.Frame,
        item: Dict[str, Any],
        colors: Dict[str, str],
        win: tk.Toplevel,
    ) -> None:
        row = tk.Frame(parent, bg=colors["panel"])
        row.pack(fill=tk.X, padx=2)

        check_text = ""
        variable = item.get("variable")
        if item["type"] == "checkbutton" and variable is not None:
            check_text = "\u2713" if variable.get() else ""

        ind = tk.Label(
            row,
            text=check_text,
            bg=colors["panel"],
            fg=colors["fg"],
            width=2,
            font=("Segoe UI", 9),
            anchor="center",
        )
        ind.pack(side=tk.LEFT, padx=(4, 0))

        lbl = tk.Label(
            row,
            text=item["label"],
            bg=colors["panel"],
            fg=colors["fg"],
            anchor="w",
            padx=6,
            pady=4,
            font=("Segoe UI", 9),
        )
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        row_widgets: List[Any] = [row, ind, lbl]
        accelerator = item.get("accelerator")
        if accelerator:
            acc = tk.Label(
                row,
                text=accelerator,
                bg=colors["panel"],
                fg=colors.get("muted", colors["fg"]),
                padx=10,
                pady=4,
                font=("Segoe UI", 9),
            )
            acc.pack(side=tk.RIGHT)
            row_widgets.append(acc)

        def _enter(_event: tk.Event) -> None:
            for widget in row_widgets:
                widget.configure(background=colors["active"])

        def _leave(_event: tk.Event) -> None:
            for widget in row_widgets:
                widget.configure(background=colors["panel"])

        def _click(_event: tk.Event) -> None:
            win.destroy()
            self._win = None

            if item["type"] == "checkbutton" and variable is not None:
                variable.set(not variable.get())

            command = item.get("command")
            if command is not None:
                command()

        for widget in row_widgets:
            widget.bind("<Enter>", _enter)
            widget.bind("<Leave>", _leave)
            widget.bind("<Button-1>", _click)

    def is_open(self) -> bool:
        return bool(self._win and self._win.winfo_exists())

    def close(self) -> None:
        self._close()

    def _close(self) -> None:
        if self._win and self._win.winfo_exists():
            self._win.destroy()
        self._win = None


class _CustomMenuBar(tk.Frame):
    """Themed text menu bar that opens _DropdownMenu popups."""

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, bd=0, highlightthickness=0)
        self._dropdowns: Dict[str, _DropdownMenu] = {}
        self._buttons: Dict[str, tk.Label] = {}
        self._colors: Dict[str, str] = {}
        self._active: Optional[str] = None
        parent.bind("<Button-1>", self._on_global_click, "+")

    def add_cascade(self, label: str, menu: _DropdownMenu) -> None:
        self._dropdowns[label] = menu

        btn = tk.Label(
            self,
            text=label,
            padx=10,
            pady=4,
            font=("Segoe UI", 9),
            cursor="arrow",
        )
        btn.pack(side=tk.LEFT)
        btn.bind("<Button-1>", lambda _event, name=label: self._on_btn_click(name))
        btn.bind("<Enter>", lambda _event, widget=btn: self._hover(widget, True))
        btn.bind("<Leave>", lambda _event, widget=btn: self._hover(widget, False))
        self._buttons[label] = btn

    def update_colors(self, colors: Dict[str, str]) -> None:
        self._colors = colors
        self.configure(bg=colors["panel"])
        for btn in self._buttons.values():
            btn.configure(background=colors["panel"], foreground=colors["fg"])

    def close_all(self) -> None:
        for dropdown in self._dropdowns.values():
            dropdown.close()
        self._active = None

    def _hover(self, btn: tk.Label, entering: bool) -> None:
        if not self._colors:
            return
        target = self._colors["active"] if entering else self._colors["panel"]
        btn.configure(background=target)

    def _on_btn_click(self, label: str) -> None:
        dropdown = self._dropdowns[label]
        if dropdown.is_open():
            dropdown.close()
            self._active = None
            return

        self.close_all()
        btn = self._buttons[label]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        dropdown.show(x, y, self._colors)
        self._active = label

    def _on_global_click(self, event: tk.Event) -> None:
        if not self._active:
            return

        dropdown = self._dropdowns.get(self._active)
        if dropdown is None or not dropdown.is_open():
            self._active = None
            return

        try:
            win = dropdown._win
            if win is None:
                self._active = None
                return

            wx, wy = win.winfo_rootx(), win.winfo_rooty()
            ww, wh = win.winfo_width(), win.winfo_height()
            if wx <= event.x_root <= wx + ww and wy <= event.y_root <= wy + wh:
                return

            for btn in self._buttons.values():
                bx, by = btn.winfo_rootx(), btn.winfo_rooty()
                bw, bh = btn.winfo_width(), btn.winfo_height()
                if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
                    return

            dropdown.close()
            self._active = None
        except tk.TclError:
            self._active = None


class BMHTextEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("BMH Text Editor")
        self.geometry("1200x760")
        self.minsize(980, 620)

        self.current_file: Optional[str] = None
        self.is_dirty = False

        self.trace_steps: List[BMHStep] = []
        self.trace_step_index = 0
        self.trace_text = ""
        self.trace_pattern = ""
        self.animation_job: Optional[str] = None
        self.is_animating = False

        self.status_var = tk.StringVar(value="Ready")
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.step_var = tk.StringVar(value="Step 0/0")
        self.full_scan_var = tk.BooleanVar(value=False)
        self.animation_delay_var = tk.IntVar(value=400)
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.show_visualization_var = tk.BooleanVar(value=True)
        self.style = ttk.Style(self)
        self.theme_colors: Dict[str, str] = {}
        self.performance_window: Optional[tk.Toplevel] = None

        self._build_ui()
        self._build_menu()
        self._apply_theme()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        self.container = ttk.Frame(self, padding=10)
        self.container.pack(fill=tk.BOTH, expand=True)

        search_row = ttk.Frame(self.container)
        search_row.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_row, text="Find").pack(side=tk.LEFT)
        ttk.Entry(search_row, textvariable=self.find_var, width=20).pack(
            side=tk.LEFT, padx=(6, 10)
        )

        ttk.Label(search_row, text="Replace").pack(side=tk.LEFT)
        ttk.Entry(search_row, textvariable=self.replace_var, width=20).pack(
            side=tk.LEFT, padx=(6, 10)
        )

        ttk.Button(search_row, text="Find Next", command=self.find_next).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Find All", command=self.find_all).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Replace Next", command=self.replace_next).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Replace All", command=self.replace_all).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_row, text="Clear Marks", command=self.clear_highlights).pack(
            side=tk.LEFT
        )

        self.split = ttk.Panedwindow(self.container, orient=tk.HORIZONTAL)
        self.split.pack(fill=tk.BOTH, expand=True)

        self.editor_frame = ttk.Frame(self.split)
        self.split.add(self.editor_frame, weight=3)

        self.editor = tk.Text(
            self.editor_frame, wrap=tk.NONE, undo=True, font=("Consolas", 11)
        )
        self.editor.grid(row=0, column=0, sticky="nsew")

        self.editor_y_scroll = ttk.Scrollbar(
            self.editor_frame,
            orient=tk.VERTICAL,
            command=self.editor.yview,
            style="Minimal.Vertical.TScrollbar",
        )
        self.editor_y_scroll.grid(row=0, column=1, sticky="ns")

        self.editor_x_scroll = ttk.Scrollbar(
            self.editor_frame,
            orient=tk.HORIZONTAL,
            command=self.editor.xview,
            style="Minimal.Horizontal.TScrollbar",
        )
        self.editor_x_scroll.grid(row=1, column=0, sticky="ew")

        # Fill the bottom-right corner so both scrollbars render cleanly.
        self.scroll_corner = tk.Frame(
            self.editor_frame,
            bd=0,
            highlightthickness=0,
        )
        self.scroll_corner.grid(row=1, column=1, sticky="nsew")

        self.editor.configure(
            yscrollcommand=self.editor_y_scroll.set,
            xscrollcommand=self.editor_x_scroll.set,
        )
        self.editor.tag_configure("match", background="#ffe8a3")
        self.editor.tag_configure("current_match", background="#ffbe55")
        self.editor.tag_configure("trace_align", background="#dbeafe")
        self.editor.tag_configure("trace_match", background="#bbf7d0")
        self.editor.tag_configure("trace_mismatch", background="#fecaca")
        self.editor.bind("<<Modified>>", self._on_text_modified)

        self.editor_frame.rowconfigure(0, weight=1)
        self.editor_frame.rowconfigure(1, weight=0)
        self.editor_frame.columnconfigure(0, weight=1)
        self.editor_frame.columnconfigure(1, weight=0)

        self.viz_frame = ttk.LabelFrame(self.split, text="BMH Visualization", padding=8)
        self.split.add(self.viz_frame, weight=2)

        viz_controls = ttk.Frame(self.viz_frame)
        viz_controls.pack(fill=tk.X, pady=(0, 8))

        ttk.Checkbutton(
            viz_controls,
            text="Full scan (continue after match)",
            variable=self.full_scan_var,
        ).pack(side=tk.LEFT)

        ttk.Button(viz_controls, text="Build Trace", command=self.build_trace).pack(
            side=tk.LEFT, padx=(10, 6)
        )
        ttk.Button(viz_controls, text="Prev", command=self.prev_trace_step).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(viz_controls, text="Next", command=self.next_trace_step).pack(
            side=tk.LEFT
        )
        self.play_button = ttk.Button(
            viz_controls, text="Play", command=self.toggle_animation
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

        ttk.Label(self.viz_frame, textvariable=self.step_var).pack(
            anchor="w", pady=(0, 6)
        )

        self.visual_text = tk.Text(
            self.viz_frame, height=16, wrap=tk.NONE, font=("Consolas", 10)
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

        ttk.Label(self.viz_frame, text="Skip Table").pack(anchor="w")
        self.skip_text = tk.Text(
            self.viz_frame, height=8, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.skip_text.pack(fill=tk.X)
        self.skip_text.configure(state=tk.DISABLED)

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

    def _build_menu(self) -> None:
        self.menu_bar = _CustomMenuBar(self)
        self.menu_bar.pack(fill=tk.X, side=tk.TOP, before=self.container)

        self.file_menu = _DropdownMenu(self)
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

        self.view_menu = _DropdownMenu(self)
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

        self.performance_menu = _DropdownMenu(self)
        self.performance_menu.add_command(
            label="Run Evaluation",
            command=self.run_performance_evaluation,
        )

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.menu_bar.add_cascade(label="Performance", menu=self.performance_menu)

        self._bind_shortcuts()

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-n>", self._on_shortcut_new)
        self.bind_all("<Control-o>", self._on_shortcut_open)
        self.bind_all("<Control-s>", self._on_shortcut_save)
        self.bind_all("<Control-S>", self._on_shortcut_save_as)

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

    def toggle_dark_mode(self) -> None:
        self._apply_theme()

    def toggle_visualization(self) -> None:
        if self.show_visualization_var.get():
            if str(self.viz_frame) not in self.split.panes():
                self.split.add(self.viz_frame, weight=2)
        else:
            if str(self.viz_frame) in self.split.panes():
                self._cancel_animation()
                self.split.forget(self.viz_frame)

    def _apply_theme(self) -> None:
        dark = self.dark_mode_var.get()
        self.style.theme_use("clam")

        if dark:
            colors = {
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
            colors = {
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

        self.configure(bg=colors["bg"])
        self.theme_colors = colors

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
        self.status_label.configure(style="Status.TLabel")
        self.status_frame.configure(
            background=colors["panel"],
            highlightbackground=colors["box_border"],
            highlightcolor=colors["box_border"],
        )

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

        self.menu_bar.update_colors(colors)

        for widget in (self.editor, self.visual_text, self.skip_text):
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

        self.scroll_corner.configure(background=colors["scroll_trough"])

        self._configure_highlight_tags(dark)

    def run_performance_evaluation(self) -> None:
        text = self._get_text_content()
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

        self._show_performance_window(results, len(text), len(pattern), iterations)
        self._set_status("Performance evaluation complete.")

    def _select_benchmark_iterations(self, text_len: int, pattern_len: int) -> int:
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
        if isinstance(result, list):
            return f"{len(result)} matches"
        return str(result)

    def _show_performance_window(
        self,
        results: List[Dict[str, Any]],
        text_len: int,
        pattern_len: int,
        iterations: int,
    ) -> None:
        if self.performance_window and self.performance_window.winfo_exists():
            self.performance_window.destroy()

        self.performance_window = tk.Toplevel(self)
        self.performance_window.title("Performance Evaluation")
        self.performance_window.geometry("920x560")
        self.performance_window.minsize(760, 480)

        colors = self.theme_colors or {
            "bg": "#f5f5f5",
            "panel": "#ffffff",
            "fg": "#1f1f1f",
            "border": "#cfcfcf",
            "muted": "#666666",
            "active": "#ececec",
            "text_bg": "#ffffff",
            "text_fg": "#000000",
            "select_bg": "#cfe3ff",
            "select_fg": "#000000",
        }

        self.performance_window.configure(bg=colors["bg"])
        self._configure_performance_styles(colors)

        summary = (
            f"Text length: {text_len}    Pattern length: {pattern_len}    "
            f"Iterations per operation: {iterations}"
        )
        ttk.Label(
            self.performance_window,
            text=summary,
            anchor="w",
            style="PerfSummary.TLabel",
        ).pack(fill=tk.X, padx=12, pady=(10, 6))

        content_frame = ttk.Frame(self.performance_window, style="Perf.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        tab_bar = tk.Frame(
            content_frame,
            bd=0,
            highlightthickness=0,
            background=colors["panel"],
        )
        tab_bar.pack(fill=tk.X, pady=(0, 6))

        table_tab = tk.Label(
            tab_bar,
            text="Table",
            background=colors["panel"],
            foreground=colors["fg"],
            font=("Segoe UI", 9),
            padx=0,
            pady=0,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        table_tab.pack(side=tk.LEFT, padx=(0, 16))

        graph_tab = tk.Label(
            tab_bar,
            text="Graph",
            background=colors["panel"],
            foreground=colors["muted"],
            font=("Segoe UI", 9),
            padx=0,
            pady=0,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        graph_tab.pack(side=tk.LEFT)

        view_container = ttk.Frame(content_frame, style="Perf.TFrame")
        view_container.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(view_container, style="Perf.TFrame")

        columns = ("operation", "runtime", "memory", "result")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Perf.Treeview",
        )
        tree.heading("operation", text="Operation")
        tree.heading("runtime", text="Avg Runtime (ms)")
        tree.heading("memory", text="Peak Memory (KB)")
        tree.heading("result", text="Result")

        tree.column("operation", width=200, anchor=tk.W)
        tree.column("runtime", width=140, anchor=tk.E)
        tree.column("memory", width=140, anchor=tk.E)
        tree.column("result", width=220, anchor=tk.W)

        tree.tag_configure(
            "perf_even", background=colors["text_bg"], foreground=colors["text_fg"]
        )
        tree.tag_configure(
            "perf_odd", background=colors["panel"], foreground=colors["text_fg"]
        )

        for index, row in enumerate(results):
            row_tag = "perf_even" if index % 2 == 0 else "perf_odd"
            tree.insert(
                "",
                tk.END,
                values=(
                    row["operation"],
                    f"{row['runtime_ms']:.4f}",
                    f"{row['memory_kb']:.2f}",
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
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        graph_frame = ttk.Frame(view_container, style="Perf.TFrame")

        graph_canvas = tk.Canvas(
            graph_frame,
            bd=0,
            highlightthickness=0,
            background=colors["text_bg"],
        )
        graph_canvas.pack(fill=tk.BOTH, expand=True)

        def _redraw(_event: tk.Event) -> None:
            self._render_performance_graph(graph_canvas, results)

        graph_canvas.bind("<Configure>", _redraw)

        def _show_view(name: str) -> None:
            if name == "table":
                graph_frame.pack_forget()
                table_frame.pack(fill=tk.BOTH, expand=True)
                table_tab.configure(foreground=colors["fg"])
                graph_tab.configure(foreground=colors["muted"])
            else:
                table_frame.pack_forget()
                graph_frame.pack(fill=tk.BOTH, expand=True)
                table_tab.configure(foreground=colors["muted"])
                graph_tab.configure(foreground=colors["fg"])

        table_tab.bind("<Button-1>", lambda _event: _show_view("table"))
        graph_tab.bind("<Button-1>", lambda _event: _show_view("graph"))

        _show_view("table")
        self._render_performance_graph(graph_canvas, results)

    def _configure_performance_styles(self, colors: Dict[str, str]) -> None:
        self.style.configure(
            "PerfSummary.TLabel",
            background=colors["bg"],
            foreground=colors["fg"],
        )
        self.style.configure(
            "Perf.TFrame",
            background=colors["panel"],
        )

        self.style.configure(
            "Perf.TNotebook",
            background=colors["panel"],
            borderwidth=0,
            relief="flat",
            bordercolor=colors["panel"],
            lightcolor=colors["panel"],
            darkcolor=colors["panel"],
            tabmargins=(0, 0, 0, 0),
        )
        self.style.configure(
            "Perf.TNotebook.Tab",
            background=colors["panel"],
            foreground=colors["fg"],
            padding=(10, 4),
            borderwidth=0,
            relief="flat",
            lightcolor=colors["panel"],
            darkcolor=colors["panel"],
        )
        self.style.layout(
            "Perf.TNotebook.Tab",
            [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Notebook.label",
                                            {"side": "top", "sticky": ""},
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        self.style.map(
            "Perf.TNotebook.Tab",
            background=[("selected", colors["panel"]), ("active", colors["panel"])],
            foreground=[("selected", colors["fg"]), ("active", colors["fg"])],
        )

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
        self.style.layout(
            "Perf.Treeview",
            [("Treeview.treearea", {"sticky": "nswe"})],
        )
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

    def _render_performance_graph(
        self,
        canvas: tk.Canvas,
        results: List[Dict[str, Any]],
    ) -> None:
        canvas.delete("all")

        colors = self.theme_colors or {
            "panel": "#ffffff",
            "fg": "#1f1f1f",
            "border": "#cfcfcf",
            "active": "#ececec",
            "text_bg": "#ffffff",
            "button_active_border": "#9aa8c3",
            "input_focus": "#8ea2c6",
        }

        canvas.configure(background=colors["text_bg"])

        width = max(760, canvas.winfo_width())
        height = max(320, canvas.winfo_height())
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

        runtime_color = colors.get("button_active_border", "#3b82f6")
        memory_color = colors.get("input_focus", "#f59e0b")

        canvas.create_text(
            width / 2,
            24,
            text="Performance Comparison",
            fill=colors["fg"],
            font=("Segoe UI", 11, "bold"),
        )

        self._draw_metric_chart(
            canvas,
            results,
            "runtime_ms",
            "Avg Runtime (ms)",
            runtime_x,
            chart_y,
            chart_w,
            chart_h,
            runtime_color,
            colors["fg"],
            colors["border"],
            colors["panel"],
            colors["active"],
        )
        self._draw_metric_chart(
            canvas,
            results,
            "memory_kb",
            "Peak Memory (KB)",
            memory_x,
            chart_y,
            chart_w,
            chart_h,
            memory_color,
            colors["fg"],
            colors["border"],
            colors["panel"],
            colors["active"],
        )

    def _draw_metric_chart(
        self,
        canvas: tk.Canvas,
        results: List[Dict[str, Any]],
        metric_key: str,
        title: str,
        x: int,
        y: int,
        width: int,
        height: int,
        bar_color: str,
        text_color: str,
        border_color: str,
        chart_bg: str,
        grid_color: str,
    ) -> None:
        values = [float(item[metric_key]) for item in results]
        max_value = max(values) if values else 1.0
        max_value = max(max_value, 1e-9)

        canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=chart_bg,
            outline=border_color,
            width=1,
        )

        for i in range(1, 5):
            y_line = y + int((height / 5) * i)
            canvas.create_line(
                x + 1,
                y_line,
                x + width - 1,
                y_line,
                fill=grid_color,
            )

        canvas.create_text(
            x + width / 2,
            y - 18,
            text=title,
            fill=text_color,
            font=("Segoe UI", 10, "bold"),
        )

        slot_w = width / max(1, len(results))
        bar_w = slot_w * 0.55

        for index, item in enumerate(results):
            value = float(item[metric_key])
            bar_h = (value / max_value) * (height - 28)
            left = x + index * slot_w + (slot_w - bar_w) / 2
            top = y + height - bar_h

            canvas.create_rectangle(
                left,
                top,
                left + bar_w,
                y + height,
                fill=bar_color,
                outline="",
            )
            canvas.create_text(
                left + bar_w / 2,
                top - 12,
                text=f"{value:.2f}",
                fill=text_color,
                font=("Segoe UI", 8),
            )
            canvas.create_text(
                left + bar_w / 2,
                y + height + 14,
                text=item["operation"],
                fill=text_color,
                font=("Segoe UI", 8),
                width=max(70, int(slot_w) - 8),
            )

    def _configure_highlight_tags(self, dark: bool) -> None:
        if dark:
            self.editor.tag_configure(
                "match", background="#6f5a12", foreground="#fff2bf"
            )
            self.editor.tag_configure(
                "current_match", background="#a06c00", foreground="#fff2bf"
            )
            self.editor.tag_configure(
                "trace_align", background="#1f3550", foreground="#e8f1ff"
            )
            self.editor.tag_configure(
                "trace_match", background="#23523a", foreground="#dcfce7"
            )
            self.editor.tag_configure(
                "trace_mismatch", background="#6a2c2c", foreground="#ffe4e6"
            )

            self.visual_text.tag_configure(
                "viz_align", background="#26364a", foreground="#e8f1ff"
            )
            self.visual_text.tag_configure(
                "viz_match", background="#1f5a3f", foreground="#dcfce7"
            )
            self.visual_text.tag_configure(
                "viz_mismatch", background="#6a2b2b", foreground="#ffe4e6"
            )
            self.visual_text.tag_configure("viz_result_match", foreground="#86efac")
            self.visual_text.tag_configure("viz_result_mismatch", foreground="#fca5a5")
        else:
            self.editor.tag_configure(
                "match", background="#ffe8a3", foreground="#000000"
            )
            self.editor.tag_configure(
                "current_match", background="#ffbe55", foreground="#000000"
            )
            self.editor.tag_configure(
                "trace_align", background="#dbeafe", foreground="#000000"
            )
            self.editor.tag_configure(
                "trace_match", background="#bbf7d0", foreground="#000000"
            )
            self.editor.tag_configure(
                "trace_mismatch", background="#fecaca", foreground="#000000"
            )

            self.visual_text.tag_configure(
                "viz_align", background="#e8eefc", foreground="#000000"
            )
            self.visual_text.tag_configure(
                "viz_match", background="#dcfce7", foreground="#166534"
            )
            self.visual_text.tag_configure(
                "viz_mismatch", background="#fee2e2", foreground="#991b1b"
            )
            self.visual_text.tag_configure("viz_result_match", foreground="#166534")
            self.visual_text.tag_configure("viz_result_mismatch", foreground="#991b1b")

    def _on_text_modified(self, _event: tk.Event) -> None:
        if self.editor.edit_modified():
            self.is_dirty = True
            self._update_window_title()
            self.editor.edit_modified(False)

    def _update_window_title(self) -> None:
        name = self.current_file if self.current_file else "Untitled"
        dirty = " *" if self.is_dirty else ""
        self.title(f"Simple Skips Text Editor - {name}{dirty}")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _get_text_content(self) -> str:
        return self.editor.get("1.0", "end-1c")

    def _set_text_content(self, content: str) -> None:
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.editor.edit_modified(False)

    def _offset_to_index(self, offset: int) -> str:
        return f"1.0+{offset}c"

    def _cursor_offset(self) -> int:
        count = self.editor.count("1.0", "insert", "chars")
        if not count:
            return 0
        return int(count[0])

    def _confirm_discard_if_needed(self) -> bool:
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

    def new_file(self) -> None:
        if not self._confirm_discard_if_needed():
            return

        self.current_file = None
        self._set_text_content("")
        self.is_dirty = False
        self._update_window_title()
        self.clear_highlights()
        self._set_status("Started a new file.")

    def open_file(self) -> None:
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
        self._set_text_content(content)
        self.is_dirty = False
        self._update_window_title()
        self.clear_highlights()
        self._set_status(f"Opened {path}")

    def save_file(self) -> bool:
        if not self.current_file:
            return self.save_as_file()

        try:
            with open(self.current_file, "w", encoding="utf-8") as handle:
                handle.write(self._get_text_content())
        except OSError as exc:
            messagebox.showerror("Save Failed", str(exc))
            return False

        self.is_dirty = False
        self._update_window_title()
        self._set_status(f"Saved {self.current_file}")
        return True

    def save_as_file(self) -> bool:
        path = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return False

        self.current_file = path
        return self.save_file()

    def _on_close(self) -> None:
        self._cancel_animation()
        if self._confirm_discard_if_needed():
            self.destroy()

    def clear_highlights(self) -> None:
        self.editor.tag_remove("match", "1.0", tk.END)
        self.editor.tag_remove("current_match", "1.0", tk.END)
        self._clear_trace_highlights()

    def _clear_trace_highlights(self) -> None:
        self.editor.tag_remove("trace_align", "1.0", tk.END)
        self.editor.tag_remove("trace_match", "1.0", tk.END)
        self.editor.tag_remove("trace_mismatch", "1.0", tk.END)

    def _highlight_range(
        self, start_offset: int, end_offset: int, current: bool = False
    ) -> None:
        start_index = self._offset_to_index(start_offset)
        end_index = self._offset_to_index(end_offset)

        if current:
            self.editor.tag_add("current_match", start_index, end_index)
        else:
            self.editor.tag_add("match", start_index, end_index)

    def _find_next_from(self, pattern: str, start_offset: int) -> Tuple[int, bool]:
        content = self._get_text_content()
        index = bmh_search(content, pattern, start_offset)
        wrapped = False

        if index == -1 and start_offset > 0:
            index = bmh_search(content, pattern, 0)
            wrapped = index != -1

        return index, wrapped

    def find_next(self) -> None:
        pattern = self.find_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        self.clear_highlights()
        start = self._cursor_offset()
        index, wrapped = self._find_next_from(pattern, start)

        if index == -1:
            self._set_status("No match found.")
            return

        self._highlight_range(index, index + len(pattern), current=True)
        self.editor.mark_set("insert", self._offset_to_index(index + len(pattern)))
        self.editor.see(self._offset_to_index(index))

        if wrapped:
            self._set_status(f"Found at index {index} (wrapped to start).")
        else:
            self._set_status(f"Found at index {index}.")

    def find_all(self) -> None:
        pattern = self.find_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        self.clear_highlights()
        content = self._get_text_content()
        matches = bmh_find_all(content, pattern, allow_overlap=True)

        for index in matches:
            self._highlight_range(index, index + len(pattern), current=False)

        if matches:
            self._set_status(f"Highlighted {len(matches)} match(es).")
        else:
            self._set_status("No matches found.")

    def replace_next(self) -> None:
        pattern = self.find_var.get()
        replacement = self.replace_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        start = self._cursor_offset()
        index, wrapped = self._find_next_from(pattern, start)

        if index == -1:
            self._set_status("No match found to replace.")
            return

        start_index = self._offset_to_index(index)
        end_index = self._offset_to_index(index + len(pattern))
        self.editor.delete(start_index, end_index)
        self.editor.insert(start_index, replacement)

        self.clear_highlights()
        replacement_end = index + len(replacement)
        self._highlight_range(index, replacement_end, current=True)
        self.editor.mark_set("insert", self._offset_to_index(replacement_end))
        self.editor.see(start_index)

        self.is_dirty = True
        self._update_window_title()

        if wrapped:
            self._set_status(f"Replaced at index {index} (wrapped to start).")
        else:
            self._set_status(f"Replaced at index {index}.")

    def replace_all(self) -> None:
        pattern = self.find_var.get()
        replacement = self.replace_var.get()
        if not pattern:
            self._set_status("Find text is empty.")
            return

        original = self._get_text_content()
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

        self._set_text_content(updated)
        self.clear_highlights()
        self.is_dirty = True
        self._update_window_title()
        self._set_status(f"Replaced {len(matches)} occurrence(s).")

    def build_trace(self) -> None:
        self._cancel_animation()
        pattern = self.find_var.get()
        if not pattern:
            self._set_status("Find text is empty. Enter pattern first.")
            return

        text = self._get_text_content()
        if not text:
            self._set_status("Editor is empty. Add text to visualize BMH.")
            return

        cursor_start = self._cursor_offset()
        stop_on_match = not self.full_scan_var.get()

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
            self.step_var.set("Step 0/0")
            self._render_skip_table(pattern)
            self._set_readonly_text(
                self.visual_text, "No steps available for this input."
            )
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
        self._cancel_animation()
        if not self.trace_steps:
            self._set_status("Build a trace first.")
            return

        if self.trace_step_index > 0:
            self.trace_step_index -= 1
            self._render_trace_step()

    def next_trace_step(self) -> None:
        self._cancel_animation()
        if not self.trace_steps:
            self._set_status("Build a trace first.")
            return

        if self.trace_step_index < len(self.trace_steps) - 1:
            self.trace_step_index += 1
            self._render_trace_step()

    def toggle_animation(self) -> None:
        if self.is_animating:
            self._cancel_animation(update_status=True)
            return

        if not self.trace_steps:
            self._set_status("Build a trace first.")
            return

        self.is_animating = True
        self.play_button.configure(text="Stop")
        self._set_status("Animation started.")
        self._animate_trace_step()

    def _animate_trace_step(self) -> None:
        if not self.is_animating:
            return

        self._render_trace_step()

        if self.trace_step_index >= len(self.trace_steps) - 1:
            self._cancel_animation(update_status=True, message="Animation completed.")
            return

        self.trace_step_index += 1
        delay = max(80, int(self.animation_delay_var.get()))
        self.animation_job = self.after(delay, self._animate_trace_step)

    def _cancel_animation(
        self,
        update_status: bool = False,
        message: str = "Animation stopped.",
    ) -> None:
        if self.animation_job is not None:
            self.after_cancel(self.animation_job)
            self.animation_job = None

        was_animating = self.is_animating
        self.is_animating = False
        self.play_button.configure(text="Play")

        if update_status and was_animating:
            self._set_status(message)

    def _render_trace_step(self) -> None:
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

        self._clear_trace_highlights()
        if len(pattern) > 0:
            align_start = self._offset_to_index(step.alignment)
            align_end = self._offset_to_index(step.alignment + len(pattern))
            self.editor.tag_add("trace_align", align_start, align_end)

        for (
            text_index,
            _pattern_index,
            _text_char,
            _pattern_char,
            matched,
        ) in step.comparisons:
            tag_name = "trace_match" if matched else "trace_mismatch"
            self.editor.tag_add(
                tag_name,
                self._offset_to_index(text_index),
                self._offset_to_index(text_index + 1),
            )

        self.editor.see(self._offset_to_index(step.alignment))

        self.step_var.set(f"Step {self.trace_step_index + 1}/{len(self.trace_steps)}")

    def _render_skip_table(self, pattern: str) -> None:
        if not pattern:
            self._set_readonly_text(self.skip_text, "No pattern set.")
            return

        table = build_skip_table(pattern)
        rows = [f"Default shift: {len(pattern)}"]

        if table:
            rows.append("Custom shifts:")
            for char in sorted(table.keys()):
                rows.append(f"  '{display_char(char)}' -> {table[char]}")
        else:
            rows.append("Pattern length is 1, so only default shift is used.")

        self._set_readonly_text(self.skip_text, "\n".join(rows))

    def _set_readonly_text(self, widget: tk.Text, content: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.configure(state=tk.DISABLED)
