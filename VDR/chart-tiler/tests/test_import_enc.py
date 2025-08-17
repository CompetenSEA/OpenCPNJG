import sqlite3
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import import_enc  # type: ignore


def fake_encode(input_000: str, output_mbtiles: str, **kw):
    conn = sqlite3.connect(output_mbtiles)
    cur = conn.cursor()
    cur.execute("CREATE TABLE metadata (name TEXT, value TEXT)")
    cur.executemany(
        "INSERT INTO metadata VALUES (?,?)",
        [
            ("bounds", "0,0,1,1"),
            ("minzoom", "0"),
            ("maxzoom", "5"),
            ("name", "foo"),
        ],
    )
    conn.commit()
    conn.close()


def fake_load(cell: Path, dsn: str) -> None:
    conn = sqlite3.connect(dsn)
    cur = conn.cursor()
    table = f"enc_{cell.stem.lower()}"
    cur.execute(f"CREATE TABLE {table} (OBJL INTEGER)")
    cur.execute(f"INSERT INTO {table} (OBJL) VALUES (1)")
    conn.commit()
    conn.close()


def test_import_enc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = tmp_path / "A.000"
    src.write_bytes(b"cell")
    dsn = tmp_path / "enc.sqlite"
    monkeypatch.setattr(import_enc, "encode_s57_to_mbtiles", fake_encode)
    monkeypatch.setattr(import_enc, "_load_cell_to_db", fake_load)
    monkeypatch.setattr(import_enc, "ENC_DIR", tmp_path)
    import_enc.import_s57(src, dsn=str(dsn), dataset_id="foo")
    assert (tmp_path / "foo.mbtiles").exists()
    conn = sqlite3.connect(dsn)
    cur = conn.cursor()
    cur.execute("SELECT OBJL FROM enc_a")
    row = cur.fetchone()
    assert row and row[0] == 1
    conn.close()
