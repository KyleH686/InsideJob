import json,sys,os
sys.path.insert(0,'../snd');from lines import L
s=open('src.html').read()
s=s.replace('/*__THREE__*/',open('three.min.js').read())
sfx=open('../snd/sfx.json').read();vo=open('../snd/vo.json').read()
s=s.replace('/*__SFX__*/{}',sfx).replace('/*__VO__*/{}',vo).replace('/*__VOTXT__*/{}',json.dumps({k:[v,t] for k,(v,t) in L.items()}))
open('inside-job.html','w').write(s)
p=s.replace('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n','')
p=p.replace('</head>\n<body data-theme="blueprint" data-mtab="build">','').replace('</body>\n</html>','')
p=p.replace("function setTheme(k){if(!STYLES[k])return;theme=k;","function setTheme(k){if(!STYLES[k])return;theme=k;document.body.dataset.theme=k;")
p=p.replace('<style>\n:root{','<style>\nhtml{background:#0c2f57}\n:root{',1)
os.makedirs('pub',exist_ok=True);open('pub/inside-job.html','w').write(p)
print(len(s)//1024,'KB')
# --- GitHub Pages / home-screen build
w=s.replace('<meta name="viewport" content="width=device-width,initial-scale=1">','<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n<meta name="theme-color" content="#0c2f57">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="black">\n<meta name="apple-mobile-web-app-title" content="Inside Job">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="icon-180.png">\n<link rel="icon" href="icon-192.png">\n<meta property="og:title" content="Inside Job">\n<meta property="og:description" content="A heist game from the other side. Five nights, six buildings, one security consultant.">\n<meta property="og:image" content="https://kyleh686.github.io/InsideJob/banner.png">\n<meta name="twitter:card" content="summary_large_image">',1)
w=w.replace('</body>\n</html>','<script>if("serviceWorker"in navigator&&location.protocol==="https:")navigator.serviceWorker.register("sw.js").catch(()=>{})</script>\n</body>\n</html>')
os.makedirs('web',exist_ok=True);open('web/index.html','w').write(w)
