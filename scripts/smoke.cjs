/* Minimal smoke for static dist (Node 18+ global fetch).
   Run: STAGE_URL=http://127.0.0.1:8081 node scripts/smoke.cjs */
const url = process.env.STAGE_URL || 'http://127.0.0.1:8081';
function hardAssert(c, m){ if(!c){ console.error(m); process.exit(3);} }

(async () => {
  try {
    const r = await fetch(url, { redirect: 'manual' });
    hardAssert(r.ok || r.status === 200, `SMOKEERR: index not OK (${r.status})`);
    const b = await r.text();
    if (!/id="map-root"/.test(b)) { console.error('SMOKE: map-root missing'); process.exit(3); }
    hardAssert(/<script[^>]+src="[^"]*index-.*?\.js"/.test(b), 'SMOKEERR: main bundle not referenced');
    if(!(/leaflet[-\w]*?\.js/.test(b) || /leaflet-src[-\w]*?\.js/.test(b))){
      console.warn('SMOKEWARN: leaflet bundle missing (likely lazy load)');
    }
    hardAssert(!/document\.write\(/.test(b), 'SMOKEERR: document.write found in index');
    console.log('SMOKE: OK');
    process.exit(0);
  } catch(e){
    console.error('SMOKEERR', e && e.stack || e);
    process.exit(3);
  }
})();
