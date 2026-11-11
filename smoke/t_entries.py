"""Smoke test: the entries as a matrix (E4, Block AE; the default from Credits Importer 3.34.29) – collected items E4, 139, 141.

Cases: join (3.34.29), matrix (3.34.30), dates (3.34.31), compact (3.35.0), restage (3.35.0), order (3.35.3), evhead (3.35.4), companies (3.35.5), remember (3.36.0), flagcols (3.36.6), chipask (3.37.14), chipinfo (3.38.6), barroom (3.40.8), compactside (3.40.10), compactlines (3.40.11) – `python3 t_entries.py <case> …` runs only those. The other test files keep the entries as before
("legacy", harness.ENTRIES_VIEW); the cases here set the matrix (the script's default)."""
import harness as H  # noqa: F401 – used by the cases
from caserun import launch_own, run_cases, sync_playwright  # noqa: F401 – the shared browser

# Credits of one Discogs release: several instruments a person, an instrument with "solo", voices, an instrument on one track
JOIN_CREDITS = [('Multi Man', 'Electric Guitar, Acoustic Guitar, Drums', 3071, ''), ('Solo Man', 'Electric Guitar, Saxophone [Solo]', 3072, ''),
                ('Voc Man', 'Lead Vocals, Backing Vocals', 3073, ''), ('Part Man', 'Piano', 3074, '2'), ('Part Man', 'Electric Guitar', 3074, '')]

ADDED = """(() => MB.relationshipEditor.state.added.map((r) => ({ id: r.id, lt: r.linkTypeID, a: (r.entity0 || {}).gid, b: (r.entity1 || {}).gid,
  attrs: ((r.attributes && r.attributes.__tree) || []).map((x) => x.typeName + (x.credited_as ? ' [' + x.credited_as + ']' : '')) })))()"""


def join_release():
    """The test release with the credits of JOIN_CREDITS only."""
    orig = H.discogs_release
    for n, _r, i, _t in JOIN_CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in JOIN_CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    return orig, rel


def staged_by(pg, view):
    """Opens the dashboard in a view (matrix / legacy), stages everything, returns the relationships added (and the page)."""
    H.ENTRIES_VIEW = view
    ctx = H.new_context(H.BROWSER)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(1500)
    label = pg.evaluate("(document.querySelector('[data-act=apply]') || {}).textContent || ''")
    pg.click('[data-act=apply]')
    pg.wait_for_timeout(1500)
    return ctx, pg, errs, pg.evaluate(ADDED), label


def case_join():
    """Credits Importer 3.34.29 (E4, step 1 of Block AE): the entries as a matrix are the default; their
    instruments and voices are joined when staged – per recording, date, artist credit and additional / guest / solo one
    relationship with all of them (⚙ Settings → Staging "Join the instruments and voices of an entry …", on).
    A) Matrix: Multi Man – one instrument relationship per recording with electric guitar, acoustic guitar, drums (drum set)
       “drums” (before: three); Solo Man – electric guitar alone and saxophone with solo apart; Voc Man – one vocal relationship
       with lead and background vocals “backing vocals”; Part Man – on track 2 piano and electric guitar together, on the others
       electric guitar – 20 relationships.
    B) Legacy (⚙ Settings → Appearance "Entries: Legacy"): a relationship per instrument, as before (33); the same instruments on
       the same recordings (the matrix's joined ones split again); the choice stored.
    C) Matrix again, a role credit typed after staging (acoustic guitar "steel-string"): stage – the joined relationship of each
       recording is taken out of the editor and staged anew with all three, acoustic guitar credited "steel-string"; nothing twice.
       (3.35.0) Then drums taken out of ① (its tick off) and staged: the joins again, with electric and acoustic guitar only.
    D) ⚙ Settings → Staging: the switch is there and on; off – nothing is joined."""
    import json
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        H.BROWSER = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx, pg, errs, mx, label_mx = staged_by(None, 'matrix')
            by_lt = lambda rels, lt: sorted([(r['b'] if r['b'] in H.REC else r['a'], tuple(sorted(r['attrs']))) for r in rels if r['lt'] == lt])
            names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in JOIN_CREDITS}
            artist_of = lambda r: names.get(r['a']) or names.get(r['b'])
            mx_multi = [r for r in mx if artist_of(r) == 'Multi Man']
            mx_solo = [r for r in mx if artist_of(r) == 'Solo Man']
            mx_voc = [r for r in mx if artist_of(r) == 'Voc Man']
            mx_part = [r for r in mx if artist_of(r) == 'Part Man']
            print('A) Matrix:', len(mx), 'Beziehungen |', label_mx.strip())
            print('   Multi Man:', sorted(set(tuple(sorted(r['attrs'])) for r in mx_multi)), len(mx_multi))
            print('   Solo Man:', sorted(set(tuple(sorted(r['attrs'])) for r in mx_solo)), len(mx_solo))
            print('   Voc Man:', sorted(set(tuple(sorted(r['attrs'])) for r in mx_voc)), len(mx_voc))
            print('   Part Man:', sorted(tuple(sorted(r['attrs'])) for r in mx_part))
            results.append(len(mx_multi) == 4 and all(sorted(r['attrs']) == ['acoustic guitar', 'drums (drum set) [drums]', 'electric guitar'] for r in mx_multi)
                           and sorted(sorted(r['attrs']) for r in mx_solo) == [['electric guitar']] * 4 + [['saxophone', 'solo']] * 4
                           and len(mx_voc) == 4 and all(sorted(r['attrs']) == ['background vocals [backing vocals]', 'lead vocals'] for r in mx_voc)
                           and sorted(sorted(r['attrs']) for r in mx_part) == [['electric guitar']] * 3 + [['electric guitar', 'piano']])
            # C) a role credit typed after staging, staged again
            # (3.34.30: in the line of the matrix)
            row = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Multi Man');
              const tr = [...g.querySelectorAll('tr.dci-em-line')].find(t => ((t.querySelector('[data-f=em-primary]') || {}).value || '') === 'acoustic guitar'); return tr ? tr.dataset.line : null; })()""")
            ids_before = sorted(r['id'] for r in mx_multi)
            if row:
                pg.fill(f'tr.dci-em-line[data-line="{row}"] [data-f=em-credit]', 'steel-string')
                pg.press(f'tr.dci-em-line[data-line="{row}"] [data-f=em-credit]', 'Tab')
                pg.wait_for_timeout(500)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            after = pg.evaluate(ADDED)
            removed = pg.evaluate("window.__removed.map(r => r.id)")
            multi2 = [r for r in after if artist_of(r) == 'Multi Man']
            print('C) neu:', sorted(set(tuple(sorted(r['attrs'])) for r in multi2)), len(multi2), '| herausgenommen:', sorted(removed) == ids_before, '| insgesamt:', len(after))
            results.append(len(multi2) == 4 and all(sorted(r['attrs']) == ['acoustic guitar [steel-string]', 'drums (drum set) [drums]', 'electric guitar'] for r in multi2)
                           and sorted(removed) == ids_before and len(after) == len(mx))
            # C2) (3.35.0) drums taken out of ① after staging: the joins are staged anew with the other two
            drums = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Multi Man');
              const tr = [...g.querySelectorAll('tr.dci-em-line')].find(t => ((t.querySelector('[data-f=em-primary]') || {}).value || '') === 'drums (drum set)'); return tr ? tr.dataset.line : null; })()""")
            if drums:
                pg.click(f'tr.dci-em-line[data-line="{drums}"] [data-f=em-tick]')
                pg.wait_for_timeout(500)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            after2 = pg.evaluate(ADDED)
            multi3 = [r for r in after2 if artist_of(r) == 'Multi Man']
            print('C2) ohne drums:', sorted(set(tuple(sorted(r['attrs'])) for r in multi3)), len(multi3), '| insgesamt:', len(after2))
            results.append(len(multi3) == 4 and all(sorted(r['attrs']) == ['acoustic guitar [steel-string]', 'electric guitar'] for r in multi3) and len(after2) == len(mx))
            # D) the switch
            H.open_settings(pg, 'staging')
            sw = pg.evaluate("(() => { const c = document.querySelector('[data-set=join]'); return c ? [c.checked, c.disabled] : null; })()")
            H.open_settings(pg, 'appearance')
            seg = pg.evaluate("[...document.querySelectorAll('[data-act=entries-view]')].map(b => [b.dataset.view, b.getAttribute('aria-pressed')])")
            print('D) Schalter:', sw, '| Ansicht:', seg)
            results.append(sw == [True, False] and seg == [['matrix', 'true'], ['legacy', 'false']])
            ctx.close()
            # B) legacy
            ctx, pg, errs2, lg, label_lg = staged_by(None, 'legacy')
            split = lambda rels: sorted((r['lt'], r['a'], r['b'], x) for r in rels for x in r['attrs'] if x not in ('solo',))
            print('B) Legacy:', len(lg), 'Beziehungen |', label_lg.strip(), '| gleiche Instrumente:', split(lg) == split(mx))
            results.append(len(lg) == len([1 for r in mx for x in r['attrs'] if x != 'solo']) and split(lg) == split(mx) and len(lg) > len(mx))
            st = pg.evaluate("(() => { try { return localStorage.getItem('dci-entries-view'); } catch (e) { return null; } })()")
            results.append(json.loads(st or 'null') == 'legacy')
            print('Fehler:', errs, errs2)
            results.append(not errs and not errs2)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            H.BROWSER.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# the blocks of an entry: head, event heads, lines (instrument or role, role credit, flags ticked, ticks, status, rows)
# ([Z-EMCELL] 3.109.0) a block's events: its own columns, not the ticks of the others' (dci-em-c-other)
BLOCKS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null;
  return [...g.querySelectorAll('.dci-em-block')].map(b => ({ key: b.dataset.block, head: (h => { const c = h.cloneNode(true); c.querySelectorAll('.dci-em-bac, .dci-insts-seg').forEach(x => x.remove()); return c.textContent; })(b.querySelector('.dci-em-bhead')).replace(/\\s+/g, ' ').trim(),
    tip: b.querySelector('.dci-em-bhead strong').title,
    ev: (() => { const heads = [...b.closest('table').querySelectorAll('thead th.dci-em-ev')]; const ln = b.querySelector('tr.dci-em-line'); const cells = ln ? [...ln.querySelectorAll('td.dci-em-c-ev')] : [];
      return heads.filter((h, i) => cells[i] && !cells[i].classList.contains('dci-em-c-none') && !cells[i].classList.contains('dci-em-c-other')); })().map(h => { const c = h.cloneNode(true); c.querySelectorAll('.dci-em-evtoggle, button.dci-em-evdate, .dci-em-evdatebox').forEach(x => x.remove()); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
    add: [...b.querySelectorAll('[data-f=em-addev] option')].filter(o => o.value).map(o => o.textContent.trim()),
    lines: [...b.querySelectorAll('tr.dci-em-line')].map(t => ({ line: t.dataset.line, n: t.dataset.rows.split(',').length, skip: t.classList.contains('dci-em-skip'),
      role: ((t.querySelector('[data-f=em-primary]') || {}).value) || t.querySelector('.dci-em-c-role').textContent.replace(/\\s+/g, ' ').trim(),
      wrote: (t.querySelector('.dci-em-raw') || { textContent: '' }).textContent.trim(), credit: (t.querySelector('[data-f=em-credit]') || { value: '-' }).value,
      flags: [...t.querySelectorAll('[data-f=em-flag]')].filter(c => c.checked).map(c => c.value), ticks: [...t.querySelectorAll('td:not(.dci-em-c-other) > [data-f=em-tick]')].map(c => c.checked),
      status: (t.querySelector('[data-emstatus]') || { textContent: '' }).textContent.trim() })) })); }"""


def sec_sel(pg, name):
    """A selector for the section of an entry (by its group key)."""
    key = pg.evaluate("(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name); return g ? g.dataset.group : ''; }", name)
    return f'section[data-group="{key}"]'


def case_matrix():
    """Credits Importer 3.34.30 (E4, step 2 of Block AE; collected items E4, 139, 141; mockup "Credits Importer – mehrere
    Instrumente in einer Zeile (E4)", version 3): an entry as a matrix – its instruments in one block (lines: the instrument of
    MusicBrainz, "written …", role credit, add. / guest / solo, a tick per event, its status, ▸ rows, ✕), the events (level ·
    date · tracks) as columns.
    A) Multi Man: one block "3 instruments · from 3 rows · One row each" ([Q-c] 3.38.14: no longer "→ instrument"), one event "① Recording all 4 tracks"
       (3.34.31: the date a field, empty), electric guitar, acoustic guitar, drums (drum set) “drums” (written “Drums”) – all ticked, "4 new" each.
    B) ▸ rows of the drums line: its row with all its fields (the legacy row) below the line.
    C) Solo Man: saxophone with "solo" ticked; "guest" ticked for electric guitar – stays (its rows).
    D) ⚙ Settings → Staging "Events shared … up to 1": Part Man (2 events) – its block shows its own, "· 2 events", folds and
       opens; "One row each": piano and electric guitar each a block with its own event and "＋ Event ▾" with the other one;
       piano: ① added and ticked (a row of its own, all 4 tracks); "Join in one block" again; the setting back to 3.
    E) Part Man: electric guitar taken out of ① – the line grey, no tick.
    F) Multi Man "One row each": three blocks, "Join in one block" offered.
    G) Staged: Multi Man – a relationship per instrument (12); Part Man – piano on all 4 recordings, no guitar; Solo Man –
       electric guitar with "guest"."""
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            a = pg.evaluate(BLOCKS, 'Multi Man')
            print('A) Multi Man:', a)
            b0 = (a or [{}])[0]
            results.append(bool(a) and len(a) == 1 and b0['head'] == '3 instruments · from 3 rows One row each'
                           and b0['ev'] == ['① Recording all 4 tracks']
                           and [(l['role'], l['credit'], l['wrote'], l['ticks'], l['status']) for l in b0['lines']] == [
                               ('electric guitar', '', '', [True], '4 new'), ('acoustic guitar', '', '', [True], '4 new'),
                               ('drums (drum set)', 'drums', 'written “Drums”', [True], '4 new')])
            multi = sec_sel(pg, 'Multi Man')
            drums = b0['lines'][2]['line'] if a else ''
            pg.click(f'{multi} tr.dci-em-line[data-line="{drums}"] [data-act=em-detail]')
            pg.wait_for_timeout(400)
            det = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' .dci-em-detail-row tr.dci-row')].map(t => (t.querySelector('[data-f=primary]') || {}).value)", multi)
            print('B) Zeilen:', det)
            results.append(det == ['drums (drum set)'])
            solo = sec_sel(pg, 'Solo Man')
            s0 = pg.evaluate(BLOCKS, 'Solo Man')
            eg = [l for l in s0[0]['lines'] if l['role'] == 'electric guitar'][0]['line'] if s0 else ''
            pg.click(f'{solo} tr.dci-em-line[data-line="{eg}"] [data-f=em-flag][value=guest]')
            pg.wait_for_timeout(400)
            s1 = pg.evaluate(BLOCKS, 'Solo Man')
            print('C) Solo Man:', [(l['role'], l['flags']) for l in s1[0]['lines']])
            results.append([(l['role'], l['flags']) for l in s1[0]['lines']] == [('electric guitar', ['guest']), ('saxophone', ['solo'])])
            # D) more events than shared
            H.open_settings(pg, 'staging')
            pg.fill('[data-set=ev-shared]', '1')
            pg.press('[data-set=ev-shared]', 'Tab')
            pg.wait_for_timeout(500)
            part = sec_sel(pg, 'Part Man')
            d0 = pg.evaluate(BLOCKS, 'Part Man')
            pg.click(f'{part} [data-act=em-fold]')
            pg.wait_for_timeout(300)
            folded = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' .dci-em-block')].map(b => [b.classList.contains('dci-em-folded'), b.querySelectorAll('tr.dci-em-line').length])", part)
            pg.click(f'{part} [data-act=em-fold]')
            pg.wait_for_timeout(300)
            pg.click(f'{part} [data-act=em-split]')
            pg.wait_for_timeout(400)
            d1 = pg.evaluate(BLOCKS, 'Part Man')
            piano = [x for x in d1 if x['lines'][0]['role'] == 'piano'][0]
            pg.select_option(f'{part} .dci-em-block[data-block="{piano["key"]}"] [data-f=em-addev]', index=1)
            pg.wait_for_timeout(400)
            d2 = pg.evaluate(BLOCKS, 'Part Man')
            piano2 = [x for x in d2 if x['lines'][0]['role'] == 'piano'][0]
            first = piano2['lines'][0]['line']
            pg.click(f'{part} tr.dci-em-line[data-line="{first}"] [data-f=em-tick] >> nth=0')
            pg.wait_for_timeout(400)
            d3 = pg.evaluate(BLOCKS, 'Part Man')
            piano3 = [x for x in d3 if x['lines'][0]['role'] == 'piano'][0]
            join_btn = pg.evaluate("(sel) => !!document.querySelector(sel + ' [data-act=em-join]')", part)
            pg.click(f'{part} [data-act=em-join]')
            pg.wait_for_timeout(400)
            d4 = pg.evaluate(BLOCKS, 'Part Man')
            print('D) geteilt:', d0[0]['head'], d0[0]['ev'], '| gefaltet:', folded, '| einzeln:', [(x['lines'][0]['role'], x['ev'], x['add']) for x in d1],
                  '| piano:', piano3['ev'], piano3['lines'][0]['ticks'], piano3['lines'][0]['n'], '| Knopf:', join_btn, '| zusammen:', [x['head'] for x in d4])
            results.append(d0[0]['head'].endswith('· 2 events One row each') and d0[0]['ev'] == ['① Recording all 4 tracks', '② Recording track 2']
                           and folded == [[True, 0]] and len(d1) == 2
                           and sorted((x['lines'][0]['role'], len(x['ev']), len(x['add'])) for x in d1) == [('electric guitar', 1, 1), ('piano', 1, 1)]
                           and piano3['ev'] == ['① Recording all 4 tracks', '② Recording track 2'] and piano3['lines'][0]['ticks'] == [True, True]
                           and piano3['lines'][0]['n'] == 2 and join_btn and len(d4) == 1)
            H.open_settings(pg, 'staging')
            pg.fill('[data-set=ev-shared]', '3')
            pg.press('[data-set=ev-shared]', 'Tab')
            pg.wait_for_timeout(400)
            # E) electric guitar of Part Man out of ①
            e0 = pg.evaluate(BLOCKS, 'Part Man')
            g_line = [l for l in e0[0]['lines'] if l['role'] == 'electric guitar'][0]['line']
            pg.click(f'{part} tr.dci-em-line[data-line="{g_line}"] [data-f=em-tick] >> nth=0')
            pg.wait_for_timeout(400)
            e1 = pg.evaluate(BLOCKS, 'Part Man')
            g1 = [l for l in e1[0]['lines'] if l['role'] == 'electric guitar'][0]
            print('E) electric guitar:', g1)
            results.append(g1['skip'] and g1['ticks'] == [False, False])
            # F) Multi Man one row each
            pg.click(f'{multi} [data-act=em-split]')
            pg.wait_for_timeout(400)
            f0 = pg.evaluate(BLOCKS, 'Multi Man')
            fj = pg.evaluate("(sel) => !!document.querySelector(sel + ' [data-act=em-join]')", multi)
            print('F) einzeln:', [x['head'] for x in f0], '| Knopf:', fj)
            results.append(len(f0) == 3 and fj)
            # G) staged
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate(ADDED)
            names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in JOIN_CREDITS}
            of = lambda n: [sorted(r['attrs']) for r in added if names.get(r['a']) == n or names.get(r['b']) == n]
            print('G) Multi Man:', len(of('Multi Man')), '| Part Man:', of('Part Man'), '| Solo Man:', of('Solo Man'))
            results.append(len(of('Multi Man')) == 12 and of('Part Man') == [['piano']] * 4
                           and sorted(of('Solo Man')) == [['electric guitar', 'guest']] * 4 + [['saxophone', 'solo']] * 4)
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# a date of the pool dropped (dragstart, dragover, drop as events: Playwright's mouse carries no Shift)
DROP = """([src, dst, shift]) => { const s = document.querySelector(src); const d = document.querySelector(dst); if (!s || !d) return false;
  const dt = new DataTransfer(); s.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
  d.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: shift }));
  d.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: shift }));
  s.dispatchEvent(new DragEvent('dragend', { bubbles: true, dataTransfer: dt })); return true; }"""
ADDED_D = """(() => MB.relationshipEditor.state.added.map((r) => ({ a: (r.entity0 || {}).gid, b: (r.entity1 || {}).gid,
  date: r.begin_date ? [r.begin_date.year, r.begin_date.month, r.begin_date.day].filter(Boolean).join('-') : '',
  attrs: ((r.attributes && r.attributes.__tree) || []).map((x) => x.typeName).sort() })))()"""


def case_dates():
    """Credits Importer 3.34.31 (E4, step 3 of Block AE; mockup version 3, board 4; collected item 139):
    dates in an entry's matrix.
    A) A date of the pool dropped onto the line of acoustic guitar (Multi Man): the line moves into the date's event – a second
       column ② with the date, acoustic guitar ticked there only (the instrument "wanders"); a message with ↶.
    B) ↶: acoustic guitar back in ①, one event again.
    C) The date dropped onto the head of ①: all three instruments get it – still one event, its head shows the date.
    D) A date typed into the head of Solo Man's ① ("2001-06-05"): its rows get it as a new date of the pool; the date of
       Multi Man's ① changed in its head ("2001-03-02"): the pool's date itself changes.
    E) ([3.78.0] Z-DND) A date dropped onto the head of Voc Man's block: both voices get it (they had none). A second date dropped
       there: they keep theirs and get a row each with the new one – a second event, ticked in ① and ②; ↶. With ⇧ Shift the second
       date replaces the first (one event).
    E2) (3.35.0) With one line of a block shown (⚙ "Lines … before ▸ n more": 1) a date dropped onto the block's head: all three
       instruments of Multi Man, also those behind "▸ 2 more" – ([3.78.0]) they keep their date (2001-03-02) and get the new one
       in an event of its own.
    F) Staged: Voc Man – lead and background vocals with the date joined (4)."""
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            chips = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => [c.dataset.id, c.textContent.replace(/\\s+/g, ' ').trim()])")
            print('   Pool:', chips)
            d1, d2 = chips[0][0], chips[-1][0]
            multi = sec_sel(pg, 'Multi Man')
            a0 = pg.evaluate(BLOCKS, 'Multi Man')
            ac = [l for l in a0[0]['lines'] if l['role'] == 'acoustic guitar'][0]['line']
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d1}"]', f'{multi} tr.dci-em-line[data-line="{ac}"]', False])
            pg.wait_for_timeout(500)
            a1 = pg.evaluate(BLOCKS, 'Multi Man')
            msg = pg.evaluate("[...document.querySelectorAll('[data-act=em-undo]')].map(x => x.closest('li, div, p').textContent.replace(/\\s+/g, ' ').trim())")
            print('A) Linie:', a1[0]['ev'], [(l['role'], l['ticks']) for l in a1[0]['lines']], '| Meldung:', msg)
            results.append(len(a1[0]['ev']) == 2 and [(l['role'], l['ticks']) for l in a1[0]['lines']] == [
                ('electric guitar', [True, False]), ('acoustic guitar', [False, True]), ('drums (drum set)', [True, False])] and len(msg) == 1)
            pg.click('[data-act=em-undo]')
            pg.wait_for_timeout(500)
            a2 = pg.evaluate(BLOCKS, 'Multi Man')
            print('B) ↶:', a2[0]['ev'], [(l['role'], l['ticks']) for l in a2[0]['lines']])
            results.append(a2[0]['ev'] == ['① Recording all 4 tracks'] and all(l['ticks'] == [True] for l in a2[0]['lines']))
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d1}"]', f'{multi} th.dci-em-ev', False])
            pg.wait_for_timeout(500)
            a3 = pg.evaluate(BLOCKS, 'Multi Man')
            v3 = pg.evaluate(H.EV_DATES, multi)
            print('C) Kopf:', a3[0]['ev'], v3, [(l['role'], l['ticks']) for l in a3[0]['lines']])
            results.append(len(a3[0]['ev']) == 1 and v3 and v3[0] != '' and all(l['ticks'] == [True] for l in a3[0]['lines']))
            # D) dates typed into the heads
            solo = sec_sel(pg, 'Solo Man')
            n_pool = len(chips)
            H.ev_date(pg, solo, '2001-06-05')
            pg.wait_for_timeout(500)
            sv = pg.evaluate(H.EV_DATES, solo)
            chips2 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => [c.dataset.id, c.textContent.replace(/\\s+/g, ' ').trim()])")
            H.ev_date(pg, multi, '2001-03-02')
            pg.wait_for_timeout(500)
            chips3 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => [c.dataset.id, c.textContent.replace(/\\s+/g, ' ').trim()])")
            mv = pg.evaluate(H.EV_DATES, multi)
            changed = [c for c in chips3 if c[0] == d1]
            print('D) Solo Man:', sv, '| Pool:', len(chips2), '| Multi Man:', mv, '| der Pool-Eintrag:', changed)
            results.append(sv == ['2001-06-05'] and len(chips2) == n_pool + 1 and mv == ['2001-03-02'] and changed and '2001-03-02' in changed[0][1])
            # E) ([3.78.0] Z-DND) onto the head of a block: set; a second date: kept, a new event; ↶; with ⇧ Shift: replaced
            voc = sec_sel(pg, 'Voc Man')
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d2}"]', f'{voc} .dci-em-bhead', False])
            pg.wait_for_timeout(500)
            e0 = pg.evaluate(H.EV_DATES, voc)
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d1}"]', f'{voc} .dci-em-bhead', False])
            pg.wait_for_timeout(500)
            e1 = pg.evaluate(BLOCKS, 'Voc Man')
            ev1 = pg.evaluate(H.EV_DATES, voc)
            msg1 = pg.evaluate("[...document.querySelectorAll('[data-act=em-undo]')].map(x => x.closest('li, div, p').textContent.replace(/\\s+/g, ' ').trim())")
            pg.click('[data-act=em-undo]')
            pg.wait_for_timeout(500)
            ev2 = pg.evaluate(H.EV_DATES, voc)
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d1}"]', f'{voc} .dci-em-bhead', True])
            pg.wait_for_timeout(500)
            ev3 = pg.evaluate(H.EV_DATES, voc)
            print('E) gesetzt:', e0, '| zweites Datum:', ev1, [(l['role'], l['ticks'], l['n']) for l in e1[0]['lines']], msg1, '| ↶:', ev2, '| mit ⇧:', ev3)
            results.append(e0 == ['2001-05'] and sorted(ev1) == ['2001-03-02', '2001-05'] and len(msg1) == 1 and 'their date stays' in msg1[0]
                           and [(l['role'], l['ticks'], l['n']) for l in e1[0]['lines']] == [('lead vocals', [True, True], 2), ('background vocals', [True, True], 2)]
                           and ev2 == ['2001-05'] and ev3 == ['2001-03-02'])
            # E2) (3.35.0) onto the head of a block whose lines are partly behind "▸ n more": all its lines
            H.open_settings(pg, 'staging')
            pg.fill('[data-set=em-show]', '1')
            pg.press('[data-set=em-show]', 'Tab')
            pg.wait_for_timeout(400)
            hidden = pg.evaluate("(sel) => document.querySelectorAll(sel + ' tr.dci-em-line').length", multi)
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d2}"]', f'{multi} .dci-em-bhead', False])
            pg.wait_for_timeout(500)
            pg.fill('[data-set=em-show]', '8')
            pg.press('[data-set=em-show]', 'Tab')
            pg.wait_for_timeout(400)
            e2 = pg.evaluate(BLOCKS, 'Multi Man')
            ev2 = pg.evaluate(H.EV_DATES, multi)
            print('E2) Kopf des Blocks, 1 Zeile gezeigt:', hidden, '| danach:', ev2, [(l['role'], l['ticks']) for l in e2[0]['lines']])
            results.append(hidden == 1 and sorted(ev2) == ['2001-03-02', '2001-05'] and all(l['ticks'] == [True, True] for l in e2[0]['lines']) and len(e2[0]['lines']) == 3)
            # F) staged
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate(ADDED_D)
            names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in JOIN_CREDITS}
            vm = sorted((r['date'], tuple(r['attrs'])) for r in added if names.get(r['a']) == 'Voc Man' or names.get(r['b']) == 'Voc Man')
            print('F) Voc Man:', vm)
            dated = [x for x in vm if x[0]]
            results.append(len(vm) == 4 and len(dated) == 4 and all(x[1] == ('background vocals', 'lead vocals') and x[0] == '2001-3-2' for x in dated))
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# the compact lines of an entry: per event (its head, its chips) or per role
CLINES = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null;
  return { wide: g.classList.contains('dci-em-entry'), compact: g.classList.contains('dci-em-centry'),
    by: (g.querySelector('[data-act=em-by][aria-pressed=true]') || {}).dataset ? (g.querySelector('[data-act=em-by][aria-pressed=true]') || { dataset: {} }).dataset.by : '',
    lines: [...g.querySelectorAll('.dci-em-cl')].map(l => ({ ev: l.dataset.emev || '', head: [...l.querySelectorAll('.dci-em-evn, .dci-cl-level, .dci-cl-date, .dci-cl-tracks')].slice(0, 4).map(x => x.textContent.trim()).join(' '),
      chips: [...l.querySelectorAll('.dci-em-chipname')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()), skip: l.classList.contains('dci-em-skip') })) }; }"""


