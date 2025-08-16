import assert from 'assert';
import { createMapAPI } from './AppMap';

function mockMap() {
  return {
    layout: [] as any[],
    style: { sources: { cm93: { tiles: ['old'] } } },
    setLayoutProperty(id: string, prop: string, value: string) {
      this.layout.push([id, prop, value]);
    },
    getStyle() {
      return this.style;
    },
    setStyle(s: any) {
      this.style = s;
      this.last = s;
    },
  } as any;
}

const map = mockMap();
const api = createMapAPI(map);
api.toggleLayer('SOUNDG', false);
assert.deepStrictEqual(map.layout[0], ['SOUNDG', 'visibility', 'none']);
api.setMarinerParams({ safety: 12 });
assert.ok(map.last.sources.cm93.tiles[0].includes('safety=12'));
console.log('ok');
