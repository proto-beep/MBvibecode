#!/usr/bin/env python3
"""The checks of the review runs that a program can do (Credits Importer 3.160.0), for whoever reviews the script from time to time.

    python3 tools/review_checks.py [types] [instruments] [overlaps] [purity] [sizes] [docs] [privacy] [rulesoff]     (none: all)

Each check prints what it found and ends with "OK" or "FINDINGS: n"; the last line is "Review checks: OK" or
"Review checks: FINDINGS in …" (exit code 0 / 1). A finding is something to look at, not always a fault – the notes say which.

  types        every relationship type of the mapping exists in MusicBrainz for its entity pair and level and is not deprecated
               (smoke/mb_link_types.json – write it anew first: tools/mb_link_types.py)
  instruments  every instrument an alias, an abbreviation or a question leads to is an instrument (or vocal) MusicBrainz has
               (needs the list of the data branch: `git show origin/stats:stats/mb-vibecode-credits-importer-instruments.json > f`,
               then INSTRUMENTS=f)
  overlaps     words two role rules match with a different result; the date hints on words that only contain a hint
  purity       the source adapters and the text recognition use neither the dashboard's state (S.) nor the page nor translations
  sizes        the size of the largest functions and of the state – to see a trend
  docs         the versions agree; storage keys and rule ids of the README exist; README.md names the newest milestones
  privacy      no personal data in the files and in the authors of the commits (the owner's name and addresses: PRIVATE="a|b")
  rulesoff     which rules the tests switch off, and how often
"""
import collections
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'mb-vibecode-credits-importer.user.js')
MAPPING = os.path.join(ROOT, 'mb-vibecode-credits-importer-mapping.json')
read = lambda p: open(p, encoding='utf-8').read()  # noqa: E731


def section(src, start, end):
    """The lines between two headings "// N. Title" of the script."""
    a = src.index(start)
    b = src.index(end, a)
    return src[a:b]


def check_types():
    m = json.loads(read(MAPPING))
    lt = json.loads(read(os.path.join(ROOT, 'smoke', 'mb_link_types.json')))
    print('  relationship types as of', lt.get('source', {}).get('date'))
    pairs = collections.defaultdict(set)
    dead = collections.defaultdict(bool)
    for t in lt['types'].values():
        if t.get('deprecated'):
            dead[t['name'].lower()] = True
            continue
        pairs[t['name'].lower()].add(tuple(sorted([t.get('type0') or '?', t.get('type1') or '?'])))
    has = lambda name, a, b: tuple(sorted([a, b])) in pairs[name.lower()] or any('?' in x for x in pairs[name.lower()])  # noqa: E731
    found = []
    todo = [(r['id'], 'artist', r.get('types', []), r.get('level', 'recording')) for r in m['ROLE_RULE_DATA']]
    for _re, c in m['COMPANY_ROLES']:
        for ent in ('label', 'artist', 'place', 'area'):
            if isinstance(c.get(ent), list):
                todo.append((c['id'], ent, c[ent], c.get('level', 'release')))
    for rid, ent, types, level in todo:
        real = [t for t in types if t not in ('misc', 'miscellaneous support', '')]
        if real and not any(has(t, ent, level) for t in real):
            found.append(f'{rid}: none of {real} exists for {ent}–{level}' + (' (deprecated)' if all(dead[t.lower()] for t in real) else ''))
    return found


def check_instruments():
    path = os.environ.get('INSTRUMENTS')
    if not path or not os.path.exists(path):
        print('  skipped: INSTRUMENTS=<file of the data branch> not given')
        return []
    m = json.loads(read(MAPPING))
    inst = {n.lower() for _g, n in json.loads(read(path))['instruments']}
    attrs = {a['name'].lower() for a in json.loads(read(os.path.join(ROOT, 'smoke', 'mb_link_types.json')))['attributes'].values()}
    ok = lambda v: v.lower() in inst or v.lower() in attrs or v.lower() == 'vocals'  # noqa: E731
    found = []
    for k, v in m['INSTRUMENT_ALIASES'].items():
        if not any(ok(x) for x in v):
            found.append(f'alias "{k}" → {v}: none is an instrument of MusicBrainz')
    for k, v in m['INSTRUMENT_ABBR'].items():
        for x in v:
            if not ok(x) and x.lower() not in {a.lower() for a in m['INSTRUMENT_ALIASES']} and not ok(x.rstrip('s')):
                found.append(f'abbreviation "{k}" → "{x}": no instrument of MusicBrainz and no alias')
    for q in m['QUESTION_RULES']:
        for o in q['options']:
            if not ok(o):
                found.append(f'{q["id"]}: option "{o}" is no instrument of MusicBrainz')
    return found


