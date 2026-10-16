"""Works matrix: ✕ takes a column out (its rows on "Skip", the column stays folded, a click brings it back; MB-only
columns are only folded); the column date also plans dates for the column's relationships that MusicBrainz has
without a date (also in a column "only in MusicBrainz"), clearing it takes them back. "Directed By" is asked:
conductor, chorus master, creative direction or miscellaneous support (task "director"), nothing assumed."""
import re
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import drag

LYRIC = H.uid('dddddddd', 50)
H.lt(158, '91fa6e73-0b22-4f35-a9ab-8a7d1e8c7b02', 'chorus master', 'artist', 'recording', (1,))
H.lt(927, 'df4b4d3e-0b5c-4f8e-9a7b-1c2d3e4f5a60', 'conductor', 'artist', 'recording', (1,))
H.lt(146, '0e2d1e4b-1d3a-4f7e-8f2c-6a5b4c3d2e10', 'creative direction', 'artist', 'release', (1,))
H.lt(1130, 'b367fae0-c4b0-48b9-a40c-f3ae4c02cf10', 'misc', 'artist', 'recording', (1150,))
H.LINKED['link_type'] = {str(k): v for k, v in H.LTS.items()}
orig_rel, orig_ws = H.discogs_release, H.ws_release


def rel():
    d = orig_rel()
    d['extraartists'].append({'name': 'Keys Guy', 'anv': '', 'role': 'Directed By', 'tracks': '', 'id': 3003, 'join': ''})
    return d


def ws():
    d = orig_ws()
    work = d['media'][0]['tracks'][0]['recording']['relations'][0]['work']
    # a lyricist MusicBrainz knows but Discogs does not name: a column "only in MusicBrainz"
    work['relations'] = work['relations'] + [{'target-type': 'artist', 'type': 'lyricist', 'type-id': H.LTS[165]['gid'], 'attributes': [],
                                              'artist': {'id': LYRIC, 'name': 'Lyric Only'}}]
    return d


