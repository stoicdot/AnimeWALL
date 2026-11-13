# AnimeWall Database Schema

**Status:** Phase 1 proposal — approval required.  
**Database:** PostgreSQL.  
**ORM:** SQLAlchemy 2.0.

## 1. Shared conventions

- Internal primary keys use PostgreSQL UUIDs.
- All timestamps use `TIMESTAMPTZ` and are written in UTC.
- Tables use `created_at`; mutable records also use `updated_at`.
- Counter columns use non-negative `BIGINT` with a default of zero.
- User-controlled text is length-limited in Pydantic and reinforced with database constraints where useful.
- Public wallpaper `id` maps to `wallpapers.public_id`, not the internal UUID. This permits current public identifiers such as `wall-1` to survive migration while new records receive opaque public IDs.
- Category and collection public identifiers are their unique slugs.

## 2. Entity relationship overview

```text
users 1 ─── N wallpapers
users 1 ─── N favorites N ─── 1 wallpapers
users 1 ─── N collections
collections 1 ─── N collection_items N ─── 1 wallpapers
categories 1 ─── N wallpapers
users 1 ─── N submissions
users 1 ─── N user_sessions
wallpapers 1 ─── N wallpaper_assets
wallpapers 1 ─── N wallpaper_events
```

`collection_items`, `user_sessions`, `wallpaper_assets` and `wallpaper_events` are supporting tables required by the actual frontend behaviours and secure storage/session design. The six original domain models (User, Wallpaper, Category, Favorite, Collection, Submission) remain the core entities.

## 3. `users`

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK, generated server-side |
| username | VARCHAR(32) | NOT NULL, UNIQUE, normalized lowercase |
| display_name | VARCHAR(80) | Nullable |
| email | VARCHAR(255) | NOT NULL, UNIQUE, normalized lowercase |
| password_hash | VARCHAR(255) | NOT NULL; Argon2id encoded hash only |
| role | VARCHAR(16) | NOT NULL, default `user`, allowed `user`/`admin` |
| is_active | BOOLEAN | NOT NULL, default true |
| email_verified_at | TIMESTAMPTZ | Nullable; do not treat email as verified until a verification flow exists |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, updated on change |

**Indexes/constraints:** unique username, unique email, role index only if admin queries justify it. The first admin must be provisioned via a controlled CLI/bootstrap operation; never hardcode admin credentials into source code or migrations.

## 4. `categories`

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK |
| slug | VARCHAR(64) | NOT NULL, UNIQUE; examples `nature`, `japanese-aesthetic` |
| name | VARCHAR(80) | NOT NULL |
| kanji | VARCHAR(32) | Nullable |
| romaji | VARCHAR(80) | Nullable |
| description | TEXT | Nullable |
| cover_path | VARCHAR(500) | Nullable; Supabase object key, not a hardcoded URL |
| is_active | BOOLEAN | NOT NULL, default true |
| sort_order | INTEGER | NOT NULL, default 0 |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:** unique slug; `(is_active, sort_order)` for public category listing.

## 5. `wallpapers`

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK |
| public_id | VARCHAR(64) | NOT NULL, UNIQUE; returned to the frontend as `id` |
| title | VARCHAR(160) | NOT NULL |
| description | TEXT | Nullable |
| kanji | VARCHAR(32) | Nullable editorial accent |
| anime_name | VARCHAR(120) | NOT NULL; frontend alias `anime` |
| artist_name | VARCHAR(160) | Nullable; frontend alias `artist` |
| category_id | UUID | NOT NULL FK → categories.id |
| created_by | UUID | NOT NULL FK → users.id |
| width | INTEGER | NOT NULL, > 0 |
| height | INTEGER | NOT NULL, > 0 |
| aspect_ratio | NUMERIC(10,5) | NOT NULL, > 0; calculated from dimensions |
| orientation | VARCHAR(16) | NOT NULL; `landscape`, `portrait`, `ultrawide`, `square` |
| license_name | VARCHAR(120) | NOT NULL; verified license/permission label |
| license_url | TEXT | Nullable |
| attribution_text | TEXT | Nullable; required when license requires attribution |
| file_format | VARCHAR(16) | NOT NULL; normalized, e.g. `webp` |
| file_size_bytes | BIGINT | NOT NULL, > 0 |
| view_count | BIGINT | NOT NULL, default 0, >= 0 |
| download_count | BIGINT | NOT NULL, default 0, >= 0 |
| favorite_count | BIGINT | NOT NULL, default 0, >= 0; transactionally maintained |
| is_featured | BOOLEAN | NOT NULL, default false |
| is_active | BOOLEAN | NOT NULL, default true |
| published_at | TIMESTAMPTZ | Nullable until approved/published |
| deleted_at | TIMESTAMPTZ | Nullable soft-delete timestamp |
| storage_cleanup_pending | BOOLEAN | NOT NULL, default false |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:**

