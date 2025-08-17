import assert from 'assert';
import { createMapAPI } from '../AppMap';

function mockMap() {
  return {
    layout: [] as any[],
    style: { sources: {} },
    setLayoutProperty(id: string, prop: string, value: string) {
      this.layout.push([id, prop, value]);
    },
    getStyle() {
      return this.style;
    },
    setStyle(s: any) {
      this.style = s;
    },
    setFilter() {},
  } as any;
}

const map = mockMap();
const api = createMapAPI(map);
api.toggleLayer('cm93-label-layer', false);
assert.deepStrictEqual(map.layout[0], ['cm93-label-layer', 'visibility', 'none']);
console.log('visibility ok');
