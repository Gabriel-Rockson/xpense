from datetime import datetime


def normalize_identifier(value: str) -> str:
    return value.lower().replace(" ", "_")


def parse_date_arg(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format '{date_str}'. Use YYYY-MM-DD format.")
