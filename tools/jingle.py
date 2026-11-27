"""BDKNG-Jingle: eigene Melodie für Bad König (selbst komponiert, keine fremden Rechte).
Motiv „Bad Kö-nig“ = kurz-kurz-lang (A–A–D), darüber I–V–vi–IV in D-Dur.
Aufruf: python3 tools/jingle.py <stil: pop|advent> <sekunden> <ausgabe.mp3>"""
import sys, subprocess, os, tempfile
from midiutil import MIDIFile

D, A, Bm, G = [50, 54, 57], [45, 49, 52], [47, 50, 54], [43, 47, 50]  # Grundakkorde (tief)
FOLGE = [D, A, Bm, G]
# Melodie je Takt (Beat-Position, Tonhöhe, Länge) – 4 Takte, dann Variation
MELODIE = [
    [(0, 69, .5), (.5, 69, .5), (1, 74, 1.5), (2.5, 78, .5), (3, 76, 1)],          # Bad Kö-nig …
    [(0, 76, .5), (.5, 76, .5), (1, 73, 1.5), (2.5, 76, .5), (3, 73, 1)],
    [(0, 71, .5), (.5, 74, .5), (1, 78, 1.5), (2.5, 76, .5), (3, 74, 1)],
    [(0, 71, .5), (.5, 71, .5), (1, 74, 1), (2, 76, 1), (3, 74, 1)],
]
MELODIE_B = [
    [(0, 69, .5), (.5, 69, .5), (1, 74, 1.5), (2.5, 78, .5), (3, 81, 1)],
    [(0, 81, .5), (.5, 79, .5), (1, 76, 1.5), (2.5, 73, .5), (3, 76, 1)],
    [(0, 78, .5), (.5, 76, .5), (1, 74, 1), (2, 78, 1), (3, 81, 1)],
    [(0, 79, 1), (1, 78, 1), (2, 76, 1), (3, 74, 1)],
]

def baue(stil, sek, out):
    bpm = 112 if stil == 'pop' else 92
    takt = 4 * 60 / bpm
    takte = max(4, int(round((sek - 2) / takt)))
    m = MIDIFile(6, deinterleave=False)
    for t in range(6): m.addTempo(t, 0, bpm)
    # Instrumente (GM): Melodie, Glocken, Akkorde, Bass
    if stil == 'pop':
        prog = {0: 0, 1: 9, 2: 4, 3: 33}     # Klavier, Glockenspiel, E-Piano, Finger-Bass
    else:
        prog = {0: 8, 1: 14, 2: 48, 3: 32}   # Celesta, Röhrenglocken, Streicher, Kontrabass
    for ch, p in prog.items(): m.addProgramChange(ch, ch, 0, p)
    for k in range(takte + 1):
        b = k * 4
        ende = k == takte
        ak = D if ende else FOLGE[k % 4]
        dauer = 4
        # Akkorde
        if stil == 'pop' and not ende:
            for s in (0, 1, 2, 3):
                for n in ak: m.addNote(2, 2, n + 12, b + s + .02, .9, 62)
        else:
            for n in ak: m.addNote(2, 2, n + 12, b, dauer, 58 if stil == 'pop' else 70)
        # Bass
        m.addNote(3, 3, ak[0] - 12, b, 1.8 if not ende else 4, 90)
        if not ende: m.addNote(3, 3, ak[0] - 12 + (7 if stil == 'pop' else 0), b + 2, 1.8, 80)
        # Melodie (erst ab Takt 2 bei advent für sanften Einstieg)
        if ende:
            m.addNote(0, 0, 74, b, 4, 95); m.addNote(1, 1, 86, b, 4, 70)
        else:
            mel = (MELODIE if (k // 4) % 2 == 0 else MELODIE_B)[k % 4]
            for (p0, n, l) in mel:
                m.addNote(0, 0, n, b + p0, l, 96 if stil == 'pop' else 88)
                if stil == 'advent' or p0 in (0, 1): m.addNote(1, 1, n + 12, b + p0, min(l, 1), 52 if stil == 'pop' else 40)
        # Schlagzeug / Schellen (Kanal 9)
        if not ende:
            for s in range(4):
                if stil == 'pop':
                    m.addNote(4, 9, 36, b + s, .4, 92 if s in (0, 2) else 70)
                    if s in (1, 3): m.addNote(4, 9, 38, b + s, .4, 78)
                    m.addNote(4, 9, 42, b + s + .5, .2, 55)
                m.addNote(4, 9, 54, b + s + (0 if stil == 'pop' else .5), .2, 60 if stil == 'pop' else 48)  # Schellenkranz
        else:
            m.addNote(4, 9, 49, b, 2, 80)
    tmp = tempfile.mkdtemp()
    mid = os.path.join(tmp, 'j.mid'); wav = os.path.join(tmp, 'j.wav')
    with open(mid, 'wb') as f: m.writeFile(f)
    sf = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
    subprocess.run(['fluidsynth', '-ni', '-g', '0.9', '-r', '44100', '-F', wav, sf, mid], check=True, capture_output=True)
    lang = sek
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af',
                    'loudnorm=I=-16:TP=-1.5,afade=t=out:st=%.2f:d=1.2' % max(0, lang - 1.2), '-t', str(lang), '-b:a', '160k', out], check=True)

if __name__ == '__main__':
    baue(sys.argv[1], float(sys.argv[2]), sys.argv[3])
