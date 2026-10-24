"""Credits Importer 3.17.1 / Companion 1.8.1: credits switched off and on on Bandcamp (collected item 5); since 3.17.5 /
1.8.3 with a click on the mark itself (collected item 20, before: ⊘).
A) The pointer resting on a mark shows its row in the dashboard (no line in the log); a click on the mark switches the
   credit off: its row goes to "Skip" in the dashboard and says so, its mark is greyed (–) and – as it is the only credit
   of its part – the part of the line too ("mixed by Bob Mix"); the log says it.
B) A group of marks ("Mixed and mastered by Mark Master"): one credit switched off greys only its mark; both switched off
   grey the text too. A click on a switched-off mark switches it on again: the row has its level back.
C) Kept for the release: after loading the edit page again and importing anew, the credits switched off are off again.
D) Choosing a level in the dashboard switches a credit on again (on Bandcamp too).
E) "Delete stored import" forgets what was switched off."""
import re
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9120, 'trumpet', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
BAND = 'https://testband.bandcamp.com'
ALBUM = f'{BAND}/album/testalbum'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND + '/'] = H.ARTISTS[3040]
H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
CREDITS = 'Written by Jane Roe, mixed by Bob Mix\nMixed and mastered by Mark Master\nTest Band – guitar\nTrumpet: Peter Evans'
TRACKS = [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]
H.BC_PAGES[ALBUM] = H.bc_html({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS}, 'trackinfo': TRACKS}, ALBUM)
for t in TRACKS:
    H.BC_PAGES[f'{BAND}{t["title_link"]}'] = H.bc_html({'artist': 'Test Band', 'album_url': '/album/testalbum', 'current': {'title': t['title'], 'credits': ''},
                                                        'trackinfo': [t]}, f'{BAND}{t["title_link"]}')
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
MARKS = """(() => { const root = document.querySelector('.tralbum-credits');
  return [...root.querySelectorAll('.dci-dg-mark')].map(m => [m.textContent, m.title.split(':')[0], m.classList.contains('dci-mark-off')]); })()"""
GREY = "[...document.querySelectorAll('.tralbum-credits .dci-bc-offtext')].map(x => x.textContent).join('|').replace(/\\s+/g, ' ')"
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


def row(pg, name, role):
    return pg.evaluate("""([n, r]) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === n);
      const tr = g && [...g.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === r);
      if (!tr) return null; const lv = tr.querySelector('[data-act=level][aria-pressed=true]');
      return [tr.dataset.row, lv ? lv.dataset.level : '', !!tr.querySelector('.dci-srcoff')]; }""", [name, role])


def toggle(bc, k):
    """Clicks the k-th mark (3.17.5: the mark itself switches its credit)."""
    bc.locator('.tralbum-credits .dci-dg-mark').nth(k).click()


def start(p):
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=True, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    return b, ctx, pg, errs


real = lambda es: [e for e in es if 'Synchronous XHR in page dismissal' not in e]

