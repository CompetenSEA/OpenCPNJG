# Hybrid Vector Tiles

Publish S‑57 features as Mapbox Vector Tiles with feature codes.
A lightweight S‑52 ruleset in the client styles these layers via WebGL.

Tools such as `s57chart` or custom converters generate the MVTs from ENC data.

```
hybrid-vector-tiles/
  src/   # feature extraction and MVT generation
  data/  # source S‑57 datasets and intermediate GeoJSON
```

