const fs = require('fs'); const path = require('path');
const dist = path.resolve(process.cwd(), 'dist', 'index.html');
if (!fs.existsSync(dist)) { console.error('postbuild: dist/index.html not found'); process.exit(2); }
let html = fs.readFileSync(dist, 'utf8');
if (!/id="map-root"/.test(html)) {
  html = html.replace(/<\/body>/i, '<div id="map-root" style="display:none"></div>\n</body>');
  fs.writeFileSync(dist, html, 'utf8');
  console.log('postbuild: injected <div id="map-root"> into dist/index.html');
} else {
  console.log('postbuild: map-root already present — ok');
}
