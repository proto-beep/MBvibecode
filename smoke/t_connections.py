"""Credits Importer 3.25.0: the list of connections (collected item 40; CONNECTIONS, ⚙ Settings → ⓘ Connections).
A) Every address of the script – its header (@match, @connect, @updateURL, @downloadURL, @homepageURL, @supportURL,
   @namespace) and every https:// address in its code – belongs to a connection of the list (by its hosts); a new site
   cannot be added to the script without the list.
B) Each connection has an id of its own, its kind and a text of what the script does with it in all four languages; a
   connection without a name of its own has one in the texts."""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')
src = open(SCRIPT, encoding='utf-8').read()
NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const texts = {};
for (const lang of Object.keys(m.I18N)) texts[lang] = Object.keys(m.I18N[lang]).filter((k) => k.startsWith('conn.'));
console.log(JSON.stringify({ conns: m.CONNECTIONS, texts }));
"""
res = json.loads(subprocess.run(['node', '-e', NODE, SCRIPT], capture_output=True, text=True, check=True).stdout)
conns = res['conns']
results = []
# A)
head = src[:src.index('==/UserScript==')]
hosts = set()
for line in head.splitlines():
    m = re.match(r'//\s*@(match|connect|updateURL|downloadURL|homepageURL|supportURL|namespace)\s+(\S+)', line)
    if not m:
        continue
    v = m.group(2)
    if m.group(1) == 'connect':
        hosts.add(v)
    else:
        h = re.match(r'(?:\*|https?)://([^/]+)', v)
        if h:
            hosts.add(h.group(1).lstrip('*.'))
body = src[src.index('==/UserScript=='):]
for h in re.findall(r'https?://([a-z0-9][a-z0-9.-]*\.[a-z]{2,})', body):
    hosts.add(h.rstrip('.'))


def owner(h):
    for c in conns:
        for d in c['hosts']:
            if d.endswith('.*') and h.startswith(d[:-2]):
                return c['id']
            if h == d or h.endswith('.' + d):
                return c['id']
    return None


found = {h: owner(h) for h in sorted(hosts)}
missing = [h for h, o in found.items() if not o]
for h, o in found.items():
    print(f'   {h:32} → {o}')
print('A) Adressen:', len(hosts), '| ohne Verbindung:', missing)
results.append(len(hosts) >= 10 and not missing)
# B)
ids = [c['id'] for c in conns]
need = [f'conn.{c["id"]}' for c in conns] + [f'conn.{c["id"]}.name' for c in conns if not c['name']] + [f'conn.kind.{c["kind"]}' for c in conns]
gaps = {lang: [k for k in need if k not in keys] for lang, keys in res['texts'].items()}
print('B) Verbindungen:', ids, '| fehlende Texte:', {k: v for k, v in gaps.items() if v})
results.append(len(ids) == len(set(ids)) and len(ids) >= 10 and not any(gaps.values()) and set(gaps) == {'en', 'de', 'es', 'fr'})
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
