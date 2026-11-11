#!/usr/bin/env python3
"""Backfill Story-ad media whose links sit inside composite_preview.ad_snaps.

Leaves the source run untouched; writes a sibling directory with content-addressed
media, a per-ad JSONL ledger, and a manifest. Usage: backfill_story_media.py RUN_DIR
"""
import hashlib, json, mimetypes, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = 'betting-ads-research/0.1 (non-commercial academic research)'
MAX_FILE = 512 * 1024**2
run = Path(sys.argv[1]).resolve()
out = run.parent / f'story_backfill_{run.name}'
media_dir = out / 'media'
media_dir.mkdir(parents=True, exist_ok=False)

existing = {}  # sha -> relative path already in the source run
for r in map(json.loads, (run / 'records.jsonl').open()):
    m = r.get('media')
    if m: existing[m['sha256']] = m['local_path']

def fetch(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read(MAX_FILE + 1)
                if len(data) > MAX_FILE: raise RuntimeError('file exceeds 512 MiB')
                return data, resp.status, resp.headers.get('content-type', '')
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500: raise
            time.sleep(min(120, 5 * 2**attempt))
        except (urllib.error.URLError, TimeoutError):
            time.sleep(min(120, 5 * 2**attempt))
    raise RuntimeError('retries exhausted')

def ext(ct, url):
    e = mimetypes.guess_extension(ct.split(';')[0].strip().lower()) if ct else None
    if e in ('.jpe', '.jpeg'): e = '.jpg'
    return e or Path(url.split('?')[0]).suffix.lower() or '.bin'

stored = {}; n = ok = fail = reused = 0; nbytes = 0
with (out / 'records.jsonl').open('w') as ledger:
    for r in map(json.loads, (run / 'records.jsonl').open()):
        if r.get('media'): continue
        snaps = ((r['ad'].get('composite_preview') or {}).get('ad_snaps') or [])
        for i, s in enumerate(snaps):
            url = s.get('top_snap_media_download_link')
            if not url: continue
            n += 1
            row = {'ad_id': r['ad_id'], 'query_advertiser': r['query_advertiser'], 'snap_index': i,
                   'media_type': s.get('top_snap_media_type'),
                   'retrieved_at_utc': datetime.now(timezone.utc).isoformat()}
            try:
                data, status, ct = fetch(url)
                sha = hashlib.sha256(data).hexdigest()
                if sha in existing:
                    path = '../' + run.name + '/' + existing[sha]; reused += 1
                elif sha in stored:
                    path = stored[sha]
                else:
                    p = media_dir / f'{sha}{ext(ct, url)}'
                    p.write_bytes(data); nbytes += len(data)
                    path = str(p.relative_to(out)); stored[sha] = path
                row.update(http_status=status, content_type=ct, byte_length=len(data), sha256=sha, local_path=path)
                ok += 1
            except Exception as e:
                row['error'] = f'{type(e).__name__}: {e}'[:200]; fail += 1
            ledger.write(json.dumps(row) + '\n'); ledger.flush()
            time.sleep(0.2)
        if n and n % 250 == 0: print(f'{n} links, ok {ok}, failed {fail}', flush=True)

manifest = {'source_run': run.name, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
            'links': n, 'downloaded': ok, 'failed': fail, 'reused_source_files': reused,
            'new_unique_files': len(stored), 'new_bytes': nbytes}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
