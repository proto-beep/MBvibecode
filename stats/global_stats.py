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
        self.release_rec_rels = {}  # [3.91.0] release → relationships on its recordings

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
        added_lt = Counter()  # [3.139.0, Z-GSTNEW] the types of the relationships added (90)
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
                name = self.lt_names.get(int(lt[1:]), lt) if lt.startswith('#') else lt
                ltypes[name] += 1
                # ((review) open or applied, as the facts of the core pass)
                if t == 90 and stt in (1, 2):
                    added_lt[name.lower()] += 1
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
        sub_rel = []
        for eds in sub_edits:
            c = Counter(r for e in eds for r in self.edit_rel.get(e, ()))
            top2 = c.most_common(2)
            # [3.91.0] (review) a tie (recordings also on another release): no release for the numbers per release
            sub_rel.append(top2[0][0] if top2 and (len(top2) == 1 or top2[0][1] > top2[1][1]) else None)
            if c:
                self.sub_releases.add(c.most_common(1)[0][0])
        # [3.91.0, Z-SRR] per release (all its submissions): its credit relationships, also by level ("Done:")
        per_rel = defaultdict(Counter)
        sources, supps, done, levels = Counter(), Counter(), Counter(), Counter()
        mix = Counter()  # [3.139.0, Z-GSTNEW] the source of a submission with its supplements ("discogs+bandcamp")
        supplemented = 0
        for k, (_, mon, ver, text) in enumerate(subs):
            by_version[ver]['submissions'] += 1
            by_month[mon]['submissions'] += 1
            src = None
            also = []
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('Source: '):
                    src = source_kind(line[8:])
                elif line.startswith('Also from: '):
                    supps[source_kind(line[11:]) or 'other'] += 1
                    also.append(source_kind(line[11:]) or 'other')
            m = DONE_RE.search(text)
            if m:
                done['credit relationships'] += int(m.group(1))
                for n, lv in LEVEL_RE.findall(m.group(3)):
                    levels[lv] += int(n)
                if sub_rel[k] is not None:
                    per_rel[sub_rel[k]]['all'] += int(m.group(1))
                    for n, lv in LEVEL_RE.findall(m.group(3)):
                        per_rel[sub_rel[k]][lv] += int(n)
                src = src or kind_from_done(m.group(2))
            for rx, what in ((LINKED_RE, 'works linked'), (FILLED_RE, 'role credits added'), (DATES_RE, 'dates added')):
                mm = rx.search(text)
                if mm:
                    done[what] += int(mm.group(1))
            sources[src or 'unknown'] += 1
            # ((review) each supplement once – also one of the same kind as the source ("bandcamp+bandcamp")
            mix['+'.join([src or 'unknown'] + sorted(also))] += 1
            supplemented += 1 if also else 0
        out['totals'] = {'edits': len(self.notes), 'submissions': len(subs), 'editors': len(editors)}
        out['by_month'] = {m: {'edits': v['edits'], 'submissions': v['submissions'], 'editors': len(v['editors'])} for m, v in sorted(by_month.items())}
        out['by_version'] = dict(sorted(by_version.items(), key=lambda kv: [int(x) for x in kv[0].split('.')]))
        out['by_edit_type'] = dict(types.most_common())
        out['by_status'] = dict(status.most_common())
        out['auto_edits'] = dict(auto.most_common())
        out['by_relationship_type'] = dict(ltypes.most_common(60))
        out['by_source'] = dict(sources.most_common())
        out['supplements'] = dict(supps.most_common())
        # [3.139.0, Z-GSTNEW] as the statistics of this browser (3.131.0): submissions supplemented by another source, their sources
        # together, remixes and commissions among the relationships added
        out['supplemented'] = {'n': supplemented, 'of': len(subs)}
        out['source_mix'] = dict(mix.most_common(12))
        out['remixes'] = {'remixer': added_lt['remixer'], 'remix_of': added_lt['remix'], 'commissioned': added_lt['commissioned']}
        out['done'] = dict(done.most_common())
        out['done_by_level'] = dict(levels.most_common())
        # [3.91.0, Z-SRR] the average and the median of the releases (numbers only); the relationships on the recordings of each for the core pass
        vals = list(per_rel.values())
        mm = lambda xs: {'mean': mean(xs), 'median': median(xs)}
        out['per_release'] = {'n': len(vals), 'rels': mm([c['all'] for c in vals]),
                              'by_level': {lv: mm([c[lv] for c in vals]) for lv in ('recording', 'release', 'work', 'release group') if any(c[lv] for c in vals)}}
        self.release_rec_rels = {r: c['recording'] for r, c in per_rel.items()}
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
                'releases': sorted(self.sub_releases), 'recordings': sorted({r for f in facts for r in f[2]}),
                'release_rec_rels': sorted([r, n] for r, n in self.release_rec_rels.items())}


