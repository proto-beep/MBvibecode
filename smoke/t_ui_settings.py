"""Settings: tabs, the menu, the symbols of the head pressed (until 3.36.4: the bridge to ⚙), settings without an import, reset, the update notice (Credits Importer 3.31.1: the tests of this topic as cases, collected item 103).

Cases: settabs, settings, pressed (until 3.36.4: bridge), ui305, reset, notice, cache (3.36.0), cache2 (3.36.1), logdiag (3.36.2), stats (3.38.0) – each the former smoke/t_<case>.py, unchanged; `python3 t_ui_settings.py <case> …` runs only those."""
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_settabs():
    """Credits Importer 3.25.0: the settings as tabs (collected items 42, 41, 40).
    A) "⚙ Settings" folds the settings out and in (only the gear: no "Close" inside); eight tabs, "General" chosen ([3.29.2] nine: "Appearance" after "General").
    B) Keys: ↓ the next tab ("Appearance"; chosen, focused), End the last, Home the first.
    C) The tab is remembered (here "Texts", with "Show the web links …" and a button to "Mapping rules"); after reloading
       the settings open on it.
    D) The ⓘ in the head opens the settings at "ⓘ Connections": a table of the connections ([3.32.10] twelve, [3.34.6] sixteen) (Harmony with its home page,
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
        results.append([t for t, _, _ in t1] == ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'beta', 'cache', 'statistics', 'connections']
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
        # D) the connections ([3.36.5] the ⓘ in the head is gone, collected item 147c: ⚙ → ⓘ Connections)
        H.open_settings(pg, 'connections')
        pg.wait_for_timeout(300)
        d1 = pg.evaluate(f"""(() => {{ const rows = [...{SET}.querySelectorAll('.dci-conn tbody tr')];
      const h = rows.find(r => r.dataset.conn === 'X005');
      return [rows.length, h ? [...h.cells].map(c => c.textContent.trim().slice(0, 40)) : null, h ? h.querySelector('a').href : '',
        [...{SET}.querySelectorAll('.dci-set-tab')].filter(b => b.getAttribute('aria-selected') === 'true').map(b => b.dataset.topic)]; }})()""")
        print('D) Verbindungen:', d1)
        results.append(d1[0] == 16 and d1[1][0] == 'Harmony' and d1[1][1] == 'Tool' and d1[1][2].startswith('Adds “Edit relationships with Credits')
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
        results.append([t for t, _ in topics] == ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'beta', 'cache', 'statistics', 'connections']
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


def case_pressed():
    """Credits Importer 3.36.5 (until 3.36.4 the case "bridge", 3.30.4): the symbols of the head show what is open, without a bridge
    (collected items 147, 149; maintainer: "dass das symbol im oberen bereich lila dunkler wird wenn die "keyboard shortcuts"
    geklickt werden finde ich ganz gut. können wir das bei allen anderen symbolen auch einführen? dann also auch auf die visuelle
    verbindung bei den einstellung verzichten", "Brücke weg", "Alle Umschalter dieser Art bitte").
    A) ⚙ Settings open: ⚙ pressed (tinted), no bridge (until 3.36.4: a strip from the symbol to the box of the settings).
    B) Every tab: the tab joins the side of the content and reaches into its frame – at 100 % and at 90 % text size; [3.34.3]
       the content as high as it can be: at the top of the tabs, or (too short for that) just low enough that the tab joins it
       with a little side below it; its upper left corner square only where the tab joins at the top.
    C) "Mapping rules" in the dashboard: their symbol pressed, no bridge; ⚙ not pressed.
    D) The log: its symbol pressed while it is shown, not when hidden; ⌨ pressed while the shortcuts are open; A−, A+, ⤢ and ✕
       never.
    E) Both closed: nothing pressed.
    F) Switches show their choice: "Entries: Matrix | Legacy" in the settings and "by event | by role" at an entry – the chosen
       button filled purple with white text, the other white."""
    BR = """(act) => { const btn = document.querySelector('.dci-head [data-act=' + act + ']'); const box = act === 'rules' ? document.querySelector('[data-el=rules-dock]') : document.querySelector('[data-el=settings]');
  return { expanded: btn.getAttribute('aria-expanded'), bg: getComputedStyle(btn).backgroundColor, after: getComputedStyle(btn, '::after').content,
    before: box ? getComputedStyle(box, '::before').content : 'none', bridgeClass: btn.className.includes('bridge') || (!!box && box.className.includes('bridge')) }; }"""
    TABS = """(() => { const el = document.querySelector('[data-el=settings]'); const paneEl = el.querySelector('.dci-set-pane'); const pane = paneEl.getBoundingClientRect();
  const sel = el.querySelector('.dci-set-tab[aria-selected=true]').getBoundingClientRect(); const first = el.querySelector('.dci-set-tab').getBoundingClientRect();
  return { above: Math.round((pane.top - sel.top) * 10) / 10, below: Math.round((pane.bottom - sel.bottom) * 10) / 10, into: Math.round(sel.right - pane.left),
    margin: parseFloat(paneEl.style.marginTop) || 0, atTabsTop: Math.abs(pane.top - first.top) <= 1, joinedTop: paneEl.classList.contains('dci-set-joined-top'),
    corner: getComputedStyle(paneEl).borderTopLeftRadius }; })()"""
    HEAD = """(() => [...document.querySelectorAll('.dci-head .dci-headbtn')].map(b => [b.dataset.act || b.textContent.trim(), b.getAttribute('aria-pressed') || b.getAttribute('aria-expanded') || '',
  getComputedStyle(b).backgroundColor]))()"""
    SEG = """(sel) => [...document.querySelectorAll(sel)].slice(0, 2).map(b => [b.textContent.trim(), b.getAttribute('aria-pressed'), getComputedStyle(b).backgroundColor, getComputedStyle(b).color])"""
    TINT, WHITE, PURPLE = 'rgb(236, 235, 246)', 'rgb(255, 255, 255)', 'rgb(115, 109, 171)'
    def tab_ok(t):
        # the tab within the side of the content, a little side below it; as high as can be; the corner square only at a join at the top
        return (t['above'] <= 1 and t['below'] >= 4.5 and 0 <= t['into'] <= 3 and (t['atTabsTop'] or abs(t['below'] - 6) <= 1)
                and t['joinedTop'] == (abs(t['above']) <= 1) and (t['corner'] == '0px') == t['joinedTop'])
    no_bridge = lambda x: x['after'] in ('none', 'normal') and x['before'] in ('none', 'normal') and not x['bridgeClass']
    TOPICS = ['general', 'appearance', 'sources', 'texts', 'discogs', 'works', 'staging', 'dates', 'beta', 'cache', 'statistics', 'connections']
    results = []
    # (the matrix of the entries, for "by event | by role")
    H.ENTRIES_VIEW = 'matrix'
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
        results.append(a1['expanded'] == 'true' and a1['bg'] == TINT and no_bridge(a1))
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
        pg.click('[data-act=zoom-in]')
        pg.wait_for_timeout(300)
        print('B) Inhalt und Reiter (100 %):', b1, '\n   90 %:', b2)
        results.append(all(tab_ok(t) for t in list(b1.values()) + list(b2.values()))
                       # the list of the connections from the top, its tab in the middle; the first tab joins at the top; a short one lower
                       and b1['connections']['margin'] == 0 and b1['connections']['above'] < -100 and b1['connections']['below'] > 100
                       and b1['general']['joinedTop'] and b1['discogs']['margin'] > 0 and not b1['discogs']['joinedTop'])
        # F) the switch "Entries" in the settings (Appearance)
        H.open_settings(pg, 'appearance')
        pg.wait_for_timeout(200)
        f1 = pg.evaluate(SEG, '[data-el=settings] [data-act=entries-view]')
        # C)
        pg.click('.dci-head [data-act=rules]')
        pg.wait_for_timeout(400)
        c1, c2 = pg.evaluate(BR, 'rules'), pg.evaluate(BR, 'settings-open')
        print('C) Regeln:', c1, '| ⚙:', c2)
        results.append(c1['expanded'] == 'true' and c1['bg'] == TINT and no_bridge(c1) and c2['expanded'] == 'false' and c2['bg'] == WHITE)
        # D) the log (shown when the dashboard opens), ⌨ and the symbols that only do something
        if pg.evaluate("document.getElementById('dci-log').hidden"):
            pg.click('.dci-head [data-act=log]')
            pg.wait_for_timeout(300)
        d1 = {x[0]: x[1:] for x in pg.evaluate(HEAD)}
        shown = pg.evaluate("!document.getElementById('dci-log').hidden")
        pg.click('.dci-head [data-act=log]')
        pg.wait_for_timeout(300)
        d2 = {x[0]: x[1:] for x in pg.evaluate(HEAD)}
        hidden = pg.evaluate("document.getElementById('dci-log').hidden")
        pg.click('.dci-head [data-act=keys-open]')
        pg.wait_for_timeout(300)
        d3 = {x[0]: x[1:] for x in pg.evaluate(HEAD)}
        pg.click('.dci-head [data-act=keys-open]')
        pg.wait_for_timeout(200)
        print('D) Log an:', shown, d1.get('log'), '| zu:', hidden, d2.get('log'), '| ⌨:', d3.get('keys-open'), '| A−, A+, ⤢:', [d3.get(k) for k in ('zoom-out', 'zoom-in', 'window-reset')])
        results.append(shown and hidden and d1['log'] == ['true', TINT] and d2['log'] == ['false', WHITE] and d3['keys-open'] == ['true', TINT]
                       and all(d3[k][0] == '' for k in ('zoom-out', 'zoom-in', 'window-reset')) and 'connections-open' not in d3)
        # E)
        pg.click('.dci-head [data-act=rules]')
        pg.wait_for_timeout(300)
        e1, e2 = pg.evaluate(BR, 'rules'), pg.evaluate(BR, 'settings-open')
        print('E) zu:', [e1['expanded'], e2['expanded'], e1['bg']])
        results.append(e1['expanded'] == 'false' and e2['expanded'] == 'false' and e1['bg'] == WHITE)
        # F) "by event | by role" at an entry of the compact matrix
        pg.click('.dci-head [data-act=view-toggle]')
        pg.wait_for_timeout(500)
        f2 = pg.evaluate(SEG, '.dci-em-by button')
        print('F) Entries:', f1, '| by event / by role:', f2)
        seg_ok = lambda f: len(f) == 2 and [x[1] for x in f].count('true') == 1 and all((x[2], x[3]) == ((PURPLE, WHITE) if x[1] == 'true' else (WHITE, 'rgb(38, 36, 48)')) for x in f)
        results.append(seg_ok(f1) and seg_ok(f2))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    H.ENTRIES_VIEW = 'legacy'
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_settingsscroll():
    """Credits Importer 3.34.3: scrolling up in the dashboard with ⚙ Settings → ⓘ Connections open and "Dates & tracks"
    expanded (collected item 122; maintainer: "ich habe das I Fenster in den Einstellungen offen und kann nicht mehr hochscrollen
    wenn der Dates & Tracks Pool aufgeklappt ist. Der Scrollbalken zappelt und wird sozusagen zurückgehalten.").
    A) Scrolled down, then up in small steps with the wheel: never back down, up to the top (until 3.34.2 every scroll event took
       the margin of the settings' content away and set it again; the browser's scroll anchoring answered by scrolling back,
       278px, again and again).
    B) Scrolling does not touch the margin of the content (no new value while nothing changes)."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=True)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        if pg.evaluate("document.querySelector('.dci-pools-toggle').getAttribute('aria-expanded')") != 'true':
            pg.click('.dci-pools-toggle')
            pg.wait_for_timeout(300)
        H.open_settings(pg, 'connections')
        pg.wait_for_timeout(500)
        pg.evaluate("""(() => { window.__tr = []; window.__styles = 0; const body = document.querySelector('#dci-overlay [data-el=body]');
      body.addEventListener('scroll', () => window.__tr.push(Math.round(body.scrollTop)), { passive: true });
      new MutationObserver((ms) => { window.__styles += ms.length; }).observe(document.querySelector('.dci-set-pane'), { attributes: true, attributeFilter: ['style', 'class'] }); })()""")
        box = pg.locator('[data-el=settings] .dci-set-pane').bounding_box()
        pg.mouse.move(box['x'] + 50, box['y'] + 50)
        for _ in range(12):
            pg.mouse.wheel(0, 300)
            pg.wait_for_timeout(50)
        pg.wait_for_timeout(400)
        down = pg.evaluate("document.querySelector('#dci-overlay [data-el=body]').scrollTop")
        pg.evaluate("window.__tr = []")
        for _ in range(int(down / 15) + 20):
            pg.mouse.wheel(0, -15)
            pg.wait_for_timeout(30)
        pg.wait_for_timeout(500)
        tr = pg.evaluate("window.__tr")
        top = pg.evaluate("document.querySelector('#dci-overlay [data-el=body]').scrollTop")
        back = [(tr[i - 1], tr[i]) for i in range(1, len(tr)) if tr[i] > tr[i - 1]]
        print('A) unten:', down, '| zurück nach unten gesprungen:', back[:5], '| oben:', top)
        results.append(down > 1500 and not back and top == 0)
        styles = pg.evaluate("window.__styles")
        print('B) Änderungen am Inhalt beim Scrollen:', styles)
        results.append(styles == 0)
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
        # [3.36.0] what is remembered for a release (its rows, the index of the releases) is no setting either
        settings = [k for k in after if not re.match(r'dci-(date-pool|date-matrix|track-pool|created-works|remember):', k) and k not in ('dci-store-epoch', 'dci-notice-version', 'dci-lang-ask', 'dci-remember-index')]  # [3.26.0] the question of the language is no setting
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
        # [3.34.0] the three newest milestones: 3.34.0, 3.33.0, 3.32.0; [3.35.0] 3.35.0, 3.34.0, 3.33.0; [3.36.0] 3.36.0, 3.35.0, 3.34.0;
        # [3.37.0] 3.37.0, 3.36.0, 3.35.0
        ok2 = ok2 and 'what’s new' in n and 'Credits Importer 3.37.0' in n and 'Credits Importer 3.36.0' in n and 'Credits Importer 3.35.0' in n and 'Credits Importer 3.34.0' not in n and 'reset once' in n
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