def check_overlaps():
    m = json.loads(read(MAPPING))
    found = []
    comp = []
    for r in m['ROLE_RULE_DATA']:
        if r.get('re'):
            try:
                comp.append((r, re.compile(r['re']['$re'], re.I if 'i' in r['re'].get('$flags', '') else 0)))
            except re.error:
                pass
    vocab = set()
    for r, _c in comp:
        mm = re.match(r'^\^\((.*)\)\$$', r['re']['$re'])
        if mm:
            vocab |= {a for a in mm.group(1).split('|') if not re.search(r'[\\\[\]()*+?{}.]', a)}
    for w in sorted(vocab):
        hits = [r for r, c in comp if c.search(w)]
        simple = [r for r in hits if r.get('kind') == 'simple']
        if len(simple) >= 2 and (simple[0].get('types'), simple[0].get('level')) != (simple[1].get('types'), simple[1].get('level')):
            found.append(f'"{w}": {simple[0]["id"]} {simple[0].get("types")} and {simple[1]["id"]} {simple[1].get("types")} – the first wins')
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
    walk(m)
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        found.append(f'the id {i} is used twice in the mapping file')
    node = ("global.localStorage={getItem:()=>null,setItem(){},removeItem(){},key:()=>null,length:0};const m=require(process.argv[1]);"
            "console.log(JSON.stringify(JSON.parse(process.argv[2]).map(([t,h])=>[t,h,(m.findDates(t,{})[0]||{}).hint])))")
    want = [['Remastered 2015', 'remastering'], ['Premastered 2001', 'mastering'], ['Grandmaster Flash, 1982', ''], ['Piano Concerto No. 2 (1901)', ''],
            ['Konzertmeister: X, 1999', ''], ['Recorded 1999', 'performance'], ['Mixed 2001', 'mix'], ['Unmixed 2001', ''], ['Unrecorded 1999', '']]
    js = subprocess.run(['node', '-e', node, SCRIPT, json.dumps(want)], capture_output=True, text=True)
    if js.returncode:
        found.append('the date hints could not be run in Node: ' + js.stderr[-200:])
    else:
        for t, h, got in json.loads(js.stdout):
            if (got or '') != h:
                found.append(f'date hint of "{t}": {got!r}, expected {h!r}')
    return found


def check_purity():
    src = read(SCRIPT)
    part = section(src, '// 3. Sources: an adapter turns a source', '// 3b. Dates, searches and forms for MusicBrainz')
    code = '\n'.join(l for l in part.split('\n') if not re.match(r'^\s*(//|\*|/\*)', l))
    found = []
    for what, rx in (('the dashboard\'s state (S.)', r'(?<![\w.$])S\.[a-zA-Z]'), ('the page (document, querySelector)', r'\bdocument\.|querySelector'),
                     ('localStorage', r'\blocalStorage\b')):
        n = len(re.findall(rx, code))
        if n:
            found.append(f'section 3 (sources, text recognition) uses {what}: {n} places')
    a = src.index('    function parse(text, ctx0) {')
    b = src.index('    function toRelease(input, ctx) {', a)
    by_source = len(re.findall(r"\b(?:source|src)\s*===\s*(?:BANDCAMP|DISCOGS|YOUTUBE|WIKIPEDIA)|ctx0?\.source\b", src[a:b]))
    if by_source:
        found.append(f'TEXT.parse branches by source: {by_source} places')
    return found


def check_sizes():
    src = read(SCRIPT)
    lines = src.split('\n')
    a = src[:src.index('    function parse(text, ctx0) {')].count('\n')
    b = src[:src.index('    function toRelease(input, ctx) {', src.index('    function parse(text, ctx0) {'))].count('\n')
    out = [('TEXT.parse', b - a)]
    for name in ('computePlan', 'renderGroupsNow', 'settingsHtml', 'loadRelease', 'applyPlan'):
        mm = re.search(rf'^  (?:async )?function {name}\b', src, re.M)
        if not mm:
            continue
        start = src[:mm.start()].count('\n')
        end = next((k for k in range(start + 1, len(lines)) if lines[k] == '  }'), start)
        out.append((name, end - start))
    fields = len(set(re.findall(r'(?<![\w.$])S\.([a-zA-Z_]\w*)', src)))
    asked = len(set(re.findall(r"ruleOn\('([A-Z]\d{3})'\)", src)))
    print(f'  lines of the script: {len(lines)}; fields of the state S: {fields}; rules asked with ruleOn(): {asked}')
    for n, k in out:
        print(f'  {n}: {k} lines')
    return []


