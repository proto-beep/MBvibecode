"""Works matrix and track groups. From the Discogs notes (S022): "Published by Pub Co (1, 3)" → track group and
suggestions in the column of Pub Co (ahead of the personal publisher evidence, which gives 1, 2); "Ghostpub (4)"
matches "Ghost Pub" (spaces); "Written by Writer W (1, 2)" is in the Discogs track credits already (no change);
"Strings arranged by Nobody Here (4)" is no entry (only the track group). ✓ keeps a suggestion, × takes it out.
Dropped (S023): onto a column head – all its roles only for the group's tracks; Shift adds; onto a role – only
that role; onto an attribute in the head of the track column – the links of the group's tracks (MB's own stay)."""
import re
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import drag

for i, n in [(567, 'cover'), (578, 'live'), (750, 'medley')]:
    H.attr(i, n, i)
H.lt(278, H.LTS[278]['gid'], 'performance', 'recording', 'work', (567, 578, 750))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
orig_rel = H.discogs_release


def rel():
    d = orig_rel()
    d['notes'] += ('\nPublished by Pub Co (1, 3); Ghostpub (4).\nWritten by Writer W (1, 2).'
                   '\nStrings arranged by Nobody Here (2, 4).')
    # Writer Z also writes the lyrics (a second role in the column)
    d['extraartists'].append({'name': 'Writer Z', 'anv': '', 'role': 'Lyrics By', 'tracks': '', 'id': 3009, 'join': ''})
    return d


