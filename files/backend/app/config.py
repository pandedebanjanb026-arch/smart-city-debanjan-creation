import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "DEBANJAN'S CREATION — Smart City API"
    VERSION = "1.0.0"

    # Database — SQLite by default (zero setup), point DATABASE_URL at
    # PostgreSQL in production, e.g. postgresql://user:pass@host:5432/dbname
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_city.db")

    # Auth
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days

    # Google Maps Platform — leave blank to fall back to free providers.
    # NEVER exposed to the frontend directly; only this backend calls Google
    # with it, and only for server-side geocoding requests.
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Free fallback geocoder (OpenStreetMap Nominatim) — used automatically
    # whenever GOOGLE_MAPS_API_KEY is not set. Nominatim's usage policy asks
    # for an identifying User-Agent with contact info.
    GEOCODE_USER_AGENT = os.getenv(
        "GEOCODE_USER_AGENT",
        "DebanjansCreationSmartCity/1.0 (set GEOCODE_USER_AGENT in .env with a contact email)"
    )

    # Optional real weather provider. Leave blank and /api/weather returns
    # clearly-labeled "Simulation Data" instead of pretending to be live.
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]


settings = Settings()
