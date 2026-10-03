"""Thin wrapper around Google Maps Platform REST endpoints that make sense to
call from the backend (keeping the key server-side). The interactive map
itself runs client-side via the Maps JavaScript API + MaxZoomService, which
requires the key in the browser by Google's own design — that's expected and
fine, since Google Maps API keys are meant to be restricted by HTTP referrer,
not treated as secret the way this service's other keys are.
"""
import httpx

from app.config import settings

GOOGLE_ELEVATION_BASE = "https://maps.googleapis.com/maps/api/elevation/json"


async def get_elevation(lat: float, lng: float):
    if not settings.GOOGLE_MAPS_API_KEY:
        return None
    async with httpx.AsyncClient(timeout=8) as client:
        res = await client.get(
            GOOGLE_ELEVATION_BASE,
            params={"locations": f"{lat},{lng}", "key": settings.GOOGLE_MAPS_API_KEY},
        )
        data = res.json()
        if data.get("status") == "OK" and data.get("results"):
            return data["results"][0]
        return None
