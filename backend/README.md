
# AnimeWall Backend

**Find Your Anime Aesthetic.**

AnimeWall is an anime wallpaper discovery and sharing platform. This repository contains its Python FastAPI backend, responsible for authentication, wallpaper management, category browsing, database operations and storage services.

## Features

- User registration and login
- JWT-based access authentication
- Argon2 password hashing
- Authenticated user profile endpoint
- Public wallpaper listing and detail endpoints
- Category listing with published wallpaper counts
- Wallpaper submission with unpublished-by-default status
- Wallpaper rights and permission validation
- Image format validation and SHA-256 checksums
- Supabase Storage integration
- Async PostgreSQL database access
- Alembic database migrations
- Consistent API error responses
- Request ID middleware
- Configurable CORS
- Automated test suite

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Driver | asyncpg |
| Migrations | Alembic |
| Validation | Pydantic |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Image Processing | Pillow |
| Storage | Supabase Storage |
| Testing | Pytest, pytest-asyncio, HTTPX |

## Project Structure

```text
backend/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── middleware.py
│   │
│   ├── models/
│   │   ├── base.py
│   │   ├── category.py
│   │   ├── user.py
│   │   ├── wallpaper.py
│   │   ├── wallpaper_asset.py
│   │   └── wallpaper_rights.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── health.py
│   │   └── wallpapers.py
│   │
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   ├── dependencies.py
│   └── main.py
│
├── docs/
├── tests/
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── .env.example
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/stoicdot/AnimeWALL.git
cd AnimeWALL/backend
```

### 2. Create a virtual environment

Windows:

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file:

Windows CMD:

```cmd
if not exist .env copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Configure the values in `.env`:

| Variable | Description |
|---|---|
| DATABASE_URL | PostgreSQL async connection URL |
| JWT_SECRET_KEY | Secret used for signing access tokens |
| JWT_ALGORITHM | JWT signing algorithm |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access-token lifetime |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_SERVICE_ROLE_KEY | Backend-only Supabase service key |
| SUPABASE_STORAGE_BUCKET | Storage bucket name |
| CORS_ORIGINS | Allowed frontend origins |
| APP_ENV | Application environment |
| DEBUG | Debug mode |

Generate a strong JWT secret locally. Never commit real secrets or your `.env` file.

**Important:** Keep the Supabase service-role key on the backend only. Never expose it in frontend JavaScript.

## Database Setup

AnimeWall uses PostgreSQL with asynchronous SQLAlchemy sessions.

After configuring `DATABASE_URL` and creating the database, apply migrations:

```bash
python -m alembic upgrade head
```

Check the current migration:

```bash
python -m alembic current
```

View migration history:

```bash
python -m alembic history
```

The migration chain includes:

1. Phase 2 foundation
2. User, category, wallpaper and wallpaper asset tables
3. Wallpaper rights records

## Running the Backend

Start the development server:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### API Documentation

| Resource | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI JSON | http://127.0.0.1:8000/openapi.json |

## API Endpoints

All API endpoints use the `/api` prefix.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Authenticate using email and password |
| GET | `/api/auth/me` | Get current authenticated user |

Protected endpoints require a Bearer access token.

Example header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories` | List active categories |

Category counts include active, rights-verified, non-deleted wallpapers.

### Wallpapers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/wallpapers` | List published wallpapers |
| GET | `/api/wallpapers/{public_id}` | Get public wallpaper details |
| POST | `/api/wallpapers` | Submit a wallpaper (authentication required) |

Wallpaper listing supports:

- `limit`
- `offset`
- `category_id`
- `search`

Example:

```http
GET /api/wallpapers?limit=20&offset=0
```

New wallpaper submissions remain unpublished by default.

### Health Checks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health/live` | Check API process |
| GET | `/api/health/ready` | Check database connectivity |

The readiness endpoint returns a service-unavailable response when the database cannot be reached.

## Testing

Run the complete test suite:

```bash
python -m pytest -v
```

The test suite covers:

- Authentication and registration
- Login and user access
- Authorization dependencies
- Category endpoints
- Health checks
- Image validation
- Wallpaper rights verification
- Password security
- Storage operations
- JWT token validation
- Wallpaper listing and details
- Wallpaper service logic

## Security

- Passwords are stored as secure Argon2 hashes.
- Access tokens are signed using JWT.
- Database credentials and signing keys belong in environment variables.
- CORS uses configured origins.
- User-submitted images are validated.
- Wallpaper rights are checked before public display.
- Error responses avoid exposing internal exception details.
- Supabase service-role credentials must remain private.

## Documentation

Additional technical documentation is available in `docs/`:

- `api-contract.md`
- `architecture.md`
- `database-schema.md`
- `frontend-integration-audit.md`
- `phase2-verification.md`

## Current Implementation Scope

The current backend implements authentication, categories, public wallpaper browsing, wallpaper details and authenticated wallpaper submission.

Collections, favorites, newsletter delivery, a full admin dashboard, and refresh-token session endpoints are not currently implemented as API routes.

Refer to the actual routers and OpenAPI specification for the current implementation.

## License

No open-source license has been specified yet. All rights and permissions for wallpaper artwork remain subject to their respective owners.

---

**Made by Stoicdot**

[GitHub](https://github.com/stoicdot)
