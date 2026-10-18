"""Companion 1.8.2 (with Credits Importer 3.17.3): the check on the MusicBrainz release page keeps its result.
A) After "Enter edit" the release page checks the staged credits: ✓ on Discogs.
B) Its next check (after 20 s) cannot read MusicBrainz (503): the marks stay ✓ – before, the unchecked marks (●) came
   back; it is tried again after 15 s and then reads MusicBrainz again (the check is newer).
C) A page in a background tab beats only about once a minute: its status counts as alive for 75 s ("hidden"), the
   status of a visible page for 8 s as before."""
import time
from playwright.sync_api import sync_playwright
import harness as H

MARKS = "[...document.querySelectorAll('.dci-dg-mark')].map(m => m.textContent)"
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


real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg, dgerr = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
    pg.click('[data-act=apply]')
    poll(dg, f"{MARKS}.includes('●')")
    staged = dg.evaluate(MARKS).count('●')
    H.submit_staged(pg)
    pg.goto(f'https://musicbrainz.org/release/{H.REL}')
    H.with_companion(pg)
    # A) checked: ✓
    poll(dg, f"(() => {{ const m = {MARKS}; return m.includes('✓') && !m.includes('●'); }})()", 30)
    a = dg.evaluate(MARKS)
    checked0 = H.STORE.data['statusMap'].get('checked')
    print('A) nach „Enter edit“:', a, '| vorgemerkt waren', staged)
    results.append(a.count('✓') >= 1 and '●' not in a)
    # B) the check after 20 s cannot read MusicBrainz
    H.WS_FAIL['release'] = 1
    t0 = time.time()
    while H.WS_FAIL.get('release', 0) > 0 and time.time() - t0 < 40:
        dg.wait_for_timeout(500)
    dg.wait_for_timeout(2500)
    b1 = dg.evaluate(MARKS)
    print('B) Prüfung ohne Antwort:', b1, '| nach', round(time.time() - t0), 's')
    poll(dg, f"(() => {{ const m = GM_getValue('statusMap'); return m && m.checked > {checked0}; }})()", 30)
    b2 = dg.evaluate(MARKS)
    print('   erneut versucht:', b2)
    results.append(H.WS_FAIL.get('release') == 0 and b1 == a and b2 == a)
    # C) a page in the background: its last beat counts for 75 s
    pg.close()
    poll(dg, f"{MARKS}.length === 0", 15)
    now = int(time.time() * 1000)
    H.STORE.set('statusBeat', {'pageId': f'release-{H.REL}', 'release': H.REL, 'ts': now - 30000, 'hidden': True})
    poll(dg, f"{MARKS}.length > 0", 10)
    c1 = len(dg.evaluate(MARKS))
    H.STORE.set('statusBeat', {'pageId': f'release-{H.REL}', 'release': H.REL, 'ts': now - 30000, 'hidden': False})
    poll(dg, f"{MARKS}.length === 0", 10)
    print('C) Hintergrund-Seite vor 30 s:', c1, 'Marken | sichtbare Seite vor 30 s: keine')
    results.append(c1 == len(a))
    print('Fehler:', real(errs), real(dgerr))
    results.append(not real(errs) and not real(dgerr))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
