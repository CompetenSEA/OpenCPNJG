import logging
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from cm93_importer import run_cm93_convert


def test_cm93_convert_fallback(tmp_path, monkeypatch, caplog):
    """Importer should fall back when the native CLI is missing."""
    monkeypatch.delenv("OPENCN_CM93_CLI", raising=False)
    monkeypatch.setenv("PATH", "", prepend=False)
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "out"
    with caplog.at_level(logging.INFO):
        assert not run_cm93_convert(src, out)
    assert "falling back to GDAL" in caplog.text
