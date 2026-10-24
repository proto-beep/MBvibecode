"""Credits Importer 3.18.0: "Add entry manually" as one line, always in view above the date pool (collected item 25).
A) The line (title, entry, role, "Add", "?") stands in the sticky block, above "Dates & tracks"; the explanation is the
   tooltip of its title and of the entry field (no paragraph any more); the search links come with "?".
B) Scrolled down to the works matrix (window): the line is still at the top of the dashboard, the pool below it.
C) An entry added from there: its row is shown where it was added (scrolled into view below the sticky block, lit up).
D) In the page (setting "In the page"): the block with the line sticks to the top of the browser window."""
from playwright.sync_api import sync_playwright
import harness as H

EXTRA = H.uid('dddddddd', 31)
H.ARTISTS[3031] = (EXTRA, 'Extra Person')
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
LINE = """(() => { const st = document.querySelector('[data-el=stick]'); const m = st && st.querySelector('[data-el=manual]');
  if (!m) return null; const kids = [...st.children].map(c => c.dataset.el);
  const t = m.querySelector('.dci-manual-title'); const s = m.querySelector('[data-el=manual-search]');
  return { kids, hidden: m.hidden, title: t.textContent.trim(), tip: t.title, fieldTip: m.querySelector('[data-f=manual-artist]').title,
    fields: [...m.querySelectorAll('input, button')].map(x => x.dataset.f || x.dataset.act), paragraph: !!m.querySelector('p, h3'),
    search: s.hidden, links: s.querySelectorAll('a[target=_blank]').length }; })()"""
POS = """(() => { const body = document.querySelector('[data-el=body]'); const m = document.querySelector('[data-el=manual]');
  const d = document.querySelector('[data-el=dates]'); const b = body.getBoundingClientRect();
  return { scrolled: Math.round(body.scrollTop), manual: Math.round(m.getBoundingClientRect().top - b.top), dates: Math.round(d.getBoundingClientRect().top - m.getBoundingClientRect().bottom),
    pad: body.style.scrollPaddingTop }; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    # A)
    a1 = pg.evaluate(LINE)
    pg.locator('[data-el=manual] [data-act=manual-search]').evaluate('b => b.click()')
    a2 = pg.evaluate(LINE)
    exp = pg.locator('[data-el=manual] [data-act=manual-search]').get_attribute('aria-expanded')
    pg.locator('[data-el=manual] [data-act=manual-search]').evaluate('b => b.click()')
    print('A) Zeile:', a1)
    print('   „?“:', a2['search'], a2['links'], exp)
    results.append(a1 is not None and a1['kids'] == ['manual', 'dates'] and not a1['hidden'] and a1['title'] == 'Add entry manually'
                   and a1['tip'].startswith('Add any MusicBrainz entry') and a1['fieldTip'] == a1['tip'] and not a1['paragraph']
                   and a1['fields'] == ['manual-artist', 'manual-role', 'add-manual', 'manual-search'] and a1['search'] and a1['links'] == 11
                   and a2['search'] is False and exp == 'true')
    # B) scrolled down
    pg.evaluate("document.querySelector('[data-el=works]').scrollIntoView({ block: 'start' })")
    pg.wait_for_timeout(300)
    b1 = pg.evaluate(POS)
    print('B) gescrollt:', b1)
    results.append(b1['scrolled'] > 300 and -2 <= b1['manual'] <= 2 and 0 <= b1['dates'] <= 2 and b1['pad'].endswith('px'))
    # C) add from there
    pg.fill('[data-f=manual-artist]', f'https://musicbrainz.org/artist/{EXTRA}')
    pg.fill('[data-f=manual-role]', 'Mixed By')
    pg.locator('[data-act=add-manual]').evaluate('b => b.click()')
    H.wait_for(pg, f"{LOGS}.some(x => /Extra Person/.test(x))", 20)
    pg.wait_for_timeout(300)
    c1 = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Extra Person');
      const tr = g && g.querySelector('tr.dci-row'); if (!tr) return null; const st = document.querySelector('[data-el=stick]').getBoundingClientRect();
      const r = tr.getBoundingClientRect(); const body = document.querySelector('[data-el=body]').getBoundingClientRect();
      return [tr.classList.contains('dci-flash'), Math.round(r.top - st.bottom) >= 0, r.bottom <= body.bottom + 1,
        document.querySelector('[data-f=manual-artist]').value, document.querySelector('[data-f=manual-role]').value]; })()""")
    print('C) hinzugefügt:', c1, [x for x in pg.evaluate(LOGS) if 'Extra Person' in x])
    results.append(c1 is not None and c1[:3] == [True, True, True] and c1[3:] == ['', ''])
    # D) in the page
    H.toggle_place(pg)
    pg.wait_for_timeout(500)
    pg.evaluate("window.scrollTo(0, document.querySelector('[data-el=works]').getBoundingClientRect().top + window.scrollY - 300)")
    pg.wait_for_timeout(300)
    d1 = pg.evaluate("""(() => { const st = document.querySelector('[data-el=stick]'); const m = st.querySelector('[data-el=manual]');
      return [Math.round(window.scrollY), Math.round(st.getBoundingClientRect().top), Math.round(m.getBoundingClientRect().top), document.documentElement.style.scrollPaddingTop]; })()""")
    print('D) in der Seite:', d1)
    results.append(d1[0] > 300 and d1[1] == 0 and d1[2] >= 0 and d1[2] <= 2 and d1[3].endswith('px'))
    H.toggle_place(pg)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
