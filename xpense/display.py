from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text

from xpense.config import cfg
from xpense.constants import TransactionType

console = Console()


def format_amount(amount: float, transaction_type: str) -> Text:
    if transaction_type == TransactionType.INCOME:
        return Text(f"+{cfg.currency} {amount:.2f}", style="bold green")
    else:
        return Text(f"-{cfg.currency} {amount:.2f}", style="bold red")


def format_balance(balance: float) -> Text:
    color = "green" if balance >= 0 else "red"
    sign = "+" if balance >= 0 else ""
    return Text(f"{sign}{cfg.currency} {balance:.2f}", style=f"bold {color}")


def show_success(message: str) -> None:
    console.print(f"[green]✓[/green] {message}")


def show_error(message: str) -> None:
    console.print(f"[red]✗[/red] {message}", style="red")


def show_transaction_list(
    transactions: list[dict[str, str]], title: str = "Transactions"
) -> None:
    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Date", style="dim")
    table.add_column("Type", justify="center")
    table.add_column("Amount", justify="right")
    table.add_column("Category", style="cyan")
    table.add_column("Account", style="yellow")
    table.add_column("Note", style="dim")

    for t in transactions:
        amount = float(t["amount"])
        formatted_amount = format_amount(amount, t["type"])

        type_emoji = "💰" if t["type"] == TransactionType.INCOME else "💸"
        type_display = f"{type_emoji} {t['type'].title()}"

        table.add_row(
            t["date"],
            type_display,
            formatted_amount,
            t["category"],
            t.get("account", "default"),
            t["note"] or "-",
        )

    console.print(table)


def show_total(total: float, filters: dict[str, Any]) -> None:
    filter_parts = []
    if filters.get("month"):
        filter_parts.append(f"Month: {filters['month']}")
    if filters.get("category"):
        filter_parts.append(f"Category: {filters['category']}")
    if filters.get("type"):
        filter_parts.append(f"Type: {filters['type']}")
    if filters.get("account"):
        filter_parts.append(f"Account: {filters['account']}")

    filter_text = " | ".join(filter_parts) if filter_parts else "All transactions"

    console.print(f"\n[bold]Total ({filter_text}):[/bold]")
    console.print(format_balance(total))
    console.print()


def show_balance(
    balance_data: dict[str, float], month: int | None = None, account: str | None = None
) -> None:
    title = "💵 Balance"
    filter_parts = []
    if month:
        filter_parts.append(f"Month: {month}")
    if account:
        filter_parts.append(f"Account: {account}")

    if filter_parts:
        title += f" ({' | '.join(filter_parts)})"

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Category", style="bold")
    table.add_column("Amount", justify="right")

    income_text = Text(
        f"+{cfg.currency} {balance_data['income']:.2f}", style="bold green"
    )
    table.add_row("Income", income_text)

    expenses_text = Text(
        f"-{cfg.currency} {balance_data['expenses']:.2f}", style="bold red"
    )
    table.add_row("Expenses", expenses_text)

    table.add_row("─" * 10, "─" * 10)
    balance_text = format_balance(balance_data["balance"])
    table.add_row("Balance", balance_text)

    console.print(table)


def show_report(
    breakdown: dict[str, dict[str, float]],
    month: int | None = None,
    account: str | None = None,
) -> None:
    title = "📊 Report"
    filter_parts = []
    if month:
        filter_parts.append(f"Month: {month}")
    if account:
        filter_parts.append(f"Account: {account}")

    if filter_parts:
        title += f" ({' | '.join(filter_parts)})"

    if breakdown["income"]:
        income_table = Table(
            title=f"{title} - Income", show_header=True, header_style="bold green"
        )
        income_table.add_column("Category", style="cyan")
        income_table.add_column("Amount", justify="right")

        income_total = 0.0
        for category, amount in sorted(breakdown["income"].items()):
            income_total += amount
            income_table.add_row(
                category, Text(f"+{cfg.currency} {amount:.2f}", style="green")
            )

        income_table.add_row("─" * 20, "─" * 15)
        income_table.add_row(
            "[bold]Total Income[/bold]",
            Text(f"+{cfg.currency} {income_total:.2f}", style="bold green"),
        )

        console.print(income_table)
        console.print()

    if breakdown["expense"]:
        expense_table = Table(
            title=f"{title} - Expenses", show_header=True, header_style="bold red"
        )
        expense_table.add_column("Category", style="cyan")
        expense_table.add_column("Amount", justify="right")

        expense_total = 0.0
        for category, amount in sorted(breakdown["expense"].items()):
            expense_total += amount
            expense_table.add_row(
                category, Text(f"-{cfg.currency} {amount:.2f}", style="red")
            )

        expense_table.add_row("─" * 20, "─" * 15)
        expense_table.add_row(
            "[bold]Total Expenses[/bold]",
            Text(f"-{cfg.currency} {expense_total:.2f}", style="bold red"),
        )

        console.print(expense_table)
        console.print()

    income_total = sum(breakdown["income"].values())
    expense_total = sum(breakdown["expense"].values())
    net_balance = income_total - expense_total

    console.print(f"[bold]Net Balance:[/bold] {format_balance(net_balance)}")
    console.print()


def show_categories(categories: list[str], transaction_type: str = "all") -> None:
    if not categories:
        console.print("[yellow]No categories found.[/yellow]")
        return

    type_label = transaction_type.title() if transaction_type != "all" else "All"
    console.print(f"\n[bold cyan]Categories ({type_label}):[/bold cyan]")

    for category in categories:
        console.print(f"  • {category}")

    console.print()


def show_accounts(accounts: list[str], transaction_type: str = "all") -> None:
    if not accounts:
        console.print("[yellow]No accounts found.[/yellow]")
        return

    type_label = transaction_type.title() if transaction_type != "all" else "All"
    console.print(f"\n[bold yellow]Accounts ({type_label}):[/bold yellow]")

    for account in accounts:
        console.print(f"  • {account}")

    console.print()


def show_account_balances(
    balances: dict[str, dict[str, float]], month: int | None = None
) -> None:
    if not balances:
        console.print("[yellow]No account balances found.[/yellow]")
        return

    title = "💳 Account Balances"
    if month:
        title += f" (Month: {month})"

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Account", style="yellow")
    table.add_column("Income", justify="right", style="green")
    table.add_column("Expenses", justify="right", style="red")
    table.add_column("Balance", justify="right")

    total_income = 0.0
    total_expenses = 0.0
    total_balance = 0.0

    for account, balance_data in sorted(balances.items()):
        income = balance_data["income"]
        expenses = balance_data["expenses"]
        balance = balance_data["balance"]

        total_income += income
        total_expenses += expenses
        total_balance += balance

        table.add_row(
            account,
            f"+{cfg.currency} {income:.2f}",
            f"-{cfg.currency} {expenses:.2f}",
            format_balance(balance),
        )

    table.add_row("─" * 10, "─" * 10, "─" * 10, "─" * 10)
    table.add_row(
        "[bold]TOTAL[/bold]",
        Text(f"+{cfg.currency} {total_income:.2f}", style="bold green"),
        Text(f"-{cfg.currency} {total_expenses:.2f}", style="bold red"),
        format_balance(total_balance),
    )

    console.print(table)
