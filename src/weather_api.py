import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

class WeatherAPI:
    """Handles OpenWeather API calls with caching and fallback."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or st.secrets.get("WEATHER_API_KEY", "4cca9dae74e69a773a7377d156058597")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.use_mock = st.secrets.get("USE_MOCK_WEATHER", "false").lower() == "true"
        self.cache = {}
        
    def get_current_weather(self, lat, lon, city_name=None):
        """Get current weather for a location."""
        cache_key = f"{lat}_{lon}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).seconds < 1800:  # 30 min cache
                return data
        
        if self.use_mock:
            return self._get_mock_weather(lat, lon, city_name)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse the response
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather_main': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'clouds': data['clouds']['all'],
                'timestamp': datetime.fromtimestamp(data['dt']),
                'city': data.get('name', city_name or 'Unknown')
            }
            
            # Cache the result
            self.cache[cache_key] = (datetime.now(), weather_data)
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return self._get_mock_weather(lat, lon, city_name)
    
    def get_forecast(self, lat, lon, days=5):
        """Get weather forecast for a location."""
        if self.use_mock:
            return self._get_mock_forecast(lat, lon, days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 readings per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_list = []
            for item in data['list']:
                forecast_list.append({
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed'],
                    'clouds': item['clouds']['all'],
                    'rain': item.get('rain', {}).get('3h', 0)
                })
            
            return pd.DataFrame(forecast_list)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API error: {e}")
            return self._get_mock_forecast(lat, lon, days)
    
    def _get_mock_weather(self, lat, lon, city_name=None):
        """Generate mock weather data for testing."""
        # Generate realistic mock data based on location
        base_temp = 25 + (lat - 20) * 0.5  # Warmer near equator
        temp = base_temp + (lon % 5) - 2
        
        return {
            'temperature': round(temp, 1),
            'humidity': round(40 + (lon % 30), 1),
            'pressure': round(1010 + (lat % 15), 1),
            'weather_main': ['Clear', 'Clouds', 'Rain', 'Haze'][int(lon) % 4],
            'weather_description': ['clear sky', 'few clouds', 'light rain', 'haze'][int(lon) % 4],
            'wind_speed': round(2 + (lat % 8), 1),
            'clouds': round(10 + (lon % 80), 0),
            'timestamp': datetime.now(),
            'city': city_name or f"City at {lat:.2f}, {lon:.2f}"
        }
    
    def _get_mock_forecast(self, lat, lon, days=5):
        """Generate mock forecast data."""
        forecasts = []
        base_temp = 25 + (lat - 20) * 0.5
        
        for day in range(days):
            for hour in [6, 9, 12, 15, 18, 21, 0, 3]:
                dt = datetime.now() + timedelta(days=day, hours=hour)
                # Diurnal variation
                hour_factor = 1 + 0.2 * (1 - abs(hour - 12) / 12)
                temp = base_temp + hour_factor * 3 + (day % 3) - 1
                
                forecasts.append({
                    'datetime': dt,
                    'temperature': round(temp, 1),
                    'humidity': round(45 + (dt.day % 25), 1),
                    'pressure': round(1010 + (dt.day % 10), 1),
                    'weather_main': ['Clear', 'Clouds', 'Rain'][(dt.day + dt.hour) % 3],
                    'weather_description': ['clear sky', 'few clouds', 'light rain'][(dt.day + dt.hour) % 3],
                    'wind_speed': round(2 + (dt.day % 6), 1),
                    'clouds': round(10 + ((dt.day + dt.hour) % 70), 0),
                    'rain': round(0.5 * ((dt.day + dt.hour) % 5), 1)
                })
        
        return pd.DataFrame(forecasts)
    
    def get_heat_index(self, temperature, humidity):
        """Calculate heat index (feels like temperature)."""
        # Simplified heat index calculation
        if temperature < 27:
            return temperature
        
        # Using simplified formula
        hi = (temperature 
              + 0.1 * humidity 
              - 10 * (1 if humidity < 40 else 0)
              + 2 * (1 if temperature > 35 else 0))
        return round(hi, 1)