- Unique `public_id`.
- `(category_id, is_active, published_at DESC)`.
- `(is_active, published_at DESC)` for latest uploads.
- `(is_active, favorite_count DESC)` for most liked.
- `(is_active, download_count DESC)` for lifetime downloads.
- `(orientation, is_active)`.
- B-tree indexes for common exact filters; add trigram/full-text indexes only after search requirements and PostgreSQL extension permissions are verified.

**Important:** `trending`, `latest`, `rank`, `resolution`, `fileSize`, `image` and `thumb` are API presentation fields, not all stored as independent columns. `resolution` is derived from width/height and a named preset; `fileSize` is formatted from `file_size_bytes`; `image`/`thumb` URLs are resolved from `wallpaper_assets`; `trending`/`rank` are derived from recent events; `latest` is computed for relevant listing responses.

## 6. `wallpaper_assets`

Stores object metadata for each resolution/role. Image bytes remain in Supabase Storage.

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK |
| wallpaper_id | UUID | NOT NULL FK → wallpapers.id, ON DELETE RESTRICT |
| variant | VARCHAR(20) | NOT NULL; `thumbnail`, `preview`, `original`, `2k`, `1080p`, `mobile` |
| bucket | VARCHAR(80) | NOT NULL |
| object_path | VARCHAR(500) | NOT NULL, UNIQUE |
| width | INTEGER | NOT NULL, > 0 |
| height | INTEGER | NOT NULL, > 0 |
| content_type | VARCHAR(100) | NOT NULL |
| size_bytes | BIGINT | NOT NULL, > 0 |
| checksum_sha256 | CHAR(64) | Nullable |
| created_at | TIMESTAMPTZ | NOT NULL |

**Constraints/indexes:** unique `(wallpaper_id, variant)`; unique object path; index wallpaper_id. `thumbnail`/`preview` assets can use the public-preview bucket. Download variants use the private-originals bucket and signed URLs.

## 7. `favorites`

| Column | PostgreSQL type | Rules |
|---|---|---|
| user_id | UUID | PK part, FK → users.id, ON DELETE CASCADE |
| wallpaper_id | UUID | PK part, FK → wallpapers.id, ON DELETE CASCADE |
| created_at | TIMESTAMPTZ | NOT NULL |

Composite primary key `(user_id, wallpaper_id)` prevents duplicate favorites. Add index `(user_id, created_at DESC)` for the Favorites page and an index on wallpaper_id for counter maintenance. Update `wallpapers.favorite_count` in the same transaction as favorite insert/delete.

## 8. `collections`

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK |
| slug | VARCHAR(80) | NOT NULL, UNIQUE |
| title | VARCHAR(120) | NOT NULL |
| kanji | VARCHAR(48) | Nullable |
| subtitle | VARCHAR(180) | Nullable |
| description | TEXT | Nullable |
| curator_note | TEXT | Nullable |
| cover_path | VARCHAR(500) | Nullable storage object key |
| is_published | BOOLEAN | NOT NULL, default false |
| sort_order | INTEGER | NOT NULL, default 0 |
| created_by | UUID | Nullable FK → users.id |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:** unique slug; `(is_published, sort_order)`.

## 9. `collection_items`

Join table for a many-to-many relationship between collections and wallpapers.

| Column | PostgreSQL type | Rules |
|---|---|---|
| collection_id | UUID | PK part, FK → collections.id, ON DELETE CASCADE |
| wallpaper_id | UUID | PK part, FK → wallpapers.id, ON DELETE CASCADE |
| position | INTEGER | NOT NULL, default 0 |
| added_at | TIMESTAMPTZ | NOT NULL |

Composite primary key prevents duplicates. Add `(collection_id, position)` index for ordered collection retrieval and an index on wallpaper_id for reverse lookup.

