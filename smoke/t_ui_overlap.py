"""Nothing of the dashboard lies on anything else (Credits Importer 3.51.0, collected item Z-OVL – texts of the statistics lay on each
other in 3.46.0; that must happen nowhere in the script): the texts of every view checked against each other –
two texts that cover each other where both can be seen (no opaque ground of one over the other) are an overlap; a text that runs out of
its card (wider than the card, the card not scrolling) too.

Cases: detector (the check itself), stats (the statistics with stored submissions, wide and narrow), dashboard (after the import, as a
window and in the page; the works matrix, the dates), views (compact view, larger text, narrow, dark, the rules window, the log),
settings (each tab), pagebar (the bar on "Edit relationships"); `python3 t_ui_overlap.py <case> …` runs only those."""
import harness as H
from caserun import run_cases, sync_playwright

# The texts of `root` that overlap where both are seen: [[text a, text b, where]] (at most 12)
OVERLAPS = r"""(sel) => {
  const root = document.querySelector(sel);
  if (!root) return [['(no ' + sel + ')', '', '']];
  const shown = (el) => { if (el.closest('details:not([open]) > :not(summary)')) return false; for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
    const st = getComputedStyle(e); if (st.display === 'none' || st.visibility === 'hidden' || +st.opacity === 0 || e.hidden) return false; } return true; };
  // a rect cut to what its scrolling or clipping ancestors show
  const clip = (el, r) => { let { left, top, right, bottom } = r;
    for (let e = el.parentElement; e && e !== document.documentElement; e = e.parentElement) {
      const st = getComputedStyle(e);
      if (/(auto|scroll|hidden|clip)/.test(st.overflowX + st.overflowY)) { const b = e.getBoundingClientRect();
        left = Math.max(left, b.left); top = Math.max(top, b.top); right = Math.min(right, b.right); bottom = Math.min(bottom, b.bottom); } }
    return right - left > 1 && bottom - top > 1 ? { left, top, right, bottom } : null; };
  const items = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || !shown(el) || el.closest('option, select, script, style, [role=tooltip], .dci-tip')) continue;
    // (text for screen readers only: clipped to nothing)
    if ((() => { for (let e = el; e && e !== root; e = e.parentElement) { const st = getComputedStyle(e); if ((st.clipPath && st.clipPath !== 'none') || (e.offsetWidth <= 1 && e.offsetHeight <= 1 && st.overflow === 'hidden')) return true; } return false; })()) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    for (const r of range.getClientRects()) { const c = clip(el, r); if (c) items.push({ el, text: n.nodeValue.trim().slice(0, 40), r: c }); }
  }
  // ((3.51.0, review) the values and placeholders of fields too)
  for (const el of root.querySelectorAll('input[type=text], input[type=number], input:not([type]), textarea, select')) {
    if (!shown(el) || !el.offsetParent) continue;
    const c = clip(el, el.getBoundingClientRect());
    if (c) items.push({ el, text: (el.value || el.placeholder || el.name || el.tagName).slice(0, 40), r: c });
  }
  const opaque = (e) => { const bg = getComputedStyle(e).backgroundColor; const m = bg.match(/rgba?\(([^)]+)\)/); if (!m) return false;
    const p = m[1].split(',').map(Number); return p.length < 4 || p[3] > 0.6; };
  // ((3.51.0, review) in the order the page is drawn: the text below is hidden only by an opaque box drawn over it – a box placed
  // (position, z-index, transform …) between the two or the upper one's own; a box in the flow paints its ground before all text, a
  // ground of the lower text's own (an ancestor) hides nothing)
  const placed = (e) => { const st = getComputedStyle(e); return st.position !== 'static' || st.transform !== 'none' || +st.opacity < 1 || st.zIndex !== 'auto'; };
  const covers = (e, low) => !e.contains(low) && opaque(e) && placed(e);
  const hidden = (a, b, x, y) => {
    const list = document.elementsFromPoint(x, y);
    const ia = list.findIndex((e) => e === a || a.contains(e));
    const ib = list.findIndex((e) => e === b || b.contains(e));
    if (ia < 0 || ib < 0) {
      // (a text running out of its box is not hit there: hidden only by a placed opaque box over the point)
      const lowEl = ia < 0 ? a : b;
      return list.slice(0, Math.max(0, ia < 0 ? ib : ia) + 1).some((e) => covers(e, lowEl) && !(ia < 0 ? b : a).contains(e));
    }
    const [top, low] = ia < ib ? [ia, ib] : [ib, ia];
    const lowEl = low === ia ? a : b;
    for (let k = top; k < low; k++) if (covers(list[k], lowEl)) return true;
    return false; };
  const out = [];
  for (let i = 0; i < items.length && out.length < 12; i++) for (let j = i + 1; j < items.length && out.length < 12; j++) {
    const a = items[i]; const b = items[j];
    if (a.el === b.el) continue;
    const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
    const h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (w < 3 || h < 3) continue;
    const x = Math.max(a.r.left, b.r.left) + w / 2; const y = Math.max(a.r.top, b.r.top) + h / 2;
    if (hidden(a.el, b.el, x, y)) continue;
    out.push([a.text, b.text, `${Math.round(x)},${Math.round(y)}`]);
  }
  return out;
}"""
# Cards and boxes whose content is wider than they are and does not scroll (a card of the statistics: not even scrolling): [[class, scrollWidth, clientWidth]]
OVERFLOWS = r"""(sel) => [...document.querySelectorAll(sel + ' .dci-stats-card, ' + sel + ' .dci-set-panel, ' + sel + ' .dci-card, ' + sel + ' .dci-mx-card')].filter((c) => c.offsetParent || getComputedStyle(c).position === 'fixed')
  .filter((c) => { const st = getComputedStyle(c); return c.scrollWidth > c.clientWidth + 2 && (c.classList.contains('dci-stats-card') || !/(auto|scroll|hidden)/.test(st.overflowX)); })
  .map((c) => [c.className + ' ' + (c.dataset.el || ''), c.scrollWidth, c.clientWidth]).slice(0, 12)"""


