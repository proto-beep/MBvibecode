"""Import 3.15.2/3.15.3: the suggestions of an entry without a match are a block right below its red mark.
A pasted text names "John Smith"; MusicBrainz has eight artists of that name.
A) The head line: the red mark, the field and the buttons; below it the suggestions as a block of their own, side by side
   and wrapping into more lines (3.15.3; 3.15.2 had one per line); no explanation as visible text – it is the tooltip of
   the block and of each suggestion.
B) Five suggestions are shown, then a clearly visible "+ 3 more" (a button of its own); a click shows all eight and
   "− fewer"; in a narrow dashboard the block takes more lines.
C) A click on a suggestion assigns it, as before."""
from playwright.sync_api import sync_playwright
import harness as H

IDS = [H.uid('dddddddd', 70 + k) for k in range(8)]
H.MB_SEARCH['artist'] = [{'id': g, 'name': 'John Smith', 'disambiguation': f'singer no. {k + 1}', 'score': 100} for k, g in enumerate(IDS)]
HEAD = """(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'John Smith');
  const m = g.querySelector('.dci-gmatch'); const st = m.querySelector('.dci-sugg-stack');
  const bad = m.querySelector('.dci-badge-bad'); const rb = bad.getBoundingClientRect(); const rs = st ? st.getBoundingClientRect() : null;
  const chips = st ? [...st.querySelectorAll('.dci-suggbtn')].map(c => Math.round(c.getBoundingClientRect().top)) : [];
  return { order: [...m.children].map(c => c.matches('.dci-sugg-stack') ? 'stack' : c.matches('.dci-badge-bad') ? 'mark' : c.tagName.toLowerCase() + (c.dataset.f ? ':' + c.dataset.f : c.dataset.act ? ':' + c.dataset.act : '')),
    below: rs ? rs.top >= rb.bottom - 1 && Math.abs(rs.left - rb.left) < 3 : false, lines: new Set(chips).size,
    shown: st ? [...st.querySelectorAll('[data-act=name-use]')].length : 0, more: (m.querySelector('[data-act=sugg-more]') || {}).textContent || '',
    flow: st ? getComputedStyle(st).flexDirection + ' ' + getComputedStyle(st).flexWrap : '', tip: st ? st.title : '', text: m.innerText }; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.click('[data-act=text-open]')
    pg.fill('[data-f=text-src]', 'Mixed by John Smith')
    pg.click('[data-act=text-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
    H.wait_for(pg, "[...document.querySelectorAll('section.dci-group')].some(s => s.querySelector('[data-act=name-use]'))", 30)
    pg.wait_for_timeout(500)
    h = pg.evaluate(HEAD)
    print('A) Reihenfolge:', h['order'], '| darunter:', h['below'], '| Fluss:', h['flow'], '| Zeilen:', h['lines'])
    print('   Tooltip:', h['tip'][:90], '| sichtbarer Erklärtext:', 'Same name in MusicBrainz' in h['text'])
    results.append(h['order'][:2] == ['mark', 'input:artist-input'] and h['order'][-1] == 'stack' and h['below'] and h['flow'] == 'row wrap'
                   and h['lines'] == 1 and 'Same name in MusicBrainz' in h['tip'] and 'Same name in MusicBrainz' not in h['text'])
    # B) five, then "+ 3 more"
    style = pg.evaluate("(() => { const b = document.querySelector('[data-act=sugg-more]'); const cs = getComputedStyle(b); return [cs.fontWeight, cs.borderTopStyle, cs.borderTopWidth]; })()")
    pg.locator('[data-act=sugg-more]').first.click(); pg.wait_for_timeout(300)
    h2 = pg.evaluate(HEAD)
    # many: the block spreads into more lines (a narrow dashboard)
    w0 = pg.evaluate("(() => { const p = document.querySelector('.dci-panel'); const w = p.style.width; p.style.width = '560px'; return w; })()"); pg.wait_for_timeout(500)
    h3 = pg.evaluate(HEAD)
    pg.evaluate(f"document.querySelector('.dci-panel').style.width = {w0!r}"); pg.wait_for_timeout(300)
    print('B) sichtbar:', h['shown'], h['more'], style, '| nach Klick:', h2['shown'], h2['more'], '| Zeilen breit:', h2['lines'], '| schmal:', h3['lines'])
    results.append(h['shown'] == 5 and h['more'] == '+ 3 more' and int(style[0]) >= 600 and style[1] == 'solid'
                   and h2['shown'] == 8 and h2['more'] == '− fewer' and h3['lines'] > h2['lines'])
    # C) assign the fourth
    pg.locator(f'[data-act=name-use][data-mbid="{IDS[3]}"]').first.evaluate('b => b.click()'); pg.wait_for_timeout(500)
    st = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'John Smith');
      return [g.className.match(/dci-st-(\\w+)/)[1], (g.querySelector('.dci-gmatch .dci-mblink') || {}).textContent || '', !!g.querySelector('.dci-sugg-stack')]; })()""")
    print('C) nach Klick:', st)
    results.append(st[0] == 'manual' and 'John Smith' in st[1] and not st[2])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
