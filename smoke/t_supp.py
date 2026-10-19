"""Import 3.5.0 (stage 2, variant B): a second source supplements the loaded one, on request only.
A) Discogs is loaded (physical media); "Supplement with" offers the linked Bandcamp album and a text; nothing is read
   from Bandcamp and no marks are shown before a click.
B) "＋ Bandcamp …": the list "Supplements from Bandcamp" – a new role for an entry (Guitar Guy, trumpet on track 2), new
   entries (Anna Viola, all tracks; Test Band, found via its Bandcamp link), a row that differs (Keys Guy, synth: Discogs track 2,
   Bandcamp 1–2; not selected: Discogs stays), a line not recognized; Bass Man's bass is confirmed: marks DG BC.
C) Test Band unticked, "Take over selected": Guitar Guy gets the trumpet row (mark BC), Anna Viola becomes an entry
   with a name suggestion; Test Band, the differing row and the line not recognized stay in the list.
D) Staged: the edit note names the album ("Also from"), what came only from Bandcamp and where the sources differ.
E) "Delete stored import …": the source chosen for the release, the supplement and the log go, the source is imported
   anew (no marks, no list).
F) The old script on the page: this one stays out and says so; started second, it warns after 3 s.
G) Import 3.8.0: a source the release does not link to, typed into the field of "Supplement with" (another Bandcamp
   album): it supplements like a linked one; the loaded source itself is refused."""
