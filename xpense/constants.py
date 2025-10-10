from enum import StrEnum


class TransactionType(StrEnum):
    """Transaction types supported by xpense."""

    EXPENSE = "expense"
    INCOME = "income"


CSV_FIELDNAMES = [
    "date",
    "type",
    "amount",
    "category",
    "account",
    "note",
]  # CSV schema field names for transaction storage.
