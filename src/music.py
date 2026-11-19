# Spy/heist music for Inside Job, composed here and rendered with FluidSynth + FluidR3_GM (MIT licence).
# usage: python3 music.py OUTDIR   -> OUTDIR/<style>_<title|heist>.wav (seamless loops) + .mp3
# needs: pip install mido; apt install fluidsynth fluid-soundfont-gm; ffmpeg
import mido, subprocess, sys, os, random
SF = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'music'
os.makedirs(OUT, exist_ok=True)
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def P(s):
    if isinstance(s, int): return s
    n = NAMES[s[0]]; i = 1
    while i < len(s) and s[i] in '#b': n += 1 if s[i] == '#' else -1; i += 1
    return n + 12 * (int(s[i:]) + 1)

class Song:
    def __init__(s, bpm, bars, swing=0.0, seed=1):
        s.bpm, s.bars, s.swing, s.ev, s.progs, s.cc = bpm, bars, swing, [], {}, {}
        s.r = random.Random(seed)
    def prog(s, ch, p, rev=40, cho=0, vol=100, pan=64):
        s.progs[ch] = p; s.cc[ch] = (rev, cho, vol, pan)
    def sw(s, b):
        f = b % 1
        return b + (s.swing / 6 if abs(f - .5) < 1e-6 else 0)
    def n(s, ch, b, d, p, v=90, hum=True):
        if p is None: return
        if isinstance(p, (list, tuple)):
            for q in p: s.n(ch, b, d, q, v, hum)
            return
        jitter = s.r.uniform(-.008, .008) if hum else 0
        vv = max(1, min(127, int(v + (s.r.randint(-6, 6) if hum else 0))))
        s.ev.append((s.sw(b) + jitter, d, P(p), vv, ch))
    def seq(s, ch, notes, v=90, off=0):
        for b, d, p in notes: s.n(ch, b + off, d, p, v)
    def render(s, name, reps=3):
        tpb = 480; L = s.bars * 4
        msgs = []
        for ch, p in s.progs.items():
            rev, cho, vol, pan = s.cc[ch]
            msgs += [(0, mido.Message('program_change', channel=ch, program=p))]
            for c, val in ((91, rev), (93, cho), (7, vol), (10, pan)):
                msgs.append((0, mido.Message('control_change', channel=ch, control=c, value=val)))
        for r in range(reps):
            for b, d, p, v, ch in s.ev:
                st = max(0, (b + r * L)); en = st + max(.05, d * .95)
                msgs.append((int(st * tpb), mido.Message('note_on', channel=ch, note=p, velocity=v)))
                msgs.append((int(en * tpb), mido.Message('note_off', channel=ch, note=p, velocity=0)))
        msgs.sort(key=lambda x: (x[0], 0 if x[1].type in ('program_change', 'control_change') else (1 if x[1].type == 'note_off' else 2)))
        mf = mido.MidiFile(ticks_per_beat=tpb); tr = mido.MidiTrack(); mf.tracks.append(tr)
        tr.append(mido.MetaMessage('set_tempo', tempo=int(6e7 / s.bpm)))
        last = 0
        for t, m in msgs: tr.append(m.copy(time=t - last)); last = t
        tr.append(mido.MetaMessage('end_of_track', time=tpb * 8))
        mid = f'{OUT}/{name}.mid'; raw = f'{OUT}/{name}_raw.wav'; mf.save(mid)
        subprocess.run(['fluidsynth', '-ni', '-g', '0.55', '-r', '44100', '-F', raw, SF, mid], check=True, capture_output=True)
        sec = L * 60 / s.bpm
        # the middle repetition carries the previous one's reverb tail, so it loops without a seam
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{sec:.4f}', '-t', f'{sec:.4f}', '-i', raw,
                        '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '44100', f'{OUT}/{name}.wav'], check=True)
        os.remove(raw)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/{name}.wav', '-b:a', '128k', f'{OUT}/{name}.mp3'], check=True)
        print(name, f'{sec:.1f}s')

