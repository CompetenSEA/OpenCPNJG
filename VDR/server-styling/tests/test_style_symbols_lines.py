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
    <symbol name='BCNLAT' rotatable='yes'>
      <bitmap width='10' height='10' x='0' y='0'/>
      <pivot x='2' y='3'/>
    </symbol>
  </symbols>
  <line-styles>
    <line-style name='CBLARE' color-ref='CHBLK' width='1' pattern='dash'/>
  </line-styles>
  <lookups>
    <lookup name='BCNLAT'/>
    <lookup name='CBLARE'/>
  </lookups>
</root>
        """.strip()
    )
    (tmpdir / "rastersymbols-day.png").write_bytes(b"")
    out = tmpdir / "style.json"
    cmd = [
        sys.executable,
        str(BUILD),
        "--assets",
        str(tmpdir),
        "--output",
        str(out),
    ]
    subprocess.check_call(cmd)
    return out


def test_symbol_anchor_and_line_dash(tmp_path: Path) -> None:
    style_path = _build(tmp_path)
    style = json.loads(style_path.read_text())
    bcn = next(lyr for lyr in style["layers"] if lyr["id"] == "BCNLAT")
    layout = bcn["layout"]
    assert layout["icon-image"][0] == "concat"
    assert layout.get("icon-offset") not in ([0, 0], None)
    assert "icon-rotate" in layout

    line = next(lyr for lyr in style["layers"] if lyr["id"] == "CBLARE")
    assert line["paint"].get("line-dasharray")

