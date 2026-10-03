from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import air_quality, auth, incidents, locations, profile, smart_city, traffic, weather
from app.config import settings
from app.utils.database import Base, engine

# Creates tables on first run (SQLite by default, or PostgreSQL if DATABASE_URL
# points at one). For a real production rollout, swap this for Alembic
# migrations -- create_all() is fine for a project at this stage.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Backend for DEBANJAN'S CREATION — Smart City Live Intelligence Dashboard. "
                 "Auto-generated interactive docs available at /docs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["health"])
def health():
    return {"ok": True, "service": settings.APP_NAME, "version": settings.VERSION}


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(locations.router)
app.include_router(locations.saved_router)
app.include_router(weather.router)
app.include_router(traffic.router)
app.include_router(air_quality.router)
app.include_router(incidents.router)
app.include_router(smart_city.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    # Never leak a raw stack trace to the client -- log it server-side instead.
    import logging
    logging.getLogger("uvicorn.error").exception("Unhandled error on %s", request.url)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"error": "Internal server error."})
