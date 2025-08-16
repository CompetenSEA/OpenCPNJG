# ENC MBTiles

MBTiles produced from S‑57 or CM93 cells are served as the primary ENC vector
base.  Each database contains a single `pbf` tile layer with features carrying
selected S‑57 attributes such as `OBJL`, `OBJNAM`, `NOBJNM` and `SCAMIN`.

## SCAMIN mapping

Features with a `SCAMIN` attribute are mapped to Mapbox Vector Tile zoom levels
using the following table:

| SCAMIN | minzoom |
|-------:|--------:|
| 90 000 | 10 |
| 45 000 | 11 |
| 22 000 | 12 |
| 12 000 | 13 |
| 8 000  | 14 |
| 4 000  | 15 |
| 2 000  | 16 |

Values outside the table are clamped to the nearest zoom.

## Troubleshooting

* `tippecanoe` missing – ensure it is installed and available on the `PATH`.
* empty tiles – verify the source `.000` file contains features.
* SCAMIN ignored – pass `--respect-scamin` to the encoder.