# drum notes
KICK, SNARE, SIDE, CHH, PHH, OHH, RIDE, BELL, CRASH, TOMH, TOMM, TOML, TAMB, SHAKER, WOOD, BRUSHSN = 36, 38, 37, 42, 44, 46, 51, 53, 49, 50, 47, 45, 54, 70, 76, 40
DR = 9

def walk(song, ch, chords, v=88, low=28, high=52):
    """walking bass: chords = list of (root, [chord tones]) per bar (4 beats)"""
    prev = None
    for bar, (root, tones) in enumerate(chords):
        nxt = chords[(bar + 1) % len(chords)][0]
        r = P(root)
        while r > 45: r -= 12
        while r < low: r += 12
        cand = [P(t) for t in tones]
        line = [r]
        for k in range(2):
            c = song.r.choice(cand)
            while c - line[-1] > 7: c -= 12
            while line[-1] - c > 7: c += 12
            c = min(high, max(low, c)); line.append(c)
        nr = P(nxt)
        while nr > 45: nr -= 12
        while nr < low: nr += 12
        line.append(nr + (1 if song.r.random() < .5 else -1))
        for k, p in enumerate(line): song.n(ch, bar * 4 + k, .9, p, v + (8 if k == 0 else 0))

def chord_stab(song, ch, b, notes, d=.4, v=85): song.n(ch, b, d, notes, v)

# ------------------------------------------------------------------ 1. VELVET CAPER: 60s cool-jazz spy
def velvet_title():
    s = Song(118, 16, swing=1.0, seed=3)
    s.prog(0, 32, rev=35, vol=118)        # acoustic bass
    s.prog(1, 11, rev=70, vol=105, pan=44) # vibraphone
    s.prog(2, 59, rev=60, vol=100, pan=84) # muted trumpet
    s.prog(3, 26, rev=50, vol=78, pan=90)  # jazz guitar comping
    s.prog(4, 67, rev=40, vol=92, pan=40)  # bari sax stabs
    s.prog(DR, 40, rev=45, vol=100)       # brush kit
    ch = [('E2', ['G2', 'B2', 'D#3']), ('E2', ['G2', 'B2', 'C#3']), ('E2', ['G2', 'B2', 'D3']), ('E2', ['G2', 'B2', 'D#3']),
          ('A1', ['C2', 'E2', 'G2']), ('A1', ['C2', 'E2', 'F#2']), ('E2', ['G2', 'B2', 'D3']), ('E2', ['G2', 'B2', 'D#3']),
          ('C2', ['E2', 'G2', 'Bb2']), ('B1', ['D#2', 'F#2', 'A2']), ('E2', ['G2', 'B2', 'D3']), ('E2', ['G2', 'B2', 'C#3']),
          ('A1', ['C2', 'E2', 'G2']), ('F#1', ['A1', 'C2', 'E2']), ('E2', ['G2', 'B2', 'D#3']), ('B1', ['D#2', 'F#2', 'A2'])]
    walk(s, 0, ch)
    voic = {'E2': ['G3', 'B3', 'D#4', 'F#4'], 'A1': ['C4', 'E4', 'G4', 'B3'], 'C2': ['E3', 'Bb3', 'D4', 'G4'], 'B1': ['A3', 'D#4', 'G4', 'C5'], 'F#1': ['A3', 'C4', 'E4', 'G#4']}
    for bar, (root, _) in enumerate(ch):
        b = bar * 4
        s.n(3, b + 1.5, .35, voic[root], 62); s.n(3, b + 3, .3, voic[root], 55)
        for k in range(4): s.n(DR, b + k, .5, RIDE, 70 if k % 2 == 0 else 62)
        s.n(DR, b + 1.5, .3, RIDE, 55); s.n(DR, b + 3.5, .3, RIDE, 55)
        s.n(DR, b + 1, .2, PHH, 60); s.n(DR, b + 3, .2, PHH, 60)
        s.n(DR, b + 1, .2, BRUSHSN, 38); s.n(DR, b + 3, .2, BRUSHSN, 42)
        if bar % 4 == 0: s.n(DR, b, .3, KICK, 55)
        if bar % 4 == 3: s.n(4, b + 3.5, .6, [P(root) + 12, P(root) + 19], 80)
    mel = [(0, 1.5, 'E5'), (1.5, .5, 'D#5'), (2, 2, 'B4'), (4, .5, 'G4'), (4.5, .5, 'A4'), (5, .5, 'B4'), (5.5, 1.5, 'C5'), (7, 1, 'B4'),
           (8, 3, 'E5'), (11, .5, 'F#5'), (11.5, .5, 'G5'), (12, 1, 'F#5'), (13, 1, 'D#5'), (14, 2, 'E5'),
           (16, 1.5, 'A5'), (17.5, .5, 'G5'), (18, 1, 'E5'), (19, 1, 'C5'), (20, 2, 'B4'), (22, .5, 'A4'), (22.5, .5, 'B4'), (23, 1, 'C5'),
           (24, 1.5, 'B4'), (25.5, .5, 'G4'), (26, 3, 'E4'),
           (44, .5, 'B4'), (44.5, .5, 'C5'), (45, .5, 'B4'), (45.5, .5, 'A#4'), (46, 2, 'B4'),
           (48, 1.5, 'C5'), (49.5, .5, 'B4'), (50, 1, 'A4'), (51, 1, 'E5'), (52, 1, 'D#5'), (53, 1, 'C5'), (54, 1, 'B4'), (55, 1, 'A4'),
           (56, 3, ['B4', 'E5']), (59, .5, 'G4'), (59.5, .5, 'A4'), (60, 1, 'B4'), (61, 1, 'A#4'), (62, 2, 'B4')]
    s.seq(1, mel, 88)
    s.seq(2, [(32, .5, 'E4'), (32.5, .5, 'G4'), (33, 1, 'Bb4'), (34, 1.5, 'A4'), (36, .5, 'D#4'), (36.5, .5, 'F#4'), (37, 1, 'A4'), (38, 1.5, 'G4'), (40, 2.5, 'E4'), (42.5, .5, 'F#4'), (43, 1, 'G4')], 92)
    s.render('velvet_title')

