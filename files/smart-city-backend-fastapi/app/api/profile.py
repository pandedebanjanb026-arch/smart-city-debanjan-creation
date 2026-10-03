from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import Profile, User
from app.utils.database import get_db
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


class PreferredLocationIn(BaseModel):
    label: Optional[str] = None
    displayName: Optional[str] = None
    lat: float
    lng: float
    level: Optional[str] = None


class ProfileUpdate(BaseModel):
    fullName: Optional[str] = None
    preferredLocation: Optional[PreferredLocationIn] = None


def _serialize(user: User, profile: Optional[Profile]):
    preferred = None
    if profile and profile.preferred_lat is not None:
        preferred = {
            "label": profile.preferred_label,
            "displayName": profile.preferred_display_name,
            "lat": profile.preferred_lat,
            "lng": profile.preferred_lng,
            "level": profile.preferred_level,
        }
    return {
        "user": {
            "id": user.id,
            "fullName": user.full_name,
            "email": user.email,
            "createdAt": user.created_at.isoformat(),
        },
        "preferredLocation": preferred,
    }


@router.get("")
def read_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    return _serialize(user, profile)


@router.put("")
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.fullName and payload.fullName.strip():
        user.full_name = payload.fullName.strip()

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        profile = Profile(user_id=user.id)
        db.add(profile)

    if payload.preferredLocation:
        loc = payload.preferredLocation
        profile.preferred_label = loc.label
        profile.preferred_display_name = loc.displayName
        profile.preferred_lat = loc.lat
        profile.preferred_lng = loc.lng
        profile.preferred_level = loc.level

    db.commit()
    db.refresh(user)
    db.refresh(profile)
    return _serialize(user, profile)
