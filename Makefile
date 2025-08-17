.RECIPEPREFIX := >
ASSETS=VDR/server-styling/dist/assets/s52
DIST=VDR/server-styling/dist
LOCK=VDR/server-styling/opencpn-assets.lock

.PHONY: assets sprite style all

assets:
>python VDR/server-styling/sync_opencpn_assets.py --lock $(LOCK) --dest $(ASSETS) --force

sprite: assets
>python VDR/server-styling/generate_sprite_json.py --chartsymbols $(ASSETS)/chartsymbols.xml --output $(DIST)/sprites/s52-day.json

style: assets
>python VDR/server-styling/build_style_json.py --chartsymbols $(ASSETS)/chartsymbols.xml --tiles-url "/tiles/cm93/{z}/{x}/{y}?fmt=mvt&sc={sc}" --source-name cm93 --source-layer features --sprite-base "/sprites/s52-day" --glyphs "/glyphs/{fontstack}/{range}.pbf" --safety-contour 10 --output $(DIST)/style.s52.day.json

all: sprite style


.PHONY: stage-assets
stage-assets:
>bash VDR/scripts/stage_assets_all.sh --force

.PHONY: dev-up
dev-up: stage-assets
>python -m venv .venv
>.venv/bin/pip install -r VDR/chart-tiler/requirements.txt
>mkdir -p VDR/server-styling/dist/sprites
>cp VDR/server-styling/dist/assets/s52/rastersymbols-day.png VDR/server-styling/dist/sprites/s52-day.png
>.venv/bin/python VDR/server-styling/generate_sprite_json.py --chartsymbols VDR/server-styling/dist/assets/s52/chartsymbols.xml --output VDR/server-styling/dist/sprites/s52-day.json
>mkdir -p VDR/server-styling/dist/glyphs
>find VDR/BAUV/src/tileserver/fonts -name '*.pbf' -print0 | xargs -0 -I{} cp {} VDR/server-styling/dist/glyphs/ 2>/dev/null || true
>.venv/bin/python VDR/chart-tiler/render_tile.py --help
