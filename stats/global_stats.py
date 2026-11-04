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
"""
import argparse
import bz2
import datetime as dt
import json
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
            groups[(editor, core)].append((seconds(post), mon, ver, text))
        # a submission: the same note of one editor, its parts at most SUBMISSION_GAP apart (its "Done:" counted once)
        subs = []
        for parts in groups.values():
            parts.sort(key=lambda p: p[0])
            last = None
            for p in parts:
                if last is None or p[0] - last > SUBMISSION_GAP:
                    subs.append(p)
                last = p[0]
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
        out['rows_read'] = dict(self.rows)
        return out


def run(stream, since, dump):
    st = Stats(since)
    handlers = {'edit': st.edit_row, 'edit_data': st.data_row, 'edit_note': st.note_row}
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
    return st.result(dump)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--input', help='the archive (.tar.bz2 or .tar); default: an uncompressed tar on stdin')
    ap.add_argument('--since', default='2026-09-01', help='edits opened from this day on (the first version: 2026-09-28)')
    ap.add_argument('--dump', default='', help='the name of the dump (its directory, e.g. 20261104-002001)')
    ap.add_argument('--out', default=f'stats/{OUT_NAME}')
    a = ap.parse_args()
    if a.input:
        opener = bz2.open if a.input.endswith('.bz2') else open
        with opener(a.input, 'rb') as fh:
            res = run(fh, a.since, a.dump)
    else:
        res = run(sys.stdin.buffer, a.since, a.dump)
    with open(a.out, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(json.dumps(res['totals']), file=sys.stderr)


if __name__ == '__main__':
    main()
