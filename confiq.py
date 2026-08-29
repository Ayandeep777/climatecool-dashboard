from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Find Excel file
excel_files = list(DATA_DIR.glob("*.xlsx"))
if excel_files:
    EXCEL_FILE_PATH = excel_files[0]
else:
    EXCEL_FILE_PATH = DATA_DIR / "V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"

# --- Model Parameters ---
WORKING_TAM_CR = 2200.0
PLANNED_Y1_REVENUE_CR = 20.0
PLANNED_Y2_REVENUE_CR = 40.0
PLANNED_Y3_REVENUE_CR = 70.0
BLENDED_NET_REALIZATION = 10500.0
WORKING_CAPITAL_PCT = 0.10

# --- Metadata ---
LAST_REFRESH_DATE = "2026-08-29"
APP_TITLE = "Climate-to-Commerce Control Tower"
