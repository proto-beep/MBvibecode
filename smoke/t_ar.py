from playwright.sync_api import sync_playwright
import harness as H
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    row = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text='Ann Rep')).first.locator('tr.dci-row').first
    print('Ebene:', row.locator('[data-act=level][aria-pressed=true]').get_attribute('data-level'), '| Task-Feld:', row.locator('[data-f=role-credit]').input_value())
    pg.click('[data-act=apply]'); pg.wait_for_timeout(2500)
    ar = pg.evaluate("window.__dispatched.filter(a => a.newRelationshipState && a.newRelationshipState.linkTypeID === 1010).map(a => [a.newRelationshipState.entity0.name, a.newRelationshipState.entity1.entityType, (a.newRelationshipState.attributes ? a.newRelationshipState.attributes.__tree : []).map(x => x.typeName + '=' + (x.text_value || ''))])")
    print('Vorgemerkt:', ar, '| Fehler:', errs)
    assert ar == [['Ann Rep', 'release_group', ['task=consultant']]]
    b.close()
