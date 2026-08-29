import pandas as pd
import streamlit as st
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)

@st.cache_data(ttl=600)
def load_excel_data(file_path: str) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load all relevant sheets from the Excel workbook.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary of DataFrames or None if error
    """
    if not Path(file_path).exists():
        logging.error(f"Excel file not found at {file_path}")
        st.error(f"Could not find data file at: {file_path}")
        return None

    try:
        excel_file = pd.ExcelFile(file_path)
        sheets_to_load = [
            "DATA_PROVENANCE",
            "DIM_DISTRICT",
            "DIM_SKU",
            "DIM_DATE",
            "DIM_DEALER",
            "FACT_WEATHER",
            "FACT_SALES",
            "FACT_INVENTORY",
            "FACT_MARKETING",
            "FACT_STAGE_GATE"
        ]
        
        data = {}
        for sheet in sheets_to_load:
            if sheet in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                data[sheet] = df
                logging.info(f"Loaded sheet: {sheet}, shape: {df.shape}")
            else:
                logging.warning(f"Sheet '{sheet}' not found.")
                data[sheet] = pd.DataFrame()
        
        # Add metadata
        data['_LOAD_TIMESTAMP'] = datetime.now().isoformat()
        data['_EXCEL_FILE'] = str(file_path)
        
        return data
        
    except Exception as e:
        logging.error(f"Error loading Excel file: {e}")
        st.error(f"Error loading data: {e}")
        return None


def get_standardized_data(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Clean, standardize, and prepare dataframes.
    
    Args:
        data_dict: Dictionary of raw dataframes
        
    Returns:
        Dictionary of processed dataframes
    """
    if not data_dict:
        return None

    # Extract dataframes
    df_district = data_dict.get("DIM_DISTRICT", pd.DataFrame()).copy()
    df_sku = data_dict.get("DIM_SKU", pd.DataFrame()).copy()
    df_date = data_dict.get("DIM_DATE", pd.DataFrame()).copy()
    df_dealer = data_dict.get("DIM_DEALER", pd.DataFrame()).copy()
    df_weather = data_dict.get("FACT_WEATHER", pd.DataFrame()).copy()
    df_sales = data_dict.get("FACT_SALES", pd.DataFrame()).copy()
    df_inventory = data_dict.get("FACT_INVENTORY", pd.DataFrame()).copy()
    df_marketing = data_dict.get("FACT_MARKETING", pd.DataFrame()).copy()
    df_stage_gate = data_dict.get("FACT_STAGE_GATE", pd.DataFrame()).copy()
    df_provenance = data_dict.get("DATA_PROVENANCE", pd.DataFrame()).copy()

    # Standardize column names
    def standardize_cols(df: pd.DataFrame) -> pd.DataFrame:
        if not df.empty:
            df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_')
        return df

    df_district = standardize_cols(df_district)
    df_sku = standardize_cols(df_sku)
    df_date = standardize_cols(df_date)
    df_dealer = standardize_cols(df_dealer)
    df_weather = standardize_cols(df_weather)
    df_sales = standardize_cols(df_sales)
    df_inventory = standardize_cols(df_inventory)
    df_marketing = standardize_cols(df_marketing)
    df_stage_gate = standardize_cols(df_stage_gate)
    df_provenance = standardize_cols(df_provenance)

    # Parse dates
    if not df_date.empty and 'DATE' in df_date.columns:
        df_date['DATE'] = pd.to_datetime(df_date['DATE'])
    if not df_date.empty and 'DATE_KEY' in df_date.columns:
        df_date['DATE_KEY'] = df_date['DATE_KEY'].astype(int)

    # Merge Date dimension with fact tables
    date_cols = ['DATE_KEY', 'DATE', 'YEAR', 'MONTH_NAME', 'QUARTER', 'SEASON_PHASE']
    date_df = df_date[date_cols] if not df_date.empty else pd.DataFrame()

    if not date_df.empty:
        if not df_weather.empty and 'DATE_KEY' in df_weather.columns:
            weather_merged = pd.merge(df_weather, date_df, on='DATE_KEY', how='left')
        else:
            weather_merged = df_weather
            
        if not df_sales.empty and 'DATE_KEY' in df_sales.columns:
            sales_merged = pd.merge(df_sales, date_df, on='DATE_KEY', how='left')
        else:
            sales_merged = df_sales
            
        if not df_inventory.empty and 'DATE_KEY' in df_inventory.columns:
            inventory_merged = pd.merge(df_inventory, date_df, on='DATE_KEY', how='left')
        else:
            inventory_merged = df_inventory
            
        if not df_marketing.empty and 'DATE_KEY' in df_marketing.columns:
            marketing_merged = pd.merge(df_marketing, date_df, on='DATE_KEY', how='left')
        else:
            marketing_merged = df_marketing
    else:
        weather_merged = df_weather
        sales_merged = df_sales
        inventory_merged = df_inventory
        marketing_merged = df_marketing

    # Merge District dimension
    if not df_district.empty:
        district_cols = ['DISTRICT_ID', 'DISTRICT_NAME', 'STATE', 'POP_M', 'URBAN_PCT', 
                        'DIST_READINESS', 'AC_GAP', 'LATITUDE', 'LONGITUDE']
        district_df = df_district[district_cols].copy() if all(c in df_district.columns for c in district_cols) else df_district
        
        if not weather_merged.empty and 'DISTRICT_ID' in weather_merged.columns:
            weather_merged = pd.merge(weather_merged, district_df, on='DISTRICT_ID', how='left')
        
        if not sales_merged.empty and 'DISTRICT_ID' in sales_merged.columns:
            sales_merged = pd.merge(sales_merged, district_df[['DISTRICT_ID', 'DISTRICT_NAME', 'STATE']], on='DISTRICT_ID', how='left')
        
        if not inventory_merged.empty and 'DISTRICT_ID' in inventory_merged.columns:
            inventory_merged = pd.merge(inventory_merged, district_df[['DISTRICT_ID', 'DISTRICT_NAME', 'STATE']], on='DISTRICT_ID', how='left')
        
        if not marketing_merged.empty and 'DISTRICT_ID' in marketing_merged.columns:
            marketing_merged = pd.merge(marketing_merged, district_df[['DISTRICT_ID', 'DISTRICT_NAME', 'STATE']], on='DISTRICT_ID', how='left')
        
        if not df_dealer.empty and 'DISTRICT_ID' in df_dealer.columns:
            dealer_district = pd.merge(df_dealer, district_df[['DISTRICT_ID', 'DISTRICT_NAME', 'STATE']], on='DISTRICT_ID', how='left')
        else:
            dealer_district = df_dealer
    else:
        dealer_district = df_dealer

    # Merge SKU dimension
    if not df_sku.empty:
        sku_cols = ['SKU_ID', 'SKU_NAME', 'CATEGORY', 'ASP_INR']
        sku_df = df_sku[sku_cols].copy() if all(c in df_sku.columns for c in sku_cols) else df_sku
        
        if not sales_merged.empty and 'SKU_ID' in sales_merged.columns:
            sales_merged = pd.merge(sales_merged, sku_df, on='SKU_ID', how='left')
        
        if not inventory_merged.empty and 'SKU_ID' in inventory_merged.columns:
            inventory_merged = pd.merge(inventory_merged, sku_df, on='SKU_ID', how='left')

    # Add timestamp
    timestamp = data_dict.get('_LOAD_TIMESTAMP', datetime.now().isoformat())
    excel_file = data_dict.get('_EXCEL_FILE', 'Unknown')

    return {
        "DIM_DISTRICT": df_district,
        "DIM_SKU": df_sku,
        "DIM_DATE": df_date,
        "DIM_DEALER": df_dealer,
        "FACT_WEATHER": weather_merged,
        "FACT_SALES": sales_merged,
        "FACT_INVENTORY": inventory_merged,
        "FACT_MARKETING": marketing_merged,
        "FACT_STAGE_GATE": df_stage_gate,
        "DATA_PROVENANCE": df_provenance,
        "DEALER_DISTRICT": dealer_district,
        "_LOAD_TIMESTAMP": timestamp,
        "_EXCEL_FILE": excel_file,
    }


@st.cache_data(ttl=300)
def load_live_weather_for_districts(df_district: pd.DataFrame) -> pd.DataFrame:
    """Load live weather for all districts."""
    try:
        from src.weather_api import WeatherAPI
        weather_api = WeatherAPI()
        return weather_api.get_weather_for_districts(df_district)
    except Exception as e:
        logging.error(f"Error loading live weather: {e}")
        return pd.DataFrame()