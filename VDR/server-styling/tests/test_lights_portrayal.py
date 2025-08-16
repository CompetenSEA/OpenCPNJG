import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "server-styling" / "build_style_json.py"


def _build(tmpdir: Path) -> Path:
    chartsymbols = tmpdir / "chartsymbols.xml"
    chartsymbols.write_text(
        """
<root>
  <color-table name='DAY_BRIGHT'>
    <color name='CHBLK' r='0' g='0' b='0'/>
  </color-table>
  <symbols>
    <symbol name='LIGHTS11'>
      <bitmap width='10' height='10' x='0' y='0'/>
    </symbol>
  </symbols>
  <lookups>
    <lookup name='LIGHTS'>
      <type>Point</type>
      <table-name>Plain</table-name>
      <instruction>SY(LIGHTS11)</instruction>
    </lookup>
  </lookups>
</root>
""".strip()
    )
    out = tmpdir / "style.json"
    cmd = [
        sys.executable,
        str(BUILD),
        "--chartsymbols",
        str(chartsymbols),
        "--tiles-url",
        "dummy",
        "--source-name",
        "src",
        "--source-layer",
        "lyr",
        "--sprite-base",
        "/sprites",
        "--glyphs",
        "/glyphs/{fontstack}/{range}.pbf",
        "--auto-cover",
        "--labels",
        "--output",
        str(out),
    ]
    subprocess.check_call(cmd)
    return out


def test_light_label_and_sector(tmp_path: Path) -> None:
    style_path = _build(tmp_path)
    style = json.loads(style_path.read_text())
    lights = next(lyr for lyr in style["layers"] if lyr["id"] == "LIGHTS")
    text_field = lights.get("layout", {}).get("text-field")
    assert "LITCHR" in json.dumps(text_field)
    sector = next(lyr for lyr in style["layers"] if lyr["id"] == "LIGHTS-sector")
    assert sector.get("metadata", {}).get("maplibre:s52") == "LIGHTS-LS(sector)"
