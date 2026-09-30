#!~/toolbox/venvs/scrapling/bin/python
"""URL -> page text via Scrapling (local, free). Used by web_fetch.py as its first rung.
  scrapling_fetch.py <url> [--stealth]   fast HTTP first; --stealth or a thin page -> stealth browser (JS rendered)."""
import sys, logging
logging.disable(logging.CRITICAL)
from scrapling.fetchers import Fetcher, StealthyFetcher

def text(p):
    return '\n'.join(' '.join(l.split()) for l in str(p.get_all_text(ignore_tags=('script', 'style', 'noscript'))).splitlines() if l.strip())

url = sys.argv[1]
t, mode = '', ''
if '--stealth' not in sys.argv:
    try:
        t, mode = text(Fetcher.get(url, stealthy_headers=True, timeout=30)), 'http'
    except Exception:
        t = ''
if len(t) < 400:
    t, mode = text(StealthyFetcher.fetch(url, headless=True, network_idle=True)), 'stealth'
sys.stderr.write(f'[scrapling] {mode}\n')
print(t)
