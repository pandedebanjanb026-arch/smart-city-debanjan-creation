from fastapi import APIRouter, Query

from app.services.weather_service import get_weather

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("")
async def weather(lat: float = Query(...), lng: float = Query(...)):
    return await get_weather(lat, lng)
