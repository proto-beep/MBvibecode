"""Discogs notes: dates and track groups found in the notes (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: datewords, facets, choose, trackpool, reldate – each the former smoke/t_<case>.py, unchanged; `python3 t_notes_dates.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_datewords():
    """Credits Importer 3.28.5: dates in the notes (collected items 64a, 64d, 80, 71, 76).
    A) In Node: "Recorded 19 & 20. 01. 2009." → 2009-01-19 – 2009-01-20 (D013, as "June 16 & 19"); "20. 01. 2009" (D002 with
       spaces); "Recorded: London - 1973 October 19" → 1973-10-19 (D017); "originally issued on LP in 1974" and "Released
       2003" give no date (D018); "Mixed May 2001. Released 2003." – no group from the sentence before (D019); "Mixed and
       mastered by Brandon Carnes in March 2026." → Mix and Mastering, "Recorded, mixed and mastered 2001" → all three (D020);
       "Recorded at X:" on the line before "12 June 2001" still names the group.
    B) The dashboard: Discogs notes "Recorded 19 & 20. 01. 2009. Mixed and mastered in March 2010. Originally issued on LP in
       2011." – the date matrix has [3.32.0] January 2009 under Performance (what the days have in common, D022; the period
       2009-01-19 – 2009-01-20 in the pool) and March 2010 under Mix and under Mastering (each its own pool entry, named for
       its group); 2011 is not in the pool."""
    import json
    import subprocess

    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const T = ['Recorded 19 & 20. 01. 2009.', 'Recorded 20. 01. 2009.', 'Recorded: London - 1973 October 19', 'Tracks 1-4 originally issued on LP in 1974.', 'Released 2003',
  'Mixed May 2001. Released 2003. Dedicated to Jim, 1999.', 'Mixed and mastered by Brandon Carnes in March 2026.', 'Recorded, mixed and mastered 2001', 'Recorded at X:\n12 June 2001'];
const v = (d) => [d.value.begin, d.value.end].map((x) => [x.year, x.month, x.day].filter((y) => y != null).join('-')).join('/');
console.log(JSON.stringify(T.map((t) => m.findDates(t).map((d) => [d.text, d.rule, v(d), d.hint, d.hints]))));
"""
    a = json.loads(subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True, check=True).stdout)
    for x in a:
        print('   ', x)
    results = []
    want = [[['19 & 20. 01. 2009', 'D013', '2009-1-19/2009-1-20', 'performance', []]],
            [['20. 01. 2009', 'D002', '2009-1-20/2009-1-20', 'performance', []]],
            [['1973 October 19', 'D017', '1973-10-19/1973-10-19', 'performance', []]],
            [], [],
            [['May 2001', 'D008', '2001-5/2001-5', 'mix', []], ['1999', 'D010', '1999/1999', '', []]],
            [['March 2026', 'D008', '2026-3/2026-3', 'mastering', ['mix', 'mastering']]],
            [['2001', 'D010', '2001/2001', 'mastering', ['performance', 'mix', 'mastering']]],
            [['12 June 2001', 'D004', '2001-6-12/2001-6-12', 'performance', []]]]
    print('A) Node:', a == want)
    results.append(a == want)
    orig = H.discogs_release


    def rel():
        d = orig()
        d['notes'] = 'Recorded 19 & 20. 01. 2009. Mixed and mastered in March 2010. Originally issued on LP in 2011.'
        return d


    H.discogs_release = rel
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
        mx = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}')")
        byId = {d['id']: d for d in pool}
        fmt = lambda d: '/'.join('-'.join(str(x) for x in (e['year'], e['month'], e['day']) if x) for e in (d['begin'], d['end']))
        cells = sorted((c['col'], byId[c['date']]['name'], fmt(byId[c['date']])) for c in mx.get('cells', []))
        names = sorted((d['name'], fmt(d)) for d in pool)
        print('B) Matrix:', cells, '| Pool:', names)
        results.append(cells == [('mastering', 'Mastering 1', '2010-3/2010-3'), ('mix', 'Mix 1', '2010-3/2010-3'), ('performance', 'Performance 1 (month)', '2009-1/2009-1')]
                       and ('Performance 1', '2009-1-19/2009-1-20') in names
                       and not any('2011' in n[1] for n in names))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_facets():
    """Credits Importer 3.28.6: track groups in the notes, "Facets" as on Discogs (collected items 64b, 64c).
    Sides A–F, side D one track without a number ("D"). The notes: "A1 to B1 recorded 22nd May 1981 in live concert at
    Goldsmith's College, London" / "C1 to D recorded 4th October 1979 at Heiman Recording Studios, London" / "E1 to F1
    recorded 2nd May 1980 at Heiman Recording Studios, London".
    A) The date matrix: three dates under Performance, each with its track group – A1–B1 (tracks 1–2), C1–D (3–5: "D" is the
       end of the range), E1–F1 (6–7).
    B) "in live concert" names tracks: "live" is offered for the existing link of track 1 (its sentence names A1–B1) with
       that reason – not for the whole release.
    C) No places or areas from the notes (no entry for Goldsmith's College, Heiman Recording Studios or London)."""
    POS = ['A1', 'B1', 'C1', 'C2', 'D', 'E1', 'F1']
    H.TITLES[:] = ['Part One', 'Part Two', 'Organic', 'Trisect', 'Ontology', 'Part Six', 'Part Seven']
    H.REC[:] = [H.uid('bbbbbbbb', i) for i in range(1, 8)]
    H.attr(578, 'live', 578)
    H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (578,))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    NOTES = ("A1 to B1 recorded 22nd May 1981 in live concert at Goldsmith's College, London\n"
             "C1 to D recorded 4th October 1979 at Heiman Recording Studios, London\n"
             "E1 to F1 recorded 2nd May 1980 at Heiman Recording Studios, London")
    orig = H.discogs_release


    def rel():
        d = orig()
        d['notes'] = NOTES
        d['tracklist'] = [{'position': p, 'title': t, 'type_': 'track', 'duration': '5:00', 'extraartists': []} for p, t in zip(POS, H.TITLES)]
        d['companies'] = [c for c in d['companies'] if c['entity_type_name'] != 'Recorded At']
        return d


    H.discogs_release = rel
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2000)
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]')")
        tgs = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-track-pool:{H.REL}') || '[]')")
        mx = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}') || '{{}}')")
        byId = {d['id']: d for d in pool}
        tgById = {g['id']: g for g in tgs}
        day = lambda d: '-'.join(str(x) for x in (d['begin']['year'], d['begin']['month'], d['begin']['day']))
        cells = sorted((c['col'], day(byId[c['date']]), [(tgById[t]['name'], tgById[t]['tracks']) for t in c['tgs']]) for c in mx.get('cells', []))
        print('A) Matrix:', cells)
        results.append(cells == [('performance', '1979-10-4', [('Tracks C1–D', [2, 3, 4])]), ('performance', '1980-5-2', [('Tracks E1–F1', [5, 6])]),
                                 ('performance', '1981-5-22', [('Tracks A1–B1', [0, 1])])])
        # B) "live" offered on track 1's existing link, for its tracks
        live = pg.evaluate("""[...document.querySelectorAll('.dci-wpill[data-attr=live]')].map(x => [x.textContent.trim(), x.title])""")
        print('B) live:', live)
        results.append(any('li?' in t and 'these tracks were recorded live' in title and 'Live recording' in title for t, title in live))
        # C) no places or areas from the notes
        names = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
        print('C) Einträge:', names)
        results.append(not any(n in names for n in ("Goldsmith's College", 'Heiman Recording Studios', 'London')))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_choose():
    """Separate days ("Recorded June 16 & 19, 1980 at …"): the pool keeps both days as Discogs gives them and gets
    the period as well; the matrix asks "choose" and applies nothing until then; choosing the period puts it on
    the rows; a group button moves the entry; without its period the single days stay. [3.32.0] Without D022 (with it the
    matrix gets the common month at once, see t_rules_window.py quickswitch)."""
    H.RULES_OFF = ['D022']  # [3.32.0] about the period and "choose": without D022 (what the days have in common at once)
    import re
    import zooid
    from common_rows import lib, cells

    zooid.setup('Recorded June 16 & 19, 1980 at Scholes Street Studio, Brooklyn, New York.')
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(300)
        pool = [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()]
        print('1) Pool:', pool)
        print('   Matrix:', cells(pg)['performance'])
        print('   Kopf:', re.sub(r'\s+', ' ', pg.locator('.dci-pools-head').inner_text()))
        pg.click('[data-el=datefind] summary')
        item = re.sub(r'\s+', ' ', pg.locator('[data-el=datefind-list] li').first.inner_text())
        print('   Fundliste:', item[:150])
        ok1 = len(pool) == 4 and 'Performance 1–2 · 1980-06-16 – 1980-06-19' in pool[2] and 'Performance 1–2 (month) · 1980-06' in pool[3] \
            and cells(pg)['performance'][0][0].startswith('choose: 2 dates as on Discogs: 1980-06-16 · 1980-06-19') and 'month only: 1980-06' in cells(pg)['performance'][0][0] \
            and 'also as a period: 1980-06-16 – 1980-06-19' in item and '1 to choose' in pg.locator('.dci-pools-head').inner_text()
        # 2) Apply before choosing: nothing on the rows
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(300)
        print('2) vor der Wahl – Liberty:', lib(pg))
        ok2 = lib(pg) == [(list(range(1, 11)), '')]
        # 3) a group button moves the entry (Mix), then back to Performance
        pg.locator('[data-el=datefind-list] li').first.locator('[data-act=datefind-use][data-group=mix]').click(); pg.wait_for_timeout(200)
        moved = (len(cells(pg)['mix']), len(cells(pg)['performance']))
        pg.evaluate("document.querySelector('[data-el=datefind]').open = true")
        pg.locator('[data-el=datefind-list] li').first.locator('[data-act=datefind-use][data-group=performance]').click(); pg.wait_for_timeout(200)
        print('3) per Knopf nach Mix (Mix, Performance):', moved, '| zurück:', (len(cells(pg)['mix']), len(cells(pg)['performance'])), '| Pool:', pg.locator('.dci-pchip-date').count())
        ok3 = moved == (1, 0) and len(cells(pg)['performance']) == 1 and pg.locator('.dci-pchip-date').count() == 4
        # 4) choose the period: it goes onto the rows (the studio too)
        pg.click('.dci-dm-choose [data-act=dm-choose][data-pick=range]'); pg.wait_for_timeout(200)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(400)
        print('4) Zeitraum gewählt:', cells(pg)['performance'], '| Liberty:', lib(pg), '| Scholes:', lib(pg, 'Scholes'))
        ok4 = lib(pg) == [(list(range(1, 11)), '1980-06-16 – 1980-06-19')] and lib(pg, 'Scholes') == [(list(range(1, 11)), '1980-06-16 – 1980-06-19')] \
            and lib(pg, 'Brooklyn') == [(list(range(1, 11)), '')]
        # 5) a fresh entry to choose; the period leaves the pool: the single days stay in the matrix
        pg.locator('.dci-dm-col[data-dmcol=performance] [data-act=dm-remove]').first.click(); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('[data-el=datefind]').open = true")
        pg.locator('[data-el=datefind-list] li').first.locator('[data-act=datefind-use][data-group=performance]').click(); pg.wait_for_timeout(200)
        rid = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].find(c => c.textContent.includes('1–2')).dataset.id")
        pg.click(f'[data-act=pool-edit][data-id="{rid}"]'); pg.wait_for_timeout(150)
        pg.on('dialog', lambda d: d.accept())
        pg.click('[data-act=pool-remove]'); pg.wait_for_timeout(300)
        print('5) Zeitraum aus dem Pool gelöscht → Matrix:', cells(pg)['performance'])
        ok5 = [c[0] for c in cells(pg)['performance']] == ['Performance 1 · 1980-06-16', 'Performance 2 · 1980-06-19']
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5], '| Fehler:', errs)
        b.close()


