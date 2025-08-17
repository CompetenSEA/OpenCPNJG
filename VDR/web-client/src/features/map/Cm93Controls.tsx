import { useEffect } from 'react';
import maplibregl from 'maplibre-gl';
import {
  setLabelVisibility,
  setPalette,
  updateMarinerParams,
} from './sources/cm93';

interface Props {
  map: maplibregl.Map;
  showLabels: boolean;
  palette: 'day' | 'dusk' | 'night';
  safety?: number;
}

export const Cm93Controls = ({ map, showLabels, palette, safety }: Props) => {
  useEffect(() => {
    setLabelVisibility(map, showLabels);
  }, [map, showLabels]);
  useEffect(() => {
    setPalette(map, palette);
  }, [map, palette]);
  useEffect(() => {
    if (safety !== undefined) {
      updateMarinerParams(map, { safety });
    }
  }, [map, safety]);
  return null;
};

export function createCm93ControlsAPI(map: any) {
  return {
    labels(v: boolean) {
      setLabelVisibility(map, v);
    },
    palette(p: 'day' | 'dusk' | 'night') {
      setPalette(map, p);
    },
    safety(s: number) {
      updateMarinerParams(map, { safety: s });
    },
  };
}