def check(pg, sel, label, scroller='#dci-overlay .dci-body'):
    """The view checked as far as it scrolls ((3.51.0, review): before only what the window showed)."""
    o = []
    PICK = "const p = document.querySelector(s); const e = p && p.scrollHeight > p.clientHeight + 2 ? p : document.scrollingElement;"
    steps = pg.evaluate("(s) => { " + PICK + " return Math.max(1, Math.ceil(e.scrollHeight / Math.max(200, e.clientHeight * 0.8))); }", scroller)
    for k in range(min(steps, 30)):
        pg.evaluate("([s, k]) => { " + PICK + " e.scrollTop = k * Math.max(200, e.clientHeight * 0.8); }", [scroller, k])
        pg.wait_for_timeout(60)
        for x in pg.evaluate(OVERLAPS, sel):
            if x[:2] not in [y[:2] for y in o]:
                o.append(x)
    pg.evaluate("(s) => { " + PICK + " e.scrollTop = 0; }", scroller)
    f = pg.evaluate(OVERFLOWS, sel)
    print(f'   {label}: Überlappungen {len(o)} {o[:6]} | übergelaufen {f[:6]}')
    return not o and not f


STAT_SEED = """(recs) => new Promise((res) => { const q = indexedDB.open('dci-stats', 1); q.onupgradeneeded = () => q.result.createObjectStore('subs', { keyPath: 'id' });
  q.onsuccess = () => { const tx = q.result.transaction('subs', 'readwrite'); const st = tx.objectStore('subs'); st.clear(); recs.forEach((r) => st.put(r));
    tx.oncomplete = () => res(true); tx.onerror = () => res(false); }; q.onerror = () => res(false); })"""


def stat_rel(k, lt, lv, et, tg, tn, i=(), d='', ds='', lk='', ru='', nw=0):
    return {'k': k, 'lt': lt, 'lv': lv, 'et': et, 'tg': tg, 'tn': tn, 'i': list(i), 'v': [], 'd': d, 'ds': ds, 'rc': 0, 'ac': 0, 'ru': ru, 'lk': lk, 'nw': nw}


