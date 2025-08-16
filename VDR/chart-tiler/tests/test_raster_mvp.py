import io
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tileserver

client = TestClient(tileserver.app)

PIL = pytest.importorskip("PIL.Image")
from PIL import Image  # type: ignore


def test_png_mvp(tmp_path: Path) -> None:
    r = client.get("/tiles/cm93/0/0/0.png?fmt=png-mvp")
    assert r.status_code == 200
    img = Image.open(io.BytesIO(r.content))
    assert img.size[0] > 1 and img.size[1] > 1
    pixels = list(img.getdata())
    assert any(p[:3] == (1, 2, 3) for p in pixels)
    assert any(p[:3] == (4, 5, 6) for p in pixels)
