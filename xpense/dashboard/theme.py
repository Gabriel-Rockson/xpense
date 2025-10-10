from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:
    INCOME = "#10b981"
    EXPENSE = "#ef4444"
    BALANCE = "#3b82f6"
    CATEGORY = "#8b5cf6"


INCOME_PALETTE = [
    "#10b981",
    "#059669",
    "#047857",
    "#065f46",
    "#064e3b",
]

EXPENSE_PALETTE = [
    "#ef4444",
    "#dc2626",
    "#b91c1c",
    "#991b1b",
    "#7f1d1d",
]

CHART_LAYOUT = {
    "hovermode": "x unified",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "font": {"size": 12},
    "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
    "hoverlabel": {
        "bgcolor": "white",
        "font_size": 13,
    },
}

GRID_CONFIG = {
    "showgrid": True,
    "gridwidth": 1,
    "gridcolor": "rgba(128,128,128,0.2)",
}
