from playwright.sync_api import sync_playwright
import harness as H

def names(pg):
    return pg.locator('.dci-group .dci-gname strong').all_inner_texts()

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    grp = lambda n: pg.locator('.dci-group').filter(has=pg.locator('.dci-gname strong', has_text=n)).first
    # 1) remove a row from Discogs and bring it back
    grp('Bob Producer').locator('[data-act=remove-row]').click(); pg.wait_for_timeout(300)
    gone = 'Bob Producer' not in names(pg)
    msg = [m for m in pg.locator('.dci-msg').all_inner_texts() if 'removed' in m.lower()]
    pg.locator('.dci-msg [data-act=row-restore]').last.click(); pg.wait_for_timeout(300)
    back = 'Bob Producer' in names(pg)
    print('1) Entfernt:', gone, msg[-1:] if msg else '', '| zurückgeholt:', back)
    # 2) remove a staged row: it is taken out of the editor at the next "Stage"
    pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    n_before = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Keys Guy').length")
    grp('Keys Guy').locator('[data-act=remove-row]').click(); pg.wait_for_timeout(300)
    pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
    removed = pg.evaluate("window.__removed.map(r => r.entity0.name)")
    n_after = pg.evaluate("MB.relationshipEditor.state.added.filter(r => r.entity0.name === 'Keys Guy').length")
    print('2) Keys Guy im Editor vorher/nachher:', n_before, n_after, '| herausgenommen:', removed)
    # 3) "Skip" all, then "only works": work relationships come back, all else stays skipped
    pg.click('[data-act=bulk-level][data-level=skip]'); pg.wait_for_timeout(300)
    pg.click('[data-act=bulk-level][data-level=only-works]'); pg.wait_for_timeout(500)
    levels = pg.evaluate("""[...document.querySelectorAll('.dci-group')].map(g => g.querySelector('.dci-gname strong').textContent + ':' +
      ([...g.querySelectorAll('tr.dci-row [data-act=level][aria-pressed=true]')].map(x => x.dataset.level).join(',') || (g.querySelector('.dci-work-note') ? 'work' : '-')))""")
    print('3) Ebenen nach „nur Werke“:', levels)
    cols = pg.locator('.dci-matrix th[data-colhead] .dci-mx-colname').all_inner_texts()
    print('   Matrix-Spalten:', [c.split('\n')[0] for c in cols])
    plan = pg.evaluate("[...document.querySelectorAll('[data-el=sum]')].map(e => e.textContent).join(' ')")
    print('   Plan:', plan[:120])
    pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
    kinds = pg.evaluate("[...new Set(MB.relationshipEditor.state.added.map(r => r.linkTypeID))].sort((a, b) => a - b)")
    print('   Nach erneutem Übernehmen im Editor (Typ-IDs):', kinds, '(165 lyricist, 167 writer, 168 composer, 208 publishing, 278 performance, 297 arranger)')
    ok_kinds = all(k in (165, 167, 168, 208, 278, 297) for k in kinds) and 167 in kinds
    ok = ok_kinds and gone and back and n_before > 0 and n_after == 0 and all(l.endswith(':skip') or l.endswith(':work') for l in levels)
    print('Ergebnis:', 'OK' if ok else 'FEHLER', '| Fehler:', errs)
    b.close()

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click('[data-act=bulk-level][data-level=only-works]'); pg.wait_for_timeout(500)
    print('4) Ohne vorheriges Übernehmen, Plan:', pg.inner_text('[data-el=sum]').replace('\n', ' ')[:120])
    pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
    kinds = pg.evaluate("[...new Set(MB.relationshipEditor.state.added.map(r => r.linkTypeID))].sort((a, b) => a - b)")
    print('   Im Editor (Typ-IDs):', kinds, '| Ergebnis:', 'OK' if kinds and all(k in (165, 167, 168, 208, 278, 297) for k in kinds) else 'FEHLER', '| Fehler:', errs)
    b.close()
