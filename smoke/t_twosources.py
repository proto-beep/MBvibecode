"""The box "Kraków 2018" (Barry Guy and Friends, five CDs; Discogs 25163152, Bandcamp, the back of the box): what two sources together give
(Credits Importer 3.233.0 ff.; the data and its target in smoke/data/krakow2018.json, the harness of it in krakow.py).

Cases: krakow3233 (3.233.0: the engineer's studio, tracks in short by media, live comments grouped and with their area, "Concept By,
Realization"), fast3234 (3.234.0: "⚡ Fast", the steps of the times named); `python3 t_twosources.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
H.NO_ANIM = True
from caserun import run_cases, sync_playwright  # noqa: E402
import krakow as K  # noqa: E402

# the comments of live recordings: their lines alone and their groups (position, text, ticked, notes)
LIVE_ALONE = """[...document.querySelectorAll('[data-el=livecom] tr[data-livecom]:not(.dci-livecom-sub)')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
  tr.querySelector('[data-f=livecom-text]').value.replace(/[‐‑]/g, '-'), tr.querySelector('[data-f=livecom-on]').checked, tr.lastElementChild.textContent.replace(/\\s+/g, ' ').trim()])"""
LIVE_GROUPS = """[...document.querySelectorAll('[data-el=livecom] tr[data-livecom-group]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
  tr.querySelector('[data-act=livecom-group]').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value.replace(/[‐‑]/g, '-'),
  tr.querySelector('[data-f=livecom-on]').checked, tr.lastElementChild.textContent.replace(/\\s+/g, ' ').trim(),
  tr.lastElementChild.querySelectorAll('.dci-livecom-warn').length])"""
# (0-based track sets → the short form of the tracks of a row)
SHORT = """(sets) => sets.map(s => window.__tracksShort({ level: 'recording', tracks: new Set(s) }))"""
SETS = [list(range(17)), [2, 3, 4, 5], list(range(16)), list(range(4, 12)) + [15, 16], [3] + list(range(12, 17)), [2, 3, 4, 5, 17], [0, 1], list(range(18))]


def _concept(rel):
    """Discogs: "Concept By, Realization – Hebert Cruz", "Concept By – Mario Burbano", "Realization – Lucia Martinez" (as Discogs 7627403 has
    them, split here to show each kind); Maya Homburger's baroque violin on 1-3 to 2-2 too (a run over the end of a medium)."""
    ex = lambda i, name, role: {'name': name, 'anv': '', 'join': '', 'role': role, 'tracks': '', 'id': i, 'resource_url': f'https://api.discogs.com/artists/{i}'}
    rel['extraartists'] += [ex(9101, 'Hebert Cruz', 'Concept By, Realization'), ex(9102, 'Mario Burbano', 'Concept By'), ex(9103, 'Lucia Martinez', 'Realization')]
    for t in rel['tracklist']:
        if t.get('position') in ('1-3', '1-4', '2-1', '2-2'):
            t['extraartists'] = t['extraartists'] + [ex(7011, 'Maya Homburger', 'Violin [Baroque Violin]')]


PEOPLE = {9101: ('Hebert Cruz', 'Hebert Cruz'), 9102: ('Mario Burbano', 'Mario Burbano'), 9103: ('Lucia Martinez', 'Lucía Martínez')}


def _run(p, off):
    """The CD imported (the release group Live), the live comments switched on: rows, ignored lines, the short tracks, the live comments."""
    K.setup('A', live=True, people=PEOPLE, discogs=_concept)
    H.RULES_OFF = list(off)
    b, pg, errs = K.open_import(p, 'A')
    pg.wait_for_timeout(800)
    if pg.evaluate("!!document.querySelector('[data-act=livecom-yes]')"):
        pg.click('[data-act=livecom-yes]')
    H.wait_for(pg, "!!document.querySelector('[data-el=livecom] tr[data-livecom], [data-el=livecom] tr[data-livecom-group]')", 30)
    H.wait_still(pg, "(document.querySelector('[data-el=livecom]') || {}).innerHTML", 15, 600)
    out = {'rows': pg.evaluate(K.ROWS), 'ign': pg.evaluate("((window.__S.release || {}).ignored || []).map(x => [x.text, x.why])"),
           'short': pg.evaluate(SHORT, SETS), 'alone': pg.evaluate(LIVE_ALONE), 'groups': pg.evaluate(LIVE_GROUPS),
           'q028': pg.evaluate("[...document.querySelectorAll('[data-question=Q028]')].length"), 'errs': errs}
    b.close()
    return out


