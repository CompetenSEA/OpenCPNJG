import maplibregl from 'maplibre-gl';

export interface MarinerParams {
  safety: number;
  shallow: number;
  deep: number;
}

export function createMapAPI(map: any) {
  const params: MarinerParams = { safety: 10, shallow: 5, deep: 30 };
  return {
    setMarinerParams(p: Partial<MarinerParams>) {
      Object.assign(params, p);
      const style = map.getStyle ? map.getStyle() : { sources: { cm93: { tiles: [] } } };
      const { safety, shallow, deep } = params;
      style.sources.cm93.tiles = [
        `/tiles/cm93/{z}/{x}/{y}?fmt=mvt&safety=${safety}&shallow=${shallow}&deep=${deep}`,
      ];
      map.setStyle(style);
    },
    toggleLayer(id: string, visible: boolean) {
      map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none');
    },
    setTheme(theme: 'day' | 'dusk' | 'night') {
      map.setStyle(`/style/s52.${theme}.json`);
    },
  };
}

export const AppMap = () => null; // Placeholder minimal component for tests

