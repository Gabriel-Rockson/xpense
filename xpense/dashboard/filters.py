from dataclasses import dataclass
from datetime import date

import streamlit as st

from xpense.dashboard.data import DashboardData


@dataclass
class FilterState:
    """User-selected filters for dashboard data."""

    date_range: tuple[date, date]
    categories: list[str]
    accounts: list[str]
    transaction_type: str

    @classmethod
    def from_sidebar(cls, data: DashboardData) -> "FilterState":
        """Build filter state from sidebar inputs."""
        min_date, max_date = data.date_range

        raw_date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        date_range = _normalize_date_range(raw_date_range, min_date, max_date)

        all_categories = data.all_categories
        categories = st.sidebar.multiselect(
            "Categories",
            options=all_categories,
            default=all_categories,
        )

        all_accounts = data.all_accounts
        accounts = st.sidebar.multiselect(
            "Accounts",
            options=all_accounts,
            default=all_accounts,
        )

        transaction_type = st.sidebar.selectbox(
            "Transaction Type",
            options=["all", "income", "expense"],
            index=0,
        )

        return cls(
            date_range,
            categories or all_categories,
            accounts or all_accounts,
            transaction_type,
        )

    def apply(self, data: DashboardData) -> DashboardData:
        """Apply filters to data."""
        return data.filter(
            self.date_range,
            self.categories,
            self.accounts,
            self.transaction_type,
        )

    def summary(self) -> str:
        """Generate human-readable filter summary."""
        parts = []

        start, end = self.date_range
        parts.append(f"📅 {start} to {end}")

        if self.transaction_type != "all":
            parts.append(f"🏷️  {self.transaction_type.title()}")

        if len(self.categories) < 10:
            parts.append(f"📂 {len(self.categories)} categories")

        if len(self.accounts) < 10:
            parts.append(f"💳 {len(self.accounts)} accounts")

        return " • ".join(parts)


def _normalize_date_range(
    raw: date | tuple, default_start: date, default_end: date
) -> tuple[date, date]:
    """Ensure date_range is always a valid tuple."""
    if not isinstance(raw, tuple):
        return (default_start, default_end)

    if len(raw) != 2:
        return (default_start, default_end)

    return raw
