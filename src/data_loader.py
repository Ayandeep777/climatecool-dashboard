import pandas as pd
import streamlit as st
from pathlib import Path
import os
import sys
sys.path.append(str(Path(__file__).parent.parent))

import config
from utils.logging_config import setup_logging

logger = setup_logging()

class DataLoader:
    """Loads and processes all sheets from the Excel data model."""

    def __init__(self, file_path: str = None):
        # Handle file path for both local and cloud deployment
        if file_path is None:
            # Try multiple possible locations
            possible_paths = [
                config.EXCEL_FILE_PATH,
                Path("data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
                Path("/mount/src/climatecool-dashboard/data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
                Path("app/data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            ]
            
            # Find the first existing path
            for path in possible_paths:
                if path.exists():
                    self.file_path = str(path)
                    break
            else:
                # If no file found, try to find any .xlsx file in data directory
                data_dir = Path("data")
                if data_dir.exists():
                    excel_files = list(data_dir.glob("*.xlsx"))
                    if excel_files:
                        self.file_path = str(excel_files[0])
                    else:
                        self.file_path = str(config.EXCEL_FILE_PATH)
                else:
                    self.file_path = str(config.EXCEL_FILE_PATH)
        else:
            self.file_path = file_path
            
        self.data = {}
        logger.info(f"DataLoader initialized with file: {self.file_path}")

    def load_all(self) -> dict:
        """Load all sheets into a dictionary of DataFrames."""
        try:
            # Check if file exists
            if not Path(self.file_path).exists():
                logger.error(f"Excel file not found at {self.file_path}")
                st.error(f"❌ Data file not found. Please ensure the Excel file is in the 'data/' directory.")
                st.info("📁 Looking for: " + self.file_path)
                return self._create_sample_data()

            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names
            logger.info(f"Found sheets: {sheet_names}")

            for sheet in sheet_names:
                try:
                    # Use the sheet name as the key, replacing spaces and dots with underscores
                    key = sheet.replace(" ", "_").replace(".", "_")
                    self.data[key] = pd.read_excel(self.file_path, sheet_name=sheet)
                    logger.info(f"Loaded sheet: {sheet} with {len(self.data[key])} rows")
                except Exception as e:
                    logger.error(f"Error loading sheet {sheet}: {e}")
                    self.data[key] = pd.DataFrame()

            # Perform basic validations
            self._validate_data()
            return self.data

        except FileNotFoundError:
            logger.error(f"Excel file not found at {self.file_path}")
            st.error(f"❌ Data file not found. Please ensure 'data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx' exists.")
            return self._create_sample_data()
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading data: {e}")
            st.error(f"❌ An unexpected error occurred: {e}")
            return self._create_sample_data()

    def _create_sample_data(self) -> dict:
        """Create sample data for demonstration when Excel file is not found."""
        logger.warning("Creating sample data for demonstration purposes.")
        
        # Create sample district data
        districts = pd.DataFrame({
            'District_ID': ['DIST_001', 'DIST_002', 'DIST_003'],
            'District_Name': ['Delhi', 'Mumbai', 'Bangalore'],
            'State': ['Delhi', 'Maharashtra', 'Karnataka'],
            'Pop_M': [16.79, 12.44, 8.44],
            'CII_Score': [62.69, 45, 40],
            'CII_Category': ['Medium', 'Medium', 'Low'],
            'TAM_Share_Pct': [12.17, 8.5, 5.2]
        })
        
        # Create sample SKU data
        skus = pd.DataFrame({
            'SKU_ID': ['SKU_001', 'SKU_002', 'SKU_003', 'SKU_004'],
            'SKU_Name': ['Personal Tower 30L', 'Mass Desert 65L', 'Heavy Desert 90L', 'Institutional 135L'],
            'ASP_INR': [6500, 9800, 13500, 18500]
        })
        
        # Create sample sales data
        sales = pd.DataFrame({
            'Date_Key': ['20260101'] * 10,
            'District_ID': ['DIST_001'] * 10,
            'SKU_ID': ['SKU_001'] * 10,
            'Units_Sold': [5, 8, 12, 6, 15, 9, 7, 11, 4, 13],
            'Gross_Revenue_INR': [32500, 52000, 78000, 39000, 97500, 58500, 45500, 71500, 26000, 84500],
            'Gross_Margin_INR': [9750, 15600, 23400, 11700, 29250, 17550, 13650, 21450, 7800, 25350]
        })
        
        return {
            'DIM_DISTRICT': districts,
            'DIM_SKU': skus,
            'FACT_SALES': sales,
            'FACT_WEATHER': pd.DataFrame(),
            'FACT_INVENTORY': pd.DataFrame(),
            'FACT_MARKETING': pd.DataFrame(),
            'DIM_DEALER': pd.DataFrame(),
            'DIM_DATE': pd.DataFrame(),
            'FACT_STAGE_GATE': pd.DataFrame(),
            'DATA_PROVENANCE': pd.DataFrame()
        }

    def _validate_data(self):
        """Validate that essential sheets and columns exist."""
        required_sheets = ['DIM_DISTRICT', 'DIM_SKU', 'FACT_WEATHER', 'FACT_SALES', 'FACT_INVENTORY', 'FACT_MARKETING']
        for sheet in required_sheets:
            if sheet not in self.data or self.data[sheet].empty:
                logger.warning(f"Required sheet '{sheet}' is missing or empty.")
                st.session_state[f"data_missing_{sheet}"] = True
            else:
                st.session_state[f"data_missing_{sheet}"] = False

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Get a specific sheet by its original name."""
        key = sheet_name.replace(" ", "_").replace(".", "_")
        return self.data.get(key, pd.DataFrame())

    def get_dim_district(self) -> pd.DataFrame:
        """Get the DIM_DISTRICT DataFrame."""
        return self.get_sheet('DIM_DISTRICT')

    def get_dim_sku(self) -> pd.DataFrame:
        """Get the DIM_SKU DataFrame."""
        return self.get_sheet('DIM_SKU')

    def get_fact_weather(self) -> pd.DataFrame:
        """Get the FACT_WEATHER DataFrame."""
        return self.get_sheet('FACT_WEATHER')

    def get_fact_sales(self) -> pd.DataFrame:
        """Get the FACT_SALES DataFrame."""
        return self.get_sheet('FACT_SALES')

    def get_fact_inventory(self) -> pd.DataFrame:
        """Get the FACT_INVENTORY DataFrame."""
        return self.get_sheet('FACT_INVENTORY')

    def get_fact_marketing(self) -> pd.DataFrame:
        """Get the FACT_MARKETING DataFrame."""
        return self.get_sheet('FACT_MARKETING')

    def get_dim_date(self) -> pd.DataFrame:
        """Get the DIM_DATE DataFrame."""
        return self.get_sheet('DIM_DATE')

    def get_dim_dealer(self) -> pd.DataFrame:
        """Get the DIM_DEALER DataFrame."""
        return self.get_sheet('DIM_DEALER')

    def get_fact_stage_gate(self) -> pd.DataFrame:
        """Get the FACT_STAGE_GATE DataFrame."""
        return self.get_sheet('FACT_STAGE_GATE')

    def get_data_provenance(self) -> pd.DataFrame:
        """Get the DATA_PROVENANCE DataFrame."""
        return self.get_sheet('DATA_PROVENANCE')
