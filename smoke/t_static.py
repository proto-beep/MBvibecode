"""Without a browser: the texts of the script, the list of connections (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: i18n, connections, mappingfile (3.33.0), round6 (3.41.5) – each the former smoke/t_<case>.py, unchanged; `python3 t_static.py <case> …` runs only those."""
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
    # (3.39.2, review) trSrcOf(src, 'key'): the text and its …Any form; log(level, a ? 'k1' : 'k2', …): both
    src_of = set(re.findall(r"\btrSrcOf\([^,]+,\s*'([\w.]+)'", code))
    used |= src_of | {k + 'Any' for k in src_of}
    for k1, k2 in re.findall(r"\blog\(\s*'(?:info|warn|error|ok)'\s*,\s*[^,'()]+\?\s*'([\w.]+)'\s*:\s*'([\w.]+)'", code):
        used |= {'log.' + k1, 'log.' + k2}
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


def case_round6():
    """Credits Importer 3.41.5 (Block BE, translation round F-6): the texts added in English since Block AL are in German, Spanish
    and French – a sample of each block (AL – BD) shown in each language differs from the English, keeps its placeholders and
    symbols; the French with a no-break space before ":" (until 3.41.4: English in all three)."""
    import json
    import subprocess
    KEYS = ['notes.off', 'gap.count', 'group.copyName', 'dm.fold', 'settings.emSide', 'group.addRole', 'livecom.all', 'stats.whereOn',
            'statsOnly.hint', 'group.skip', 'settings.skipHide', 'repeat.button', 'repeat.ask', 'matrix.coverAuto', 'suite.ask', 'suite.yes',
            'settings.suiteNaming', 'medley.split', 'suite.partPick', 'log.partsFound']
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const keys = JSON.parse(process.argv[2]);
const out = {};
for (const l of ['en', 'de', 'es', 'fr']) { m.setLang(l); out[l] = keys.map((k) => m.tr(k, { tracks: 'T', name: 'N', n: 2, title: 'X', track: '1.3', names: 'M', list: 'L' })); }
console.log(JSON.stringify(out));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(KEYS)], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else {'error': js.stderr[-400:]}
    same = {l: [k for k, a, b in zip(KEYS, got.get('en', []), got.get(l, [])) if a == b] for l in ('de', 'es', 'fr')}
    print('A) wie Englisch:', same)
    print('B) Beispiele:', [got.get(l, [None] * 15)[14] for l in ('de', 'es', 'fr')], [got.get(l, [None] * 10)[9] for l in ('de', 'es', 'fr')])
    sym = [k for i, k in enumerate(KEYS) for l in ('de', 'es', 'fr') if any(c in got['en'][i] and c not in got[l][i] for c in '✓⊘↻＋')] if 'en' in got else ['?']
    fr_colon = 'fr' in got and '\u00a0:' in got['fr'][KEYS.index('suite.partPick') + 1]
    print('C) Zeichen fehlen:', sym, '| fr „\u00a0:“:', fr_colon)
    results = ['error' not in got, not any(same.values()), not sym, fr_colon]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_legacy():
    """Credits Importer 3.41.7 (collected item Z-LG): the view "Legacy" of the entries (⚙ Settings → Appearance → Entries) is named
    "Legacy" in every language – and so in the note of 3.35.0 that names it (until 3.41.6: Klassisch, Clásica, Classique)."""
    import json
    import subprocess
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const out = {};
for (const l of ['en', 'de', 'es', 'fr']) { m.setLang(l); out[l] = [m.tr('settings.entries.legacy'), m.tr('ms.3.35.0')]; }
console.log(JSON.stringify(out));
"""
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else {'error': js.stderr[-400:]}
    print('A)', {l: v[0] for l, v in got.items() if l != 'error'})
    old = [l for l, v in got.items() if l != 'error' and any(w in v[1] for w in ('Klassisch', 'Clásica', 'Classique'))]
    print('B) alte Namen in ms.3.35.0:', old)
    results = ['error' not in got, all(v[0] == 'Legacy' for l, v in got.items() if l != 'error'), not old,
               all('Legacy' in v[1] for l, v in got.items() if l != 'error')]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_gapbtn3112():
    """Credits Importer 3.112.0 (collected item Z-GAPBTN): the line at the top of the release page – "Count exactly" and "Import
    credits …" small round buttons (outlined, filled), not underlined text (until 3.111.0)."""
    import os
    import re
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mb-vibecode-credits-importer.user.js'), encoding='utf-8').read()
    cnt = re.search(r'<button type="button" data-gap="count"[^>]*>', src)
    imp = re.search(r'<button type="button" data-gap="import"[^>]*>', src)
    pill = re.search(r"const pill = '([^']*)'", src)
    print('count:', cnt and cnt.group(0)[:160], '\nimport:', imp and imp.group(0)[:160], '\npill:', pill and pill.group(1))
    ok = bool(cnt and imp and pill) and 'underline' not in cnt.group(0) + imp.group(0) and '${pill}' in cnt.group(0) and '${pill}' in imp.group(0) \
        and 'border-radius:999px' in pill.group(1) and 'background:#736dab' in imp.group(0) and 'background:#fff' in cnt.group(0)
    print('Ergebnis:', 'OK' if ok else 'FEHLER')


