from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import Incident
from app.utils.database import get_db

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


class IncidentIn(BaseModel):
    locationLabel: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: str
    severity: str
    status: str = "Active"


@router.get("")
def list_incidents(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: float = Query(10, description="Only used when lat/lng are given"),
    db: Session = Depends(get_db),
):
    query = db.query(Incident)
    rows = query.order_by(Incident.created_at.desc()).limit(100).all()

    if lat is not None and lng is not None:
        def within_radius(row):
            if row.lat is None or row.lng is None:
                return False
            # Flat-earth approximation is fine at this radius for a demo filter.
            dlat = (row.lat - lat) * 111.0
            dlng = (row.lng - lng) * 111.0 * 0.9
            return (dlat ** 2 + dlng ** 2) ** 0.5 <= radius_km
        rows = [r for r in rows if within_radius(r)]

    return [
        {
            "id": r.id, "locationLabel": r.location_label, "lat": r.lat, "lng": r.lng,
            "type": r.type, "severity": r.severity, "status": r.status,
            "createdAt": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.post("", status_code=201)
def report_incident(payload: IncidentIn, db: Session = Depends(get_db)):
    row = Incident(
        location_label=payload.locationLabel, lat=payload.lat, lng=payload.lng,
        type=payload.type, severity=payload.severity, status=payload.status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id}