with sync_playwright() as p:
    b, ctx, pg, errs = start(p)
    bc, bcerr = H.open_bandcamp(ctx, ALBUM)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark').length >= 6")
    bc.wait_for_timeout(500)
    # A) the pointer resting on a mark shows its row; a click switches the credit off
    bc.locator('.tralbum-credits .dci-dg-mark').nth(1).hover()
    H.wait_for(pg, "document.querySelectorAll('tr.dci-flash').length > 0", 10)
    hidden = pg.evaluate("[...document.querySelectorAll('tr.dci-flash')].map(t => t.querySelector('.dci-drole').textContent.trim())")
    shown = [x for x in pg.evaluate(LOGS) if 'From Bandcamp' in x]
    bc.mouse.move(5, 5)
    level0 = row(pg, 'Bob Mix', 'Mixed By')[1]
    toggle(bc, 1)
    H.wait_for(pg, f"{LOGS}.some(x => /Bob Mix – Mixed By switched off/.test(x))", 15)
    poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][1].classList.contains('dci-mark-off')")
    a1 = row(pg, 'Bob Mix', 'Mixed By')
    a2 = bc.evaluate(MARKS)[1]
    a3 = bc.evaluate(GREY)
    print('A) Zeiger auf der Marke → Zeile:', hidden, '| Protokoll:', shown, '| Zeile:', a1, '(vorher', level0, ') | Marke:', a2, '| grau:', a3)
    results.append(hidden == ['Mixed By'] and shown == [] and a1[1] == 'skip' and a1[2] and a2 == ['–', 'Mixed By', True] and a3 == 'mixed by Bob Mix')
    # B) a group: one off, then both, then one on again
    toggle(bc, 3)
    poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][3].classList.contains('dci-mark-off')")
    b1 = [bc.evaluate(MARKS)[2:4], bc.evaluate(GREY)]
    toggle(bc, 2)
    poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][2].classList.contains('dci-mark-off')")
    bc.wait_for_timeout(300)
    b2 = bc.evaluate(GREY)
    master = row(pg, 'Mark Master', 'Mastered By')
    toggle(bc, 3)
    poll(bc, "![...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][3].classList.contains('dci-mark-off')")
    bc.wait_for_timeout(300)
    b3 = [row(pg, 'Mark Master', 'Mastered By'), bc.evaluate(GREY)]
    print('B) eins aus:', b1, '| beide aus:', b2, master, '| wieder an:', b3)
    results.append(b1[0] == [['○', 'Mixed By', False], ['–', 'Mastered By', True]] and b1[1] == 'mixed by Bob Mix'
                   and b2 == 'mixed by Bob Mix|Mixed and mastered by Mark Master' and master[1] == 'skip'
                   and b3[0][1] == 'release' and not b3[0][2] and b3[1] == 'mixed by Bob Mix')
    # C) kept for the release
    pg.evaluate("Object.keys(sessionStorage).filter(k => k.startsWith('dci-')).forEach(k => sessionStorage.removeItem(k))")
    pg.reload()
    H.with_companion(pg)
    pg.add_script_tag(content=H.GM_XHR_SHIM)
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(500)
    c1 = [row(pg, 'Bob Mix', 'Mixed By'), row(pg, 'Mark Master', 'Mixed By'), row(pg, 'Mark Master', 'Mastered By')]
    poll(bc, "[...document.querySelectorAll('.tralbum-credits .dci-dg-mark.dci-mark-off')].length === 2")
    c2 = [m[2] for m in bc.evaluate(MARKS)]
    print('C) nach Neuladen:', c1, '| Marken aus:', c2)
    results.append([x[1] for x in c1] == ['skip', 'skip', 'release'] and c2 == [False, True, True, False, False, False])
    # D) a level chosen in the dashboard switches it on
    rid = row(pg, 'Bob Mix', 'Mixed By')[0]
    pg.locator(f'tr[data-row="{rid}"] [data-act=level][data-level=recording]').click()
    poll(bc, "![...document.querySelectorAll('.tralbum-credits .dci-dg-mark')][1].classList.contains('dci-mark-off')")
    d1 = [row(pg, 'Bob Mix', 'Mixed By'), [m[2] for m in bc.evaluate(MARKS)], [x for x in pg.evaluate(LOGS) if 'switched on' in x][-1:]]
    print('D) Ebene gewählt:', d1)
    results.append(d1[0][1] == 'recording' and not d1[0][2] and d1[1] == [False, False, True, False, False, False]
                   and d1[2] == ['Bandcamp: Bob Mix – Mixed By switched on again'])
    # E) "Delete stored import"
    H.src_menu(pg, 'forget-open')
    pg.locator('[data-act=forget-do]').click()
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(1500)
    e1 = [row(pg, 'Mark Master', 'Mixed By'), pg.evaluate(f"localStorage.getItem('dci-src-off:{H.REL}')")]
    poll(bc, "document.querySelectorAll('.tralbum-credits .dci-dg-mark.dci-mark-off').length === 0")
    print('E) nach „Gespeicherten Import löschen“:', e1)
    results.append(e1[0][1] != 'skip' and e1[1] is None)
    print('Fehler:', real(errs), real(bcerr))
    results.append(not real(errs) and not real(bcerr))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
