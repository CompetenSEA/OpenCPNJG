import create from 'zustand';

export interface MapState {
  zoom: number;
  center: [number, number];
  safetyContour: number;
  shallowContour: number;
  deepContour: number;
  palette: string;
  labelVisible: boolean;
  setZoom: (z: number) => void;
  setCenter: (c: [number, number]) => void;
  setSafetyContour: (s: number) => void;
  setShallowContour: (s: number) => void;
  setDeepContour: (d: number) => void;
  setPalette: (p: string) => void;
  setLabelVisible: (v: boolean) => void;
}

export const useMapStore = create<MapState>((set) => ({
  zoom: 2,
  center: [0, 0],
  safetyContour: 0,
  shallowContour: 0,
  deepContour: 0,
  palette: 'day',
  labelVisible: true,
  setZoom: (zoom) => set({ zoom }),
  setCenter: (center) => set({ center }),
  setSafetyContour: (safetyContour) => set({ safetyContour }),
  setShallowContour: (shallowContour) => set({ shallowContour }),
  setDeepContour: (deepContour) => set({ deepContour }),
  setPalette: (palette) => set({ palette }),
  setLabelVisible: (labelVisible) => set({ labelVisible }),
}));
