"""Credits Importer 3.30.3: the date pool and the track pool fold on their own, scroll bars of the works matrix
(collected items 93, 94; 2026-10-25).
A) "Dates & tracks" folded with "keep the pools in the bar": "▾ Date pool" folds the date pool in – "▸ Date pool (3)",
   no chips, stored; the track pool stays; after reloading still folded; "▸ Date pool" shows it again (nothing stored).
B) Open block: the same button folds the track pool there ("▸ Track pool (1)"), and shows it again.
C) Works matrix, 1000 px wide: a scroll bar above the matrix (it is wider than the window); moving it moves the matrix,
   moving the matrix moves it. The lower edge of the matrix out of view: a second bar at the bottom of the visible
   area; the lower edge in view: no second bar."""
from playwright.sync_api import sync_playwright
import harness as H

KEPT = """(() => { const b = document.querySelector('[data-el=dates]'); const lab = (sel) => { const x = b.querySelector(sel + ' [data-act=pool-fold]'); return x ? x.textContent.replace(/\\s+/g, ' ').trim() : null; };
  return { dates: lab('.dci-pool-dates'), tracks: lab('.dci-tracks-bar'), dchips: b.querySelectorAll('.dci-pchip-date').length, tchips: b.querySelectorAll('.dci-pchip-tg').length,
    stored: localStorage.getItem('dci-pool-fold') }; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.set_viewport_size({'width': 1000, 'height': 700})
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(600)
    # a track group, so that both pools have chips
    pg.evaluate(f"localStorage.setItem('dci-track-pool:{H.REL}', JSON.stringify([{{ id: 'tg1', name: 'Side A', tracks: [0, 1] }}]))")
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('.dci-pools-toggle') && document.querySelector('.dci-mx-wrap')", 60)
    pg.wait_for_timeout(800)
    st = lambda: pg.evaluate(KEPT)
    # A) the folded block with the kept pools
    if pg.evaluate("document.querySelector('.dci-pools-toggle').getAttribute('aria-expanded')") == 'true':
        pg.click('.dci-pools-toggle')
        pg.wait_for_timeout(300)
    a0 = st()
    pg.click('[data-el=dates] .dci-pool-dates [data-act=pool-fold]')
    pg.wait_for_timeout(300)
    a1 = st()
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "document.querySelector('.dci-pools-toggle')", 60)
    pg.wait_for_timeout(800)
    a2 = st()
    pg.click('[data-el=dates] .dci-pool-dates [data-act=pool-fold]')
    pg.wait_for_timeout(300)
    a3 = st()
    print('A) Leiste:', a0, '\n   Date pool zu:', a1, '\n   neu geladen:', a2, '\n   wieder auf:', a3)
    results.append(a0['dates'] == '▾ Date pool' and a0['dchips'] >= 1 and a0['tchips'] == 1 and a1['dates'] == '▸ Date pool (%d)' % a0['dchips'] and a1['dchips'] == 0
                   and a1['tchips'] == 1 and a1['stored'] == '{"dates":true}' and a2['dates'] == a1['dates'] and a3['dates'] == '▾ Date pool' and a3['dchips'] == a0['dchips']
                   and a3['stored'] is None)
    # B) the open block
    pg.click('.dci-pools-toggle')
    pg.wait_for_timeout(300)
    pg.click('[data-el=dates] .dci-pools-body .dci-tracks-bar [data-act=pool-fold]')
    pg.wait_for_timeout(300)
    b1 = st()
    pg.click('[data-el=dates] .dci-pools-body .dci-tracks-bar [data-act=pool-fold]')
    pg.wait_for_timeout(300)
    b2 = st()
    print('B) offen – Track pool zu:', b1, '| wieder auf:', b2)
    results.append(b1['tracks'] == '▸ Track pool (1)' and b1['tchips'] == 0 and b2['tracks'] == '▾ Track pool' and b2['tchips'] == 1)
    pg.click('.dci-pools-toggle')
    pg.wait_for_timeout(300)
    # C) the scroll bars of the works matrix
    MX = """(() => { const w = document.querySelector('.dci-mx-wrap'); const t = document.querySelector('[data-mxhs=top]'); const bt = document.querySelector('[data-mxhs=bottom]');
      const body = document.querySelector('#dci-overlay .dci-body').getBoundingClientRect();
      return { over: w.scrollWidth > w.clientWidth, top: !t.hidden, bottom: !bt.hidden, wl: Math.round(w.scrollLeft), tl: Math.round(t.scrollLeft), bl: Math.round(bt.scrollLeft),
        bottomIn: !bt.hidden && bt.getBoundingClientRect().bottom <= body.bottom + 1 && bt.getBoundingClientRect().top >= body.top }; })()"""
    pg.evaluate("document.querySelector('.dci-mx-wrap').scrollIntoView({ block: 'start' })")
    pg.wait_for_timeout(300)
    c0 = pg.evaluate(MX)
    pg.evaluate("(() => { const t = document.querySelector('[data-mxhs=top]'); t.scrollLeft = 200; t.dispatchEvent(new Event('scroll')); })()")
    pg.wait_for_timeout(300)
    c1 = pg.evaluate(MX)
    pg.evaluate("(() => { const w = document.querySelector('.dci-mx-wrap'); w.scrollLeft = 60; w.dispatchEvent(new Event('scroll')); })()")
    pg.wait_for_timeout(300)
    c2 = pg.evaluate(MX)
    # the matrix starts near the bottom of the visible area: its lower edge out of view
    pg.evaluate("""(() => { const body = document.querySelector('#dci-overlay .dci-body'); const w = document.querySelector('.dci-mx-wrap');
      body.scrollTop += w.getBoundingClientRect().top - body.getBoundingClientRect().bottom + 160; })()""")
    pg.wait_for_timeout(500)
    c3 = pg.evaluate(MX)
    pg.evaluate("document.querySelector('.dci-mx-end').scrollIntoView({ block: 'center' })")
    pg.wait_for_timeout(500)
    c4 = pg.evaluate(MX)
    print('C) Matrix:', c0, '\n   oben 200:', c1, '\n   Matrix 60:', c2, '\n   unterer Rand außer Sicht:', c3, '\n   in Sicht:', c4)
    results.append(c0['over'] and c0['top'] and c1['wl'] == 200 and c2['tl'] == 60 and c3['bottom'] and c3['bottomIn'] and c3['bl'] == 60 and not c4['bottom'])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