def case_cache():
    """Credits Importer 3.36.0 (collected item 146; maintainer: "global einen schalter … der sich änderungen und import
    einstellungen an releases merkt oder eben nicht. standardmäßig auf jeden fall aus", "ja genau, soll alles wieder kommen",
    "bitte nach deinem vorschlag", "setting -> Cache", "50 releases ist gut, aber lass das doch auch einstellen … den gebrauchten
    speicher anzeigen in KB oder MB mit einer kommazahl", "bitte 1-100. 0=aus", 146d "ja einverstanden"): remembered per release.
    A) The script's default: ⚙ Settings → "Cache" (after Beta), "Remember changes and import settings per release" off, 50
       releases, "Forget all …" not to click, "0 releases · 0.0 KB · all data of the script in this browser: … KB".
    B) Off: a role credit typed (Bass Man "fretless"), Photo Guy taken out (Skip), a date in the pool – the page loaded again:
       all as from the source, nothing of the release stored (no pool, no rows).
    C) On: what the tab holds stored at once ("1 release · … KB"); the same changes, the page loaded again: they come back
       (the log says so).
    D) The source changed (Photo Guy no longer credited, Bass Man "Electric Bass"): what was changed of their lines is left out
       ("2 remembered changes no longer fit the source"), the pool date is there.
    E) The number 0: the switch goes off; ticked again: 50.
    F) Another release stored before (a pool of its own, used earlier): with 1 release to remember it is forgotten – when something
       is stored next (3.36.1; not at each step of the field).
    G) "Forget all remembered releases …" (asked): nothing of the release stored any more, "0 releases"."""
    import re
    H.REMEMBER = False
    rel_key = lambda p: f'dci-{p}:{H.REL}'
    CACHE = """(() => { const pane = document.querySelector('.dci-set-pane'); const tabs = [...document.querySelectorAll('.dci-set-tab')].map(t => t.textContent.trim());
      const sw = pane && pane.querySelector('[data-set=remember]'); const n = pane && pane.querySelector('[data-set=remember-max]');
      const f = pane && pane.querySelector('[data-act=remember-forget]'); const z = pane && pane.querySelector('[data-el=remember-size]');
      return { tabs, on: sw ? sw.checked : null, max: n ? n.value : null, forget: f ? !f.disabled : null, size: z ? z.textContent.replace(/\\s+/g, ' ').trim() : '' }; })()"""
    ROWS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => [(tr.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level, (tr.querySelector('[data-f=role-credit]') || { value: '-' }).value]) : null; }"""
    orig = H.discogs_release
    results = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())

            def load():
                pg.wait_for_selector('#dci-open', timeout=20000)
                H.open_dashboard(pg)
                H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
                pg.wait_for_timeout(1200)

            def again():
                pg.reload()
                pg.add_script_tag(content=H.MAIN)
                load()

            def change():
                bass = pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Bass Man'); return g.querySelector('tr.dci-row').dataset.row; })()")
                pg.fill(f'tr.dci-row[data-row="{bass}"] [data-f=role-credit]', 'fretless')
                pg.press(f'tr.dci-row[data-row="{bass}"] [data-f=role-credit]', 'Tab')
                photo = pg.evaluate("(() => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === 'Photo Guy'); return g.querySelector('tr.dci-row').dataset.row; })()")
                pg.click(f'tr.dci-row[data-row="{photo}"] [data-act=level][data-level=skip]')
                if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
                    pg.click('.dci-pools-toggle')
                pg.click('[data-act=pool-new]')
                pg.fill('[data-f=pf-name]', 'Kept')
                pg.fill('[data-f=pf-by]', '2019')
                pg.click('[data-act=pool-save]')
                pg.wait_for_timeout(1600)
            state = lambda: (pg.evaluate(ROWS, 'Bass Man'), pg.evaluate(ROWS, 'Photo Guy'), pg.evaluate("[...document.querySelectorAll('.dci-pchip-date')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Kept/.test(t)).length"))
            stored = lambda: pg.evaluate("(keys) => keys.filter(k => localStorage.getItem(k) !== null)", [rel_key('date-pool'), rel_key('remember'), 'dci-remember-index'])
            load()
            H.open_settings(pg, 'cache')
            a = pg.evaluate(CACHE)
            print('A) Cache:', a)
            results.append(a['tabs'][-4:] == ['Beta', 'Cache', 'Statistics', 'ⓘ Connections'] and a['on'] is False and a['max'] == '50' and a['forget'] is False
                           and re.match(r'^0 releases · 0\.0 KB · all data of the script in this browser: \d+\.\d KB$', a['size']) is not None)
            change()
            b0 = state()
            again()
            b1 = state()
            print('B) aus – geändert:', b0, '| neu geladen:', b1, '| gespeichert:', stored())
            results.append(b0 == ([['recording', 'fretless']], [['skip', '-']], 1) and b1 == ([['recording', '']], [['release', '']], 0) and stored() == [])
            H.open_settings(pg, 'cache')
            pg.click('.dci-set-pane [data-set=remember]')
            pg.wait_for_timeout(500)
            c0 = pg.evaluate(CACHE)
            change()
            again()
            c1 = state()
            logl = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /remembered change/.test(t))")
            print('C) an:', c0, '| neu geladen:', c1, '| Log:', logl, '| gespeichert:', stored())
            results.append(c0['on'] is True and c0['size'].startswith('1 release · ') and c1 == ([['recording', 'fretless']], [['skip', '-']], 1)
                           and bool(logl) and stored() == [rel_key('date-pool'), rel_key('remember'), 'dci-remember-index'])

            def rel2():
                d = orig()
                d['extraartists'] = [x for x in d['extraartists'] if x['name'] != 'Photo Guy']
                for x in d['extraartists']:
                    if x['name'] == 'Bass Man':
                        x['role'] = 'Electric Bass'
                return d
            H.discogs_release = rel2
            again()
            d1 = state()
            msg = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /no longer fit/.test(t))")
            print('D) Quelle geändert:', d1, '| Meldung:', msg)
            results.append(d1[1] is None and d1[0] and d1[0][0][1] != 'fretless' and d1[2] == 1 and bool(msg) and msg[0].startswith('2 remembered changes no longer fit the source'))
            H.discogs_release = orig
            H.open_settings(pg, 'cache')
            pg.fill('.dci-set-pane [data-set=remember-max]', '0')
            pg.press('.dci-set-pane [data-set=remember-max]', 'Tab')
            pg.wait_for_timeout(400)
            e0 = pg.evaluate(CACHE)
            e0s = pg.evaluate("localStorage.getItem('dci-remember-on')")
            pg.click('.dci-set-pane [data-set=remember]')
            pg.wait_for_timeout(400)
            e1 = pg.evaluate(CACHE)
            print('E) 0:', e0['on'], e0['max'], e0s, '| wieder an:', e1['on'], e1['max'])
            results.append(e0['on'] is False and e0['max'] == '0' and e0s is None and e1['on'] is True and e1['max'] == '50')
            other = '11111111-2222-4333-8444-555555555555'
            pg.evaluate("(id) => { localStorage.setItem('dci-date-pool:' + id, JSON.stringify([{ id: 'd1', name: 'Old' }]));"
                        " localStorage.setItem('dci-remember-index', JSON.stringify([[id, 1]])); }", other)
            pg.fill('.dci-set-pane [data-set=remember-max]', '1')
            pg.press('.dci-set-pane [data-set=remember-max]', 'Tab')
            pg.wait_for_timeout(400)
            # [3.36.1] the oldest go when something is stored next (not at each step of the field)
            f0 = pg.evaluate("(id) => localStorage.getItem('dci-date-pool:' + id) !== null", other)
            pg.click('[data-act=pool-new]')
            pg.fill('[data-f=pf-name]', 'Next')
            pg.fill('[data-f=pf-by]', '2020')
            pg.click('[data-act=pool-save]')
            pg.wait_for_timeout(400)
            f1 = pg.evaluate("(id) => [localStorage.getItem('dci-date-pool:' + id), JSON.parse(localStorage.getItem('dci-remember-index') || '[]').map(x => x[0])]", other)
            print('F) anderes Release: noch da', f0, '| nach dem Speichern:', f1)
            results.append(f0 and f1[0] is None and f1[1] == [H.REL])
            pg.click('.dci-set-pane [data-act=remember-forget]')
            pg.wait_for_timeout(500)
            g1 = pg.evaluate(CACHE)
            print('G) vergessen:', g1['size'], '| gespeichert:', stored())
            results.append(g1['size'].startswith('0 releases · ') and stored() == [] and g1['forget'] is False)
            print('Fehler:', errs)
            results.append(not errs)
            b.close()
    finally:
        H.discogs_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_cache2():
    """Credits Importer 3.36.1 (the review of 3.36.0): remembered per release – removed rows, another source, a tab opened while off.
    A) On: Bass Man credited "fretless", Photo Guy's row removed (✕) – the page loaded again: "fretless", Photo Guy without a row
       (before: his row came back as a new line of the source).
    B) A pasted text imported (another source of the release), the page loaded again: Bass Man still "fretless" – the text has a
       snapshot of its own (before: it replaced the one of Discogs).
    C) Off, the page loaded again (nothing read: Bass Man without credit); switched on: a message "This release was remembered
       before …" with "Load the page again"; a credit typed meanwhile is not stored (what was remembered is not written over);
       loaded again: "fretless" back."""
    H.REMEMBER = True
    ROWS = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name);
      return g ? [...g.querySelectorAll('tr.dci-row')].map(tr => [(tr.querySelector('[data-act=level][aria-pressed=true]') || { dataset: {} }).dataset.level, (tr.querySelector('[data-f=role-credit]') || { value: '-' }).value]) : null; }"""
    row_of = "(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(x => x.querySelector('.dci-gname strong').textContent.trim() === name); const t = g && g.querySelector('tr.dci-row'); return t ? t.dataset.row : ''; }"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())

        def load():
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
            pg.wait_for_timeout(1200)

        def again():
            pg.reload()
            pg.add_script_tag(content=H.MAIN)
            load()

        def credit(text):
            r = pg.evaluate(row_of, 'Bass Man')
            pg.fill(f'tr.dci-row[data-row="{r}"] [data-f=role-credit]', text)
            pg.press(f'tr.dci-row[data-row="{r}"] [data-f=role-credit]', 'Tab')
        load()
        credit('fretless')
        photo = pg.evaluate(row_of, 'Photo Guy')
        pg.click(f'tr.dci-row[data-row="{photo}"] [data-act=remove-row]')
        pg.wait_for_timeout(1600)
        again()
        a1 = (pg.evaluate(ROWS, 'Bass Man'), pg.evaluate(ROWS, 'Photo Guy'))
        print('A) neu geladen:', a1)
        results.append(a1[0] == [['recording', 'fretless']] and not a1[1])
        H.src_menu(pg, 'text-open')
        pg.fill('[data-f=text-src]', 'Jane Roe – guitar')
        pg.click('[data-act=text-load]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1600)
        jane = pg.evaluate(ROWS, 'Jane Roe')
        again()
        b1 = pg.evaluate(ROWS, 'Bass Man')
        print('B) Text:', jane, '| neu geladen:', b1)
        results.append(bool(jane) and b1 == [['recording', 'fretless']])
        H.open_settings(pg, 'cache')
        pg.click('.dci-set-pane [data-set=remember]')
        pg.wait_for_timeout(300)
        again()
        c0 = pg.evaluate(ROWS, 'Bass Man')
        H.open_settings(pg, 'cache')
        pg.click('.dci-set-pane [data-set=remember]')
        pg.wait_for_timeout(300)
        msg = pg.evaluate("[...document.querySelectorAll('.dci-msg')].map(m => m.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /remembered before/.test(t))")
        credit('typed meanwhile')
        pg.wait_for_timeout(1600)
        again()
        c1 = pg.evaluate(ROWS, 'Bass Man')
        print('C) aus, neu geladen:', c0, '| Meldung:', msg, '| an, neu geladen:', c1)
        results.append(c0 == [['recording', '']] and bool(msg) and 'Load the page again' in msg[0] and c1 == [['recording', 'fretless']])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_logdiag():
    """Credits Importer 3.36.2 (maintainer: "Bitte eine Option, die die Diagnose Funktion im Log ermöglicht oder den Button
    ausblendet. Standardmäßig aus."): the diagnosis in the log as a setting.
    A) The log open: no "Start diagnosis"; ⚙ Settings → General "Diagnosis in the log" off.
    B) On: the button in the log, stored.
    C) Diagnosis started, the setting off: it stops (the log says so), the button goes.
    D) On again, "↺ Defaults" of General: off, no button."""
    DIAGBTN = "!!document.querySelector('#dci-log [data-log-act=diag]')"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.open_settings(pg, 'general')
        a = [pg.evaluate(DIAGBTN), pg.locator('.dci-set-pane [data-set=log-diag]').is_checked()]
        pg.click('.dci-set-pane [data-set=log-diag]')
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate(DIAGBTN), pg.evaluate("localStorage.getItem('dci-log-diag')")]
        pg.evaluate("document.querySelector('#dci-log [data-log-act=diag]').click()")  # the log window may lie below the dashboard
        pg.wait_for_timeout(700)
        c0 = pg.evaluate("(document.querySelector('#dci-log [data-log-act=diag]') || {}).textContent || ''")
        pg.click('.dci-set-pane [data-set=log-diag]')
        pg.wait_for_timeout(300)
        c1 = [pg.evaluate(DIAGBTN), pg.evaluate("[...document.querySelectorAll('#dci-log li')].some(li => /Diagnosis stopped/.test(li.textContent))"), pg.evaluate("localStorage.getItem('dci-log-diag')")]
        pg.click('.dci-set-pane [data-set=log-diag]')
        pg.wait_for_timeout(300)
        pg.click('.dci-set-pane [data-act=settings-reset][data-topic=general]')
        pg.wait_for_timeout(500)
        d1 = [pg.evaluate(DIAGBTN), pg.locator('.dci-set-pane [data-set=log-diag]').is_checked(), pg.evaluate("localStorage.getItem('dci-log-diag')")]
        print('A) Standard:', a, '| B) an:', b1, '| C) gestartet:', c0, '→ aus:', c1, '| D) zurückgesetzt:', d1)
        results.append(a == [False, False] and b1 == [True, 'true'] and c0 == 'Stop diagnosis' and c1 == [False, True, None] and d1 == [False, False, None])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


