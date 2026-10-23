"""Credits Importer 3.20.0 / 3.21.1: the media dialog loads the chosen media in MB's relationship editor in the background,
and asks about the works there when many tracks have none (collected items 34 and 44).
Four media (1, 2, 1, 0 tracks: medium 4 has no tracklist in MusicBrainz, like CDs 2–13 of "Eternal"); MB's editor has
loaded medium 1 only. [3.21.1] The editor is built as MusicBrainz builds it (musicbrainz-server, usePagedMediumTable):
each medium a link `a.expand-medium#disc<n>` "2 ▶ CD" (number before the format, no aria-expanded), its tracks in the
next tbody (hidden while folded), "Expand all mediums", and a medium shown in part with "Load all tracks..." (medium 2:
MB loads one track, the link loads the rest).
A) The dialog: "This release has 4 media", medium 4 named as without a tracklist; "Load the chosen media …" (off at
   first) says how many of the chosen media are not loaded yet; the works box ("3 tracks without a work", "Look up works"
   pressed) – both follow the choice (medium 1 alone: no box).
B) Ticked, "Not now", Import: all media chosen → MB's "Expand all mediums"; medium 2's "Load all tracks..." clicked; the
   loading starts before the source is read (log before "Media chosen"); log, message, the tick is remembered; no work
   lookups.
C) "Skip works matrix" in the dialog: the matrix is skipped for this release (its rows on "Skip"), not asked again.
D) Media 1 and 3 only: their own toggles (#disc3), no "Expand all mediums".
E) The web service leaves out the tracks of medium 2 and the relationships of medium 1's recordings (as MusicBrainz does
   with very many recordings): both are read from MB's own pages of tracks (/ws/js/tracks/<medium id>) – the dialog
   still offers medium 2 with its 2 tracks, and track 1 keeps its work (3 tracks without a work, not 4); the log names it."""
import re
from playwright.sync_api import sync_playwright
import harness as H

H.MEDIA = [1, 2, 1, 0]
orig = H.discogs_release


def rel():
    d = orig()
    for i, t in enumerate(d['tracklist']):
        t['position'] = ['1-1', '2-1', '2-2', '3-1'][i]
    return d


