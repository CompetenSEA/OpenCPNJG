# BAUV Assets

The BAUV project supplies a collection of nautical SVG symbols.  Only the
symbols stored under `VDR/BAUV/src/public/svg` are consumed by the style builder
and may be redistributed by this repository.  Additional files shipped with the
upstream project are ignored.

## Adapter

`third_party/bauv_adapter.py` exposes a light‑weight API for accessing these
assets from tooling.  Typical usage::

```python
from VDR.third_party import bauv_adapter

for name, path in bauv_adapter.iter_symbols():
    print(name, path)

palette = bauv_adapter.load_palette()
```

The adapter intentionally returns paths and dictionaries; callers are free to
rasterise the SVGs or interpret the palette as required.

## Sprites

`server-styling/tools/bauv_sprite.py` rasterises selected BAUV symbols using the
`resvg` command line tool and packs them into a MapLibre compatible sprite sheet
written to `server-styling/dist/sprites/`.
