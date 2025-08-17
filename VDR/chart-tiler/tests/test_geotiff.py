import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ingest_charts  # type: ignore
import raster_mvp  # type: ignore

PIL = pytest.importorskip("PIL.Image")
from PIL import Image  # type: ignore


def test_ensure_cog_converts_non_cog(tmp_path: Path) -> None:
    tif = tmp_path / "in.tif"
    tif.write_bytes(b"x")

    def fake_run(cmd, check, capture_output=False, text=False):
        class P:
            stdout = ""
        if cmd[0] == "gdalinfo":
            return P()
        if cmd[0] == "gdal_translate":
            Path(cmd[-1]).write_bytes(b"cog")
            return P()
        raise AssertionError(cmd)

    with mock.patch("subprocess.run", side_effect=fake_run) as run:
        out = ingest_charts.ensure_cog(tif)
        assert out.exists()
    assert run.call_args_list[0][0][0][0] == "gdalinfo"
    assert run.call_args_list[1][0][0][0] == "gdal_translate"


def test_ensure_cog_skips_when_cog(tmp_path: Path) -> None:
    tif = tmp_path / "in.tif"
    tif.write_bytes(b"x")

    def fake_run(cmd, check, capture_output=False, text=False):
        class P:
            stdout = "Cloud Optimized GeoTIFF"
        if cmd[0] == "gdalinfo":
            return P()
        raise AssertionError(cmd)

    with mock.patch("subprocess.run", side_effect=fake_run) as run:
        out = ingest_charts.ensure_cog(tif)
        assert out == tif
    assert run.call_count == 1


def test_resample_image_respects_metadata(monkeypatch):
    img = Image.new("L", (1, 1), color=1)
    calls = []
    orig_resize = Image.Image.resize

    def fake_resize(self, size, resample=None, *args, **kwargs):
        calls.append(resample)
        return orig_resize(self, size, resample=resample, *args, **kwargs)

    monkeypatch.setattr(Image.Image, "resize", fake_resize)
    raster_mvp.resample_image(img, nodata=None, categorical=True)
    out = raster_mvp.resample_image(Image.new("L", (1, 1), color=1), nodata=1, categorical=False)
    assert calls[0] == Image.NEAREST
    assert calls[1] == Image.BILINEAR
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 0
