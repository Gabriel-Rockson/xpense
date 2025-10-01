"""Main entry point for xpense CLI."""

import sys
from xpense.cli import app, add_expense_default


def main():
    """Entry point that handles default expense syntax."""
    if len(sys.argv) > 1:
        try:
            amount = float(sys.argv[1])
        except ValueError:
            app()
            return

        if len(sys.argv) < 3:
            from xpense.display import show_error
            import typer
            show_error("Usage: xpense AMOUNT CATEGORY [NOTE]")
            raise typer.Exit(1)

        category = sys.argv[2]
        note = sys.argv[3] if len(sys.argv) > 3 else ""

        add_expense_default(amount, category, None, note)
        return

    app()


if __name__ == "__main__":
    main()