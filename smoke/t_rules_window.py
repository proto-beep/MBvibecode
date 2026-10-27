"""The window "Mapping rules": its words, in the dashboard, rule ids at rows, quick switches, ✎ at built-in rules, export and import (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: rulesname, rulesdock, rowrules – each the former smoke/t_<case>.py, unchanged –, quickswitch, [3.33.1] ruleedit, mappingio, mappingconflict; `python3 t_rules_window.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_rulesname():
    """Import 3.13.2: the window "Mapping rules" names Discogs only while Discogs is the loaded source.
    A) Discogs loaded: "Try a Discogs role:", the column "Discogs", "Discogs role → MusicBrainz", the hint with "as on Discogs".
    B) A pasted text loaded while the window is open: the window follows at once – "Try a role:", column "Role",
       "Role → MusicBrainz", "Role (without details)", the hint "as the source writes it".
    C) Discogs again: the Discogs words are back."""
    STATE = """(() => { const w = document.getElementById('dci-rules'); return {
  label: w.querySelector('[data-rf=test-label]').textContent.trim(),
  col: w.querySelector('[data-rsect=roles] thead th:nth-child(3)').textContent.trim(),
  kind: [...w.querySelectorAll('[data-uf=kind] option')].map(o => o.textContent.trim()),
  field: w.querySelector('[data-uf=discogs]').closest('label').textContent.trim(),
  hint: w.querySelector('[data-rf=result]').textContent.trim() }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.locator('[data-act=rules]').first.click()
        pg.wait_for_selector('#dci-rules [data-rsect=roles]')
        a = pg.evaluate(STATE)
        print('A)', a)
        results.append(a['label'] == 'Try a Discogs role:' and a['col'] == 'Discogs' and a['kind'][0] == 'Discogs role → MusicBrainz'
                       and a['field'].startswith('Discogs role (without details)') and 'as on Discogs' in a['hint'])
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Bass Man – bass')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(500)
        bb = pg.evaluate(STATE)
        print('B)', bb)
        results.append(bb['label'] == 'Try a role:' and bb['col'] == 'Role' and bb['kind'] == ['Role → MusicBrainz', 'Spelling → MB instrument']
                       and bb['field'].startswith('Role (without details)') and 'as the source writes it' in bb['hint'])
        H.src_menu(pg)
        pg.fill('[data-f=discogs-input]', '1234')
        pg.click('[data-act=discogs-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 3", 90)
        pg.wait_for_timeout(500)
        c = pg.evaluate(STATE)
        print('C)', c['label'], c['col'])
        results.append(c['label'] == 'Try a Discogs role:' and c['col'] == 'Discogs')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rulesdock():
    """Credits Importer 3.30.0: "Mapping rules" in the dashboard (collected item 75; the maintainer's answer of
    2026-10-24 17:42: "ja standardmäßig im Dashboard und ja soll sich die Einstellung merken. ja nur eines öffnen und das
    andere schließen").
    A) By default the symbol "Mapping rules" in the head opens them in the dashboard below its head (not a window of their
       own; the symbol pressed, the test field focused, "⧉ As window" in their head).
    B) ⚙ Settings opened: the rules close; "Mapping rules" again: the settings close.
    C) "⧉ As window": the rules float as a window (stored "window"), still open; ⚙ Settings leave the window open.
    D) Reloaded: they open as a window again; ⚙ Settings → Appearance says "as a window"; "in the dashboard" there brings
       them back (nothing stored).
    E) The symbol closes them again, Escape too.
    F) A rule id at a row opens them at that rule (highlighted, in view) – [3.30.2] as a window (item 75b; t_rowrules.py)."""
    STATE = """(() => { const r = document.getElementById('dci-rules'); const dock = document.querySelector('#dci-overlay [data-el=rules-dock]');
  const set = document.querySelector('[data-el=settings]'); const b = document.querySelector('.dci-head [data-act=rules]');
  return { open: !!(r && !r.hidden && r.offsetParent !== null) || !!(r && !r.hidden && getComputedStyle(r).position === 'fixed'),
    docked: !!(r && dock && dock.contains(r) && r.classList.contains('dci-rules-docked')), dockShown: !!(dock && !dock.hidden),
    position: r ? getComputedStyle(r).position : '', pressed: b.getAttribute('aria-expanded'), settings: !!(set && !set.hidden),
    place: r ? (r.querySelector('[data-rules-place]') || {}).textContent : '', focus: !!(document.activeElement && document.activeElement.dataset.rf === 'test'),
    stored: localStorage.getItem('dci-rules-place') }; })()"""
    RULES = '.dci-head [data-act=rules]'
    GEAR = '.dci-head [data-act=settings-open]'
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(500)
        st = lambda: pg.evaluate(STATE)
        # A)
        pg.click(RULES)
        pg.wait_for_timeout(300)
        a1 = st()
        print('A) geöffnet:', a1)
        results.append(a1['open'] and a1['docked'] and a1['dockShown'] and a1['position'] == 'static' and a1['pressed'] == 'true' and a1['focus']
                       and a1['place'].strip() == '⧉ As window' and a1['stored'] is None)
        # B) only one of both
        pg.click(GEAR)
        pg.wait_for_timeout(300)
        b1 = st()
        pg.click(RULES)
        pg.wait_for_timeout(300)
        b2 = st()
        print('B) ⚙ auf:', [b1['open'], b1['settings'], b1['pressed']], '| Regeln wieder:', [b2['open'], b2['settings']])
        results.append(not b1['open'] and b1['settings'] and b1['pressed'] == 'false' and b2['open'] and not b2['settings'])
        # C) as a window
        pg.click('#dci-rules [data-rules-place=window]')
        pg.wait_for_timeout(300)
        c1 = st()
        pg.click(GEAR)
        pg.wait_for_timeout(300)
        c2 = st()
        print('C) als Fenster:', c1, '| ⚙ dazu:', [c2['open'], c2['settings']])
        results.append(c1['open'] and not c1['docked'] and not c1['dockShown'] and c1['position'] == 'fixed' and c1['stored'] == '"window"'
                       and c1['place'].strip() == 'Into the dashboard' and c2['open'] and c2['settings'])
        pg.click(GEAR)
        # D) remembered
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        pg.click(RULES)
        pg.wait_for_timeout(300)
        d1 = st()
        H.open_settings(pg, 'appearance')
        d2 = pg.evaluate("[...document.querySelectorAll('.dci-set-pane [data-act=rules-place]')].map(x => [x.dataset.place, x.getAttribute('aria-pressed')])")
        pg.click('.dci-set-pane [data-act=rules-place][data-place=dashboard]')
        pg.wait_for_timeout(300)
        d3 = st()
        print('D) neu geladen:', [d1['open'], d1['docked'], d1['position']], '| Darstellung:', d2, '| im Dashboard:', [d3['open'], d3['docked'], d3['stored'], d3['settings']])
        results.append(d1['open'] and not d1['docked'] and d1['position'] == 'fixed' and d2 == [['dashboard', 'false'], ['window', 'true']]
                       and d3['open'] and d3['docked'] and d3['stored'] is None and not d3['settings'])
        # E) closed by the symbol, by Escape
        pg.click(RULES)
        pg.wait_for_timeout(300)
        e1 = st()
        pg.click(RULES)
        pg.wait_for_timeout(300)
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
        e2 = st()
        print('E) Symbol:', [e1['open'], e1['dockShown'], e1['pressed']], '| Escape:', [e2['open'], e2['dockShown'], pg.evaluate("!document.getElementById('dci-overlay').hidden")])
        results.append(not e1['open'] and not e1['dockShown'] and e1['pressed'] == 'false' and not e2['open'] and not e2['dockShown']
                       and pg.evaluate("!document.getElementById('dci-overlay').hidden"))
        # F) a rule id at a row
        rid = pg.evaluate("(document.querySelector('tr.dci-row [data-act=rule-goto]') || {}).dataset.rule")
        pg.locator(f'tr.dci-row [data-act=rule-goto][data-rule="{rid}"]').first.click()
        pg.wait_for_timeout(500)
        f1 = pg.evaluate("""(() => { const r = document.querySelector('#dci-rules tr.dci-rule-hit'); if (!r) return null;
      const body = document.querySelector('#dci-rules .dci-rules-body').getBoundingClientRect(); const rb = r.getBoundingClientRect();
      return [r.dataset.rid, rb.top >= body.top - 1 && rb.bottom <= body.bottom + 1]; })()""")
        print('F) Regel', rid, '→', f1, st()['docked'])
        results.append(f1 == [rid, True] and not st()['docked'] and st()['position'] == 'fixed')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_rowrules():
    """Credits Importer 3.30.2: rule ids at rows open the mapping rules as a window, the arrow in the head of an entry
    (collected items 75b, 82b; the maintainer's answers of 2026-10-25 01:59).
    A) A rule id at a row opens the rules as a window (not in the dashboard, where the symbol opens them; nothing stored),
       at that rule; the row stays where it was on the screen.
    B) The symbol in the head closes that window; the symbol again opens the rules in the dashboard.
    C) "Into the dashboard" in such a window: in the dashboard (the place stays "in the dashboard", nothing stored).
    D) ⚙ Settings → Appearance "Rule ids and ⓘ at rows open them: like the symbol" (stored "symbol"): a rule id opens them in
       the dashboard.
    E) Compact view: the arrow ▸ in the head of an entry opens all its rows (▾); one row closed again: ▸; ▸ opens all,
       ▾ closes all."""
    STATE = """(() => { const r = document.getElementById('dci-rules'); const dock = document.querySelector('#dci-overlay [data-el=rules-dock]');
  return { open: !!(r && !r.hidden), docked: !!(r && dock && dock.contains(r) && r.classList.contains('dci-rules-docked')), position: r ? getComputedStyle(r).position : '',
    hit: (document.querySelector('#dci-rules tr.dci-rule-hit') || {dataset: {}}).dataset.rid || null, stored: [localStorage.getItem('dci-rules-place'), localStorage.getItem('dci-rules-rowplace')],
    pressed: document.querySelector('.dci-head [data-act=rules]').getAttribute('aria-expanded') }; })()"""
    RULES = '.dci-head [data-act=rules]'
    ROWID = "section.dci-group:has(.dci-gname strong:text-is('Bob Producer')) tr.dci-row [data-act=rule-goto]"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.set_viewport_size({'width': 1300, 'height': 900})
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        st = lambda: pg.evaluate(STATE)
        # A)
        btn = pg.locator(ROWID).first
        btn.scroll_into_view_if_needed()
        rid = btn.get_attribute('data-rule')
        y0 = btn.evaluate('b => Math.round(b.getBoundingClientRect().top)')
        btn.click()
        pg.wait_for_timeout(500)
        a1 = st()
        y1 = pg.locator(ROWID).first.evaluate('b => Math.round(b.getBoundingClientRect().top)')
        print('A) Regel-ID', rid, '→', a1, '| Zeile vorher/nachher:', y0, y1)
        results.append(a1['open'] and not a1['docked'] and a1['position'] == 'fixed' and a1['hit'] == rid and a1['stored'] == [None, None] and abs(y1 - y0) <= 2)
        # B)
        pg.click(RULES)
        pg.wait_for_timeout(300)
        b1 = st()
        pg.click(RULES)
        pg.wait_for_timeout(300)
        b2 = st()
        print('B) Symbol schließt:', [b1['open'], b1['pressed']], '| Symbol öffnet:', [b2['open'], b2['docked']])
        results.append(not b1['open'] and b1['pressed'] == 'false' and b2['open'] and b2['docked'])
        pg.click(RULES)
        pg.wait_for_timeout(200)
        # C)
        pg.locator(ROWID).first.click()
        pg.wait_for_timeout(400)
        pg.click('#dci-rules [data-rules-place=dashboard]')
        pg.wait_for_timeout(300)
        c1 = st()
        print('C) „Into the dashboard“:', [c1['open'], c1['docked'], c1['stored']])
        results.append(c1['open'] and c1['docked'] and c1['stored'] == [None, None])
        pg.click(RULES)
        pg.wait_for_timeout(200)
        # D)
        H.open_settings(pg, 'appearance')
        d0 = pg.evaluate("[...document.querySelectorAll('.dci-set-pane [data-act=rules-rowplace]')].map(x => [x.dataset.place, x.getAttribute('aria-pressed')])")
        pg.click('.dci-set-pane [data-act=rules-rowplace][data-place=symbol]')
        pg.wait_for_timeout(200)
        pg.click('.dci-head [data-act=settings-open]')
        pg.locator(ROWID).first.click()
        pg.wait_for_timeout(400)
        d1 = st()
        print('D) Einstellung:', d0, '| wie das Symbol:', [d1['open'], d1['docked'], d1['stored']])
        results.append(d0 == [['window', 'true'], ['symbol', 'false']] and d1['open'] and d1['docked'] and d1['stored'] == [None, '"symbol"'])
        pg.click(RULES)
        pg.wait_for_timeout(200)
        # E) the arrow in the head (compact view): Bass Man with a second role
        sec = "section.dci-group:has(.dci-gname strong:text-is('Bass Man'))"
        pg.click(f'{sec} [data-act=add-role]')
        pg.wait_for_timeout(300)
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(400)
        ARROW = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
      const a = g.querySelector('.dci-gname [data-act=group-openall]'); return [a ? a.textContent.trim() : null, a ? a.getAttribute('aria-expanded') : null,
      [...g.querySelectorAll('tr.dci-row')].map(tr => tr.classList.contains('dci-open'))]; })()"""
        pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man');
      g.querySelectorAll('tr.dci-row.dci-open .dci-cl-close').forEach(b => b.click()); })()""")
        pg.wait_for_timeout(300)
        e0 = pg.evaluate(ARROW)
        pg.click(f'{sec} .dci-gname [data-act=group-openall]')
        pg.wait_for_timeout(300)
        e1 = pg.evaluate(ARROW)
        pg.locator(f'{sec} tr.dci-row.dci-open .dci-cl-close').first.click()
        pg.wait_for_timeout(300)
        e2 = pg.evaluate(ARROW)
        pg.click(f'{sec} .dci-gname [data-act=group-openall]')
        pg.wait_for_timeout(300)
        e3 = pg.evaluate(ARROW)
        pg.click(f'{sec} .dci-gname [data-act=group-openall]')
        pg.wait_for_timeout(300)
        e4 = pg.evaluate(ARROW)
        print('E) Pfeil:', e0, e1, e2, e3, e4)
        results.append(e0 == ['▸', 'false', [False, False]] and e1 == ['▾', 'true', [True, True]] and e2[0] == '▸' and e2[2].count(True) == 1
                       and e3 == ['▾', 'true', [True, True]] and e4 == ['▸', 'false', [False, False]])
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(300)
        e5 = pg.evaluate("document.querySelectorAll('.dci-gname [data-act=group-openall]').length")
        print('   volle Ansicht – Pfeile im Kopf:', e5)
        results.append(e5 == 0)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_quickswitch():
    """Credits Importer 3.32.0 (milestone "Quick switches"): quick switches at the top of "Mapping rules" (collected item 97d;
    maintainer: "bitte lass das aber an- und abstellen. im mapping ganz oben evtl. (mit klickbarem verweis dann wo es verwendet
    wird)", "auf jeden fall noch die regel, dass performance dates die über mehrere tage hinweg gehen nach meinen regeln auf
    den kleinsten gemeinsamen nenner gekürzt werden").
    A) Seven switches in this order – S045, D022, S021, S031, S007 on, D023 and S046 off – each with its id. [3.32.8] In a box
       of their own (head, frame with round corners of 4 px), each switch a button (pressed = on; collected item 116).
    B) A click on an id shows that rule in the list below (highlighted).
    C) A quick switch and the rule's own switch are the same: S007 off at the top (a click on its button) → off in the list and
       stored; on again.
    D) D022: "Recorded March 1–3, 2001" in the notes → under Performance the month 2001-03 at once (the period stays in the
       pool); D022 off → the period again (the suggestions not applied yet are placed anew); on → the month.
    E) S045: a pasted text "Composed by Tomas Fujiwara (BMI)" and "Lyrics by Ann Poe / GEMA" → Tomas Fujiwara and Ann Poe
       without the society, BMI and GEMA as the release's rights societies."""
    from common_rows import cells
    # [3.32.8] each switch a button (aria-pressed) with its id next to it, in a box of its own (item 116)
    QS = """[...document.querySelectorAll('#dci-rules [data-rf=quick] .dci-qbtn-wrap')].map(x => [x.querySelector('[data-qs-goto]').textContent.trim(), x.querySelector('[data-qs-toggle]').getAttribute('aria-pressed') === 'true'])"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        perf0 = [c[0] for c in cells(pg).get('performance', [])]
        pool0 = pg.evaluate("[...document.querySelectorAll('.dci-pchip-date .dci-chip-main')].map(c => c.textContent.trim())")
        pg.click('.dci-head [data-act=rules]'); pg.wait_for_timeout(300)
        a = pg.evaluate(QS)
        box = pg.evaluate("""(() => { const q = document.querySelector('#dci-rules [data-rf=quick] .dci-quick'); const st = getComputedStyle(q);
          return [!!q.querySelector('.dci-quick-h strong'), q.querySelectorAll('.dci-quick-grid > .dci-qbtn-wrap').length, st.borderTopStyle, st.borderTopLeftRadius,
            q.querySelector('[data-qs-toggle=S045]').textContent.replace(/\\s+/g, ' ').trim()]; })()""")
        print('A) Schalter:', a, '| Kasten:', box)
        results.append(a == [['S045', True], ['D022', True], ['S021', True], ['S031', True], ['S007', True], ['D023', False], ['S046', False]]
                       and box[:4] == [True, 7, 'solid', '4px'] and box[4].startswith('Rights society after a writer’s name'))
        pg.click('#dci-rules [data-qs-goto=S031]'); pg.wait_for_timeout(300)
        hit = pg.evaluate("[...document.querySelectorAll('#dci-rules tr.dci-rule-hit')].map(r => r.dataset.rid)")
        print('B) gezeigt:', hit)
        results.append(hit == ['S031'])
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=S007]'); pg.wait_for_timeout(500)
        c1 = [pg.locator('#dci-rules [data-rf=tables] [data-rule-on=S007]').is_checked(), pg.evaluate("localStorage.getItem('dci-rules-off')")]
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=S007]'); pg.wait_for_timeout(500)
        c2 = [pg.locator('#dci-rules [data-rf=tables] [data-rule-on=S007]').is_checked(), pg.evaluate("localStorage.getItem('dci-rules-off')")]
        print('C) S007 aus:', c1, '| wieder an:', c2)
        results.append(c1[0] is False and 'S007' in (c1[1] or '') and c2[0] is True and 'S007' not in (c2[1] or ''))
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=D022]'); pg.wait_for_timeout(600)
        perf1 = [c[0] for c in cells(pg).get('performance', [])]
        pg.click('#dci-rules [data-rf=quick] [data-qs-toggle=D022]'); pg.wait_for_timeout(600)
        perf2 = [c[0] for c in cells(pg).get('performance', [])]
        print('D) Performance:', perf0, '| Pool:', pool0, '| D022 aus:', perf1, '| an:', perf2)
        results.append(perf0 == ['Performance 1 (month) · 2001-03'] and any('2001-03-01 – 2001-03-03' in x for x in pool0)
                       and perf1 == ['Performance 1 · 2001-03-01 – 2001-03-03'] and perf2 == perf0)
        # E) a pasted text
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Composed by Tomas Fujiwara (BMI)\nLyrics by Ann Poe / GEMA')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1200)
        groups = pg.evaluate("[...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(), [...g.querySelectorAll('tr.dci-row .dci-drole')].map(x => x.textContent.trim())])")
        # [3.32.4] the name only (the head has the tag of its kind before it)
        cols = pg.evaluate("[...document.querySelectorAll('.dci-matrix th[data-colhead] .dci-mx-colname')].map(x => (x.querySelector('.dci-mblink, strong') || x).textContent.replace(/^MB/, '').trim().split(/\\s/).slice(0, 2).join(' '))")
        print('E) Einträge:', groups, '| Spalten:', cols)
        names = [g[0] for g in groups]
        results.append('BMI' in names and 'GEMA' in names and dict(groups).get('BMI') == ['Rights Society'] and dict(groups).get('GEMA') == ['Rights Society']
                       and 'Tomas Fujiwara' in cols and 'Ann Poe' in cols and not any('BMI' in c or 'GEMA' in c for c in cols))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



# [3.33.1] a row of the dashboard by its role: [type, role credit, rule ids]
ROW = """(role) => { const tr = [...document.querySelectorAll('tr.dci-row')].find(r => (r.querySelector('.dci-drole') || {}).textContent.trim() === role);
  if (!tr) return null; const t = tr.querySelector('[data-f=type]'); const c = tr.querySelector('[data-f=role-credit]');
  return [t ? (t.selectedOptions && t.selectedOptions[0] ? t.selectedOptions[0].textContent.trim() : t.value) : '', c ? c.value : '', [...tr.querySelectorAll('.dci-ruleid')].map(x => x.textContent.trim()).join(' ')]; }"""
TEST = """(text) => { const t = document.querySelector('#dci-rules [data-rf=test]'); t.value = text; t.dispatchEvent(new Event('input', { bubbles: true }));
  return document.querySelector('#dci-rules [data-rf=result]').innerText.replace(/\\s+/g, ' ').trim(); }"""


def open_rules(pg):
    pg.click('.dci-head [data-act=rules]')
    pg.wait_for_selector('#dci-rules [data-rsect=roles]')
    pg.wait_for_timeout(200)


def case_ruleedit():
    """Credits Importer 3.33.1: ✎ at the built-in rules (collected item E7; maintainer: "auch direkt an der Regel").
    A) ✎ at role rules without code (R071) and at company rules (C023), "code" at rules with code (R031, no ✎); ✎ at the lists
       T001, T002, T003, T038, T045, T048, at no other list.
    B) ✎ R071: the form shows the rule as built in – the pattern as role words, the type, the level, no role credit.
    C) Saved with one more word ("pictures by") and the role credit "photos": "Pictures By" in the test field maps with R071
       and the credit; the dashboard's row "Photography By" gets the credit at once; the rule is marked "changed", "Your changes"
       shows it (role credit – → “photos”), the line of the file counts it; stored (dci-mapping-changes, with was: null).
    D) A wrong regular expression ("^(photo") is not saved: an error in the form, the change stays as it was.
    E) The change stays after the page is loaded again.
    F) ✎ T002: a word added ("zither") – in the list at once, "Your changes" shows + zither; T045 says "after loading the page".
    G) ↺ (asked first) takes the change back: the built-in rule again, also in the row; ↺ all (asked first) the rest."""
    results = []
    asked = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: (asked.append(d.message), d.accept()))
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        row0 = pg.evaluate(ROW, 'Photography By')
        open_rules(pg)
        a = pg.evaluate("""(() => { const w = document.getElementById('dci-rules'); const has = (id) => !!w.querySelector(`[data-redit-open="${id}"]`);
          const code = (id) => { const r = w.querySelector(`[data-rf=tables] tr[data-rid="${id}"]`); return !!(r && r.querySelector('.dci-codetag')); };
          return { R071: has('R071'), C023: has('C023'), R031: [has('R031'), code('R031')],
            lists: [...w.querySelectorAll('[data-ledit-open]')].map(x => x.dataset.leditOpen).sort() }; })()""")
        print('A)', a, '| Zeile vorher:', row0)
        results.append(a == {'R071': True, 'C023': True, 'R031': [False, True], 'lists': ['T001', 'T002', 'T003', 'T038', 'T045', 'T048']})
        pg.click('#dci-rules [data-redit-open=R071]')
        pg.wait_for_timeout(200)
        form = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#dci-rules [data-redit] [data-redit-f]')].map(f => [f.dataset.reditF, f.value]))")
        print('B) Formular:', form)
        results.append(form.get('pmode') == 'words' and form.get('pattern', '').startswith('photography by | photography | photographer') and form.get('types') == 'photography'
                       and form.get('level') == 'release' and form.get('creditMode') == 'none' and form.get('instr') == '')
        pg.fill('#dci-rules [data-redit-f=pattern]', form['pattern'] + ' | pictures by')
        pg.select_option('#dci-rules [data-redit-f=creditMode]', 'text')
        pg.wait_for_timeout(150)
        pg.fill('#dci-rules [data-redit-f=credit]', 'photos')
        pg.click('#dci-rules [data-redit-save]')
        pg.wait_for_timeout(600)
        test = pg.evaluate(TEST, 'Pictures By')
        row1 = pg.evaluate(ROW, 'Photography By')
        c = pg.evaluate("""(() => { const w = document.getElementById('dci-rules'); const r = w.querySelector('[data-rf=tables] tr[data-rid=R071]');
          return [r.classList.contains('dci-rchanged'), (r.querySelector('.dci-changed') || {}).textContent, (w.querySelector('[data-mchg=R071]') || {}).innerText,
            w.querySelector('[data-rf=mapping-src]').textContent, JSON.parse(localStorage.getItem('dci-mapping-changes'))]; })()""")
        print('C) Test:', test, '| Zeile:', row1, '| markiert:', c[:4], '| gespeichert:', c[4])
        st = c[4] or {}
        results.append('photography' in test and 'R071' in test and 'photos' in test and row1 and row1[1] == 'photos' and c[0] and c[1] == 'changed'
                       and 'Role credit: – → “photos”' in (c[2] or '') and 'pictures by' in (c[2] or '') and c[3].endswith('your changes: 1')
                       and st.get('rules', {}).get('R071', {}).get('set', {}).get('credit') == 'photos' and st['rules']['R071']['was'].get('credit') is None
                       and st['rules']['R071']['set']['re']['$re'].endswith('|pictures by)$') and st.get('base') == H.VERSION)
        pg.click('#dci-rules [data-redit-open=R071]')
        pg.wait_for_timeout(150)
        pg.select_option('#dci-rules [data-redit-f=pmode]', 're')
        pg.wait_for_timeout(150)
        pg.fill('#dci-rules [data-redit-f=pattern]', '^(photo')
        pg.click('#dci-rules [data-redit-save]')
        pg.wait_for_timeout(300)
        d = [pg.evaluate("(document.querySelector('#dci-rules .dci-redit-err') || {}).textContent || ''"),
             pg.evaluate("JSON.parse(localStorage.getItem('dci-mapping-changes')).rules.R071.set.re.$re")]
        print('D) Fehler:', d)
        results.append(d[0].startswith('The pattern cannot be used:') and d[1].endswith('|pictures by)$'))
        pg.click('#dci-rules [data-redit-cancel]')
        # E) the page again
        pg2, errs2 = H.open_mb_edit(ctx, companion=False)
        pg2.on('dialog', lambda d: (asked.append(d.message), d.accept()))
        pg2.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg2)
        pg2.wait_for_timeout(1200)
        e = [pg2.evaluate(ROW, 'Photography By'), pg2.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /change of built-in rules is in effect/.test(t)).length")]
        print('E) neu geladen:', e)
        results.append(e[0] and e[0][1] == 'photos' and e[1] == 1)
        pg.close()
        pg = pg2
        open_rules(pg)
        pg.click('#dci-rules [data-ledit-open=T002]')
        pg.wait_for_timeout(200)
        text = pg.input_value('#dci-rules [data-ledit-text]')
        pg.fill('#dci-rules [data-ledit-text]', text + '\nZither')
        pg.click('#dci-rules [data-ledit-save]')
        pg.wait_for_timeout(500)
        pg.click('#dci-rules [data-ledit-open=T045]')
        pg.wait_for_timeout(200)
        f = [pg.evaluate("document.querySelector('#dci-rules [data-rsect=words] p').textContent.includes('zither')"),
             pg.evaluate("(document.querySelector('#dci-rules [data-mchg=T002]') || {}).innerText || ''"),
             pg.evaluate("document.querySelector('#dci-rules [data-ledit=T045]').innerText.includes('takes full effect after loading the page again')"),
             'zither' not in text]
        print('F) T002:', f)
        results.append(f[0] and '+ zither' in f[1] and f[2] and f[3])
        pg.click('#dci-rules [data-ledit-cancel]')
        pg.wait_for_timeout(150)
        n_asked = len(asked)
        pg.click('#dci-rules [data-mchg=R071] [data-mchg-reset]')
        pg.wait_for_timeout(600)
        g1 = [pg.evaluate(ROW, 'Photography By'), pg.evaluate(TEST, 'Pictures By'), pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('dci-mapping-changes')).rules)"), asked[n_asked:]]
        pg.click('#dci-rules [data-mchg-resetall]')
        pg.wait_for_timeout(600)
        g2 = [pg.evaluate("localStorage.getItem('dci-mapping-changes')"), pg.evaluate("document.querySelector('#dci-rules [data-rsect=words] p').textContent.includes('zither')"), asked[n_asked + 1:]]
        print('G) ↺ R071:', g1, '| ↺ alle:', g2)
        results.append(g1[0] == row0 and 'R071' not in g1[1] and g1[2] == [] and len(g1[3]) == 1 and 'R071' in g1[3][0]
                       and g2[0] is None and not g2[1] and len(g2[2]) == 1 and 'Really reset all' in g2[2][0])
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_mappingio():
    """Credits Importer 3.33.1: export and import of the register (collected item E7).
    A) Export "the whole register" without changes is the mapping file, byte for byte (a pull request shows only what changed);
       with a change only the line of that rule differs.
    B) Export "my changes": format mb-vibecode-credits-importer-mapping-changes, version 2, the script's and the file's version,
       own rules, switches, the changed rule; "Copy" puts the same into the clipboard.
    C) Import of pasted text: a preview – a rule new with its fields before → after and its roles mapped before → after, a list
       (+ a word), an own rule, a switch; skipped: an unknown id, a rule with code, a wrong pattern; a conflict (the built-in
       rule differed at the export). Nothing is taken over before "Take over".
    D) "Take over" (merge): the changes are there; the conflict is marked in "Your changes" until "Keep mine".
    E) An old rules file (mb-x-vibecode-rules, version 1) through the file chooser: its own rule; dropped onto the window: the
       preview too.
    F) "Replace my changes" with a whole register (one rule changed, one list that cannot be changed here – skipped): only that
       rule stays, own rules and switches stay."""
    import json
    import os
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://musicbrainz.org')
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        open_rules(pg)
        mapping_file = H.MAPPING_TEXT

        def export(what):
            pg.select_option('#dci-rules [data-mio=what]', what)
            pg.wait_for_timeout(100)
            with pg.expect_download() as dl:
                pg.click('#dci-rules [data-mio-save]')
            d = dl.value
            return d.suggested_filename, open(d.path(), encoding='utf-8').read()

        name0, reg0 = export('register')
        # one change: R071's level (✎)
        pg.click('#dci-rules [data-redit-open=R071]')
        pg.wait_for_timeout(150)
        pg.select_option('#dci-rules [data-redit-f=level]', 'recording')
        pg.click('#dci-rules [data-redit-save]')
        pg.wait_for_timeout(500)
        name1, reg1 = export('register')
        diff = [(x, y) for x, y in zip(mapping_file.split('\n'), reg1.split('\n')) if x != y]
        print('A) Datei:', name0, reg0 == mapping_file, '| mit Änderung:', name1, len(diff), diff[0][1][:80] if diff else '')
        results.append(name0 == 'mb-vibecode-credits-importer-mapping.json' and reg0 == mapping_file and len(diff) == 1 and '"id":"R071"' in diff[0][1]
                       and '"level":"recording"' in diff[0][1] and len(reg1.split('\n')) == len(mapping_file.split('\n')))
        name2, ch = export('changes')
        chd = json.loads(ch)
        pg.click('#dci-rules [data-mio-copy]')
        pg.wait_for_timeout(400)
        clip = pg.evaluate("navigator.clipboard.readText()")
        status = pg.evaluate("document.querySelector('#dci-rules [data-rf=mio-status]').textContent")
        print('B)', name2, {k: chd[k] for k in ('format', 'version', 'script', 'mapping')}, chd['rules'], '| Zwischenablage gleich:', json.loads(clip)['rules'] == chd['rules'], status)
        results.append(name2 == 'mb-vibecode-credits-importer-mapping-changes.json' and chd['format'] == 'mb-vibecode-credits-importer-mapping-changes' and chd['version'] == 2
                       and chd['script'] == H.VERSION and chd['mapping'] == H.VERSION and chd['rules'] == {'R071': {'set': {'level': 'recording'}, 'was': {'level': 'release'}}}
                       and chd['own'] == [] and isinstance(chd['off'], list) and json.loads(clip)['rules'] == chd['rules'] and status == 'Copied to the clipboard')
        # C) a file made by hand, pasted
        paste = {'format': 'mb-vibecode-credits-importer-mapping-changes', 'version': 2, 'script': '3.33.9', 'mapping': '3.33.9',
                 'own': [{'id': 'U001', 'kind': 'role', 'on': True, 'discogs': 'gizmo', 'details': '', 'detailsMode': 'any', 'type': 'instrument', 'level': 'recording', 'instrument': 'theremin', 'credit': ''}],
                 'off': ['S007'],
                 'rules': {'R070': {'set': {'credit': 'cover painting'}, 'was': {'credit': 'cover art'}},
                           'C023': {'set': {'place': ['recorded at', 'engineered at'], 'level': 'release'}, 'was': {'level': 'work'}},
                           'R999': {'set': {'level': 'release'}}, 'R031': {'set': {'level': 'release'}}, 'C003': {'set': {'re': {'$re': '^(licensed', '$flags': ''}}}},
                 'lists': {'T002': {'add': ['zither'], 'remove': []}, 'T099': {'add': ['x']}}}
        pg.click('#dci-rules .dci-mio-paste > summary')
        pg.fill('#dci-rules [data-mio=paste]', json.dumps(paste))
        pg.click('#dci-rules [data-mio-read]')
        pg.wait_for_timeout(500)
        prev = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#dci-rules [data-rf=preview] li')].map(li => [li.dataset.mprev, [li.className.replace('dci-mprev-', ''), li.innerText.replace(/\\s+/g, ' ').trim()]]))")
        stored = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('dci-mapping-changes')).rules)")
        print('C) Vorschau:')
        for k, v in prev.items():
            print('  ', k, v)
        ok_c = (prev.get('R070', [''])[0] == 'new' and '“cover art” → “cover painting”' in prev['R070'][1] and 'cover art:' in prev['R070'][1]
                and prev.get('C023', [''])[0] == 'new' and 'Types for places recorded at → recorded at, engineered at' in prev['C023'][1] and '⚠' in prev['C023'][1]
                and prev.get('T002', [''])[0] == 'changed' and '+ zither' in prev['T002'][1] and prev.get('U001', [''])[0] == 'new' and prev.get('S007', [''])[0] == 'off'
                and prev.get('R999', [''])[0] == 'skipped' and 'not in the mapping file' in prev['R999'][1] and prev.get('R031', [''])[0] == 'skipped' and 'code' in prev['R031'][1]
                and prev.get('C003', [''])[0] == 'skipped' and 'pattern cannot be used' in prev['C003'][1] and prev.get('T099', [''])[0] == 'skipped' and stored == ['R071'])
        results.append(ok_c)
        pg.click('#dci-rules [data-mimport-apply]')
        pg.wait_for_timeout(700)
        d = pg.evaluate("""(() => { const st = JSON.parse(localStorage.getItem('dci-mapping-changes')); const w = document.getElementById('dci-rules');
          return [Object.keys(st.rules).sort(), st.lists, JSON.parse(localStorage.getItem('dci-user-rules')).map(u => u.id + ' ' + u.discogs), JSON.parse(localStorage.getItem('dci-rules-off')),
            [...w.querySelectorAll('[data-rf=changes] li.dci-mchg-conflict')].map(li => li.dataset.mchg), (w.querySelector('[data-rf=tables] tr[data-rid=C023] .dci-changed') || {}).textContent]; })()""")
        pg.click('#dci-rules [data-mchg=C023] [data-mchg-keep]')
        pg.wait_for_timeout(300)
        d2 = pg.evaluate("[...document.querySelectorAll('#dci-rules [data-rf=changes] li.dci-mchg-conflict')].length")
        print('D) übernommen:', d, '| nach „Keep mine“:', d2)
        results.append(d[0] == ['C023', 'R070', 'R071'] and d[1] == {'T002': {'add': ['zither'], 'remove': []}} and d[2] == ['U001 gizmo'] and 'S007' in d[3]
                       and d[4] == ['C023'] and d[5] == 'changed · ⚠' and d2 == 0)
        # E) an old rules file: chosen, and dropped onto the window
        old = {'format': 'mb-x-vibecode-rules', 'version': 1, 'rules': [{'id': 'U001', 'kind': 'instrument', 'on': True, 'discogs': 'gtr', 'instrument': 'guitar'}], 'off': ['S031']}
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '__old_rules.json')
        with open(path, 'w') as fh:
            json.dump(old, fh)
        pg.set_input_files('#dci-rules [data-rules-import]', path)
        pg.wait_for_timeout(600)
        e1 = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#dci-rules [data-rf=preview] li')].map(li => [li.dataset.mprev, li.className.replace('dci-mprev-', '')]))")
        e1k = pg.evaluate("document.querySelector('#dci-rules [data-rf=preview] p').textContent")
        pg.click('#dci-rules [data-mimport-cancel]')
        pg.wait_for_timeout(200)
        dt = pg.evaluate_handle("(t) => { const d = new DataTransfer(); d.items.add(new File([t], 'drop.json', { type: 'application/json' })); return d; }", json.dumps(old))
        pg.dispatch_event('#dci-rules', 'dragover', {'dataTransfer': dt})
        pg.dispatch_event('#dci-rules', 'drop', {'dataTransfer': dt})
        pg.wait_for_timeout(600)
        e2 = pg.evaluate("document.querySelector('#dci-rules [data-rf=preview] strong').textContent")
        pg.click('#dci-rules [data-mimport-apply]')
        pg.wait_for_timeout(600)
        e3 = pg.evaluate("JSON.parse(localStorage.getItem('dci-user-rules')).map(u => u.id + ' ' + u.discogs)")
        os.remove(path)
        print('E) alte Datei:', e1, e1k, '| gezogen:', e2, '| eigene Regeln:', e3)
        results.append(e1 == {'U002': 'new', 'S031': 'off'} and 'older version' in e1k and e2 == 'Preview of the import: drop.json' and e3 == ['U001 gizmo', 'U002 gtr'])
        # F) a whole register replacing my changes of built-in rules
        reg = json.loads(mapping_file)
        for r in reg['ROLE_RULE_DATA']:
            if r['id'] == 'R002':
                r['level'] = 'release'
        reg['TEXT_ABBREV'] = {'$re': 'etc', '$flags': ''}
        pg.fill('#dci-rules [data-mio=paste]', json.dumps(reg))
        pg.click('#dci-rules [data-mio-read]')
        pg.wait_for_timeout(500)
        pg.check('#dci-rules [data-mimport-mode][value=replace]')
        pg.wait_for_timeout(400)
        f1 = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#dci-rules [data-rf=preview] li')].map(li => [li.dataset.mprev, li.className.replace('dci-mprev-', '')]))")
        pg.click('#dci-rules [data-mimport-apply]')
        pg.wait_for_timeout(600)
        f2 = pg.evaluate("[Object.keys(JSON.parse(localStorage.getItem('dci-mapping-changes')).rules), JSON.parse(localStorage.getItem('dci-mapping-changes')).lists, JSON.parse(localStorage.getItem('dci-user-rules')).length, JSON.parse(localStorage.getItem('dci-rules-off')).includes('S007')]")
        print('F) Vorschau:', f1, '| danach:', f2)
        results.append(f1 == {'R002': 'new', 'C023': 'removed', 'R070': 'removed', 'R071': 'removed', 'T002': 'changed', 'TEXT_ABBREV': 'skipped'}
                       and f2 == [['R002'], {}, 2, True])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_mappingconflict():
    """Credits Importer 3.33.1: your changes after an update of the mapping file (collected item E7).
    A) A stored change whose built-in value was different (as after an update): the log warns at the start, the rule is marked
       "changed · ⚠", "Your changes" names the built-in value then and now, with "Keep mine" and "Discard".
    B) A change of a rule that is no longer in the file: "no longer in the mapping file", only "Discard".
    C) "Discard" (asked first): the change goes, the built-in rule applies.
    D) ⚙ Settings → reset with "own rules" ticked also resets your changes of built-in rules (the text names them)."""
    import json
    results = []
    stored = {'rules': {'R071': {'set': {'credit': 'photos'}, 'was': {'credit': 'photo credit'}}, 'R998': {'set': {'level': 'release'}, 'was': {'level': 'recording'}}},
              'lists': {}, 'base': '3.33.0'}
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("if (!sessionStorage.getItem('t-preset')) { localStorage.setItem('dci-mapping-changes', %s); sessionStorage.setItem('t-preset', '1'); }" % json.dumps(json.dumps(stored)))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        asked = []
        pg.on('dialog', lambda d: (asked.append(d.message), d.accept()))
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1200)
        logw = pg.evaluate("[...document.querySelectorAll('#dci-log li.dci-log-warn')].map(li => li.textContent).filter(t => /changed since your change/.test(t))")
        open_rules(pg)
        a = pg.evaluate("""(() => { const w = document.getElementById('dci-rules');
          return [(w.querySelector('[data-rf=tables] tr[data-rid=R071] .dci-changed') || {}).textContent, w.querySelector('[data-mchg=R071]').innerText.replace(/\\s+/g, ' '),
            !!w.querySelector('[data-mchg=R071] [data-mchg-keep]'), w.querySelector('[data-mchg=R998]').innerText.replace(/\\s+/g, ' '), !!w.querySelector('[data-mchg=R998] [data-mchg-keep]')]; })()""")
        print('A) Log:', logw, '| R071:', a[:3], '| B) R998:', a[3:])
        results.append(len(logw) == 1 and 'R071, R998' in logw[0] and a[0] == 'changed · ⚠' and 'Role credit “photo credit” → –' in a[1] and 'Keep mine' in a[1] and 'Discard' in a[1] and a[2])
        results.append('no longer in the mapping file' in a[3] and not a[4])
        pg.click('#dci-rules [data-mchg=R071] [data-mchg-reset]')
        pg.wait_for_timeout(500)
        c = [pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('dci-mapping-changes')).rules)"), pg.evaluate(ROW, 'Photography By'), asked]
        print('C) verworfen:', c)
        results.append(c[0] == ['R998'] and c[1] and c[1][1] == '' and len(c[2]) == 1)
        H.open_reset(pg)
        pg.wait_for_timeout(200)
        label = pg.evaluate("document.querySelector('[data-f=reset-rules]').closest('label').textContent.trim()")
        pg.check('[data-f=reset-rules]')
        pg.click('[data-act=reset-do]')
        pg.wait_for_timeout(2000)
        dd = pg.evaluate("localStorage.getItem('dci-mapping-changes')")
        print('D) Text:', label, '| danach:', dd)
        results.append('your changes of built-in rules (1)' in label and dd is None)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
