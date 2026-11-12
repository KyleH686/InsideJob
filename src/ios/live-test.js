// Tests the iOS app loader: app origin on :8701 (ios/ folder), fake "GitHub Pages" on :8702 with switchable behaviour.
const {chromium,devices}=require('playwright');const fs=require('fs'),http=require('http'),crypto=require('crypto'),path=require('path');
const game=fs.readFileSync('ios/game.html');const mk=(v,brk)=>{let h=game.toString('utf8').replace('Inside Job · v30 · ','Inside Job · v'+v+' · ');if(brk)h=h.replace('<script>window.IJ_APP=true</script>','<script>window.IJ_APP=true;throw new Error("boom")</script>').replace('function frame(','function frameX(');return Buffer.from(h)};
const ver=(b,v,o)=>JSON.stringify(Object.assign({v,size:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex'),shell:1},o||{}));
let R={mode:'off'},hits=[];
http.createServer((q,s)=>{let f=q.url.split('?')[0];if(f==='/')f='/index.html';const p=path.join('ios',f);if(!fs.existsSync(p)){s.writeHead(404);return s.end()}
 s.writeHead(200,{'content-type':f.endsWith('.css')?'text/css':f.endsWith('.woff2')?'font/woff2':f.endsWith('.json')?'application/json':'text/html; charset=utf-8'});s.end(fs.readFileSync(p))}).listen(8701);
http.createServer((q,s)=>{const f=q.url.split('?')[0];hits.push(f);const H={'access-control-allow-origin':'*'};
 if(R.mode==='off'){return q.socket.destroy()}
 if(R.mode==='hang')return; // never answers
 if(R.mode==='500'){s.writeHead(500,H);return s.end('no')}
 if(f==='/version.json'){s.writeHead(200,H);return s.end(R.vjson)}
 if(f==='/game.html'){if(R.stall){s.writeHead(200,H);s.write(R.body.slice(0,500000));return}
  s.writeHead(200,H);let o=0;const step=()=>{if(o>=R.body.length)return s.end();s.write(R.body.slice(o,o+400000));o+=400000;setTimeout(step,R.slow||5)};return step()}
 s.writeHead(404,H);s.end()}).listen(8702);
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const out=[];const ok=(n,c,x)=>{const l=(c?'PASS ':'FAIL ')+n+(x?'  '+x:'');out.push(l);console.error(new Date().toISOString().slice(14,19),l);};
async function ctx(extra){const c=await b.newContext({...devices['iPhone 13']});const p=await c.newPage();p.errs=[];p.on('pageerror',e=>p.errs.push(e.message));
 await p.addInitScript(x=>{window.requestAnimationFrame=()=>0;window.IJ_REMOTE='http://127.0.0.1:8702/';Object.assign(window,x||{});try{if(!localStorage.getItem('ij-tut')){localStorage.setItem('ij-tut','1');localStorage.setItem('ij-theme','sketch3d');localStorage.setItem('ij-best','{"keep":7}')}}catch(e){}},extra);return [c,p]}
async function open(p,wait){hits=[];p.errs.length=0;const t=Date.now();await p.goto('http://127.0.0.1:8701/');await p.waitForFunction(()=>window.IJ_LIVE&&typeof frame==='function'&&document.querySelector('.hfoot'),null,{timeout:wait||40000,polling:100}).catch(()=>{});
 const r=await p.evaluate(()=>({live:window.IJ_LIVE,foot:(document.querySelector('.hfoot')||{}).textContent,app:window.IJ_APP,best:localStorage.getItem('ij-best'),tr:localStorage.getItem('ijx-try'),okv:localStorage.getItem('ijx-ok'),frame:typeof frame}));r.ms=Date.now()-t;r.hits=hits.slice();return r}
const v=r=>r.foot?(r.foot.match(/v(\d+)/)||[])[1]:'none';
const plays=async p=>{await p.waitForTimeout(1500);return p.evaluate(()=>{try{for(let k=0;k<3;k++)frame(performance.now());hideHome();SITE='gallery';clearSave();newGame();for(let k=0;k<10;k++)render(1/30);const st=document.querySelector('#stage').getBoundingClientRect();return {w:Math.round(st.width),fonts:[...document.fonts].filter(f=>f.status==='loaded').length,three:typeof R3!=='undefined'&&!!R3.kit,sw:document.documentElement.scrollWidth,iw:innerWidth}}catch(e){return {err:e.message}}})};
const v31=mk(31),v32=mk(32),bad=mk(33,true);
// 1 offline, first launch
{const [c,p]=await ctx();R={mode:'off'};const r=await open(p);ok('offline first launch runs built-in v30',v(r)==='30'&&r.live&&!r.live.live&&r.app===true,JSON.stringify({ms:r.ms,errs:p.errs}));
 const g=await plays(p);ok('built-in copy plays (3D, fonts, no overflow)',!g.err&&g.three&&g.fonts>=3&&g.sw<=g.iw&&!p.errs.length,JSON.stringify(g)+p.errs.join('|'));await p.screenshot({path:'live-1.png'});
 // 2 server answers 500
 R={mode:'500'};let r2=await open(p);ok('server error runs v30',v(r2)==='30',r2.ms+'ms');
 // 3 server never answers
 {const [c2,p2]=await ctx();R={mode:'hang'};const r3=await open(p2);ok('silent server: starts v30 within 5 s',v(r3)==='30'&&r3.ms<5000,r3.ms+'ms');await c2.close()}
 // 4 same version online
 R={mode:'on',vjson:ver(game,30),body:game};r2=await open(p);ok('same version: no download',v(r2)==='30'&&!r2.hits.includes('/game.html'),r2.hits.join(','));
 // 5 needs newer app shell
 R={mode:'on',vjson:ver(v31,31,{shell:2}),body:v31};r2=await open(p);ok('update needing a newer app is ignored',v(r2)==='30'&&!r2.hits.includes('/game.html'));
 // 6 damaged downloads
 R={mode:'on',vjson:ver(v31,31,{size:v31.length+5}),body:v31};r2=await open(p);ok('wrong size rejected, runs v30',v(r2)==='30'&&r2.hits.includes('/game.html'));
 R={mode:'on',vjson:ver(v31,31,{sha256:'00'}),body:v31};r2=await open(p);ok('wrong checksum rejected, runs v30',v(r2)==='30');
 R={mode:'on',vjson:ver(v31,31),body:v31.slice(0,v31.length-9)};r2=await open(p);ok('cut-off file rejected, runs v30',v(r2)==='30');
 await c.close()}
// 7 stalled download + skip
{const [c,p]=await ctx({IJ_STALL_MS:2500});R={mode:'on',vjson:ver(v31,31),body:v31,stall:1};let r=await open(p);ok('stalled download gives up, runs v30',v(r)==='30',r.ms+'ms');await c.close()}
{const [c,p]=await ctx();R={mode:'on',vjson:ver(v31,31),body:v31,slow:400};hits=[];const t=Date.now();await p.goto('http://127.0.0.1:8701/');await p.waitForFunction(()=>document.querySelector('#u.on'),null,{timeout:5000,polling:100});await p.waitForTimeout(900);await p.screenshot({path:'live-updating.png'});const w=await p.evaluate(()=>document.getElementById('fill').style.width+' '+document.getElementById('msg').textContent);await p.click('#skip');await p.waitForFunction(()=>window.IJ_LIVE&&document.querySelector('.hfoot'),null,{timeout:8000,polling:100}).catch(()=>{});
 const f=await p.evaluate(()=>(document.querySelector('.hfoot')||{}).textContent||'');ok('progress shown, Skip starts v30 at once',/v30/.test(f)&&/Updating to v31/.test(w)&&Date.now()-t<6000,w+' '+(Date.now()-t)+'ms');await c.close()}
// 8 good update, then offline, then newer update, saves kept
{const [c,p]=await ctx();R={mode:'on',vjson:ver(v31,31),body:v31};let r=await open(p);ok('update downloads and runs v31',v(r)==='31'&&r.live.live&&r.app===true,r.ms+'ms '+p.errs.join('|'));ok('save data kept across update',r.best==='{"keep":7}');
 const g=await plays(p);ok('updated copy plays (3D, fonts, no overflow)',!g.err&&g.three&&g.fonts>=3&&g.sw<=g.iw&&!p.errs.length,JSON.stringify(g)+p.errs.join('|'));await p.screenshot({path:'live-2.png'});
 await p.waitForTimeout(3500);const okv=await p.evaluate(()=>localStorage.getItem('ijx-ok'));ok('update marked as working',okv==='31',okv);
 R={mode:'off'};r=await open(p);ok('offline afterwards still runs v31',v(r)==='31',r.ms+'ms');
 R={mode:'on',vjson:ver(v31,31),body:v31};r=await open(p);ok('online, nothing new: v31, no download',v(r)==='31'&&!r.hits.includes('/game.html'));
 R={mode:'on',vjson:ver(v32,32),body:v32};r=await open(p);ok('next update runs v32',v(r)==='32');
 R={mode:'on',vjson:ver(v31,31,{sha256:'00'}),body:v31};r=await open(p);ok('older version online is ignored',v(r)==='32'&&!r.hits.includes('/game.html'));
 // 9 update that will not start
 R={mode:'on',vjson:ver(bad,33),body:bad};r=await open(p,7000);const a=r.tr;await p.waitForTimeout(4500);r=await open(p,7000);const b2=r.tr;await p.waitForTimeout(4500);
 r=await open(p);ok('update that will not start is dropped after two tries',a==='33:1'&&b2==='33:2'&&v(r)==='30'&&!r.hits.includes('/game.html'),[a,b2,v(r),r.hits.join(',')].join(' '));
 const v34=mk(34);R={mode:'on',vjson:ver(v34,34),body:v34};r=await open(p);ok('a later fixed update still installs',v(r)==='34');
 await c.close()}
await b.close();process.exit(0)})();
