"""Main entry point for xpense CLI."""

import sys
from datetime import datetime
from xpense.cli import app, add_expense_default


def _parse_date_from_args():
    """Parse and remove --date or -d flag from sys.argv."""
    date = None
    date_str = None

    if "--date" in sys.argv:
        idx = sys.argv.index("--date")
        if idx + 1 < len(sys.argv):
            date_str = sys.argv[idx + 1]
            sys.argv.pop(idx)
            sys.argv.pop(idx)
    elif "-d" in sys.argv:
        idx = sys.argv.index("-d")
        if idx + 1 < len(sys.argv):
            date_str = sys.argv[idx + 1]
            sys.argv.pop(idx)
            sys.argv.pop(idx)

    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            from xpense.display import show_error
            show_error(f"Invalid date format '{date_str}'. Use YYYY-MM-DD (e.g., 2024-01-15)")
            import sys as sys_module
            sys_module.exit(1)

    return date


def main():
    """Entry point that handles default expense syntax."""
    if len(sys.argv) > 1:
        try:
            amount = float(sys.argv[1])
        except ValueError:
            app()
            return

        date = _parse_date_from_args()

        if len(sys.argv) < 3:
            from xpense.display import show_error
            import typer
            show_error("Usage: xpense AMOUNT CATEGORY [NOTE] [--date YYYY-MM-DD]")
            raise typer.Exit(1)

        category = sys.argv[2]
        note = sys.argv[3] if len(sys.argv) > 3 else ""

        add_expense_default(amount, category, None, note, date)
        return

    app()


if __name__ == "__main__":
    main()