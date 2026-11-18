# An accessibility audit of the dashboard on the test page (Credits Importer 3.160.0, review run 3): names of controls, contrast
# (light and dark), places clicked that the keyboard cannot reach. Usage: python3 tools/a11y_audit.py smoke [dark]
import json
import sys
sys.path.insert(0, sys.argv[1])
from playwright.sync_api import sync_playwright  # noqa: E402
import harness as H  # noqa: E402

DARK = len(sys.argv) > 2 and sys.argv[2] == 'dark'
AUDIT = r"""() => {
  const root = document.querySelector('#dci-overlay') || document.body;
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const nameOf = (e) => {
    const lb = e.getAttribute('aria-labelledby');
    const byId = lb ? lb.split(/\s+/).map((i) => (document.getElementById(i) || {}).textContent || '').join(' ') : '';
    const lab = e.id ? document.querySelector(`label[for="${CSS.escape(e.id)}"]`) : null;
    const wrap = e.closest('label');
    return [e.getAttribute('aria-label'), byId, e.getAttribute('title'), lab && lab.textContent, wrap && wrap.textContent, e.textContent, e.getAttribute('placeholder'), e.getAttribute('alt'), e.value && e.type === 'button' ? e.value : '']
      .map((x) => String(x || '').replace(/\s+/g, ' ').trim()).find(Boolean) || '';
  };
  const sig = (e) => `${e.tagName.toLowerCase()}${e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : ''}${e.dataset.act ? `[act=${e.dataset.act}]` : ''}${e.dataset.f ? `[f=${e.dataset.f}]` : ''}${e.dataset.set ? `[set=${e.dataset.set}]` : ''}`;
  const noName = {};
  const symbolOnly = {};
  for (const e of root.querySelectorAll('button, a[href], input:not([type=hidden]), select, textarea, [role=button], [role=checkbox], [role=tab]')) {
    if (!vis(e)) continue;
    const n = nameOf(e);
    if (!n) noName[sig(e)] = (noName[sig(e)] || 0) + 1;
    // a name of signs only, no title and no aria-label: a screen reader says the sign
    else if (!e.getAttribute('aria-label') && !e.getAttribute('title') && !/[\p{L}\p{N}]/u.test(n)) symbolOnly[`${sig(e)} “${n.slice(0, 6)}”`] = (symbolOnly[`${sig(e)} “${n.slice(0, 6)}”`] || 0) + 1;
  }
  // clicked, but not reachable by keyboard
  const noKey = {};
  for (const e of root.querySelectorAll('[data-act], [data-pick], [data-toggle]')) {
    if (!vis(e) || /^(BUTTON|A|INPUT|SELECT|TEXTAREA|SUMMARY|LABEL)$/.test(e.tagName)) continue;
    if (e.tabIndex >= 0 || e.closest('button, a[href], label, summary')) continue;
    noKey[sig(e)] = (noKey[sig(e)] || 0) + 1;
  }
  // contrast
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const over = (top, under) => ({ r: top.r * top.a + under.r * (1 - top.a), g: top.g * top.a + under.g * (1 - top.a), b: top.b * top.a + under.b * (1 - top.a), a: 1 });
  const bgOf = (e) => {
    const stack = [];
    for (let x = e; x; x = x.parentElement) { const s = getComputedStyle(x); const c = parse(s.backgroundColor); if (s.backgroundImage && s.backgroundImage !== 'none') return null; if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; } }
    let base = { r: 255, g: 255, b: 255, a: 1 };
    for (const c of stack.reverse()) base = over(c, base);
    return base;
  };
  const low = {};
  let texts = 0;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const t = walker.currentNode;
    const e = t.parentElement;
    if (!e || seen.has(e) || !t.textContent.trim() || !vis(e)) continue;
    seen.add(e);
    const s = getComputedStyle(e);
    if (Number(s.opacity) === 0) continue;
    const fg0 = parse(s.color); const bg = bgOf(e);
    if (!fg0 || !bg) continue;
    texts++;
    let op = 1; for (let x = e; x && x !== root.parentElement; x = x.parentElement) op *= Number(getComputedStyle(x).opacity);
    const fg = over({ ...fg0, a: fg0.a * op }, bg);
    const l1 = lum(fg); const l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const size = parseFloat(s.fontSize); const bold = Number(s.fontWeight) >= 700;
    const need = size >= 24 || (size >= 18.66 && bold) ? 3 : 4.5;
    const disabled = e.closest('[disabled], [aria-disabled=true], .dci-off, .dci-disabled');
    if (ratio < need && !disabled) {
      const k = `${sig(e)} ${s.color} on rgb(${Math.round(bg.r)}, ${Math.round(bg.g)}, ${Math.round(bg.b)})`;
      if (!low[k]) low[k] = { n: 0, ratio: Math.round(ratio * 100) / 100, sample: t.textContent.trim().slice(0, 30), size };
      low[k].n++;
    }
  }
  return { noName, symbolOnly, noKey, low, texts };
}"""


def show(tag, res):
    print(f'=== {tag}: texts {res["texts"]}')
    for k in ('noName', 'symbolOnly', 'noKey'):
        items = sorted(res[k].items(), key=lambda x: -x[1])
        print(f'  {k}: {len(items)} kinds, {sum(v for _, v in items)} elements')
        for s, n in items[:25]:
            print(f'     {n:4d}  {s}')
    low = sorted(res['low'].items(), key=lambda x: x[1]['ratio'])
    print(f'  low contrast: {len(low)} kinds, {sum(v["n"] for _, v in low)} elements')
    for s, v in low[:40]:
        print(f'     {v["ratio"]:5.2f}  x{v["n"]:<4d} {s}  “{v["sample"]}” {v["size"]}px')


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = b.new_context(viewport={'width': 1400, 'height': 3000}, device_scale_factor=1, color_scheme='dark' if DARK else 'light')
    H.install_routes(ctx)
    H.add_mapping(ctx)
    if DARK:
        ctx.add_init_script("if (location.host === 'musicbrainz.org') { localStorage.setItem('dci-theme-window', JSON.stringify('dark')); localStorage.setItem('dci-theme-page', JSON.stringify('dark')); }")
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    show('dashboard', pg.evaluate(AUDIT))
    # the works matrix on its own
    wm = pg.evaluate(AUDIT.replace("document.querySelector('#dci-overlay')", "document.querySelector('#dci-overlay [data-el=works]')"))
    show('works matrix', wm)
    pg.evaluate("document.querySelector('#dci-overlay .dci-head [data-act=settings]') && document.querySelector('#dci-overlay .dci-head [data-act=settings]').click()")
    pg.wait_for_timeout(800)
    sel = pg.evaluate("(() => { const e = document.querySelector('#dci-settings, .dci-settings, [data-el=settings]'); return e ? (e.id ? '#' + e.id : '.' + e.className.split(' ')[0]) : ''; })()")
    print('settings root:', sel)
    if sel:
        show('settings', pg.evaluate(AUDIT.replace("document.querySelector('#dci-overlay')", f"document.querySelector('{sel}')")))
    print('errors:', errs[:3])
    b.close()
