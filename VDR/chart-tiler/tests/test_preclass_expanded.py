from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from s52_preclass import S52PreClassifier, ContourConfig


def _classifier(cfg=None):
    cfg = cfg or ContourConfig(hazardBuffer=25.0, safety=10.0, shallow=5.0, deep=30.0)
    return S52PreClassifier(cfg, colors={}, symbols={})


def test_rotated_beacon() -> None:
    cls = _classifier()
    props = {'CAT': 1, 'ORIENT': 90, 'OBJNAM': 'Beacon'}
    res = cls.classify('BCNLAT', props)
    assert res['navaidIcon'].startswith('BCNLAT')
    assert res['orient'] == 90
    assert res['name'] == 'Beacon'


def test_intertidal_hazard_icon() -> None:
    cls = _classifier()
    props = {'VALSOU': 1, 'WATLEV': 2}
    res = cls.classify('OBSTRN', props)
    assert res['hazardIcon']
    assert res['hazardWatlev'] == 2
    assert res['hazardBuffer'] == 25.0


def test_safety_nearest_depcnt() -> None:
    cls = _classifier()
    a = cls.classify('DEPCNT', {'VALDCO': 8})
    b = cls.classify('DEPCNT', {'VALDCO': 12})
    cls.finalize()
    assert a['role'] == 'safety' or b['role'] == 'safety'
    assert a['role'] != b['role']


def test_dashed_cable_hint() -> None:
    cls = _classifier()
    res = cls.classify('CBLARE', {'lnstl': 'dash'})
    assert res['linePattern'] == 'dash'
