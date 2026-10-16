"""Update notice and the one-time reset of stored data: a first installation shows no notice; an update from a
version before 2.11.0 clears all settings and data once (the list of created works stays) and shows the latest
milestones with a note about the reset; closing it is remembered; an update from 2.9.0 shows the milestones
since then; the notice follows the language; an update from 2.12.0 (storage generation 2) resets once more
(generation 4, Credits Importer 3.5.0: a fresh start, the list of created works too). The companion clears its shared
storage and the cover settings once."""
import re
from playwright.sync_api import sync_playwright
import harness as H

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
    ok2 = ok2 and 'what’s new' in n and 'Credits Importer 3.12.0' in n and 'Credits Importer 3.10.0' in n and 'Credits Importer 3.5.0' in n and 'Credits Importer 3.3.0' not in n and 'reset once' in n
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
