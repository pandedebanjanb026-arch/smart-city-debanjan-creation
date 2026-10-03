from fastapi import APIRouter, Query

from app.services.traffic_service import get_traffic

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


@router.get("")
def traffic(lat: float = Query(...), lng: float = Query(...)):
    return get_traffic(lat, lng)
