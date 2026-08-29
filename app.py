import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
import streamlit as st
import pandas as pd
from pathlib import Path

# Try to import from config, fallback if not found
try:
    from config import Config
except ImportError:
    # Fallback config if file not found
    class Config:
        APP_TITLE = "V-Guard ClimateCool"
        APP_ICON = "🌊"
        APP_LAYOUT = "wide"
        EXCEL_DATA_PATH = "data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"
        LIVE_WEATHER_ENABLED = True
        USE_MOCK_WEATHER = True
        WEATHER_API_KEY = ""
        RANDOM_SEED = 42

# Import from src
try:
    from src.data_loader import load_excel_data, get_standardized_data
    from src.climate_engine import calculate_heat_score, calculate_cii
    from utils.formatting import format_currency, format_number, format_timestamp, get_decision_color
except ImportError:
    # Fallback functions if imports fail
    def load_excel_data(path):
        return None
    def get_standardized_data(data):
        return data
    def calculate_heat_score(row):
        return 50
    def calculate_cii(df):
        return df
    def format_currency(val):
        return f"₹{val:,.0f}"
    def format_number(val):
        return f"{val:,.0f}"
    def format_timestamp(ts):
        return str(ts)
    def get_decision_color(decision):
        return "#6b7280"

logging.basicConfig(level=logging.INFO)

# Page Config
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout=Config.APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# ========== DATA LOADING ==========
@st.cache_data(ttl=600)
def load_data():
    raw_data = load_excel_data(Config.EXCEL_DATA_PATH)
    if raw_data is None:
        st.warning("Using sample data - Excel file not found")
        # Create sample data if file not found
        sample_df = pd.DataFrame({
            'DISTRICT_NAME': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata'],
            'STATE': ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal'],
            'POP_M': [16.79, 12.44, 8.44, 7.09, 4.50],
            'CII_SCORE': [62.69, 45.0, 40.0, 35.0, 30.0],
        })
        return {
            'DIM_DISTRICT': sample_df,
            'FACT_SALES': pd.DataFrame(),
            'FACT_WEATHER': pd.DataFrame(),
            'FACT_INVENTORY': pd.DataFrame(),
            'FACT_MARKETING': pd.DataFrame(),
            'DATA_STATUS': 'SAMPLE DATA',
            '_LOAD_TIMESTAMP': datetime.now().isoformat(),
        }
    
    processed_data = get_standardized_data(raw_data)
    processed_data['DATA_STATUS'] = 'DATA LOADED'
    processed_data['_LOAD_TIMESTAMP'] = datetime.now().isoformat()
    return processed_data

data = load_data()

# ========== HEADER ==========
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"{Config.APP_ICON} {Config.APP_TITLE}")
    st.caption("Climate-to-Commerce Control Tower")

with col2:
    status = data.get('DATA_STATUS', 'UNKNOWN')
    st.metric("Status", status)

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🎯 Control Panel")
    st.divider()
    
    if 'DIM_DISTRICT' in data and not data['DIM_DISTRICT'].empty:
        districts = data['DIM_DISTRICT']['DISTRICT_NAME'].tolist()
        selected = st.selectbox("Select District", districts)
    
    st.divider()
    st.subheader("📊 Scenario Controls")
    temp_anomaly = st.slider("Temperature Anomaly (°C)", -2.0, 5.0, 0.0, 0.5)
    marketing_uplift = st.slider("Marketing Uplift (%)", -50, 100, 0, 10)

def check_and_load_data():
    """Check if data file exists, if not, offer upload."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    excel_files = list(data_dir.glob("*.xlsx"))
    
    if not excel_files:
        st.warning("📁 No Excel data file found in the 'data' directory.")
        
        # Allow file upload
        uploaded_file = st.file_uploader(
            "Upload the ClimateCool Excel data file",
            type=['xlsx'],
            help="Upload the Excel file from the data/ directory"
        )
        
        if uploaded_file is not None:
            # Save the uploaded file
            file_path = data_dir / "V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ File saved successfully! Loading data...")
            st.rerun()
        return False
    return True



# ========== MAIN DASHBOARD ==========
st.header("🏢 Executive Dashboard")

# Simple KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", "₹84.3 Cr", "↑ 12.5%")
with col2:
    st.metric("Units Sold", "19,048", "↑ 8.2%")
with col3:
    st.metric("Heat Score", "67.4", "↑ 3.1%")
with col4:
    st.metric("Active Districts", "22", "→")

def main():
    # Check for data file
    if not check_and_load_data():
        st.stop()

# Show some data
if 'DIM_DISTRICT' in data and not data['DIM_DISTRICT'].empty:
    st.subheader("📍 District Overview")
    st.dataframe(data['DIM_DISTRICT'].head(10))

st.divider()
st.caption(f"📊 {Config.APP_TITLE} | Last Updated: {format_timestamp(data.get('_LOAD_TIMESTAMP', datetime.now()))}")
