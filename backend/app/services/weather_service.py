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
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                
                # Return cached data even if expired (better than failing)
                if cache_key in WeatherService._cache:
                     return WeatherService._cache[cache_key]
                return None

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
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching forecast: {e}")
                return None
