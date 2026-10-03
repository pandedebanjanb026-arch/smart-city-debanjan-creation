# DEBANJAN'S CREATION — Smart City API (Python / FastAPI)

The production-track backend for the Smart City Live Intelligence Dashboard,
built to the spec's requested structure: FastAPI, SQLAlchemy (SQLite by
default, PostgreSQL via one env var), JWT auth, and a modular services layer
per data type.

## Project overview

- **What it is:** a REST API for auth/profile/saved-locations, plus
  location search (Google Geocoding when you provide a key, OpenStreetMap
  Nominatim otherwise) and Smart City data endpoints (weather, air quality,
  traffic, incidents).
- **What it is not (yet):** connected to real traffic or air-quality
  providers — there's no free, no-key, real-time source for either, so
  those two always return clearly-labeled simulation data. Weather goes
  live automatically the moment you add an `OPENWEATHER_API_KEY`.

## Technology stack

Python · FastAPI · SQLAlchemy · SQLite/PostgreSQL · JWT (python-jose) ·
bcrypt (passlib) · httpx · Google Maps Platform (optional) · OpenWeatherMap
(optional)

## Folder structure

```
backend-fastapi/
├── app/
│   ├── main.py                 # FastAPI app, router wiring, CORS, error handler
│   ├── config.py                # Settings loaded from environment variables
│   ├── api/
│   │   ├── auth.py              # register / login / logout
│   │   ├── profile.py           # profile + preferred location
│   │   ├── locations.py         # /api/location/search, /details, saved locations, recent searches
│   │   ├── weather.py
│   │   ├── traffic.py
│   │   ├── air_quality.py
│   │   ├── incidents.py
│   │   └── smart_city.py        # combined overview endpoint
│   ├── services/
│   │   ├── geocoding_service.py # Google Geocoding or Nominatim, normalized
│   │   ├── google_maps_service.py
│   │   ├── weather_service.py   # real OpenWeatherMap or labeled simulation
│   │   ├── traffic_service.py   # traffic + air-quality simulation (documented seam for a real provider)
│   │   └── location_service.py  # saved-location / history queries
│   ├── models/__init__.py       # SQLAlchemy models
│   └── utils/                   # database session, security, auth dependency
├── docs/API.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md (this file)
```

I added `api/auth.py` and `api/profile.py` beyond the six files the spec's
folder tree named explicitly — section 18 (Register/Login/Logout/Profile)
needs them, and `main.py` wires them in alongside the rest.

## Environment variables

Copy `.env.example` to `.env` and fill in:

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | No (defaults to local SQLite) | `postgresql://user:pass@host:5432/dbname` in production |
| `JWT_SECRET` | Yes | Long random string signing session tokens |
| `JWT_EXPIRE_MINUTES` | No | Default 7 days |
| `GOOGLE_MAPS_API_KEY` | No | Enables real Google Geocoding server-side; leave blank to use Nominatim |
| `GEOCODE_USER_AGENT` | No | Only used with the Nominatim fallback |
| `OPENWEATHER_API_KEY` | No | Enables real weather; leave blank for labeled simulation |
| `CORS_ORIGINS` | No | Comma-separated list, default `*` |

None of these are committed — `.env` is git-ignored, only `.env.example` is tracked.

## Local installation

```bash
cd backend-fastapi
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit JWT_SECRET at minimum
uvicorn app.main:app --reload
```

API is live at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`. First run creates `smart_city.db`
automatically from the SQLAlchemy models — no manual migration step needed
for this stage of the project.

**Note on this environment:** these files were written and syntax-checked
(`python -m py_compile`) here, but this sandbox has no outbound network
access, so `pip install` and a live run couldn't be executed from here.
Nothing about that changes the code — install and run it locally with the
steps above.

## Database setup

- **Default (SQLite):** nothing to do — the `.db` file is created next to
  `app/` on first run.
- **PostgreSQL:** create a database, then set
  `DATABASE_URL=postgresql://user:password@host:5432/dbname` in `.env`.
  `psycopg2-binary` is already in `requirements.txt`. Tables are created the
  same way via SQLAlchemy — no schema file to run by hand.

## Google Maps API setup

1. In Google Cloud Console, create a project and enable **Geocoding API**
   (used here) and, for the frontend, **Maps JavaScript API** + **Places
   API**.
2. Create an API key, restrict it (HTTP referrers for the frontend key,
   IP/API restrictions for this backend's server-side key — Google
   recommends using *separate* keys for browser vs. server use).
3. Put the server-side key in this backend's `.env` as
   `GOOGLE_MAPS_API_KEY`. Put your browser-side key directly in the
   frontend's `GOOGLE_MAPS_API_KEY` constant (see the frontend's own notes —
   browser Maps JS API keys are restricted by referrer, not treated as a
   secret, so that one *is* meant to ship in client code).
4. Leave either blank and the corresponding feature falls back to a free,
   no-key alternative automatically (Nominatim for search; OpenStreetMap/
   Esri tiles for the map itself).

## Frontend setup

Point the dashboard's `BACKEND_URL` constant at wherever this API runs
(`http://localhost:8000/api` locally, or your deployed URL). The dashboard
pings `/api/health` on load and uses this backend automatically when it's
reachable; otherwise it falls back to its own in-browser demo mode.

## Deployment

- **Backend:** any ASGI-friendly host — Render, Railway, Fly.io, a plain VM
  with `uvicorn`/`gunicorn` behind Nginx, etc. Set the same environment
  variables there instead of a `.env` file.
- **Database:** managed PostgreSQL (Render/Railway/Neon/RDS) — just change
  `DATABASE_URL`.
- **Frontend:** the dashboard is a single static HTML file — any static
  host (Netlify, Vercel, GitHub Pages, S3) works. Update `BACKEND_URL` to
  the deployed API's address before publishing.

This repo doesn't include actual hosting-provider config (no Render/Fly
account exists to generate one against), so there's no `render.yaml` /
`Procfile` invented here — add the one your chosen host wants once you pick it.

## Security

- Passwords hashed with bcrypt, never stored or logged in plain text.
- JWT-based sessions; `Authorization: Bearer <token>` on protected routes.
- CORS restricted via `CORS_ORIGINS` (defaults to `*` for local dev — lock
  this down in production).
- All input validated via Pydantic models; invalid requests get a 4xx with
  a plain-language `error` field, not a stack trace.
- Unhandled exceptions are caught centrally and returned as a generic 500 —
  details go to the server log, never to the client.
- No secrets in source control (`.env` is git-ignored; only `.env.example`
  is committed).

## API documentation

See `docs/API.md` for a quick reference, or run the server and open
`/docs` for FastAPI's live, interactive OpenAPI UI.
