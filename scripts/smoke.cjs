const http = require('http');
const https = require('https');
const { URL } = require('url');
function get(u){
  const U = new URL(u);
  const client = U.protocol === 'https:' ? https : http;
  return new Promise((res,rej)=>client.get(U,r=>{
    let d=''; r.on('data',c=>d+=c); r.on('end',()=>res({c:r.statusCode,b:d}));
  }).on('error',rej));
}
(async()=>{
  const base=process.env.STAGE_URL||'http://localhost:8080';
  const r=await get(base+'/');
  if(r.c!==200){ console.error('SMOKE: / status',r.c); process.exit(2); }
  if(!/id="map-root"/.test(r.b)){ console.error('SMOKE: map-root missing'); process.exit(3); }
  console.log('SMOKE: OK'); process.exit(0);
})().catch(e=>{console.error('SMOKEERR',e);process.exit(1);});
