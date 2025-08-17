import maplibregl from 'maplibre-gl';

let dict: Record<string, string> = {};

export async function registerCm93Sources(map: maplibregl.Map) {
  const [core, label, d] = await Promise.all([
    fetch('/tiles/cm93-core.tilejson').then((r) => r.json()),
    fetch('/tiles/cm93-label.tilejson').then((r) => r.json()),
    fetch('/tiles/cm93/dict.json').then((r) => r.json()),
  ]);
  dict = d;
  map.addSource('cm93-core', { type: 'vector', ...core });
  map.addSource('cm93-label', { type: 'vector', ...label });
}

export function dictLookup(id: number | string): string | undefined {
  return dict[String(id)];
}

export function getDict() {
  return dict;
}

const marinerParams = { safety: 10 };

export function setLabelVisibility(map: maplibregl.Map, visible: boolean) {
  map.setLayoutProperty('cm93-label-layer', 'visibility', visible ? 'visible' : 'none');
}

const palettes: Record<'day' | 'dusk' | 'night', string> = {
  day: '#a0a0f0',
  dusk: '#666699',
  night: '#222244',
};

export function setPalette(
  map: maplibregl.Map,
  palette: 'day' | 'dusk' | 'night'
) {
  const style = map.getStyle();
  if (!style || !style.layers) return;
  style.layers = style.layers.map((l: any) => {
    if (l.id === 'DEPARE-fill') {
      return {
        ...l,
        paint: { ...(l.paint || {}), 'fill-color': palettes[palette] },
      };
    }
    return l;
  });
  map.setStyle(style);
}

export function updateMarinerParams(
  map: maplibregl.Map,
  p: Partial<typeof marinerParams>
) {
  Object.assign(marinerParams, p);
  map.setFilter('cm93-depth', ['<=', ['get', 'depth'], marinerParams.safety]);
}
