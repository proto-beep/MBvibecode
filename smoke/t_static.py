"""Without a browser: the texts of the script, the list of connections (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: i18n, connections, mappingfile (3.33.0) – each the former smoke/t_<case>.py, unchanged; `python3 t_static.py <case> …` runs only those."""
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
    # [3.34.0] German, Spanish and French in the languages file, English in the script
    LANGUAGES = Path(__file__).resolve().parent.parent / 'mb-vibecode-credits-importer-languages.json'
    LANGS = ['en', 'de', 'es', 'fr']
    src = SCRIPT.read_text(encoding='utf-8')
    start = src.index('  const I18N = {')
    m = re.compile(r'\n    en: \{\n').search(src, start)
    end = src.index('\n    },', m.end())
    texts = {}
    for line in src[m.end():end].split('\n'):
        mm = re.match(r'      ("(?:[^"\\]|\\.)*"): (".*"),$', line)
        if mm:
            texts[json.loads(mm.group(1))] = json.loads(mm.group(2))
    blocks = {'en': texts}
    blocks.update({lang: v for lang, v in json.loads(LANGUAGES.read_text(encoding='utf-8')).items() if lang in LANGS})
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


def case_mappingfile():
    """Credits Importer 3.33.0 (milestone "Mapping file", item E7): the data of the register in mb-vibecode-credits-importer-mapping.json.
    A) The file: format 1, its version the script's (@version), each of its lists used in the script (`const X = MAP.X`) and
       each `MAP.X` of the script in the file; regular expressions as {"$re", "$flags"} that compile, sets as {"$set"}.
    B) The header: @resource mapping at …/main/mb-vibecode-credits-importer-mapping.json?v=<version>, @grant GM_getResourceText
       and GM.getResourceUrl, @connect raw.githubusercontent.com.
    C) In Node the script reads the file next to it (the register's golden test needs nothing else)."""
    import json
    import os
    import re
    import subprocess

    HERE = os.path.dirname(os.path.abspath(__file__))
    SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')
    FILE = os.path.join(HERE, '..', 'mb-vibecode-credits-importer-mapping.json')
    src = open(SCRIPT, encoding='utf-8').read()
    data = json.load(open(FILE, encoding='utf-8'))
    version = re.search(r'^// @version\s+(\S+)', src, re.M).group(1)
    keys = [k for k in data if k not in ('format', 'version', 'about')]
    used = set(re.findall(r'\bconst (\w+) = MAP\.(\w+);', src))
    used_names = {b for a, b in used}
    bad_pairs = [(a, b) for a, b in used if a != b]
    regs = []

    def walk(v):
        if isinstance(v, dict):
            if '$re' in v:
                regs.append((v['$re'], v.get('$flags', '')))
                return
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    walk(data)
    js = subprocess.run(['node', '-e', "const r = JSON.parse(process.argv[1]); let bad = []; for (const [s, f] of r) { try { new RegExp(s, f); } catch (e) { bad.push(s.slice(0, 40)); } } console.log(JSON.stringify(bad));",
                         json.dumps(regs)], capture_output=True, text=True, check=True)
    bad_re = json.loads(js.stdout)
    print('A) Format:', data.get('format'), '| Version:', data.get('version'), 'Skript:', version, '| Listen:', len(keys), '| im Skript:', len(used_names),
          '| nicht benutzt:', sorted(set(keys) - used_names), '| fehlen:', sorted(used_names - set(keys)), '| Muster:', len(regs), 'kaputt:', bad_re, bad_pairs)
    ok_a = data.get('format') == 1 and data.get('version') == version and set(keys) == used_names and not bad_pairs and len(regs) > 50 and not bad_re
    head = src[:src.index('// ==/UserScript==')]
    res = re.search(r'^// @resource\s+mapping\s+(\S+)$', head, re.M)
    print('B) @resource:', res and res.group(1))
    ok_b = bool(res) and res.group(1) == f'https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-mapping.json?v={version}' \
        and '// @grant        GM_getResourceText' in head and '// @grant        GM.getResourceUrl' in head and '// @connect      raw.githubusercontent.com' in head
    node = subprocess.run(['node', '-e', "global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 }; const m = require(process.argv[1]); console.log(m.mapRole('Mixed By', []).rule)",
                           SCRIPT], capture_output=True, text=True)
    print('C) Node:', node.stdout.strip(), node.stderr[-200:])
    ok_c = node.stdout.strip() == 'R033'
    print('Ergebnis:', 'OK' if ok_a and ok_b and ok_c else 'FEHLER', [ok_a, ok_b, ok_c])



