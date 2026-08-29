import os
from pathlib import Path

# --- Base Paths ---
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Look for Excel file in data directory
excel_files = list(DATA_DIR.glob("*.xlsx"))
if excel_files:
    EXCEL_FILE_PATH = excel_files[0]
else:
    # Fallback path
    EXCEL_FILE_PATH = DATA_DIR / "V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"

# --- Weather API ---
# Streamlit secrets are used in production. This is a fallback.
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_mock_api_key")
USE_MOCK_WEATHER = os.getenv("USE_MOCK_WEATHER", "True").lower() == "true"
LAST_REFRESH_DATE = "2026-08-29"

# --- Model Parameters (from your case assumptions) ---
WORKING_TAM_CR = 2200.0  # ₹2,200 Cr
PLANNED_Y1_REVENUE_CR = 20.0
PLANNED_Y2_REVENUE_CR = 40.0
PLANNED_Y3_REVENUE_CR = 70.0
BLENDED_NET_REALIZATION = 10500.0
WORKING_CAPITAL_PCT = 0.10

# --- Project Metadata ---
APP_TITLE = "Climate-to-Commerce Control Tower"
APP_ICON = "❄️"
