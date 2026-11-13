// Screenshots of the iOS page at each device size. usage: node dev.js [outdir] [filter] [look]
const {chromium}=require('playwright');const fs=require('fs');
const D={ // name:[w,h,top,right,bottom,left]
 'se-p':[375,667,20,0,0,0],'ip-p':[390,844,47,0,34,0],'ip-l':[844,390,0,47,21,47],'max-p':[430,932,59,0,34,0],
 'duoC-p':[466,678,40,0,24,0],'duoC-l':[678,466,0,40,21,40],'duoO-p':[669,951,24,0,20,0],'duoO-l':[951,669,24,0,20,0],'duoS-p':[626,890,24,0,20,0],
 'mini-p':[744,1133,24,0,20,0],'pad-p':[820,1180,24,0,20,0],'pad-l':[1180,820,24,0,20,0],'pro-l':[1366,1024,24,0,20,0]};
const out=process.argv[2]||'dev';const filt=process.argv[3]||'';const look=process.argv[4]||'sketch3d';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
for(const n in D){if(filt&&!new RegExp(filt).test(n))continue;const [w,h,t,r,bo,l]=D[n];const ins={top:t,right:r,bottom:bo,left:l};
 let s=fs.readFileSync('ios/game.html','utf8');for(const k in ins)s=s.split(`env(safe-area-inset-${k})`).join(ins[k]+'px');const tf='ios/_t-'+n+'.html';fs.writeFileSync(tf,s);
 const c=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,hasTouch:true,isMobile:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.addInitScript(lk=>{window.requestAnimationFrame=()=>0;try{localStorage.setItem('ij-tut','1');localStorage.setItem('ij-theme',lk)}catch(e){}},look);
 await p.goto('file://'+__dirname+'/'+tf);await p.waitForTimeout(2200);
 const ov=()=>p.evaluate(()=>{const bad=[];const W=innerWidth,H=innerHeight;document.querySelectorAll('button,.tool,[role=button]').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height)return;const cs=getComputedStyle(e);if(cs.visibility==='hidden')return;if(r.right>W+1||r.bottom>H+1||r.left<-1||r.top<-1)bad.push((e.id||e.textContent.trim().slice(0,14))+':off');else if(r.width<30||r.height<30)bad.push((e.id||e.textContent.trim().slice(0,14))+':'+Math.round(r.width)+'x'+Math.round(r.height))});return bad.slice(0,14).join(', ')});
 const R={};
 await p.evaluate(()=>{for(let k=0;k<3;k++)frame(performance.now())});await p.screenshot({path:`${out}/${n}-1home.png`});R.home=await ov();
 await p.evaluate(()=>{hideHome();SITE='gallery';clearSave();newGame();for(let k=0;k<10;k++)render(1/30)});await p.waitForTimeout(200);await p.screenshot({path:`${out}/${n}-2build.png`});R.build=await ov();
 R.cls=await p.evaluate(()=>document.body.className+' u'+LAY.u.toFixed(2)+(document.querySelector('#tools').getBoundingClientRect().bottom>document.querySelector('#buildCard').getBoundingClientRect().bottom+1?' TOOLS-CLIPPED':''));R.stage=await p.evaluate(()=>{const r=document.querySelector('#stage').getBoundingClientRect();return Math.round(r.width)+'x'+Math.round(r.height)+' '+Math.round(100*r.width*r.height/(innerWidth*innerHeight))+'%'});
 await p.evaluate(()=>{try{optionsSheet()}catch(e){}});await p.waitForTimeout(250);await p.screenshot({path:`${out}/${n}-3opt.png`});R.opt=await ov();
 if(process.argv[5]==='full'){
  await p.evaluate(()=>{hideSheet();ST.cash=5000;try{place('guard',idx(22,20),{noRoute:true});const g=ST.devices.find(d=>d.type==='guard');g.route=[idx(32,13),idx(22,13)];place('camera',idx(20,18));devicesChanged()}catch(e){};ST.sel=ST.devices.find(d=>d.type==='camera');refreshUI();resize();for(let k=0;k<6;k++)render(1/30)});await p.waitForTimeout(150);await p.screenshot({path:`${out}/${n}-4sel.png`});R.sel=await ov()+await p.evaluate(()=>{const b=[...document.querySelectorAll('#selBtns button')].pop();return b&&b.getBoundingClientRect().bottom>document.querySelector('#buildCard').getBoundingClientRect().bottom+1?' SEL-CLIPPED':''});
  await p.evaluate(()=>{ST.sel=null;refreshUI();startNight();let k=0;while(k<60*40&&!ST.thieves.some(t=>t.state==='in')){stepSim(1/60);if(k%40===0)render(1/10);k++}for(let j=0;j<90;j++){stepSim(1/60);if(j%3===0)render(1/20)}refreshUI()});await p.waitForTimeout(150);await p.screenshot({path:`${out}/${n}-5night.png`});R.night=await ov();
  await p.evaluate(()=>{setMTab('crew');for(let k=0;k<3;k++)render(1/30)});await p.waitForTimeout(100);await p.screenshot({path:`${out}/${n}-6crew.png`});
  await p.evaluate(()=>{setMTab('build');try{endNight()}catch(e){};for(let k=0;k<5;k++)render(1/30)});await p.waitForTimeout(500);await p.screenshot({path:`${out}/${n}-7report.png`});R.rep=await ov();
 }
 console.log(n,JSON.stringify(R),errs.slice(0,3).join('|'));await c.close()}
await b.close()})();
