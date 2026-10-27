"""Media: a release with several media, loading media in the editor, the media choice (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: media, mediaload, mediasel – each the former smoke/t_<case>.py, unchanged; `python3 t_media_choice.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_media():
    """Release with two media: "CD2, tracks 1–3", "Disc 1", medium headings in the track form, and "+ new track
    group" with a whole medium or one group per medium."""
    import re
    import zooid
    from common_rows import cells
    zooid.setup('CD2, tracks 1–3 recorded May 1, 2020 at Brooklyn Recording.\nDisc 1 recorded April 4, 2020.')
    H.MEDIA = [5, 5]
    orig = H.discogs_release


    def rel():
        d = orig()
        for i, t in enumerate(d['tracklist']):
            t['position'] = f'{1 + i // 5}-{1 + i % 5}'
        for e in d['extraartists']:
            if e['tracks']:
                e['tracks'] = '2-1 to 2-5'
        return d


    H.discogs_release = rel
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click('[data-el=datefind] summary')
        items = [re.sub(r'\s+', ' ', i)[:90] for i in pg.locator('[data-el=datefind-list] li').all_inner_texts()]
        print('Gefunden:', items)
        print('Matrix (Vorschläge):', cells(pg)['performance'])
        print('Track-Pool:', pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
        opts = pg.locator('[data-f=tg-new-pick] option').all_inner_texts()
        print('Auswahl „+ neue Track-Gruppe“:', opts)
        pg.select_option('[data-f=tg-new-pick]', 'pick'); pg.wait_for_timeout(200)
        print('Medium-Überschriften im Formular:', pg.locator('.dci-track-form [data-act=tg-medium]').all_inner_texts())
        pg.locator('.dci-track-form [data-act=tg-medium]').nth(1).click(); pg.wait_for_timeout(200)
        checked = pg.evaluate("[...document.querySelectorAll('.dci-track-form input[data-f=tg-track]:checked')].map(c => Number(c.dataset.i))")
        print('Klick auf Medium 2 hakt an (Index):', checked)
        pg.click('[data-act=tg-cancel]'); pg.wait_for_timeout(100)
        pg.select_option('[data-f=tg-new-pick]', 'all'); pg.wait_for_timeout(200)
        groups = [re.sub(r'\s+', ' ', g) for g in pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts()]
        print('Nach „alle Medien“ (Medium 1 gibt es schon als „Tracks 1-1–1-5“):', groups)
        pg.select_option('[data-f=tg-new-pick]', 'm:2'); pg.wait_for_timeout(200)
        again = len(pg.locator('.dci-tracks-bar .dci-chip-main').all_inner_texts())
        ok = ('tracks 2-1–2-3' in items[0] and checked == [5, 6, 7, 8, 9] and len(opts) == 5 and len(groups) == 3
              and 'Medium 2 · CD 5 tracks' in groups and again == len(groups)
              and [c[1] for c in cells(pg)['performance']] == [['Tracks 2-1–2-3'], ['Tracks 1-1–1-5']])
        print('Ergebnis:', 'OK' if ok else 'FEHLER', '| Fehler:', errs)
        b.close()


def case_mediaload():
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
    C) "Skip works" ([3.32.1] until then "Skip works matrix") in the dialog: the matrix is skipped for this release (its rows on "Skip"), not asked again.
    D) Media 1 and 3 only: their own toggles (#disc3), no "Expand all mediums".
    E) The web service leaves out the tracks of medium 2 and the relationships of medium 1's recordings (as MusicBrainz does
       with very many recordings): both are read from MB's own pages of tracks (/ws/js/tracks/<medium id>) – the dialog
       still offers medium 2 with its 2 tracks, and track 1 keeps its work (3 tracks without a work, not 4); the log names it."""
    import re

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


def case_mediasel():
    """Media choice before the import (release with three media): "All" with the release level is the import as before;
    media 2-3 without the release level: only their credits, credits without tracks on their tracks, nothing on the
    release (group), works matrix and medium filter only with those media; "Choose media …" asks again (after a
    confirmation); a remembered choice is preselected next time (still asked); unknown media in the text field;
    cancelling keeps the import, Escape on the first question imports nothing (a message offers the question again)."""
    import re

    H.MEDIA = [2, 1, 1]
    orig = H.discogs_release


    def rel():
        d = orig()
        pos = ['1-1', '1-2', '2-1', '3-1']
        for i, t in enumerate(d['tracklist']):
            t['position'] = pos[i]
        for e in d['extraartists']:
            if e['name'] == 'Keys Guy':
                e['tracks'] = '2-1'
            if e['name'] == 'Drum Guy':
                e['tracks'] = '1-1 to 1-2'
        return d


    H.discogs_release = rel
    DLG = '[data-el=media]'
    STATE = """(() => {
  const groups = [...document.querySelectorAll('#dci-overlay section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent,
    [...g.querySelectorAll('tr.dci-row')].map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1] + ((tr.querySelector('[data-tcount]') || {}).textContent ? ':' + tr.querySelector('[data-tcount]').textContent.trim() : ''))]);
  const matrix = [...new Set([...document.querySelectorAll('.dci-matrix tr[data-work]')].map(tr => Number(tr.dataset.work)))];
  const cols = [...document.querySelectorAll('[data-colhead]')].map(h => h.dataset.colhead.startsWith('mb:') ? 'mb' : (h.querySelector('.dci-mx-name, strong') || h).textContent.trim().slice(0, 20));
  const filter = [...document.querySelectorAll('[data-f=medium-filter] option')].map(o => o.textContent.trim());
  const now = (document.querySelector('.dci-media-now') || {}).textContent || '';
  return { groups, matrix, cols, filter, now };
})()"""
    results = []


    def dialog(pg):
        pg.wait_for_selector(f'{DLG} [data-mact=ok]', timeout=20000)
        return pg.evaluate(f"""(() => {{ const d = document.querySelector('{DLG}');
      return {{ pressed: [...d.querySelectorAll('[data-mact=toggle]')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => Number(b.dataset.m)),
        text: d.querySelector('[data-mf=text]').value, release: d.querySelector('[data-mf=release]').checked,
        remember: d.querySelector('[data-mf=remember]').checked, sum: d.querySelector('[data-mel=sum]').textContent,
        err: d.querySelector('[data-mel=err]').hidden ? '' : d.querySelector('[data-mel=err]').textContent,
        ok: !d.querySelector('[data-mact=ok]').disabled, hint: d.querySelector('.dci-media-body > p.dci-sub').textContent }}; }})()""")


    def done(pg):
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(1500)


    def names(st):
        return sorted(g[0] for g in st['groups'])


    def clear_log(pg):
        pg.evaluate("document.querySelector('#dci-log [data-log-act=clear]').click()")


    def ok_click(pg):
        # the log is kept in the session: cleared, so "Import complete" is the one of this import
        clear_log(pg)
        pg.click(f'{DLG} [data-mact=ok]')


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg, media=False)

        # A) the question, preselected "All" with the release level: the import as before
        q = dialog(pg)
        print('A1) Frage:', q)
        ok_a = q['pressed'] == [1, 2, 3] and q['text'] == '1-3' and q['release'] and not q['remember'] and q['sum'] == '3 of 3 media · 4 tracks' and q['ok']
        ok_click(pg)
        done(pg)
        base = pg.evaluate(STATE)
        print('A2) alle Medien:', base)
        ok_a = ok_a and 'Drum Guy' in names(base) and 'Photo Guy' in names(base) and 'Sony' in names(base) and base['matrix'] == [0, 1, 2, 3] \
            and base['now'] == 'all media with the release level' and base['filter'][0] == 'all' and len(base['filter']) == 4
        results.append(ok_a)

        # B) "Choose media …": media 2-3 without the release level
        pg.click('[data-act=media-choose]')
        q = dialog(pg)
        pg.fill(f'{DLG} [data-mf=text]', '2-3')
        pg.click(f'{DLG} [data-mf=release]')
        q = dialog(pg)
        print('B1) Frage mit „2-3“, ohne Release-Ebene:', q['pressed'], q['release'], q['sum'])
        ok_b = q['pressed'] == [2, 3] and not q['release'] and q['sum'] == '2 of 3 media · 2 tracks'
        ok_click(pg)
        done(pg)
        st = pg.evaluate(STATE)
        print('B2) Zeilen:', st['groups'])
        print('    Matrix:', st['matrix'], st['cols'], '| Filter:', st['filter'], '| Auswahl:', st['now'])
        g = dict(st['groups'])
        logs = pg.locator('#dci-log li').all_inner_texts()
        print('    Protokoll:', [x for x in logs if 'Media' in x])
        ok_b = ok_b and names(st) == ['Abbey Road Studios', 'Bass Man', 'Bob Producer', 'Ghost Pub', 'Guitar Guy', 'Keys Guy', 'Other Pub', 'Pub Co', 'Writer Z'] \
            and g['Bass Man'] == ['recording:2 of 2 tracks'] and g['Keys Guy'] == ['recording:1 of 2 tracks'] and g['Abbey Road Studios'] == ['recording:2 of 2 tracks'] \
            and st['matrix'] == [2, 3] and not any('Writer W' in c for c in st['cols']) and any('Writer Z' in c for c in st['cols']) \
            and st['now'] == 'media 2-3 without the release level' and len(st['filter']) == 3 and not any(o.startswith('Medium 1 ') for o in st['filter']) \
            and any('Media chosen: media 2-3 without the release level' in x for x in logs)
        results.append(ok_b)

        # C) only medium 1 (buttons), with the release level, remembered; cancelling later keeps that import
        pg.click('[data-act=media-choose]')
        dialog(pg)
        pg.click(f'{DLG} [data-mact=none]')
        q0 = dialog(pg)
        pg.click(f'{DLG} [data-mact=toggle][data-m="1"]')
        pg.check(f'{DLG} [data-mf=remember]')
        q = dialog(pg)
        print('C1) „Keine“:', q0['text'] or '–', q0['ok'], '| Medium 1:', q['text'], q['pressed'], q['release'])
        ok_c = q0['text'] == '' and q0['ok'] and q['text'] == '1' and q['pressed'] == [1] and q['release']
        ok_click(pg)
        done(pg)
        st = pg.evaluate(STATE)
        print('C2) Zeilen:', names(st), '| Matrix:', st['matrix'], '| Filter:', st['filter'], '| Auswahl:', st['now'])
        ok_c = ok_c and names(st) == ['Abbey Road Studios', 'Ann Rep', 'Bass Man', 'Bob Producer', 'Drum Guy', 'Ghost Pub', 'Guitar Guy', 'Other Pub', 'Photo Guy', 'Pub Co', 'Sony', 'Writer W'] \
            and st['matrix'] == [0, 1] and st['filter'] == [] and st['now'] == 'media 1 with the release level'
        stored = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-media-sel'))['{H.REL}']")
        print('    gemerkt:', stored)
        ok_c = ok_c and stored['media'] == [1] and stored['release'] is True
        pg.click('[data-act=media-choose]')
        q = dialog(pg)
        print('C3) erneut gefragt, vorausgewählt:', q['pressed'], q['remember'], '|', q['hint'][:40])
        pg.click(f'{DLG} [data-mact=cancel]'); pg.wait_for_timeout(300)
        st2 = pg.evaluate(STATE)
        ok_c = ok_c and q['pressed'] == [1] and q['remember'] and q['hint'].startswith('Preselected') and names(st2) == names(st) \
            and pg.locator(DLG).is_hidden()
        results.append(ok_c)

        # D) after reloading: still asked (remembered choice preselected); unknown media; Escape imports nothing
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg, media=False)
        q = dialog(pg)
        pg.fill(f'{DLG} [data-mf=text]', '1-4, x')
        bad = dialog(pg)
        pg.fill(f'{DLG} [data-mf=text]', '1, 3')
        q2 = dialog(pg)
        print('D1) nach Neuladen:', q['pressed'], q['remember'], '| „1-4, x“:', bad['err'], bad['ok'], '| „1, 3“:', q2['pressed'], q2['ok'])
        ok_d = q['pressed'] == [1] and q['remember'] and 'Not a medium of this release: 4, x (media: 1-3)' == bad['err'] and not bad['ok'] \
            and q2['pressed'] == [1, 3] and q2['ok'] and q2['err'] == ''
        pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
        msg = pg.locator('[data-el=msgs]').inner_text()
        print('D2) Escape:', pg.locator(DLG).is_hidden(), '| Nachricht:', re.sub(r'\s+', ' ', msg), '| Zeilen:', pg.locator('#dci-overlay section.dci-group').count())
        ok_d = ok_d and pg.locator(DLG).is_hidden() and 'Import cancelled' in msg and pg.locator('#dci-overlay section.dci-group').count() == 0
        pg.click('[data-el=msgs] [data-act=media-choose]')
        dialog(pg)
        pg.click(f'{DLG} [data-mact=all]')
        pg.uncheck(f'{DLG} [data-mf=remember]')
        ok_click(pg)
        done(pg)
        st = pg.evaluate(STATE)
        same = sorted(map(str, st['groups'])) == sorted(map(str, base['groups'])) and st['matrix'] == base['matrix'] and st['cols'] == base['cols']
        if not same:
            print('   vorher:', base); print('   jetzt: ', st)
        print('D3) „Alle“ mit Release-Ebene wie vorher:', same, '| gemerkt:', pg.evaluate("localStorage.getItem('dci-media-sel')"))
        ok_d = ok_d and same and pg.evaluate("localStorage.getItem('dci-media-sel')") is None
        results.append(ok_d)
        print('Fehler:', errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
