"""Credits Importer 3.26.0: the head of the dashboard in one line (collected item 30).
A) One line: title · the source (link) · "Source ▾" · "+ Supplement" · the status of the view · text size · ⚙, Mapping
   rules, Log, ⓘ, ⤢, ✕ with own symbols (aria-label and tooltip); no language, no window/page switch, no switches of
   the navigation in the head; the words next to the symbols only in a wide dashboard.
B) "Source ▾": a menu with another source, "Paste text …", order of the sources, Bandcamp, "Delete stored import …";
   Escape and a click elsewhere close it (the dashboard stays open); "Paste text …" closes it and opens the text below
   the head.
C) "+ Supplement" opens and closes the bar "Supplement with".
D) After the installation the page bar asks for the language once (the browser's preselected: English; fr-FR:
   Français); the hint follows the choice; OK stores it and the question is gone, also after reloading. An update
   (the version of the update notice known) does not ask.
E) The language in ⚙ Settings → General: Español – the dashboard in Spanish, the settings still open at General.
I) [3.27.2] With the companion and no Discogs tab: "open in background" in the status stands out (purple, white, bold).
[3.27.2] The symbol of the compact view first in the tools of the head (item 60)."""
from playwright.sync_api import sync_playwright
import harness as H

HEAD = """(() => { const h = document.querySelector('.dci-head'); const kids = [...h.children].filter(k => k.offsetParent !== null);
  const tops = kids.map(k => Math.round(k.getBoundingClientRect().top + k.getBoundingClientRect().height / 2));
  const btns = [...h.querySelectorAll('.dci-head-tools .dci-ibtn')].map(b => [b.dataset.act, !!b.querySelector('svg.dci-ico'), b.getAttribute('aria-label'), b.title]);
  const label = h.querySelector('.dci-hlabel');
  return { spread: Math.max(...tops) - Math.min(...tops), btns, zoom: h.querySelector('[data-el=zoom]').textContent.trim(),
    lang: h.querySelectorAll('[data-f=lang]').length, place: h.querySelectorAll('[data-act=place-toggle]').length,
    switches: h.querySelectorAll('[data-sync-mode], [data-dg-status], [data-click-toggle]').length, status: !!h.querySelector('.dci-syncstatus'),
    label: getComputedStyle(label).display }; })()"""
