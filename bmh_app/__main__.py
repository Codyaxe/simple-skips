"""Entry point for the BMH Text Editor application."""

from .main_window import BMHTextEditor


def main() -> None:
    """Launch the application."""
    app = BMHTextEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