# [E8] (3.38.0) the statistics: helpers
ENTER_EDIT = """(() => { if (document.getElementById('test-enter-edit')) return; const ta = document.getElementById('edit-note-text'); const f = document.createElement('form');
  f.addEventListener('submit', (e) => e.preventDefault()); ta.parentNode.insertBefore(f, ta); f.appendChild(ta); const btn = document.createElement('button');
  btn.type = 'submit'; btn.className = 'submit positive'; btn.textContent = 'Enter edit'; btn.id = 'test-enter-edit'; f.appendChild(btn); })()"""
STAT_COUNT = """() => new Promise((res) => { const q = indexedDB.open('dci-stats', 1); q.onupgradeneeded = () => q.result.createObjectStore('subs', { keyPath: 'id' });
  q.onsuccess = () => { const tx = q.result.transaction('subs', 'readonly'); const g = tx.objectStore('subs').getAll(); g.onsuccess = () => res(g.result); g.onerror = () => res(null); };
  q.onerror = () => res(null); })"""


def js_release_of(added):
    """/ws/js/release of the test release with the relationships staged in the editor (as MusicBrainz has them after "Enter edit")."""
    recs = {g: [] for g in H.REC}
    rel = []
    for r in added:
        for a, b in ((r['e0'], r['e1']), (r['e1'], r['e0'])):
            if a in recs:
                recs[a].append({'linkTypeID': r['lt'], 'target': {'gid': b}})
                break
            if a == H.REL:
                rel.append({'linkTypeID': r['lt'], 'target': {'gid': b}})
                break
    return {'gid': H.REL, 'relationships': rel, 'releaseGroup': {'secondaryTypeIDs': []},
            'mediums': [{'position': 1, 'tracks': [{'number': str(i + 1), 'recording': {'gid': g, 'comment': '', 'relationships': recs[g]}} for i, g in enumerate(H.REC)]}]}


