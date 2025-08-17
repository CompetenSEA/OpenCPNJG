import maplibregl from 'maplibre-gl';

interface DictEntry {
  name: string;
  label: string[];
}

interface Dict {
  objects: Record<string, DictEntry>;
  lights: Record<string, string>;
}

let dict: Dict = { objects: {}, lights: {} };

export async function registerCm93Sources(map: maplibregl.Map) {
  const [core, label, d] = await Promise.all([
    fetch('/tiles/cm93-core.tilejson').then((r) => r.json()),
    fetch('/tiles/cm93-label.tilejson').then((r) => r.json()),
    fetch('/tiles/cm93/dict.json').then((r) => r.json()),
  ]);
  dict = d as Dict;
  map.addSource('cm93-core', { type: 'vector', ...core });
  map.addSource('cm93-label', { type: 'vector', ...label });
}

export function dictLookup(id: number | string): string | undefined {
  const entry = dict.objects[String(id)];
  return entry ? entry.name : undefined;
}

export function lightLookup(code: number | string): string | undefined {
  return dict.lights[String(code)];
}

export function getDict() {
  return dict;
}
