#!/usr/bin/env python3
"""The relationship types of MusicBrainz with their link phrases, for the tests (Credits Importer 3.38.10, collected item 177).

    python3 tools/mb_link_types.py <checkout of metabrainz/musicbrainz-server> [out.json]

Reads two files of the server's repository (a sparse checkout of just these is enough):
  - po/relationships.pot: every relationship type's name, link phrase, reverse and long link phrase as MusicBrainz has them
    now (the strings the site translates; each one names the ids of the types that use it);
  - t/sql/initial.sql: the types of the server's test database – id, parent, the two entity types, deprecated –; types added
    later are not there: they keep their phrases, their entity types stay empty.
Writes smoke/mb_link_types.json (default): { "source": {...}, "types": { id: {...} }, "attributes": { id: name } }.

[3.100.0] Types added after the test database have no entity types there: those the importer uses get them from ADDED_LATER
(as musicbrainz.org/relationships/<pair> lists them and as their descriptions name them), marked "later": true.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sql_values(line):
    """The values of one "INSERT INTO x VALUES (...);" line (strings with '' inside, NULL, numbers, true/false)."""
    body = line[line.index('(') + 1:line.rindex(')')]
    out, i, n = [], 0, len(body)
    while i < n:
        c = body[i]
        if c in ' ,':
            i += 1
            continue
        if c == "'":
            j, buf = i + 1, []
            while j < n:
                if body[j] == "'" and j + 1 < n and body[j + 1] == "'":
                    buf.append("'")
                    j += 2
                elif body[j] == "'":
                    break
                else:
                    buf.append(body[j])
                    j += 1
            out.append(''.join(buf))
            i = j + 1
        else:
            j = i
            while j < n and body[j] != ',':
                j += 1
            tok = body[i:j].strip()
            out.append(None if tok == 'NULL' else True if tok == 'true' else False if tok == 'false' else int(tok) if re.fullmatch(r'-?\d+', tok) else tok)
            i = j
    return out


def pot_entries(text):
    """(references, msgid) of each entry of a .pot file."""
    for block in text.split('\n\n'):
        refs = ' '.join(l[3:] for l in block.split('\n') if l.startswith('#: '))
        m = re.search(r'^msgid ((?:"(?:[^"\\]|\\.)*"\s*)+)', block, re.M)
        if not refs or not m:
            continue
        msgid = ''.join(json.loads(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"', m.group(1)))
        yield refs.split(), msgid


# [3.100.0] types added after the test database: id → (entity0, entity1, parent) – label–release (musicbrainz.org/relationships/
# label-release: misc → art direction, artwork → design → graphic design, illustration; photography; contracted tasks → produced
# for), artist–release (artwork, design, illustration, translator), and the others their descriptions name
ADDED_LATER = {
    1170: ('label', 'release', None), 1171: ('label', 'release', 1170), 1172: ('label', 'release', 1171), 1173: ('label', 'release', 1170),
    1174: ('label', 'release', None), 1175: ('label', 'release', None), 951: ('label', 'release', None), 950: ('label', 'recording', None),
    993: ('artist', 'release', None), 928: ('artist', 'release', 993), 927: ('artist', 'release', 993), 871: ('artist', 'release', 54),
    872: ('artist', 'work', 167), 1231: ('artist', 'event', None), 1241: ('artist', 'recording', None), 1303: ('event', 'label', None),
}


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'smoke', 'mb_link_types.json')
    types, attrs = {}, {}
    for line in open(os.path.join(src, 't', 'sql', 'initial.sql'), encoding='utf-8'):
        if line.startswith('INSERT INTO link_type VALUES'):
            v = sql_values(line)
            types[v[0]] = {'id': v[0], 'parent': v[1], 'gid': v[3], 'type0': v[4], 'type1': v[5], 'name': v[6], 'deprecated': bool(v[12])}
        elif line.startswith('INSERT INTO link_attribute_type VALUES'):
            v = sql_values(line)
            attrs[v[0]] = {'id': v[0], 'parent': v[1], 'root': v[2], 'name': v[5]}
    pot = open(os.path.join(src, 'po', 'relationships.pot'), encoding='utf-8').read()
    for refs, msgid in pot_entries(pot):
        for ref in refs:
            m = re.fullmatch(r'DB:(link_type|link_attribute_type)/(\w+):(\d+)', ref)
            if not m:
                continue
            table, field, i = m.group(1), m.group(2), int(m.group(3))
            if table == 'link_type' and field in ('name', 'link_phrase', 'reverse_link_phrase', 'long_link_phrase'):
                types.setdefault(i, {'id': i, 'parent': None, 'gid': '', 'type0': '', 'type1': '', 'deprecated': False})[field] = msgid
            elif table == 'link_attribute_type' and field == 'name':
                attrs.setdefault(i, {'id': i, 'parent': None, 'root': None})['name'] = msgid
    for i, (t0, t1, parent) in ADDED_LATER.items():
        t = types.get(i)
        if t and not t['type0']:
            t.update({'type0': t0, 'type1': t1, 'parent': parent, 'later': True})
    try:
        commit = subprocess.run(['git', '-C', src, 'log', '-1', '--format=%H %cs'], capture_output=True, text=True).stdout.split()
    except OSError:
        commit = []
    doc = {'source': {'repository': 'metabrainz/musicbrainz-server', 'commit': commit[0] if commit else '', 'date': commit[1] if len(commit) > 1 else '',
                      'files': ['po/relationships.pot', 't/sql/initial.sql']},
           'types': {str(k): types[k] for k in sorted(types)}, 'attributes': {str(k): attrs[k] for k in sorted(attrs)}}
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=0, sort_keys=True)
        f.write('\n')
    typed = sum(1 for t in types.values() if t['type0'])
    later = sum(1 for t in types.values() if t.get('later'))
    print(f'{len(types)} relationship types ({typed} with their entity types, {later} of them added later), {len(attrs)} attributes → {out}')


if __name__ == '__main__':
    main()
