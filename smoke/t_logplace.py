"""Log placement ("Place:" in the log's head): beside the edit note (right / left: the edit note keeps its place and
gets the rest of its width, the log takes its height and follows it), above it (full width, the dragged height is
remembered) or its own window again. Too narrow beside it → above, with a hint; MusicBrainz drawing the edit note
anew → the log follows; the place is remembered after reloading; "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults") → window."""
from playwright.sync_api import sync_playwright
import harness as H

# MusicBrainz's edit note is as wide as the form
CSS = '#edit-note-text { width: 100%; height: 90px; box-sizing: border-box; }'
GEOM = """(() => { const r = (el) => { const b = el.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; };
  const log = document.getElementById('dci-log'); const note = document.getElementById('edit-note-text');
  return { log: r(log), note: r(note), cls: log.className, parent: log.parentElement.id || log.parentElement.tagName, before: note.previousElementSibling === log,
    pos: getComputedStyle(log).position, float: getComputedStyle(log).cssFloat, clear: !!document.getElementById('dci-log-clear'),
    noteW: note.style.width, stored: localStorage.getItem('dci-log-place') }; })()"""
results = []


def place(pg, value):
    pg.evaluate(f"""() => {{ const s = document.querySelector('#dci-log [data-log-f=place]'); s.value = '{value}';
      s.dispatchEvent(new Event('change', {{ bubbles: true }})); }}""")
    pg.wait_for_timeout(300)
    return pg.evaluate(GEOM)


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.add_style_tag(content=CSS)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    g0 = pg.evaluate(GEOM)
    opts = pg.locator('#dci-log [data-log-f=place] option').all_inner_texts()
    print('0) Fenster:', g0['pos'], g0['parent'], '| Auswahl:', opts)
    ok0 = g0['pos'] == 'fixed' and g0['parent'] == 'BODY' and opts == ['window', 'left of edit note', 'right of edit note', 'above edit note']

    # A) right of the edit note
    g = place(pg, 'right')
    print('A1) rechts:', g)
    ok_a = g['before'] and 'dci-log-dock-right' in g['cls'] and g['float'] == 'right' and g['pos'] == 'relative' and g['clear'] \
        and g['note'][0] + g['note'][2] <= g['log'][0] and abs(g['note'][1] - g['log'][1]) <= 2 and g['log'][3] == 140 and g['stored'] == '"right"'
    pg.evaluate("document.getElementById('edit-note-text').style.height = '260px'"); pg.wait_for_timeout(300)
    g2 = pg.evaluate(GEOM)
    print('A2) Bearbeitungsnotiz höher gezogen → Protokoll:', g2['log'][3], '| Notiz:', g2['note'][3])
    ok_a = ok_a and abs(g2['log'][3] - g2['note'][3]) <= 1
    log_txt = pg.locator('#dci-log li').last.inner_text()
    print('A3) Protokoll:', log_txt)
    ok_a = ok_a and 'Log shown: right of edit note' in log_txt
    results.append(ok0 and ok_a)

    # B) left, then above, then the window again
    g = place(pg, 'left')
    print('B1) links:', g['log'], g['note'], g['float'])
    ok_b = g['float'] == 'left' and g['log'][0] + g['log'][2] <= g['note'][0] and abs(g['note'][1] - g['log'][1]) <= 2
    g = place(pg, 'above')
    print('B2) darüber:', g['log'], g['note'], '| Breite Notiz:', repr(g['noteW']), '| clear:', g['clear'])
    ok_b = ok_b and g['before'] and g['float'] == 'none' and g['log'][1] + g['log'][3] <= g['note'][1] and abs(g['log'][2] - g['note'][2]) <= 1 \
        and g['noteW'] == '' and not g['clear'] and g['log'][3] == 180
    # the dragged height above the edit note is remembered
    pg.evaluate("document.getElementById('dci-log').style.height = '230px'"); pg.wait_for_timeout(800)
    stored_h = pg.evaluate("localStorage.getItem('dci-log-dock-h')")
    print('B3) Höhe gezogen → gespeichert:', stored_h)
    ok_b = ok_b and stored_h == '230'
    g = place(pg, 'window')
    print('B4) Fenster:', g['pos'], g['parent'], '| Breite Notiz:', repr(g['noteW']), '| gespeichert:', g['stored'])
    ok_b = ok_b and g['pos'] == 'fixed' and g['parent'] == 'BODY' and g['noteW'] == '' and g['stored'] is None
    results.append(ok_b)

    # C) too narrow beside it → above (hint); wider again → right; MB draws the edit note anew → the log follows
    place(pg, 'right')
    pg.set_viewport_size({'width': 600, 'height': 900}); pg.wait_for_timeout(500)
    g = pg.evaluate(GEOM)
    hint = pg.evaluate("[document.querySelector('#dci-log [data-log-f=place]').title, document.querySelector('#dci-log [data-log-f=place]').className, document.querySelector('#dci-log [data-log-f=place]').value]")
    print('C1) schmal:', g['cls'], '| Hinweis:', hint)
    ok_c = 'dci-log-dock-above' in g['cls'] and 'Not enough room' in hint[0] and 'dci-log-place-off' in hint[1] and hint[2] == 'right' and g['noteW'] == ''
    pg.set_viewport_size({'width': 1500, 'height': 1000}); pg.wait_for_timeout(500)
    g = pg.evaluate(GEOM)
    print('C2) wieder breit:', g['cls'])
    ok_c = ok_c and 'dci-log-dock-right' in g['cls']
    pg.evaluate("""() => { const old = document.getElementById('edit-note-text'); const n = document.createElement('textarea');
      n.id = 'edit-note-text'; n.value = old.value; document.getElementById('content').appendChild(n); old.remove(); }""")
    pg.wait_for_timeout(400)
    g = pg.evaluate(GEOM)
    print('C3) Notiz neu gezeichnet → Protokoll davor:', g['before'], g['cls'])
    ok_c = ok_c and g['before'] and 'dci-log-dock-right' in g['cls']
    results.append(ok_c)

    # D) remembered after reloading; "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults") → window
    pg.reload()
    pg.add_style_tag(content=CSS)
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    g = pg.evaluate(GEOM)
    print('D1) nach Neuladen:', g['cls'], g['before'])
    ok_d = 'dci-log-dock-right' in g['cls'] and g['before']
    H.open_reset(pg); pg.wait_for_timeout(200)
    pg.click('[data-act=reset-do]'); pg.wait_for_timeout(600)
    g = pg.evaluate(GEOM)
    print('D2) Standard:', g['pos'], g['parent'], g['stored'], '| Breite Notiz:', repr(g['noteW']))
    ok_d = ok_d and g['pos'] == 'fixed' and g['parent'] == 'BODY' and g['stored'] is None and g['noteW'] == ''
    results.append(ok_d)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
