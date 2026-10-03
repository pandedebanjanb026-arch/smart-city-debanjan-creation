from fastapi import APIRouter, Query

from app.services.traffic_service import get_air_quality

router = APIRouter(prefix="/api/air-quality", tags=["air-quality"])


@router.get("")
def air_quality(lat: float = Query(...), lng: float = Query(...)):
    return get_air_quality(lat, lng)
