# Server-Side Styling

This module pre-renders raster chart tiles using an S‑52 renderer (e.g. `ps52plib` or `libS52`).
Generated tiles are served as standard XYZ/COG imagery for MapLibre to display beneath deck.gl overlays.

```
server-styling/
  src/       # raster tiler sources / build scripts
  tiles/     # output chart tiles (e.g. COG, MBTiles)
```

