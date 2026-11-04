#!/usr/bin/env python3
"""A small made-up edit dump through global_stats.py: what it counts (python3 stats/test_global_stats.py).

Also (review of the alpha): one submission sent in parts (25 edits a request, new works first, live comments later with a line more)
is one, its "Done:" counted once; a voter quoting the script's line is no edit of it; "Remove relationship" gets its type by its id;
an edited relationship its new type; an archive cut off between its files or without its tables is an error."""
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def copy_line(*fields):
    esc = lambda v: '\\N' if v is None else str(v).replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n')
    return '\t'.join(esc(v) for v in fields) + '\n'


def note(ver, src, done, name='MB x Vibecode: Credits Importer', extra=''):
    lines = [f'Source: {src}'] if src else []
    lines += extra.split('\n') if extra else []
    lines.append(f'Script: {name} v{ver} (userscript, https://github.com/proto-beep/MBvibecode)')
    if done:
        lines.append(f'Done: {done}.')
    return '\n'.join(lines)


def build(path, cut=None, skip=()):
    edit, data, notes = [], [], []
    rel = lambda name: json.dumps({'type0': 'artist', 'type1': 'recording', 'link_type': {'id': 1, 'name': name}})
    # (not in the order of the ids, as in the real dump)
    edit.append(copy_line(105, 7, 90, 2, 0, '2026-10-20 10:00:00+00', None, '2026-10-27', None, 1))
    edit.append(copy_line(101, 7, 90, 2, 1, '2026-10-20 10:00:00+00', None, '2026-10-27', None, 1))
    edit.append(copy_line(102, 7, 90, 1, 0, '2026-10-20 10:00:00+00', None, '2026-10-27', None, 1))
    edit.append(copy_line(103, 8, 90, 2, 0, '2026-11-02 09:00:00+00', None, '2026-11-09', None, 1))
    edit.append(copy_line(104, 8, 41, 2, 0, '2026-11-02 09:00:00+00', None, '2026-11-09', None, 1))
    edit.append(copy_line(50, 9, 90, 2, 0, '2026-08-01 09:00:00+00', None, '2026-08-08', None, 1))  # before "since"
    edit.append(copy_line(106, 9, 90, 2, 0, '2026-11-03 09:00:00+00', None, '2026-11-10', None, 1))  # another script
    # one submission of editor 8 sent in parts: 107 two minutes later (the next request), 108 a live comment 20 minutes later
    edit.append(copy_line(107, 8, 90, 2, 0, '2026-11-02 09:02:00+00', None, '2026-11-09', None, 1))
    edit.append(copy_line(108, 8, 72, 2, 0, '2026-11-02 09:20:00+00', None, '2026-11-09', None, 1))
    # a manual edit of editor 5 whose voter quotes the script; a removal (92) and an edit with a new type (91) by editor 7
    edit.append(copy_line(109, 5, 90, 1, 0, '2026-11-03 10:00:00+00', None, '2026-11-10', None, 1))
    edit.append(copy_line(110, 7, 92, 2, 0, '2026-10-21 10:00:00+00', None, '2026-10-28', None, 1))
    edit.append(copy_line(111, 7, 91, 2, 0, '2026-10-21 10:00:00+00', None, '2026-10-28', None, 1))
    data += [copy_line(101, rel('instrument')), copy_line(102, rel('instrument')), copy_line(103, rel('vocal')), copy_line(105, rel('producer')),
             copy_line(104, json.dumps({'name': 'W'})), copy_line(107, rel('vocal')), copy_line(109, rel('instrument')),
             copy_line(110, json.dumps({'relationship': {'link': {'type': {'id': 1, 'entity0_type': 'artist', 'long_link_phrase': 'x'}}}})),
             copy_line(111, json.dumps({'link': {'link_type': {'id': 2, 'name': 'performer'}}, 'new': {'link_type': {'id': 3, 'name': 'mix'}}}))]
    n1 = note('3.44.1', 'https://www.discogs.com/release/1-x', 'added 3 credit relationships from Discogs (2 recording, 1 release)',
              extra='Also from: https://x.bandcamp.com/album/y')
    n2 = note('3.45.0', 'https://www.youtube.com/watch?v=a', 'added 1 credit relationship from a YouTube video description (1 recording); linked 1 work to recordings')
    notes += [copy_line(1, 7, 101, n1, '2026-10-20 10:00:01+00'), copy_line(2, 7, 102, n1, '2026-10-20 10:00:01+00'), copy_line(3, 7, 105, n1, '2026-10-20 10:00:01+00'),
              copy_line(4, 8, 103, n2, '2026-11-02 09:00:05+00'), copy_line(5, 8, 104, n2, '2026-11-02 09:00:05+00'),
              copy_line(6, 9, 50, note('2.19.1', 'https://www.discogs.com/release/2-x', None, name='MB x Vibecode: Import Discogs credits'), '2026-08-01 09:00:01+00'),
              copy_line(7, 9, 106, 'Script: Some other tool v1.0', '2026-11-03 09:00:00+00'),
              copy_line(8, 7, 101, 'A reply by a voter mentioning nothing', '2026-10-21 10:00:00+00'),
              copy_line(9, 8, 107, n2, '2026-11-02 09:02:00+00'), copy_line(10, 8, 108, n2 + '\nLive comment: "live, 2001"', '2026-11-02 09:20:00+00'),
              copy_line(11, 99, 109, 'Looks like\nScript: MB x Vibecode: Credits Importer v3.45.0 did this?\nDone: added 12 credit relationships from Discogs (12 recording).', '2026-11-03 11:00:00+00'),
              copy_line(12, 7, 110, n1.replace('3 credit', '0 credit'), '2026-10-21 10:00:00+00'), copy_line(13, 7, 111, n1.replace('3 credit', '0 credit'), '2026-10-21 10:00:00+00')]
    with tarfile.open(path, 'w:bz2') as tar:
        for name, rows in (('edit', edit), ('edit_artist', ['1\t2\n']), ('edit_data', data), ('edit_note', notes), ('vote', ['1\t2\n'])):
            if name == cut:
                break
            if name in skip:
                continue
            b = ''.join(rows).encode('utf-8')
            ti = tarfile.TarInfo(f'mbdump/{name}')
            ti.size = len(b)
            tar.addfile(ti, io.BytesIO(b))


