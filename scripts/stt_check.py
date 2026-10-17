"""Check TTS turns against the script with ElevenLabs speech-to-text.
usage: stt_check.py [--lang fa] [--dir audio/turns] [--threshold 0.85] [t001 t007 …]
Reads T from turns.py in the current folder: T = [(section, speaker, text), ...]; files are <dir>/t001.mp3 …
Key: env ELEVENLABS_API_KEY, else Keychain service $ELEVENLABS_KEYCHAIN_SERVICE (default "elevenlabs-api-key").
Writes audio/stt_check.json and prints turns below the threshold. STT does NOT catch vowel errors —
names and ambiguous words still need a human listen. Very short lines score low without being wrong."""
import argparse, concurrent.futures as cf, difflib, json, os, re, subprocess, sys

sys.path.insert(0, os.getcwd())
from turns import T  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--lang', default='fa'); ap.add_argument('--dir', default='audio/turns')
ap.add_argument('--threshold', type=float, default=0.85); ap.add_argument('ids', nargs='*')
a = ap.parse_args()

K = os.environ.get('ELEVENLABS_API_KEY') or subprocess.check_output(
    ['security', 'find-generic-password', '-s', os.environ.get('ELEVENLABS_KEYCHAIN_SERVICE', 'elevenlabs-api-key'), '-w']).decode().strip()

def norm(s):
    s = re.sub(r'\[[^\]]*\]', '', s)                      # audio tags
    s = re.sub(r'[ً-ْٰ]', '', s)            # Arabic-script diacritics
    s = re.sub(r'[^\w\s]', '', s.replace('‌', ''))    # punctuation, ZWNJ
    return re.sub(r'\s+', ' ', s).strip()

def run(i):
    tid = f't{i:03d}'
    out = subprocess.check_output(['curl', '-s', '-H', f'xi-api-key: {K}', '-F', 'model_id=scribe_v1',
                                   '-F', f'language_code={a.lang}', '-F', f'file=@{a.dir}/{tid}.mp3',
                                   'https://api.elevenlabs.io/v1/speech-to-text'])
    got = json.loads(out).get('text', ''); want = T[i - 1][2].replace('|', ' ')
    return tid, difflib.SequenceMatcher(None, norm(want), norm(got)).ratio(), got

ids = [int(x[1:]) for x in a.ids] or range(1, len(T) + 1)
res = {}
with cf.ThreadPoolExecutor(6) as ex:
    for tid, r, g in ex.map(run, ids): res[tid] = (round(r, 3), g)
os.makedirs('audio', exist_ok=True)
json.dump(res, open('audio/stt_check.json', 'w'), ensure_ascii=False, indent=1)
for tid, (r, g) in sorted(res.items()):
    if r < a.threshold: print(tid, r, '|', g)
print('checked', len(res), 'min', min(r for r, _ in res.values()))
