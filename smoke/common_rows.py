"""Helpers shared by the date tests: rows of an entry (tracks and date) as the dashboard shows them."""


def rows_of(pg, name):
    return pg.evaluate(f"""[...document.querySelectorAll('.dci-group')].filter(g => g.querySelector('.dci-gname').textContent.includes('{name}'))
      .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(tr => {{
        const v = (f) => {{ const e = tr.querySelector('[data-f=' + f + ']'); return e ? e.value : ''; }};
        // 3.9.0: a date from the pool or the matrix is a chip (its fields only after ✎)
        const chip = tr.querySelector('.dci-datechip');
        const date = chip ? chip.dataset.date : v('rd-by') ? [v('rd-by'), v('rd-bm'), v('rd-bd')].filter(Boolean).join('-') + (v('rd-ey') && (v('rd-ey') + v('rd-em') + v('rd-ed')) !== (v('rd-by') + v('rd-bm') + v('rd-bd')) ? ' – ' + [v('rd-ey'), v('rd-em'), v('rd-ed')].filter(Boolean).join('-') : '') : '';
        return (tr.querySelector('[data-tcount]') || {{textContent: ''}}).textContent.trim() + ' | ' + date;
      }})""")


def tracks_of_rows(pg, name):
    return pg.evaluate(f"""(() => {{ const out = []; document.querySelectorAll('.dci-group').forEach(g => {{
      if (!g.querySelector('.dci-gname').textContent.includes('{name}')) return;
      g.querySelectorAll('tr.dci-tracksrow').forEach(t => out.push([...t.querySelectorAll('input[data-f=track]:checked')].map(c => Number(c.dataset.i) + 1)));
    }}); return out; }})()""")


def lib(pg, name='Liberty Ellman'):
    """[(tracks, date), …] of an entry's rows."""
    return list(zip(tracks_of_rows(pg, name), [r.split(' | ')[1] for r in rows_of(pg, name)]))


def cells(pg):
    """The matrix: {column: [(date label, [track groups], dashed)]}."""
    return pg.evaluate("""(() => { const out = {}; document.querySelectorAll('.dci-dm-col').forEach(c => {
      out[c.dataset.dmcol] = [...c.querySelectorAll('.dci-dm-cell')].map(x => [x.classList.contains('dci-dm-choose')
        ? 'choose: ' + [...x.querySelectorAll('.dci-dm-opt')].map(o => o.textContent.trim().replace(/\\s+/g, ' ')).join(' | ')
        : x.querySelector('.dci-dm-date .dci-chip-main').textContent.trim(),
        [...x.querySelectorAll('.dci-tg-chip')].map(t => t.firstChild.textContent.trim()), x.classList.contains('dci-dm-auto')]);
    }); return out; })()""")


def stage(pg):
    pg.click('[data-act=apply]')
    pg.wait_for_timeout(2500)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    pg.wait_for_timeout(1500)


def drag(pg, src, dst, steps=10):
    """Drag with the mouse in small steps (Playwright's drag_and_drop does not start a drag while a field has focus)."""
    a = pg.locator(src).first
    b = pg.locator(dst).first
    # In the middle of the list: near its edges the dashboard scrolls while dragging (after 0.2 s, as browsers do)
    b.evaluate("e => e.scrollIntoView({ block: 'center', inline: 'center' })")
    sa = a.bounding_box()
    sb = b.bounding_box()
    x0, y0 = sa['x'] + min(20, sa['width'] / 2), sa['y'] + sa['height'] / 2
    x1, y1 = sb['x'] + sb['width'] / 2, sb['y'] + sb['height'] / 2
    pg.mouse.move(x0, y0)
    pg.mouse.down()
    for k in range(1, steps + 1):
        pg.mouse.move(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
        pg.wait_for_timeout(20)
    pg.mouse.up()
    pg.wait_for_timeout(300)


def date_field(row, f):
    """A date field of a row (rd-by …): its input, or – a date from the pool or the matrix (a chip) – read from the chip."""
    if row.locator(f'[data-f={f}]').count():
        return row.locator(f'[data-f={f}]').input_value()
    chip = row.locator('.dci-datechip')
    if not chip.count():
        return ''
    text = chip.get_attribute('data-date') or ''
    begin, _, end = text.partition(' – ')
    end = end or begin
    part = (begin if f[3] == 'b' else end).split('-')
    k = {'y': 0, 'm': 1, 'd': 2}[f[4]]
    return part[k] if k < len(part) else ''
