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
