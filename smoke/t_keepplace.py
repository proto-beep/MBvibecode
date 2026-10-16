"""After creating an entry through MusicBrainz's form ("Create artist …"), the dashboard stays where it was: the
entry you came from keeps its place on the screen, although a message is added at the top and the dashboard is
redrawn (window and page). Scroll anchoring is switched off, as in browsers without it (Safari) and where the
entry itself is drawn anew."""
from playwright.sync_api import sync_playwright
import harness as H

orig = H.discogs_release
NEW = H.uid('dddddddd', 77)


def rel():
    d = orig()
    d['extraartists'] += [{'name': 'Nobody Known', 'anv': '', 'role': 'Vocals', 'tracks': '', 'id': 3999, 'join': ''}]
    return d


H.discogs_release = rel
results = []


NO_ANCHOR = '* { overflow-anchor: none !important; }'


def run(pg, inpage):
    pg.add_style_tag(content=NO_ANCHOR)
    key = pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(g => g.querySelector('.dci-gname strong').textContent === 'Nobody Known').dataset.group")
    sel = f'section.dci-group[data-group="{key}"]'
    # the entry in the middle of the screen
    pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{ block: 'center' }})")
    pg.wait_for_timeout(300)
    # 3.9.0: the button scrolled into view first (the click would scroll it), then the place is measured
    pg.locator(f'{sel} [data-act=artist-create]').scroll_into_view_if_needed()
    pg.wait_for_timeout(200)
    top0 = pg.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().top")
    msgs0 = pg.locator('[data-el=msgs] > *').count()
    pg.click(f'{sel} [data-act=artist-create]')
    pg.wait_for_selector('[data-el=sub]:not([hidden])', timeout=20000)
    pg.wait_for_timeout(300)
    # the form was submitted: MusicBrainz shows the new artist
    pg.evaluate(f"document.querySelector('[data-el=sub-frame]').src = 'https://musicbrainz.org/artist/{NEW}'")
    pg.wait_for_timeout(2600)
    top1 = pg.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().top")
    msgs1 = pg.locator('[data-el=msgs] > *').count()
    status = pg.evaluate(f"document.querySelector('{sel}').className")
    print(('In der Seite' if inpage else 'Fenster') + ':', 'Eintrag oben vorher', round(top0), '| nachher', round(top1), '| Nachrichten', msgs0, '→', msgs1, '|', status)
    return abs(top1 - top0) <= 3 and msgs1 > msgs0 and 'dci-st-created' in status


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    results.append(run(pg, False))
    # in the page
    pg2, errs2 = H.open_mb_edit(ctx, companion=False)
    pg2.evaluate("localStorage.setItem('dci-place', JSON.stringify('page'))")
    pg2.reload()
    pg2.add_script_tag(content=H.MAIN)
    pg2.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg2)
    pg2.wait_for_timeout(500)
    results.append(run(pg2, True))
    print('Fehler:', errs, errs2)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
