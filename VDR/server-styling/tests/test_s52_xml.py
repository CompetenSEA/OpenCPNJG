import xml.etree.ElementTree as ET
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'server-styling'))

from s52_xml import parse_symbols, parse_linestyles, parse_lookups


def test_chartsymbols_parsing():
    path = ROOT / 'server-styling' / 'dist' / 'assets' / 's52' / 'chartsymbols.xml'
    root = ET.parse(path).getroot()
    symbols = parse_symbols(root)
    assert len(symbols) >= 300
    linestyles = parse_linestyles(root)
    assert len(linestyles) >= 50
    lookups = parse_lookups(root)
    objs = {l['objl'] for l in lookups}
    for name in ['DEPARE', 'DEPCNT', 'COALNE', 'SOUNDG']:
        assert name in objs
