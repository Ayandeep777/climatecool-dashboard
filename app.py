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
    
    # Use simple page names without emojis for internal mapping
    page_options = {
        "Control Tower": "control_tower",
        "Opportunity": "opportunity",
        "Climate Intelligence": "climate_intelligence",
        "Demand Engine": "demand_engine",
        "Inventory Command": "inventory_command",
        "SKU & Dealer": "sku_dealer",
        "Heat-Trigger Marketing": "heat_trigger_marketing",
        "Financials": "financials",
        "Stage Gates": "stage_gates",
        "Data Sources": "data_sources"
    }
    
    # Create display names with emojis
    display_names = {
        "control_tower": "🏢 Control Tower",
        "opportunity": "📍 Opportunity",
        "climate_intelligence": "🌤️ Climate Intelligence",
        "demand_engine": "📈 Demand Engine",
        "inventory_command": "📦 Inventory Command",
        "sku_dealer": "🛒 SKU & Dealer",
        "heat_trigger_marketing": "📢 Heat-Trigger Marketing",
        "financials": "💰 Financials",
        "stage_gates": "🚀 Stage Gates",
        "data_sources": "📊 Data Sources"
    }
    
    # Create a list of display names for the radio
    display_list = list(display_names.values())
    
    selected_display = st.sidebar.radio(
        "Choose a Module",
        display_list,
        index=0,
    )
    
    # Map back to internal page name
    page_map = {v: k for k, v in display_names.items()}
    page = page_map.get(selected_display, "control_tower")

    # --- Page Routing ---
    try:
        if page == "control_tower":
            from pages import control_tower as page_module
            page_module.render(app_data)
        elif page == "opportunity":
            from pages import opportunity as page_module
            page_module.render(app_data)
        elif page == "climate_intelligence":
            from pages import climate_intelligence as page_module
            page_module.render(app_data)
        elif page == "demand_engine":
            from pages import demand_engine as page_module
            page_module.render(app_data)
        elif page == "inventory_command":
            from pages import inventory_command as page_module
            page_module.render(app_data)
        elif page == "sku_dealer":
            from pages import sku_dealer as page_module
            page_module.render(app_data)
        elif page == "heat_trigger_marketing":
            from pages import heat_trigger_marketing as page_module
            page_module.render(app_data)
        elif page == "financials":
            from pages import financials as page_module
            page_module.render(app_data)
        elif page == "stage_gates":
            from pages import stage_gates as page_module
            page_module.render(app_data)
        elif page == "data_sources":
            from pages import data_sources as page_module
            page_module.render(app_data)
    except ImportError as e:
        st.error(f"Error loading page: {e}")
        st.info("Please ensure all page modules exist in the 'pages' directory.")
        # Show the Control Tower as fallback
        try:
            from pages import control_tower as page_module
            page_module.render(app_data)
        except:
            st.warning("Unable to load any page. Please check your installation.")

    # --- Footer ---
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Data Snapshot: {config.LAST_REFRESH_DATE}")
    if st.session_state.sample_data:
        st.sidebar.caption("📌 Using sample data (Excel file not found)")

if __name__ == "__main__":
    main()
