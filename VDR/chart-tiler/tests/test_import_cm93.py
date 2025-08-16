import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import import_cm93  # type: ignore

if "OPENCN_CM93_CLI" not in os.environ:
    pytest.skip("OPENCN_CM93_CLI not set", allow_module_level=True)


def test_import_cm93_placeholder(tmp_path):
    # This test only runs when the external CM93 adapter is available.
    src = tmp_path / "cm93"
    src.mkdir()
    import_cm93.import_tree(src)
