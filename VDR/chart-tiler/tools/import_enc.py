from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from convert_charts import encode_s57_to_mbtiles

# Default ENC dataset directory; override with ENC_DIR env var at runtime.
ENC_DIR = Path(__file__).resolve().parents[1] / "data" / "enc"


def import_s57(
    src: Path,
    dataset_id: Optional[str] = None,
    *,
    respect_scamin: bool = True,
    minzoom: int = 5,
    maxzoom: int = 14,
) -> Path:
    """Encode ``src`` S-57 cell to MBTiles and move into the ENC directory."""

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
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--id", help="Dataset identifier")
    ap.add_argument("--no-respect-scamin", dest="respect_scamin", action="store_false")
    ap.set_defaults(respect_scamin=True)
    ap.add_argument("--minzoom", type=int, default=5)
    ap.add_argument("--maxzoom", type=int, default=14)
    args = ap.parse_args(argv)
    import_s57(
        args.src,
        dataset_id=args.id,
        respect_scamin=args.respect_scamin,
        minzoom=args.minzoom,
        maxzoom=args.maxzoom,
    )


if __name__ == "__main__":
    main()
