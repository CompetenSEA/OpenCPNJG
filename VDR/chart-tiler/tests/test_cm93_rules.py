import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from cm93_rules import zoom_band_for, apply_scamin


def test_zoom_band_membership():
    assert zoom_band_for("LNDARE") == "overview"
    assert zoom_band_for("SOUNDG") == "harbor"
    assert zoom_band_for("UNKNOWN") is None


def test_apply_scamin():
    assert apply_scamin("SOUNDG", 12)
    assert not apply_scamin("SOUNDG", 8)
    assert apply_scamin("LNDARE", 0)