def case_compact():
    """Credits Importer 3.35.0 (E4, the last step of Block AE, milestone "Entries as a matrix"; mockup version 3, board 1): an entry
    compact as a matrix. A) ☰ compact: Multi Man – one line "① Recording no date all 4 tracks" with the chips electric guitar ·
    acoustic guitar ·
       drums (drum set) “drums”; Part Man – ① electric guitar, ② (track 2) piano.
    B) The piano chip dragged onto the line of ① with ⇧ Shift ([3.78.0] Z-DND; without it the role is in both): piano moves there –
       one line ① with both (in the order of the source); ② is gone ([Z-EVCOL] 3.103.0: it stays, empty, until taken away with ✕).
    C) ✕ on acoustic guitar (Multi Man): out of ① – "Taken out: acoustic guitar".
    D) "by role" for Solo Man: a line per role with its events.
    E) ▸ in the head of Multi Man: its full matrix here; ▾ compact again; a chip clicked: the full matrix, at its line.
    F) ⚙ Settings → Staging "An entry, compact, at first: by role": every entry by role (Solo Man as chosen).
    G) The summary says how many relationships a row per instrument would be (joined)."""
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            summ = pg.evaluate("(document.querySelector('[data-el=sum-joined]') || { textContent: '' }).textContent.trim()")
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            a_multi = pg.evaluate(CLINES, 'Multi Man')
            a_part = pg.evaluate(CLINES, 'Part Man')
            print('A) Multi Man:', a_multi, '| Part Man:', [(l['head'], l['chips']) for l in a_part['lines']])
            results.append(a_multi['compact'] and not a_multi['wide'] and a_multi['by'] == 'event'
                           and [(l['head'], l['chips']) for l in a_multi['lines']] == [('① Recording no date all 4 tracks', ['electric guitar', 'acoustic guitar', 'drums (drum set) “drums”'])]
                           and [(l['head'], l['chips']) for l in a_part['lines']] == [('① Recording no date all 4 tracks', ['electric guitar']), ('② Recording no date track 2', ['piano'])])
            part = sec_sel(pg, 'Part Man')
            ev1, ev2 = a_part['lines'][0]['ev'], a_part['lines'][1]['ev']
            pg.evaluate(DROP, [f'{part} .dci-em-cl[data-emev="{ev2}"] .dci-em-chip', f'{part} .dci-em-cl[data-emev="{ev1}"]', True])
            pg.wait_for_timeout(500)
            b_part = pg.evaluate(CLINES, 'Part Man')
            print('B) gezogen:', [(l['head'], l['chips']) for l in b_part['lines']])
            # ([Z-EVCOL] 3.103.0) the event left empty stays (grey, ✕) until taken away
            results.append([(l['head'], l['chips']) for l in b_part['lines']][0] == ('① Recording no date all 4 tracks', ['piano', 'electric guitar'])
                           and len(b_part['lines']) == 2 and b_part['lines'][1]['chips'] == [] and b_part['lines'][1]['head'].startswith('②'))
            multi = sec_sel(pg, 'Multi Man')
            pg.click(f'{multi} .dci-em-chip:has-text("acoustic guitar") [data-act=em-chipout]')
            pg.wait_for_timeout(500)
            c_multi = pg.evaluate(CLINES, 'Multi Man')
            print('C) ✕:', [(l['head'], l['chips'], l['skip']) for l in c_multi['lines']])
            results.append([(l['chips'], l['skip']) for l in c_multi['lines']] == [(['electric guitar', 'drums (drum set) “drums”'], False), (['acoustic guitar'], True)])
            solo = sec_sel(pg, 'Solo Man')
            pg.click(f'{solo} [data-act=em-by][data-by=role]')
            pg.wait_for_timeout(400)
            d_solo = pg.evaluate(CLINES, 'Solo Man')
            print('D) by role:', d_solo['by'], [(l['chips'], l['head']) for l in d_solo['lines']])
            results.append(d_solo['by'] == 'role' and [l['chips'] for l in d_solo['lines']] == [['electric guitar'], ['saxophone · solo']])
            pg.click(f'{multi} [data-act=em-wide]')
            pg.wait_for_timeout(400)
            e1 = pg.evaluate(CLINES, 'Multi Man')
            e1b = pg.evaluate(BLOCKS, 'Multi Man')
            pg.click(f'{multi} [data-act=em-wide]')
            pg.wait_for_timeout(400)
            e2 = pg.evaluate(CLINES, 'Multi Man')
            pg.click(f'{multi} .dci-em-chip:has-text("drums") [data-act=em-chip]')
            pg.wait_for_timeout(400)
            e3 = pg.evaluate(CLINES, 'Multi Man')
            flash = pg.evaluate("(sel) => !!document.querySelector(sel + ' tr.dci-em-line.dci-flash')", multi)
            print('E) ▸:', e1['wide'], len(e1b or []), '| ▾:', e2['compact'], '| Chip:', e3['wide'], flash)
            results.append(e1['wide'] and len(e1b) == 1 and e2['compact'] and e3['wide'] and flash)
            H.open_settings(pg, 'staging')
            pg.click('.dci-set-pane [data-act=em-by-default][data-by=role]')
            pg.wait_for_timeout(400)
            f_part = pg.evaluate(CLINES, 'Part Man')
            stored = pg.evaluate("localStorage.getItem('dci-em-by')")
            pg.click('.dci-set-pane [data-act=em-by-default][data-by=event]')
            pg.wait_for_timeout(300)
            print('F) Standard by role:', f_part['by'], stored, '| G) Summe:', summ)
            results.append(f_part['by'] == 'role' and stored == '"role"' and 'a relationship per instrument would be 33' in summ)
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_restage():
    """Credits Importer 3.35.0 (fixes after a review of Block AE): what was staged follows when the joining changes.
    A) Staged: Multi Man – 4 joined relationships (electric guitar, acoustic guitar, drums).
    B) "One row each", staged again: the joined ones taken out, a relationship per instrument (12).
    C) "Join in one block", staged again: the singles taken out, joined again (4).
    D) A joined relationship changed in the relationship editor itself (an artist credit), then a role credit typed: staged –
       from 3.83.0 (S124) the changed one is replaced too and a message names it: four anew, nothing twice (until 3.82.0 the changed
       one stayed as it was, its rows not staged again)."""
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in JOIN_CREDITS}
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            multi_of = lambda: [r for r in pg.evaluate(ADDED) if names.get(r['a']) == 'Multi Man' or names.get(r['b']) == 'Multi Man']
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            a = multi_of()
            print('A)', len(a), sorted(set(tuple(sorted(r['attrs'])) for r in a)))
            results.append(len(a) == 4 and all(len(r['attrs']) == 3 for r in a))
            multi = sec_sel(pg, 'Multi Man')
            pg.click(f'{multi} [data-act=em-split]')
            pg.wait_for_timeout(400)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            bb = multi_of()
            print('B) einzeln:', len(bb), sorted(set(tuple(sorted(r['attrs'])) for r in bb)))
            results.append(len(bb) == 12 and all(len(r['attrs']) == 1 for r in bb))
            # (the foot of the entry may lie below the footer of the dashboard: a click by script)
            pg.evaluate("(sel) => document.querySelector(sel + ' [data-act=em-join]').click()", multi)
            pg.wait_for_timeout(400)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            c = multi_of()
            print('C) zusammen:', len(c), sorted(set(tuple(sorted(r['attrs'])) for r in c)))
            results.append(len(c) == 4 and all(len(r['attrs']) == 3 for r in c))
            # D) one of them changed in the editor itself
            edited = pg.evaluate("""(gid) => { const re = MB.relationshipEditor; const st = re.state.added.find(r => (r.entity0 || {}).gid === gid || (r.entity1 || {}).gid === gid);
              const changed = { ...st, entity1_credit: 'M. Man', entity0_credit: st.entity0_credit };
              re.dispatch({ type: 'update-relationship-state', sourceEntity: st.entity1, oldRelationshipState: st, newRelationshipState: changed }); return st.id; }""", H.uid('dddddddd', 3071 - 2990))
            line = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Multi Man');
              const tr = [...g.querySelectorAll('tr.dci-em-line')].find(t => ((t.querySelector('[data-f=em-primary]') || {}).value || '') === 'electric guitar'); return tr ? tr.dataset.line : null; })()""")
            pg.fill(f'{multi} tr.dci-em-line[data-line="{line}"] [data-f=em-credit]', 'lead')
            pg.press(f'{multi} tr.dci-em-line[data-line="{line}"] [data-f=em-credit]', 'Tab')
            pg.wait_for_timeout(400)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            d = multi_of()
            kept = [r for r in d if r['id'] == edited]
            fresh = [r for r in d if r['id'] != edited]
            print('D) geändert behalten:', len(kept), kept[0]['attrs'] if kept else None, '| neu:', len(fresh), sorted(set(tuple(sorted(r['attrs'])) for r in fresh)))
            # (3.83.0, S124) the changed one is replaced too – by what the dashboard has now – and named (until 3.82.0 it stayed)
            said = pg.evaluate("[...document.querySelectorAll('.dci-msg')].some(m => /replaced by what the dashboard has now/.test(m.textContent))")
            results.append(len(kept) == 0 and len(fresh) == 4 and all('electric guitar [lead]' in r['attrs'] for r in fresh) and said)
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# a line dragged by its ⠿ onto another line: before it (upper half) or after it (lower half)
DROP_AT = """([src, dst, after]) => { const s = document.querySelector(src); const d = document.querySelector(dst); if (!s || !d) return false;
  const box = d.getBoundingClientRect(); const y = after ? box.bottom - 2 : box.top + 2; const x = box.left + 20;
  const dt = new DataTransfer(); s.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
  d.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt, clientX: x, clientY: y }));
  const mark = d.classList.contains('dci-dm-over') ? (d.classList.contains('dci-em-after') ? 'after' : 'before') : '';
  d.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt, clientX: x, clientY: y }));
  s.dispatchEvent(new DragEvent('dragend', { bubbles: true, dataTransfer: dt })); return mark; }"""


def case_order():
    """Credits Importer 3.35.3 (AE-2): the lines
    of a block in another order.
    A) Multi Man: ⠿ at each line of its block (electric guitar · acoustic guitar · drums); drums dragged onto the upper half of
       electric guitar – the mark above it, drums first.
    B) Electric guitar dropped onto the lower half of acoustic guitar – the mark below it: drums · acoustic guitar · electric
       guitar.
    C) Alt+↑ on ⠿ of electric guitar: one place up (drums · electric guitar · acoustic guitar), ⠿ keeps the focus.
    D) A line of another entry (Voc Man) dropped onto Multi Man's lines: nothing (not a place for it, no mark). Solo Man: ⠿ at
       both lines of its block; after "One row each" each line is a block of its own – no ⠿.
    E) ☰ compact: the chips in the new order.
    F) Staged: Multi Man – one relationship per recording with all three instruments, as before (4).
    G) The page loaded again (a new import): the order of the source again (3.36.0: as long as the release is not remembered –
       ⚙ Settings → Cache, off by default)."""
    H.REMEMBER = False
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    roles = lambda bl: [l['role'] for l in bl[0]['lines']] if bl else None
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            multi = sec_sel(pg, 'Multi Man')
            a0 = pg.evaluate(BLOCKS, 'Multi Man')
            grips = pg.evaluate("(sel) => document.querySelectorAll(sel + ' tr.dci-em-line .dci-em-grip').length", multi)
            ids = {l['role']: l['line'] for l in a0[0]['lines']}
            mark_a = pg.evaluate(DROP_AT, [f'{multi} tr.dci-em-line[data-line="{ids["drums (drum set)"]}"] .dci-em-grip', f'{multi} tr.dci-em-line[data-line="{ids["electric guitar"]}"]', False])
            pg.wait_for_timeout(400)
            a1 = pg.evaluate(BLOCKS, 'Multi Man')
            print('A) vorher:', roles(a0), '| ⠿:', grips, '| Marke:', mark_a, '| nachher:', roles(a1))
            results.append(roles(a0) == ['electric guitar', 'acoustic guitar', 'drums (drum set)'] and grips == 3 and mark_a == 'before'
                           and roles(a1) == ['drums (drum set)', 'electric guitar', 'acoustic guitar'])
            mark_b = pg.evaluate(DROP_AT, [f'{multi} tr.dci-em-line[data-line="{ids["electric guitar"]}"] .dci-em-grip', f'{multi} tr.dci-em-line[data-line="{ids["acoustic guitar"]}"]', True])
            pg.wait_for_timeout(400)
            b1 = pg.evaluate(BLOCKS, 'Multi Man')
            print('B) Marke:', mark_b, '| nachher:', roles(b1))
            results.append(mark_b == 'after' and roles(b1) == ['drums (drum set)', 'acoustic guitar', 'electric guitar'])
            pg.focus(f'{multi} tr.dci-em-line[data-line="{ids["electric guitar"]}"] .dci-em-grip')
            pg.keyboard.press('Alt+ArrowUp')
            pg.wait_for_timeout(400)
            c1 = pg.evaluate(BLOCKS, 'Multi Man')
            focus = pg.evaluate("(() => { const a = document.activeElement; return a && a.classList.contains('dci-em-grip') ? a.dataset.id : ''; })()")
            print('C) Alt+↑:', roles(c1), '| Fokus:', focus == ids['electric guitar'])
            results.append(roles(c1) == ['drums (drum set)', 'electric guitar', 'acoustic guitar'] and focus == ids['electric guitar'])
            voc = sec_sel(pg, 'Voc Man')
            v0 = pg.evaluate(BLOCKS, 'Voc Man')
            mark_d = pg.evaluate(DROP_AT, [f'{voc} tr.dci-em-line .dci-em-grip', f'{multi} tr.dci-em-line[data-line="{ids["drums (drum set)"]}"]', False])
            pg.wait_for_timeout(400)
            d1 = pg.evaluate(BLOCKS, 'Multi Man')
            d_voc = pg.evaluate(BLOCKS, 'Voc Man')
            solo = sec_sel(pg, 'Solo Man')
            grips_of = "(sel) => [...document.querySelectorAll(sel + ' .dci-em-block')].map(b => b.querySelectorAll('.dci-em-grip').length)"
            solo_joined = pg.evaluate(grips_of, solo)
            pg.click(f'{solo} [data-act=em-split]')
            pg.wait_for_timeout(400)
            solo_grips = [solo_joined, pg.evaluate(grips_of, solo)]
            print('D) andere Zeile:', mark_d, roles(d1), roles(d_voc), '| Solo Man ⠿ je Block:', solo_grips)
            results.append(mark_d == '' and roles(d1) == roles(c1) and roles(d_voc) == roles(v0) and solo_grips == [[2], [0, 0]])
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(500)
            e1 = pg.evaluate(CLINES, 'Multi Man')
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(500)
            print('E) kompakt:', [l['chips'] for l in e1['lines']])
            results.append([l['chips'] for l in e1['lines']] == [['drums (drum set) “drums”', 'electric guitar', 'acoustic guitar']])
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate(ADDED)
            names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in JOIN_CREDITS}
            of = lambda n: [sorted(r['attrs']) for r in added if names.get(r['a']) == n or names.get(r['b']) == n]
            print('F) Multi Man:', of('Multi Man'))
            results.append(of('Multi Man') == [['acoustic guitar', 'drums (drum set) [drums]', 'electric guitar']] * 4)
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            g1 = pg.evaluate(BLOCKS, 'Multi Man')
            print('G) neu geladen:', roles(g1))
            results.append(roles(g1) == ['electric guitar', 'acoustic guitar', 'drums (drum set)'])
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# an opened event: level, date, pool, tracks
EVEDIT = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
  const ed = g && g.querySelector('.dci-em-evedit'); if (!ed) return null;
  return { title: ed.querySelector('strong').textContent.trim(), levels: [...ed.querySelectorAll('[data-act=em-evlevel]')].map(b => b.textContent.trim() + (b.getAttribute('aria-pressed') === 'true' ? '*' : '')),
    date: (b => (b ? (() => { const v = (k) => (b.querySelector('[data-f=ed-' + k + ']') || {}).value || ''; const bb = [v('by'), v('bm'), v('bd')].filter(Boolean).join('-');
      const ee = [v('ey'), v('em'), v('ed')].filter(Boolean).join('-'); return bb + (ee && ee !== bb ? ' – ' + ee : ''); })() : undefined))(ed.querySelector('[data-evdate]')), pool: [...ed.querySelectorAll('.dci-em-evpool')].map(b => b.textContent.trim() + (b.getAttribute('aria-pressed') === 'true' ? '*' : '')),
    tracks: [...ed.querySelectorAll('[data-f=em-evtrack]')].filter(c => c.checked).map(c => Number(c.dataset.i)), n: ed.querySelectorAll('[data-f=em-evtrack]').length,
    open: [...g.querySelectorAll('th.dci-em-ev.dci-em-evopen')].map(h => { const c = h.cloneNode(true); c.querySelectorAll('button.dci-em-evdate, .dci-em-evdatebox').forEach(x => x.remove());
      return c.textContent.replace(/\\s+/g, ' ').replace('▾', '').trim(); }) }; }"""


