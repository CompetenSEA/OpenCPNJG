import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppMap } from './AppMap';

declare global {
  interface Window {
    __MAPLIBRE_DEBUG?: boolean;
    VDR_CONFIG?: { enableServiceWorker?: boolean };
  }
}

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<AppMap />);
}

// Prevent default install prompts (no A2HS UI)
window.addEventListener('beforeinstallprompt', (e) => e.preventDefault());

// Optional service worker registration behind config flag
if ('serviceWorker' in navigator && window.VDR_CONFIG?.enableServiceWorker) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((err) => {
      console.error('Service worker registration failed', err);
    });
  });
}
