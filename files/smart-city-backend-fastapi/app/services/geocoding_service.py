"""Server-side geocoding. Prefers the official Google Geocoding API when
GOOGLE_MAPS_API_KEY is configured; otherwise falls back to the free
OpenStreetMap Nominatim service. Either way, this never invents coordinates —
it returns exactly what the upstream provider verifies, normalized into one
shape so the frontend doesn't need to know which provider answered.
"""
import httpx

from app.config import settings

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
GOOGLE_GEOCODE_BASE = "https://maps.googleapis.com/maps/api/geocode/json"


def _normalize_google(result: dict) -> dict:
    location = result["geometry"]["location"]
    address = {}
    for comp in result.get("address_components", []):
        types = comp.get("types") or []
        if types:
            address[types[0]] = comp.get("long_name")
    return {
        "display_name": result.get("formatted_address"),
        "name": (result.get("address_components") or [{}])[0].get("long_name"),
        "lat": location["lat"],
        "lon": location["lng"],
        "type": (result.get("types") or ["place"])[0],
        "addresstype": (result.get("types") or ["place"])[0],
        "place_id": result.get("place_id"),
        "address": address,
        "source": "Google Geocoding API",
    }


async def geocode_search(query: str) -> list:
    if settings.GOOGLE_MAPS_API_KEY:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(
                GOOGLE_GEOCODE_BASE,
                params={"address": query, "key": settings.GOOGLE_MAPS_API_KEY},
            )
            data = res.json()
            if data.get("status") == "OK":
                return [_normalize_google(r) for r in data["results"]]
            return []

    async with httpx.AsyncClient(timeout=8, headers={"User-Agent": settings.GEOCODE_USER_AGENT}) as client:
        res = await client.get(
            f"{NOMINATIM_BASE}/search",
            params={"format": "jsonv2", "addressdetails": 1, "limit": 8, "q": query, "accept-language": "en"},
        )
        results = res.json()
        for r in results:
            r["source"] = "OpenStreetMap Nominatim"
        return results


async def geocode_details(lat: float, lng: float):
    if settings.GOOGLE_MAPS_API_KEY:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(
                GOOGLE_GEOCODE_BASE,
                params={"latlng": f"{lat},{lng}", "key": settings.GOOGLE_MAPS_API_KEY},
            )
            data = res.json()
            if data.get("status") == "OK" and data["results"]:
                return _normalize_google(data["results"][0])
            return None

    async with httpx.AsyncClient(timeout=8, headers={"User-Agent": settings.GEOCODE_USER_AGENT}) as client:
        res = await client.get(
            f"{NOMINATIM_BASE}/reverse",
            params={"format": "jsonv2", "addressdetails": 1, "lat": lat, "lon": lng, "accept-language": "en"},
        )
        data = res.json()
        if "error" in data:
            return None
        data["source"] = "OpenStreetMap Nominatim"
        return data
