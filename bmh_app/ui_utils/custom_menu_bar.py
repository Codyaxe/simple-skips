"""Custom themed menu bar implementation."""

from typing import Dict, Optional

import tkinter as tk

from .dropdown_menu import DropdownMenu


class CustomMenuBar(tk.Frame):
    """Themed text menu bar that opens DropdownMenu popups."""

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, bd=0, highlightthickness=0)
        self._dropdowns: Dict[str, DropdownMenu] = {}
        self._buttons: Dict[str, tk.Label] = {}
        self._colors: Dict[str, str] = {}
        self._active: Optional[str] = None
        parent.bind("<Button-1>", self._on_global_click, "+")

    def add_cascade(self, label: str, menu: DropdownMenu) -> None:
        """Add a cascade menu to the menu bar."""
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
        """Update menu bar colors for theme changes."""
        self._colors = colors
        self.configure(bg=colors["panel"])
        for btn in self._buttons.values():
            btn.configure(background=colors["panel"], foreground=colors["fg"])

    def close_all(self) -> None:
        """Close all open dropdowns."""
        for dropdown in self._dropdowns.values():
            dropdown.close()
        self._active = None

    def _hover(self, btn: tk.Label, entering: bool) -> None:
        """Handle button hover."""
        if not self._colors:
            return
        target = self._colors["active"] if entering else self._colors["panel"]
        btn.configure(background=target)

    def _on_btn_click(self, label: str) -> None:
        """Handle menu button click."""
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
        """Handle global click to close dropdown if clicking outside."""
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
