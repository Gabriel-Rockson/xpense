from datetime import datetime

import streamlit as st

from xpense.config import cfg
from xpense.dashboard.charts import (
    account_analysis,
    account_summary_table,
    balance_over_time,
    category_breakdown_pie,
    monthly_income_vs_expenses,
    top_categories_bar,
)
from xpense.dashboard.data import DashboardData, load_data
from xpense.dashboard.filters import FilterState
from xpense.dashboard.metrics import Metrics


def configure_page():
    """Set up page configuration and styling."""
    st.set_page_config(
        page_title="xpense Dashboard",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def show_onboarding():
    """Display welcome message for new users."""
    st.title("💰 Welcome to xpense Dashboard")
    st.info("No transactions found. Start tracking your finances!")

    st.subheader("Quick Start")
    st.code("xpense 25.50 lunch 'at the office'", language="bash")
    st.caption("Add an expense")

    st.code("xpense add 1000 salary 'monthly paycheck'", language="bash")
    st.caption("Add income")


def empty_state(message: str, help_command: str | None = None):
    """Show consistent empty state message."""
    st.info(f"📊 {message}")
    if help_command:
        st.code(help_command, language="bash")


def show_header(data: DashboardData, filters: FilterState):
    """Display dashboard title and filter summary."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("💰 xpense Dashboard")
        st.caption(filters.summary())

    with col2:
        st.metric(
            label="Currency",
            value=cfg.currency,
        )
        st.caption(f"Default account: **{cfg.get_default_account()}**")


def show_kpis(data: DashboardData):
    """Display KPI cards with metrics."""
    metrics = Metrics.from_data(data)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total Balance",
            value=f"{cfg.currency} {metrics.balance:,.2f}",
            delta=f"{metrics.savings_rate:.1f}% savings rate",
            delta_color="normal" if metrics.balance >= 0 else "inverse",
        )

    with col2:
        st.metric(
            label="📈 Total Income",
            value=f"{cfg.currency} {metrics.income:,.2f}",
        )

    with col3:
        st.metric(
            label="📉 Total Expenses",
            value=f"{cfg.currency} {metrics.expenses:,.2f}",
        )

    with col4:
        st.metric(
            label="📊 Transactions",
            value=f"{metrics.transaction_count:,}",
        )


def show_trends_tab(data: DashboardData):
    """Display trends and time series analysis."""
    st.subheader("Financial Trends")

    try:
        st.plotly_chart(balance_over_time(data), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render balance trend: {e}")

    try:
        st.plotly_chart(monthly_income_vs_expenses(data), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render monthly comparison: {e}")


def show_categories_tab(data: DashboardData):
    """Display category analysis."""
    st.subheader("Category Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Expenses")
        if data.expenses.empty:
            empty_state("No expenses found")
        else:
            try:
                st.plotly_chart(
                    category_breakdown_pie(data, "expense"), use_container_width=True
                )
                st.plotly_chart(
                    top_categories_bar(data, "expense", limit=10),
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Failed to render expense charts: {e}")

    with col2:
        st.markdown("### Income")
        if data.income.empty:
            empty_state("No income found")
        else:
            try:
                st.plotly_chart(
                    category_breakdown_pie(data, "income"), use_container_width=True
                )
                st.plotly_chart(
                    top_categories_bar(data, "income", limit=10),
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Failed to render income charts: {e}")


def show_accounts_tab(data: DashboardData):
    """Display account overview and details."""
    st.subheader("Account Overview")

    try:
        st.plotly_chart(account_analysis(data), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render account analysis: {e}")

    st.subheader("Account Details")

    try:
        summary = account_summary_table(data)
        st.dataframe(summary, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Failed to generate account summary: {e}")


def show_transactions_tab(data: DashboardData):
    """Display transaction history with sorting."""
    st.subheader("Transaction History")

    col1, col2 = st.columns([3, 1])

    with col1:
        sort_by = st.selectbox(
            "Sort by",
            options=["date", "amount", "category", "account"],
            index=0,
        )

    with col2:
        sort_order = st.radio("Order", options=["Descending", "Ascending"], index=0)

    df = data.enriched.copy()
    df = df.sort_values(sort_by, ascending=(sort_order == "Ascending"))

    display_df = df[
        ["date", "type", "signed_amount", "category", "account", "note"]
    ].copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d %H:%M")

    display_df.columns = ["Date", "Type", "Amount", "Category", "Account", "Note"]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format=f"{cfg.currency} %.2f",
            ),
        },
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"xpense_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def main():
    """Main dashboard entry point."""
    configure_page()

    data = load_data()
    if data is None:
        show_onboarding()
        return

    st.sidebar.header("🎛️ Filters")
    filters = FilterState.from_sidebar(data)
    filtered = filters.apply(data)

    if filtered.is_empty:
        st.warning("No transactions match the selected filters.")
        return

    show_header(filtered, filters)
    st.markdown("---")
    show_kpis(filtered)
    st.markdown("---")

    tabs = st.tabs(["📈 Trends", "🎯 Categories", "💳 Accounts", "📋 Transactions"])

    with tabs[0]:
        show_trends_tab(filtered)

    with tabs[1]:
        show_categories_tab(filtered)

    with tabs[2]:
        show_accounts_tab(filtered)

    with tabs[3]:
        show_transactions_tab(filtered)


if __name__ == "__main__":
    main()
