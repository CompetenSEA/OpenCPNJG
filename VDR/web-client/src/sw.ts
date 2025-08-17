// Service worker for VDR web client
// Pre-caches core static assets and implements a tile cache backed by
// IndexedDB with an approximate 500 MB LRU eviction policy.

const STATIC_CACHE = 'vdr-static-v1';
const TILE_DB = 'vdr-tile-cache';
const TILE_STORE = 'tiles';
const MAX_BYTES = 500 * 1024 * 1024;

// ---- install: pre-cache sprite/glyphs/dict ------------------------------
self.addEventListener('install', (event: ExtendableEvent) => {
  event.waitUntil(precacheStatic());
});

async function precacheStatic(): Promise<void> {
  try {
    const res = await fetch('/static/cas/manifest.json');
    const manifest: Record<string, string> = await res.json();
    const urls: string[] = [];
    ['sprite.png', 'sprite.json', 'dict.json'].forEach((k) => {
      if (manifest[k]) urls.push(`/static/cas/${manifest[k]}`);
    });
    Object.keys(manifest)
      .filter((k) => k.startsWith('glyphs/'))
      .forEach((k) => urls.push(`/static/cas/${manifest[k]}`));
    const cache = await caches.open(STATIC_CACHE);
    await cache.addAll(urls);
  } catch (err) {
    console.error('precache error', err);
  }
}

// ---- IndexedDB helpers --------------------------------------------------
function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(TILE_DB, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      db.createObjectStore(TILE_STORE, { keyPath: 'url' });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

interface TileRecord {
  url: string;
  blob: Blob;
  size: number;
  ts: number;
}

async function getTile(db: IDBDatabase, url: string): Promise<Blob | null> {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(TILE_STORE, 'readonly');
    const req = tx.objectStore(TILE_STORE).get(url);
    req.onsuccess = () => {
      const val = req.result as TileRecord | undefined;
      resolve(val ? val.blob : null);
    };
    req.onerror = () => reject(req.error);
  });
}

async function putTile(db: IDBDatabase, url: string, blob: Blob): Promise<void> {
  const record: TileRecord = { url, blob, size: blob.size, ts: Date.now() };
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(TILE_STORE, 'readwrite');
    const req = tx.objectStore(TILE_STORE).put(record);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
  await evict(db);
}

async function evict(db: IDBDatabase): Promise<void> {
  const tx = db.transaction(TILE_STORE, 'readwrite');
  const store = tx.objectStore(TILE_STORE);
  const items: TileRecord[] = [];
  let total = 0;
  await new Promise<void>((resolve, reject) => {
    const cursorReq = store.openCursor();
    cursorReq.onsuccess = () => {
      const cursor = cursorReq.result;
      if (cursor) {
        const val = cursor.value as TileRecord;
        total += val.size;
        items.push(val);
        cursor.continue();
      } else {
        resolve();
      }
    };
    cursorReq.onerror = () => reject(cursorReq.error);
  });
  if (total <= MAX_BYTES) return;
  items.sort((a, b) => a.ts - b.ts); // oldest first
  for (const rec of items) {
    if (total <= MAX_BYTES) break;
    await new Promise<void>((resolve, reject) => {
      const del = store.delete(rec.url);
      del.onsuccess = () => resolve();
      del.onerror = () => reject(del.error);
    });
    total -= rec.size;
  }
}

// ---- fetch handler ------------------------------------------------------
self.addEventListener('fetch', (event: FetchEvent) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/tiles/')) {
    event.respondWith(handleTileRequest(event.request));
  }
});

async function handleTileRequest(req: Request): Promise<Response> {
  const db = await openDB();
  const cached = await getTile(db, req.url);
  if (cached) {
    return new Response(cached);
  }
  const resp = await fetch(req);
  const blob = await resp.clone().blob();
  await putTile(db, req.url, blob);
  return resp;
}

// ---- idle prefetch queue ------------------------------------------------
const prefetchQueue: string[] = [];
let prefetchScheduled = false;

self.addEventListener('message', (event: ExtendableMessageEvent) => {
  const data = event.data as { type: string; urls?: string[] };
  if (data && data.type === 'prefetch' && Array.isArray(data.urls)) {
    prefetchQueue.push(...data.urls);
    schedulePrefetch();
  }
});

function schedulePrefetch() {
  if (prefetchScheduled) return;
  prefetchScheduled = true;
  (self as any).requestIdleCallback(async () => {
    prefetchScheduled = false;
    const url = prefetchQueue.shift();
    if (url) {
      try {
        await fetch(url);
      } catch (err) {
        // ignore network errors for prefetch
      }
      schedulePrefetch();
    }
  });
}

export {};
