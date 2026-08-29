import pandas as pd
import streamlit as st
from pathlib import Path
import os
import sys
import tempfile
import shutil
sys.path.append(str(Path(__file__).parent.parent))

import config
from utils.logging_config import setup_logging

logger = setup_logging()

class DataLoader:
    """Loads and processes all sheets from the Excel data model."""

    def __init__(self, file_path: str = None):
        self.file_path = None
        self.file_found = False
        self.data = {}
        
        # Try to find the file in multiple locations
        if file_path:
            self.file_path = file_path
        else:
            self.file_path = self._find_excel_file()
        
        logger.info(f"DataLoader initialized with file: {self.file_path}")
        logger.info(f"File exists: {Path(self.file_path).exists() if self.file_path else False}")

    def _find_excel_file(self):
        """Find the Excel file in various possible locations."""
        possible_paths = [
            # Current directory paths
            Path("data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            Path("data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            Path("./data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            Path("../data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            
            # Streamlit Cloud paths
            Path("/mount/src/climatecool-dashboard/data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            Path("/app/data/V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            
            # Look for any Excel file in data directory
            Path("data").glob("*.xlsx"),
            Path("./data").glob("*.xlsx"),
            
            # Current working directory
            Path("V-Guard ClimateCool PowerBI Data Model and Datasets.xlsx"),
            Path("ClimateCool.xlsx"),
        ]
        
        # Check each path
        for path in possible_paths:
            if isinstance(path, Path) and path.exists():
                logger.info(f"Found Excel file at: {path}")
                return str(path)
        
        # Try to find any .xlsx file in data directory
        data_dir = Path("data")
        if data_dir.exists():
            excel_files = list(data_dir.glob("*.xlsx"))
            if excel_files:
                logger.info(f"Found Excel file at: {excel_files[0]}")
                return str(excel_files[0])
        
        # Check if file is in current directory
        excel_files = list(Path(".").glob("*.xlsx"))
        if excel_files:
            logger.info(f"Found Excel file in current directory: {excel_files[0]}")
            return str(excel_files[0])
        
        logger.warning("No Excel file found in any location")
        return None

    def load_all(self) -> dict:
        """Load all sheets into a dictionary of DataFrames."""
        try:
            # If file_path is None or file doesn't exist, try to find it again
            if not self.file_path or not Path(self.file_path).exists():
                self.file_path = self._find_excel_file()
                
                if not self.file_path or not Path(self.file_path).exists():
                    logger.error("Excel file not found")
                    st.warning("📁 Excel file not found. Please upload the file.")
                    return self._create_sample_data()

            logger.info(f"Loading Excel file from: {self.file_path}")
            
            # Check if file is readable
            try:
                excel_file = pd.ExcelFile(self.file_path)
            except Exception as e:
                logger.error(f"Error reading Excel file: {e}")
                st.error(f"❌ Error reading Excel file: {e}")
                return self._create_sample_data()
            
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

            # Verify we have data
            if not self.data or all(df.empty for df in self.data.values()):
                logger.error("No data loaded from Excel file")
                st.error("❌ No data loaded from the Excel file. Please check the file format.")
                return self._create_sample_data()
            
            # Check if we have the essential sheets
            has_districts = 'DIM_DISTRICT' in self.data and not self.data['DIM_DISTRICT'].empty
            has_sales = 'FACT_SALES' in self.data and not self.data['FACT_SALES'].empty
            
            if not has_districts or not has_sales:
                logger.warning("Essential sheets missing or empty")
                st.warning("⚠️ Some essential sheets are missing or empty. Using available data.")
            
            self.file_found = True
            return self.data

        except FileNotFoundError as e:
            logger.error(f"Excel file not found: {e}")
            st.error(f"❌ Data file not found: {e}")
            return self._create_sample_data()
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading data: {e}")
            st.error(f"❌ An unexpected error occurred: {e}")
            return self._create_sample_data()

    def _create_sample_data(self) -> dict:
        """Create sample data for demonstration when Excel file is not found."""
        st.info("📊 Using sample data for demonstration. Upload your Excel file to see real data.")
        
        # Create sample district data
        districts = pd.DataFrame({
            'District_ID': ['DIST_001', 'DIST_002', 'DIST_003', 'DIST_004', 'DIST_005'],
            'District_Name': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata'],
            'State': ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal'],
            'Pop_M': [16.79, 12.44, 8.44, 7.09, 4.5],
            'CII_Score': [62.69, 45, 40, 35, 30],
            'CII_Category': ['Medium', 'Medium', 'Low', 'Low', 'Low'],
            'TAM_Share_Pct': [12.17, 8.5, 5.2, 4.8, 3.5],
            'Latitude': [28.61, 19.08, 12.97, 13.08, 22.57],
            'Longitude': [77.21, 72.88, 77.59, 80.27, 88.36]
        })
        
        # Create sample SKU data
        skus = pd.DataFrame({
            'SKU_ID': ['SKU_001', 'SKU_002', 'SKU_003', 'SKU_004'],
            'SKU_Name': ['Personal Tower 30L', 'Mass Desert 65L', 'Heavy Desert 90L', 'Institutional 135L'],
            'ASP_INR': [6500, 9800, 13500, 18500],
            'Gross_Margin_Pct': [26.15, 29.59, 31.85, 32.97]
        })
        
        # Create sample sales data
        sales_data = []
        districts_list = ['DIST_001', 'DIST_002', 'DIST_003', 'DIST_004', 'DIST_005']
        skus_list = ['SKU_001', 'SKU_002', 'SKU_003', 'SKU_004']
        
        import random
        random.seed(42)
        
        for i, district in enumerate(districts_list):
            for sku in skus_list:
                for month in range(1, 13):
                    units = random.randint(5, 50)
                    price = 6500 if sku == 'SKU_001' else (9800 if sku == 'SKU_002' else (13500 if sku == 'SKU_003' else 18500))
                    revenue = units * price
                    margin = revenue * (0.26 if sku == 'SKU_001' else (0.29 if sku == 'SKU_002' else (0.31 if sku == 'SKU_003' else 0.32)))
                    sales_data.append({
                        'Date_Key': f'2026{month:02d}01',
                        'District_ID': district,
                        'SKU_ID': sku,
                        'Units_Sold': units,
                        'Gross_Revenue_INR': revenue,
                        'Gross_Margin_INR': margin
                    })
        
        sales = pd.DataFrame(sales_data)
        
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
        required_sheets = ['DIM_DISTRICT', 'DIM_SKU', 'FACT_SALES']
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
