"""Shared query helpers for a user's saved locations and recent-search
history, used by app.api.locations. Kept separate from the route module so
the same logic can be reused (e.g. by a future recommendations feature)
without duplicating queries.
"""
from sqlalchemy.orm import Session

from app.models import LocationHistory, SavedLocation


def list_saved_locations(db: Session, user_id: int):
    return (
        db.query(SavedLocation)
        .filter(SavedLocation.user_id == user_id)
        .order_by(SavedLocation.created_at.desc())
        .all()
    )


def record_search_history(db: Session, user_id: int, label: str, display_name: str, lat: float, lng: float, limit: int = 20):
    entry = LocationHistory(user_id=user_id, label=label, display_name=display_name, lat=lat, lng=lng)
    db.add(entry)
    db.commit()

    # Keep the table small -- trim anything past the most recent `limit` entries.
    old_ids = (
        db.query(LocationHistory.id)
        .filter(LocationHistory.user_id == user_id)
        .order_by(LocationHistory.searched_at.desc())
        .offset(limit)
        .all()
    )
    if old_ids:
        db.query(LocationHistory).filter(LocationHistory.id.in_([row.id for row in old_ids])).delete(
            synchronize_session=False
        )
        db.commit()


def list_recent_searches(db: Session, user_id: int, limit: int = 10):
    return (
        db.query(LocationHistory)
        .filter(LocationHistory.user_id == user_id)
        .order_by(LocationHistory.searched_at.desc())
        .limit(limit)
        .all()
    )
