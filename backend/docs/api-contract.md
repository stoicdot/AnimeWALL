# AnimeWall REST API Contract

**Base path:** `/api`  
**Status:** Phase 1 proposal — stable contracts to be implemented after approval.  
**Content type:** `application/json`, except endpoints documented as multipart.

## 1. Common response format

### List response

```json
{
  "data": [
    {
      "id": "wall-1",
      "title": "Twilight Over Shinjuku Crossing",
      "anime": "Your Name",
      "artist": "Verified artist credit",
      "category": "Japanese Aesthetic",
      "categoryId": "japanese-aesthetic",
      "collection": "sakura-dreams",
      "resolution": "3840 x 2160 (4K UHD)",
      "aspectRatio": "16:9",
      "orientation": "Landscape",
      "width": 3840,
      "height": 2160,
      "fileSize": "8.6 MB",
      "format": "WebP",
      "featured": true,
      "trending": false,
      "latest": true,
      "rank": null,
      "views": 0,
      "downloads": 0,
      "likes": 0,
      "colors": ["#2C3647", "#D48B70"],
      "tags": ["twilight", "cityscape"],
      "description": "Verified description.",
      "image": "https://storage-preview-url.example/preview.webp",
      "thumb": "https://storage-thumbnail-url.example/thumb.webp",
      "assets": {
        "original": {"available": true},
        "2k": {"available": false},
        "1080p": {"available": true},
        "mobile": {"available": false}
      }
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 24,
    "total": 24,
    "pages": 1
  }
}
```

The example values illustrate field names only; they are not real asset URLs or claims that any current sample artwork is cleared for publication. Actual URLs must come from configured Supabase Storage objects.

### Single-resource response

```json
{
  "data": {
    "id": "wall-1",
    "title": "Wallpaper title"
  }
}
```

### Error response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "details": {"page_size": "Must be between 1 and 100."},
    "request_id": "request-id"
  }
}
```

Never return Python tracebacks, SQL text, credentials, storage service-role keys or token values in error responses.

## 2. Public wallpaper endpoints

### `GET /api/wallpapers`

**Authentication:** Not required.  
**Purpose:** Home, Explore, latest, trending and filtered gallery data.

| Query parameter | Type | Meaning |
|---|---|---|
| q | string | Search title, anime name, artist, description and tags |
| category | string | Category slug, e.g. `nature` |
| collection | string | Collection slug, e.g. `sakura-dreams` |
| anime | string | Exact or normalized anime title filter |
| resolution | string | Existing UI preset label or normalized preset (`4k`, `2k`, `1080p`, `mobile`, `ultrawide`) |
| orientation | string | `landscape`, `portrait`, `ultrawide`, `square` |
| sort | string | `popular`, `latest`, `likes`, `downloads`; default `popular` |
| featured | boolean | Optional featured-only filter |
| page | integer | Default 1 |
| page_size | integer | Default 24; maximum 100 |

**Response:** `200 OK`, list response with the frontend-compatible wallpaper fields. `category` is the display name and `categoryId` is the category slug. `image` and `thumb` are resolved preview URLs.

Example:

```http
GET /api/wallpapers?q=shinkai&category=landscape&orientation=landscape&sort=popular&page=1&page_size=24
```

The existing Explore controls map to these query parameters. The frontend adapter converts the selected dropdown values to normalized query values if required.

### `GET /api/wallpapers/{wallpaper_id}`

**Authentication:** Not required.  
**Response:** `200 OK` with complete detail data, palette, license/attribution metadata and available asset variants; `404 NOT_FOUND` if not public or not found.

### `POST /api/wallpapers/{wallpaper_id}/downloads`

**Authentication:** Not required for the initial public-download policy; rate-limited.  
**Request:**

```json
{"variant": "original"}
```

Allowed variants: `original`, `2k`, `1080p`, `mobile`. The selected variant must exist and be available.

**Response:** `200 OK`

```json
{
  "data": {
    "download_url": "short-lived-signed-storage-url",
    "expires_at": "2026-11-12T15:00:00Z",
    "file_name": "AnimeWall_Twilight_Original.webp",
    "variant": "original"
  }
}
```

This endpoint records a download request when it issues the signed URL; it cannot prove that the browser completed saving the file. The frontend must use the returned URL, not assume the currently displayed preview equals the selected resolution.

## 3. Categories

### `GET /api/categories`

**Authentication:** Not required.  
**Response:** `200 OK`

```json
{
  "data": [
    {
      "id": "nature",
      "name": "Nature",
      "kanji": "自然",
      "romaji": "Shizen",
      "description": "Category description.",
      "count": 12,
      "cover": "storage-preview-url"
    }
  ]
}
```

`count` is calculated from active, published wallpapers. `cover` is a real URL derived from the stored `cover_path`.

### `GET /api/categories/{slug}`

**Authentication:** Not required. Returns category details and optionally the first page of matching wallpapers. `404` for unknown/inactive slug.

## 4. Collections

### `GET /api/collections`

**Authentication:** Not required. Returns published collections ordered by `sort_order`. Response fields preserve the current UI: `id` (slug), `title`, `kanji`, `subtitle`, `description`, `curatorNote`, `cover`, `wallpaperIds` (public wallpaper IDs) and `count`.

### `GET /api/collections/{slug}`

**Authentication:** Not required. Returns one published collection and its ordered wallpaper list.

## 5. Authentication

### `POST /api/auth/register`

**Authentication:** Not required; rate-limited.  
**Request:**

```json
{
  "username": "stoicdot",
  "email": "user@example.com",
  "password": "a-long-unique-password"
}
```

**Response:** `201 Created`; creates an Argon2id password hash, user record and refresh session. Returns an access token in JSON and sets the refresh token as a Secure, HttpOnly cookie. Registration does not create an admin account.

### `POST /api/auth/login`

**Authentication:** Not required; rate-limited.  
**Request:**

```json
{"identifier": "stoicdot", "password": "a-long-unique-password"}
```

`identifier` accepts username or email. **Response:** `200 OK` with access token, token type, expiry and minimal user object; sets refresh cookie.

### `POST /api/auth/refresh`

**Authentication:** Refresh cookie plus CSRF protection required. Rotates the refresh token and returns a new access token. Reuse of a rotated token revokes the affected session.

### `POST /api/auth/logout`

**Authentication:** Current session required. Revokes the current refresh session and clears cookies. `204 No Content` on success.

### `POST /api/auth/logout-all`

**Authentication:** Current user required. Revokes all active sessions for that user. `204 No Content`.

### `GET /api/auth/me`

**Authentication:** Bearer access token required. Returns:

```json
{
  "data": {
    "id": "user-uuid",
    "username": "stoicdot",
    "display_name": null,
    "email": "user@example.com",
    "role": "user"
  }
}
```

## 6. Favorites

### `GET /api/favorites`

**Authentication:** Required. Returns the current user's favorite wallpapers using the same wallpaper response fields and pagination envelope.

### `POST /api/favorites`

**Authentication:** Required.  
**Request:** `{"wallpaper_id": "wall-1"}`  
**Response:** `201 Created` for a new favorite; repeated requests are idempotent and return the existing favorite rather than creating duplicates.

### `DELETE /api/favorites/{wallpaper_id}`

**Authentication:** Required. Removes the current user's favorite. `204 No Content`; repeated deletion may return `204` to keep the operation idempotent.

The browser's current guest favorites stay in localStorage. After successful login, a future frontend adapter can call a sync endpoint or submit the saved public IDs to merge them into the account; that sync endpoint is not part of the first public contract and must be separately approved.

## 7. Submissions

### `POST /api/submissions`

**Authentication:** Required.  
**Content type:** `multipart/form-data`.

Fields: `title`, `description` (optional), `anime_name`, `artist_name` (optional), `category_slug`, `license_name`, `license_url` (optional), `attribution_text` (optional) and `file`.

**Response:** `202 Accepted` with submission ID and status `pending`. The image stays in private staging storage until reviewed. The API rejects unsupported file formats, oversized files, invalid image payloads and missing license information.

### `GET /api/submissions/me`

**Authentication:** Required. Returns the current user's submissions and statuses.

## 8. Admin endpoints

All admin endpoints require a valid authenticated user with `role=admin`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/dashboard` | User, wallpaper, download and pending-submission totals |
| GET | `/api/admin/submissions` | Paginated moderation queue; filter by status |
| PATCH | `/api/admin/submissions/{submission_id}` | Approve or reject with reviewer note |
| POST | `/api/admin/wallpapers` | Create/publish a wallpaper (multipart or validated metadata + upload flow) |
| PATCH | `/api/admin/wallpapers/{wallpaper_id}` | Update wallpaper metadata/active status |
| DELETE | `/api/admin/wallpapers/{wallpaper_id}` | Soft-delete and attempt safe storage cleanup |
| POST | `/api/admin/categories` | Create category |
| PATCH | `/api/admin/categories/{slug}` | Update category |
| DELETE | `/api/admin/categories/{slug}` | Deactivate/delete only when referential rules allow |

