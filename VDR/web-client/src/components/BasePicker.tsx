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
      .then(setCharts)
      .catch(() => {});
  }, []);
  const community = process.env.OSM_USE_COMMUNITY !== '0';
  function select(kind: 'osm' | 'geotiff' | 'enc', id?: string) {
    api.setBase(kind, id);
    setBase(kind);
  }
  return null;
};

// lightweight helper for tests
export function createBasePickerAPI(api: ReturnType<typeof createMapAPI>) {
  return {
    async load(): Promise<Chart[]> {
      const resp = await fetch('/charts');
      return resp.json();
    },
    select(kind: 'osm' | 'geotiff' | 'enc', id?: string) {
      api.setBase(kind, id);
    },
  };
}
