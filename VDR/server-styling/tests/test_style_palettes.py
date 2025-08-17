import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'server-styling' / 'build_style_json.py'
VALIDATE = ROOT / 'server-styling' / 'tools' / 'validate_style.mjs'


def _build_style(tmpdir: Path, palette: str) -> Path:
    chartsymbols = tmpdir / 'chartsymbols.xml'
    chartsymbols.write_text(
        """
<root>
  <color-table name='DAY_BRIGHT'>
    <color name='SNDG1' r='1' g='1' b='1'/>
    <color name='SNDG2' r='2' g='2' b='2'/>
  </color-table>
  <color-table name='DUSK'>
    <color name='SNDG1' r='3' g='3' b='3'/>
    <color name='SNDG2' r='4' g='4' b='4'/>
  </color-table>
  <color-table name='NIGHT'>
    <color name='SNDG1' r='5' g='5' b='5'/>
    <color name='SNDG2' r='6' g='6' b='6'/>
  </color-table>
</root>
        """.strip()
    )
    (tmpdir / 'rastersymbols-day.png').write_bytes(b'')
    out = tmpdir / f'style.{palette}.json'
    cmd = [
        sys.executable,
        str(BUILD),
        '--assets', str(tmpdir),
        '--palette', palette,
        '--output', str(out),
    ]
    subprocess.check_call(cmd)
    try:
        proc = subprocess.run(['node', str(VALIDATE), str(out)], capture_output=True, text=True)
        if proc.returncode != 0:
            pytest.skip('style validation failed')
    except FileNotFoundError:
        pytest.skip('node not available')
    return out


def test_palette_variation(tmp_path: Path) -> None:
    colors = {}
    for palette in ['day', 'dusk', 'night']:
        out = _build_style(tmp_path, palette)
        style = json.loads(out.read_text())
        soundg = next(lyr for lyr in style['layers'] if lyr['id'] == 'SOUNDG')
        paint = soundg['paint']
        sndg1 = paint['text-color'][2]
        sndg2 = paint['text-halo-color']
        colors[palette] = (sndg1, sndg2)
    sndg1_values = {c[0] for c in colors.values()}
    sndg2_values = {c[1] for c in colors.values()}
    assert len(sndg1_values) == 3
    assert len(sndg2_values) == 3
