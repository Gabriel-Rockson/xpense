"""CLI commands for xpense using Typer."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from xpense.config import cfg
from xpense.display import (
    console,
    show_balance,
    show_categories,
    show_error,
    show_report,
    show_success,
    show_total,
    show_transaction_list,
)
from xpense.storage import TransactionStorage

app = typer.Typer(
    help="A beautiful CLI expense and income tracker",
    add_completion=False,
    no_args_is_help=False,
)

storage = TransactionStorage()
config = cfg


def _validate_amount(amount: float) -> bool:
    if amount <= 0:
        show_error("Amount must be positive")
        return False
    return True


def _validate_and_get_account(account: str | None) -> str | None:
    if account is None:
        account = config.get_default_account()

    if not config.is_account_registered(account):
        suggestions = config.suggest_accounts(account)
        if suggestions:
            show_error(
                f"Account '{account}' not registered. Did you mean: {', '.join(suggestions)}?"
            )
        else:
            show_error(
                f"Account '{account}' not registered. Add it first with: xpense account add {account}"
            )
        return None

    return account


def _format_account_suffix(account: str) -> str:
    return f" [{account}]" if account != config.get_default_account() else ""


def add_expense_default(
    amount: float, category: str, account: str = None, note: str = "", date: Optional[datetime] = None
) -> None:
    """Add expense with default syntax."""
    try:
        if not _validate_amount(amount):
            sys.exit(1)

        validated_account = _validate_and_get_account(account)
        if validated_account is None:
            sys.exit(1)

        transaction = storage.add_transaction(
            transaction_type="expense",
            amount=amount,
            category=category,
            account=validated_account,
            note=note,
            date=date,
        )

        account_suffix = _format_account_suffix(transaction["account"])
        show_success(
            f"Expense added: -{cfg.currency} {amount:.2f} in {transaction['category']}{account_suffix}"
        )

    except SystemExit:
        raise
    except Exception as e:
        show_error(f"Failed to add expense: {str(e)}")
        sys.exit(1)


@app.command(name="add")
def add_income(
    amount: float,
    category: str,
    note: Annotated[str, typer.Argument()] = "",
    account: Annotated[
        Optional[str],
        typer.Option("--account", "-a", help="Account name (default: from config)"),
    ] = None,
    date: Annotated[
        Optional[str],
        typer.Option("--date", "-d", help="Transaction date in YYYY-MM-DD format"),
    ] = None,
) -> None:
    """Add INCOME transaction (positive/incoming money)."""
    try:
        if not _validate_amount(amount):
            raise typer.Exit(1)

        validated_account = _validate_and_get_account(account)
        if validated_account is None:
            raise typer.Exit(1)

        parsed_date = None
        if date:
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                show_error(f"Invalid date format '{date}'. Use YYYY-MM-DD (e.g., 2024-01-15)")
                raise typer.Exit(1)

        transaction = storage.add_transaction(
            transaction_type="income",
            amount=amount,
            category=category,
            account=validated_account,
            note=note,
            date=parsed_date,
        )

        account_suffix = _format_account_suffix(transaction["account"])
        show_success(
            f"Income added: +{cfg.currency} {amount:.2f} in {transaction['category']}{account_suffix}"
        )

    except typer.Exit:
        raise
    except Exception as e:
        show_error(f"Failed to add income: {str(e)}")
        raise typer.Exit(1)


def _validate_month(month: int | None) -> None:
    if month is not None and (month < 1 or month > 12):
        show_error("Month must be between 1 and 12")
        raise typer.Exit(1)


def _validate_transaction_type(type: str) -> None:
    if type not in ["expense", "income", "all"]:
        show_error("Type must be 'expense', 'income', or 'all'")
        raise typer.Exit(1)


def _build_filter_title(base: str, month: int | None, category: str | None, type: str, account: str | None) -> str:
    parts = [base]
    if month:
        parts.append(f"Month: {month}")
    if category:
        parts.append(f"Category: {category}")
    if type != "all":
        parts.append(f"Type: {type.title()}")
    if account:
        parts.append(f"Account: {account}")
    return " | ".join(parts)


@app.command()
def list(
    month: Annotated[Optional[int], typer.Option(help="Filter by month (1-12)")] = None,
    category: Annotated[Optional[str], typer.Option(help="Filter by category")] = None,
    type: Annotated[
        Optional[str], typer.Option(help="Filter by type: expense, income, or all")
    ] = "all",
    account: Annotated[
        Optional[str], typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """List transactions with optional filters."""
    try:
        _validate_month(month)
        _validate_transaction_type(type)

        transaction_type = None if type == "all" else type
        transactions = storage.get_transactions(
            month=month,
            category=category,
            transaction_type=transaction_type,
            account=account,
        )

        title = _build_filter_title("Transactions", month, category, type, account)
        show_transaction_list(transactions, title=title)

    except Exception as e:
        show_error(f"Failed to list transactions: {str(e)}")
        raise typer.Exit(1)


@app.command()
def total(
    month: Annotated[Optional[int], typer.Option(help="Filter by month (1-12)")] = None,
    category: Annotated[Optional[str], typer.Option(help="Filter by category")] = None,
    account: Annotated[
        Optional[str], typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """Show total with optional filters."""
    try:
        _validate_month(month)
        total_amount = storage.calculate_total(
            month=month, category=category, account=account
        )
        filters = {"month": month, "category": category, "account": account}
        show_total(total_amount, filters)

    except Exception as e:
        show_error(f"Failed to calculate total: {str(e)}")
        raise typer.Exit(1)


@app.command()
def balance(
    month: Annotated[Optional[int], typer.Option(help="Filter by month (1-12)")] = None,
    account: Annotated[
        Optional[str], typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """Show net balance (income - expenses)."""
    try:
        _validate_month(month)
        balance_data = storage.calculate_balance(month=month, account=account)
        show_balance(balance_data, month=month, account=account)

    except Exception as e:
        show_error(f"Failed to calculate balance: {str(e)}")
        raise typer.Exit(1)


@app.command()
def report(
    month: Annotated[Optional[int], typer.Option(help="Filter by month (1-12)")] = None,
    account: Annotated[
        Optional[str], typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """Show beautiful breakdown by category with totals for both income and expenses."""
    try:
        _validate_month(month)
        breakdown = storage.get_category_breakdown(month=month, account=account)
        show_report(breakdown, month=month, account=account)

    except Exception as e:
        show_error(f"Failed to generate report: {str(e)}")
        raise typer.Exit(1)


@app.command()
def categories(
    type: Annotated[
        Optional[str], typer.Option(help="Filter by type: expense, income, or all")
    ] = "all",
) -> None:
    """List all categories used."""
    try:
        _validate_transaction_type(type)
        transaction_type = None if type == "all" else type
        category_list = storage.get_categories(transaction_type=transaction_type)
        show_categories(category_list, transaction_type=type)

    except Exception as e:
        show_error(f"Failed to list categories: {str(e)}")
        raise typer.Exit(1)


@app.command()
def accounts(
    type: Annotated[
        Optional[str], typer.Option(help="Filter by type: expense, income, or all")
    ] = "all",
) -> None:
    """List all accounts used."""
    try:
        _validate_transaction_type(type)

        from xpense.display import show_accounts

        transaction_type = None if type == "all" else type
        account_list = storage.get_accounts(transaction_type=transaction_type)
        show_accounts(account_list, transaction_type=type)

    except Exception as e:
        show_error(f"Failed to list accounts: {str(e)}")
        raise typer.Exit(1)


@app.command(name="account-balances")
def account_balances(
    month: Annotated[Optional[int], typer.Option(help="Filter by month (1-12)")] = None,
) -> None:
    """Show balance breakdown by account."""
    try:
        _validate_month(month)

        from xpense.display import show_account_balances

        balances = storage.get_account_balances(month=month)
        show_account_balances(balances, month=month)

    except Exception as e:
        show_error(f"Failed to calculate account balances: {str(e)}")
        raise typer.Exit(1)


@app.command()
def export(
    output: Annotated[Optional[str], typer.Option(help="Output file path")] = None,
) -> None:
    """Export transactions to CSV."""
    try:
        if output is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            output = f"xpense_{timestamp}.csv"

        output_path = Path(output)
        count = storage.export_to_csv(output_path)

        show_success(f"Exported {count} transactions to {output_path}")

    except Exception as e:
        show_error(f"Failed to export: {str(e)}")
        raise typer.Exit(1)


account_app = typer.Typer(help="Manage accounts")
app.add_typer(account_app, name="account")


@account_app.command(name="add")
def account_add(account_name: str) -> None:
    """Register a new account."""
    try:
        config.add_account(account_name)
        show_success(f"Account '{account_name}' added successfully")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to add account: {str(e)}")
        raise typer.Exit(1)


@account_app.command(name="list")
def account_list() -> None:
    """List all registered accounts."""
    try:
        from rich.table import Table

        accounts = config.get_accounts()
        default_account = config.get_default_account()

        if not accounts:
            console.print("[yellow]No accounts registered.[/yellow]")
            return

        table = Table(
            title="📁 Registered Accounts", show_header=True, header_style="bold cyan"
        )
        table.add_column("Account", style="yellow")
        table.add_column("Default", justify="center")

        for account in sorted(accounts):
            is_default = "✓" if account == default_account else ""
            table.add_row(account, is_default)

        console.print(table)

    except Exception as e:
        show_error(f"Failed to list accounts: {str(e)}")
        raise typer.Exit(1)


@account_app.command(name="remove")
def account_remove(
    account_name: str,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Remove a registered account."""
    try:
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to remove account '{account_name}'?"
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(0)

        config.remove_account(account_name)
        show_success(f"Account '{account_name}' removed successfully")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to remove account: {str(e)}")
        raise typer.Exit(1)