def velvet_heist():
    s = Song(146, 8, swing=.6, seed=4)
    s.prog(0, 33, rev=25, vol=118); s.prog(1, 11, rev=60, vol=90, pan=40); s.prog(2, 59, rev=55, vol=98, pan=86)
    s.prog(4, 61, rev=40, vol=96); s.prog(5, 0, rev=30, vol=85, pan=50); s.prog(DR, 0, rev=30, vol=105)
    riff = ['E2', 'E2', 'G2', 'E2', 'Bb2', 'E2', 'A2', 'G2']
    roots = [0, 0, 0, 0, 5, 5, 8, 7]
    for bar in range(8):
        b = bar * 4; t = roots[bar]
        for k, p in enumerate(riff): s.n(0, b + k * .5, .4, P(p) + t, 100 if k == 0 else 84)
        for k, p in enumerate(riff[:4]): s.n(5, b + k * .5 + 2, .3, P(p) + t + 12, 55)
        for k in range(8): s.n(DR, b + k * .5, .2, CHH, 70 if k % 2 == 0 else 50)
        s.n(DR, b, .3, KICK, 95); s.n(DR, b + 2.5, .3, KICK, 80); s.n(DR, b + 1, .3, SNARE, 78); s.n(DR, b + 3, .3, SNARE, 85)
        if bar % 2 == 1: s.n(4, b + 3.5, .5, [P('E4') + t, P('G4') + t, P('B4') + t, P('D#5') + t], 92)
    s.n(DR, 0, 1, CRASH, 80)
    s.seq(2, [(8, .5, 'B4'), (8.5, .5, 'C5'), (9, 1, 'B4'), (10, .5, 'G4'), (10.5, 1, 'E4'), (24, .5, 'C5'), (24.5, .5, 'D#5'), (25, 1.5, 'E5'), (28, .5, 'B4'), (28.5, 1, 'A#4'), (29.5, 1.5, 'B4')], 90)
    for b in [2, 6, 18, 22]: s.n(1, b, 1, ['E5', 'B5'], 70)
    s.n(DR, 30, .3, TOMH, 80); s.n(DR, 30.5, .3, TOMM, 80); s.n(DR, 31, .3, TOML, 85); s.n(DR, 31.5, .3, TOML, 88)
    s.render('velvet_heist')