def case_evhead():
    """Credits Importer 3.35.4 (AE-3, on roles MusicBrainz has not on the new level): an event opened below its block.
    A) Part Man: ▸ in the head of ② (piano, track 2) opens it – "Event ② – … all its rows (1)", the levels of its types
       (here Recording only – the test's MusicBrainz has instruments on recordings only – and [3.44.0] Skip), the date field, the dates of the
       pool, the tracks with track 2 ticked; the head marked.
    B) Track 3 ticked: ② on tracks 2–3, still open, the focus on the box; both boxes taken off one after the other – the last
       one stays with a message (an event needs a track).
    C) "All": piano on all 4 tracks – the same event as electric guitar (①): one event, the opened one follows (2 rows).
    D) A date typed ("2024-03"): both rows have it, a date of the pool; "no date": without; the date of the pool chosen: with it.
    E) Level Man ("Producer" on the recordings ①, "Mastered By" on the release ②): ① to Release – the producer joins
       mastering's event (one event, 2 rows, the opened event follows); back to Recording – the producer moves (all tracks),
       mastering stays with the note "Mastered By stays on the level Release: MusicBrainz has no “mastering” on the level
       Recording"; "ok" takes the note away.
    F) ✕ in the opened event closes it.
    G) Staged: Part Man – piano and electric guitar together on the 4 recordings with the date 2024-03."""
    orig, rel0 = join_release()
    extra = [('Level Man', 'Producer', 3075, ''), ('Level Man', 'Mastered By', 3075, '')]
    H.ARTISTS[3075] = (H.uid('dddddddd', 3075 - 2990), 'Level Man')

    def rel():
        d = rel0()
        d['extraartists'] += [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in extra]
        return d
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            part = sec_sel(pg, 'Part Man')
            p0 = pg.evaluate(BLOCKS, 'Part Man')
            pg.click(f'{part} th.dci-em-ev >> nth=1 >> [data-act=em-evopen]')
            pg.wait_for_timeout(400)
            a1 = pg.evaluate(EVEDIT, 'Part Man')
            print('A) vorher:', p0[0]['ev'] if p0 else None, '| offen:', a1)
            results.append(bool(a1) and a1['title'] == 'Event ② – what you set here goes for all its rows (1)' and a1['levels'] == ['Recording*', 'Skip']
                           and a1['date'] == '' and a1['tracks'] == [1] and a1['n'] == 4 and a1['open'] == ['② Recording track 2'])
            pg.click(f'{part} .dci-em-evedit [data-f=em-evtrack][data-i="2"]')
            pg.wait_for_timeout(400)
            b1 = pg.evaluate(EVEDIT, 'Part Man')
            focus = pg.evaluate("(() => { const a = document.activeElement; return a && a.dataset ? a.dataset.f + ':' + a.dataset.i : ''; })()")
            pg.click(f'{part} .dci-em-evedit [data-f=em-evtrack][data-i="1"]')
            pg.wait_for_timeout(400)
            pg.click(f'{part} .dci-em-evedit [data-f=em-evtrack][data-i="2"]')
            pg.wait_for_timeout(400)
            b2 = pg.evaluate(EVEDIT, 'Part Man')
            msg = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent).join(' | ')")
            print('B) Track 3:', b1['tracks'] if b1 else None, '| Fokus:', focus, '| letzter:', b2['tracks'] if b2 else None, '| Meldung:', 'at least one track' in msg)
            results.append(bool(b1) and b1['tracks'] == [1, 2] and focus == 'em-evtrack:2' and bool(b2) and b2['tracks'] == [2] and 'at least one track' in msg)
            pg.click(f'{part} .dci-em-evedit [data-act=em-evall]')
            pg.wait_for_timeout(400)
            c1 = pg.evaluate(EVEDIT, 'Part Man')
            c1b = pg.evaluate(BLOCKS, 'Part Man')
            print('C) alle:', c1, '| Ereignisse:', c1b[0]['ev'] if c1b else None)
            results.append(bool(c1) and c1['title'].endswith('(2)') and c1['tracks'] == [0, 1, 2, 3] and c1b[0]['ev'] == ['① Recording all 4 tracks'])
            H.ev_date(pg, part, '2024-03', inline=True)
            pg.wait_for_timeout(500)
            d1 = pg.evaluate(EVEDIT, 'Part Man')
            pg.click(f'{part} .dci-em-evedit [data-act=em-evpool][data-id=""]')
            pg.wait_for_timeout(400)
            d2 = pg.evaluate(EVEDIT, 'Part Man')
            pg.click(f'{part} .dci-em-evedit .dci-em-evpool:has-text("2024-03")')
            pg.wait_for_timeout(400)
            d3 = pg.evaluate(EVEDIT, 'Part Man')
            print('D) Datum:', d1['date'] if d1 else None, d1['pool'] if d1 else None, '| ohne:', d2['date'] if d2 else None, '| Pool:', d3['date'] if d3 else None, d3['pool'] if d3 else None)
            results.append(bool(d1) and d1['date'] == '2024-03' and any(x.endswith('*') for x in d1['pool']) and bool(d2) and d2['date'] == ''
                           and bool(d3) and d3['date'] == '2024-03' and d3['title'].endswith('(2)'))
            lvl = sec_sel(pg, 'Level Man')
            e0 = pg.evaluate(BLOCKS, 'Level Man')
            pg.click(f'{lvl} th.dci-em-ev >> nth=0 >> [data-act=em-evopen]')
            pg.wait_for_timeout(400)
            e1 = pg.evaluate(EVEDIT, 'Level Man')
            pg.click(f'{lvl} .dci-em-evedit [data-act=em-evlevel][data-level=release]')
            pg.wait_for_timeout(400)
            e2 = pg.evaluate(EVEDIT, 'Level Man')
            e2b = pg.evaluate(BLOCKS, 'Level Man')
            pg.click(f'{lvl} .dci-em-evedit [data-act=em-evlevel][data-level=recording]')
            pg.wait_for_timeout(400)
            e3 = pg.evaluate(EVEDIT, 'Level Man')
            kept = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' .dci-em-kept')].map(k => k.textContent.replace(/\\s+/g, ' ').trim())", lvl)
            pg.click(f'{lvl} [data-act=em-keptok]')
            pg.wait_for_timeout(300)
            kept2 = pg.evaluate("(sel) => document.querySelectorAll(sel + ' .dci-em-kept').length", lvl)
            print('E) vorher:', e0[0]['ev'] if e0 else None, '| offen:', e1, '| Release:', e2, e2b[0]['ev'] if e2b else None,
                  '| zurück:', e3, '| Hinweis:', kept, kept2)
            results.append(bool(e1) and e1['title'].endswith('(1)') and e1['levels'] == ['Recording*', 'Release', 'Skip']
                           and bool(e2) and e2['title'].endswith('(2)') and e2['levels'] == ['Recording', 'Release*', 'Skip'] and e2b[0]['ev'] == ['① Release']
                           and bool(e3) and e3['levels'] == ['Recording*', 'Release', 'Skip'] and e3['tracks'] == [0, 1, 2, 3] and e3['title'].endswith('(1)')
                           and kept == ['Mastered By stays on the level Release: MusicBrainz has no “mastering” on the level Recording ok'] and kept2 == 0)
            pg.click(f'{lvl} .dci-em-evedit [data-act=em-evopen]')
            pg.wait_for_timeout(300)
            f1 = pg.evaluate(EVEDIT, 'Level Man')
            print('F) zu:', f1)
            results.append(f1 is None)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate(ADDED_D)
            pm = H.uid('dddddddd', 3074 - 2990)
            mine = sorted((r['date'], tuple(r['attrs'])) for r in added if pm in (r['a'], r['b']))
            print('G) Part Man:', mine)
            results.append(mine == [('2024-3', ('electric guitar', 'piano'))] * 4)
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_evdatefields():
    """Credits Importer 3.42.1 (collected item Z-EDM; Q-db): the date in the head of an event of an entry's matrix as MusicBrainz
    has it. Solo Man's ① (no date):
    A) The head shows "no date" as a button (until 3.42.0 a text field); clicked: below it the fields Begin and End (year, month,
       day) and "ended", "⇣" (the begin into the end), "Apply", "no date", ✕.
    B) Begin 2001-03-02, End 2001-03-20, Apply: the head shows "2001-03-02 – 2001-03-20", the rows have the date (a new date of the
       pool); opened again: the fields hold it.
    C) Month 13: "Apply" says what is wrong, nothing changes. "2004-05-06 – 2004-05-09" pasted into the year of Begin: the fields of
       begin and end filled. ✕ closes the fields.
    D) "no date": the event without a date again.
    E) (3.42.8, review) Another entry's event below (its fields there) shows nothing typed in Solo Man's head – the events share their
       key; an error in the fields below opens no second box in the head."""
    orig, rel = join_release()
    H.discogs_release = rel
    BOX = """(sel) => { const b = document.querySelector(sel + ' th.dci-em-ev [data-evdate]'); if (!b) return null; const v = (k) => (b.querySelector('[data-f=ed-' + k + ']') || {}).value;
      return { f: ['by', 'bm', 'bd', 'ey', 'em', 'ed'].map(v), ended: !!b.querySelector('[data-f=ed-ended]'), btns: [...b.querySelectorAll('button')].map(x => x.dataset.act),
        err: (b.querySelector('[data-el=evdate-error]') || {}).textContent || '' }; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            solo = sec_sel(pg, 'Solo Man')
            btn = f'{solo} th.dci-em-ev button.dci-em-evdate'
            a0 = [pg.evaluate("(s) => document.querySelector(s).textContent.trim()", btn), pg.evaluate(BOX, solo)]
            pg.click(btn); pg.wait_for_timeout(250)
            a1 = [pg.evaluate("(s) => document.querySelector(s).getAttribute('aria-expanded')", btn), pg.evaluate(BOX, solo)]
            print('A)', a0, a1)
            results.append(a0 == ['no date', None] and a1[0] == 'true' and a1[1] and a1[1]['f'] == [''] * 6 and a1[1]['ended']
                           and a1[1]['btns'] == ['ed-copy', 'em-evdate-apply', 'em-evdate-clear', 'em-evdate-open'])
            # "⇣" copies the begin into the end
            pg.fill(f'{solo} th.dci-em-ev [data-evdate] [data-f=ed-by]', '1999')
            pg.click(f'{solo} th.dci-em-ev [data-evdate] [data-act=ed-copy]'); pg.wait_for_timeout(150)
            results.append(pg.evaluate(BOX, solo)['f'][3] == '1999')
            box = f'{solo} th.dci-em-ev [data-evdate]'
            for k, v in (('by', '2001'), ('bm', '03'), ('bd', '02'), ('ey', '2001'), ('em', '03'), ('ed', '20')):
                pg.fill(f'{box} [data-f=ed-{k}]', v)
            pg.click(f'{box} [data-act=em-evdate-apply]'); pg.wait_for_timeout(400)
            b0 = [pg.evaluate(H.EV_DATES, solo), pg.evaluate(BOX, solo), pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /2001-03-02 – 2001-03-20/.test(t)).length")]
            pg.click(btn); pg.wait_for_timeout(250)
            b1 = pg.evaluate(BOX, solo)
            print('B)', b0, b1)
            results.append(b0[0] == ['2001-03-02 – 2001-03-20'] and b0[1] is None and b0[2] == 1 and b1 and b1['f'] == ['2001', '03', '02', '2001', '03', '20'])
            pg.fill(f'{box} [data-f=ed-bm]', '13')
            pg.click(f'{box} [data-act=em-evdate-apply]'); pg.wait_for_timeout(300)
            c0 = [pg.evaluate(BOX, solo), pg.evaluate(H.EV_DATES, solo)]
            pg.evaluate("""([sel, text]) => { const el = document.querySelector(sel); const dt = new DataTransfer(); dt.setData('text', text);
              el.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); }""", [f'{box} [data-f=ed-by]', '2004-05-06 – 2004-05-09'])
            pg.wait_for_timeout(200)
            c1 = pg.evaluate(BOX, solo)
            pg.click(f'{box} [data-act=em-evdate-open]'); pg.wait_for_timeout(250)
            c2 = pg.evaluate(BOX, solo)
            print('C)', c0, '| eingefügt:', c1 and c1['f'], '| ✕:', c2)
            results.append(c0[0] and c0[0]['err'] and c0[1] == ['2001-03-02 – 2001-03-20'] and c1 and c1['f'] == ['2004', '05', '06', '2004', '05', '09'] and c2 is None)
            pg.click(btn); pg.wait_for_timeout(250)
            pg.click(f'{box} [data-act=em-evdate-clear]'); pg.wait_for_timeout(400)
            d0 = pg.evaluate(H.EV_DATES, solo)
            print('D)', d0)
            results.append(d0 == [''])
            # E) (3.42.8, review) what was typed in one entry's box is no other entry's: Multi Man's ① opened below (its fields there), an
            # error in Solo Man's head; an error in the fields below opens no second box in the head
            multi = sec_sel(pg, 'Multi Man')
            pg.click(f'{multi} th.dci-em-ev >> nth=0 >> [data-act=em-evopen]'); pg.wait_for_timeout(300)
            pg.click(btn); pg.wait_for_timeout(250)
            pg.fill(f'{box} [data-f=ed-by]', '2001')
            pg.fill(f'{box} [data-f=ed-bm]', '13')
            pg.click(f'{box} [data-act=em-evdate-apply]'); pg.wait_for_timeout(300)
            INL = """(sel) => { const b = document.querySelector(sel + ' .dci-em-evdatebox-inline'); return b ? { by: b.querySelector('[data-f=ed-by]').value, err: (b.querySelector('[data-el=evdate-error]') || {}).textContent || '' } : null; }"""
            e0 = [pg.evaluate(BOX, solo), pg.evaluate(INL, multi)]
            pg.fill(f'{multi} .dci-em-evdatebox-inline [data-f=ed-by]', '2001')
            pg.fill(f'{multi} .dci-em-evdatebox-inline [data-f=ed-bm]', '14')
            pg.click(f'{multi} .dci-em-evdatebox-inline [data-act=em-evdate-apply]'); pg.wait_for_timeout(300)
            e1 = [pg.evaluate(INL, multi), pg.evaluate("(sel) => document.querySelectorAll(sel + ' [data-evdate]').length", multi), pg.evaluate(BOX, multi)]
            print('E) Solo Man (Kopf):', e0[0] and e0[0]['err'], '| Multi Man unten:', e0[1], '| Fehler unten:', e1)
            results.append(e0[0] and e0[0]['err'] and e0[1] == {'by': '', 'err': ''} and e1[0] and e1[0]['err'] and e1[0]['by'] == '2001' and e1[1] == 1 and e1[2] is None)
            # F) (3.43.3, full review P4) "from 2015 to ????" pasted into the year of Begin ticks "ended" (it was skipped); a begin-only date
            # with "ended" is not the pool's entry of the same year without it (the pool entry was reused, its "ended" taken)
            pg.evaluate("""([sel, text]) => { const el = document.querySelector(sel); const dt = new DataTransfer(); dt.setData('text', text);
              el.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true })); }""", [f'{box} [data-f=ed-by]', 'from 2015 to ????'])
            pg.wait_for_timeout(200)
            f0 = pg.evaluate(f"(() => {{ const b = document.querySelector('{box}'); return [b.querySelector('[data-f=ed-by]').value, b.querySelector('[data-f=ed-ended]').checked]; }})()")
            for k, v in (('by', '1998'), ('bm', ''), ('bd', ''), ('ey', ''), ('em', ''), ('ed', '')):
                pg.fill(f'{box} [data-f=ed-{k}]', v)
            pg.evaluate(f"document.querySelector('{box} [data-f=ed-ended]').checked = false")
            pg.click(f'{box} [data-act=em-evdate-apply]'); pg.wait_for_timeout(400)
            pg.fill(f'{multi} .dci-em-evdatebox-inline [data-f=ed-by]', '1998')
            pg.fill(f'{multi} .dci-em-evdatebox-inline [data-f=ed-bm]', '')
            pg.evaluate(f"document.querySelector('{multi} .dci-em-evdatebox-inline [data-f=ed-ended]').checked = true")
            pg.click(f'{multi} .dci-em-evdatebox-inline [data-act=em-evdate-apply]'); pg.wait_for_timeout(400)
            f1 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /1998/.test(t))")
            f2 = pg.evaluate("(() => { const pool = JSON.parse(localStorage.getItem('dci-date-pool:aaaaaaaa-1111-4111-8111-000000000001') || '[]'); return pool.filter(d => d.begin && d.begin.year === 1998).map(d => !!d.ended); })()")
            print('F) eingefügt „from 2015 to ????“:', f0, '| Pool 1998:', f1, '| ended:', f2)
            results.append(f0 == ['2015', True] and len(f1) == 2 and sorted(f2) == [False, True])
            print('Fehler:', errs)
            results.append(not errs)
        finally:
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_companies():
    """Credits Importer 3.35.5 (AE-4): companies and places as a matrix when a row of theirs offers a date and/or tracks.
    A) The test release: Abbey Road Studios (a place, "Recorded At" on the 4 recordings) – a matrix: a block "recorded at"
       ([Q-c] 3.38.14; its tooltip "from Discogs: Recorded At"; until 3.38.13 "Recorded At → recorded at"), ① Recording all 4 tracks, ticked; Sony ("Phonographic Copyright (p)", a label on the release) – a matrix,
       ① Release (3.69.0, S101: without "whole release").
    B) Pub Co ("Published By" on the works): its rows as before (no matrix – nothing on it offers a date or tracks).
    C) ☰ compact: Abbey Road Studios a line "① Recording no date all 4 tracks" with the chip "recorded at".
    D) Staged: the relationships of the companies and places the same as in the legacy view.
    E) A date typed into the head of Abbey Road's event (2001-03): staged "recorded at" on the 4 recordings with it."""
    results = []
    with sync_playwright() as p:
        H.BROWSER = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx, pg, errs, leg, _label = staged_by(None, 'legacy')
            ctx.close()
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(H.BROWSER)
            pg, errs2 = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            kind = "(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name); return g ? [g.classList.contains('dci-em-entry'), g.querySelectorAll('tr.dci-row').length] : null; }"
            abbey = pg.evaluate(BLOCKS, 'Abbey Road Studios')
            sony = pg.evaluate(BLOCKS, 'Sony')
            k_abbey, k_sony, k_pub = pg.evaluate(kind, 'Abbey Road Studios'), pg.evaluate(kind, 'Sony'), pg.evaluate(kind, 'Pub Co')
            print('A) Abbey Road:', k_abbey, abbey, '| Sony:', k_sony, sony)
            results.append(k_abbey == [True, 0] and bool(abbey) and len(abbey) == 1 and abbey[0]['head'] == 'recorded at' and abbey[0]['tip'] == 'from Discogs: Recorded At'
                           and abbey[0]['ev'] == ['① Recording all 4 tracks'] and abbey[0]['lines'][0]['ticks'] == [True]
                           and k_sony == [True, 0] and bool(sony) and sony[0]['ev'] == ['① Release'] and sony[0]['lines'][0]['ticks'] == [True])
            print('B) Pub Co:', k_pub)
            results.append(bool(k_pub) and k_pub[0] is False and k_pub[1] >= 1)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(500)
            c_abbey = pg.evaluate(CLINES, 'Abbey Road Studios')
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(500)
            print('C) kompakt:', c_abbey)
            results.append(bool(c_abbey) and c_abbey['compact'] and [(l['head'], l['chips']) for l in c_abbey['lines']] == [('① Recording no date all 4 tracks', ['recorded at'])])
            ids = {v[1] for v in H.COMPANIES.values()}
            comp = lambda rels: sorted((r['lt'], r['a'], r['b'], tuple(r['attrs'])) for r in rels if r['a'] in ids or r['b'] in ids)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            mx = pg.evaluate(ADDED)
            print('D) Firmen:', len(comp(mx)), '| legacy:', len(comp(leg)), '| gleich:', comp(mx) == comp(leg))
            results.append(len(comp(leg)) > 0 and comp(mx) == comp(leg))
            ctx.close()
            # E) a date for the place
            ctx = H.new_context(H.BROWSER)
            pg, errs3 = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            sec = sec_sel(pg, 'Abbey Road Studios')
            H.ev_date(pg, sec, '2001-03')
            pg.wait_for_timeout(600)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            dd = pg.evaluate(ADDED_D)
            place = H.uid('eeeeeeee', 2)
            mine = sorted(r['date'] for r in dd if place in (r['a'], r['b']))
            print('E) recorded at:', mine)
            results.append(mine == ['2001-3'] * 4)
            print('Fehler:', errs, errs2, errs3)
            results.append(not errs and not errs2 and not errs3)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.BROWSER.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_remember():
    """Credits Importer 3.36.0 (146): the matrix of a remembered release after the
    page is loaded again (⚙ Settings → Cache on): Multi Man's lines in the order dragged (drums first), Part Man's event ② on the
    tracks set in the opened event (2–3), Solo Man "One row each" – all as before; staged the same (20)."""
    H.REMEMBER = True
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    sl = lambda bl: [(x['head'], x['ev'], [l['role'] for l in x['lines']]) for x in (bl or [])]
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())

            def load():
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                pg.wait_for_timeout(1500)
            load()
            multi = sec_sel(pg, 'Multi Man')
            ids = {l['role']: l['line'] for l in pg.evaluate(BLOCKS, 'Multi Man')[0]['lines']}
            pg.evaluate(DROP_AT, [f'{multi} tr.dci-em-line[data-line="{ids["drums (drum set)"]}"] .dci-em-grip', f'{multi} tr.dci-em-line[data-line="{ids["electric guitar"]}"]', False])
            pg.wait_for_timeout(300)
            part = sec_sel(pg, 'Part Man')
            pg.click(f'{part} th.dci-em-ev >> nth=1 >> [data-act=em-evopen]')
            pg.wait_for_timeout(300)
            pg.click(f'{part} .dci-em-evedit [data-f=em-evtrack][data-i="2"]')
            pg.wait_for_timeout(300)
            pg.click(f'{sec_sel(pg, "Solo Man")} [data-act=em-split]')
            pg.wait_for_timeout(1600)
            before = [sl(pg.evaluate(BLOCKS, n)) for n in ('Multi Man', 'Part Man', 'Solo Man')]
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            load()
            after = [sl(pg.evaluate(BLOCKS, n)) for n in ('Multi Man', 'Part Man', 'Solo Man')]
            print('vorher:', before)
            print('nachher:', after)
            results.append(before == after and before[0][0][2][0] == 'drums (drum set)' and before[1][0][1][1] == '② Recording tracks 2, 3' and len(before[2]) == 2)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            n = len(pg.evaluate(ADDED))
            print('gestaged:', n)
            results.append(n == 20)
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_flagcols():
    """Credits Importer 3.36.6 (collected item 148; with a screenshot of "add. guestsolo" over three checkboxes): in the
    full matrix each attribute of the lines (add., guest, solo …) is a column of its own – its word centred over the checkboxes of
    every line (±2 px), not wider
    than its cell, at 100 % and at the largest text size (A+ ×3); until 3.36.5 one cell with fixed widths: the checkboxes 4, 11
    and 18 px to the right of their words. [Z-ALIGN] (3.100.0) with "Attributes: separate" (Variante B)."""
    H.ENTRIES_VIEW = 'matrix'
    orig, rel = join_release()
    H.discogs_release = rel
    CHECK = """(() => { const out = []; for (const tbl of document.querySelectorAll('.dci-em-grid')) {
      const ths = [...tbl.querySelectorAll('thead th')]; const idx = ths.map((t, i) => [t, i]).filter(([t]) => t.classList.contains('dci-em-c-flag') && t.textContent.trim());
      for (const [th, i] of idx) { const r = th.getBoundingClientRect(); const rg = document.createRange(); rg.selectNodeContents(th); const w = rg.getBoundingClientRect();
        const boxes = [...tbl.querySelectorAll('tbody tr.dci-em-line')].map(tr => tr.children[i] && tr.children[i].querySelector('input[type=checkbox]')).filter(Boolean);
        out.push({ word: th.textContent.trim(), off: boxes.map(b => { const q = b.getBoundingClientRect(); return Math.round((q.left + q.width / 2 - (w.left + w.width / 2)) * 10) / 10; }),
          fits: w.width <= r.width + 0.5, n: boxes.length }); } } return out; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1000)
            # [Z-ALIGN] (3.100.0) a column per attribute: "Attributes: separate" (default: together in one column)
            pg.click('[data-act=em-attr][data-attr=split] >> nth=0')
            pg.wait_for_timeout(500)
            a1 = pg.evaluate(CHECK)
            for _ in range(3):
                pg.click('[data-act=zoom-in]')
                pg.wait_for_timeout(200)
            pg.wait_for_timeout(300)
            a2 = pg.evaluate(CHECK)
            for _ in range(3):
                pg.click('[data-act=zoom-out]')
            print('100 %:', a1)
            print('A+ ×3:', a2)
            ok = lambda a: a and all(x['n'] and x['fits'] and all(abs(o) <= 2 for o in x['off']) for x in a) and {'add.', 'guest', 'solo'} <= {x['word'] for x in a}
            results.append(ok(a1) and ok(a2))
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_chipask():
    """Credits Importer 3.37.14 (collected item 163): in an entry compact as a
    matrix a chip with a question has ▾ – its answers below it.
    A) "Bass" (Q001): "? bass" with ▾ – electric bass guitar · double bass · acoustic bass guitar ([3.97.0] · bass guitar); "double bass" chosen: the
       chip "double bass “bass”" without "?" and without ▾, the list closed, all rows of the line double bass.
    B) "Taischigoto" (no instrument of MusicBrainz): "? Taischigoto" ▾ – taishōgoto · other instruments “taischigoto” ·
       miscellaneous support …; Esc closes the list (the focus back on ▾); taishōgoto chosen: "taishōgoto “taischigoto”".
    C) "Directed By" (Q003): ▾ – conductor · chorus master · …; conductor chosen: no "?".
    D) The chip's name still opens the full matrix."""
    H.ENTRIES_VIEW = 'matrix'
    H.attr(9151, 'taishōgoto', 14, 14)
    H.attr(9124, 'other instruments', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CREDITS = [('Low Man', 'Bass, Taischigoto', 3081), ('Drum Guy', 'Directed By', 3082)]
    for n, _r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    CHIPS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [...g.querySelectorAll('.dci-em-cl .dci-em-chip')].map(c => ({ name: c.querySelector('.dci-em-chipname').textContent.replace(/\\s+/g, ' ').trim(),
        q: !!c.querySelector('[data-act=em-chipask]'), menu: [...c.querySelectorAll('.dci-em-chipmenu button')].map(b => b.textContent.trim()), line: c.dataset.line,
        rows: c.dataset.rows })) : null; }"""
    ROWS = "(ids) => ids.split(',').map(id => { const r = (window.__dciRows || []).find(x => x.id === id); return r || id; })"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            low = sec_sel(pg, 'Low Man')
            a0 = pg.evaluate(CHIPS, 'Low Man')
            bass = next((c for c in a0 or [] if c['name'].startswith('? bass')), None)
            if bass:
                pg.click(f'{low} .dci-em-chip[data-line="{bass["line"]}"] [data-act=em-chipask]')
                pg.wait_for_timeout(400)
            a1 = pg.evaluate(CHIPS, 'Low Man')
            focus = pg.evaluate("(document.activeElement && document.activeElement.closest('.dci-em-chipmenu')) ? document.activeElement.textContent.trim() : ''")
            vis = pg.evaluate("""(() => { const m = document.querySelector('.dci-em-chipmenu'); if (!m) return null; const r = m.getBoundingClientRect();
              const e = document.elementFromPoint(r.left + 8, r.top + r.height / 2); return !!(e && m.contains(e)); })()""")
            if bass:
                pg.click(f'{low} .dci-em-chipmenu [data-act=instr-pick][data-instr="double bass"]')
                pg.wait_for_timeout(500)
            a2 = pg.evaluate(CHIPS, 'Low Man')
            bass2 = next((c for c in a2 or [] if 'double bass' in c['name']), None)
            print('A) vorher:', a0, '| ▾:', a1, focus, vis, '| double bass:', a2)
            results.append(bool(bass) and bass['q'] and [c['menu'] for c in a1 if c['line'] == bass['line']][0] == ['electric bass guitar', 'double bass', 'acoustic bass guitar', 'bass guitar']
                           and focus == 'electric bass guitar' and vis is True
                           and bool(bass2) and bass2['name'] == 'double bass “bass”' and not bass2['q'] and not bass2['menu'] and not any(c['menu'] for c in a2))
            # B) Taischigoto, Esc
            tai = next((c for c in a2 or [] if c['name'].startswith('? Taischigoto')), None)
            if tai:
                pg.click(f'{low} .dci-em-chip[data-line="{tai["line"]}"] [data-act=em-chipask]')
                pg.wait_for_timeout(400)
            b1 = pg.evaluate(CHIPS, 'Low Man')
            pg.keyboard.press('Escape')
            pg.wait_for_timeout(400)
            b2 = pg.evaluate(CHIPS, 'Low Man')
            open_dash = pg.evaluate("!!document.querySelector('#dci-overlay') && !document.querySelector('#dci-overlay').hidden")
            back = pg.evaluate("(document.activeElement || {}).dataset ? document.activeElement.dataset.act : ''")
            if tai:
                pg.click(f'{low} .dci-em-chip[data-line="{tai["line"]}"] [data-act=em-chipask]')
                pg.wait_for_timeout(400)
                pg.click(f'{low} .dci-em-chipmenu [data-act=instr-pick][data-instr="taishōgoto"]')
                pg.wait_for_timeout(500)
            b3 = pg.evaluate(CHIPS, 'Low Man')
            menu_b = [c['menu'] for c in b1 if tai and c['line'] == tai['line']]
            print('B) ▾:', menu_b, '| Esc:', [c['menu'] for c in b2], open_dash, back, '| taishōgoto:', b3)
            results.append(bool(tai) and menu_b and menu_b[0][:2] == ['taishōgoto', 'other instruments “taischigoto”'] and menu_b[0][-1].startswith('miscellaneous support')
                           and not any(c['menu'] for c in b2) and open_dash and back == 'em-chipask'
                           and any(c['name'] == 'taishōgoto “taischigoto”' and not c['q'] for c in b3))
            # C) Directed By
            dg = sec_sel(pg, 'Drum Guy')
            c0 = pg.evaluate(CHIPS, 'Drum Guy')
            if c0:
                pg.click(f'{dg} .dci-em-chip [data-act=em-chipask]')
                pg.wait_for_timeout(400)
            c1 = pg.evaluate(CHIPS, 'Drum Guy')
            if c1 and c1[0]['menu']:
                pg.click(f'{dg} .dci-em-chipmenu [data-act=type-pick][data-opt="0"]')
                pg.wait_for_timeout(500)
            c2 = pg.evaluate(CHIPS, 'Drum Guy')
            print('C) Directed By:', c0, '| ▾:', c1, '| conductor:', c2)
            results.append(bool(c0) and c0[0]['name'].startswith('? ') and c0[0]['q'] and c1[0]['menu'][:2] == ['conductor', 'chorus master']
                           and bool(c2) and not c2[0]['name'].startswith('? ') and not c2[0]['q'])
            # D) the chip's name opens the full matrix
            pg.click(f'{low} .dci-em-chipname >> nth=0')
            pg.wait_for_timeout(500)
            wide = pg.evaluate("(sel) => !!document.querySelector(sel + ' tr.dci-em-line')", low)
            print('D) volle Matrix:', wide)
            results.append(wide)
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_chipinfo():
    """Credits Importer 3.38.6 (collected item 163b): a chip whose
    note has its answer applied has a small grey ⓘ after its name, the note as its tooltip – none while a question is open ("?").
    A) Before answering: "? bass", "? Taischigoto", "? Directed By" without ⓘ; "Buddha Machine" (none is like it, set to other
       instruments) with ⓘ – "“Buddha Machine” is no instrument of MusicBrainz, and none is like it: other instruments “Buddha
       machine”" (grey, right after the name).
    B) taishōgoto chosen: ⓘ "“Taischigoto” is no instrument of MusicBrainz – chosen: taishōgoto", "A spelling of its own: credited
       “taischigoto”." and "Written small – unknown to MusicBrainz: Taischigoto → taischigoto", a line each; double bass (Q001): no ⓘ
       (no note).
    C) conductor chosen for "Directed By": ⓘ "“Directed By” – chosen: conductor"."""
    H.ENTRIES_VIEW = 'matrix'
    H.attr(9151, 'taishōgoto', 14, 14)
    H.attr(9124, 'other instruments', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CREDITS = [('Low Man', 'Bass, Taischigoto, Buddha Machine', 3081), ('Drum Guy', 'Directed By', 3082)]
    for n, _r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    CHIPS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [...g.querySelectorAll('.dci-em-cl .dci-em-chip')].map(c => { const i = c.querySelector('.dci-em-chipinfo');
        return { name: c.querySelector('.dci-em-chipname').textContent.replace(/\\s+/g, ' ').trim(), line: c.dataset.line,
          info: i ? i.title : null, color: i ? getComputedStyle(i).color : null, after: i ? i.previousElementSibling.classList.contains('dci-em-chipname') : null }; }) : null; }"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            low, dg = sec_sel(pg, 'Low Man'), sec_sel(pg, 'Drum Guy')
            a = pg.evaluate(CHIPS, 'Low Man') + pg.evaluate(CHIPS, 'Drum Guy')
            for c in a:
                print('A)', c)
            by = lambda cs, start: next((c for c in cs if c['name'].startswith(start)), None)
            bud = by(a, 'other instruments') or by(a, 'Buddha') or by(a, 'buddha')
            ok_a = all(by(a, x) and by(a, x)['info'] is None for x in ('? bass', '? Taischigoto', '? ')) and bool(bud) and bool(bud['info']) \
                and bud['info'] == '“Buddha Machine” is no instrument of MusicBrainz, and none is like it: other instruments “Buddha machine”' \
                and bud['color'] == 'rgb(109, 106, 124)' and bud['after']
            # B)
            tai = by(a, '? Taischigoto')
            bass = by(a, '? bass')
            for c, instr in ((tai, 'taishōgoto'), (bass, 'double bass')):
                if c:
                    pg.click(f'{low} .dci-em-chip[data-line="{c["line"]}"] [data-act=em-chipask]'); pg.wait_for_timeout(400)
                    pg.click(f'{low} .dci-em-chipmenu [data-act=instr-pick][data-instr="{instr}"]'); pg.wait_for_timeout(500)
            b1 = pg.evaluate(CHIPS, 'Low Man')
            print('B)', b1)
            t2, b2 = by(b1, 'taishōgoto'), by(b1, 'double bass')
            ok_b = bool(t2) and t2['info'] == ('“Taischigoto” is no instrument of MusicBrainz – chosen: taishōgoto\nA spelling of its own: credited “taischigoto”.\n'
                                               'Written small – unknown to MusicBrainz: Taischigoto → taischigoto') \
                and bool(b2) and b2['info'] is None
            # C)
            pg.click(f'{dg} .dci-em-chip [data-act=em-chipask]'); pg.wait_for_timeout(400)
            pg.click(f'{dg} .dci-em-chipmenu [data-act=type-pick][data-opt="0"]'); pg.wait_for_timeout(500)
            c1 = pg.evaluate(CHIPS, 'Drum Guy')
            print('C)', c1)
            ok_c = bool(c1) and c1[0]['info'] == '“Directed By” – chosen: conductor'
            print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
            results += [ok_a, ok_b, ok_c]
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_barroom():
    """Credits Importer 3.40.8 (collected item Z-SB): a scroll bar drawn over the content (overlay scroll bars of macOS and
    Windows 11; here Chromium's FluentOverlayScrollbar) no longer covers the last line of the matrix – "written “Drums”"
    below the role field of Multi Man.
    A) A wide dashboard: the block fits, no room added.
    B) A narrow one (700 px): the block scrolls sideways, its bar takes no room – 16 px below the last line, the line
       "written “Drums”" above the bar; (review) only boxes that scroll get it; wide again: the room goes.
    C) A classic scroll bar (it takes room of its own): no room added, the line above the bar anyway."""
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    INFO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      const s = g.querySelector('.dci-em-scroll'); const r = s.getBoundingClientRect(); const raw = [...s.querySelectorAll('.dci-em-raw')].pop();
      return { over: s.scrollWidth > s.clientWidth + 1, own: s.offsetHeight - s.clientHeight, room: s.classList.contains('dci-barroom'), pad: getComputedStyle(s).paddingBottom,
        raw: raw ? raw.textContent.trim() : '', free: Math.round(r.bottom - raw.getBoundingClientRect().bottom) }; }"""
    try:
        H.ENTRIES_VIEW = 'matrix'
        for mode in ('overlay', 'classic'):
            args = list(H.LAUNCH_ARGS) + (['--enable-features=FluentOverlayScrollbar'] if mode == 'overlay' else [])
            b = launch_own(args=args, ignore_default_args=['--hide-scrollbars'])
            try:
                ctx = H.new_context(b)
                pg, errs = H.open_mb_edit(ctx, companion=False)
                pg.on('dialog', lambda d: d.accept())
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                pg.wait_for_timeout(1000)
                wide = pg.evaluate(INFO, 'Multi Man')
                pg.set_viewport_size({'width': 700, 'height': 1000})
                pg.wait_for_timeout(600)
                narrow = pg.evaluate(INFO, 'Multi Man')
                # (3.40.8, review) only boxes that scroll sideways get the room (the rows of an entry in a .dci-rowswrap do not scroll)
                scrolls = pg.evaluate("[...document.querySelectorAll('.dci-barroom')].map(e => getComputedStyle(e).overflowX)")
                pg.set_viewport_size({'width': 1500, 'height': 1000})
                pg.click('[data-act=window-reset]')
                pg.wait_for_timeout(600)
                again = pg.evaluate(INFO, 'Multi Man')
                print(f'{mode}: breit:', wide, '\n   schmal:', narrow, '| mit Platz:', scrolls, '\n   wieder breit:', again, '| Fehler:', errs)
                if mode == 'overlay':
                    results.append(not wide['over'] and not wide['room'] and wide['pad'] == '0px')
                    results.append(narrow['over'] and narrow['own'] == 0 and narrow['room'] and narrow['pad'] == '16px' and narrow['raw'] == 'written “Drums”' and narrow['free'] >= 16
                                   and bool(scrolls) and all(x in ('auto', 'scroll') for x in scrolls))
                    results.append(not again['room'] and again['pad'] == '0px')
                else:
                    results.append(narrow['over'] and narrow['own'] >= 10 and not narrow['room'] and narrow['pad'] == '0px' and narrow['free'] >= narrow['own'])
                results.append(not errs)
            finally:
                b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_compactside():
    """Credits Importer 3.40.10 (collected item Z-KH, mockup C; Q-bi, Q-bk, Q-bf): a compact entry lower – "by event | by role" at
    the right of its head; the relationships to stage, "Writing credits: in the works matrix" (its tooltip the whole sentence) and
    the button "＋ Another role for …" in a column beside its lines (until 3.40.9 three lines below them and the toggle a line of
    its own).
    A) Barry Guy (double bass, composer): the toggle in the head, no line of its own; the column right of the lines, at their
       height; no link "+ Another role" below.
    B) by role: the lines per role, the column the same.
    C) "＋ Another role for Barry Guy" ((3.73.0, Z-ARL) "＋ Another role", the name in its tooltip): a new row, his full matrix opened with its line (double bass and the new one; as the link did).
    D) The full view: the matrix of the entry, the link below it as before, no column, no toggle in the head; (3.40.11, review) the
       entry folded there (▾, compact lines): the column and the toggle as in the compact view."""
    CRED = [('Barry Guy', 'Double Bass', 3101, ''), ('Barry Guy', 'Composed By', 3101, ''), ('Evan Parker', 'Tenor Saxophone', 3102, '')]
    for n, _r, i, _t in CRED:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in CRED]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    INFO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const side = g.querySelector('.dci-em-side'); const lines = g.querySelector('.dci-em-compact');
      const r = (e) => e ? e.getBoundingClientRect() : null; const sr = r(side), lr = r(lines && lines.querySelector('.dci-em-cl'));
      const btn = side && side.querySelector('[data-act=add-role]'); const note = side && side.querySelector('.dci-work-note');
      return { headBy: !!g.querySelector('.dci-ghead [data-act=em-by]'), chead: !!g.querySelector('.dci-em-chead'),
        by: (g.querySelector('[data-act=em-by][aria-pressed=true]') || {}).dataset ? g.querySelector('[data-act=em-by][aria-pressed=true]').dataset.by : null,
        side: side ? [...side.children].map(c => c.textContent.trim()) : null, btnCls: btn ? btn.className : '', note: note ? [note.textContent.trim(), note.title] : null,
        beside: !!(sr && lr && sr.left >= lr.right && Math.abs(sr.top - lr.top) < 12), linkBelow: !!g.querySelector(':scope > [data-act=add-role]'),
        roleLines: g.querySelectorAll('.dci-em-clrole').length, wide: !!g.querySelector('.dci-em:not(.dci-em-compact)') }; }"""
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(800)
            a = pg.evaluate(INFO, 'Barry Guy')
            ep = pg.evaluate(INFO, 'Evan Parker')
            print('A) Barry Guy:', a, '\n   Evan Parker:', ep['side'])
            results.append(a['headBy'] and not a['chead'] and a['by'] == 'event' and a['beside'] and not a['linkBelow']
                           and len(a['side']) == 3 and a['side'][0].endswith('relationships to stage') and a['side'][2] == '＋ Another role'
                           and a['note'] == ['Writing credits: in the works matrix', 'The writing credits of this entry are in the works matrix.'] and 'dci-addrole-btn' in a['btnCls']
                           and ep['side'] is not None and len(ep['side']) == 2 and ep['side'][1] == '＋ Another role')
            sec = sec_sel(pg, 'Barry Guy')
            pg.click(f'{sec} [data-act=em-by][data-by=role]')
            pg.wait_for_timeout(500)
            bb = pg.evaluate(INFO, 'Barry Guy')
            print('B) by role:', bb)
            results.append(bb['by'] == 'role' and bb['roleLines'] >= 1 and bb['headBy'] and bb['side'] == a['side'] and bb['beside'])
            LINES = "[...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Barry Guy').querySelectorAll('tr.dci-em-line').length"
            pg.click(f'{sec} .dci-em-side [data-act=add-role]')
            pg.click('[data-el=arq] [data-act=arq-free]')  # ([Z-ARQ] 3.86.0) the role typed by hand
            pg.wait_for_timeout(600)
            c = pg.evaluate(INFO, 'Barry Guy')
            n1 = pg.evaluate(LINES)
            print('C) ＋:', c['wide'], c['side'], '| Zeilen der Matrix:', n1)
            results.append(c['wide'] and c['side'] is None and n1 == 2)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(800)
            d = pg.evaluate(INFO, 'Evan Parker')
            pg.click(f"{sec_sel(pg, 'Evan Parker')} [data-act=group-fold]")
            pg.wait_for_timeout(500)
            d2 = pg.evaluate(INFO, 'Evan Parker')
            print('D) volle Ansicht:', d, '\n   eingeklappt:', d2['side'], d2['headBy'], d2['linkBelow'])
            results.append(d['side'] is None and not d['headBy'] and d['linkBelow'] and d['wide'] and d2['side'] and d2['headBy'] and not d2['linkBelow'])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_compactlines():
    """Credits Importer 3.40.11 (collected item Z-KH, mockup B; Q-bi, Q-bo, Q-bp, Q-bg): ⚙ Settings → Appearance "Compact entries:
    notes beside the lines | in the lines".
    A) "notes beside the lines" chosen by default.
    B) "in the lines" (stored): no column; the end of the last line "5 to stage" and "＋ role" (its tooltip "+ Another role for Barry
       Guy"); in the head "✓ link" (its tooltip "found via Discogs link") and "✎ works ↓" (its tooltip the whole sentence).
    C) by role: the same at the end of the last line.
    D) "✎ works ↓": the works matrix in view, lit up.
    E) "＋ role": the full matrix with a new line.
    F) The full view: "found via Discogs link" as before, no "✎ works ↓".
    G) ↺ of Appearance: "notes beside the lines" again (the column back).
    H) (3.40.11, review) "Joey Bada$$" (piano, vocals): "＋ role" and its tooltip with the name as it is; vocal taken out (✕): the line "Taken out"
       gets no tail – it stays at the end of the line of the event."""
    CRED = [('Barry Guy', 'Double Bass', 3101, ''), ('Barry Guy', 'Composed By', 3101, ''), ('Evan Parker', 'Tenor Saxophone', 3102, ''),
            ('Joey Bada$$', 'Piano', 3103, ''), ('Joey Bada$$', 'Vocals', 3103, '')]
    for n, _r, i, _t in CRED:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in CRED]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    INFO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const lines = [...g.querySelectorAll('.dci-em-compact .dci-em-cl')]; const last = lines[lines.length - 1];
      const tail = last && last.querySelector('.dci-em-tail'); const btn = tail && tail.querySelector('[data-act=add-role]');
      const badge = g.querySelector('.dci-gmatch .dci-badge-ok'); const works = g.querySelector('.dci-ghead [data-act=works-goto]');
      return { side: !!g.querySelector('.dci-em-side'), tails: g.querySelectorAll('.dci-em-tail').length, tail: tail ? tail.textContent.replace(/\\s+/g, ' ').trim() : null,
        btn: btn ? [btn.textContent.trim(), btn.title] : null, badge: badge ? [badge.textContent.trim(), badge.title] : null,
        works: works ? [works.textContent.trim(), works.title] : null, headBy: !!g.querySelector('.dci-ghead [data-act=em-by]'), roleLines: g.querySelectorAll('.dci-em-clrole').length,
        lastIsRole: !!(last && last.classList.contains('dci-em-clrole')) }; }"""
    SEG = "[...document.querySelectorAll('[data-el=settings] [data-act=em-side]')].map(b => [b.dataset.side, b.textContent.trim(), b.getAttribute('aria-pressed')])"
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            H.open_settings(pg, 'appearance')
            a = [pg.evaluate(SEG), pg.evaluate("(r => r ? r.textContent.replace(/\\s+/g, ' ').trim() : '')(document.querySelector('[data-el=settings] [data-act=em-side]').closest('.dci-set-row, label, div'))")]
            print('A) Einstellung:', a)
            results.append(a[0] == [['beside', 'notes beside the lines', 'true'], ['lines', 'in the lines', 'false']] and a[1].startswith('Compact entries'))
            pg.click('[data-el=settings] [data-act=em-side][data-side=lines]')
            pg.wait_for_timeout(600)
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            bg = pg.evaluate(INFO, 'Barry Guy')
            ep = pg.evaluate(INFO, 'Evan Parker')
            stored = pg.evaluate("localStorage.getItem('dci-em-side')")
            print('B) Barry Guy:', bg, '\n   Evan Parker:', ep, '| gespeichert:', stored)
            results.append(stored == '"lines"' and not bg['side'] and bg['tails'] == 1 and bg['tail'] == '5 to stage ＋ role' and bg['btn'] == ['＋ role', '+ Another role for Barry Guy']
                           and bg['badge'] == ['✓ link', 'found via Discogs link'] and bg['works'] == ['✎ works ↓', 'The writing credits of this entry are in the works matrix.']
                           and bg['headBy'] and ep['works'] is None and ep['tail'] == '4 to stage ＋ role')
            sec = sec_sel(pg, 'Barry Guy')
            pg.click(f'{sec} [data-act=em-by][data-by=role]')
            pg.wait_for_timeout(500)
            c = pg.evaluate(INFO, 'Barry Guy')
            print('C) by role:', c)
            results.append(c['roleLines'] >= 1 and c['lastIsRole'] and c['tails'] == 1 and c['tail'] == '5 to stage ＋ role')
            pg.click(f'{sec} [data-act=works-goto]')
            pg.wait_for_timeout(400)
            # the top of the works matrix right below the part of the dashboard that stays in view (Add entry manually, the pools) – (3.52.0)
            # or as far as the dashboard scrolls (the shorter works matrix may end the dashboard)
            d = pg.evaluate("""(w => { if (!w) return null; const body = document.querySelector('[data-el=body]').getBoundingClientRect();
              const stick = document.querySelector('[data-el=stick]').getBoundingClientRect(); const t = w.getBoundingClientRect().top;
              const b = document.querySelector('[data-el=body]'); const end = b.scrollTop + b.clientHeight >= b.scrollHeight - 2;
              return [w.classList.contains('dci-flash'), t >= stick.bottom - 2 && (t <= stick.bottom + 40 || end) && t < body.bottom]; })(document.querySelector('[data-el=works]'))""")
            print('D) Werke:', d)
            results.append(d == [True, True])
            pg.click(f'{sec} .dci-em-tail [data-act=add-role]')
            pg.click('[data-el=arq] [data-act=arq-free]')  # ([Z-ARQ] 3.86.0) the role typed by hand
            pg.wait_for_timeout(600)
            e = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Barry Guy').querySelectorAll('tr.dci-em-line').length")
            print('E) ＋ role: Zeilen der Matrix', e)
            results.append(e == 2)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            f = pg.evaluate(INFO, 'Evan Parker')
            print('F) volle Ansicht:', f['badge'], f['works'], f['tails'])
            results.append(f['badge'] == ['found via Discogs link', ''] and f['works'] is None and f['tails'] == 0)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            H.open_settings(pg, 'appearance')
            pg.click('[data-el=settings] [data-act=settings-reset][data-topic=appearance]')
            pg.wait_for_timeout(800)
            g = [pg.evaluate("localStorage.getItem('dci-em-side')"), pg.evaluate(SEG)]
            # (the reset of Appearance sets the full view too: back to compact to see the column)
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            if pg.evaluate("!document.querySelector('#dci-overlay.dci-compact')"):
                pg.click('.dci-head [data-act=view-toggle]')
                pg.wait_for_timeout(600)
            g2 = pg.evaluate(INFO, 'Evan Parker')
            print('G) ↺:', g, '| Evan Parker:', g2['side'], g2['tails'], g2['badge'])
            results.append(g[0] is None and g[1][0][2] == 'true' and g2['side'] and g2['tails'] == 0 and g2['badge'] == ['found via Discogs link', ''])
            # H) a name with "$", a line "Taken out"
            H.open_settings(pg, 'appearance')
            pg.click('[data-el=settings] [data-act=em-side][data-side=lines]')
            pg.wait_for_timeout(500)
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            h0 = pg.evaluate(INFO, 'Joey Bada$$')
            jb = sec_sel(pg, 'Joey Bada$$')
            pg.locator(f'{jb} .dci-em-chip', has_text='vocal').locator('[data-act=em-chipout]').click()
            pg.wait_for_timeout(500)
            h1 = pg.evaluate("""(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
              return [...g.querySelectorAll('.dci-em-compact .dci-em-cl')].map(l => [l.classList.contains('dci-em-skip'), !!l.querySelector('.dci-em-tail')]); }""", 'Joey Bada$$')
            print('H) Joey Bada$$:', h0['btn'], '| Zeilen (Taken out, Ende):', h1)
            results.append(h0['btn'] == ['＋ role', '+ Another role for Joey Bada$$'] and h1 == [[False, True], [True, False]])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_review43():
    """Credits Importer 3.43.5 (full review, package P6 – the UI).
    A) An entry as a matrix: "Remove" in an opened line's row takes the line off the screen (until 3.43.4 the line with its ticks
       stayed until a later redraw).
    B) Text typed into "Paste text" survives a redraw of the source panel (the menu "Source ▾" opened: renderSource) – until 3.43.4
       the textarea came back empty (the text was read only at "Load").
    C) "Mapping rules" open, the language switched to German: the window's title follows ("Mapping-Regeln"); until 3.43.4 it kept
       the English texts."""
    orig, rel = join_release()
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            # (the rules as a window of their own: open beside the settings – in the dashboard, ⚙ Settings closes them)
            pg.evaluate("localStorage.setItem('dci-rules-place', JSON.stringify('window'))")
            pg.reload(); pg.add_script_tag(content=H.MAIN)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            solo = sec_sel(pg, 'Solo Man')
            lines0 = pg.evaluate("(sel) => document.querySelectorAll(sel + ' tr.dci-em-line').length", solo)
            pg.click(f'{solo} tr.dci-em-line [data-act=em-detail]'); pg.wait_for_timeout(300)
            pg.click(f'{solo} .dci-em-detail-row tr.dci-row [data-act=remove-row]'); pg.wait_for_timeout(500)
            lines1 = pg.evaluate("(sel) => document.querySelectorAll(sel + ' tr.dci-em-line').length", solo)
            print('A) Zeilen der Matrix:', lines0, '→ nach „Remove“:', lines1)
            results.append(lines0 >= 1 and lines1 == lines0 - 1)
            # B) the pasted text through a redraw
            H.src_menu(pg, 'text-open'); pg.wait_for_timeout(200)
            pg.fill('[data-f=text-src]', 'Bass – Jane Roe')
            pg.fill('[data-f=text-origin]', 'booklet')
            H.src_menu(pg); pg.wait_for_timeout(200)
            H.src_menu(pg); pg.wait_for_timeout(200)
            b1 = pg.evaluate("[document.querySelector('[data-f=text-src]').value, document.querySelector('[data-f=text-origin]').value]")
            print('B) Text nach dem Neuzeichnen:', b1)
            results.append(b1 == ['Bass – Jane Roe', 'booklet'])
            # C) the rules window and the language
            pg.click('.dci-head [data-act=rules]'); pg.wait_for_timeout(300)
            c0 = pg.evaluate("document.getElementById('dci-rules-title').textContent.trim()")
            H.open_settings(pg, 'general')
            pg.select_option('[data-f=lang]', 'de'); pg.wait_for_timeout(600)
            c1 = pg.evaluate("(() => { const r = document.getElementById('dci-rules'); return r ? [r.hidden, document.getElementById('dci-rules-title').textContent.trim()] : null; })()")
            print('C) Regelfenster:', c0, '→ Deutsch:', c1, '| Fehler:', errs)
            results.append(c0 == 'Mapping rules' and c1 and c1[0] is False and c1[1] != 'Mapping rules' and not errs)
        finally:
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_levelclick():
    """Credits Importer 3.44.0 (collected item Z-CLV; Q-eh, Q-ei, Q-ej): the level of an event is a button wherever it shows.
    A) Compact (lines by event): Solo Man's ① "Recording" is a button (the tooltip names the next level); clicks go through the levels
       MusicBrainz has for his roles – Recording → Release → Skip → Recording; on "Skip" the event stays at its place, grey, "① Skip"
       (its rows on "Skip"), a click takes it back to Recording on the same tracks.
    B) An arranger (Discogs "Arranged By"; from 3.94.0 with S150 off – on, it starts on Work, see arr394): Work is in the circle –
       Recording → Release → Work (the rows into the works matrix).
    C) The full matrix: the level in the head of the event's column is a button (the same circle); the ticks of an event on "Skip" are
       shown, not changeable; the opened event offers "Skip" too."""
    orig, rel = join_release()

    def rel2():
        d = rel()
        d['extraartists'].append({'name': 'Arr Man', 'anv': '', 'role': 'Arranged By', 'tracks': '', 'id': 3075, 'join': ''})
        return d
    H.ARTISTS[3075] = (H.uid('dddddddd', 85), 'Arr Man')
    H.discogs_release = rel2
    # MusicBrainz's instrument on the release (44) and the arranger of a recording (297 there; the harness's 297 is the work's) and
    # of a release (295), as on MusicBrainz – for this case only (caserun restores the harness)
    H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.lt(1297, '22661fb8-cdb7-4f67-8385-b2a8be6c9f0d', 'arranger', 'artist', 'recording', (1,))
    H.lt(295, '34d5334e-a4c8-4b65-a5f8-bbcc9c81d13d', 'arranger', 'artist', 'release', (1,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    LV = "(sel) => [...document.querySelectorAll(sel + ' [data-act=em-evlevel-next]')].map(b => [b.dataset.n, b.dataset.level, b.title])"
    ROWS = "(name) => [...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent.trim() === name).flatMap(g => [...g.querySelectorAll('tr.dci-row')].map(tr => { const b = tr.querySelector('[data-act=level][aria-pressed=true], .dci-cl-level[data-level]'); return b ? b.dataset.level : null; }))"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False, view='compact')
            pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S150']))")
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)
            solo = sec_sel(pg, 'Solo Man')
            seq = [pg.evaluate(LV, solo)]
            skip_line = None
            for k in range(3):
                pg.click(f'{solo} [data-act=em-evlevel-next][data-n="1"]'); pg.wait_for_timeout(400)
                seq.append(pg.evaluate(LV, solo))
                if k == 1:
                    skip_line = pg.evaluate("(sel) => { const l = document.querySelector(sel + ' .dci-em-cl.dci-em-skip[data-emskip]'); return l ? l.textContent.replace(/\\s+/g, ' ').trim().slice(0, 40) : null; }", solo)
            levels = [s0[0][1] if s0 else None for s0 in seq]
            tracks = pg.evaluate("(sel) => (document.querySelector(sel + ' .dci-em-cl[data-emev] .dci-cl-tracks') || {}).textContent", solo)
            print('A) Ebenen:', levels, '| Tooltip:', seq[0][0][2] if seq[0] else None, '| Skip am Platz:', skip_line, '| Tracks danach:', tracks)
            results.append(levels == ['recording', 'release', 'skip', 'recording'] and seq[0][0][2].endswith('“Release”')
                           and skip_line and skip_line.startswith('① Skip') and seq[2][0][2].endswith('“Recording” again'))
            # B) the arranger: Work in the circle
            arr = sec_sel(pg, 'Arr Man')
            a0 = pg.evaluate(LV, arr)
            steps = [a0[0][1] if a0 else None]
            for _ in range(3):
                cur = pg.evaluate(LV, arr)
                if not cur:
                    break
                pg.click(f'{arr} [data-act=em-evlevel-next][data-n="1"]'); pg.wait_for_timeout(500)
                cur = pg.evaluate(LV, arr)
                steps.append(cur[0][1] if cur else 'work?')
            wrows = pg.evaluate("[...document.querySelectorAll('th.dci-mx-col')].map(t => t.textContent).join(' ').includes('Arr Man')")
            print('B) Arrangeur:', steps, '| in der Werke-Matrix:', wrows)
            results.append(steps[0] == 'recording' and 'release' in steps and steps[-1] == 'work?' and wrows)
            # D) (3.44.1, review) Part Man has two events (all tracks, track 2): ① to Release – the events sort anew, the focus stays
            # on the level of the event clicked (now ② Release)
            part = sec_sel(pg, 'Part Man')
            d0 = pg.evaluate(LV, part)
            pg.click(f'{part} [data-act=em-evlevel-next][data-n="1"]'); pg.wait_for_timeout(400)
            d1 = pg.evaluate(LV, part)
            foc = pg.evaluate("(() => { const b = document.activeElement; return b && b.dataset.act === 'em-evlevel-next' ? [b.dataset.n, b.dataset.level] : null; })()")
            print('D) Part Man:', [x[:2] for x in d0], '→', [x[:2] for x in d1], '| Fokus:', foc)
            results.append([x[1] for x in d0] == ['recording', 'recording'] and [x[1] for x in d1] == ['recording', 'release'] and foc == ['2', 'release'])
            print('Fehler:', errs)
            results.append(not errs)
            pg.evaluate("localStorage.setItem('dci-view', JSON.stringify('full')); localStorage.removeItem('dci-remember:%s')" % H.REL)
            pg.close()
            # C) the full matrix
            pg2, errs2 = H.open_mb_edit(ctx, companion=False, view='full')
            pg2.on('dialog', lambda d: d.accept())
            pg2.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg2)
            H.wait_for(pg2, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg2.wait_for_timeout(1200)
            solo2 = sec_sel(pg2, 'Solo Man')
            h0 = pg2.evaluate("(sel) => [...document.querySelectorAll(sel + ' th.dci-em-ev [data-act=em-evlevel-next]')].map(b => b.dataset.level)", solo2)
            pg2.click(f'{solo2} th.dci-em-ev [data-act=em-evlevel-next][data-n="1"]'); pg2.wait_for_timeout(400)
            pg2.click(f'{solo2} th.dci-em-ev [data-act=em-evlevel-next][data-n="1"]'); pg2.wait_for_timeout(400)
            h1 = pg2.evaluate("(sel) => { const th = document.querySelector(sel + ' th.dci-em-evskip'); const t = [...document.querySelectorAll(sel + ' td.dci-em-c-skip input')]; return th ? [th.textContent.replace(/\\s+/g, ' ').trim(), t.length, t.every(x => x.disabled), t.some(x => x.checked)] : null; }", solo2)
            pg2.click(f'{solo2} th.dci-em-ev [data-act=em-evlevel-next][data-n="1"]'); pg2.wait_for_timeout(400)
            pg2.click(f'{solo2} th.dci-em-ev [data-act=em-evopen]'); pg2.wait_for_timeout(300)
            seg = pg2.evaluate("(sel) => [...document.querySelectorAll(sel + ' [data-act=em-evlevel]')].map(b => b.dataset.level)", solo2)
            # E) (3.44.1, review) Part Man: ① (all tracks, electric guitar) on Skip; the guitar line ticked into ② (track 2) – a row of
            # its own, the skipped event keeps its row (until 3.44.0 the skipped row was taken for it)
            part2 = sec_sel(pg2, 'Part Man')
            # the guitar line: the one whose tick is in the event of all tracks (the piano is on track 2 only) – the last line
            gl = pg2.evaluate("(sel) => { const ls = [...document.querySelectorAll(sel + ' tr.dci-em-line')]; return ls.length ? ls[ls.length - 1].dataset.line : null; }", part2)
            GEV = "([sel, line]) => { const x = [...document.querySelectorAll(sel + ' tr.dci-em-line[data-line=\"' + line + '\"] input[data-f=em-tick]')].find(i => i.checked); return x ? x.dataset.ev : null; }"
            # (clicked until the guitar's event is on Skip – the page may have come back remembered from the compact one)
            for _ in range(4):
                ev = pg2.evaluate(GEV, [part2, gl])
                if not ev or ev.startswith('skip|'):
                    break
                pg2.evaluate("([sel, ev]) => { const b = [...document.querySelectorAll(sel + ' th.dci-em-ev [data-act=em-evlevel-next]')].find(x => x.dataset.ev === ev); if (b) b.click(); }", [part2, ev])
                pg2.wait_for_timeout(400)
            heads = pg2.evaluate("(sel) => [...document.querySelectorAll(sel + ' th.dci-em-ev')].map(th => th.classList.contains('dci-em-evskip') ? 'skip' : 'ev')", part2)
            box = pg2.evaluate("([sel, line]) => [...document.querySelectorAll(sel + ' tr.dci-em-line[data-line=\"' + line + '\"] input[data-f=em-tick]')].map(x => [x.dataset.ev.startsWith('skip|'), x.checked, x.disabled])", [part2, gl])
            free = [i for i, x in enumerate(box) if not x[0] and not x[1]]
            if free:
                pg2.locator(f'{part2} tr.dci-em-line[data-line="{gl}"] input[data-f=em-tick]').nth(free[0]).check(); pg2.wait_for_timeout(400)
            box2 = pg2.evaluate("([sel, line]) => [...document.querySelectorAll(sel + ' tr.dci-em-line[data-line=\"' + line + '\"] input[data-f=em-tick]')].map(x => [x.dataset.ev.startsWith('skip|'), x.checked])", [part2, gl])
            print('E) Köpfe:', heads, '| Gitarre vorher:', box, '| nachher:', box2)
            results.append('skip' in heads and free and [x for x in box2 if x[0]] == [[True, True]] and [x for x in box2 if not x[0]] == [[False, True]])
            print('C) Kopf:', h0, '| Skip:', h1, '| geöffnet:', seg, '| Fehler:', errs2)
            results.append(h0 and h0[0] == 'recording' and h1 and h1[0].startswith('① Skip') and h1[2] and h1[3] and seg == ['recording', 'release', 'skip'] and not errs2)
        finally:
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_viewbits():
    """Credits Importer 3.69.0 (collected items Z-WRL, Z-CIN, Z-CRY, Z-CMK; rules S101–S104).
    A) Z-CIN: Joey Bada$$ (piano, vocals – one event): the two chips one below the other in a block of their own (before: in one line).
    B) Z-WRL: Lina Notes ("Liner Notes", on the release): the line without "whole release".
    C) Z-CRY: "Nobody Known" (not in MusicBrainz): "Create artist …" yellow; Bass Man (found): no such button.
    D) Z-CMK: a click into the white field of Joey's line of the event: a jump on Discogs for Joey (the entry, two rows); (review) a
       button of the line (its level) jumps not; "Create artist …" really yellow (its background).
    E) Rules S101–S104 off: one line of chips, "whole release", the button as before, no jump from the line."""
    CRED = [('Joey Bada$$', 'Piano', 3103, ''), ('Joey Bada$$', 'Vocals', 3103, ''), ('Lina Notes', 'Liner Notes', 3104, ''), ('Nobody Known', 'Guitar', 3999, '')]
    for n, _r, i, _t in CRED[:3]:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = d['extraartists'] + [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in CRED]
        return d
    H.discogs_release = rel
    view0 = H.ENTRIES_VIEW
    G = "(name) => [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name)"
    results = []

    def run(off=False):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=True, view='compact')
            pg.on('dialog', lambda d: d.accept())
            if off:
                pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S101', 'S102', 'S103', 'S104']))")
            pg.evaluate("window.__shows = []; document.addEventListener('dci:to-discogs', (e) => { try { const m = JSON.parse(e.detail); if (m.type === 'show') window.__shows.push(m); } catch (x) {} })")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            pg.wait_for_timeout(1500)
            out = {}
            out['chips'] = pg.evaluate(f"""(() => {{ const g = ({G})('Joey Bada$$'); if (!g) return null; const line = [...g.querySelectorAll('.dci-em-cl')].find(l => l.querySelectorAll('.dci-em-chip').length >= 2);
              if (!line) return null; const c = [...line.querySelectorAll('.dci-em-chip')].map(x => x.getBoundingClientRect().top); return {{ list: !!line.querySelector('.dci-em-cllist'), stacked: c[1] > c[0] + 5 }}; }})()""")
            out['lina'] = pg.evaluate(f"(() => {{ const g = ({G})('Lina Notes'); return g ? /whole release/.test(g.textContent) : null; }})()")
            out['create'] = pg.evaluate(f"""(() => {{ const g = ({G})('Nobody Known'); const b = g && g.querySelector('[data-act=artist-create]');
              const bm = ({G})('Bass Man'); return [b ? b.classList.contains('dci-create-miss') && getComputedStyle(b).backgroundColor !== 'rgb(255, 255, 255)' : null, !!(bm && bm.querySelector('[data-act=artist-create]'))]; }})()""")
            pg.evaluate("window.__shows = []")
            pg.evaluate(f"""(() => {{ const g = ({G})('Joey Bada$$'); const line = [...g.querySelectorAll('.dci-em-cl')].find(l => l.querySelectorAll('.dci-em-chip').length >= 2);
              const r = line.getBoundingClientRect(); line.dispatchEvent(new MouseEvent('click', {{ bubbles: true, clientX: r.right - 4, clientY: r.top + 4 }})); }})()""")
            pg.wait_for_timeout(800)
            out['shows'] = pg.evaluate("window.__shows.map(m => [m.artistName, m.role])")
            # ((review) a button of the line jumps not; a chip: its own row
            pg.evaluate("window.__shows = []")
            pg.evaluate(f"""(() => {{ const g = ({G})('Joey Bada$$'); const b = g.querySelector('.dci-em-cl .dci-cl-level, .dci-em-cl button'); if (b) b.dispatchEvent(new MouseEvent('click', {{ bubbles: true }})); }})()""")
            pg.wait_for_timeout(700)
            out['btn'] = pg.evaluate("window.__shows.length")
            out['errs'] = errs
            b.close()
            return out

    try:
        o = run()
        print('A)', o['chips'], '| B)', o['lina'], '| C)', o['create'], '| D)', o['shows'], o['errs'])
        results.append(o['chips'] == {'list': True, 'stacked': True})
        results.append(o['lina'] is False)
        results.append(o['create'] == [True, False])
        results.append(o['shows'] and o['shows'][-1][0] == 'Joey Bada$$' and o['shows'][-1][1] == '' and o['btn'] == 0 and not o['errs'])
        o2 = run(off=True)
        print('E)', o2['chips'], o2['lina'], o2['create'], o2['shows'])
        results.append(o2['chips'] and not o2['chips']['list'] and o2['lina'] is True and o2['create'][0] is False and not o2['shows'])
    finally:
        H.ENTRIES_VIEW = view0
        H.discogs_release = orig
        for _n, _r, i, _t in CRED[:3]:
            H.ARTISTS.pop(i, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dnd378():
    """Credits Importer 3.78.0 (collected item Z-DND): drag & drop the same everywhere – a drop adds (what is there stays), ⇧ Shift
    replaces; a drop that changed something says so, with ↶; ⠿ picks a chip for clicks and Enter (no mouse needed).
    A) Compact, by event: a pool date dropped onto "no date" in the short line of Solo Man's ① – the event gets it; a second
       date dropped there: ① keeps its date, ② has the new one; ↶ – one event again.
    B) Rows: a pool date dropped onto Guitar Guy's date field (1999): it stays, the new date gets a row of its own ("… a row of its
       own – its date 1999 stays"); ↶ of the drop: the row is gone; with ⇧ Shift: replaced; ↶ after a change (the row on Skip):
       not undone, said so.
    C) Works matrix: a pool date onto the head of a column – set, with ↶; another date without ⇧: "already has a date … ⇧ Shift" and
       nothing changed; with ⇧ Shift: replaced.
    D) ⠿ of a pool date: the places are marked (picking) and a line says what to do; a click on Keys Guy's date: set; Enter on Bass
       Man's date button: set; Esc ends it.
    E) A chip let go over the edit note of the page: the drop is cancelled (nothing typed into it)."""
    from common_rows import date_field
    orig, rel = join_release()
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            # --- A) compact, by event
            H.discogs_release = rel
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            chips = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.dataset.id)")
            d1, d2 = chips[0], chips[-1]
            pg.click('.dci-head [data-act=view-toggle]')
            H.wait_for(pg, "!!document.querySelector('.dci-em-cl[data-emev] .dci-cl-date[data-evdrop]')", 15)
            solo = sec_sel(pg, 'Solo Man')
            SHORT = "(sel) => [...document.querySelectorAll(sel + ' .dci-em-cl[data-emev] .dci-cl-date')].map(x => x.textContent.trim())"
            a0 = pg.evaluate(SHORT, solo)
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d1}"]', f'{solo} .dci-cl-date[data-evdrop]', False])
            H.wait_ok(pg, f"(() => {{ const x = document.querySelector({solo + ' .dci-cl-date[data-evdrop]'!r}); return !!x && x.textContent.trim() !== 'no date'; }})()", 10)
            a1 = pg.evaluate(SHORT, solo)
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d2}"]', f'{solo} .dci-cl-date[data-evdrop]', False])
            H.wait_ok(pg, f"document.querySelectorAll({solo + ' .dci-em-cl[data-emev]'!r}).length === 2", 10)
            a2 = pg.evaluate(SHORT, solo)
            pg.click('[data-act=em-undo]')
            H.wait_ok(pg, f"document.querySelectorAll({solo + ' .dci-em-cl[data-emev]'!r}).length === 1", 10)
            a3 = pg.evaluate(SHORT, solo)
            print('A) kurze Zeile:', a0, '→', a1, '| zweites Datum:', a2, '| ↶:', a3, '| Fehler:', errs)
            results.append(a0 == ['no date'] and len(a1) == 1 and a1[0] != 'no date' and len(a2) == 2 and a1[0] in a2 and a3 == a1 and not errs)
            ctx.close()

            # --- B–E) rows (the classic view), the works matrix
            H.discogs_release = orig
            H.ENTRIES_VIEW = 'legacy'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(800)
            idof = lambda text: pg.evaluate(f"[...document.querySelectorAll('.dci-pchip-date')].find(c => c.querySelector('.dci-chip-main').textContent.trim().startsWith({text!r})).dataset.id")
            rows = lambda name: pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text=name)).first.locator('tr.dci-row')
            dsel = lambda name, k=0: f'tr[data-row="{rows(name).nth(k).get_attribute("data-row")}"] .dci-c-date'
            msgs = lambda: [m.replace('\n', ' ') for m in pg.locator('.dci-msg').all_inner_texts()]
            perf, mix = idof('Performance 1 ·'), idof('Mix 1')
            rows('Guitar Guy').first.locator('[data-act=date-open]').click(); pg.keyboard.type('1999'); pg.wait_for_timeout(300)
            n0 = rows('Guitar Guy').count()
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{perf}"]', dsel('Guitar Guy'), False])
            H.wait_ok(pg, f"document.querySelectorAll('.dci-group').length && [...document.querySelectorAll('.dci-msg')].some(m => /a row of its own/.test(m.textContent))", 10)
            n1 = rows('Guitar Guy').count()
            b1 = [date_field(rows('Guitar Guy').nth(k), 'rd-by') for k in range(n1)]
            m1 = [m for m in msgs() if 'a row of its own' in m]
            pg.click('.dci-msg [data-act=drop-undo]')
            H.wait_ok(pg, "!document.querySelector('[data-act=drop-undo]')", 10)
            n2 = rows('Guitar Guy').count()
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{perf}"]', dsel('Guitar Guy'), True])
            pg.wait_for_timeout(400)
            b3 = (rows('Guitar Guy').count(), date_field(rows('Guitar Guy').first, 'rd-by'), date_field(rows('Guitar Guy').first, 'rd-bm'))
            # ((review) ↶ only while nothing changed since the drop: the row put on Skip – not undone, said so)
            rows('Guitar Guy').first.locator('[data-act=level][data-level=skip]').click()
            pg.wait_for_timeout(300)
            pg.click('.dci-msg [data-act=drop-undo]')
            pg.wait_for_timeout(300)
            stale = [m for m in msgs() if 'Not undone' in m]
            print('B) Zeilen:', n0, '→', n1, b1, m1[:1], '| ↶:', n2, '| mit ⇧:', b3, '| ↶ nach einer Änderung:', stale[:1])
            results.append(n1 == n0 + 1 and b1[0] == '1999' and '2001' in b1[1:] and len(m1) == 1 and '1999' in m1[0] and n2 == n0 and b3 == (n0, '2001', '03') and len(stale) == 1)
            rows('Guitar Guy').first.locator('[data-act=level]').first.click()
            pg.wait_for_timeout(300)
            # C) works matrix: the head of a column
            HEAD = "(document.querySelector('[data-colhead] .dci-mx-datechip') || { textContent: '' }).textContent.trim()"
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{perf}"]', '[data-colhead]:not(.dci-mx-locked) .dci-mx-card', False])
            pg.wait_for_timeout(400)
            c1 = (pg.evaluate(HEAD), pg.locator('[data-act=drop-undo]').count())
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{mix}"]', '[data-colhead]:not(.dci-mx-locked) .dci-mx-card', False])
            pg.wait_for_timeout(400)
            c2 = (pg.evaluate(HEAD), [m for m in msgs() if 'already has a date' in m][:1])
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{mix}"]', '[data-colhead]:not(.dci-mx-locked) .dci-mx-card', True])
            pg.wait_for_timeout(400)
            c3 = pg.evaluate(HEAD)
            print('C) Spaltenkopf:', c1, '| ohne ⇧:', c2, '| mit ⇧:', c3)
            results.append('2001-03-01' in c1[0] and c1[1] == 1 and c2[0] == c1[0] and len(c2[1]) == 1 and 'Shift' in c2[1][0] and '2001-05' in c3)
            # D) ⠿: clicks and Enter
            pg.click(f'.dci-pchip-date[data-id="{perf}"] [data-act=dm-pick]')
            pg.wait_for_timeout(300)
            d0 = pg.evaluate("[document.getElementById('dci-overlay').classList.contains('dci-dm-picking'), (document.querySelector('.dci-dm-pickhint') || { textContent: '' }).textContent]")
            keys0 = date_field(rows('Keys Guy').first, 'rd-bm')
            pg.locator(dsel('Keys Guy')).click()
            pg.wait_for_timeout(400)
            keys1 = (date_field(rows('Keys Guy').first, 'rd-by'), date_field(rows('Keys Guy').first, 'rd-bm'))
            bass0 = date_field(rows('Bass Man').first, 'rd-by')
            btn = rows('Bass Man').first.locator('.dci-c-date button').first
            btn.focus()
            pg.keyboard.press('Enter')
            pg.wait_for_timeout(400)
            bass1 = (date_field(rows('Bass Man').first, 'rd-by'), date_field(rows('Bass Man').first, 'rd-bm'))
            pg.keyboard.press('Escape')
            pg.wait_for_timeout(300)
            d1x = pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-dm-picking')")
            print('D) ⠿:', d0, '| Keys Guy:', keys0, '→', keys1, '| Bass Man:', bass0, '→', bass1, '| Esc:', d1x)
            results.append(d0[0] and 'picked' in d0[1] and keys1 == ('2001', '03') and bass1 == ('2001', '03') and d1x is False)
            # E) let go over the edit note
            e1 = pg.evaluate(f"""() => {{ const s = document.querySelector('.dci-pchip-date[data-id="{mix}"]'); const t = document.getElementById('edit-note-text');
      if (!s || !t) return null; const dt = new DataTransfer(); s.dispatchEvent(new DragEvent('dragstart', {{ bubbles: true, dataTransfer: dt }}));
      const ok = t.dispatchEvent(new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt }}));
      s.dispatchEvent(new DragEvent('dragend', {{ bubbles: true, dataTransfer: dt }})); return [ok, t.value]; }}""")
            print('E) Bearbeitungsnotiz:', e1, '| Fehler:', errs)
            results.append(e1 is not None and e1[0] is False and mix not in e1[1] and not errs)
        finally:
            H.discogs_release = orig
            H.ENTRIES_VIEW = 'legacy'
            for _n, _r, i, _t in JOIN_CREDITS:
                H.ARTISTS.pop(i, None)
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_rlv383():
    """Credits Importer 3.83.0 (collected item Z-RLV, rule S124): staged, then changed in the dashboard – staged again.
    A) Bob Producer (producer, on the 4 recordings) staged, then his level switched to Release and staged again: the four recording
       relationships are taken out of the editor, one on the release added.
    B) Staged again on the recordings (the level back), one of them changed in the relationship editor itself (its credit), then the
       level to Release once more: all four taken out (until 3.82.0 the changed one stayed – "to remove by hand"), a message names it.
    C) The type changed (producer → mix, Release back to Recording first): replaced in place (no second relationship).
    D) (review) One of them taken out in the relationship editor itself, then the credit changed in the dashboard: added anew (until
       the review "changed in the editor itself" – never staged again).
    E) (review) One's type changed in the relationship editor itself (mix → producer), then the credit: the dashboard's type again
       (until the review the type of the editor stayed), a message names it."""
    import common_rows as C
    BOB = H.ARTISTS[3005][0]
    BOB_ADDED = f"""MB.relationshipEditor.state.added.filter(r => (r.entity0 || {{}}).gid === '{BOB}' || (r.entity1 || {{}}).gid === '{BOB}').map(r => [r.linkTypeID, ((r.entity0 || {{}}).gid === '{BOB}' ? r.entity1 : r.entity0).entityType])"""
    H.lt(30, H.LTS[30]['gid'], 'producer', 'artist', 'release', (1, 526))
    H.lt(143, H.LTS[143]['gid'], 'mix', 'artist', 'recording', (1, 526))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_still(pg, "document.body.innerHTML", 15, 300)
        key = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(s => /Bob Producer/.test(s.querySelector('.dci-gname').textContent)).dataset.group")

        def level(lv):
            pg.locator(f'section.dci-group[data-group="{key}"] [data-act=level][data-level={lv}]').first.evaluate('b => b.click()')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
        C.stage(pg)
        a0 = pg.evaluate(BOB_ADDED)
        level('release')
        C.stage(pg)
        a1 = pg.evaluate(BOB_ADDED)
        print('A)', a0, '→', a1)
        results.append(sorted(a0) == [[141, 'recording']] * 4 and a1 == [[30, 'release']])
        level('recording')
        C.stage(pg)
        b0 = pg.evaluate(BOB_ADDED)
        # (one of them changed in the editor itself: its credit)
        pg.evaluate(f"""(() => {{ const st = MB.relationshipEditor.state; const i = st.added.findIndex(r => r.linkTypeID === 141 && ((r.entity0 || {{}}).gid === '{BOB}' || (r.entity1 || {{}}).gid === '{BOB}'));
          const added = [...st.added]; added[i] = {{ ...added[i], entity0_credit: 'Bobby P.' }}; MB.relationshipEditor.state = {{ ...st, added }}; }})()""")
        level('release')
        C.stage(pg)
        b1 = pg.evaluate(BOB_ADDED)
        msgs = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent).join(' | ')")
        print('B)', b0, '→', b1, '|', [m for m in msgs.split(' | ') if 'editor itself' in m][:2])
        results.append(sorted(b0) == [[141, 'recording']] * 4 and b1 == [[30, 'release']] and 'replaced by what the dashboard has now' in msgs and 'remove by hand' not in msgs)
        level('recording')
        C.stage(pg)
        rid = pg.evaluate(f"document.querySelector('section.dci-group[data-group=\"{key}\"] tr.dci-row').dataset.row")
        pg.select_option(f'tr[data-row="{rid}"] [data-f=type]', label='mix')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        C.stage(pg)
        c1 = pg.evaluate(BOB_ADDED)
        print('C)', c1)
        results.append(sorted(c1) == [[143, 'recording']] * 4)
        BOB_CRED = f"""MB.relationshipEditor.state.added.filter(r => (r.entity0 || {{}}).gid === '{BOB}' || (r.entity1 || {{}}).gid === '{BOB}').map(r => [r.linkTypeID, r.entity0_credit || r.entity1_credit || ''])"""

        def credit(v):
            f = pg.locator(f'section.dci-group[data-group="{key}"] [data-f=credit]').first
            f.fill(v)
            f.evaluate("e => e.dispatchEvent(new Event('change', { bubbles: true }))")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
        # D) (review) one taken out in the editor itself, then the credit changed: added anew (until the review "changed there")
        pg.evaluate(f"""(() => {{ const st = MB.relationshipEditor.state; const i = st.added.findIndex(r => r.linkTypeID === 143 && (r.entity0 || {{}}).gid === '{BOB}');
          MB.relationshipEditor.state = {{ ...st, added: st.added.filter((_, k) => k !== i) }}; }})()""")
        credit('B. Producer')
        C.stage(pg)
        d1 = pg.evaluate(BOB_CRED)
        print('D)', d1)
        results.append(sorted(d1) == [[143, 'B. Producer']] * 4)
        # E) (review) one's type changed in the editor itself (→ producer), then the credit: the dashboard's type again, named
        pg.evaluate(f"""(() => {{ const st = MB.relationshipEditor.state; const i = st.added.findIndex(r => r.linkTypeID === 143 && (r.entity0 || {{}}).gid === '{BOB}');
          const added = [...st.added]; added[i] = {{ ...added[i], linkTypeID: 141 }}; MB.relationshipEditor.state = {{ ...st, added }}; }})()""")
        credit('Bob P.')
        C.stage(pg)
        e1 = pg.evaluate(BOB_CRED)
        msgs = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent).join(' | ')")
        print('E)', e1, 'replaced by what the dashboard has now' in msgs)
        results.append(sorted(e1) == [[143, 'Bob P.']] * 4 and 'replaced by what the dashboard has now' in msgs)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_arq386():
    """Credits Importer 3.86.0 (collected item Z-ARQ, rule S134): "＋ Another role" asks the relationship type.
    A) Rows (the classic view), Bob Producer: the question below his name – a search field, the types by level (Recording first,
       "performer", "instrument" … the common ones first); "mix" typed: only types with "mix"; "mix" chosen: a row "mix" on the
       recordings, the question gone.
    B) The matrix of an entry (Solo Man of the release of case dnd378): his events to tick, the first ticked; all ticked, "producer"
       chosen: a line "producer" on each (their tracks).
    C) "Type a role yourself (e.g. Pressed By)": as until 3.85.0 – a new row, its role field focused; Esc closes the question.
    D) Rule S134 off: no question, the row at once.
    E) (review) One question at a time – another entry's "＋ Another role" closes the first; Enter in the search takes the first type."""
    orig, rel = join_release()
    ROWTYPES = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes(name));
      return g ? [...g.querySelectorAll('tr.dci-row')].map(r => { const t = r.querySelector('[data-f=type]'); return [(t && t.selectedOptions[0] || {}).text || '', (r.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || '']; }) : null; }"""
    results = []

    def open_page(p, view, off=False):
        H.ENTRIES_VIEW = view
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        if off:
            pg.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S083', 'S134']))")
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        return b, pg, errs

    sel = lambda name: f"[...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes({name!r}))"
    try:
        with sync_playwright() as p:
            H.discogs_release = orig
            b, pg, errs = open_page(p, 'legacy')
            n0 = len(pg.evaluate(ROWTYPES, 'Bob Producer'))
            pg.evaluate(f"{sel('Bob Producer')}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            lv = pg.evaluate("[...document.querySelectorAll('[data-el=arq] [data-arqlv]')].map(x => x.dataset.arqlv)")
            first = pg.evaluate("[...document.querySelectorAll('[data-el=arq] [data-arqlv=recording] [data-act=arq-pick]')].slice(0, 3).map(b => b.dataset.type)")
            focused = pg.evaluate("document.activeElement && document.activeElement.dataset.f")
            pg.keyboard.type('mix')
            pg.wait_for_timeout(200)
            found = pg.evaluate("[...document.querySelectorAll('[data-el=arq] [data-act=arq-pick]')].map(b => b.dataset.type)")
            pg.locator('[data-el=arq] [data-arqlv=recording] [data-act=arq-pick][data-type=mix]').click()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            rows = pg.evaluate(ROWTYPES, 'Bob Producer')
            print('A)', lv, first, focused, found, rows[n0:], pg.evaluate("!!document.querySelector('[data-el=arq]')"))
            results.append(lv[:1] == ['recording'] and first[:2] == ['performer', 'instrument'] and focused == 'arq-q' and found and all('mix' in t for t in found)
                           and rows[n0:] == [['mix', 'recording']] and not pg.evaluate("!!document.querySelector('[data-el=arq]')"))
            # C) typed by hand; Esc
            pg.evaluate(f"{sel('Bob Producer')}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            pg.keyboard.press('Escape')
            pg.wait_for_timeout(200)
            esc = pg.evaluate("!!document.querySelector('[data-el=arq]')")
            pg.evaluate(f"{sel('Bob Producer')}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            pg.click('[data-el=arq] [data-act=arq-free]')
            pg.wait_for_timeout(300)
            c = pg.evaluate("document.activeElement && document.activeElement.dataset.f")
            print('C)', esc, c)
            results.append(not esc and c == 'role-text')
            # E) (review) one question at a time (another entry's closes it); Enter takes the first type found
            pg.evaluate(f"{sel('Bob Producer')}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            pg.evaluate(f"{sel('Guitar Guy')}.querySelector('[data-act=add-role]').click()")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            boxes = pg.evaluate("[...document.querySelectorAll('[data-el=arq]')].map(x => x.closest('[data-group]').querySelector('.dci-gname').textContent.includes('Guitar Guy'))")
            n2 = len(pg.evaluate(ROWTYPES, 'Guitar Guy'))
            pg.keyboard.type('mix')
            pg.keyboard.press('Enter')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            e = pg.evaluate(ROWTYPES, 'Guitar Guy')[n2:]
            print('E)', boxes, e)
            results.append(boxes == [True] and e == [['mix', 'recording']])
            results.append(not errs)
            b.close()
        with sync_playwright() as p:
            H.discogs_release = rel
            b, pg, errs = open_page(p, 'matrix')
            pg.evaluate(f"{sel('Solo Man')}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            evs = pg.evaluate("[...document.querySelectorAll('[data-el=arq] [data-f=arq-ev]')].map(x => x.checked)")
            pg.evaluate("document.querySelectorAll('[data-el=arq] [data-f=arq-ev]').forEach(x => { if (!x.checked) x.click(); })")
            pg.locator('[data-el=arq] [data-arqlv=recording] [data-act=arq-pick][data-type=producer]').click()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            # ([Z-EMTYPE] 3.108.0) the role of a line a choice: its chosen type
            added = pg.evaluate(f"[...{sel('Solo Man')}.querySelectorAll('tr[data-rows]')].map(x => {{ const r = x.querySelector('select.dci-em-role'); return r ? r.selectedOptions[0].textContent.trim() : x.textContent.replace(/\\s+/g, ' ').trim(); }}).filter(t => /^producer/.test(t))")
            print('B)', evs, added)
            results.append(len(evs) >= 1 and evs[0] and not any(evs[1:]) and len(added) == len(evs))
            results.append(not errs)
            b.close()
        with sync_playwright() as p:
            H.discogs_release = orig
            b, pg, errs = open_page(p, 'legacy', off=True)
            pg.evaluate(f"{sel('Bob Producer')}.querySelector('[data-act=add-role]').click()")
            pg.wait_for_timeout(300)
            d = [pg.evaluate("!!document.querySelector('[data-el=arq]')"), pg.evaluate("document.activeElement && document.activeElement.dataset.f")]
            print('D)', d)
            results.append(d == [False, 'role-text'])
            b.close()
    finally:
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_arq387():
    """Credits Importer 3.87.0 (collected items Z-ARQ2, Z-ARQ3): "＋ Another role" of Bob Producer (rows, the classic view).
    A) The types as columns, one for each level in its colour (Recording first); a search without a hit on a level: that column left
       out ("mix": no column Work); nothing found: no column.
    B) "＋ New event": its tracks (all four ticked) – 1 and 2 off, a date typed (2020-05-05); "producer" of Recording: a row on
       tracks 3, 4 with that date.
    C) "instrument" chosen, "percussion" as its instrument: no role credit (until 3.86.0 "instrument").
    D) (review) Staged: the producer of the new event (tracks 3, 4, dated) beside Bob's producer without a date on all four.
    E) (review) A date that cannot be read ("soon"): a message, the types off; no track ("none"): the types off too."""
    import common_rows as C
    H.ENTRIES_VIEW = 'legacy'
    sel = lambda name: f"[...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes({name!r}))"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)

        def ask():
            pg.evaluate(f"{sel('Bob Producer')}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
        COLS = "[...document.querySelectorAll('[data-el=arq] .dci-arq-col')].map(c => c.dataset.arqlv + ':' + (c.getAttribute('style') || '').includes('--dci-lvl-' + c.dataset.arqlv))"
        ask()
        a0 = pg.evaluate(COLS)
        pg.keyboard.type('mix')
        pg.wait_for_timeout(200)
        a1 = pg.evaluate(COLS)
        pg.keyboard.type('qqq')
        pg.wait_for_timeout(200)
        a2 = [pg.evaluate(COLS), pg.evaluate("document.querySelector('[data-el=arq-list]').textContent.trim().slice(0, 30)")]
        print('A)', a0, a1, a2)
        results.append(len(a0) >= 2 and a0[0] == 'recording:true' and all(x.endswith('true') for x in a0) and 'work:true' in a0 and 'work:true' not in a1 and a1 and a2[0] == [] and a2[1].startswith('No relationship type'))
        pg.keyboard.press('Escape')
        n0 = len(C.rows_of(pg, 'Bob Producer'))
        ask()
        pg.click('[data-el=arq] [data-f=arq-new]')
        pg.wait_for_timeout(200)
        on0 = pg.evaluate("[...document.querySelectorAll('[data-el=arq-new] [data-act=arq-ntrack]')].map(b => b.getAttribute('aria-pressed'))")
        pg.click('[data-el=arq-new] [data-act=arq-ntrack][data-i="0"]')
        pg.click('[data-el=arq-new] [data-act=arq-ntrack][data-i="1"]')
        pg.fill('[data-el=arq-new] [data-f=arq-ndate]', '2020-05-05')
        pg.locator('[data-el=arq] [data-arqlv=recording] [data-act=arq-pick][data-type=producer]').click()
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        rows = C.rows_of(pg, 'Bob Producer')[n0:]
        tr = C.tracks_of_rows(pg, 'Bob Producer')
        print('B)', on0, rows, tr[-1:] if tr else tr)
        results.append(on0 == ['true'] * 4 and len(rows) == 1 and rows[0].endswith('2020-05-05') and (not tr or tr[-1] == [3, 4]))
        ask()
        pg.locator('[data-el=arq] [data-arqlv=recording] [data-act=arq-pick][data-type=instrument]').click()
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        rid = pg.evaluate(f"[...{sel('Bob Producer')}.querySelectorAll('tr.dci-row')].pop().dataset.row")
        f = pg.locator(f'tr[data-row="{rid}"] [data-f=primary]')
        f.fill('percussion')
        f.evaluate("e => e.dispatchEvent(new Event('change', { bubbles: true }))")
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        c = pg.evaluate(f"(() => {{ const e = document.querySelector('tr[data-row=\"{rid}\"] [data-f=role-credit]'); return e ? [e.value, e.placeholder] : null; }})()")
        print('C)', c)
        results.append(c is not None and c[0] == '' and 'instrument' not in (c[1] or '').lower())
        # D) (review) staged: the dated row beside the undated one of tracks 3, 4 – not merged into it (until the review lost)
        C.stage(pg)
        BOB = H.ARTISTS[3005][0]
        d = pg.evaluate(f"""MB.relationshipEditor.state.added.filter(r => r.linkTypeID === 141 && ((r.entity0 || {{}}).gid === '{BOB}' || (r.entity1 || {{}}).gid === '{BOB}'))
          .map(r => (r.begin_date || {{}}).year || 0)""")
        # E) (review) a date that cannot be read, or no track: a message, the types off
        ask()
        pg.click('[data-el=arq] [data-f=arq-new]')
        pg.wait_for_timeout(200)
        pg.fill('[data-el=arq-new] [data-f=arq-ndate]', 'soon')
        e1 = pg.evaluate("[!document.querySelector('[data-el=arq-nerr]').hidden, [...document.querySelectorAll('[data-el=arq] .dci-arq-type')].every(b => b.disabled)]")
        pg.fill('[data-el=arq-new] [data-f=arq-ndate]', '')
        pg.click('[data-el=arq-new] [data-act=arq-nnone]')
        pg.wait_for_timeout(200)
        e2 = pg.evaluate("[[...document.querySelectorAll('[data-el=arq] .dci-arq-type')].every(b => b.disabled), document.querySelector('[data-el=arq-nerr]').hidden]")
        pg.click('[data-el=arq] [data-act=arq-close]')
        pg.wait_for_timeout(200)
        print('D)', sorted(d), 'E)', e1, e2)
        results.append(sorted(d) == [0, 0, 0, 0, 2020, 2020] and e1 == [True, True] and e2 == [True, True])
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_arr394():
    """Credits Importer 3.94.0 (Z-ARRL, Z-ARRD; rule S150): arrangements of works.
    A) Discogs "Arranged By – Writer Z" (no writing credits on the release): arranger on the works (the works matrix); the entry among
       "Writing credits and arrangements of the works" (after the other entries); its line "arranger · Work" – a click puts it back on
       "Recording", the entry among the others again; its level then clicks through Recording → Release → Work and stays a button.
    B) Discogs "Arranged By [Strings]": on the recordings (an arrangement for the recording).
    C) A text "All songs were arranged by Writer Z": on the works; "Arranged by Writer Z" alone: on the recordings; (review) not a song
       word elsewhere in the line ("Melody Gardot - vocals, arrangements", "Vocals on tracks 2, 4 by Jane Doe, arranged by Writer Z").
    D) Bandcamp "All songs was written & arranged by Writer Z": arranger on the works (until 3.93.0 on the recordings)."""
    H.lt(9297, H.uid('1a1a1a1a', 9297), 'arranger', 'artist', 'recording', ())
    H.lt(9295, H.uid('1a1a1a1a', 9295), 'arranger', 'artist', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release
    WZ = "[...document.querySelectorAll('section.dci-group')].find(g => /Writer Z/.test((g.querySelector('.dci-gname') || {}).textContent || ''))"
    STATE = f"""(() => {{ const g = {WZ}; if (!g) return null; const wo = !!g.closest('[data-el=workonly]');
      return [wo, [...g.querySelectorAll('[data-act=em-evlevel-next], [data-act=arr-level]')].map(x => x.textContent.trim()),
        (document.querySelector('[data-el=workonly] h3') || {{ textContent: '' }}).textContent.trim()]; }})()"""
    MXCOL = "[...document.querySelectorAll('.dci-works th')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Writer Z/.test(t))"
    results = []

    def discogs(role):
        def rel():
            d = orig()
            for t in d['tracklist']:
                t['extraartists'] = []
            d['extraartists'].append({'name': 'Writer Z', 'anv': '', 'role': role, 'tracks': '', 'id': 3009, 'join': ''})
            return d
        return rel

    def open_pg(p):
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        return b, pg, errs

    try:
        H.ENTRIES_VIEW = 'matrix'
        # A) "Arranged By"
        H.discogs_release = discogs('Arranged By')
        with sync_playwright() as p:
            b, pg, errs = open_pg(p)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(400)
            a0 = pg.evaluate(STATE)
            mx = pg.evaluate(MXCOL)
            seq = []
            for _ in range(4):
                pg.locator(f"section.dci-group:has(.dci-gname:has-text('Writer Z')) [data-act=em-evlevel-next], section.dci-group:has(.dci-gname:has-text('Writer Z')) [data-act=arr-level]").first.click()
                pg.wait_for_timeout(400)
                seq.append(pg.evaluate(STATE))
            print('A)', a0, mx, '\n  ', seq)
            results.append(a0 == [True, ['Work'], 'Writing credits and arrangements of the works'] and len(mx) == 1 and 'arranger' in mx[0]
                           and [x[:2] for x in seq] == [[False, ['Recording']], [False, ['Release']], [True, ['Work']], [False, ['Recording']]] and not errs)
            b.close()
        # B) "Arranged By [Strings]"
        H.discogs_release = discogs('Arranged By [Strings]')
        with sync_playwright() as p:
            b, pg, errs = open_pg(p)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(400)
            b0 = pg.evaluate(STATE)
            print('B)', b0)
            results.append(b0 is not None and b0[0] is False and b0[1] == ['Recording'])
            b.close()
        # C) texts
        H.discogs_release = orig
        out = []
        for text in ['All songs were arranged by Writer Z\nJane Doe: guitar', 'Arranged by Writer Z\nJane Doe: guitar',
                     'Melody Gardot - vocals, arrangements\nVocals on tracks 2, 4 by Jane Doe, arranged by Writer Z']:
            with sync_playwright() as p:
                b, pg, errs = open_pg(p)
                H.src_menu(pg, 'text-open')
                pg.fill('[data-f=text-src]', text)
                pg.click('[data-act=text-load]')
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
                H.wait_still(pg, "document.body.innerHTML", 10, 300)
                out.append([pg.evaluate(f"(() => {{ const g = {WZ}; return g ? !!g.closest('[data-el=workonly]') : null; }})()"), len(pg.evaluate(MXCOL))])
                b.close()
        print('C)', out)
        results.append(out == [[True, 1], [False, 0], [False, 0]])
    finally:
        H.discogs_release = orig
    # D) Bandcamp
    album = 'https://testband.bandcamp.com/album/testalbum'
    H.BC_PAGES[album] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'All songs was written & arranged by Writer Z\n\nJane Doe: guitar',
                                  'about': '', 'release_date': '01 Jan 2023 00:00:00 GMT'},
                                  'trackinfo': [{'track_num': i + 1, 'title': t, 'duration': 180.0} for i, t in enumerate(H.TITLES)]}, band='Test Band')
    orig_ws = H.ws_release

    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': album}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d
    H.ws_release = ws
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            d = [pg.evaluate(f"(() => {{ const g = {WZ}; return g ? !!g.closest('[data-el=workonly]') : null; }})()"), pg.evaluate(MXCOL)]
            print('D)', d)
            results.append(d[0] is True and len(d[1]) == 1 and 'arranger' in d[1][0] and not errs)
            b.close()
    finally:
        H.ws_release = orig_ws
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_qgtr397():
    """Credits Importer 3.97.0 (collected item Z-QGTR): the questions of an instrument family also offer the family itself.
    A) Chips ▾: "Guitar" (Q002) – electric guitar · acoustic guitar · guitar; "Bass" (Q001) – … · bass guitar; "Horns" (Q013, horn
       set at once) – brass · wind instruments.
    B) "guitar" chosen for "Guitar": the chip "guitar" without "?" (the question answered – until 3.96.0 the word itself kept asking),
       ▾ offers the others (as for "Horns"); staged: guitar without a role credit.
    C) "wind instruments" chosen for "Horns": "wind instruments “horns”"."""
    H.ENTRIES_VIEW = 'matrix'
    H.attr(9152, 'horn', 14, 14)
    H.attr(9153, 'brass', 14, 14)
    H.attr(9154, 'wind instruments', 14, 14)
    H.attr(9155, 'bass guitar', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CREDITS = [('Low Man', 'Guitar, Bass, Horns', 3081)]
    for n, _r, i in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d

    H.discogs_release = rel
    CHIPS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [...g.querySelectorAll('.dci-em-cl .dci-em-chip')].map(c => ({ name: c.querySelector('.dci-em-chipname').textContent.replace(/\\s+/g, ' ').trim(),
        q: !!c.querySelector('[data-act=em-chipask]'), line: c.dataset.line })) : null; }"""
    MENU = "() => [...document.querySelectorAll('.dci-em-chipmenu button')].map(b => b.textContent.trim())"
    STAGED = """(() => MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity0.name === 'Low Man').map(r => (r.attributes && r.attributes.__tree ? r.attributes.__tree : [])
      .map(a => (a.type ? a.type.name : '') + (a.credited_as ? ' “' + a.credited_as + '”' : ''))).flat().filter((x, i, a) => a.indexOf(x) === i).sort())()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            pg.click('.dci-head [data-act=view-toggle]')
            pg.wait_for_timeout(600)
            low = sec_sel(pg, 'Low Man')

            def menu_of(word):
                c = next((x for x in pg.evaluate(CHIPS, 'Low Man') or [] if word in x['name'].lower()), None)
                if not c or not c['q'] and word != 'horn':
                    return c, None
                btn = pg.locator(f'{low} .dci-em-chip[data-line="{c["line"]}"] [data-act=em-chipask]')
                if not btn.count():
                    return c, None
                btn.click(); pg.wait_for_timeout(400)
                m = pg.evaluate(MENU)
                pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
                return c, m
            a0 = pg.evaluate(CHIPS, 'Low Man')
            g, mg = menu_of('guitar')
            ba, mb = menu_of('bass')
            print('A)', a0, '| Guitar:', mg, '| Bass:', mb)
            results.append(mg == ['electric guitar', 'acoustic guitar', 'guitar'] and mb == ['electric bass guitar', 'double bass', 'acoustic bass guitar', 'bass guitar'])
            pg.click(f'{low} .dci-em-chip[data-line="{g["line"]}"] [data-act=em-chipask]'); pg.wait_for_timeout(400)
            pg.click(f'{low} .dci-em-chipmenu [data-act=instr-pick][data-instr="guitar"]'); pg.wait_for_timeout(500)
            b0 = pg.evaluate(CHIPS, 'Low Man')
            g2 = next((x for x in b0 if x['name'].startswith('guitar') or x['name'] == '? guitar'), None)
            print('B)', b0)
            # (like "Horns": ▾ stays for the other answers, the "?" goes)
            results.append(bool(g2) and g2['name'] == 'guitar')
            # the Horns chip: horn set at once, its ▾ (no "?") offers brass and wind instruments
            h = next((x for x in b0 if 'horn' in x['name']), None)
            mh = None
            if h:
                pg.locator(f'{low} .dci-em-chip[data-line="{h["line"]}"] .dci-em-chipname').first.evaluate('x => 0')
                btn = pg.locator(f'{low} .dci-em-chip[data-line="{h["line"]}"] [data-act=em-chipask]')
                if btn.count():
                    btn.click(); pg.wait_for_timeout(400)
                    mh = pg.evaluate(MENU)
                    if 'wind instruments' in (mh or []):
                        pg.click(f'{low} .dci-em-chipmenu [data-act=instr-pick][data-instr="wind instruments"]'); pg.wait_for_timeout(500)
            c0 = pg.evaluate(CHIPS, 'Low Man')
            print('C)', h, mh, c0)
            results.append(mh == ['brass', 'wind instruments'] and any(x['name'] == 'wind instruments “horns”' for x in c0))
            pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
            pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
            d0 = pg.evaluate(STAGED)
            print('D)', d0)
            results.append('guitar' in d0 and 'wind instruments “horns”' in d0)
            print('Fehler:', errs)
            results.append(not errs)
        finally:
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_msyn397():
    """Credits Importer 3.97.0 (collected item Z-MSYN; rule S155, off and greyed): several models of one instrument of an entry on a
    recording – one instrument, the role credits joined by commas.
    Synth Man: "Synthesizer [Juno 6]" on tracks 1–2, "Synthesizer [Multipoly]" on tracks 1–3; Guitar Man: "Electric Guitar
    [Telecaster]" and "Electric Guitar [Les Paul]" on track 4.
    A) Matrix (joined): tracks 1–2 one synthesizer “juno 6, multipoly” each, track 3 synthesizer “multipoly” (until 3.96.0 the second
       row of the same relationship was left out – tracks 1–2 only “juno 6”); track 4 one electric guitar “Telecaster, Les Paul”.
    B) "Join the instruments … " off (⚙ Settings, stored): the same – the models of one instrument are still one relationship.
    C) Mapping rules: the quick switch S155 "… each role credit on its own" – off, disabled, its note below the switches; a click
       changes nothing; its checkbox in the list disabled."""
    CREDITS = [('Synth Man', 'Synthesizer [Juno 6]', 3091, '1 to 2'), ('Synth Man', 'Synthesizer [Multipoly]', 3091, '1 to 3'),
               ('Guitar Man', 'Electric Guitar [Telecaster]', 3092, '4'), ('Guitar Man', 'Electric Guitar [Les Paul]', 3092, '4')]
    for n, _r, i, _t in CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)
    orig = H.discogs_release

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in CREDITS}
    rec_no = {g: k + 1 for k, g in enumerate(H.REC)}

    def summary(rels):
        return sorted((names.get(r['a']) or names.get(r['b']) or '?', rec_no.get(r['b']) or rec_no.get(r['a']) or 0, tuple(sorted(r['attrs'])))
                      for r in rels if (names.get(r['a']) or names.get(r['b'])))
    # (the details of Discogs in lower case as before – "juno 6")
    # ([3.99.0, Z-JUNO] models of the mapping in Discogs's brackets as written: "Juno 6", "Multipoly")
    want = [('Guitar Man', 4, ('electric guitar [Telecaster, Les Paul]',)), ('Synth Man', 1, ('synthesizer [Juno 6, Multipoly]',)),
            ('Synth Man', 2, ('synthesizer [Juno 6, Multipoly]',)), ('Synth Man', 3, ('synthesizer [Multipoly]',))]
    results = []
    with sync_playwright() as p:
        H.BROWSER = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            ctx, pg, errs, mx, _label = staged_by(None, 'matrix')
            a0 = summary(mx)
            print('A) verbunden:', a0)
            results.append(a0 == want)
            ctx.close()
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(H.BROWSER)
            ctx.add_init_script(script="try { localStorage.setItem('dci-join', 'false'); } catch (e) {}")
            pg, errs2 = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            pg.click('[data-act=apply]'); pg.wait_for_timeout(1500)
            b0 = summary(pg.evaluate(ADDED))
            print('B) einzeln:', b0)
            results.append(b0 == want)
            # C) the quick switch in "Mapping rules"
            pg.click('.dci-head [data-act=rules]')
            pg.wait_for_selector('#dci-rules [data-rsect=roles]')
            pg.wait_for_timeout(300)
            QS = """(() => { const b = document.querySelector('#dci-rules [data-qs-toggle=S155]'); const n = document.querySelector('#dci-rules [data-qs-note=S155]');
              const c = document.querySelector('#dci-rules input[data-rule-on=S155]');
              return b ? [b.getAttribute('aria-pressed'), b.disabled, b.textContent.replace(/\\s+/g, ' ').trim(), n ? n.textContent : '', c ? c.disabled : null, c ? c.checked : null] : null; })()"""
            c0 = pg.evaluate(QS)
            if c0:
                pg.evaluate("document.querySelector('#dci-rules [data-qs-toggle=S155]').click()")
                pg.wait_for_timeout(300)
            c1 = pg.evaluate(QS)
            print('C)', c0, c1)
            results.append(bool(c0) and c0[0] == 'false' and c0[1] is True and 'each role credit on its own' in c0[2] and 'Cannot be switched on yet' in c0[3]
                           and c0[4] is True and c0[5] is False and c1 == c0)
            print('Fehler:', errs, errs2)
            results.append(not errs and not errs2)
        finally:
            H.discogs_release = orig
            H.BROWSER.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



# [Z-ALIGN] (3.100.0) a person with an instrument and three roles of their own (recording level), one at the release level
ALIGN_CREDITS = [('Mix Man', 'Electric Guitar [Solo], Producer, Mixed By, Mastered By', 3075, '')]

# the geometry of an entry's matrix: its tables, the words of its head, per line its role, the centre of each event cell (None:
# the block does not show that event; '' no checkbox), its attributes (together: the words of the labels, separate: per column)
ALIGN = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const tbl = g.querySelector('.dci-em-grid');
  const cx = (el) => { const r = el.getBoundingClientRect(); return Math.round((r.left + r.width / 2) * 10) / 10; };
  return { tables: g.querySelectorAll('.dci-em-grid').length, blocks: g.querySelectorAll('.dci-em-block').length,
    head: [...tbl.querySelectorAll('thead th')].map(t => t.classList.contains('dci-em-ev') ? 'EV' : t.textContent.replace(/\\s+/g, ' ').trim()),
    lines: [...tbl.querySelectorAll('tr.dci-em-line')].map(tr => ({ role: ((tr.querySelector('[data-f=em-primary]') || {}).value) || tr.querySelector('.dci-em-c-role').textContent.replace(/\\s+/g, ' ').trim(),
      ev: [...tr.querySelectorAll('td.dci-em-c-ev')].map(td => td.classList.contains('dci-em-c-none') ? null : td.querySelector('input') ? cx(td.querySelector('input')) : ''),
      joint: [...tr.querySelectorAll('td.dci-em-c-flags label')].map(l => (l.querySelector('input').checked ? '+' : '') + l.textContent.trim()),
      split: [...tr.querySelectorAll('td.dci-em-c-flag')].map(td => { const c = td.querySelector('input'); return c ? (c.checked ? '+' : '') + c.value : ''; }) })),
    store: localStorage.getItem('dci-em-attr') }; }"""


