import React from 'react';
import { useMapStore } from '../state';

export const Toolbar: React.FC = () => {
  const {
    safetyContour,
    shallowContour,
    deepContour,
    palette,
    labelVisible,
    setSafetyContour,
    setShallowContour,
    setDeepContour,
    setPalette,
    setLabelVisible,
  } = useMapStore();
  return (
    <div>
      <label>
        Labels
        <input
          type="checkbox"
          checked={labelVisible}
          onChange={(e) => setLabelVisible(e.target.checked)}
        />
      </label>
      <div>
        {['day', 'dusk', 'night'].map((p) => (
          <button key={p} onClick={() => setPalette(p)} disabled={palette === p}>
            {p}
          </button>
        ))}
      </div>
      <div>
        <label>Safety Contour: {safetyContour}m</label>
        <input
          type="range"
          min={0}
          max={20}
          value={safetyContour}
          onChange={(e) => setSafetyContour(Number(e.target.value))}
        />
      </div>
      <div>
        <label>Shallow Contour: {shallowContour}m</label>
        <input
          type="range"
          min={0}
          max={20}
          value={shallowContour}
          onChange={(e) => setShallowContour(Number(e.target.value))}
        />
      </div>
      <div>
        <label>Deep Contour: {deepContour}m</label>
        <input
          type="range"
          min={0}
          max={50}
          value={deepContour}
          onChange={(e) => setDeepContour(Number(e.target.value))}
        />
      </div>
    </div>
  );
};
