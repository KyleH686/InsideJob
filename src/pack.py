import subprocess,base64,json,os,glob
G={
 'step':['dl/footstep_concrete_000.ogg','dl/footstep_concrete_001.ogg','dl/footstep_concrete_002.ogg','dl/footstep_concrete_003.ogg'],
 'doorOpen':['ss/doorOpen_0.mp3','ss/doorOpen_1.mp3'],
 'slam':['dl/doorClose_000.ogg','dl/doorClose_001.ogg','dl/doorClose_002.ogg'],
 'slamHit':['dl/impactPlate_heavy_000.ogg'],
 'zap':['dl/zap_0.ogg','dl/zap_1.ogg'],
 'mirror':['dl/forceField_000.ogg','dl/forceField_001.ogg'],
 'plate':['dl/impactMetal_heavy_000.ogg','dl/impactMetal_heavy_001.ogg'],
 'click':['ss/metalClick_0.mp3','ss/latch_0.mp3'],
 'tackle':['dl/impactPunch_heavy_000.ogg','dl/impactPunch_heavy_001.ogg'],
 'bodyDrop':['ss/bodyDrop_0.mp3','ss/bodyDrop_1.mp3'],
 'stamp':['dl/impactWood_heavy_000.ogg'],
 'place':['dl/chips_0.ogg','dl/chips_1.ogg'],
 'sell':['ss/coins_0.mp3','ss/coins_1.mp3'],
 'grab':['ss/metal_0.mp3','ss/metal_1.mp3','ss/cloth_0.mp3'],
 'breach':['dl/impactMetal_000.ogg','dl/impactMetal_001.ogg','dl/impactMetal_002.ogg','dl/impactMetal_003.ogg'],
 'crack':['ss/tick_0.mp3','ss/metalClick_0.mp3','ss/switch_0.mp3'],
 'smoke':['dl/woosh.ogg'],
 'hiss':['dl/slime_000.ogg'],
 'glitch':['dl/phaserDown.ogg'],
 'static':['ss/static_0.mp3','ss/static_1.mp3','ss/static_2.mp3','ss/static_3.mp3'],
 'alarm':['dl/twoTone.ogg'],
 'alarm3':['dl/threeTone.ogg'],
 'ui':['dl/select_005.ogg','dl/click_003.ogg'],
 'deny':['dl/error_004.ogg','dl/error_006.ogg'],
 'confirm':['dl/confirmation_002.ogg','dl/confirmation_004.ogg'],
 'upgrade':['dl/maximize_006.ogg'],
 'fake':['dl/impactGlass_heavy_000.ogg'],
 'lowDown':['dl/lowDown.ogg'],
 'bell':['dl/impactBell_heavy_000.ogg'],
 'jingGood':['dl/jing_good.ogg'],'jingBad':['dl/jing_bad.ogg'],'jingCatch':['dl/jing_catch.ogg'],
 'stun':['dl/zap3down.ogg'],
 'boom':['dl/lowFrequency_explosion_000.ogg'],
 'stepWood':['ss/stepWood_0.mp3','ss/stepWood_1.mp3','ss/stepWood_2.mp3','ss/stepWood_3.mp3'],
 'stepCarpet':['ss/stepCarpet_0.mp3','ss/stepCarpet_1.mp3','ss/stepCarpet_2.mp3'],
 'stepHard':['ss/stepHard_0.mp3','ss/stepHard_1.mp3','ss/stepHard_2.mp3','ss/stepHard_3.mp3'],
 'stepGrass':['ss/stepGrass_0.mp3','ss/stepGrass_1.mp3'],
 'creak':['ss/creak_0.mp3','ss/creak_1.mp3','ss/creak_2.mp3'],
 'cuffs':['ss/latch_0.mp3','dl/impactPlate_light_000.ogg'],
 'rustle':['ss/leather_0.mp3','ss/leather_1.mp3'],
 'whoosh':['dl/scratch_002.ogg'],
}
out={}
os.makedirs('enc',exist_ok=True)
for k,fs in G.items():
    out[k]=[]
    for n,f in enumerate(fs):
        o=f'enc/{k}_{n}.mp3'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f,'-t','2.5','-ac','1','-ar','24000','-b:a','40k',o],check=True)
        out[k].append(base64.b64encode(open(o,'rb').read()).decode())
for n,f in [('musHeist','dl/mus_heist.ogg'),('musPlan','dl/mus_plan.ogg')]:
    o=f'enc/{n}.mp3';subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f,'-ac','1','-ar','32000','-b:a','56k',o],check=True);out[n]=[base64.b64encode(open(o,'rb').read()).decode()]
vo={}
for f in sorted(glob.glob('vo/*.mp3')):
    vo[os.path.basename(f)[:-4]]=base64.b64encode(open(f,'rb').read()).decode()
json.dump(out,open('sfx.json','w'));json.dump(vo,open('vo.json','w'))
print(os.path.getsize('sfx.json')//1024,'KB sfx',os.path.getsize('vo.json')//1024,'KB vo')
