# OpenCPN CM93 Reading Notes

## Reading index

| File | Function / Class | Purpose |
| ---- | ---------------- | ------- |
| `gui/src/Quilt.cpp` | `QuiltCandidate::GetCandidateRegion` | Builds the region used to test whether a chart contributes to the quilt; CM93 charts force a fixed -80° to 80° latitude envelope and subtract `NOCOVR` polygons for gaps【F:gui/src/Quilt.cpp†L107-L156】【F:gui/src/Quilt.cpp†L170-L205】 |
| `gui/src/cm93.cpp` | `cm93compchart::GetCMScaleFromVP` | Derives CM93 scale tier from viewport resolution, adjusting by the detail slider (`g_cm93_zoom_factor`) before comparing against predefined scale breaks【F:gui/src/cm93.cpp†L4680-L4703】 |
| `gui/src/cm93.cpp` | M_COVR handling block | When decoding coverage polygons the code stores per‑cell WGS84 offsets and optional user corrections, building a coverage set used later for object translation【F:gui/src/cm93.cpp†L3450-L3525】【F:gui/src/cm93.cpp†L3560-L3577】 |
| `gui/src/s57obj.cpp` | `S57Obj::AddAttribute` | Captures the `SCAMIN` attribute so later rendering can drop features below a minimum scale【F:gui/src/s57obj.cpp†L200-L208】 |
| `gui/src/s57_ocpn_utils.cpp` | `s57_ProcessExtendedLightSectors` | Builds sector arcs from `SECTR1/SECTR2/VALNMR` and `COLOUR`, defaulting to yellow 2.5 NM and marking leading lights via `CATLIT`【F:gui/src/s57_ocpn_utils.cpp†L161-L250】 |
| `gui/src/s57chart.cpp` | Light description builder | Concatenates `LITCHR`, `SIGGRP`, colour initial, `SIGPER`, `VALNMR` and sector bearings into human‑readable labels【F:gui/src/s57chart.cpp†L5925-L6051】 |

## Behavioral rules

```pseudo
function candidate_charts(viewport):
    for each chart:
        region = chart.coverage
        subtract any NOCOVR polygons
        if region intersects viewport:
            yield chart

function cm93_detail_scale(viewport, slider):
    scale = meters_per_pixel(viewport)
    scale *= 0.6 ** (slider * scale**(-0.05))
    return tier_for(scale)

function apply_offsets(feature, lat, lon):
    mcd = lookup_cover_set(lat, lon)
    dx, dy = mcd.user_offsets or mcd.transform_offsets
    return translate(feature, dx, dy)

function scamin_visible(objl, z):
    rule = scamin_table.get(objl)
    return rule is None or rule.zmin <= z <= rule.zmax
```

## Concept mapping

OpenCPN concept | VDR equivalent
----------------|----------------
Quilting of multiple CM93 cells | Pre‑built zoom bands with `cm93_schemas.yml`; server selects features per zoom, client over‑zooms if needed
CM93 detail slider | `cm93_rules.apply_scamin` and zoom bands control feature density
Per‑cell offsets dialog | `cm93_importer.py` loads offsets CSV and `validate_offsets.py` checks continuity
SCAMIN attribute | Declarative rules in `portrayal/scamin.yml`

These notes capture enough behaviour to re‑implement CM93 handling without consulting the original C++ again.
