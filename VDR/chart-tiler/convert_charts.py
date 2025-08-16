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
import os
import pathlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Iterable, Optional, List

import csv
from pathlib import Path

from osgeo import gdal, ogr


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


def s57_to_mbtiles(s57_path: str, output_mbtiles: str) -> None:
    """Generate vector tiles from an S-57 dataset using tippecanoe.

    The S-57 features are first exported to GeoJSON using ``ogr2ogr`` and then
    piped to ``tippecanoe`` which builds the MBTiles database.  Both commands
    are invoked via ``subprocess`` to avoid any C++ dependencies.
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
        tippecanoe_cmd = [
            "tippecanoe",
            "-o",
            output_mbtiles,
            "-zg",
            "--drop-densest-as-needed",
        ]
        for attr in _named_attributes():
            tippecanoe_cmd.extend(["--include", attr])
        tippecanoe_cmd.append(str(geojson))
        subprocess.check_call(tippecanoe_cmd)


# ---------------------------------------------------------------------------
# CM93 handling
# ---------------------------------------------------------------------------


def cm93_to_s57(cm93_path: str, output_s57: str) -> None:
    """Convert a CM93 file to an intermediate S-57 000 file.

    Full CM93 decoding is outside the scope of this demonstration.  In a
    production pipeline this function would implement the parsing logic ported
    from the original C++ reader.  Here we simply raise ``NotImplementedError``
    to make the omission explicit while keeping the public API stable.
    """

    raise NotImplementedError(
        "CM93 conversion requires a dedicated parser which is not implemented"
    )


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

    s57_to_mbtiles(str(s57_path), str(mbtiles))
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
