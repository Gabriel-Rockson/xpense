from dataclasses import dataclass
from datetime import date
from functools import cached_property

import pandas as pd
import streamlit as st

from xpense.storage import TransactionStorage


@dataclass
class DashboardData:
    """Encapsulates transaction data with computed columns and filtering."""

    df: pd.DataFrame

    @cached_property
    def enriched(self) -> pd.DataFrame:
        """Add computed columns once and cache the result."""
        df = self.df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = df["amount"].astype(float)
        df["signed_amount"] = df.apply(
            lambda row: row["amount"] if row["type"] == "income" else -row["amount"],
            axis=1,
        )
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%Y-%m")
        return df

    def filter(
        self,
        date_range: tuple[date, date] | None = None,
        categories: list[str] | None = None,
        accounts: list[str] | None = None,
        transaction_type: str = "all",
    ) -> "DashboardData":
        """Return new DashboardData with filters applied."""
        df = self.enriched

        if date_range:
            start, end = date_range
            df = df[
                (df["date"] >= pd.to_datetime(start))
                & (df["date"] <= pd.to_datetime(end))
            ]

        if categories:
            df = df[df["category"].isin(categories)]

        if accounts:
            df = df[df["account"].isin(accounts)]

        if transaction_type != "all":
            df = df[df["type"] == transaction_type]

        return DashboardData(df.reset_index(drop=True))

    @property
    def income(self) -> pd.DataFrame:
        """Return only income transactions."""
        return self.enriched[self.enriched["type"] == "income"]

    @property
    def expenses(self) -> pd.DataFrame:
        """Return only expense transactions."""
        return self.enriched[self.enriched["type"] == "expense"]

    @property
    def is_empty(self) -> bool:
        """Check if dataset is empty."""
        return len(self.df) == 0

    @property
    def date_range(self) -> tuple[date, date]:
        """Get min and max dates in dataset."""
        dates = self.enriched["date"]
        return (dates.min().date(), dates.max().date())

    @property
    def all_categories(self) -> list[str]:
        """Get sorted list of all categories."""
        return sorted(self.enriched["category"].unique().tolist())

    @property
    def all_accounts(self) -> list[str]:
        """Get sorted list of all accounts."""
        return sorted(self.enriched["account"].unique().tolist())


@st.cache_data
def load_data() -> DashboardData | None:
    """Load transaction data with validation and error handling."""
    try:
        storage = TransactionStorage()
        transactions = storage.get_transactions()

        if not transactions:
            return None

        df = pd.DataFrame(transactions)

        required_columns = ["date", "type", "amount", "category", "account", "note"]
        missing = set(required_columns) - set(df.columns)
        if missing:
            st.error(f"CSV missing required columns: {', '.join(missing)}")
            return None

        return DashboardData(df)

    except FileNotFoundError:
        return None
    except pd.errors.ParserError as e:
        st.error(f"Failed to parse CSV file: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error loading data: {e}")
        return None