def seed_stats(pg):
    now = pg.evaluate("Date.now()")
    day = 86400000
    relA = {'title': 'A long title of a release', 'year': 1985, 'country': 'JP', 'formats': ['CD'], 'labels': ['ECM Records'], 'before': 0}
    relB = {'title': 'B', 'year': 1993, 'country': 'CA', 'formats': ['CD', 'Vinyl'], 'labels': ['Intakt'], 'before': 3}
    recs = []
    for k, (src, rel, supp) in enumerate([('bandcamp', relA, ['discogs']), ('discogs', relB, []), ('youtube', relA, []), ('bandcamp', relB, []),
                                          ('text', relA, []), ('ocr', relB, [])]):
        recs.append({'v': 2, 'id': f'x:{k}', 'mbid': f'm{k % 3}', 'at': now - k * day, 'start': now - k * day - 400000 - k * 90000, 'ms': 400000 + k * 90000,
                     'idle': 0, 'src': src, 'supp': supp, 'rel': rel, 'own': 1, 'ocr': {'supp': False, 'images': 2, 'lines': 10, 'corrected': 3} if src == 'ocr' else None,
                     'rels': [stat_rel('n', 'instrument', 'recording', 'artist', 'g1', 'Jane Roe-Longname', ['double bass'], 'day', 'notes', 'link', 'R001'),
                              stat_rel('n', 'recorded at', 'recording', 'place', 'p1', 'Sound Development Studio', lk='link'),
                              stat_rel('n', 'producer', 'release', 'artist', 'g2', 'Joe', lk='hand'),
                              stat_rel('s', 'performance', 'recording', 'work', 'w1', 'Song')]})
    return pg.evaluate(STAT_SEED, recs)


def open_page(p):
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    return b, pg, errs


