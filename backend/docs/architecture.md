# AnimeWall Backend Architecture

**Project:** AnimeWall  
**Tagline:** Find Your Anime Aesthetic.  
**Design identity:** Japanese-inspired minimalism; English is the primary product language.  
**Document status:** Phase 1 proposal — requires founder approval before implementation.

## 1. Current frontend baseline

The inspected source files are a vanilla HTML/CSS/JavaScript single-page application, not a React + Vite application. The supplied implementation contains:

- Six views: Home, Explore, Categories, Collections, Favorites and About.
- Eight category records, six collection records and 24 sample wallpaper records (`wall-1` through `wall-24`).
- Client-side search and filters for anime, resolution and orientation.
- Four sort modes: popular, latest, likes and downloads.
- A hash-based wallpaper detail modal, favorite controls, direct image download, command palette and theme preference.
- A newsletter form and a profile button, neither of which currently calls a backend.

The HTML references `css/styles.css`, `js/data.js` and `js/app.js`; the README describes that same nested layout. The individual files supplied to this workspace were flattened into the upload root. Preserve the original project layout when integrating; do not infer that the original project itself is flattened.

## 2. Architecture decision

Use a **modular monolith**: one FastAPI application with independent feature modules. Do not introduce microservices, Redis, Celery or a frontend rewrite for the initial release.

Reasons:

1. One deployment and one API contract keep the initial project operationally simple.
2. Routers, services and data models remain separated, so modules can be extracted later if there is a proven scaling need.
3. PostgreSQL remains the source of truth for user, wallpaper, category, favorite, collection and submission metadata.
4. Supabase Storage stores image objects; PostgreSQL stores object keys and metadata, never image bytes.

## 3. System context

```text
Browser
  └── Existing AnimeWall HTML/CSS/JavaScript SPA
        └── HTTPS JSON requests (/api/*)
              └── Nginx reverse proxy
                    └── Uvicorn / FastAPI
                          ├── Routers and request schemas
                          ├── Authentication / authorization
                          ├── Feature services
                          ├── SQLAlchemy 2.0 data layer
                          │     └── PostgreSQL
                          └── Storage service
                                └── Supabase Storage
```

Deployment target: Ubuntu on AWS EC2, Nginx in front of Uvicorn. PostgreSQL should be a separately managed PostgreSQL service where possible, rather than sharing the application EC2 instance's disk and failure domain. The database hosting provider is not selected in this design.

## 4. Backend technology choices

| Concern | Decision |
|---|---|
| Runtime | Python 3.12+ |
| HTTP API | FastAPI |
| ASGI server | Uvicorn |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL |
| Database access | Async SQLAlchemy sessions with an async PostgreSQL driver |
| Password hashing | Argon2id through a maintained password-hashing package |
| JWT | Short-lived signed access JWTs |
| Refresh sessions | Random opaque refresh token, stored only as a hash in PostgreSQL; rotated on refresh |
| Image processing | Pillow for image verification, dimensions and thumbnail generation |
| Storage | Supabase Storage through a backend-only storage service |
| HTTP client | `httpx` for async storage/API operations where needed |
| Testing | pytest, pytest-asyncio and HTTPX test client |

Pin and test compatible dependency versions when Phase 2 starts. Do not install dependencies based only on unpinned `latest` versions.

## 5. Application modules