H.discogs_release = rel
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
# MB's editor as MusicBrainz builds it: media 2 and 3 folded and not loaded; medium 2 is loaded in part first
EDITOR = """(() => { const st = MB.relationshipEditor.state; window.__saved = {}; window.__clicks = []; window.__more = []; window.__all = 0;
  for (const m of st.entity.mediums) if (m.position > 1 && m.track_count) { window.__saved[m.id] = m.tracks; m.tracks = null; }
  const box = document.createElement('div');
  box.innerHTML = '<button type="button" id="expand-all-mediums">Expand all mediums</button><table id="mb-media"></table>';
  const t = box.querySelector('table');
  for (const m of st.entity.mediums) {
    const open = m.position === 1;
    t.insertAdjacentHTML('beforeend', `<tbody><tr class="subh"><td></td><td><input type="checkbox" class="medium-recordings"> <a class="expand-medium"
      href="/medium/x${m.position}" id="disc${m.position}"><span>${m.position}</span><span class="expand-triangle">${open ? '\\u25BC' : '\\u25B6'}</span>CD</a></td></tr></tbody>
      <tbody${open ? '' : ' style="display: none"'}></tbody>`);
  }
  document.getElementById('editor').append(box);
  const load = (m) => setTimeout(() => {
    const body = document.getElementById('disc' + m.position).closest('tbody').nextElementSibling;
    const all = window.__saved[m.id] || [];
    if (m.position === 2) {
      st.loadedTracks.set(m.id, all.slice(0, 1));
      body.innerHTML = '<tr><td>This medium has too many tracks to load at once; <a class="load-tracks" href="#">Load all tracks...</a></td></tr>';
    } else st.loadedTracks.set(m.id, all);
  }, 400);
  const expand = (m) => { const a = document.getElementById('disc' + m.position); const tri = a.querySelector('.expand-triangle');
    if (tri.textContent === '\\u25BC') return; tri.textContent = '\\u25BC'; a.closest('tbody').nextElementSibling.style.display = '';
    if (window.__saved[m.id]) load(m); };
  box.addEventListener('click', (e) => {
    const a = e.target.closest('a.expand-medium, a.load-tracks, #expand-all-mediums'); if (!a) return; e.preventDefault();
    if (a.id === 'expand-all-mediums') { window.__all++; st.entity.mediums.forEach(expand); return; }
    if (a.classList.contains('load-tracks')) { const m = st.entity.mediums.find((x) => x.position === 2); window.__more.push(2);
      setTimeout(() => { st.loadedTracks.set(m.id, window.__saved[m.id]); a.closest('tr').remove(); }, 400); return; }
    const p = Number(a.id.slice(4)); window.__clicks.push(p); expand(st.entity.mediums.find((x) => x.position === p));
  });
})()"""
DLG = """(() => { const d = document.querySelector('[data-el=media]'); if (!d || d.hidden) return null; const w = d.querySelector('[data-mel=works]');
  return { intro: d.querySelector('.dci-media-body p').textContent.trim(), empty: (d.querySelector('[data-mel=empty]') || {}).textContent || '',
    media: [...d.querySelectorAll('[data-mact=toggle]')].map(b => b.textContent.trim()),
    load: d.querySelector('[data-mf=load]').checked, state: d.querySelector('[data-mel=load]').textContent.trim(), works: !w.hidden,
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
    pg.evaluate(EDITOR)
    H.open_dashboard(pg, media=False)
    pg.wait_for_selector('[data-el=media] [data-mact=ok]', timeout=30000)
    pg.wait_for_timeout(300)
    return pg, errs


def loaded(pg, n):
    H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 1", 60)
    for m in n:
        H.wait_for(pg, f"{LOGS}.some(x => /Medium {m} (loaded|did not load) in the editor/.test(x))", 40)
    pg.wait_for_timeout(1000)


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
    print('   nur Medium 1:', a2['state'], a2['works'])
    results.append(a1 is not None and a1['intro'].startswith('This release has 4 media.') and len(a1['media']) == 3
                   and a1['empty'].startswith('Without a tracklist in MusicBrainz: medium 4 – add its tracks in the release editor first')
                   and not a1['load'] and a1['state'] == '(2 of them not loaded yet: 2-3)' and a1['works']
                   and a1['n'] == '3 tracks without a work in the chosen media:' and 'about 1 min' in a1['time'] and a1['pressed'] == ['yes']
                   and a2['state'] == '(all of them loaded)' and not a2['works'])
    # B)
    q0 = len(H.WORK_QUERIES)
    pg.locator('[data-el=media] [data-mf=load]').check()
    pg.locator('[data-el=media] [data-mact=works][data-w=no]').click()
    pg.locator('[data-el=media] [data-mact=ok]').click()
    loaded(pg, [2, 3])
    logs = pg.evaluate(LOGS)
    bg = next((i for i, x in enumerate(logs) if 'in the background' in x), 99)
    chosen = next((i for i, x in enumerate(logs) if x.startswith('Works of the tracks without a work')), -1)
    log = [x for x in logs if re.search(r'loaded in the editor|in the background|media choice|no tracklist', x)]
    b1 = [pg.evaluate("window.__all"), pg.evaluate("window.__clicks"), pg.evaluate("window.__more"), pg.evaluate("localStorage.getItem('dci-media-load')"),
          pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent.trim()).filter(t => /loaded in the editor/.test(t))"),
          bool(pg.evaluate("document.querySelector('[data-el=works-lookups-off]')")), len(H.WORK_QUERIES) - q0, bg < chosen]
    print('B) Alle aufklappen, Klicks, „Load all tracks“, gemerkt, Meldung, Werk-Hinweis, Abfragen, vor dem Lesen der Quelle:', b1)
    print('   Protokoll:', log)
    results.append(b1 == [1, [], [2], 'true', ['2 media are loaded in the editor.'], True, 0, True]
                   and 'Media 2-3 are loaded in the editor in the background' in log and 'Medium 2 loaded in the editor' in log
                   and 'Medium 3 loaded in the editor' in log and 'Works of the tracks without a work (media choice): Not now' in log
                   and 'Medium 4 has no tracklist in MusicBrainz – nothing can be imported for it' in log)
    print('Fehler:', real(errs))
    results.append(not real(errs))
    pg.close()
    # C) skip the works matrix in the dialog
    pg, errs = start(ctx)
    c0 = pg.evaluate(DLG)
    pg.locator('[data-el=media] [data-mact=works][data-w=skip]').click()
    pg.locator('[data-el=media] [data-mact=ok]').click()
    loaded(pg, [2, 3])
    c1 = [pg.evaluate(f"localStorage.getItem('dci-works-skip:{H.REL}')"), (pg.evaluate("(document.querySelector('[data-el=works] .dci-works-skipped') || {}).textContent") or ''),
          pg.evaluate("!document.querySelector('[data-el=works-ask]')")]
    print('C) Dialog vorher:', c0['load'], c0['state'], '| übersprungen:', c1)
    results.append(c0['load'] and c1 == ['true', 'skipped', True])
    pg.evaluate(f"localStorage.removeItem('dci-works-skip:{H.REL}')")
    pg.close()
    # D) media 1 and 3 only: the toggle of medium 3, not "Expand all mediums"
    pg, errs = start(ctx)
    pg.fill('[data-el=media] [data-mf=text]', '1, 3')
    pg.wait_for_timeout(200)
    pg.locator('[data-el=media] [data-mact=ok]').click()
    loaded(pg, [3])
    d1 = [pg.evaluate("window.__all"), pg.evaluate("window.__clicks"), pg.evaluate("window.__more")]
    print('D) Medien 1 und 3 – alle aufklappen, Klicks, „Load all tracks“:', d1)
    results.append(d1 == [0, [3], []])
    pg.close()
    # E) the web service leaves out the tracks of medium 2 and the relationships of medium 1
    H.WS_DROP_TRACKS.add(2)
    H.WS_NO_RELS.add(1)
    pg, errs = start(ctx)
    e0 = pg.evaluate(DLG)
    logs = pg.evaluate(LOGS)
    e1 = [x for x in logs if re.search(r'web service left out|read from the relationship editor', x)]
    print('E) Dialog:', e0['media'], e0['n'], '| Seiten:', H.JS_TRACKS_CALLS, '| Protokoll:', e1)
    results.append(e0['media'] == ['Medium 1 · CD (1 track)', 'Medium 2 · CD (2 tracks)', 'Medium 3 · CD (1 track)']
                   and e0['n'] == '3 tracks without a work in the chosen media:' and (4501, 1) in H.JS_TRACKS_CALLS and (4502, 1) in H.JS_TRACKS_CALLS
                   and e1 == ['MusicBrainz’s web service left out tracks or relationships of medium 1-2: read from the relationship editor',
                              'Medium 1: 1 track read from the relationship editor', 'Medium 2: 2 tracks read from the relationship editor'])
    pg.locator('[data-el=media] [data-mact=ok]').click()
    H.wait_for(pg, f"{LOGS}.filter(x => /Import complete/.test(x)).length >= 1", 60)
    pg.wait_for_timeout(800)
    pg.evaluate("localStorage.removeItem('dci-aw-ask'); localStorage.removeItem('dci-media-load')")
    print('Fehler:', real(errs))
    results.append(not real(errs))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