def case_stats():
    """Z-OVL: the statistics (all cards, from six stored submissions) – 1500 px and 1000 px wide: no two texts on each other (the head
    "with supplement" of "Sources" lay over "per relationship" and the card beside it, 3.46.0 – 3.50.0), no card wider than it is."""
    results = []
    with sync_playwright() as p:
        b, pg, errs = open_page(p)
        seed_stats(pg)
        H.open_dashboard(pg)
        pg.wait_for_timeout(600)
        H.open_stats(pg)
        pg.wait_for_timeout(1200)
        for w in (1500, 1000):
            pg.set_viewport_size({'width': w, 'height': 1200})
            pg.wait_for_timeout(600)
            results.append(check(pg, '[data-el=stats]', f'Statistik {w} px'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_dashboard():
    """Z-OVL: the dashboard after the import of the harness's release – head, entries, dates, works matrix, foot – as a window (1500 and
    1100 px) and in the page."""
    results = []
    with sync_playwright() as p:
        b, pg, errs = open_page(p)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2500)
        for w in (1500, 1100):
            pg.set_viewport_size({'width': w, 'height': 1100})
            pg.wait_for_timeout(600)
            results.append(check(pg, '#dci-overlay', f'Fenster {w} px'))
        H.toggle_place(pg)
        pg.wait_for_timeout(1200)
        results.append(check(pg, '#dci-overlay', 'in der Seite'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_settings():
    """Z-OVL: each tab of ⚙ Settings (1500 and 1000 px)."""
    results = []
    with sync_playwright() as p:
        b, pg, errs = open_page(p)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        H.open_settings(pg)
        # ([Z-BETAOFF] 3.115.0) not a tab greyed out (Beta)
        tabs = pg.evaluate("[...document.querySelectorAll('[data-el=settings] .dci-set-tab:not([aria-disabled=true])')].map(t => t.dataset.topic)")
        for w in (1500, 1000):
            pg.set_viewport_size({'width': w, 'height': 1100})
            for t in tabs:
                pg.click(f'[data-el=settings] .dci-set-tab[data-topic={t}]')
                pg.wait_for_timeout(250)
                results.append(check(pg, '[data-el=settings]', f'{t} {w} px'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_detector():
    """The check itself: two texts laid on each other in the dashboard are found; one under an opaque ground is not; a card of the
    statistics made too narrow for its table is found."""
    results = []
    with sync_playwright() as p:
        b, pg, errs = open_page(p)
        H.open_dashboard(pg)
        pg.wait_for_timeout(800)
        pg.evaluate("""() => { const o = document.body; const d = document.createElement('div'); d.id = 'ovl-test';
          d.innerHTML = '<span style="position:absolute;left:40px;top:40px;font-size:20px">Overlapping one</span><span style="position:absolute;left:60px;top:44px;font-size:20px">Overlapping two</span>'
            + '<span style="position:absolute;left:40px;top:140px;font-size:20px">Hidden below</span><span style="position:absolute;left:30px;top:130px;width:300px;height:50px;background:#fff;font-size:20px">Cover on top</span>';
          d.style.cssText = 'position:fixed;left:0;top:0;width:400px;height:300px;z-index:2147483647'; o.append(d); }""")
        o = pg.evaluate(OVERLAPS, '#ovl-test')
        print('   gefunden:', o)
        results.append(len(o) == 1 and 'Overlapping' in o[0][0] and 'Overlapping' in o[0][1])
        # ((3.51.0, review) a cell's text running into the next cell with a ground of its own: found; a card too narrow for its table: found)
        pg.evaluate("""() => { const d = document.createElement('div'); d.id = 'ovl-test2'; d.style.cssText = 'position:fixed;left:0;top:320px;z-index:2147483647;background:#fff';
          d.innerHTML = '<table style="table-layout:fixed;width:200px;border-collapse:collapse"><tr><td style="width:100px;white-space:nowrap;font-size:16px">A very long head of a column</td>'
            + '<td style="width:100px;background:#f7f6fb;font-size:16px">Next one</td></tr></table>'
            + '<div class="dci-stats-card" style="width:120px"><table><tr><td style="white-space:nowrap">a wide table that does not fit</td></tr></table></div>';
          document.body.append(d); }""")
        o2 = pg.evaluate(OVERLAPS, '#ovl-test2')
        f2 = pg.evaluate(OVERFLOWS, '#ovl-test2')
        print('   Zelle in Zelle:', o2, '| zu schmal:', f2)
        results.append(len(o2) >= 1 and len(f2) == 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_pagebar():
    """Credits Importer 3.51.0 (collected item Z-IML; Q-gc3): on "Edit relationships" the bar of the script is one line – "Import
    credits …" with its switches and the navigation of the source pages ("Discogs view: …") beside it (before: below it); in a
    narrow window the navigation goes below. The question of the language stays a line of its own above them; (3.51.0, review) the
    warning of a second copy of the script too."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx)  # (with the companion: its navigation is shown)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelectorAll('#dci-overlay [data-act=close]').forEach(b => b.click())")
        pg.evaluate("(() => { const d = document.createElement('div'); d.id = 'dci-twice'; d.textContent = 'Twice'; document.getElementById('dci-pagebar').prepend(d); })()")
        pg.wait_for_timeout(600)
        TOPS = "['#dci-launcher', '#dci-controls', '#dci-langask', '#dci-twice'].map(s => { const e = document.querySelector(s); if (!e || e.hidden) return null; const r = e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom)]; })"
        for w in (1500, 480):
            pg.set_viewport_size({'width': w, 'height': 900})
            pg.wait_for_timeout(400)
            t = pg.evaluate(TOPS)
            print(f'   {w} px: launcher, controls, language:', t)
            if None in t[:2]:
                results.append(False)
                continue
            same = abs(t[0][0] - t[1][0]) < 12 or (t[1][0] < t[0][1] and t[0][0] < t[1][1])
            results.append(same if w == 1500 else t[1][0] >= t[0][1])
            for k in (2, 3):
                if t[k]:
                    results.append(t[k][1] <= min(t[0][0], t[1][0]))
        results.append(check(pg, '#dci-pagebar', 'Leiste'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_views():
    """Z-OVL ((3.51.0, review) the views left out before): the dashboard after the import in the compact view, with larger text (150 %),
    narrow (900 px), in the dark theme; the window "Mapping rules" and the log."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("try { localStorage.setItem('dci-view', JSON.stringify('compact')); localStorage.setItem('dci-scale', '1.5'); localStorage.setItem('dci-theme-window', JSON.stringify('dark')); } catch (e) {}")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        pg.wait_for_timeout(2500)
        state = pg.evaluate("[document.documentElement.className, getComputedStyle(document.querySelector('#dci-overlay')).fontSize]")
        print('   Zustand:', state)
        for w in (1400, 900):
            pg.set_viewport_size({'width': w, 'height': 1000})
            pg.wait_for_timeout(600)
            results.append(check(pg, '#dci-overlay', f'kompakt, 150 %, dunkel, {w} px'))
        pg.click('.dci-head [data-act=rules]')
        pg.wait_for_timeout(800)
        results.append(check(pg, '#dci-rules', 'Mapping rules', scroller='#dci-rules .dci-rules-body'))
        pg.evaluate("document.querySelectorAll('#dci-rules [data-act=rules-close], #dci-rules .dci-close').forEach(b => b.click())")
        pg.evaluate("(() => { const l = document.getElementById('dci-log'); if (l) l.hidden = false; })()")
        pg.wait_for_timeout(300)
        results.append(check(pg, '#dci-log', 'Log', scroller='#dci-log'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