H.discogs_release, H.ws_release = rel, ws
results = []
with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)

    # A) "Directed By": please choose; nothing staged until then
    row = lambda: pg.locator('tr.dci-row').filter(has=pg.locator('.dci-drole', has_text='Directed By')).first
    typ = lambda: row().locator('[data-f=type]').evaluate("s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text : ''")
    ask = re.sub(r'\s+', ' ', row().locator('.dci-type-ask').inner_text())
    planned = lambda: pg.evaluate("[...document.querySelectorAll('[data-status]')].length") and row().locator('.dci-status').inner_text()
    print('A1) Directed By:', ask[:160], '| Typ:', typ(), '| Status:', planned()[:60], '| Regeln:', row().locator('.dci-ruleid').all_inner_texts())
    ok_a = 'please choose' in ask and typ().startswith('Choose') and 'Q003' in row().locator('.dci-ruleid').all_inner_texts()
    picks = []
    for label in ['chorus master', 'creative direction', 'miscellaneous support']:
        row().locator('[data-act=type-pick]', has_text=label).click(); pg.wait_for_timeout(200)
        rc = row().locator('[data-f=role-credit]').input_value() if row().locator('[data-f=role-credit]').count() else ''
        picks.append((typ(), row().get_attribute('class').split('dci-lv-')[1].split()[0], rc, row().locator('.dci-type-ask [aria-pressed=true]').inner_text()))
    print('A2) gewählt:', picks)
    ok_a = ok_a and picks[0][:2] == ('chorus master', 'recording') and picks[1][:2] == ('creative direction', 'release') \
        and picks[2][0] == 'misc' and picks[2][2] == 'director' and 'miscellaneous support' in picks[2][3]
    results.append(ok_a)

    # B) take a column out and back
    WK = pg.evaluate("[...document.querySelectorAll('[data-colhead]')].find(h => h.textContent.includes('Writer W')).dataset.colhead")
    writer_rows = lambda: pg.evaluate("""[...document.querySelectorAll('.dci-group')].filter(g => (g.querySelector('.dci-gname') || {textContent: ''}).textContent.includes('Writer W'))
      .flatMap(g => [...g.querySelectorAll('tr.dci-row')]).map(tr => (tr.className.match(/dci-lv-(\\w+)/) || [])[1])""")
    before = writer_rows()
    pg.click(f'[data-colhead="{WK}"] [data-act=mx-col-remove]'); pg.wait_for_timeout(300)
    out = writer_rows()
    stub = pg.locator('th.dci-mx-removed [data-act=mx-col-restore]')
    stub_title = stub.get_attribute('title') if stub.count() else ''
    print('B1) Writer W Ebenen vorher:', before, '| nach ✕:', out, '| Spalte:', stub_title)
    stub.click(); pg.wait_for_timeout(300)
    back = writer_rows()
    print('    zurückgeholt:', back, '| Spaltenkopf wieder da:', pg.locator(f'[data-colhead="{WK}"]').count())
    # (work-level rows live in the works matrix; in the list they show only while skipped)
    ok_b = before == [] and out == ['skip'] and 'Writer W' in stub_title and back == [] and pg.locator(f'[data-colhead="{WK}"]').count() == 1
    mbcol = f'mb:{LYRIC}'
    pg.click(f'[data-colhead="{mbcol}"] [data-act=mx-col-remove]'); pg.wait_for_timeout(200)
    folded = pg.locator(f'th.dci-mx-collapsed [data-act=mx-collapse][data-col="{mbcol}"]').count()
    print('B2) Spalte „nur in MusicBrainz“ ✕ → eingeklappt:', folded)
    ok_b = ok_b and folded == 1
    pg.click(f'[data-act=mx-collapse][data-col="{mbcol}"]'); pg.wait_for_timeout(200)
    results.append(ok_b)

    # C) column dates for relationships already in MusicBrainz without a date
    date = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-date')].find(c => c.textContent.includes('Performance 1 ·')).dataset.id")
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'[data-colhead="{WK}"] .dci-mx-card')
    w0 = f'.dci-mx-cell[data-col="{WK}"][data-mrow^="w:0"] .dci-mx-fill'
    f1 = [re.sub(r'\s+', ' ', x) for x in pg.locator(w0).all_inner_texts()]
    drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', f'[data-colhead="{mbcol}"] .dci-mx-card')
    f2 = [re.sub(r'\s+', ' ', x) for x in pg.locator(f'.dci-mx-cell[data-col="{mbcol}"][data-mrow^="w:0"] .dci-mx-fill').all_inner_texts()]
    print('C1) Spaltendatum Writer W → bestehender Composer:', f1, '| Spalte nur in MB → Lyricist:', f2)
    # clearing the column date takes back what it planned (its fields are in the ▾ menu)
    pg.click(f'[data-colhead="{mbcol}"] [data-act=mx-colmenu]'); pg.wait_for_timeout(300)
    yb = pg.locator(f'[data-colhead="{mbcol}"] [data-f=cd-by]')
    yb.fill(''); yb.dispatch_event('input'); pg.wait_for_timeout(200)
    for f in ('cd-bm', 'cd-bd', 'cd-ey', 'cd-em', 'cd-ed'):
        x = pg.locator(f'[data-colhead="{mbcol}"] [data-f={f}]')
        if x.count():
            x.fill(''); x.dispatch_event('input')
    pg.wait_for_timeout(200)
    ended = pg.locator(f'[data-colhead="{mbcol}"] [data-f=cd-ended]')
    if ended.count() and ended.is_checked():
        ended.uncheck()
    pg.wait_for_timeout(300)
    f3 = pg.locator(f'.dci-mx-cell[data-col="{mbcol}"][data-mrow^="w:0"] .dci-mx-fill').count()
    print('    Spaltendatum geleert → geplant:', f3)
    ok_c = len(f1) == 1 and 'composer' in f1[0] and '2001-03-01' in f1[0] and len(f2) == 1 and 'lyricist' in f2[0] and f3 == 0
    # staging: the existing composer gets the date (the editor knows it)
    pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
      re.state = {{ ...re.state, existingRels: [{{ id: 9001, linkTypeID: 168, entity0: {{ gid: '{H.ARTISTS[3007][0]}', entityType: 'artist', id: 3007, name: 'Writer W' }},
        entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'x' }}, begin_date: null, end_date: null, ended: false,
        attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
    pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
    st = pg.evaluate("(() => { const r = MB.relationshipEditor.state.added.find(x => x.id === 9001); return r && [r.begin_date, r._status]; })()")
    print('C2) im Editor:', st)
    ok_c = ok_c and st and st[0] == {'year': 2001, 'month': 3, 'day': 1} and st[1] == 2
    results.append(ok_c)
    print('Fehler:', errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
