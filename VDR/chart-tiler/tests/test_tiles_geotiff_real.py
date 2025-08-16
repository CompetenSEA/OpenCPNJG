import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tileserver import app, reg  # noqa: E402


def _make_cog(tmp_path: Path) -> None:
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    arr = np.ones((1, 256, 256), dtype=np.uint8) * 255
    transform = from_origin(-180, 90, 360 / 256, 180 / 256)
    tif = tmp_path / "test.tif"
    with rasterio.open(
        tif,
        "w",
        driver="GTiff",
        height=256,
        width=256,
        count=1,
        dtype=arr.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(arr)
    (tmp_path / "test.cog.json").write_text(json.dumps({"bbox": [-180, -90, 180, 90]}))


def test_real_render(tmp_path: Path) -> None:
    pytest.importorskip("rio_tiler")
    pytest.importorskip("rasterio")
    _make_cog(tmp_path)
    reg.scan([tmp_path])
    client = TestClient(app)
    resp = client.get("/tiles/geotiff/test/0/0/0.png")
    assert resp.status_code == 200
    assert resp.headers["X-Tile-Cache"] == "miss"
