# Operator Runbook

## Refresh the Registry

```bash
cd VDR/chart-tiler
python -c "from registry import get_registry; get_registry().scan([Path('data')])"  # refresh
```

## Import a GeoTIFF

```bash
cd VDR/chart-tiler
make geotiff-cog SRC=/charts/foo.tif
```

## Select Base Map

The web client reads `/charts` to populate the base picker.  Toggle between
`osm`, `geotiff` and `enc` bases at runtime without reloading the page.
