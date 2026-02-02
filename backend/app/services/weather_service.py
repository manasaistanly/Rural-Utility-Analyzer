import httpx
from datetime import datetime
from app.core.config import settings

class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    _cache = {}
    _cache_expiry = {}
    CACHE_DURATION = 600 # 10 minutes

    @staticmethod
    async def get_current_weather(lat: float = 17.3850, lon: float = 78.4867):
        # 1. Check Cache
        cache_key = f"weather_{lat}_{lon}"
        if cache_key in WeatherService._cache:
            if (datetime.now() - WeatherService._cache_expiry[cache_key]).total_seconds() < WeatherService.CACHE_DURATION:
                 return WeatherService._cache[cache_key]

        # 2. Fetch from API
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{WeatherService.BASE_URL}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": settings.WEATHER_API_KEY,
                        "units": "metric"
                    },
                    timeout=5.0 # Timeout after 5s
                )
                response.raise_for_status()
                data = response.json()
                
                # 3. Update Cache
                WeatherService._cache[cache_key] = data
                WeatherService._cache_expiry[cache_key] = datetime.now()
                
                return data
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    print("Weather API Rate Limit Reached! Using mock data.")
                    # Fallback Mock Data
                    mock_data = {
                        "main": {"temp": 28.5, "humidity": 65},
                        "weather": [{"main": "Clear", "description": "clear sky"}],
                        "name": "Hyderabad"
                    }
                    return mock_data
                print(f"HTTP Error fetching weather data: {e}")
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                
            # Return cached data even if expired (better than failing)
            if cache_key in WeatherService._cache:
                    return WeatherService._cache[cache_key]
            
            # Final Fallback if everything fails
            return {
                "main": {"temp": 25.0, "humidity": 60},
                "weather": [{"main": "Clouds", "description": "scattered clouds"}],
                "name": "Fallback City"
            }

    @staticmethod
    async def get_forecast(lat: float = 17.3850, lon: float = 78.4867):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{WeatherService.BASE_URL}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": settings.WEATHER_API_KEY,
                        "units": "metric"
                    }
                )
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                     # Mock Forecast Structure
                     return {
                         "list": [
                             {"dt": 1640000000, "main": {"temp": 28}, "weather": [{"main": "Clear"}]}
                         ]
                     }
            except Exception as e:
                print(f"Error fetching forecast: {e}")
                return None
