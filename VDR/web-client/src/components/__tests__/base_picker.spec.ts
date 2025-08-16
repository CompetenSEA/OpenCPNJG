import assert from 'assert';
import { createMapAPI } from '../AppMap';
import { createBasePickerAPI } from '../BasePicker';

declare const global: any;

global.fetch = async () => ({
  json: async () => [
    { id: 'osm', kind: 'osm', name: 'OSM' },
    { id: 'g1', kind: 'geotiff', name: 'g1' },
  ],
});

function mockMap() {
  return {
    style: { sources: {} as any },
    setStyle(s: any) { this.style = s; },
    getStyle() { return this.style; },
  } as any;
}

(async () => {
  const map = mockMap();
  const api = createMapAPI(map);
  const picker = createBasePickerAPI(api);
  await picker.load();
  picker.select('osm');
  assert.ok(map.style.transformRequest, 'transformRequest added');
  picker.select('geotiff', 'g1');
  assert.ok(map.style.sources.base.tiles[0].includes('/tiles/geotiff/g1'));
  console.log('base picker ok');
})();
