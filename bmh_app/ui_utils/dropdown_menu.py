"""Custom themed dropdown menu implementation."""

from typing import Any, Callable, Dict, List, Optional

import tkinter as tk


class DropdownMenu:
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
        """Add a command item to the menu."""
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
        """Add a checkbutton item to the menu."""
        self._items.append(
            {
                "type": "checkbutton",
                "label": label,
                "variable": variable,
                "command": command,
            }
        )

    def add_separator(self) -> None:
        """Add a separator line to the menu."""
        self._items.append({"type": "separator"})

    def show(self, x: int, y: int, colors: Dict[str, str]) -> None:
        """Display the dropdown at the given coordinates."""
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
        """Build a single menu row."""
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
        """Check if dropdown is currently open."""
        return bool(self._win and self._win.winfo_exists())

    def close(self) -> None:
        """Close the dropdown."""
        self._close()

    def _close(self) -> None:
        """Internal close method."""
        if self._win and self._win.winfo_exists():
            self._win.destroy()
        self._win = None
