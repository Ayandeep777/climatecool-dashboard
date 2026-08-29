import pandas as pd
import streamlit as st

def format_currency(value, prefix="₹"):
    """Format currency values."""
    if pd.isna(value) or value is None:
        return f"{prefix}0"
    if value >= 1e7:  # Crores
        return f"{prefix}{value/1e7:.2f} Cr"
    elif value >= 1e5:  # Lakhs
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

def get_data_quality_score(df):
    """Calculate a simple data quality score."""
    if df is None or df.empty:
        return 0
    
    total_cells = df.size
    null_cells = df.isna().sum().sum()
    
    if total_cells == 0:
        return 0
    
    completeness = 1 - (null_cells / total_cells)
    return int(completeness * 100)
