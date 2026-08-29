import pandas as pd
import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

class DataLoader:
    """Loads and processes all sheets from the Excel data model."""

    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.data = {}

    def load_all(self) -> dict:
        """Load all sheets from the Excel file."""
        try:
            # Try to find the file
            if not self.file_path:
                data_dir = Path("data")
                excel_files = list(data_dir.glob("*.xlsx")) + list(Path(".").glob("*.xlsx"))
                if excel_files:
                    self.file_path = str(excel_files[0])
                else:
                    return self._create_sample_data()
            
            if not Path(self.file_path).exists():
                return self._create_sample_data()
            
            # Load the file
            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names
            
            for sheet in sheet_names:
                key = sheet.replace(" ", "_").replace(".", "_")
                self.data[key] = pd.read_excel(self.file_path, sheet_name=sheet)
            
            return self.data
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return self._create_sample_data()

    def _create_sample_data(self) -> dict:
        """Create sample data when file is not found."""
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

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        key = sheet_name.replace(" ", "_").replace(".", "_")
        return self.data.get(key, pd.DataFrame())
