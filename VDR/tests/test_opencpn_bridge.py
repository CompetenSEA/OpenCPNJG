from __future__ import annotations

from pathlib import Path
import pytest

pytestmark = pytest.mark.bridge

# Skip if bridge is not available
opencpn_bridge = pytest.importorskip("opencpn_bridge")

DATA_DIR = Path(__file__).resolve().parent.parent / "testdata"


@pytest.fixture
def senc_file(tmp_path: Path) -> Path:
    """Build a temporary SENC file from the sample dataset."""
    src = DATA_DIR / "sample.000"
    if not src.exists():
        pytest.skip("sample dataset missing")
    dest = tmp_path / "sample.senc"
    opencpn_bridge.build_senc(str(src), str(dest))  # type: ignore[attr-defined]
    return dest


def test_build_senc_creates_output(senc_file: Path) -> None:
    assert senc_file.exists()
    assert senc_file.stat().st_size > 0


def test_query_features_returns_features(senc_file: Path) -> None:
    bbox = (-180.0, -90.0, 180.0, 90.0)
    features = list(opencpn_bridge.query_features(str(senc_file), bbox))  # type: ignore[attr-defined]
    assert features
