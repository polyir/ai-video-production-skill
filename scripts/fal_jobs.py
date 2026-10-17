"""Budget-capped fal.ai job runner for images and image-to-video.
usage: fal_jobs.py [--cap reel|video|<usd>] estimate | submit [ids…] | poll | download
Run from a project's fal/ folder (or set FAL_WORKDIR). State: jobs.json, outputs: out/.

Key: env FAL_KEY, else macOS Keychain service $FAL_KEYCHAIN_SERVICE (default "fal-api-key"). Never printed.
Caps: env FAL_CAP_REEL (default 3.45), FAL_CAP_VIDEO (default 5.75), FAL_IMAGE_MAX (1.0), FAL_IMAGE_TARGET (0.30).

Job fields (jobs.json is a list):
  id, endpoint, input            input is sent as-is (prompt, aspect_ratio, resolution, duration, …)
  refs {param: ref | [refs]}     ref = id of an earlier job (its output URL) or a local file path (uploaded)
  kind image|video               default: video if the endpoint name has "video", else image
  usd                            explicit cost when the unit price is ambiguous (units, tokens)

submit refuses to send anything if the estimated total exceeds the cap or any image costs >= FAL_IMAGE_MAX.
Video models' own audio is forced off (audio comes from a dedicated audio tool).
Prices in VIDEO_RES_PRICE were read from fal model pages in Sept-Oct 2026 — re-check before relying on them."""
import json, mimetypes, os, subprocess, sys, time, urllib.parse, urllib.request

def _key():
    if os.environ.get('FAL_KEY'): return os.environ['FAL_KEY']
    svc = os.environ.get('FAL_KEYCHAIN_SERVICE', 'fal-api-key')
    return subprocess.check_output(['security', 'find-generic-password', '-a', os.environ['USER'], '-s', svc, '-w']).decode().strip()

KEY = _key()
HERE = os.environ.get('FAL_WORKDIR') or os.getcwd()
STATE = os.path.join(HERE, 'jobs.json')
CAPS = {'reel': float(os.environ.get('FAL_CAP_REEL', 3.45)), 'video': float(os.environ.get('FAL_CAP_VIDEO', 5.75))}
IMAGE_MAX, IMAGE_TARGET = float(os.environ.get('FAL_IMAGE_MAX', 1.0)), float(os.environ.get('FAL_IMAGE_TARGET', 0.30))
DEFAULT_SECONDS = {'veo3.1': 8, 'gemini-omni-flash': 8, 'wan-3.0': 5, 'kling-video': 5}

def urlopen(req, timeout):
    """urlopen with retries: the home network drops ~half the TLS handshakes to fal (2026-10-14)."""
    for k in range(12):
        try: return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError: raise
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            if k == 11: raise
            time.sleep(min(15, 2 + 2 * k))

def api(url, body=None, method=None, auth=True, ctype='application/json'):
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    headers = {'Content-Type': ctype, 'User-Agent': 'fal-jobs'}
    if auth: headers['Authorization'] = f'Key {KEY}'
    req = urllib.request.Request(url, data=data, method=method or ('POST' if data is not None else 'GET'), headers=headers)
    try: return json.load(urlopen(req, timeout=40))
    except urllib.error.HTTPError as e: return {'error': e.code, 'body': e.read().decode()[:500]}

def app_id(endpoint): return '/'.join(endpoint.split('/')[:2])
def kind(j): return j.get('kind') or ('video' if 'video' in j['endpoint'] else 'image')

def upload(path):
    ctype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    init = api('https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3',
               {'content_type': ctype, 'file_name': os.path.basename(path)})
    if 'upload_url' not in init: raise SystemExit(f'upload init failed {init}')
    urlopen(urllib.request.Request(init['upload_url'], data=open(path, 'rb').read(), method='PUT',
                                                  headers={'Content-Type': ctype}), timeout=300)
    return init['file_url']

def output_url(result):
    for key in ('video', 'image'):
        if isinstance(result.get(key), dict) and result[key].get('url'): return result[key]['url']
    for key in ('images', 'videos'):
        if result.get(key): return result[key][0]['url']
    return None

def prices(endpoints):
    q = urllib.parse.urlencode([('endpoint_id', e) for e in sorted(set(endpoints))])
    r = api(f'https://api.fal.ai/v1/models/pricing?{q}')
    if 'prices' not in r: raise SystemExit(f'pricing failed {r}')
    return {p['endpoint_id']: p for p in r['prices']}

def seconds(j):
    d = j['input'].get('duration')
    if d is not None: return float(str(d).rstrip('s'))
    return next((v for k, v in DEFAULT_SECONDS.items() if k in j['endpoint']), 8)

# The pricing API returns only the base tier; these come from the model pages (2026-09-27).
# (endpoint prefix, $/second by resolution, schema default resolution) — first match wins.
VIDEO_RES_PRICE = [
    ('alibaba/wan-3.0-prime/', {'480p': 0.068, '720p': 0.14, '1080p': 0.28}, '1080p'),
    ('alibaba/wan-3.0/', {'480p': 0.05, '720p': 0.10, '1080p': 0.20}, '1080p'),
    ('google/gemini-omni-flash/', {'360p': 0.03, '720p': 0.10, '1080p': 0.15, '4k': 0.30}, None),
    ('fal-ai/veo3.1/image-to-video', {'720p': 0.20, '1080p': 0.20, '4k': 0.40}, '720p'),  # audio off
    ('fal-ai/kling-video/v2.6/pro/', {'1080p': 0.07}, '1080p'),  # audio off ($0.14 with); no resolution input
]
IMAGE_RES_FACTOR = {'fal-ai/nano-banana-2': {'0.5K': 0.75, '2K': 1.5, '4K': 2}, 'fal-ai/nano-banana-pro': {'4K': 2}}

