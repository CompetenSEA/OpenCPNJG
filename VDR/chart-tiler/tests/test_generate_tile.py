import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "charts_py" / "src"))
import charts_py

def test_generate_tile():
    charts_py.load_cell("dummy_cell.dat")
    opts = {"format": "png", "palette": "day", "safetyContour": 0.0}
    data = charts_py.generate_tile([0.0, 0.0, 1.0, 1.0], 0, opts)
    assert data.startswith(b"\x89PNG")
