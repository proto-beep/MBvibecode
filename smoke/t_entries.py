"""Smoke test: the entries as a matrix (E4, Block AE; the default from Credits Importer 3.34.29) – collected items E4, 139, 141.

Cases: join (3.34.29), matrix (3.34.30), dates (3.34.31), compact (3.35.0), restage (3.35.0), order (3.35.3), evhead (3.35.4), companies (3.35.5), remember (3.36.0), flagcols (3.36.6), chipask (3.37.14), chipinfo (3.38.6) – `python3 t_entries.py <case> …` runs only those. The other test files keep the entries as before
("legacy", harness.ENTRIES_VIEW); the cases here set the matrix (the script's default)."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser

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
    """Credits Importer 3.34.29 (E4, step 1 of Block AE; maintainer: "kannst du Block AE umsetzen und als standard führen? die
    alte darstellung aber als "Legacy" darstellung in den einstellungen behalten"): the entries as a matrix are the default; their
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
  return [...g.querySelectorAll('.dci-em-block')].map(b => ({ key: b.dataset.block, head: b.querySelector('.dci-em-bhead').textContent.replace(/\\s+/g, ' ').trim(),
    ev: [...b.querySelectorAll('th.dci-em-ev')].map(h => { const c = h.cloneNode(true); c.querySelectorAll('.dci-em-evtoggle').forEach(x => x.remove()); return c.textContent.replace(/\\s+/g, ' ').trim(); }),
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
    A) Multi Man: one block "3 instruments → instrument · from 3 rows · One row each", one event "① Recording all 4 tracks"
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
            results.append(bool(a) and len(a) == 1 and b0['head'] == '3 instruments → instrument · from 3 rows One row each'
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
    """Credits Importer 3.34.31 (E4, step 3 of Block AE; mockup version 3, board 4; collected item 139, maintainer: "ja mach
    das mal", "das soll immer das selbe sein. wenn ich also das event hier editiere verändert sich auch der date/track pool"):
    dates in an entry's matrix.
    A) A date of the pool dropped onto the line of acoustic guitar (Multi Man): the line moves into the date's event – a second
       column ② with the date, acoustic guitar ticked there only (the instrument "wanders"); a message with ↶.
    B) ↶: acoustic guitar back in ①, one event again.
    C) The date dropped onto the head of ①: all three instruments get it – still one event, its head shows the date.
    D) A date typed into the head of Solo Man's ① ("2001-06-05"): its rows get it as a new date of the pool; the date of
       Multi Man's ① changed in its head ("2001-03-02"): the pool's date itself changes.
    E) Another date dropped with ⇧ Shift onto the head of Voc Man's block: both voices stay without a date and get a row with
       it – ticked in ① and ②, a yellow question each ("… with and without a date – only … · keep both"); "only" for lead
       vocals: its row without a date goes (① stays ① – the events keep their numbers); "keep both" for background vocals: the
       question goes.
    E2) (3.35.0) With one line of a block shown (⚙ "Lines … before ▸ n more": 1) a date dropped onto the block's head: all three
       instruments of Multi Man get it, also those behind "▸ 2 more".
    F) Staged: Voc Man – lead and background vocals with the date joined (4), background vocals without a date (4)."""
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
            v3 = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' th.dci-em-ev [data-f=em-evdate]')].map(x => x.value)", multi)
            print('C) Kopf:', a3[0]['ev'], v3, [(l['role'], l['ticks']) for l in a3[0]['lines']])
            results.append(len(a3[0]['ev']) == 1 and v3 and v3[0] != '' and all(l['ticks'] == [True] for l in a3[0]['lines']))
            # D) dates typed into the heads
            solo = sec_sel(pg, 'Solo Man')
            n_pool = len(chips)
            pg.fill(f'{solo} th.dci-em-ev [data-f=em-evdate]', '2001-06-05')
            pg.press(f'{solo} th.dci-em-ev [data-f=em-evdate]', 'Tab')
            pg.wait_for_timeout(500)
            sv = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' th.dci-em-ev [data-f=em-evdate]')].map(x => x.value)", solo)
            chips2 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => [c.dataset.id, c.textContent.replace(/\\s+/g, ' ').trim()])")
            pg.fill(f'{multi} th.dci-em-ev [data-f=em-evdate]', '2001-03-02')
            pg.press(f'{multi} th.dci-em-ev [data-f=em-evdate]', 'Tab')
            pg.wait_for_timeout(500)
            chips3 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => [c.dataset.id, c.textContent.replace(/\\s+/g, ' ').trim()])")
            mv = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' th.dci-em-ev [data-f=em-evdate]')].map(x => x.value)", multi)
            changed = [c for c in chips3 if c[0] == d1]
            print('D) Solo Man:', sv, '| Pool:', len(chips2), '| Multi Man:', mv, '| der Pool-Eintrag:', changed)
            results.append(sv == ['2001-06-05'] and len(chips2) == n_pool + 1 and mv == ['2001-03-02'] and changed and '2001-03-02' in changed[0][1])
            # E) with Shift onto the head of a block
            voc = sec_sel(pg, 'Voc Man')
            pg.evaluate(DROP, [f'.dci-pchip-date[data-id="{d2}"]', f'{voc} .dci-em-bhead', True])
            pg.wait_for_timeout(500)
            e0 = pg.evaluate(BLOCKS, 'Voc Man')
            asks = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' .dci-em-both')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())", voc)
            print('E) mit ⇧:', e0[0]['ev'], [(l['role'], l['ticks'], l['n']) for l in e0[0]['lines']], '| Fragen:', asks)
            ok_e = len(e0[0]['ev']) == 2 and [(l['role'], l['ticks'], l['n']) for l in e0[0]['lines']] == [('lead vocals', [True, True], 2), ('background vocals', [True, True], 2)] \
                and len(asks) == 2 and all('with and without a date' in x and 'keep both' in x for x in asks)
            lead = e0[0]['lines'][0]['line']
            back = e0[0]['lines'][1]['line']
            pg.click(f'{voc} tr.dci-em-ask[data-rows] >> nth=0 >> [data-act=em-only]')
            pg.wait_for_timeout(400)
            pg.click(f'{voc} tr.dci-em-ask[data-rows] >> nth=0 >> [data-act=em-both]')
            pg.wait_for_timeout(400)
            e1 = pg.evaluate(BLOCKS, 'Voc Man')
            asks1 = pg.evaluate("(sel) => document.querySelectorAll(sel + ' .dci-em-both').length", voc)
            print('   only / both:', [(l['role'], l['ticks']) for l in e1[0]['lines']], '| Fragen:', asks1, lead, back)
            results.append(ok_e and [(l['role'], l['ticks']) for l in e1[0]['lines']] == [('lead vocals', [False, True]), ('background vocals', [True, True])] and asks1 == 0)
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
            ev2 = pg.evaluate("(sel) => [...document.querySelectorAll(sel + ' th.dci-em-ev [data-f=em-evdate]')].map(x => x.value)", multi)
            print('E2) Kopf des Blocks, 1 Zeile gezeigt:', hidden, '| danach:', ev2, [(l['role'], l['ticks']) for l in e2[0]['lines']])
            results.append(hidden == 1 and ev2 == ['2001-05'] and all(l['ticks'] == [True] for l in e2[0]['lines']) and len(e2[0]['lines']) == 3)
            # F) staged
            pg.click('[data-act=apply]')
            pg.wait_for_timeout(1500)
            added = pg.evaluate(ADDED_D)
            names = {H.uid('dddddddd', i - 2990): n for n, _r, i, _t in JOIN_CREDITS}
            vm = sorted((r['date'], tuple(r['attrs'])) for r in added if names.get(r['a']) == 'Voc Man' or names.get(r['b']) == 'Voc Man')
            print('F) Voc Man:', vm)
            dated = [x for x in vm if x[0]]
            results.append(len(vm) == 8 and len(dated) == 4 and all(x[1] == ('background vocals', 'lead vocals') for x in dated)
                           and all(x[1] == ('background vocals',) for x in vm if not x[0]))
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
    """Credits Importer 3.35.0 (E4, the last step of Block AE, milestone "Entries as a matrix"; mockup version 3, board 1: "die
    kompakte Ansicht ist die Matrix gedreht"): an entry compact as a matrix.
    A) ☰ compact: Multi Man – one line "① Recording no date all 4 tracks" with the chips electric guitar · acoustic guitar ·
       drums (drum set) “drums”; Part Man – ① electric guitar, ② (track 2) piano.
    B) The piano chip dragged onto the line of ①: piano moves there – one line ① with both (in the order of the source); ② is
       gone.
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
            pg.evaluate(DROP, [f'{part} .dci-em-cl[data-emev="{ev2}"] .dci-em-chip', f'{part} .dci-em-cl[data-emev="{ev1}"]', False])
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
       the changed one stays as it is (its rows are not staged again, the summary of the staging says so), the other three are
       staged anew – nothing twice."""
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
            results.append(len(kept) == 1 and len(fresh) == 3 and all('electric guitar [lead]' in r['attrs'] for r in fresh) and 'electric guitar' in kept[0]['attrs'])
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
    """Credits Importer 3.35.3 (AE-2; maintainer: "bitte noch ziehen ermöglichen", "ja nur bis zum nächsten import"): the lines
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
    date: (ed.querySelector('[data-f=em-evdate]') || {}).value, pool: [...ed.querySelectorAll('.dci-em-evpool')].map(b => b.textContent.trim() + (b.getAttribute('aria-pressed') === 'true' ? '*' : '')),
    tracks: [...ed.querySelectorAll('[data-f=em-evtrack]')].filter(c => c.checked).map(c => Number(c.dataset.i)), n: ed.querySelectorAll('[data-f=em-evtrack]').length,
    open: [...g.querySelectorAll('th.dci-em-ev.dci-em-evopen')].map(h => h.textContent.replace(/\\s+/g, ' ').replace('▾', '').trim()) }; }"""


