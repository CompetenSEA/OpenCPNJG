# OpenCPN Vendor Map

| File (OpenCPN path) | Key classes/functions | Purpose (1–2 lines) | Notable includes |
| --- | --- | --- | --- |
| gui/include/gui/IDX_entry.h | IDX_entry | Tidal/current station index definition | <wx/dynarray.h> |
| gui/src/IDX_entry.cpp | WX_DEFINE_OBJARRAY, IDX_entry ctor/dtor | Implement IDX_entry array management | "IDX_entry.h", <wx/arrimpl.cpp> |
| gui/src/cm93.cpp | cm93chart and helpers | CM93 vector chart reader | many <wx/...>, s52s57.h |
| gui/src/s57_ocpn_utils.cpp | s57_GetVisibleLightSectors | S57 utility for light sector visibility | chcanv.h, pluginmanager.h, Quilt.h |
| gui/src/s57chart.cpp | s57chart | S57 chart handling and drawing | s57obj.h, <wx/...> |
| gui/src/s57obj.cpp | s57Obj class | Represent S57 features and objects | <wx/...>, s57obj.h |
| libs/iso8211/include/iso8211.h | DDFModule, DDFRecord | ISO 8211 data structures | gdal/cpl_port.h |
| libs/iso8211/include/s57.h | S57 constants | S57 dataset structures & constants | gdal/ogr_feature.h |
| libs/iso8211/src/ddffield.cpp | DDFField methods | Access ISO 8211 field data | cpl_conv.h |
| libs/iso8211/src/ddffielddefn.cpp | DDFFieldDefn | Field format definitions | cpl_conv.h |
| libs/iso8211/src/ddfmodule.cpp | DDFModule::Open | Read ISO 8211 modules | cpl_conv.h |
| libs/iso8211/src/ddfrecord.cpp | DDFRecord::Read | Parse ISO 8211 records | cpl_conv.h |
| libs/iso8211/src/ddfrecordindex.cpp | DDFRecordIndex | Cache ISO 8211 records | iso8211.h |
| libs/iso8211/src/ddfsubfielddefn.cpp | DDFSubfieldDefn | Define subfields in ISO 8211 | iso8211.h |
| libs/iso8211/src/ddfutils.cpp | DDFScanInt | Utility helpers for ISO 8211 parsing | cpl_conv.h |
| libs/s57-charts/include/ogr_s57.h | OGRS57Layer/DataSource | OGR bindings for S57 data | s57.h |
| libs/s57-charts/include/s57.h | S57Reader, S57ClassRegistrar | High‑level S57 translator declarations | ogr_api.h, iso8211.h |
| libs/s57-charts/include/s57class_registrar.h | S57ClassRegistrar | Lookup S57 object classes | cpl_port.h |
| libs/s57-charts/include/s57registrar_mgr.h | S57RegistrarMgr | Manage S57 class registrars | cpl_port.h |
| libs/s57-charts/src/ogrs57datasource.cpp | OGRS57DataSource | Open and manage S57 layers | cpl_conv.h |
| libs/s57-charts/src/ogrs57layer.cpp | OGRS57Layer | Layer interface over S57 features | cpl_conv.h |
| libs/s57-charts/src/s57classregistrar.cpp | S57ClassRegistrar | Load S57 object class definitions | cpl_conv.h |
| libs/s57-charts/src/s57featuredefns.cpp | S57FeatureDefns | Feature definition utilities | cpl_conv.h |
| libs/s57-charts/src/s57reader.cpp | S57Reader | Read S57 records and build features | cpl_conv.h, cpl_string.h |
| libs/s57-charts/src/s57registrar_mgr.cpp | S57RegistrarMgr | Manage multiple registrars | cpl_conv.h |
## CPL usage in vendored OpenCPN subset

| File | Included CPL headers | Referenced CPL symbols |
| ---- | -------------------- | ---------------------- |
| libs/iso8211/include/iso8211.h | cpl_port.h | – |
| libs/iso8211/include/s57.h | – | CPL_DLL |
| libs/iso8211/src/ddfmodule.cpp | cpl_conv.h | CPLAssert, CPLMalloc, CPLFree, CPLRealloc, CPLError, CPLE_AppDefined, CPLE_FileIO, CPLE_OpenFailed, VSIFRead, VSIFWrite |
| libs/iso8211/src/ddfrecord.cpp | cpl_conv.h | CPLAssert, CPLDebug, CPLMalloc, CPLFree, CPLRealloc, CPLError, CPLE_AppDefined, CPLE_FileIO, VSIFRead, VSIFWrite |
| libs/iso8211/src/ddffield.cpp | cpl_conv.h | – |
| libs/iso8211/src/ddffielddefn.cpp | cpl_string.h | CPLAssert, CPLMalloc, CPLRealloc, CPLFree, CPLStrdup, CPLError, CPLE_AppDefined |
| libs/iso8211/src/ddfsubfielddefn.cpp | cpl_conv.h | CPLAssert, CPLDebug, CPLMalloc, CPLFree, CPLStrdup, CPLError, CPLE_AppDefined, CPL_LSB |
| libs/iso8211/src/ddfutils.cpp | cpl_conv.h | CPLMalloc, CPLStrdup |
| libs/iso8211/src/ddfrecordindex.cpp* | cpl_conv.h | CPLFree, CPLRealloc, CPL_CSVID |

*`ddfrecordindex.cpp` includes `s57.h` (OGR) and is excluded from the build.*

## CPL symbol resolution

| CPL symbol | Implemented in | Notes |
| ---------- | -------------- | ----- |
| CPLMalloc, CPLFree, CPLRealloc, CPLStrdup | cpl_conv.cpp | requires cpl_conv.h, cpl_vsi.h, cpl_error.h |
| CPLError, CPLDebug, CPLAssert, CPLE_AppDefined, CPLE_FileIO, CPLE_OpenFailed | cpl_error.cpp | requires cpl_error.h (cpl_port.h) |
| VSIFRead, VSIFWrite | cpl_vsisimple.cpp | requires cpl_vsi.h |
| CPL_LSB, CPL_DLL | cpl_port.h | header only |

### CPL header dependencies

| CPL header | Companion headers |
| ---------- | ----------------- |
| cpl_port.h | – |
| cpl_error.h | cpl_port.h |
| cpl_vsi.h | cpl_port.h, cpl_error.h |
| cpl_conv.h | cpl_port.h, cpl_vsi.h, cpl_error.h |
| cpl_string.h | cpl_vsi.h, cpl_error.h, cpl_conv.h |

## Forbidden includes report

The following files reference forbidden headers and are excluded from the build:

- libs/iso8211/include/s57.h → `#include "gdal/ogr_feature.h"`
- libs/iso8211/src/ddfrecordindex.cpp → `#include "s57.h"` (transitively pulls OGR)

No other vendored files include `ogr_*`, `s52*`, `wx/`, `gl*`, `Osenc*`, or `Quilt*`.