## 10. `submissions`

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK |
| submitted_by | UUID | NOT NULL FK → users.id |
| title | VARCHAR(160) | NOT NULL |
| description | TEXT | Nullable |
| anime_name | VARCHAR(120) | NOT NULL |
| artist_name | VARCHAR(160) | Nullable |
| category_id | UUID | NOT NULL FK → categories.id |
| license_name | VARCHAR(120) | NOT NULL |
| license_url | TEXT | Nullable |
| attribution_text | TEXT | Nullable |
| source_bucket | VARCHAR(80) | NOT NULL |
| source_object_path | VARCHAR(500) | NOT NULL, UNIQUE |
| thumbnail_object_path | VARCHAR(500) | Nullable, UNIQUE |
| width | INTEGER | NOT NULL, > 0 |
| height | INTEGER | NOT NULL, > 0 |
| content_type | VARCHAR(100) | NOT NULL |
| size_bytes | BIGINT | NOT NULL, > 0 |
| status | VARCHAR(16) | NOT NULL, default `pending`; `pending`/`approved`/`rejected` |
| reviewed_by | UUID | Nullable FK → users.id |
| reviewed_at | TIMESTAMPTZ | Nullable |
| reviewer_note | TEXT | Nullable |
| approved_wallpaper_id | UUID | Nullable FK → wallpapers.id |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:** `(status, created_at)` for moderation queue; submitted_by; reviewed_by. Approval is transactional in PostgreSQL. Storage copy/move is idempotent and failures must leave a retryable state rather than creating a broken published record.

## 11. `user_sessions`

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK; JWT `sid` |
| user_id | UUID | NOT NULL FK → users.id, ON DELETE CASCADE |
| refresh_token_hash | CHAR(64) | NOT NULL, UNIQUE |
| expires_at | TIMESTAMPTZ | NOT NULL |
| last_used_at | TIMESTAMPTZ | Nullable |
| revoked_at | TIMESTAMPTZ | Nullable |
| created_at | TIMESTAMPTZ | NOT NULL |
| user_agent | VARCHAR(500) | Nullable; no raw access/refresh tokens |

Index `(user_id, revoked_at, expires_at)` for session administration. Store only the refresh-token hash, never the raw refresh token.

## 12. `wallpaper_events`

Supports recent popularity/trending calculations and download analytics.

| Column | PostgreSQL type | Rules |
|---|---|---|
| id | UUID | PK |
| wallpaper_id | UUID | NOT NULL FK → wallpapers.id, ON DELETE CASCADE |
| user_id | UUID | Nullable FK → users.id, ON DELETE SET NULL |
| event_type | VARCHAR(16) | NOT NULL; `view` or `download` |
| created_at | TIMESTAMPTZ | NOT NULL |

Indexes: `(event_type, created_at DESC, wallpaper_id)` and `(wallpaper_id, created_at DESC)`. Avoid storing raw IP addresses. Add retention/aggregation once traffic volume is known. Increment lifetime counters atomically in the same transaction as the event insertion.

## 13. Optional `newsletter_subscriptions`

The current UI contains a newsletter form, but no email delivery provider has been selected. The database may store `email` (unique, normalized), `status` (`pending_confirmation`, `active`, `unsubscribed`), `created_at`, `confirmed_at` and `unsubscribed_at`. Sending confirmation and campaign email is out of scope until an email provider and consent workflow are approved.

## 14. Delete and referential-integrity policy

- Users: deactivate accounts by default; cascade session/favorite cleanup only under an approved account-deletion flow.
- Wallpapers: soft delete first; do not cascade-delete object storage implicitly from a database FK.
- Favorites and collection memberships: cascade when the referenced user/wallpaper/collection is permanently removed.
- Categories: do not delete while active wallpapers reference them; deactivate or reassign first.
- Collections: remove memberships on permanent deletion.
- Submissions: preserve moderation history; do not hard-delete as part of normal reject flow.

## 15. Migration and seed policy

- Create tables and constraints through Alembic only.
- Seed category/collection metadata with idempotent migrations or a repeatable seed command.
- Do not automatically import the current 24 wallpaper URLs as production content. The supplied dataset does not contain per-image licensing evidence. Import wallpapers only after the owner verifies rights/permissions and storage assets are uploaded.
- Preserve `wall-1`…`wall-24` as public IDs only for records that are legitimately imported.
