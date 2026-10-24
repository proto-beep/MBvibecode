"""“↺ Reset all settings …” (⚙ Settings; until 3.24 “↺ Defaults” in the head): all settings back to their defaults (language, text size, switches, matrix and pool options,
the cover box on Discogs through the companion); own rules and stored pools only when ticked; the list of
created works never."""
import re
from playwright.sync_api import sync_playwright
import harness as H

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
