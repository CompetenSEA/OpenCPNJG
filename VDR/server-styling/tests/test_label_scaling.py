import json
import subprocess
import sys
from pathlib import Path


def _build_style(tmp_path: Path) -> dict:
    chartsymbols = tmp_path / "chartsymbols.xml"
    chartsymbols.write_text(
        """
<root><color-table name='DAY_BRIGHT'>
  <color name='SNDG1' r='1' g='1' b='1'/>
  <color name='SNDG2' r='2' g='2' b='2'/>
  <color name='CHBLK' r='0' g='0' b='0'/>
</color-table></root>
"""
    )
    (tmp_path / "rastersymbols-day.png").write_bytes(b"")
    out = tmp_path / "style.json"
    build = Path(__file__).resolve().parents[2] / "server-styling" / "build_style_json.py"
    cmd = [
        sys.executable,
        str(build),
        "--assets",
        str(tmp_path),
        "--labels",
        "--output",
        str(out),
    ]
    subprocess.check_call(cmd)
    return json.loads(out.read_text())


def test_soundg_scaling(tmp_path: Path) -> None:
    style = _build_style(tmp_path)
    soundg = next(lyr for lyr in style["layers"] if lyr["id"] == "SOUNDG")
    size = soundg["layout"]["text-size"]
    assert size[0] == "interpolate"
    assert soundg.get("minzoom", 0) >= 10


def test_seamark_name_layer(tmp_path: Path) -> None:
    style = _build_style(tmp_path)
    seamark = next(
        lyr
        for lyr in style["layers"]
        if lyr.get("metadata", {}).get("maplibre:s52") == "NAVAID-SY(nameLabel)"
    )
    assert seamark.get("minzoom", 0) >= 11
