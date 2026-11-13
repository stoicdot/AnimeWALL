# AnimeWall Backend — Phase 2 Foundation

This folder contains the Phase 2 FastAPI foundation for the existing AnimeWall frontend. It does not replace or modify the frontend.

## Included in Phase 2

- FastAPI application and OpenAPI documentation.
- Pydantic Settings configuration loaded from environment variables.
- Async SQLAlchemy 2.0 engine and request-scoped PostgreSQL sessions using `asyncpg`.
- PostgreSQL liveness/readiness checks.
- Configurable exact-origin CORS with credentials enabled for the future refresh-cookie flow.
- Server-generated request IDs and consistent, non-sensitive error responses.
- Async Alembic environment and an empty baseline migration.
- Automated tests for health, database-readiness behaviour, CORS, error envelopes and OpenAPI availability.
- Verification record in `docs/phase2-verification.md`.

## Not implemented yet

No business tables, authentication endpoints, wallpaper CRUD, favorites, collections, Supabase uploads or admin APIs are included in Phase 2. Those are intentionally deferred to later phases. The first Alembic migration is empty and only establishes migration history; it does not create domain tables.

## Requirements

- Python 3.12 or newer.
- PostgreSQL 14+ (local or hosted).
- A database named `animewall` and a user with permission to connect/create migration objects.

## Windows PowerShell setup

Run these commands from the `backend` directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Open `.env` and replace `CHANGE_ME` in `DATABASE_URL` with your PostgreSQL password. If the password contains URL-reserved characters such as `@`, `:`, `/`, `#` or `%`, URL-encode those characters.

## Linux / macOS setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env` and configure `DATABASE_URL` before running migrations or the readiness check.

## Run the backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Liveness: <http://127.0.0.1:8000/api/health/live>
- Readiness (requires reachable PostgreSQL): <http://127.0.0.1:8000/api/health/ready>

The application can start while PostgreSQL is unavailable; `/api/health/live` will still report process liveness, while `/api/health/ready` returns `503 DATABASE_UNAVAILABLE` until PostgreSQL is reachable.

## Apply Alembic baseline

After creating the database and configuring `.env`:

```bash
alembic upgrade head
alembic current
```

The current Phase 2 baseline is intentionally empty. It creates Alembic's version table but no AnimeWall business tables. The domain schema will arrive in later migrations alongside the SQLAlchemy models. See `docs/phase2-verification.md` for checks completed and limitations.

## Run tests

```bash
python -m pytest -q
```

The readiness tests override the database dependency with test doubles. They do not require a running PostgreSQL instance.

## Frontend CORS

`CORS_ORIGINS` is a JSON array in `.env`. Add the exact origin (scheme, hostname and port) used by your static frontend server. Examples for common local ports are already included. Do not use `*` when credentialed requests are enabled.

## Security notes

- `.env` is ignored by Git; commit only `.env.example`.
- No production passwords, signing keys or Supabase credentials are included.
- Do not expose the Supabase service-role key to the browser.
- PostgreSQL should use a dedicated least-privilege application user in production.
- HTTPS, production secret management, authentication and CSRF enforcement are completed in their relevant later phases.
