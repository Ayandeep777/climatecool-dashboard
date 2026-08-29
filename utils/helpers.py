import pandas as pd

def format_currency(value, prefix="₹"):
    """Format currency values."""
    if pd.isna(value) or value is None:
        return f"{prefix}0"
    if value >= 1e7:
        return f"{prefix}{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"{prefix}{value/1e5:.2f} L"
    else:
        return f"{prefix}{value:,.0f}"

def format_number(value):
    """Format large numbers."""
    if pd.isna(value) or value is None:
        return "0"
    if value >= 1e7:
        return f"{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"{value/1e5:.2f} L"
    else:
        return f"{value:,.0f}"
