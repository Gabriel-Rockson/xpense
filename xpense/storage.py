"""Storage layer for xpense transactions."""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class TransactionStorage:
    """Manages transaction storage in CSV format."""

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = Path.home() / ".xpense"

        self.data_dir = data_dir

        is_dev = os.getenv("XPENSE_ENV", "production") == "development"
        csv_filename = "expenses.dev.csv" if is_dev else "expenses.csv"
        self.csv_path = data_dir / csv_filename

        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            self._write_header()

    def _write_header(self) -> None:
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "amount", "category", "account", "note"])

    def add_transaction(
        self,
        transaction_type: str,
        amount: float,
        category: str,
        account: str = "default",
        note: str = "",
        date: Optional[datetime] = None,
    ) -> dict[str, str]:
        if date is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
        normalized_category = category.lower().replace(" ", "_")
        normalized_account = account.lower().replace(" ", "_")

        transaction = {
            "date": timestamp,
            "type": transaction_type,
            "amount": str(amount),
            "category": normalized_category,
            "account": normalized_account,
            "note": note,
        }

        with open(self.csv_path, "a", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["date", "type", "amount", "category", "account", "note"]
            )
            writer.writerow(transaction)

        return transaction

    def get_transactions(
        self,
        month: Optional[int] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        account: Optional[str] = None,
    ) -> list[dict[str, str]]:
        if not self.csv_path.exists():
            return []

        transactions = []

        with open(self.csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if month is not None:
                    transaction_date = datetime.strptime(
                        row["date"], "%Y-%m-%d %H:%M:%S"
                    )
                    if transaction_date.month != month:
                        continue

                if category is not None:
                    normalized_category = category.lower().replace(" ", "_")
                    if row["category"] != normalized_category:
                        continue

                if transaction_type is not None and transaction_type != "all":
                    if row["type"] != transaction_type:
                        continue

                if account is not None:
                    normalized_account = account.lower().replace(" ", "_")
                    if row.get("account", "default") != normalized_account:
                        continue

                transactions.append(row)

        return transactions

    def get_categories(self, transaction_type: Optional[str] = None) -> list[str]:
        transactions = self.get_transactions(transaction_type=transaction_type)
        categories = set(t["category"] for t in transactions)
        return sorted(categories)

    def get_accounts(self, transaction_type: Optional[str] = None) -> list[str]:
        transactions = self.get_transactions(transaction_type=transaction_type)
        accounts = set(t.get("account", "default") for t in transactions)
        return sorted(accounts)

    def calculate_total(
        self,
        month: Optional[int] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        account: Optional[str] = None,
    ) -> float:
        transactions = self.get_transactions(
            month=month,
            category=category,
            transaction_type=transaction_type,
            account=account,
        )

        total = 0.0
        for t in transactions:
            amount = float(t["amount"])
            if t["type"] == "expense":
                total -= amount
            else:
                total += amount

        return total

    def calculate_balance(
        self, month: Optional[int] = None, account: Optional[str] = None
    ) -> dict[str, float]:
        transactions = self.get_transactions(month=month, account=account)

        income = sum(float(t["amount"]) for t in transactions if t["type"] == "income")
        expenses = sum(
            float(t["amount"]) for t in transactions if t["type"] == "expense"
        )
        balance = income - expenses

        return {"income": income, "expenses": expenses, "balance": balance}

    def get_category_breakdown(
        self, month: Optional[int] = None, account: Optional[str] = None
    ) -> dict[str, dict[str, float]]:
        transactions = self.get_transactions(month=month, account=account)

        breakdown = {"income": {}, "expense": {}}

        for t in transactions:
            category = t["category"]
            amount = float(t["amount"])
            transaction_type = t["type"]

            if category not in breakdown[transaction_type]:
                breakdown[transaction_type][category] = 0.0

            breakdown[transaction_type][category] += amount

        return breakdown

    def get_account_balances(
        self, month: Optional[int] = None
    ) -> dict[str, dict[str, float]]:
        accounts = self.get_accounts()
        balances = {}

        for account in accounts:
            balances[account] = self.calculate_balance(month=month, account=account)

        return balances

    def export_to_csv(self, output_path: Path) -> int:
        transactions = self.get_transactions()

        with open(output_path, "w", newline="") as f:
            if transactions:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "date",
                        "type",
                        "amount",
                        "category",
                        "account",
                        "note",
                    ],
                )
                writer.writeheader()
                writer.writerows(transactions)

        return len(transactions)
