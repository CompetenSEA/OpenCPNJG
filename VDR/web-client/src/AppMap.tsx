import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { createDeckOverlay } from './layers/DeckOverlay';

// AppMap loads the published style and overlays demo Deck.GL layers.
import { useMapStore } from './state';
import { Toolbar } from './components/Toolbar';

export const AppMap: React.FC = () => {
  const { zoom, center, palette, setZoom, setCenter } = useMapStore();
  const mapRef = useRef<maplibregl.Map | null>(null);
  const overlayRef = useRef<MapboxOverlay | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const map = new maplibregl.Map({
      container: containerRef.current!,
      style: `/style/s52.${palette}.json`,
      center,
      zoom,
    });
    mapRef.current = map;
    overlayRef.current = createDeckOverlay();
    map.addControl(overlayRef.current);
    map.on('moveend', () => {
      setZoom(map.getZoom());
      const c = map.getCenter();
      setCenter([c.lng, c.lat]);
    });
    return () => {
      overlayRef.current?.finalize();
      map.remove();
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const overlay = overlayRef.current;
    if (!map) return;
    map.setStyle(`/style/s52.${palette}.json`);
    if (overlay) {
      map.once('styledata', () => map.addControl(overlay));
    }
  }, [palette]);

  return (
    <div>
      <div style={{ height: '400px' }} ref={containerRef} />
      <Toolbar />
    </div>
  );
};
