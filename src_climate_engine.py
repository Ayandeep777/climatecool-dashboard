import pandas as pd
import numpy as np
from config import Config

def calculate_heat_score(row: pd.Series) -> float:
    """
    Calculate a dynamic Heat Score (0-100) based on weather factors.
    
    Args:
        row: Row with weather data
        
    Returns:
        Heat Score (0-100)
    """
    weights = Config.HEAT_SCORE_WEIGHTS
    
    # Normalize factors to 0-100
    temp_score = np.clip((row.get('TMAX_OBSERVED', 25) - 25) / (45 - 25) * 100, 0, 100)
    anomaly_score = np.clip((row.get('TEMP_ANOMALY', 0) + 2) / 6 * 100, 0, 100)
    
    # Humidity suitability: Lower humidity is better for evaporative coolers
    humidity = row.get('RELATIVE_HUMIDITY', 50)
    humidity_score = 100 - np.clip(humidity / 100 * 100, 0, 100)
    
    heatwave_days = row.get('HEATWAVE_DAYS', 0)
    heatwave_score = np.clip(heatwave_days / 15 * 100, 0, 100)  # Max 15 days/month
    
    # Calculate weighted score
    heat_score = (
        weights['temperature'] * temp_score +
        weights['anomaly'] * anomaly_score +
        weights['humidity'] * humidity_score +
        weights['heatwave'] * heatwave_score
    )
    
    return np.clip(heat_score, 0, 100)


def calculate_cii(df_district: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    """
    Calculate the Climate Intelligence Index (CII) for each district.
    
    Args:
        df_district: District dataframe
        weights: Optional custom weights
        
    Returns:
        DataFrame with CII scores
    """
    if weights is None:
        weights = Config.CII_WEIGHTS
    
    df = df_district.copy()
    
    # Normalize each component to 0-100
    if 'POP_M' in df.columns:
        df['POP_SCORE'] = np.clip(
            (df['POP_M'] - df['POP_M'].min()) / (df['POP_M'].max() - df['POP_M'].min()) * 100,
            0, 100
        )
    else:
        df['POP_SCORE'] = 50
    
    # Use existing scores or calculate
    scores = {
        'heat_intensity': df.get('HEAT_INTENSITY_SCORE', 50),
        'humidity_suitability': df.get('HUMIDITY_SUITABILITY_SCORE', 50),
        'category_demand': df.get('CATEGORY_DEMAND_SCORE', 50),
        'distribution_readiness': df.get('DIST_READINESS', 50),
        'ac_affordability_gap': df.get('AC_GAP', 50),
    }
    
    # Calculate CII
    df['CII_SCORE'] = (
        weights['heat_intensity'] * scores['heat_intensity'].fillna(50) +
        weights['humidity_suitability'] * scores['humidity_suitability'].fillna(50) +
        weights['population'] * df['POP_SCORE'].fillna(50) +
        weights['category_demand'] * scores['category_demand'].fillna(50) +
        weights['distribution_readiness'] * scores['distribution_readiness'].fillna(50) +
        weights['ac_affordability_gap'] * scores['ac_affordability_gap'].fillna(50)
    )
    
    # Rank and categorize
    df['CII_RANK'] = df['CII_SCORE'].rank(ascending=False).astype(int)
    
    bins = [0, 50, 65, 80, 100]
    labels = ['Low', 'Medium', 'High', 'Very High']
    df['CII_CATEGORY'] = pd.cut(df['CII_SCORE'], bins=bins, labels=labels, right=True)
    
    return df


def get_heat_status(heat_score: float) -> dict:
    """
    Get heat status based on score.
    
    Args:
        heat_score: Heat score (0-100)
        
    Returns:
        Dict with status, color, and recommendation
    """
    if heat_score >= 70:
        return {
            'status': 'RED',
            'color': '#ef4444',
            'recommendation': 'ACTIVATE',
            'severity': 'High'
        }
    elif heat_score >= 50:
        return {
            'status': 'AMBER',
            'color': '#eab308',
            'recommendation': 'MONITOR',
            'severity': 'Medium'
        }
    else:
        return {
            'status': 'GREEN',
            'color': '#22c55e',
            'recommendation': 'HOLD',
            'severity': 'Low'
        }