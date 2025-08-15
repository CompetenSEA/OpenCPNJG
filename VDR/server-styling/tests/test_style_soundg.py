import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'server-styling'))
from s52_xml import parse_day_colors


def test_soundg_day_tokens():
    style_path = ROOT / 'server-styling' / 'dist' / 'style.s52.day.json'
    chartsymbols = ROOT / 'server-styling' / 'dist' / 'assets' / 's52' / 'chartsymbols.xml'
    if not style_path.exists() or not chartsymbols.exists():
        pytest.skip('style or chartsymbols missing')
    style = json.loads(style_path.read_text())
    root = ET.parse(chartsymbols).getroot()
    colors = parse_day_colors(root)
    sndg1 = colors.get('SNDG1')
    sndg2 = colors.get('SNDG2')
    assert sndg1 and sndg2
    soundg = next(lyr for lyr in style['layers'] if lyr['id'] == 'SOUNDG')
    paint = soundg.get('paint', {})
    assert sndg1 in paint.get('text-color', [])
    assert paint.get('text-halo-color') == sndg2
