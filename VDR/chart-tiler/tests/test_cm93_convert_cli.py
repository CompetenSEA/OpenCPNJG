import os
import stat
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from cm93_importer import run_cm93_convert


def test_run_cm93_convert(tmp_path, monkeypatch):
    script = tmp_path / "cm93_convert"
    script.write_text(
        "#! /usr/bin/env python3\n"
        "import pathlib, sys\n"
        "out = pathlib.Path(sys.argv[sys.argv.index('--out')+1])\n"
        "out.mkdir(parents=True, exist_ok=True)\n"
        "(out/'pts.geojson').write_text('{}')\n"
    )
    script.chmod(stat.S_IRWXU)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ.get('PATH','')}")
    src = tmp_path / "src"; src.mkdir()
    out = tmp_path / "out"
    assert run_cm93_convert(src, out)
    assert (out / 'pts.geojson').exists()
