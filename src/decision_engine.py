import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DecisionEngine:
    """Provides business decisions based on data analysis."""

    def __init__(self):
        pass

    def analyze_performance(self, metrics):
        """Analyze performance metrics and provide recommendations."""
        recommendations = []
        
        # Revenue analysis
        if 'total_revenue' in metrics:
            revenue = metrics['total_revenue']
            if revenue < 20000000:  # Less than 2Cr
                recommendations.append({
                    'area': 'Revenue',
                    'status': 'Warning',
                    'recommendation': 'Revenue below target. Consider increasing marketing spend.'
                })
            elif revenue > 50000000:
                recommendations.append({
                    'area': 'Revenue',
                    'status': 'Excellent',
                    'recommendation': 'Revenue exceeds targets. Consider scaling up.'
                })
        
        # Margin analysis
        if 'gross_margin_pct' in metrics:
            margin = metrics['gross_margin_pct']
            if margin < 25:
                recommendations.append({
                    'area': 'Margin',
                    'status': 'Warning',
                    'recommendation': 'Margins are low. Review pricing and costs.'
                })
        
        # CII analysis
        if 'cii_score' in metrics:
            cii = metrics['cii_score']
            if cii > 60:
                recommendations.append({
                    'area': 'Climate Intelligence',
                    'status': 'Good',
                    'recommendation': 'High CII score. Focus marketing efforts here.'
                })
        
        return recommendations