# --- [3.55.0, Z-AGS] the core pass: MusicBrainz's mbdump.tar.bz2 (once a week) -------------------------------------------------
# (the columns as in MusicBrainz's admin/sql/CreateTables.sql; the tables in the order of the archive – alphabetical)
CORE_TABLES = ('area', 'artist', 'artist_type', 'gender', 'iso_3166_1', 'language', 'link_attribute_type', 'medium', 'recording', 'release',
               'release_group', 'release_group_primary_type', 'release_group_secondary_type', 'release_group_secondary_type_join', 'script',
               # [3.61.0, Z-RDU2] the tracks: the whole length of each release (its media's tracks together)
               'track',
               # [3.107.0, Z-ITREE] the instruments and their "type of" relationships (l_instrument_instrument before link in the archive)
               'instrument', 'l_instrument_instrument', 'link')
CORE_NEEDED = ('area', 'artist', 'iso_3166_1', 'medium', 'release', 'release_group')
ROOT_INSTRUMENT, ROOT_VOCAL = 14, 3
AREA_COUNTRY = 1
# (area types of a town: City, Municipality, District)
TOWN_TYPES = (3, 4, 5)
TOP = 40
# [3.107.0, Z-ITREE] MusicBrainz's link type "subtype" between instruments: entity0 has entity1 as a subtype ("soprano saxophone" is a
# "type of" "saxophone"); the file the script reads (the data branch), and how many weeks of changes it keeps
SUBTYPE_LT = 736
ITREE_FORMAT = 'mb-vibecode-instrument-tree'
ITREE_NAME = 'mb-vibecode-credits-importer-instruments.json'
ITREE_CHANGES = 12


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
        # [3.91.0, Z-SRR] the relationships on the recordings of each release; its tracks (not data tracks) as its recordings
        self.rec_rels = {int(r): int(n) for r, n in facts.get('release_rec_rels', [])}
        self.rel_tracks = defaultdict(set)  # release → its recordings (distinct; not data tracks, not a pregap)
        self.area = {}  # area id → (name, type)
        self.artist = {}  # artist id → [type id, gender id, begin year, end year, ended, area, begin area]
        self.names = {k: {} for k in ('artist_type', 'gender', 'language', 'script', 'release_group_primary_type', 'release_group_secondary_type')}
        self.iso = {}  # area id → ISO 3166-1
        self.root = {}  # link attribute type → its root
        self.media = Counter()  # release → number of media
        self.lengths = {}  # recording → length (ms)
        self.medium_rel = {}  # [3.61.0] medium → release (of the releases wanted)
        self.rel_len = {}  # [3.61.0] release → [length of its tracks together (ms), every track with a length]
        self.release = {}  # release → (release group, language, script)
        self.rg_type = {}
        self.rg_sec = defaultdict(list)
        self.want_rg = set()
        self.rows = Counter()
        # [3.107.0, Z-ITREE] instrument id → (gid, name); the relationships between instruments (link, entity0, entity1); their links' types
        self.instr = {}
        self.ii = []
        self.want_link = set()
        self.link_type = {}

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
                self.medium_rel[int(f[0])] = r
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
        # [3.61.0, Z-RDU2] track (id, gid, recording, medium, position, number, name, artist_credit, length, …): after medium
        elif table == 'track' and len(f) > 8:
            r = self.medium_rel.get(num(f[3]))
            # ((review) a data track (is_data_track, f[11]) has no length of music: not counted)
            if r is not None and not (len(f) > 11 and f[11] == b't'):
                if num(f[4]) != 0 and num(f[2]) is not None:
                    self.rel_tracks[r].add(num(f[2]))
                acc = self.rel_len.setdefault(r, [0, True])
                ln = num(f[8])
                if ln and ln > 0:
                    acc[0] += ln
                else:
                    acc[1] = False
        # ((review) release comes before release_group: only the release groups of those releases)
        elif table == 'release_group' and len(f) > 4:
            i = int(f[0])
            if i in self.want_rg:
                self.rg_type[i] = num(f[4])
        elif table == 'release_group_secondary_type_join' and len(f) > 1:
            i = int(f[0])
            if i in self.want_rg:
                self.rg_sec[i].append(num(f[1]))
        # [3.107.0, Z-ITREE] instrument (id, gid, name, type, …); l_instrument_instrument (id, link, entity0, entity1, …); link (id, link_type, …)
        elif table == 'instrument' and len(f) > 2:
            self.instr[int(f[0])] = (f[1].decode('ascii', 'replace'), unescape(f[2].decode('utf-8', 'replace')))
        elif table == 'l_instrument_instrument' and len(f) > 3:
            self.ii.append((num(f[1]), num(f[2]), num(f[3])))
            self.want_link.add(num(f[1]))
        elif table == 'link' and len(f) > 1:
            i = num(f[0])
            if i in self.want_link:
                self.link_type[i] = num(f[1])

    def itree(self, dump, old=None):
        """[3.107.0, Z-ITREE] The instruments with their "type of" relationships – and what changed since the file of before (`old`)."""
        names = sorted(self.instr.values(), key=lambda x: (x[1].lower(), x[0]))
        at = {g: k for k, (g, _n) in enumerate(names)}
        pairs = sorted({(at[self.instr[e0][0]], at[self.instr[e1][0]]) for lk, e0, e1 in self.ii
                        if self.link_type.get(lk) == SUBTYPE_LT and e0 in self.instr and e1 in self.instr and e0 != e1})
        out = {'format': ITREE_FORMAT, 'version': 1, 'dump': dump, 'generated': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'instruments': [[g, n] for g, n in names], 'subtype': [list(x) for x in pairs], 'changes': []}
        changes = []
        if isinstance(old, dict) and old.get('format') == ITREE_FORMAT and isinstance(old.get('instruments'), list):
            changes = [c for c in (old.get('changes') or []) if isinstance(c, dict)]
            def parents(d):
                inst = d.get('instruments') or []
                up = {g: set() for g, _n in inst}
                for a, b in d.get('subtype') or []:
                    if 0 <= a < len(inst) and 0 <= b < len(inst):
                        up[inst[b][0]].add(inst[a][0])
                return up, {g: n for g, n in inst}
            o_up, o_name = parents(old)
            n_up, n_name = parents(out)
            added = sorted(n_name[g] for g in n_up if g not in o_up)
            removed = sorted(o_name[g] for g in o_up if g not in n_up)
            moved = sorted(n_name[g] for g in n_up if g in o_up and n_up[g] != o_up[g])
            renamed = sorted(f'{o_name[g]} → {n_name[g]}' for g in n_up if g in o_name and o_name[g] != n_name[g])
            if added or removed or moved or renamed:
                changes.insert(0, {'dump': dump, 'added': added, 'removed': removed, 'moved': moved, 'renamed': renamed})
        out['changes'] = changes[:ITREE_CHANGES]
        return out

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
        known = [r for r in self.rec_rels if self.rel_tracks.get(r)]
        nrec = {r: len(self.rel_tracks[r]) for r in known}
        # [3.61.0, Z-RDU2] the whole length of the releases whose every track has a length
        rel_lens = [t for t, whole in self.rel_len.values() if whole and t > 0]
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
            'lengths': {'recordings': len(lens), 'median_ms': median(lens), 'mean_ms': mean(lens),
                        'releases': len(rel_lens), 'release_median_ms': median(rel_lens), 'release_mean_ms': mean(rel_lens)},
            'role_credits': {'n': cred, 'of': base},
            # [3.91.0, Z-SRR] per release: its recordings, and the relationships on them per recording (the releases with tracks)
            'per_release': {'n': len(known), 'recordings': {'mean': mean(list(nrec.values())), 'median': median(list(nrec.values()))},
                            'rels_per_recording': {'mean': mean([self.rec_rels[r] / nrec[r] for r in known]),
                                                   'median': median([self.rec_rels[r] / nrec[r] for r in known])}},
        }


