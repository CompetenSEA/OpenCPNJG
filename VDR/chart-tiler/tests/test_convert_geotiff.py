import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from pathlib import Path
from unittest import mock

from tools import convert_geotiff


def fake_run(cmd, check, capture_output=False, text=False):
    class P:
        def __init__(self):
            self.stdout = (
                "Upper Left  (-180.0, 90.0)\n"
                "Lower Right (180.0,-90.0)\n"
                "EPSG:4326\n"
                "Pixel Size = (0.5,-0.5)\n"
                "Overviews: 256x256 128x128 64x64 32x32\n"
            )
    if cmd[0] == "gdal_translate":
        # create output file to satisfy checksum
        Path(cmd[-1]).write_bytes(b"cog")
        return P()
    return P()


def test_convert(tmp_path):
    tif = tmp_path / "in.tif"
    tif.write_bytes(b"dummy")
    convert_geotiff.DATA_DIR = tmp_path
    convert_geotiff.DATA_DIR.mkdir(exist_ok=True)
    with mock.patch("subprocess.run", side_effect=fake_run) as run:
        out = convert_geotiff.convert(tif)
        assert out.exists()
        sidecar = out.with_suffix(".json")
        info = json.loads(sidecar.read_text())
        assert info["bbox"] == [-180.0, -90.0, 180.0, 90.0]
        assert info["epsg"] == 4326
        assert len(info["overviews"]) >= 4
        # second run uses sidecar and does not call gdal again
        out2 = convert_geotiff.convert(tif)
        assert out2 == out
        assert run.call_count == 2
