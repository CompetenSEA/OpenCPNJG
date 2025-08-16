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
    out = tmpdir / 'style.json'
    cmd = [
        sys.executable,
        str(BUILD),
        '--chartsymbols', str(chartsymbols),
        '--tiles-url', 'dummy',
        '--source-name', 'src',
        '--source-layer', 'lyr',
        '--sprite-base', '/sprites',
        '--glyphs', '/glyphs/{fontstack}/{range}.pbf',
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
    assert layout['text-size'][0] == 'interpolate'
