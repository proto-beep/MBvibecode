"""Credits Importer 3.27.3: the messages at the top close and fold (collected item 56).
A) After the import two messages (dates from the notes): a line "▾ 2 messages" above them, each with ✕ (a symbol – the
   text of the message stays as it was).
B) ✕ closes one; with one message left the fold line is gone.
C) Two messages again (an error: "no Discogs release or Bandcamp album recognized"): "▾ 2 messages" folds them in –
   "▸ 2 messages", nothing else shown; a new warning or error unfolds them.
D) A new import ("Delete stored import …", the release imported afresh) shows its messages again, unfolded: closed means
   until the next import."""
from playwright.sync_api import sync_playwright
import harness as H

# [3.30.8] the shared month of "March 1–3, 2001" no longer counts as a date without a group: a date that really has none
_orig_rel = H.discogs_release


def _rel():
    d = _orig_rel()
    d['notes'] += ' The band met on 4 July 2000.'
    return d


H.discogs_release = _rel

MSGS = """(() => { const el = document.querySelector('[data-el=msgs]'); const head = el.querySelector('.dci-msgs-fold');
  return { head: head ? head.textContent.replace(/\\s+/g, ' ').trim() : null, expanded: head ? head.getAttribute('aria-expanded') : null,
    msgs: [...el.querySelectorAll('.dci-msg')].map(m => [m.textContent.trim().slice(0, 40), !!m.querySelector('.dci-msg-x svg')]) }; })()"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(600)
    st = lambda: pg.evaluate(MSGS)
    # A)
    a1 = st()
    print('A)', a1)
    results.append(a1['head'] == '▾ 2 messages' and a1['expanded'] == 'true' and len(a1['msgs']) == 2 and all(x[1] for x in a1['msgs'])
                   and a1['msgs'][0][0].startswith('2 dates from the notes were placed'))
    # B)
    pg.click('[data-el=msgs] .dci-msg >> nth=0 >> .dci-msg-x')
    pg.wait_for_timeout(200)
    b1 = st()
    print('B) eine geschlossen:', b1)
    results.append(b1['head'] is None and len(b1['msgs']) == 1 and b1['msgs'][0][0].startswith('1 date from the notes has no word'))
    # C) an error: two again; fold; a new error unfolds
    H.src_menu(pg)
    pg.fill('[data-f=discogs-input]', 'no release here')
    pg.click('[data-act=discogs-load]')
    pg.wait_for_timeout(300)
    c1 = st()
    pg.click('[data-act=msgs-fold]')
    pg.wait_for_timeout(200)
    c2 = st()
    H.src_menu(pg)
    pg.fill('[data-f=discogs-input]', 'still nothing')
    pg.click('[data-act=discogs-load]')
    pg.wait_for_timeout(300)
    c3 = st()
    print('C) zwei:', c1['head'], '| eingeklappt:', c2, '| neuer Fehler:', c3['head'], c3['expanded'], len(c3['msgs']))
    results.append(c1['head'] == '▾ 2 messages' and c2 == {'head': '▸ 2 messages', 'expanded': 'false', 'msgs': []}
                   and c3['head'] == '▾ 3 messages' and c3['expanded'] == 'true' and len(c3['msgs']) == 3)
    pg.click('[data-act=msgs-fold]')
    pg.wait_for_timeout(200)
    # D) a new import from scratch ("Delete stored import …"): its messages again, unfolded
    H.src_menu(pg, 'forget-open')
    pg.click('[data-act=forget-do]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(600)
    d1 = st()
    print('D) neuer Import:', d1)
    results.append(d1['head'] == '▾ 2 messages' and d1['expanded'] == 'true' and any(m[0].startswith('2 dates from the notes were placed') for m in d1['msgs']))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