def case_trackpool():
    """Dates for some tracks (Discogs notes of Zooid – Cut You Where You Was): found dates are placed in the date
    matrix as suggestions with their track groups and studios; "Apply" splits the rows; applying again gives the
    same rows; removing a date and applying again brings the rows back together. [3.32.0] Without D022 (periods and
    "choose" as before)."""
    H.RULES_OFF = ['D022']  # [3.32.0] about the period and "choose": without D022 (what the days have in common at once)
    import re
    import zooid
    from common_rows import lib, cells, stage

    PW = sync_playwright().start()


    def run(notes, label):
        zooid.setup(notes)
        b = PW.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        return b, pg, errs

    # 1) two sessions, the second on two consecutive days
    b, pg, errs = run(zooid.NOTES_TWO_DAYS, 'zwei Tage')
    print('Meldung:', [m[:90] for m in pg.locator('.dci-msg').all_inner_texts()])
    print('Matrix (Vorschläge):', cells(pg)['performance'])
    print('Track-Pool:', pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
    before = lib(pg)
    pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(500)
    for n in ['Liberty Ellman', 'Henry Threadgill', 'Jose Davila', 'Brooklyn Recording', 'Scholes Street Studio']:
        print(f'  {n}:', lib(pg, n))
    want = sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '2025-06-23 – 2025-06-24')])
    ok1 = sorted(lib(pg)) == want and before == [([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], '')] \
        and lib(pg, 'Brooklyn') == [([1, 2, 3, 4, 5], '2025-06-25')] and lib(pg, 'Scholes') == [([6, 7, 8, 9, 10], '2025-06-23 – 2025-06-24')] \
        and lib(pg, 'Jose Davila') == [([6, 7, 8, 9, 10], '2025-06-23 – 2025-06-24')] and not any(c[2] for c in cells(pg)['performance'])
    # applying again gives the same rows (no further copies)
    pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
    ok1b = sorted(lib(pg)) == want
    print('Zweites „Anwenden“ unverändert:', ok1b)
    stage(pg)
    staged = pg.evaluate("""MB.relationshipEditor.state.added.filter(r => ['Liberty Ellman', 'Scholes Street Studio', 'Brooklyn Recording'].includes(r.entity0.name)).length""")
    print('Vorgemerkt (Liberty, Studios):', staged, '(erwartet 20)')
    # 1b) the second date goes: Liberty's rows come back together, the second part loses its date
    pg.locator('.dci-dm-col[data-dmcol=performance] .dci-dm-cell').nth(1).locator('[data-act=dm-remove]').first.click(); pg.wait_for_timeout(200)
    print('Hinweis nach Entfernen:', pg.locator('[data-el=dates] .dci-dm-pending').first.inner_text())
    pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
    print('Nach Entfernen von Performance 2 + Anwenden – Liberty:', lib(pg), '| Scholes:', lib(pg, 'Scholes'))
    ok1c = sorted(lib(pg)) == sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '')]) and lib(pg, 'Scholes') == [(list(range(1, 11)), '')]
    print('[zwei Tage] Ergebnis:', 'OK' if ok1 and ok1b and ok1c and staged == 20 else 'FEHLER', [ok1, ok1b, ok1c], '| Fehler:', errs)
    b.close()

    # 2) the second session on two separate days: the matrix asks ("choose"); single days → two rows per track
    b, pg, errs = run(zooid.NOTES_SEPARATE, 'getrennte Tage')
    print('Matrix:', cells(pg)['performance'], '| Wählen:', [re.sub(r'\s+', ' ', x) for x in pg.locator('.dci-dm-choose .dci-dm-opt').all_inner_texts()])
    print('Pool:', [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()])
    pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
    print('  vor der Wahl – Liberty:', lib(pg), '|', [m[:60] for m in pg.locator('.dci-msg').all_inner_texts() if 'choose' in m])
    ok2a = lib(pg) == [([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '')] and pg.locator('.dci-pchip-date').count() == 5
    pg.click('.dci-dm-choose [data-act=dm-choose][data-pick=single]'); pg.wait_for_timeout(200)
    print('  gewählt „einzeln“:', cells(pg)['performance'])
    pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
    print('  Liberty Ellman:', lib(pg))
    print('  Scholes Street Studio:', lib(pg, 'Scholes'))
    stage(pg)
    n_lib = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Liberty Ellman').length")
    print('[getrennte Tage] Liberty vorgemerkt:', n_lib, '(erwartet 15: 5 + 5×2) |', 'OK' if n_lib == 15 and ok2a else 'FEHLER', '| Fehler:', errs)
    b.close()

    # 3) "as single dates" for the consecutive days: the period's suggestion is replaced by two single dates
    b, pg, errs = run(zooid.NOTES_TWO_DAYS, 'einzelne Tage')
    pg.click('[data-el=datefind] summary')
    pg.locator('[data-el=datefind-list] li').nth(1).locator('[data-act=datefind-split]').click(); pg.wait_for_timeout(200)
    pg.locator('[data-el=datefind-list] li').nth(1).locator('[data-act=datefind-use][data-group=performance]').click(); pg.wait_for_timeout(300)
    m = cells(pg)['performance']
    print('Matrix:', m)
    print('Fundliste:', re.sub(r'\s+', ' ', pg.locator('[data-el=datefind-list] li').nth(1).inner_text())[:140])
    pg.locator('[data-act=dm-apply]').first.evaluate('b => b.click()'); pg.wait_for_timeout(400)
    print('  Liberty Ellman:', lib(pg))
    ok3 = len(m) == 3 and sorted(lib(pg)) == sorted([([1, 2, 3, 4, 5], '2025-06-25'), ([6, 7, 8, 9, 10], '2025-06-23'), ([6, 7, 8, 9, 10], '2025-06-24')])
    print('[einzelne Tage] Ergebnis:', 'OK' if ok3 else 'FEHLER', '| Fehler:', errs)
    b.close()
    PW.stop()


def case_reldate():
    """Import 3.10.0: a date of the date matrix only for the release level.
    The Discogs notes give two performance dates (the studio days in March, a release concert in June). In the column
    "Performance" the June date is marked "Release level". [3.32.0] Without D022 (the March period as before).
    A) Applied: the rows on recordings take only the March dates (no copy for June), a row on the release level takes June.
    B) A row switched from recording to the release level takes the June date at once; switched back, the March dates.
    C) A date typed into a row by hand stays when the row changes its level.
    D) The mark is stored with the matrix (after loading the dashboard again it is still there)."""
    H.RULES_OFF = ['D022']  # [3.32.0] about the period and "choose": without D022 (what the days have in common at once)
    from common_rows import rows_of

    # instruments on the release level exist in MusicBrainz too
    H.lt(44, '67555849-61e5-455b-96e3-29733f0115f5', 'instrument', 'artist', 'release', (14, 1, 194, 596))
    H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
    orig = H.discogs_release


    def release():
        d = orig()
        d['notes'] = 'Recorded March 1–3, 2001 at Abbey Road Studios. Recorded live at the release concert June 5, 2001.'
        return d


    H.discogs_release = release
    level = lambda pg, name, lv: pg.evaluate(f"""(() => {{ const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === '{name}');
  g.querySelector('tr.dci-row [data-act=level][data-level={lv}]').click(); }})()""")
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        cells = pg.evaluate("[...document.querySelectorAll('.dci-dm-col[data-dmcol=performance] .dci-dm-cell')].map(c => [c.dataset.id, c.querySelector('.dci-chip-main').textContent.trim()])")
        print('Spalte Performance:', cells)
        june = next(cid for cid, t in cells if '2001-06-05' in t)
        pg.check(f'[data-f=dm-rel][data-cell="{june}"]'); pg.wait_for_timeout(300)
        level(pg, 'Guitar Guy', 'release'); pg.wait_for_timeout(300)
        pg.locator('[data-el=dates] .dci-apply').first.evaluate('b => b.click()'); pg.wait_for_timeout(800)
        bass, guitar = rows_of(pg, 'Bass Man'), rows_of(pg, 'Guitar Guy')
        print('A) Bass Man:', bass, '| Guitar Guy (Release):', guitar)
        ok_a = bass == ['4 of 4 tracks | 2001-03-01 – 2001-03-03'] and guitar and guitar[0].endswith('| 2001-06-05')
        results.append(ok_a)
        # B) switching the level
        level(pg, 'Bass Man', 'release'); pg.wait_for_timeout(400)
        up = rows_of(pg, 'Bass Man')
        level(pg, 'Bass Man', 'recording'); pg.wait_for_timeout(400)
        back = rows_of(pg, 'Bass Man')
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'new level' in x]
        print('B) Bass Man → Release:', up, '| zurück:', back, '|', logs[-1:])
        ok_b = up and up[0].endswith('| 2001-06-05') and back == ['4 of 4 tracks | 2001-03-01 – 2001-03-03'] and len(logs) >= 2
        results.append(ok_b)
        # C) a date typed by hand stays
        g = pg.locator('section.dci-group').filter(has=pg.locator('.dci-gname strong', has_text='Keys Guy')).first
        g.locator('[data-act=date-edit]').first.click(); pg.wait_for_timeout(200)
        g.locator('[data-f=rd-by]').first.fill('1999'); g.locator('[data-f=rd-by]').first.dispatch_event('input'); pg.wait_for_timeout(200)
        level(pg, 'Keys Guy', 'release'); pg.wait_for_timeout(400)
        keys = rows_of(pg, 'Keys Guy')
        print('C) Keys Guy (eigenes Datum) → Release:', keys)
        ok_c = keys and keys[0].split(' | ')[1].startswith('1999')
        results.append(ok_c)
        # D) stored with the matrix, and still there after the dashboard was loaded again
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(500)
        stored = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-date-matrix:{H.REL}')).cells || []).filter(c => c.rel).map(c => c.date)")
        june_id = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}')) || []).filter(d => d.begin && d.begin.month === 6).map(d => d.id)")
        print('D) nach Neuladen als Release-Ebene markiert:', stored, '| Juni-Datum:', june_id)
        ok_d = len(stored) == 1 and stored[0] in june_id
        results.append(ok_d)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