def run_core(stream, facts, dump, keep=None):
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
    # [3.61.0, review] the tracks are not needed – without them (or before medium) the whole lengths of the releases are missing: say so
    if not core.rows.get('track'):
        print('warning: no rows of track – the whole lengths of the releases are not counted', file=sys.stderr, flush=True)
    elif core.rows.get('medium') and not core.rel_len:
        print('warning: track gave no lengths (read before medium?) – the whole lengths of the releases are not counted', file=sys.stderr, flush=True)
    if missing:
        raise SystemExit(f'the core archive is not complete: {", ".join(missing)} – nothing written')
    # [3.107.0, Z-ITREE] the instruments' tree for the script (kept by the caller); ((review) no instruments or no "type of" read: not kept)
    if keep is not None:
        # ((review) also none of them a "type of": a file without one would make the script ask nothing for a week
        if not core.instr or not core.ii or not any(t == SUBTYPE_LT for t in core.link_type.values()):
            print('warning: no instruments, or their relationships or links not read (in this order) – no tree of instruments written',
                  file=sys.stderr, flush=True)
        else:
            keep['tree'] = core
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
    # [3.107.0, Z-ITREE]
    ap.add_argument('--instruments', help='core pass: where to write the tree of instruments (the "type of" relationships)')
    ap.add_argument('--instruments-old', help='core pass: the tree of instruments of before (its changes are kept, the new ones added)')
    a = ap.parse_args()
    opener = (bz2.open if a.input and a.input.endswith('.bz2') else open) if a.input else None
    if a.core:
        facts = json.load(open(a.facts, encoding='utf-8'))
        keep = {} if a.instruments else None
        if a.input:
            with opener(a.input, 'rb') as fh:
                core = run_core(fh, facts, a.dump, keep)
        else:
            core = run_core(sys.stdin.buffer, facts, a.dump, keep)
        res = json.load(open(a.merge, encoding='utf-8'))
        res['core'] = core
        out = a.merge
        if keep is not None:
            res['core']['itree'] = bool(keep.get('tree'))  # ((review) the workflow does not read the core dump again at once without one
        if keep and keep.get('tree'):
            old = None
            try:
                old = json.load(open(a.instruments_old, encoding='utf-8')) if a.instruments_old else None
            except (OSError, ValueError):
                old = None
            try:
                tree = keep['tree'].itree(a.dump, old)
            except (KeyError, IndexError, TypeError, ValueError) as e:
                # ((review) a file of before that cannot be read: the tree without its changes (not the core section lost)
                print(f'warning: the tree of before not read ({e}) – written without its changes', file=sys.stderr, flush=True)
                tree = keep['tree'].itree(a.dump, None)
            with open(a.instruments + '.tmp', 'w', encoding='utf-8') as fh:
                json.dump(tree, fh, ensure_ascii=False, separators=(',', ':'))
                fh.write('\n')
            os.replace(a.instruments + '.tmp', a.instruments)
            print(f'instruments: {len(tree["instruments"])}, type of: {len(tree["subtype"])}, changes: {len(tree["changes"])}', file=sys.stderr)
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
