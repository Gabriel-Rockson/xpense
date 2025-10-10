from dataclasses import dataclass

from xpense.dashboard.data import DashboardData


@dataclass
class Metrics:
    """Financial KPIs calculated from transaction data."""

    income: float
    expenses: float
    balance: float
    savings_rate: float
    transaction_count: int

    @classmethod
    def from_data(cls, data: DashboardData) -> "Metrics":
        """Calculate all metrics from dashboard data."""
        income_total = data.income["amount"].sum()
        expense_total = data.expenses["amount"].sum()
        balance = income_total - expense_total
        savings_rate = (balance / income_total * 100) if income_total > 0 else 0.0

        return cls(
            income=float(income_total),
            expenses=float(expense_total),
            balance=float(balance),
            savings_rate=float(savings_rate),
            transaction_count=len(data.enriched),
        )
