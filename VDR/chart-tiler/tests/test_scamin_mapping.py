from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import convert_charts
from convert_charts import scamin_to_zoom, _SCAMIN_ZOOM_MAP  # noqa:E402


def test_scamin_table_mapping() -> None:
    for scale, zoom in _SCAMIN_ZOOM_MAP.items():
        assert scamin_to_zoom(scale) == zoom


def test_monotonic_and_clamped() -> None:
    values = [scamin_to_zoom(s) for s in sorted(_SCAMIN_ZOOM_MAP.keys(), reverse=True)]
    assert values == sorted(values)
    assert scamin_to_zoom(1000) == 16
    assert scamin_to_zoom(100000000) == 0


def test_respect_scamin_default(monkeypatch, tmp_path) -> None:
    calls = {}

    def fake_s57_to_mbtiles(path, mbtiles, respect_scamin=True, scamin_map=None, minzoom=5, maxzoom=14):
        calls["respect"] = respect_scamin

    def fake_s57_to_cog(*args, **kwargs):
        pass

    def fake_layers(path):  # pragma: no cover - stub
        return ["L1"]

    monkeypatch.setattr(convert_charts, "_s57_layers", fake_layers)
    monkeypatch.setattr(convert_charts, "s57_to_mbtiles", fake_s57_to_mbtiles)
    monkeypatch.setattr(convert_charts, "s57_to_cog", fake_s57_to_cog)

    chart = tmp_path / "chart.000"
    chart.write_text("")
    out_dir = tmp_path / "out"

    convert_charts.main([str(chart), str(out_dir)])
    assert calls["respect"] is True

    convert_charts.main([str(chart), str(out_dir / "o2"), "--no-respect-scamin"])
    assert calls["respect"] is False
