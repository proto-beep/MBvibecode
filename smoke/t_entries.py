"""Smoke test: the entries as a matrix (E4, Block AE; the default from Credits Importer 3.34.29) – collected items E4, 139, 141.

Cases: join (3.34.29), matrix (3.34.30), dates (3.34.31) – `python3 t_entries.py <case> …` runs only those. The other test files keep the entries as before
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
    ev: [...b.querySelectorAll('th.dci-em-ev')].map(h => h.textContent.replace(/\\s+/g, ' ').trim()),
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


run_cases(globals())
