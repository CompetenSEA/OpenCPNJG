import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Stub out heavy GDAL dependency for import
osgeo = types.ModuleType("osgeo")
osgeo.gdal = types.ModuleType("gdal")
osgeo.ogr = types.ModuleType("ogr")
sys.modules.setdefault("osgeo", osgeo)
sys.modules.setdefault("osgeo.gdal", osgeo.gdal)
sys.modules.setdefault("osgeo.ogr", osgeo.ogr)

from convert_charts import _named_attributes


def test_named_attributes_contains_objnam():
    attrs = _named_attributes()
    assert "OBJNAM" in attrs
    assert "NOBJNM" in attrs
