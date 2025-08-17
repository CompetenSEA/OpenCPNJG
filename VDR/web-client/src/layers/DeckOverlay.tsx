import { MapboxOverlay } from '@deck.gl/mapbox';
import { IconLayer, PathLayer, TripsLayer } from '@deck.gl/layers';

export function createPathLayer(data: any[] = []) {
  return new PathLayer({
    id: 'demo-path',
    data,
    getPath: (d: any) => d.path,
    getColor: [255, 0, 0],
    widthMinPixels: 2,
  });
}

export function createTripsLayer(data: any[] = []) {
  return new TripsLayer({
    id: 'demo-trips',
    data,
    getPath: (d: any) => d.path,
    getTimestamps: (d: any) => d.timestamps,
    getColor: [0, 128, 255],
    widthMinPixels: 2,
    trailLength: 180,
    currentTime: 0,
  });
}

export function createIconLayer(data: any[] = []) {
  return new IconLayer({
    id: 'demo-icons',
    data,
    getPosition: (d: any) => d.coordinates,
    getIcon: (d: any) => d.icon,
    getSize: 24,
    iconAtlas: '',
    iconMapping: {},
  });
}

export function createDeckOverlay(): MapboxOverlay {
  return new MapboxOverlay({
    layers: [createPathLayer(), createTripsLayer(), createIconLayer()],
  });
}
