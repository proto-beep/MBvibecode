"""Page bar and pools: the language is chosen in the page bar before the dashboard is opened; "Dates & tracks"
folds also at its bottom; folded, the date pool stays in the bar (on by default) and its dates can be dragged
onto rows from there; drag hints; the common month/year of recording periods (D014); "Horn [French]",
"Flugel Horn" without role credit; "Produced By" in "Companies, etc." is producer."""
import re
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import drag, date_field

for i, n in [(9110, 'French horn'), (9111, 'horn'), (9112, 'flugelhorn')]:
    H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'][str(i)] = H.ATTRS[i]
orig = H.discogs_release


def rel():
    d = orig()
    d['notes'] += '\nOverdubs recorded June 3 to September 30, 2002.\nStrings recorded December 2003 to January 2004.'
    ex = lambda name, role, i: {'name': name, 'anv': '', 'role': role, 'tracks': '', 'id': i, 'join': ''}
    d['extraartists'] += [ex('Keys Guy', 'Horn [French], Flugel Horn', 3003)]
    d['companies'].append({'name': 'Bob Producer', 'entity_type_name': 'Produced By', 'id': 1006, 'catno': ''})
    return d


H.discogs_release = rel
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    # 1) language in the page bar, before the dashboard is opened
    lab = lambda: re.sub(r'\s+', ' ', pg.locator('#dci-launcher').inner_text())
    print('1) Seitenleiste:', lab()[:120])
    pg.select_option('#dci-launcher [data-dci-lang]', 'de'); pg.wait_for_timeout(200)
    print('   nach „Deutsch“:', lab()[:120], '| gespeichert:', pg.evaluate("localStorage.getItem('dci-lang')"))
    ok1 = 'Sprache:' in lab() and 'Credits importieren' in lab() and pg.locator('#dci-overlay').count() == 0
    H.open_dashboard(pg)
    pg.wait_for_timeout(300)
    H.open_settings(pg, 'general')  # [3.26.0] the language is only in the settings
    ok1 = ok1 and pg.locator('#dci-title').inner_text() == 'Credits Importer' and pg.locator('[data-f=lang]').input_value() == 'de'
    pg.select_option('[data-f=lang]', 'en'); pg.wait_for_timeout(300)
    ok1 = ok1 and pg.locator('#dci-launcher [data-dci-lang]').input_value() == 'en' and 'Language:' in lab()
    print('   Dashboard Deutsch, zurück auf Englisch im Kopf → Seitenleiste:', pg.locator('#dci-launcher [data-dci-lang]').input_value(), ok1)
    # 2) D014: common month / year of recording periods
    chips = [re.sub(r'\s+', ' ', c) for c in pg.locator('.dci-pchip-date .dci-chip-main').all_inner_texts()]
    print('2) Pool:', chips)
    # names are made when the dates are found – here the dashboard was in German
    ok2 = any(c.startswith('Performance 1 (Monat) · 2001-03') for c in chips) and any(c.startswith('Performance 2 (Jahr) · 2002 ') for c in chips) \
        and any(c.startswith('Performance 3 · 2003-12 – 2004-01') for c in chips) and len(chips) == 6
    # 3) drag hints; folding at the bottom; folded, the date pool stays and its dates can be dragged onto rows
    hints = pg.locator('.dci-drag-hint').count()
    pg.click('.dci-pools-fold'); pg.wait_for_timeout(200)
    kept = pg.locator('.dci-pools-kept .dci-pchip-date').count()
    print('3) Hinweise:', hints, '| unten eingeklappt → offen:', pg.locator('.dci-pools-toggle').get_attribute('aria-expanded'), '| oben behalten:', kept)
    row = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text='Drum Guy')).first.locator('tr.dci-row').first
    rid = row.get_attribute('data-row')
    perf = pg.evaluate("[...document.querySelectorAll('.dci-pools-kept .dci-pchip-date')].find(c => c.textContent.includes('Performance 1 ·')).dataset.id")
    drag(pg, f'.dci-pools-kept .dci-pchip-date[data-id="{perf}"] .dci-chip-main', f'tr[data-row="{rid}"] .dci-c-date')
    year = date_field(row, 'rd-by')
    print('   eingeklappt auf Drum Guy gezogen:', year)
    ok3 = hints == 1 and pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') == 'false' and kept == len(chips) and year == '2001'
    pg.click('.dci-pools-toggle'); pg.wait_for_timeout(150)
    pg.uncheck('[data-f=pools-keep]'); pg.click('.dci-pools-fold'); pg.wait_for_timeout(150)
    ok3 = ok3 and pg.locator('.dci-pools-kept').count() == 0 and pg.evaluate("localStorage.getItem('dci-pools-keep')") == 'false'
    print('   „oben behalten“ aus → Pool eingeklappt weg:', pg.locator('.dci-pools-kept').count() == 0)
    # 4) instruments and producer
    def rowinfo(raw):
        tr = pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text=raw)).first
        typ = tr.locator('[data-f=type]').evaluate("s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : ''")
        prim = tr.locator('[data-f=primary]').input_value() if tr.locator('[data-f=primary]').count() else ''
        rc = tr.locator('[data-f=role-credit]').input_value() if tr.locator('[data-f=role-credit]').count() else ''
        return typ, prim, rc
    horn, flugel, prod = rowinfo('Horn [French]'), rowinfo('Flugel Horn'), rowinfo('Produced By')
    comp = pg.locator('[data-el=companies] .dci-group').filter(has=pg.locator('.dci-gname', has_text='Bob Producer')).first.locator('tr.dci-row').first
    ctype = comp.locator('[data-f=type]').evaluate("s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : ''")
    print('4) Horn [French]:', horn, '| Flugel Horn:', flugel, '| Produced By:', prod, '| Companies „Produced By“:', ctype)
    ok4 = horn == ('instrument', 'French horn', '') and flugel == ('instrument', 'flugelhorn', '') and prod[0] == 'producer' and ctype == 'producer'
    print('Ergebnis:', 'OK' if all([ok1, ok2, ok3, ok4]) else 'FEHLER', [ok1, ok2, ok3, ok4], '| Fehler:', errs)
    b.close()
