"""Window or page, the log, staying in place after a form, texts that name the source (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: inline, logplace, keepplace, srctexts – each the former smoke/t_<case>.py, unchanged; `python3 t_ui_place.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_inline():
    """The dashboard in the page instead of a window: switched in the page bar before opening, placed below the
    import button, the page scrolls with it (dates block and footer stay in view), switched back in ⚙ Settings → General
    (3.26.0; before: in the dashboard header), remembered after a reload, back to the window with "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults")."""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        seg = pg.locator('#dci-launcher .dci-place-seg button')
        print('Schalter in der Seitenleiste:', seg.all_inner_texts(), [seg.nth(i).get_attribute('aria-pressed') for i in range(2)])
        pg.click('#dci-launcher [data-place=page]')
        pg.wait_for_timeout(200)
        # 3.5.1: the switch shows the choice at once, before the dashboard was opened
        pressed0 = [seg.nth(i).get_attribute('aria-pressed') for i in range(2)]
        print('0) Schalter nach dem Klick (Dashboard noch zu):', pressed0)
        H.open_dashboard(pg)
        pg.wait_for_timeout(400)
        where = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const panel = o.querySelector('.dci-panel');
      return { afterBar: document.getElementById('dci-pagebar').nextElementSibling === o, inline: o.classList.contains('dci-inline'),
        position: getComputedStyle(panel).position, bodyOverflow: getComputedStyle(o.querySelector('.dci-body')).overflowY }; })()""")
        print('1) in der Seite:', where)
        ok1 = where['afterBar'] and where['inline'] and where['position'] == 'relative' and where['bodyOverflow'] == 'visible' and pressed0 == ['false', 'true']
        # 2) the page scrolls; the dates block ([3.18.0] with the line "Add entry manually") sticks to the top, the footer to the bottom
        pg.evaluate("window.scrollTo(0, document.querySelector('[data-el=companies]').getBoundingClientRect().top + window.scrollY - 200)")
        pg.wait_for_timeout(300)
        pos = pg.evaluate("""(() => ({ y: Math.round(window.scrollY), dates: Math.round(document.querySelector('[data-el=stick]').getBoundingClientRect().top),
      foot: Math.round(window.innerHeight - document.querySelector('.dci-foot').getBoundingClientRect().bottom) }))()""")
        print('2) gescrollt:', pos)
        ok2 = pos['y'] > 300 and pos['dates'] == 0 and pos['foot'] == 0
        # 3) dragging the head moves nothing
        box = pg.locator('.dci-head h2').bounding_box()
        pg.mouse.move(box['x'] + 5, box['y'] + 5); pg.mouse.down(); pg.mouse.move(box['x'] + 200, box['y'] + 100); pg.mouse.up()
        style = pg.evaluate("document.querySelector('.dci-panel').getAttribute('style') || ''")
        print('3) Kopf gezogen → Stil:', repr(style))
        ok3 = 'left' not in style
        # 4) back to a window – [3.26.0] in ⚙ Settings → General (the head has no switch any more); remembered
        H.open_settings(pg, 'appearance')  # [3.29.2] the place is under "Appearance" now
        pg.click('[data-el=settings] [data-act=place-toggle]'); pg.wait_for_timeout(300)
        back = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); return { parent: o.parentNode === document.body,
      position: getComputedStyle(o.querySelector('.dci-panel')).position, stored: localStorage.getItem('dci-place') }; })()""")
        print('4) zurück als Fenster:', back)
        ok4 = back['parent'] and back['position'] == 'fixed' and back['stored'] is None
        pg.click('[data-el=settings] [data-act=place-toggle]'); pg.wait_for_timeout(200)
        pg.reload(); pg.add_script_tag(content=H.MAIN); pg.wait_for_selector('#dci-open', timeout=20000)
        pressed = pg.locator('#dci-launcher [data-place=page]').get_attribute('aria-pressed')
        pg.click('#dci-open'); pg.wait_for_selector('.dci-inline .dci-pools-head', timeout=30000)
        print('5) nach Neuladen: in der Seite gedrückt', pressed, '| Dashboard in der Seite:', pg.locator('#dci-overlay.dci-inline').count())
        ok5 = pressed == 'true' and pg.locator('#dci-overlay.dci-inline').count() == 1
        # 6) "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults"): window again
        H.open_reset(pg); pg.click('[data-act=reset-do]'); pg.wait_for_timeout(500)
        print('6) nach ↺ Standard: Fenster', pg.locator('#dci-overlay.dci-inline').count() == 0, '| Seitenleiste:', pg.locator('#dci-launcher [data-place=window]').get_attribute('aria-pressed'))
        ok6 = pg.locator('#dci-overlay.dci-inline').count() == 0 and pg.locator('#dci-launcher [data-place=window]').get_attribute('aria-pressed') == 'true'
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5, ok6]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5, ok6], '| Fehler:', errs)
        b.close()


def case_logplace():
    """Log placement ("Place:" in the log's head): beside the edit note (right / left: the edit note keeps its place and
    gets the rest of its width, the log takes its height and follows it), above it (full width, the dragged height is
    remembered) or its own window again. Too narrow beside it → above, with a hint; MusicBrainz drawing the edit note
    anew → the log follows; the place is remembered after reloading; "↺ Reset all settings …" (⚙ Settings, until 3.24 "↺ Defaults") → window."""
    H.MAIN = H.MAIN_SLOW  # [3.31.1] the time matters here: the script's own gap between requests to MusicBrainz
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


def case_keepplace():
    """After creating an entry through MusicBrainz's form ("Create artist …"), the dashboard stays where it was: the
    entry you came from keeps its place on the screen, although a message is added at the top and the dashboard is
    redrawn (window and page). Scroll anchoring is switched off, as in browsers without it (Safari) and where the
    entry itself is drawn anew."""
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


def case_srctexts():
    """Import 3.16.2: texts that named Discogs say "the source" when another source is loaded (as "Mapping rules" in 3.13.2).
    A) Discogs loaded: the question for "Guitar" says "Discogs only says “Guitar”", a role credit taken over is tagged "from
       Discogs"; the placeholder of "Add entry manually" says "a role as the source writes it" (for any source).
    B) A pasted text loaded: "The source (pasted text) only says “Guitar”", the tag "from the source" (tooltip "Taken from
       the source (pasted text)"), and a track without writers says "The source (pasted text) names no writers for this
       track"."""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    TEXTS = """(() => ({ ask: [...document.querySelectorAll('.dci-bass-ask')].map(x => x.textContent.replace(/\\s+/g, ' ').trim().slice(0, 60)),
  ph: (document.querySelector('[data-f=manual-role]') || {}).placeholder || '',
  tag: [...document.querySelectorAll('.dci-credit-name .dci-src')].map(x => [x.textContent.trim(), x.title]),
  writers: [...document.querySelectorAll('tr[data-work] .dci-info')].map(x => x.title) }))()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Checks complete/.test(x))", 90)
        pg.wait_for_timeout(500)
        a = pg.evaluate(TEXTS)
        print('A) Discogs:', a['ask'][:1], '|', a['ph'], '|', a['tag'][:1])
        results.append(any(x.startswith('Discogs only says “Guitar”') for x in a['ask']) and 'a role as the source writes it' in a['ph']
                       and a['tag'] and a['tag'][0] == ['from Discogs', 'Taken from Discogs'])
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Guitar – John Smith\nLayout by Jane Roe')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, f"{LOGS}.filter(x => /Checks complete/.test(x)).length >= 2", 90)
        pg.wait_for_timeout(500)
        t = pg.evaluate(TEXTS)
        print('B) Text:', t['ask'][:1], '|', t['ph'], '|', t['tag'][:1], '|', t['writers'][:1])
        results.append(any(x.startswith('The source (pasted text) only says “Guitar”') for x in t['ask'])
                       and t['tag'] and t['tag'][0] == ['from the source', 'Taken from the source (pasted text)']
                       and any(w.startswith('The source (pasted text) names no writers for this track') for w in t['writers']))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