def cost(j, price):
    """Estimate in USD from the model's unit price, resolution and duration."""
    if 'usd' in j: return j['usd']
    for prefix, table, default in VIDEO_RES_PRICE:
        if j['endpoint'].startswith(prefix):
            res = j['input'].get('resolution', default)
            if res not in table: raise SystemExit(f"{j['id']}: set resolution to one of {list(table)}")
            return table[res] * seconds(j)
    p = price.get(j['endpoint'])
    if not p: raise SystemExit(f"{j['id']}: no price for {j['endpoint']}")
    unit = p['unit']
    if unit in ('image', 'images'):
        family = next((f for f in IMAGE_RES_FACTOR if j['endpoint'].startswith(f)), None)
        factor = IMAGE_RES_FACTOR.get(family, {}).get(j['input'].get('resolution'), 1)
        return p['unit_price'] * factor * j['input'].get('num_images', 1)
    elif unit in ('second', 'seconds'): n = seconds(j)
    elif unit == '1000 tokens' and 'seedance' in j['endpoint']:
        # fal: tokens = h * w * seconds * 24 / 1024; 1080p is billed ~$0.0234 instead of the 480p/720p base
        res = j['input'].get('resolution', '720p')
        if str(j['input'].get('duration', 'auto')) == 'auto': raise SystemExit(f"{j['id']}: set an explicit duration for Seedance")
        short = int(res.rstrip('p')); long = round(short * 16 / 9)
        n = short * long * seconds(j) * 24 / 1024 / 1000
        return n * (0.0234 if res == '1080p' else p['unit_price'])
    else: raise SystemExit(f"{j['id']}: ambiguous unit «{unit}» for {j['endpoint']}; set \"usd\" after checking the model page")
    return p['unit_price'] * n

J = json.load(open(STATE)); byid = {j['id']: j for j in J}
def save(): json.dump(J, open(STATE, 'w'), ensure_ascii=False, indent=1)

args = sys.argv[1:]
cap = None
if args[:1] == ['--cap']:
    cap = CAPS.get(args[1]) or float(args[1]); args = args[2:]
cmd = args[0]

def check_budget():
    price = prices(j['endpoint'] for j in J)
    total = 0.0
    for j in J:
        c = cost(j, price); total += c
        flag = ''
        if kind(j) == 'image':
            if c >= IMAGE_MAX: raise SystemExit(f"{j['id']}: ${c:.3f} per image breaks the ${IMAGE_MAX:.2f} limit")
            if c > IMAGE_TARGET: flag = '  (above target)'
        print(f"{j['id']:8} {kind(j):5} {j['endpoint']:48} ${c:6.3f}{flag}")
    print(f'total ≈ ${total:.2f}' + (f' / cap ${cap:.2f}' if cap else ''))
    if cap and total > cap: raise SystemExit('over budget cap — nothing submitted')
    return total

if cmd == 'estimate':
    check_budget()
elif cmd == 'submit':
    if cap is None: raise SystemExit('submit needs --cap reel|video|<usd>')
    check_budget()
    only = set(args[1:])
    for j in J:
        if j.get('request_id') or (only and j['id'] not in only): continue
        body = dict(j['input'])
        if 'veo' in j['endpoint']: body['generate_audio'] = False
        if 'wan' in j['endpoint']: body['audio'] = False
        if 'seedance' in j['endpoint']: body['generate_audio'] = False
        if 'kling' in j['endpoint']: body['generate_audio'] = False  # default is on and doubles the price
        waiting = None
        for param, ref in (j.get('refs') or {}).items():
            urls = []
            for r in (ref if isinstance(ref, list) else [ref]):
                if r in byid:
                    if not byid[r].get('url'): waiting = r; break
                    urls.append(byid[r]['url'])
                else:
                    j.setdefault('uploads', {})
                    if r not in j['uploads']: j['uploads'][r] = upload(os.path.join(HERE, r)); save()
                    urls.append(j['uploads'][r])
            body[param] = urls if isinstance(ref, list) else (urls[0] if urls else None)
        if waiting: print(j['id'], 'waiting for', waiting); continue
        r = api(f"https://queue.fal.run/{j['endpoint']}", body)
        j['request_id'] = r.get('request_id'); print(j['id'], j['request_id'] or r); save()
elif cmd == 'poll':
    for j in J:
        if not j.get('request_id') or j.get('url'): continue
        base = f"https://queue.fal.run/{app_id(j['endpoint'])}/requests/{j['request_id']}"
        s = api(base + '/status'); j['status'] = s.get('status')
        if j['status'] == 'COMPLETED':
            res = api(base); j['url'] = output_url(res)
            if not j['url']: j['error'] = json.dumps(res)[:400]
        print(j['id'], j['status'], j.get('error', ''))
    save()
elif cmd == 'download':
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    for j in J:
        if j.get('url') and not j.get('file'):
            ext = os.path.splitext(urllib.parse.urlparse(j['url']).path)[1] or ('.mp4' if kind(j) == 'video' else '.png')
            f = os.path.join(HERE, 'out', j['id'] + ext)
            for attempt in range(3):
                try: urllib.request.urlretrieve(j['url'], f); break
                except Exception as e: print('retry', j['id'], e); time.sleep(3)
            j['file'] = f; print('saved', j['id']); save()
