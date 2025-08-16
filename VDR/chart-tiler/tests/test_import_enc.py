import sqlite3
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import registry as regmod  # type: ignore
from registry import Registry  # type: ignore
from tools import import_enc  # type: ignore


def fake_run(cmd, check):
    if cmd[0] == "ogr2ogr":
        Path(cmd[-2]).write_text(
            '{"type":"Feature","geometry":{"type":"Point","coordinates":[0,0]},"properties":{"OBJL":"BOYSPP"}}\n'
        )
    elif cmd[0] == "tippecanoe":
        out = Path(cmd[cmd.index("-o") + 1])
        conn = sqlite3.connect(out)
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
    class P:
        stdout = ""
    return P()


def test_import_enc(tmp_path, monkeypatch):
    src = tmp_path / "enc"
    src.mkdir()
    (src / "A.000").write_bytes(b"cell")
    monkeypatch.setattr(import_enc, "_have_tools", lambda: True)
    monkeypatch.setattr(import_enc.subprocess, "run", fake_run)
    monkeypatch.setattr(import_enc, "DATA_DIR", tmp_path)
    monkeypatch.setattr(regmod, "DB_PATH", tmp_path / "reg.sqlite")
    reg = Registry(regmod.DB_PATH)
    regmod._registry = reg
    import_enc.import_dir(src, name="foo")
    assert (tmp_path / "foo.mbtiles").exists()
    assert (tmp_path / "foo.meta.json").exists()
    items = reg.list(kind="enc")
    assert items and items[0].id == "foo"
