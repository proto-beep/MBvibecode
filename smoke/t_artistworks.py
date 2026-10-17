"""Import 3.15.0: the tracks without a work are compared with all works of the release's artists, its writers and its
performers (works linked to the artist, and works of the artist's recordings – also covers), in the background.
A) Track 4 (no writers): the release artist's work "Song Four" is offered ("work of Test Band"), under the heading that
   names the artists. Track 3 (Writer Z, nothing found): the bassist recorded "Song Three" (a cover, "Song Three (live)")
   – offered with that recording. Track 2: the writer's own search and his works find the same work – shown once.
B) The order: the release's artists first, then the writers, then the performers; the log names the works read and the
   result; a work chosen from these is linked as one found by the search, and goes into the stored works (3.16.0) of the
   artists credited on its track.
C) Read once per session: a second import (a pasted text) compares again without asking MusicBrainz again (the release
   artist's work is offered again for track 4, whose chosen work was given up).
D) A large catalogue: an artist with 2,500 recordings takes longer than 10 seconds – a message says why; with the
   setting "at most 2,000 per artist" (3.16.0; default 4,000) only the first 2,000 are read, and a message says so.
E) A result of the background does not disturb typing: while a date field of the works matrix is being typed in, the
   matrix is not drawn anew (focus and text stay); once the field is left, the work found is shown."""
import re
from playwright.sync_api import sync_playwright
import harness as H

TB = H.uid('dddddddd', 60)
BASS, GUITAR, WW, WZ = H.ARTISTS[3001][0], H.ARTISTS[3002][0], H.ARTISTS[3007][0], H.ARTISTS[3009][0]
W2, W3, W4 = H.uid('cccccccc', 72), H.uid('cccccccc', 73), H.uid('cccccccc', 74)
H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
H.WORK_SEARCH.append({'id': W2, 'title': H.TITLES[1], 'aliases': [], 'type': 'Song',
                      'relations': [{'target-type': 'artist', 'type': 'writer', 'artist': {'id': WW, 'name': 'Writer W'}}]})
H.ARTIST_WORKS.update({TB: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []},
                            {'id': H.uid('cccccccc', 79), 'title': 'Another Song', 'type': 'Song', 'aliases': []}],
                       WW: [{'id': W2, 'title': H.TITLES[1], 'type': 'Song', 'aliases': []}]})
H.ARTIST_RECORDINGS.update({BASS: [{'title': 'Song Three (live)', 'work': {'id': W3, 'title': H.TITLES[2], 'type': 'Song'}},
                                   {'title': 'Jam', 'work': None}]})
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
SAME = """(i) => { const td = document.querySelector(`tr[data-work="${i}"]`); const s = td && td.querySelector('.dci-same');
  return s ? [s.querySelector('strong').textContent, [...s.querySelectorAll('li')].map(li => [li.querySelector('[data-act=work-pick]').dataset.gid,
    li.querySelector('.dci-sub').textContent.trim()])] : null; }"""


def same(pg, i):
    return pg.evaluate(f"({SAME})({i})")