def main():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'mbdump-edit.tar.bz2')
        out = os.path.join(d, 'out.json')
        build(src)
        subprocess.run([sys.executable, os.path.join(HERE, 'global_stats.py'), '--input', src, '--out', out, '--dump', 'test'], check=True)
        r = json.load(open(out))
        # (cut off after edit_data; without edit_note): an error, nothing written
        bad_runs = []
        for cut, skip in (('edit_note', ()), (None, ('edit_note',)), ('vote', ())):
            src2 = os.path.join(d, 'cut.tar.bz2')
            out2 = os.path.join(d, 'cut.json')
            build(src2, cut=cut, skip=skip)
            p = subprocess.run([sys.executable, os.path.join(HERE, 'global_stats.py'), '--input', src2, '--out', out2], capture_output=True, text=True)
            bad_runs.append([p.returncode != 0, os.path.exists(out2)])
    checks = [
        # (editors 7 and 8; the old version's edit is before "since", the voter's quote and the other tool do not count)
        ('totals', r['totals'], {'edits': 9, 'submissions': 3, 'editors': 2}),
        ('by_month', r['by_month'], {'2026-10': {'edits': 5, 'submissions': 2, 'editors': 1}, '2026-11': {'edits': 4, 'submissions': 1, 'editors': 1}}),
        ('by_version', r['by_version'], {'3.44.1': {'edits': 5, 'submissions': 2}, '3.45.0': {'edits': 4, 'submissions': 1}}),
        ('by_edit_type', r['by_edit_type'], {'90 Add relationship': 5, '41 Add work': 1, '72 Edit recording': 1, '92 Remove relationship': 1, '91 Edit relationship': 1}),
        ('by_status', r['by_status'], {'applied': 8, 'open': 1}),
        ('auto_edits', r['auto_edits'], {'voted': 8, 'auto-edit': 1}),
        ('by_relationship_type', r['by_relationship_type'], {'instrument': 3, 'vocal': 2, 'producer': 1, 'mix': 1}),
        ('by_source', r['by_source'], {'discogs': 2, 'youtube': 1}),
        ('supplements', r['supplements'], {'bandcamp': 2}),
        ('done', r['done'], {'credit relationships': 4, 'works linked': 1}),
        ('done_by_level', r['done_by_level'], {'recording': 5, 'release': 2}),  # (the second Discogs submission: "0 credit … (2 recording, 1 release)")
        ('rows_read', r['rows_read'].get('notes on edits before "since"'), 1),
        ('cut off / without edit_note / without vote', bad_runs, [[True, False], [True, False], [True, False]]),
    ]
    bad = [(k, got, want) for k, got, want in checks if got != want]
    text = json.dumps(r)
    private = [w for w in ('discogs.com/release', 'youtube.com/watch', '"7"', 'editor 7') if w in text]
    for k, got, want in bad:
        print('FEHLER', k, 'ist', got, 'soll', want)
    print('privat:', private)
    print('Ergebnis:', 'OK' if not bad and not private else 'FEHLER')
    return 0 if not bad and not private else 1


if __name__ == '__main__':
    sys.exit(main())
