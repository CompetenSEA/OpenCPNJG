# Server-Side Styling

This module pre-renders raster chart tiles using an S‑52 renderer (e.g. `ps52plib` or `libS52`).
Generated tiles are served as standard XYZ/COG imagery for MapLibre to display beneath deck.gl overlays.

```
server-styling/
  src/       # raster tiler sources / build scripts
  tiles/     # output chart tiles (e.g. COG, MBTiles)
```


## S-52 assets

The S-52 renderer depends on upstream symbol and lookup tables from the
[OpenCPN](https://github.com/OpenCPN/OpenCPN) project.  To keep builds
reproducible these files are fetched on demand based on the commit pinned in
`opencpn-assets.lock`.

```
server-styling/
  opencpn-assets.lock  # upstream repo/path/commit
  opencpn-assets/      # populated by sync script (ignored by git)
```

Fetch the assets and generate the required MapLibre artifacts:

```bash
python VDR/server-styling/sync_opencpn_assets.py
python VDR/server-styling/build_style_json.py \
  --rulebook VDR/server-styling/opencpn-assets \
  --output VDR/server-styling/style.s52.day.json
python VDR/server-styling/generate_sprite_json.py \
  --chartsymbols VDR/server-styling/opencpn-assets/chartsymbols.xml \
  --output VDR/server-styling/sprites/s52-day.json
```

The generated `style.s52.day.json`, `sprites/s52-day.json` and upstream
`rastersymbols-day.png` can then be served alongside vector tiles.
