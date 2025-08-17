from __future__ import annotations

import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import registry


def _stub_bridge(tmp_path: Path) -> None:
    mod = types.ModuleType("opencpn_bridge")

    def build_senc(src: str, dst: str, provenance_path: str | None = None) -> None:
        Path(dst).write_text("senc")
        if provenance_path:
            Path(provenance_path).write_text(json.dumps({}))

    def query_features(path: str) -> dict[str, object]:
        return {"bbox": [0.0, 0.0, 1.0, 1.0], "scale_min": 1000, "scale_max": 2000}

    mod.build_senc = build_senc  # type: ignore[attr-defined]
    mod.query_features = query_features  # type: ignore[attr-defined]
    sys.modules["opencpn_bridge"] = mod


def test_registry_entry_after_ingest(tmp_path, monkeypatch):
    _stub_bridge(tmp_path)
    monkeypatch.setattr(registry, "DB_PATH", tmp_path / "registry.sqlite")
    registry._registry = None

    import opencpn_ingest

    monkeypatch.setattr(opencpn_ingest, "ASSETS_DIR", tmp_path)
    src = tmp_path / "src"
    src.mkdir()
    opencpn_ingest.ingest(src, "ds1")

    reg = registry.get_registry()
    rec = reg.get("ds1")
    from opencpn_ingest import _scale_to_zoom
    assert rec is not None
    assert rec.bbox == [0.0, 0.0, 1.0, 1.0]
    assert rec.minzoom == _scale_to_zoom(2000)
    assert rec.maxzoom == _scale_to_zoom(1000)
    assert rec.senc_path and Path(rec.senc_path).exists()
    assert rec.provenance_path and Path(rec.provenance_path).exists()
