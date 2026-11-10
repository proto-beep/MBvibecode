"""Works: the disambiguation comments of live recordings (Credits Importer 3.72.0: split off t_works_more.py, collected item Z-TST).

Cases: livecom (3.32.9), livecomrun (3.32.10), liveoffer (3.37.3), livegroup (3.38.3), liveall (3.40.13), livedate (3.62.0), livetracks (3.66.0); `python3 t_works_live.py <case> …` runs only those."""
import re
import urllib.parse
import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser


def case_livecom():
    """Credits Importer 3.32.9: disambiguation comments of live recordings – the proposals (collected item 113).
    A) ⚙ Settings → Staging: "Live recordings: add a disambiguation comment" is off – no list above "Stage …" ([3.37.3] the offer
       instead, case liveoffer); switched on (stored).
    B) The release group is Live: tracks 2–4 (planned links with "live" preselected, S021) are listed – track 1 (a link in
       MusicBrainz without "live") is not; "live: Abbey Road Studios, New York, NY, USA" (the place of "recorded at", its area
       from MusicBrainz: city, US state code, "USA"); track 3 has "live" in MusicBrainz (ticked), track 4 another comment (not
       tickable, red note).
       [3.38.3] Tracks 2 and 3 are one line "2, 3 · ▸ 2 tracks" ([Z-TRR] 3.93.0) (the same comment, item 168), ▸ shows them; the heading "▾ Live
       disambiguation comments: 2 of 3" (item 170).
    C) The place credited as "Iridium" and the matrix applied (the date 2001-03 on the place): "live, 2001‐03: Iridium, New
       York, NY, USA"; a comment changed by hand stays and says so; unticked stays unticked.
       [Z-LC] (3.40.13) The box "All" is for tracks 2 and 3 only (track 4 cannot be ticked)."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    LIST = """(() => { const el = document.querySelector('[data-el=livecom]'); if (!el || el.hidden) return null;
      return [...el.querySelectorAll('tr[data-livecom]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value,
        tr.querySelector('[data-f=livecom-on]').checked, tr.querySelector('[data-f=livecom-on]').disabled, tr.lastElementChild.textContent.replace(/\\s+/g, ' ').trim()]); })()"""
    EXPAND = """(() => { for (let k = 0; k < 20; k++) { const b = document.querySelector('[data-el=livecom] [data-act=livecom-group][aria-expanded=false]');
      if (!b) return k; b.click(); } return -1; })()"""
    GROUPS = """[...document.querySelectorAll('[data-el=livecom] tr[data-livecom-group]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
      tr.querySelector('[data-act=livecom-group]').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value, tr.querySelector('[data-f=livecom-on]').checked])"""
    ALONE = "[...document.querySelectorAll('[data-el=livecom] tr[data-livecom]:not(.dci-livecom-sub) .dci-livecom-pos')].map(x => x.textContent.trim())"
    HEAD = "(document.querySelector('[data-el=livecom] .dci-livecom-head') || {textContent: ''}).textContent.trim()"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(1000)
        a0 = pg.evaluate(LIST)
        offer0 = pg.evaluate("!!document.querySelector('[data-el=livecom] .dci-livecom-offer')")
        H.open_settings(pg, 'staging')
        sw = pg.locator('[data-el=settings] [data-set=live-comments]')
        off0 = sw.is_checked()
        sw.check()
        pg.wait_for_timeout(2500)
        stored = pg.evaluate("localStorage.getItem('dci-live-comments')")
        b0 = pg.evaluate(GROUPS), pg.evaluate(ALONE), pg.evaluate(HEAD)
        pg.evaluate(EXPAND); pg.wait_for_timeout(200)
        b1 = pg.evaluate(LIST)
        print('A) vorher:', a0, '| Angebot:', offer0, '| Schalter an?', off0, '| gespeichert:', stored)
        print('B) Gruppen:', b0, '\n  ', b1)
        ok_a = a0 == [] and offer0 and off0 is False and stored == 'true'
        base = 'live: Abbey Road Studios, New York, NY, USA'
        ok_b = b1 is not None and [x[0] for x in b1] == ['2', '3', '4'] and all(x[1] == base for x in b1) \
            and [x[2] for x in b1] == [True, True, False] and [x[3] for x in b1] == [False, False, True] and 'demo version' in b1[2][4] \
            and not pg.evaluate("!!document.querySelector('[data-el=livecom] .dci-livecom-offer')") \
            and b0[0] == [['2, 3', '▸ 2 tracks', base, True]] and b0[1] == ['4'] and b0[2] == '▾ Live disambiguation comments: 2 of 3' \
            and pg.evaluate("document.querySelector('[data-el=livecom] thead [data-all]').dataset.recs.split(',').length") == 2
        # C)
        rid = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => /Abbey Road Studios/.test(s.querySelector('.dci-gname').textContent));
          return g ? g.querySelector('tr.dci-row').dataset.row : null; })()""")
        pg.fill(f'tr[data-row="{rid}"] [data-f=credit]', 'Iridium')
        pg.locator(f'tr[data-row="{rid}"] [data-f=credit]').dispatch_event('change')
        pg.wait_for_timeout(300)
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(600)
        c1 = pg.evaluate(LIST)
        pg.fill('tr[data-livecom] [data-f=livecom-text] >> nth=0', 'live, 2001: Iridium (by hand)')
        pg.locator('tr[data-livecom] [data-f=livecom-text] >> nth=0').dispatch_event('change')
        pg.locator('tr[data-livecom] [data-f=livecom-on] >> nth=1').uncheck()
        pg.wait_for_timeout(300)
        c2 = pg.evaluate(LIST)
        print('C)', c1, '\n  ', c2)
        want = 'live, 2001‐03: Iridium, New York, NY, USA'
        ok_c = c1 and [x[1] for x in c1[:2]] == [want, want] and c2[0][1] == 'live, 2001: Iridium (by hand)' and 'changed by you' in c2[0][4] \
            and c2[1][2] is False and c2[0][2] is True
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livecomrun():
    """Credits Importer 3.32.10: disambiguation comments of live recordings – entered after "Enter edit" (collected item 113).
    A) Staged with the setting on: the job of the release holds the ticked comments (tracks 2 and 3) and the edit note – the
       script's block and "MB: QoL: Seed the batch recording comments script v2022.6.13: Seed live comments"; nothing is sent.
    B) "Enter edit" (the form of the edit note submitted): MusicBrainz has the relationships – the place credited "The Iridium"
       now (changed in the relationship editor) –: one POST to /ws/js/edit/create with two edits of type 72, "live, 2001‐03: The
       Iridium, New York, NY, USA" (MusicBrainz's credit), the edit note of the job; the log says in red what changed; a box on
       the page lists it; the job is done (a second "Enter edit" sends nothing).
    C) The release page MusicBrainz shows next: a job armed there (track 2 only, its comment changed by hand) is entered on that
       page – the hand-made comment with the new credit; "live" in MusicBrainz counts as no comment, another one is not
       overwritten (red).
    (3.66.0, collected item Z-LCP, rule S096) The box tidied up: "2 comments entered:", each comment once with its tracks
       ("“live, 2001‐03: The Iridium, New York, NY, USA” – tracks 2, 3"; before one long line of tracks and comments); on the release
       page "Not entered:" with "Track 4: MusicBrainz has another comment “demo version” – not overwritten"."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    area = {'name': 'New York', 'typeID': 3, 'containment': [{'name': 'New York', 'typeID': 2, 'primary_code': 'US-NY'},
                                                             {'name': 'United States', 'typeID': 1, 'primary_code': 'US', 'country_code': 'US'}]}

    def js_release(credit, comments):
        tracks = []
        for i, g in enumerate(H.REC):
            rels = [{'linkTypeID': 278, 'attributes': [{'typeID': 578}], 'target': {'gid': H.uid('cdcdcdcd', i + 1), 'name': H.TITLES[i]}}] if i else []
            if i:
                rels.append({'linkTypeID': 693, 'entity0_credit': credit, 'begin_date': {'year': 2001, 'month': 3, 'day': None}, 'end_date': {'year': 2001, 'month': 3, 'day': None},
                             'target': {'gid': PLACE, 'name': 'Abbey Road Studios', 'area': area}})
            tracks.append({'number': str(i + 1), 'recording': {'gid': g, 'comment': comments.get(i + 1, ''), 'relationships': rels}})
        return {'gid': H.REL, 'mediums': [{'position': 1, 'tracks': tracks}], 'releaseGroup': {'secondaryTypeIDs': [6]}}

    JOB = f"JSON.parse(localStorage.getItem('dci-live-job:{H.REL}') || 'null')"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        ctx.add_init_script("try { localStorage.setItem('dci-live-comments', 'true'); } catch (e) {}")
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        rid = pg.evaluate("""(() => { const g = [...document.querySelectorAll('section.dci-group')].find(s => /Abbey Road Studios/.test(s.querySelector('.dci-gname').textContent));
          return g ? g.querySelector('tr.dci-row').dataset.row : null; })()""")
        pg.fill(f'tr[data-row="{rid}"] [data-f=credit]', 'Iridium')
        pg.locator(f'tr[data-row="{rid}"] [data-f=credit]').dispatch_event('change')
        if pg.locator('.dci-pools-toggle').get_attribute('aria-expanded') != 'true':
            pg.click('.dci-pools-toggle'); pg.wait_for_timeout(200)
        pg.click('[data-act=dm-apply]'); pg.wait_for_timeout(600)
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(1500)
        job = pg.evaluate(JOB)
        print('A) Auftrag:', job and [(x['pos'], x['comment'], x['place']) for x in job['items']], '| Notiz endet:', job and repr(job['note'][-90:]), '| gesendet:', len(H.EDITS_POSTED))
        want = 'live, 2001‐03: Iridium, New York, NY, USA'
        ok_a = bool(job) and [(x['pos'], x['comment']) for x in job['items']] == [('2', want), ('3', want)] and job['items'][0]['place']['credit'] == 'Iridium' \
            and job['note'].endswith('\n\nMB: QoL: Seed the batch recording comments script v2022.6.13: Seed live comments') and 'MB x Vibecode' in job['note'] and not H.EDITS_POSTED
        # B) "Enter edit": the relationships saved, the place credited otherwise in the editor
        H.WS_JS_RELEASE.update(js_release('The Iridium', {3: 'live', 4: 'demo version'}))
        pg.evaluate("""(() => { const ta = document.getElementById('edit-note-text'); const f = document.createElement('form'); f.addEventListener('submit', (e) => e.preventDefault());
          ta.parentNode.insertBefore(f, ta); f.appendChild(ta); const btn = document.createElement('button'); btn.type = 'submit'; btn.className = 'submit positive';
          btn.textContent = 'Enter edit'; btn.id = 'test-enter-edit'; f.appendChild(btn); })()""")
        # (the button is below the dashboard: clicked as the page would be)
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(2500)
        posted = list(H.EDITS_POSTED)
        logs = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => [li.className, li.textContent.replace(/\\s+/g, ' ').trim()]).filter(x => /live recording|credit of|comment/i.test(x[1]))")
        notice = pg.evaluate("(() => { const n = document.getElementById('dci-livecom-notice'); return n ? n.textContent.replace(/\\s+/g, ' ').trim() : null; })()")
        groups = pg.evaluate("[...document.querySelectorAll('#dci-livecom-notice .dci-livecom-group')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())")
        print('   Gruppen:', groups)
        job2 = pg.evaluate(JOB)
        pg.evaluate("document.getElementById('test-enter-edit').click()")
        pg.wait_for_timeout(1500)
        print('B) gesendet:', posted, '\n   Protokoll:', logs, '\n   Kasten:', notice, '| erledigt:', bool(job2 and job2.get('done')), '| danach:', len(H.EDITS_POSTED))
        new = 'live, 2001‐03: The Iridium, New York, NY, USA'
        ok_b = len(posted) == 1 and [(e['edit_type'], e['to_edit'], e['comment']) for e in posted[0]['edits']] == [(72, H.REC[1], new), (72, H.REC[2], new)] \
            and posted[0]['editNote'] == job['note'] and posted[0]['makeVotable'] is False \
            and any(c == 'dci-log-error' and '“Iridium” → “The Iridium”' in t for c, t in logs) and any('Comments of 2 live recordings entered' in t for c, t in logs) \
            and notice and 'The Iridium' in notice and bool(job2 and job2.get('done')) and len(H.EDITS_POSTED) == 1 \
            and groups == ['“live, 2001‐03: The Iridium, New York, NY, USA” – tracks 2, 3'] and '2 comments entered:' in notice
        pg.close()
        # C) the release page
        H.WS_JS_RELEASE.clear()
        H.WS_JS_RELEASE.update(js_release('The Iridium', {4: 'demo version'}))
        armed = {'release': H.REL, 'at': 1, 'armedAt': 0, 'note': 'note C\n\nMB: QoL: Seed the batch recording comments script v2022.6.13: Seed live comments',
                 'items': [{'rec': H.REC[1], 'pos': '2', 'comment': 'live 2001: Iridium (by hand)', 'manual': True, 'place': {'mbid': PLACE, 'credit': 'Iridium', 'name': 'Abbey Road Studios'}},
                           {'rec': H.REC[3], 'pos': '4', 'comment': want, 'manual': False, 'place': {'mbid': PLACE, 'credit': 'Iridium', 'name': 'Abbey Road Studios'}}]}
        rp, errs2 = H.open_mb_any(ctx, f'https://musicbrainz.org/release/{H.REL}')
        rp.evaluate("(job) => { job.armedAt = Date.now(); localStorage.setItem('dci-live-job:%s', JSON.stringify(job)); }" % H.REL, armed)
        rp.reload()
        rp.wait_for_timeout(2500)
        posted3 = H.EDITS_POSTED[1:]
        notice3 = rp.evaluate("(() => { const n = document.getElementById('dci-livecom-notice'); return n ? [...n.querySelectorAll('.dci-livecom-line')].map(d => [d.className, d.textContent]) : null; })()")
        logged = rp.evaluate("JSON.parse(sessionStorage.getItem('dci-log:%s') || '[]').map(e => [e.level, e.key])" % H.REL)
        print('C) gesendet:', posted3, '\n   Kasten:', notice3, '\n   Protokoll:', logged)
        ok_c = len(posted3) == 1 and [(e['to_edit'], e['comment']) for e in posted3[0]['edits']] == [(H.REC[1], 'live 2001: The Iridium (by hand)')] \
            and posted3[0]['editNote'] == armed['note'] and notice3 and any('dci-livecom-error' in c and 'demo version' in t for c, t in notice3) \
            and ['dci-livecom-line dci-livecom-skiphead', 'Not entered:'] in notice3 and ['dci-livecom-line dci-livecom-error', 'Track 4: MusicBrainz has another comment “demo version” – not overwritten'] in notice3 \
            and ['error', 'liveOther'] in logged and ['ok', 'liveSet'] in logged
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_liveoffer():
    """Credits Importer 3.37.3: the comments of live recordings offered while the setting is off (collected item 150b).
    A) The setting off, the release group Live: above "Stage …" the offer "Tracks 2–4 are live recordings. Propose
       disambiguation comments for them (“live: Abbey Road Studios, New York, NY, USA”)?" – no list; its tooltip names
       ⚙ Settings → Staging → “Live recordings: add a disambiguation comment”.
    B) ✓: the list as with the setting on (tracks 2–4, 2 and 3 ticked – [3.38.3] one line, ▸ shows them), the setting stays off
       (not stored); the log says so;
       staged: the job of the release holds tracks 2 and 3.
    C) The page loaded again: the offer is back (for the case, not stored); ✕: no offer, no list, the log says so; the job is
       gone."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    LIST = """(() => { const el = document.querySelector('[data-el=livecom]'); if (!el || el.hidden) return null;
      return [...el.querySelectorAll('tr[data-livecom]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value,
        tr.querySelector('[data-f=livecom-on]').checked]); })()"""
    EXPAND = """(() => { for (let k = 0; k < 20; k++) { const b = document.querySelector('[data-el=livecom] [data-act=livecom-group][aria-expanded=false]');
      if (!b) return k; b.click(); } return -1; })()"""
    OFFER = """(() => { const o = document.querySelector('[data-el=livecom]:not([hidden]) .dci-livecom-offer'); return o ? [o.querySelector('span').textContent.replace(/\\s+/g, ' ').trim(), o.title,
      [...o.querySelectorAll('button')].map(b => b.textContent.trim())] : null; })()"""
    LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /Comments of live recordings/.test(t))"
    JOB = f"JSON.parse(localStorage.getItem('dci-live-job:{H.REL}') || 'null')"
    base = 'live: Abbey Road Studios, New York, NY, USA'

    def stage(pg):
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(1500)

    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        a_offer, a_list = pg.evaluate(OFFER), pg.evaluate(LIST)
        print('A) Angebot:', a_offer, '| Liste:', a_list)
        ok_a = bool(a_offer) and a_offer[0] == f'Tracks 2–4 are live recordings. Propose disambiguation comments for them (“{base}”)?' \
            and '⚙ Settings → Staging → “Live recordings: add a disambiguation comment”' in a_offer[1] and a_offer[2] == ['✓ Propose comments', '✕ Not for this release'] \
            and a_list == []
        # B) ✓
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
        pg.evaluate(EXPAND); pg.wait_for_timeout(200)
        b_list, b_offer = pg.evaluate(LIST), pg.evaluate(OFFER)
        stored = pg.evaluate("localStorage.getItem('dci-live-comments')")
        H.open_settings(pg, 'staging')
        sw_on = pg.locator('[data-el=settings] [data-set=live-comments]').is_checked()
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()')
        pg.wait_for_timeout(300)
        b_logs = pg.evaluate(LOGS)
        stage(pg)
        job = pg.evaluate(JOB)
        print('B) Liste:', b_list, '| Angebot:', b_offer, '| Einstellung:', stored, sw_on, '\n   Protokoll:', b_logs, '\n   Auftrag:', job and [(x['pos'], x['comment']) for x in job['items']])
        ok_b = b_list == [['2', base, True], ['3', base, True], ['4', base, False]] and b_offer is None and stored is None and sw_on is False \
            and any('proposed for this release' in t for t in b_logs) and bool(job) and [(x['pos'], x['comment']) for x in job['items']] == [('2', base), ('3', base)]
        # C) loaded again, ✕
        pg.reload(); pg.add_script_tag(content=H.MAIN)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        c_offer = pg.evaluate(OFFER)
        pg.click('[data-act=livecom-no]'); pg.wait_for_timeout(500)
        c_offer2, c_list, c_logs, c_job = pg.evaluate(OFFER), pg.evaluate(LIST), pg.evaluate(LOGS), pg.evaluate(JOB)
        print('C) Angebot wieder:', bool(c_offer), '| nach ✕:', c_offer2, c_list, '\n   Protokoll:', c_logs, '| Auftrag:', c_job)
        ok_c = bool(c_offer) and c_offer2 is None and c_list is None and any('not for this release' in t for t in c_logs) and c_job is None
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livegroup():
    """Credits Importer 3.38.3: the comments of live recordings in short (collected items 168, 170).
    A) Two media of two tracks, the release group Live, the setting off: the offer names the whole medium and the other track –
       "Live recordings: track 1.2, CD 2. Propose disambiguation comments for them (“live: Abbey Road Studios”)?" (the positions
       as in the list; [3.38.13] F-2: in their order, until 3.38.12 "CD 2, track 1.2").
    B) ✓: one line for the three (the same comment) – "1.2, CD 2", "▸ 3 tracks"; ▸ shows the three; its text changed: all three
       have it (each "changed by you"); unticked: all three unticked – "0 of 3".
    C) The heading "▾ Live disambiguation comments: …" is the last line of the box, at its right edge, below the list; the list at
       most a third of the dashboard's height; the heading clicked: only the heading, at the same place (bottom right), ▸;
       [3.38.13] (F-1) the heading purple with white text, open and closed (darker under the pointer)."""
    H.MEDIA = [2, 2]
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        return d

    H.ws_release = ws
    OFFER = """(() => { const o = document.querySelector('[data-el=livecom]:not([hidden]) .dci-livecom-offer'); return o ? o.querySelector('span').textContent.replace(/\\s+/g, ' ').trim() : null; })()"""
    GROUPS = """[...document.querySelectorAll('[data-el=livecom] tr[data-livecom-group]')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
      tr.querySelector('[data-act=livecom-group]').textContent.trim(), tr.querySelector('[data-f=livecom-text]').value, tr.querySelector('[data-f=livecom-on]').checked])"""
    SUBS = """[...document.querySelectorAll('[data-el=livecom] tr.dci-livecom-sub')].map(tr => [tr.querySelector('.dci-livecom-pos').textContent.trim(),
      tr.querySelector('[data-f=livecom-text]').value, tr.querySelector('[data-f=livecom-on]').checked, tr.lastElementChild.textContent.replace(/\\s+/g, ' ').trim()])"""
    BOX = """(() => { const box = document.querySelector('[data-el=livecom] .dci-livecom-box'); if (!box) return null; const h = box.querySelector('.dci-livecom-head');
      const body = box.querySelector('.dci-livecom-body'); const r = (e) => { const x = e.getBoundingClientRect(); return [Math.round(x.left), Math.round(x.top), Math.round(x.right), Math.round(x.bottom)]; };
      return { last: box.lastElementChild.contains(h), head: h.textContent.trim(), h: r(h), box: r(box), body: body ? r(body) : null, bg: getComputedStyle(h).backgroundColor, color: getComputedStyle(h).color,
        max: body ? parseFloat(body.style.maxHeight) : null, dash: Math.round(document.getElementById('dci-overlay').getBoundingClientRect().height) }; })()"""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        a = pg.evaluate(OFFER)
        print('A) Angebot:', a)
        # [3.38.13] (F-2) in the order of the positions (until 3.38.12 "CD 2, track 1.2")
        ok_a = a == 'Live recordings: track 1.2, CD 2. Propose disambiguation comments for them (“live: Abbey Road Studios”)?'
        # B)
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
        g0 = pg.evaluate(GROUPS)
        pg.click('[data-el=livecom] [data-act=livecom-group]'); pg.wait_for_timeout(200)
        s0 = pg.evaluate(SUBS)
        pg.fill('tr[data-livecom-group] [data-f=livecom-text]', 'live (all three)')
        pg.press('tr[data-livecom-group] [data-f=livecom-text]', 'Tab')
        pg.wait_for_timeout(300)
        s1 = pg.evaluate(SUBS)
        pg.locator('tr[data-livecom-group] [data-f=livecom-on]').uncheck()
        pg.wait_for_timeout(300)
        s2, g2 = pg.evaluate(SUBS), pg.evaluate(GROUPS)
        print('B) Gruppe:', g0, '\n   ▸:', s0, '\n   Text:', s1, '\n   aus:', g2, s2)
        ok_b = len(g0) == 1 and g0[0][0] == '1.2, CD 2' and g0[0][1] == '▸ 3 tracks' and g0[0][3] is True and [x[0] for x in s0] == ['1.2', '2.1', '2.2'] \
            and all(x[1] == g0[0][2] for x in s0) and all(x[1] == 'live (all three)' and 'changed by you' in x[3] for x in s1) \
            and len(g2) == 1 and g2[0][3] is False and all(x[2] is False for x in s2)
        # C) the heading
        c1 = pg.evaluate(BOX)
        pg.click('[data-el=livecom] .dci-livecom-head'); pg.wait_for_timeout(300)
        c2 = pg.evaluate(BOX)
        print('C) offen:', c1, '\n   zu:', c2)
        ok_c = bool(c1 and c2) and c1['last'] and c1['head'].startswith('▾ Live disambiguation comments: 0 of 3') and abs(c1['h'][2] - c1['box'][2]) <= 12 \
            and c1['body'] and c1['h'][1] >= c1['body'][3] - 1 and c1['max'] <= max(120, c1['dash'] / 3) + 2 \
            and c2['body'] is None and c2['head'].startswith('▸ Live disambiguation comments') and abs(c2['h'][2] - c1['h'][2]) <= 2 and abs(c2['h'][3] - c1['h'][3]) <= 2 \
            and c1['bg'] == 'rgb(115, 109, 171)' and c1['color'] == 'rgb(255, 255, 255)' and c2['bg'] in ('rgb(115, 109, 171)', 'rgb(75, 69, 133)')
        print('A)', ok_a, '| B)', ok_b, '| C)', ok_c)
        results += [ok_a, ok_b, ok_c]
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_liveall():
    """Credits Importer 3.40.13 (collected item Z-LC): one box for all live disambiguation comments.
    A) Two media of two tracks, the release group Live, ✓ proposed: a first line "All" above the list – ticked (all three are),
       its label "All live disambiguation comments".
    B) The group opened, track 2.1 unticked: "All" mixed (neither ticked nor not), "2 of 3".
    C) "All" clicked: all three ticked ("3 of 3"), not mixed; again: none ("0 of 3").
    D) (case livecom's release) a recording MusicBrainz has another comment for cannot be ticked: not among those of "All"."""
    H.MEDIA = [2, 2]
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        return d

    H.ws_release = ws
    ALL = """(() => { const x = document.querySelector('[data-el=livecom] thead tr.dci-livecom-all [data-f=livecom-on]'); if (!x) return null;
      return [x.checked, x.indeterminate, x.closest('tr').textContent.trim(), x.getAttribute('aria-label'), x.dataset.recs.split(',').length]; })()"""
    ONS = "[...document.querySelectorAll('[data-el=livecom] tbody [data-f=livecom-on]')].map(x => x.checked)"
    HEAD = "(document.querySelector('[data-el=livecom] .dci-livecom-head') || {textContent: ''}).textContent.trim()"
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
        a0 = pg.evaluate(ALL)
        print('A)', a0)
        results.append(a0 == [True, False, 'All', 'All live disambiguation comments', 3])
        pg.click('[data-el=livecom] [data-act=livecom-group]'); pg.wait_for_timeout(200)
        pg.locator('tr.dci-livecom-sub [data-f=livecom-on] >> nth=1').evaluate('x => x.click()')
        pg.wait_for_timeout(300)
        b0 = [pg.evaluate(ALL), pg.evaluate(HEAD)]
        print('B)', b0)
        results.append(b0[0] is not None and b0[0][:2] == [False, True] and b0[1].startswith('▾ Live disambiguation comments: 2 of 3'))
        pg.click('[data-el=livecom] thead [data-f=livecom-on]'); pg.wait_for_timeout(300)
        c0 = [pg.evaluate(ALL), pg.evaluate(HEAD), pg.evaluate(ONS)]
        pg.click('[data-el=livecom] thead [data-f=livecom-on]'); pg.wait_for_timeout(300)
        c1 = [pg.evaluate(ALL), pg.evaluate(HEAD), pg.evaluate(ONS)]
        print('C) an:', c0, '\n   aus:', c1)
        results.append(c0[0][:2] == [True, False] and c0[1].startswith('▾ Live disambiguation comments: 3 of 3') and all(c0[2])
                       and c1[0][:2] == [False, False] and c1[1].startswith('▾ Live disambiguation comments: 0 of 3') and not any(c1[2]))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livedate():
    """Credits Importer 3.62.0 (collected items Z-PDT, Z-LVD; rule S089): the notes say "Performed in St. Ann’s Church, Dublin, Ireland
    on February 22nd, 2018".
    A) Z-PDT: the date is in the pool as Performance (until 3.61.0 another name: "performed" was no word of Performance).
    B) Z-LVD: as the seed script takes it, the comment has only dates on relationships – "live: Abbey Road Studios, New York, NY, USA"
       before the date matrix is applied; a hint names the concert date (2018-02-22) that is on no relationship yet (none before).
    C) Rule S089 off: "live: Abbey Road Studios, New York, NY, USA" and no hint, as before."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig, orig_dg = H.ws_release, H.discogs_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        return d

    def dg():
        d = orig_dg()
        d['notes'] = 'Performed in St. Ann’s Church, Dublin, Ireland on February 22nd, 2018.'
        return d
    H.ws_release, H.discogs_release = ws, dg
    LIST = """(() => { const el = document.querySelector('[data-el=livecom]'); if (!el || el.hidden) return null;
      // (the offer above "Stage …" quotes the comment: “…”; the list once it is on)
      const m = el.textContent.match(/\\(“([^”]+)”\\)/);
      return [...new Set([...el.querySelectorAll('[data-f=livecom-text]')].map(x => x.value).concat(m ? [m[1]] : []))]; })()"""
    results = []

    def run(off):
        with sync_playwright() as p:
            b = p.chromium.launch(args=H.LAUNCH_ARGS)
            ctx = H.new_context(b)
            pg, errs = H.open_mb_edit(ctx, companion=False)
            pg.on('dialog', lambda d: d.accept())
            pg.evaluate(f"localStorage.setItem('dci-rules-off', JSON.stringify({['S083', 'S089'] if off else ['S083']}))")
            pg.wait_for_selector('#dci-open', timeout=20000)
            H.open_dashboard(pg)
            pg.wait_for_timeout(2500)
            pool = pg.evaluate("[...document.querySelectorAll('[data-el=dates] .dci-pchip-date, .dci-pchip-date')].map(c => c.textContent.replace(/\\s+/g, ' ').trim())")
            lst = pg.evaluate(LIST)
            if pg.evaluate("!!document.querySelector('[data-act=livecom-yes]')"):
                pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(500)
            hint = pg.evaluate("(() => { const el = document.querySelector('[data-el=livecom]'); return el ? el.textContent.includes('date of the concert (2018-02-22)') : null; })()")
            print('   Hinweis:', hint)
            b.close()
            return pool, lst, errs, hint

    pool, lst, errs, hint = run(False)
    print('A) Pool:', pool)
    results.append(any('Performance' in x and '2018-02-22' in x for x in pool))
    print('B)', lst)
    results.append(bool(lst) and all(x == 'live: Abbey Road Studios, New York, NY, USA' for x in lst) and hint and not errs)
    _, lst2, _, hint2 = run(True)
    print('C)', lst2)
    results.append(bool(lst2) and all(x == 'live: Abbey Road Studios, New York, NY, USA' for x in lst2) and not hint2)
    H.ws_release, H.discogs_release = orig, orig_dg
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_livetracks():
    """Credits Importer 3.66.0 (collected item Z-LCP), in Node: the tracks of a comment in short – "2", "3", "4", "6" → "2–4, 6";
    several media "1.1", "1.2", "1.3", "2.1" → "1.1–1.3, 2.1" (one medium written without it: "1–3, 1"); the same track once.
    (review) The sides of a record: "A1–A3, B1"; "1.3", "3" and "03" are one track ("3, 4" with 4 – [Z-TRR] 3.93.0: two tracks one by one), counted once."""
    import json
    import subprocess
    node = r"""
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {}, key: () => null, length: 0 };
const m = require(process.argv[1]);
console.log(JSON.stringify([m.liveTracksText(['2', '3', '4', '6', '3'], false), m.liveTracksText(['1.1', '1.2', '1.3', '2.1'], true), m.liveTracksText(['1.1', '1.2', '1.3', '2.1'], false), m.liveTracksText(['A1', '2'], false),
  m.liveTracksText(['1.A2', '1.A1', '1.A3', '1.B1', '1.3'], false), m.liveTracksText(['1.3', '3', '03', '4'], false), m.liveTracksCount(['1.3', '3', '4'])]));
