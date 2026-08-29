import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FinancialEngine:
    """Calculates financial metrics for the dashboard."""

    def __init__(self, sales_df: pd.DataFrame, inventory_df: pd.DataFrame):
        self.sales_df = sales_df
        self.inventory_df = inventory_df

    def calculate_ebitda(self, revenue, cogs, operating_expenses):
        """Calculate EBITDA."""
        gross_profit = revenue - cogs
        ebitda = gross_profit - operating_expenses
        return ebitda

    def calculate_working_capital(self, inventory_value, receivables, payables):
        """Calculate working capital."""
        return inventory_value + receivables - payables

    def get_financial_summary(self):
        """Get a summary of key financial metrics."""
        if self.sales_df is None or self.sales_df.empty:
            return {
                'total_revenue': 0,
                'total_cogs': 0,
                'total_gross_margin': 0,
                'gross_margin_pct': 0
            }
        
        total_revenue = self.sales_df['Gross_Revenue_INR'].sum()
        total_cogs = self.sales_df['COGS_INR'].sum() if 'COGS_INR' in self.sales_df.columns else 0
        total_gross_margin = self.sales_df['Gross_Margin_INR'].sum() if 'Gross_Margin_INR' in self.sales_df.columns else 0
        
        gross_margin_pct = (total_gross_margin / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_cogs': total_cogs,
            'total_gross_margin': total_gross_margin,
            'gross_margin_pct': gross_margin_pct
        }
