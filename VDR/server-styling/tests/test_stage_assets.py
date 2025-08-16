"""Tests for ``stage_local_assets.py``.

The test exercises the staging helper using repository‑local assets.  It is
written to be skip‑safe – if the ``data/s57data`` directory is missing the
test will skip rather than fail so CI environments without the data can still
run the rest of the suite.
"""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
SCRIPT = ROOT / "server-styling" / "tools" / "stage_local_assets.py"

ASSETS = [
    "chartsymbols.xml",
    "rastersymbols-day.png",
    "S52RAZDS.RLE",
    "s57objectclasses.csv",
    "s57attributes.csv",
    "attdecode.csv",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_stage_assets(tmp_path: Path) -> None:
    repo_data = REPO_ROOT / "data" / "s57data"
    if not repo_data.exists():
        pytest.skip("s57 data missing")

    dest = tmp_path / "assets" / "s52"
    subprocess.check_call(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-data",
            str(repo_data),
            "--dest",
            str(dest),
            "--force",
        ]
    )

    manifest_path = dest / "assets.manifest.json"
    with manifest_path.open() as fh:
        manifest = json.load(fh)

    assert set(manifest) == set(ASSETS)
    for name in ASSETS:
        file_path = dest / name
        assert file_path.is_file()
        assert manifest[name] == _sha256(file_path)

