import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_csp_mapping_threshold():
    cov_path = ROOT / 'server-styling' / 'dist' / 'coverage' / 'csp_coverage.json'
    if not cov_path.exists():
        pytest.skip('coverage data missing')
    data = json.loads(cov_path.read_text())
    assert data.get('coverage', 0) >= 0.85