# ------------------------------------------------------------------ 2. TWANG: surf-guitar spy
def surf_riff(s, b, t, v=100, ch=0):
    r1 = ['E3', 'E3', 'G3', 'E3', 'A3', 'E3', 'Bb3', 'A3', 'G3', 'E3', 'G3', 'A3', 'G3', 'E3', 'D3', 'E3']
    for k, p in enumerate(r1): s.n(ch, b + k * .5, .42, P(p) + t, v if k % 4 == 0 else v - 14)

def twang_title():
    s = Song(150, 16, seed=5)
    s.prog(0, 27, rev=95, cho=30, vol=112, pan=58)  # clean electric guitar, drenched in reverb
    s.prog(1, 34, rev=20, vol=112)                  # picked bass
    s.prog(2, 61, rev=60, vol=96, pan=72)           # brass
    s.prog(3, 16, rev=50, vol=70, pan=40)           # organ
    s.prog(4, 56, rev=70, vol=96, pan=78)           # trumpet
    s.prog(DR, 0, rev=40, vol=108)
    form = [0, 0, 0, 0, 5, 5, 0, 0, 7, 8, 7, 7, 0, 0, 5, 7]
    for bar2 in range(8):
        b = bar2 * 8
        t1, t2 = form[bar2 * 2], form[bar2 * 2 + 1]
        surf_riff(s, b, t1 if t1 == t2 else t1)
        if t1 != t2:  # riff spans 2 bars; re-pitch the second half
            s.ev = [e if not (e[4] == 0 and b + 4 <= e[0] < b + 8) else (e[0], e[1], e[2] - t1 + t2, e[3], e[4]) for e in s.ev]
    for bar in range(16):
        b = bar * 4; t = form[bar]
        for k in range(8): s.n(1, b + k * .5, .4, P('E2') + t + (7 if k in (3, 7) else 0), 92 if k % 2 == 0 else 78)
        for k in range(8): s.n(DR, b + k * .5, .2, RIDE if bar >= 8 else CHH, 68 if k % 2 == 0 else 52)
        s.n(DR, b, .3, KICK, 100); s.n(DR, b + 1.5, .3, KICK, 80); s.n(DR, b + 2, .3, KICK, 95)
        s.n(DR, b + 1, .3, SNARE, 90); s.n(DR, b + 3, .3, SNARE, 96)
        for k in range(16): s.n(DR, b + k * .25, .1, TAMB, 34 if k % 2 else 44)
        s.n(3, b, 3.8, [P('E4') + t, P('B4') + t, P('G4') + t], 50 if bar < 8 else 62)
    for b in (28, 60):
        for k, d in enumerate([TOMH, TOMH, TOMM, TOMM, TOML, TOML, TOML, SNARE]): s.n(DR, b + k * .5, .3, d, 85 + k * 3)
    s.n(DR, 0, 1, CRASH, 90); s.n(DR, 32, 1, CRASH, 95)
    for b, t in [(32, 7), (36, 8), (40, 7), (44, 7)]: s.n(2, b, 1.6, [P('E4') + t, P('B4') + t, P('E5') + t], 96); s.n(2, b + 2.5, .4, [P('E4') + t, P('B4') + t], 90)
    s.seq(4, [(48, 3, 'B4'), (51, .5, 'A4'), (51.5, .5, 'G4'), (52, 3, 'E5'), (55, 1, 'D5'), (56, 2, 'C5'), (58, 1, 'B4'), (59, 1, 'A4'), (60, 3.5, 'B4')], 96)
    s.render('twang_title')