def aligned(geo):
    """Every event column: the checkboxes of all lines at the same place (±1 px); a cell of each line in each column."""
    if not geo or not geo['lines']:
        return False
    n = len(geo['lines'][0]['ev'])
    for i in range(n):
        xs = [ln['ev'][i] for ln in geo['lines'] if len(ln['ev']) == n and isinstance(ln['ev'][i], float)]
        if any(len(ln['ev']) != n for ln in geo['lines']) or not xs or max(xs) - min(xs) > 1:
            return False
    return True


def case_align3100():
    """Credits Importer 3.100.0 (collected item Z-ALIGN; with a screenshot: each role of an entry a table of its own, the event
    and attribute columns of the blocks at other places – "so kann man es nicht Matrix nennen"): an entry's matrix is one table.
    A) Mix Man (electric guitar with "solo", producer, mixer, mastering): one table, its head once ("Attributes" one column, two
       events); each block a part of it; the ticks of all lines exactly below each other; the guitar's attributes together
       (add. guest +solo).
    B) "guest" ticked by its word: the guitar's rows get it.
    C) The head stays on top while the table scrolls (its box made low).
    D) "Attributes: separate" above the matrix: a column per attribute of the entry (add., guest, solo, assistant), ticks
       still aligned; stored ("split"); ⚙ Settings → Staging shows "separate" pressed; "together" there: one column again,
       nothing stored.
    E) ⚙ Settings → Staging "Events shared … up to 1": each block shows its own events – still one table, a line has an empty
       cell under an event of another block, aligned."""
    orig = H.discogs_release
    for n, _r, i, _t in ALIGN_CREDITS:
        H.ARTISTS[i] = (H.uid('dddddddd', i - 2990), n)

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, i, t in ALIGN_CREDITS]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        try:
            H.ENTRIES_VIEW = 'matrix'
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1500)
            a = pg.evaluate(ALIGN, 'Mix Man')
            print('A)', a)
            gtr = [ln for ln in (a or {}).get('lines', []) if ln['role'] == 'electric guitar']
            results.append(bool(a) and a['tables'] == 1 and a['blocks'] >= 3 and 'Attributes' in a['head'] and a['head'].count('EV') == 2
                           and len(a['lines']) >= 4 and aligned(a) and bool(gtr) and gtr[0]['joint'][:3] == ['add.', 'guest', '+solo']
                           and a['store'] is None)
            sec = sec_sel(pg, 'Mix Man')
            pg.click(f'{sec} tr.dci-em-line:has([data-f=em-primary][value="electric guitar"]) td.dci-em-c-flags label:has([value=guest])')
            pg.wait_for_timeout(400)
            bl = pg.evaluate(BLOCKS, 'Mix Man')
            gflags = [ln['flags'] for blk in (bl or []) for ln in blk['lines'] if ln['role'] == 'electric guitar']
            print('B)', gflags)
            results.append(gflags == [['guest', 'solo']] or gflags == [['solo', 'guest']])
            c = pg.evaluate("""(sel) => { const w = document.querySelector(sel + ' .dci-em-onewrap'); if (!w) return null; w.style.maxHeight = '90px'; w.scrollTop = 40;
              const th = w.querySelector('thead th'); return { scrolled: w.scrollTop, off: Math.round(th.getBoundingClientRect().top - w.getBoundingClientRect().top - w.clientTop) }; }""", sec)
            print('C)', c)
            results.append(bool(c) and c['scrolled'] > 0 and abs(c['off']) <= 1)
            pg.evaluate("(sel) => { const w = document.querySelector(sel + ' .dci-em-onewrap'); w.style.maxHeight = ''; w.scrollTop = 0; }", sec)
            pg.click(f'{sec} [data-act=em-attr][data-attr=split]')
            pg.wait_for_timeout(500)
            d = pg.evaluate(ALIGN, 'Mix Man')
            words = [h for h in d['head'] if h in ('add.', 'guest', 'solo', 'co', 'executive', 'assistant', 'associate')] if d else []
            H.open_settings(pg, 'staging')
            pressed = pg.evaluate("[...document.querySelectorAll('[data-el=settings] [data-act=em-attr]')].map(b => b.dataset.attr + ':' + b.getAttribute('aria-pressed'))")
            print('D)', d and d['head'], d and [ln['split'] for ln in d['lines']], d and d['store'], pressed)
            gs = [ln['split'] for ln in (d or {}).get('lines', []) if ln['role'] == 'electric guitar']
            results.append(bool(d) and d['tables'] == 1 and 'Attributes' not in d['head'] and {'add.', 'guest', 'solo', 'assistant'} <= set(words)
                           and aligned(d) and bool(gs) and '+guest' in gs[0] and '+solo' in gs[0] and d['store'] == '"split"' and pressed == ['joint:false', 'split:true'])
            pg.click('[data-el=settings] [data-act=em-attr][data-attr=joint]')
            pg.wait_for_timeout(500)
            d2 = pg.evaluate(ALIGN, 'Mix Man')
            print('D2)', d2 and d2['head'], d2 and d2['store'])
            results.append(bool(d2) and 'Attributes' in d2['head'] and d2['store'] is None)
            pg.fill('[data-set=ev-shared]', '1')
            pg.press('[data-set=ev-shared]', 'Tab')
            pg.wait_for_timeout(500)
            e = pg.evaluate(ALIGN, 'Mix Man')
            print('E)', e and [(ln['role'], ln['ev']) for ln in e['lines']], e and e['tables'])
            nones = [ln['ev'].count(None) for ln in (e or {}).get('lines', [])]
            results.append(bool(e) and e['tables'] == 1 and e['head'].count('EV') == 2 and aligned(e) and any(nones) and all(n < 2 for n in nones))
            print('Fehler:', errs)
            results.append(not errs)
            ctx.close()
        finally:
            H.ENTRIES_VIEW = 'legacy'
            H.discogs_release = orig
            b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_rwrt3100():
    """Credits Importer 3.100.0 (collected item Z-RWRT): "＋ Another role" offers the writing roles on the release level – writer,
    composer, lyricist, librettist (as on MusicBrainz, artist–release) – always, under "Writing" below the release's other types
    (until 3.99.0 behind "+ n more"). Bob Producer: "composer" chosen there – a row "composer" on the release; staged: an
    artist–release "composer" relationship."""
    import copy
    orig = H.discogs_release
    lts0, linked0 = copy.deepcopy(H.LTS), copy.deepcopy(H.LINKED.get('link_type'))
    for i, gid, name in ((54, 'ca7a474a-a1cd-4431-9230-56a17f553090', 'writer'), (55, '01ce32b0-d873-4baa-8025-714b45c0c754', 'composer'),
                         (56, 'a2af367a-b040-46f8-af21-310f92dfe97b', 'lyricist'), (57, 'dd182715-ca2b-4e4b-80b1-d21742fda0dc', 'librettist')):
        H.lt(i, gid, name, 'artist', 'release', (1,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    sel = "[...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes('Bob Producer'))"
    ROWTYPES = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname').textContent.includes(name));
      return g ? [...g.querySelectorAll('tr.dci-row')].map(r => { const t = r.querySelector('[data-f=type]'); return [(t && t.selectedOptions[0] || {}).text || '', (r.querySelector('[data-act=level][aria-pressed=true]') || {}).dataset ? r.querySelector('[data-act=level][aria-pressed=true]').dataset.level : '']; }) : []; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            n0 = len(pg.evaluate(ROWTYPES, 'Bob Producer'))
            pg.evaluate(f"{sel}.querySelector('[data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            col = pg.evaluate("""(() => { const c = document.querySelector('[data-el=arq] [data-arqlv=release] .dci-arq-colb'); if (!c) return null;
              const kids = [...c.children]; const k = kids.findIndex(x => x.dataset.arqsub === 'writing');
              return { sub: k < 0 ? null : kids[k].textContent.trim(), writing: k < 0 ? [] : kids.slice(k + 1).map(x => x.dataset.type), before: kids.slice(0, Math.max(k, 0)).map(x => x.dataset.type || x.textContent.trim()) }; })()""")
            print('A)', col)
            results.append(bool(col) and col['sub'] == 'Writing' and col['writing'] == ['writer', 'composer', 'lyricist', 'librettist']
                           and not set(col['writing']) & set(col['before']))
            pg.locator('[data-el=arq] [data-arqlv=release] [data-act=arq-pick][data-type=composer]').click()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            rows = pg.evaluate(ROWTYPES, 'Bob Producer')[n0:]
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate("MB.relationshipEditor.state.added.map(r => r.linkTypeID)")
            print('B)', rows, added)
            results.append(rows == [['composer', 'release']] and 55 in added)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.LINKED['link_type'] = linked0
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_artl3100():
    """Credits Importer 3.100.0 (collected item Z-ARTL, rule S159): a label credited for the artwork ("Artwork: Cyclical Dreams" on
    the label's Bandcamp page) – most such names are people, so only a label beyond doubt.
    Discogs: "Artwork – Cyclical Dreams" (a label of the release in MusicBrainz), "Artwork – Other Label" (only in Discogs's labels),
    "Artwork – Pat Person" (no label).
    A) Cyclical Dreams: a label entry, linked to MusicBrainz's label at once, "Linked as the label: MusicBrainz has it as a label of
       this release"; its row the label–release "artwork". Other Label: a label (not linked – MusicBrainz's label still to choose),
       "As the label – Discogs lists it …". Pat Person stays an artist.
    B) "As an artist instead": an artist again, its row artist–release "artwork"; "As the label": the label again.
    C) Staged: a label–release "artwork" relationship of Cyclical Dreams.
    D) (review) "＋ Another role" design while it is the label, then "As an artist instead": nothing of one kind staged with the other.
    E) (review) "Linked Label", found through its Discogs link, stays an artist although the release has a label of that name."""
    import copy
    orig = H.discogs_release
    lts0, linked0, labels0 = copy.deepcopy(H.LTS), copy.deepcopy(H.LINKED.get('link_type')), list(H.RELEASE_LABELS)
    H.lt(993, H.uid('1aaa0000', 993), 'artwork', 'artist', 'release', (1,))
    for i, name in ((1170, 'artwork'), (1171, 'design'), (1172, 'graphic design'), (1173, 'illustration'), (1174, 'art direction'), (1175, 'photography')):
        H.lt(i, H.uid('1aaa0000', i), name, 'label', 'release', ())
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    LAB = H.uid('1abe1000', 1)
    H.RELEASE_LABELS[:] = [(LAB, 'Cyclical Dreams')]
    H.COMPANIES[9901] = ('label', LAB, 'Cyclical Dreams')
    CR = [('Cyclical Dreams', 'Artwork', 3101), ('Other Label', 'Artwork', 3102), ('Pat Person', 'Artwork', 3103), ('Linked Label', 'Artwork', 3104)]
    # ((review) an artist found through its Discogs link stays that artist, though MusicBrainz has a label of that name on the release
    H.ARTISTS[3104] = (H.uid('dddddddd', 3104), 'Linked Label')
    H.RELEASE_LABELS.append((H.uid('1abe1000', 2), 'Linked Label'))

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CR]
        d['companies'] = []
        d['labels'] = [{'name': 'Other Label', 'id': 9102, 'catno': 'OL 1'}]
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    ENT = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const n = g.querySelector('[data-el=artl]');
      return { kind: [...g.classList].find(c => c.startsWith('dci-kind-')), link: (g.querySelector('.dci-gmatch a[href*="/label/"], .dci-gmatch a[href*="/artist/"]') || {}).getAttribute ? (g.querySelector('.dci-gmatch a[href*="/label/"], .dci-gmatch a[href*="/artist/"]') || { getAttribute: () => '' }).getAttribute('href') : '',
        note: n ? n.textContent.replace(/\\s+/g, ' ').trim() : '', types: [...g.querySelectorAll('tr.dci-row [data-f=type]')].map(t => (t.selectedOptions[0] || {}).text || '') }; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            a = [pg.evaluate(ENT, n) for n in ('Cyclical Dreams', 'Other Label', 'Pat Person')]
            print('A)', a)
            results.append(bool(a[0]) and a[0]['kind'] == 'dci-kind-label' and a[0]['link'] == f'/label/{LAB}'
                           and a[0]['note'].startswith('Linked as the label: MusicBrainz has it as a label of this release.') and 'As an artist instead' in a[0]['note']
                           and a[0]['types'] == ['artwork']
                           and bool(a[1]) and a[1]['kind'] == 'dci-kind-label' and a[1]['note'].startswith('As the label – Discogs lists it as a label or company of this release; choose')
                           and bool(a[2]) and a[2]['kind'] == 'dci-kind-artist' and a[2]['note'] == '')
            sec = sec_sel(pg, 'Cyclical Dreams')
            pg.click(f'{sec} [data-act=artl-toggle]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            b1 = pg.evaluate(ENT, 'Cyclical Dreams')
            pg.click(f'{sec} [data-act=artl-toggle]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            b2 = pg.evaluate(ENT, 'Cyclical Dreams')
            print('B)', b1, b2)
            results.append(bool(b1) and b1['kind'] == 'dci-kind-artist' and b1['note'].startswith('Credited as an artist') and 'As the label' in b1['note'] and b1['types'] == ['artwork']
                           and b2 == a[0])
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate("MB.relationshipEditor.state.added.map(r => [r.linkTypeID, (r.entity0 || {}).gid, (r.entity1 || {}).gid])")
            print('C)', [x for x in added if x[0] in (993, 1170)])
            results.append(any(x[0] == 1170 and LAB in (x[1], x[2]) for x in added))
            # D) (review) a role added while it is the label ("＋ Another role" → design), then "As an artist instead": no label type with
            # the artist, no artist type with the label staged; E) Linked Label (found through its link) stays an artist
            pg.evaluate(f"document.querySelector('{sec} [data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            pg.locator('[data-el=arq] [data-arqlv=release] [data-act=arq-pick][data-type=design]').click()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            d1 = pg.evaluate(ENT, 'Cyclical Dreams')
            pg.click(f'{sec} [data-act=artl-toggle]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            d2 = pg.evaluate(ENT, 'Cyclical Dreams')
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            kinds = pg.evaluate("MB.relationshipEditor.state.added.map(r => [r.linkTypeID, (r.entity0 || {}).entityType])")
            e0 = pg.evaluate(ENT, 'Linked Label')
            print('D)', d1, d2, [x for x in kinds if x[0] in (993, 1170, 1171, 928)], 'E)', e0)
            results.append(bool(d1) and d1['types'] == ['artwork', 'design'] and bool(d2) and d2['kind'] == 'dci-kind-artist'
                           and not any(x[0] in (1170, 1171) and x[1] == 'artist' for x in kinds) and not any(x[0] in (993, 928) and x[1] == 'label' for x in kinds)
                           and bool(e0) and e0['kind'] == 'dci-kind-artist' and e0['note'] == '')
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.LINKED['link_type'] = linked0
        H.RELEASE_LABELS[:] = labels0
        H.COMPANIES.pop(9901, None)
        H.ARTISTS.pop(3104, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_detail3102():
    """Credits Importer 3.102.0 (collected items Z-DATP, Z-UNCR, Z-PLAYS, Z-LNTR, Z-LITI; rules D031, S167, S168, R117): Detail – "A Concert"
    as Discogs lists it: "Double Bass [Uncredited] – Barry Guy, Johnny Dyani", "Drums [Uncredited] – John Stevens (2)", "Trombone [Uncredited] –
    Paul Rutherford (2)", "Soprano Saxophone, Tenor Saxophone – Frode Gjerstad", (for the test) Barry Guy also "Producer", "Liner Notes
    [Translation By (English)] – Sebastian Scotney", "Little Instruments – Pat Person"; the notes "This was recorded by Norwegian State radio,
    at the Hennie-Onstad art centre outside Oslo on September 11th 1983. The first time I played with Rutherford and Guy. At the time I played
    soprano and tenor sax." and (for the test) "On the second part I also played bass clarinet and tenor sax."
    A) Johnny Dyani (only uncredited): on Skip, at the entry "Not named on the release (Discogs: uncredited) – on Skip:" with "Take anyway";
       Barry Guy: his producer row as before, double bass on Skip with "Take “double bass” anyway"; "Take all uncredited" offered.
    B) "Take anyway" at Johnny Dyani: his row on the recording, Barry Guy's still on Skip; (review) Paul Rutherford's level clicked by hand:
       no note any more; "Take all uncredited": none on Skip, no such note.
    C) The pool: September 11th 1983 a performance date (until 3.101.0 "recorded" was too far before the date).
    D) "I played soprano and tenor sax": nothing asked (credited); "bass clarinet": asked once above the entries, Frode Gjerstad chosen
       (he plays the tenor sax of that sentence); taken: his row bass clarinet, the question gone.
    E) Staged: Sebastian Scotney's liner notes with the attribute translator; Pat Person other instruments "Little Instruments"."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    for i, n in ((9124, 'other instruments'), (9130, 'trombone'), (9131, 'soprano saxophone'), (9132, 'tenor saxophone'), (9133, 'bass clarinet')):
        H.attr(i, n, 14, 14)
    H.attr(9134, 'translator', 9134)
    H.LTS[24]['attributes']['9134'] = {'min': 0, 'max': None}
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CR = [('Barry Guy', 'Double Bass [Uncredited], Producer', 3201), ('Johnny Dyani', 'Double Bass [Uncredited]', 3202),
          ('John Stevens (2)', 'Drums [Uncredited]', 3203), ('Paul Rutherford (2)', 'Trombone [Uncredited]', 3204),
          ('Frode Gjerstad', 'Soprano Saxophone, Tenor Saxophone', 3205), ('Sebastian Scotney', 'Liner Notes [Translation By (English)]', 3206),
          ('Pat Person', 'Little Instruments', 3207)]
    for n, _r, i in CR:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n.replace(' (2)', ''))
    NOTES = ('This was recorded by Norwegian State radio, at the Hennie-Onstad art centre outside Oslo on September 11th 1983. The first time '
             'I played with Rutherford and Guy. At the time I played soprano and tenor sax. On the second part I also played bass clarinet and tenor sax.')

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CR]
        d['notes'] = NOTES
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    ENT = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const n = g.querySelector('[data-el=uncr]');
      return { uncr: n ? n.textContent.replace(/\\s+/g, ' ').trim() : '', btns: n ? [...n.querySelectorAll('button')].map(b => b.textContent.trim()) : [],
        rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
          const pr = tr.querySelector('[data-f=primary]'); return [t ? (t.options[t.selectedIndex] || {}).text : '', lv ? lv.dataset.level : '', pr ? pr.value : '']; }) }; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            jd, bg = pg.evaluate(ENT, 'Johnny Dyani'), pg.evaluate(ENT, 'Barry Guy')
            print('A)', jd, bg)
            results.append(bool(jd) and jd['uncr'].startswith('Not named on the release (Discogs: uncredited) – on Skip:') and 'Take anyway' in jd['btns']
                           and 'Take all uncredited' in jd['btns'] and all(r[1] in ('', 'skip') for r in jd['rows'])
                           and bool(bg) and 'Take “double bass” anyway' in bg['btns'] and 'Take anyway' not in bg['btns']
                           and any(r[0] == 'producer' and r[1] == 'recording' for r in bg['rows']) and any(r[1] == 'skip' for r in bg['rows']))
            pg.click(f"{sec_sel(pg, 'Johnny Dyani')} [data-act=uncr-take]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            jd2, bg2 = pg.evaluate(ENT, 'Johnny Dyani'), pg.evaluate(ENT, 'Barry Guy')
            # (review) a level clicked by hand takes it too: Paul Rutherford's box gone
            pg.click(f"{sec_sel(pg, 'Paul Rutherford')} tr.dci-row [data-act=level][data-level=recording]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pr = pg.evaluate(ENT, 'Paul Rutherford')
            pg.click(f"{sec_sel(pg, 'Barry Guy')} [data-act=uncr-all]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            after = [pg.evaluate(ENT, n) for n in ('Barry Guy', 'John Stevens', 'Paul Rutherford')]
            print('B)', jd2, bg2, pr, after)
            results.append(bool(jd2) and jd2['uncr'] == '' and jd2['rows'][0][1] == 'recording' and bool(bg2) and bg2['uncr'] != ''
                           and bool(pr) and pr['uncr'] == '' and pr['rows'][0][1] == 'recording'
                           and all(e and e['uncr'] == '' and all(r[1] == 'recording' for r in e['rows']) for e in after))
            pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
            fmt = lambda d: '/'.join('-'.join(str(x) for x in (e['year'], e['month'], e['day']) if x) for e in (d['begin'], d['end']))
            names = sorted((d['name'], fmt(d)) for d in pool)
            print('C)', names)
            results.append(any(n.startswith('Performance') and f == '1983-9-11/1983-9-11' for n, f in names))
            asks = pg.evaluate("""[...document.querySelectorAll('[data-el=plays] [data-plays]:not(select):not(button)')].map(o => { const s = o.querySelector('select');
              return [o.previousElementSibling ? o.previousElementSibling.textContent.trim() : '', s ? (s.selectedOptions[0] || {}).text : '']; })""")
            print('D)', asks)
            pg.click('[data-el=plays] [data-act=plays-take]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            fg = pg.evaluate(ENT, 'Frode Gjerstad')
            gone = pg.evaluate("!document.querySelector('[data-el=plays]')")
            print('   ', fg, gone)
            results.append(len(asks) == 1 and 'bass clarinet' in asks[0][0] and 'soprano' not in asks[0][0].split('–')[-1] and asks[0][1] == 'Frode Gjerstad'
                           and bool(fg) and any(r[2] == 'bass clarinet' for r in fg['rows']) and gone)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate("""MB.relationshipEditor.state.added.map((r) => [r.linkTypeID, ((r.entity0 || {}).name || ''), ((r.attributes && r.attributes.__tree) || []).map((x) => x.typeName + (x.credited_as ? ' [' + x.credited_as + ']' : ''))])""")
            print('E)', [x for x in added if x[1] in ('Sebastian Scotney', 'Pat Person')])
            results.append(any(x[0] == 24 and x[1] == 'Sebastian Scotney' and 'translator' in x[2] for x in added)
                           and any(x[0] == 148 and x[1] == 'Pat Person' and any(a.lower() == 'other instruments [little instruments]' for a in x[2]) for x in added))
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        for k, v in linked0.items():
            H.LINKED[k] = v
        for _n, _r, i in CR:
            H.ARTISTS.pop(i, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_insts3103():
    """Credits Importer 3.103.0 (collected item Z-INSTS, rules S169, S170): Discogs names Jane Roe with five instruments without tracks
    (soprano and tenor saxophone, flute, bass clarinet, little instruments), Sax Two with soprano saxophone and flute, both as guest.
    A) Jane Roe: "💡 5 instruments without tracks …" with "Put them on the release"; Sax Two (two): no suggestion, the switch
       "Instruments: per track | on the release" ("per track" pressed).
    B) "Put them on the release": Jane Roe's five rows on the release (no release-level date in the matrix: the date they had); one automatic
       row on the recordings – instrument without an instrument (a little instrument has no group with the others: "instruments"),
       all 4 tracks, its note; the suggestion gone, "on the release" pressed.
    C) Sax Two "on the release": the automatic row "woodwind" (their group in MusicBrainz's tree; not named by Discogs: said), with
       "guest" (both have it).
    D) Back and forth three times (Jane Roe; "solo" ticked on the automatic row before): always the same rows – per track no automatic
       row, on the release one (with "solo" kept).
    E) Staged (on the release): Jane Roe instrument–release 5 times, instrument–recording 4 times without an instrument ("solo");
       Sax Two's recordings "woodwind" with guest.
    F) The quick switch S170 off: Jane Roe's … and Sax Two's automatic row "instruments" (no instrument)."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    # ([Z-ITREE] 3.107.0) flat as on MusicBrainz – the kinds in the instruments' tree of the workflow
    H.attr(9140, 'woodwind', 14, 14)
    for i, n in ((9124, 'other instruments'), (9131, 'soprano saxophone'), (9132, 'tenor saxophone'), (9133, 'bass clarinet'), (9142, 'flute')):
        H.attr(i, n, 14, 14)
    H.ITREE_EDGES[:] = [(9140, 9106), (9106, 9131), (9106, 9132), (9140, 9133), (9140, 9142)]
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CR = [('Jane Roe', 'Soprano Saxophone, Tenor Saxophone, Flute, Bass Clarinet, Little Instruments', 3301),
          ('Sax Two', 'Soprano Saxophone [Guest], Flute [Guest]', 3302)]
    for n, _r, i in CR:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n)

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CR]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    ENT = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const bar = g.querySelector('[data-el=insts]');
      return { sugg: !!(bar && bar.querySelector('.dci-insts-sugg')), seg: [...g.querySelectorAll('[data-act=insts-set][aria-pressed=true]')].map(b => b.dataset.insts),
        notes: [...g.querySelectorAll('.dci-insts-note')].map(n => n.textContent.trim()),
        rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
          const pr = tr.querySelector('[data-f=primary]'); return [t ? (t.options[t.selectedIndex] || {}).text : '', lv ? lv.dataset.level : '', pr ? pr.value : '',
          (tr.querySelector('[data-tcount]') || { textContent: '' }).textContent.trim(), [...tr.querySelectorAll('[data-f=flag]:checked, [data-f=flags]:checked')].map(c => c.value)]; }) }; }"""
    ADDED = """MB.relationshipEditor.state.added.map((r) => [r.linkTypeID, ((r.entity0 || {}).name || ''), (r.entity1 || {}).entityType || '',
      ((r.attributes && r.attributes.__tree) || []).map((x) => x.typeName).sort().join(','), r.begin_date ? [r.begin_date.year, r.begin_date.month, r.begin_date.day].join('-') : ''])"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            jr, st = pg.evaluate(ENT, 'Jane Roe'), pg.evaluate(ENT, 'Sax Two')
            print('A)', jr, st)
            results.append(bool(jr) and jr['sugg'] and jr['seg'] == ['track'] and len(jr['rows']) == 5 and bool(st) and not st['sugg'] and st['seg'] == ['track'])
            pg.click(f"{sec_sel(pg, 'Jane Roe')} .dci-insts-sugg [data-act=insts-set][data-insts=release]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            jr2 = pg.evaluate(ENT, 'Jane Roe')
            print('B)', jr2)
            rel5 = [r for r in jr2['rows'] if r[1] == 'release']
            auto = [r for r in jr2['rows'] if r[1] == 'recording']
            results.append(not jr2['sugg'] and jr2['seg'] == ['release'] and len(rel5) == 5 and all(r[0] == 'instrument' for r in rel5)
                           and len(auto) == 1 and auto[0][0] == 'instrument' and auto[0][2] == '' and auto[0][3] == '4 of 4 tracks' and len(jr2['notes']) == 1)
            pg.click(f"{sec_sel(pg, 'Sax Two')} [data-act=insts-set][data-insts=release]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            st2 = pg.evaluate(ENT, 'Sax Two')
            print('C)', st2)
            a2 = [r for r in st2['rows'] if r[1] == 'recording']
            results.append(len(a2) == 1 and a2[0][2] == 'woodwind' and 'guest' in a2[0][4] and any('“woodwind”' in n for n in st2['notes']))
            # D) "solo" ticked on Jane Roe's automatic row, then back and forth three times
            jsec = sec_sel(pg, 'Jane Roe')
            states = []
            auto_row = pg.evaluate(f"""(() => {{ const tr = [...document.querySelectorAll('{jsec} tr.dci-row')].find(t => t.querySelector('[data-act=level][data-level=recording][aria-pressed=true]'));
              const c = tr && tr.querySelector('[data-f=flag][value=solo], [data-f=flags][value=solo]'); if (c) c.click(); return !!c; }})()""")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            for k in range(3):
                pg.click(f"{jsec} [data-act=insts-set][data-insts=track]")
                H.wait_still(pg, "document.body.innerHTML", 10, 150)
                t1 = pg.evaluate(ENT, 'Jane Roe')
                pg.click(f"{jsec} [data-act=insts-set][data-insts=release]")
                H.wait_still(pg, "document.body.innerHTML", 10, 150)
                t2 = pg.evaluate(ENT, 'Jane Roe')
                states.append((len(t1['rows']), sorted(set(r[1] for r in t1['rows'])), len(t2['rows']), [r[4] for r in t2['rows'] if r[1] == 'recording']))
            print('D)', auto_row, states)
            results.append(auto_row and all(x == (5, ['recording'], 6, [['solo']]) for x in states))
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate(ADDED)
            mine = [x for x in added if x[1] in ('Jane Roe', 'Sax Two')]
            print('E)', mine)
            jrel = [x for x in mine if x[1] == 'Jane Roe' and x[0] == 44]
            jrec = [x for x in mine if x[1] == 'Jane Roe' and x[0] == 148]
            srec = [x for x in mine if x[1] == 'Sax Two' and x[0] == 148]
            results.append(len(jrel) == 5 and len(jrec) == 4 and all(x[3] == 'solo' for x in jrec) and len(srec) == 4 and all(x[3] == 'guest,woodwind' for x in srec))
            print('Fehler:', errs)
            results.append(not errs)
            # F) the quick switch S170 off: "instruments" for Sax Two
            ctx2 = H.new_context(b)
            pg2, errs2 = H.open_mb_edit(ctx2, companion=False)
            pg2.on('dialog', lambda d: d.accept())
            pg2.evaluate("localStorage.setItem('dci-rules-off', JSON.stringify(['S170']))")
            pg2.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg2)
            H.wait_for(pg2, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg2, "document.body.innerHTML", 10, 300)
            pg2.click(f"{sec_sel(pg2, 'Sax Two')} [data-act=insts-set][data-insts=release]")
            H.wait_still(pg2, "document.body.innerHTML", 10, 200)
            f = pg2.evaluate(ENT, 'Sax Two')
            print('F)', f)
            results.append(bool(f) and [r[2] for r in f['rows'] if r[1] == 'recording'] == [''] and not errs2)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.ITREE_EDGES.clear()
        for k, v in linked0.items():
            H.LINKED[k] = v
        for _n, _r, i in CR:
            H.ARTISTS.pop(i, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_evcol3103():
    """Credits Importer 3.103.0 (collected items Z-EVCOL, Z-ATTR3, Z-ARHL; rule D032) in the matrix: Discogs names Pia Note with "Piano" and
    "Liner Notes"; the notes "Tracks 1 and 2 recorded March 1, 2001. Tracks 3 and 4 recorded March 3, 2001."
    A) Her events: ① the recordings, ② the release without a date (liner notes).
    B) Piano unticked in ①: the column stays – grey, "✕" in its head; ticked again: an event as before (no grey column).
    C) Unticked again and ✕: the column is gone.
    D) The attributes together: at most three side by side (a grid of three columns).
    E) "＋ Another role" → instrument: its line framed yellow until an instrument is there, then not ([Z-ARHL2] 3.105.0: every cell of it
       yellow, the role's cell too).
    F) (D032) in the full view, the date matrix applied (piano: a row for tracks 1–2 on March 1, one for 3–4 on March 3), the piano of
       tracks 3–4 put on the release: March 3 kept – not without a date beside the liner notes (until 3.102.0 it joined them)."""
    import copy
    orig = H.discogs_release
    lts0 = copy.deepcopy(H.LTS)
    linked0 = copy.deepcopy(H.LINKED.get('link_type'))
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.ARTISTS[3311] = (H.uid('dddddddd', 3311), 'Pia Note')

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Pia Note', 'anv': '', 'role': 'Piano, Liner Notes', 'tracks': '', 'id': 3311, 'join': ''}]
        d['companies'] = []
        d['notes'] = 'Tracks 1 and 2 recorded March 1, 2001. Tracks 3 and 4 recorded March 3, 2001.'
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    HEADS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [...g.querySelectorAll('thead th[data-evhead]')].map(th => [th.classList.contains('dci-em-evghost'), th.textContent.replace(/\\s+/g, ' ').trim()]) : null; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'matrix'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            sec = sec_sel(pg, 'Pia Note')
            if not pg.locator(f'{sec} table.dci-em-one').count():
                pg.click(f'{sec} [data-act=em-wide]')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
            h0 = pg.evaluate(HEADS, 'Pia Note')
            print('A)', h0)
            results.append(bool(h0) and len(h0) == 2 and not any(x[0] for x in h0) and 'no date' in h0[1][1].lower())
            piano = f"{sec} tr.dci-em-line:has(input[data-f=em-primary]) input[data-f=em-tick]"
            ev1 = pg.evaluate(f"document.querySelector('{sec} thead th[data-evhead]').dataset.evhead")
            pg.locator(f'{piano}[data-ev="{ev1}"]').uncheck()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            h1 = pg.evaluate(HEADS, 'Pia Note')
            pg.locator(f'{piano}[data-ev="{ev1}"]').check()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            h2 = pg.evaluate(HEADS, 'Pia Note')
            print('B)', h1, h2)
            results.append(bool(h1) and len(h1) == 2 and h1[0][0] and not h1[1][0] and pg.locator(f'{sec} th.dci-em-evghost').count() == 0 and h2 == h0)
            pg.locator(f'{piano}[data-ev="{ev1}"]').uncheck()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pg.click(f'{sec} th.dci-em-evghost [data-act=em-ghost-drop]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            h3 = pg.evaluate(HEADS, 'Pia Note')
            print('C)', h3)
            results.append(bool(h3) and len(h3) == 1 and not any(x[0] for x in h3))
            grid = pg.evaluate(f"(() => {{ const g = document.querySelector('{sec} .dci-em-flaggrid'); return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : 0; }})()")
            print('D)', grid)
            results.append(grid == 3)
            pg.evaluate(f"document.querySelector('{sec} [data-act=add-role]').click()")
            H.wait_for(pg, "!!document.querySelector('[data-el=arq]')", 10)
            pg.locator('[data-el=arq] [data-arqlv=recording] [data-act=arq-pick][data-type=instrument]').first.click()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            e1 = pg.locator(f'{sec} tr.dci-arhl').count()
            # ([Z-ARHL2] 3.105.0) every cell yellow – the role's cell (it stays in place, white of its own) too
            bg = pg.evaluate(f"[...document.querySelectorAll('{sec} tr.dci-em-line.dci-arhl > td')].map(td => getComputedStyle(td).backgroundColor)")
            inp = pg.locator(f'{sec} tr.dci-arhl input[data-f=primary], {sec} tr.dci-arhl input[data-f=em-primary]').first
            inp.fill('guitar')
            inp.press('Tab')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            e2 = pg.locator(f'{sec} tr.dci-arhl').count()
            print('E)', e1, e2, bg)
            results.append(e1 >= 1 and e2 == 0 and bool(bg) and all(c == 'rgb(255, 251, 230)' for c in bg))
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
        # F) the full view: the piano of the second date put on the release keeps its date
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            sec = sec_sel(pg, 'Pia Note')
            pg.click('[data-act=dm-apply]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pg.locator(f'{sec} tr.dci-row:has([data-f=primary]) [data-act=level][data-level=release]').last.click()
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate("""MB.relationshipEditor.state.added.filter((r) => (r.entity0 || {}).name === 'Pia Note' && (r.entity1 || {}).entityType === 'release')
              .map((r) => [r.linkTypeID, r.begin_date ? [r.begin_date.year, r.begin_date.month, r.begin_date.day].join('-') : ''])""")
            print('F)', added)
            results.append(sorted(added) == [[24, ''], [44, '2001-3-3']] and not errs)
            b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.LINKED['link_type'] = linked0
        H.ARTISTS.pop(3311, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_instsrem3103():
    """Credits Importer 3.103.0 (Z-INSTS, review): "on the release" remembered – Jane Roe's five instruments put on the release, the page
    loaded again: on the release again (five rows there, one automatic row on the recordings, "on the release" pressed); "per track":
    the five on the recordings again, no automatic row."""
    import copy
    orig = H.discogs_release
    lts0, attrs0, rem0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS), H.REMEMBER
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    for i, n in ((9124, 'other instruments'), (9131, 'soprano saxophone'), (9132, 'tenor saxophone'), (9133, 'bass clarinet'), (9142, 'flute')):
        H.attr(i, n, 14, 14)
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS[3301] = (H.uid('dddddddd', 3301), 'Jane Roe')
    H.REMEMBER = True

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Jane Roe', 'anv': '', 'role': 'Soprano Saxophone, Tenor Saxophone, Flute, Bass Clarinet, Little Instruments', 'tracks': '', 'id': 3301, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    LV = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [[...g.querySelectorAll('[data-act=insts-set][aria-pressed=true]')].map(b => b.dataset.insts),
        [...g.querySelectorAll('tr.dci-row')].map(tr => { const lv = tr.querySelector('[data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : ''; })] : null; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())

            def load():
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                pg.wait_for_timeout(1500)
            load()
            pg.click(f"{sec_sel(pg, 'Jane Roe')} [data-act=insts-set][data-insts=release]")
            pg.wait_for_timeout(1600)
            before = pg.evaluate(LV, 'Jane Roe')
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            load()
            after = pg.evaluate(LV, 'Jane Roe')
            pg.click(f"{sec_sel(pg, 'Jane Roe')} [data-act=insts-set][data-insts=track]")
            pg.wait_for_timeout(400)
            back = pg.evaluate(LV, 'Jane Roe')
            print('vorher:', before, '| nachher:', after, '| je Track:', back)
            want = [['release'], ['release'] * 5 + ['recording']]
            results.append(before == want and after == want and back == [['track'], ['recording'] * 5])
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.REMEMBER = rem0
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        for k, v in linked0.items():
            H.LINKED[k] = v
        H.ARTISTS.pop(3301, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bzk3105():
    """Credits Importer 3.105.0 (collected item Z-BZK, question Q014): Discogs's plain "Bouzouki" – which bouzouki? The bouzouki itself
    and every kind of it in MusicBrainz's instrument tree (here irish bouzouki and tzouras), in the full list and in the matrix line;
    irish bouzouki chosen: the instrument irish bouzouki, credited "bouzouki"."""
    import copy
    orig = H.discogs_release
    attrs0 = copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy(H.LINKED.get('link_attribute_type'))
    H.attr(9150, 'bouzouki', 14, 14)
    H.attr(9151, 'irish bouzouki', 14, 14)
    H.attr(9152, 'tzouras', 14, 14)
    H.ITREE_EDGES[:] = [(9150, 9151), (9150, 9152)]  # ([Z-ITREE] 3.107.0) flat as on MusicBrainz, the kinds in the tree
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS[3321] = (H.uid('dddddddd', 3321), 'Bo Zou')

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Bo Zou', 'anv': '', 'role': 'Bouzouki', 'tracks': '', 'id': 3321, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    results = []
    try:
        for view in ('legacy', 'matrix'):
            with sync_playwright() as p:
                H.ENTRIES_VIEW = view
                b = p.chromium.launch(args=H.LAUNCH_ARGS)
                ctx = H.new_context(b)
                pg, errs = H.open_mb_edit(ctx, companion=False)
                pg.on('dialog', lambda d: d.accept())
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                H.wait_still(pg, "document.body.innerHTML", 10, 300)
                sec = sec_sel(pg, 'Bo Zou')
                opts = pg.evaluate(f"[...document.querySelectorAll('{sec} [data-question=Q014] [data-act=instr-pick], {sec} [data-cl-ask=instr] [data-value], {sec} .dci-em-chipask [data-instr]')].map(b => b.dataset.instr || b.dataset.value || b.textContent.trim())")
                print(view, 'A)', opts)
                ok = opts[:3] == ['bouzouki', 'irish bouzouki', 'tzouras']
                if view == 'legacy':
                    pg.click(f"{sec} [data-question=Q014] [data-act=instr-pick][data-instr='irish bouzouki']")
                    H.wait_still(pg, "document.body.innerHTML", 10, 200)
                    got = pg.evaluate(f"[document.querySelector('{sec} [data-f=primary]').value, (document.querySelector('{sec} [data-f=credit], {sec} [data-f=role-credit]') || {{}}).value || '']")
                    print('   B)', got)
                    ok = ok and got[0] == 'irish bouzouki'
                results.append(ok and not errs)
                b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.ITREE_EDGES.clear()
        H.LINKED['link_attribute_type'] = linked0
        H.ARTISTS.pop(3321, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dsup3106():
    """Credits Importer 3.106.0 (collected item Z-DSUP; rules S172, S173, S174): the import against what MusicBrainz has.
    MusicBrainz: Drum Guy drums on track 1 (as always in these tests) and piano on track 2; Sax Man saxophone on all four recordings; Sax Two saxophone on
    them; Fine Man tenor saxophone on them; Bass Man double bass on track 1 without a date. Discogs: Drum Guy Drums and Electric Guitar, Sax Man
    Tenor Saxophone, Sax Two Tenor Saxophone and Alto Saxophone, Fine Man Saxophone, Bass Man Double Bass (all tracks); the notes
    "Recorded March 1–3, 2001".
    A) Drum Guy: "Compared with MusicBrainz – Only on MusicBrainz: piano (1×)", electric guitar held on Skip ("Add anyway"), drums not
       (MusicBrainz has them). Fine Man: saxophone held (MusicBrainz more precise). Sax Man: "tenor saxophone instead of
       saxophone" – "Update". Sax Two: tenor and alto saxophone on the release (MusicBrainz keeps saxophone on the recordings).
    A2) (review) Drum Guy's drums typed into ("gui"): not held (a row changed by hand).
    B) The date matrix applied: Bass Man "Date of double bass: MusicBrainz has none – add 2001-03" – ([Z-DSUP3] 3.107.0) taken already.
    C) "Update", "Take", "Add anyway" and staged (the editor with MusicBrainz's relationships of Sax Man and Bass Man): Sax Man's four
       relationships of MusicBrainz now tenor saxophone (edited, not added),
       Bass Man's on track 1 with 2001-03, Drum Guy's electric guitar added; Fine Man nothing.
    D) The matrix: compact, the line "only on MusicBrainz" with piano; full, a yellow line of its own."""
    import copy
    orig = H.discogs_release
    lts0, attrs0, extra0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS), copy.deepcopy(H.MB_EXTRA)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    H.attr(9132, 'tenor saxophone', 14, 14)
    H.ITREE_EDGES[:] = [(9106, 9107), (9106, 9132)]  # ([Z-ITREE] 3.107.0) flat as on MusicBrainz, the kinds in the tree
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    PEOPLE = [('Sax Man', 3331, 'Tenor Saxophone'), ('Sax Two', 3332, 'Tenor Saxophone, Alto Saxophone'), ('Fine Man', 3333, 'Saxophone'), ('Bass Man', 3334, 'Double Bass')]
    for n, i, _r in PEOPLE:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n)
    rel_ = lambda i, name, attrs: {'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'], 'attributes': attrs, 'attribute-values': {},
                                   'artist': {'id': H.ARTISTS[i][0], 'name': name}, 'begin': '', 'end': ''}
    for k, rec in enumerate(H.REC):
        H.MB_EXTRA[rec] = H.MB_EXTRA.get(rec, []) + [rel_(3331, 'Sax Man', ['saxophone']), rel_(3332, 'Sax Two', ['saxophone']), rel_(3333, 'Fine Man', ['tenor saxophone'])] \
            + ([rel_(3334, 'Bass Man', ['double bass'])] if k == 0 else []) + ([{**rel_(3004, 'Drum Guy', ['piano']), 'artist': {'id': H.ARTISTS[3004][0], 'name': 'Drum Guy'}}] if k == 1 else [])

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Drum Guy', 'anv': '', 'role': 'Drums, Electric Guitar', 'tracks': '', 'id': 3004, 'join': ''}] \
            + [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, i, r in PEOPLE]
        d['companies'] = []
        d['notes'] = 'Recorded March 1–3, 2001.'
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    BOX = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const b = g.querySelector('[data-el=dsup]');
      return { lines: b ? [...b.querySelectorAll('.dci-dsup-l')].map(l => [l.dataset.dsup, l.textContent.replace(/\\s+/g, ' ').trim()]) : [],
        rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const lv = tr.querySelector('[data-act=level][aria-pressed=true]'); const pr = tr.querySelector('[data-f=primary]');
          return [pr ? pr.value : '', lv ? lv.dataset.level : '', tr.classList.contains('dci-dsup-mark')]; }) }; }"""
    STATES = """(gids) => { const out = []; const seen = new WeakSet(); let steps = 0;
      const names = (t) => { const o = []; const walk = (n) => { if (!n || typeof n !== 'object') return; if (n.value && n.value.type) o.push(n.value.typeName || n.value.type.name || ''); walk(n.left); walk(n.right); }; walk(t); return o.sort(); };
      const visit = (v, d) => { if (!v || typeof v !== 'object' || seen.has(v) || d > 40 || steps++ > 400000) return; seen.add(v);
        if (v.linkTypeID && v.entity0 && v.entity1 && gids.includes(v.entity0.gid)) out.push([v.entity0.name, v.entity1.gid, names(v.attributes), v.begin_date ? [v.begin_date.year, v.begin_date.month].join('-') : '', v._status]);
        if (v instanceof Map) { v.forEach((x) => visit(x, d + 1)); return; } Object.keys(v).forEach((k) => visit(v[k], d + 1)); };
      visit(MB.relationshipEditor.state, 0); return out; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            dg, sm, s2, fm = [pg.evaluate(BOX, n) for n in ('Drum Guy', 'Sax Man', 'Sax Two', 'Fine Man')]
            print('A)', dg, '\n  ', sm, '\n  ', s2, '\n  ', fm)
            results.append(bool(dg) and ['mbonly', 'Only on MusicBrainz: piano (1×)'] in dg['lines'] and any(l[0] == 'conflict' for l in dg['lines'])
                           and any(r[1] == 'skip' and r[2] for r in dg['rows'])
                           and bool(sm) and any(l[0] == 'update' and 'instead of “saxophone”' in l[1] for l in sm['lines'])
                           and bool(s2) and sorted(r[0] for r in s2['rows'] if r[1] == 'release') == ['alto saxophone', 'tenor saxophone'] and sum(l[0] == 'release' for l in s2['lines']) == 2
                           and bool(fm) and any(l[0] == 'covered' for l in fm['lines']) and all(r[1] == 'skip' for r in fm['rows']))
            # (review) a role typed into is not held: Drum Guy's drums changed by hand stay on their level
            dsec0 = sec_sel(pg, 'Drum Guy')
            inp = pg.locator(f"{dsec0} tr.dci-row [data-f=primary]").first
            inp.fill('gui')
            pg.wait_for_timeout(900)
            typed = pg.evaluate(BOX, 'Drum Guy')
            inp.fill('drums (drum set)')
            inp.press('Tab')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            print('A2)', typed)
            results.append(any(r[0] == 'gui' and r[1] == 'recording' for r in typed['rows']))
            pg.click('[data-act=dm-apply]')
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            bm = pg.evaluate(BOX, 'Bass Man')
            print('B)', bm)
            results.append(bool(bm) and any(l[0] == 'date-add' and 'add 2001-03' in l[1] for l in bm['lines']))
            # the relationships of MusicBrainz as the relationship editor has them (the test's editor: "existingRels")
            import json as _j
            at = lambda i: {'type': {'gid': H.ATTRS[i]['gid'], 'id': i, 'name': H.ATTRS[i]['name']}, 'typeID': i, 'typeName': H.ATTRS[i]['name']}
            ex = [{'id': 9100 + k, 'linkTypeID': 148, 'entity0': {'gid': H.ARTISTS[3331][0], 'entityType': 'artist', 'id': 3331, 'name': 'Sax Man'},
                   'entity1': {'gid': rec, 'entityType': 'recording', 'id': 5001 + k, 'name': 'x'}, 'begin_date': None, 'end_date': None, 'ended': False,
                   'attributes': {'__tree': [at(9106)]}, 'entity0_credit': '', 'entity1_credit': '', '_status': 0} for k, rec in enumerate(H.REC)]
            ex.append({'id': 9200, 'linkTypeID': 148, 'entity0': {'gid': H.ARTISTS[3334][0], 'entityType': 'artist', 'id': 3334, 'name': 'Bass Man'},
                       'entity1': {'gid': H.REC[0], 'entityType': 'recording', 'id': 5001, 'name': 'x'}, 'begin_date': None, 'end_date': None, 'ended': False,
                       'attributes': {'__tree': [at(9102)]}, 'entity0_credit': '', 'entity1_credit': '', '_status': 0})
            pg.evaluate(f"(() => {{ const re = MB.relationshipEditor; re.state = {{ ...re.state, existingRels: {_j.dumps(ex)} }}; }})()")
            pg.click(f"{sec_sel(pg, 'Sax Man')} [data-el=dsup] [data-act=dsup-take]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            # ([Z-DSUP3] 3.107.0) a date MusicBrainz does not have is taken without a click
            taken = pg.locator(f"{sec_sel(pg, 'Bass Man')} [data-el=dsup] [data-act=dsup-date]").first.get_attribute('aria-pressed')
            print('B2)', taken)
            results.append(taken == 'true')
            pg.click(f"{sec_sel(pg, 'Drum Guy')} [data-el=dsup] [data-act=dsup-take]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(2000)
            added = pg.evaluate("""MB.relationshipEditor.state.added.map((r) => [((r.entity0 || {}).name || ''), r._status, ((r.attributes && r.attributes.__tree) || []).map((x) => x.typeName || x.type.name).sort().join(','),
              r.begin_date ? [r.begin_date.year, r.begin_date.month].join('-') : ''])""")
            print('C)', added)
            sax = [x for x in added if x[0] == 'Sax Man']
            bass = [x for x in added if x[0] == 'Bass Man' and x[1] == 2]
            results.append(len(sax) == 4 and all(x[1] == 2 and x[2] == 'tenor saxophone' for x in sax) and len(bass) == 1 and bass[0][3] == '2001-3' and bass[0][2] == 'double bass'
                           and not any(x[0] == 'Fine Man' for x in added) and sum(x[0] == 'Drum Guy' and x[2] == 'electric guitar' and x[1] == 1 for x in added) == 4)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'matrix'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            dsec = sec_sel(pg, 'Drum Guy')
            wide = pg.evaluate(f"[...document.querySelectorAll('{dsec} tr.dci-em-mbonly')].map(t => t.textContent.replace(/\\s+/g, ' ').trim())")
            pg.click('.dci-head [data-act=view-toggle]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            line = pg.evaluate(f"(() => {{ const l = document.querySelector('{dsec} [data-el=mbonly]'); return l ? l.textContent.replace(/\\s+/g, ' ').trim() : ''; }})()")
            print('D)', line, wide)
            results.append(line == 'only on MusicBrainz piano (1×)' and wide == ['only on MusicBrainz piano (1×)'] and not errs)
            b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.ITREE_EDGES.clear()
        H.MB_EXTRA.clear()
        H.MB_EXTRA.update(extra0)
        for k, v in linked0.items():
            H.LINKED[k] = v
        for _n, i, _r in PEOPLE:
            H.ARTISTS.pop(i, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_itree3107():
    """Credits Importer 3.107.0 (Z-ITREE): MusicBrainz's relationship editor has its instruments flat (all right below "instrument") –
    which is a kind of which is in the instruments' tree (the workflow's file on the data branch, else MusicBrainz's "type of").
    Reed Man: Soprano Saxophone, Tenor Saxophone (Discogs), "on the release".
    A) No file of the workflow (404): MusicBrainz asked for the instruments (/ws/2/instrument/…?inc=instrument-rels) – the automatic row
       "saxophone" (both "type of" saxophone); kept in this browser.
    B) With the file (soprano and tenor saxophone below saxophone): "saxophone" without asking MusicBrainz; the file kept in this browser.
    C) The kinds of bouzouki asked from the tree as well (irish bouzouki, tzouras – flat attributes).
    (review) In A and B: Up Man's "Tenor Saxophone" against MusicBrainz's saxophone – an update, no conflict (not judged before the tree is there)."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    for i, n in ((9131, 'soprano saxophone'), (9132, 'tenor saxophone'), (9150, 'bouzouki'), (9151, 'irish bouzouki'), (9152, 'tzouras')):
        H.attr(i, n, 14, 14)
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    g = lambda i: H.ATTRS[i]['gid']
    H.ARTISTS[3341] = (H.uid('dddddddd', 3341), 'Reed Man')
    H.ARTISTS[3342] = (H.uid('dddddddd', 3342), 'Bo Zou')
    H.ARTISTS[3343] = (H.uid('dddddddd', 3343), 'Up Man')
    extra0 = copy.deepcopy(H.MB_EXTRA)
    # ((review) MusicBrainz has Up Man's saxophone on the recordings: "tenor saxophone" an update – also while the tree comes from MusicBrainz
    for rec in H.REC:
        H.MB_EXTRA[rec] = H.MB_EXTRA.get(rec, []) + [{'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'], 'attributes': ['saxophone'],
                                                       'attribute-values': {}, 'artist': {'id': H.ARTISTS[3343][0], 'name': 'Up Man'}, 'begin': '', 'end': ''}]

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Reed Man', 'anv': '', 'role': 'Soprano Saxophone, Tenor Saxophone', 'tracks': '', 'id': 3341, 'join': ''},
                             {'name': 'Bo Zou', 'anv': '', 'role': 'Bouzouki', 'tracks': '', 'id': 3342, 'join': ''},
                             {'name': 'Up Man', 'anv': '', 'role': 'Tenor Saxophone', 'tracks': '', 'id': 3343, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    AUTO = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; return [...g.querySelectorAll('tr.dci-row')].filter(tr => tr.querySelector('[data-act=level][data-level=recording][aria-pressed=true]'))
        .map(tr => (tr.querySelector('[data-f=primary]') || { value: '?' }).value); }"""
    OPTS = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Bo Zou');
      return g ? [...g.querySelectorAll('[data-question=Q014] [data-act=instr-pick]')].map(b => b.dataset.instr) : null; })()"""
    results = []

    def run(ctx, label):
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        pg.click(f"{sec_sel(pg, 'Reed Man')} [data-act=insts-set][data-insts=release]")
        H.wait_for(pg, f"(({AUTO})('Reed Man') || []).join() === 'saxophone' && ({OPTS} || []).length >= 3", 20)
        auto = pg.evaluate(AUTO, 'Reed Man')
        opts = pg.evaluate(OPTS)
        H.wait_for(pg, "!!document.querySelector('section.dci-group [data-el=dsup] [data-dsup=update]')", 20)
        upd = pg.evaluate("[...document.querySelectorAll('section.dci-group [data-el=dsup] .dci-dsup-l')].map(l => [l.dataset.dsup, l.textContent.replace(/\\s+/g, ' ').trim()])")
        pg.wait_for_timeout(2500)  # (MusicBrainz's answers written to the browser after they stop)
        kept = pg.evaluate("[localStorage.getItem('dci-itree') !== null, Object.keys(JSON.parse(localStorage.getItem('dci-itree-live') || '{}')).length]")
        print(label, auto, opts, kept, upd, H.INSTRUMENT_REQUESTS, errs)
        return auto, opts, kept, errs, upd

    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            # A) no file: MusicBrainz asked
            H.ITREE_OFF[0] = True
            H.INSTRUMENT_RELS.update({g(9131): [(g(9106), 'backward')], g(9132): [(g(9106), 'backward')], g(9106): [(g(9131), 'forward'), (g(9132), 'forward')],
                                      g(9150): [(g(9151), 'forward'), (g(9152), 'forward')]})
            H.INSTRUMENT_REQUESTS.clear()
            auto, opts, kept, errs, upd = run(H.new_context(b), 'A)')
            asked = set(H.INSTRUMENT_REQUESTS)
            upd_ok = lambda u: any(x[0] == 'update' and '“tenor saxophone” instead of “saxophone”' in x[1] for x in u) and not any(x[0] in ('conflict', 'mbonly') for x in u)
            results.append(auto == ['saxophone'] and {g(9131), g(9132)} <= asked and not kept[0] and kept[1] >= 2 and upd_ok(upd) and not errs)
            # B) the file of the workflow: nothing asked
            H.ITREE_OFF[0] = False
            H.ITREE_EDGES[:] = [(9106, 9131), (9106, 9132), (9150, 9151), (9150, 9152)]
            H.INSTRUMENT_REQUESTS.clear()
            auto2, opts2, kept2, errs2, upd2 = run(H.new_context(b), 'B)')
            results.append(auto2 == ['saxophone'] and not H.INSTRUMENT_REQUESTS and kept2[0] and upd_ok(upd2) and not errs2)
            # C) the kinds of bouzouki (both runs)
            print('C)', opts, opts2)
            results.append(all(o and {'bouzouki', 'irish bouzouki', 'tzouras'} <= set(o) for o in (opts, opts2)))
            b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
        H.ITREE_OFF[0] = False
        H.ITREE_EDGES.clear()
        H.INSTRUMENT_RELS.clear()
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        for k, v in linked0.items():
            H.LINKED[k] = v
        H.ARTISTS.pop(3341, None)
        H.ARTISTS.pop(3342, None)
        H.ARTISTS.pop(3343, None)
        H.MB_EXTRA.clear()
        H.MB_EXTRA.update(extra0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dsup3107():
    """Credits Importer 3.107.0 (collected items Z-DSUP3, Z-DSUP2, Z-DSUPWHY): the dates of the pools for relationships MusicBrainz has.
    MusicBrainz: Wood Man trombone on all four recordings without a date; Same Man double bass on them with 2001-03; Prod Man piano on
    track 1. Discogs: Wood Man Trombone, Same Man Double Bass, Prod Man Producer; the notes "Recorded March 1–3, 2001".
    A) After the import: Wood Man's and Same Man's rows on Skip (MusicBrainz has them); Prod Man without the box (his source names no
       instrument – no "only on MusicBrainz: piano").
    B) The date matrix applied: Wood Man's row back on the recordings, "add 2001-03" taken without a click; Same Man's stays on Skip
       (MusicBrainz has the date).
    C) Staged (the editor with Wood Man's four relationships): the four edited with 2001-03, none added.
    D) Developer mode, "show why an entry has no box": Prod Man's grey note names MusicBrainz's piano; Same Man's says his rows are all
       MusicBrainz's already (on Skip) – compared once the pools are applied. (review) B2: a click takes the date back, another again."""
    import copy
    import json as _j
    orig = H.discogs_release
    lts0, attrs0, extra0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS), copy.deepcopy(H.MB_EXTRA)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    H.attr(9160, 'trombone', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    PEOPLE = [('Wood Man', 3351, 'Trombone'), ('Same Man', 3352, 'Double Bass'), ('Prod Man', 3353, 'Producer')]
    for n, i, _r in PEOPLE:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n)
    rel_ = lambda i, name, attrs, begin='': {'target-type': 'artist', 'type': 'instrument', 'type-id': H.LTS[148]['gid'], 'attributes': attrs, 'attribute-values': {},
                                             'artist': {'id': H.ARTISTS[i][0], 'name': name}, 'begin': begin, 'end': begin}
    for k, rec in enumerate(H.REC):
        H.MB_EXTRA[rec] = H.MB_EXTRA.get(rec, []) + [rel_(3351, 'Wood Man', ['trombone']), rel_(3352, 'Same Man', ['double bass'], '2001-03')] \
            + ([rel_(3353, 'Prod Man', ['piano'])] if k == 0 else [])

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, i, r in PEOPLE]
        d['companies'] = []
        d['notes'] = 'Recorded March 1–3, 2001.'
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    BOX = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      if (!g) return null; const b = g.querySelector('.dci-dsup[data-el=dsup]'); const w = g.querySelector('.dci-dsupwhy');
      return { lines: b ? [...b.querySelectorAll('.dci-dsup-l')].map(l => [l.dataset.dsup, l.textContent.replace(/\\s+/g, ' ').trim(), (l.querySelector('[data-act=dsup-date]') || { getAttribute: () => '' }).getAttribute('aria-pressed')]) : [],
        why: w ? [w.dataset.why, w.textContent.trim()] : null,
        rows: [...g.querySelectorAll('tr.dci-row')].map(tr => { const lv = tr.querySelector('[data-act=level][aria-pressed=true]'); const pr = tr.querySelector('[data-f=primary]');
          return [pr ? pr.value : '', lv ? lv.dataset.level : '']; }) }; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            wm, sm, pm = [pg.evaluate(BOX, n) for n in ('Wood Man', 'Same Man', 'Prod Man')]
            print('A)', wm, '\n  ', sm, '\n  ', pm)
            results.append(bool(wm) and [r[1] for r in wm['rows']] == ['skip'] and bool(sm) and [r[1] for r in sm['rows']] == ['skip']
                           and bool(pm) and pm['lines'] == [])
            pg.click('[data-act=dm-apply]')
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            wm2, sm2 = pg.evaluate(BOX, 'Wood Man'), pg.evaluate(BOX, 'Same Man')
            print('B)', wm2, '\n  ', sm2)
            results.append([r[1] for r in wm2['rows']] == ['recording'] and any(l[0] == 'date-add' and 'add 2001-03' in l[1] and l[2] == 'true' for l in wm2['lines'])
                           and [r[1] for r in sm2['rows']] == ['skip'] and sm2['lines'] == [])
            # ((review) a click takes the date back, another takes it again
            btn = f"{sec_sel(pg, 'Wood Man')} [data-el=dsup] [data-act=dsup-date]"
            pg.click(btn)
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            back = pg.locator(btn).first.get_attribute('aria-pressed')
            pg.click(btn)
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            again = pg.locator(btn).first.get_attribute('aria-pressed')
            print('B2)', back, again)
            results.append(back == 'false' and again == 'true')
            at = lambda i: {'type': {'gid': H.ATTRS[i]['gid'], 'id': i, 'name': H.ATTRS[i]['name']}, 'typeID': i, 'typeName': H.ATTRS[i]['name']}
            ex = [{'id': 9300 + k, 'linkTypeID': 148, 'entity0': {'gid': H.ARTISTS[3351][0], 'entityType': 'artist', 'id': 3351, 'name': 'Wood Man'},
                   'entity1': {'gid': rec, 'entityType': 'recording', 'id': 5001 + k, 'name': 'x'}, 'begin_date': None, 'end_date': None, 'ended': False,
                   'attributes': {'__tree': [at(9160)]}, 'entity0_credit': '', 'entity1_credit': '', '_status': 0} for k, rec in enumerate(H.REC)]
            pg.evaluate(f"(() => {{ const re = MB.relationshipEditor; re.state = {{ ...re.state, existingRels: {_j.dumps(ex)} }}; }})()")
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(2000)
            added = pg.evaluate("""MB.relationshipEditor.state.added.map((r) => [((r.entity0 || {}).name || ''), r._status, ((r.attributes && r.attributes.__tree) || []).map((x) => x.typeName || x.type.name).sort().join(','),
              r.begin_date ? [r.begin_date.year, r.begin_date.month].join('-') : ''])""")
            mine = [x for x in added if x[0] in ('Wood Man', 'Same Man')]
            print('C)', mine)
            results.append(len(mine) == 4 and all(x[:4] == ['Wood Man', 2, 'trombone', '2001-3'] for x in mine))
            print('Fehler:', errs)
            results.append(not errs)
            # D) developer mode: why no box
            ctx2 = H.new_context(b)
            pg2, errs2 = H.open_mb_edit(ctx2, companion=False)
            pg2.on('dialog', lambda d: d.accept())
            pg2.evaluate("localStorage.setItem('dci-dev', 'true'); localStorage.setItem('dci-dsup-why', 'true')")
            pg2.reload()
            pg2.add_script_tag(content=H.MAIN)
            pg2.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg2)
            H.wait_for(pg2, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg2, "document.body.innerHTML", 10, 300)
            pm3, sm3 = pg2.evaluate(BOX, 'Prod Man'), pg2.evaluate(BOX, 'Same Man')
            print('D)', pm3['why'], sm3['why'])
            results.append(bool(pm3['why']) and pm3['why'][0] == 'noMatch' and 'instrument piano on 1 recordings' in pm3['why'][1]
                           and pm3['why'][1].startswith('MB x Vibecode: Credits Importer – compared with MusicBrainz (developer mode):')
                           and bool(sm3['why']) and sm3['why'][0] == 'allThere' and 'all its 1 rows' in sm3['why'][1] and not errs2)
            b.close()
    finally:
        H.ENTRIES_VIEW = 'legacy'
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.MB_EXTRA.clear()
        H.MB_EXTRA.update(extra0)
        for k, v in linked0.items():
            H.LINKED[k] = v
        for _n, i, _r in PEOPLE:
            H.ARTISTS.pop(i, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_lvlrg3108():
    """Credits Importer 3.108.0 (collected item Z-LVLRG): "Level for all rows: … Release group". All rows on the release first; then
    "Release group": the A&R row goes there (MusicBrainz has "artists and repertoire" on the release group), the others stay on the
    release – a message names their roles. B) (review) MusicBrainz without the release group: no row moved, a warning."""
    orig = H.discogs_release
    H.ARTISTS[3361] = (H.uid('dddddddd', 3361), 'Rep Guy')

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Rep Guy', 'anv': '', 'role': 'A&R', 'tracks': '', 'id': 3361, 'join': ''},
                             {'name': 'Drum Guy', 'anv': '', 'role': 'Drums', 'tracks': '', 'id': 3004, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    LV = """[...document.querySelectorAll('tr.dci-row')].map(tr => [(tr.closest('section.dci-group').querySelector('.dci-gname strong') || {}).textContent.trim(),
      (tr.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level || ''])"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            btns = pg.evaluate("[...document.querySelectorAll('[data-el=toolbar] [data-act=bulk-level]')].map(b => b.dataset.level)")
            pg.locator('[data-el=toolbar] [data-act=bulk-level][data-level=release]').evaluate('b => b.click()')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            l1 = pg.evaluate(LV)
            pg.locator('[data-el=toolbar] [data-act=bulk-level][data-level=release_group]').evaluate('b => b.click()')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            l2 = pg.evaluate(LV)
            msg = pg.evaluate("[...document.querySelectorAll('.dci-msg, [data-el=messages] li, .dci-messages li')].map(m => m.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Release group:/.test(t))")
            print('Knöpfe:', btns, '| Release:', l1, '| Release group:', l2, '|', msg, '| Fehler:', errs)
            # ([Z-SCOPE] 3.112.0) no "only works" any more: the works' filter does it
            results.append(btns == ['recording', 'release', 'release_group', 'skip'] and ['Rep Guy', 'release'] in l1 and ['Rep Guy', 'release_group'] in l2
                           and ['Drum Guy', 'release'] in l2 and len(msg) == 1 and 'drums' in msg[0].lower() and 'stays' in msg[0] and not errs)
            ctx.close()
            # B) (review) MusicBrainz without the release group of the release: no row moved, a warning
            orig_ws = H.ws_release

            def ws(full=False):
                d = orig_ws(full)
                d.pop('release-group', None)
                return d
            H.ws_release = ws
            try:
                ctx = H.new_context(b)
                pg, errs = H.open_mb_edit(ctx, companion=False)
                pg.on('dialog', lambda d: d.accept())
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                H.wait_still(pg, "document.body.innerHTML", 10, 300)
                before = pg.evaluate(LV)
                pg.locator('[data-el=toolbar] [data-act=bulk-level][data-level=release_group]').evaluate('b => b.click()')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
                after = pg.evaluate(LV)
                warn = pg.evaluate("[...document.querySelectorAll('.dci-msg, [data-el=messages] li, .dci-messages li')].map(m => m.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /did not give the release group/.test(t))")
                print('B) ohne Release group:', before == after, '|', warn, '| Fehler:', errs)
                results.append(before == after and len(warn) == 1 and not errs)
            finally:
                H.ws_release = orig_ws
            b.close()
    finally:
        H.discogs_release = orig
        H.ARTISTS.pop(3361, None)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_emtype3108():
    """Credits Importer 3.108.0 (collected items Z-EMTYPE, Z-UNCR2). A) In the matrix the role of a line is a choice of MusicBrainz's
    types of its level (until 3.107.0 plain text – the role could not be changed there): "Artwork" (no type in the harness) shows
    "Artwork → no type" first, the tooltip names the source's role; "design" chosen – the row has that type (the list view shows
    it, the matrix again).
    B) The note on uncredited roles is yellow (a rule of its own, not the grey note)."""
    orig = H.discogs_release
    H.ARTISTS[3361] = (H.uid('dddddddd', 3361), 'Art Guy')

    def rel():
        d = orig()
        d['extraartists'] = [{'name': 'Art Guy', 'anv': '', 'role': 'Artwork', 'tracks': '', 'id': 3361, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    SEL = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => (x.querySelector('.dci-gname strong') || {}).textContent.trim() === 'Art Guy');
      const r = g && g.querySelector('.dci-em-role'); if (!r) return null;
      return [r.tagName, r.tagName === 'SELECT' ? r.value : r.textContent.trim(), r.title, r.tagName === 'SELECT' ? [...r.options].map(o => o.value) : []]; })()"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'matrix'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            a0 = pg.evaluate(SEL)
            print('A) vorher:', a0 and a0[:3], '| Typen:', a0 and len(a0[3]))
            ok_a0 = bool(a0) and a0[0] == 'SELECT' and a0[1] == '' and a0[3][0] == '' and 'Artwork' in a0[2] and 'design' in a0[3]
            if ok_a0:
                pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => (x.querySelector('.dci-gname strong') || {}).textContent.trim() === 'Art Guy');
                  const r = g.querySelector('select.dci-em-typesel'); r.value = 'design'; r.dispatchEvent(new Event('change', { bubbles: true })); })()""")
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
            a1 = pg.evaluate(SEL)
            pg.click('.dci-head [data-act=view-toggle]'); pg.wait_for_timeout(600)
            lst = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => (x.querySelector('.dci-gname strong') || {}).textContent.trim() === 'Art Guy');
              if (!g) return null; const s = g.querySelector('[data-f=type]'); return s ? s.selectedOptions[0].textContent.trim() : g.textContent.replace(/\\s+/g, ' ').trim().slice(0, 300); })()""")
            print('   nachher:', a1 and a1[:2], '| Liste:', lst)
            ok_a = ok_a0 and bool(a1) and a1[1] == 'design' and bool(lst) and ('design' == lst or 'design “artwork”' in lst)
            css = pg.evaluate("""(() => { for (const sh of document.styleSheets) { let rules; try { rules = sh.cssRules; } catch (e) { continue; }
              for (const r of rules) if (r.selectorText === '.dci-note.dci-uncr') return r.style.backgroundColor; } return null; })()""")
            print('B) Hinweis:', css, '| Fehler:', errs)
            ok_b = css == 'rgb(255, 248, 219)'
            results += [ok_a, ok_b, not errs]
            b.close()
    finally:
        H.discogs_release = orig
        H.ARTISTS.pop(3361, None)
        H.ENTRIES_VIEW = 'legacy'
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_emcell3109():
    """Credits Importer 3.109.0 (collected items Z-EMCELL, Z-EMSCR, Z-EMNOTE): Cell Lu – "Piano" track 1, "Vocals" track 2, "Drums"
    track 3, "Producer", "Liner Notes" (five events: more than shared, each block its own); Sax Two – "Soprano Saxophone [Guest], Flute [Guest]".
    A) Cells of events a block does not show are ticks where MusicBrainz has the type on the event's level (until 3.108.0 striped,
       nothing to tick): piano at ① (all tracks), ③ (track 2), ⑤ (release); liner notes only at ⑤ (no liner notes on recordings).
    B) Piano ticked at ①: on all tracks too (its track 1 stays).
    C) Both ticks of the piano taken away: the line stays, grey, its ticks free; ticked at ③ again: piano on track 2.
    D) Z-EMSCR (narrow window): a bar above the head as wide as the table; moved, the table follows; ⇧ + wheel scrolls sideways.
       Z-EMNOTE: the block's head stays at the left edge of the box, not wider than it.
    E) Sax Two "on the release", then the soprano saxophone ticked on the recordings: the automatic row's tick there yellow, its
       tooltip names the soprano saxophone.
    F) The compact view: a chip of the piano dragged – the events where it is not and that can have it are targets (dashed), the
       liner notes' chip: the recordings are no target; the drag ended: none."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    for i, n in ((9131, 'soprano saxophone'), (9142, 'flute')):
        H.attr(i, n, 14, 14)
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS[3371] = (H.uid('dddddddd', 3371), 'Cell Lu')
    H.ARTISTS[3372] = (H.uid('dddddddd', 3372), 'Sax Two')
    CR = [('Cell Lu', 'Piano', '1', 3371), ('Cell Lu', 'Vocals', '2', 3371), ('Cell Lu', 'Drums', '3', 3371), ('Cell Lu', 'Producer', '', 3371),
          ('Cell Lu', 'Liner Notes', '', 3371), ('Sax Two', 'Soprano Saxophone [Guest], Flute [Guest]', '', 3372)]

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, t, i in CR]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    SEC = "(name) => [...document.querySelectorAll('section.dci-group')].find(x => (x.querySelector('.dci-gname strong') || {}).textContent.trim() === name)"
    GRID = """([sec, name]) => { const g = (%s)(name); const t = g && g.querySelector('table.dci-em-one'); if (!t) return null;
      const nm = (tr) => { const p = tr.querySelector('[data-f=em-primary]'); if (p && p.value) return p.value; const r = tr.querySelector('.dci-em-role');
        return !r ? '' : r.tagName === 'SELECT' ? (r.selectedOptions[0] || {}).text || '' : r.textContent; };
      return [...t.querySelectorAll('tr.dci-em-line')].map(tr => [nm(tr),
        tr.classList.contains('dci-em-skip'), [...tr.querySelectorAll('td.dci-em-c-ev')].map(td => { const c = td.querySelector('input');
          return (td.classList.contains('dci-em-c-other') ? 'o' : td.classList.contains('dci-em-c-none') ? '-' : '') + (c ? (c.checked ? 'X' : '.') + (c.disabled ? 'D' : '') : '')
            + (td.classList.contains('dci-em-c-autohl') ? '!' : ''); })]); }""" % SEC
    TICK = """([name, line, i]) => { const g = (%s)(name); const nm = (tr) => { const p = tr.querySelector('[data-f=em-primary]'); if (p && p.value) return p.value;
      const r = tr.querySelector('.dci-em-role'); return !r ? '' : r.tagName === 'SELECT' ? (r.selectedOptions[0] || {}).text || '' : r.textContent; };
      const tr = [...g.querySelectorAll('tr.dci-em-line')].find(tr => nm(tr) === line); const c = tr.querySelectorAll('td.dci-em-c-ev')[i].querySelector('input'); c.click(); return c.checked; }""" % SEC
    grid = lambda pg, n: {r[0]: r[1:] for r in pg.evaluate(GRID, ['', n]) or []}
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'matrix'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            g0 = grid(pg, 'Cell Lu')
            print('A)', g0)
            results.append(g0.get('piano') == [False, ['o.', 'X', 'o.', '.', 'o.']] and g0.get('liner notes') == [False, ['-', '-', '-', '-', 'X']]
                           and g0.get('producer') == [False, ['X', 'o.', 'o.', 'o.', 'o.']])
            # B)
            pg.evaluate(TICK, ['Cell Lu', 'piano', 0])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            g1 = grid(pg, 'Cell Lu')
            print('B)', g1.get('piano'))
            results.append(g1.get('piano', [0, []])[1][:2] == ['X', 'X'])
            # C)
            pg.evaluate(TICK, ['Cell Lu', 'piano', 0])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            pg.evaluate(TICK, ['Cell Lu', 'piano', 1])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            g2 = grid(pg, 'Cell Lu')
            pi = g2.get('piano') or [False, []]
            free = [k for k, c in enumerate(pi[1]) if c and 'D' not in c and c.strip('o') in ('.',)]
            ix = next((k for k, c in enumerate(pi[1]) if c == 'o.'), None)
            print('C) leer:', pi, '| frei:', free)
            ok_c = pi[0] is True and 'X' not in ''.join(pi[1]) and len(free) >= 3 and ix is not None
            if ix is not None:
                pg.evaluate(TICK, ['Cell Lu', 'piano', ix])
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
            g3 = grid(pg, 'Cell Lu')
            head = pg.evaluate("[...document.querySelectorAll('table.dci-em-one thead th')].map(th => th.textContent.replace(/\\s+/g, ' ').trim())")
            print('   wieder:', g3.get('piano'), head)
            p3 = g3.get('piano') or [True, []]
            evs = [h for h in head if 'Recording' in h or 'Release' in h]
            ok_c = ok_c and p3[0] is False and sum(c.count('X') for c in p3[1]) == 1
            results.append(ok_c)
            # D)
            pg.click('#dci-log [data-act=log-hide], #dci-log button:has-text("Hide")') if pg.locator('#dci-log button:has-text("Hide")').count() else None
            pg.set_viewport_size({'width': 700, 'height': 800})
            pg.wait_for_timeout(600)
            ST = """(name) => { const g = (%s)(name); const w = g.querySelector('.dci-em-onewrap'); const top = g.querySelector('.dci-em-hbar-top'); const h = g.querySelector('.dci-em-bhead');
              const wr = w.getBoundingClientRect(), hr = h.getBoundingClientRect();
              return { sw: w.scrollWidth, cw: w.clientWidth, sl: w.scrollLeft, top: top ? [top.hidden, top.firstElementChild.style.width, top.scrollLeft] : null,
                head: [Math.round(hr.left - wr.left), Math.round(hr.width)] }; }""" % SEC
            d0 = pg.evaluate(ST, 'Cell Lu')
            pg.evaluate("(name) => { const t = (%s)(name).querySelector('.dci-em-hbar-top'); t.scrollLeft = 150; t.dispatchEvent(new Event('scroll')); }" % SEC, 'Cell Lu')
            pg.wait_for_timeout(300)
            d1 = pg.evaluate(ST, 'Cell Lu')
            pg.evaluate("(name) => { const w = (%s)(name).querySelector('.dci-em-onewrap td.dci-em-c-ev'); w.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, shiftKey: true, bubbles: true, cancelable: true })); }" % SEC, 'Cell Lu')
            pg.wait_for_timeout(300)
            d2 = pg.evaluate(ST, 'Cell Lu')
            # (review) a tick draws the entry anew: the box stays where it was scrolled to, the bar shown
            pg.evaluate(TICK, ['Cell Lu', 'drums (drum set)', 4])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            d3 = pg.evaluate(ST, 'Cell Lu')
            print('D)', d0, d1, d2, d3)
            results.append(d0['sw'] > d0['cw'] and d0['top'] and d0['top'][0] is False and d0['top'][1] == f"{d0['sw']}px"
                           and d1['sl'] == 150 and d2['sl'] == 250 and abs(d1['head'][0]) <= 2 and d1['head'][1] <= d1['cw']
                           and d3['sl'] == 250 and d3['top'] and d3['top'][0] is False and d3['top'][2] == 250)
            pg.set_viewport_size({'width': 1280, 'height': 900})
            pg.wait_for_timeout(400)
            # E)
            pg.click(f"{sec_sel(pg, 'Sax Two')} [data-act=insts-set][data-insts=release]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            s0 = grid(pg, 'Sax Two')
            print('E) vorher:', s0)
            rec = next((k for k, c in enumerate(s0.get('soprano saxophone', [0, []])[1]) if c in ('.', 'o.')), None)
            if rec is not None:
                pg.evaluate(TICK, ['Sax Two', 'soprano saxophone', rec])
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
            s1 = grid(pg, 'Sax Two')
            tip = pg.evaluate("(name) => ((%s)(name).querySelector('td.dci-em-c-autohl') || {}).title || ''" % SEC, 'Sax Two')
            print('   nachher:', s1, '|', tip)
            auto = [v for k, v in s1.items() if k not in ('soprano saxophone', 'flute')]
            results.append(rec is not None and any('X!' in v[1] for v in auto) and 'soprano saxophone' in tip
                           and not any('!' in c for k, v in s0.items() for c in v[1]))
            # F)
            pg.click('.dci-head [data-act=view-toggle]')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            DRAG = """([name, line]) => { const g = (%s)(name); const chip = [...g.querySelectorAll('.dci-em-chip[data-drag=em-chip]')].find(c => c.querySelector('.dci-em-chipname').textContent.trim().startsWith(line));
              if (!chip) return null; chip.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: new DataTransfer() }));
              const out = [...g.querySelectorAll('.dci-em-cl[data-emev]')].map(x => (x.classList.contains('dci-em-cltarget') ? 'T' : x.classList.contains('dci-em-clnot') ? 'N' : '-'));
              chip.dispatchEvent(new DragEvent('dragend', { bubbles: true })); return out; }""" % SEC
            f1 = pg.evaluate(DRAG, ['Cell Lu', 'piano'])
            f2 = pg.evaluate(DRAG, ['Cell Lu', 'liner notes'])
            left = pg.evaluate("document.querySelectorAll('.dci-em-cltarget, .dci-em-clnot').length")
            print('F)', f1, f2, left)
            results.append(bool(f1) and f1.count('T') >= 3 and f1.count('-') >= 1 and bool(f2) and f2.count('N') >= 3 and f2.count('T') == 0 and left == 0)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.LINKED.update(linked0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_instl3109():
    """Credits Importer 3.109.0 (collected item Z-INSTL): Discogs names Jane Voice with "Voice, Soprano Saxophone, Flute" without tracks.
    "Instruments: on the release" – her three rows on the release; the question of "Voice" (Q011) answered "other vocals “voice”": the row
    stays on the release (MusicBrainz has vocal on the release; until 3.108.0 the answer's level, the recordings, came back); "vocals" the
    same. A row on the recordings answered: stays there. (review) Only a level put there: "Directed By" (Q003, its rule's level the recordings)
    answered "creative direction" goes to the release group, as before (MusicBrainz has it on the recordings too)."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    for i, n in ((9131, 'soprano saxophone'), (9142, 'flute')):
        H.attr(i, n, 14, 14)
    H.attr(9125, 'other vocals', 3, 3)
    H.lt(9511, H.uid('1a1a1a1a', 9511), 'creative direction', 'artist', 'recording', (1,))
    H.lt(9512, H.uid('1a1a1a1a', 9512), 'creative direction', 'artist', 'release_group', (1,))
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.lt(9057, H.uid('ffffffff', 9057), 'vocal', 'artist', 'release', (3, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CR = [('Jane Voice', 'Voice, Soprano Saxophone, Flute', 3381), ('Joe Voice', 'Voice', 3382), ('Poe Voice', 'Directed By', 3383)]
    for n, _r, i in CR:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n)

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CR]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    VOICE = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      const tr = g && [...g.querySelectorAll('tr.dci-row')].find(t => (t.querySelector('.dci-drole') || { dataset: {} }).dataset.raw.trim() === 'Voice'); if (!tr) return null;
      const lv = tr.querySelector('[data-act=level][aria-pressed=true]'); const pr = tr.querySelector('[data-f=primary]');
      return [lv ? lv.dataset.level : '', pr ? pr.value : '', [...tr.querySelectorAll('.dci-type-ask [data-act=type-pick]')].map(b => b.textContent.trim())]; }"""
    PICK = """([name, label]) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      const tr = [...g.querySelectorAll('tr.dci-row')].find(t => (t.querySelector('.dci-drole') || { dataset: {} }).dataset.raw.trim() === 'Voice');
      const b = [...tr.querySelectorAll('.dci-type-ask [data-act=type-pick]')].find(x => x.textContent.trim() === label); if (b) b.click(); return !!b; }"""
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            pg.click(f"{sec_sel(pg, 'Jane Voice')} [data-act=insts-set][data-insts=release]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            v0 = pg.evaluate(VOICE, 'Jane Voice')
            ok1 = pg.evaluate(PICK, ['Jane Voice', 'other vocals “voice”'])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            v1 = pg.evaluate(VOICE, 'Jane Voice')
            ok2 = pg.evaluate(PICK, ['Jane Voice', 'vocals'])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            v2 = pg.evaluate(VOICE, 'Jane Voice')
            pg.evaluate(PICK, ['Joe Voice', 'other vocals “voice”'])
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            j1 = pg.evaluate(VOICE, 'Joe Voice')
            POE = """() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Poe Voice');
              const tr = g && g.querySelector('tr.dci-row'); if (!tr) return null; const lv = () => (tr.isConnected ? tr : g.querySelector('tr.dci-row')).querySelector('[data-act=level][aria-pressed=true]');
              const before = (lv() || { dataset: {} }).dataset.level; const b = [...tr.querySelectorAll('.dci-type-ask [data-act=type-pick]')].find(x => x.textContent.trim() === 'creative direction');
              if (b) b.click(); return [before, !!b]; }"""
            po0 = pg.evaluate(POE)
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            po1 = pg.evaluate("""() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Poe Voice');
              const tr = g && g.querySelector('tr.dci-row'); const lv = tr && tr.querySelector('[data-act=level][aria-pressed=true]'); return lv ? lv.dataset.level : ''; }""")
            print('Jane:', v0, ok1, v1, ok2, v2, '| Joe:', j1, '| Poe:', po0, po1)
            results.append(bool(v0) and v0[0] == 'release' and ok1 and v1[:2] == ['release', 'other vocals'] and ok2 and v2[0] == 'release'
                           and bool(j1) and j1[:2] == ['recording', 'other vocals'] and bool(po0) and po0 == ['recording', True] and po1 == 'release_group')
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.LINKED.update(linked0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_yell3110():
    """Credits Importer 3.110.0 (collected item Z-YELL): what is open, counted and marked – must (orange: not staged without an answer)
    and can (yellow: staged as suggested). Discogs: "Directed By" (Dir Ed; Q003, no type), "English Translation" (Tr Eng; liner notes
    taken as a suggestion), "Bass" (Bass Guy; Q001, bass until chosen), "Producer" of No Link (not on MusicBrainz), Sax Two's soprano
    saxophone and flute (Z-INSTS).
    A) The footer: "● 2 must" (Dir Ed, No Link) and "● 4 can" (Tr Eng, Bass Guy, the two dates of the notes – Z-YELLDATE 3.112.0;
       since 3.112.0 "● 2" and "● 4", the words in the tooltip – Z-YELLSHORT); the entries' heads a dot each; Dir Ed's row orange,
       Tr Eng's question yellow with ✓ / ✕.
    B) "● 2 must" clicked: to the first one (flashing).
    C) Tr Eng ✓: the answer taken (no suggestion any more), "● 1 can"; Dir Ed answered "creative direction": "● 1 must".
    D) Sax Two "on the release", the soprano saxophone ticked on the recordings: a can more (the automatic row); ✓ – green with ↺,
       not counted, kept for the release (with "Remember"); ↺ – open again.
    E) ⚙ Settings → Staging "One counter": "● n open" alone.
    F) The compact view: the entries stay folded, the dots at their heads, Bass Guy's compact line yellow.
    G) The matrix view, compact: Bass Guy's chip yellow.
    H) (review) Tr Eng's ✓ green with ↺ (it stays visible); the keys by the entry's MBID; the import repeated (with "Remember"): Tr Eng
       confirmed still (green), not counted."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    for i, n in ((9131, 'soprano saxophone'), (9142, 'flute')):
        H.attr(i, n, 14, 14)
    H.attr(1018, 'translator', 1018)
    H.LTS[24]['attributes']['1018'] = {'min': 0, 'max': None}
    H.lt(44, H.uid('1aaa0000', 44), 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.lt(9511, H.uid('1a1a1a1a', 9511), 'creative direction', 'artist', 'recording', (1,))
    H.lt(9512, H.uid('1a1a1a1a', 9512), 'creative direction', 'artist', 'release_group', (1,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CR = [('Dir Ed', 'Directed By', 3391), ('Tr Eng', 'English Translation', 3392), ('Bass Guy', 'Bass', 3393), ('Sax Two', 'Soprano Saxophone, Flute', 3394)]
    for n, _r, i in CR:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n)

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': '', 'id': i, 'join': ''} for n, r, i in CR] \
            + [{'name': 'No Link', 'anv': '', 'role': 'Producer', 'tracks': '', 'id': 3395, 'join': ''}]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    FOOT = "[...document.querySelectorAll('[data-el=yell] .dci-yell-c')].map(c => [c.className.replace('dci-yell-c ', ''), c.querySelector('.dci-yell-n').textContent.trim()])"
    DOTS = """[...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
      [...g.querySelectorAll('.dci-yell-dot')].map(d => d.className.replace('dci-yell-dot ', '') + ':' + d.textContent.trim())]).filter(x => x[1].length)"""
    SEC = "(name) => [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name)"
    MARK = """(name) => { const g = (%s)(name); return g ? [...g.querySelectorAll('.dci-yell-must, .dci-yell-can, .dci-yell-ok')].map(x => x.tagName.toLowerCase() + '.' + [...x.classList].filter(c => c.startsWith('dci-yell') || c.startsWith('dci-type-ask') || c.startsWith('dci-em-chip') || c === 'dci-row' || c === 'dci-em-line').join('.')
      + (x.querySelector(':scope > .dci-yell-ctl, .dci-yell-ctl') ? '+ctl' : '')) : null; }""" % SEC
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            f0, d0 = pg.evaluate(FOOT), pg.evaluate(DOTS)
            m0 = {n: pg.evaluate(MARK, n) for n in ('Dir Ed', 'Tr Eng', 'Bass Guy', 'No Link')}
            print('A)', f0, d0, m0)
            results.append(f0 == [['dci-yell-c-must', '● 2'], ['dci-yell-c-can', '● 4']]
                           and dict(d0).get('Dir Ed') == ['dci-yell-dot-must:● 1'] and dict(d0).get('Tr Eng') == ['dci-yell-dot-can:● 1']
                           and dict(d0).get('Bass Guy') == ['dci-yell-dot-can:● 1'] and dict(d0).get('No Link') == ['dci-yell-dot-must:● 1']
                           and any('dci-yell-must' in x for x in m0['Dir Ed']) and any('dci-type-ask' in x and 'dci-yell-can' in x and x.endswith('+ctl') for x in m0['Tr Eng']))
            # B)
            pg.click('[data-el=yell] .dci-yell-c-must .dci-yell-n')
            pg.wait_for_timeout(300)
            fl = pg.evaluate("[...document.querySelectorAll('.dci-flash')].map(x => (x.closest('section.dci-group') || { querySelector: () => null }).querySelector('.dci-gname strong')?.textContent.trim())")
            print('B)', fl)
            results.append(len(fl) >= 1 and fl[0] in ('Dir Ed', 'No Link'))
            # C)
            pg.evaluate("(name) => (%s)(name).querySelector('.dci-yell-ctl [data-act=yell-ok]').click()" % SEC, 'Tr Eng')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            f1 = pg.evaluate(FOOT)
            pre = pg.evaluate("(name) => !!(%s)(name).querySelector('.dci-type-preset')" % SEC, 'Tr Eng')
            pg.evaluate("(name) => [...(%s)(name).querySelectorAll('[data-act=type-pick]')].find(b => b.textContent.trim() === 'creative direction').click()" % SEC, 'Dir Ed')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            f2 = pg.evaluate(FOOT)
            print('C)', f1, pre, f2)
            green = pg.evaluate("(name) => { const q = (%s)(name).querySelector('.dci-type-ask'); return !!q && q.classList.contains('dci-yell-ok') && !!q.querySelector('[data-act=yell-undo]'); }" % SEC, 'Tr Eng')
            print('   grün:', green)
            results.append(f1 == [['dci-yell-c-must', '● 2'], ['dci-yell-c-can', '● 3']] and not pre and green
                           and f2 == [['dci-yell-c-must', '● 1'], ['dci-yell-c-can', '● 3']])
            # D)
            pg.click(f"{sec_sel(pg, 'Sax Two')} [data-act=insts-set][data-insts=release]")
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            # the soprano saxophone also on the recordings: its row's level clicked (a row of its own on all tracks)
            sop = pg.evaluate("""(name) => { const g = (%s)(name); const tr = [...g.querySelectorAll('tr.dci-row')].find(t => (t.querySelector('[data-f=primary]') || {}).value === 'soprano saxophone');
              return tr ? tr.dataset.row : null; }""" % SEC, 'Sax Two')
            if sop:
                pg.click(f'tr.dci-row[data-row="{sop}"] [data-act=level][data-level=recording]')
                H.wait_still(pg, "document.body.innerHTML", 10, 200)
            f3 = pg.evaluate(FOOT)
            m3 = pg.evaluate(MARK, 'Sax Two')
            ok_btn = pg.evaluate("(name) => { const b = (%s)(name).querySelector('.dci-yell-ctl [data-act=yell-ok]'); if (b) b.click(); return !!b; }" % SEC, 'Sax Two')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            f4 = pg.evaluate(FOOT)
            m4 = pg.evaluate(MARK, 'Sax Two')
            kept = pg.evaluate(f"localStorage.getItem('dci-yell:{H.REL}')")
            undo = pg.evaluate("(name) => { const b = (%s)(name).querySelector('.dci-yell-ctl [data-act=yell-undo]'); if (b) b.click(); return !!b; }" % SEC, 'Sax Two')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            f5 = pg.evaluate(FOOT)
            print('D)', sop, f3, m3, ok_btn, f4, m4, kept, undo, f5)
            results.append(f3 == [['dci-yell-c-must', '● 1'], ['dci-yell-c-can', '● 4']] and ok_btn
                           and f4 == [['dci-yell-c-must', '● 1'], ['dci-yell-c-can', '● 3']] and any('dci-yell-ok' in x for x in m4)
                           and bool(kept) and 'auto:dddddddd-' in kept and 'p:dddddddd-' in kept and undo and f5 == f3)
            # E)
            H.open_settings(pg, 'staging')
            pg.check('[data-f=yell-one]')
            pg.wait_for_timeout(300)
            f6 = pg.evaluate(FOOT)
            pg.uncheck('[data-f=yell-one]')
            pg.wait_for_timeout(300)
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
            pg.wait_for_timeout(200)
            print('E)', f6)
            results.append(f6 == [['dci-yell-c-all', '● 5']])
            # F)
            pg.locator('.dci-head [data-act=view-toggle]').evaluate('b => b.click()')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            d7 = pg.evaluate(DOTS)
            chip = pg.evaluate("(name) => { const g = (%s)(name); const c = g && g.querySelector('.dci-em-chip, tr.dci-row'); return c ? c.className : null; }" % SEC, 'Bass Guy')
            print('F)', d7, chip)
            results.append(dict(d7).get('Bass Guy') == ['dci-yell-dot-can:● 1'] and bool(chip) and 'dci-yell-can' in chip)
            # G)
            H.open_settings(pg, 'appearance')
            mx = pg.evaluate("(() => { const b = document.querySelector('[data-el=settings] [data-act=entries-view][data-view=matrix]'); if (b) b.click(); return !!b; })()")
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            chip2 = pg.evaluate("(name) => { const g = (%s)(name); const c = g && g.querySelector('.dci-em-chip'); return c ? c.className : null; }" % SEC, 'Bass Guy')
            print('G)', mx, chip2)
            results.append(mx and bool(chip2) and 'dci-yell-can' in chip2)
            # H)
            pg.click('[data-el=source] [data-act=repeat-open]')
            pg.wait_for_timeout(200)
            pg.click('[data-el=repeat] [data-act=repeat-do]')
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            f8 = pg.evaluate(FOOT)
            tr8 = pg.evaluate("(name) => { const g = (%s)(name); const q = g && g.querySelector('.dci-yell-ok'); return q ? q.className : null; }" % SEC, 'Tr Eng')
            print('H)', f8, tr8)
            results.append(bool(tr8) and 'dci-yell-ok' in tr8 and f8 and f8[1][1] == '● 3')
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.LINKED.update(linked0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_sort3112():
    """Credits Importer 3.112.0 (collected items Z-SORT, Z-SCOPE): the order of the entries and the works' filter in the line "Level
    for all rows" (the test release: Bass Man, Guitar Guy, Keys Guy, Drum Guy – instruments –, Photo Guy, Ann Rep, Bob Producer …).
    A) "Order:" as in the source by default; "by kind": headings, "Instruments" first with the four players in the source's order,
       no entry twice (until 3.111.0 no choice).
    B) "by name": the entries by name, no heading.
    C) "by level": Bob Producer on Skip – under "Skipped" at the end; the choice kept (dci-sort).
    D) ⚙ Settings → Appearance "Offer the order …" off: no choice, the source's order.
    E) "Works: with | only | without" (no "only works", no line "Stage:"); "only" chosen, the import repeated: "with" again; (review)
       "Skip" for all, "only" (the works back), "with": all on Skip again."""
    NAMES = """[...document.querySelectorAll('[data-el=groups] section.dci-group')].map(g => g.querySelector('.dci-gname strong').textContent.trim())"""
    HEADS = """[...document.querySelectorAll('[data-el=groups] .dci-sorthead')].map(h => h.textContent.trim())"""
    FIRST = """(() => { const out = []; let h = null; for (const el of document.querySelectorAll('[data-el=groups] .dci-sorthead, [data-el=groups] section.dci-group')) {
      if (el.matches('.dci-sorthead')) h = el.textContent.trim(); else out.push([h, el.querySelector('.dci-gname strong').textContent.trim()]); } return out; })()"""
    results = []
    with sync_playwright() as p:
        H.ENTRIES_VIEW = 'legacy'
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        src = pg.evaluate(NAMES)
        opts = pg.evaluate("[...document.querySelectorAll('[data-el=toolbar] [data-f=sort-mode] option')].map(o => o.value)")
        sel0 = pg.evaluate("(document.querySelector('[data-f=sort-mode]') || {}).value")
        pg.select_option('[data-f=sort-mode]', 'kind')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        k = pg.evaluate(FIRST)
        heads = pg.evaluate(HEADS)
        print('A) Quelle:', src, '| Optionen:', opts, sel0, '\n   nach Art:', k, heads)
        inst = [n for h, n in k if h == 'Instruments']
        results.append(opts == ['source', 'kind', 'alpha', 'etype', 'level'] and sel0 == 'source' and heads[:1] == ['Instruments']
                       and inst == [n for n in src if n in inst] and len(inst) >= 3 and sorted(n for _h, n in k) == sorted(src) and len(heads) == len(set(heads)))
        pg.select_option('[data-f=sort-mode]', 'alpha')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        al = pg.evaluate(NAMES)
        print('B)', al, pg.evaluate(HEADS))
        results.append(al == sorted(src, key=str.lower) and pg.evaluate(HEADS) == [])
        pg.click("section.dci-group:has(.dci-gname strong:text-is('Bob Producer')) tr.dci-row [data-act=level][data-level=skip]")
        pg.select_option('[data-f=sort-mode]', 'level')
        H.wait_still(pg, "document.body.innerHTML", 10, 200)
        lv = pg.evaluate(FIRST)
        kept = pg.evaluate("localStorage.getItem('dci-sort')")
        print('C)', lv, kept)
        results.append(lv[-1] == ['Skipped', 'Bob Producer'] and lv[0][0] == 'Recordings' and kept == '"level"')
        H.open_settings(pg, 'appearance')
        pg.uncheck('[data-f=sort-on]')
        pg.wait_for_timeout(300)
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        off = [pg.evaluate("!!document.querySelector('[data-f=sort-mode]')"), pg.evaluate(NAMES), pg.evaluate(HEADS)]
        print('D)', off)
        results.append(off[0] is False and off[1] == src and off[2] == [])
        sc = pg.evaluate("[!!document.querySelector('[data-act=bulk-level][data-level=only-works]'), [...document.querySelectorAll('[data-act=scope]')].map(b => b.textContent.trim()), (document.querySelector('.dci-scope-label') || {}).textContent]")
        pg.click('[data-act=scope][data-scope=work]')
        pg.wait_for_timeout(400)
        on = pg.evaluate("(document.querySelector('[data-act=scope][aria-pressed=true]') || {}).dataset?.scope")
        pg.click('[data-el=source] [data-act=repeat-open]')
        pg.wait_for_timeout(200)
        pg.click('[data-el=repeat] [data-act=repeat-do]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
        H.wait_still(pg, "document.body.innerHTML", 10, 300)
        after = pg.evaluate("(document.querySelector('[data-act=scope][aria-pressed=true]') || {}).dataset?.scope")
        print('E)', sc, on, after)
        # (review) "Skip" for all, "only", "with": the works on Skip again (the filter changes no row for good)
        pg.click('[data-act=bulk-level][data-level=skip]')
        pg.wait_for_timeout(300)
        pg.click('[data-act=scope][data-scope=work]')
        pg.wait_for_timeout(300)
        mid = pg.evaluate("[...document.querySelectorAll('.dci-matrix th[data-colhead]')].length")
        pg.click('[data-act=scope][data-scope=all]')
        pg.wait_for_timeout(300)
        back = pg.evaluate("MB.relationshipEditor ? [...document.querySelectorAll('tr.dci-row [data-act=level][aria-pressed=true]')].map(b => b.dataset.level).filter(l => l !== 'skip').length : -1")
        print('   Skip, nur, mit – Matrix-Spalten bei „nur“:', mid, '| danach nicht Skip:', back)
        results.append(mid > 0 and back == 0)
        results.append(sc[0] is False and sc[1] == ['with', 'only', 'without'] and sc[2] == 'Works:' and on == 'work' and after == 'all')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_instlca3113():
    """Credits Importer 3.113.0 (collected item Z-INSTLCA, S177): ⑃ the common level of an entry's instruments. Discogs: Sax Two
    "Soprano Saxophone, Flute" (both woodwind), Voc Two "Lead Vocals, Backing Vocals", Track Guy "Piano" on track 1 and "Organ" on 2.
    A) Sax Two: ⑃ beside "Instruments:", its tooltip "… woodwind …"; a click: a row woodwind on the recordings, all tracks, the two
       instruments stay; ⑃ pressed; again: the row gone (until 3.112.0 no ⑃).
    B) Voc Two: ⑃ "… vocals …": a row vocal without a voice.
    C) Track Guy (tracks of their own): no ⑃. (review) The import repeated: the row of Voc Two there again, once, ⑃ pressed.
    D) ⚙ Settings → Appearance "Offer ⑃" off: none."""
    import copy
    orig = H.discogs_release
    lts0, attrs0 = copy.deepcopy(H.LTS), copy.deepcopy(H.ATTRS)
    linked0 = copy.deepcopy({k: H.LINKED.get(k) for k in ('link_type', 'link_attribute_type')})
    H.attr(9300, 'woodwind', 14, 14)
    for i, n in ((9131, 'soprano saxophone'), (9142, 'flute')):
        H.attr(i, n, 14, 9300)
    for i, n in ((9401, 'piano'), (9402, 'organ')):
        if i not in H.ATTRS:
            H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    CR = [('Sax Two', 'Soprano Saxophone, Flute', '', 3411), ('Voc Two', 'Lead Vocals, Backing Vocals', '', 3412), ('Track Guy', 'Piano', '1', 3413), ('Track Guy', 'Organ', '2', 3413)]
    for n, _r, _t, i in CR:
        H.ARTISTS[i] = (H.uid('dddddddd', i), n)

    def rel():
        d = orig()
        d['extraartists'] = [{'name': n, 'anv': '', 'role': r, 'tracks': t, 'id': i, 'join': ''} for n, r, t, i in CR]
        d['companies'] = []
        for t in d['tracklist']:
            t['extraartists'] = []
        return d
    H.discogs_release = rel
    SEC = "(name) => [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name)"
    BTN = "(name) => { const b = (%s)(name)?.querySelector('[data-act=insts-common]'); return b ? [b.title, b.getAttribute('aria-pressed')] : null; }" % SEC
    ROWS = """(name) => [...(%s)(name).querySelectorAll('tr.dci-row')].map(r => [((r.querySelector('[data-f=type]') || {}).selectedOptions || [])[0]?.dataset.name || '',
      (r.querySelector('[data-f=primary]') || {}).value || '', ([...r.querySelectorAll('[data-act=level][aria-pressed=true]')][0] || { dataset: {} }).dataset.level || '',
      r.querySelectorAll('.dci-trk input:checked, [data-f=track]:checked').length])""" % SEC
    results = []
    try:
        with sync_playwright() as p:
            H.ENTRIES_VIEW = 'legacy'
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            a0 = pg.evaluate(BTN, 'Sax Two')
            r0 = pg.evaluate(ROWS, 'Sax Two')
            pg.evaluate("(name) => (%s)(name).querySelector('[data-act=insts-common]').click()" % SEC, 'Sax Two')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            r1 = pg.evaluate(ROWS, 'Sax Two')
            a1 = pg.evaluate(BTN, 'Sax Two')
            pg.evaluate("(name) => (%s)(name).querySelector('[data-act=insts-common]').click()" % SEC, 'Sax Two')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            r2 = pg.evaluate(ROWS, 'Sax Two')
            print('A)', a0, r0, '\n  ', r1, a1, '\n  ', r2)
            results.append(bool(a0) and 'woodwind' in a0[0] and a0[1] == 'false' and len(r1) == len(r0) + 1 and r1[-1][:3] == ['instrument', 'woodwind', 'recording']
                           and r1[:len(r0)] == r0 and a1 and a1[1] == 'true' and r2 == r0)
            v0 = pg.evaluate(BTN, 'Voc Two')
            pg.evaluate("(name) => (%s)(name).querySelector('[data-act=insts-common]').click()" % SEC, 'Voc Two')
            H.wait_still(pg, "document.body.innerHTML", 10, 200)
            v1 = pg.evaluate(ROWS, 'Voc Two')
            print('B)', v0, v1)
            results.append(bool(v0) and 'vocals' in v0[0] and v1[-1][0] == 'vocal' and v1[-1][1] == '' and len(v1) == 3)
            t0 = pg.evaluate(BTN, 'Track Guy')
            print('C)', t0)
            results.append(t0 is None)
            # (review) the import repeated (keeping what was changed): the row of Voc Two there again, once
            pg.click('[data-el=source] [data-act=repeat-open]')
            pg.wait_for_timeout(200)
            pg.click('[data-el=repeat] [data-act=repeat-do]')
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
            H.wait_still(pg, "document.body.innerHTML", 10, 300)
            v2 = pg.evaluate(ROWS, 'Voc Two')
            vb = pg.evaluate(BTN, 'Voc Two')
            print('   wiederholt:', v2, vb)
            results.append(len(v2) == 3 and v2[-1][:2] == ['vocal', ''] and bool(vb) and vb[1] == 'true')
            H.open_settings(pg, 'appearance')
            pg.uncheck('[data-f=insts-common-on]')
            pg.wait_for_timeout(300)
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
            pg.wait_for_timeout(300)
            d0 = pg.evaluate(BTN, 'Sax Two')
            print('D)', d0)
            results.append(d0 is None)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
        H.LTS.clear()
        H.LTS.update(lts0)
        H.ATTRS.clear()
        H.ATTRS.update(attrs0)
        H.LINKED.update(linked0)
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
