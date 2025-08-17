import assert from 'assert';
import { setLabelVisibility, setPalette, updateMarinerParams } from '../sources/cm93';

function mockMap() {
  return {
    style: {
      sources: {},
      layers: [{ id: 'DEPARE-fill', paint: { 'fill-color': '#a0a0f0' } }],
    },
    layout: [] as any[],
    filters: [] as any[],
    setLayoutProperty(id: string, prop: string, value: string) {
      this.layout.push([id, prop, value]);
    },
    getStyle() {
      return this.style;
    },
    setStyle(s: any) {
      this.style = s;
    },
    setFilter(id: string, exp: any) {
      this.filters.push([id, exp]);
    },
  } as any;
}

const map = mockMap();
setLabelVisibility(map, false);
assert.deepStrictEqual(map.layout[0], ['cm93-label-layer', 'visibility', 'none']);

setPalette(map, 'night');
assert.strictEqual(
  map.style.layers.find((l: any) => l.id === 'DEPARE-fill').paint['fill-color'],
  '#222244'
);

updateMarinerParams(map, { safety: 8 });
assert.deepStrictEqual(map.filters[0], ['cm93-depth', ['<=', ['get', 'depth'], 8]]);

console.log('cm93 controls ok');
