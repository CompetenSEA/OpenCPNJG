import sys
import gzip
import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure modules are importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ingest_charts  # noqa: E402  # isort:skip
import tileserver  # noqa: E402  # isort:skip

TILES = [
    ("/tiles/cm93/0/0/0.png?sc=10", 100, "13cdf73d971c90b0394dd0a268b8b8d3f930ee7ca36f1a7d04c8d90ebb238346"),
    (
        "/tiles/cm93/0/0/0?fmt=mvt&sc=10",
        300,
        "1b890b03e9622ecaccd0809783b1824bbaf363325366b79da5cee0bdeffa87e9",
    ),
    ("/tiles/cm93-core/12/0/0.pbf", 300, "e4f074fc13a65fe58c0baf7fddfc2f0dd88c57d90388b9ae81b1f15cd0d4844b"),
]


@pytest.mark.integration
def test_tiles_have_size_and_hash(tmp_path):
    """Ingest tiny datasets and verify tile responses."""

    # Ingest chart dictionary to simulate dataset setup; fall back gracefully
    try:
        ingest_charts.main(tmp_path / "charts.sqlite")
    except Exception:
        # charts_py helpers may be unavailable in minimal environments
        pass

    client = TestClient(tileserver.app)
    for url, limit, expected_hash in TILES:
        resp = client.get(url)
        assert resp.status_code == 200, url

        gz_size = len(gzip.compress(resp.content))
        assert gz_size < limit, f"{url} exceeds gzip budget"

        digest = hashlib.sha256(resp.content).hexdigest()
        assert digest == expected_hash, f"{url} content changed"