@account_app.command(name="set-default")
def account_set_default(account_name: str) -> None:
    """Set the default account."""
    try:
        config.set_default_account(account_name)
        show_success(f"Default account set to '{account_name}'")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to set default account: {str(e)}")
        raise typer.Exit(1)


config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


@config_app.command(name="show")
def config_show() -> None:
    """Show current configuration."""
    try:
        from rich.table import Table

        table = Table(
            title="⚙️  Configuration", show_header=True, header_style="bold cyan"
        )
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Default Account", config.get_default_account())
        table.add_row("Currency", config.get("currency", "USD"))
        table.add_row("Registered Accounts", ", ".join(config.get_accounts()))

        console.print(table)

    except Exception as e:
        show_error(f"Failed to show config: {str(e)}")
        raise typer.Exit(1)


@config_app.command(name="set-currency")
def config_set_currency(currency_code: str) -> None:
    """Set the currency code (e.g., USD, GHS, EUR)."""
    try:
        config.set_currency(currency_code)
        show_success(f"Currency set to '{config.currency}'")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to set currency: {str(e)}")
        raise typer.Exit(1)


@config_app.command(name="reset")
def config_reset(
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Reset configuration to defaults."""
    try:
        if not force:
            confirm = typer.confirm(
                "Are you sure you want to reset all configuration to defaults?"
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(0)

        config.reset()
        show_success("Configuration reset to defaults")

    except Exception as e:
        show_error(f"Failed to reset config: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

