import json, subprocess, sys, shutil
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "server-styling" / "build_style_json.py"
VALIDATE = ROOT / "server-styling" / "tools" / "validate_style.mjs"


def _build(tmpdir: Path) -> Path:
    chartsymbols = tmpdir / "chartsymbols.xml"
    chartsymbols.write_text(
        """
<root>
  <color-table name='DAY_BRIGHT'>
    <color name='CHBLK' r='0' g='0' b='0'/>
    <color name='LANDA' r='1' g='2' b='3'/>
  </color-table>
  <symbols>
    <symbol name='PNT1'>
      <bitmap width='10' height='10' x='0' y='0'/>
    </symbol>
  </symbols>
  <line-styles>
    <line-style name='DASH' color-ref='CHBLK' width='1' pattern='dash'/>
  </line-styles>
  <patterns>
    <pattern name='PAT1'>
      <bitmap width='10' height='10' x='0' y='0'/>
    </pattern>
  </patterns>
  <lookups>
    <lookup name='OBJPT'>
      <type>Point</type>
      <table-name>Plain</table-name>
      <instruction>SY(PNT1)</instruction>
    </lookup>
    <lookup name='OBJLN'>
      <type>Line</type>
      <table-name>Plain</table-name>
      <instruction>LS(DASH,1,CHBLK)</instruction>
    </lookup>
    <lookup name='OBJAR'>
      <type>Area</type>
      <table-name>Plain</table-name>
      <instruction>AC(LANDA);AP(PAT1)</instruction>
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
        "--output",
        str(out),
    ]
    subprocess.check_call(cmd)
    return out


def test_auto_cover(tmp_path: Path) -> None:
    style_path = _build(tmp_path)
    style = json.loads(style_path.read_text())
    ids = {lyr["id"] for lyr in style["layers"]}
    assert {"OBJPT", "OBJLN", "OBJAR"} <= ids
    node = shutil.which("node")
    if node:
        try:
            subprocess.check_call(
                [node, "-e", "require.resolve('@maplibre/maplibre-gl-style-spec')"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            pytest.skip("validator not installed")
        subprocess.check_call([node, str(VALIDATE), str(style_path)])
    else:
        pytest.skip("node not installed")


def test_presence_coverage_real_assets() -> None:
    cov_path = ROOT / "server-styling" / "dist" / "coverage" / "style_coverage.json"
    if not cov_path.exists():
        pytest.skip("coverage data missing")
    data = json.loads(cov_path.read_text())
    assert data.get("coveredByStyle") == data.get("totalLookups")
