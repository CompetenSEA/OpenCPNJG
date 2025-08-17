import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def test_s57_catalogue_parity() -> None:
    csv_path = ROOT / "server-styling" / "dist" / "assets" / "s52" / "s57objectclasses.csv"
    if not csv_path.exists():
        pytest.skip("s57 catalogue missing")
    report = ROOT / "server-styling" / "dist" / "coverage" / "s57_catalogue.json"
    if not report.exists():
        pytest.skip("coverage report missing")
    data = json.loads(report.read_text())
    for key in [
        "totalClasses",
        "s52Lookups",
        "handledByStyles",
        "missingClasses",
        "ignoredClasses",
    ]:
        assert key in data
    ignored = set(data.get("ignoredClasses", []))
    total = data.get("totalClasses", 0) - len(ignored)
    handled = data.get("handledByStyles", 0)
    assert handled >= total - 1

