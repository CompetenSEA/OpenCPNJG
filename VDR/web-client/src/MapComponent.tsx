import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { useMapStore } from './state';

export const MapComponent: React.FC = () => {
  const { zoom, center, safetyContour, palette, setZoom, setCenter, setSafetyContour, setPalette } = useMapStore();
  const mapRef = useRef<maplibregl.Map | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const map = new maplibregl.Map({
      container: containerRef.current!,
      style: { version: 8, sources: {}, layers: [] },
      center,
      zoom,
    });
    mapRef.current = map;
    map.on('moveend', () => {
      setZoom(map.getZoom());
      const c = map.getCenter();
      setCenter([c.lng, c.lat]);
    });
    return () => map.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const url = `/tiles/cm93/{z}/{x}/{y}?fmt=mvt&palette=${palette}&safetyContour=${safetyContour}`;
    if (map.getSource('cm93')) {
      map.removeLayer('SOUNDG');
      map.removeSource('cm93');
    }
    map.addSource('cm93', { type: 'vector', tiles: [url], maxzoom: 14 });
    map.addLayer({
      id: 'SOUNDG',
      type: 'circle',
      source: 'cm93',
      'source-layer': 'SOUNDG',
      paint: {
        'circle-color': ['case', ['get', 'isShallow'], '#000000', '#9c9c9c'],
      },
    });
  }, [safetyContour, palette]);

  return (
    <div>
      <div style={{ height: '400px' }} ref={containerRef} />
      <div>
        <label>Safety Contour: {safetyContour}m</label>
        <input
          type="range"
          min={0}
          max={20}
          value={safetyContour}
          onChange={(e) => setSafetyContour(Number(e.target.value))}
        />
        <div>
          {['day', 'dusk', 'night'].map((p) => (
            <button key={p} onClick={() => setPalette(p)} disabled={palette === p}>
              {p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
