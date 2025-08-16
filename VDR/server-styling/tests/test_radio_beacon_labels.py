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
  </color-table>
  <symbols>
    <symbol name='RTPBCN02'>
      <bitmap width='10' height='10' x='0' y='0'/>
      <pivot x='5' y='5'/>
    </symbol>
  </symbols>
  <lookups>
    <lookup name='RTPBCN'/>
  </lookups>
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


def test_radio_beacon_has_label(tmp_path: Path) -> None:
    style_path = _build_style(tmp_path)
    style = json.loads(style_path.read_text())
    layer = next(lyr for lyr in style['layers'] if lyr['id'] == 'RTPBCN')
    layout = layer['layout']
    assert layout['icon-image'][0] == 'concat'
    # Ensure the symbol was resolved to RTPBCN02
    assert layout['icon-image'][2][-1] == 'RTPBCN02'
    # Labels enabled: text-field uses OBJNAM
    assert layout['text-field'][1] == ['get', 'OBJNAM']
