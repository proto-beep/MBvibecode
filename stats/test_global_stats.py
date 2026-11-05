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
    # ((3.55.0, review) 107 failed in the vote: its relationship is not in MusicBrainz – not among the facts)
    edit.append(copy_line(107, 8, 90, 3, 0, '2026-11-02 09:02:00+00', None, '2026-11-09', None, 1))
    edit.append(copy_line(108, 8, 72, 2, 0, '2026-11-02 09:20:00+00', None, '2026-11-09', None, 1))
    # a manual edit of editor 5 whose voter quotes the script; a removal (92) and an edit with a new type (91) by editor 7
    edit.append(copy_line(109, 5, 90, 1, 0, '2026-11-03 10:00:00+00', None, '2026-11-10', None, 1))
    edit.append(copy_line(110, 7, 92, 2, 0, '2026-10-21 10:00:00+00', None, '2026-10-28', None, 1))
    edit.append(copy_line(111, 7, 91, 2, 0, '2026-10-21 10:00:00+00', None, '2026-10-28', None, 1))
    # [3.55.0] the added relationships with their artist, date, attributes and credit
    relx = lambda name, artist, rec, year=None, attrs=(), credit='': json.dumps({'type0': 'artist', 'type1': 'recording', 'link_type': {'id': 1, 'name': name},
                                                                          'entity0': {'id': artist, 'name': 'X'}, 'entity1': {'id': rec, 'name': 'R'}, 'entity0_credit': credit,
                                                                          'begin_date': {'year': year, 'month': None, 'day': None},
                                                                          'attributes': [{'type': {'id': t, 'name': 'a'}, 'credited_as': c} for t, c in attrs]})
    # ((review) the year as digits too, as Moose's Int takes it)
    data += [copy_line(101, relx('instrument', 501, 801, 1995, [(229, 'lead')], 'Ann B.')), copy_line(102, relx('instrument', 502, 802, None, [(229, '')])),
             copy_line(103, relx('vocal', 501, 801, '1985', [(4, '')])), copy_line(105, relx('producer', 503, 803, 2001)),
             copy_line(104, json.dumps({'name': 'W'})), copy_line(107, relx('vocal', 504, 804, None, [(4, 'lead vocals')])), copy_line(109, rel('instrument')),
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
        for name, rows in (('edit', edit), ('edit_artist', ['1\t2\n']), ('edit_data', data), ('edit_note', notes),
                           # ((review) MusicBrainz links an edit of a recording's relationship with every release of it: the submission's release is
                           # the one most of its edits have – 701, not 705)
                           ('edit_recording', ['101\t801\n', '102\t802\n', '105\t899\n', '109\t809\n']),
                           ('edit_release', ['101\t701\n', '101\t705\n', '102\t701\n', '105\t701\n', '103\t702\n', '109\t703\n']),
                           ('vote', ['1\t2\n'])):
            if name == cut:
                break
            if name in skip:
                continue
            b = ''.join(rows).encode('utf-8')
            ti = tarfile.TarInfo(f'mbdump/{name}')
            ti.size = len(b)
            tar.addfile(ti, io.BytesIO(b))


def build_core(path, cut=None):
    """[3.55.0] A small made-up mbdump.tar.bz2 (the tables of the core pass, their columns as in MusicBrainz)."""
    N = None
    art = lambda i, b, e, t, area, g, ended, barea: copy_line(i, 'g', 'n', 'n', b, N, N, e, N, N, t, area, g, '', 0, 'x', 't' if ended else 'f', barea, N)
    tables = [
        ('area', [copy_line(1, 'g', 'United States', 1), copy_line(2, 'g', 'Chicago', 3), copy_line(3, 'g', 'Germany', 1), copy_line(4, 'g', 'Bavaria', 2)]),
        ('artist', [art(501, 1930, 1990, 1, 1, 2, True, 2), art(502, 1965, 1972, 2, 3, N, True, 4), art(503, 1985, N, 1, 3, 1, False, N), art(900, 1900, N, 1, 1, 1, False, N)]),
        ('artist_type', [copy_line(1, 'Person', N, 0, N, 'g'), copy_line(2, 'Group', N, 0, N, 'g')]),
        ('gender', [copy_line(1, 'Male', N, 0, N, 'g'), copy_line(2, 'Female', N, 0, N, 'g')]),
        ('iso_3166_1', [copy_line(1, 'US'), copy_line(3, 'DE')]),
        ('language', [copy_line(120, 'eng', 'eng', 'en', 'English', 2, 'eng')]),
        ('link_attribute_type', [copy_line(3, N, 3, 0, 'g', 'vocal'), copy_line(4, 3, 3, 0, 'g', 'lead vocals'), copy_line(14, N, 14, 0, 'g', 'instrument'), copy_line(229, 14, 14, 0, 'g', 'guitar')]),
        ('medium', [copy_line(1, 701, 1, N), copy_line(2, 701, 2, N), copy_line(3, 702, 1, N), copy_line(4, 999, 1, N)]),
        ('recording', [copy_line(801, 'g', 'a', 1, 200000), copy_line(802, 'g', 'b', 1, 100000), copy_line(803, 'g', 'c', 1, N), copy_line(999, 'g', 'd', 1, 5)]),
        ('release', [copy_line(701, 'g', 'A', 1, 601, 1, N, 120, 28), copy_line(702, 'g', 'B', 1, 602, 1, N, N, 28), copy_line(703, 'g', 'C', 1, 601, 1, N, 120, 28)]),
        ('release_group', [copy_line(601, 'g', 'A', 1, 1), copy_line(602, 'g', 'B', 1, N)]),
        ('release_group_primary_type', [copy_line(1, 'Album', N, 0, N, 'g')]),
        ('release_group_secondary_type', [copy_line(6, 'Live', N, 0, N, 'g')]),
        ('release_group_secondary_type_join', [copy_line(601, 6, 'x')]),
        ('script', [copy_line(28, 'Latn', '215', 'Latin', 4)]),
    ]
    with tarfile.open(path, 'w:bz2') as tar:
        for name, rows in tables:
            if name == cut:
                break
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
        # [3.55.0] the facts for the core pass, the core pass merged into the result; without the core tables an error
        facts = os.path.join(d, 'facts.json')
        subprocess.run([sys.executable, os.path.join(HERE, 'global_stats.py'), '--input', src, '--out', out, '--dump', 'test', '--facts', facts], check=True)
        fx = json.load(open(facts))
        core_src = os.path.join(d, 'mbdump.tar.bz2')
        build_core(core_src)
        subprocess.run([sys.executable, os.path.join(HERE, 'global_stats.py'), '--core', '--input', core_src, '--facts', facts, '--merge', out, '--dump', 'core-test'], check=True)
        r2 = json.load(open(out))
        build_core(core_src, cut='medium')
        p3 = subprocess.run([sys.executable, os.path.join(HERE, 'global_stats.py'), '--core', '--input', core_src, '--facts', facts, '--merge', out], capture_output=True, text=True)
        r3 = json.load(open(out))
        # a run without the core pass keeps the section "core" of before (--keep-core)
        keep = os.path.join(d, 'keep.json')
        out4 = os.path.join(d, 'out4.json')
        json.dump({'core': {'dump': 'old'}}, open(keep, 'w'))
        subprocess.run([sys.executable, os.path.join(HERE, 'global_stats.py'), '--input', src, '--out', out4, '--keep-core', keep], check=True)
        r4 = json.load(open(out4))
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
        ('by_status', r['by_status'], {'applied': 7, 'open': 1, 'failed vote': 1}),
        ('auto_edits', r['auto_edits'], {'voted': 8, 'auto-edit': 1}),
        ('by_relationship_type', r['by_relationship_type'], {'instrument': 3, 'vocal': 2, 'producer': 1, 'mix': 1}),
        ('by_source', r['by_source'], {'discogs': 2, 'youtube': 1}),
        ('supplements', r['supplements'], {'bandcamp': 2}),
        ('done', r['done'], {'credit relationships': 4, 'works linked': 1}),
        ('done_by_level', r['done_by_level'], {'recording': 5, 'release': 2}),  # (the second Discogs submission: "0 credit … (2 recording, 1 release)")
        ('rows_read', r['rows_read'].get('notes on edits before "since"'), 1),
        ('cut off / without edit_note / without vote', bad_runs, [[True, False], [True, False], [True, False]]),
        # [3.55.0] (the voter's edit 109 not among the script's; 504 not in the core dump)
        ('credits', r['credits'], {'credited_as': {'n': 1, 'of': 4}}),
        ('facts', [sorted(map(tuple, fx['artists']), key=lambda x: (x[0], x[1] or 0)), fx['releases'], fx['recordings'], len(fx['attrs'])],
         [sorted([(501, 1995), (502, None), (501, 1985), (503, 2001)], key=lambda x: (x[0], x[1] or 0)), [701, 702], [801, 802, 803], 3]),
        ('core artists', r2['core']['artists'], {'n': 3, 'of': 3, 'types': {'Person': 2, 'Group': 1}, 'genders': {'Female': 1, 'Male': 1},
                                                 'decades': {'1930s': 1, '1960s': 1, '1980s': 1}, 'countries': {'DE': 2, 'US': 1}, 'towns': {'Chicago': 1},
                                                 'centuries': {'1900': 3, '2000': 1}, 'posthumous': {'n': 1, 'of': 2}}),
        ('core releases', r2['core']['releases'], {'n': 2, 'media': {'multi': 1, 'single': 1}, 'rg_primary': {'Album': 1, '-': 1}, 'rg_secondary': {'Live': 1},
                                                   'languages': {'eng': 1, '-': 1}, 'scripts': {'Latn': 2}}),
        ('core lengths', r2['core']['lengths'], {'recordings': 2, 'median_ms': 150000.0, 'mean_ms': 150000.0}),
        ('core role credits', r2['core']['role_credits'], {'n': 1, 'of': 3}),
        ('core dump; the rest kept', [r2['core']['dump'], r2['totals']], ['core-test', r['totals']]),
        ('core cut off: an error, the result as it was', [p3.returncode != 0, r3.get('core', {}).get('dump')], [True, 'core-test']),
        ('keep-core', r4.get('core'), {'dump': 'old'}),
    ]
    bad = [(k, got, want) for k, got, want in checks if got != want]
    text = json.dumps(r2)
    private = [w for w in ('discogs.com/release', 'youtube.com/watch', '"7"', 'editor 7') if w in text]
    for k, got, want in bad:
        print('FEHLER', k, 'ist', got, 'soll', want)
    print('privat:', private)
    print('Ergebnis:', 'OK' if not bad and not private else 'FEHLER')
    return 0 if not bad and not private else 1


if __name__ == '__main__':
    sys.exit(main())
