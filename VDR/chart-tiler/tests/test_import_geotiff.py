import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import registry as regmod  # type: ignore
from registry import Registry  # type: ignore
from tools import import_geotiff  # type: ignore


def fake_convert(path: Path, tmp_dir: Path) -> Path:
    out = tmp_dir / f"{path.stem}.cog.tif"
    out.write_bytes(b"cog")
    sidecar = out.with_suffix(".json")
    sidecar.write_text(json.dumps({"bbox": [0, 0, 1, 1]}))
    return out


def test_import_geotiff(tmp_path: Path, monkeypatch):
    tif = tmp_path / "in.tif"
    tif.write_bytes(b"x")
    monkeypatch.setattr(import_geotiff, "_have_gdal", lambda: True)
    monkeypatch.setattr(regmod, "DB_PATH", tmp_path / "r.sqlite")
    reg = Registry(regmod.DB_PATH)
    regmod._registry = reg
    monkeypatch.setattr(import_geotiff.convert_geotiff, "convert", lambda p: fake_convert(p, tmp_path))
    import_geotiff.import_file(tif)
    items = reg.list(kind="geotiff")
    assert items and items[0].id == "in"
