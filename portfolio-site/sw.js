// Desacratio Portfolio — Service Worker
const CACHE = 'desacratio-portfolio-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/script.js',
    '/manifest.json',
    '/favicon.ico',
    '/assets/icons/favicon.svg',
    '/assets/icons/favicon-16x16.png',
    '/assets/icons/favicon-32x32.png',
    '/assets/icons/apple-touch-icon.png',
    '/assets/icons/android-chrome-192x192.png',
    '/assets/icons/android-chrome-512x512.png',
];

self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    if (
        event.request.url.includes('fonts.googleapis.com') ||
        event.request.url.includes('fonts.gstatic.com')
    ) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                return cached || fetch(event.request).then((response) => {
                    const clone = response.clone();
                    caches.open(CACHE).then((cache) => cache.put(event.request, clone));
                    return response;
                });
            })
        );
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                const clone = response.clone();
                caches.open(CACHE).then((cache) => cache.put(event.request, clone));
                return response;
            })
            .catch(() => {
                return caches.match(event.request).then((cached) => {
                    if (!cached && event.request.mode === 'navigate') {
                        return caches.match('/');
                    }
                    return cached;
                });
            })
    );
});
