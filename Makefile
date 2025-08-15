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

