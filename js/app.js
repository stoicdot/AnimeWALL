/**
 * AnimeWall — Core Frontend Application Logic
 * Japanese Minimalist & Editorial Wallpaper Platform
 */

(function () {
  'use strict';

  // State Management
  const AppState = {
    currentView: 'home',
    currentWallpaperId: null,
    searchQuery: '',
    selectedCategory: 'all',
    selectedAnime: 'All Anime',
    selectedResolution: 'All Resolutions',
    selectedOrientation: 'All',
    selectedSort: 'popular',
    favorites: new Set(),
    theme: 'light',
    activeModalIndex: -1
  };

  // DOM Elements Cache
  const DOM = {
    // Header & Nav
    navLinks: document.querySelectorAll('.nav-link, .mobile-nav-link'),
    mobileDrawer: document.getElementById('mobile-drawer'),
    mobileToggleBtn: document.getElementById('mobile-toggle-btn'),
    navFavCount: document.getElementById('nav-fav-count'),
    themeToggleBtn: document.getElementById('theme-toggle-btn'),
    themeSunIcon: document.getElementById('theme-sun-icon'),
    themeMoonIcon: document.getElementById('theme-moon-icon'),
    searchOpenBtn: document.getElementById('search-open-btn'),
    userProfileBtn: document.getElementById('user-profile-btn'),

    // Views
    views: {
      home: document.getElementById('home-view'),
      explore: document.getElementById('explore-view'),
      categories: document.getElementById('categories-view'),
      collections: document.getElementById('collections-view'),
      favorites: document.getElementById('favorites-view'),
      about: document.getElementById('about-view')
    },

    // Homepage Containers
    homeFeaturedGallery: document.getElementById('home-featured-gallery'),
    homeCategoriesGrid: document.getElementById('home-categories-grid'),
    homeTrendingGrid: document.getElementById('home-trending-grid'),
    homeCollectionsGrid: document.getElementById('home-collections-grid'),
    homeLatestGallery: document.getElementById('home-latest-gallery'),

    // Explore Page Elements
    exploreSearchInput: document.getElementById('explore-search-input'),
    exploreSearchClear: document.getElementById('explore-search-clear'),
    exploreCategoryPills: document.getElementById('explore-category-pills'),
    filterAnimeSelect: document.getElementById('filter-anime-select'),
    filterResolutionSelect: document.getElementById('filter-resolution-select'),
    filterOrientationSelect: document.getElementById('filter-orientation-select'),
    filterSortSelect: document.getElementById('filter-sort-select'),
    activeFiltersBar: document.getElementById('active-filters-bar'),
    activeTagsList: document.getElementById('active-tags-list'),
    activeResultsCounter: document.getElementById('active-results-counter'),
    clearAllFiltersBtn: document.getElementById('clear-all-filters-btn'),
    exploreMasonryGallery: document.getElementById('explore-masonry-gallery'),
    exploreEmptyState: document.getElementById('explore-empty-state'),

    // Full Categories & Collections
    fullCategoriesGrid: document.getElementById('full-categories-grid'),
    fullCollectionsGrid: document.getElementById('full-collections-grid'),

    // Favorites Page
    favoritesMasonryGallery: document.getElementById('favorites-masonry-gallery'),
    favoritesEmptyState: document.getElementById('favorites-empty-state'),
    favStatusSubtitle: document.getElementById('fav-status-subtitle'),
    favDownloadAllBtn: document.getElementById('fav-download-all-btn'),
    favClearAllBtn: document.getElementById('fav-clear-all-btn'),

    // Wallpaper Details Modal
    modal: document.getElementById('wallpaper-detail-modal'),
    modalCloseBtn: document.getElementById('modal-close-btn'),
    modalBreadcrumbCategory: document.getElementById('modal-breadcrumb-category'),
    modalBreadcrumbTitle: document.getElementById('modal-breadcrumb-title'),
    modalPreviewImg: document.getElementById('modal-preview-img'),
    modalZoomBtn: document.getElementById('modal-zoom-btn'),
    modalCategoryBadge: document.getElementById('modal-category-badge'),
    modalKanjiStamp: document.getElementById('modal-kanji-stamp'),
    modalWallpaperTitle: document.getElementById('modal-wallpaper-title'),
    modalAnimeTitle: document.getElementById('modal-anime-title'),
    modalDescText: document.getElementById('modal-desc-text'),
    modalSpecRes: document.getElementById('modal-spec-res'),
    modalSpecRatio: document.getElementById('modal-spec-ratio'),
    modalSpecArtist: document.getElementById('modal-spec-artist'),
    modalSpecFormat: document.getElementById('modal-spec-format'),
    modalPaletteSwatches: document.getElementById('modal-palette-swatches'),
    modalDownloadResSelect: document.getElementById('modal-download-res-select'),
    modalDownloadBtn: document.getElementById('modal-download-btn'),
    modalFavToggleBtn: document.getElementById('modal-fav-toggle-btn'),
    modalFavText: document.getElementById('modal-fav-text'),
    modalShareBtn: document.getElementById('modal-share-btn'),
    modalRelatedGrid: document.getElementById('modal-related-grid'),

    // Command Palette Modal
    commandPaletteModal: document.getElementById('command-palette-modal'),
    commandPaletteInput: document.getElementById('command-palette-input'),
    commandResultsList: document.getElementById('command-results-list'),

    // Toast Container
    toastContainer: document.getElementById('toast-container')
  };

  // ========================================================================
  // Initialization & Storage Sync
  // ========================================================================
  function initApp() {
    loadStoredPreferences();
    setupDropdownFilters();
    renderCategoryPills();
    renderAllViews();
    setupEventListeners();
    handleRoute();
  }

  function loadStoredPreferences() {
    // Favorites
    try {
      const savedFavs = localStorage.getItem('animewall_favorites');
      if (savedFavs) {
        AppState.favorites = new Set(JSON.parse(savedFavs));
      }
    } catch (e) {
      console.warn('LocalStorage not accessible', e);
    }
    updateNavFavoritesBadge();

    // Theme
    try {
      const savedTheme = localStorage.getItem('animewall_theme') || 'light';
      setTheme(savedTheme);
    } catch (e) {
      setTheme('light');
    }
  }

  function saveStoredPreferences() {
    try {
      localStorage.setItem('animewall_favorites', JSON.stringify([...AppState.favorites]));
    } catch (e) {}
  }

  // ========================================================================
  // Theme Toggle (Light & Sumi Ink Dark)
  // ========================================================================
  function setTheme(theme) {
    AppState.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('animewall_theme', theme);
    } catch (e) {}

    if (theme === 'dark') {
      DOM.themeSunIcon.style.display = 'none';
      DOM.themeMoonIcon.style.display = 'block';
      DOM.themeToggleBtn.setAttribute('title', 'Switch to Washi Light Theme');
    } else {
      DOM.themeSunIcon.style.display = 'block';
      DOM.themeMoonIcon.style.display = 'none';
      DOM.themeToggleBtn.setAttribute('title', 'Switch to Sumi Night Theme');
    }
  }

  function toggleTheme() {
    const nextTheme = AppState.theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    showToast(nextTheme === 'dark' ? 'Sumi Night Theme enabled' : 'Washi Light Theme enabled', 'info');
  }

  // ========================================================================
  // Routing Engine (SPA Hash Router)
  // ========================================================================
  function handleRoute() {
    const hash = window.location.hash.slice(1) || 'home';

    if (hash.startsWith('wallpaper/')) {
      const wallpaperId = hash.replace('wallpaper/', '');
      openWallpaperModal(wallpaperId);
      return;
    }

    if (hash.startsWith('category/')) {
      const catId = hash.replace('category/', '');
      quickFilterCategory(catId);
      return;
    }

    if (hash.startsWith('collection/')) {
      const collId = hash.replace('collection/', '');
      quickFilterCollection(collId);
      return;
    }

    // Standard view routing
    const validViews = ['home', 'explore', 'categories', 'collections', 'favorites', 'about'];
    const targetView = validViews.includes(hash) ? hash : 'home';
    switchView(targetView);
  }

  function switchView(viewName) {
    AppState.currentView = viewName;

    // Toggle active view sections
    Object.keys(DOM.views).forEach((key) => {
      if (DOM.views[key]) {
        if (key === viewName) {
          DOM.views[key].classList.add('active');
        } else {
          DOM.views[key].classList.remove('active');
        }
      }
    });

    // Update active navbar indicator
    DOM.navLinks.forEach((link) => {
      const linkView = link.getAttribute('data-view');
      if (linkView === viewName) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Close mobile drawer if open
    DOM.mobileDrawer.classList.remove('open');

    // Close detail modal if open
    closeModal(false);

    // If favorites view, refresh favorites
    if (viewName === 'favorites') {
      renderFavoritesView();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ========================================================================
  // Card HTML Generator (Japanese Minimalist Card)
  // ========================================================================
  function createWallpaperCardHTML(wallpaper, options = {}) {
    const isFav = AppState.favorites.has(wallpaper.id);
    const favActiveClass = isFav ? 'active' : '';

    return `
      <article class="wallpaper-card" data-id="${wallpaper.id}" onclick="window.AnimeApp.openWallpaper('${wallpaper.id}');">
        <div class="wallpaper-media-wrap">
          <img 
            src="${wallpaper.thumb || wallpaper.image}" 
            alt="${wallpaper.title} — ${wallpaper.anime}" 
            class="wallpaper-img" 
            loading="lazy"
            onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80';"
          >
          <div class="card-floating-actions" onclick="event.stopPropagation();">
            <button 
              class="card-action-btn favorite-btn ${favActiveClass}" 
              data-fav-id="${wallpaper.id}" 
              title="${isFav ? 'Remove from Favorites' : 'Save to Favorites'}"
              onclick="window.AnimeApp.toggleFavorite('${wallpaper.id}', event);"
            >
              <svg viewBox="0 0 24 24" fill="${isFav ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
              </svg>
            </button>
          </div>
          ${wallpaper.featured ? `<div class="card-floating-badge">Curated</div>` : ''}
        </div>
        <div class="wallpaper-info">
          <div class="wallpaper-meta-row">
            <span class="wallpaper-category-tag">${wallpaper.category}</span>
            <span class="wallpaper-res-tag">${wallpaper.aspectRatio}</span>
          </div>
          <h3 class="wallpaper-title">${wallpaper.title}</h3>
          <div class="wallpaper-anime-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;opacity:0.7;">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            <span>${wallpaper.anime}</span>
          </div>
        </div>
      </article>
    `;
  }

  // ========================================================================
  // Homepage Rendering
  // ========================================================================
  function renderAllViews() {
    renderHomeFeatured();
    renderHomeCategories();
    renderHomeTrending();
    renderHomeCollections();
    renderHomeLatest();
    renderFullCategories();
    renderFullCollections();
    renderExploreGallery();
    renderFavoritesView();
  }

  function renderHomeFeatured() {
    const featured = WALLPAPERS_DATA.filter(w => w.featured).slice(0, 8);
    DOM.homeFeaturedGallery.innerHTML = featured.map(w => createWallpaperCardHTML(w)).join('');
  }

  function renderHomeCategories() {
    DOM.homeCategoriesGrid.innerHTML = CATEGORIES_DATA.map(cat => `
      <div class="category-card" onclick="window.AnimeApp.quickFilterCategory('${cat.id}');">
        <img src="${cat.cover}" alt="${cat.name}" class="category-card-bg" loading="lazy">
        <div class="category-overlay"></div>
        <div class="category-watermark-kanji" aria-hidden="true">${cat.kanji}</div>
        <div class="category-content">
          <span class="category-count-badge">${cat.count} Wallpapers</span>
          <h3 class="category-name">${cat.name}</h3>
          <p class="category-subline">${cat.romaji} — ${cat.description.slice(0, 48)}...</p>
        </div>
      </div>
    `).join('');
  }

  function renderHomeTrending() {
    const trending = WALLPAPERS_DATA.filter(w => w.trending).slice(0, 4);
    DOM.homeTrendingGrid.innerHTML = trending.map((w, index) => `
      <div class="trending-card" onclick="window.AnimeApp.openWallpaper('${w.id}');">
        <div class="trending-rank-badge">#0${index + 1}</div>
        <div class="trending-media">
          <img src="${w.thumb || w.image}" alt="${w.title}" class="trending-img" loading="lazy">
        </div>
        <div class="wallpaper-info">
          <div class="wallpaper-meta-row">
            <span class="wallpaper-category-tag">${w.category}</span>
            <span class="wallpaper-res-tag">${w.resolution.split(' ')[0]}</span>
          </div>
          <h3 class="wallpaper-title" style="font-size:1rem;">${w.title}</h3>
          <div class="wallpaper-anime-title">${w.anime}</div>
        </div>
      </div>
    `).join('');
  }

  function renderHomeCollections() {
    DOM.homeCollectionsGrid.innerHTML = COLLECTIONS_DATA.slice(0, 3).map(coll => `
      <div class="collection-card" onclick="window.AnimeApp.quickFilterCollection('${coll.id}');">
        <div class="collection-media">
          <img src="${coll.cover}" alt="${coll.title}" class="collection-img" loading="lazy">
          <div class="collection-kanji-stamp">${coll.kanji}</div>
        </div>
        <div class="collection-body">
          <h3 class="collection-title">${coll.title}</h3>
          <span class="collection-subtitle">${coll.subtitle}</span>
          <p class="collection-desc">${coll.description}</p>
          <div class="collection-footer">
            <span>${coll.wallpaperIds.length} Curated Artworks</span>
            <span class="collection-explore-btn">
              <span>View</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </span>
          </div>
        </div>
      </div>
    `).join('');
  }

  function renderHomeLatest() {
    const latest = WALLPAPERS_DATA.filter(w => w.latest).slice(0, 6);
    DOM.homeLatestGallery.innerHTML = latest.map(w => createWallpaperCardHTML(w)).join('');
  }

  // ========================================================================
  // Full Categories & Collections Pages
  // ========================================================================
  function renderFullCategories() {
    DOM.fullCategoriesGrid.innerHTML = CATEGORIES_DATA.map(cat => `
      <div class="category-card" style="aspect-ratio: 16/9;" onclick="window.AnimeApp.quickFilterCategory('${cat.id}');">
        <img src="${cat.cover}" alt="${cat.name}" class="category-card-bg" loading="lazy">
        <div class="category-overlay"></div>
        <div class="category-watermark-kanji" aria-hidden="true">${cat.kanji}</div>
        <div class="category-content">
          <span class="category-count-badge">${cat.count} Master Wallpapers</span>
          <h2 class="category-name" style="font-size:1.75rem;">${cat.name} <span style="font-size:1.125rem; font-weight:normal; opacity:0.8;">(${cat.kanji})</span></h2>
          <p class="category-subline" style="font-size:0.9375rem; max-width:440px; margin-top:0.5rem; line-height:1.5;">${cat.description}</p>
          <div style="margin-top:1rem; display:inline-flex; align-items:center; gap:0.5rem; font-size:0.875rem; font-weight:600; color:var(--white);">
            <span>Explore ${cat.name} Wallpapers</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:15px;height:15px;">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </div>
        </div>
      </div>
    `).join('');
  }

  function renderFullCollections() {
    DOM.fullCollectionsGrid.innerHTML = COLLECTIONS_DATA.map(coll => `
      <div class="collection-card" onclick="window.AnimeApp.quickFilterCollection('${coll.id}');">
        <div class="collection-media" style="aspect-ratio: 16/9;">
          <img src="${coll.cover}" alt="${coll.title}" class="collection-img" loading="lazy">
          <div class="collection-kanji-stamp" style="font-size:0.875rem;">${coll.kanji}</div>
        </div>
        <div class="collection-body" style="padding: 2rem;">
          <h2 class="collection-title" style="font-size:1.625rem;">${coll.title}</h2>
          <span class="collection-subtitle" style="font-size:0.9375rem;">${coll.subtitle}</span>
          <p class="collection-desc" style="font-size:0.9375rem; line-height:1.65; margin-bottom:1.5rem;">${coll.description}</p>
          <div style="background-color:var(--bg-secondary); padding:0.875rem 1rem; border-radius:var(--radius-sm); border:1px solid var(--border-color); font-size:0.8125rem; color:var(--text-secondary); margin-bottom:1.5rem;">
            <strong style="color:var(--text-primary); display:block; margin-bottom:0.25rem;">Curator’s Note:</strong>
            ${coll.curatorNote}
          </div>
          <div class="collection-footer">
            <span>${coll.wallpaperIds.length} Master-grade Wallpapers</span>
            <span class="btn-primary" style="padding:0.5rem 1rem; font-size:0.8125rem;">
              <span>Explore Collection</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </span>
          </div>
        </div>
      </div>
    `).join('');
  }

  // ========================================================================
  // Explore Page Filtering & Masonry Engine
  // ========================================================================
  function setupDropdownFilters() {
    // Anime Dropdown
    DOM.filterAnimeSelect.innerHTML = ANIME_TITLES.map(title => `
      <option value="${title}">${title}</option>
    `).join('');

    // Resolution Dropdown
    DOM.filterResolutionSelect.innerHTML = RESOLUTIONS.map(res => `
      <option value="${res}">${res}</option>
    `).join('');
  }

  function renderCategoryPills() {
    const pillsHTML = [
      `
      <button class="filter-pill ${AppState.selectedCategory === 'all' ? 'active' : ''}" data-cat="all">
        <span>All Aesthetics</span>
        <span class="filter-pill-count">${WALLPAPERS_DATA.length}</span>
      </button>
      `
    ];

    CATEGORIES_DATA.forEach(cat => {
      const activeClass = AppState.selectedCategory === cat.name ? 'active' : '';
      pillsHTML.push(`
        <button class="filter-pill ${activeClass}" data-cat="${cat.name}">
          <span>${cat.name}</span>
          <span class="filter-pill-count">${cat.count}</span>
        </button>
      `);
    });

    DOM.exploreCategoryPills.innerHTML = pillsHTML.join('');

    // Attach pill clicks
    DOM.exploreCategoryPills.querySelectorAll('.filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.getAttribute('data-cat');
        AppState.selectedCategory = cat;
        renderCategoryPills();
        renderExploreGallery();
      });
    });
  }

  function getFilteredWallpapers() {
    let filtered = [...WALLPAPERS_DATA];

    // Search Query Filter
    if (AppState.searchQuery.trim()) {
      const q = AppState.searchQuery.toLowerCase().trim();
      filtered = filtered.filter(w => {
        return (
          w.title.toLowerCase().includes(q) ||
          w.anime.toLowerCase().includes(q) ||
          w.category.toLowerCase().includes(q) ||
          w.artist.toLowerCase().includes(q) ||
          w.tags.some(t => t.toLowerCase().includes(q)) ||
          w.description.toLowerCase().includes(q)
        );
      });
    }

    // Category Filter
    if (AppState.selectedCategory && AppState.selectedCategory !== 'all') {
      filtered = filtered.filter(w => w.category === AppState.selectedCategory);
    }

    // Anime Series Filter
    if (AppState.selectedAnime && AppState.selectedAnime !== 'All Anime') {
      filtered = filtered.filter(w => w.anime === AppState.selectedAnime);
    }

    // Resolution Filter
    if (AppState.selectedResolution && AppState.selectedResolution !== 'All Resolutions') {
      filtered = filtered.filter(w => w.resolution === AppState.selectedResolution);
    }

    // Orientation Filter
    if (AppState.selectedOrientation && AppState.selectedOrientation !== 'All') {
      filtered = filtered.filter(w => w.orientation === AppState.selectedOrientation);
    }

    // Sort Logic
    switch (AppState.selectedSort) {
      case 'latest':
        filtered.sort((a, b) => (b.latest ? 1 : 0) - (a.latest ? 1 : 0) || b.id.localeCompare(a.id));
        break;
      case 'likes':
        filtered.sort((a, b) => b.likes - a.likes);
        break;
      case 'downloads':
        filtered.sort((a, b) => b.downloads - a.downloads);
        break;
      case 'popular':
      default:
        filtered.sort((a, b) => a.rank - b.rank);
        break;
    }

    return filtered;
  }

  function renderExploreGallery() {
    const filtered = getFilteredWallpapers();
    updateActiveFilterBadges(filtered.length);

    if (filtered.length === 0) {
      DOM.exploreMasonryGallery.innerHTML = '';
      DOM.exploreEmptyState.style.display = 'flex';
      return;
    }

    DOM.exploreEmptyState.style.display = 'none';
    DOM.exploreMasonryGallery.innerHTML = filtered.map(w => createWallpaperCardHTML(w)).join('');
  }

  function updateActiveFilterBadges(count) {
    const activeFilters = [];

    if (AppState.searchQuery.trim()) {
      activeFilters.push({
        label: `Search: "${AppState.searchQuery.trim()}"`,
        clear: () => {
          AppState.searchQuery = '';
          DOM.exploreSearchInput.value = '';
          DOM.exploreSearchClear.style.display = 'none';
        }
      });
    }

    if (AppState.selectedCategory !== 'all') {
      activeFilters.push({
        label: `Category: ${AppState.selectedCategory}`,
        clear: () => {
          AppState.selectedCategory = 'all';
          renderCategoryPills();
        }
      });
    }

    if (AppState.selectedAnime !== 'All Anime') {
      activeFilters.push({
        label: `Anime: ${AppState.selectedAnime}`,
        clear: () => {
          AppState.selectedAnime = 'All Anime';
          DOM.filterAnimeSelect.value = 'All Anime';
        }
      });
    }

    if (AppState.selectedResolution !== 'All Resolutions') {
      activeFilters.push({
        label: `Res: ${AppState.selectedResolution.split(' ')[0]}`,
        clear: () => {
          AppState.selectedResolution = 'All Resolutions';
          DOM.filterResolutionSelect.value = 'All Resolutions';
        }
      });
    }

    if (AppState.selectedOrientation !== 'All') {
      activeFilters.push({
        label: `Orientation: ${AppState.selectedOrientation}`,
        clear: () => {
          AppState.selectedOrientation = 'All';
          DOM.filterOrientationSelect.value = 'All';
        }
      });
    }

    if (activeFilters.length > 0) {
      DOM.activeFiltersBar.style.display = 'flex';
      DOM.activeResultsCounter.textContent = `Showing ${count} of ${WALLPAPERS_DATA.length} wallpapers`;
      DOM.activeTagsList.innerHTML = activeFilters.map((f, i) => `
        <span class="active-filter-badge">
          <span>${f.label}</span>
          <button type="button" data-clear-idx="${i}" title="Remove filter" onclick="window.AnimeApp.clearFilterIndex(${i});">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </span>
      `).join('');
      // Store current clear handlers
      window._activeFilterClears = activeFilters.map(f => f.clear);
    } else {
      DOM.activeFiltersBar.style.display = 'none';
    }
  }

  function clearFilters() {
    AppState.searchQuery = '';
    AppState.selectedCategory = 'all';
    AppState.selectedAnime = 'All Anime';
    AppState.selectedResolution = 'All Resolutions';
    AppState.selectedOrientation = 'All';
    AppState.selectedSort = 'popular';

    DOM.exploreSearchInput.value = '';
    DOM.exploreSearchClear.style.display = 'none';
    DOM.filterAnimeSelect.value = 'All Anime';
    DOM.filterResolutionSelect.value = 'All Resolutions';
    DOM.filterOrientationSelect.value = 'All';
    DOM.filterSortSelect.value = 'popular';

    renderCategoryPills();
    renderExploreGallery();
    showToast('Filters cleared', 'info');
  }

  function quickFilterCategory(catIdOrName) {
    // Look up category
    const cat = CATEGORIES_DATA.find(c => c.id === catIdOrName || c.name.toLowerCase() === catIdOrName.toLowerCase());
    const catName = cat ? cat.name : catIdOrName;

    AppState.selectedCategory = catName;
    window.location.hash = '#explore';
    switchView('explore');
    renderCategoryPills();
    renderExploreGallery();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    showToast(`Showing ${catName} wallpapers`, 'info');
  }

  function quickFilterCollection(collId) {
    const coll = COLLECTIONS_DATA.find(c => c.id === collId);
    if (!coll) return;

    // Filter wallpapers belonging to this collection
    clearFilters();
    window.location.hash = '#explore';
    switchView('explore');

    // Filter by collection IDs
    const collWallpapers = WALLPAPERS_DATA.filter(w => coll.wallpaperIds.includes(w.id));
    DOM.exploreMasonryGallery.innerHTML = collWallpapers.map(w => createWallpaperCardHTML(w)).join('');
    DOM.activeFiltersBar.style.display = 'flex';
    DOM.activeResultsCounter.textContent = `Collection: ${coll.title} (${collWallpapers.length} wallpapers)`;
    DOM.activeTagsList.innerHTML = `
      <span class="active-filter-badge">
        <span>Collection: ${coll.title}</span>
        <button type="button" onclick="window.AnimeApp.clearFilters();">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </span>
    `;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    showToast(`Opened collection "${coll.title}"`, 'info');
  }

  // ========================================================================
  // Favorites Management
  // ========================================================================
  function toggleFavorite(wallpaperId, event) {
    if (event) event.stopPropagation();

    const isFav = AppState.favorites.has(wallpaperId);
    const wallpaper = WALLPAPERS_DATA.find(w => w.id === wallpaperId);
    const title = wallpaper ? wallpaper.title : 'Wallpaper';

    if (isFav) {
      AppState.favorites.delete(wallpaperId);
      showToast(`Removed "${title}" from Favorites`, 'info');
    } else {
      AppState.favorites.add(wallpaperId);
      showToast(`Saved "${title}" to Favorites`, 'success');
    }

    saveStoredPreferences();
    updateNavFavoritesBadge();

    // Sync button states on cards
    document.querySelectorAll(`[data-fav-id="${wallpaperId}"]`).forEach(btn => {
      if (AppState.favorites.has(wallpaperId)) {
        btn.classList.add('active');
        btn.querySelector('svg').setAttribute('fill', 'currentColor');
      } else {
        btn.classList.remove('active');
        btn.querySelector('svg').setAttribute('fill', 'none');
      }
    });

    // If modal is open for this wallpaper, update modal button
    if (AppState.currentWallpaperId === wallpaperId) {
      syncModalFavoriteState();
    }

    // If on favorites view, re-render
    if (AppState.currentView === 'favorites') {
      renderFavoritesView();
    }
  }

  function updateNavFavoritesBadge() {
    const count = AppState.favorites.size;
    DOM.navFavCount.textContent = count;
    if (count > 0) {
      DOM.navFavCount.classList.remove('empty');
    } else {
      DOM.navFavCount.classList.add('empty');
    }
  }

  function renderFavoritesView() {
    const favWallpapers = WALLPAPERS_DATA.filter(w => AppState.favorites.has(w.id));
    const count = favWallpapers.length;

    if (count === 0) {
      DOM.favoritesMasonryGallery.innerHTML = '';
      DOM.favoritesEmptyState.style.display = 'flex';
      DOM.favStatusSubtitle.textContent = 'Your personal library is currently empty.';
      DOM.favDownloadAllBtn.style.display = 'none';
      DOM.favClearAllBtn.style.display = 'none';
      return;
    }

    DOM.favoritesEmptyState.style.display = 'none';
    DOM.favStatusSubtitle.textContent = `You have saved ${count} curated wallpaper${count > 1 ? 's' : ''}.`;
    DOM.favDownloadAllBtn.style.display = 'inline-flex';
    DOM.favClearAllBtn.style.display = 'inline-flex';
    DOM.favoritesMasonryGallery.innerHTML = favWallpapers.map(w => createWallpaperCardHTML(w)).join('');
  }

  function downloadAllFavorites() {
    const favCount = AppState.favorites.size;
    if (favCount === 0) return;

    showToast(`Downloading batch archive (${favCount} high-res wallpapers)...`, 'success');
    
    // Simulate batch archive triggering download of the first item and link list
    const firstFav = WALLPAPERS_DATA.find(w => AppState.favorites.has(w.id));
    if (firstFav) {
      downloadFile(firstFav.image, `AnimeWall_Collection_${firstFav.id}.jpg`);
    }
  }

  function clearAllFavorites() {
    if (AppState.favorites.size === 0) return;
    if (confirm('Are you sure you want to clear all saved wallpapers from your favorites?')) {
      AppState.favorites.clear();
      saveStoredPreferences();
      updateNavFavoritesBadge();
      renderFavoritesView();
      showToast('All saved wallpapers cleared', 'info');
    }
  }

  // ========================================================================
  // Wallpaper Details Modal Controller
  // ========================================================================
  function openWallpaperModal(wallpaperId) {
    const wallpaper = WALLPAPERS_DATA.find(w => w.id === wallpaperId);
    if (!wallpaper) return;

    AppState.currentWallpaperId = wallpaperId;
    AppState.activeModalIndex = WALLPAPERS_DATA.findIndex(w => w.id === wallpaperId);

    // Update Modal Data
    DOM.modalBreadcrumbCategory.textContent = wallpaper.category;
    DOM.modalBreadcrumbTitle.textContent = wallpaper.title;
    DOM.modalPreviewImg.src = wallpaper.image;
    DOM.modalPreviewImg.alt = `${wallpaper.title} — ${wallpaper.anime}`;
    DOM.modalCategoryBadge.textContent = wallpaper.category;
    DOM.modalKanjiStamp.textContent = wallpaper.kanji ? wallpaper.kanji.slice(0, 1) : '美';
    DOM.modalWallpaperTitle.textContent = wallpaper.title;
    DOM.modalAnimeTitle.textContent = wallpaper.anime;
    DOM.modalDescText.textContent = wallpaper.description;

    // Specs
    DOM.modalSpecRes.textContent = wallpaper.resolution;
    DOM.modalSpecRatio.textContent = `${wallpaper.aspectRatio} ${wallpaper.orientation}`;
    DOM.modalSpecArtist.textContent = wallpaper.artist;
    DOM.modalSpecFormat.textContent = `${wallpaper.format} • ${wallpaper.fileSize}`;

    // Color Palette Swatches
    DOM.modalPaletteSwatches.innerHTML = wallpaper.colors.map(hex => `
      <div 
        class="palette-swatch" 
        style="background-color: ${hex};" 
        title="Copy ${hex}" 
        onclick="window.AnimeApp.copyColorHex('${hex}');"
      ></div>
    `).join('');

    // Sync Favorite Button State
    syncModalFavoriteState();

    // Related Wallpapers
    renderModalRelated(wallpaper);

    // Show Modal
    DOM.modal.classList.add('open');
    DOM.modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Update URL hash without scroll jumps
    if (window.location.hash !== `#wallpaper/${wallpaperId}`) {
      history.pushState(null, '', `#wallpaper/${wallpaperId}`);
    }
  }

  function closeModal(restoreHash = true) {
    if (!DOM.modal.classList.contains('open')) return;

    DOM.modal.classList.remove('open');
    DOM.modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    AppState.currentWallpaperId = null;

    if (restoreHash) {
      // Revert hash to current view
      history.pushState(null, '', `#${AppState.currentView}`);
    }
  }

  function syncModalFavoriteState() {
    if (!AppState.currentWallpaperId) return;
    const isFav = AppState.favorites.has(AppState.currentWallpaperId);
    if (isFav) {
      DOM.modalFavToggleBtn.classList.add('active');
      DOM.modalFavToggleBtn.querySelector('svg').setAttribute('fill', 'currentColor');
      DOM.modalFavText.textContent = 'Saved in Favorites';
    } else {
      DOM.modalFavToggleBtn.classList.remove('active');
      DOM.modalFavToggleBtn.querySelector('svg').setAttribute('fill', 'none');
      DOM.modalFavText.textContent = 'Save to Favorites';
    }
  }

  function toggleModalFavorite() {
    if (!AppState.currentWallpaperId) return;
    toggleFavorite(AppState.currentWallpaperId);
  }

  function copyWallpaperLink() {
    if (!AppState.currentWallpaperId) return;
    const url = `${window.location.origin}${window.location.pathname}#wallpaper/${AppState.currentWallpaperId}`;
    navigator.clipboard.writeText(url).then(() => {
      showToast('Artwork link copied to clipboard!', 'success');
    }).catch(() => {
      showToast('Link copied to clipboard', 'info');
    });
  }

  function copyColorHex(hex) {
    navigator.clipboard.writeText(hex).then(() => {
      showToast(`Copied color ${hex} to clipboard!`, 'info');
    });
  }

  function renderModalRelated(currentWallpaper) {
    // Find up to 4 wallpapers in same category or anime, excluding current
    let related = WALLPAPERS_DATA.filter(w => w.id !== currentWallpaper.id && (w.category === currentWallpaper.category || w.anime === currentWallpaper.anime));
    if (related.length < 4) {
      const remaining = WALLPAPERS_DATA.filter(w => w.id !== currentWallpaper.id && !related.includes(w));
      related = [...related, ...remaining];
    }
    related = related.slice(0, 4);

    DOM.modalRelatedGrid.innerHTML = related.map(w => `
      <div 
        class="wallpaper-card" 
        style="margin-bottom:0;" 
        onclick="window.AnimeApp.openWallpaper('${w.id}');"
      >
        <div class="wallpaper-media-wrap" style="aspect-ratio:16/10;">
          <img src="${w.thumb || w.image}" alt="${w.title}" class="wallpaper-img" loading="lazy">
        </div>
        <div class="wallpaper-info" style="padding:0.75rem 1rem;">
          <h4 class="wallpaper-title" style="font-size:0.875rem;">${w.title}</h4>
          <span style="font-size:0.75rem; color:var(--text-secondary);">${w.anime}</span>
        </div>
      </div>
    `).join('');
  }

  // ========================================================================
  // Direct Download Engine
  // ========================================================================
  function triggerWallpaperDownload() {
    if (!AppState.currentWallpaperId) return;
    const wallpaper = WALLPAPERS_DATA.find(w => w.id === AppState.currentWallpaperId);
    if (!wallpaper) return;

    const resChoice = DOM.modalDownloadResSelect.value;
    const cleanTitle = wallpaper.title.replace(/[^a-zA-Z0-9]/g, '_');
    const fileName = `AnimeWall_${cleanTitle}_${resChoice}.jpg`;

    showToast(`Downloading "${wallpaper.title}" in ${resChoice.toUpperCase()}...`, 'success');

    // Trigger genuine image download
    downloadFile(wallpaper.image, fileName);
  }

  function downloadFile(url, fileName) {
    // Fetch image as blob for direct local download
    fetch(url)
      .then(res => res.blob())
      .then(blob => {
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = blobUrl;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
          window.URL.revokeObjectURL(blobUrl);
          document.body.removeChild(a);
        }, 300);
      })
      .catch(() => {
        // Fallback standard direct download anchor
        const a = document.createElement('a');
        a.target = '_blank';
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      });
  }

  // ========================================================================
  // Quick Search Command Palette (Ctrl + K)
  // ========================================================================
  function openCommandPalette() {
    DOM.commandPaletteModal.classList.add('open');
    DOM.commandPaletteInput.value = '';
    renderCommandResults('');
    DOM.commandPaletteInput.focus();
  }

  function closeCommandPalette() {
    DOM.commandPaletteModal.classList.remove('open');
  }

  function renderCommandResults(query) {
    const q = query.toLowerCase().trim();
    let matches = WALLPAPERS_DATA;

    if (q) {
      matches = matches.filter(w => {
        return (
          w.title.toLowerCase().includes(q) ||
          w.anime.toLowerCase().includes(q) ||
          w.category.toLowerCase().includes(q) ||
          w.artist.toLowerCase().includes(q) ||
          w.tags.some(t => t.toLowerCase().includes(q))
        );
      });
    }

    matches = matches.slice(0, 6);

    if (matches.length === 0) {
      DOM.commandResultsList.innerHTML = `
        <div style="padding:1.5rem; text-align:center; color:var(--text-muted); font-size:0.875rem;">
          No matching wallpapers found for "${query}"
        </div>
      `;
      return;
    }

    DOM.commandResultsList.innerHTML = matches.map(w => `
      <div class="command-result-item" onclick="window.AnimeApp.selectCommandItem('${w.id}');">
        <img src="${w.thumb || w.image}" alt="${w.title}" class="command-result-thumb">
        <div class="command-result-info">
          <span class="command-result-title">${w.title}</span>
          <span class="command-result-sub">${w.anime} • ${w.category}</span>
        </div>
      </div>
    `).join('');
  }

  function selectCommandItem(wallpaperId) {
    closeCommandPalette();
    openWallpaperModal(wallpaperId);
  }

  // ========================================================================
  // Toast Notifications
  // ========================================================================
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast toast-accent';
    toast.innerHTML = `
      <div class="hanko-mini" style="width:16px;height:16px;font-size:0.625rem;background:var(--accent-red);color:#FFF;border-radius:2px;display:flex;align-items:center;justify-content:center;font-family:var(--font-serif);">印</div>
      <span>${message}</span>
    `;

    DOM.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => {
        if (toast.parentNode) {
          DOM.toastContainer.removeChild(toast);
        }
      }, 250);
    }, 3200);
  }

  // ========================================================================
  // Event Listeners Setup
  // ========================================================================
  function setupEventListeners() {
    // Hash Routing
    window.addEventListener('hashchange', handleRoute);

    // Mobile Hamburger
    DOM.mobileToggleBtn.addEventListener('click', () => {
      DOM.mobileDrawer.classList.toggle('open');
    });

    // Theme Toggle
    DOM.themeToggleBtn.addEventListener('click', toggleTheme);

    // User Profile Action
    DOM.userProfileBtn.addEventListener('click', () => {
      showToast('Curator Profile: AnimeWall Master Archive (2026)', 'info');
    });

    // Modal Close Button & Backdrop
    DOM.modalCloseBtn.addEventListener('click', () => closeModal(true));
    DOM.modal.addEventListener('click', (e) => {
      if (e.target === DOM.modal) closeModal(true);
    });

    // Zoom Toggle Button
    DOM.modalZoomBtn.addEventListener('click', () => {
      if (DOM.modalPreviewImg.src) {
        window.open(DOM.modalPreviewImg.src, '_blank');
      }
    });

    // Explore Live Search
    DOM.exploreSearchInput.addEventListener('input', (e) => {
      AppState.searchQuery = e.target.value;
      DOM.exploreSearchClear.style.display = AppState.searchQuery ? 'flex' : 'none';
      renderExploreGallery();
    });

    DOM.exploreSearchClear.addEventListener('click', () => {
      AppState.searchQuery = '';
      DOM.exploreSearchInput.value = '';
      DOM.exploreSearchClear.style.display = 'none';
      renderExploreGallery();
    });

    // Explore Filter Dropdowns
    DOM.filterAnimeSelect.addEventListener('change', (e) => {
      AppState.selectedAnime = e.target.value;
      renderExploreGallery();
    });

    DOM.filterResolutionSelect.addEventListener('change', (e) => {
      AppState.selectedResolution = e.target.value;
      renderExploreGallery();
    });

    DOM.filterOrientationSelect.addEventListener('change', (e) => {
      AppState.selectedOrientation = e.target.value;
      renderExploreGallery();
    });

    DOM.filterSortSelect.addEventListener('change', (e) => {
      AppState.selectedSort = e.target.value;
      renderExploreGallery();
    });

    DOM.clearAllFiltersBtn.addEventListener('click', clearFilters);

    // Command Palette Trigger
    DOM.searchOpenBtn.addEventListener('click', openCommandPalette);
    DOM.commandPaletteModal.addEventListener('click', (e) => {
      if (e.target === DOM.commandPaletteModal) closeCommandPalette();
    });

    DOM.commandPaletteInput.addEventListener('input', (e) => {
      renderCommandResults(e.target.value);
    });

    // Global Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      // Ctrl + K or Cmd + K: Quick Search
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (DOM.commandPaletteModal.classList.contains('open')) {
          closeCommandPalette();
        } else {
          openCommandPalette();
        }
        return;
      }

      // Escape: Close Modals
      if (e.key === 'Escape') {
        if (DOM.commandPaletteModal.classList.contains('open')) {
          closeCommandPalette();
          return;
        }
        if (DOM.modal.classList.contains('open')) {
          closeModal(true);
          return;
        }
        if (DOM.mobileDrawer.classList.contains('open')) {
          DOM.mobileDrawer.classList.remove('open');
          return;
        }
      }

      // Left / Right arrow navigation when wallpaper modal is open
      if (DOM.modal.classList.contains('open')) {
        const wallpapers = getFilteredWallpapers();
        if (wallpapers.length <= 1) return;

        if (e.key === 'ArrowRight') {
          e.preventDefault();
          let nextIdx = (AppState.activeModalIndex + 1) % wallpapers.length;
          openWallpaperModal(wallpapers[nextIdx].id);
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          let prevIdx = (AppState.activeModalIndex - 1 + wallpapers.length) % wallpapers.length;
          openWallpaperModal(wallpapers[prevIdx].id);
        }
      }
    });

    // Home Section Trending "View All" Link
    const trendingViewAll = document.getElementById('home-trending-view-all');
    if (trendingViewAll) {
      trendingViewAll.addEventListener('click', (e) => {
        e.preventDefault();
        AppState.selectedSort = 'popular';
        DOM.filterSortSelect.value = 'popular';
        window.location.hash = '#explore';
      });
    }

    // Home Section Latest "View All" Link
    const latestViewAll = document.getElementById('home-latest-view-all');
    if (latestViewAll) {
      latestViewAll.addEventListener('click', (e) => {
        e.preventDefault();
        AppState.selectedSort = 'latest';
        DOM.filterSortSelect.value = 'latest';
        window.location.hash = '#explore';
      });
    }
  }

  // Newsletter Submission Handler
  function handleNewsletter(form) {
    const input = form.querySelector('input[type="email"]');
    const email = input.value.trim();
    if (email) {
      showToast(`Thank you for subscribing! Aesthetic updates sent to ${email}`, 'success');
      form.reset();
    }
  }

  // Clear single filter index
  function clearFilterIndex(idx) {
    if (window._activeFilterClears && window._activeFilterClears[idx]) {
      window._activeFilterClears[idx]();
      renderExploreGallery();
    }
  }

  // Export Public API to Window for Inline HTML Handlers
  window.AnimeApp = {
    openWallpaper: openWallpaperModal,
    closeModal: closeModal,
    toggleFavorite: toggleFavorite,
    toggleModalFavorite: toggleModalFavorite,
    copyWallpaperLink: copyWallpaperLink,
    copyColorHex: copyColorHex,
    triggerWallpaperDownload: triggerWallpaperDownload,
    quickFilterCategory: quickFilterCategory,
    quickFilterCollection: quickFilterCollection,
    clearFilters: clearFilters,
    clearFilterIndex: clearFilterIndex,
    downloadAllFavorites: downloadAllFavorites,
    clearAllFavorites: clearAllFavorites,
    handleNewsletter: handleNewsletter,
    selectCommandItem: selectCommandItem,
    showToast: showToast
  };

  // Launch Application on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }

})();
