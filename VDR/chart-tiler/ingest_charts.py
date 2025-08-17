"""Utility for generating a chart dictionary SQLite database.

The :mod:`charts_py` module (implemented either by a lightweight Python
fallback or the real ``libcharts`` bindings) exposes helpers returning
metadata about S‑57/CM93 chart object classes, attribute classes and global
chart properties.  ``ingest_charts.py`` persists this information to a small
SQLite file for quick lookup by the tile server.

The resulting database contains three tables:

``object_class``
    ``id`` (INTEGER PRIMARY KEY) – numeric identifier used in S‑57
    ``acronym`` (TEXT) – short code such as ``BOYSPP``
    ``name`` (TEXT) – human readable description

``attribute_class``
    ``id`` (INTEGER PRIMARY KEY)
    ``acronym`` (TEXT)
    ``name`` (TEXT)

``chart_metadata``
    ``key`` (TEXT PRIMARY KEY)
    ``value`` (TEXT)

Example
-------
>>> python ingest_charts.py charts.sqlite

Parameters
----------
output : Path, optional
    Location of the SQLite database to create.  Defaults to ``charts.sqlite``
    in the current working directory.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Tuple
import subprocess

import charts_py


def _is_cog(path: Path) -> bool:
    """Return ``True`` if *path* points to a Cloud Optimized GeoTIFF."""

    try:
        proc = subprocess.run(
            ["gdalinfo", str(path)], capture_output=True, text=True, check=True
        )
    except Exception:
        return False
    return "Cloud Optimized GeoTIFF" in proc.stdout


def ensure_cog(path: Path) -> Path:
    """Ensure *path* is a COG, converting it if necessary.

    If *path* is not already a Cloud Optimized GeoTIFF it is converted using
    ``gdal_translate -of COG`` and the converted file path is returned.
    """

    if _is_cog(path):
        return path
    out = path.with_suffix(".cog.tif")
    subprocess.run(["gdal_translate", "-of", "COG", str(path), str(out)], check=True)
    return out


def _create_schema(cur: sqlite3.Cursor) -> None:
    """Create database tables if they do not yet exist."""

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS object_class (
            id INTEGER PRIMARY KEY,
            acronym TEXT NOT NULL,
            name TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attribute_class (
            id INTEGER PRIMARY KEY,
            acronym TEXT NOT NULL,
            name TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chart_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )


def _populate_table(cur: sqlite3.Cursor, table: str, rows: Iterable[Tuple]) -> None:
    """Insert rows into *table* replacing existing entries.

    ``INSERT OR REPLACE`` ensures rerunning the script updates records rather
    than failing due to ``PRIMARY KEY`` conflicts.
    """

    placeholders = ",".join(["?"] * len(next(iter(rows), [])))
    sql = f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})"
    cur.executemany(sql, rows)


def main(db_path: Path) -> None:
    """Populate *db_path* with chart dictionary metadata."""

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        _create_schema(cur)
        _populate_table(cur, "object_class", charts_py.get_object_classes())
        _populate_table(cur, "attribute_class", charts_py.get_attribute_classes())
        _populate_table(cur, "chart_metadata", charts_py.get_chart_metadata())
        conn.commit()


if __name__ == "__main__":  # pragma: no cover - CLI convenience
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        default="charts.sqlite",
        type=Path,
        help="Path to output SQLite database",
    )
    main(parser.parse_args().output)
