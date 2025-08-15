import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUILD_ALL = ROOT / "server-styling" / "tools" / "build_all_styles.py"
COVER = ROOT / "server-styling" / "s52_coverage.py"


def _have_node() -> bool:
    try:
        subprocess.run(["node", "--version"], stdout=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def test_coverage_floor(tmp_path: Path) -> None:
    chartsymbols = ROOT / "server-styling" / "dist" / "assets" / "s52" / "chartsymbols.xml"
    baseline = ROOT / "server-styling" / "dist" / "coverage" / "style_coverage.prev.json"
    if not chartsymbols.exists() or not baseline.exists() or not _have_node():
        pytest.skip("baseline or node missing")

    subprocess.check_call(
        [
            sys.executable,
            str(BUILD_ALL),
            "--chartsymbols",
            str(chartsymbols),
            "--tiles-url",
            "dummy",
            "--source-name",
            "src",
            "--source-layer",
            "lyr",
            "--sprite-base",
            "/sprites/s52-day",
            "--sprite-prefix",
            "s52-",
            "--glyphs",
            "/glyphs/{fontstack}/{range}.pbf",
        ]
    )
    subprocess.check_call(
        [
            sys.executable,
            str(COVER),
            "--chartsymbols",
            str(chartsymbols),
            "--baseline",
            str(baseline),
        ]
    )
    prev = json.loads(baseline.read_text())
    curr = json.loads(
        (ROOT / "server-styling" / "dist" / "coverage" / "style_coverage.json").read_text()
    )
    assert curr["coveredByStyle"] >= prev.get("coveredByStyle", 0) + 3