results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
    pg.wait_for_timeout(300)
    # A)
    s4, s3, s2 = same(pg, 3), same(pg, 2), same(pg, 1)
    print('A) Track 4:', s4)
    print('   Track 3:', s3)
    print('   Track 2:', s2)
    results.append(s4 is not None and s4[1] == [[W4, 'Song – work of Test Band']] and 'release' in s4[0]
                   and s3 is not None and s3[1] == [[W3, 'Song – recorded by Bass Man (“Song Three (live)”)']]
                   and s2 is not None and [g for g, _ in s2[1]] == [W2] and 'by these writers' in s2[0])
    # B) order of the artists, the log, picking a work
    order = []
    for kind, artist, off in H.BROWSES:
        if artist not in order:
            order.append(artist)
    names = {TB: 'Test Band', WW: 'Writer W', WZ: 'Writer Z', BASS: 'Bass Man', GUITAR: 'Guitar Guy'}
    print('B) Reihenfolge:', [names.get(a, a[-3:]) for a in order])
    log = [x for x in pg.evaluate(LOGS) if 'Works of' in x]
    print('   Protokoll:', log)
    ok_order = order[:3] == [TB, WW, WZ] and BASS in order[3:] and GUITAR in order[3:]
    ok_log = ('Works of Test Band: 2 works read (linked to the artist or recorded by them)' in log
              and 'Works of the artists compared: 3 works with the same title as a track (1.2, 1.3, 1.4)' in log
              and not any('Guitar Guy' in x or 'large catalogue' in x for x in log))
    pg.locator('tr[data-work="3"]').locator(f'[data-act=work-pick][data-gid="{W4}"]').evaluate('b => b.click()')
    pg.wait_for_timeout(400)
    picked = [x for x in pg.evaluate(LOGS) if 'chosen for linking' in x]
    # 3.16.0: the work chosen goes into the stored works of the artists credited on the track (Bass Man plays on all tracks)
    pg.wait_for_timeout(500)
    kept = pg.evaluate("""new Promise(r => { const q = indexedDB.open('dci-works', 1); q.onsuccess = () => {
      const t = q.result.transaction('artists').objectStore('artists').get('%s'); t.onsuccess = () => r(t.result ? t.result.works.map(w => w[0]) : null); }; })""" % BASS)
    print('   gespeicherte Werke von Bass Man:', kept)
    print('   gewählt:', picked, '| Track 4 hat Werk:', pg.locator('tr[data-work="3"]').locator('.dci-same').count() == 0)
    results.append(ok_order and ok_log and picked == ['Track 1.4: work “Song Four” chosen for linking'] and kept and W4 in kept and W3 in kept
                   and pg.locator('tr[data-work="3"]').locator('.dci-same').count() == 0)
    # C) a second import: compared again from what was read (the work chosen for track 4 is given up before)
    pg.locator('tr[data-work="3"] [data-act=work-unplan]').evaluate('b => b.click()')
    pg.wait_for_timeout(300)
    n0 = len(H.BROWSES)
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', 'Bass – Bass Man')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, f"{LOGS}.filter(x => /Works of the artists compared/.test(x)).length >= 2", 60)
    pg.wait_for_timeout(500)
    s4b = same(pg, 3)
    print('C) neue Anfragen:', len(H.BROWSES) - n0, '| Track 4:', s4b)
    results.append(len(H.BROWSES) == n0 and s4b is not None and s4b[1] == [[W4, 'Song – work of Test Band']])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()

    # D) a large catalogue (a page of its own: the works read are kept per session)
    H.RELEASE_AC[:] = []
    H.ARTIST_WORKS.clear()
    H.ARTIST_RECORDINGS.clear()
    H.ARTIST_RECORDINGS[GUITAR] = 2500
    H.BROWSES.clear()
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    # 3.16.0: at most 2,000 works and recordings per artist (the setting, stored; read when the script starts)
    pg.evaluate("localStorage.setItem('dci-aw-max', '2000')")
    pg.reload(); pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 120)
    msgs = [re.sub(r'\s+', ' ', m) for m in pg.locator('.dci-msg').all_inner_texts() if 'Guitar Guy' in m]
    log = [x for x in pg.evaluate(LOGS) if 'Guitar Guy' in x]
    recs = [off for kind, a, off in H.BROWSES if kind == 'recording' and a == GUITAR]
    print('D) Meldungen:', msgs)
    print('   Protokoll:', log)
    print('   Aufnahmen gelesen bis Offset:', max(recs), '| Anfragen:', len(recs))
    results.append(any('takes a while: a large catalogue (2500 recordings' in m for m in msgs)
                   and any('Guitar Guy has 2500 works and recordings; only the first 2000 were compared' in m for m in msgs)
                   and any('a large catalogue' in x for x in log) and any('only the first 2000 compared' in x for x in log)
                   and len(recs) == 20 and max(recs) == 1900)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()

    # E) typing in the works matrix while the comparison finds a work
    H.ARTIST_RECORDINGS.clear()
    DRUM = H.ARTISTS[3004][0]
    H.ARTIST_RECORDINGS[DRUM] = [{'title': 'Song Four', 'work': {'id': W4, 'title': H.TITLES[3], 'type': 'Song'}}]
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.locator('[data-colhead] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
    pg.locator('[data-f=cd-by]').first.click()
    pg.keyboard.type('19', delay=100)
    H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
    pg.keyboard.type('99', delay=100)
    st = pg.evaluate("(() => { const a = document.activeElement; return [a && a.dataset ? a.dataset.f : '', a && a.value]; })()")
    during = same(pg, 3)
    print('E) beim Tippen:', st, '| Track 4:', during, '|', [x for x in pg.evaluate(LOGS) if 'compared' in x])
    pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(1200)
    after = same(pg, 3)
    print('   nach dem Verlassen – Track 4:', after)
    results.append(st == ['cd-by', '1999'] and during is None and after is not None and after[1] == [[W4, 'Song – recorded by Drum Guy (“Song Four”)']])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
