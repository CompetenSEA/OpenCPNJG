# CM93 MVT Schema

Vector tiles expose two planes:

- **Core** – areas, lines, points, soundings and lights served from `/tiles/cm93-core/{z}/{x}/{y}.pbf`.
- **Label** – text features served from `/tiles/cm93-label/{z}/{x}/{y}.pbf`.

All tiles use `EXTENT=4096` and honour the declarative `SCAMIN` rules in `chart-tiler/config/portrayal/scamin.yml`.
The dictionary at `/tiles/cm93/dict.json` maps integer IDs to S‑57 object class names for style lookup.
