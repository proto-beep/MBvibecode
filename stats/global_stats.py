#!/usr/bin/env python3
"""Global statistics of MB x Vibecode: Credits Importer from MusicBrainz's edit dump (alpha, collected item Z-GST).

MetaBrainz publishes the full export twice a week; its file mbdump-edit.tar.bz2 holds the tables edit, edit_data, edit_note …
(PostgreSQL COPY text: one row a line, tab-separated, \\N for NULL). This script reads that archive as a stream – nothing is
written to disk – and counts the edits whose editor wrote the script's edit note on them ("Script: MB x Vibecode: Credits
Importer v…", before 3.1.0 "MB x Vibecode: Import Discogs credits").

Only numbers leave it: no editor, no edit, no release, no URL. The number of different editors is a count.

    curl -fsSL "$BASE/$DUMP/mbdump-edit.tar.bz2" | lbzip2 -dc | python3 stats/global_stats.py --dump "$DUMP"
    python3 stats/global_stats.py --input some.tar.bz2      # a file (tests)

The tables come in the order of the archive: edit (kept for the edits from --since on), edit_data (the relationship type of those
edits), edit_note (the notes of the script) – so one pass is enough. An archive without those tables, or one that ends before its
last table (vote), is an error: nothing is written.

[Credits Importer 3.55.0, Z-AGS] Also from the edit dump: "credited as" of the relationships added by the script (credits). With
--facts the facts the core pass needs are written to a file of the run (not committed): the artists of the added relationships with
the year of their dates, the attributes (type id, credited), the releases and recordings of the script's edits (edit_release,
edit_recording). The core pass (--core, once a week, MusicBrainz's mbdump.tar.bz2 as a stream) looks those up in the tables artist,
area, iso_3166_1, artist_type, gender, link_attribute_type, medium, recording, release, release_group (and its types), language and
script and adds the section "core" to the result (--merge): numbers only, as everything here.

    curl … mbdump.tar.bz2 | lbzip2 -dc | python3 stats/global_stats.py --core --facts facts.json --merge global.json --dump "$DUMP"
"""
import argparse
import bz2
import datetime as dt
import json
import os
import re
import sys
import tarfile
from collections import Counter, defaultdict

SCRIPT = 'MB x Vibecode: Credits Importer'
NAMES = ('MB x Vibecode: Credits Importer', 'MB x Vibecode: Import Discogs credits')
OUT_NAME = 'mb-vibecode-credits-importer-global.json'
# (MusicBrainz's lib/MusicBrainz/Server/Constants.pm)
EDIT_TYPES = {90: 'Add relationship', 91: 'Edit relationship', 92: 'Remove relationship', 99: 'Reorder relationships', 41: 'Add work',
              42: 'Edit work', 1: 'Add artist', 2: 'Edit artist', 10: 'Add label', 61: 'Add place', 71: 'Add standalone recording',
              72: 'Edit recording', 32: 'Edit release', 46: 'Add work alias', 6: 'Add artist alias'}
STATUS = {1: 'open', 2: 'applied', 3: 'failed vote', 4: 'failed dependency', 5: 'error', 6: 'failed prerequisite', 7: 'no votes', 9: 'deleted'}
REL_TYPES = (90, 91, 92)
# (the script's own line, at the start of a line – a voter quoting it elsewhere does not count)
NOTE_RE = re.compile(r'^Script: (MB x Vibecode: (?:Credits Importer|Import Discogs credits)) v?(\d+\.\d+(?:\.\d+)?)', re.M)
DONE_RE = re.compile(r'added (\d+) credit relationships? from (.+?) \(([^)]*)\)')
LEVEL_RE = re.compile(r'(\d+) (recording|release group|release|work)')
LINKED_RE = re.compile(r'linked (\d+) works? to recordings')
FILLED_RE = re.compile(r'added role credits to (\d+) existing')
DATES_RE = re.compile(r'added dates to (\d+) existing')
CORE = ('Source: ', 'Also from: ', 'Script: ', 'Done: ')
# MusicBrainz sends a submission in parts (25 edits a request, new works first; live comments up to 30 minutes later): the same note
# of an editor within this time is one submission
SUBMISSION_GAP = 30 * 60
NEEDED = ('edit', 'edit_data', 'edit_note')
# [3.55.0] the entities of a relationship that can carry a "credited as"
CREDITABLE = ('artist', 'label', 'place')
LAST = 'vote'
ESC = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v'}


