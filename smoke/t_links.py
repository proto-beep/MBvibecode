"""Credits Importer 3.24.0: several linked releases of one source (collected item 51).
A release linked to three Discogs releases: 1234, 1240 (more credits) and 999 (Discogs does not have it).
A) The dialog "This release is linked to 3 Discogs releases" lists them; each is read in the background and counted
   (credits, companies, tracks); 999 "could not be read"; 1240 has the most data: bold, "most data", preselected.
B) "Open all in background tabs": the three Discogs pages in background tabs (GM_openInTab, not active).
C) "Import": Discogs 1240 is loaded, the log says it was chosen from three, the choice is remembered for this release;
   opened again, the dashboard loads 1240 at once (no dialog).
D) Another choice by hand (1234, "Remember" unticked): 1234 is loaded, nothing remembered. E) "Cancel": the message
   "… Choose one above.", nothing loaded."""
from playwright.sync_api import sync_playwright
import harness as H

dg = H.discogs_release()
more = dict(dg, id=1240, title='Testalbum (deluxe)')
more['extraartists'] = dg['extraartists'] + [{'name': 'Keys Guy', 'anv': '', 'role': 'Piano', 'tracks': '', 'id': 3003, 'join': ''},
                                             {'name': 'Guitar Guy', 'anv': '', 'role': 'Mandolin', 'tracks': '', 'id': 3002, 'join': ''},
                                             {'name': 'Bass Man', 'anv': '', 'role': 'Arranged By', 'tracks': '', 'id': 3001, 'join': ''}]
H.DG_API['/releases/1240'] = more
H.DG_API['/releases/999'] = None
orig_ws = H.ws_release


def ws(full=False):
    d = orig_ws(full)
    d['relations'] += [{'target-type': 'url', 'type': 'discogs', 'url': {'resource': 'https://www.discogs.com/release/1240'}},
                       {'target-type': 'url', 'type': 'discogs', 'url': {'resource': 'https://www.discogs.com/release/999'}}]
    return d


H.ws_release = ws
DLG = """(() => { const d = document.querySelector('[data-el=links]'); if (!d || d.hidden) return null;
  return { title: d.querySelector('h3').textContent.trim(), rows: [...d.querySelectorAll('.dci-link-opt')].map(r => ({ name: r.querySelector('.dci-link-name').textContent.trim(),
    count: r.querySelector('[data-lel=count]').textContent.trim(), best: r.classList.contains('dci-link-best') && !r.querySelector('.dci-link-bestmark').hidden,
    bold: getComputedStyle(r.querySelector('.dci-link-name')).fontWeight, checked: r.querySelector('input').checked })) }; })()"""
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
SOURCE = "document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 40)"
results = []


def open_dlg(pg):
    pg.evaluate("() => { window.__tabs = []; window.GM_openInTab = (u, o) => { window.__tabs.push([u, o]); }; }")
    pg.click('#dci-open')
    pg.wait_for_selector('[data-el=links]:not([hidden])', timeout=20000)
    H.wait_for(pg, "![...document.querySelectorAll('[data-el=links] [data-lel=count]')].some(s => /counting/.test(s.textContent))", 60)
    pg.wait_for_timeout(300)
    return pg.evaluate(DLG)


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    # A)
    d = open_dlg(pg)
    print('A)', d['title'])
    for r in d['rows']:
        print('   ', r)
    rows = {r['name']: r for r in d['rows']}
    ok_a = d['title'] == 'This release is linked to 3 Discogs releases' and list(rows) == ['Discogs 1234', 'Discogs 1240', 'Discogs 999'] \
        and rows['Discogs 1240']['best'] and rows['Discogs 1240']['checked'] and rows['Discogs 1240']['bold'] == '700' \
        and not rows['Discogs 1234']['best'] and rows['Discogs 1234']['bold'] != '700' \
        and rows['Discogs 1240']['count'].startswith('“Testalbum (deluxe)” – credits: ') and 'tracks: 4' in rows['Discogs 1240']['count'] \
        and rows['Discogs 999']['count'].startswith('could not be read')
    results.append(ok_a)
    # B)
    pg.click('[data-el=links] [data-lact=tabs]')
    pg.wait_for_timeout(300)
    tabs = pg.evaluate('window.__tabs')
    print('B) Hintergrund-Tabs:', tabs)
    results.append([t[0] for t in tabs] == ['https://www.discogs.com/release/1234', 'https://www.discogs.com/release/1240', 'https://www.discogs.com/release/999']
                   and all(t[1] and t[1].get('active') is False for t in tabs))
    # C)
    pg.click('[data-el=links] [data-lact=ok]')
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    pg.wait_for_timeout(500)
    src = pg.evaluate(SOURCE)
    chosen = [x for x in pg.evaluate(LOGS) if 'Chosen from' in x]
    kept = pg.evaluate(f"(JSON.parse(localStorage.getItem('dci-source-pick') || '{{}}')['{H.REL}'] || {{}}).id")
    print('C) Quelle:', src, '| Protokoll:', chosen, '| gemerkt:', kept)
    ok_c = 'Discogs 1240' in src and chosen == ['Chosen from 3 linked Discogs releases: Discogs 1240'] and kept == '1240'
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    pg.click('#dci-open')
    H.wait_for(pg, f"{LOGS}.some(x => /Source chosen for this release before/.test(x))", 60)
    H.wait_for(pg, "/Discogs 1240/.test(document.querySelector('[data-el=source]').innerText)", 60)
    pg.wait_for_timeout(500)
    again = [pg.evaluate(SOURCE), pg.evaluate("!document.querySelector('[data-el=links]') || document.querySelector('[data-el=links]').hidden"),
             [x for x in pg.evaluate(LOGS) if 'chosen' in x.lower()]]
    print('   neu geöffnet:', again)
    ok_c = ok_c and 'Discogs 1240' in again[0] and again[1] and any('Source chosen for this release before: Discogs' in x for x in again[2])
    results.append(ok_c)
    # D) another choice, not remembered
    pg.evaluate("localStorage.removeItem('dci-source-pick')")
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    open_dlg(pg)
    pg.click("[data-el=links] input[name=dci-link-pick][value='0']")
    pg.click('[data-el=links] [data-lf=remember]')
    pg.click('[data-el=links] [data-lact=ok]')
    H.wait_for(pg, "/Discogs 1234/.test(document.querySelector('[data-el=source]').innerText)", 60)
    pg.wait_for_timeout(800)
    d1 = [pg.evaluate(SOURCE), pg.evaluate("localStorage.getItem('dci-source-pick')")]
    print('D) von Hand 1234, nicht gemerkt:', d1)
    results.append('Discogs 1234' in d1[0] and d1[1] is None)
    # E) cancel
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    open_dlg(pg)
    pg.click('[data-el=links] [data-lact=cancel]')
    pg.wait_for_timeout(500)
    msgs = pg.locator('.dci-msg').all_inner_texts()
    e1 = [any('linked to 3 Discogs releases. Choose one above.' in m for m in msgs), pg.locator('tr.dci-row').count()]
    print('E) Abbrechen:', e1)
    results.append(e1 == [True, 0])
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
