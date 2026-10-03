"""Aggregate endpoint -- combines weather, air quality, and traffic for a
location into one response, matching the frontend's module-strip overview.
Each field carries its own `source`, so the client can render "Simulation
Data" vs a real provider name without the backend needing to lie about it.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.services.traffic_service import get_air_quality, get_traffic
from app.services.weather_service import get_weather
from app.utils.database import get_db
from app.models import Incident

router = APIRouter(prefix="/api/smart-city", tags=["smart-city"])


@router.get("/overview")
async def overview(lat: float = Query(...), lng: float = Query(...), db: Session = Depends(get_db)):
    weather = await get_weather(lat, lng)
    traffic = get_traffic(lat, lng)
    air = get_air_quality(lat, lng)

    incidents = (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "weather": weather,
        "traffic": traffic,
        "airQuality": air,
        "incidentCount": len(incidents),
    }
