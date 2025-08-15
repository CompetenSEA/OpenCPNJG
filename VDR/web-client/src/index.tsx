import React from 'react';
import { createRoot } from 'react-dom/client';
import { MapComponent } from './MapComponent';

declare global {
  interface Window {
    __MAPLIBRE_DEBUG?: boolean;
  }
}

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<MapComponent />);
}