import re
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9120, 'trumpet', 14, 14)
H.attr(9121, 'viola', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
ALBUM = 'https://testband.bandcamp.com/album/testalbum'
BAND = 'https://testband.bandcamp.com/'
H.ARTISTS[3040] = (H.uid('dddddddd', 40), 'Test Band')
H.BC_ARTISTS[BAND] = H.ARTISTS[3040]
H.RELEASE_AC[:] = [(H.ARTISTS[3040][0], 'Test Band', 'Test Band', '')]
H.MB_SEARCH['artist'] = [{'id': H.uid('dddddddd', 42), 'name': 'Anna Viola', 'disambiguation': 'violist', 'score': 100}]
CREDITS = 'Bass Man – bass\nTrumpet: Guitar Guy (track 2)\nKeys Guy – synth (tracks 1–2)\nViola: Anna Viola\nTest Band – guitar\nSee you on tour.'
OTHER = 'https://otherband.bandcamp.com/album/live'
H.BC_PAGES[OTHER] = H.bc_page({'artist': 'Other Band', 'current': {'title': 'Live', 'credits': 'Bass Man – bass\nTrumpet: Drum Guy (track 3)', 'about': ''},
                               'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS, 'about': ''},
                               'trackinfo': [{'track_num': i + 1, 'title': t} for i, t in enumerate(H.TITLES)]})
orig_ws = H.ws_release


def ws():
    d = orig_ws()
    d['relations'].append({'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}})
    return d


H.ws_release = ws
logs = lambda pg, pat: [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if re.search(pat, x)]
done = lambda pg, n: H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= {n}", 90)
SUPP = """[...document.querySelectorAll('.dci-supp-row')].map(tr => [tr.querySelector('.dci-supp-kind').textContent.trim(),
  (tr.children[2].querySelector('strong') || tr.children[2]).textContent.trim(), tr.querySelector('input').checked, tr.children[5].textContent.replace(/\\s+/g, ' ').trim()])"""
MARKS = """(name, role) => { const g = [...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === name);
  if (!g) return null; const tr = [...g.querySelectorAll('tr.dci-row')].find(t => t.querySelector('.dci-drole').textContent.trim() === role);
  return tr ? [...tr.querySelectorAll('.dci-srcmark')].map(m => m.textContent.trim()) : 'no row'; }"""
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    # A) on request only
    bar = pg.evaluate("[...document.querySelectorAll('.dci-suppbar .dci-supp-btn')].map(b => b.textContent.trim())")
    a_ok = bar == ['＋ Bandcamp testband.bandcamp.com/album/testalbum', '＋ Text …'] and pg.evaluate("document.querySelector('[data-el=supp]').hidden") \
        and not pg.evaluate("window.__gmXhr.length") and not pg.locator('.dci-srcmark').count()
    print('A) Leiste:', bar, '| Bandcamp-Abrufe:', pg.evaluate("window.__gmXhr.length"), '| Marken:', pg.locator('.dci-srcmark').count())
    results.append(a_ok)
    # B) the list
    pg.click('[data-act=supp-load]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Supplement from Bandcamp/.test(li.textContent))", 60)
    H.wait_for(pg, "!document.querySelector('[data-el=busy]').textContent", 30)
    pg.wait_for_timeout(500)
    items = pg.evaluate(SUPP)
    summary = pg.locator('.dci-supp-head span').first.inner_text()
    hints = pg.evaluate("[...document.querySelectorAll('.dci-supp-row-entry')].map(tr => tr.children[6].textContent.replace(/\\s+/g, ' ').trim())")
    m_bass = pg.evaluate(f"({MARKS})('Bass Man', 'Bass')")
    m_keys = pg.evaluate(f"({MARKS})('Keys Guy', 'Synth')")
    print('B)', summary, '\n  ', items, '\n   Hinweise:', hints, '| Bass Man:', m_bass, '| Keys Guy:', m_keys)
    kinds = {(k, n): (sel, t) for k, n, sel, t in items}
    b_ok = kinds.get(('new role', 'Guitar Guy')) == (True, '2') and kinds.get(('new entry', 'Anna Viola')) == (True, 'all') \
        and kinds.get(('new entry', 'Test Band')) == (True, 'all') and kinds.get(('differs', 'Keys Guy'), (None, ''))[0] is False \
        and '1, 2' in kinds.get(('differs', 'Keys Guy'), (None, ''))[1] and ('not recognized', 'See you on tour.') not in kinds \
        and any(k == 'not recognized' for k, *_ in items) and summary.startswith('confirmed: 1 · new: 3 · differing: 1 · not recognized: 1') \
        and m_bass == ['DG', 'BC'] and m_keys == ['DG', 'BC ≠'] and any('suggestion: Anna Viola (violist)' in h for h in hints) \
        and any('via the Bandcamp link: Test Band' in h for h in hints)
    results.append(b_ok)
    # C) Test Band unticked, take over
    pg.evaluate("[...document.querySelectorAll('.dci-supp-row')].find(tr => tr.textContent.includes('Test Band')).querySelector('input').click()")
    pg.wait_for_timeout(200)
    pg.click('[data-act=supp-apply]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Taken over from Bandcamp: 2/.test(li.textContent))", 30)
    pg.wait_for_timeout(1500)
    m_gg = pg.evaluate(f"({MARKS})('Guitar Guy', 'Trumpet')")
    anna = pg.evaluate("[...document.querySelectorAll('section.dci-group')].filter(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Anna Viola').map(s => [s.className.match(/dci-st-(\\w+)/)[1], [...s.querySelectorAll('[data-act=name-use]')].map(b => b.textContent.trim())])")
    left = pg.evaluate(SUPP)
    print('C) Guitar Guy Trumpet:', m_gg, '| Anna Viola:', anna, '| bleibt:', [(k, n) for k, n, *_ in left])
    c_ok = m_gg == ['BC'] and anna and anna[0][0] == 'missing' and anna[0][1] == ['Anna Viola (violist)'] \
        and [(k, n) for k, n, *_ in left] == [('differs', 'Keys Guy'), ('new entry', 'Test Band'), ('not recognized', '–')]
    results.append(c_ok)
    # D) staged: the edit note
    pg.evaluate("[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Anna Viola').querySelector('[data-act=name-use]').click()")
    pg.wait_for_timeout(300)
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
    pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
    note = pg.evaluate("document.getElementById('edit-note-text').value").splitlines()
    print('D) Notiz:', [l for l in note if not l.startswith('Script')][:6])
    d_ok = note[0] == 'Source: https://www.discogs.com/release/1234' and note[1] == f'Also from: {ALBUM}' \
        and any(l.startswith('1 credit also in Bandcamp; added from Bandcamp only: Guitar Guy, trumpet (tracks 2); Anna Viola, viola (all tracks).') for l in note) \
        and any(l.startswith('Sources differ: Keys Guy, synthesizer – Discogs: 2, Bandcamp: 1, 2; kept Discogs') for l in note)
    results.append(d_ok)
    # G) a typed source that is not linked
    pg.fill('[data-f=supp-url]', 'https://www.discogs.com/release/1234')
    pg.click('[data-act=supp-url]'); pg.wait_for_timeout(400)
    same = pg.locator('.dci-msg').all_inner_texts()
    pg.fill('[data-f=supp-url]', OTHER + '?from=x')
    pg.click('[data-act=supp-url]')
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Supplement from Bandcamp/.test(li.textContent)).length >= 2", 60)
    H.wait_for(pg, "!document.querySelector('[data-el=busy]').textContent", 30)
    pg.wait_for_timeout(500)
    chip = pg.locator('.dci-supp-on').all_inner_texts()
    items_g = pg.evaluate(SUPP)
    print('G) gleiche Quelle:', [m for m in same if 'already' in m][:1], '| Chip:', chip, '| Liste:', [(k, n, t) for k, n, _, t in items_g])
    g_ok = any('That is the source loaded already.' in m for m in same) and chip and 'otherband.bandcamp.com/album/live' in chip[0] \
        and ('new role', 'Drum Guy', '3') in [(k, n, t) for k, n, _, t in items_g]
    results.append(g_ok)
    # E) delete the stored import
    pg.select_option('[data-f=discogs-pick]', 'discogs|1234')
    done(pg, 2)
    pg.wait_for_timeout(500)
    picked = pg.evaluate(f"Object.keys(JSON.parse(localStorage.getItem('dci-source-pick') || '{{}}'))")
    pg.click('[data-act=forget-open]')
    asked = pg.locator('.dci-forget strong').inner_text()
    pg.click('[data-act=forget-do]')
    done(pg, 1)
    pg.wait_for_timeout(800)
    after = pg.evaluate("localStorage.getItem('dci-source-pick')")
    first = pg.locator('#dci-log li').first.inner_text()
    print('E) gewählt vorher:', picked, '|', asked, '| nachher:', after, '| Protokoll beginnt:', first[9:80], '| Liste:',
          pg.evaluate("document.querySelector('[data-el=supp]').hidden"), '| Marken:', pg.locator('.dci-srcmark').count())
    e_ok = picked == [H.REL] and asked == 'Delete the stored import of this release?' and after is None and 'Stored import of this release deleted' in first \
        and pg.evaluate("document.querySelector('[data-el=supp]').hidden") and not pg.locator('.dci-srcmark').count() \
        and not logs(pg, 'Supplement from') and bool(logs(pg, 'Import complete'))
    results.append(e_ok)
    print('Fehler:', errs)
    results.append(not errs)
    # F) the old script on the page
    old = ctx.new_page()
    old.goto(f'https://musicbrainz.org/release/{H.REL}/edit-relationships')
    old.add_script_tag(content="const s = document.createElement('style'); s.id = 'dci-styles'; document.head.appendChild(s);")
    old.add_script_tag(content=H.MAIN)
    old.wait_for_timeout(800)
    f1 = [old.locator('#dci-twice').count(), old.locator('#dci-open').count()]
    second, _ = H.open_mb_edit(ctx, companion=False)
    second.wait_for_selector('#dci-open', timeout=20000)
    second.evaluate("const s = document.createElement('style'); s.id = 'dci-styles'; document.head.appendChild(s);")
    second.wait_for_timeout(3500)
    f2 = second.locator('#dci-twice').inner_text() if second.locator('#dci-twice').count() else ''
    print('F) zuerst das alte:', f1, '| danach:', f2[:90])
    results.append(f1 == [1, 0] and f2.startswith('Two importer scripts are running on this page'))
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
