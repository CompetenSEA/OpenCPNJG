#!/usr/bin/env node
/**
 * Bake Mapbox glyph PBFs from the fonts listed in
 * `VDR/server-styling/fonts.lock`. Download the referenced .ttf files and
 * place them in `VDR/assets/fonts/` before running. The generated glyphs are
 * written to `<repo>/glyphs/{fontstack}/{start}-{end}.pbf`.
 */
const fs = require('fs');
const path = require('path');
const fontnik = require('fontnik');

async function rangeAsync(buf, start, end) {
  return new Promise((resolve, reject) => {
    fontnik.range({ font: buf, start, end }, (err, res) => {
      if (err) reject(err); else resolve(res);
    });
  });
}

async function bake() {
  const root = path.resolve(__dirname, '..');
  const lockPath = path.join(root, 'server-styling', 'fonts.lock');
  const lock = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
  const glyphsDir = path.resolve(root, '..', 'glyphs');

  for (const font of lock.fonts) {
    const fontstack = path.basename(font.file, path.extname(font.file));
    const ttfPath = path.join(root, 'assets', 'fonts', font.file);
    const buf = fs.readFileSync(ttfPath);
    for (let start = 0; start < 65536; start += 256) {
      const end = start + 255;
      const pbf = await rangeAsync(buf, start, end);
      const outDir = path.join(glyphsDir, fontstack);
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(path.join(outDir, `${start}-${end}.pbf`), pbf);
    }
    console.log(`Baked glyphs for ${fontstack}`);
  }
}

bake().catch(err => {
  console.error(err);
  process.exit(1);
});
