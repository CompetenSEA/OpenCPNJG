import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'server-styling' / 'build_style_json.py'


def _build_style(tmpdir: Path) -> Path:
    chartsymbols = tmpdir / 'chartsymbols.xml'
    chartsymbols.write_text(
        """
<root>
  <color-table name='DAY_BRIGHT'>
    <color name='CHBLK' r='0' g='0' b='0'/>
    <color name='LANDA' r='1' g='1' b='1'/>
  </color-table>
</root>
        """.strip()
    )
    (tmpdir / 'rastersymbols-day.png').write_bytes(b'')
    out = tmpdir / 'style.json'
    cmd = [
        sys.executable,
        str(BUILD),
        '--assets', str(tmpdir),
        '--labels',
        '--output', str(out),
    ]
    subprocess.check_call(cmd)
    return out


def test_feature_name_layer(tmp_path: Path) -> None:
    out = _build_style(tmp_path)
    style = json.loads(out.read_text())
    layer = next((lyr for lyr in style['layers'] if lyr['id'] == 'feature-names'), None)
    assert layer is not None
    layout = layer['layout']
    assert layout['text-field'][0] == 'coalesce'
    ts = layout['text-size']
    assert ts[0] == 'interpolate'
    # zoom, size pairs
    assert ts[3] == 5 and ts[4] == 12
    assert ts[5] == 12 and ts[6] == 16
