"""Credits Importer 3.28.3 / Companion 1.9.0: the dates and track groups the dashboard uses, underlined in the texts of
the source (collected item 63).
A) Discogs: the notes "Dedicated to Jim, 1999." and "Tracks 1-2 recorded March 1–3, 2001 at Abbey Road Studios. Mixed May
   2001." – both dates with a word naming their group go into the date matrix, so "March 1–3, 2001" and "May 2001" are
   underlined in the date colour, "Tracks 1-2" (the track group of its sentence in the matrix) in the track colour;
   "1999" (only in the pool) is not. The tooltip says where the dashboard uses it.
B) The pool date "1999" dropped onto a row: underlined too ("the date of a row").
C) "Status on Discogs" switched off: no underlines (and no marks); on again: back.
D) Bandcamp: "Recorded by Jane Roe in 2020" in the credits and "Tracks 1-2 mixed in July 2019." in the "about" text –
   each underlined in its text, "Tracks 1-2" too ("2020" in its line, not in "released January 1, 2020" above the
   credits); the credit marks are still there.
E) [1.9.0] Two lines of one artist with the same role ("Vocals [Clean]", "Vocals [Screams]"): a mark on each line."""
import json
from playwright.sync_api import sync_playwright
import harness as H

NOTES = 'Dedicated to Jim, 1999.\nTracks 1-2 recorded March 1–3, 2001 at Abbey Road Studios. Mixed May 2001.'
orig_rel = H.discogs_release
orig_page = H.discogs_page
H.ARTISTS[3015] = (H.uid('dddddddd', 25), 'Valfar')


def rel():
    d = orig_rel()
    d['notes'] = NOTES
    d['extraartists'] += [{'name': 'Valfar', 'anv': '', 'role': 'Vocals [Clean]', 'tracks': '', 'id': 3015, 'join': ''},
                          {'name': 'Valfar', 'anv': '', 'role': 'Vocals [Screams]', 'tracks': '', 'id': 3015, 'join': ''}]
    return d


def page():
    extra = ''.join(f'<li><span>{r}</span> – <a href="/artist/3015-Valfar">Valfar</a></li>' for r in ('Vocals [Clean]', 'Vocals [Screams]'))
    p = orig_page().replace('</ul><h2>Companies, etc.</h2>', f'{extra}</ul><h2>Companies, etc.</h2>')
    notes = ('<section id="release-notes"><header><h2>Notes</h2></header><div>Dedicated to Jim, 1999.<br>Tracks 1-2 recorded March 1–3, 2001'
             ' at Abbey Road Studios. Mixed May 2001.</div></section>')
    return p.replace('</body>', f'{notes}</body>')


H.discogs_release = rel
H.discogs_page = page
UL = """(() => ['dci-txt-date', 'dci-txt-tracks'].map(c => [...document.querySelectorAll('.' + c)].map(s => [s.textContent, s.title])))()"""
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


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx, companion=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    poll(dg, "document.querySelectorAll('#release-notes .dci-txt-date').length >= 2")
    dg.wait_for_timeout(600)
    a1 = dg.evaluate(UL)
    print('A) unterstrichen (Daten, Trackgruppen):', a1)
    results.append([x[0] for x in a1[0]] == ['March 1–3, 2001', 'May 2001'] and [x[0] for x in a1[1]] == ['Tracks 1-2']
                   and all('in the date matrix' in x[1] for x in a1[0] + a1[1])
                   and dg.evaluate("document.querySelector('#release-notes').textContent.replace(/\\s+/g, ' ').includes('Dedicated to Jim, 1999.')"))
    # B) "1999" from the pool onto a row
    dropped = pg.evaluate("""(() => { const src = [...document.querySelectorAll('[data-drag=date]')].find(x => /1999/.test(x.textContent));
      const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bob Producer');
      const dst = g && g.querySelector('tr.dci-row .dci-c-date');
      if (!src || !dst) return [!!src, !!dst];
      const dt = new DataTransfer();
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
      dst.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
      dst.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
      src.dispatchEvent(new DragEvent('dragend', { bubbles: true, dataTransfer: dt }));
      return [true, true]; })()""")
    print('   gezogen:', dropped)
    pg.wait_for_timeout(500)
    poll(dg, "[...document.querySelectorAll('.dci-txt-date')].some(s => s.textContent === '1999')")
    b1 = dg.evaluate(UL)[0]
    print('B) 1999 auf einer Zeile:', b1)
    results.append(['1999', 'Credits Importer: “1999” is the date of a row'] in b1 and len(b1) == 3)
    # C) status off and on
    H.open_settings(pg, 'discogs')
    pg.locator('[data-el=settings] [data-dg-status]').first.click()
    poll(dg, "!document.querySelector('.dci-txt-date, .dci-txt-tracks, .dci-dg-mark')")
    c1 = dg.evaluate(UL)
    pg.locator('[data-el=settings] [data-dg-status]').first.click()
    poll(dg, "document.querySelectorAll('.dci-txt-date').length >= 3")
    c2 = dg.evaluate(UL)
    print('C) aus:', c1, '| wieder an:', [len(x) for x in c2])
    results.append(c1 == [[], []] and [len(x) for x in c2] == [3, 1])
    # E) two lines of Valfar
    e1 = dg.evaluate("[...document.querySelectorAll('#release-credits li')].filter(li => /Vocals/.test(li.textContent)).map(li => [li.querySelector('span').textContent, li.querySelectorAll('.dci-dg-mark').length])")
    print('E) Valfar:', e1)
    results.append(e1 == [['Vocals [Clean]', 1], ['Vocals [Screams]', 1]])
    print('Fehler:', errs, dgerr)
    results.append(not errs and not dgerr)
    b.close()

# D) Bandcamp
H.attr(9121, 'viola', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
BAND = 'https://testband.bandcamp.com'
ALBUM = f'{BAND}/album/testalbum'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': 'Recorded by Jane Roe in 2020\nViola: Anna Viola',
                               'about': 'Tracks 1-2 mixed in July 2019.', 'release_date': '01 Jan 2020 00:00:00 GMT'}, 'trackinfo': TRACKS}, ALBUM)
for i, t in enumerate(TRACKS):
    url = f'{BAND}{t["title_link"]}'
    H.BC_PAGES[url] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                 'trackinfo': [t]}, url)
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    bc, bcerr = H.open_bandcamp(ctx, ALBUM)
    pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    poll(bc, "document.querySelectorAll('.dci-txt-date').length >= 2")
    bc.wait_for_timeout(600)
    d1 = bc.evaluate("""(() => ['.tralbum-credits', '.tralbum-about'].map(sel => { const r = document.querySelector(sel);
      return [[...r.querySelectorAll('.dci-txt-date')].map(s => s.textContent), [...r.querySelectorAll('.dci-txt-tracks')].map(s => s.textContent),
        r.querySelectorAll('.dci-dg-mark').length, [...r.querySelectorAll('.dci-txt-date')].map(s => (s.previousSibling || {}).textContent || '')]; }))()""")
    print('D) Bandcamp (Credits, about):', d1)
    results.append([x[:3] for x in d1] == [[['2020'], [], 2], [['July 2019'], ['Tracks 1-2'], 0]] and d1[0][3][0].endswith('Jane Roe in '))
    bcerr = [e for e in bcerr if 'page dismissal' not in e]
    print('Fehler:', errs, bcerr)
    results.append(not errs and not bcerr)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
