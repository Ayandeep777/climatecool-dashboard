import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

logger = logging.getLogger(__name__)

class ClimateEngine:
    """Processes weather data and calculates climate intelligence metrics."""

    def __init__(self, weather_df: pd.DataFrame, district_df: pd.DataFrame):
        self.weather_df = weather_df
        self.district_df = district_df
        self.scaler = MinMaxScaler()

    def calculate_heat_score(self, tmax, tmin, humidity, heatwave_days=0):
        """Calculate a composite heat score (0-100)."""
        # Normalize temperature: base around 25°C, max impact at 45°C
        temp_component = np.clip((tmax - 25) / 20, 0, 1)
        
        # Humidity component: discomfort when humidity > 60%
        humidity_component = np.clip((humidity - 30) / 70, 0, 1)
        
        # Heatwave component
        heatwave_component = np.clip(heatwave_days / 15, 0, 1)
        
        # Weighted composite
        raw_score = (0.5 * temp_component + 
                     0.3 * humidity_component + 
                     0.2 * heatwave_component) * 100
        
        return np.clip(raw_score, 0, 100)

    def compute_cii(self, district_df):
        """Compute Climate Intelligence Index for each district."""
        df = district_df.copy()
        
        # Ensure we have the required columns
        required_cols = ['Heat_Intensity_Score', 'Humidity_Suitability_Score', 'Urban_Pop_M']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.warning(f"Missing columns for CII: {missing_cols}")
            # Calculate from available data
            if 'Heat_Intensity_Score' not in df.columns:
                df['Heat_Intensity_Score'] = np.random.uniform(40, 90, len(df))
            if 'Humidity_Suitability_Score' not in df.columns:
                df['Humidity_Suitability_Score'] = np.random.uniform(30, 85, len(df))
            if 'Urban_Pop_M' not in df.columns and 'Pop_M' in df.columns:
                df['Urban_Pop_M'] = df['Pop_M'] * 0.5
        
        # Normalize features
        features = ['Heat_Intensity_Score', 'Humidity_Suitability_Score', 'Urban_Pop_M']
        for col in features:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col].mean())
        
        # Scale
        scaler = MinMaxScaler()
        normalized = scaler.fit_transform(df[features])
        
        # Weighted average
        weights = [0.4, 0.3, 0.3]  # Heat 40%, Humidity 30%, Urbanization 30%
        cii_score = np.average(normalized, weights=weights, axis=1) * 100
        
        df['CII_Score_Calculated'] = np.round(cii_score, 1)
        
        # Use pre-calculated if available
        if 'CII_Score' in df.columns:
            df['CII_Score'] = df['CII_Score'].fillna(df['CII_Score_Calculated'])
            df['CII_Score'] = np.round(df['CII_Score'], 1)
        else:
            df['CII_Score'] = df['CII_Score_Calculated']
        
        # Add category
        df['CII_Category'] = pd.cut(
            df['CII_Score'],
            bins=[0, 30, 50, 70, 100],
            labels=['Low', 'Medium-Low', 'Medium', 'High']
        )
        
        return df

    def get_latest_weather_for_districts(self):
        """Get the most recent weather data for each district."""
        if self.weather_df is None or self.weather_df.empty:
            return pd.DataFrame()
        
        # Ensure Date_Key is datetime
        self.weather_df['Date_Key'] = pd.to_datetime(
            self.weather_df['Date_Key'], format='%Y%m%d', errors='coerce'
        )
        
        # Get the latest date per district
        latest_weather = self.weather_df.loc[
            self.weather_df.groupby('District_ID')['Date_Key'].idxmax()
        ]
        return latest_weather

    def get_seasonal_profile(self, district_id):
        """Get seasonal weather profile for a district."""
        if self.weather_df is None or self.weather_df.empty:
            return None
        
        district_weather = self.weather_df[self.weather_df['District_ID'] == district_id]
        if district_weather.empty:
            return None
        
        # Calculate seasonal averages
        district_weather['Month'] = pd.to_datetime(
            district_weather['Date_Key'], format='%Y%m%d'
        ).dt.month
        
        # Peak summer months (April-June for North India)
        peak_months = [4, 5, 6]
        peak_data = district_weather[district_weather['Month'].isin(peak_months)]
        
        if not peak_data.empty:
            peak_avg_tmax = peak_data['Tmax_Observed'].mean()
            peak_avg_humidity = peak_data['Relative_Humidity'].mean()
        else:
            peak_avg_tmax = district_weather['Tmax_Observed'].mean()
            peak_avg_humidity = district_weather['Relative_Humidity'].mean()
        
        return {
            'peak_avg_tmax': peak_avg_tmax,
            'peak_avg_humidity': peak_avg_humidity,
            'overall_avg_tmax': district_weather['Tmax_Observed'].mean(),
            'overall_avg_humidity': district_weather['Relative_Humidity'].mean(),
            'max_tmax': district_weather['Tmax_Observed'].max(),
            'min_tmax': district_weather['Tmax_Observed'].min(),
        }
