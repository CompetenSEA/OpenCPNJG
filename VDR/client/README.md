# Client Architecture

MapLibre provides the base map and manages raster/vector chart tiles.
deck.gl renders analytic overlays:
* `TripsLayer` – animated vessel tracks
* `PathLayer`/`LineLayer` – prediction vectors and trails
* `IconLayer` – CPA markers or vessel icons

Optional drawing tools (e.g. nebula.gl) share the same WebGL context.

```
client/
  src/    # frontend implementation (MapLibre + deck.gl)
  public/ # static assets
```

