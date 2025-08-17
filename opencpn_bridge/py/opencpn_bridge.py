from pathlib import Path


def build_senc(chart_path: str, output_dir: str) -> str:  # pragma: no cover - stub
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    (Path(output_dir) / "provenance.json").write_text('{"stub": true}\n')
    return output_dir


def query_tile_mvt(senc_root: str, z: int, x: int, y: int) -> bytes:  # pragma: no cover - stub
    return b""
