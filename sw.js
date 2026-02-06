// ============================================================================
// PROJECT LAZARUS — Service Worker
// Precaches the app shell for full offline operation.
// ============================================================================

const CACHE_NAME = 'lazarus-v1';

const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// External CDN resources to cache on first use
const CDN_CACHE = 'lazarus-cdn-v1';

// ── Install: Precache app shell ─────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ── Activate: Clean old caches ──────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((name) => name !== CACHE_NAME && name !== CDN_CACHE)
          .map((name) => caches.delete(name))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: Offline-first with network fallback ──────────────────────────────
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests (OSC API POSTs go straight to camera)
  if (event.request.method !== 'GET') return;

  // Camera requests: network-only (never cache camera data)
  if (url.hostname === '192.168.107.1') return;

  // CDN resources (Three.js, fonts, FFmpeg): cache-first after first load
  if (url.hostname.includes('cdnjs.cloudflare.com') ||
      url.hostname.includes('fonts.googleapis.com') ||
      url.hostname.includes('fonts.gstatic.com') ||
      url.hostname.includes('esm.sh') ||
      url.hostname.includes('unpkg.com')) {
    event.respondWith(
      caches.open(CDN_CACHE).then((cache) =>
        cache.match(event.request).then((cached) => {
          if (cached) return cached;
          return fetch(event.request).then((response) => {
            if (response.ok) cache.put(event.request, response.clone());
            return response;
          });
        })
      )
    );
    return;
  }

  // App shell: cache-first, network fallback
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((response) => {
        // Cache successful responses for next time
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
