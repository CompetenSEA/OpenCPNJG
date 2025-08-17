from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer

from convert_charts import encode_s57_to_mbtiles

# Default ENC dataset directory; override with ENC_DIR env var at runtime.
_DEFAULT_DIR = Path(__file__).resolve().parent / "data" / "enc"
ENC_DIR = Path(os.environ.get("ENC_DIR", _DEFAULT_DIR))

app = typer.Typer()


def _load_cell_to_db(src: Path, dsn: str) -> None:
    """Load ``src`` S-57 cell into ``enc_*`` tables of ``dsn`` database."""
    layer = src.stem.upper()
    table = f"enc_{layer.lower()}"
    subprocess.run(
        [
            "ogr2ogr",
            "-append",
            "-f",
            "SQLite",
            dsn,
            str(src),
            "-nln",
            table,
            "-sql",
            f"SELECT *, CAST(OBJL AS INTEGER) AS OBJL FROM {layer}",
        ],
        check=True,
    )


def import_s57(
    src: Path,
    dsn: str,
    dataset_id: str | None = None,
    *,
    respect_scamin: bool = True,
    minzoom: int = 5,
    maxzoom: int = 14,
) -> Path:
    """Encode ``src`` to MBTiles and load its features into ``dsn``."""

    src = Path(src)
    dataset_id = dataset_id or src.stem.lower()
    enc_dir = Path(ENC_DIR)
    enc_dir.mkdir(parents=True, exist_ok=True)
    out = enc_dir / f"{dataset_id}.mbtiles"
    tmp = out.with_suffix(".tmp.mbtiles")
    encode_s57_to_mbtiles(
        str(src),
        str(tmp),
        respect_scamin=respect_scamin,
        minzoom=minzoom,
        maxzoom=maxzoom,
    )
    tmp.rename(out)
    _load_cell_to_db(src, dsn)
    return out


@app.command("import-enc")
def import_enc_cli(source: Path, dsn: str) -> None:
    """Import all S-57 cells from ``source`` into ``dsn``."""
    for cell in sorted(Path(source).glob("*.000")):
        mbtiles = import_s57(cell, dsn=dsn)
        print(mbtiles)


if __name__ == "__main__":
    app()
