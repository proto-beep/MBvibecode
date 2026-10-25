"""Without a browser: the texts of the script, the list of connections (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: i18n, connections – each the former smoke/t_<case>.py, unchanged; `python3 t_static.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_i18n():
    """Credits Importer 3.27.1: the texts of the script (collected items 68, 69).
    English is the base: every text the code asks for must be there in English. German, Spanish and French are translated
    every few versions; until then the script shows the English text, so a missing translation is reported, not an error.
    A) Every key the code names (tr, trSrc, trRules, trView, trIn, log, logView, showMessage) is in English (or as a plural
       ".other", or as its "…Any" form).
    B) No translation without its English text (left over), no placeholder in a translation that English does not have.
    C) French: a no-break space before ":", ";", "?", "!" and "»" and after "«" – never a plain space.
    D) Report: how many texts each language still lacks, and which (not an error).
    E) A text missing in German (plain and plural) shows in English (Node).
    Run with LIST=1 to print every missing key."""
    import json
    import os
    import re
    import subprocess
    from pathlib import Path

    SCRIPT = Path(__file__).resolve().parent.parent / 'mb-vibecode-credits-importer.user.js'
    LANGS = ['en', 'de', 'es', 'fr']
    src = SCRIPT.read_text(encoding='utf-8')
    start = src.index('  const I18N = {')
    blocks = {}
    pos = start
    for lang in LANGS:
        m = re.compile(r'\n    ' + lang + r': \{\n').search(src, pos)
        end = src.index('\n    },', m.end())
        texts = {}
        for line in src[m.end():end].split('\n'):
            mm = re.match(r'      ("(?:[^"\\]|\\.)*"): (".*"),$', line)
            if mm:
                texts[json.loads(mm.group(1))] = json.loads(mm.group(2))
        blocks[lang] = texts
        pos = end
    i18n_end = src.index('\n  };', start)
    code = src[:start] + src[i18n_end:]
    en = blocks['en']
    results = []

    # A) keys the code names
    used = set(re.findall(r"\b(?:tr|trSrc|trRules|trView)\(\s*'([\w.]+)'", code))
    used |= set(re.findall(r"\btrIn\([^,]+,\s*'([\w.]+)'", code))
    used |= {'log.' + k for k in re.findall(r"\b(?:log|logView)\(\s*'(?:info|warn|error|ok)'\s*,\s*'([\w.]+)'", code)}
    used |= set(re.findall(r"\bshowMessage\(\s*'(?:info|warn|error|ok)'\s*,\s*'([\w.]+)'", code))
    missing_en = sorted(k for k in used if k not in en and f'{k}.other' not in en and f'{k}Any' not in en)
    print('A) Schlüssel im Code:', len(used), '| ohne englischen Text:', missing_en or 'keiner')
    results.append(not missing_en)

    # B) left over, placeholders
    ph = lambda t: set(re.findall(r'\{(\w+)\}', t))
    left, extra = {}, {}
    for lang in LANGS[1:]:
        left[lang] = [k for k in blocks[lang] if k not in en]
        extra[lang] = [k for k, t in blocks[lang].items() if k in en and ph(t) - ph(en[k])]
    print('B) übrig ohne Englisch:', {k: v[:5] for k, v in left.items() if v} or 'nichts', '| fremde Platzhalter:', {k: v[:5] for k, v in extra.items() if v} or 'keine')
    results.append(not any(left.values()) and not any(extra.values()))

    # C) French spaces
    bad = [k for k, t in blocks['fr'].items() if re.search(r' [:;?!»]|« ', t)]
    print('C) Französisch mit einfachem Leerzeichen:', bad[:10] or 'keins', f'({len(bad)})' if bad else '')
    results.append(not bad)

    # D) report
    for lang in LANGS[1:]:
        miss = [k for k in en if k not in blocks[lang]]
        share = 100 * (len(en) - len(miss)) / len(en)
        print(f'D) {lang}: {len(blocks[lang])} Texte, {len(miss)} noch nicht übersetzt ({share:.1f} % übersetzt)'
              + (f' – {", ".join(miss[:8])}{" …" if len(miss) > 8 else ""}' if miss else ''))
        if os.environ.get('LIST') and miss:
            print('   ' + '\n   '.join(miss))
    # E) the English fallback
    NODE = """const m = require(process.argv[1]); delete m.I18N.de['source.load']; delete m.I18N.de['tracks.count.one']; delete m.I18N.de['tracks.count.other'];
m.setLang('de'); console.log(JSON.stringify([m.tr('source.load'), m.tr('tracks.count', { sel: 2, n: 4 }), m.tr('source.other')]));"""
    e1 = json.loads(subprocess.run(['node', '-e', NODE, str(SCRIPT)], capture_output=True, text=True, check=True).stdout)
    print('E) Deutsch ohne Übersetzung:', e1)
    results.append(e1[0] == 'Load' and e1[1] == '2 of 4 tracks' and e1[2].startswith('Andere Quelle'))
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_connections():
    """Credits Importer 3.25.0: the list of connections (collected item 40; CONNECTIONS, ⚙ Settings → ⓘ Connections).
    A) Every address of the script – its header (@match, @connect, @updateURL, @downloadURL, @homepageURL, @supportURL,
       @namespace) and every https:// address in its code – belongs to a connection of the list (by its hosts); a new site
       cannot be added to the script without the list.
    B) Each connection has an id of its own, its kind and a text of what the script does with it in English ([3.27.1] the
       other languages may follow later – until then English shows; before: all four required); a connection without a name
       of its own has one in the texts."""
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
    print('B) Verbindungen:', ids, '| fehlende Texte (nur Englisch zählt):', {k: v for k, v in gaps.items() if v})
    results.append(len(ids) == len(set(ids)) and len(ids) >= 10 and not gaps['en'])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