MENU = """(() => { const m = document.querySelector('.dci-srcmenu'); return { open: !m.hidden, aria: document.querySelector('[data-act=srcmenu]').getAttribute('aria-expanded'),
  items: [...m.querySelectorAll('[data-act], [data-f]')].map(e => e.dataset.act || e.dataset.f) }; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    # D) the question of the language (first installation)
    d0 = pg.evaluate("""(() => { const q = document.getElementById('dci-langask'); return q ? [q.querySelector('input:checked').value,
      q.querySelector('.dci-langask-hint').textContent, localStorage.getItem('dci-lang-ask')] : null; })()""")
    pg.check('#dci-langask input[value=de]')
    d1 = [pg.locator('#dci-langask .dci-langask-hint').inner_text(), pg.locator('#dci-langask .dci-langask-ok').inner_text()]
    pg.click('#dci-langask .dci-langask-ok')
    pg.wait_for_timeout(300)
    d2 = [pg.evaluate("localStorage.getItem('dci-lang')"), pg.evaluate("localStorage.getItem('dci-lang-ask')"), pg.locator('#dci-langask').count(),
          pg.locator('#dci-open').inner_text()]
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    d3 = [pg.locator('#dci-langask').count(), pg.locator('#dci-open').inner_text()]
    print('D) Frage:', d0, '| Deutsch gewählt:', d1, '| OK:', d2, '| neu geladen:', d3)
    results.append(d0 and d0[0] == 'en' and d0[1].startswith('Choose the language of the Credits Importer') and d0[2] == 'true'
                   and d1[0].startswith('Wähle die Sprache des Credits Importers') and d2 == ['"de"', None, 0, 'Credits importieren …'] and d3 == [0, 'Credits importieren …'])
    pg.evaluate("localStorage.setItem('dci-lang', JSON.stringify('en'))")
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(500)
    # A) one line
    a1 = pg.evaluate(HEAD)
    pg.evaluate("(() => { const p = document.querySelector('#dci-overlay .dci-panel'); p.style.width = '1700px'; p.style.left = '0px'; })()")
    pg.set_viewport_size({'width': 1800, 'height': 1000})
    pg.wait_for_timeout(300)
    a2 = pg.evaluate(HEAD)
    print('A) Kopf:', {k: v for k, v in a1.items() if k != 'btns'}, '\n   Knöpfe:', a1['btns'], '\n   breit:', a2['spread'], a2['label'])
    # [3.27.2] the symbol of the compact view first, left of the text size (item 60)
    results.append(a1['spread'] <= 6 and [x[0] for x in a1['btns']] == ['view-toggle', 'settings-open', 'rules', 'log', 'connections-open', 'window-reset', 'close']
                   and all(x[1] and x[2] and x[3] for x in a1['btns']) and a1['btns'][1][2] == 'Settings' and a1['btns'][0][2] == 'Compact' and a1['zoom'] == '100 %'
                   and a1['lang'] == 0 and a1['place'] == 0 and a1['switches'] == 0 and a1['status'] and a1['label'] == 'none'
                   and a2['spread'] <= 6 and a2['label'] != 'none')
    pg.set_viewport_size({'width': 1500, 'height': 1000})
    pg.click('.dci-head [data-act=window-reset]')
    pg.wait_for_timeout(300)
    # B) the menu
    b0 = pg.evaluate(MENU)
    pg.click('.dci-head [data-act=srcmenu]')
    pg.wait_for_timeout(150)
    b1 = pg.evaluate(MENU)
    b1f = pg.evaluate("document.activeElement.dataset.f")
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(150)
    b2 = [pg.evaluate(MENU)['open'], pg.evaluate("document.activeElement.dataset.act"), pg.evaluate("!document.getElementById('dci-overlay').hidden")]
    H.src_menu(pg)
    pg.click('.dci-head h2')
    pg.wait_for_timeout(150)
    b3 = pg.evaluate(MENU)['open']
    H.src_menu(pg, 'text-open')
    b4 = [pg.evaluate(MENU)['open'], pg.evaluate("!!document.querySelector('[data-el=srcpanels] [data-f=text-src]')"), pg.evaluate("!document.querySelector('.dci-head [data-f=text-src]')")]
    pg.click('[data-act=text-cancel]')
    print('B) zu:', b0, '| offen:', b1, b1f, '| Escape:', b2, '| Klick daneben offen:', b3, '| Text:', b4)
    results.append(not b0['open'] and b0['aria'] == 'false' and b1['open'] and b1['aria'] == 'true' and b1f == 'discogs-input'
                   and b1['items'] == ['discogs-input', 'discogs-load', 'text-open', 'srcorder-toggle', 'bc-toggle', 'forget-open']
                   and b2 == [False, 'srcmenu', True] and b3 is False and b4 == [False, True, True])
    # C) + Supplement
    c0 = pg.evaluate("!!document.querySelector('.dci-suppbar')")
    pg.click('.dci-head [data-act=supp-open]')
    pg.wait_for_timeout(150)
    c1 = [pg.evaluate("!!document.querySelector('[data-el=srcpanels] .dci-suppbar')"), pg.locator('.dci-head [data-act=supp-open]').get_attribute('aria-expanded')]
    pg.click('.dci-head [data-act=supp-open]')
    pg.wait_for_timeout(150)
    c2 = pg.evaluate("!!document.querySelector('.dci-suppbar')")
    print('C) Leiste vorher:', c0, '| auf:', c1, '| wieder zu:', not c2)
    results.append(not c0 and c1 == [True, 'true'] and not c2)
    # E) the language in the settings
    H.open_settings(pg, 'general')
    pg.select_option('[data-el=settings] [data-f=lang]', 'es')
    pg.wait_for_timeout(500)
    e1 = [pg.locator('.dci-head [data-act=settings-open]').get_attribute('aria-label'), pg.evaluate("!document.querySelector('[data-el=settings]').hidden"),
          pg.evaluate("[...document.querySelectorAll('.dci-set-tab')].filter(t => t.getAttribute('aria-selected') === 'true').map(t => t.dataset.topic)"),
          pg.locator('.dci-head [data-act=srcmenu]').inner_text().strip()]
    print('E) Spanisch:', e1)
    results.append(e1 == ['Ajustes', True, ['general'], 'Fuente'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
    b = p.chromium.launch(args=H.LAUNCH_ARGS)

    # I) [3.27.2] with the companion and no Discogs tab: "open in background" stands out (item 65)
    ctx4 = H.new_context(b)
    pg4, errs4 = H.open_mb_edit(ctx4, companion=True)
    pg4.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg4)
    H.wait_for(pg4, "!!document.querySelector('.dci-head .dci-syncstatus [data-act=sync-open]')", 30)
    i1 = pg4.evaluate("""(() => { const b = document.querySelector('.dci-head .dci-syncstatus [data-act=sync-open]'); const st = getComputedStyle(b);
      return [b.textContent.trim(), st.backgroundColor, st.color, st.fontWeight]; })()""")
    print('I) Status-Knopf:', i1)
    results.append(i1[0] == 'open in background' and i1[1] == 'rgb(115, 109, 171)' and i1[2] == 'rgb(255, 255, 255)' and i1[3] in ('600', '700'))
    pg4.close()

    # D2) another browser language; D3) an update does not ask
    ctx2 = b.new_context(viewport={'width': 1500, 'height': 1000}, locale='fr-FR')
    H.install_routes(ctx2)
    pg2, errs2 = H.open_mb_edit(ctx2, companion=False)
    pg2.wait_for_selector('#dci-open', timeout=20000)
    f1 = pg2.evaluate("(() => { const q = document.getElementById('dci-langask'); return q ? [q.querySelector('input:checked').value, q.querySelector('.dci-langask-hint').textContent.slice(0, 30)] : null; })()")
    ctx3 = H.new_context(b)
    ctx3.add_init_script("localStorage.setItem('dci-notice-version', JSON.stringify('3.25.0')); localStorage.setItem('dci-store-epoch', '4');")
    pg3, errs3 = H.open_mb_edit(ctx3, companion=False)
    pg3.wait_for_selector('#dci-open', timeout=20000)
    f2 = [pg3.locator('#dci-langask').count(), pg3.evaluate("localStorage.getItem('dci-lang-ask')")]
    print('D2) fr-FR:', f1, '| D3) Update:', f2)
    results.append(f1 == ['fr', 'Choisissez la langue du Credit'] and f2 == [0, None])
    results.append(not errs2 and not errs3)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
