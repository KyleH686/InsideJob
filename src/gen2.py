# Control lines: Kokoro (Apache 2.0) voice bf_lily. Guard lines are left as they are.
import subprocess,sys,os,soundfile as sf
sys.path.insert(0,'.')
from lines import L
from kokoro_onnx import Kokoro
k=Kokoro('../kok/dl/kokoro-v1.0.onnx','../kok/dl/voices-v1.0.bin')
AF='highpass=f=180,lowpass=f=6000,acompressor=threshold=0.2:ratio=3,loudnorm=I=-19.5:TP=-1.5:LRA=7'
only=sys.argv[1:]
n=0
for key,(v,t) in L.items():
    if v!='ctl' or (only and key not in only): continue
    s,sr=k.create(t,voice='bf_lily',speed=1.0,lang='en-gb');w=f'vo/{key}.wav';sf.write(w,s,sr)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-af',AF,'-ac','1','-ar','24000','-b:a','40k',f'vo/{key}.mp3'],check=True);os.remove(w);n+=1
print(n)