```text
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── middleware.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── utils/
├── alembic/
├── tests/
├── docs/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Layer responsibilities

- **Routers:** HTTP path, method, status code, dependencies and response selection. No business rules or raw SQL.
- **Schemas:** Validate incoming data and serialize stable API responses.
- **Services:** Business rules, query construction, moderation workflow, counter updates and storage orchestration.
- **Models:** SQLAlchemy tables, relationships and database constraints.
- **Database:** Async engine, session factory and transaction scope.
- **Core:** Configuration, JWT/password utilities, exception mapping and request middleware.
- **Dependencies:** Database session, current user and admin authorization.
- **Utils:** File signatures, image checks and small reusable primitives.

## 6. API conventions

- API prefix: `/api` (preserves the endpoint style already proposed for AnimeWall).
- Request and response bodies: JSON except multipart image uploads.
- Content encoding: UTF-8.
- Datetimes: ISO 8601 UTC strings.
- Internal database primary keys: UUID.
- Public wallpaper identifier: stable string `public_id`. Existing IDs such as `wall-1` can be imported unchanged; new records may use UUID strings. The frontend continues to consume this public identifier as `wallpaper.id`.
- Public category and collection identifiers: stable slugs, for example `nature` and `sakura-dreams`.
- Pagination: `page` and `page_size`, with a maximum page size of 100.
- Consistent success envelope: `{"data": ..., "meta": ...}` when metadata is useful.
- Consistent error envelope: `{"error":{"code":"...","message":"...","details":null,"request_id":"..."}}`.

## 7. Authentication and session design

1. Store passwords only as Argon2id hashes. Never log passwords or tokens.
2. Issue short-lived access JWTs (proposed lifetime: 15 minutes) containing `sub` (user UUID), `sid` (session UUID), `iat`, `exp` and `jti`.
3. Return the access token in the login/refresh JSON response. Keep it in frontend memory rather than persistent localStorage.
4. Issue a high-entropy opaque refresh token in an `HttpOnly`, `Secure` cookie. Store only its SHA-256 hash in `user_sessions`.
5. Rotate the refresh token on every refresh. Reuse of a previously rotated token revokes that session.
6. Logout revokes the current session and clears the cookie. A separate logout-all operation can revoke every session for the account.
7. Check session revocation and user active status during access-token authentication so logout can invalidate the current session immediately. This adds a small indexed database lookup per authenticated request; revisit only after measuring load.
8. Use role-based authorization (`user`, `admin`) on the server. Hiding admin UI is not authorization.
9. Because cookie-based refresh is used, configure allowed frontend origins, credentialed CORS and CSRF protection for refresh/logout. Never use wildcard CORS with credentials.

## 8. Image storage design

Use separate Supabase buckets:

- `wallpaper-previews` — public read for small preview/thumbnail objects that are intentionally discoverable.
- `wallpaper-originals` — private read; downloads are issued through short-lived signed URLs.
- `wallpaper-submissions` — private staging area for pending user submissions.

The backend uses the Supabase service-role credential. It must exist only in backend environment variables and must never be shipped to the browser.

Upload pipeline:

1. Authenticate and authorize the uploader.
2. Enforce request-size limits at Nginx and application level.
3. Allow only approved raster formats initially: JPEG, PNG and WebP.
4. Verify file signature and successfully decode the image; do not trust the browser-provided MIME type or filename.
5. Enforce a proposed 15 MiB maximum per uploaded file and a pixel-count limit to mitigate decompression bombs.
6. Re-encode/sanitize images and remove unneeded metadata such as EXIF location data.
7. Generate unique object keys; never use a user-provided filename as the storage key.
8. Generate a thumbnail and store dimensions, MIME type, byte size and object key in PostgreSQL.
9. Return API-generated preview URLs; create signed download URLs only when requested.

A wallpaper delete is a two-resource operation (PostgreSQL + Storage). Use a safe cleanup state: mark the record inactive/deleted, attempt idempotent object deletion, and retain `storage_cleanup_pending=true` if Storage deletion fails. Provide an admin retry path. Do not claim a successful storage deletion when it failed.

## 9. Search, filtering and popularity

Supported filters reflect the existing Explore page:

- Free-text query across title, anime name, artist and description/tags.
- Category slug.
- Anime name.
- Resolution preset or dimensions.
- Orientation: `landscape`, `portrait`, `ultrawide`, `square`.
- Collection slug.
- Featured state.

Sorting:

- `popular`: popularity derived from download events in the preceding seven days (with a documented deterministic tie-breaker).
- `latest`: newest published records first.
- `likes`: highest favorite count first.
- `downloads`: highest lifetime download count first.

The existing `trending` and `latest` Boolean flags and `rank` are presentation conveniences in the static dataset, not authoritative database fields. Compute them for the API response instead of maintaining stale flags.

## 10. Security baseline

- Secrets only in environment variables; `.env` is ignored by Git.
- Production uses HTTPS.
- Exact-origin CORS allowlist.
- Argon2id password hashes and short-lived JWT access tokens.
- Refresh-token rotation and revocation.
- Admin checks on every admin endpoint.
- Pydantic validation and SQLAlchemy parameterized queries.
- Upload size, format, signature and decoded-image validation.
- Rate-limit registration, login, refresh, downloads and upload endpoints. Use Nginx limits initially; do not rely on per-process in-memory rate counters in a multi-worker deployment.
- Generic public errors; detailed tracebacks only in server logs with request IDs.
- No service-role key, DB password, JWT secret or refresh token in frontend code or Git.

## 11. Deferred decisions (not silently assumed)

- PostgreSQL hosting provider and production connection URL.
- Frontend production origin/domain and exact CORS allowlist.
- Email delivery provider and double-opt-in workflow for the newsletter.
- Whether guests may download every resolution or only previews.
- The licensing policy and evidence required before a submission can be approved.
- Whether the separate React + Vite frontend mentioned in the earlier project brief exists. The only current source provided is vanilla HTML/CSS/JavaScript.

## 12. Approval gate

No backend implementation or destructive frontend edits should begin until the founder approves this architecture and the companion database/API documents. After approval, Phase 2 begins with the backend skeleton, settings, database connectivity and first Alembic migration.
