"""Works matrix: a date dropped onto a cell with a relationship already in MusicBrainz without a date is added to
it as an edit (× takes it back before staging; a date MusicBrainz already has stays); the edit note says so.
Release page: credits of works that were new in the editor (no MBID yet) are found through their recording,
also when the dashboard showed them as staged (●)."""
import re
from playwright.sync_api import sync_playwright
import harness as H
from common_rows import drag

PW = sync_playwright().start()
results = []
WRITER_W = H.ARTISTS[3007][0]
WRITER_Z = H.ARTISTS[3009][0]


def open_mb(companion=False):
    b = PW.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    dg = None
    if companion:
        dg, _ = H.open_discogs(ctx)
    pg, errs = H.open_mb_edit(ctx, companion=companion)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    pg.wait_for_timeout(500)
    return b, pg, dg, errs


# --- E) dates for relationships already in MusicBrainz ------------------------------------------------------
b, pg, _, errs = open_mb()
# the relationship editor knows the existing composer relationship of Writer W on work 1 (no date)
pg.evaluate(f"""() => {{ const re = MB.relationshipEditor;
  re.state = {{ ...re.state, existingRels: [{{ id: 9001, linkTypeID: 168, entity0: {{ gid: '{WRITER_W}', entityType: 'artist', id: 3007, name: 'Writer W' }},
    entity1: {{ gid: '{H.WORK1}', entityType: 'work', id: 7001, name: 'x' }}, begin_date: null, end_date: null, ended: false,
    attributes: null, entity0_credit: '', entity1_credit: '', _status: 0 }}] }}; }}""")
ww = '.dci-mx-cell[data-col="k:a15"][data-mrow^="w:0"]'
pg.click(f'{ww} [data-act=mx-cell]'); pg.wait_for_timeout(200)          # the Discogs writer off: only MB's composer is left
date = pg.evaluate("[...document.querySelectorAll('.dci-pools-body .dci-pchip-date')].find(c => c.textContent.includes('Performance 1 ·')).dataset.id")
drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
fill = re.sub(r'\s+', ' ', pg.locator(f'{ww} .dci-mx-fill').inner_text()) if pg.locator(f'{ww} .dci-mx-fill').count() else ''
print('E1) grüne Zelle (nur MB-Composer) – geplant:', fill, '| data-fill:', pg.locator(ww).get_attribute('data-fill'))
ok_e1 = '2001-03-01' in fill and pg.locator(f'{ww} [data-act=mx-fill-remove]').count() == 1
pg.click(f'{ww} [data-act=mx-fill-remove]'); pg.wait_for_timeout(150)
gone = pg.locator(f'{ww} .dci-mx-fill').count() == 0
drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
print('    × nimmt es zurück:', gone)
ok_e1 = ok_e1 and gone
# staging: the existing relationship is changed (date, status "edited"), the edit note says so
pg.click('[data-act=apply]'); pg.wait_for_timeout(3500)
pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
st = pg.evaluate("(() => { const r = MB.relationshipEditor.state.added.find(x => x.id === 9001); return r && [r.begin_date, r.end_date, r._status]; })()")
note = pg.locator('#edit-note-text').input_value()
msgs = [m[:100] for m in pg.locator('.dci-msg').all_inner_texts() if 'existing relationship' in m]
staged_fill = re.sub(r'\s+', ' ', pg.locator(f'{ww} .dci-mx-fill').inner_text()) if pg.locator(f'{ww} .dci-mx-fill').count() else ''
print('E2) im Editor:', st, '| Meldung:', msgs, '| Zelle:', staged_fill)
print('    Bearbeitungsnotiz:', [l for l in note.split('\n') if 'existing' in l or 'Dates' in l])
ok_e2 = st and st[0] == {'year': 2001, 'month': 3, 'day': 1} and st[1] and st[1].get('day') == 3 and st[2] == 2 \
    and 'added dates to 1 existing relationship without a date' in note and '✓' in staged_fill and any('Date added to 1 existing' in m for m in msgs)
