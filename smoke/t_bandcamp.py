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
from playwright.sync_api import sync_playwright
import harness as H

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
   [...g.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim())]])))()"""
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
    pg.select_option('[data-f=discogs-pick]', f'bandcamp|{ALBUM}')
    done(pg, 2)
    pg.wait_for_timeout(800)
    g = pg.evaluate(GROUPS)
    calls = pg.evaluate('window.__gmXhr')
    unrec = pg.evaluate("[...document.querySelectorAll('.dci-unrec li')].map(li => li.textContent)")
    print('B) Quelle:', source(pg), '| Abrufe:', len(calls), calls[:2])
    for k, v in g.items():
        print('   ', k, v)
    print('   nicht erkannt:', unrec)
    ok_b = 'Testalbum (Bandcamp)' in source(pg) and calls[0] == ALBUM and len(calls) == 5 \
        and g['Test Band'][0] == 'linked' and g['Test Band'][1] == ['guitar · 4 of 4 tracks'] \
        and g['Jane Roe'][1] == ['Mixed By · 4 of 4 tracks'] and g['Peter Evans'][1] == ['Trumpet · 4 of 4 tracks'] \
        and g['Anna Viola'][1] == ['Viola · 1 of 4 tracks'] and unrec == ['Thanks Mom.']
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
    pg.click('[data-act=srcorder-toggle]'); pg.wait_for_timeout(200)
    lists = pg.evaluate("[...document.querySelectorAll('[data-srcorder]')].map(ol => [ol.dataset.srcorder, [...ol.querySelectorAll('li')].map(li => li.dataset.id), ol.closest('.dci-srcorder-col').querySelector('strong').textContent.trim()])")
    pg.click('[data-act=srcorder-move][data-list=digital][data-src=discogs][data-dir="-1"]'); pg.wait_for_timeout(200)
    stored = pg.evaluate("JSON.parse(localStorage.getItem('dci-source-order'))")
    reopen(pg)
    print('C) digital zuerst:', first, '| Listen:', lists, '| gespeichert:', stored, '| danach:', source(pg))
    ok_c = 'Testalbum (Bandcamp)' in first and lists[0][1] == ['discogs', 'bandcamp'] and lists[1][1] == ['bandcamp', 'discogs'] \
        and '(this release)' in lists[1][2] and stored['digital'] == ['discogs', 'bandcamp'] and 'Discogs 1234' in source(pg)
    results.append(ok_c)

    # D) the Bandcamp menu: no track pages; the page test
    pg.click('[data-act=bc-toggle]'); pg.wait_for_timeout(200)
    pg.uncheck('[data-f=bc-tracks]'); pg.wait_for_timeout(100)
    pg.fill('[data-f=bc-test-url]', ALBUM + '?x=1')
    pg.click('[data-act=bc-test]')
    pg.wait_for_selector('[data-bc-result]:not(:empty)', timeout=10000)
    pg.wait_for_function("!/Loading/.test(document.querySelector('[data-bc-result]').textContent)", timeout=10000)
    test = pg.locator('[data-bc-result]').inner_text()
    pg.select_option('[data-f=discogs-pick]', f'bandcamp|{ALBUM}')
    done(pg, 2)
    pg.wait_for_timeout(500)
    g = pg.evaluate(GROUPS)
    print('D) Test:', test, '| ohne Track-Seiten:', 'Anna Viola' in g, '| gespeichert:', pg.evaluate("localStorage.getItem('dci-bc-tracks')"))
    ok_d = test.startswith('Read: “Testalbum”, 4 tracks, 4 lines of credits, 4 track pages (via GM_xmlhttpRequest)') and 'Anna Viola' not in g \
        and 'Test Band' in g and pg.evaluate("localStorage.getItem('dci-bc-tracks')") == 'false'
    results.append(ok_d)

    # E) a band spelled differently in MusicBrainz: only a suggestion
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
    pg.fill('[data-f=discogs-input]', ALBUM)
    pg.click('[data-act=discogs-load]')
    done(pg, 4)
    pg.wait_for_timeout(500)
    g1 = pg.evaluate(GROUPS).get('Test Band')
    spell = pg.evaluate(SPELL)
    H.RELEASE_AC[:] = [(gid, 'The Test Band', 'TEST BAND', '')]
    reopen(pg)
    g2 = pg.evaluate(GROUPS).get('Test Band')
    head = pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(g => g.querySelector('.dci-gname strong').textContent === 'Test Band').map(g => (g.querySelector('.dci-alias-suggest .dci-sub') || {}).textContent)[0]")
    log = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'names it differently in its artist credit' in x]
    print('F) MB „The Test Band“, Release „Test Band“:', g1, '| Release „TEST BAND“:', g2, '|', head, '|', log[-1:])
    spell2 = pg.evaluate(SPELL)
    print('   Schreibweise:', spell, '|', spell2)
    ok_f = spell and spell[1] and 'Bandcamp “Test Band” · release (artist credit) “Test Band” · MusicBrainz “The Test Band”' in spell[0] \
        and spell[2] == ['“The Test Band”'] and spell2 and '“TEST BAND”' in spell2[0] and spell2[2] == ['“TEST BAND”', '“The Test Band”']
    ok_f = ok_f and g1[0] == 'linked' and g2[0] == 'missing' and g2[2] == ['The Test Band'] and 'TEST BAND' in (head or '') and any('(TEST BAND)' in x for x in log)
    results.append(ok_f)
    print('Fehler:', errs, errs2)
    results.append(not errs and not errs2)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
