import sqlite3
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from registry import list_datasets  # type: ignore
from tools import import_enc  # type: ignore


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


def test_import_enc(tmp_path, monkeypatch):
    src = tmp_path / "A.000"
    src.write_bytes(b"cell")
    monkeypatch.setattr(import_enc, "encode_s57_to_mbtiles", fake_encode)
    monkeypatch.setattr(import_enc, "ENC_DIR", tmp_path)
    import_enc.import_s57(src, dataset_id="foo")
    assert (tmp_path / "foo.mbtiles").exists()
    datasets = list_datasets(tmp_path)
    assert datasets and datasets[0].id == "foo"
