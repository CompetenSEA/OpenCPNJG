import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "charts_py" / "src"))
from fastapi.testclient import TestClient
import tileserver

client = TestClient(tileserver.app)

def test_tile_endpoint_png():
    r = client.get("/tiles/cm93/0/0/0?fmt=png&palette=day&safetyContour=0")
    assert r.status_code == 200
    assert r.content.startswith(b"\x89PNG")


def test_tile_endpoint_mvt():
    r = client.get("/tiles/cm93/0/0/0?fmt=mvt&palette=day&safetyContour=10")
    assert r.status_code == 200
    from mapbox_vector_tile import decode

    tile = decode(r.content)
    assert "SOUNDG" in tile
    props = tile["SOUNDG"]["features"][0]["properties"]
    assert "isShallow" in props

def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"tile_gen_ms" in r.content


def test_cache_hits_metric():
    import re

    # First call primes the cache; second should be served from the LRU cache.
    client.get("/tiles/cm93/0/0/0?fmt=png&palette=day&safetyContour=0")
    client.get("/tiles/cm93/0/0/0?fmt=png&palette=day&safetyContour=0")
    metrics = client.get("/metrics").text
    match = re.search(r"cache_hits_total\s+(\d+)", metrics)
    assert match and int(match.group(1)) >= 1
