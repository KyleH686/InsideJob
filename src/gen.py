import wave,subprocess,json,sys,os
sys.path.insert(0,'.')
from lines import L
from piper import PiperVoice
from piper.config import SynthesisConfig
V={'ctl':PiperVoice.load('../voices/en-gb-alan-low/en-gb-alan-low.onnx'),'grd':PiperVoice.load('../voices/en-us-ryan-high/en-us-ryan-high.onnx')}
for k,(v,t) in L.items():
    if os.path.exists(f'vo/{k}.mp3'): continue
    w=f'vo/{k}.wav'
    with wave.open(w,'wb') as f: V[v].synthesize_wav(t,f,syn_config=SynthesisConfig(length_scale=.92 if v=='ctl' else .85))
    af='highpass=f=350,lowpass=f=3300,acompressor=threshold=0.1:ratio=6,volume=1.6' if v=='ctl' else 'highpass=f=300,lowpass=f=3600,acompressor=threshold=0.15:ratio=4,volume=1.4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-af',af,'-ac','1','-ar','22050','-b:a','32k',f'vo/{k}.mp3'])
print(len(L))
