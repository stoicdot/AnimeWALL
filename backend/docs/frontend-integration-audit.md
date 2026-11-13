# AnimeWall Frontend Integration Audit

**Sources inspected:** `index.html`, `styles.css`, `app.js`, `data.js`, `README.md`.  
**Status:** Source audit; no source files modified.

## 1. Actual application type

The supplied project is a vanilla HTML/CSS/JavaScript SPA. `index.html` loads `js/data.js` and `js/app.js`; `app.js` uses an IIFE, global dataset constants and a hash-based router. No React, Vite, JSX or package manifest was included in the supplied files.

The project README describes this expected layout:

```text
animeWEBSITE/
├── index.html
├── css/styles.css
├── js/data.js
├── js/app.js
└── README.md
```

The uploaded individual files appeared at the workspace root because they were uploaded separately. Preserve the source project's intended directory layout.

## 2. Existing views and their backend data

| Existing view/section | Current source | Planned API |
|---|---|---|
| Home featured gallery | `WALLPAPERS_DATA.filter(featured)` | `GET /api/wallpapers?featured=true&page_size=8` |
| Home categories | `CATEGORIES_DATA` | `GET /api/categories` |
| Home trending | `WALLPAPERS_DATA.filter(trending)` | `GET /api/wallpapers?sort=popular&page_size=4` |
| Home collections | `COLLECTIONS_DATA` | `GET /api/collections` |
| Home latest | `WALLPAPERS_DATA.filter(latest)` | `GET /api/wallpapers?sort=latest&page_size=6` |
| Explore | Client-side filtering of static wallpapers | `GET /api/wallpapers` with query params |
| Categories | `CATEGORIES_DATA` | `GET /api/categories` |
| Collections | `COLLECTIONS_DATA` + wallpaper ID arrays | `GET /api/collections` and collection detail |
| Favorites | `localStorage` key `animewall_favorites` | Authenticated `/api/favorites`; keep guest mode local |
| Wallpaper modal | Static wallpaper object | `GET /api/wallpapers/{id}` |
| Download | Fetches `wallpaper.image` regardless of selected resolution | `POST /api/wallpapers/{id}/downloads` with selected variant |
| Newsletter | Displays a success toast without sending a request | Deferred newsletter API after provider/consent decision |
| Profile button | Displays a placeholder toast | Login/profile UI integration required |

## 3. Existing data model compatibility

The supplied `data.js` has 24 wallpaper objects with these properties:

`id`, `title`, `kanji`, `anime`, `artist`, `category`, `collection`, `resolution`, `aspectRatio`, `orientation`, `width`, `height`, `fileSize`, `format`, `featured`, `trending`, `latest`, `rank`, `views`, `downloads`, `likes`, `colors`, `tags`, `description`, `image`, `thumb`.

The API adapter should preserve the UI-facing property names to minimize changes in card/modal rendering. Internal database naming can remain idiomatic (`anime_name`, `artist_name`, `download_count`, `favorite_count`, etc.).

`wallpapers.id` in the API is the stable public identifier. The 24 current identifiers can be preserved for legally cleared imports; new records use a generated opaque identifier.

Categories currently use slugs:

`nature`, `japanese-aesthetic`, `dark`, `minimalist`, `cyberpunk`, `romance`, `action`, `landscape`.

Collections currently use slugs:

`sakura-dreams`, `midnight-tokyo`, `endless-summer`, `quiet-mountains`, `neon-nights`, `dark-aesthetics`.

## 4. Existing interactions to preserve

- Hash routes: `#home`, `#explore`, `#categories`, `#collections`, `#favorites`, `#about`, `#wallpaper/:id`, plus category/collection shortcuts.
- Search command palette and Explore live search.
- Category, anime, resolution and orientation filters.
- Popular, latest, likes and downloads sorting.
- Wallpaper detail modal, related artwork list, color palette copy, share-link copy and keyboard controls.
- Light/dark theme preference.
- Guest favorites localStorage behaviour.

Do not alter visual styles or layout as part of backend work unless a small integration control (login/register, account menu or upload form) is specifically approved.

## 5. Functional gaps found in the current source

1. **No account forms:** the profile control is a placeholder action; no registration/login form exists in the supplied HTML.
2. **Guest-only favorites:** favorites persist only in `localStorage` today.
3. **Download selection not honoured:** the selected resolution is included in the filename, but the current implementation always downloads `wallpaper.image`.
4. **Newsletter is simulated:** the form handler only displays a success toast and resets the form; it does not submit an email to a service.
5. **No submission workflow UI:** no user wallpaper-upload form is present in the supplied HTML.
6. **No admin dashboard UI:** no admin view is present in the supplied HTML. Backend admin APIs can exist independently, but a dashboard requires a later frontend task.
7. **Founder/contact content:** the About content does not identify the founder in the supplied excerpt. The footer currently links to `curator@animewall.gallery`, which conflicts with the founder-provided public contact address. The requested public creator credit and GitHub URL need a minimal content update when frontend editing is approved.
8. **Static placeholder data/assets:** the sample wallpaper records contain URLs and attribution-like strings but no per-image licensing evidence. Do not seed or republish these records as production wallpapers until rights/permission and source attribution are verified.

## 6. Minimal frontend integration strategy

1. Add one small `api.js` module (or equivalent inside the existing app structure) containing `API_BASE_URL`, JSON/error parsing and fetch helpers.
2. Keep `data.js` temporarily as a development fallback, behind a clear environment/config flag. Production should load server data.
3. Add a mapper from backend response fields to the current renderer shape. The mapper preserves `anime`, `artist`, `category`, `image`, `thumb`, `aspectRatio`, `downloads` and `likes`.
4. Load home sections from dedicated API calls and Explore results from a paginated endpoint.
5. Keep theme in localStorage; it is a local visual preference, not a backend resource.
6. Keep unauthenticated favorites in localStorage. When login is introduced, synchronize the guest list and then use the favorites API.
7. Update the download button to request the chosen variant and use the signed URL returned by the API.
8. Add login/register and submission controls only after their visual integration is approved. Do not rebuild the site's header or page layout.

## 7. Rights and data integrity note

The current sample data describes anime titles/artists and references remote images, but the source files do not document copyright permission or licenses. Production import must be gated by verified rights/permission and required attribution. The backend must reject submissions that omit the required license declaration and keep pending uploads private until moderation is complete.
