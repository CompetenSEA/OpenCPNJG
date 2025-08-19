# Vendored OpenCPN subset

| File | Key classes / functions | Purpose | Notes (deps / headers) |
| --- | --- | --- | --- |
| `libs/iso8211/include/iso8211.h` | `DDFModule`, `DDFFieldDefn`, `DDFRecord` | Core ISO 8211 data structures and access API | includes `gdal/cpl_port.h` |
| `libs/iso8211/include/s57.h` | `S57Reader`, `S57ClassRegistrar`, `DDFRecordIndex` | S‑57 translator declarations | depends on `gdal/ogr_feature.h`, `iso8211.h` |
| `libs/iso8211/src/ddfmodule.cpp` | `DDFModule::Open`, `ReadRecord`, `Close` | Implement ISO 8211 module I/O | includes `gdal/cpl_conv.h` |
| `libs/iso8211/src/ddfrecord.cpp` | `DDFRecord::Read`, `GetField` | Parse ISO 8211 records into fields | uses `iso8211.h` |
| `libs/iso8211/src/ddfrecordindex.cpp` | `DDFRecordIndex` | Cache ISO 8211 records keyed by integer | includes `iso8211.h` |
| `libs/iso8211/src/ddfutils.cpp` | `DDFScanInt`, `DDFFetchVariable` | Utility helpers for ISO 8211 parsing | includes `gdal/cpl_conv.h` |
| `libs/iso8211/src/ddffield.cpp` | `DDFField::GetData`, `Reset` | Access field raw data and iterators | depends on `iso8211.h`, `gdal/cpl_conv.h` |
| `libs/iso8211/src/ddfsubfielddefn.cpp` | `DDFSubfieldDefn::GetDataType` | Define individual subfields within a field | includes `iso8211.h` |
| `libs/iso8211/src/ddffielddefn.cpp` | `DDFFieldDefn::Create`, `AddSubfield` | Define field format and subfields | includes `iso8211.h` |
| `libs/s57-charts/include/s57.h` | `S57Reader`, `S57ClassRegistrar` | High‑level S‑57 logic separate from OGR bindings | depends on `gdal/ogr_api.h`, `iso8211.h` |
| `libs/s57-charts/include/ogr_s57.h` | `OGRS57Layer`, `OGRS57DataSource` | OGR bindings for S‑57 layers and datasources | includes `s57.h`, `gdal/ogr_api.h` |
| `libs/s57-charts/src/s57reader.cpp` | `S57Reader::Open`, `ReadNextRecord` | Read and interpret S‑57 records | uses `gdal/cpl_conv.h`, `ogr_s57.h` |
| `libs/s57-charts/src/ogrs57datasource.cpp` | `OGRS57DataSource::Open` | Manage a collection of S‑57 layers via OGR | includes `gdal/cpl_conv.h` |
| `libs/s57-charts/src/ogrs57layer.cpp` | `OGRS57Layer::GetNextFeature` | Layer interface over S‑57 features | includes `gdal/cpl_conv.h` |
| `gui/include/gui/cm93.h` | `M_COVR_Desc`, `Get_CM93_CellIndex` | CM93 chart object definitions and helpers | pulls in `s57chart.h`, `wx/listctrl.h` |
| `gui/src/cm93.cpp` | `cm93chart` methods, dictionary loading | Implementation of CM93 reader and geometry transforms | depends on `wx` headers, `gdal/ogr_api.h`, `s52plib` |
| `gui/include/gui/chartdb.h` | `ChartDB`, `ChartStack` | Interface for chart database access | includes `wx/xml/xml.h`, `chartdbs.h` |
| `gui/include/gui/chartdbs.h` | `ChartDatabase`, `ChartDirInfo`, `ChartGroup` | Store and query chart metadata | uses `<map>`, `<vector>`, `bbox.h`, `LLRegion.h` |
| `gui/src/chartdb.cpp` | `ChartDB::Open`, `GetDBDirEntries` | Load and manage chart database on disk | uses many `wx` headers |
| `gui/src/chartdbs.cpp` | `ChartDatabase::Load`, `ChartGroup::AddChart` | Persist and query chart database records | uses `wx` headers, plugins |
| `gui/include/gui/IDX_entry.h` | `IDX_entry` struct and arrays | Definition of CM93 index entries | includes `wx/dynarray.h` |
| `gui/src/IDX_entry.cpp` | `IDX_entry` methods | Parse CM93 index entry blocks | uses `<wx/arrimpl.cpp>` |
| `gui/src/s57chart.cpp` | `s57chart` class methods | S‑57 chart drawing and data access | includes `iso8211`, heavy `wx`/`gdal` deps |
