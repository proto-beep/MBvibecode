"""Credits Importer 3.27.0: the compact view of the entries (collected item 31; milestone). [3.27.2] Full is the default
again (item 72), the symbol in the head switches (item 60).
A) Full at first (nothing stored); the symbol in the head (not pressed) switches to compact – pressed, stored "compact"
   (until 3.27.1: compact by default, "Compact | Full" above the entries); one line per row – the role as written
   → type and instrument, level, tracks in short, date (or "no date"), what is open in colour (yellow "Bass: which
   instrument?"); the fields of the full row and the "credited as" block hidden.
B) A click on the line opens the full row (its type field focused); "▴ compact" closes it again.
C) The tracks and the date of the compact line are still drop targets: a track group ("Side A", tracks 1–2) dropped
   onto it gives "tracks 1–2", a date of the pool shows on the line.
D) The question answered in the opened row ("double bass"): the line says so, the yellow mark is gone.
E) A skipped row: grey, with ✕ – out of the dashboard; the next import brings it back.
F) "Compact" remembered after reloading; ⚙ Settings → General has the same switch: "Full" – every row with its fields,
   nothing stored.
G) A jump to an incomplete row (› in the summary) opens it."""
import re
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import drag

LINE = """(name) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; return [...g.querySelectorAll('tr.dci-row')].map(tr => { const c = tr.querySelector('.dci-cline');
    return { id: tr.dataset.row, open: tr.classList.contains('dci-open'), text: c ? [...c.children].map(x => x.textContent.replace(/\\s+/g, ' ').trim()).join(' ') : '',
      flags: c ? [...c.querySelectorAll('.dci-cl-flag')].map(f => [f.className.replace('dci-cl-flag ', ''), f.textContent.trim()]) : [],
      typeVisible: !!tr.querySelector('[data-f=type]') && tr.querySelector('[data-f=type]').offsetParent !== null,
      hasDate: !!(c && c.querySelector('.dci-cl-date.dci-cl-has')), x: !!(c && c.querySelector('.dci-cl-x')), bg: getComputedStyle(tr).backgroundColor }; }); }"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, view=None)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(800)
    line = lambda name: pg.evaluate(LINE, name)
    # A) full at first; the symbol in the head
    VIEWBTN = '.dci-head [data-act=view-toggle]'
    a_full = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), pg.locator(VIEWBTN).get_attribute('aria-pressed'),
              pg.evaluate("document.querySelectorAll('.dci-toolbar [data-act=view]').length"), line('Bass Man')[0]['typeVisible']]
    pg.click(VIEWBTN)
    pg.wait_for_timeout(400)
    a0 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), pg.locator(VIEWBTN).get_attribute('aria-pressed'),
          pg.evaluate("[...document.querySelectorAll('.dci-variants')].filter(v => v.offsetParent !== null).length"),
          pg.evaluate("localStorage.getItem('dci-view')")]
    bass = line('Bass Man')
    print('A) zuerst voll:', a_full, '| nach dem Symbol:', a0, '\n   Bass Man:', bass)
    results.append(a_full == [False, 'false', 0, True] and a0 == [True, 'true', 0, '"compact"'] and bass and bass[0]['text'].startswith('▸ Bass → instrument · bass Recording all 4 tracks no date')
                   and bass[0]['flags'] == [['dci-cl-ask', 'Bass: which instrument?']] and not bass[0]['typeVisible'])
    # B) open, close
    rid = bass[0]['id']
    pg.click(f'tr[data-row="{rid}"] .dci-cl-role')
    pg.wait_for_timeout(200)
    b1 = [line('Bass Man')[0]['open'], line('Bass Man')[0]['typeVisible'], pg.evaluate("document.activeElement.dataset.f"),
          pg.evaluate("[...document.querySelectorAll('.dci-variants')].filter(v => v.offsetParent !== null).length")]
    pg.click(f'tr[data-row="{rid}"] .dci-cl-close')
    pg.wait_for_timeout(200)
    b2 = [line('Bass Man')[0]['open'], pg.evaluate("document.activeElement.classList.contains('dci-cl-tgl')")]
    print('B) offen, Typ sichtbar, Fokus, „credited as“:', b1, '| wieder zu, Fokus:', b2)
    results.append(b1 == [True, True, 'type', 1] and b2 == [False, True])
    # C) drops onto the compact line
    pg.click('[data-act=tg-new]')
    pg.fill('[data-f=tg-name]', 'Side A')
    pg.check('[data-f=tg-track][data-i="0"]')
    pg.check('[data-f=tg-track][data-i="1"]')
    pg.click('[data-act=tg-save]')
    pg.wait_for_timeout(200)
    guitar = line('Guitar Guy')[0]['id']
    gid = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-tg')].find(c => c.textContent.includes('Side A')).dataset.id")
    drag(pg, f'.dci-pools-body .dci-pchip-tg[data-id="{gid}"] .dci-chip-main', f'tr[data-row="{guitar}"] .dci-cl-tracks')
    c1 = line('Guitar Guy')[0]
    date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
    dlabel = pg.evaluate(f"document.querySelector('.dci-pools-body .dci-pchip-date[data-id=\"{date}\"] .dci-chip-main').textContent.replace(/\\s+/g, ' ').trim()")
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'tr[data-row="{guitar}"] .dci-cl-date')
    c2 = line('Guitar Guy')[0]
    print('C) Trackgruppe:', c1['text'], '| Datum', repr(dlabel[:30]), '→', c2['text'], c2['hasDate'])
    results.append('tracks 1–2' in c1['text'] and c2['hasDate'] and dlabel.split(' · ')[0] in c2['text'] and not c2['open'])
    # D) the question answered in the opened row
    pg.click(f'tr[data-row="{rid}"] .dci-cl-flag')
    pg.wait_for_timeout(200)
    pg.click(f'tr[data-row="{rid}"] [data-act=instr-pick][data-instr="double bass"]')
    pg.wait_for_timeout(400)
    pg.click(f'tr[data-row="{rid}"] .dci-cl-close')
    pg.wait_for_timeout(300)
    d1 = line('Bass Man')[0]
    print('D) beantwortet:', d1['text'], d1['flags'])
    results.append('→ instrument · double bass' in d1['text'] and d1['flags'] == [])
    # E) a skipped row: grey with ✕
    pg.click(f'tr[data-row="{guitar}"] .dci-cl-role')
    pg.click(f'tr[data-row="{guitar}"] [data-act=level][data-level=skip]')
    pg.wait_for_timeout(300)
    pg.click(f'tr[data-row="{guitar}"] .dci-cl-close')
    pg.wait_for_timeout(300)
    e1 = line('Guitar Guy')[0]
    pg.click(f'tr[data-row="{guitar}"] .dci-cl-x')
    pg.wait_for_timeout(300)
    e2 = [line('Guitar Guy'), [m for m in pg.locator('.dci-msg').all_inner_texts() if 'Guitar Guy' in m][:1]]
    print('E) Skip:', e1['text'], e1['x'], e1['bg'], '| ✕:', e2)
    results.append(e1['text'].startswith('▸ Guitar Skip') and e1['x'] and e1['bg'] != 'rgb(255, 255, 255)' and e2[0] is None and bool(e2[1]))
    # F) compact remembered, full in the settings
    f1 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), line('Bass Man')[0]['typeVisible'], pg.evaluate("localStorage.getItem('dci-view')")]
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 60)
    pg.wait_for_timeout(800)
    f2 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), line('Guitar Guy') is not None]
    H.open_settings(pg, 'general')
    f3 = pg.evaluate("[...document.querySelectorAll('[data-el=settings] [data-act=view]')].map(b => [b.dataset.view, b.getAttribute('aria-pressed')])")
    pg.click('[data-el=settings] [data-act=view][data-view=full]')
    pg.wait_for_timeout(300)
    f4 = [pg.evaluate("document.getElementById('dci-overlay').classList.contains('dci-compact')"), pg.evaluate("localStorage.getItem('dci-view')"),
          pg.locator(VIEWBTN).get_attribute('aria-pressed'), line('Bass Man')[0]['typeVisible']]
    pg.click('[data-el=settings] [data-act=view][data-view=compact]')
    pg.wait_for_timeout(300)
    print('F) kompakt:', f1, '| neu geladen:', f2, '| Einstellungen:', f3, '| voll dort:', f4)
    results.append(f1 == [True, False, '"compact"'] and f2 == [True, True] and f3 == [['compact', 'true'], ['full', 'false']] and f4 == [False, None, 'false', True])
    pg.click('.dci-head [data-act=settings-open]')
    # G) a new row ("+ Another role") is open; closed and incomplete, a jump to it (› in the summary) opens it again
    pg.click('section.dci-group:has(.dci-gname strong:text-is("Bass Man")) [data-act=add-role]')
    pg.wait_for_timeout(300)
    rows = line('Bass Man')
    new_row = rows[-1]
    pg.click(f'tr[data-row="{new_row['id']}"] .dci-cl-close')
    pg.wait_for_timeout(300)
    g0 = [new_row['open'], line('Bass Man')[-1]['open'], line('Bass Man')[-1]['flags'][:1]]
    pg.click('.dci-incomplete .dci-textbtn[data-act=inc-next]')
    pg.wait_for_timeout(400)
    g1 = line('Bass Man')[-1]['open']
    print('G) neue Zeile offen, zu, Markierung:', g0, '| nach ›:', g1)
    results.append(g0[0] and not g0[1] and g0[2] and g0[2][0][0] == 'dci-cl-bad' and g1)
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
