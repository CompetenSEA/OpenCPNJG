import { useEffect, useState } from 'react';
import { createMapAPI } from './AppMap';

export interface Chart {
  id: string;
  kind: string;
  name: string;
}

interface Props {
  api: ReturnType<typeof createMapAPI>;
}

export const BasePicker = ({ api }: Props) => {
  const [charts, setCharts] = useState<Chart[]>([]);
  const [base, setBase] = useState<'osm' | 'geotiff' | 'enc'>('enc');
  useEffect(() => {
    fetch('/charts')
      .then((r) => r.json())
      .then((data) => {
        const items: Chart[] = [];
        if (data.enc?.datasets) {
          items.push(
            ...data.enc.datasets.map((d: any) => ({ id: d.id, kind: 'enc', name: d.title }))
          );
        }
        if (data.base?.includes('geotiff') && data.geotiff?.datasets) {
          items.push(
            ...data.geotiff.datasets.map((d: any) => ({ id: d.id, kind: 'geotiff', name: d.title }))
          );
        }
        if (data.base?.includes('osm')) {
          items.push({ id: 'osm', kind: 'osm', name: 'OSM' });
        }
        setCharts(items);
      })
      .catch(() => {});
  }, []);
  function select(kind: 'osm' | 'geotiff' | 'enc', id?: string) {
    if (kind === 'enc') {
      api.setBase('enc', id);
      setBase('enc');
    } else {
      api.setBase(kind, id);
      setBase(kind);
    }
  }
  return null;
};

// lightweight helper for tests
export function createBasePickerAPI(api: ReturnType<typeof createMapAPI>) {
  return {
    async load(): Promise<Chart[]> {
      const resp = await fetch('/charts');
      const data = await resp.json();
      const items: Chart[] = [];
      if (data.enc?.datasets) {
        items.push(...data.enc.datasets.map((d: any) => ({ id: d.id, kind: 'enc', name: d.title })));
      }
      if (data.base?.includes('geotiff') && data.geotiff?.datasets) {
        items.push(
          ...data.geotiff.datasets.map((d: any) => ({ id: d.id, kind: 'geotiff', name: d.title }))
        );
      }
      if (data.base?.includes('osm')) {
        items.push({ id: 'osm', kind: 'osm', name: 'OSM' });
      }
      return items;
    },
    select(kind: 'osm' | 'geotiff' | 'enc', id?: string) {
      api.setBase(kind, id);
    },
  };
}
