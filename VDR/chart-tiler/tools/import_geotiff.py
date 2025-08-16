from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from registry import get_registry
from tools import convert_geotiff


def _have_gdal() -> bool:
    return shutil.which("gdal_translate") is not None


def import_file(src: Path) -> Path:
    if not _have_gdal():
        print("SKIP: GDAL tools missing", file=sys.stderr)
        return src
    cog = convert_geotiff.convert(src)
    reg = get_registry()
    reg.register_cog(cog.with_suffix(".json"), cog)
    return cog


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    args = ap.parse_args(argv)
    import_file(args.src)


if __name__ == "__main__":
    main()