# a second "Stage" does not change it again
n_before = pg.evaluate("window.__dispatched.filter(a => a.oldRelationshipState && a.oldRelationshipState.id === 9001).length")
pg.click('[data-act=apply]') if pg.locator('[data-act=apply]:not([disabled])').count() else None
pg.wait_for_timeout(1500)
n_after = pg.evaluate("window.__dispatched.filter(a => a.oldRelationshipState && a.oldRelationshipState.id === 9001).length")
print('    zweites „Übernehmen“: Änderungen an der Beziehung', n_before, '→', n_after)
ok_e2 = ok_e2 and n_before == n_after == 1
results += [ok_e1, ok_e2]
print('Fehler E:', errs)
b.close()

# a date MusicBrainz already has stays: the cell says so
orig_ws = H.ws_release


def ws_dated():
    d = orig_ws()
    rel = d['media'][0]['tracks'][0]['recording']['relations'][0]['work']['relations'][0]
    rel['begin'] = '1970'
    rel['end'] = '1970'
    return d


H.ws_release = ws_dated
b, pg, _, errs = open_mb()
pg.click(f'{ww} [data-act=mx-cell]'); pg.wait_for_timeout(200)
date = pg.evaluate("document.querySelector('.dci-pools-body .dci-pchip-date').dataset.id")
drag(pg, f'.dci-pools-body .dci-pchip-date[data-id="{date}"] .dci-chip-main', ww)
m = [x[:120] for x in pg.locator('.dci-msg').all_inner_texts() if 'with a date' in x]
print('E3) MB-Beziehung hat schon ein Datum:', m, '| geplant:', pg.locator(f'{ww} .dci-mx-fill').count())
results.append(len(m) == 1 and pg.locator(f'{ww} .dci-mx-fill').count() == 0)
H.ws_release = orig_ws
b.close()

# --- D) release page: credits of a work that was new in the editor --------------------------------------------
H.MB_EXTRA.clear()
b, pg, dg, errs = open_mb(companion=True)
H.wait_for(pg, "document.querySelector('[data-el=sync]').textContent.includes('connected')", 20)
pg.click('tr[data-work="2"] [data-act=work-pending]'); pg.wait_for_timeout(400)   # track 3: a new work in the editor
pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
pg.wait_for_timeout(1500)
# (the Discogs page of the test has no line for Writer Z, so the status the companion keeps is looked at)
z = lambda: [(i['status'], i.get('note')) for i in (H.STORE.data.get('statusMap') or {}).get('items', []) if i['artistId'] == 3009]
print('D1) nach Übernehmen – Writer Z:', z())
H.submit_staged(pg)
NEW = H.uid('cccccccc', 33)
link = lambda rels: {'target-type': 'work', 'type': 'performance', 'type-id': H.LTS[278]['gid'], 'attributes': [],
                     'work': {'id': NEW, 'title': 'Song Three', 'relations': rels}}
# the link of the new work is still an open edit: not part of the release yet
pg.goto(f'https://musicbrainz.org/release/{H.REL}')
H.with_companion(pg)
dg.wait_for_timeout(6000)
open_edit = z()
print('D2) Link noch offen – Writer Z:', open_edit)
pr = pg
pr.close()
# applied: MusicBrainz made the work (new MBID) with its composer
H.MB_EXTRA[H.REC[2]] = [link([{'target-type': 'artist', 'type': 'composer', 'type-id': H.LTS[168]['gid'], 'attributes': [],
                              'artist': {'id': WRITER_Z, 'name': 'Writer Z'}}])]
dg.wait_for_timeout(9000)
pr, _ = H.open_mb_release(dg.context)
dg.wait_for_timeout(6000)
done = z()
items = [(i['role'], i['status'], i.get('note'), i.get('mb')) for i in H.STORE.data['statusMap']['items'] if i['artistId'] == 3009]
print('D3) Werk angelegt – Writer Z:', done, '| Einträge:', items)
results.append(open_edit == [('pending', '0/1')] and done == [('mb', '')] and items and items[0][3].get('r') and not items[0][3].get('t'))
print('Fehler D:', errs)
b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
PW.stop()
