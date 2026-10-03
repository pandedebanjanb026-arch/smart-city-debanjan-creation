# API Reference

FastAPI generates interactive docs automatically once the server is running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Raw OpenAPI schema: `http://localhost:8000/openapi.json`

This file is a quick human-readable summary of the same routes.

## Health

`GET /api/health` — `{ ok, service, version }`

## Auth

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/auth/register` | `fullName, email, password, confirmPassword` | Creates account, returns `{ token, user }` |
| POST | `/api/auth/login` | `email, password` | Returns `{ token, user }` |
| POST | `/api/auth/logout` | — | Stateless; client discards the token |

## Profile (auth required — `Authorization: Bearer <token>`)

| Method | Path | Notes |
|---|---|---|
| GET | `/api/profile` | Returns `{ user, preferredLocation }` |
| PUT | `/api/profile` | Body: `{ fullName?, preferredLocation? }` |

## Location search (Google Geocoding when `GOOGLE_MAPS_API_KEY` is set, Nominatim otherwise)

| Method | Path | Notes |
|---|---|---|
| GET | `/api/location/search?q=` | Universal search — country down to address. 404 if nothing matches. |
| GET | `/api/location/details?lat=&lng=` | Reverse geocode. 404 if nothing matches. |

## Saved locations & history (auth required)

| Method | Path | Notes |
|---|---|---|
| GET | `/api/locations` | List saved locations |
| POST | `/api/locations` | Body: `{ label, displayName?, lat, lng, level? }` |
| DELETE | `/api/locations/{id}` | Remove a saved location |
| GET | `/api/locations/recent` | Last 10 searches (auto-recorded when logged in and searching) |

## Smart City data

| Method | Path | Notes |
|---|---|---|
| GET | `/api/weather?lat=&lng=` | Real (OpenWeatherMap) if `OPENWEATHER_API_KEY` set, else `source: "Simulation Data"` |
| GET | `/api/air-quality?lat=&lng=` | Always `source: "Simulation Data"` in this build — no no-key real-time AQI provider wired in |
| GET | `/api/traffic?lat=&lng=` | Always `source: "Traffic Simulation"` — includes a naive AI-style signal-timing suggestion |
| GET | `/api/incidents?lat=&lng=&radius_km=` | Real DB-backed incident reports (starts empty until `POST /api/incidents`) |
| POST | `/api/incidents` | Report an incident: `{ locationLabel?, lat?, lng?, type, severity, status? }` |
| GET | `/api/smart-city/overview?lat=&lng=` | Combines weather + traffic + air quality + incident count in one call |

Every simulated field carries an explicit `source` value ("Simulation Data" /
"Traffic Simulation") so the frontend never has to guess whether a number is
real.
