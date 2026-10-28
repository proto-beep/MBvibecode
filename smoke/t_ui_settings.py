"""Settings: tabs, the menu, the bridge to ⚙, settings without an import, reset, the update notice (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: settabs, settings, bridge, ui305, reset, notice – each the former smoke/t_<case>.py, unchanged; `python3 t_ui_settings.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_settabs():
    """Credits Importer 3.25.0: the settings as tabs (collected items 42, 41, 40).
    A) "⚙ Settings" folds the settings out and in (only the gear: no "Close" inside); eight tabs, "General" chosen ([3.29.2] nine: "Appearance" after "General").
    B) Keys: ↓ the next tab ("Appearance"; chosen, focused), End the last, Home the first.
    C) The tab is remembered (here "Texts", with "Show the web links …" and a button to "Mapping rules"); after reloading
       the settings open on it.
    D) The ⓘ in the head opens the settings at "ⓘ Connections": a table of the connections ([3.32.10] twelve) (Harmony with its home page,
       kind, what the script does, permissions, since).
    E) "↺ Reset all settings …" below the tabs shows the question in the settings (no tab chosen); "Cancel" goes back to
       the tab. The head has no "↺ Defaults" any more.
    F) A narrow dashboard: the tabs stand in a row above the content.
    G) [3.27.2] A click on the heading "Settings" (a tooltip, no link look) folds them in; the focus goes to ⚙ (item 57)."""
    SET = "document.querySelector('[data-el=settings]')"
    TABS = f"[...{SET}.querySelectorAll('.dci-set-tab')].map(b => [b.dataset.topic, b.getAttribute('aria-selected'), document.activeElement === b])"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        # A)
        gear = '.dci-head [data-act=settings-open]'
        pg.click(gear)
        pg.wait_for_timeout(300)
        t1 = pg.evaluate(TABS)
        a = [pg.evaluate(f"!{SET}.hidden"), pg.evaluate(f"{SET}.querySelectorAll('[data-act=settings-open]').length"), pg.locator(gear).get_attribute('aria-expanded')]
        pg.click(gear)
        pg.wait_for_timeout(200)
        a.append(pg.evaluate(f"{SET}.hidden"))
        print('A) Tabs:', [(t, s) for t, s, _ in t1], '| offen, Schließen innen, aria, wieder zu:', a)
        results.append([t for t, _, _ in t1] == ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'beta', 'connections']
                       and [t for t, s, _ in t1 if s == 'true'] == ['general'] and a == [True, 0, 'true', True])
        # B) keys
        pg.click(gear)
        pg.wait_for_timeout(200)
        pg.focus('[data-el=settings] .dci-set-tab[data-topic=general]')
        pg.keyboard.press('ArrowDown')
        pg.wait_for_timeout(150)
        k1 = [(t, f) for t, s, f in pg.evaluate(TABS) if s == 'true']
        pg.keyboard.press('End')
        pg.wait_for_timeout(150)
        k2 = [(t, f) for t, s, f in pg.evaluate(TABS) if s == 'true']
        pg.keyboard.press('Home')
        pg.wait_for_timeout(150)
        k3 = [(t, f) for t, s, f in pg.evaluate(TABS) if s == 'true']
        print('B) ↓:', k1, '| Ende:', k2, '| Pos1:', k3)
        results.append(k1 == [('appearance', True)] and k2 == [('connections', True)] and k3 == [('general', True)])
        # C) remembered
        pg.click('[data-el=settings] .dci-set-tab[data-topic=texts]')
        pg.wait_for_timeout(200)
        c1 = [pg.evaluate("localStorage.getItem('dci-settings-tab')"), pg.evaluate(f"!!{SET}.querySelector('.dci-set-pane [data-set=weblinks-show]')"),
              pg.evaluate(f"!!{SET}.querySelector('.dci-set-pane [data-act=rules]')")]
        pg.reload()
        pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.click(gear)
        pg.wait_for_timeout(300)
        c2 = [t for t, s, _ in pg.evaluate(TABS) if s == 'true']
        print('C) gespeichert, Links-Einstellung, Regeln-Knopf:', c1, '| nach Neuladen gewählt:', c2)
        results.append(c1 == ['"texts"', True, True] and c2 == ['texts'])
        pg.click(gear)
        # D) the ⓘ in the head
        pg.click('.dci-head [data-act=connections-open]')
        pg.wait_for_timeout(300)
        d1 = pg.evaluate(f"""(() => {{ const rows = [...{SET}.querySelectorAll('.dci-conn tbody tr')];
      const h = rows.find(r => r.dataset.conn === 'X005');
      return [rows.length, h ? [...h.cells].map(c => c.textContent.trim().slice(0, 40)) : null, h ? h.querySelector('a').href : '',
        [...{SET}.querySelectorAll('.dci-set-tab')].filter(b => b.getAttribute('aria-selected') === 'true').map(b => b.dataset.topic)]; }})()""")
        print('D) Verbindungen:', d1)
        results.append(d1[0] == 14 and d1[1][0] == 'Harmony' and d1[1][1] == 'Tool' and d1[1][2].startswith('Adds “Edit relationships with Credits')
                       and d1[1][3].startswith('@match harmony.pulsewidth.org.uk') and d1[1][4] == '3.19.1' and d1[2] == 'https://harmony.pulsewidth.org.uk/'
                       and d1[3] == ['connections'])
        # E) reset all, in the settings
        pg.click('[data-el=settings] .dci-set-tab[data-topic=works]')
        pg.click('[data-el=settings] [data-act=reset-open]')
        pg.wait_for_timeout(200)
        e1 = [pg.evaluate(f"!!{SET}.querySelector('.dci-set-pane [data-el=reset] [data-act=reset-do]')"),
              [t for t, s, _ in pg.evaluate(TABS) if s == 'true'], pg.evaluate("document.activeElement.dataset.act")]
        pg.click('[data-el=settings] [data-act=reset-cancel]')
        pg.wait_for_timeout(200)
        e2 = [pg.evaluate(f"!!{SET}.querySelector('[data-el=reset]')"), [t for t, s, _ in pg.evaluate(TABS) if s == 'true'],
              pg.evaluate("document.querySelectorAll('.dci-head [data-act=reset-open]').length")]
        print('E) Frage in den Einstellungen, gewählt, Fokus:', e1, '| nach Abbrechen:', e2)
        results.append(e1 == [True, [], 'reset-cancel'] and e2 == [False, ['works'], 0])
        # F) narrow
        tops = f"[...{SET}.querySelectorAll('.dci-set-tab')].slice(0, 2).map(b => Math.round(b.getBoundingClientRect().top))"
        wide = pg.evaluate(tops)
        pg.evaluate("(() => { const p = document.querySelector('#dci-overlay .dci-panel'); p.style.width = '470px'; })()")
        pg.wait_for_timeout(400)
        narrow = pg.evaluate(tops)
        print('F) breit (oben):', wide, '| schmal:', narrow)
        results.append(wide[0] != wide[1] and narrow[0] == narrow[1])
        # G) [3.27.2] the heading "Settings" folds them in (item 57)
        if pg.evaluate(f"{SET}.hidden"):
            pg.click(gear)
            pg.wait_for_timeout(200)
        title = pg.locator('[data-el=settings] .dci-set-title')
        g1 = [title.inner_text(), title.get_attribute('title'), pg.evaluate("getComputedStyle(document.querySelector('[data-el=settings] .dci-set-title')).textDecorationLine")]
        title.click()
        pg.wait_for_timeout(200)
        g2 = [pg.evaluate(f"{SET}.hidden"), pg.locator(gear).get_attribute('aria-expanded'), pg.evaluate("document.activeElement.dataset.act")]
        print('G) Überschrift:', g1, '| danach zu, aria, Fokus:', g2)
        results.append(g1 == ['Settings', 'Fold the settings in (as ⚙ does)', 'none'] and g2 == [True, 'false', 'settings-open'])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_settings():
    """Import 3.16.0: the menu "Settings" and the stored works of the artists.
    A) "⚙ Settings" in the head opens the menu: [3.25.0] eight tabs, "General" chosen; "Works" shows its defaults (on, 4000 with "= 40 requests,
       about 44 s per artist", 10 seconds, 900 entries, 7 days).
    B) Shared switches: "apply automatically" ticked in the menu ticks the switch below the date matrix (and is stored);
       "add role credits" ticked in the footer shows ticked in the menu.
    C) A value: 2,000 per artist is stored (with the new cost), 2,050 becomes 2,100 (steps of 100); a topic's "↺" asks and
       sets the topic back (the stored keys go).
    D) The works read are kept beyond reloading the page: loaded again, the release artist is not asked again ("from the
       store", the work is offered again); the menu says "7 artists stored" (release artist, writers, musicians); "Clear the
       stored works" asks and empties it –
       loaded again, the artist is asked again.
    E) Switched off ("Compare …" unticked, stored): after loading again nothing is asked, no hit is offered.
    F) A button of the Discogs view in the menu ("Track highlight") switches the same setting as the one in the head."""
    TB = H.uid('dddddddd', 60)
    W4 = H.uid('cccccccc', 94)
    H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
    H.ARTIST_WORKS.update({TB: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []}]})
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
    SET = "document.querySelector('[data-el=settings]')"
    results = []


    def open_set(pg, topic=None):
        """[3.25.0] the settings open, the tab of a topic chosen (one at a time)."""
        if pg.evaluate(f"{SET}.hidden"):
            pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
        if topic and pg.locator(f'[data-act=settings-topic][data-topic={topic}]').get_attribute('aria-selected') != 'true':
            pg.locator(f'[data-act=settings-topic][data-topic={topic}]').evaluate('b => b.click()'); pg.wait_for_timeout(200)


    def load(pg, wait_compare=True):
        """Loads the page again (the log of the release is kept: the lines of this load are the ones after those before)."""
        word = 'Works of the artists compared' if wait_compare else 'Checks complete'
        n = len([x for x in pg.evaluate(LOGS) if word in x])
        pg.reload(); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.filter(x => x.includes('{word}')).length > {n}", 90)
        pg.wait_for_timeout(500)


    def offered(pg):
        return pg.evaluate("[...document.querySelectorAll('tr[data-work=\"3\"] .dci-same [data-act=work-pick]')].map(b => b.dataset.gid)")


    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        DIALOGS = []
        pg.on('dialog', lambda d: (DIALOGS.append(d.message), d.accept()))
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
        pg.wait_for_timeout(300)
        # A) the menu
        open_set(pg)
        topics = pg.evaluate(f"[...{SET}.querySelectorAll('[data-act=settings-topic]')].map(b => [b.dataset.topic, b.getAttribute('aria-selected')])")
        open_set(pg, 'works')
        vals = pg.evaluate(f"""(() => {{ const s = {SET}; const v = (k) => s.querySelector('[data-set=' + k + ']');
      return [v('aw-on').checked, v('awMax').value, v('awSlowSec').value, v('awSlowN').value, v('awDays').value, s.querySelector('[data-el=aw-cost]').textContent]; }})()""")
        print('A) Themen:', topics, '| Werke:', vals)
        results.append([t for t, _ in topics] == ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'beta', 'connections']
                       and [t for t, e in topics if e == 'true'] == ['general']
                       and vals == [True, '4000', '10', '900', '7', '= 40 requests, about 44 s per artist'])
        # B) shared switches
        open_set(pg, 'dates')
        pg.locator('[data-el=settings] [data-f=dm-auto]').check(); pg.wait_for_timeout(400)
        below = pg.evaluate("[...document.querySelectorAll('[data-f=dm-auto]')].filter(x => !x.closest('[data-el=settings]')).map(x => x.checked)")
        stored = pg.evaluate("localStorage.getItem('dci-dm-auto')")
        open_set(pg, 'staging')
        pg.locator('footer [data-f=fill-credits]').evaluate('x => x.click()'); pg.wait_for_timeout(400)
        menu_fill = pg.evaluate(f"{SET}.querySelector('[data-f=fill-credits]').checked")
        print('B) „automatisch anwenden“ unter der Matrix:', below, '| gespeichert:', stored, '| „Rollen-Credits“ im Menü nach Klick unten:', menu_fill)
        results.append(below == [True] and stored == 'true' and menu_fill is True)
        # C) a value, steps, a topic's reset
        open_set(pg, 'works')
        f = pg.locator('[data-el=settings] [data-set=awMax]')
        f.fill('2000'); f.press('Enter'); pg.wait_for_timeout(300)
        v1 = [pg.evaluate("localStorage.getItem('dci-aw-max')"), pg.evaluate(f"{SET}.querySelector('[data-el=aw-cost]').textContent")]
        f = pg.locator('[data-el=settings] [data-set=awMax]')
        f.fill('2050'); f.press('Enter'); pg.wait_for_timeout(300)
        v2 = pg.evaluate("localStorage.getItem('dci-aw-max')")
        DIALOGS.clear()
        pg.locator('[data-el=settings] [data-act=settings-reset][data-topic=works]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        v3 = [pg.evaluate("localStorage.getItem('dci-aw-max')"), pg.evaluate(f"{SET}.querySelector('[data-set=awMax]').value")]
        asked = list(DIALOGS)
        print('C) 2000:', v1, '| 2050 →', v2, '| ↺ Werke:', asked, v3)
        results.append(v1 == ['2000', '= 20 requests, about 22 s per artist'] and v2 == '2100' and asked and '“Works”' in asked[0] and v3 == [None, '4000'])
        # D) kept beyond reloading
        n0 = len([1 for k, a, _ in H.BROWSES if a == TB])
        load(pg)
        n1 = len([1 for k, a, _ in H.BROWSES if a == TB])
        stored_log = [x for x in pg.evaluate(LOGS) if 'Test Band' in x and 'from the store' in x]
        hit = offered(pg)
        open_set(pg, 'works')
        pg.wait_for_timeout(500)
        count = pg.evaluate(f"({SET}.querySelector('[data-act=aw-clear]').parentElement.textContent || '').replace(/\\s+/g, ' ').trim()")
        DIALOGS.clear()
        pg.locator('[data-el=settings] [data-act=aw-clear]').evaluate('b => b.click()'); pg.wait_for_timeout(600)
        asked = list(DIALOGS)
        cleared = [x for x in pg.evaluate(LOGS) if 'Stored works cleared' in x]
        load(pg)
        n2 = len([1 for k, a, _ in H.BROWSES if a == TB])
        print('D) Anfragen an Test Band:', n0, '→ nach Neuladen', n1, '→ nach Leeren und Neuladen', n2, '|', stored_log, '| Treffer:', hit == [W4])
        print('   Menü:', count, '| Frage:', asked, '|', cleared)
        results.append(n0 == 2 and n1 == 2 and n2 == 4 and len(stored_log) == 1 and 'Test Band: 1 work from the store' in stored_log[0]
                       and hit == [W4] and '7 artists stored' in count and asked and 'of 7 artists' in asked[0] and cleared == ['Stored works cleared (7 artists)'])
        # E) switched off
        open_set(pg, 'works')
        pg.locator('[data-el=settings] [data-set=aw-on]').uncheck(); pg.wait_for_timeout(300)
        off_stored = pg.evaluate("localStorage.getItem('dci-aw-on')")
        nb = len(H.BROWSES)
        load(pg, wait_compare=False)
        pg.wait_for_timeout(2500)
        print('E) aus – gespeichert:', off_stored, '| neue Anfragen:', len(H.BROWSES) - nb, '| Treffer Track 4:', offered(pg))
        results.append(off_stored == 'false' and len(H.BROWSES) == nb and offered(pg) == [])
        # F) a button of the Discogs view in the menu
        open_set(pg, 'discogs')
        before = pg.evaluate("localStorage.getItem('dci-dg-hover')")
        pg.locator('[data-el=settings] [data-dg-hover]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
        after = [pg.evaluate("localStorage.getItem('dci-dg-hover')"), pg.evaluate("[...document.querySelectorAll('[data-dg-hover]')].map(b => b.getAttribute('aria-pressed'))")]
        print('F) Track-Hervorhebung:', before, '→', after)
        results.append(after[0] == 'false' and after[1] and all(x == 'false' for x in after[1]))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_bridge():
    """Credits Importer 3.30.4: the settings join their tabs, a bridge from ⚙ and "Mapping rules" to what they opened
    (collected item 87; the maintainer's screenshots of 2026-10-25 01:59).
    A) ⚙ Settings open: ⚙ pressed (tinted), a bridge from it to the box of the settings – below the symbol down to the head's
       lower edge, from there to the box, as wide as the symbol.
    B) Every tab: the content starts at the height of the chosen tab and the tab reaches into its frame – at 100 % and at
       90 % text size (until 3.30.3 the tabs below the content had nothing to join, at 90 % the tab stood out).
    C) "Mapping rules" in the dashboard: their symbol has the bridge, ⚙ not.
    D) The box scrolled away: only the part at the symbol stays; back: the whole bridge.
    E) Both closed: no bridge, nothing pressed."""
    BR = """(act) => { const btn = document.querySelector('.dci-head [data-act=' + act + ']'); const box = act === 'rules' ? document.querySelector('[data-el=rules-dock]') : document.querySelector('[data-el=settings]');
  const head = document.querySelector('.dci-head').getBoundingClientRect(); const b = btn.getBoundingClientRect(); const p = box.getBoundingClientRect(); const cs = getComputedStyle(box);
  const v = (k) => parseFloat(cs.getPropertyValue(k)) || 0;
  return { expanded: btn.getAttribute('aria-expanded'), bg: getComputedStyle(btn).backgroundColor, btnBridge: btn.classList.contains('dci-bridged'),
    down: parseFloat(getComputedStyle(btn).getPropertyValue('--dci-bridge-down')) || 0, downOk: Math.abs(b.bottom - 1 + (parseFloat(getComputedStyle(btn).getPropertyValue('--dci-bridge-down')) || 0) - head.bottom) <= 2,
    boxBridge: box.classList.contains('dci-bridged-box'), xOk: Math.abs(p.left + box.clientLeft + v('--dci-bridge-x') - b.left) <= 1, wOk: Math.abs(v('--dci-bridge-w') - b.width) <= 1,
    hOk: Math.abs(p.top - v('--dci-bridge-h') - head.bottom) <= 1 }; }"""
    TABS = """(() => { const el = document.querySelector('[data-el=settings]'); const pane = el.querySelector('.dci-set-pane').getBoundingClientRect();
  const sel = el.querySelector('.dci-set-tab[aria-selected=true]').getBoundingClientRect();
  return [Math.round(pane.top - sel.top), Math.round(sel.right - pane.left)]; })()"""
    TOPICS = ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'beta', 'connections']
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.set_viewport_size({'width': 1400, 'height': 900})
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(600)
        # A)
        H.open_settings(pg, 'general')
        pg.wait_for_timeout(300)
        a1 = pg.evaluate(BR, 'settings-open')
        print('A) ⚙:', a1)
        results.append(a1['expanded'] == 'true' and a1['bg'] == 'rgb(236, 235, 246)' and a1['btnBridge'] and a1['down'] > 0 and a1['downOk']
                       and a1['boxBridge'] and a1['xOk'] and a1['wOk'] and a1['hOk'])
        # B)
        b1 = {}
        for t in TOPICS:
            H.open_settings(pg, t)
            pg.wait_for_timeout(150)
            b1[t] = pg.evaluate(TABS)
        pg.click('[data-act=zoom-out]')
        pg.wait_for_timeout(300)
        b2 = {}
        for t in ('discogs', 'staging', 'dates'):
            H.open_settings(pg, t)
            pg.wait_for_timeout(150)
            b2[t] = pg.evaluate(TABS)
        a2 = pg.evaluate(BR, 'settings-open')
        pg.click('[data-act=zoom-in]')
        pg.wait_for_timeout(300)
        print('B) Inhalt − Reiter oben, Überlappung (100 %):', b1, '\n   90 %:', b2, '| Brücke 90 %:', [a2['xOk'], a2['hOk'], a2['downOk']])
        results.append(all(abs(d) <= 1 and 0 <= o <= 3 for d, o in list(b1.values()) + list(b2.values())) and a2['xOk'] and a2['hOk'] and a2['downOk'])
        # C)
        pg.click('.dci-head [data-act=rules]')
        pg.wait_for_timeout(400)
        c1, c2 = pg.evaluate(BR, 'rules'), pg.evaluate(BR, 'settings-open')
        print('C) Regeln:', c1, '| ⚙:', [c2['expanded'], c2['btnBridge']])
        results.append(c1['expanded'] == 'true' and c1['btnBridge'] and c1['boxBridge'] and c1['xOk'] and c1['hOk'] and c2['expanded'] == 'false' and not c2['btnBridge'])
        # D) scrolled away
        pg.evaluate("document.querySelector('#dci-overlay .dci-body').scrollTop = 400")
        pg.wait_for_timeout(300)
        d1 = pg.evaluate(BR, 'rules')
        pg.evaluate("document.querySelector('#dci-overlay .dci-body').scrollTop = 0")
        pg.wait_for_timeout(300)
        d2 = pg.evaluate(BR, 'rules')
        print('D) weggescrollt:', [d1['btnBridge'], d1['boxBridge']], '| zurück:', [d2['btnBridge'], d2['boxBridge'], d2['hOk']])
        results.append(d1['btnBridge'] and not d1['boxBridge'] and d2['btnBridge'] and d2['boxBridge'] and d2['hOk'])
        # E)
        pg.click('.dci-head [data-act=rules]')
        pg.wait_for_timeout(300)
        e1, e2 = pg.evaluate(BR, 'rules'), pg.evaluate(BR, 'settings-open')
        print('E) zu:', [e1['expanded'], e1['btnBridge'], e2['expanded'], e2['btnBridge'], e1['bg']])
        results.append(e1['expanded'] == 'false' and not e1['btnBridge'] and not e2['btnBridge'] and e1['bg'] == 'rgb(255, 255, 255)')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ui305():
    """Credits Importer 3.30.5: ⚙ below "Import credits …" opens only the settings, the tab "Source pages", tracks typed into
    a track group (collected items 88, 90; the maintainer's answers of 2026-10-25 02:28).
    A) Before any import: ⚙ in the bar below "Import credits …" opens the dashboard with its settings at "Source pages"
       (until 3.30.4 "Discogs and Bandcamp view"; the tab key stays "discogs") – the import does not start (no request to
       Discogs, nothing in the log about it); a message says so and offers "Start import". German: "Quellseiten".
    B) "Start import" in the message: the import runs, the message is gone.
    C) A new track group: the field "Tracks:" next to "Name" – "1-2, 4" ticks tracks 1, 2 and 4; ticks changed by hand show
       in the field ("1–3, 4" → "1–4"); "9" (no track of the release) is named in red and the group is not saved; "2-3"
       saves a group of tracks 2 and 3. Editing a group shows its tracks in the field."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=True)
        pg.on('dialog', lambda d: d.accept())
        reqs = []
        pg.on('request', lambda r: reqs.append(r.url))
        pg.wait_for_selector('#dci-open', timeout=20000)
        pg.wait_for_timeout(800)
        # A) settings only
        pg.locator('#dci-controls [data-nav-settings]').click()
        pg.wait_for_timeout(1500)
        a1 = pg.evaluate("""(() => { const o = document.getElementById('dci-overlay'); const tab = document.querySelector('.dci-set-tab[aria-selected=true]');
      return [!!o && !o.hidden, !document.querySelector('[data-el=settings]').hidden, tab ? [tab.dataset.topic, tab.textContent.trim()] : null,
        [...document.querySelectorAll('[data-el=msgs] .dci-msg')].map(m => [m.textContent.replace(/\\s+/g, ' ').trim().slice(0, 80), !!m.querySelector('[data-act=start-import]')]),
        document.querySelector('[data-el=toolbar]').hidden, [...document.querySelectorAll('#dci-log li')].some(li => /Import complete|Reading/.test(li.textContent))]; })()""")
        dg = [u for u in reqs if '/releases/' in u or 'discogs' in u.lower() and '/api' in u]
        print('A) nur Einstellungen:', a1, '| Anfragen an Discogs:', dg[:3])
        results.append(a1[0] and a1[1] and a1[2] == ['discogs', 'Source pages'] and len(a1[3]) == 1 and a1[3][0][1]
                       and 'has not started' in a1[3][0][0] and a1[4] and not a1[5] and not dg)
        # B) start the import from the message
        pg.click('[data-el=msgs] [data-act=start-import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        b1 = pg.evaluate("[[...document.querySelectorAll('[data-el=msgs] .dci-msg')].some(m => /has not started/.test(m.textContent)), document.querySelectorAll('section.dci-group').length]")
        print('B) nach „Start import“ – Hinweis noch da, Einträge:', b1)
        results.append(not b1[0] and b1[1] > 3)
        # C) tracks typed into a track group
        if pg.evaluate("document.querySelector('.dci-pools-toggle').getAttribute('aria-expanded')") != 'true':
            pg.click('.dci-pools-toggle')
            pg.wait_for_timeout(300)
        pg.click('[data-act=tg-new]')
        pg.wait_for_timeout(300)
        TICKS = "[...document.querySelectorAll('.dci-track-form input[data-f=tg-track]')].filter(c => c.checked).map(c => Number(c.dataset.i) + 1)"
        f = pg.locator('.dci-track-form input[data-f=tg-text]')
        f.fill('1-2, 4')
        pg.wait_for_timeout(200)
        c1 = [pg.evaluate(TICKS), pg.evaluate("document.activeElement.dataset.f")]
        pg.locator('.dci-track-form input[data-f=tg-track][data-i="2"]').check()
        pg.wait_for_timeout(200)
        c2 = [pg.evaluate(TICKS), f.input_value()]
        f.fill('9')
        pg.wait_for_timeout(200)
        c3 = [pg.evaluate(TICKS), pg.locator('.dci-track-form .dci-err').inner_text()]
        pg.click('[data-act=tg-save]')
        pg.wait_for_timeout(300)
        c4 = [pg.evaluate("!!document.querySelector('.dci-track-form')"), pg.locator('.dci-track-form .dci-err').inner_text()]
        f = pg.locator('.dci-track-form input[data-f=tg-text]')
        f.fill('2-3')
        pg.wait_for_timeout(200)
        f.press('Enter')
        pg.wait_for_timeout(400)
        pool = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-track-pool:{H.REL}') || '[]').map(g => [g.name, g.tracks])")
        gid = pg.evaluate("(document.querySelector('[data-act=tg-edit]') || {dataset: {}}).dataset.id")
        pg.click(f'[data-act=tg-edit][data-id="{gid}"]')
        pg.wait_for_timeout(300)
        c5 = pg.locator('.dci-track-form input[data-f=tg-text]').input_value()
        print('C) „1-2, 4“:', c1, '| Häkchen 3 dazu:', c2, '| „9“:', c3, '| Speichern mit „9“:', c4, '| „2-3“ gespeichert:', pool, '| bearbeiten:', c5)
        results.append(c1 == [[1, 2, 4], 'tg-text'] and c2 == [[1, 2, 3, 4], '1–4'] and c3[0] == [1, 2, 3, 4] and '9' in c3[1]
                       and c4[0] and '9' in c4[1] and pool == [['Tracks 2–3', [1, 2]]] and c5 == '2–3')
        # German name of the tab
        pg.click('[data-act=tg-cancel]')
        H.open_settings(pg, 'general')
        pg.select_option('[data-el=settings] [data-f=lang]', 'de')
        pg.wait_for_timeout(600)
        de = pg.evaluate("document.querySelector('.dci-set-tab[data-topic=discogs]').textContent.trim()")
        print('   Deutsch:', de)
        results.append(de == 'Quellseiten')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_reset():
    """“↺ Reset all settings …” (⚙ Settings; until 3.24 “↺ Defaults” in the head): all settings back to their defaults (language, text size, switches, matrix and pool options,
    the cover box on Discogs through the companion); own rules and stored pools only when ticked; the list of
    created works never."""
    import re

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        dg, dg_errs = H.open_discogs(ctx)
        dg.evaluate("localStorage.setItem('dci-art-pos', JSON.stringify({x: 5, y: 5})); localStorage.setItem('dci-art-collapsed', '1')")
        pg, errs = H.open_mb_edit(ctx)
        pg.evaluate("""() => { const set = (k, v) => localStorage.setItem(k, JSON.stringify(v));
      set('dci-sync-mode', 'hover'); set('dci-dg-artwork', false); set('dci-dm-auto', true); set('dci-fill-credits', true);
      set('dci-role-codes', 'gema'); set('dci-user-rules', [{ id: 'U001', kind: 'role', on: true, discogs: 'Foo', type: 'performer', level: 'recording' }]);
      set('dci-rules-off', ['R001']); set('dci-date-pool:other', [{ id: 'd1', name: 'X', begin: { year: 1999 }, end: { year: 1999 }, ended: true }]);
      set('dci-created-works:other', [{ i: 0, gid: 'g' }]); }""")
        pg.reload(); H.with_companion(pg); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.open_settings(pg, 'general')  # [3.26.0] the language is only in the settings
        pg.select_option('[data-f=lang]', 'de'); pg.wait_for_timeout(300)
        pg.click('[data-act=zoom-in]'); pg.click('[data-act=zoom-in]')
        pg.click('.dci-pools-toggle'); pg.wait_for_timeout(150)
        keys = lambda: pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-') && !k.startsWith('dci-geom')).sort()")
        print('Vorher:', keys(), '| Titel:', pg.locator('#dci-title').inner_text(), '| Zoom:', pg.locator('[data-el=zoom]').inner_text())
        # 1) settings and own rules, not the pools
        H.open_reset(pg); pg.wait_for_timeout(150)
        print('1) Dialog:', re.sub(r'\s+', ' ', pg.locator('[data-el=reset]').inner_text())[:260])
        pg.check('[data-f=reset-rules]')
        pg.click('[data-act=reset-do]'); pg.wait_for_timeout(2500)
        after = keys()
        art = dg.evaluate("[localStorage.getItem('dci-art-pos'), localStorage.getItem('dci-art-collapsed')]")
        print('   Nachher:', after)
        print('   Titel:', pg.locator('#dci-title').inner_text(), '| Zoom:', pg.locator('[data-el=zoom]').inner_text(), '| Meldung:', [m for m in pg.locator('.dci-msg').all_inner_texts() if 'defaults' in m])
        print('   Cover auf Discogs (Position, eingeklappt):', art, '| Daten & Tracks offen:', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'),
              '| automatisch anwenden:', pg.locator('[data-f=dm-auto]').is_checked() if pg.locator('[data-f=dm-auto]').count() else '–')
        settings = [k for k in after if not re.match(r'dci-(date-pool|date-matrix|track-pool|created-works):', k) and k not in ('dci-store-epoch', 'dci-notice-version', 'dci-lang-ask')]  # [3.26.0] the question of the language is no setting
        ok1 = set(settings) <= {'dci-log-open'} and 'dci-date-pool:other' in after and 'dci-created-works:other' in after \
            and pg.locator('#dci-title').inner_text() == 'Credits Importer' and pg.locator('[data-el=zoom]').inner_text() == '100 %' \
            and art == [None, None]
        # 2) with the pools: the stored pools of all releases go, the created works stay
        H.open_reset(pg); pg.wait_for_timeout(150)
        pg.check('[data-f=reset-pools]')
        pg.click('[data-act=reset-do]'); pg.wait_for_timeout(800)
        print('2) mit Pools:', keys())
        ok2 = 'dci-date-pool:other' not in keys() and 'dci-created-works:other' in keys()
        print('Ergebnis:', 'OK' if ok1 and ok2 else 'FEHLER', [ok1, ok2], '| Fehler:', errs, dg_errs)
        b.close()


def case_notice():
    """Update notice and the one-time reset of stored data: a first installation shows no notice; an update from a
    version before 2.11.0 clears all settings and data once (the list of created works stays) and shows the latest
    milestones with a note about the reset; closing it is remembered; an update from 2.9.0 shows the milestones
    since then; the notice follows the language; an update from 2.12.0 (storage generation 2) resets once more
    (generation 4, Credits Importer 3.5.0: a fresh start, the list of created works too). The companion clears its shared
    storage and the cover settings once."""
    import re

    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        keys = lambda: pg.evaluate("Object.keys(localStorage).filter(k => k.startsWith('dci-')).sort()")
        notice = lambda: re.sub(r'\s+', ' ', pg.locator('#dci-notice').inner_text()) if pg.locator('#dci-notice').count() else None
        reload = lambda: (pg.reload(), pg.add_script_tag(content=H.MAIN), pg.wait_for_selector('#dci-open', timeout=20000), pg.wait_for_timeout(300))
        print('1) Erstinstallation – Nachricht:', notice(), '| Speicher:', keys())
        ok1 = notice() is None and 'dci-notice-version' in keys() and 'dci-store-epoch' in keys()
        # 2) as if 2.10.0 ran before: old settings, own rules, pools, created works
        pg.evaluate("""() => { localStorage.clear(); const set = (k, v) => localStorage.setItem(k, JSON.stringify(v));
      set('dci-lang', 'de'); set('dci-user-rules', [{ id: 'U001' }]); set('dci-rules-off', ['R001']); set('dci-stamp-overwrite', false);
      set('dci-date-pool:x', [{ id: 'd1' }]); set('dci-created-works:x', [{ i: 0, gid: 'g' }]); set('dci-place', 'page'); }""")
        pg.evaluate("sessionStorage.setItem('dci-work-options', '{}')")
        reload()
        print('2) Update von 2.10.0 – Speicher:', keys(), '| Sitzung:', pg.evaluate("Object.keys(sessionStorage).filter(k => k.startsWith('dci-'))"))
        print('   Nachricht:', notice())
        n = notice() or ''
        ok2 = keys() == ['dci-notice-version', 'dci-store-epoch', 'dci-updated-from'] or set(keys()) == {'dci-store-epoch', 'dci-updated-from'}
        # [3.34.0] the three newest milestones: 3.34.0, 3.33.0, 3.32.0
        ok2 = ok2 and 'what’s new' in n and 'Credits Importer 3.34.0' in n and 'Credits Importer 3.33.0' in n and 'Credits Importer 3.32.0' in n and 'Credits Importer 3.31.0' not in n and 'reset once' in n
        # 3) closing is remembered
        pg.click('#dci-notice .dci-notice-x'); pg.wait_for_timeout(200)
        reload()
        print('3) geschlossen, neu geladen – Nachricht:', notice(), '| gesehen:', pg.evaluate("localStorage.getItem('dci-notice-version')"))
        ok3 = notice() is None and 'dci-updated-from' not in keys()
        # 4) update from 2.9.0, dashboard language German: the milestones since then, in German
        pg.evaluate("localStorage.setItem('dci-notice-version', JSON.stringify('2.9.0')); localStorage.setItem('dci-lang', JSON.stringify('de'))")
        reload()
        print('4) Update von 2.9.0 (Deutsch):', notice())
        n = notice() or ''
        ok4 = 'das ist neu' in n and 'Import 2.13.0' in n and 'Import 2.11.0' in n and 'Import 2.10.0' in n and 'Import 2.9.0' not in n and 'Daten des Skripts einmal zurückgesetzt' not in n
        # 4b) update from 2.12.0 (generation 2): reset once more, the milestone of 2.13.0 and the note about the reset
        pg.click('#dci-notice .dci-notice-x'); pg.wait_for_timeout(100)
        pg.evaluate("""() => { const set = (k, v) => localStorage.setItem(k, JSON.stringify(v));
      set('dci-notice-version', '2.12.0'); localStorage.setItem('dci-store-epoch', '2'); set('dci-pools-keep', false); set('dci-lang', 'en'); }""")
        reload()
        n = notice() or ''
        print('4b) Update von 2.12.0:', keys(), '|', n[:160])
        ok4 = ok4 and 'Import 2.13.0' in n and 'Import 2.11.0' not in n and 'reset once' in n and 'dci-pools-keep' not in keys() \
            and pg.evaluate("localStorage.getItem('dci-store-epoch')") == '4'
        # 5) the companion: shared storage and the cover box settings on Discogs are cleared once
        dg, dg_errs = H.open_discogs(ctx)
        dg.wait_for_timeout(500)
        dg.evaluate("""() => { GM_deleteValue('storeEpoch'); GM_setValue('statusMapIndex', ['x']); GM_setValue('statusMap:x', { a: 1 });
      localStorage.setItem('dci-art-pos', '{"x":5,"y":5}'); localStorage.removeItem('dci-store-epoch'); }""")
        dg.wait_for_timeout(300)
        dg.reload(); H.with_companion(dg); dg.wait_for_timeout(1200)
        gm = dg.evaluate("[GM_getValue('statusMapIndex'), GM_getValue('statusMap:x'), GM_getValue('storeEpoch'), localStorage.getItem('dci-art-pos'), localStorage.getItem('dci-store-epoch')]")
        print('5) Companion nach Update:', gm)
        ok5 = gm[0] is None and gm[1] is None and gm[2] == 4 and gm[3] is None and gm[4] == '4'
        print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4, ok5]) else 'FEHLER', [ok1, ok2, ok3, ok4, ok5], '| Fehler:', errs, dg_errs)
        b.close()


run_cases(globals())
