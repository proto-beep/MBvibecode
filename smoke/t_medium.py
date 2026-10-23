"""Credits Importer 3.21.4: credits for a medium the release does not have (collected item 39; S026, T035), "Translated by" in
Bandcamp credits (33h; Q007), the reasons of the lines left out on purpose.
A release of Digital Media with a Bandcamp album whose credits name vinyl mastering, a lacquer cut and a translation.
A) Left out (no entry, no row), each with its reason in "… left out on purpose": "Vinyl LP mastering by Sean Price at
   Misery Loves Co." (also the studio, which is only for the vinyl), "Mastered by Max Vinyl (vinyl)", "Lacquer cut by Lou
   Lacquer", "Vinyl master: Vic Master". "Vinyl LP mastering and digital mastering by Dana Digital at Sound House": Dana
   Digital keeps the digital mastering (without "digital" as role credit), Sound House stays.
B) "Translated by Ana Ruiz" (Bandcamp): no type until chosen, the question offers liner notes (suggested) and translator
   (lyrics); liner notes puts it on the release.
C) The reasons: "Thanks Mom." – thanks; the vinyl lines – "for Vinyl LP – this release: Digital Media"."""
from playwright.sync_api import sync_playwright
import harness as H

H.attr(9120, 'trumpet', 14, 14)
H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
ALBUM = 'https://testband.bandcamp.com/album/testalbum'
CREDITS = """Vinyl LP mastering by Sean Price at Misery Loves Co.
Vinyl LP mastering and digital mastering by Dana Digital at Sound House
Mastered by Max Vinyl (vinyl)
Lacquer cut by Lou Lacquer
Vinyl master: Vic Master
Translated by Ana Ruiz
Trumpet: Peter Evans
Thanks Mom."""
H.BC_PAGES[ALBUM] = H.bc_page({'artist': 'Test Band', 'current': {'title': 'Testalbum', 'credits': CREDITS, 'about': '', 'release_date': '01 Jan 2020 00:00:00 GMT'},
                               'trackinfo': [{'track_num': i + 1, 'title': t, 'title_link': f'/track/song-{i + 1}', 'duration': 180.0} for i, t in enumerate(H.TITLES)]})
for i, t in enumerate(H.TITLES):
    H.BC_PAGES[f'https://testband.bandcamp.com/track/song-{i + 1}'] = H.bc_page({'current': {'title': t, 'credits': ''}})
orig_ws = H.ws_release


def ws(full=False):
    d = orig_ws(full)
    d['relations'] = [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': ALBUM}}]
    for m in d['media']:
        m['format'] = 'Digital Media'
    return d


H.ws_release = ws
ROWS = """(() => Object.fromEntries([...document.querySelectorAll('section.dci-group')].map(g => [g.querySelector('.dci-gname strong').textContent.trim(),
  [...g.querySelectorAll('tr.dci-row')].map(tr => { const t = tr.querySelector('[data-f=type]'); const c = tr.querySelector('[data-f=role-credit]');
    const lv = tr.querySelector('.dci-c-level [aria-pressed=true]');
    return [tr.querySelector('.dci-drole').textContent.trim(), t ? (t.options[t.selectedIndex] || {}).text : '', c ? c.value : '',
      (tr.querySelector('.dci-type-ask') || { textContent: '' }).textContent.replace(/\\s+/g, ' ').trim(), lv ? lv.textContent.trim() : '']; })])))()"""
IGN = "[...document.querySelectorAll('.dci-ignored li')].map(li => [li.querySelector('.dci-ign-text').textContent, (li.querySelector('.dci-ign-why') || {}).textContent || ''])"
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
    pg.wait_for_timeout(800)
    src = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').slice(0, 60)")
    g = pg.evaluate(ROWS)
    for k, v in g.items():
        print('   ', k, v)
    ign = pg.evaluate(IGN)
    print('   ausgelassen:', ign)
    logs = [x[9:] for x in pg.locator('#dci-log li').all_inner_texts() if 'left out' in x]
    print('   Protokoll:', logs)
    # A)
    gone = [n for n in ('Sean Price', 'Misery Loves Co.', 'Max Vinyl', 'Lou Lacquer', 'Vic Master') if n in g]
    dana = g.get('Dana Digital') or []
    ok_a = 'Bandcamp' in src and not gone and len(dana) == 1 and dana[0][1] == 'mastering' and dana[0][2] == '' and 'Sound House' in g \
        and 'Peter Evans' in g and len(logs) == 6
    print('A) Quelle:', src, '| noch da:', gone, '| Dana Digital:', dana, '| Sound House:', 'Sound House' in g, ok_a)
    # B)
    ana = (g.get('Ana Ruiz') or [['', '', '', '', '']])[0]
    sec = "[...document.querySelectorAll('section.dci-group')].find(s => s.querySelector('.dci-gname strong').textContent.trim() === 'Ana Ruiz')"
    opts = pg.evaluate(f"(() => {{ const s = {sec}; return s ? [...s.querySelectorAll('.dci-type-ask [data-act=type-pick]')].map(b => [b.textContent.replace(/\\s+/g, ' ').trim(), b.classList.contains('dci-type-sugg')]) : []; }})()")
    if opts:
        pg.evaluate(f"{sec}.querySelector('.dci-type-ask [data-act=type-pick][data-opt=\"0\"]').click()")
        pg.wait_for_timeout(500)
    after = (pg.evaluate(ROWS).get('Ana Ruiz') or [['']])[0]
    print('B) Ana Ruiz:', ana[:2], ana[3][:90], '| Wahl:', opts, '| nach „liner notes“:', after[:3], after[4])
    ok_b = ana[1] in ('Choose type …', '') and 'mostly the translation of the liner notes' in ana[3] \
        and opts == [['liner notes suggested', True], ['translator (lyrics)', False]] and after[1] == 'liner notes' and after[2] == 'translation' and after[4] == 'Release'
    # C)
    why = dict(ign)
    ok_c = why.get('Thanks Mom.') == '– thanks' \
        and why.get('Vinyl LP mastering by Sean Price at Misery Loves Co.') == '– for Vinyl LP – this release: Digital Media' \
        and why.get('Mastered by Max Vinyl (vinyl)') == '– for vinyl – this release: Digital Media' \
        and why.get('Lacquer cut by Lou Lacquer') == '– for lacquer cut – this release: Digital Media' \
        and why.get('Vinyl LP mastering and digital mastering by Dana Digital at Sound House') == '– for Vinyl LP – this release: Digital Media' \
        and why.get('Vinyl master: Vic Master') == '– for Vinyl – this release: Digital Media'
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
    results += [ok_a, ok_b, ok_c]
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