def case_stats():
    """Credits Importer 3.38.0 (E8, milestone "Statistics"; maintainer: "die statistiken sollen erstmal in den einstellung sein",
    "von Musicbrainz bestätigt", "Nein das Sammeln soll an sein (und natürlich ausschaltbar). Bei den Resetfunktionen soll es geben:
    "keep statistics"", "der erste Import zählt, sofern die seite nicht neu geladen wurde", "ja soll angehakt sein", "ich glaube
    einen export brauchen wir nicht", "Setze mal alle Ideen für die Statistik um und erstelle die Statistik.").
    A) ⚙ Settings → "Statistics" (after "Cache"): "Collect statistics" on, nothing counted yet.
    B) Everything staged, "Enter edit": the relationships in MusicBrainz's /ws/js/release – counted once (log "Statistics: n
       relationships confirmed by MusicBrainz and counted"; the job gone; one record in the database dci-stats with the time from
       the first import).
    C) The tab: 1 release, n relationships, 100 % new, the release had relationships before or was empty, the times; over months
       (this month), over days (today); the most frequent artists, instruments, types.
    D) "Reset all settings" with "keep statistics" (ticked): kept; unticked: deleted.
    E) Switched off: "Enter edit" makes no job.
    F) The release page MusicBrainz shows after "Enter edit": a job waiting there is counted – a relationship not in MusicBrainz is
       left out, and so is one MusicBrainz had before ("n0": no more of its kind than before); the time until the page began to load.
       F2) A job with nothing to look up there (a supplement): counted at once on the release page shown right after "Enter edit"."""
    import re
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(800)
        H.open_settings(pg, 'statistics')
        pg.wait_for_timeout(400)
        tabs = pg.evaluate("[...document.querySelectorAll('[data-el=settings] .dci-set-tab')].map(t => t.dataset.topic)")
        a = pg.evaluate("[!!document.querySelector('[data-el=stats-empty]'), (document.querySelector('[data-set=stats-on]') || {}).checked]")
        print('A) Reiter:', tabs, '| leer, an:', a)
        results.append(tabs[-3:] == ['cache', 'statistics', 'connections'] and a == [True, True])
        # B) staged, "Enter edit"
        pg.click('[data-act=apply]')
        pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(800)
        added = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0 && r.entity1).map(r => ({ lt: r.linkTypeID, e0: r.entity0.gid, e1: r.entity1.gid }))")
        H.WS_JS_RELEASE.clear()
        H.WS_JS_RELEASE.update(js_release_of(added))
        pg.evaluate(ENTER_EDIT)
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(2500)
        logs = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Statistics/.test(t))")
        job = pg.evaluate(f"localStorage.getItem('dci-stat-job:{H.REL}')")
        recs = pg.evaluate(STAT_COUNT)
        n = len(added)
        print('B) gestagt:', n, '| Protokoll:', logs, '| Auftrag:', job, '| Datensätze:', [(r['mbid'], len(r['rels']), r['ms'] is not None, r['src']) for r in recs or []])
        results.append(n > 0 and any(f'Statistics: {n} relationships confirmed by MusicBrainz and counted' in t for t in logs) and job is None
                       and recs is not None and len(recs) == 1 and len(recs[0]['rels']) == n and recs[0]['ms'] is not None and recs[0]['ms'] > 0 and recs[0]['src'] == 'discogs'
                       and recs[0]['rel'] is not None and 'before' in recs[0]['rel'])
        # C) the tab
        H.open_settings(pg, 'cache')
        H.open_settings(pg, 'statistics')
        pg.wait_for_timeout(500)
        TILES = "Object.fromEntries([...document.querySelectorAll('.dci-stats-tile')].map(t => [t.dataset.stat, t.querySelector('.dci-stats-num').textContent.trim()]))"
        tiles = pg.evaluate(TILES)
        month = pg.evaluate("(() => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); })()")
        day = pg.evaluate("(() => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); })()")
        rows_m = pg.evaluate("[...document.querySelectorAll('[data-el=stats-periods] tbody tr')].map(t => [...t.children].map(c => c.textContent.trim()))")
        pg.click('[data-act=stats-period][data-period=day]')
        pg.wait_for_timeout(300)
        rows_d = pg.evaluate("[...document.querySelectorAll('[data-el=stats-periods] tbody tr')].map(t => [...t.children].map(c => c.textContent.trim()))")
        tops = pg.evaluate("Object.fromEntries(['artists', 'instr', 'types'].map(k => [k, [...document.querySelectorAll(`[data-el=stats-top-${k}] li`)].map(li => li.textContent.replace(/\\s+/g, ' ').trim())]))")
        stored = pg.evaluate("localStorage.getItem('dci-stats-period')")
        print('C) Kacheln:', tiles, '\n   Monate:', rows_m, '| Tage:', rows_d, stored, '\n   Top:', tops)
        results.append(tiles.get('releases') == '1' and tiles.get('rels') == str(n) and tiles.get('newSupp') == '100 % / 0 %' and tiles.get('before') in ('100 % / 0 %', '0 % / 100 %')
                       and tiles.get('created') == '0' and bool(re.match(r'^[\d.,]+ (s|min)', tiles.get('perRelease', ''))) and bool(re.match(r'^[\d.,]+ (s|min)', tiles.get('perRel', '')))
                       and len(rows_m) == 1 and rows_m[0][0] == month and rows_m[0][1] == '1' and rows_m[0][2] == str(n) and rows_m[0][3] == '100 %'
                       and len(rows_d) == 1 and rows_d[0][0] == day and stored == '"day"'
                       and bool(tops['artists'] and tops['instr'] and tops['types']))
        # D) reset all settings: kept, then deleted
        H.open_reset(pg)
        pg.wait_for_timeout(150)
        keep = pg.is_checked('[data-f=reset-keepstats]')
        pg.click('[data-act=reset-do]')
        pg.wait_for_timeout(1200)
        d1 = len(pg.evaluate(STAT_COUNT) or [])
        H.open_reset(pg)
        pg.wait_for_timeout(150)
        pg.uncheck('[data-f=reset-keepstats]')
        pg.click('[data-act=reset-do]')
        pg.wait_for_timeout(1200)
        d2 = len(pg.evaluate(STAT_COUNT) or [])
        print('D) behalten angehakt:', keep, '| danach:', d1, '| ohne Haken:', d2)
        results.append(keep and d1 == 1 and d2 == 0)
        # E) off: no job
        H.open_settings(pg, 'statistics')
        pg.wait_for_timeout(300)
        pg.uncheck('[data-set=stats-on]')
        pg.wait_for_timeout(200)
        off = pg.evaluate("localStorage.getItem('dci-stats-on')")
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(800)
        job_e = pg.evaluate(f"localStorage.getItem('dci-stat-job:{H.REL}')")
        print('E) aus:', off, '| Auftrag:', job_e)
        results.append(off == 'false' and job_e is None)
        print('Fehler:', errs)
        results.append(not errs)
        pg.close()
        # F) the release page
        rec_gid = H.REC[1]
        found = next((x for x in js_release_of(added)['mediums'][0]['tracks'] if x['recording']['gid'] == rec_gid), None)
        tgt = found['recording']['relationships'][0] if found and found['recording']['relationships'] else {'linkTypeID': 148, 'target': {'gid': H.uid('dddddddd', 1)}}
        job = {'armedAt': 0, 'rec': {'v': 1, 'mbid': H.REL, 'start': 0, 'rel': {'before': 0}, 'src': 'discogs', 'supp': [], 'ocr': None, 'rels': [
            {'k': 'n', 'lt': 'instrument', 'lv': 'recording', 'et': 'artist', 'tg': tgt['target']['gid'], 'tn': 'X', 'i': ['guitar'], 'v': [], 'd': '', 'ds': '', 'rc': 0, 'ac': 0, 'ru': '', 'lk': 'link', 'nw': 0,
             'c': {'on': 'recording', 'src': rec_gid, 'lt': tgt['linkTypeID'], 'tgt': tgt['target']['gid']}},
            {'k': 'n', 'lt': 'instrument', 'lv': 'recording', 'et': 'artist', 'tg': 'nope', 'tn': 'Y', 'i': [], 'v': [], 'd': '', 'ds': '', 'rc': 0, 'ac': 0, 'ru': '', 'lk': 'link', 'nw': 0,
             'c': {'on': 'recording', 'src': rec_gid, 'lt': 1, 'tgt': 'nope'}},
            {'k': 'n', 'lt': 'instrument', 'lv': 'recording', 'et': 'artist', 'tg': tgt['target']['gid'], 'tn': 'Z', 'i': [], 'v': [], 'd': '', 'ds': '', 'rc': 0, 'ac': 0, 'ru': '', 'lk': 'link', 'nw': 0,
             'c': {'on': 'recording', 'src': rec_gid, 'lt': tgt['linkTypeID'], 'tgt': tgt['target']['gid'], 'n0': 1}}]}}
        rp, errs2 = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}')
        rp.evaluate("(job) => { job.armedAt = Date.now(); job.rec.start = Date.now() - 60000; localStorage.setItem('dci-stat-job:%s', JSON.stringify(job)); }" % H.REL, job)
        rp.reload()
        rp.wait_for_timeout(16000)
        recs_f = rp.evaluate(STAT_COUNT) or []
        job_f = rp.evaluate(f"localStorage.getItem('dci-stat-job:{H.REL}')")
        print('F) Release-Seite:', [(len(r['rels']), r['ms']) for r in recs_f], '| Auftrag:', job_f, '| Fehler:', errs2)
        results.append(len(recs_f) == 1 and len(recs_f[0]['rels']) == 1 and recs_f[0]['rels'][0]['tn'] == 'X' and 'c' not in recs_f[0]['rels'][0]
                       and 60000 <= recs_f[0]['ms'] < 75000 and job_f is None and not errs2)
        # F2) nothing to look up: at once
        job2 = {'armedAt': 0, 'rec': {'v': 1, 'mbid': H.REL, 'start': 0, 'rel': {'before': 1}, 'src': 'discogs', 'supp': [], 'ocr': None, 'rels': [
            {'k': 's', 'lt': 'instrument', 'lv': 'recording', 'et': 'artist', 'tg': 'g', 'tn': 'S', 'i': [], 'v': [], 'd': 'year', 'ds': 'hand', 'rc': 0, 'ac': 0, 'ru': '', 'lk': 'link', 'nw': 0}]}}
        rp.evaluate("(job) => { job.armedAt = Date.now(); job.rec.start = Date.now() - 1000; localStorage.setItem('dci-stat-job:%s', JSON.stringify(job)); }" % H.REL, job2)
        rp.reload()
        rp.wait_for_timeout(2500)
        recs_f2 = rp.evaluate(STAT_COUNT) or []
        print('F2) ohne Nachschlagbares:', [(len(r['rels']), r['rels'][0]['k']) for r in recs_f2])
        results.append(len(recs_f2) == 2 and any(r['rels'][0]['k'] == 's' for r in recs_f2))
        H.WS_JS_RELEASE.clear()
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