def check_docs():
    src = read(SCRIPT)
    found = []
    v = re.search(r'@version\s+(\S+)', src).group(1)
    readme = glob.glob(os.path.join(ROOT, 'mb-vibecode-credits-importer-v*-README.md'))
    vers = {'mapping file': json.loads(read(MAPPING)).get('version'),
            'languages file': json.loads(read(os.path.join(ROOT, 'mb-vibecode-credits-importer-languages.json'))).get('version'),
            'README name': (re.search(r'-v([\d.]+)-README', readme[0]) or [None, None])[1] if readme else None,
            'CHANGELOG': (re.search(r'^### Import ([\d.]+)', read(os.path.join(ROOT, 'mb-vibecode-credits-importer-CHANGELOG.md')), re.M) or [None, None])[1],
            'CODE-CHANGES': (re.search(r'^## Import ([\d.]+)', read(os.path.join(ROOT, 'mb-vibecode-credits-importer-CODE-CHANGES.md')), re.M) or [None, None])[1]}
    for k, x in vers.items():
        if x != v:
            found.append(f'version of the {k}: {x}, the script: {v}')
    if readme:
        rd = read(readme[0])
        keys = set(re.findall(r"(?:readJson|writeJson|getItem|setItem|removeItem)\([^)]*?'(dci-[a-z0-9-]+)", src)) | set(re.findall(r"const [A-Z_]+_KEY = '(dci-[a-z0-9-]+)'", src))
        named = set(re.findall(r'`(dci-[a-z0-9-]+)', rd))
        missing = sorted(keys - named)
        if missing:
            found.append(f'{len(missing)} storage keys of the code the README does not name: {", ".join(missing[:12])}{" …" if len(missing) > 12 else ""}')
        mp = read(MAPPING)
        unknown = sorted(i for i in set(re.findall(r'\b([SDRWQCT]\d{3})\b', rd)) if not re.search(r"['\"]" + i + r"['\"]", src) and f'"{i}"' not in mp and not i.endswith('901'))
        if unknown:
            found.append(f'rule ids of the README that do not exist: {", ".join(unknown)}')
    short = os.path.join(ROOT, 'README.md')
    if os.path.exists(short):
        newest = re.findall(r"\{ v: '(\d+\.\d+)\.\d+',", src[src.index('const MILESTONES = ['):])[:5]
        shown = re.findall(r'^\| (\d+\.\d+) \|', read(short), re.M)[:5]
        if newest != shown:
            found.append(f'README.md "What\'s new" names {shown}, the newest milestones are {newest}')
    return found


def check_privacy():
    found = []
    words = [w for w in os.environ.get('PRIVATE', '').split('|') if w]
    if not words:
        print('  PRIVATE="name|address" not given: only the authors of the commits are listed')
    else:
        rx = re.compile('|'.join(re.escape(w) for w in words), re.I)
        for p in glob.glob(os.path.join(ROOT, '**', '*'), recursive=True):
            if os.path.isfile(p) and '.git' + os.sep not in p and not p.endswith(('.png', '.pyc')):
                try:
                    n = len(rx.findall(read(p)))
                except UnicodeDecodeError:
                    continue
                if n:
                    found.append(f'{os.path.relpath(p, ROOT)}: {n} places')
        log = subprocess.run(['git', '-C', ROOT, 'log', '--all', '--format=%B'], capture_output=True, text=True).stdout
        if rx.search(log):
            found.append('a commit message names private data')
    who = subprocess.run(['git', '-C', ROOT, 'log', '--all', '--format=%ae|%ce'], capture_output=True, text=True).stdout.split()
    hosts = collections.Counter(x.split('@')[-1] for pair in who for x in pair.split('|') if '@' in x)
    print('  hosts of the addresses of authors and committers:', dict(hosts))
    private = {h: n for h, n in hosts.items() if not h.endswith(('noreply.github.com', 'github.com', 'anthropic.com'))}
    if private:
        found.append(f'commits with an address that is not a no-reply address: {private} (GitHub → Settings → Emails → "Keep my email addresses private")')
    return found


def check_rulesoff():
    c = collections.Counter()
    for f in glob.glob(os.path.join(ROOT, 'smoke', '*.py')):
        for m in re.finditer(r"dci-rules-off'?,\s*JSON\.stringify\((\[[^\]]*\])", read(f)):
            for i in re.findall(r"'(\+?[A-Z]\d{3})'", m.group(1)):
                c[i] += 1
    default_off = set(json.loads(read(MAPPING))['DEFAULT_OFF_RULES']['$set'])
    print('  rules the tests switch off (times):', ', '.join(f'{i} {n}' for i, n in c.most_common(12)))
    return [f'{i} is on by default and switched off in {n} places of the tests – what it does is tested less than what it replaced'
            for i, n in c.most_common() if n >= 5 and i not in default_off and not i.startswith('+')]


CHECKS = {'types': check_types, 'instruments': check_instruments, 'overlaps': check_overlaps, 'purity': check_purity, 'sizes': check_sizes,
          'docs': check_docs, 'privacy': check_privacy, 'rulesoff': check_rulesoff}


def main():
    want = [a for a in sys.argv[1:] if a in CHECKS] or list(CHECKS)
    bad = []
    for name in want:
        print(f'== {name}')
        found = CHECKS[name]()
        for f in found:
            print('  -', f)
        print('  ' + ('OK' if not found else f'FINDINGS: {len(found)}'))
        if found:
            bad.append(name)
    print('Review checks: ' + ('OK' if not bad else 'FINDINGS in ' + ', '.join(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
