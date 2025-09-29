# xpense

A beautiful CLI expense and income tracker with gorgeous terminal output.

## Features

- Track expenses and income with ease
- Beautiful reports with category breakdowns
- Calculate balance (income - expenses)
- Color-coded output (green for income, red for expenses)
- Simple CSV storage at `~/.xpense/expenses.csv`
- Powerful filtering by month and category
- Export transactions to CSV

## Installation

### From PyPI (recommended)

```bash
pip install xpense
```

### From source

```bash
# Clone the repository
git clone https://github.com/Gabriel-Rockson/xpense.git
cd xpense

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Usage

### Add Transactions

**Add an expense (default behavior):**
```bash
# Quick syntax - amount, category, optional note
xpense 20 transport "to the office"
xpense 45.50 food "lunch at restaurant"
xpense 100 utilities "electricity bill"
```

**Add income:**
```bash
# Use 'add' subcommand for income
xpense add 2000 salary "from day job"
xpense add 500 freelance "web design project"
```

### View Transactions

**List all transactions:**
```bash
xpense list
```

**Filter by month:**
```bash
xpense list --month 3  # March transactions
```

**Filter by category:**
```bash
xpense list --category food
```

**Filter by type:**
```bash
xpense list --type expense  # Only expenses
xpense list --type income   # Only income
```

**Combine filters:**
```bash
xpense list --month 3 --category food --type expense
```

### Calculate Totals

**Total of all transactions:**
```bash
xpense total
```

**Total for a specific month:**
```bash
xpense total --month 3
```

**Total for a specific category:**
```bash
xpense total --category food
```

### Check Balance

**Balance (income - expenses):**
```bash
xpense balance
```

**Monthly balance:**
```bash
xpense balance --month 3
```

### Generate Reports

**Detailed category breakdown:**
```bash
xpense report
```

**Monthly report:**
```bash
xpense report --month 3
```

### List Categories

**All categories:**
```bash
xpense categories
```

**Only expense categories:**
```bash
xpense categories --type expense
```

**Only income categories:**
```bash
xpense categories --type income
```

### Export Data

**Export to default filename (xpense_YYYYMMDD.csv):**
```bash
xpense export
```

**Export to custom file:**
```bash
xpense export --output my_transactions.csv
```

## Data Structure

Transactions are stored in CSV format at `~/.xpense/expenses.csv` with the following structure:

```csv
date,type,amount,category,note
2025-09-29 10:30:00,expense,20.0,transport,to the office
2025-09-29 12:15:00,income,2000.0,salary,from day job
```

### Fields

- **date**: ISO format timestamp (YYYY-MM-DD HH:MM:SS)
- **type**: "income" or "expense"
- **amount**: Positive float value
- **category**: Lowercase with underscores (automatically normalized)
- **note**: Optional description

## Examples

```bash
# Track daily expenses
xpense 5 coffee "morning latte"
xpense 12.50 lunch "sandwich and drink"
xpense 50 gas "fuel for car"

# Record income
xpense add 3000 salary "monthly paycheck"
xpense add 150 freelance "side project"

# Check current month's balance
xpense balance --month $(date +%-m)

# Generate monthly report
xpense report --month $(date +%-m)

# See all food expenses
xpense list --category food --type expense

# Export data for analysis
xpense export --output transactions_2025.csv
```

## Color Coding

- **Green**: Income (positive transactions)
- **Red**: Expenses (negative transactions)
- **Cyan**: Categories and headers

## Project Structure

```
xpense/
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── LICENSE                 # MIT License
└── xpense/
    ├── __init__.py         # Package initialization
    ├── main.py             # CLI entry point
    ├── cli.py              # Typer commands
    ├── storage.py          # CSV operations
    └── display.py          # Rich formatting
```

## Development

```bash
# Install development dependencies
uv sync

# Run the CLI locally
uv run xpense --help

# Run with Python
python -m xpense.main
```

## License

MIT License - See LICENSE file for details
