"""Display utilities using Rich for beautiful terminal output."""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.text import Text


console = Console()


def format_amount(amount: float, transaction_type: str) -> Text:
    """
    Format amount with color based on transaction type.

    Args:
        amount: Transaction amount
        transaction_type: "income" or "expense"

    Returns:
        Rich Text object with colored amount
    """
    if transaction_type == "income":
        return Text(f"+${amount:.2f}", style="bold green")
    else:
        return Text(f"-${amount:.2f}", style="bold red")


def format_balance(balance: float) -> Text:
    """
    Format balance with color based on positive/negative.

    Args:
        balance: Balance amount

    Returns:
        Rich Text object with colored balance
    """
    color = "green" if balance >= 0 else "red"
    sign = "+" if balance >= 0 else ""
    return Text(f"{sign}${balance:.2f}", style=f"bold {color}")


def show_success(message: str) -> None:
    """Show success message with checkmark."""
    console.print(f"[green]✓[/green] {message}")


def show_error(message: str) -> None:
    """Show error message."""
    console.print(f"[red]✗[/red] {message}", style="red")


def show_transaction_list(
    transactions: List[Dict[str, str]],
    title: str = "Transactions"
) -> None:
    """
    Display transactions in a table.

    Args:
        transactions: List of transaction dictionaries
        title: Table title
    """
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

        # Add emoji for type
        type_emoji = "💰" if t["type"] == "income" else "💸"
        type_display = f"{type_emoji} {t['type'].title()}"

        table.add_row(
            t["date"],
            type_display,
            formatted_amount,
            t["category"],
            t.get("account", "default"),
            t["note"] or "-"
        )

    console.print(table)


def show_total(
    total: float,
    filters: Dict[str, any]
) -> None:
    """
    Display total with filter information.

    Args:
        total: Total amount
        filters: Dictionary of applied filters
    """
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


def show_balance(balance_data: Dict[str, float], month: int = None, account: str = None) -> None:
    """
    Display balance breakdown.

    Args:
        balance_data: Dictionary with income, expenses, and balance
        month: Optional month filter
        account: Optional account filter
    """
    title = f"💵 Balance"
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

    # Income row
    income_text = Text(f"+${balance_data['income']:.2f}", style="bold green")
    table.add_row("Income", income_text)

    # Expenses row
    expenses_text = Text(f"-${balance_data['expenses']:.2f}", style="bold red")
    table.add_row("Expenses", expenses_text)

    # Balance row
    table.add_row("─" * 10, "─" * 10)
    balance_text = format_balance(balance_data['balance'])
    table.add_row("Balance", balance_text)

    console.print(table)


def show_report(
    breakdown: Dict[str, Dict[str, float]],
    month: int = None,
    account: str = None
) -> None:
    """
    Display detailed report by category.

    Args:
        breakdown: Dictionary with income and expense breakdowns by category
        month: Optional month filter
        account: Optional account filter
    """
    title = f"📊 Report"
    filter_parts = []
    if month:
        filter_parts.append(f"Month: {month}")
    if account:
        filter_parts.append(f"Account: {account}")

    if filter_parts:
        title += f" ({' | '.join(filter_parts)})"

    # Income table
    if breakdown["income"]:
        income_table = Table(
            title=f"{title} - Income",
            show_header=True,
            header_style="bold green"
        )
        income_table.add_column("Category", style="cyan")
        income_table.add_column("Amount", justify="right")

        income_total = 0.0
        for category, amount in sorted(breakdown["income"].items()):
            income_total += amount
            income_table.add_row(
                category,
                Text(f"+${amount:.2f}", style="green")
            )

        income_table.add_row("─" * 20, "─" * 15)
        income_table.add_row(
            "[bold]Total Income[/bold]",
            Text(f"+${income_total:.2f}", style="bold green")
        )

        console.print(income_table)
        console.print()

    # Expense table
    if breakdown["expense"]:
        expense_table = Table(
            title=f"{title} - Expenses",
            show_header=True,
            header_style="bold red"
        )
        expense_table.add_column("Category", style="cyan")
        expense_table.add_column("Amount", justify="right")

        expense_total = 0.0
        for category, amount in sorted(breakdown["expense"].items()):
            expense_total += amount
            expense_table.add_row(
                category,
                Text(f"-${amount:.2f}", style="red")
            )

        expense_table.add_row("─" * 20, "─" * 15)
        expense_table.add_row(
            "[bold]Total Expenses[/bold]",
            Text(f"-${expense_total:.2f}", style="bold red")
        )

        console.print(expense_table)
        console.print()

    # Net balance
    income_total = sum(breakdown["income"].values())
    expense_total = sum(breakdown["expense"].values())
    net_balance = income_total - expense_total

    console.print(f"[bold]Net Balance:[/bold] {format_balance(net_balance)}")
    console.print()


def show_categories(
    categories: List[str],
    transaction_type: str = "all"
) -> None:
    """
    Display list of categories.

    Args:
        categories: List of category names
        transaction_type: Type filter applied
    """
    if not categories:
        console.print("[yellow]No categories found.[/yellow]")
        return

    type_label = transaction_type.title() if transaction_type != "all" else "All"
    console.print(f"\n[bold cyan]Categories ({type_label}):[/bold cyan]")

    for category in categories:
        console.print(f"  • {category}")

    console.print()


def show_accounts(
    accounts: List[str],
    transaction_type: str = "all"
) -> None:
    """
    Display list of accounts.

    Args:
        accounts: List of account names
        transaction_type: Type filter applied
    """
    if not accounts:
        console.print("[yellow]No accounts found.[/yellow]")
        return

    type_label = transaction_type.title() if transaction_type != "all" else "All"
    console.print(f"\n[bold yellow]Accounts ({type_label}):[/bold yellow]")

    for account in accounts:
        console.print(f"  • {account}")

    console.print()


def show_account_balances(
    balances: Dict[str, Dict[str, float]],
    month: int = None
) -> None:
    """
    Display balance breakdown by account.

    Args:
        balances: Dictionary mapping account names to balance data
        month: Optional month filter
    """
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
        income = balance_data['income']
        expenses = balance_data['expenses']
        balance = balance_data['balance']

        total_income += income
        total_expenses += expenses
        total_balance += balance

        table.add_row(
            account,
            f"+${income:.2f}",
            f"-${expenses:.2f}",
            format_balance(balance)
        )

    # Add totals row
    table.add_row("─" * 10, "─" * 10, "─" * 10, "─" * 10)
    table.add_row(
        "[bold]TOTAL[/bold]",
        Text(f"+${total_income:.2f}", style="bold green"),
        Text(f"-${total_expenses:.2f}", style="bold red"),
        format_balance(total_balance)
    )

    console.print(table)