def case_languagesfile():
    """Credits Importer 3.34.0 (milestone "Languages file", item E6): German, Spanish and French in
    mb-vibecode-credits-importer-languages.json, English in the script.
    A) The file: format 1, its version the script's, an object of texts for de, es and fr (nothing else besides format,
       version, about); one text a line (the layout of tools/i18n_add.py – a pull request shows only what changed).
    B) The script keeps only English (no block de / es / fr in `const I18N`), every key of the file is in English.
    C) The header: @resource languages at …/main/mb-vibecode-credits-importer-languages.json?v=<version>.
    D) In Node the script reads the file next to it: German texts, and English where German has none."""
    import json
    import os
    import re
    import subprocess
    import sys

    HERE = os.path.dirname(os.path.abspath(__file__))
    SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')
    FILE = os.path.join(HERE, '..', 'mb-vibecode-credits-importer-languages.json')
    src = open(SCRIPT, encoding='utf-8').read()
    text = open(FILE, encoding='utf-8').read()
    data = json.loads(text)
    version = re.search(r'^// @version\s+(\S+)', src, re.M).group(1)
    sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
    import i18n_add
    layout = []
    i18n_add.LANGUAGES = type('W', (), {'write_text': lambda self, t, encoding=None: layout.append(t)})()
    i18n_add.write_languages(data)
    print('A) Format:', data.get('format'), '| Version:', data.get('version'), 'Skript:', version, '| Teile:', sorted(data), '| Texte:', {k: len(data[k]) for k in ('de', 'es', 'fr') if k in data},
          '| Aufbau wie i18n_add:', layout[0] == text)
    ok_a = data.get('format') == 1 and data.get('version') == version and sorted(data) == ['about', 'de', 'es', 'format', 'fr', 'version'] \
        and all(isinstance(data[k], dict) and len(data[k]) > 1000 for k in ('de', 'es', 'fr')) and layout[0] == text
    start = src.index('  const I18N = {')
    i18n = src[start:src.index('\n  };', start)]
    blocks = re.findall(r'^    (\w+): \{$', i18n, re.M)
    en = set(json.loads(m) for m in re.findall(r'^      ("(?:[^"\\]|\\.)*"): ', i18n, re.M))
    extra = {k: [x for x in data[k] if x not in en][:5] for k in ('de', 'es', 'fr')}
    print('B) Blöcke im Skript:', blocks, '| Englisch:', len(en), '| ohne Englisch:', extra)
    ok_b = blocks == ['en'] and not any(extra.values())
    head = src[:src.index('// ==/UserScript==')]
    res = re.search(r'^// @resource\s+languages\s+(\S+)$', head, re.M)
    print('C) @resource:', res and res.group(1))
    ok_c = bool(res) and res.group(1) == f'https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-languages.json?v={version}'
    node = subprocess.run(['node', '-e', "global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 }; const m = require(process.argv[1]); m.setLang('de'); "
                           "delete m.I18N.de['common.on']; console.log(JSON.stringify([m.tr('source.load'), m.tr('common.on'), Object.keys(m.I18N).sort()]))",
                           SCRIPT], capture_output=True, text=True)
    print('D) Node:', node.stdout.strip(), node.stderr[-200:])
    d = json.loads(node.stdout or 'null')
    ok_d = bool(d) and d[0] == data['de']['source.load'] and d[0] != 'Load' and d[1] == 'on' and d[2] == ['de', 'en', 'es', 'fr']
    print('Ergebnis:', 'OK' if ok_a and ok_b and ok_c and ok_d else 'FEHLER', [ok_a, ok_b, ok_c, ok_d])


run_cases(globals())
