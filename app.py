import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to the path - FIXED
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import config - FIXED with proper path
try:
    import config
except ImportError:
    # Fallback config if import fails
    class Config:
        EXCEL_FILE_PATH = Path("data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx")
        WEATHER_API_KEY = "mock_key"
        USE_MOCK_WEATHER = True
        LAST_REFRESH_DATE = "2026-08-29"
        WORKING_TAM_CR = 2200.0
        PLANNED_Y1_REVENUE_CR = 20.0
        PLANNED_Y2_REVENUE_CR = 40.0
        PLANNED_Y3_REVENUE_CR = 70.0
        BLENDED_NET_REALIZATION = 10500.0
        WORKING_CAPITAL_PCT = 0.10
    config = Config()

from src.data_loader import DataLoader

# Configure page
st.set_page_config(
    page_title="Climate-to-Commerce Control Tower",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Session State ---
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

if 'app_data' not in st.session_state:
    st.session_state.app_data = {}

if 'sample_data' not in st.session_state:
    st.session_state.sample_data = True

# --- File Upload Section ---
def handle_file_upload():
    """Handle file upload for the Excel data file."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Data Management")
    
    # Check if data is loaded
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Look for existing Excel file
    existing_files = list(data_dir.glob("*.xlsx")) + list(Path(".").glob("*.xlsx"))
    
    if existing_files:
        st.sidebar.success(f"✅ Data file found: {existing_files[0].name}")
        return True
    
    # Allow file upload
    st.sidebar.warning("⚠️ No data file found")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel Data File",
        type=['xlsx'],
        help="Upload the V-Guard ClimateCool Excel data file"
    )
    
    if uploaded_file is not None:
        # Save to data directory
        file_path = data_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"✅ File saved: {uploaded_file.name}")
        st.rerun()
        return True
    
    return False

# --- Load Data ---
@st.cache_resource(ttl=3600)
def load_app_data():
    """Load and cache the entire data model."""
    try:
        import pandas as pd
        data_loader = DataLoader()
        app_data = data_loader.load_all()
        
        # Check if we're using sample data
        is_sample = len(app_data.get('DIM_DISTRICT', pd.DataFrame())) < 10
        st.session_state.sample_data = is_sample
        
        if is_sample:
            st.session_state.data_loaded = False
        else:
            st.session_state.data_loaded = True
        
        return app_data
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return None

# --- Main App ---
def main():
    # Sidebar header
    st.sidebar.title("❄️ ClimateCool")
    st.sidebar.caption("V-Guard Industries")
    st.sidebar.markdown("---")
    
    # Handle file upload
    handle_file_upload()
    
    # Load data
    with st.spinner("Loading the Climate-to-Commerce Control Tower..."):
        app_data = load_app_data()
        st.session_state.app_data = app_data

    if app_data is None:
        st.error("Failed to load data. Please check your file and try again.")
        st.stop()

    # Show data status
    if st.session_state.sample_data:
        st.sidebar.warning("⚠️ Using sample data")
    else:
        st.sidebar.success("✅ Live data loaded")
    
    st.sidebar.markdown("---")

    # --- Sidebar Navigation ---
    st.sidebar.subheader("📊 Navigation")
    
    # Simple page navigation without special characters in keys
    page_options = {
        "🏢 Control Tower": "control_tower",
        "📍 Opportunity": "opportunity",
        "🌤️ Climate Intelligence": "climate_intelligence",
        "📈 Demand Engine": "demand_engine",
        "📦 Inventory Command": "inventory_command",
        "🛒 SKU & Dealer": "sku_dealer",
        "📢 Heat-Trigger Marketing": "heat_trigger_marketing",
        "💰 Financials": "financials",
        "🚀 Stage Gates": "stage_gates",
        "📊 Data Sources": "data_sources"
    }
    
    selected_display = st.sidebar.radio(
        "Choose a Module",
        list(page_options.keys()),
        index=0,
    )
    
    page = page_options[selected_display]

    # --- Page Routing ---
    try:
        if page == "control_tower":
            from pages.control_tower import render
            render(app_data)
        elif page == "opportunity":
            from pages.opportunity import render
            render(app_data)
        elif page == "climate_intelligence":
            from pages.climate_intelligence import render
            render(app_data)
        elif page == "demand_engine":
            from pages.demand_engine import render
            render(app_data)
        elif page == "inventory_command":
            from pages.inventory_command import render
            render(app_data)
        elif page == "sku_dealer":
            from pages.sku_dealer import render
            render(app_data)
        elif page == "heat_trigger_marketing":
            from pages.heat_trigger_marketing import render
            render(app_data)
        elif page == "financials":
            from pages.financials import render
            render(app_data)
        elif page == "stage_gates":
            from pages.stage_gates import render
            render(app_data)
        elif page == "data_sources":
            from pages.data_sources import render
            render(app_data)
    except ImportError as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please ensure all page modules exist in the 'pages' directory.")
        # Show the Control Tower as fallback
        try:
            from pages.control_tower import render
            render(app_data)
        except:
            st.warning("Unable to load any page. Please check your installation.")

    # --- Footer ---
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Data Snapshot: {config.LAST_REFRESH_DATE}")
    if st.session_state.sample_data:
        st.sidebar.caption("📌 Using sample data (Excel file not found)")

if __name__ == "__main__":
    main()