def twang_heist():
    s = Song(166, 8, seed=6)
    s.prog(0, 27, rev=90, cho=30, vol=108, pan=58); s.prog(1, 34, rev=20, vol=112); s.prog(2, 61, rev=55, vol=92, pan=72)
    s.prog(DR, 0, rev=35, vol=108)
    form = [0, 0, 0, 0, 5, 5, 7, 8]
    for bar2 in range(4):
        b = bar2 * 8; t = form[bar2 * 2]; surf_riff(s, b, t, 96)
    s.ev = [(e[0], e[1], e[2] + (8 - 7) if (e[4] == 0 and 28 <= e[0] < 32) else e[2], e[3], e[4]) for e in s.ev]
    for bar in range(8):
        b = bar * 4; t = form[bar]
        for k in range(8): s.n(1, b + k * .5, .4, P('E2') + t, 96 if k % 2 == 0 else 80)
        for k in range(16): s.n(DR, b + k * .25, .1, CHH, 60 if k % 4 == 0 else 38)
        for k in (0, 1.5, 2, 3.5): s.n(DR, b + k, .2, KICK, 92)
        s.n(DR, b + 1, .3, SNARE, 90); s.n(DR, b + 3, .3, SNARE, 96)
        if bar % 2 == 1: s.n(2, b + 3, .5, [P('E4') + t, P('B4') + t, P('E5') + t], 95); s.n(2, b + 3.5, .4, [P('F4') + t, P('C5') + t, P('F5') + t], 90)
    for k, d in enumerate([SNARE, SNARE, TOMH, TOMM, TOML, TOML, KICK, SNARE]): s.n(DR, 28 + k * .5, .3, d, 85 + k * 3)
    s.n(DR, 0, 1, CRASH, 90)
    s.render('twang_heist')

