import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DealerEngine:
    """Analyzes dealer performance and provides insights."""

    def __init__(self, dealer_df: pd.DataFrame):
        self.dealer_df = dealer_df

    def get_dealer_performance(self, district_id=None):
        """Get dealer performance metrics."""
        if self.dealer_df is None or self.dealer_df.empty:
            return pd.DataFrame()
        
        df = self.dealer_df.copy()
        if district_id:
            df = df[df['District_ID'] == district_id]
        
        tier_dist = df['Dealer_Tier'].value_counts().reset_index()
        tier_dist.columns = ['Tier', 'Count']
        
        return tier_dist

    def get_district_dealer_summary(self, district_id):
        """Get dealer summary for a specific district."""
        if self.dealer_df is None or self.dealer_df.empty:
            return pd.DataFrame()
        
        df = self.dealer_df[self.dealer_df['District_ID'] == district_id]
        if df.empty:
            return pd.DataFrame()
        
        summary = {
            'Total_Dealers': len(df),
            'Tier_A': len(df[df['Dealer_Tier'] == 'Tier A']),
            'Tier_B': len(df[df['Dealer_Tier'] == 'Tier B']),
            'Tier_C': len(df[df['Dealer_Tier'] == 'Tier C']),
            'Active_Dealers': len(df[df['Active_Status'] == 'Active']),
            'Total_Credit_Limit': df['Credit_Limit_INR'].sum()
        }
        
        return pd.DataFrame([summary])
