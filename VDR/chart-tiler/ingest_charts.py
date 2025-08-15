"""Populate an SQLite database with chart dictionary metadata.

The `charts_py` module exposes helpers returning entries for CM93/S‑57
object classes, attribute classes and general chart metadata.  This script
stores them in a small SQLite database for fast lookup at runtime.

Usage:
    python ingest_charts.py [output_path]

The database defaults to `charts.sqlite` in the current directory.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
import charts_py


def main(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS object_class (id INTEGER PRIMARY KEY, acronym TEXT, name TEXT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS attribute_class (id INTEGER PRIMARY KEY, acronym TEXT, name TEXT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS chart_metadata (key TEXT PRIMARY KEY, value TEXT)"
    )

    cur.executemany("INSERT INTO object_class VALUES (?, ?, ?)", charts_py.get_object_classes())
    cur.executemany(
        "INSERT INTO attribute_class VALUES (?, ?, ?)", charts_py.get_attribute_classes()
    )
    cur.executemany("INSERT INTO chart_metadata VALUES (?, ?)", charts_py.get_chart_metadata())

    conn.commit()
    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest chart dictionaries into SQLite.")
    parser.add_argument(
        "output", nargs="?", default="charts.sqlite", help="Path to output SQLite DB"
    )
    args = parser.parse_args()
    main(Path(args.output))
