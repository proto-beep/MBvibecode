from playwright.sync_api import sync_playwright
import harness as H

def ticks(pg):
    return pg.evaluate("""() => {
      const out = {};
      document.querySelectorAll('.dci-matrix th[data-colhead]').forEach((th) => {
        const name = th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong').textContent.trim();
        const key = th.dataset.colhead;
        out[name] = [...document.querySelectorAll(`.dci-mx-cell[data-col="${key}"]`)]
          .filter((c) => c.classList.contains('dci-mx-on'))
          .map((c) => Number(c.closest('tr').dataset.work) + 1);
      });
      return out;
    }""")

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    print('Log Verlage:', [l[9:100] for l in pg.locator('#dci-log li').all_inner_texts() if 'ublisher' in l])
    print('Spalten:', pg.locator('.dci-matrix th[data-colhead] .dci-mx-colname').all_inner_texts())
    t = ticks(pg)
    print('Angehakte Tracks je Spalte:', t)
    print('Verlagsstatus:', pg.evaluate("[...document.querySelectorAll('.dci-matrix th[data-colhead]')].map(th => th.querySelector('.dci-mx-colname').textContent.trim().split('\\n')[0] + ': ' + ([...th.querySelectorAll('.dci-sub')].map(x => x.textContent.trim()).filter(Boolean).join(' | ')))"))
    b.close()

with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    col = lambda name: pg.evaluate(f"[...document.querySelectorAll('.dci-matrix th[data-colhead]')].find(th => th.textContent.includes('{name}')).dataset.colhead")
    cell = lambda name, track: pg.locator(f'.dci-matrix tr[data-work="{track - 1}"] .dci-mx-cell[data-col="{col(name)}"]')
    print('Tooltip Pub Co, Track 1:', cell('Pub Co', 1).get_attribute('title'))
    print('Tooltip Other Pub, Track 1:', cell('Other Pub', 1).get_attribute('title'))
    cell('Other Pub', 1).locator('[data-act=mx-cell]').click(); pg.wait_for_timeout(300)
    cell('Ghost Pub', 4).locator('[data-act=mx-cell]').click(); pg.wait_for_timeout(300)
    # "check evidence" is in the ▾ menu of a publisher column
    pg.locator(f'[data-colhead="{col("Pub Co")}"] [data-act=mx-colmenu]').first.click(); pg.wait_for_timeout(300)
    pg.locator('[data-act=mx-pub-check]').first.click(); pg.wait_for_timeout(2500)
    t = ticks(pg)
    print('Nach Handauswahl + „Belege prüfen“:', {k.replace('MB', '').split(' not')[0]: v for k, v in t.items()})
    ok = t.get('MBOther Pub') == [1] and t.get('MBPub Co') == [1, 2]
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
    pub = pg.evaluate("window.__dispatched.filter(a => a.newRelationshipState && a.newRelationshipState.linkTypeID === 208).map(a => a.newRelationshipState.entity0.name + ' → ' + a.newRelationshipState.entity1.name)")
    print('Im Editor vorgemerkte Verlagsbeziehungen:', pub)
    print('Ergebnis:', 'OK' if ok and pub == ['Pub Co → Song One', 'Other Pub → Song One'] or ok and sorted(pub) == sorted(['Pub Co → Song One', 'Other Pub → Song One']) else 'PRÜFEN', '| Fehler:', errs)
    b.close()
