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
BLOCKS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null;
  return [...g.querySelectorAll('.dci-em-block')].map(b => ({ key: b.dataset.block, head: (h => { const c = h.cloneNode(true); c.querySelectorAll('.dci-em-bac').forEach(x => x.remove()); return c.textContent; })(b.querySelector('.dci-em-bhead')).replace(/\\s+/g, ' ').trim(),
    tip: b.querySelector('.dci-em-bhead strong').title,
    ev: [...b.querySelectorAll('th.dci-em-ev')].map(h => { const c = h.cloneNode(true); c.querySelectorAll('.dci-em-evtoggle, button.dci-em-evdate, .dci-em-evdatebox').forEach(x => x.remove()); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
    add: [...b.querySelectorAll('[data-f=em-addev] option')].filter(o => o.value).map(o => o.textContent.trim()),
    lines: [...b.querySelectorAll('tr.dci-em-line')].map(t => ({ line: t.dataset.line, n: t.dataset.rows.split(',').length, skip: t.classList.contains('dci-em-skip'),
      role: ((t.querySelector('[data-f=em-primary]') || {}).value) || t.querySelector('.dci-em-c-role').textContent.replace(/\\s+/g, ' ').trim(),
      wrote: (t.querySelector('.dci-em-raw') || { textContent: '' }).textContent.trim(), credit: (t.querySelector('[data-f=em-credit]') || { value: '-' }).value,
      flags: [...t.querySelectorAll('[data-f=em-flag]')].filter(c => c.checked).map(c => c.value), ticks: [...t.querySelectorAll('[data-f=em-tick]')].map(c => c.checked),
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
       one line ① with both (in the order of the source); ② is gone.
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
            results.append([(l['head'], l['chips']) for l in b_part['lines']] == [('① Recording no date all 4 tracks', ['piano', 'electric guitar'])])
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
    and 18 px to the right of their words."""
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
    A) "Bass" (Q001): "? bass" with ▾ – electric bass guitar · double bass · acoustic bass guitar; "double bass" chosen: the
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
            results.append(bool(bass) and bass['q'] and [c['menu'] for c in a1 if c['line'] == bass['line']][0] == ['electric bass guitar', 'double bass', 'acoustic bass guitar']
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
            added = pg.evaluate(f"[...{sel('Solo Man')}.querySelectorAll('tr[data-rows]')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /^producer/.test(t))")
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

run_cases(globals())
