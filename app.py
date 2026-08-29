import streamlit as st
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

import config
from src.data_loader import DataLoader
from utils.logging_config import setup_logging

# Initialize logger
logger = setup_logging()

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
    st.session_state.sample_data = False

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
        data_loader = DataLoader()
        app_data = data_loader.load_all()
        
        # Check if we're using sample data
        is_sample = len(app_data.get('DIM_DISTRICT', pd.DataFrame())) < 10
        st.session_state.sample_data = is_sample
        
        if is_sample:
            logger.info("Using sample data (Excel file not found)")
        else:
            logger.info("Data model loaded successfully from Excel file")
            st.session_state.data_loaded = True
        
        return app_data
    except Exception as e:
        logger.error(f"Failed to load data model: {e}")
        st.error(f"Failed to load data: {e}")
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
        st.stop()

    # Show data status
    if st.session_state.sample_data:
        st.sidebar.warning("⚠️ Using sample data")
    else:
        st.sidebar.success("✅ Live data loaded")
    
    st.sidebar.markdown("---")

    # --- Sidebar Navigation ---
    st.sidebar.subheader("📊 Navigation")
    page = st.sidebar.radio(
        "Choose a Module",
        [
            "🏢 Control Tower",
            "📍 Opportunity",
            "🌤️ Climate Intelligence",
            "📈 Demand Engine",
            "📦 Inventory Command",
            "🛒 SKU & Dealer",
            "📢 Heat-Trigger Marketing",
            "💰 Financials",
            "🚀 Stage Gates",
            "📊 Data Sources & Assumptions",
        ],
        index=0,
    )

    # --- Page Routing ---
    try:
        if page == "🏢 Control Tower":
            from pages import 1_Control_Tower as page_module
            page_module.render(app_data)
        elif page == "📍 Opportunity":
            from pages import 2_Opportunity as page_module
            page_module.render(app_data)
        elif page == "🌤️ Climate Intelligence":
            from pages import 3_Climate_Intelligence as page_module
            page_module.render(app_data)
        elif page == "📈 Demand Engine":
            from pages import 4_Demand_Engine as page_module
            page_module.render(app_data)
        elif page == "📦 Inventory Command":
            from pages import 5_Inventory_Command as page_module
            page_module.render(app_data)
        elif page == "🛒 SKU & Dealer":
            from pages import 6_SKU_Dealer as page_module
            page_module.render(app_data)
        elif page == "📢 Heat-Trigger Marketing":
            from pages import 7_Heat_Trigger_Marketing as page_module
            page_module.render(app_data)
        elif page == "💰 Financials":
            from pages import 8_Financials as page_module
            page_module.render(app_data)
        elif page == "🚀 Stage Gates":
            from pages import 9_Stage_Gates as page_module
            page_module.render(app_data)
        elif page == "📊 Data Sources & Assumptions":
            from pages import 10_Data_Sources as page_module
            page_module.render(app_data)
    except ImportError as e:
        st.error(f"Error loading page: {e}")
        st.info("Please ensure all page modules exist in the 'pages' directory.")

    # --- Footer ---
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Data Snapshot: {config.LAST_REFRESH_DATE}")
    if st.session_state.sample_data:
        st.sidebar.caption("📌 Using sample data (Excel file not found)")

if __name__ == "__main__":
    main()
