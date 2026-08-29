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
        uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=['xlsx'])
        if uploaded_file is not None:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            file_path = data_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.sidebar.success("File uploaded! Refreshing...")
            st.rerun()
    else:
        st.sidebar.success("✅ Data loaded")
    
    st.sidebar.markdown("---")
    
    # Navigation
    pages = {
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
    
    selected = st.sidebar.radio("Navigate", list(pages.keys()))
    page = pages[selected]
    
    # Render pages
    if page == "control_tower":
        render_control_tower(app_data)
    elif page == "opportunity":
        render_opportunity(app_data)
    elif page == "climate_intelligence":
        render_climate_intelligence(app_data)
    elif page == "demand_engine":
        render_demand_engine(app_data)
    elif page == "inventory_command":
        render_inventory_command(app_data)
    elif page == "sku_dealer":
        render_sku_dealer(app_data)
    elif page == "heat_trigger_marketing":
        render_heat_trigger_marketing(app_data)
    elif page == "financials":
        render_financials(app_data)
    elif page == "stage_gates":
        render_stage_gates(app_data)
    elif page == "data_sources":
        render_data_sources(app_data)

# --- Page Rendering Functions ---

def render_control_tower(app_data):
    st.title("🏢 Control Tower - Executive Dashboard")
    st.caption("Climate-to-Commerce Control Tower | V-Guard Industries")
    
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
    st.subheader("🏙️ District Overview")
    if not district_df.empty:
        display_cols = ['District_Name', 'State', 'Pop_M', 'CII_Score', 'CII_Category']
        available_cols = [col for col in display_cols if col in district_df.columns]
        if available_cols:
            st.dataframe(district_df[available_cols].head(10), use_container_width=True)
    else:
        st.info("No district data available")

def render_opportunity(app_data):
    st.title("📍 Opportunity - District Ranking")
    st.caption("Identify high-potential districts for ClimateCool")
    
    district_df = app_data.get('DIM_DISTRICT', pd.DataFrame())
    
    if not district_df.empty:
        # Sort by CII Score
        if 'CII_Score' in district_df.columns:
            sorted_df = district_df.sort_values('CII_Score', ascending=False)
            
            # Show ranking
            st.subheader("🏆 District Rankings by Climate Intelligence Index")
            
            display_cols = ['District_Name', 'State', 'CII_Score', 'CII_Category', 'Pop_M']
            available_cols = [col for col in display_cols if col in sorted_df.columns]
            
            if available_cols:
                # Add rank column
                sorted_df['Rank'] = range(1, len(sorted_df) + 1)
                st.dataframe(sorted_df[['Rank'] + available_cols].head(15), use_container_width=True)
            
            # Show top districts chart
            st.subheader("Top 10 Districts")
            if 'District_Name' in sorted_df.columns and 'CII_Score' in sorted_df.columns:
                import plotly.express as px
                fig = px.bar(
                    sorted_df.head(10),
                    x='District_Name',
                    y='CII_Score',
                    color='CII_Category',
                    title="Top 10 Districts by Climate Intelligence Index",
                    labels={'CII_Score': 'CII Score', 'District_Name': 'District'}
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No district data available")

def render_climate_intelligence(app_data):
    st.title("🌤️ Climate Intelligence")
    st.caption("Real-time climate intelligence and weather analysis")
    
    district_df = app_data.get('DIM_DISTRICT', pd.DataFrame())
    weather_df = app_data.get('FACT_WEATHER', pd.DataFrame())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Climate Intelligence Index by District")
        if not district_df.empty and 'CII_Score' in district_df.columns:
            # Show CII distribution
            import plotly.express as px
            fig = px.histogram(
                district_df,
                x='CII_Score',
                color='CII_Category',
                title="CII Score Distribution",
                labels={'CII_Score': 'CII Score', 'count': 'Number of Districts'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No climate data available")
    
    with col2:
        st.subheader("Heat Intensity vs Urbanization")
        if not district_df.empty:
            if 'Heat_Intensity_Score' in district_df.columns and 'Urban_Pop_M' in district_df.columns:
                import plotly.express as px
                fig = px.scatter(
                    district_df,
                    x='Urban_Pop_M',
                    y='Heat_Intensity_Score',
                    size='Pop_M',
                    color='CII_Category',
                    hover_data=['District_Name'],
                    title="Heat Intensity vs Urban Population",
                    labels={'Urban_Pop_M': 'Urban Population (M)', 'Heat_Intensity_Score': 'Heat Intensity'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Heat intensity data not available")

def render_demand_engine(app_data):
    st.title("📈 Demand Engine")
    st.caption("Demand forecasting and predictive analytics")
    
    sales_df = app_data.get('FACT_SALES', pd.DataFrame())
    
    if not sales_df.empty:
        # Show sales trends
        st.subheader("Sales Trends")
        
        # Aggregate by date if Date_Key exists
        if 'Date_Key' in sales_df.columns:
            sales_trend = sales_df.groupby('Date_Key')['Units_Sold'].sum().reset_index()
            
            import plotly.express as px
            fig = px.line(
                sales_trend,
                x='Date_Key',
                y='Units_Sold',
                title="Sales Trend",
                labels={'Units_Sold': 'Units Sold', 'Date_Key': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # SKU performance
        st.subheader("SKU Performance")
        sku_perf = sales_df.groupby('SKU_ID').agg({
            'Units_Sold': 'sum',
            'Gross_Revenue_INR': 'sum'
        }).reset_index()
        st.dataframe(sku_perf, use_container_width=True)
    else:
        st.info("No sales data available for demand forecasting")

def render_inventory_command(app_data):
    st.title("📦 Inventory Command")
    st.caption("Inventory management and optimization")
    
    inventory_df = app_data.get('FACT_INVENTORY', pd.DataFrame())
    
    if not inventory_df.empty:
        st.subheader("Inventory Overview")
        st.dataframe(inventory_df.head(20), use_container_width=True)
        
        # Stockout analysis
        if 'Stockout_Days' in inventory_df.columns:
            stockout_summary = inventory_df.groupby('District_ID')['Stockout_Days'].sum().reset_index()
            import plotly.express as px
            fig = px.bar(
                stockout_summary.head(10),
                x='District_ID',
                y='Stockout_Days',
                title="Stockout Days by District",
                labels={'Stockout_Days': 'Stockout Days', 'District_ID': 'District'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No inventory data available")

def render_sku_dealer(app_data):
    st.title("🛒 SKU & Dealer Analysis")
    st.caption("SKU performance and dealer network analysis")
    
    sku_df = app_data.get('DIM_SKU', pd.DataFrame())
    dealer_df = app_data.get('DIM_DEALER', pd.DataFrame())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SKU Portfolio")
        if not sku_df.empty:
            st.dataframe(sku_df, use_container_width=True)
        else:
            st.info("No SKU data available")
    
    with col2:
        st.subheader("Dealer Distribution")
        if not dealer_df.empty:
            tier_dist = dealer_df['Dealer_Tier'].value_counts().reset_index()
            tier_dist.columns = ['Tier', 'Count']
            import plotly.express as px
            fig = px.pie(
                tier_dist,
                values='Count',
                names='Tier',
                title="Dealer Tier Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No dealer data available")

def render_heat_trigger_marketing(app_data):
    st.title("📢 Heat-Trigger Marketing")
    st.caption("Marketing campaigns triggered by heat intensity")
    
    marketing_df = app_data.get('FACT_MARKETING', pd.DataFrame())
    
    if not marketing_df.empty:
        st.subheader("Marketing Performance")
        st.dataframe(marketing_df.head(20), use_container_width=True)
        
        # ROAS analysis
        if 'ROAS' in marketing_df.columns:
            import plotly.express as px
            fig = px.box(
                marketing_df,
                y='ROAS',
                title="ROAS Distribution",
                labels={'ROAS': 'Return on Ad Spend'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No marketing data available")

def render_financials(app_data):
    st.title("💰 Financials")
    st.caption("Financial performance and metrics")
    
    sales_df = app_data.get('FACT_SALES', pd.DataFrame())
    
    if not sales_df.empty:
        total_revenue = sales_df['Gross_Revenue_INR'].sum()
        total_margin = sales_df['Gross_Margin_INR'].sum() if 'Gross_Margin_INR' in sales_df.columns else 0
        margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"₹{total_revenue/1e7:.2f} Cr")
        with col2:
            st.metric("Total Margin", f"₹{total_margin/1e7:.2f} Cr")
        with col3:
            st.metric("Margin %", f"{margin_pct:.1f}%")
        
        # Revenue by SKU
        st.subheader("Revenue by SKU")
        sku_revenue = sales_df.groupby('SKU_ID')['Gross_Revenue_INR'].sum().reset_index()
        import plotly.express as px
        fig = px.bar(
            sku_revenue,
            x='SKU_ID',
            y='Gross_Revenue_INR',
            title="Revenue by SKU",
            labels={'Gross_Revenue_INR': 'Revenue (₹)', 'SKU_ID': 'SKU'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No financial data available")

def render_stage_gates(app_data):
    st.title("🚀 Stage Gates")
    st.caption("Business milestones and stage gate tracking")
    
    stage_gate_df = app_data.get('FACT_STAGE_GATE', pd.DataFrame())
    
    if not stage_gate_df.empty:
        st.dataframe(stage_gate_df, use_container_width=True)
        
        # Show pass/fail status
        if 'Pass_Fail_Status' in stage_gate_df.columns:
            status_counts = stage_gate_df['Pass_Fail_Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            import plotly.express as px
            fig = px.pie(
                status_counts,
                values='Count',
                names='Status',
                title="Stage Gate Status",
                color='Status',
                color_discrete_map={'PASS': 'green', 'FAIL': 'red'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No stage gate data available")

def render_data_sources(app_data):
    st.title("📊 Data Sources & Assumptions")
    st.caption("Data provenance and key assumptions")
    
    provenance_df = app_data.get('DATA_PROVENANCE', pd.DataFrame())
    
    if not provenance_df.empty:
        st.subheader("Data Provenance")
        st.dataframe(provenance_df, use_container_width=True)
    else:
        st.info("No provenance data available")
    
    # Show assumptions
    st.subheader("📝 Key Assumptions")
    assumptions = {
        "Working TAM": "₹2,200 Cr",
        "Y1 Planned Revenue": "₹20 Cr",
        "Y2 Planned Revenue": "₹40 Cr",
        "Y3 Planned Revenue": "₹70 Cr",
        "Blended Net Realization": "₹10,500 per unit",
        "Working Capital": "10% of Sales"
    }
    
    for key, value in assumptions.items():
        st.write(f"- **{key}**: {value}")

if __name__ == "__main__":
    main()
