import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import format_currency, format_number

def render(app_data):
    st.title("🏢 Control Tower - Executive Dashboard")
    st.caption("Climate-to-Commerce Control Tower | V-Guard Industries")
    
    # Check if we're using sample data
    is_sample = st.session_state.get('sample_data', True)
    if is_sample:
        st.warning("📊 Using sample data - Excel file not found. Please upload your Excel file using the sidebar.")
    
    # Get data
    district_df = app_data.get('DIM_DISTRICT', pd.DataFrame())
    sales_df = app_data.get('FACT_SALES', pd.DataFrame())
    weather_df = app_data.get('FACT_WEATHER', pd.DataFrame())
    inventory_df = app_data.get('FACT_INVENTORY', pd.DataFrame())
    marketing_df = app_data.get('FACT_MARKETING', pd.DataFrame())
    
    # --- KPI Cards ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate metrics
    if not sales_df.empty:
        total_revenue = sales_df['Gross_Revenue_INR'].sum()
        total_units = sales_df['Units_Sold'].sum()
    else:
        total_revenue = 84300000
        total_units = 19048
    
    if not weather_df.empty and 'Heat_Score' in weather_df.columns:
        avg_heat = weather_df['Heat_Score'].mean()
    else:
        avg_heat = 67.4
    
    active_districts = len(district_df['District_ID'].unique()) if not district_df.empty else 22
    
    # Temperature Anomaly
    anomaly = 0.0
    if not weather_df.empty and 'Temp_Anomaly' in weather_df.columns:
        anomaly = weather_df['Temp_Anomaly'].mean()
    
    with col1:
        st.metric(
            "Total Revenue",
            format_currency(total_revenue),
            delta="12.5% vs Plan",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Units Sold",
            format_number(total_units),
            delta="8.2% vs Plan",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Heat Score",
            f"{avg_heat:.1f}",
            delta="+3.1%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric("Active Districts", active_districts)
    
    with col5:
        st.metric("Temperature Anomaly", f"{anomaly:.2f}°C")
    
    # --- District Overview Table ---
    st.subheader("District Overview")
    
    if not district_df.empty:
        # Select columns for display
        display_cols = ['District_Name', 'State', 'Pop_M', 'CII_Score', 'CII_Category']
        available_cols = [col for col in display_cols if col in district_df.columns]
        
        if available_cols:
            district_display = district_df[available_cols].copy()
            district_display = district_display.head(10)
            
            # Rename columns
            rename_map = {
                'District_Name': 'District',
                'Pop_M': 'Population (M)',
                'CII_Score': 'CII Score'
            }
            district_display = district_display.rename(columns=rename_map)
            
            st.dataframe(
                district_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "District": st.column_config.TextColumn("District", width="medium"),
                    "State": st.column_config.TextColumn("State", width="small"),
                    "Population (M)": st.column_config.NumberColumn("Population (M)", format="%.2f"),
                    "CII Score": st.column_config.NumberColumn("CII Score", format="%.1f"),
                    "CII_Category": st.column_config.TextColumn("Category", width="small"),
                }
            )
        else:
            st.info("No district data available")
    else:
        st.info("No district data available. Please upload the Excel file.")
    
    # --- Charts Row ---
    col1, col2 = st.columns(2)
    
    # Sales by District
    with col1:
        st.subheader("Sales by District")
        if not sales_df.empty and not district_df.empty:
            district_sales = sales_df.groupby('District_ID')['Gross_Revenue_INR'].sum().reset_index()
            
            # Merge with district names
            if 'District_Name' in district_df.columns:
                district_sales = district_sales.merge(
                    district_df[['District_ID', 'District_Name']], 
                    on='District_ID', 
                    how='left'
                )
                x_col = 'District_Name'
            else:
                x_col = 'District_ID'
            
            fig = px.bar(
                district_sales.head(10),
                x=x_col,
                y='Gross_Revenue_INR',
                title="Top 10 Districts by Revenue",
                labels={'Gross_Revenue_INR': 'Revenue (₹)', x_col: 'District'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available")
    
    # SKU Mix
    with col2:
        st.subheader("SKU Mix")
        if not sales_df.empty:
            sku_sales = sales_df.groupby('SKU_ID')['Units_Sold'].sum().reset_index()
            
            fig = px.pie(
                sku_sales,
                values='Units_Sold',
                names='SKU_ID',
                title="Sales Distribution by SKU"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available")
    
    # --- Marketing Performance ---
    st.subheader("Marketing Performance")
    if not marketing_df.empty:
        col1, col2, col3 = st.columns(3)
        
        total_spend = marketing_df['Spend_INR'].sum() if 'Spend_INR' in marketing_df.columns else 0
        total_revenue_attr = marketing_df['Attributed_Revenue_INR'].sum() if 'Attributed_Revenue_INR' in marketing_df.columns else 0
        avg_roas = marketing_df['ROAS'].mean() if 'ROAS' in marketing_df.columns else 0
        
        with col1:
            st.metric("Total Marketing Spend", format_currency(total_spend))
        with col2:
            st.metric("Attributed Revenue", format_currency(total_revenue_attr))
        with col3:
            st.metric("Avg ROAS", f"{avg_roas:.1f}x")
    else:
        st.info("No marketing data available")
    
    # --- Data Status ---
    with st.expander("📊 Data Status", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Data Sources**")
            st.write(f"- Districts: {len(district_df)}")
            st.write(f"- Sales Records: {len(sales_df)}")
            st.write(f"- Weather Records: {len(weather_df)}")
        with col2:
            st.write("**Data Quality**")
            st.write(f"- Sample Data: {'Yes' if is_sample else 'No'}")
            if is_sample:
                st.warning("⚠️ Using sample data. Upload your Excel file for real data.")
