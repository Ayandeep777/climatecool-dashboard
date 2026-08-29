import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, Optional, List
from config import Config

logging.basicConfig(level=logging.INFO)

class WeatherAPI:
    """Real-time weather data fetcher with multiple fallback mechanisms."""
    
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = Config.WEATHER_API_BASE_URL
        self.use_openweather = Config.USE_OPENWEATHER
        self.use_mock = Config.USE_MOCK_WEATHER
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def get_live_weather(self, lat: float, lon: float, district_name: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch live weather for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            district_name: Optional district name for logging
            
        Returns:
            Dict with standardized weather data or None if failed
        """
        cache_key = f"{lat:.2f},{lon:.2f}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        weather_data = None
        
        # Try OpenWeather API first
        if self.use_openweather and self.api_key and self.api_key != "your_openweather_api_key_here":
            try:
                weather_data = self._fetch_openweather(lat, lon)
                if weather_data:
                    self.cache[cache_key] = (datetime.now(), weather_data)
                    logging.info(f"Fetched live weather for {district_name or 'location'}")
                    return weather_data
            except Exception as e:
                logging.warning(f"OpenWeather API failed: {e}")
        
        # Fallback to mock data
        if self.use_mock:
            weather_data = self._fetch_mock_weather(lat, lon, district_name)
            if weather_data:
                self.cache[cache_key] = (datetime.now(), weather_data)
                logging.info(f"Using mock weather for {district_name or 'location'}")
                return weather_data
        
        return None
    
    def _fetch_openweather(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch weather from OpenWeather API."""
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(f"{self.base_url}weather", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Calculate temperature anomaly (compared to 30-year normal)
                # Simple proxy using monthly averages
                month = datetime.now().month
                monthly_normals = {
                    1: 20, 2: 22, 3: 28, 4: 35, 5: 38, 6: 37,
                    7: 33, 8: 32, 9: 31, 10: 28, 11: 24, 12: 21
                }
                normal_temp = monthly_normals.get(month, 28)
                temp_anomaly = data['main']['temp'] - normal_temp
                
                return {
                    'tmax_observed': data['main']['temp_max'],
                    'tmin_observed': data['main']['temp_min'],
                    'temp_obs': data['main']['temp'],
                    'temp_anomaly': round(temp_anomaly, 2),
                    'relative_humidity': data['main']['humidity'],
                    'rainfall_mm': data.get('rain', {}).get('1h', 0),
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'weather_condition': data['weather'][0]['description'],
                    'heatwave_days': 1 if data['main']['temp'] > 40 else 0,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'OpenWeather Live'
                }
            else:
                logging.error(f"OpenWeather API error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            return None
    
    def _fetch_mock_weather(self, lat: float, lon: float, district_name: Optional[str] = None) -> Dict:
        """Generate realistic mock weather data based on location."""
        # Use deterministic but realistic values
        # Base values for North India
        month = datetime.now().month
        
        # Temperature patterns (simplified)
        base_temp = 28
        season_factor = 1 + 0.3 * np.sin((month - 5) * 2 * np.pi / 12)
        
        # Humidity patterns
        base_humidity = 45
        humidity_factor = 1 + 0.5 * np.sin((month - 7) * 2 * np.pi / 12)
        
        # Add location-based variation
        lat_factor = (lat - 20) / 10  # 20-30N range
        temp_offset = lat_factor * 5
        
        # Add some randomness
        np.random.seed(int(abs(lat * 100 + lon * 100) * 1000 + month))
        noise_temp = np.random.normal(0, 2)
        noise_humidity = np.random.normal(0, 5)
        
        tmax = base_temp * season_factor + temp_offset + noise_temp
        tmin = tmax - np.random.uniform(5, 12)
        humidity = base_humidity * humidity_factor + noise_humidity
        
        # Normalize values
        tmax = np.clip(tmax, 15, 45)
        tmin = np.clip(tmin, 5, 35)
        humidity = np.clip(humidity, 15, 90)
        
        # Calculate anomaly based on historical normal
        monthly_normals = {
            1: 20, 2: 22, 3: 28, 4: 35, 5: 38, 6: 37,
            7: 33, 8: 32, 9: 31, 10: 28, 11: 24, 12: 21
        }
        normal_temp = monthly_normals.get(month, 28)
        temp_anomaly = tmax - normal_temp
        
        return {
            'tmax_observed': round(tmax, 1),
            'tmin_observed': round(tmin, 1),
            'temp_obs': round((tmax + tmin) / 2, 1),
            'temp_anomaly': round(temp_anomaly, 2),
            'relative_humidity': round(humidity, 1),
            'rainfall_mm': round(max(0, np.random.exponential(10)), 1),
            'pressure': round(1013 + np.random.normal(0, 10), 1),
            'wind_speed': round(np.random.exponential(3), 1),
            'weather_condition': 'Clear' if humidity < 60 else 'Cloudy',
            'heatwave_days': 1 if tmax > 40 else 0,
            'timestamp': datetime.now().isoformat(),
            'source': 'Mock IMD Data'
        }

    def get_weather_for_districts(self, df_district: pd.DataFrame) -> pd.DataFrame:
        """
        Fetch weather for all districts in the dataframe.
        
        Args:
            df_district: DataFrame with district information
            
        Returns:
            DataFrame with weather data for each district
        """
        weather_data = []
        
        for idx, row in df_district.iterrows():
            # Get coordinates from config or use from dataframe
            district_name = row.get('DISTRICT_NAME', '')
            lat = row.get('LATITUDE', None)
            lon = row.get('LONGITUDE', None)
            
            # If coordinates missing, use config defaults
            if lat is None or lon is None:
                if district_name in Config.DISTRICT_COORDINATES:
                    coords = Config.DISTRICT_COORDINATES[district_name]
                    lat = coords['lat']
                    lon = coords['lon']
                else:
                    continue
            
            weather = self.get_live_weather(lat, lon, district_name)
            
            if weather:
                weather['DISTRICT_ID'] = row.get('DISTRICT_ID', None)
                weather['DISTRICT_NAME'] = district_name
                weather['STATE'] = row.get('STATE', None)
                weather_data.append(weather)
            
            # Rate limiting for API
            time.sleep(0.2)
        
        return pd.DataFrame(weather_data)

    def get_forecast(self, lat: float, lon: float, days: int = 5) -> Optional[pd.DataFrame]:
        """
        Get weather forecast for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast
            
        Returns:
            DataFrame with forecast data
        """
        if not self.api_key or self.api_key == "your_openweather_api_key_here":
            return self._generate_mock_forecast(lat, lon, days)
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': days * 8  # 3-hour intervals
        }
        
        try:
            response = requests.get(f"{self.base_url}forecast", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast_data = []
                
                for item in data['list'][:days * 8]:
                    forecast_data.append({
                        'datetime': item['dt_txt'],
                        'temp': item['main']['temp'],
                        'temp_max': item['main']['temp_max'],
                        'temp_min': item['main']['temp_min'],
                        'humidity': item['main']['humidity'],
                        'rainfall': item.get('rain', {}).get('3h', 0),
                        'weather': item['weather'][0]['description'],
                    })
                
                return pd.DataFrame(forecast_data)
            else:
                logging.error(f"Forecast API error: {response.status_code}")
                return self._generate_mock_forecast(lat, lon, days)
                
        except Exception as e:
            logging.error(f"Forecast error: {e}")
            return self._generate_mock_forecast(lat, lon, days)
    
    def _generate_mock_forecast(self, lat: float, lon: float, days: int) -> pd.DataFrame:
        """Generate mock forecast data."""
        forecast_data = []
        current_time = datetime.now()
        
        for day in range(days):
            for hour in [6, 12, 18, 24]:
                dt = current_time + timedelta(days=day, hours=hour - current_time.hour)
                
                # Generate realistic patterns
                temp_base = 28 + (day * 0.5)
                hour_factor = 1 + 0.2 * np.sin((hour - 6) * np.pi / 12)
                temp = temp_base * hour_factor + np.random.normal(0, 2)
                
                forecast_data.append({
                    'datetime': dt.isoformat(),
                    'temp': round(np.clip(temp, 15, 45), 1),
                    'temp_max': round(np.clip(temp + 3, 15, 45), 1),
                    'temp_min': round(np.clip(temp - 5, 5, 35), 1),
                    'humidity': round(np.clip(45 + np.random.normal(0, 10), 15, 90), 1),
                    'rainfall': round(max(0, np.random.exponential(5)), 1),
                    'weather': ['Clear', 'Cloudy', 'Partly Cloudy', 'Rain'][np.random.randint(0, 4)],
                })
        
        return pd.DataFrame(forecast_data)