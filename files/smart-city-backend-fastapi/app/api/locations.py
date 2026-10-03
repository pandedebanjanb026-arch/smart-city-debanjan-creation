from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import SavedLocation, User
from app.services.geocoding_service import geocode_details, geocode_search
from app.services.location_service import list_recent_searches, list_saved_locations, record_search_history
from app.utils.database import get_db
from app.utils.deps import get_current_user, get_current_user_optional

# GET /api/location/search, GET /api/location/details -- universal geocoding
router = APIRouter(prefix="/api/location", tags=["location"])

# GET/POST/DELETE /api/locations -- the signed-in user's own saved places + history
saved_router = APIRouter(prefix="/api/locations", tags=["saved-locations"])


@router.get("/search")
async def search_location(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    results = await geocode_search(q)
    if not results:
        raise HTTPException(404, "Location not found.")
    if user:
        top = results[0]
        record_search_history(
            db, user.id,
            label=top.get("name") or (top.get("display_name") or "").split(",")[0],
            display_name=top.get("display_name") or "",
            lat=float(top["lat"]), lng=float(top["lon"]),
        )
    return results


@router.get("/details")
async def location_details(lat: float, lng: float):
    result = await geocode_details(lat, lng)
    if not result:
        raise HTTPException(404, "Location not found.")
    return result


class SavedLocationIn(BaseModel):
    label: str
    displayName: Optional[str] = None
    lat: float
    lng: float
    level: Optional[str] = None


@saved_router.get("")
def list_saved(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = list_saved_locations(db, user.id)
    return [
        {"id": r.id, "label": r.label, "displayName": r.display_name, "lat": r.lat, "lng": r.lng, "level": r.level}
        for r in rows
    ]


@saved_router.post("", status_code=201)
def save_location(payload: SavedLocationIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = SavedLocation(
        user_id=user.id,
        label=payload.label,
        display_name=payload.displayName or payload.label,
        lat=payload.lat,
        lng=payload.lng,
        level=payload.level,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id}


@saved_router.delete("/{location_id}")
def delete_saved(location_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(SavedLocation).filter(SavedLocation.id == location_id, SavedLocation.user_id == user.id).first()
    if not row:
        raise HTTPException(404, "Saved location not found.")
    db.delete(row)
    db.commit()
    return {"ok": True}


@saved_router.get("/recent")
def recent_searches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = list_recent_searches(db, user.id)
    return [
        {"label": r.label, "displayName": r.display_name, "lat": r.lat, "lng": r.lng, "searchedAt": r.searched_at.isoformat()}
        for r in rows
    ]
