#!/usr/bin/env python3
"""Convert CM93 or S-57 charts to vector MBTiles and raster COG tiles.

This module provides a command line utility and reusable functions for turning
S-57 (and CM93 after optional conversion) datasets into vector and raster tile
sets.  Vector tiles are generated as MBTiles using the `tippecanoe` command line
utility.  Raster tiles are produced as Cloud Optimized GeoTIFFs using GDAL.

The implementation is intentionally pure Python – no bindings to the original
C++ rendering engine are used.  All heavy lifting is delegated to widely
available command line tools which have Python bindings.

Example
-------
    $ python convert_charts.py ENC_ROOT/US5MD11M.000 out_dir

The script will generate two files inside ``out_dir``:
``US5MD11M.mbtiles`` (vector tiles) and ``US5MD11M.tif`` (COG raster).

Uploading to a remote Hostinger VPS is optional and can be enabled with the
``--upload`` flag together with SSH credentials.  The upload uses SFTP over
paramiko.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Iterable, Optional, List, Dict

import csv
from pathlib import Path

try:  # pragma: no cover - GDAL optional in tests
    from osgeo import gdal, ogr
except Exception:  # pragma: no cover
    gdal = None  # type: ignore
    ogr = None  # type: ignore


@dataclass
class UploadTarget:
    """Connection information for an SFTP upload."""

    host: str
    username: str
    password: str
    remote_dir: str = "."


# ---------------------------------------------------------------------------
# S-57 handling
# ---------------------------------------------------------------------------


def _s57_layers(path: str) -> Iterable[str]:
    """Return layer names in an S-57 dataset."""

    ds = ogr.Open(path)
    if ds is None:
        raise RuntimeError(f"Unable to open S-57 dataset: {path}")
    return [ds.GetLayer(i).GetName() for i in range(ds.GetLayerCount())]


def _named_attributes() -> List[str]:
    """Return attribute acronyms considered object names.

    The attribute definitions are sourced from ``s57attributes.csv`` which is
    part of the OpenCPN distribution.  Only the ``OBJNAM`` and ``NOBJNM``
    acronyms are currently recognised.  The function gracefully handles a
    missing catalogue file so that the tiler can operate in constrained test
    environments.
    """

    attrs: List[str] = []
    csv_path = Path(__file__).resolve().parents[2] / "data" / "s57data" / "s57attributes.csv"
    if not csv_path.exists():
        return attrs
    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            acronym = row.get("Acronym") or row.get("ACRONYM") or row.get("Attribute")
            if acronym in {"OBJNAM", "NOBJNM"}:
                attrs.append(acronym)
    return attrs


_SCAMIN_ZOOM_MAP: Dict[int, int] = {
    50000000: 0,
    20000000: 2,
    12000000: 3,
    6000000: 4,
    3000000: 5,
    1500000: 6,
    700000: 7,
    350000: 8,
    180000: 9,
    90000: 10,
    45000: 11,
    22000: 12,
    12000: 13,
    8000: 14,
    4000: 15,
    2000: 16,
}


def scamin_to_zoom(scamin: float, mapping: Optional[Dict[int, int]] = None) -> int:
    """Map an S-57 ``SCAMIN`` value (scale denominator) to a WebMercator zoom."""

    if scamin is None:
        return 0
    try:
        scamin_val = float(scamin)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return 0
    mapping = mapping or _SCAMIN_ZOOM_MAP
    # Iterate from largest scale denominator downwards
    for scale in sorted(mapping.keys(), reverse=True):
        if scamin_val >= scale:
            return max(0, min(16, mapping[scale]))
    # Smaller than smallest known scale -> max zoom
    return 16


def s57_to_cog(s57_path: str, output_tif: str) -> None:
    """Render an S-57 dataset to a Cloud Optimised GeoTIFF.

    The function uses GDAL's built in rasterisation to first render the vector
    layers into a temporary GeoTIFF and then translates it into a COG compliant
    file.  The output can be served directly by standard tile servers.
    """

    layers = _s57_layers(s57_path)
    if not layers:
        raise RuntimeError("No layers found in S-57 dataset")

    # Render to temporary raster using gdal.Rasterize
    tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
    tmp.close()

    gdal.Rasterize(
        tmp.name,
        s57_path,
        format="GTiff",
        outputType=gdal.GDT_Byte,
        allTouched=True,
        layers=layers,
    )

    # Translate to COG
    gdal.Translate(
        output_tif,
        tmp.name,
        format="COG",
        creationOptions=[
            "COMPRESS=LZW",
            "PREDICTOR=2",
            "OVERVIEWS=AUTO",
        ],
    )
    os.unlink(tmp.name)


def s57_to_mbtiles(
    s57_path: str,
    output_mbtiles: str,
    respect_scamin: bool = False,
    scamin_map: Optional[Dict[int, int]] = None,
) -> None:
    """Generate vector tiles from an S-57 dataset using tippecanoe.

    The S-57 features are first exported to GeoJSON using ``ogr2ogr`` and then
    piped to ``tippecanoe`` which builds the MBTiles database.  Both commands
    are invoked via ``subprocess`` to avoid any C++ dependencies.  When
    ``respect_scamin`` is true each feature gains a ``tippecanoe`` property
    derived from the ``SCAMIN`` attribute using :func:`scamin_to_zoom`.
    """

    layers = _s57_layers(s57_path)
    if not layers:
        raise RuntimeError("No layers found in S-57 dataset")

    with tempfile.TemporaryDirectory() as tmpdir:
        geojson = pathlib.Path(tmpdir, "chart.geojson")
        subprocess.check_call(
            [
                "ogr2ogr",
                "-f",
                "GeoJSON",
                str(geojson),
                s57_path,
            ]
        )

        if respect_scamin:
            data = json.loads(geojson.read_text())
            for feat in data.get("features", []):
                props = feat.get("properties", {})
                scamin = props.get("SCAMIN")
                if isinstance(scamin, (int, float)):
                    z = scamin_to_zoom(scamin, scamin_map)
                    meta = feat.setdefault("tippecanoe", {})
                    meta["minzoom"] = z
                    meta["maxzoom"] = 16
            geojson.write_text(json.dumps(data))

        tippecanoe_cmd = [
            "tippecanoe",
            "-o",
            output_mbtiles,
            "-zg",
            "--drop-densest-as-needed",
        ]
        for attr in _named_attributes() + ["SCAMIN"]:
            tippecanoe_cmd.extend(["--include", attr])
        tippecanoe_cmd.append(str(geojson))
        subprocess.check_call(tippecanoe_cmd)


# ---------------------------------------------------------------------------
# CM93 handling
# ---------------------------------------------------------------------------


def cm93_to_s57(cm93_path: str, output_s57: str) -> None:
    """Convert a CM93 cell to a temporary S-57 ``.000`` file.

    The preferred implementation shells out to an external CLI which understands
    CM93.  Set the environment variable ``OPENCN_CM93_CLI`` to point at a
    compatible binary providing a ``cm93_to_s57 <cm93> <out.000>`` style
    interface.  When the variable is unset a :class:`NotImplementedError` is
    raised with a helpful message so callers can skip gracefully in test
    environments.
    """

    cli = os.environ.get("OPENCN_CM93_CLI")
    if not cli:
        raise NotImplementedError(
            "CM93 conversion requires OpenCPN CM93 reader; set OPENCN_CM93_CLI"
        )
    subprocess.check_call([cli, cm93_path, output_s57])


# ---------------------------------------------------------------------------
# Upload helper
# ---------------------------------------------------------------------------


def upload_to_host(target: UploadTarget, *files: str) -> None:
    """Upload generated files to a remote Hostinger server using SFTP."""

    import paramiko

    transport = paramiko.Transport((target.host, 22))
    transport.connect(username=target.username, password=target.password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        for f in files:
            remote = os.path.join(target.remote_dir, os.path.basename(f))
            sftp.put(f, remote)
    finally:
        sftp.close()
        transport.close()


# ---------------------------------------------------------------------------
# Command line interface
# ---------------------------------------------------------------------------


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chart", help="Path to S-57 000 file or CM93 cell")
    parser.add_argument("output", help="Directory for generated tiles")
    parser.add_argument("--upload", action="store_true", help="Upload to remote host")
    parser.add_argument("--host", help="Hostinger hostname")
    parser.add_argument("--user", help="SFTP username")
    parser.add_argument("--password", help="SFTP password")
    parser.add_argument("--remote-dir", default=".", help="Remote directory")
    parser.add_argument(
        "--respect-scamin",
        action="store_true",
        help="Encode tippecanoe minzoom from SCAMIN",
    )
    args = parser.parse_args(argv)

    chart_path = pathlib.Path(args.chart)
    out_dir = pathlib.Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = chart_path.stem
    s57_path = chart_path

    # If the source is CM93 convert it first
    if chart_path.suffix.lower() in {".cm93", ".0000"}:
        s57_path = out_dir / f"{stem}.000"
        cm93_to_s57(str(chart_path), str(s57_path))

    mbtiles = out_dir / f"{stem}.mbtiles"
    cog = out_dir / f"{stem}.tif"

    s57_to_mbtiles(str(s57_path), str(mbtiles), respect_scamin=args.respect_scamin)
    s57_to_cog(str(s57_path), str(cog))

    if args.upload:
        if not all([args.host, args.user, args.password]):
            parser.error("--upload requires --host, --user and --password")
        upload_to_host(
            UploadTarget(args.host, args.user, args.password, args.remote_dir),
            str(mbtiles),
            str(cog),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
