import maplibregl from 'maplibre-gl';
import { useEffect, useRef } from 'react';

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
      const style = map.getStyle ? map.getStyle() : { sources: { enc: { tiles: [] } } };
      const { safety, shallow, deep } = params;
      style.sources.enc.tiles = [
        `/tiles/enc/{z}/{x}/{y}?fmt=mvt&safety=${safety}&shallow=${shallow}&deep=${deep}`,
      ];
      map.setStyle(style);
    },
    toggleLayer(id: string, visible: boolean) {
      map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none');
    },
    setTheme(theme: 'day' | 'dusk' | 'night') {
      map.setStyle(`/style/s52.${theme}.json`);
    },
    setBase(base: 'osm' | 'geotiff' | 'enc', chartId?: string) {
      const style = map.getStyle ? map.getStyle() : { sources: {} };
      if (base === 'osm') {
        if (process.env.OSM_USE_COMMUNITY === '0') {
          delete style.sources.base;
        } else {
          style.sources.base = {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
          };
          style.transformRequest = (url: string) => {
            if (url.includes('openstreetmap')) {
              return { url, headers: { 'User-Agent': 'vdr-app' } }; // TODO self-host OSM
            }
            return { url } as any;
          };
        }
      } else if (base === 'geotiff' && chartId) {
        style.sources.base = {
          type: 'raster',
          tiles: [`/tiles/geotiff/${chartId}/{z}/{x}/{y}.png`],
          tileSize: 256,
        };
      } else if (base === 'enc') {
        style.sources.base = {
          type: 'vector',
          tiles: ['/tiles/enc/{z}/{x}/{y}?fmt=mvt'],
        };
        style.sources.enc = style.sources.base;
      }
      map.setStyle(style);
    },
  };
}

interface AppMapProps {
  base: 'osm' | 'geotiff' | 'enc';
  chartId?: string;
}

export const AppMap = ({ base, chartId }: AppMapProps) => {
  const mapRef = useRef<any>();
  useEffect(() => {
    const map = {
      style: { sources: {} as any },
      setStyle(s: any) { this.style = s; },
      getStyle() { return this.style; },
      setLayoutProperty() {},
      addSource() {},
      addLayer() {},
    };
    mapRef.current = map;
    createMapAPI(map).setBase(base, chartId);
  }, []);
  useEffect(() => {
    if (mapRef.current) {
      createMapAPI(mapRef.current).setBase(base, chartId);
    }
  }, [base, chartId]);
  return null;
};