def case_review3159():
    """Credits Importer 3.159.0 (Z-REVIEW-FABLE, review run 2: architecture, contradicting mappings) – what the run corrected, kept so:
    A) No rule id twice in the mapping file (until 3.158.0 Q013 was the question of "Horns" and that of a group's members: one switch
       for both; the members' question is Q016 now).
    B) Every S rule of the register is asked somewhere – ruleOn('S…') or a role rule's `special` – or is one of FIXED_RULES, whose
       switch the list of the mapping rules shows ticked and greyed (nine rules had a switch that changed nothing).
    C) What a rule's "where" names exists in the code (six rules named functions that were renamed or gone).
    D) Dates: "Remastered 2015" belongs to the remastering (not the mastering – "master" was found inside "remastered"), "Premastered"
       to the mastering; "Piano Concerto No. 2 (1901)" and "Konzertmeister" name no performance ("concert" was found inside them).
    E) Instruments under MusicBrainz's present names: shakers, tenor horn / alto horn."""
    import json
    import re
    import subprocess
    root = H.ROOT
    src = (root / 'mb-vibecode-credits-importer.user.js').read_text(encoding='utf-8')
    mapping = json.loads((root / 'mb-vibecode-credits-importer-mapping.json').read_text(encoding='utf-8'))
    ids = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('id'), str) and re.match(r'^[A-Z]\d{3}$', o['id']):
                ids.append(o['id'])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(mapping)
    twice = sorted({i for i in ids if ids.count(i) > 1})
    print('A) ids twice in the mapping file:', twice)
    reg = dict(re.findall(r"\{ id: '(S\d{3})', where: '((?:[^'\\]|\\.)*)'", src))
    lines = src.split('\n')
    code = '\n'.join(l for l in lines if not re.match(r"\s*\{ id: '[A-Z]\d{3}', where:", l))
    asked = set(re.findall(r"ruleOn(?:Stored)?\('(S\d{3})'\)", code)) | {r['special'] for r in mapping['ROLE_RULE_DATA'] if r.get('special')}
    fixed = set(re.findall(r"'(S\d{3})'", re.search(r'const FIXED_RULES = new Set\(\[([^\]]*)\]\)', src).group(1)))
    never = sorted(i for i in reg if i not in asked and i not in fixed)
    both = sorted(fixed & asked)
    print('B) S rules:', len(reg), '| never asked and not fixed:', never, '| fixed but asked:', both, '| fixed:', sorted(fixed))
    stop = {'with', 'from', 'also', 'review', 'rules', 'data', 'their', 'text', 'code', 'list', 'lists', 'table', 'tables', 'dashboard', 'register',
            'mapping', 'case', 'json', 'part', 'parts', 'companion', 'bcArt'}
    gone = {}
    for i, w in reg.items():
        for t in re.findall(r'[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*', w):
            base = t.split('.')[-1]
            if len(base) < 4 or base in stop or base.lower() in stop or re.match(r'^[A-Z]\d{3}$', base):
                continue
            if not re.search(r'\b' + re.escape(base) + r'\b', code) and base not in mapping:
                gone.setdefault(i, []).append(t)
    print('C) "where" names not in the code:', gone)
    node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const out = JSON.parse(process.argv[2]).map((t) => [t, m.findDates(t, {}).map((d) => [d.text, d.hint, d.hints])]);