"""
    o = subprocess.run(['node', '-e', node, str(H.ROOT / 'mb-vibecode-credits-importer.user.js')], capture_output=True, text=True)
    res = json.loads(o.stdout) if o.returncode == 0 else o.stderr[-300:]
    print(res)
    results = [res == ['2–4, 6', '1.1–1.3, 2.1', '1–3, 1', '2, A1', '3, A1–A3, B1', '3, 4', 2]]
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_live3108():
    """Credits Importer 3.108.0 (collected item Z-LIVE2): the disambiguation comments forgotten at the first staging can still be
    switched on afterwards (until 3.107.0 a staging without ticked comments wrote no job, and ticking them later changed nothing).
    A) The setting off, the offer not answered, staged: no job; then ✓ on the dashboard – the job holds tracks 2 and 3.
    B) The setting on: before any staging, ticking makes no job; all unticked and staged: no job; ticked again afterwards – the job
       holds tracks 2 and 3 and the log says "saved" once; unticked again – the job is gone.
    C) The setting switched on in ⚙ Settings after a staging with it off: the job is there."""
    PLACE = H.COMPANIES[1002][1]
    NYC, NYS, US = H.uid('abababab', 1), H.uid('abababab', 2), H.uid('abababab', 3)
    H.PLACE_AREAS[PLACE] = NYC
    H.AREA_INFO.update({NYC: {'name': 'New York', 'type': 'City', 'parent': NYS}, NYS: {'name': 'New York', 'type': 'Subdivision', 'iso2': ['US-NY'], 'parent': US},
                        US: {'name': 'United States', 'type': 'Country', 'iso1': ['US']}})
    orig = H.ws_release

    def ws(full=False):
        d = orig(full)
        d['release-group']['secondary-types'] = ['Live']
        for m in d['media']:
            for t in m['tracks']:
                if t['position'] == 3:
                    t['recording']['disambiguation'] = 'live'
                if t['position'] == 4:
                    t['recording']['disambiguation'] = 'demo version'
        return d

    H.ws_release = ws
    JOB = f"JSON.parse(localStorage.getItem('dci-live-job:{H.REL}') || 'null')"
    ITEMS = f"(() => {{ const j = JSON.parse(localStorage.getItem('dci-live-job:{H.REL}') || 'null'); return j ? j.items.map(x => x.pos) : null; }})()"
    TICK = """(on) => { let n = 0; document.querySelectorAll('[data-el=livecom] tr[data-livecom-group] [data-f=livecom-on], [data-el=livecom] tr[data-livecom]:not(.dci-livecom-sub) [data-f=livecom-on]').forEach(el => {
      if (el.disabled || el.checked === on) return; el.checked = on; el.dispatchEvent(new Event('change', { bubbles: true })); n++; }); return n; }"""
    SAVED = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim()).filter(t => /saved for .Enter edit.|after .Enter edit./i.test(t)).length"

    def stage(pg):
        pg.click('[data-act=apply]'); pg.wait_for_timeout(3000)
        pg.evaluate("document.querySelectorAll('.dci-subdlg button').forEach(b => { if (/^no$|nein|not now/i.test(b.textContent.trim())) b.click(); })")
        pg.wait_for_timeout(1500)

    def opened(ctx):
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        pg.wait_for_timeout(2500)
        return pg, errs

    results, errs_all = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        # A) the offer answered after the staging
        ctx = H.new_context(b)
        pg, errs = opened(ctx)
        offer = pg.locator('[data-act=livecom-yes]').count()
        stage(pg)
        a0 = pg.evaluate(JOB)
        pg.click('[data-act=livecom-yes]'); pg.wait_for_timeout(600)
        a1 = pg.evaluate(ITEMS)
        print('A) Angebot:', offer, '| nach Staging:', a0, '| nach ✓:', a1)
        ok_a = offer == 1 and a0 is None and a1 == ['2', '3']
        errs_all += errs
        ctx.close()
        # B) the setting on, all unticked at the staging
        ctx = H.new_context(b)
        ctx.add_init_script("try { localStorage.setItem('dci-live-comments', 'true'); } catch (e) {}")
        pg, errs = opened(ctx)
        n_off = pg.evaluate(TICK, False); pg.wait_for_timeout(300)
        n_on = pg.evaluate(TICK, True); pg.wait_for_timeout(300)
        b0 = pg.evaluate(JOB)
        pg.evaluate(TICK, False); pg.wait_for_timeout(300)
        stage(pg)
        b1 = pg.evaluate(JOB)
        saved0 = pg.evaluate(SAVED)
        pg.evaluate(TICK, True); pg.wait_for_timeout(600)
        b2 = pg.evaluate(ITEMS)
        saved1 = pg.evaluate(SAVED)
        pg.evaluate(TICK, False); pg.wait_for_timeout(600)
        b3 = pg.evaluate(JOB)
        print('B) aus/an:', n_off, n_on, '| vor Staging:', b0, '| nach Staging:', b1, '| angehakt:', b2, '| Protokoll:', saved0, saved1, '| wieder aus:', b3)
        ok_b = n_off >= 1 and n_on >= 1 and b0 is None and b1 is None and b2 == ['2', '3'] and saved1 == saved0 + 1 and b3 is None
        errs_all += errs
        ctx.close()
        # C) the setting switched on after the staging
        ctx = H.new_context(b)
        pg, errs = opened(ctx)
        stage(pg)
        c0 = pg.evaluate(JOB)
        H.open_settings(pg, 'staging')
        pg.locator('[data-el=settings] [data-set=live-comments]').check(); pg.wait_for_timeout(800)
        c1 = pg.evaluate(ITEMS)
        print('C) nach Staging:', c0, '| Einstellung an:', c1)
        ok_c = c0 is None and c1 == ['2', '3']
        errs_all += errs
        b.close()
    print('A)', ok_a, '| B)', ok_b, '| C)', ok_c, '| Fehler:', errs_all)
    results += [ok_a, ok_b, ok_c, not errs_all]
    H.ws_release = orig
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
