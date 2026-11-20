import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from lines import L
s=open('src.html').read()
s=s.replace('/*__THREE__*/',open('three.min.js').read())
s=s.replace('/*__R3X__*/',open('kk/r3x.js').read()).replace('/*__CHARS__*/{}',open('kk/chars.json').read())
sfx=open('snd/sfx.json').read();vo=open('snd/vo.json').read()
s=s.replace('/*__SFX__*/{}',sfx).replace('/*__VO__*/{}',vo).replace('/*__VOTXT__*/{}',json.dumps({k:[v,t] for k,(v,t) in L.items()}))
open('inside-job.html','w').write(s)
p=s.replace('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n','')
p=p.replace('</head>\n<body data-theme="blueprint" data-mtab="build">','').replace('</body>\n</html>','')
p=p.replace("function setTheme(k){if(!STYLES[k])return;theme=k;","function setTheme(k){if(!STYLES[k])return;theme=k;document.body.dataset.theme=k;")
p=p.replace('<style>\n:root{','<style>\nhtml{background:#0c2f57}\n:root{',1)
os.makedirs('pub',exist_ok=True);open('pub/inside-job.html','w').write(p)
print(len(s)//1024,'KB')

# v39: keep the game inside the notch / Dynamic Island / home bar on phones, with a small extra margin,
# and paint the bars around it in the selected theme's background colour.
# Some iOS web views report env(safe-area-inset-*) as 0 after the loader swaps the page in, so the
# app and home-screen web app fall back to the known iPhone insets when that happens.
SAFE_CSS='<style>:root{--pe:0px;--sat:max(env(safe-area-inset-top),var(--fsat,0px));--sar:max(env(safe-area-inset-right),var(--fsar,0px));--sab:max(env(safe-area-inset-bottom),var(--fsab,0px));--sal:max(env(safe-area-inset-left),var(--fsal,0px))}\n@media (pointer:coarse) and (max-width:500px),(pointer:coarse) and (max-height:500px){:root{--pe:6px}}\nhtml{background:var(--ijbg,#0c2f57)}\nbody{box-sizing:border-box;padding:calc(var(--sat) + var(--pe)) calc(var(--sar) + var(--pe)) calc(var(--sab) + var(--pe)) calc(var(--sal) + var(--pe))}#app{height:100%!important}</style>\n</head>'
SAFE_JS='<script>(function(){var d=document.documentElement,last="";function safe(){var p=document.createElement("div");p.style.cssText="position:fixed;visibility:hidden;pointer-events:none;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)";document.body.appendChild(p);var c=getComputedStyle(p),z=!(parseFloat(c.paddingTop)||parseFloat(c.paddingBottom)||parseFloat(c.paddingLeft)||parseFloat(c.paddingRight));p.remove();var t=0,r=0,b=0,l=0,L=Math.max(screen.width,screen.height),S=Math.min(screen.width,screen.height);if(z&&(window.IJ_APP||navigator.standalone)&&/iPhone/.test(navigator.userAgent)&&L>=812&&S<500){var n=L>=852?59:47;if(innerWidth>innerHeight){l=r=n;b=21}else{t=n;b=34}}var k=[t,r,b,l].join();if(k===last)return;last=k;d.style.setProperty("--fsat",t+"px");d.style.setProperty("--fsar",r+"px");d.style.setProperty("--fsab",b+"px");d.style.setProperty("--fsal",l+"px");if(t||r||b||l)setTimeout(function(){dispatchEvent(new Event("resize"))},0)}function bg(){var v=getComputedStyle(document.body).getPropertyValue("--bg").trim();if(!v)return;d.style.setProperty("--ijbg",v);var m=document.querySelector("meta[name=theme-color]");if(m)m.setAttribute("content",v)}safe();bg();addEventListener("resize",safe);addEventListener("orientationchange",function(){setTimeout(safe,300)});new MutationObserver(bg).observe(document.body,{attributes:true,attributeFilter:["data-theme"]})})()</script>\n</body>\n</html>'
# --- GitHub Pages / home-screen build
w=s.replace('<meta name="viewport" content="width=device-width,initial-scale=1">','<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n<meta name="theme-color" content="#0c2f57">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="black">\n<meta name="apple-mobile-web-app-title" content="Inside Job">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="icon-180.png">\n<link rel="icon" href="icon-192.png">\n<meta property="og:title" content="Inside Job">\n<meta property="og:description" content="A heist game from the other side. Five nights, six buildings, one security consultant.">\n<meta property="og:image" content="https://kyleh686.github.io/InsideJob/banner.png">\n<meta name="twitter:card" content="summary_large_image">',1)
# the page draws edge to edge (viewport-fit=cover); SAFE_CSS/SAFE_JS keep the game clear of the notch and home bar
w=w.replace('</head>',SAFE_CSS,1);w=w.replace('</body>\n</html>',SAFE_JS,1);assert 'MutationObserver(bg)' in w
w=w.replace('</body>\n</html>','<script>if("serviceWorker"in navigator&&location.protocol==="https:")navigator.serviceWorker.register("sw.js").catch(()=>{})</script>\n</body>\n</html>')
os.makedirs('web',exist_ok=True);open('web/index.html','w').write(w)

# --- iOS app build (Capacitor / Xcode): offline fonts, notch safe areas, no browser-only bits
import re
i=re.sub(r'<link rel="preconnect"[^>]*>\n','',s)
i,n=re.subn(r'<link href="https://fonts.googleapis.com[^>]*>','<link rel="stylesheet" href="fonts/fonts.css">',i);assert n==1
i=i.replace('<meta name="viewport" content="width=device-width,initial-scale=1">','<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n<script>window.IJ_APP=true</script>',1)
i=i.replace('</head>',SAFE_CSS,1);i=i.replace('</body>\n</html>',SAFE_JS,1);assert 'MutationObserver(bg)' in i
# The app opens index.html, a small loader. It starts game.html, or a newer copy it fetched from GitHub Pages
# (this same folder is served there). version.json tells installed apps which version is live.
import hashlib
ver=int(re.search(r'Inside Job · v(\d+) · ',s).group(1));ib=i.encode('utf-8')
os.makedirs('ios',exist_ok=True);open('ios/game.html','wb').write(ib)
ld=open('ios/loader.html').read();assert '/*__VER__*/0' in ld
# Live updates (the app fetching newer game.html from GitHub Pages) are OFF for App Store builds. IJ_LIVE=1 python3 build.py turns them back on for play-testing builds.
LIVE=os.environ.get('IJ_LIVE','0')=='1';assert '/*__LIVE__*/1' in ld
open('ios/index.html','w').write(ld.replace('/*__VER__*/0',str(ver)).replace('/*__LIVE__*/1','1' if LIVE else '0'))
open('ios/version.json','w').write(json.dumps({'v':ver,'size':len(ib),'sha256':hashlib.sha256(ib).hexdigest(),'shell':1})+'\n')
print('ios v%d'%ver,len(ib)//1024,'KB','live updates ON' if LIVE else 'live updates off (App Store)')
