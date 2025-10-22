const fs = require('fs');
const path = require('path');
const file = path.resolve(process.cwd(), 'index.html');
if (!fs.existsSync(file)) {
  console.error('fix-map-root: index.html not found at project root');
  process.exit(2);
}
let s = fs.readFileSync(file, 'utf8');
const hadRoot = /id="(root|app)"/.test(s);
s = s.replace(/id="(root|app)"/, 'id="map-root"');
if (!/id="map-root"/.test(s)) {
  s = s.replace(/<\/body>/i, '<div id="map-root"></div>\n</body>');
}
fs.writeFileSync(file, s, 'utf8');
console.log('fix-map-root: index.html normalized to id="map-root"', hadRoot ? '(replaced)' : '(inserted)');
