import assert from 'assert';
import { createMapAPI } from '../AppMap';

declare const global: any;

let called = 0;
global.fetch = async (url: string) => {
  if (url === '/charts') called++;
  return {
    json: async () => ({ enc: { datasets: [{ id: 'ds1', title: 'A', bounds: [0, 0, 1, 1] }] } }),
  };
};

function mockMap() {
  return {
    style: { sources: {} as any },
    setStyle(s: any) { this.style = s; },
    getStyle() { return this.style; },
    layout: [] as any[],
    setLayoutProperty(id: string, prop: string, value: string) {
      this.layout.push([id, prop, value]);
    },
    fitBounds() {},
  } as any;
}

(async () => {
  const map = mockMap();
  const api = createMapAPI(map);
  const ds = await api.loadCharts();
  assert.strictEqual(called, 1);
  api.setDataset(ds[0].id, ds[0].bounds);
  assert.ok(map.style.sources.enc.tiles[0].includes('/tiles/enc/ds1/'));
  api.setMarinerParams({ safety: 9 });
  assert.ok(map.style.sources.enc.tiles[0].includes('/tiles/enc/ds1/'));
  assert.ok(map.style.sources.enc.tiles[0].includes('safety=9'));
  console.log('enc ok');
})();
