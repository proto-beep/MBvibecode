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
from playwright.sync_api import sync_playwright
import harness as H

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
