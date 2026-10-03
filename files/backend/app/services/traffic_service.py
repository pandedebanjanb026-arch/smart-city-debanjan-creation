"""Traffic and air-quality data.

There is no free, no-key, real-time traffic or AQI provider suitable for a
demo project, so both are honestly generated as deterministic simulation
data -- clearly labeled as such, never presented as live sensor data. Each
function is written as a single seam: if you add a real provider (Google
Roads/Traffic, IQAir, OpenAQI, etc.) later, only this file changes -- the
API routes and frontend contract stay the same.
"""
import random
from datetime import datetime, timezone


def get_traffic(lat: float, lng: float) -> dict:
    rnd = random.Random(f"traffic_{round(lat,3)}_{round(lng,3)}_{datetime.now(timezone.utc).date()}")
    roads = [
        {"name": f"Road {chr(65+i)}", "congestion": round(15 + rnd.random() * 80)}
        for i in range(3)
    ]
    busiest = max(roads, key=lambda r: r["congestion"])
    level = "HIGH" if busiest["congestion"] > 70 else "MODERATE" if busiest["congestion"] > 40 else "LOW"
    return {
        "source": "Traffic Simulation",
        "level": level,
        "roads": roads,
        "aiRecommendation": f"Increase green-light duration on {busiest['name']} by 20 seconds."
                             if level != "LOW" else "No signal-timing changes recommended right now.",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }


def get_air_quality(lat: float, lng: float) -> dict:
    rnd = random.Random(f"aqi_{round(lat,3)}_{round(lng,3)}_{datetime.now(timezone.utc).date()}")
    aqi = round(30 + rnd.random() * 220)
    category = "Good" if aqi < 50 else "Moderate" if aqi < 100 else "Poor" if aqi < 180 else "Very Poor"
    return {
        "source": "Simulation Data",
        "aqi": aqi,
        "category": category,
        "pm25": round(8 + rnd.random() * 140, 1),
        "pm10": round(15 + rnd.random() * 180, 1),
        "no2": round(5 + rnd.random() * 60, 1),
        "so2": round(2 + rnd.random() * 30, 1),
        "co": round(0.2 + rnd.random() * 2.5, 2),
        "o3": round(10 + rnd.random() * 90, 1),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