def case_krakow3233():
    """Credits Importer 3.233.0 (collected items Z-ENGSTUDIO, Z-TRACKSMEDIA, Z-LIVECOMGROUP, Z-LIVECOMAREA, Z-CONCEPTREAL; rules S568 – S572): the CD of
    "Kraków 2018" with Discogs, its release group Live.
    A) S571: "Recorded, mixed and mastered by [...] (DTS Studio)" in the notes gives DTS Studio no "recorded at" (Discogs lists Alchemia and Radio
       Kraków "Recorded At"; listed as left out, "the studio of the engineer"); Discogs's "Recorded By – DTS Studio, Kraków" of a place is left out,
       said at the row; "Mixed At" and "Mastered At" stay; Alchemia on 1.1–4.5, Radio Kraków on 5.1.
    B) S568: tracks in short – "media 1–4", "tracks 1.3–2.2", "media 1–3, 4.1–4.4", "media 2–3, 4.4, 4.5", "1.4, medium 4", "1.3–2.2, medium 5",
       "tracks 1.1, 1.2", "all 18 tracks".
    C) Live comments: 1.1–4.5 one line "live, 2018-10: Alchemia Club, Kraków, Poland" (17 tracks; the place as the notes credit it), 5.1 its own. S571 off (DTS Studio recorded at too):
       S570 – both places in Kraków: "live, 2018-10: Kraków, Poland", the places said once at the line, ticked. S570 off too: S569 – the 17 tracks
       with "Different places …" still one line, the warning once.
    D) S572: "Concept By, Realization" one row – creative direction on the release group, credited "concept, realization"; "Concept By" credited
       "concept"; "Realization" alone asked (Q028).
    E) All five rules off: as until 3.232.0 – DTS Studio recorded at, "tracks 1.1–1.4, 2.1–2.4, …", every line with a note alone, "concept" a
       miscellaneous support and "Realization" a graphic design."""
    results = []
    with sync_playwright() as p:
        o = _run(p, [])
        rows = [r for r in o['rows'] if r['level'] != 'skip']
        dts = [(r['raw'], r['level'], r['notes']) for r in o['rows'] if r['company'] and r['name'].startswith('DTS')]
        places = {r['mb'] or r['name']: r['tracks'] for r in rows if r['company'] and r['raw'] == 'Recorded At'}
        print('A)', dts, places, [x for x in o['ign'] if x[1] == 'engStudio'])
        results.append(not any(x[0] == 'Recorded At' and x[1] != 'skip' for x in dts) and ('Recorded By', 'skip', ['engStudio']) in [(a, b, c) for a, b, c in dts]
                       and any(x[0] == 'Mixed At' and x[1] != 'skip' for x in dts) and any(x[0] == 'Mastered At' and x[1] != 'skip' for x in dts)
                       and places.get('Alchemia') == list(range(1, 18)) and places.get('Radio Kraków SA.') == [18]
                       and any(x[1] == 'engStudio' and 'DTS Studio' in x[0] for x in o['ign']))
        print('B)', o['short'])
        results.append(o['short'] == ['media 1–4', 'tracks 1.3–2.2', 'media 1–3, 4.1–4.4', 'media 2–3, 4.4, 4.5', '1.4, medium 4', '1.3–2.2, medium 5',
                                      'tracks 1.1, 1.2', 'all 18 tracks'])
        print('C)', o['groups'], o['alone'])
        g = o['groups']
        results.append(len(g) == 1 and g[0][1] == '▸ 17 tracks' and g[0][2] == 'live, 2018-10: Alchemia Club, Kraków, Poland' and g[0][3] is True
                       and [x[1] for x in o['alone']] == ['live, 2018-10-13: Radio Kraków, Kraków, Poland'])
        cd = {r['name']: [(x['types'][:1], x['level'], x['credit']) for x in o['rows'] if x['name'] == r['name'] and x['level'] != 'skip']
              for r in o['rows'] if r['name'] in ('Hebert Cruz', 'Mario Burbano', 'Lucia Martinez')}
        print('D)', cd, 'Q028:', o['q028'])
        results.append(cd.get('Hebert Cruz') == [(['creative direction'], 'release_group', 'concept, realization')]
                       and cd.get('Mario Burbano') == [(['creative direction'], 'release_group', 'concept')]
                       and len(cd.get('Lucia Martinez') or []) == 1 and cd['Lucia Martinez'][0][0] == [] and o['q028'] >= 1)
        results.append(not o['errs'])
        o2 = _run(p, ['S571'])
        g2 = o2['groups']
        print('C) S571 off:', g2, o2['alone'])
        results.append(len(g2) == 1 and g2[0][1] == '▸ 17 tracks' and g2[0][2] == 'live, 2018-10: Kraków, Poland' and g2[0][3] is True
                       and 'Places in the same area: ' in g2[0][4] and g2[0][4].count('Places in the same area') == 1
                       and [x[1] for x in o2['alone']] == ['live, 2018-10-13: Kraków, Poland'])
        o3 = _run(p, ['S571', 'S570'])
        g3 = o3['groups']
        print('C) S571, S570 off:', g3, o3['alone'])
        results.append(len(g3) == 1 and g3[0][1] == '▸ 17 tracks' and g3[0][3] is False and g3[0][5] == 1 and g3[0][4].count('Different places') == 1)
        o4 = _run(p, ['S568', 'S569', 'S570', 'S571', 'S572'])
        dts4 = [(r['raw'], r['level']) for r in o4['rows'] if r['company'] and r['name'].startswith('DTS') and r['level'] != 'skip']
        cd4 = sorted((x['types'][:1], x['credit']) for x in o4['rows'] if x['name'] == 'Hebert Cruz' and x['level'] != 'skip')
        print('E)', dts4, o4['short'][:2], len(o4['groups']), len(o4['alone']), cd4)
        results.append(('Recorded At', 'recording') in dts4 and o4['short'][0] == 'tracks 1.1–1.4, 2.1–2.4, 3.1–3.4, 4.1–4.5' and o4['short'][1] == 'tracks 1.3, 1.4, 2.1, 2.2'
                       and not o4['groups'] and len(o4['alone']) == 18 and cd4 == [(['graphic design'], 'realization'), (['misc'], 'concept')])
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_fast3234():
    """Credits Importer 3.234.0 (collected items Z-FASTMODE, Z-TIMINGNAMES2; rules S573, S574): the CD of "Kraków 2018" (its release group Live, the
    live comments on).
    A) "⚡ Fast" on (stored before): the log says what is left out; no works on the artists' pages read (no browse of works or recordings), no
       missing links looked up, no sources of other releases; the works matrix says so with "Read them now"; the works of the writers are still
       searched; "More" of the head shows ⚡ Fast pressed, ⚙ Settings → General ticked.
    B) "Read them now": the works of the artists are read (browses), the line goes.
    C) The times of the import name every step (no "?"; "areas of the live comments"), "⚡ fast" at the end.
    D) ⚡ Fast off in "More": stored as off; the missing links are looked up now.
    E) Without the switch stored: an import reads the artists' works at once (as until 3.233.0)."""
    results = []
    INIT = "if (!localStorage.getItem('dci-store-epoch')) localStorage.setItem('dci-store-epoch', '4'); if (localStorage.getItem('dci-fast') === null && !sessionStorage.getItem('dci-t')) { localStorage.setItem('dci-fast', 'true'); sessionStorage.setItem('dci-t', '1'); }"
    with sync_playwright() as p:
        K.setup('A', live=True)
        H.BROWSES.clear()
        b, pg, errs = K.open_import(p, 'A', init=INIT)
        if pg.evaluate("!!document.querySelector('[data-act=livecom-yes]')"):
            pg.click('[data-act=livecom-yes]')
        pg.wait_for_timeout(4000)
        lg = pg.evaluate(K.LOG)
        line = pg.evaluate("(document.querySelector('[data-el=aw-line]') || {textContent: ''}).textContent.trim()")
        more = pg.evaluate("(document.querySelector('#dci-overlay [data-act=fast-mode]') || {}).getAttribute ? document.querySelector('#dci-overlay [data-act=fast-mode]').getAttribute('aria-pressed') : null")
        H.open_settings(pg, 'general')
        box = pg.evaluate("(document.querySelector('[data-set=fast-mode]') || {}).checked")
        timing = [x for x in lg if 'Times of this import' in x]
        print('A)', [x for x in lg if 'Fast' in x], '| line:', line, '| More:', more, box, '| browses:', len(H.BROWSES))
        results.append(any('⚡ Fast: left out' in x for x in lg) and len(H.BROWSES) == 0 and 'Read them now' in line and more == 'true' and box is True
                       and not any('missing links' in x for x in timing) and not any('other releases of the group' in x for x in timing)
                       and any('works of the writers' in x or 'Work search' in x for x in lg))
        pg.click('[data-el=aw-line] [data-act=mx-aw-fast]')
        H.wait_for(pg, f"{len(H.BROWSES)} < 0 || [...document.querySelectorAll('#dci-log li')].some(li => /read now/.test(li.textContent))", 20)
        pg.wait_for_timeout(3000)
        line2 = pg.evaluate("(document.querySelector('[data-el=aw-line]') || {textContent: ''}).textContent.trim()")
        print('B) browses:', len(H.BROWSES), '| line:', line2)
        results.append(len(H.BROWSES) > 0 and 'Read them now' not in line2)
        lg = pg.evaluate(K.LOG)
        timing = [x for x in lg if 'Times of this import' in x]
        print('C)', timing[-1][:400] if timing else None)
        results.append(bool(timing) and ' ? ' not in timing[-1] and '; ?' not in timing[-1] and timing[-1].rstrip().endswith('⚡ fast') and 'areas of the live comments' in timing[-1])
        pg.evaluate("document.querySelector('#dci-overlay [data-act=head-more]').click()")
        pg.wait_for_timeout(200)
        pg.evaluate("document.querySelector('#dci-overlay [data-act=fast-mode]').click()")
        pg.wait_for_timeout(3000)
        st = pg.evaluate("localStorage.getItem('dci-fast')")
        lg = pg.evaluate(K.LOG)
        print('D) stored:', st, [x for x in lg if 'Fast import' in x][-1:])
        results.append(st is None and any('⚡ Fast import' in x and 'off' in x for x in lg))
        results.append(not errs)
        b.close()
        H.BROWSES.clear()
        b, pg, errs = K.open_import(p, 'A')
        pg.wait_for_timeout(3000)
        lg = pg.evaluate(K.LOG)
        print('E) browses:', len(H.BROWSES), [x for x in lg if 'Fast' in x])
        results.append(len(H.BROWSES) > 0 and not any('⚡ Fast: left out' in x for x in lg))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
