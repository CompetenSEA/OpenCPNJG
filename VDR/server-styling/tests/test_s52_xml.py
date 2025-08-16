import xml.etree.ElementTree as ET
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'server-styling'))

from s52_xml import (
    parse_symbols,
    parse_linestyles,
    parse_lookups,
    parse_s57_catalogue,
    parse_s57_attributes,
)
import pytest


def test_chartsymbols_parsing():
    path = ROOT / 'server-styling' / 'dist' / 'assets' / 's52' / 'chartsymbols.xml'
    if not path.exists():
        pytest.skip('chartsymbols missing')
    root = ET.parse(path).getroot()
    symbols = parse_symbols(root)
    assert len(symbols) >= 300
    linestyles = parse_linestyles(root)
    assert len(linestyles) >= 50
    lookups = parse_lookups(root)
    objs = {l['objl'] for l in lookups}
    for name in ['DEPARE', 'DEPCNT', 'COALNE', 'SOUNDG']:
        assert name in objs


def test_symbol_anchor_and_rotation():
    path = ROOT / 'server-styling' / 'dist' / 'assets' / 's52' / 'chartsymbols.xml'
    if not path.exists():
        pytest.skip('chartsymbols missing')
    root = ET.parse(path).getroot()
    symbols = parse_symbols(root)
    sym = symbols.get('ISODGR51')
    if not sym or 'anchor' not in sym:
        pytest.skip('ISODGR51 anchor missing in this chartsymbols.xml')
    assert sym['anchor'] == (9, 9)


def test_symbol_rotation_flag():
    path = ROOT / 'server-styling' / 'dist' / 'assets' / 's52' / 'chartsymbols.xml'
    if not path.exists():
        pytest.skip('chartsymbols missing')
    root = ET.parse(path).getroot()
    symbols = parse_symbols(root)
    sym = symbols.get('LITVES03')
    if not sym or 'rotate' not in sym:
        pytest.skip('LITVES03 rotation flag missing in this chartsymbols.xml')
    assert sym['rotate'] is True


def test_s57_catalogue_and_attributes():
    data_dir = ROOT.parent / 'data' / 's57data'
    cat_path = data_dir / 's57objectclasses.csv'
    attr_path = data_dir / 's57attributes.csv'
    if not cat_path.exists() or not attr_path.exists():
        pytest.skip('s57 CSV catalogues missing')
    catalogue = parse_s57_catalogue(cat_path)
    assert catalogue.get('BCNCAR') == {'P'}
    assert 'L' in catalogue.get('DEPCNT', set())
    attrs = parse_s57_attributes(attr_path)
    for key in ['OBJNAM', 'NOBJNM', 'QUAPOS', 'WATLEV', 'SCAMIN', 'ORIENT']:
        assert key in attrs
    assert attrs['OBJNAM']['type'] == 'S'
