# CM93 Cell Transitions and Offsets

Imported CM93 cells may require regional position corrections. The importer reads `--offsets` CSV files with columns:

```
cell_id, region_id, offset_dx_m, offset_dy_m
```

`cm93_importer.apply_offsets` translates geometries before loading into the database. The accompanying script `scripts/validate_offsets.py` compares adjacent cell boundaries before and after offsets and fails if the post‑offset gap exceeds a tolerance.
