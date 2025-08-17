import sqlite3
import shutil
from pathlib import Path
import unittest

from opencpn_bridge.py.ingest import ingest_dataset
from opencpn_bridge.registry import list_datasets


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

            ingest_dataset("ds1", src, "test")

            cache = self.root / ".cache" / "senc" / "ds1"
            self.assertTrue((cache / "provenance.json").exists())

            datasets = list(list_datasets())
            self.assertEqual(len(datasets), 1)
            ds = datasets[0]
            self.assertEqual(ds["id"], "ds1")
            self.assertEqual(ds["bounds"], [0, 0, 0, 0])
            self.assertEqual(ds["minzoom"], 0)
            self.assertEqual(ds["maxzoom"], 0)

            ingest_dataset("ds1", src, "test")
            self.assertEqual(len(list(list_datasets())), 1)


if __name__ == "__main__":
    unittest.main()