def unescape(v):
    """A field of COPY text: \\N is NULL; \\n, \\t, \\\\ … as the characters."""
    if v == '\\N':
        return None
    if '\\' not in v:
        return v
    return re.sub(r'\\(.)', lambda m: ESC.get(m.group(1), m.group(1)), v)


def source_kind(url):
    u = (url or '').lower()
    for host, kind in (('discogs.com', 'discogs'), ('bandcamp.com', 'bandcamp'), ('youtube.com', 'youtube'), ('youtu.be', 'youtube')):
        if host in u:
            return kind
    return 'other' if u else None


def kind_from_done(words):
    w = (words or '').lower()
    for k in ('discogs', 'bandcamp', 'youtube'):
        if k in w:
            return k
    if 'cover' in w or 'artwork' in w:
        return 'cover art text'
    if 'text' in w:
        return 'pasted text'
    return 'other'


def as_int(v):
    """A number of the edit data – also one given as digits ("1999"; (review) Moose's Int takes them)."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    return int(v) if isinstance(v, str) and v.strip().lstrip('-').isdigit() else None


def rel_facts(d, lt):
    """[3.55.0] An added relationship from its data, in short (a string – (review) millions of them are kept until the notes are
    read): "artists|year|recordings|attributes|creditable credited" – the ids of its artists and recordings, the year of its begin date,
    its attributes ("type id:credited"), whether it has an artist, a label or a place and whether one of them is credited."""
    types = [d.get('type0') or lt.get('entity0_type'), d.get('type1') or lt.get('entity1_type')]
    ents = [d.get('entity0') if isinstance(d.get('entity0'), dict) else {}, d.get('entity1') if isinstance(d.get('entity1'), dict) else {}]
    ids = lambda kind: ','.join(str(as_int(e.get('id'))) for t, e in zip(types, ents) if t == kind and as_int(e.get('id')) is not None)
    bd = d.get('begin_date') if isinstance(d.get('begin_date'), dict) else {}
    year = as_int(bd.get('year'))
    attrs = []
    for a in d.get('attributes') or []:
        if not isinstance(a, dict):
            continue
        t = a.get('type') if isinstance(a.get('type'), dict) else {}
        if as_int(t.get('id')) is not None:
            attrs.append(f"{as_int(t.get('id'))}:{1 if str(a.get('credited_as') or '').strip() else 0}")
    creditable = any(t in CREDITABLE for t in types)
    credited = any(str(d.get(f'entity{k}_credit') or '').strip() for k, t in enumerate(types) if t in CREDITABLE)
    return f"{ids('artist')}|{'' if year is None else year}|{ids('recording')}|{','.join(attrs)}|{int(creditable)}{int(credited)}"


def facts_of(text):
    """[3.55.0] The parts of rel_facts: (artist ids, year, recording ids, ((type id, credited), …), creditable, credited)."""
    a, y, r, at, fl = text.split('|')
    nums = lambda x: tuple(int(v) for v in x.split(',') if v)
    attrs = tuple((int(t), int(c)) for t, c in (x.split(':') for x in at.split(',') if x))
    return nums(a), int(y) if y else None, nums(r), attrs, fl[0] == '1', fl[1] == '1'


def seconds(ts):
    """A timestamp of the dump ("2026-10-20 10:00:01.123+00") in seconds (UTC)."""
    try:
        t = dt.datetime.fromisoformat(ts.replace(' ', 'T', 1))
        if t.tzinfo is None:
            t = t.replace(tzinfo=dt.timezone.utc)
        return t.timestamp()
    except (ValueError, AttributeError):
        return 0.0


class Stats:
    def __init__(self, since):
        self.since = since
        self.since_b = since.encode()
        # the edits from "since" on, by id (the dump is not in the order of the ids: an edit changed later is further on):
        # editor << 32 | month << 24 | type << 12 | status << 4 | autoedit
        self.edits = {}
        self.months = []
        self.month_ix = {}
        self.rel_ids = set()
        self.ltype = {}  # edit id → relationship type (a name, or "#id" until its name is known)
        self.lt_names = {}  # link type id → name (from the edits that carry it)
        self.rows = Counter()
        self.notes = {}  # edit id → (note id, note text, post time) – the earliest of the edit's own editor
        # [3.55.0] an added relationship (90), in short (rel_facts); the releases of the script's edits (edit_release, edit → {release})
        self.facts = {}
        self.edit_rel = defaultdict(set)
        self.sub_releases = set()

    def edit_row(self, raw):
        # id, editor, type, status, autoedit, open_time, …
        f = raw.split(b'\t', 6)
        if len(f) < 6 or f[5][:10] < self.since_b or f[5] == b'\\N':
            return
        i = int(f[0])
        m = f[5][:7].decode()
        if m not in self.month_ix:
            self.month_ix[m] = len(self.months)
            self.months.append(m)
        t = int(f[2])
        self.edits[i] = int(f[1]) << 32 | self.month_ix[m] << 24 | t << 12 | int(f[3]) << 4 | (1 if f[4] not in (b'0', b'\\N') else 0)
        if t in REL_TYPES:
            self.rel_ids.add(i)

    def info(self, edit_id):
        """The editor, type, status, autoedit and month of an edit from "since" on (None: before it)."""
        v = self.edits.get(edit_id)
        if v is None:
            return None
        return v >> 32, (v >> 12) & 0xFFF, (v >> 4) & 0xFF, v & 1, self.months[(v >> 24) & 0xFF]

    def data_row(self, raw):
        # (only the relationship edits are read: the id first, the rest only for them)
        tab = raw.find(b'\t')
        if tab < 1:
            return
        i = int(raw[:tab])
        if i not in self.rel_ids:
            return
        try:
            d = json.loads(unescape(raw[tab + 1:].decode('utf-8', 'replace').rstrip('\n')))
        except (ValueError, TypeError):
            return
        if not isinstance(d, dict):
            return
        g = lambda o, *ks: next((o.get(k) for k in ks if isinstance(o, dict) and isinstance(o.get(k), dict)), None)
        # add (90): link_type {id, name}; edit (91): new.link_type when the type changed, else link.link_type; remove (92):
        # relationship.link.type {id, …} without a name (lib/MusicBrainz/Server/Edit/Relationship/*.pm)
        lt = g(d.get('new') if isinstance(d.get('new'), dict) else {}, 'link_type') or g(d, 'link_type') \
            or g(g(d, 'link') or {}, 'link_type') or g(g(g(d, 'relationship') or {}, 'link') or {}, 'type')
        if not lt:
            return
        name, lid = lt.get('name'), lt.get('id')
        if name and lid is not None:
            self.lt_names[lid] = name
        if name:
            self.ltype[i] = name
        elif lid is not None:
            self.ltype[i] = f'#{lid}'
        # [3.55.0] what an added relationship is made of (only 90: its entities, date, attributes and credits are in its data)
        if (self.edits.get(i, 0) >> 12) & 0xFFF == 90:
            self.facts[i] = rel_facts(d, lt)

    def link_row(self, raw):
        # [3.55.0] edit_release (edit, release) – after edit_note: only the script's edits
        f = raw.split(b'\t', 2)
        if len(f) >= 2 and f[0].isdigit() and int(f[0]) in self.notes and f[1].strip().isdigit():
            self.edit_rel[int(f[0])].add(int(f[1]))

    def note_row(self, raw):
        # id, editor, edit, text, post_time
        if b'MB x Vibecode' not in raw:
            return
        f = raw.decode('utf-8', 'replace').rstrip('\n').split('\t')
        if len(f) < 5:
            return
        text = unescape(f[3]) or ''
        if not NOTE_RE.search(text):
            return
        nid, editor, edit_id = int(f[0]), int(f[1]), int(f[2])
        inf = self.info(edit_id)
        if inf is None:
            self.rows['notes on edits before "since"'] += 1
            return
        # (only a note of the edit's own editor: a voter's comment is no edit of the script)
        if inf[0] != editor:
            return
        old = self.notes.get(edit_id)
        if old is None or nid < old[0]:
            self.notes[edit_id] = (nid, text, f[4])

    def result(self, dump):
        out = {'script': SCRIPT, 'names': list(NAMES), 'dump': dump, 'generated': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'since': self.since, 'privacy': 'numbers only: no editors, edits, releases or URLs; "editors" is how many different ones'}
        by_month = defaultdict(lambda: {'edits': 0, 'submissions': 0, 'editors': set()})
        by_version = defaultdict(lambda: {'edits': 0, 'submissions': 0})
        types, status, ltypes, auto = Counter(), Counter(), Counter(), Counter()
        editors = set()
        groups = defaultdict(list)  # (editor, the script's lines) → [(time, month, version, text)]
        for edit_id, (nid, text, post) in self.notes.items():
            editor, t, stt, au, mon = self.info(edit_id)
            ver = NOTE_RE.search(text).group(2)
            editors.add(editor)
            by_version[ver]['edits'] += 1
            by_month[mon]['edits'] += 1
            by_month[mon]['editors'].add(editor)
            types[f'{t} {EDIT_TYPES.get(t, "other")}'] += 1
            status[STATUS.get(stt, str(stt))] += 1
            auto['auto-edit' if au else 'voted'] += 1
            if edit_id in self.ltype:
                lt = self.ltype[edit_id]
                ltypes[self.lt_names.get(int(lt[1:]), lt) if lt.startswith('#') else lt] += 1
            core = '\n'.join(line.strip() for line in text.split('\n') if line.strip().startswith(CORE))
            groups[(editor, core)].append((seconds(post), mon, ver, text, edit_id))
        # a submission: the same note of one editor, its parts at most SUBMISSION_GAP apart (its "Done:" counted once)
        subs = []
        sub_edits = []
        for parts in groups.values():
            parts.sort(key=lambda p: p[0])
            last = None
            for p in parts:
                if last is None or p[0] - last > SUBMISSION_GAP:
                    subs.append(p[:4])
                    sub_edits.append([])
                sub_edits[-1].append(p[4])
                last = p[0]
        # [3.55.0] (review) the release of a submission: the one most of its edits are linked with (MusicBrainz links a relationship of a
        # recording or a work also with every release of it – not those)
        for eds in sub_edits:
            c = Counter(r for e in eds for r in self.edit_rel.get(e, ()))
            if c:
                self.sub_releases.add(c.most_common(1)[0][0])
        sources, supps, done, levels = Counter(), Counter(), Counter(), Counter()
        for _, mon, ver, text in subs:
            by_version[ver]['submissions'] += 1
            by_month[mon]['submissions'] += 1
            src = None
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('Source: '):
                    src = source_kind(line[8:])
                elif line.startswith('Also from: '):
                    supps[source_kind(line[11:]) or 'other'] += 1
            m = DONE_RE.search(text)
            if m:
                done['credit relationships'] += int(m.group(1))
                for n, lv in LEVEL_RE.findall(m.group(3)):
                    levels[lv] += int(n)
                src = src or kind_from_done(m.group(2))
            for rx, what in ((LINKED_RE, 'works linked'), (FILLED_RE, 'role credits added'), (DATES_RE, 'dates added')):
                mm = rx.search(text)
                if mm:
                    done[what] += int(mm.group(1))
            sources[src or 'unknown'] += 1
        out['totals'] = {'edits': len(self.notes), 'submissions': len(subs), 'editors': len(editors)}
        out['by_month'] = {m: {'edits': v['edits'], 'submissions': v['submissions'], 'editors': len(v['editors'])} for m, v in sorted(by_month.items())}
        out['by_version'] = dict(sorted(by_version.items(), key=lambda kv: [int(x) for x in kv[0].split('.')]))
        out['by_edit_type'] = dict(types.most_common())
        out['by_status'] = dict(status.most_common())
        out['auto_edits'] = dict(auto.most_common())
        out['by_relationship_type'] = dict(ltypes.most_common(60))
        out['by_source'] = dict(sources.most_common())
        out['supplements'] = dict(supps.most_common())
        out['done'] = dict(done.most_common())
        out['done_by_level'] = dict(levels.most_common())
        # [3.55.0, Z-ALI] "credited as" of the relationships the script added with an artist, a label or a place
        facts = self.script_facts()
        out['credits'] = {'credited_as': {'n': sum(1 for f in facts if f[4] and f[5]), 'of': sum(1 for f in facts if f[4])}}
        out['rows_read'] = dict(self.rows)
        return out

    def script_facts(self):
        """[3.55.0] The facts of the relationships the script added – (review) open or applied ones (not those that failed or went)."""
        return [facts_of(self.facts[e]) for e in self.notes if e in self.facts and self.info(e)[2] in (1, 2)]

    def facts_out(self):
        """[3.55.0] What the core pass needs (a file of the run, not committed)."""
        facts = self.script_facts()
        return {'artists': [[a, f[1]] for f in facts for a in f[0]], 'attrs': [list(map(list, f[3])) for f in facts if f[3]],
                'releases': sorted(self.sub_releases), 'recordings': sorted({r for f in facts for r in f[2]})}


# --- [3.55.0, Z-AGS] the core pass: MusicBrainz's mbdump.tar.bz2 (once a week) -------------------------------------------------
# (the columns as in MusicBrainz's admin/sql/CreateTables.sql; the tables in the order of the archive – alphabetical)
CORE_TABLES = ('area', 'artist', 'artist_type', 'gender', 'iso_3166_1', 'language', 'link_attribute_type', 'medium', 'recording', 'release',
               'release_group', 'release_group_primary_type', 'release_group_secondary_type', 'release_group_secondary_type_join', 'script')
CORE_NEEDED = ('area', 'artist', 'iso_3166_1', 'medium', 'release', 'release_group')
ROOT_INSTRUMENT, ROOT_VOCAL = 14, 3
AREA_COUNTRY = 1
# (area types of a town: City, Municipality, District)
TOWN_TYPES = (3, 4, 5)
TOP = 40


def median(xs):
    v = sorted(xs)
    if not v:
        return None
    h = len(v) // 2
    return v[h] if len(v) % 2 else (v[h - 1] + v[h]) / 2


def mean(xs):
    return sum(xs) / len(xs) if xs else None


class Core:
    def __init__(self, facts, year):
        self.year = year
        self.art_rels = [(int(a), y) for a, y in facts.get('artists', [])]
        self.want_art = {a for a, _ in self.art_rels}
        self.attrs = facts.get('attrs', [])
        self.want_rel = set(facts.get('releases', []))
        self.want_rec = set(facts.get('recordings', []))
        self.area = {}  # area id → (name, type)
        self.artist = {}  # artist id → [type id, gender id, begin year, end year, ended, area, begin area]
        self.names = {k: {} for k in ('artist_type', 'gender', 'language', 'script', 'release_group_primary_type', 'release_group_secondary_type')}
        self.iso = {}  # area id → ISO 3166-1
        self.root = {}  # link attribute type → its root
        self.media = Counter()  # release → number of media
        self.lengths = {}  # recording → length (ms)
        self.release = {}  # release → (release group, language, script)
        self.rg_type = {}
        self.rg_sec = defaultdict(list)
        self.want_rg = set()
        self.rows = Counter()

    def row(self, table, raw):
        f = raw.rstrip(b'\n').split(b'\t')
        num = lambda x: int(x) if x and x != b'\\N' and x.lstrip(b'-').isdigit() else None
        if table == 'area' and len(f) > 3:
            self.area[int(f[0])] = (unescape(f[2].decode('utf-8', 'replace')), num(f[3]))
        elif table == 'artist' and len(f) > 18:
            i = int(f[0])
            if i in self.want_art:
                self.artist[i] = [num(f[10]), num(f[12]), num(f[4]), num(f[7]), f[16] == b't', num(f[11]), num(f[17])]
        elif table in self.names and len(f) > 1:
            # (language: id, iso_code_2t, iso_code_2b, iso_code_1, name, frequency, iso_code_3; script: id, iso_code, …)
            k = {'language': 6, 'script': 1}.get(table, 1)
            if len(f) > k:
                self.names[table][int(f[0])] = unescape(f[k].decode('utf-8', 'replace')) or ''
        elif table == 'iso_3166_1' and len(f) > 1:
            self.iso[int(f[0])] = f[1].decode()
        elif table == 'link_attribute_type' and len(f) > 2:
            self.root[int(f[0])] = num(f[2])
        elif table == 'medium' and len(f) > 1:
            r = num(f[1])
            if r in self.want_rel:
                self.media[r] += 1
        elif table == 'recording' and len(f) > 4:
            i = int(f[0])
            if i in self.want_rec:
                ln = num(f[4])
                if ln and ln > 0:
                    self.lengths[i] = ln
        elif table == 'release' and len(f) > 8:
            i = int(f[0])
            if i in self.want_rel:
                self.release[i] = (num(f[4]), num(f[7]), num(f[8]))
                self.want_rg.add(num(f[4]))
        # ((review) release comes before release_group: only the release groups of those releases)
        elif table == 'release_group' and len(f) > 4:
            i = int(f[0])
            if i in self.want_rg:
                self.rg_type[i] = num(f[4])
        elif table == 'release_group_secondary_type_join' and len(f) > 1:
            i = int(f[0])
            if i in self.want_rg:
                self.rg_sec[i].append(num(f[1]))

    def result(self):
        top = lambda c, n=TOP: dict(c.most_common(n))
        nm = self.names
        # the artists (each once)
        types, genders, decades, countries, towns, centuries = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
        for t, g, b, e, ended, area, barea in self.artist.values():
            tname = nm['artist_type'].get(t, '')
            types[tname or '-'] += 1
            if g:
                genders[nm['gender'].get(g, str(g))] += 1
            if b and b <= self.year:
                decades[f'{b // 10 * 10}s'] += 1
            c = self.iso.get(area)
            if c:
                countries[c] += 1
            ba = self.area.get(barea)
            if ba and ba[1] in TOWN_TYPES:
                towns[ba[0]] += 1
            if b and b <= self.year:
                to = e or (b if ended else min(self.year, b + 120) if tname == 'Person' else self.year)
                for cc in range(b // 100 * 100, max(b, to) + 1, 100):
                    centuries[str(cc)] += 1
        post = sum(1 for a, y in self.art_rels if y and a in self.artist and self.artist[a][3] and y > self.artist[a][3])
        post_of = sum(1 for a, y in self.art_rels if y and a in self.artist and self.artist[a][3])
        # the releases (each once)
        media, rgp, rgs, langs, scripts = Counter(), Counter(), Counter(), Counter(), Counter()
        for r, (rg, lang, scr) in self.release.items():
            n = self.media.get(r, 0)
            if n:
                media['multi' if n > 1 else 'single'] += 1
            rgp[nm['release_group_primary_type'].get(self.rg_type.get(rg), '') or '-'] += 1
            for x in self.rg_sec.get(rg, []):
                rgs[nm['release_group_secondary_type'].get(x, str(x))] += 1
            langs[nm['language'].get(lang, '') or '-'] += 1
            scripts[nm['script'].get(scr, '') or '-'] += 1
        lens = list(self.lengths.values())
        # role credits: of the relationships with an instrument or vocal attribute, those with one of them credited
        base = cred = 0
        for attrs in self.attrs:
            iv = [c for t, c in attrs if self.root.get(t) in (ROOT_INSTRUMENT, ROOT_VOCAL)]
            if iv:
                base += 1
                cred += 1 if any(iv) else 0
        return {
            'artists': {'n': len(self.artist), 'of': len(self.want_art), 'types': top(types), 'genders': top(genders), 'decades': top(decades),
                        'countries': top(countries), 'towns': top(towns, 20), 'centuries': dict(sorted(centuries.items())), 'posthumous': {'n': post, 'of': post_of}},
            'releases': {'n': len(self.release), 'media': top(media), 'rg_primary': top(rgp), 'rg_secondary': top(rgs), 'languages': top(langs), 'scripts': top(scripts)},
            'lengths': {'recordings': len(lens), 'median_ms': median(lens), 'mean_ms': mean(lens)},
            'role_credits': {'n': cred, 'of': base},
        }


def run_core(stream, facts, dump):
    core = Core(facts, dt.date.today().year)
    seen = []
    with tarfile.open(fileobj=stream, mode='r|') as tar:
        for member in tar:
            table = member.name.rsplit('/', 1)[-1]
            seen.append(table)
            if table not in CORE_TABLES or not member.isfile():
                continue
            n = 0
            for raw in tar.extractfile(member):
                n += 1
                core.row(table, raw)
            core.rows[table] = n
            print(f'{table}: {n} rows', file=sys.stderr, flush=True)
    missing = [t for t in CORE_NEEDED if not core.rows.get(t)]
    if missing:
        raise SystemExit(f'the core archive is not complete: {", ".join(missing)} – nothing written')
    return {'dump': dump, **core.result()}


def run(stream, since, dump):
    st = Stats(since)
    handlers = {'edit': st.edit_row, 'edit_data': st.data_row, 'edit_note': st.note_row,
                'edit_release': st.link_row}
    seen = []
    with tarfile.open(fileobj=stream, mode='r|') as tar:
        for member in tar:
            table = member.name.rsplit('/', 1)[-1]
            seen.append(table)
            h = handlers.get(table)
            if not h or not member.isfile():
                continue
            n = 0
            for raw in tar.extractfile(member):
                n += 1
                h(raw)
            st.rows[table] = n
            print(f'{table}: {n} rows', file=sys.stderr, flush=True)
    # (a dump cut off at a file's border, or of another layout, would give zeros: an error instead)
    missing = [t for t in NEEDED if not st.rows.get(t)]
    if missing or LAST not in seen:
        raise SystemExit(f'the archive is not complete: {", ".join(missing) or "no " + LAST} – nothing written')
    return st.result(dump), st.facts_out()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--input', help='the archive (.tar.bz2 or .tar); default: an uncompressed tar on stdin')
    ap.add_argument('--since', default='2026-09-01', help='edits opened from this day on (the first version: 2026-09-28)')
    ap.add_argument('--dump', default='', help='the name of the dump (its directory, e.g. 20261104-002001)')
    ap.add_argument('--out', default=f'stats/{OUT_NAME}')
    # [3.55.0, Z-AGS]
    ap.add_argument('--facts', help='edit pass: where to write the facts for the core pass; core pass: the facts to read')
    ap.add_argument('--core', action='store_true', help='the core pass: mbdump.tar.bz2 (with --facts and --merge)')
    ap.add_argument('--merge', help='core pass: the result of the edit pass, its section "core" set')
    ap.add_argument('--keep-core', help='a result of before: its section "core" kept in --out (a run without the core pass)')
    a = ap.parse_args()
    opener = (bz2.open if a.input and a.input.endswith('.bz2') else open) if a.input else None
    if a.core:
        facts = json.load(open(a.facts, encoding='utf-8'))
        if a.input:
            with opener(a.input, 'rb') as fh:
                core = run_core(fh, facts, a.dump)
        else:
            core = run_core(sys.stdin.buffer, facts, a.dump)
        res = json.load(open(a.merge, encoding='utf-8'))
        res['core'] = core
        out = a.merge
    else:
        if a.input:
            with opener(a.input, 'rb') as fh:
                res, facts = run(fh, a.since, a.dump)
        else:
            res, facts = run(sys.stdin.buffer, a.since, a.dump)
        if a.facts:
            with open(a.facts, 'w', encoding='utf-8') as fh:
                json.dump(facts, fh)
        if a.keep_core:
            try:
                old = json.load(open(a.keep_core, encoding='utf-8'))
                if isinstance(old, dict) and isinstance(old.get('core'), dict):
                    res['core'] = old['core']
            except (OSError, ValueError):
                pass
        out = a.out
    # ((review) written in full first, then put in place)
    with open(out + '.tmp', 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    os.replace(out + '.tmp', out)
    print(json.dumps(res.get('totals', {})), file=sys.stderr)


if __name__ == '__main__':
    main()
