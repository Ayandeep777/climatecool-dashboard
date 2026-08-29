# V-Guard ClimateCool Dashboard

## 🌊 Climate-to-Commerce Control Tower

An interactive management dashboard for V-Guard's ClimateCool strategy, combining real-time weather data with demand forecasting, inventory optimization, and SKU recommendations.

## 🚀 Features

- **Real-time Weather Integration**: Fetches live weather data from OpenWeather API
- **Climate Intelligence Index**: Weighted scoring of district potential
- **Demand Forecasting**: ML-based demand prediction
- **Inventory Optimization**: Smart inventory recommendations
- **SKU Recommendations**: Context-aware product suggestions
- **Interactive Visualizations**: Plotly-powered charts and maps
- **Scenario Simulation**: What-if analysis for business planning

## 📋 Prerequisites

- Python 3.9+
- OpenWeather API Key (optional, falls back to mock data)
- V-Guard ClimateCool Excel dataset

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Ayandeep777/climatecool-dashboard.git
cd climatecool-dashboard

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API key if available