import { readFileSync } from 'node:fs';
import { validateStyleMin } from '@maplibre/maplibre-gl-style-spec';
const path = process.argv[2];
if (!path) {
  console.error('Usage: node validate_style.mjs <style.json>');
  process.exit(2);
}
const style = JSON.parse(readFileSync(path, 'utf8'));
const result = validateStyleMin(style);
if (Array.isArray(result) && result.length) {
  console.error(JSON.stringify(result, null, 2));
  process.exit(2);
}
console.log('OK');
