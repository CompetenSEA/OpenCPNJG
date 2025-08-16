from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from convert_charts import scamin_to_zoom, _SCAMIN_ZOOM_MAP  # noqa:E402


def test_scamin_table_mapping() -> None:
    for scale, zoom in _SCAMIN_ZOOM_MAP.items():
        assert scamin_to_zoom(scale) == zoom


def test_monotonic_and_clamped() -> None:
    values = [scamin_to_zoom(s) for s in sorted(_SCAMIN_ZOOM_MAP.keys(), reverse=True)]
    assert values == sorted(values)
    assert scamin_to_zoom(1000) == 16
    assert scamin_to_zoom(100000000) == 0