console.log(JSON.stringify(out));
"""
    texts = ['Remastered 2015.', 'Re-mastered 2015', 'Premastered 2001', 'Mastered 1985, remastered 2015', 'Remastered and mixed 2020', 'Grandmaster Flash, 1982',
             'Piano Concerto No. 2 (1901)', 'Konzertmeister: X, 1999', 'Recorded at the concert, 1970', 'Konzerte 1999']
    js = subprocess.run(['node', '-e', node, str(root / 'mb-vibecode-credits-importer.user.js'), json.dumps(texts)], capture_output=True, text=True)
    got = dict(json.loads(js.stdout)) if not js.returncode else {}
    for t in texts:
        print('D)', t, '→', got.get(t), js.stderr[-200:] if js.returncode else '')
    hint = lambda t, k=0: (got.get(t) or [[None, None, []]] * (k + 1))[k][1]  # noqa: E731
    ok_d = (hint('Remastered 2015.') == 'remastering' and hint('Re-mastered 2015') == 'remastering' and hint('Premastered 2001') == 'mastering'
            and [hint('Mastered 1985, remastered 2015'), hint('Mastered 1985, remastered 2015', 1)] == ['mastering', 'remastering']
            and got.get('Remastered and mixed 2020', [[0, 0, []]])[0][2] == ['remastering', 'mix'] and hint('Grandmaster Flash, 1982') == ''
            and hint('Piano Concerto No. 2 (1901)') == '' and hint('Konzertmeister: X, 1999') == ''
            and hint('Recorded at the concert, 1970') == 'performance' and hint('Konzerte 1999') == 'performance')
    al = mapping['INSTRUMENT_ALIASES']
    ok_e = al.get('bug shaker', [''])[0] == 'shakers' and al.get('tenor horn', [''])[0] == 'tenor horn / alto horn' and al.get('alto horn', [''])[0] == 'tenor horn / alto horn'
    print('E)', al.get('bug shaker'), al.get('tenor horn'), al.get('alto horn'))
    results = [not twice, not never and not both and len(fixed) == 9, not gone, ok_d, ok_e,
               'data-rule-fixed=' in src and '"rules.fixedTitle"' in src]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_small3162():
    """Credits Importer 3.162.0 (the small corrections proposed by review runs 2 and 3).
    A) Roles: "Tenor", "Baritone", "Soprano" alone are asked (R121–R123, Q017–Q019) like "Alto"; "Bugle" and "Laúd" too (R124, R125;
       no translation to flugelhorn / lute any more); "Text By" asks like "Text" (R100); "Libretto" is the librettist, "Second Engineer"
       the engineer with "assistant", "Video By" the video director, "Arranged At" for a person the arranger.
    B) Companies: "Filmed At" → video shot at, "Arranged At" → arranged at (places); "Licensed To" has no type for an artist.
    C) Dates: "master" and "mix" alone are no hint ("original master tapes in 1998", "Mix Master Mike, 1998", "DJ Mix series, 2004");
       "Mastered 1985", "Mixed in 2004", "Final mix, March 1998" still are.
    D) "Tape: No Problema Tapes / Vinyl: Hiraeth Records" is left out as the label of an edition (S294); "Tape: John Doe" stays a credit.
    E) The setting "Offer ⑃" is gone; a quick switch that needs another rule says so (QS_NEEDS)."""
    import json
    import subprocess
    root = H.ROOT
    src = (root / 'mb-vibecode-credits-importer.user.js').read_text(encoding='utf-8')
    node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const inp = JSON.parse(process.argv[2]);
const role = (w) => { const r = m.mapRole(w, []); return [r.rule || '', r.types, r.level, (r.flags || []).join(',')]; };
const comp = (w) => { const r = m.mapCompanyRole(w); const o = r.typeOptions || {}; return [r.rule || '', o.place || [], o.area || [], o.artist || [], o.label || []]; };
const isRole = (p) => /^(tapes?|guitar)$/i.test(String(p).trim());
const parse = (t) => { const r = m.SOURCES.text.parse(t, { isRole, isCompanyRole: () => false, resolveTracks: () => null, resolveTitles: () => null, artistNames: ['The Band'], trackCount: 8 });
  return [r.credits.map((c) => [c.who && c.who.name, c.role]), r.ignored.map((u) => u.why)]; };
console.log(JSON.stringify({ roles: Object.fromEntries(inp.roles.map((w) => [w, role(w)])), comps: Object.fromEntries(inp.comps.map((w) => [w, comp(w)])),
  dates: Object.fromEntries(inp.dates.map((t) => [t, m.findDates(t, {}).map((d) => d.hint)])), texts: Object.fromEntries(inp.texts.map((t) => [t, parse(t)])) }));
"""
    inp = {'roles': ['Alto', 'Tenor', 'Baritone', 'Soprano', 'Bugle', 'Laúd', 'Text', 'Text By', 'Libretto', 'Second Engineer', 'Video By', 'Arranged At',
                     'Tenor Saxophone', 'Notes'],
           'comps': ['Filmed At', 'Arranged At', 'Licensed To'],
           'dates': ['Mastered 1985', 'original master tapes in 1998', 'Mix Master Mike, 1998', 'DJ Mix series, 2004', 'Mixed in 2004', 'Final mix, March 1998'],
           'texts': ['Tape: No Problema Tapes / Vinyl: Hiraeth Records', 'Tape: No Problema Tapes\nVinyl: Hiraeth', 'Tape: John Doe', 'Tape: John Doe\nVinyl: Jane Roe']}
    js = subprocess.run(['node', '-e', node, str(root / 'mb-vibecode-credits-importer.user.js'), json.dumps(inp)], capture_output=True, text=True)
    got = json.loads(js.stdout) if not js.returncode else {'roles': {}, 'comps': {}, 'dates': {}, 'texts': {}}
    if js.returncode:
        print(js.stderr[-400:])
    r = got['roles']
    for k, v in r.items():
        print('A)', k, '→', v)
    rule = lambda w: (r.get(w) or [''])[0]  # noqa: E731
    ok_a = ([rule(w) for w in ['Alto', 'Tenor', 'Baritone', 'Soprano', 'Bugle', 'Laúd', 'Text', 'Text By']] == ['R102', 'R121', 'R122', 'R123', 'R124', 'R125', 'R100', 'R100']
            and r.get('Libretto', ['', []])[1][:1] == ['librettist'] and r.get('Second Engineer') == ['R120', ['engineer'], 'recording', 'assistant']
            and r.get('Video By', ['', []])[1] == ['video director'] and r.get('Arranged At', ['', []])[1][:1] == ['arranger']
            and rule('Tenor Saxophone') == 'R096' and rule('Notes') == 'R082')
    c = got['comps']
    print('B)', c)
    ok_b = (c.get('Filmed At', ['', []])[1] == ['video shot at'] and c.get('Arranged At', ['', []])[1] == ['arranged at']
            and c.get('Licensed To', ['', [], [], ['x'], []])[3] == [] and c.get('Licensed To')[4] == ['licensee'])
    d = got['dates']
    print('C)', d)
    ok_c = (d.get('Mastered 1985') == ['mastering'] and d.get('original master tapes in 1998') == [''] and d.get('Mix Master Mike, 1998') == ['']
            and d.get('DJ Mix series, 2004') == [''] and d.get('Mixed in 2004') == ['mix'] and d.get('Final mix, March 1998') == ['mix'])
    t = got['texts']
    print('D)', t)
    ok_d = (t.get('Tape: No Problema Tapes / Vinyl: Hiraeth Records') == [[], ['formatLabel']] and t.get('Tape: No Problema Tapes\nVinyl: Hiraeth') == [[], ['formatLabel', 'formatLabel']]
            and t.get('Tape: John Doe') == [[['John Doe', 'Tape']], []] and (t.get('Tape: John Doe\nVinyl: Jane Roe') or [[]])[0] == [['John Doe', 'Tape']])
    ok_e = 'insts-common-on' not in src and '"settings.instsCommon"' not in src and "const QS_NEEDS = { S045: 'S160' };" in src
    print('E)', ok_e)
    results = [ok_a, ok_b, ok_c, ok_d, ok_e]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_video3164():
    """Credits Importer 3.164.0 (proposals F-CAMSWITCH, F-DJMIX) in Node.
    A) "Mixed By [DJ Mix]" is the DJ-mix on the release; "Mixed By" alone the mix on the recordings.
    B) Camera work ("Cameras", "Filmed By") follows the quick switch S263: on – miscellaneous support; off – left out (Skip) like the
       other video credits MusicBrainz has no type for.
    C) ℗ (C001): on the recordings; with S297 on, on the release."""
    import json
    import subprocess
    root = H.ROOT
    node = r"""
const off = JSON.parse(process.argv[2]);
global.localStorage = { getItem: (k) => (k === 'dci-rules-off' ? JSON.stringify(off) : null), setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const role = (w, mods = []) => { const r = m.mapRole(w, mods); return [r.rule || '', r.types, r.level]; };
console.log(JSON.stringify({ mixed: role('Mixed By'), dj: role('Mixed By', ['DJ Mix']), cam: role('Cameras'), filmed: role('Filmed By'), pc: m.mapCompanyRole('Phonographic Copyright (p)').level }));
"""
    run = lambda off: json.loads(subprocess.run(['node', '-e', node, str(root / 'mb-vibecode-credits-importer.user.js'), json.dumps(off)], capture_output=True, text=True).stdout or '{}')  # noqa: E731
    on, off = run([]), run(['S263', '+S297'])
    print('A)', on.get('mixed'), on.get('dj'))
    print('B)', on.get('cam'), on.get('filmed'), '| S263 off:', off.get('cam'), off.get('filmed'))
    print('C)', on.get('pc'), '| S297 on:', off.get('pc'))
    results = [on.get('mixed') == ['R033', ['mix'], 'recording'] and on.get('dj') == ['R033', ['mix-dj'], 'release'],
               on.get('cam') == ['R110', ['misc'], 'recording'] and off.get('cam') == ['R110', [], 'skip'] and off.get('filmed') == ['R110', [], 'skip'],
               on.get('pc') == 'recording' and off.get('pc') == 'release']
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_block3169():
    """Credits Importer 3.169.0 (Z-HYPHENTRACKS – S298, Z-BCSHOPBLOCK – S299), the text reader in Node.
    A) A lineup in one paragraph, "Name-Role On Tracks …" (Beatport; Shpongle – Nothing Lasts… But Nothing Is Lost): thirteen credits, each
       role with its tracks – Pete Callard acoustic guitar 1–3, 18–20 and electric guitar 18, 19; Hari-Om (the name has a hyphen) vocals;
       Chris Barker bass; Raja Ram flute and vocals; Simon Posford live drums, bass guitar 4 and 9, and five roles for all tracks. The heading
       "Musicians In The Studio" is a heading, "Sonic Trickery" no role.
    B) Lines that are no such lineup stay: "Jean-Luc Ponty - violin", "The mix-down was done on tracks 1 to 4 by A-B" (no credit).
    C) The text of a vinyl edition on Bandcamp (the same album): nothing "not recognized", no credit, no company – the name of the edition,
       what the records look like and the block about shipping are "shop". "Disc A: recorded live at Café Oto" is not a shop line.
    D) S298 and S299 off: as until 3.168.0 (the paragraph no credit; the shop's lines not recognized)."""
    import json
    import subprocess
    root = H.ROOT
    node = r"""
const off = JSON.parse(process.argv[3]);
global.localStorage = { getItem: (k) => (k === 'dci-rules-off' ? JSON.stringify(off) : null), setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback)
  // ("live drums": an alias of the drum set from 3.169.0 – INSTRUMENT_ALIASES)
  || /^(acoustic guitar|electric guitar|bass guitar|guitar|vocals|bass|flute|drums|live drums|computers|synths|keyboards|violin)$/i.test(p.base); };
const trackSet = (spec) => { const out = new Set(); for (const part of String(spec).replace(/\b(?:and|tracks?)\b/gi, ',').split(/[,&]/)) { const t = part.trim(); if (!t) continue;
  const mm = t.match(/^(\d+)(?:\s*[–-]\s*(\d+))?$/); if (!mm) return null; for (let i = +mm[1]; i <= +(mm[2] || mm[1]); i++) if (i >= 1 && i <= 20) out.add(i - 1); } return out.size ? out : null; };
const run = (t) => { const r = m.SOURCES.text.parse(t, { isRole, isCompanyRole: () => false, resolveTracks: trackSet, resolveTitles: () => null, artistNames: ['Shpongle'], trackCount: 20 });
  return { credits: r.credits.map((c) => [c.who.name, c.role, c.tracks && c.tracks.indexes ? c.tracks.indexes.map((x) => x + 1).join(',') : 'all']), companies: r.companies.length,
    ignored: r.ignored.map((x) => x.why), unrecognized: r.unrecognized.map((u) => String(u.text || u)) }; };
console.log(JSON.stringify(JSON.parse(process.argv[2]).map(run)));
"""
    BEAT = ('Musicians In The Studio Pete Callard-Acoustic Guitar On Tracks 1,2,3,18,19,20, Electric Guitar on Tracks 18,19 Hari-Om- Vocals On Tracks 9,10,14,15 '
            'Chris Barker-Bass on Tracks 3,7,16 Raja Ram- Flute On Tracks 7,13,15,17,19 and Vocals on Tracks 2,7,8,11,12,13,19 Simon Posford-Live Drums on Tracks 1,2,7,8,18,19, '
            'Bass Guitar on Tracks 4 & 9 Drum Programming,Computers,Synths,Keyboards,Sonic Trickery & Production on all tracks.')
    PKG = "Nothing Lasts...But nothing is Lost (Limited Edition 400 'The Blob' Coloured Variant) 2xLP set.\nRecord/Vinyl + Digital Album\nNothing Lasts (Limited Edition 400 Coloured Variant) 2xLP set.\n\n- This is a 2 x 180gsm heavyweight coloured variant vinyl LP set.\n- DiscA/B - Transparent green with gold blob\n- Disc C/D - transparent gold with green blob\n- Packaged in a standard Sleeve.\n- Edition of 400 only.\n\n+++++INTERNATIONAL SHIPPING +++++\n\n++PLEASE READ BEFORE ORDERING++\n\n- WE DO NOT SHIP TO PO BOXES or SHIP STATIONS.\n\n- ALL ORDERS ARE SENT BY TRACKED COURIER SERVICE ONLY, PLEASE DO NOT ASK US TO SHIP REGULAR MAIL.\n\n- PLEASE INCLUDE YOUR PHONE NUMBER WITH YOU ORDER\n- All orders are shipped with full value of items declared.\n- Please note we are not responsible for any delays caused by destination customs clearance processes or customs clearance fees in destination countries.\n- If your order is returned to us for any reason, we will ship it once more free or charge, if it's returned to us again undelivered then we will issue a full refund.\n- PLEASE MAKE SURE YOUR ADDRESS IS CORRECT-\n\n- Shipping Times -\n\nUK: 2-3 days\nEUROPE: 4-5 days\nJAPAN: 4-6 days\nAUSTRALIA: 5-8 days\nREST OF WORLD: 5-8 days\n\nIncludes unlimited streaming of Nothing Lasts...But Nothing Is Lost (Remastered) via the free Bandcamp app, plus high-quality download in MP3, FLAC and more.\nDownload available in 24-bit/44.1kHz."
    texts = [BEAT, 'Jean-Luc Ponty - violin', 'The mix-down was done on tracks 1 to 4 by A-B', PKG, 'Disc A: recorded live at Café Oto']

    def run(off):
        js = subprocess.run(['node', '-e', node, str(root / 'mb-vibecode-credits-importer.user.js'), json.dumps(texts), json.dumps(off)], capture_output=True, text=True)
        if js.returncode:
            print(js.stderr[-400:])
        return json.loads(js.stdout) if not js.returncode else [{'credits': [], 'companies': 0, 'ignored': [], 'unrecognized': []}] * len(texts)
    on, off = run([]), run(['S298', 'S299'])
    a = on[0]
    for c in a['credits']:
        print('A)', c)
    print('A) ignored:', a['ignored'], '| not recognized:', a['unrecognized'])
    want = [['Pete Callard', 'Acoustic Guitar', '1,2,3,18,19,20'], ['Pete Callard', 'Electric Guitar', '18,19'], ['Hari-Om', 'Vocals', '9,10,14,15'], ['Chris Barker', 'Bass', '3,7,16'],
            ['Raja Ram', 'Flute', '7,13,15,17,19'], ['Raja Ram', 'Vocals', '2,7,8,11,12,13,19'], ['Simon Posford', 'Live Drums', '1,2,7,8,18,19'], ['Simon Posford', 'Bass Guitar', '4,9'],
            ['Simon Posford', 'Drum Programming', 'all'], ['Simon Posford', 'Computers', 'all'], ['Simon Posford', 'Synths', 'all'], ['Simon Posford', 'Keyboards', 'all'],
            ['Simon Posford', 'Production', 'all']]
    ok_a = a['credits'] == want and not a['unrecognized'] and 'heading' in a['ignored']
    print('B)', on[1]['credits'], on[2])
    ok_b = on[1]['credits'] == [['Jean-Luc Ponty', 'violin', 'all']] and not on[2]['credits']
    c = on[3]
    print('C)', len(c['credits']), c['companies'], c['unrecognized'], sorted(set(c['ignored'])), len(c['ignored']), '|', on[4])
    ok_c = not c['credits'] and not c['companies'] and not c['unrecognized'] and c['ignored'].count('shop') >= 20 and 'shop' not in on[4]['ignored']
    print('D)', len(off[0]['credits']), off[0]['ignored'], len(off[3]['unrecognized']))
    ok_d = not off[0]['credits'] and len(off[3]['unrecognized']) >= 15
    results = [ok_a, ok_b, ok_c, ok_d]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_storagedoc3171():
    """Credits Importer 3.171.0 (F-STORAGEDOC): the README's table of the storage keys is the one written from the code.
    A) `tools/storage_keys.py --check` finds no difference.
    B) The reader finds the keys however they are written: a literal, a constant, a key per release, the store named or not; a key of
       TOPIC_KEYS has its tab.
    C) A key the code gets and the README lacks is found (the check on a script with one more key says so)."""
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
    import storage_keys as K
    a = K.check()
    print('A)', a or 'OK')
    keys = K.read_keys()
    b = [keys.get('dci-lang'), keys.get('dci-chrome'), keys.get('dci-log:<release>'), keys.get('dci-autostart')]
    print('B)', len(keys), b)
    okb = (len(keys) > 140 and b[0] and b[0]['topic'] == 'general' and b[1] == {'store': {'localStorage'}, 'const': 'CHROME_KEY', 'topic': 'appearance'}
           and b[2] and b[2]['const'] == 'LOG_KEY' and b[3] and b[3]['store'] == {'sessionStorage'})
    src = open(K.SCRIPT, encoding='utf-8').read() + "\n  readJson('localStorage', 'dci-not-in-the-readme', 1);\n"
    more = K.read_keys(src)
    readme = open(K.readme_path(), encoding='utf-8').read()
    c = ['dci-not-in-the-readme' in more, '`dci-not-in-the-readme`' in readme, len(more) - len(keys)]
    print('C)', c)
    results = [not a, bool(okb), c == [True, False, 1]]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
