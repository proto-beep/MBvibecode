"""Credits Importer 3.24.1: the tracks of a source compared with MusicBrainz's – their number and their titles (collected
item 52; S030, T038).
A) The dialog of three linked Discogs releases: 1240 has the most credits but five tracks – yellow "differs from the
   MusicBrainz release: 5 tracks instead of 4"; preselected (bold) is 1234, the most data among those whose tracks fit,
   marked "most data with matching tracks"; 999 cannot be read.
B) 1240 imported anyway: the yellow message in the dashboard ("… 5 tracks instead of 4 …") and in the log.
C) Every import: titles with small differences ("Song One (Remastered)", "The Song Two", "Song Three – Live",
   "song four") fit – no message; D) two titles quite different ("Intro", "Outro") – "2 of 4 titles differ", with the
   titles in the message."""
import copy
from playwright.sync_api import sync_playwright
import harness as H

dg = H.discogs_release()
more = copy.deepcopy(dg)
more.update(id=1240, title='Testalbum (deluxe)')
more['extraartists'] += [{'name': 'Keys Guy', 'anv': '', 'role': 'Piano', 'tracks': '', 'id': 3003, 'join': ''},
                         {'name': 'Guitar Guy', 'anv': '', 'role': 'Mandolin', 'tracks': '', 'id': 3002, 'join': ''}]
more['tracklist'].append({'position': '5', 'title': 'Bonus Track', 'type_': 'track', 'duration': '3:00', 'extraartists': []})
H.DG_API['/releases/1240'] = more
H.DG_API['/releases/999'] = None
near = copy.deepcopy(dg)
near.update(id=1250)
for t, title in zip(near['tracklist'], ['Song One (Remastered)', 'The Song Two', 'Song Three – Live', 'song four']):
    t['title'] = title
H.DG_API['/releases/1250'] = near
far = copy.deepcopy(dg)
far.update(id=1260)
for t, title in zip(far['tracklist'], ['Intro', 'Outro', 'Song Three', 'Song Four']):
    t['title'] = title
H.DG_API['/releases/1260'] = far
orig_ws = H.ws_release
LINKS = [1240, 999]


def ws(full=False):
    d = orig_ws(full)
    d['relations'] = [r for r in d['relations'] if not (LINKS and LINKS[0] in (1250, 1260))] + \
        [{'target-type': 'url', 'type': 'discogs', 'url': {'resource': f'https://www.discogs.com/release/{i}'}} for i in LINKS]
    return d


H.ws_release = ws
DLG = """(() => { const d = document.querySelector('[data-el=links]'); if (!d || d.hidden) return null;
  return [...d.querySelectorAll('.dci-link-opt')].map(r => ({ name: r.querySelector('.dci-link-name').textContent.trim(),
    warn: r.querySelector('[data-lel=tracks]').hidden ? '' : r.querySelector('[data-lel=tracks]').textContent.trim(),
    warnBg: getComputedStyle(r.querySelector('[data-lel=tracks]')).backgroundColor,
    best: r.classList.contains('dci-link-best') ? r.querySelector('.dci-link-bestmark').textContent.trim() : '', checked: r.querySelector('input').checked })); })()"""
MSG = "[...document.querySelectorAll('.dci-msg-tracks')].map(m => [m.textContent.replace(/\\s+/g, ' ').trim(), getComputedStyle(m).backgroundColor])"
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
results = []


def dashboard(ctx, links):
    LINKS[:] = links
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    return pg, errs


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    # A)
    pg, errs = dashboard(ctx, [1240, 999])
    pg.click('#dci-open')
    pg.wait_for_selector('[data-el=links]:not([hidden])', timeout=20000)
    H.wait_for(pg, "![...document.querySelectorAll('[data-el=links] [data-lel=count]')].some(s => /counting/.test(s.textContent))", 60)
    pg.wait_for_timeout(300)
    rows = {r['name']: r for r in pg.evaluate(DLG)}
    for r in rows.values():
        print('   ', r)
    ok_a = rows['Discogs 1240']['warn'] == 'differs from the MusicBrainz release: 5 tracks instead of 4' and rows['Discogs 1240']['warnBg'] == 'rgb(255, 248, 219)' \
        and rows['Discogs 1234']['best'] == 'most data with matching tracks' and rows['Discogs 1234']['checked'] and not rows['Discogs 1240']['best'] \
        and rows['Discogs 1234']['warn'] == '' and rows['Discogs 999']['warn'] == ''
    print('A)', ok_a)
    results.append(ok_a)
    # B) 1240 anyway
    pg.click("[data-el=links] input[name=dci-link-pick][value='1']")
    pg.click('[data-el=links] [data-lf=remember]')
    pg.click('[data-el=links] [data-lact=ok]')
    H.wait_for(pg, "/Discogs 1240/.test(document.querySelector('[data-el=source]').innerText)", 60)
    H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
    msg = pg.evaluate(MSG)
    logs = [x for x in pg.evaluate(LOGS) if 'Tracks differ' in x or 'tracks differ' in x]
    print('B) Meldung:', msg, '\n   Protokoll:', logs)
    ok_b = len(msg) == 1 and msg[0][0].startswith('Discogs differs from the MusicBrainz release: 5 tracks instead of 4. Tracks are matched in order') \
        and msg[0][1] == 'rgb(255, 248, 219)' and any('Discogs 1240: tracks differ from MusicBrainz – 5 tracks instead of 4' in x for x in logs) \
        and any(x.startswith('Tracks differ from MusicBrainz: Discogs – 5 tracks instead of 4') for x in logs)
    results.append(ok_b)
    print('Fehler:', errs)
    results.append(not errs)
    pg.close()
    # C) small differences: no message; D) two titles quite different
    for name, links in [('C', [1250]), ('D', [1260])]:
        pg, errs = dashboard(ctx, links)
        pg.evaluate("localStorage.removeItem('dci-source-pick')")
        pg.click('#dci-open')
        H.wait_for(pg, f"/Discogs {links[0]}/.test(document.querySelector('[data-el=source]').innerText)", 60)
        H.wait_for(pg, f"{LOGS}.some(x => /Import complete/.test(x))", 60)
        msg = pg.evaluate(MSG)
        print(f'{name}) Discogs {links[0]}:', msg)
        if name == 'C':
            results.append(msg == [])
        else:
            results.append(len(msg) == 1 and 'Discogs differs from the MusicBrainz release: 2 of 4 titles differ (1: “Intro” ≠ “Song One”; 2: “Outro” ≠ “Song Two”)' in msg[0][0])
        print('Fehler:', errs)
        results.append(not errs)
        pg.close()
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
