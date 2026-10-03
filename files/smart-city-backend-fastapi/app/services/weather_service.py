"""Weather data. Calls OpenWeatherMap server-side when OPENWEATHER_API_KEY is
configured (so the key never reaches the browser). Without a key, returns
deterministic, clearly-labeled simulation data instead of pretending to be a
live reading -- per the project's "never fabricate real-world data" rule.
"""
import random
from datetime import datetime, timezone

import httpx

from app.config import settings

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather(lat: float, lng: float) -> dict:
    if settings.OPENWEATHER_API_KEY:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(
                OPENWEATHER_BASE,
                params={"lat": lat, "lon": lng, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"},
            )
            if res.status_code == 200:
                data = res.json()
                return {
                    "source": "OpenWeatherMap",
                    "temp": data["main"]["temp"],
                    "feelsLike": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"].get("pressure"),
                    "visibility": data.get("visibility"),
                    "wind": data["wind"]["speed"],
                    "rainLastHour": (data.get("rain") or {}).get("1h", 0),
                    "condition": data["weather"][0]["description"].title(),
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                }
            # Real provider errored (bad key, quota, etc.) -- fall through to simulation
            # rather than surfacing a raw failure to the user.

    rnd = random.Random(f"{round(lat,3)}_{round(lng,3)}_{datetime.now(timezone.utc).date()}")
    return {
        "source": "Simulation Data",
        "temp": round(20 + rnd.random() * 16, 1),
        "feelsLike": round(19 + rnd.random() * 17, 1),
        "humidity": round(35 + rnd.random() * 55),
        "pressure": round(995 + rnd.random() * 30),
        "visibility": round(4000 + rnd.random() * 6000),
        "wind": round(4 + rnd.random() * 28, 1),
        "rainLastHour": round(rnd.random() * 8, 1),
        "condition": rnd.choice(["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Thunderstorms", "Haze"]),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
