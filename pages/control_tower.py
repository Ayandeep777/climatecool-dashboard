import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.weather_api import WeatherAPI
from src.climate_engine import ClimateEngine
from utils.helpers import format_currency, format_number

def render(app_data):
    st.title("🏢 Control Tower - Executive Dashboard")
    st.caption("Climate-to-Commerce Control Tower | V-Guard Industries")
    
    # Initialize weather API
    weather_api = WeatherAPI()
    
    # Get data
    district_df = app_data.get('DIM_DISTRICT', pd.DataFrame())
    sales_df = app_data.get('FACT_SALES', pd.DataFrame())
    weather_df = app_data.get('FACT_WEATHER', pd.DataFrame())
    
    # Check if using sample data
    is_sample = st.session_state.get('sample_data', True)
    if is_sample:
        st.warning("📊 Using sample data. Upload your Excel file for real data.")
    
    # --- Live Weather Section ---
    st.subheader("🌤️ Live Weather")
    
    # Get districts with coordinates
    if not district_df.empty and 'Latitude' in district_df.columns and 'Longitude' in district_df.columns:
        # Select a district for weather
        district_names = district_df['District_Name'].tolist()
        selected_district = st.selectbox("Select District for Live Weather", district_names, index=0)
        
        # Get coordinates
        district_row = district_df[district_df['District_Name'] == selected_district].iloc[0]
        lat = district_row.get('Latitude', 28.61)
        lon = district_row.get('Longitude', 77.21)
        
        # Get weather
        with st.spinner(f"Fetching weather for {selected_district}..."):
            weather_data = weather_api.get_current_weather(lat, lon, selected_district)
        
        if weather_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Temperature", f"{weather_data['temperature']:.1f}°C")
            with col2:
                st.metric("Humidity", f"{weather_data['humidity']:.0f}%")
            with col3:
                heat_index = weather_api.get_heat_index(
                    weather_data['temperature'], 
                    weather_data['humidity']
                )
                st.metric("Feels Like", f"{heat_index:.1f}°C")
            with col4:
                st.metric("Weather", weather_data['weather_main'])
            
            # Get forecast
            forecast_df = weather_api.get_forecast(lat, lon, days=3)
            if not forecast_df.empty:
                # Show forecast chart
                fig = px.line(
                    forecast_df,
                    x='datetime',
                    y='temperature',
                    title=f"3-Day Forecast for {selected_district}",
                    labels={'temperature': 'Temperature (°C)', 'datetime': 'Date/Time'}
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("District coordinates not available. Please ensure your data has Latitude and Longitude columns.")
    
    # --- KPI Cards ---
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate metrics
    total_revenue = sales_df['Gross_Revenue_INR'].sum() if not sales_df.empty else 84300000
    total_units = sales_df['Units_Sold'].sum() if not sales_df.empty else 19048
    active_districts = len(district_df['District_ID'].unique()) if not district_df.empty else 22
    
    # Get heat score from weather or data
    if weather_data:
        heat_score = weather_api.get_heat_index(weather_data['temperature'], weather_data['humidity'])
    elif not weather_df.empty and 'Heat_Score' in weather_df.columns:
        heat_score = weather_df['Heat_Score'].mean()
    else:
        heat_score = 67.4
    
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
            "Heat Index",
            f"{heat_score:.1f}°C",
            delta="+3.1%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric("Active Districts", active_districts)
    
    with col5:
        # Show data status
        status = "✅ Live" if not is_sample and not weather_df.empty else "⚠️ Sample"
        st.metric("Data Status", status)
    
    # --- District Overview Table ---
    st.subheader("🏙️ District Overview")
    
    if not district_df.empty:
        display_cols = ['District_Name', 'State', 'Pop_M', 'CII_Score', 'CII_Category']
        available_cols = [col for col in display_cols if col in district_df.columns]
        
        if available_cols:
            district_display = district_df[available_cols].copy()
            
            # Add weather column if available
            if weather_data and 'District_Name' in district_df.columns:
                district_display['Current Temp (°C)'] = weather_data['temperature']
                district_display['Current Humidity (%)'] = weather_data['humidity']
            
            st.dataframe(
                district_display.head(10),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No district data available")
    else:
        st.info("No district data available")
    
    # --- Charts ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by District")
        if not sales_df.empty and not district_df.empty:
            district_sales = sales_df.groupby('District_ID')['Gross_Revenue_INR'].sum().reset_index()
            
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