### `PATCH /api/admin/submissions/{submission_id}` request

```json
{
  "status": "approved",
  "reviewer_note": "License information verified."
}
```

`status` must be `approved` or `rejected`. Approval creates a published Wallpaper and its asset records. Rejection retains the submission record and reviewer note. A submission may not be approved without verified licensing/permission evidence.

### `GET /api/admin/dashboard` response

```json
{
  "data": {
    "total_users": 0,
    "total_wallpapers": 0,
    "total_downloads": 0,
    "pending_submissions": 0
  }
}
```

Numbers are live database aggregates, not hardcoded display values.

## 9. Newsletter

The current HTML has a newsletter form but no delivery provider is configured. Proposed `POST /api/newsletter` accepts `{"email":"..."}` and records a pending-consent subscription only after the project owner approves the provider and consent flow. Do not show a success state implying email delivery until the backend confirms the subscription workflow. Campaign delivery, confirmation email and unsubscribe links depend on the provider decision.

## 10. HTTP status and error map

| Status | Use |
|---|---|
| 200 | Successful GET/PATCH or idempotent operation |
| 201 | New resource created |
| 202 | Submission accepted for moderation |
| 204 | Successful logout/delete with no response body |
| 400 | Invalid state transition or malformed request |
| 401 | Missing, invalid, expired or revoked authentication |
| 403 | Authenticated but not permitted |
| 404 | Resource not found or not visible publicly |
| 409 | Duplicate username/email or conflicting resource state |
| 413 | Upload too large |
| 415 | Unsupported media type |
| 422 | Schema/field validation error |
| 429 | Rate limit exceeded |
| 500 | Generic unexpected server error |
| 503 | Temporary database/storage dependency failure |

## 11. OpenAPI

FastAPI will publish Swagger UI at `/docs`, ReDoc at `/redoc` and the OpenAPI JSON at `/openapi.json` in development. Production documentation exposure can be restricted by environment configuration if desired.
