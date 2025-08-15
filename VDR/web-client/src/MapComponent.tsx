import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { useMapStore } from './state';

export const MapComponent: React.FC = () => {
  const { zoom, center, safetyContour, palette, setZoom, setCenter, setSafetyContour, setPalette } = useMapStore();
  const mapRef = useRef<maplibregl.Map | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const baseStyleRef = useRef<any | null>(null);

  useEffect(() => {
    async function init() {
      const resp = await fetch('/s52-style.json');
      const style = await resp.json();
      baseStyleRef.current = style;
      style.sources.cm93.tiles = [`/tiles/cm93/{z}/{x}/{y}?fmt=mvt&palette=${palette}&safetyContour=${safetyContour}`];
      const map = new maplibregl.Map({
        container: containerRef.current!,
        style,
        center,
        zoom,
      });
      mapRef.current = map;
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
    const base = baseStyleRef.current;
    if (!map || !base) return;
    const next = JSON.parse(JSON.stringify(base));
    next.sources.cm93.tiles = [`/tiles/cm93/{z}/{x}/{y}?fmt=mvt&palette=${palette}&safetyContour=${safetyContour}`];
    map.setStyle(next);
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
