import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { useMapStore } from './state';
import { registerCm93Sources, getDict, dictLookup } from './features/map/sources/cm93';
import { Toolbar } from './components/Toolbar';

const paletteColors: Record<string, string> = {
  day: '#a0a0f0',
  dusk: '#6666aa',
  night: '#333355',
};

export const MapComponent: React.FC = () => {
  const {
    zoom,
    center,
    safetyContour,
    palette,
    labelVisible,
    setZoom,
    setCenter,
  } = useMapStore();
  const mapRef = useRef<maplibregl.Map | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function init() {
      const map = new maplibregl.Map({
        container: containerRef.current!,
        style: { version: 8, sources: {}, layers: [] },
        center,
        zoom,
      });
      mapRef.current = map;
      await registerCm93Sources(map);
      const dict = getDict();
      const depareCode = Number(
        Object.keys(dict).find((id) => dictLookup(id) === 'DEPARE')
      );
      map.addLayer({
        id: 'DEPARE-fill',
        type: 'fill',
        source: 'cm93-core',
        'source-layer': 'features',
        filter: [
          'all',
          ['==', ['get', 'OBJL'], depareCode],
          ['<=', ['get', 'DRVAL1'], safetyContour],
        ],
        paint: { 'fill-color': paletteColors[palette] || '#a0a0f0' },
      });
      map.addLayer({
        id: 'cm93-label-layer',
        type: 'symbol',
        source: 'cm93-label',
        'source-layer': 'labels',
        layout: { 'text-field': ['get', 'text'] },
      });
      map.on('moveend', () => {
        setZoom(map.getZoom());
        const c = map.getCenter();
        setCenter([c.lng, c.lat]);
      });
    }
    init();
    return () => mapRef.current?.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const dict = getDict();
    const depareCode = Number(
      Object.keys(dict).find((id) => dictLookup(id) === 'DEPARE')
    );
    map.setFilter('DEPARE-fill', [
      'all',
      ['==', ['get', 'OBJL'], depareCode],
      ['<=', ['get', 'DRVAL1'], safetyContour],
    ]);
  }, [safetyContour]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.setPaintProperty('DEPARE-fill', 'fill-color', paletteColors[palette] || '#a0a0f0');
  }, [palette]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.setLayoutProperty(
      'cm93-label-layer',
      'visibility',
      labelVisible ? 'visible' : 'none'
    );
  }, [labelVisible]);

  return (
    <div>
      <div style={{ height: '400px' }} ref={containerRef} />
      <Toolbar />
    </div>
  );
};
