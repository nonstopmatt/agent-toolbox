#!/usr/bin/env python3
"""Firecrawl-scrape stand-in: URL -> readable text/markdown on stdout.

  python3 ~/toolbox/bin/web_fetch.py <url> [--max 20000] [--via scrapling|jina|nimble|plain]

Chain (first that returns real content wins, the one that served it is printed to stderr):
  1. Scrapling    local, free, no key; HTTP then stealth browser (venv ~/toolbox/venvs/scrapling)
  2. Jina Reader  r.jina.ai   markdown, like firecrawl_scrape   key ~/.config/vb/jina_key
  3. Nimble       webit.live  JS-rendered HTML -> text          key ~/.config/vb/nimble_key
  4. plain GET    urllib      no JS, no key
"Real content" = at least 400 chars and not a login/challenge page; an empty result is
reported as NOT FETCHED, never as "the page has nothing" (exit 2).
Keys are read from files and never printed.
"""
import json, os, re, sys, urllib.request

KEYS = os.path.expanduser('~/.config/vb')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'
BLOCKED = re.compile(r'just a moment|attention required|verify you are human|access denied|captcha', re.I)


def key(name):
    try:
        return open(os.path.join(KEYS, name)).read().strip()
    except OSError:
        return None


def html_text(h):
    h = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?i)<(br|/p|/div|/li|/h[1-6]|/tr)[^>]*>', '\n', h)
    t = re.sub(r'<[^>]+>', ' ', h)
    for a, b in (('&amp;', '&'), ('&nbsp;', ' '), ('&#39;', "'"), ('&quot;', '"'), ('&lt;', '<'), ('&gt;', '>')):
        t = t.replace(a, b)
    return re.sub(r'\n\s*\n+', '\n\n', re.sub(r'[ \t]+', ' ', t)).strip()


def scrapling(url):
    import subprocess
    r = subprocess.run([os.path.expanduser('~/toolbox/bin/scrapling_fetch.py'), url], capture_output=True, text=True, timeout=150)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-200:])
    return r.stdout.strip()


def jina(url):
    k = key('jina_key')
    h = {'User-Agent': UA, 'X-Return-Format': 'markdown'}
    if k:
        h['Authorization'] = 'Bearer ' + k
    return urllib.request.urlopen(urllib.request.Request('https://r.jina.ai/' + url, headers=h), timeout=60).read().decode('utf-8', 'replace')


def nimble(url):
    k = key('nimble_key')
    if not k:
        raise RuntimeError('no nimble key')
    body = json.dumps({'url': url, 'render': True, 'country': 'US', 'locale': 'en'}).encode()
    req = urllib.request.Request('https://api.webit.live/api/v1/realtime/web', data=body, method='POST',
                                 headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(req, timeout=90))
    return html_text(d.get('html_content') or '')


def plain(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30).read()
    return html_text(raw.decode('utf-8', 'replace'))


def fetch(url, via=None):
    for name, fn in [('scrapling', scrapling), ('jina', jina), ('nimble', nimble), ('plain', plain)]:
        if via and name != via:
            continue
        try:
            t = fn(url)
        except Exception as e:
            print(f'[web_fetch] {name} failed: {str(e)[:120]}', file=sys.stderr)
            continue
        if len(t) >= 400 and not BLOCKED.search(t[:1500]):
            return name, t
        print(f'[web_fetch] {name} returned {len(t)} chars (blocked or empty), trying next', file=sys.stderr)
    return None, ''


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    mx = int(args[args.index('--max') + 1]) if '--max' in args else 20000
    via = args[args.index('--via') + 1] if '--via' in args else None
    who, text = fetch(args[0], via)
    if not who:
        print(f'[web_fetch] NOT FETCHED: {args[0]} (all providers failed; try claude-in-chrome)', file=sys.stderr)
        sys.exit(2)
    print(f'[web_fetch] served by {who}, {len(text)} chars', file=sys.stderr)
    print(text[:mx])
