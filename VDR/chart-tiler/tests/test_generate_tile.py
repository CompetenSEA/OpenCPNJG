import subprocess
import sys
from pathlib import Path
import shutil
import ctypes

ROOT = Path(__file__).resolve().parents[2]
LIB_DIR = ROOT / "opencpn-libs"
BUILD_DIR = LIB_DIR / "build"

# Build C++ library
subprocess.run(["cmake", "-S", str(LIB_DIR), "-B", str(BUILD_DIR)], check=True)
subprocess.run(["cmake", "--build", str(BUILD_DIR)], check=True)

# Build Python extension
PKG_DIR = ROOT / "chart-tiler" / "charts_py"
subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"], cwd=PKG_DIR, check=True)

# copy library next to extension for runtime resolution
for lib in ["libcharts.so", "libcharts.so.0", "libcharts.so.0.1.0"]:
    shutil.copy(BUILD_DIR / lib, PKG_DIR / f"src/charts_py/{lib}")

ctypes.CDLL(str(PKG_DIR / "src/charts_py/libcharts.so"))

sys.path.insert(0, str(PKG_DIR / "src"))
import charts_py

def test_generate_tile(tmp_path):
    sample = tmp_path / "dummy_cell.dat"
    sample.write_bytes(b"DUMMY")
    charts_py.load_cell(str(sample))
    data = charts_py.generate_tile([0.0, 0.0, 1.0, 1.0], 0, fmt="png")
    assert data.startswith(b"PNG")
