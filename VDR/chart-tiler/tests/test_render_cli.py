import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH = str(ROOT / "charts_py" / "src")

def test_render_tile_cli(tmp_path):
    out = tmp_path / "tile.png"
    env = {**os.environ, "PYTHONPATH": PYTHONPATH}
    subprocess.run(
        [sys.executable, str(ROOT / "render_tile.py"), "0", "0", "0", "--output", str(out)],
        check=True,
        env=env,
    )
    data = out.read_bytes()
    assert data.startswith(b"\x89PNG")
