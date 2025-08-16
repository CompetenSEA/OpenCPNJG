import assert from 'assert';
import { createMapAPI } from '../AppMap';

function mockMap() {
  return {
    style: { sources: {} as any },
    setStyle(s: any) { this.style = s; },
    getStyle() { return this.style; },
    layout: [] as any[],
    setLayoutProperty(id: string, prop: string, value: string) {
      this.layout.push([id, prop, value]);
    },
  } as any;
}

const map = mockMap();
const api = createMapAPI(map);
api.setBase('enc');
assert.ok(map.style.sources.base.tiles[0].includes('/tiles/enc'));
api.setMarinerParams({ safety: 9 });
assert.ok(map.style.sources.enc.tiles[0].includes('safety=9'));
console.log('enc ok');
