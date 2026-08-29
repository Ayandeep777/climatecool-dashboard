import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import logging
import streamlit as st
from config import Config

logging.basicConfig(level=logging.INFO)

@st.cache_resource
def train_demand_model(df_sales_weather: pd.DataFrame):
    """
    Train a Random Forest model to forecast demand.
    
    Args:
        df_sales_weather: Merged sales and weather data
        
    Returns:
        Tuple of (model, scaler, features, metrics)
    """
    if df_sales_weather.empty:
        return None, None, None, None
    
    # Feature engineering
    df = df_sales_weather.copy()
    
    # Create lag features
    if 'DISTRICT_ID' in df.columns:
        df['TEMP_ANOMALY_LAG1'] = df.groupby('DISTRICT_ID')['TEMP_ANOMALY'].shift(1)
        df['HEAT_SCORE_LAG1'] = df.groupby('DISTRICT_ID')['HEAT_SCORE'].shift(1)
        df['UNITS_SOLD_LAG1'] = df.groupby('DISTRICT_ID')['UNITS_SOLD'].shift(1)
    
    # Drop rows with missing values
    required_cols = ['UNITS_SOLD', 'TMAX_OBSERVED', 'TEMP_ANOMALY', 'RELATIVE_HUMIDITY', 
                     'HEAT_SCORE', 'HEATWAVE_DAYS']
    df = df.dropna(subset=required_cols)
    
    if len(df) < 30:
        logging.warning("Not enough data to train a robust model.")
        return None, None, None, None

    # Features
    features = ['TMAX_OBSERVED', 'TEMP_ANOMALY', 'RELATIVE_HUMIDITY', 
                'HEAT_SCORE', 'HEATWAVE_DAYS']
    
    # Add lag features if available
    if 'TEMP_ANOMALY_LAG1' in df.columns:
        features.append('TEMP_ANOMALY_LAG1')
    if 'HEAT_SCORE_LAG1' in df.columns:
        features.append('HEAT_SCORE_LAG1')
    if 'UNITS_SOLD_LAG1' in df.columns:
        features.append('UNITS_SOLD_LAG1')
        # Drop rows with NaN in lag features
        df = df.dropna(subset=['UNITS_SOLD_LAG1'])
    
    X = df[features]
    y = df['UNITS_SOLD']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=Config.RANDOM_SEED
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestReg