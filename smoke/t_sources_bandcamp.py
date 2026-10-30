"""Bandcamp: as a source, the "about" text, leaving it out, liner notes, label pages, track pages (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: bandcamp, about, aboutoff, linernotes, labelpage, bctrack, aboutcredits (3.32.6) – each the former smoke/t_<case>.py, unchanged; `python3 t_sources_bandcamp.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_bandcamp():
    """Import 3.3.0 (E2): Bandcamp as a source, and the order of the sources.
    A) Physical media: Discogs comes first in the list, so Discogs is loaded; the picker offers both linked sources.
    B) Bandcamp chosen in the picker: the album page is read through GM_xmlhttpRequest (data-tralbum), its credits as a
       text (E1), the credits of each track page for their track only; the band's name links to its Bandcamp page and is
       assigned because MusicBrainz spells it the same; a line without credits is listed. The choice is remembered for
       this release (loaded again after a reload). The edit note names the album.
    C) Digital media: Bandcamp first by default; moving Discogs up in the list for digital media loads Discogs after a
       reload (no choice remembered for this release in a new browser profile).
    D) The Bandcamp menu: without the track pages, their credits are not read; "Test page" says what it found.
    E) A band that is not in the release's artist credit is only suggested (rule 4).
    F) Import 3.3.1: the spelling is compared with the release's artist credit (below its title), not with the name of the MB
       artist: "The Test Band" in MusicBrainz, credited "Test Band" on the release → assigned; credited "TEST BAND" → only a
       suggestion, which says how the release names it. Import 3.5.0: the entry shows the three spellings (Bandcamp, the
       release's artist credit, MusicBrainz), those that differ marked."""
    import json
    import re

    H.attr(9120, 'trumpet', 14, 14)
    H.attr(9121, 'viola', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    ALBUM = 'https://testband.bandcamp.com/album/testalbum'
    BAND = 'https://testband.bandcamp.com/'
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND] = H.ARTISTS[3040]
    H.BC_ARTISTS['https://strictband.bandcamp.com/'] = (H.uid('dddddddd', 41), 'StrictBand')
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]


    def album(band, credits, about=''):
        return {'artist': band, 'current': {'title': 'Testalbum', 'credits': credits, 'about': about, 'release_date': '01 Jan 2020 00:00:00 GMT'},
                'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]}


    H.BC_PAGES[ALBUM] = H.bc_page(album('Test Band', 'Test Band – guitar\nMixed by Jane Roe\nTrumpet: Peter Evans\nThanks Mom.'))
    for i, t in enumerate(H.TITLES):
        H.BC_PAGES[f'https://testband.bandcamp.com/track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': 'Viola: Anna Viola' if i == 1 else ''}})
    H.BC_PAGES['https://strictband.bandcamp.com/album/x'] = H.bc_page(album('Strict Band', 'Strict Band – trumpet'))
    DIGITAL = {'on': False}
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM + '?from=embed'}})
        if DIGITAL['on']:
            for m in d['media']:
                m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [g.className.match(/dci-st-(\\w+)/)[1], [...g.querySelectorAll('tr.dci-row')].map(tr => tr.querySelector('.dci-drole').textContent.trim() + ' · ' + ((tr.querySelector('[data-tcount]') || {}).textContent || '').trim()),
   // 3.15.2: the name of a suggestion without its mark ("spelled differently")
   [...g.querySelectorAll('[data-act=name-use]')].map(b => [...b.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim())]])))()"""
    done = lambda pg, n: H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= {n}", 90)
    SPELL = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Test Band');
  const sp = g && g.querySelector('.dci-spell'); return sp ? [sp.textContent.replace(/\\s+/g, ' ').trim(), sp.classList.contains('dci-spell-diff'),
  [...sp.querySelectorAll('.dci-spell-x')].map(x => x.textContent.trim())] : null; })()"""
    source = lambda pg: pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 90)")
    results = []


    def fresh(pw, digital=False):
        DIGITAL['on'] = digital
        b = pw.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        return b, ctx, pg, errs


    def reopen(pg):
        pg.evaluate("Object.keys(sessionStorage).filter(k => k.startsWith('dci-')).forEach(k => sessionStorage.removeItem(k))")
        pg.reload()
        pg.add_script_tag(content=H.GM_XHR_SHIM)
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        done(pg, 1)
        pg.wait_for_timeout(500)


    with sync_playwright() as p:
        # A) physical media: Discogs first
        b, ctx, pg, errs = fresh(p)
        H.open_dashboard(pg)
        opts = pg.evaluate("[...document.querySelectorAll('[data-f=discogs-pick] option')].map(o => o.textContent.trim())")
        print('A) Quelle:', source(pg), '| Auswahl:', opts)
        ok_a = 'Discogs 1234' in source(pg) and opts[1:] == ['Discogs 1234', 'Bandcamp testband.bandcamp.com/album/testalbum']
        results.append(ok_a)

        # B) Bandcamp chosen
        H.src_menu(pg)
        pg.select_option('[data-f=discogs-pick]', f'bandcamp|{ALBUM}')
        done(pg, 2)
        pg.wait_for_timeout(800)
        g = pg.evaluate(GROUPS)
        calls = pg.evaluate('window.__gmXhr')
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        # [3.21.0] thanks: listed apart as left out on purpose
        unrec += ['ignored: ' + x for x in pg.evaluate("[...document.querySelectorAll('.dci-ignored li .dci-ign-text')].map(li => li.textContent)")]
        print('B) Quelle:', source(pg), '| Abrufe:', len(calls), calls[:2])
        for k, v in g.items():
            print('   ', k, v)
        print('   nicht erkannt:', unrec)
        ok_b = 'Testalbum (Bandcamp)' in source(pg) and calls[0] == ALBUM and len(calls) == 5 \
            and g['Test Band'][0] == 'linked' and g['Test Band'][1] == ['guitar · 4 of 4 tracks'] \
            and g['Jane Roe'][1] == ['Mixed By · 4 of 4 tracks'] and g['Peter Evans'][1] == ['Trumpet · 4 of 4 tracks'] \
            and g['Anna Viola'][1] == ['Viola · 1 of 4 tracks'] and unrec == ['ignored: Thanks Mom.']
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        note = pg.evaluate("document.getElementById('edit-note-text').value")
        print('   Notiz:', [l for l in note.splitlines() if l.startswith('Source') or 'from Bandcamp' in l])
        ok_b = ok_b and f'Source: {ALBUM}' in note.splitlines() and any('from Bandcamp (' in l for l in note.splitlines())
        reopen(pg)
        kept = [x for x in pg.locator('#dci-log li').all_inner_texts() if 'chosen for this release' in x]
        print('   nach Neuladen:', source(pg), '|', kept[-1:])
        ok_b = ok_b and 'Testalbum (Bandcamp)' in source(pg) and bool(kept)
        results.append(ok_b)
        b.close()

        # C) digital media: Bandcamp first; Discogs moved up for digital media
        b, ctx, pg, errs2 = fresh(p, digital=True)
        H.open_dashboard(pg)
        first = source(pg)
        H.src_menu(pg, 'srcorder-toggle'); pg.wait_for_timeout(200)
        lists = pg.evaluate("[...document.querySelectorAll('[data-srcorder]')].map(ol => [ol.dataset.srcorder, [...ol.querySelectorAll('li')].map(li => li.dataset.id), ol.closest('.dci-srcorder-col').querySelector('strong').textContent.trim()])")
        pg.click('[data-act=srcorder-move][data-list=digital][data-src=discogs][data-dir="-1"]'); pg.wait_for_timeout(200)
        stored = pg.evaluate("JSON.parse(localStorage.getItem('dci-source-order'))")
        reopen(pg)
        print('C) digital zuerst:', first, '| Listen:', lists, '| gespeichert:', stored, '| danach:', source(pg))
        ok_c = 'Testalbum (Bandcamp)' in first and lists[0][1] == ['discogs', 'bandcamp'] and lists[1][1] == ['bandcamp', 'discogs'] \
            and '(this release)' in lists[1][2] and stored['digital'] == ['discogs', 'bandcamp'] and 'Discogs 1234' in source(pg)
        results.append(ok_c)

        # D) the Bandcamp menu: no track pages; the page test
        H.src_menu(pg, 'bc-toggle'); pg.wait_for_timeout(200)
        pg.uncheck('[data-f=bc-tracks]'); pg.wait_for_timeout(100)
        pg.fill('[data-f=bc-test-url]', ALBUM + '?x=1')
        pg.click('[data-act=bc-test]')
        pg.wait_for_selector('[data-bc-result]:not(:empty)', timeout=10000)
        pg.wait_for_function("!/Loading/.test(document.querySelector('[data-bc-result]').textContent)", timeout=10000)
        test = pg.locator('[data-bc-result]').inner_text()
        H.src_menu(pg)
        pg.select_option('[data-f=discogs-pick]', f'bandcamp|{ALBUM}')
        done(pg, 2)
        pg.wait_for_timeout(500)
        g = pg.evaluate(GROUPS)
        print('D) Test:', test, '| ohne Track-Seiten:', 'Anna Viola' in g, '| gespeichert:', pg.evaluate("localStorage.getItem('dci-bc-tracks')"))
        ok_d = test.startswith('Read: “Testalbum”, 4 tracks, 4 lines of credits, 4 track pages (via GM_xmlhttpRequest)') and 'Anna Viola' not in g \
            and 'Test Band' in g and pg.evaluate("localStorage.getItem('dci-bc-tracks')") == 'false'
        results.append(ok_d)

        # E) a band spelled differently in MusicBrainz: only a suggestion
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', 'https://strictband.bandcamp.com/album/x')
        pg.click('[data-act=discogs-load]')
        done(pg, 3)
        pg.wait_for_timeout(500)
        g = pg.evaluate(GROUPS)
        log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'names it differently in its artist credit' in x]
        print('E) Strict Band:', g.get('Strict Band'), '|', log[-1:])
        ok_e = g.get('Strict Band', [''])[0] == 'missing' and g['Strict Band'][2] == ['StrictBand'] and bool(log)
        results.append(ok_e)

        # F) the spelling as the release names it (artist credit), not as MusicBrainz names the artist
        gid = H.ARTISTS[3040][0]
        H.BC_ARTISTS[BAND] = (gid, 'The Test Band')
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', ALBUM)
        pg.click('[data-act=discogs-load]')
        done(pg, 4)
        pg.wait_for_timeout(500)
        g1 = pg.evaluate(GROUPS).get('Test Band')
        spell = pg.evaluate(SPELL)
        H.RELEASE_AC[:] = [(gid, 'The Test Band', 'TEST BAND', '')]
        reopen(pg)
        g2 = pg.evaluate(GROUPS).get('Test Band')
        head = pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent === 'Test Band').map(g => [(g.querySelector('.dci-sugg-stack') || {}).title, [...g.querySelectorAll('.dci-sugg-stack .dci-similar')].map(x => x.textContent)])[0]")
        log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'names it differently in its artist credit' in x]
        print('F) MB „The Test Band“, Release „Test Band“:', g1, '| Release „TEST BAND“:', g2, '|', head, '|', log[-1:])
        spell2 = pg.evaluate(SPELL)
        print('   Schreibweise:', spell, '|', spell2)
        ok_f = spell and spell[1] and 'Bandcamp “Test Band” · release (artist credit) “Test Band” · MusicBrainz “The Test Band”' in spell[0] \
            and spell[2] == ['“The Test Band”'] and spell2 and '“TEST BAND”' in spell2[0] and spell2[2] == ['“TEST BAND”', '“The Test Band”']
        ok_f = ok_f and g1[0] == 'linked' and g2[0] == 'missing' and g2[2] == ['The Test Band'] and 'TEST BAND' in (head or ['', []])[0] and 'spelled differently' in (head or ['', []])[1] and any('(TEST BAND)' in x for x in log)
        results.append(ok_f)
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_about():
    """Import 3.7.0: the "about" text of a Bandcamp album: "recorded at Loft in Cologne, june 16/17 2018".
    A) The place: an entry "Loft" (Cologne) with "Recorded At"; MusicBrainz places of that name are suggested only in
       that area (a "Loft" in New York is not); the about text's prose is not read as credits and not listed as not
       recognized.
    B) The date: "june 16/17 2018" (and "16/17 June 2018") – two days in a row, in the date pool as a period
       (2018-06-16 – 2018-06-17), which can be split into the single days as with "June 16 & 17, 2018".
    C) "Loft, Cologne" in the credits works the same way.
    D) A private place is no place: "mixed at home in Oslo" gives no entry "home" (and is not listed as not recognized).
    E) What follows "at" without being a place gives no entry either (3.13.1): "recorded at the same time as the video",
       "overdubs at last, in the summer of 2018"."""
    ALBUM = 'https://testband.bandcamp.com/album/swift'
    H.MB_SEARCH['place'] = [
        {'id': H.uid('eeeeeeee', 60), 'name': 'Loft', 'disambiguation': '', 'area': {'name': 'Cologne'}, 'score': 100},
        {'id': H.uid('eeeeeeee', 61), 'name': 'The Loft', 'disambiguation': '', 'area': {'name': 'New York'}, 'score': 100},
        {'id': H.uid('eeeeeeee', 62), 'name': 'Loft', 'disambiguation': 'club', 'area': {'name': 'New York'}, 'score': 100},
        {'id': H.uid('eeeeeeee', 63), 'name': 'Studio Nord', 'disambiguation': '', 'area': {'name': 'Bremen'}, 'score': 100},
    ]
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {
        'title': 'Swift', 'credits': 'Bass Man – bass\nMastered at Studio Nord, Bremen',
        'about': 'An evening of improvised music, three friends, one room.\nrecorded at Loft in Cologne, june 16/17 2018\nmixed at home in Oslo, july 2018\nrecorded at the same time as the video\noverdubs recorded at last, in the summer of 2018'},
        'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  [[...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim()), [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim())]])))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1000)
        g = pg.evaluate(GROUPS)
        unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
        stored = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, JSON.stringify(d.begin), JSON.stringify(d.end)].join(' '))")
        for k, v in g.items():
            print('   ', k, v)
        print('   nicht erkannt:', unrec, '| Pool:', stored)
        loft = next((v for k, v in g.items() if k.startswith('Place Loft') or 'Loft (Cologne)' in k), None)
        nord = next((v for k, v in g.items() if 'Studio Nord (Bremen)' in k), None)
        ok_a = loft is not None and loft[0] == ['Recorded At'] and loft[1] == ['Loft (Cologne) – place'] and not unrec
        ok_b = any('{"year":2018,"month":6,"day":16} {"year":2018,"month":6,"day":17}' in s for s in stored)
        ok_c = nord is not None and nord[0] == ['Mastered At'] and nord[1] == ['Studio Nord (Bremen) – place']
        ok_d = not any('home' in k.lower() for k in g)
        ok_e = not any(w in k.lower() for k in g for w in ('same time', 'last'))
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| D)', ok_d, '| E)', ok_e)
        results += [ok_a, ok_b, ok_c, ok_d, ok_e]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_aboutoff():
    """Import 3.16.1: "Leave out the “about” text" (Bandcamp, per release, at once, without a new import).
    The credits name "Mastered at Studio Nord, Bremen, March 2019"; the "about" text "recorded at Loft in Cologne, june 16/17
    2018".
    A) The checkbox stands next to "Delete stored import …" (a Bandcamp release with an "about" text).
    B) Ticked: the entry "Loft" (from the about text) is hidden, "Studio Nord" (credits) stays; the June dates leave the pool,
       March 2019 stays; the log says so; stored for the release.
    C) Ticked off again: "Loft" is back with what was changed in it ("credited as" typed before), the June dates are back.
    D) Kept for the release: ticked, the page loaded again – the box is ticked, "Loft" hidden, no June date in the pool.
    E) "Delete stored import" sets it back."""
    import json

    ALBUM = 'https://testband.bandcamp.com/album/swift'
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {
        'title': 'Swift', 'credits': 'Bass Man – bass\nMastered at Studio Nord, Bremen, March 2019',
        'about': 'An evening of improvised music.\nrecorded at Loft in Cologne, june 16/17 2018'},
        'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    STATE = f"""(() => {{ const vis = (re) => [...document.querySelectorAll('section.dci-group')].filter(g => re.test(g.querySelector('.dci-gname').textContent))
    .map(g => getComputedStyle(g).display !== 'none');
  const pool = JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => JSON.stringify(d.begin));
  const box = document.querySelector('[data-f=about-off]');
  return {{ box: box ? box.checked : null, loft: vis(/Loft/), nord: vis(/Studio Nord/), june: pool.some(x => /"month":6/.test(x)), march: pool.some(x => /"year":2019,"month":3/.test(x)),
    stored: localStorage.getItem('dci-about-off:{H.REL}') !== null }}; }})()"""
    results = []


    def imported(pg, n):
        H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= {n}", 90)
        pg.wait_for_timeout(1200)


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        imported(pg, 1)
        s0 = pg.evaluate(STATE)
        near = pg.evaluate("(() => { const f = document.querySelector('[data-act=forget-open]'); const l = document.querySelector('[data-f=about-off]'); return !!(f && l && f.parentElement === l.closest('label').parentElement); })()")
        print('A)', s0, '| neben „Delete stored import“:', near)
        results.append(s0['box'] is False and s0['loft'] == [True] and s0['june'] and s0['march'] and near)
        # a change in the Loft row
        loft_credit = "[...document.querySelectorAll('section.dci-group')].find(g => /Loft/.test(g.querySelector('.dci-gname').textContent)).querySelector('tr.dci-row [data-f=credit]')"
        pg.evaluate(f"(() => {{ const i = {loft_credit}; i.value = 'The Loft'; i.dispatchEvent(new Event('input', {{ bubbles: true }})); i.dispatchEvent(new Event('change', {{ bubbles: true }})); }})()")
        pg.wait_for_timeout(300)
        # B) ticked
        H.src_menu(pg)
        pg.locator('[data-f=about-off]').check(); pg.wait_for_timeout(600)
        s1 = pg.evaluate(STATE)
        log = [x for x in pg.evaluate(LOGS) if '“about” text' in x]
        print('B)', s1, '|', log)
        results.append(s1['box'] is True and s1['loft'] == [False] and s1['nord'] == [True] and not s1['june'] and s1['march'] and s1['stored']
                       and log and log[-1] == '“about” text left out (rows hidden: 1, dates out of the pool: 2)')
        # C) off again: back, with the change
        H.src_menu(pg)
        pg.locator('[data-f=about-off]').uncheck(); pg.wait_for_timeout(600)
        s2 = pg.evaluate(STATE)
        kept = pg.evaluate(f"{loft_credit}.value")
        log = [x for x in pg.evaluate(LOGS) if '“about” text' in x]
        print('C)', s2, '| „credited as“:', kept, '|', log[-1:])
        results.append(s2['box'] is False and s2['loft'] == [True] and s2['june'] and not s2['stored'] and kept == 'The Loft' and log[-1] == '“about” text taken in again (rows back: 1, dates back: 2)')
        # D) kept for the release
        H.src_menu(pg)
        pg.locator('[data-f=about-off]').check(); pg.wait_for_timeout(600)
        pg.reload(); pg.add_script_tag(content=H.GM_XHR_SHIM); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.click('#dci-open')
        imported(pg, 2)
        s3 = pg.evaluate(STATE)
        print('D) nach Neuladen:', s3)
        results.append(s3['box'] is True and s3['loft'] == [False] and not s3['june'] and s3['march'])
        # E) "Delete stored import" sets it back
        H.src_menu(pg, 'forget-open')
        pg.click('[data-act=forget-do]')
        imported(pg, 1)  # the log of the release starts anew
        s4 = pg.evaluate(STATE)
        print('E) nach „Delete stored import“:', s4)
        results.append(s4['box'] is False and s4['loft'] == [True] and s4['june'] and not s4['stored'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_linernotes():
    """Credits Importer 3.17.2: liner notes in Bandcamp's "about" text (collected item 19).
    A) In Node (BANDCAMP.linerNotes): prose of at least five sentences (over several paragraphs) and a name below it – after
       an empty line ("— Jane Roe, Berlin, May 2019"), on the line right below ("Jane Roe"), or at the end of the last line
       after a sign ("… our music. ~ Jane Roe") – gives the name; four sentences, a last line that is no name ("Special
       thanks", "Thanks to everyone"), a name after a sign without a finished sentence before it, and the "about" text of
       "Invisible Places" give nothing.
    B) In the dashboard: an entry "Jane Roe" with the row "Liner Notes" (liner notes, release level) that says "From the
       “about” text"; MusicBrainz artists of that name only as suggestions (nothing assigned); the date by the name in the
       date pool as a suggestion named for the liner notes.
    C) "Leave out the about text": the row hidden and the date out of the pool; ticked off again, both back.
    D) With the companion: the row jumps to the name's line in the "about" text (only that sentence, no mark).
    E) 3.17.6: the liner notes row shows that date as a suggestion (dashed, yellow) in its date cell; ✓ takes it."""
    import json
    import subprocess

    PROSE = ('This record was a long time coming. We met in a cold basement in the winter of 2017. The songs grew slowly, '
             'one evening at a time.\n\nNone of us knew where it would lead. But every take taught us something new.\n'
             'Listen to it loud, and listen to it twice.')
    REAL = ('The music on this album was recorded in September and October 2026. It is an approach to ambient music with a more '
            'meditative and “earthty” character. The music originally appeared in Home Concert 85, but was re-recorded with attention '
            'to detail, dynamic mixing and sound design.\nThe last track, “Neptune’s Dream”, was previously released as a '
            'digital-only single and was remastered for this release.')
    CASES = {
        'blank line': PROSE + '\n\n— Jane Roe, Berlin, May 2019',
        'line below': PROSE + '\nJane Roe',
        'end of line': PROSE[:-1] + '. ~ Jane Roe',
        'four sentences': 'One two three. Four five six. Seven eight nine. Ten eleven twelve.\n\nJane Roe',
        'special thanks': PROSE + '\n\nSpecial Thanks',
        'thanks to everyone': PROSE + '\n\nThanks to everyone',
        'no sentence before': PROSE + ' And the last one – Neptune Dream',
        'invisible places': REAL,
    }
    NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const cases = JSON.parse(process.argv[2]);
const out = {};
for (const [k, text] of Object.entries(cases)) {
  const r = m.SOURCES.bandcamp.linerNotes(text);
  out[k] = r ? [r.name, r.line, r.part, r.pi] : null;
}
console.log(JSON.stringify(out));
"""
    results = []
    js = subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), json.dumps(CASES)], capture_output=True, text=True)
    if js.returncode:
        print(js.stderr[-1500:])
    got = json.loads(js.stdout) if not js.returncode else {}
    for k, v in got.items():
        print(f'A) {k}:', v)
    results.append(got.get('blank line') == ['Jane Roe', '— Jane Roe, Berlin, May 2019', '— Jane Roe, Berlin, May 2019', 0]
                   and got.get('line below') == ['Jane Roe', 'Jane Roe', 'Jane Roe', 0]
                   and got.get('end of line') == ['Jane Roe', 'Listen to it loud, and listen to it twice. ~ Jane Roe', 'Jane Roe', 1]
                   and all(got.get(k) is None for k in ['four sentences', 'special thanks', 'thanks to everyone', 'no sentence before', 'invisible places']))

    BAND = 'https://testband.bandcamp.com'
    ALBUM = f'{BAND}/album/testalbum'
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
    H.MB_SEARCH.setdefault('artist', []).append({'id': H.uid('dddddddd', 77), 'name': 'Jane Roe', 'aliases': []})
    TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
    H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'Test Band – guitar', 'about': CASES['blank line']},
                                   'trackinfo': TRACKS}, ALBUM)
    for t in TRACKS:
        H.BC_PAGES[f'{BAND}{t["title_link"]}'] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                                            'trackinfo': [t]}, f'{BAND}{t["title_link"]}')
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    ENTRY = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Jane Roe');
  if (!g) return null; const tr = g.querySelector('tr.dci-row'); const lv = tr && tr.querySelector('[data-act=level][aria-pressed=true]');
  return [g.className.match(/dci-st-(\\w+)/)[1], tr ? tr.querySelector('.dci-drole').textContent.trim() : '', tr ? (tr.querySelector('[data-f=type]') || {}).value : '',
    lv ? lv.dataset.level : '', [...g.querySelectorAll('.dci-sub')].map(x => x.textContent.trim()).filter(t => /about/.test(t)),
    [...g.querySelectorAll('[data-act=name-use]')].length, !!(tr && tr.offsetParent)]; })()"""
    POOL = f"JSON.parse(localStorage.getItem('dci-date-pool:{H.REL}') || '[]').map(d => [d.name, d.begin && [d.begin.year, d.begin.month]])"


    def poll(pg, js, timeout=20):
        for _ in range(timeout * 5):
            try:
                if pg.evaluate(js):
                    return True
            except Exception:
                pass
            pg.wait_for_timeout(200)
        raise TimeoutError(js)


    real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        bc, bcerr = H.open_bandcamp(ctx, ALBUM)
        pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        pg.wait_for_timeout(1500)
        b1 = pg.evaluate(ENTRY)
        pool = pg.evaluate(POOL)
        print('B) Eintrag:', b1, '| Pool:', pool)
        results.append(b1 is not None and b1[1] == 'Liner Notes' and b1[3] == 'release' and b1[4] == ['From the “about” text'] and b1[5] >= 1
                       and b1[0] != 'linked' and ['Liner notes – Jane Roe', [2019, 5]] in pool)
        # D) the jump: the sentence with the name, no mark in the about text
        rid = pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Jane Roe'); return g.querySelector('tr.dci-row').dataset.row; })()")
        pg.locator(f'tr[data-row="{rid}"] .dci-drole').click()
        poll(bc, "!!document.querySelector('.dci-bc-hl')")
        bc.wait_for_timeout(300)
        d1 = [bc.evaluate("[...document.querySelectorAll('.dci-bc-hl')].map(x => x.textContent).join('')"), bc.evaluate("document.querySelectorAll('.tralbum-about .dci-dg-mark').length")]
        print('D) Sprung:', d1)
        results.append(d1 == ['— Jane Roe, Berlin, May 2019', 0])
        # C) leave out the about text
        H.src_menu(pg)
        pg.locator('[data-f=about-off]').check()
        pg.wait_for_timeout(800)
        c1 = [pg.evaluate(ENTRY), pg.evaluate(POOL)]
        H.src_menu(pg)
        pg.locator('[data-f=about-off]').uncheck()
        pg.wait_for_timeout(800)
        c2 = [pg.evaluate(ENTRY), pg.evaluate(POOL)]
        print('C) ausgelassen:', c1, '| wieder da:', c2)
        results.append((c1[0] is None or not c1[0][6] or c1[0][3] == 'skip') and not any(n == 'Liner notes – Jane Roe' for n, _ in c1[1])
                       and c2[0] is not None and c2[0][3] == 'release' and ['Liner notes – Jane Roe', [2019, 5]] in c2[1])
        # E) the date as a suggestion at the row; ✓ takes it
        SUGG = f"""(() => {{ const tr = document.querySelector('tr[data-row="{rid}"]'); const c = tr && tr.querySelector('.dci-datechip-sugg');
      const d = tr && tr.querySelector('.dci-datechip:not(.dci-datechip-sugg)'); return [c ? c.textContent.replace(/[✓✕]/g, '').trim() : null, d ? d.dataset.date : null]; }})()"""
        e1 = pg.evaluate(SUGG)
        pg.locator(f'tr[data-row="{rid}"] [data-act=date-take]').click()
        pg.wait_for_timeout(500)
        e2 = pg.evaluate(SUGG)
        print('E) Vorschlag an der Zeile:', e1, '| übernommen:', e2)
        results.append(e1[0] is not None and 'Liner notes – Jane Roe' in e1[0] and e1[1] is None and e2[0] is None and e2[1] == '2019-05')
        print('Fehler:', real(errs), real(bcerr))
        results.append(not real(errs) and not real(bcerr))
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_labelpage():
    """Credits Importer 3.22.1: an album on a label's Bandcamp page (collected item 46), and people not found through their
    own link are searched by name.
    A) A Bandcamp album of Yunclas on the page of the label "Grabaciones Autobombo" (its "data-band"): Yunclas gets no
       Bandcamp link (the page is not his), so not "no MB artist with this Bandcamp link" – he is searched by name: the
       release's artist Yunclas first, marked "release artist" ([3.37.1] "in this release: release artist", E5a), then the other
       Yunclas; nothing assigned. The entry says
       whose page it is (with a link) and names MusicBrainz's label with that page, "a label of this release ✓"; the source
       line says "on the Bandcamp page of Grabaciones Autobombo", the log too. A click on the suggestion assigns it.
    B) In Node: the account's name from "data-band" (else "og:site_name"); the artist's own page ("The Test Band" for Test
       Band; "Jane Roe & Friends" on Jane Roe's page is hers) keeps the link of the band, a label's page does not.
    C) Discogs: a person whose Discogs link MusicBrainz does not have ("no MB artist with this Discogs link") gets the
       same-named entries as suggestions, the release's artist first."""
    import json
    import os
    import subprocess

    HERE = os.path.dirname(os.path.abspath(__file__))
    SCRIPT = os.path.join(HERE, '..', 'mb-vibecode-credits-importer.user.js')
    YUN = H.uid('dddddddd', 60)
    YUN2 = H.uid('dddddddd', 61)
    LABEL = H.uid('eeeeeeee', 60)
    PAGE = 'https://grabacionesautobombo.bandcamp.com/'
    ALBUM = PAGE + 'album/xixon'
    H.RELEASE_AC[:] = [(YUN, 'Yunclas', 'Yunclas', '')]
    H.MB_SEARCH['artist'] = [{'id': YUN, 'name': 'Yunclas', 'disambiguation': '', 'score': 100},
                             {'id': YUN2, 'name': 'Yunclas', 'disambiguation': 'Spanish rapper', 'score': 100}]
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Yunclas', 'current': {'title': 'Xixón', 'credits': 'Recorded by Yunclas in Xixon, Asturies, Spain', 'about': '',
                                    'release_date': '01 Jan 2020 00:00:00 GMT'},
                                   'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]},
                                  band='Grabaciones Autobombo')
    for i, t in enumerate(H.TITLES):
        H.BC_PAGES[f'{PAGE}track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': ''}}, band='Grabaciones Autobombo')
    orig_ws, orig_url = H.ws_release, H.ws_url


    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        d['label-info'] = [{'catalog-number': 'GA01', 'label': {'id': LABEL, 'name': 'Grabaciones Autobombo'}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    def ws_url(query):
        if PAGE in [x for x in __import__('urllib.parse').parse.parse_qs(query).get('resource', [])]:
            return {'urls': [{'resource': PAGE, 'relations': [{'target-type': 'label', 'label': {'id': LABEL, 'name': 'Grabaciones Autobombo', 'disambiguation': ''}}]}]}
        return orig_url(query)


    H.ws_release = ws
    H.ws_url = ws_url
    GROUPS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => ({ key: g.dataset.group, cls: g.className,
  name: g.querySelector('.dci-gname strong').textContent.trim(), head: g.querySelector('.dci-gname').textContent.replace(/\\s+/g, ' ').trim(),
  match: (g.querySelector('.dci-gmatch .dci-badge') || { textContent: '' }).textContent.trim(),
  sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()),
  page: (g.querySelector('.dci-pageof') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim(),
  pageLink: (g.querySelector('.dci-pageof a') || { href: '' }).href, mbLink: (g.querySelector('.dci-gname .dci-mblink, .dci-gmatch .dci-mblink') || { href: '' }).href })))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1000)
        g = {x['name']: x for x in pg.evaluate(GROUPS)}
        yun = g.get('Yunclas') or {'sugg': [], 'page': '', 'match': '', 'cls': '', 'head': '', 'pageLink': '', 'key': ''}
        src = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 120)")
        logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Bandcamp page' in x or 'with this Bandcamp link' in x]
        print('A) Yunclas:', yun['head'], '|', yun['match'], '| Vorschläge:', yun['sugg'])
        print('   Hinweis:', yun['page'], yun['pageLink'])
        print('   Quelle:', src, '\n   Protokoll:', logs)
        ok_a = 'Bandcamp' not in yun['head'] and 'not assigned yet (no link)' in yun['match'] and 'dci-st-missing' in yun['cls'] \
            and yun['sugg'][:2] == ['Yunclas in this release: release artist', 'Yunclas (Spanish rapper)'] \
            and 'The Bandcamp page of this album belongs to Grabaciones Autobombo – not Yunclas\'s own page' in yun['page'] and yun['pageLink'] == PAGE \
            and 'in MusicBrainz: label Grabaciones Autobombo – a label of this release ✓' in yun['page'] \
            and 'on the Bandcamp page of Grabaciones Autobombo' in src \
            and any('Yunclas: the album is on the Bandcamp page of Grabaciones Autobombo' in x for x in logs) \
            and any('label Grabaciones Autobombo in MusicBrainz – a label of this release' in x for x in logs) and not any('with this Bandcamp link' in x for x in logs)
        pg.click(f"section[data-group=\"{yun['key']}\"] [data-act=name-use]")
        pg.wait_for_timeout(400)
        after = {x['name']: x for x in pg.evaluate(GROUPS)}.get('Yunclas', {})
        print('   nach Klick:', after.get('cls'), after.get('mbLink'))
        ok_a = ok_a and 'dci-st-manual' in after.get('cls', '') and after.get('mbLink', '').endswith(YUN)
        results.append(ok_a)
        print('Fehler:', errs)
        results.append(not errs)
        pg.close()

        # B) in Node
        NODE = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const bc = m.SOURCES.bandcamp;
const page = (band, meta) => `<html><head>${meta ? `<meta property="og:site_name" content="${meta}">` : ''}</head><body><script data-tralbum="{}"${band ? ` data-band="${band.replace(/"/g, '&quot;')}"` : ''}></script></body></html>`;
const names = [bc.bandPageName(page(JSON.stringify({ id: 1, name: 'Grabaciones Autobombo' }))), bc.bandPageName(page('', 'Jane Roe')), bc.bandPageName(page('', ''))];
const ctx = { isRole: (x) => /^guitar/i.test(x), isCompanyRole: () => false, resolveTracks: () => null, sig: () => 'x' };
const data = (artist) => ({ artist, current: { credits: `Guitar – ${artist}` }, trackinfo: [{ track_num: 1, title: 'A' }] });
const id = (artist, pageName) => { const r = bc.toRelease(data(artist), 'https://x.bandcamp.com/album/a', [], ctx, { pageName });
  const c = r.credits[0]; return [c.who.id || '', !!c.who.pageOf, r.band.own]; };
console.log(JSON.stringify({ names, own: id('Test Band', 'The Test Band'), friends: id('Jane Roe & Friends', 'Jane Roe'), label: id('Yunclas', 'Grabaciones Autobombo'), none: id('Test Band', '') }));
"""
        out = json.loads(subprocess.run(['node', '-e', NODE, SCRIPT], capture_output=True, text=True, check=True).stdout)
        print('B)', out)
        ok_b = out['names'] == ['Grabaciones Autobombo', 'Jane Roe', ''] and out['own'] == ['https://x.bandcamp.com/', False, True] \
            and out['friends'] == ['', False, True] and out['label'] == ['', True, False] and out['none'] == ['https://x.bandcamp.com/', False, True]
        results.append(ok_b)

        # C) Discogs: a person MusicBrainz does not have with this Discogs link
        H.ws_release, H.ws_url = orig_ws, orig_url
        orig_dg = H.discogs_release

        def dg():
            d = orig_dg()
            d['extraartists'].append({'name': 'Yunclas', 'anv': '', 'role': 'Mastered By', 'tracks': '', 'id': 3060, 'join': ''})
            return d

        H.discogs_release = dg
        ctx2 = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx2, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1000)
        g = {x['name']: x for x in pg.evaluate(GROUPS)}
        yd = g.get('Yunclas') or {'sugg': [], 'match': '', 'head': ''}
        others = {k: v['sugg'] for k, v in g.items() if k != 'Yunclas' and v['sugg']}
        print('C) Yunclas (Discogs):', yd['head'], '|', yd['match'], '| Vorschläge:', yd['sugg'], '| andere mit Vorschlägen:', others)
        ok_c = 'Discogs' in yd['head'] and 'no MB artist with this Discogs link' in yd['match'] and yd['sugg'][:2] == ['Yunclas in this release: release artist', 'Yunclas (Spanish rapper)'] \
            and not others
        results.append(ok_c)
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bctrack():
    """Credits Importer 3.28.1 / Companion 1.8.4: a Bandcamp track page as the release (collected items 55, 73, 74).
    A) A digital release linked to a track page of its own (a single, no album): Bandcamp is loaded from it – the source
       names the track page, its credits are read once (the page is asked for once, although "Read the credits of the
       Bandcamp track pages too" is on). A Bandcamp tab on that page (companion 1.8.4): "connected", a mark before each credit.
    B) In Node: a track page is a Bandcamp release ("?from=embed" left out, host and kind in lower case), next to the album
       pages a release links to; other pages of Bandcamp are none.
    C) "Other source" with a track page of an album ("…/track/song-2?from=embed"): loaded, only its own credit; the Bandcamp
       tab is "on another page" – "Load the release there" loads it (a track page of an album is that album's and its
       own release) – "connected", its mark.
    D) "Test page" with the track page: one track, two lines of credits, no other track pages.
    E) The texts: "Read the credits of the Bandcamp track pages too" (item 73); in a narrow dashboard the long texts of
       the settings wrap inside the settings ("Release editor: the button …", item 74) instead of running out of them."""
    import json
    import subprocess

    H.attr(9120, 'trumpet', 14, 14)
    H.attr(9121, 'viola', 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    BAND = 'https://testband.bandcamp.com'
    SINGLE = f'{BAND}/track/single-song'
    SONG2 = f'{BAND}/track/song-2'
    H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
    H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
    H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
    ONE = [{'track_num': None, 'title': 'Single Song', 'title_link': '/track/single-song', 'duration': 200.0}]
    H.BC_PAGES[SINGLE] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Single Song', 'credits': 'Mixed by Jane Roe\nTrumpet: Peter Evans',
                                    'release_date': '01 Jan 2020 00:00:00 GMT'}, 'trackinfo': ONE}, SINGLE)
    H.BC_PAGES[SONG2] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': 'Song Two', 'credits': 'Viola: Anna Viola'},
                                   'trackinfo': [{'track_num': 2, 'title': 'Song Two', 'title_link': '/track/song-2', 'duration': 180.0}]}, SONG2)


    class Counted(dict):
        """The pages of Bandcamp, counting how often each is asked for."""
        asked = {}

        def get(self, k, d=None):
            Counted.asked[k] = Counted.asked.get(k, 0) + 1
            return super().get(k, d)


    H.BC_PAGES = Counted(H.BC_PAGES)
    orig_ws = H.ws_release


    def ws():
        d = orig_ws()
        d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': SINGLE + '?from=embed'}})
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d


    H.ws_release = ws
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SYNC = "document.querySelector('[data-el=sync] .dci-syncstatus').textContent.replace(/\\s+/g, ' ').trim()"
    ROWS = """(() => [...document.querySelectorAll('section.dci-group')].map(g => g.querySelector('.dci-gname strong').textContent.trim() + ': '
  + [...g.querySelectorAll('tr.dci-row')].map(tr => tr.querySelector('.dci-drole').textContent.trim()).join(', ')))()"""
    SOURCE = "(() => { const a = document.querySelector('[data-el=source] a[href*=bandcamp]'); return a ? [a.textContent.trim(), a.href] : null; })()"
    results = []


    def poll(pg, js, timeout=20):
        for _ in range(timeout * 5):
            try:
                if pg.evaluate(js):
                    return True
            except Exception:
                pass
            pg.wait_for_timeout(200)
        raise TimeoutError(js)


    done = lambda pg, n: H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= {n}", 60)
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        bc, bcerr = H.open_bandcamp(ctx, SINGLE)
        pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        before = Counted.asked.get(SINGLE, 0)  # the Bandcamp tab itself
        H.open_dashboard(pg)
        done(pg, 1)
        pg.wait_for_timeout(800)
        # A)
        a1 = [pg.evaluate(SOURCE), pg.evaluate(ROWS), Counted.asked.get(SINGLE, 0) - before]
        H.wait_for(pg, f"{SYNC}.includes('connected')", 20)
        poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark').length >= 2")
        a2 = [pg.evaluate(SYNC), bc.evaluate("document.querySelectorAll('.tralbum-credits .dci-dg-mark').length")]
        print('A) Quelle, Einträge, Anfragen an die Track-Seite:', a1, '| Bandcamp-Tab:', a2)
        results.append(a1[0] == ['Single Song (Bandcamp)', SINGLE] and a1[1] == ['Jane Roe: Mixed By', 'Peter Evans: Trumpet']
                       and a1[2] == 1 and a2[0].startswith('Bandcamp view: connected') and a2[1] == 2)
        # B) in Node
        node = """const m = require(process.argv[1]); const bc = m.SOURCES.bandcamp;
      const ids = ['https://TestBand.bandcamp.com/TRACK/Single-Song?from=embed', 'https://testband.bandcamp.com/album/testalbum#x', 'https://testband.bandcamp.com/music', 'https://testband.bandcamp.com/'].map(bc.parseReleaseId);
      const links = bc.releaseLinks(['https://testband.bandcamp.com/album/a', 'https://testband.bandcamp.com/track/b?x=1', 'https://testband.bandcamp.com/track/b'].map((u) => ({ 'target-type': 'url', url: { resource: u } }))).map((l) => l.id);
      console.log(JSON.stringify([ids, links, bc.isTrackPage('https://x.bandcamp.com/track/y'), bc.isTrackPage('https://x.bandcamp.com/album/y')]));"""
        b1 = json.loads(subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True, check=True).stdout)
        print('B) Node:', b1)
        results.append(b1 == [['https://testband.bandcamp.com/track/Single-Song', 'https://testband.bandcamp.com/album/testalbum', '', ''],
                              ['https://testband.bandcamp.com/album/a', 'https://testband.bandcamp.com/track/b'], True, False])
        # C) another source: a track page of an album
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', SONG2 + '?from=embed')
        pg.click('[data-act=discogs-load]')
        done(pg, 2)
        pg.wait_for_timeout(800)
        c1 = [pg.evaluate(SOURCE), pg.evaluate(ROWS)]
        H.wait_for(pg, f"{SYNC}.includes('on another page')", 20)
        c2 = pg.evaluate(SYNC)
        pg.locator('[data-el=sync] [data-act=sync-load]').click()
        poll(bc, f"location.href === '{SONG2}'")
        H.wait_for(pg, f"{SYNC}.includes('connected')", 20)
        poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark').length >= 1")
        c3 = [pg.evaluate(SYNC), bc.evaluate("document.querySelectorAll('.tralbum-credits .dci-dg-mark').length")]
        print('C) Quelle, Einträge:', c1, '| Tab:', c2, '→', c3)
        results.append(c1 == [['Song Two (Bandcamp)', SONG2], ['Anna Viola: Viola']] and 'on another page' in c2
                       and c3[0].startswith('Bandcamp view: connected') and c3[1] == 1)
        # D) "Test page"
        H.src_menu(pg, 'bc-toggle')
        pg.wait_for_timeout(200)
        pg.fill('[data-f=bc-test-url]', SINGLE + '?from=embed')
        pg.click('[data-act=bc-test]')
        H.wait_for(pg, "!!document.querySelector('[data-bc-result]') && !/…|\\.\\.\\./.test(document.querySelector('[data-bc-result]').textContent)", 20)
        d1 = pg.evaluate("document.querySelector('[data-bc-result]').textContent.trim()")
        print('D) Test:', d1)
        results.append(d1.startswith('Read: “Single Song”, 1 tracks, 2 lines of credits, 0 track pages'))
        # E) the texts, wrapped in a narrow dashboard
        pg.click('.dci-head [data-act=settings-open]')
        pg.wait_for_timeout(200)
        pg.click('[data-el=settings] .dci-set-tab[data-topic=sources]')
        pg.wait_for_timeout(200)
        pg.evaluate("(() => { const p = document.querySelector('#dci-overlay .dci-panel'); p.style.width = '520px'; })()")
        pg.wait_for_timeout(400)
        e1 = pg.evaluate("""(() => { const pane = document.querySelector('[data-el=settings] .dci-set-pane').getBoundingClientRect();
      const lab = (sel) => document.querySelector(`[data-el=settings] .dci-set-pane label:has(${sel})`);
      const t = lab('[data-f=bc-tracks]'); const l = lab('[data-set=after-edit]'); const r = l.getBoundingClientRect();
      const line = parseFloat(getComputedStyle(l).lineHeight) || 18;
      return [t.textContent.trim(), Math.round(r.right) <= Math.round(pane.right), r.height > line * 1.5, l.querySelector('input').getBoundingClientRect().top < r.top + line]; })()""")
        print('E) Text, innerhalb, umgebrochen, Kästchen oben:', e1)
        results.append(e1 == ['Read the credits of the Bandcamp track pages too', True, True, True])
        # (the Bandcamp tab: the harness's storage cannot be written while a page is left – not the companion's doing)
        bcerr = [e for e in bcerr if 'page dismissal' not in e]
        print('Fehler:', errs, bcerr)
        results.append(not errs and not bcerr)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_aboutcredits():
    """Credits Importer 3.32.6: the credits of Bandcamp's "about" text (collected item 115, rule S049; Vivarium Recordings,
    j4vaman – "Ephemeral": the credits field empty, all in the "about" text).
    A) In Node: the "about" text gives j4vaman with "Music By" (written "Muisc", S050) and "Cover art", both from the "about"
       text, and "Liner Notes" for "j4vavaman" – the signature "-j4vavaman" (one word, small letters, a digit; two letters off
       the album's artist) above the credit line; nothing listed as not recognized from it. With S049 off: only the liner notes.
       linerNotes without the credit lines and the artist's name gives nothing (as before).
    B) The dashboard: j4vaman (the album is on the label's page) with "Cover art" from the "about" text; the works matrix has
       his column (composer, S050); j4vavaman with "Liner Notes", the release's artist j4vaman as the first suggestion
       (release artist, similar name) – nothing assigned; "Bandcamp has no credits" does not come.
    C) ⚙ Settings → Texts: "Bandcamp: read the credits in the “about” text" is on; off → stored (S049)."""
    import json
    import subprocess

    ABOUT = ('VR_266\n\nj4vaman - Ephemeral\n\nRuntime: 28:31\n\n"Ephemeral is my fifth solo album.\n\nThis album is a follow up to my previous '
             'one, "Never Ending Void" and is mostly based on the concept of afterlife and memories.\n\nIt\'s also my first proper ambient/dark '
             'ambient record, without much experimentation that would shift it into different genres. But as usual with my work, there are '
             'various samples from old public service advertisements, archival films and radio programs here and there."\n\n-j4vavaman\n\n'
             'Muisc and cover art by j4vaman')
    NODE = r"""
const off = process.argv[3];
global.localStorage = { getItem: (k) => (k === 'dci-rules-off' && off ? off : null), setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
const bc = m.SOURCES.bandcamp;
const about = process.argv[2];
const isRole = (phrase) => { const p = m.parseRoleNotation(phrase)[0]; if (!p || !p.base || /\d/.test(p.base)) return false;
  const r = m.mapRole(p.base, p.mods); return !!(r.rule && r.rule !== 'R096' && !r.fallback); };
const ctx = { isRole, isCompanyRole: () => false, resolveTracks: () => null, sig: () => 'x', artistNames: ['j4vaman'] };
const r = bc.toRelease({ artist: 'j4vaman', current: { credits: '', about }, trackinfo: [{ track_num: 1, title: 'A Familiar Stranger' }] },
  'https://vivariumrecordings.bandcamp.com/album/ephemeral', [], ctx, { pageName: 'Vivarium Recordings' });
const plain = bc.linerNotes(about);
console.log(JSON.stringify({ credits: r.credits.map((c) => [c.who.name, c.role, !!c.fromAbout, (c.typos || []).map((t) => t.written).join()]),
  unrec: r.unrecognized, plain: plain && plain.name }));
"""
    results = []
    run = lambda off: json.loads(subprocess.run(['node', '-e', NODE, str(H.ROOT / 'mb-vibecode-credits-importer.user.js'), ABOUT, off], capture_output=True, text=True, check=True).stdout)
    a = run('')
    a_off = run('["S049"]')
    print('A)', a, '\n   S049 aus:', a_off)
    ok_a = sorted(a['credits']) == sorted([['j4vaman', 'Music By', True, 'Muisc'], ['j4vaman', 'Cover art', True, ''], ['j4vavaman', 'Liner Notes', True, '']]) \
        and not a['unrec'] and a['plain'] is None and a_off['credits'] == [['j4vavaman', 'Liner Notes', True, '']]
    results.append(ok_a)

    PAGE = 'https://vivariumrecordings.bandcamp.com/'
    ALBUM = PAGE + 'album/ephemeral'
    J4 = H.uid('dddddddd', 115)
    H.RELEASE_AC[:] = [(J4, 'j4vaman', 'j4vaman', '')]
    H.MB_SEARCH['artist'] = [{'id': J4, 'name': 'j4vaman', 'disambiguation': '', 'score': 100}]
    H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'j4vaman', 'current': {'title': 'Ephemeral', 'credits': '', 'about': ABOUT, 'release_date': '23 Oct 2026 00:00:00 GMT'},
                                   'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]},
                                  band='Vivarium Recordings')
    for i, t in enumerate(H.TITLES):
        H.BC_PAGES[f'{PAGE}track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': ''}}, band='Vivarium Recordings')
    orig_ws = H.ws_release

    def ws(full=False):
        d = orig_ws(full)
        d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
        for m in d['media']:
            m['format'] = 'Digital Media'
        return d

    H.ws_release = ws
    GROUPS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), {
  sugg: [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), cls: g.className,
  rows: [...g.querySelectorAll('tr.dci-row')].map(tr => tr.querySelector('.dci-drole').parentElement.textContent.replace(/\\s+/g, ' ').trim()) }])))()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1500)
        g = pg.evaluate(GROUPS)
        for k, v in g.items():
            print('   ', k, v)
        j4 = g.get('j4vaman') or {'rows': [], 'sugg': []}
        jv = g.get('j4vavaman') or {'rows': [], 'sugg': []}
        col = pg.evaluate("""(() => { const th = [...document.querySelectorAll('th.dci-mx-col')].find(t => /j4vaman/.test(t.querySelector('.dci-mx-colname').textContent));
          return th ? [th.querySelector('.dci-mx-roles').textContent.replace(/\\s+/g, ' ').trim(), (th.querySelector('[data-rule=S050]') || { title: '' }).title] : null; })()""")
        msgs = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(e => e.textContent.replace(/\\s+/g, ' ').trim())")
        print('B) j4vaman:', j4['rows'], '| Spalte:', col, '| j4vavaman:', jv['rows'], jv['sugg'], '| Meldungen:', msgs)
        ok_b = any('Cover art' in r and 'From the “about” text' in r for r in j4['rows']) and col and col[0].startswith('composer') \
            and col[1] == 'Read as “Music” (written “Muisc”)' and any('Liner Notes' in r for r in jv['rows']) \
            and jv['sugg'][:1] and jv['sugg'][0].startswith('j4vaman') and 'release artist' in jv['sugg'][0] and 'similar' in jv['sugg'][0] \
            and 'dci-st-missing' in jv['cls'] and not any('has no credits' in x for x in msgs)
        H.open_settings(pg, 'texts')
        sw = pg.locator('[data-el=settings] [data-set=rule-on][data-rule=S049]')
        on0 = sw.is_checked()
        sw.uncheck()
        pg.wait_for_timeout(300)
        off = pg.evaluate("JSON.parse(localStorage.getItem('dci-rules-off') || '[]')")
        print('C) an:', on0, '| aus gespeichert:', off)
        ok_c = on0 and 'S049' in off
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
