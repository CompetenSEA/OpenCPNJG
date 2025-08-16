import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_style() -> dict:
    style_path = ROOT / 'server-styling' / 'dist' / 'style.s52.day.json'
    if not style_path.exists():
        pytest.skip('style not built')
    return json.loads(style_path.read_text())


def test_depth_contours_and_soundings():
    style = _load_style()
    safety = next(lyr for lyr in style['layers'] if lyr['id'] == 'DEPCNT-safety')
    assert safety.get('paint', {}).get('line-width') == 2
    lowacc = next(lyr for lyr in style['layers'] if lyr['id'] == 'DEPCNT-lowacc')
    assert 'line-dasharray' in lowacc.get('paint', {})
    soundg = next(lyr for lyr in style['layers'] if lyr['id'] == 'SOUNDG')
    assert 'number-format' in json.dumps(soundg.get('layout', {}).get('text-field'))


def test_hazard_icons():
    style = _load_style()
    hazard = next(lyr for lyr in style['layers'] if lyr['id'] == 'udw-hazards')
    icon_expr = json.dumps(hazard.get('layout', {}).get('icon-image'))
    assert 'DANGER' in icon_expr
    assert 'WATLEV' in icon_expr
    assert 'maplibre:s52Fallback' not in hazard.get('metadata', {})