# ------------------------------------------------------------------ 3. BLACKOUT: modern electronic stealth
def blackout(heist):
    s = Song(116 if heist else 100, 8 if heist else 16, seed=7 + heist)
    s.prog(0, 38, rev=15, vol=110)              # synth bass
    s.prog(1, 45, rev=55, vol=92, pan=40)        # pizzicato strings
    s.prog(2, 49, rev=80, vol=82)                # slow strings
    s.prog(3, 9, rev=80, vol=80, pan=90)         # glockenspiel
    s.prog(4, 89, rev=90, vol=72)                # warm pad
    s.prog(5, 44 if heist else 47, rev=70, vol=90) # tremolo strings / timpani
    s.prog(DR, 25 if heist else 0, rev=40, vol=100)
    prog = ['D', 'D', 'Bb', 'Bb', 'G', 'G', 'A', 'A'] if heist else ['D', 'D', 'D', 'D', 'Bb', 'Bb', 'Bb', 'Bb', 'G', 'G', 'G', 'G', 'A', 'A', 'Bb', 'A']
    if not heist: prog = ['D', 'D', 'Bb', 'Bb', 'G', 'G', 'A', 'A', 'D', 'D', 'Bb', 'Bb', 'G', 'C', 'A', 'A']
    triads = {'D': ['D', 'F', 'A'], 'Bb': ['Bb', 'D', 'F'], 'G': ['G', 'Bb', 'D'], 'A': ['A', 'C#', 'E'], 'C': ['C', 'E', 'G']}
    for bar, c in enumerate(prog):
        b = bar * 4; root = P(c + '1') if c not in ('Bb', 'A', 'G', 'C') else P(c + ('0' if c in ('Bb', 'A') else '1'))
        if root < P('A0'): root += 12
        pat = [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1] if heist else [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0]
        for k in range(16):
            if pat[k]: s.n(0, b + k * .25, .2, root + (12 if k in (6, 14) else 0), 100 if k % 4 == 0 else 78, hum=False)
        tri = [P(n + '4') for n in triads[c]]
        arp = [tri[0], tri[1], tri[2], tri[1]] * 2
        for k, p in enumerate(arp): s.n(1, b + k * .5, .3, p, 70 if k % 2 == 0 else 58)
        if bar % 2 == 0: s.n(2, b, 7.8, [P(n + '3') for n in triads[c]] + [P(triads[c][0] + '4')], 62); s.n(4, b, 7.8, [P(n + '3') for n in triads[c]], 55)
        for k in range(16): s.n(DR, b + k * .25, .1, CHH, 46 if k % 4 == 2 else 30, hum=False)
        s.n(DR, b, .3, KICK, 96); s.n(DR, b + 2.75 if heist else b + 2.5, .3, KICK, 80)
        s.n(DR, b + 3, .2, SIDE if not heist else SNARE, 70)
        if heist: s.n(DR, b + 1, .2, SNARE, 60); s.n(5, b, 4, [P(triads[c][0] + '5')], 52 + bar * 5)
    if not heist:
        for b in (0, 16, 32, 48): s.n(5, b, 2, 'D2', 100); s.n(5, b + .5, 1, 'D2', 70)
        s.seq(3, [(32, 1, 'A5'), (33, 1, 'D6'), (34, 2, 'C#6'), (36, 1, 'A5'), (37, .5, 'Bb5'), (37.5, 2.5, 'A5'),
                  (40, 1, 'G5'), (41, 1, 'Bb5'), (42, 2, 'A5'), (44, 1, 'F5'), (45, 1, 'E5'), (46, 2, 'D5'),
                  (48, 1, 'A5'), (49, 1, 'D6'), (50, 2, 'E6'), (52, 2, 'F6'), (54, 2, 'E6'), (56, 4, 'C#6'), (60, 4, 'A5')], 80)
    else:
        s.seq(3, [(8, .5, 'A5'), (8.5, .5, 'D6'), (9, 1, 'C#6'), (24, .5, 'A5'), (24.5, .5, 'F6'), (25, 1, 'E6')], 78)
        for k, d in enumerate([TOML, TOML, TOMM, TOMM, TOMH, TOMH, SNARE, SNARE]): s.n(DR, 30 + k * .25, .2, d, 80 + k * 4)
    s.render('blackout_heist' if heist else 'blackout_title')

# ------------------------------------------------------------------ 4. MIDNIGHT NOIR: slow smoky lounge
def noir_title():
    s = Song(84, 16, swing=1.0, seed=9)
    s.prog(0, 32, rev=40, vol=115); s.prog(1, 0, rev=65, vol=88, pan=50); s.prog(2, 66, rev=70, vol=104, pan=76)
    s.prog(3, 48, rev=85, vol=60); s.prog(DR, 40, rev=50, vol=96)
    chords = [('C2', ['Eb3', 'G3', 'Bb3', 'D4']), ('C2', ['Eb3', 'G3', 'Bb3', 'D4']), ('F1', ['Ab3', 'C4', 'Eb4', 'G4']), ('F1', ['Ab3', 'C4', 'Eb4', 'G4']),
              ('Ab1', ['Gb3', 'C4', 'Eb4', 'F4']), ('G1', ['F3', 'B3', 'Eb4', 'Ab4']), ('C2', ['Eb3', 'G3', 'Bb3', 'D4']), ('G1', ['F3', 'B3', 'D4', 'Ab4'])] * 2
    for bar, (root, v) in enumerate(chords):
        b = bar * 4; r = P(root)
        s.n(0, b, 1.8, r, 92); s.n(0, b + 2, 1.8, r + 7 if bar % 2 == 0 else r + (12 if r < P('E2') else -5), 84)
        s.n(1, b, 1.2, v, 58); s.n(1, b + 2.5, .8, v[1:], 50)
        s.n(DR, b + 1, .3, BRUSHSN, 40); s.n(DR, b + 3, .3, BRUSHSN, 46)
        for k in range(4): s.n(DR, b + k, .4, RIDE, 50)
        s.n(DR, b + 1.5, .2, RIDE, 40); s.n(DR, b + 3.5, .2, RIDE, 40); s.n(DR, b + 1, .2, PHH, 50); s.n(DR, b + 3, .2, PHH, 50)
        if bar >= 8 and bar % 2 == 0: s.n(3, b, 7.8, v, 50)
    sax = [(0, 1, 'G4'), (1, .5, 'Bb4'), (1.5, 2.5, 'C5'), (4, .5, 'D5'), (4.5, .5, 'Eb5'), (5, 1, 'D5'), (6, 2, 'C5'),
           (8, 1, 'Ab4'), (9, .5, 'C5'), (9.5, 2.5, 'Eb5'), (12, 1, 'D5'), (13, 1, 'C5'), (14, 2, 'G4'),
           (16, 1, 'Ab4'), (17, .5, 'G4'), (17.5, .5, 'F4'), (18, 2, 'Eb4'), (20, 1, 'D4'), (21, .5, 'F4'), (21.5, 2.5, 'B4'),
           (24, 3, 'C5'), (28, .5, 'D5'), (28.5, .5, 'C5'), (29, .5, 'B4'), (29.5, .5, 'Ab4'), (30, 2, 'G4'),
           (40, 1, 'Eb5'), (41, .5, 'D5'), (41.5, 2.5, 'C5'), (44, 1, 'Ab4'), (45, 1, 'G4'), (46, 2, 'F4'),
           (48, 1, 'Gb4'), (49, 1, 'Eb4'), (50, 2, 'C4'), (52, 1, 'B3'), (53, 1, 'D4'), (54, 2, 'F4'),
           (56, 4, 'G4'), (60, .5, 'F4'), (60.5, .5, 'Ab4'), (61, 1, 'B4'), (62, 2, 'D5')]
    s.seq(2, sax, 86)
    s.render('noir_title')