def case_evhead():
    """Credits Importer 3.35.4 (AE-3; maintainer: "wenn man den ereigniskopf öffnet soll man datum und tracks einstellen können",
    "auch ebene ändern können", on roles MusicBrainz has not on the new level: "ja passt"): an event opened below its block.
    A) Part Man: ▸ in the head of ② (piano, track 2) opens it – "Event ② – … all its rows (1)", the levels of its types
       (here Recording only – the test's MusicBrainz has instruments on recordings only), the date field, the dates of the
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
            results.append(bool(a1) and a1['title'] == 'Event ② – what you set here goes for all its rows (1)' and a1['levels'] == ['Recording*']
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
            pg.fill(f'{part} .dci-em-evedit [data-f=em-evdate]', '2024-03')
            pg.press(f'{part} .dci-em-evedit [data-f=em-evdate]', 'Tab')
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
            results.append(bool(e1) and e1['title'].endswith('(1)') and e1['levels'] == ['Recording*', 'Release']
                           and bool(e2) and e2['title'].endswith('(2)') and e2['levels'] == ['Recording', 'Release*'] and e2b[0]['ev'] == ['① Release whole release']
                           and bool(e3) and e3['levels'] == ['Recording*', 'Release'] and e3['tracks'] == [0, 1, 2, 3] and e3['title'].endswith('(1)')
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


def case_companies():
    """Credits Importer 3.35.5 (AE-4; maintainer: "ja können auch in die matrix", "alle einträge die daten und/oder tracks anbieten.
    solche einträge kommen ja eher selten vor."): companies and places as a matrix when a row of theirs offers a date and/or tracks.
    A) The test release: Abbey Road Studios (a place, "Recorded At" on the 4 recordings) – a matrix: a block "Recorded At →
       recorded at", ① Recording all 4 tracks, ticked; Sony ("Phonographic Copyright (p)", a label on the release) – a matrix,
       ① Release whole release.
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
            results.append(k_abbey == [True, 0] and bool(abbey) and len(abbey) == 1 and abbey[0]['head'].startswith('Recorded At → recorded at')
                           and abbey[0]['ev'] == ['① Recording all 4 tracks'] and abbey[0]['lines'][0]['ticks'] == [True]
                           and k_sony == [True, 0] and bool(sony) and sony[0]['ev'] == ['① Release whole release'] and sony[0]['lines'][0]['ticks'] == [True])
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
            pg.fill(f'{sec} th.dci-em-ev [data-f=em-evdate]', '2001-03')
            pg.press(f'{sec} th.dci-em-ev [data-f=em-evdate]', 'Tab')
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
    """Credits Importer 3.36.0 (146; maintainer: "ja genau, soll alles wieder kommen"): the matrix of a remembered release after the
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
            results.append(before == after and before[0][0][2][0] == 'drums (drum set)' and before[1][0][1][1] == '② Recording tracks 2–3' and len(before[2]) == 2)
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
    """Credits Importer 3.36.6 (collected item 148; maintainer, with a screenshot of "add. guestsolo" over three checkboxes: "die anzeige
    hier ist noch nicht gut abgestimmt. solo muss über der rechten checkbox stehen."): in the full matrix each attribute of the
    lines (add., guest, solo …) is a column of its own – its word centred over the checkboxes of every line (±2 px), not wider
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
    """Credits Importer 3.37.14 (collected item 163; maintainer, with a screenshot of the chips "? bass ✕": "kann man die
    rollenabfragen nicht auch direkt auf dieser ebene durchführen? per drop down menü?", "ja das passt"): in an entry compact as a
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
    """Credits Importer 3.38.6 (collected item 163b; maintainer: "ja dezentes zeichen mit Tooltip", "ja nimm das ⓘ"): a chip whose
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


run_cases(globals())
