import os
import streamlit as st

class Config:
    APP_TITLE = "V-Guard ClimateCool"
    APP_ICON = "🌊"
    APP_LAYOUT = "wide"
    APP_SIDEBAR_STATE = "expanded"
    
    EXCEL_DATA_PATH = "data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"
    DATA_STATUS = "CURRENT ANALYTICAL SNAPSHOT"
    
    # Read from Streamlit secrets (deployment) or environment variables (local)
    try:
        WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY", "")
    except:
        WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    
    try:
        USE_MOCK_WEATHER = st.secrets.get("USE_MOCK_WEATHER", "true") == "true"
    except:
        USE_MOCK_WEATHER = os.getenv("USE_MOCK_WEATHER", "true") == "true"
    
    LIVE_WEATHER_ENABLED = True
    USE_OPENWEATHER = True
    WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5/"
    
    RANDOM_SEED = 42
    
    CII_WEIGHTS = {
        "heat_intensity": 0.25,
        "humidity_suitability": 0.20,
        "population": 0.20,
        "category_demand": 0.15,
        "distribution_readiness": 0.10,
        "ac_affordability_gap": 0.10,
    }
    
    HEAT_SCORE_WEIGHTS = {
        "temperature": 0.35,
        "anomaly": 0.25,
        "humidity": 0.20,
        "heatwave": 0.20,
    }
    
    DECISION_THRESHOLDS = {
        "heat_score_high": 70,
        "heat_score_medium": 50,
        "cii_high": 65,
        "cii_medium": 50,
        "sell_through_good": 0.70,
        "roas_good": 8.0,
    }
    
    DISTRICT_COORDINATES = {
        "Kota": {"lat": 25.18, "lon": 75.83},
        "Bikaner": {"lat": 28.01, "lon": 73.31},
        "Delhi": {"lat": 28.61, "lon": 77.21},
        "Agra": {"lat": 27.18, "lon": 78.01},
        "Jodhpur": {"lat": 26.29, "lon": 73.02},
        "Prayagraj": {"lat": 25.43, "lon": 81.85},
        "Hisar": {"lat": 29.15, "lon": 75.72},
        "Jaipur": {"lat": 26.91, "lon": 75.79},
        "Kanpur Nagar": {"lat": 26.45, "lon": 80.33},
        "Alwar": {"lat": 27.55, "lon": 76.60},
        "Bathinda": {"lat": 30.21, "lon": 74.95},
        "Rohtak": {"lat": 28.90, "lon": 76.58},
        "Varanasi": {"lat": 25.32, "lon": 82.97},
        "Lucknow": {"lat": 26.85, "lon": 80.95},
        "Gurugram": {"lat": 28.46, "lon": 77.03},
        "Faridabad": {"lat": 28.41, "lon": 77.32},
        "Panipat": {"lat": 29.39, "lon": 76.97},
        "Ghaziabad": {"lat": 28.67, "lon": 77.45},
        "Gautam Buddh Nagar": {"lat": 28.53, "lon": 77.39},
        "Meerut": {"lat": 28.98, "lon": 77.71},
        "Ludhiana": {"lat": 30.90, "lon": 75.85},
        "Amritsar": {"lat": 31.63, "lon": 74.87},
    }