import sys
from playwright.sync_api import sync_playwright
import harness as H
OUT = sys.argv[1]
PROPOSAL = """
#dci-overlay .dci-group { --kind: #8a8799; --kind-bg: #f4f3f7; border-left: 5px solid var(--kind); background: #fff; border-radius: 0 6px 6px 0;
  box-shadow: 0 1px 4px rgba(38, 36, 48, .10); padding: 0 12px 8px 14px; margin: 0 0 28px; }
#dci-overlay .dci-group .dci-ghead { background: var(--kind-bg); margin: 0 -12px 8px -14px; padding: 8px 12px 8px 14px; border-radius: 0 6px 0 0; }
#dci-overlay .dci-kind-artist { --kind: #736dab; --kind-bg: #f0eff9; }
#dci-overlay .dci-kind-label { --kind: #2a8a8a; --kind-bg: #e8f4f4; }
#dci-overlay .dci-kind-place { --kind: #d9822b; --kind-bg: #fcf0e4; }
#dci-overlay .dci-kind-tag { display: inline-block; margin-right: 8px; padding: 0 7px; border-radius: 10px; background: var(--kind); color: #fff;
  font-size: 11px; font-weight: 600; letter-spacing: .02em; vertical-align: 1px; }
#dci-overlay .dci-group tbody tr.dci-row:nth-child(4n+3) td { background: #faf9fd; }
#dci-overlay .dci-group .dci-table td { border-bottom: 1px solid #eeedf3; }
"""
KIND = """() => {
  const label = { artist: 'Artist', label: 'Label', place: 'Place' };
  document.querySelectorAll('#dci-overlay .dci-group').forEach((g) => {
    const href = [...g.querySelectorAll('.dci-gmatch a')].map((a) => a.getAttribute('href') || '').join(' ');
    const kind = /\\/place\\//.test(href) ? 'place' : /\\/label\\//.test(href) || g.closest('[data-el=companies]') ? 'label' : 'artist';
    g.classList.add('dci-kind-' + kind);
    const name = g.querySelector('.dci-gname');
    if (name && !name.querySelector('.dci-kind-tag')) name.insertAdjacentHTML('afterbegin', `<span class="dci-kind-tag">${label[kind]}</span>`);
  });
}"""
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = b.new_context(viewport={'width': 1300, 'height': 2600}, device_scale_factor=1)
    H.install_routes(ctx)
    H.add_mapping(ctx)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(800)
    # the same section before and after: the last artists and the companies
    pg.add_style_tag(content='#dci-log { display: none !important; } #dci-overlay [data-el=dates] { position: static !important; }')
    def shoot(name):
        first = pg.locator('.dci-group').filter(has=pg.locator('.dci-gname', has_text='Drum Guy')).first
        comp = pg.locator('[data-el=companies]')
        pg.evaluate("(y) => { const b = document.querySelector('[data-el=body]'); b.scrollTop += y - b.getBoundingClientRect().top - 8; }", first.bounding_box()['y'])
        pg.wait_for_timeout(300)
        top = first.bounding_box()['y'] - 6
        groups = comp.locator('.dci-group')
        last = groups.nth(min(1, groups.count() - 1)).bounding_box()
        bottom = last['y'] + last['height'] + 6
        bb = pg.locator('[data-el=body]').bounding_box()
        pg.screenshot(path=f'{OUT}/{name}.png', clip={'x': bb['x'], 'y': top, 'width': bb['width'], 'height': min(bottom - top, bb['y'] + bb['height'] - top)})
    if len(sys.argv) > 2 and sys.argv[2] == 'real':
        shoot('farben-umgesetzt')
    else:
        shoot('farben-vorher')
        pg.add_style_tag(content=PROPOSAL)
        pg.evaluate(KIND)
        pg.wait_for_timeout(300)
        shoot('farben-nachher')
    print('ok', errs)
    b.close()
