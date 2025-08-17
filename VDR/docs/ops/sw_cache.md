# Service worker caching

The web client ships with a service worker that pre-caches a handful of
static assets and manages a sizeable tile cache.

## Cached assets

On installation the worker fetches `/static/cas/manifest.json` and
preloads the following objects if present:

- `dict.json`
- `sprite.png` / `sprite.json`
- glyph range files such as `glyphs/0-255.pbf`

These files are content addressed and served from `/static/cas/<sha>`.
Updates simply publish new hashed filenames and manifest entries, so
clients will download new assets automatically when the manifest changes.

## Tile cache

Vector tiles requested under `/tiles/` are stored in an IndexedDB object
store.  Records include a timestamp and byte size which allows an
approximate 500 MB least-recently-used eviction policy.  When the cache
exceeds the limit the oldest entries are pruned until usage drops below
the threshold.

## Invalidation

Because assets are hashed and referenced via the manifest, updating the
server with new files invalidates previous cache entries implicitly.  The
tile cache does not attempt fine-grained invalidation; deleting browser
storage or increasing the manifest version is sufficient to force a
complete refresh.
