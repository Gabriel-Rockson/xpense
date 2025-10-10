import sys
from datetime import datetime

import typer

from xpense.cli import add_expense_default, app
from xpense.display import show_error
from xpense.utils import parse_date_arg


def _parse_date_from_args() -> datetime | None:
    """Parse and remove --date or -d flag from sys.argv."""
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
            return parse_date_arg(date_str)
        except ValueError as e:
            show_error(str(e))
            sys.exit(1)

    return None


def main() -> None:
    """Entry point that handles default expense syntax."""
    if len(sys.argv) > 1:
        try:
            amount = float(sys.argv[1])
        except ValueError:
            app()
            return

        date = _parse_date_from_args()

        if len(sys.argv) < 3:
            show_error("Usage: xpense AMOUNT CATEGORY [NOTE] [--date YYYY-MM-DD]")
            raise typer.Exit(1)

        category = sys.argv[2]
        note = sys.argv[3] if len(sys.argv) > 3 else ""

        add_expense_default(amount, category, None, note, date)
        return

    app()


if __name__ == "__main__":
    main()

