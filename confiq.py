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
    # Try current directory
    excel_files = list(Path(".").glob("*.xlsx"))
    if excel_files:
        EXCEL_FILE_PATH = excel_files[0]
    else:
        EXCEL_FILE_PATH = data / "V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"

# --- Weather API ---
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "4cca9dae74e69a773a7377d156058597")
USE_MOCK_WEATHER = os.getenv("USE_MOCK_WEATHER", "True").lower() == "true"
LAST_REFRESH_DATE = "2026-08-29"

# --- Model Parameters ---
WORKING_TAM_CR = 2200.0
PLANNED_Y1_REVENUE_CR = 20.0
PLANNED_Y2_REVENUE_CR = 40.0
PLANNED_Y3_REVENUE_CR = 70.0
BLENDED_NET_REALIZATION = 10500.0
WORKING_CAPITAL_PCT = 0.10

# --- Project Metadata ---
APP_TITLE = "Climate-to-Commerce Control Tower"
APP_ICON = "❄️"
