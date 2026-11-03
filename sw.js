/* MoneyBall service worker — hand-rolled (Dispatch #2, annex §1).
 *
 * Shell: precache-first (pages, manifest, icons, install kit,
 * and the small feeds). Feed JSON: stale-while-revalidate with
 * a 24h expiration — the cached copy renders immediately, the
 * network answer replaces it, and an expired entry is dropped
 * rather than served stale forever. Large feeds (pools,
 * wallets) are runtime-cached only, never precached.
 *
 * Control discipline (the SOFA caveat: a worker can install
 * yet never control): install calls skipWaiting and activate
 * calls clients.claim, so the first load after registration is
 * already controlled and the offline test is meaningful.
 */
const VERSION = "moneyball-pwa-v1";
const SHELL_CACHE = `${VERSION}-shell`;
const FEED_CACHE = `${VERSION}-feeds`;
const FEED_MAX_AGE_MS = 24 * 60 * 60 * 1000;

const SHELL = [
  "./",
  "./index.html",
  "./cards.html",
  "./pools.html",
  "./settlement.html",
  "./manifest.webmanifest",
  "./install.js",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
];
const SMALL_FEEDS = [
  "./data/book-feed.json",
  "./data/cards-feed.json",
  "./data/settlement-report.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const shell = await caches.open(SHELL_CACHE);
      await shell.addAll(SHELL);
      const feeds = await caches.open(FEED_CACHE);
      await feeds.addAll(SMALL_FEEDS);
      await self.skipWaiting();
    })()
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => !k.startsWith(VERSION))
          .map((k) => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

async function feedSWR(request) {
  const cache = await caches.open(FEED_CACHE);
  const cached = await cache.match(request);
  if (cached) {
    const fetchedAt = Number(cached.headers.get("x-mb-fetched-at") || 0);
    if (Date.now() - fetchedAt > FEED_MAX_AGE_MS) {
      await cache.delete(request);
    }
  }
  const network = fetch(request)
    .then(async (response) => {
      if (response.ok) {
        const body = await response.clone().text();
        const stamped = new Response(body, {
          status: response.status,
          statusText: response.statusText,
          headers: {
            "Content-Type": "application/json",
            "x-mb-fetched-at": String(Date.now()),
          },
        });
        await cache.put(request, stamped);
      }
      return response;
    })
    .catch(() => null);
  const fresh = await cache.match(request);
  return fresh || (await network) || Response.error();
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET") return;
  if (url.origin !== self.location.origin) return;
  if (url.pathname.includes("/data/") && url.pathname.endsWith(".json")) {
    event.respondWith(feedSWR(event.request));
    return;
  }
  event.respondWith(
    (async () => {
      const shell = await caches.open(SHELL_CACHE);
      const hit = await shell.match(event.request, {
        ignoreSearch: true,
      });
      if (hit) return hit;
      try {
        const response = await fetch(event.request);
        if (response.ok && event.request.mode === "navigate") {
          await shell.put(event.request, response.clone());
        }
        return response;
      } catch (err) {
        const index = await shell.match("./index.html");
        if (event.request.mode === "navigate" && index) return index;
        throw err;
      }
    })()
  );
});