H.discogs_release = rel
COLS = """(() => { const out = {};
  document.querySelectorAll('.dci-matrix th[data-colhead]').forEach((th) => {
    const name = (th.querySelector('.dci-mx-colname .dci-mblink, .dci-mx-colname strong') || {}).textContent.replace(/^MB/, '').trim();
    out[name] = [...document.querySelectorAll(`.dci-mx-cell[data-col="${th.dataset.colhead}"]`)].filter(c => c.classList.contains('dci-mx-on'))
      .map(c => (Number(c.closest('tr').dataset.work) + 1) + (c.classList.contains('dci-mx-sugg') ? 's' : '') + (c.querySelectorAll('.dci-mxchip-on, .dci-mxchip-sugg, .dci-mxchip-wait').length > 1 ? '+' : ''));
  }); return out; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(1500)
    cols = lambda: pg.evaluate(COLS)
    colkey = lambda name: pg.evaluate(f"[...document.querySelectorAll('.dci-matrix th[data-colhead]')].find(th => th.textContent.includes({name!r})).dataset.colhead")
    cell = lambda name, track: f'.dci-matrix tr[data-work="{track - 1}"] .dci-mx-cell[data-col="{colkey(name)}"]'
    pool = lambda: pg.evaluate("[...new Set([...document.querySelectorAll('.dci-pchip-tg')].map(c => c.textContent.replace(/\\s+/g, ' ').trim()))]")

    # A) from the notes
    c0 = cols()
    logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'Notes:' in x]
    print('A1) Track-Pool:', pool())
    print('    Spalten (s = Vorschlag):', c0)
    print('    Protokoll:', logs)
    ok_a = c0.get('Pub Co') == ['1s', '3s'] and c0.get('Ghost Pub') == ['4s'] and c0.get('Writer W') == ['1', '2'] \
        and any('Pub Co · 1, 3' in x for x in pool()) and any('Ghostpub · 4' in x for x in pool()) and any('Nobody Here · 2, 4' in x for x in pool()) \
        and any('Nobody Here' in x and 'only a track group' in x for x in logs) and any('Writer W' in x and 'only a track group' in x for x in logs)
    pg.click(f'{cell("Pub Co", 1)} [data-act=mx-sugg-ok]'); pg.wait_for_timeout(200)
    pg.click(f'{cell("Pub Co", 3)} [data-act=mx-sugg-no]'); pg.wait_for_timeout(200)
    c1 = cols()
    print('A2) ✓ Track 1, × Track 3:', c1.get('Pub Co'))
    ok_a = ok_a and c1.get('Pub Co') == ['1']
    results.append(ok_a)

    # B) a track group onto a column head, with Shift, onto one role
    pg.click('[data-act=tg-new]'); pg.fill('[data-f=tg-name]', 'Side A')
    pg.check('[data-f=tg-track][data-i="0"]'); pg.check('[data-f=tg-track][data-i="1"]'); pg.click('[data-act=tg-save]'); pg.wait_for_timeout(200)
    gid = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Side A')).dataset.id")
    wz = colkey('Writer Z')
    print('B0) Writer Z vorher:', cols().get('Writer Z'))
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'[data-colhead="{wz}"] .dci-mx-card .dci-mx-credit')
    b1 = cols().get('Writer Z')
    # Shift: the group of track 4 added (synthetic events carry the Shift key)
    g4 = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Ghostpub')).dataset.id")
    hints = pg.evaluate(f"""(() => {{
      const src = document.querySelector('.dci-pools-body .dci-pchip-tg[data-id="{g4}"] .dci-chip-main').closest('[data-drag]');
      const dst = document.querySelector('[data-colhead="{wz}"] .dci-mx-card');
      const after = (el) => getComputedStyle(el, '::after').content;
      const dt = new DataTransfer();
      src.dispatchEvent(new DragEvent('dragstart', {{ bubbles: true, dataTransfer: dt }}));
      const out = [getComputedStyle(dst).outlineStyle];
      dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt }}));
      out.push(after(dst));
      dst.dispatchEvent(new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
      out.push(after(dst));
      dst.dispatchEvent(new DragEvent('drop', {{ bubbles: true, cancelable: true, dataTransfer: dt, shiftKey: true }}));
      src.dispatchEvent(new DragEvent('dragend', {{ bubbles: true, dataTransfer: dt }}));
      return out; }})()""")
    pg.wait_for_timeout(300)
    b2 = cols().get('Writer Z')
    print('B1) „Side A“ auf Writer Z:', b1, '| mit Umschalt Track 4 dazu:', b2, '| Hinweise:', hints)
    ok_b = b1 == ['1+', '2+'] and b2 == ['1+', '2+', '4+'] and hints[0] == 'dashed' and 'only the works of these tracks' in hints[1] and 'adds the works' in hints[2]
    # onto one role: lyricist only on the works of track 1 (group "Pub Co · 1, 3" → track 1 has a work, 3 waits)
    g13 = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Pub Co')).dataset.id")
    lyr = pg.evaluate(f"[...document.querySelectorAll('[data-colhead=\"{wz}\"] [data-tgrole]')].find(r => r.textContent.trim() === 'lyricist').dataset.tgrole")
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{g13}"] .dci-chip-main', f'[data-colhead="{wz}"] [data-tgrole="{lyr}"]')
    roles = pg.evaluate(f"""[1, 2, 3, 4].map(t => [...document.querySelectorAll('.dci-matrix tr[data-work="' + (t - 1) + '"] .dci-mx-cell[data-col="{wz}"] .dci-mxchip')].map(c => c.textContent.trim().split(' ')[0]).sort())""")
    print('B2) „Pub Co · 1, 3“ auf die Rolle lyricist – Rollen je Track:', roles)
    ok_b = ok_b and roles == [['composer', 'lyricist'], ['composer'], ['lyricist'], ['composer']]
    results.append(ok_b)

    # C) onto an attribute in the head of the track column: "li" for the works of "Side A" (tracks 1, 2)
    pg.click('tr[data-work="1"] [data-act=work-pending]'); pg.wait_for_timeout(300)
    pg.click('tr[data-work="2"] [data-act=work-pending]'); pg.wait_for_timeout(300)
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', '.dci-wattrs-all [data-tgattr=live]')
    live = pg.evaluate("""[...document.querySelectorAll('.dci-matrix tbody tr[data-mrow]')].filter(tr => tr.dataset.mrow.match(/^[wp]:/))
      .map(tr => [Number(tr.dataset.work) + 1, [...tr.querySelectorAll('.dci-wpill-on, .dci-wpill-mb')].map(b => b.textContent.trim())])""")
    print('C1) „Side A“ auf „li“:', live)
    ok_c = live == [[1, ['li✎']], [2, ['li']], [3, []]]
    results.append(ok_c)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
