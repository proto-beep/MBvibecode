"""Status marks on Discogs for credits on track lines: one mark on each line, with the status of that track
("Written-By – Writer W" under tracks 1 and 2: two marks). On the release page each line is checked on its own:
track 2's work is new in the editor and its link still open → ✗ there, ✓ on track 1; once the work is linked,
✓ on both."""
from playwright.sync_api import sync_playwright
import harness as H

WRITER = H.ARTISTS[3007][0]
results = []


def marks(dg):
    return dg.evaluate("""[...document.querySelectorAll('.dci-dg-mark')].filter(m => m.closest('[data-track-position]'))
      .map(m => [m.closest('[data-track-position]').dataset.trackPosition, m.textContent, m.closest('div, li').querySelector('a').textContent, m.title.slice(0, 40)])""")


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    dg.wait_for_timeout(1500)
    m0 = marks(dg)
    print('1) vor dem Übernehmen (Track-Zeilen):', m0)
    ok1 = sorted((x[0], x[2]) for x in m0) == [('1', 'Writer W'), ('2', 'Writer W')] and all(x[1] == '○' for x in m0)
    # track 2 gets a new work in the editor; everything is staged
    pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(400)
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    dg.wait_for_timeout(2000)
    m1 = marks(dg)
    print('2) nach Übernehmen:', m1)
    ok1 = ok1 and sorted(x[1] for x in m1) == ['●', '●'] and any(x[3].startswith('1:') for x in m1)
    results.append(ok1)
    H.submit_staged(pg)
    # the link of the new work (track 2) is still an open edit
    pg.goto(f'https://musicbrainz.org/release/{H.REL}')
    H.with_companion(pg)
    dg.wait_for_timeout(6000)
    m2 = dict((x[0], x[1]) for x in marks(dg))
    print('3) Release-Seite, Werk-Link von Track 2 noch offen:', m2)
    pg.close()
    # MusicBrainz linked the new work with its writer
    H.MB_EXTRA[H.REC[1]] = [{'target-type': 'work', 'type': 'performance', 'type-id': H.LTS[278]['gid'], 'attributes': [],
                             'work': {'id': H.uid('cccccccc', 44), 'title': 'Song Two', 'relations': [
                                 {'target-type': 'artist', 'type': 'writer', 'type-id': H.LTS[167]['gid'], 'attributes': [], 'artist': {'id': WRITER, 'name': 'Writer W'}}]}}]
    dg.wait_for_timeout(9000)
    pr, _ = H.open_mb_release(ctx)
    dg.wait_for_timeout(6000)
    m3 = dict((x[0], x[1]) for x in marks(dg))
    print('4) Werk verknüpft:', m3)
    results.append(m2 == {'1': '✓', '2': '✗'} and m3 == {'1': '✓', '2': '✓'})
    print('Fehler:', errs, dgerr)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
