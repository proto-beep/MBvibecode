"""Media choice before the import (release with three media): "All" with the release level is the import as before;
media 2-3 without the release level: only their credits, credits without tracks on their tracks, nothing on the
release (group), works matrix and medium filter only with those media; "Choose media …" asks again (after a
confirmation); a remembered choice is preselected next time (still asked); unknown media in the text field;
cancelling keeps the import, Escape on the first question imports nothing (a message offers the question again)."""
import re
from playwright.sync_api import sync_playwright
import harness as H

H.MEDIA = [2, 1, 1]
orig = H.discogs_release


def rel():
    d = orig()
    pos = ['1-1', '1-2', '2-1', '3-1']
    for i, t in enumerate(d['tracklist']):
        t['position'] = pos[i]
    for e in d['extraartists']:
        if e['name'] == 'Keys Guy':
            e['tracks'] = '2-1'
        if e['name'] == 'Drum Guy':
            e['tracks'] = '1-1 to 1-2'
    return d


H.discogs_release = rel
DLG = '[data-el=media]'
STATE = """(() => {
  const groups = [...document.querySelectorAll('#dci-overlay section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent,
    [...g.querySelectorAll('tr.dci-row')].map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1] + ((tr.querySelector('[data-tcount]') || {}).textContent ? ':' + tr.querySelector('[data-tcount]').textContent.trim() : ''))]);
  const matrix = [...new Set([...document.querySelectorAll('.dci-matrix tr[data-work]')].map(tr => Number(tr.dataset.work)))];
  const cols = [...document.querySelectorAll('[data-colhead]')].map(h => h.dataset.colhead.startsWith('mb:') ? 'mb' : (h.querySelector('.dci-mx-name, strong') || h).textContent.trim().slice(0, 20));
  const filter = [...document.querySelectorAll('[data-f=medium-filter] option')].map(o => o.textContent.trim());
  const now = (document.querySelector('.dci-media-now') || {}).textContent || '';
  return { groups, matrix, cols, filter, now };
})()"""
results = []


def dialog(pg):
    pg.wait_for_selector(f'{DLG} [data-mact=ok]', timeout=20000)
    return pg.evaluate(f"""(() => {{ const d = document.querySelector('{DLG}');
      return {{ pressed: [...d.querySelectorAll('[data-mact=toggle]')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => Number(b.dataset.m)),
        text: d.querySelector('[data-mf=text]').value, release: d.querySelector('[data-mf=release]').checked,
        remember: d.querySelector('[data-mf=remember]').checked, sum: d.querySelector('[data-mel=sum]').textContent,
        err: d.querySelector('[data-mel=err]').hidden ? '' : d.querySelector('[data-mel=err]').textContent,
        ok: !d.querySelector('[data-mact=ok]').disabled, hint: d.querySelector('.dci-media-body > p.dci-sub').textContent }}; }})()""")


def done(pg):
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
    pg.wait_for_timeout(1500)


def names(st):
    return sorted(g[0] for g in st['groups'])


def clear_log(pg):
    pg.evaluate("document.querySelector('#dci-log [data-log-act=clear]').click()")


