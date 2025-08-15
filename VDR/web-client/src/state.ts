import create from 'zustand';

export interface MapState {
  zoom: number;
  center: [number, number];
  safetyContour: number;
  palette: string;
  setZoom: (z: number) => void;
  setCenter: (c: [number, number]) => void;
  setSafetyContour: (s: number) => void;
  setPalette: (p: string) => void;
}

export const useMapStore = create<MapState>((set) => ({
  zoom: 2,
  center: [0, 0],
  safetyContour: 0,
  palette: 'day',
  setZoom: (zoom) => set({ zoom }),
  setCenter: (center) => set({ center }),
  setSafetyContour: (safetyContour) => set({ safetyContour }),
  setPalette: (palette) => set({ palette }),
}));
