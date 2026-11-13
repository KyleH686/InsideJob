# Guard lines: Kokoro (Apache 2.0) voice bm_george, through a walkie-talkie filter. Replaces the old piper guard voice.
# Usage: python gen3.py <kokoro-v1.0.onnx> <voices-v1.0.bin> [out.json]
# Writes the guard lines into snd/vo.json (or into out.json, a copy, if given).
import subprocess,sys,os,json,base64,tempfile,soundfile as sf
here=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,here)
from lines import L
from kokoro_onnx import Kokoro
from kokoro_onnx.config import EspeakConfig
# On macOS the espeak-ng bundled with kokoro-onnx can't find its data; point it at a system espeak-ng instead
# (brew install espeak-ng), e.g. ESPEAK_LIB=/opt/homebrew/lib/libespeak-ng.dylib ESPEAK_DATA=/opt/homebrew/share/espeak-ng-data
ec=EspeakConfig(lib_path=os.environ['ESPEAK_LIB'],data_path=os.environ.get('ESPEAK_DATA')) if os.environ.get('ESPEAK_LIB') else None
k=Kokoro(sys.argv[1],sys.argv[2],espeak_config=ec)
AF='silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.06,highpass=f=300,lowpass=f=3600,acompressor=threshold=0.15:ratio=4,loudnorm=I=-19:TP=-1.5:LRA=7'
src=os.path.join(here,'snd','vo.json');out=sys.argv[3] if len(sys.argv)>3 else src
vo=json.load(open(src));tmp=tempfile.mkdtemp();n=0
for key,(v,t) in L.items():
    if v!='grd': continue
    s,sr=k.create(t,voice='bm_george',speed=1.12,lang='en-gb')
    w=os.path.join(tmp,key+'.wav');m=os.path.join(tmp,key+'.mp3');sf.write(w,s,sr)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-af',AF,'-ac','1','-ar','22050','-b:a','32k',m],check=True)
    vo[key]=base64.b64encode(open(m,'rb').read()).decode();n+=1
json.dump(vo,open(out,'w'));print(n,'guard lines ->',out,os.path.getsize(out)//1024,'KB')