def ok_click(pg):
    # the log is kept in the session: cleared, so "Import complete" is the one of this import
    clear_log(pg)
    pg.click(f'{DLG} [data-mact=ok]')


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg, media=False)

    # A) the question, preselected "All" with the release level: the import as before
    q = dialog(pg)
    print('A1) Frage:', q)
    ok_a = q['pressed'] == [1, 2, 3] and q['text'] == '1-3' and q['release'] and not q['remember'] and q['sum'] == '3 of 3 media · 4 tracks' and q['ok']
    ok_click(pg)
    done(pg)
    base = pg.evaluate(STATE)
    print('A2) alle Medien:', base)
    ok_a = ok_a and 'Drum Guy' in names(base) and 'Photo Guy' in names(base) and 'Sony' in names(base) and base['matrix'] == [0, 1, 2, 3] \
        and base['now'] == 'all media with the release level' and base['filter'][0] == 'all' and len(base['filter']) == 4
    results.append(ok_a)

    # B) "Choose media …": media 2-3 without the release level
    pg.click('[data-act=media-choose]')
    q = dialog(pg)
    pg.fill(f'{DLG} [data-mf=text]', '2-3')
    pg.click(f'{DLG} [data-mf=release]')
    q = dialog(pg)
    print('B1) Frage mit „2-3“, ohne Release-Ebene:', q['pressed'], q['release'], q['sum'])
    ok_b = q['pressed'] == [2, 3] and not q['release'] and q['sum'] == '2 of 3 media · 2 tracks'
    ok_click(pg)
    done(pg)
    st = pg.evaluate(STATE)
    print('B2) Zeilen:', st['groups'])
    print('    Matrix:', st['matrix'], st['cols'], '| Filter:', st['filter'], '| Auswahl:', st['now'])
    g = dict(st['groups'])
    logs = pg.locator('#dci-log li').all_inner_texts()
    print('    Protokoll:', [x for x in logs if 'Media' in x])
    ok_b = ok_b and names(st) == ['Abbey Road Studios', 'Bass Man', 'Bob Producer', 'Ghost Pub', 'Guitar Guy', 'Keys Guy', 'Other Pub', 'Pub Co', 'Writer Z'] \
        and g['Bass Man'] == ['recording:2 of 2 tracks'] and g['Keys Guy'] == ['recording:1 of 2 tracks'] and g['Abbey Road Studios'] == ['recording:2 of 2 tracks'] \
        and st['matrix'] == [2, 3] and not any('Writer W' in c for c in st['cols']) and any('Writer Z' in c for c in st['cols']) \
        and st['now'] == 'media 2-3 without the release level' and len(st['filter']) == 3 and not any(o.startswith('Medium 1 ') for o in st['filter']) \
        and any('Media chosen: media 2-3 without the release level' in x for x in logs)
    results.append(ok_b)

    # C) only medium 1 (buttons), with the release level, remembered; cancelling later keeps that import
    pg.click('[data-act=media-choose]')
    dialog(pg)
    pg.click(f'{DLG} [data-mact=none]')
    q0 = dialog(pg)
    pg.click(f'{DLG} [data-mact=toggle][data-m="1"]')
    pg.check(f'{DLG} [data-mf=remember]')
    q = dialog(pg)
    print('C1) „Keine“:', q0['text'] or '–', q0['ok'], '| Medium 1:', q['text'], q['pressed'], q['release'])
    ok_c = q0['text'] == '' and q0['ok'] and q['text'] == '1' and q['pressed'] == [1] and q['release']
    ok_click(pg)
    done(pg)
    st = pg.evaluate(STATE)
    print('C2) Zeilen:', names(st), '| Matrix:', st['matrix'], '| Filter:', st['filter'], '| Auswahl:', st['now'])
    ok_c = ok_c and names(st) == ['Abbey Road Studios', 'Ann Rep', 'Bass Man', 'Bob Producer', 'Drum Guy', 'Ghost Pub', 'Guitar Guy', 'Other Pub', 'Photo Guy', 'Pub Co', 'Sony', 'Writer W'] \
        and st['matrix'] == [0, 1] and st['filter'] == [] and st['now'] == 'media 1 with the release level'
    stored = pg.evaluate(f"JSON.parse(localStorage.getItem('dci-media-sel'))['{H.REL}']")
    print('    gemerkt:', stored)
    ok_c = ok_c and stored['media'] == [1] and stored['release'] is True
    pg.click('[data-act=media-choose]')
    q = dialog(pg)
    print('C3) erneut gefragt, vorausgewählt:', q['pressed'], q['remember'], '|', q['hint'][:40])
    pg.click(f'{DLG} [data-mact=cancel]'); pg.wait_for_timeout(300)
    st2 = pg.evaluate(STATE)
    ok_c = ok_c and q['pressed'] == [1] and q['remember'] and q['hint'].startswith('Preselected') and names(st2) == names(st) \
        and pg.locator(DLG).is_hidden()
    results.append(ok_c)

    # D) after reloading: still asked (remembered choice preselected); unknown media; Escape imports nothing
    pg.reload()
    pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg, media=False)
    q = dialog(pg)
    pg.fill(f'{DLG} [data-mf=text]', '1-4, x')
    bad = dialog(pg)
    pg.fill(f'{DLG} [data-mf=text]', '1, 3')
    q2 = dialog(pg)
    print('D1) nach Neuladen:', q['pressed'], q['remember'], '| „1-4, x“:', bad['err'], bad['ok'], '| „1, 3“:', q2['pressed'], q2['ok'])
    ok_d = q['pressed'] == [1] and q['remember'] and 'Not a medium of this release: 4, x (media: 1-3)' == bad['err'] and not bad['ok'] \
        and q2['pressed'] == [1, 3] and q2['ok'] and q2['err'] == ''
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
    msg = pg.locator('[data-el=msgs]').inner_text()
    print('D2) Escape:', pg.locator(DLG).is_hidden(), '| Nachricht:', re.sub(r'\s+', ' ', msg), '| Zeilen:', pg.locator('#dci-overlay section.dci-group').count())
    ok_d = ok_d and pg.locator(DLG).is_hidden() and 'Import cancelled' in msg and pg.locator('#dci-overlay section.dci-group').count() == 0
    pg.click('[data-el=msgs] [data-act=media-choose]')
    dialog(pg)
    pg.click(f'{DLG} [data-mact=all]')
    pg.uncheck(f'{DLG} [data-mf=remember]')
    ok_click(pg)
    done(pg)
    st = pg.evaluate(STATE)
    same = sorted(map(str, st['groups'])) == sorted(map(str, base['groups'])) and st['matrix'] == base['matrix'] and st['cols'] == base['cols']
    if not same:
        print('   vorher:', base); print('   jetzt: ', st)
    print('D3) „Alle“ mit Release-Ebene wie vorher:', same, '| gemerkt:', pg.evaluate("localStorage.getItem('dci-media-sel')"))
    ok_d = ok_d and same and pg.evaluate("localStorage.getItem('dci-media-sel')") is None
    results.append(ok_d)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
