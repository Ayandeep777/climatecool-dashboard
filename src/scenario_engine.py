import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ScenarioEngine:
    """Handles what-if analysis and scenario simulations."""

    def __init__(self):
        pass

    def simulate_revenue(self, base_revenue, growth_rate, years=3):
        """Simulate revenue growth over multiple years."""
        projections = []
        current = base_revenue
        for year in range(1, years + 1):
            current = current * (1 + growth_rate)
            projections.append({
                'year': year,
                'revenue': current,
                'growth': growth_rate * 100
            })
        return pd.DataFrame(projections)

    def simulate_marketing_uplift(self, base_revenue, uplift_pct):
        """Simulate revenue uplift from marketing."""
        uplifted_revenue = base_revenue * (1 + uplift_pct / 100)
        return {
            'base_revenue': base_revenue,
            'uplift_pct': uplift_pct,
            'uplifted_revenue': uplifted_revenue,
            'incremental_revenue': uplifted_revenue - base_revenue
        }

    def run_what_if(self, base_metrics, changes):
        """Run a what-if analysis with multiple changes."""
        results = {}
        for key, value in changes.items():
            if key == 'revenue_uplift':
                results['revenue_scenario'] = self.simulate_revenue(
                    base_metrics.get('revenue', 0),
                    value / 100
                )
            elif key == 'marketing_uplift':
                results['marketing_scenario'] = self.simulate_marketing_uplift(
                    base_metrics.get('revenue', 0),
                    value
                )
        return results
