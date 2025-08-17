import json
import sqlite3
import shutil
from pathlib import Path
import unittest

from opencpn_bridge.py.ingest import ingest_dataset


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.registry = self.root / "registry" / "registry.sqlite"
        if self.registry.exists():
            conn = sqlite3.connect(self.registry)
            conn.execute("DELETE FROM datasets")
            conn.commit()
            conn.close()
        else:
            self.registry.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        cache = self.root / ".cache"
        if cache.exists():
            shutil.rmtree(cache)
        if self.registry.exists():
            conn = sqlite3.connect(self.registry)
            conn.execute("DELETE FROM datasets")
            conn.commit()
            conn.close()

    def test_idempotent_ingest(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            src = Path(tmp)
            meta = {"bounds": [0, 0, 1, 1], "minzoom": 0, "maxzoom": 10}
            (src / "provenance.json").write_text(json.dumps(meta))
            (src / "data.txt").write_text("data")

            ingest_dataset("ds1", src, "test")

            cache = self.root / ".cache" / "senc" / "ds1"
            self.assertTrue((cache / "data.txt").exists())

            conn = sqlite3.connect(self.registry)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM datasets WHERE id=?", ("ds1",))
            self.assertEqual(cur.fetchone()[0], 1)
            conn.close()

            meta["minzoom"] = 1
            (src / "provenance.json").write_text(json.dumps(meta))
            ingest_dataset("ds1", src, "test")

            conn = sqlite3.connect(self.registry)
            cur = conn.cursor()
            cur.execute("SELECT minzoom FROM datasets WHERE id=?", ("ds1",))
            self.assertEqual(cur.fetchone()[0], 1)
            cur.execute("SELECT COUNT(*) FROM datasets")
            self.assertEqual(cur.fetchone()[0], 1)
            conn.close()


if __name__ == "__main__":
    unittest.main()
