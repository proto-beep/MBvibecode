"""Mapping: "Mix", "Recording", "Engineer [Mix]", "Engineer [Recording]" without role credit (W006, W007);
"Engineer [Mix, Recording, Assistant]" is one row per task (S018); "Trumpet [Pocket Trumpet]" is the instrument
pocket trumpet without role credit. Rule ids next to ⓘ open "Mapping rules" at that rule (highlighted, also
when a search hid it). Dragging out of the dates block: the list scrolls up only after the pointer was further
down once and then stays below the block a moment."""
import re
from playwright.sync_api import sync_playwright
import harness as H

for i, n in [(9120, 'trumpet'), (9121, 'pocket trumpet')]:
    H.attr(i, n, 14, 14)
    H.LINKED['link_attribute_type'][str(i)] = H.ATTRS[i]
# as in MusicBrainz: mix, recording and producer have a "task" attribute (where a role credit would go)
for i in (143, 128, 141):
    H.LTS[i]['attributes']['1150'] = {'min': 0, 'max': None}
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
orig = H.discogs_release
ROLES = ['Mix', 'Recording', 'Engineer [Mix, Recording, Assistant]', 'Trumpet [Pocket Trumpet]']


def rel():
    d = orig()
    d['extraartists'] += [{'name': 'Keys Guy', 'anv': '', 'role': ', '.join(ROLES), 'tracks': '', 'id': 3003, 'join': ''}]
    return d


H.discogs_release = rel
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(400)
    rows = pg.evaluate("""[...document.querySelectorAll('[data-group] tr.dci-row')].filter(tr => tr.closest('[data-group]').querySelector('.dci-gname').textContent.includes('Keys Guy'))
      .map(tr => { const v = (f) => { const e = tr.querySelector('[data-f=' + f + ']'); return e ? (e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).text : e.value) : '-'; };
        return [tr.querySelector('.dci-drole').textContent.trim(), v('type'), v('primary'), v('role-credit'),
          [...tr.querySelectorAll('input[data-f=flag]:checked')].map(c => c.value).join(','), tr.querySelector('.dci-c-role').textContent.replace(/\\s+/g, ' ').trim()]; })""")
    for r in rows:
        print('  ', r[:5], '|', r[5][:110])
    by = {r[0]: r for r in rows}
    mix, rec = by.get('Mix'), by.get('Recording')
    emix, erec = by.get('Engineer [Mix, Assistant]'), by.get('Engineer [Recording, Assistant]')
    tp = by.get('Trumpet [Pocket Trumpet]')
    ok1 = mix and mix[1] == 'mix' and mix[3] == '' and rec and rec[1] == 'recording' and rec[3] == '' \
        and emix and emix[1] == 'mix' and emix[3] == '' and 'assistant' in emix[4] and 'S018' in emix[5] and 'Engineer [Mix, Recording, Assistant]' in emix[5] \
        and erec and erec[1] == 'recording' and erec[3] == '' and 'assistant' in erec[4] \
        and tp and tp[2] == 'pocket trumpet' and tp[3] == ''
    print('1) Mapping:', ok1)
    results.append(ok1)

    # 2) a rule id opens "Mapping rules" at that rule, also when a search hid it
    pg.click('[data-act=rules]'); pg.wait_for_timeout(200)
    pg.fill('#dci-rules [data-rf=search]', 'pocket'); pg.wait_for_timeout(150)
    pg.click('#dci-rules [data-rules-close]')
    tr = pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text='Engineer [Mix, Assistant]')).first
    ids = tr.locator('.dci-ruleid').all_inner_texts()
    tr.locator('.dci-ruleid', has_text='W006').click(); pg.wait_for_timeout(400)
    hit = pg.evaluate("""(() => { const r = document.querySelector('#dci-rules tr.dci-rule-hit'); if (!r) return null;
      const box = document.querySelector('#dci-rules').getBoundingClientRect(); const rb = r.getBoundingClientRect();
      return [r.dataset.rid, !r.hidden, rb.top >= box.top && rb.bottom <= box.bottom, document.querySelector('#dci-rules [data-rf=test]').value,
        document.querySelector('#dci-rules [data-rf=search]').value]; })()""")
    print('2) Regeln der Zeile:', ids, '| Klick auf W006 →', hit)
    tr.locator('.dci-ruleid', has_text='R033').click(); pg.wait_for_timeout(300)
    hit2 = pg.evaluate("[...document.querySelectorAll('#dci-rules tr.dci-rule-hit')].map(r => r.dataset.rid)")
    print('   dann R033 →', hit2)
    ok2 = ids == ['R033', 'W006', 'S018', 'S019'] and hit and hit[0] == 'W006' and hit[1] and hit[2] and hit[3] == 'Engineer [Mix, Assistant]' and hit[4] == '' and hit2 == ['R033']
    results.append(ok2)
    pg.click('#dci-rules [data-rules-close]')

    # 3) autoscroll as in browsers: only after 0.2 s in an edge zone (anew after leaving it), then gently faster
    pg.evaluate("document.querySelector('#dci-overlay [data-el=body]').scrollTop = 600")
    pg.wait_for_timeout(100)
    res = pg.evaluate("""async () => {
      const body = document.querySelector('#dci-overlay [data-el=body]');
      const dates = document.querySelector('#dci-overlay [data-el=dates]');
      const chip = document.querySelector('.dci-pchip-date');
      const y0 = dates.getBoundingClientRect().bottom + 10;          // just below the dates block
      const yb = body.getBoundingClientRect().bottom - 5;            // at the lower edge
      const dt = new DataTransfer();
      const over = (y) => body.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt, clientX: 300, clientY: y }));
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      const stay = async (y, ms) => { const t = Date.now(); while (Date.now() - t < ms) { over(y); await wait(40); } };
      chip.dispatchEvent(new DragEvent('dragstart', { bubbles: true, dataTransfer: dt }));
      const start = body.scrollTop;
      await stay(y0, 150); over(y0 + 200);                           // out of the block: passes the zone in 150 ms
      const passed = body.scrollTop;
      await stay(y0, 150); over(y0 + 200); await stay(y0, 150);      // in, out, in again: the wait starts anew
      const anew = body.scrollTop;
      await stay(y0, 500);                                           // stays: scrolls up
      const up = body.scrollTop;
      over(y0 + 200); const a = body.scrollTop;
      await stay(yb, 600);                                           // lower edge: scrolls down after the wait
      const down = body.scrollTop;
      chip.dispatchEvent(new DragEvent('dragend', { bubbles: true, dataTransfer: dt }));
      return [start, passed, anew, up, a, down];
    }""")
    print('3) scrollTop: Start, durchgezogen (150 ms), erneut kurz, länger oben, …, unten länger:', res)
    ok3 = res[0] > 0 and res[1] == res[0] and res[2] == res[0] and res[3] < res[0] and res[5] > res[4]
    results.append(ok3)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
