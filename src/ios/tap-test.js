// Real taps on the touch layout at each device size: pick a tool, place it, rotate, start the night, change speed, tabs, menu.
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const [n,w,h] of [['iPhone',390,844],['iPhone landscape',844,390],['Duo folded',466,678],['Duo open',669,951],['iPad',820,1180],['iPad landscape',1180,820]]){
 const c=await b.newContext({viewport:{width:w,height:h},hasTouch:true,isMobile:true});const p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.addInitScript(()=>{window.requestAnimationFrame=()=>0;localStorage.setItem('ij-tut','1');localStorage.setItem('ij-theme','sketch')});
 await p.goto('file://'+__dirname+'/ios/game.html');await p.waitForTimeout(1200);
 await p.evaluate(()=>{hideHome();SITE='gallery';clearSave();newGame();resize();for(let k=0;k<5;k++)render(1/30)});
 const R={};
 await p.locator('#tools .tool').nth(0).tap();R.tool=await p.evaluate(()=>ST.tool);
 const pt=await p.evaluate(()=>{const r=cv.getBoundingClientRect();return [r.left+(20.5/W)*r.width,r.top+(18.5/H)*r.height]});
 await p.touchscreen.tap(pt[0],pt[1]);await p.waitForTimeout(250);await p.evaluate(()=>{for(let k=0;k<3;k++)render(1/30)});
 R.placed=await p.evaluate(()=>ST.devices.map(d=>d.type+'@'+d.x+','+d.y).join(' '));R.sel=await p.evaluate(()=>!!ST.sel);
 if(R.sel){const nb=p.locator('#selBtns button');R.btns=await nb.count();
  const snap=()=>p.evaluate(()=>ST.sel?JSON.stringify(ST.sel,(k,v)=>typeof v==='number'?+v.toFixed(3):(typeof v==='object'&&v&&k&&k[0]==='_')?undefined:v).slice(0,400):'none');
  const a=await snap();await nb.nth(0).tap();const z=await snap();R.rotated=a!==z;
  await p.locator('#selBtns button',{hasText:'Done'}).tap().catch(()=>{});R.done=await p.evaluate(()=>!ST.sel)}
 await p.locator('#go').tap();await p.waitForTimeout(200);R.phase=await p.evaluate(()=>ST.phase);
 await p.evaluate(()=>{for(let j=0;j<60;j++){stepSim(1/60)}render(1/30);refreshUI()});
 await p.locator('#speedRow button').nth(2).tap();R.speed=await p.evaluate(()=>ST.speed);
 R.abil=await p.evaluate(()=>[...document.querySelectorAll('#abil button')].map(e=>{const r=e.getBoundingClientRect();return Math.round(r.width)+'x'+Math.round(r.height)}).join(' '));
 await p.locator('#mtabs button').nth(2).tap();R.tab=await p.evaluate(()=>document.body.dataset.mtab);
 await p.locator('#homeBtn').tap();R.home=await p.evaluate(()=>homeOn());await p.locator('#hMenu button').nth(0).tap();R.resumed=await p.evaluate(()=>!homeOn());
 const good=R.tool==='camera'&&/camera@/.test(R.placed)&&R.sel&&R.rotated&&R.done&&R.phase==='heist'&&R.speed===4&&R.tab==='radio'&&R.home&&R.resumed&&!errs.length;
 console.log(good?'PASS':'FAIL',n,JSON.stringify(R),errs.join('|'));await c.close()}
await b.close()})();
