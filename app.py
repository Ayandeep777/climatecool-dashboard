import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Configure page
st.set_page_config(
    page_title="Climate-to-Commerce Control Tower",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'app_data' not in st.session_state:
    st.session_state.app_data = {}
if 'sample_data' not in st.session_state:
    st.session_state.sample_data = True

# --- Data Loading ---
@st.cache_resource
def load_data():
    """Load data from Excel file or create sample data."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    excel_files = list(data_dir.glob("*.xlsx")) + list(Path(".").glob("*.xlsx"))
    
    if excel_files:
        try:
            df_dict = pd.read_excel(excel_files[0], sheet_name=None)
            st.session_state.sample_data = False
            return df_dict
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    # Create sample data
    st.session_state.sample_data = True
    return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration."""
    districts = pd.DataFrame({
        'District_ID': ['DIST_001', 'DIST_002', 'DIST_003', 'DIST_004', 'DIST_005'],
        'District_Name': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata'],
        'State': ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal'],
        'Pop_M': [16.79, 12.44, 8.44, 7.09, 4.5],
        'CII_Score': [62.69, 45, 40, 35, 30],
        'CII_Category': ['Medium', 'Medium', 'Low', 'Low', 'Low'],
        'Latitude': [28.61, 19.08, 12.97, 13.08, 22.57],
        'Longitude': [77.21, 72.88, 77.59, 80.27, 88.36]
    })
    
    sales = pd.DataFrame({
        'Date_Key': ['20260101'] * 10,
        'District_ID': ['DIST_001'] * 10,
        'SKU_ID': ['SKU_001', 'SKU_002', 'SKU_003', 'SKU_004'] * 2 + ['SKU_001', 'SKU_002'],
        'Units_Sold': [5, 8, 12, 6, 15, 9, 7, 11, 4, 13],
        'Gross_Revenue_INR': [32500, 78400, 162000, 111000, 97500, 88200, 94500, 203500, 26000, 127400],
        'Gross_Margin_INR': [9750, 23200, 51600, 36600, 29250, 26100, 30100, 67100, 7800, 39200]
    })
    
    skus = pd.DataFrame({
        'SKU_ID': ['SKU_001', 'SKU_002', 'SKU_003', 'SKU_004'],
        'SKU_Name': ['Personal Tower 30L', 'Mass Desert 65L', 'Heavy Desert 90L', 'Institutional 135L'],
        'ASP_INR': [6500, 9800, 13500, 18500]
    })
    
    return {
        'DIM_DISTRICT': districts,
        'DIM_SKU': skus,
        'FACT_SALES': sales
    }

# --- Main App ---
def main():
    # Sidebar
    st.sidebar.title("❄️ ClimateCool")
    st.sidebar.caption("V-Guard Industries")
    
    # Load data
    app_data = load_data()
    st.session_state.app_data = app_data
    
    # Show status
    if st.session_state.sample_data:
        st.sidebar.warning("⚠️ Using sample data")
        if st.sidebar.file_uploader("Upload Excel file", type=['xlsx']):
            st.rerun()
    else:
        st.sidebar.success("✅ Data loaded")
    
    st.sidebar.markdown("---")
    
    # Navigation
    pages = {
        "🏢 Control Tower": "control_tower",
        "📊 Data Status": "data_status"
    }
    
    selected = st.sidebar.radio("Navigate", list(pages.keys()))
    page = pages[selected]
    
    # Render pages
    if page == "control_tower":
        render_control_tower(app_data)
    elif page == "data_status":
        render_data_status(app_data)

def render_control_tower(app_data):
    st.title("🏢 Control Tower")
    
    district_df = app_data.get('DIM_DISTRICT', pd.DataFrame())
    sales_df = app_data.get('FACT_SALES', pd.DataFrame())
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = sales_df['Gross_Revenue_INR'].sum() if not sales_df.empty else 84300000
    total_units = sales_df['Units_Sold'].sum() if not sales_df.empty else 19048
    active_districts = len(district_df) if not district_df.empty else 22
    
    with col1:
        st.metric("Total Revenue", f"₹{total_revenue/1e7:.2f} Cr")
    with col2:
        st.metric("Units Sold", f"{total_units:,}")
    with col3:
        st.metric("Active Districts", active_districts)
    with col4:
        st.metric("Data Status", "Sample" if st.session_state.sample_data else "Live")
    
    # District Overview
    st.subheader("District Overview")
    if not district_df.empty:
        st.dataframe(district_df[['District_Name', 'State', 'Pop_M', 'CII_Score', 'CII_Category']], 
                    use_container_width=True)
    else:
        st.info("No district data available")

def render_data_status(app_data):
    st.title("📊 Data Status")
    
    st.write("### Available Data")
    for key, df in app_data.items():
        if not df.empty:
            st.write(f"- **{key}**: {len(df)} rows")
    
    st.write("### File Status")
    if st.session_state.sample_data:
        st.warning("Using sample data")
        st.info("Upload your Excel file to use real data")
    else:
        st.success("Data loaded from Excel file")

if __name__ == "__main__":
    main()