def noir_heist():
    s = Song(108, 8, swing=.8, seed=10)
    s.prog(0, 32, rev=30, vol=118); s.prog(1, 45, rev=50, vol=90, pan=40); s.prog(2, 59, rev=60, vol=96, pan=82)
    s.prog(3, 0, rev=50, vol=80, pan=56); s.prog(DR, 40, rev=40, vol=100)
    ch = [('C2', ['Eb2', 'G2', 'Bb2']), ('C2', ['Eb2', 'G2', 'B2']), ('F1', ['Ab1', 'C2', 'Eb2']), ('F1', ['Ab1', 'C2', 'D2']),
          ('Ab1', ['C2', 'Eb2', 'Gb2']), ('G1', ['B1', 'D2', 'F2']), ('C2', ['Eb2', 'G2', 'Bb2']), ('G1', ['B1', 'D2', 'Ab2'])]
    walk(s, 0, ch, low=29)
    for bar, (root, tones) in enumerate(ch):
        b = bar * 4
        for k in range(8): s.n(1, b + k * .5, .3, P(tones[k % 3]) + 24, 66 if k % 2 == 0 else 52)
        for k in range(4): s.n(DR, b + k, .4, RIDE, 64)
        s.n(DR, b + 1.5, .2, RIDE, 50); s.n(DR, b + 3.5, .2, RIDE, 50); s.n(DR, b + 1, .2, BRUSHSN, 60); s.n(DR, b + 3, .2, BRUSHSN, 66)
        s.n(DR, b + 1, .2, PHH, 55); s.n(DR, b + 3, .2, PHH, 55)
        s.n(3, b + 3.5, .3, [P(t) + 24 for t in tones], 55)
    s.seq(2, [(4, .5, 'G4'), (4.5, .5, 'Bb4'), (5, 1, 'B4'), (6, 1.5, 'C5'), (20, .5, 'Eb5'), (20.5, .5, 'D5'), (21, .5, 'C5'), (21.5, .5, 'B4'), (22, 1.5, 'G4')], 88)
    s.render('noir_heist')

for f in (velvet_title, velvet_heist, twang_title, twang_heist, lambda: blackout(False), lambda: blackout(True), noir_title, noir_heist): f()
