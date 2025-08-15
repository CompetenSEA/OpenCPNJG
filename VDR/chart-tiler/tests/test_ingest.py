import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH = str(ROOT / "charts_py" / "src")

def test_ingest_creates_db(tmp_path):
    db = tmp_path / "charts.sqlite"
    env = {**os.environ, "PYTHONPATH": PYTHONPATH}
    subprocess.run([sys.executable, str(ROOT / "ingest_charts.py"), str(db)], check=True, env=env)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    conn.close()
    assert {"object_class", "attribute_class", "chart_metadata"} <= tables
