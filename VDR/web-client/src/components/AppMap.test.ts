import assert from 'assert';
import { createMapAPI } from './AppMap';

function mockMap() {
  return {
    layout: [] as any[],
    style: { sources: { enc: { tiles: ['old'] } } },
    filters: [] as any[],
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
    setFilter(id: string, exp: any) {
      this.filters.push([id, exp]);
    },
  } as any;
}

const map = mockMap();
const api = createMapAPI(map);
api.setDataset('ds1');
api.toggleLayer('SOUNDG', false);
assert.deepStrictEqual(map.layout[0], ['SOUNDG', 'visibility', 'none']);
assert.ok(!map.last.sources.enc.tiles[0].includes('safety='));
api.setMarinerParams({ safety: 12 });
assert.deepStrictEqual(map.filters[0], ['enc-depth', ['<=', ['get', 'depth'], 12]]);
console.log('ok');
