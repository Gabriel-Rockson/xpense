import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from xpense.config import cfg
from xpense.dashboard.data import DashboardData
from xpense.dashboard.theme import (
    CHART_LAYOUT,
    EXPENSE_PALETTE,
    GRID_CONFIG,
    INCOME_PALETTE,
    Colors,
)


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply consistent theme to any chart."""
    fig.update_layout(**CHART_LAYOUT)
    fig.update_xaxes(**GRID_CONFIG)
    fig.update_yaxes(**GRID_CONFIG)
    return fig


def balance_over_time(data: DashboardData) -> go.Figure:
    """Plot cumulative balance trend over time."""
    df = data.enriched.sort_values("date")
    df["cumulative_balance"] = df["signed_amount"].cumsum()

    fig = px.line(
        df,
        x="date",
        y="cumulative_balance",
        title="Balance Trend Over Time",
        labels={"cumulative_balance": f"Balance ({cfg.currency})", "date": "Date"},
    )

    fig.update_traces(line_color=Colors.INCOME, line_width=3)
    return apply_theme(fig)


def monthly_income_vs_expenses(data: DashboardData) -> go.Figure:
    """Plot monthly income and expenses side by side."""
    monthly = (
        data.enriched.groupby(["month_name", "type"])["amount"]
        .sum()
        .reset_index()
        .pivot(index="month_name", columns="type", values="amount")
        .fillna(0)
        .reset_index()
    )

    fig = go.Figure()

    if "income" in monthly.columns:
        fig.add_trace(
            go.Bar(
                name="Income",
                x=monthly["month_name"],
                y=monthly["income"],
                marker_color=Colors.INCOME,
            )
        )

    if "expense" in monthly.columns:
        fig.add_trace(
            go.Bar(
                name="Expenses",
                x=monthly["month_name"],
                y=monthly["expense"],
                marker_color=Colors.EXPENSE,
            )
        )

    fig.update_layout(
        title="Monthly Income vs Expenses",
        xaxis_title="Month",
        yaxis_title=f"Amount ({cfg.currency})",
        barmode="group",
    )

    return apply_theme(fig)


def category_breakdown_pie(data: DashboardData, transaction_type: str) -> go.Figure:
    """Show category distribution as pie chart."""
    type_data = data.income if transaction_type == "income" else data.expenses
    totals = type_data.groupby("category")["amount"].sum().sort_values(ascending=False)

    palette = INCOME_PALETTE if transaction_type == "income" else EXPENSE_PALETTE

    fig = px.pie(
        values=totals.values,
        names=totals.index,
        title=f"{transaction_type.title()} by Category",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Greens
        if transaction_type == "income"
        else px.colors.sequential.Reds,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    return apply_theme(fig)


def top_categories_bar(
    data: DashboardData, transaction_type: str, limit: int = 10
) -> go.Figure:
    """Show top N categories as horizontal bar chart."""
    type_data = data.income if transaction_type == "income" else data.expenses
    top = (
        type_data.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=True)
        .tail(limit)
    )

    color = Colors.INCOME if transaction_type == "income" else Colors.EXPENSE

    fig = px.bar(
        x=top.values,
        y=top.index,
        orientation="h",
        title=f"Top {limit} {transaction_type.title()} Categories",
        labels={"x": f"Amount ({cfg.currency})", "y": "Category"},
        color_discrete_sequence=[color],
    )

    return apply_theme(fig)


def account_analysis(data: DashboardData) -> go.Figure:
    """Show income, expenses, and balance by account - optimized with groupby."""
    # Fixed performance issue: use groupby instead of loop
    summary = (
        data.enriched.groupby(["account", "type"])["amount"]
        .sum()
        .unstack(fill_value=0.0)
    )

    if "income" not in summary.columns:
        summary["income"] = 0.0
    if "expense" not in summary.columns:
        summary["expense"] = 0.0

    summary["balance"] = summary["income"] - summary["expense"]
    summary = summary.reset_index()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Income",
            x=summary["account"],
            y=summary["income"],
            marker_color=Colors.INCOME,
        )
    )

    fig.add_trace(
        go.Bar(
            name="Expenses",
            x=summary["account"],
            y=summary["expense"],
            marker_color=Colors.EXPENSE,
        )
    )

    fig.add_trace(
        go.Scatter(
            name="Balance",
            x=summary["account"],
            y=summary["balance"],
            mode="lines+markers",
            marker=dict(size=10, color=Colors.BALANCE),
            line=dict(width=3, color=Colors.BALANCE),
        )
    )

    fig.update_layout(
        title="Account Analysis",
        xaxis_title="Account",
        yaxis_title=f"Amount ({cfg.currency})",
    )

    return apply_theme(fig)


def account_summary_table(data: DashboardData) -> pd.DataFrame:
    """Generate account summary table - optimized with groupby."""
    summary = (
        data.enriched.groupby(["account", "type"])["amount"]
        .agg(["count", "sum"])
        .unstack(fill_value=0.0)
    )

    # Flatten column names
    summary.columns = [f"{typ}_{stat}" for stat, typ in summary.columns]
    summary = summary.reset_index()

    # Ensure all required columns exist
    for col in ["income_count", "income_sum", "expense_count", "expense_sum"]:
        if col not in summary.columns:
            summary[col] = 0.0

    summary["total_transactions"] = summary["income_count"] + summary["expense_count"]
    summary["balance"] = summary["income_sum"] - summary["expense_sum"]

    # Rename for display
    summary = summary.rename(
        columns={
            "account": "Account",
            "total_transactions": "Transactions",
            "income_sum": "Income",
            "expense_sum": "Expenses",
            "balance": "Balance",
        }
    )

    return summary[["Account", "Transactions", "Income", "Expenses", "Balance"]]
