"""Credits Importer 3.20.0: the media dialog loads the chosen media in MB's relationship editor in the background, and asks
about the works there when many tracks have none (collected item 34).
Three media (2, 1, 1 tracks); MB's editor has loaded medium 1 only (media 2 and 3 open with their toggle).
A) The dialog: "Load the chosen media in the relationship editor in the background" (off at first) says how many of the
   chosen media are not loaded yet; with "Ask before the work lookups from 2 tracks" the box with the number of tracks
   without a work and the time, "Look up works" pressed; both follow the choice of media (medium 1 alone: 1 track, no box).
B) Ticked, "Not now", Import: media 2 and 3 are opened one after another while the import runs (log, message), the tick is
   remembered; the work lookups are left out (the works section offers "Look up now"), nothing is looked up.
C) "Skip works matrix" in the dialog: the matrix is skipped for this release (its rows on "Skip"), not asked again."""
import re
from playwright.sync_api import sync_playwright
import harness as H

H.MEDIA = [2, 1, 1]
orig = H.discogs_release


def rel():
    d = orig()
    for i, t in enumerate(d['tracklist']):
        t['position'] = ['1-1', '1-2', '2-1', '3-1'][i]
    return d


H.discogs_release = rel
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
# MB's editor with media 2 and 3 not loaded: their tracks come when their toggle is clicked
UNLOAD = """(() => { const st = MB.relationshipEditor.state; window.__saved = {};
  for (const m of st.entity.mediums) if (m.position > 1) { window.__saved[m.position] = m.tracks; m.tracks = []; }
  const t = document.createElement('table'); t.id = 'mb-media';
  t.innerHTML = [2, 3].map(p => `<tbody><tr><th>Medium ${p} <button type="button" aria-expanded="false" data-p="${p}">▸</button></th></tr></tbody>`).join('');
  document.getElementById('editor').append(t);
  t.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; const p = Number(b.dataset.p);
    b.setAttribute('aria-expanded', 'true'); window.__clicks = (window.__clicks || []).concat(p);
    setTimeout(() => st.loadedTracks.set(p, window.__saved[p]), 400); });
})()"""
DLG = """(() => { const d = document.querySelector('[data-el=media]'); if (!d || d.hidden) return null; const w = d.querySelector('[data-mel=works]');
  return { load: d.querySelector('[data-mf=load]').checked, state: d.querySelector('[data-mel=load]').textContent.trim(), works: !w.hidden,
    n: d.querySelector('[data-mel=works-n]').textContent.trim(), time: d.querySelector('[data-mel=works-time]').textContent.trim(),
    pressed: [...d.querySelectorAll('[data-mact=works][aria-pressed=true]')].map(b => b.dataset.w) }; })()"""
results = []


def start(ctx):
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.evaluate("localStorage.setItem('dci-aw-ask', '2')")
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.evaluate(UNLOAD)
    H.open_dashboard(pg, media=False)
    pg.wait_for_selector('[data-el=media] [data-mact=ok]', timeout=30000)
    pg.wait_for_timeout(300)
    return pg, errs


real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = start(ctx)
    # A)
    a1 = pg.evaluate(DLG)
    pg.fill('[data-el=media] [data-mf=text]', '1')
    pg.wait_for_timeout(200)
    a2 = pg.evaluate(DLG)
    pg.locator('[data-el=media] [data-mact=all]').click()
    pg.wait_for_timeout(200)
    print('A) Dialog:', a1)
    print('   nur Medium 1:', a2)
    results.append(a1 is not None and not a1['load'] and a1['state'] == '(2 of them not loaded yet: 2-3)' and a1['works']
                   and a1['n'] == '3 tracks without a work in the chosen media:' and 'about 1 min' in a1['time'] and a1['pressed'] == ['yes']
                   and a2['state'] == '(all of them loaded)' and not a2['works'])
    # B)
    q0 = len(H.WORK_QUERIES)
    pg.locator('[data-el=media] [data-mf=load]').check()
    pg.locator('[data-el=media] [data-mact=works][data-w=no]').click()
    pg.locator('[data-el=media] [data-mact=ok]').click()
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    H.wait_for(pg, f"{LOGS}.some(x => /Medium 3 loaded in the editor/.test(x))", 30)
    pg.wait_for_timeout(1500)
    log = [x for x in pg.evaluate(LOGS) if re.search(r'loaded in the editor|in the background|media choice', x)]
    b1 = [pg.evaluate("window.__clicks"), pg.evaluate("localStorage.getItem('dci-media-load')"),
          pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent.trim()).filter(t => /loaded in the editor/.test(t))"),
          bool(pg.evaluate("document.querySelector('[data-el=works-lookups-off]')")), len(H.WORK_QUERIES) - q0]
    print('B) geklickt, gemerkt, Meldung, Werk-Hinweis, Abfragen:', b1)
    print('   Protokoll:', log)
    results.append(b1[0] == [2, 3] and b1[1] == 'true' and b1[2] == ['2 media are loaded in the editor.'] and b1[3] and b1[4] == 0
                   and 'Media 2-3 are loaded in the editor in the background' in log and 'Medium 2 loaded in the editor' in log
                   and 'Works of the tracks without a work (media choice): Not now' in log)
    print('Fehler:', real(errs))
    results.append(not real(errs))
    pg.close()
    # C) skip the works matrix in the dialog
    pg, errs = start(ctx)
    c0 = pg.evaluate(DLG)
    pg.locator('[data-el=media] [data-mact=works][data-w=skip]').click()
    pg.locator('[data-el=media] [data-mact=ok]').click()
    H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 1", 60)
    pg.wait_for_timeout(1500)
    c1 = [pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')"), (pg.evaluate("(document.querySelector('[data-el=works] .dci-works-skipped') || {}).textContent") or ''),
          pg.evaluate("!document.querySelector('[data-el=works-ask]')")]
    print('C) Dialog vorher:', c0['load'], c0['state'], '| übersprungen:', c1)
    results.append(c0['load'] and c1 == ['true', 'skipped', True])
    pg.evaluate(f"localStorage.removeItem('dci-works-skip:{H.REL}'); localStorage.removeItem('dci-aw-ask'); localStorage.removeItem('dci-media-load')")
    print('Fehler:', real(errs))
    results.append(not real(errs))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
