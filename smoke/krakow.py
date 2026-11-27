"""[3.233.0] The box "Kraków 2018" (Barry Guy and Friends, Not Two Records MW1031-2; five CDs, also a digital release) as test data: Discogs
25163152, its Bandcamp album, the back of the box as a text and MusicBrainz as on 2026-11-27 (both releases share their 18 recordings; the artist
credit of track 4.5 as corrected that day). Discogs has the performers of each track (mostly without instruments), the places of its headings and
the dates of its notes; Bandcamp the instruments in its track titles ("Lopez dr// Mazur, el-b // Pursglove, tp") and the lineup of the last piece
as its credits. The data: smoke/data/krakow2018.json (the target – who plays what on which track – in "target").

    import krakow as K
    K.setup('A')            # the CD with Discogs as its source; 'B': the digital release with Bandcamp
    out = K.run(p, 'A')     # imported (and the added source – supp: 'bandcamp' | 'discogs' | 'text'), the rows and what was compared
"""
import json
import os

import harness as H

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'data', 'krakow2018.json'), encoding='utf-8'))
INSTR = ['trumpet', 'percussion', 'cymbal', 'violin', 'baroque violin', 'bass guitar', 'reed trumpet', 'electric bass']
# Kraków, Lesser Poland, Poland – the area of the three places
KRK, MAL, PL = H.uid('abababab', 31), H.uid('abababab', 32), H.uid('abababab', 33)


def gid_of(did):
    """The MusicBrainz id of a person of Discogs (its own where MusicBrainz has one in the data)."""
    _n, gid, _m = D['people'][str(did)]
    return gid or H.uid('dddddddd', 700 + int(did) % 100)


def setup(direction, live=False, people=None, discogs=None):
    """The harness as MusicBrainz, Discogs and Bandcamp have the box: 'A' the CD (Discogs linked), 'B' / 'C' the digital release (Bandcamp
    linked). live: the release group "Live". people: more people of Discogs {id: (Discogs name, MB name)}; discogs: a function changing the
    answer of Discogs (a copy)."""
    for k, n in enumerate(INSTR):
        if not any(a['name'] == n for a in H.ATTRS.values()):
            H.attr(9600 + k, n, 14, 14)
    H.LINKED['link_attribute_type'] = {str(k): v for k, v in H.ATTRS.items()}
    H.ARTISTS.clear()
    for did in D['people']:
        H.ARTISTS[int(did)] = (gid_of(did), D['people'][did][2])
    for did, (_dn, mbname) in (people or {}).items():
        H.ARTISTS[int(did)] = (H.uid('dddddddd', 800 + int(did) % 100), mbname)
    H.COMPANIES.clear()
    for did, (et, _gid, name, area) in D['companies'].items():
        g = H.uid('eeeeeeee', 800 + int(did) % 100)
        H.COMPANIES[int(did)] = (et, g, name)
        if area:
            H.PLACE_AREAS[name] = 'Kraków'
            H.PLACE_AREAS[g] = KRK
    H.AREA_INFO.update({KRK: {'name': 'Kraków', 'type': 'City', 'parent': MAL}, MAL: {'name': 'Lesser Poland', 'type': 'Subdivision', 'iso2': ['PL-12'], 'parent': PL},
                        PL: {'name': 'Poland', 'type': 'Country', 'iso1': ['PL']}})
    rel = json.loads(json.dumps(D['discogs']))
    if discogs:
        discogs(rel)
    H.DISCOGS_ID = rel['id']
    H.DG_API[f"/releases/{rel['id']}"] = rel
    H.REL_TITLE = 'Kraków 2018'
    cd = direction == 'A'
    H.TITLES[:] = D['mb']['titles_cd'] if cd else D['mb']['titles_digital']
    H.REC[:] = D['mb']['recordings']
    H.MEDIA = D['mb']['media']
    H.MEDIA_FORMAT = 'CD' if cd else 'Digital Media'
    gid = {D['people'][d][2]: gid_of(d) for d in D['people']}
    gid.update(D['mb']['groups'])
    H.RELEASE_AC[:] = [(gid['Barry Guy'], 'Barry Guy', 'Barry Guy', ' and Friends')]
    H.RELEASE_LABELS[:] = [(H.uid('eeeeeeee', 801), 'Not Two Records', 'MW1031-2')]
    bc = D['bandcamp']
    H.BC_PAGES[bc['url']] = H.bc_page({'artist': 'Barry Guy', 'current': {'title': bc['title'], 'credits': bc['credits'], 'about': bc['about']},
                                       'packages': [], 'trackinfo': [{'track_num': i + 1, 'title': t, 'duration': float(s)} for i, (t, s) in enumerate(bc['tracks'])]},
                                      band='Not Two Records')

    def ws(full=False):
        tracks = []
        for i, g in enumerate(H.REC):
            names, joins = D['mb']['track_ac'][i]
            ac = [{'name': n, 'joinphrase': j, 'artist': {'id': gid[n], 'name': n}} for n, j in zip(names, joins)]
            tracks.append({'position': i + 1, 'number': str(i + 1), 'title': H.TITLES[i], 'artist-credit': ac,
                           'recording': {'id': g, 'title': H.TITLES[i], 'relations': [], 'artist-credit': ac}})
        rels = ([{'target-type': 'url', 'type': 'discogs', 'url': {'resource': f"https://www.discogs.com/release/{rel['id']}"}}] if cd else
                [{'target-type': 'url', 'type': 'purchase for download', 'url': {'resource': bc['url']}},
                 {'target-type': 'url', 'type': 'free streaming', 'url': {'resource': bc['url']}}])
        media = H.split_media(tracks, 'title')
        return {'id': H.REL, 'title': H.REL_TITLE, 'date': '2022-11' if cd else '2026-11-21', 'text-representation': {'language': 'zxx'},
                'release-group': {'id': H.RG, 'title': 'Kraków 2018', 'relations': [], **({'secondary-types': ['Live']} if live else {})},
                'artist-credit': [{'name': x[2], 'joinphrase': x[3], 'artist': {'id': x[0], 'name': x[1]}} for x in H.RELEASE_AC],
                'label-info': [{'catalog-number': x[2], 'label': {'id': x[0], 'name': x[1]}} for x in H.RELEASE_LABELS],
                'relations': rels, 'media': media if full else [H.trim_medium(m) for m in media]}
    H.ws_release = ws
    # (the state and the short form of tracks for the cases)
    H.MAIN = H.MAIN.replace('  const S = {', '  window.__tracksShort = (r) => tracksShort(r);\n  const S = window.__S = {', 1)


ROWS = """window.__S.rows.map(r => ({
  name: (window.__S.artists.get(r.artistKey) || {}).name || '', mb: (window.__S.artists.get(r.artistKey) || {}).mbName || '',
  company: !!(window.__S.artists.get(r.artistKey) || {}).company, raw: r.raw || '', types: r.types || [], level: r.level,
  tracks: [...r.tracks].sort((a, b) => a - b).map(i => i + 1), primary: r.primaryText || '', credit: r.roleCredit || '', notes: r.notes || [],
  date: r.date ? [r.date.by, r.date.bm, r.date.bd].filter(Boolean).join('-') + (r.date.ey ? ' – ' + [r.date.ey, r.date.em, r.date.ed].filter(Boolean).join('-') : '') : '',
  supp: r.supp || '', took: r.suppTook ? r.suppTook.short : '' }))"""
ITEMS = """(window.__S.supp ? window.__S.supp.items : []).map(it => ({ kind: it.kind, sel: !!it.sel, name: it.name || ((window.__S.artists.get(it.artistKey) || {}).name) || '',
  line: it.line || '', rel: it.rel || '', tracks: (it.tracks || []).map(i => i + 1), all: !!it.all, more: !!it.more, conflict: !!it.conflict, addWins: !!it.addWins,
  first: it.firstTracks || '', to: it.toPrimary || '', why: it.why || '' }))"""
LOG = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.trim())"


def log_has(pg, pattern, timeout=90):
    H.wait_for(pg, f"[...document.querySelectorAll('#dci-log li')].some(li => /{pattern}/.test(li.textContent))", timeout)


def dm_apply(pg):
    """The suggestions of the date matrix applied ("Apply", when it has something to apply)."""
    on = pg.evaluate("(() => { const b = document.querySelector('#dci-overlay [data-act=dm-apply]'); return !!b && !b.disabled; })()")
    if on:
        pg.evaluate("document.querySelector('#dci-overlay [data-act=dm-apply]').click()")
        H.wait_still(pg, "document.body.innerHTML", 10, 400)
    return on


def open_import(p, direction, view='full', init=''):
    """The release opened, the dashboard imported, the date matrix applied: (browser, page, errors). init: a script run before the page's own."""
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    if init:
        ctx.add_init_script(init)
    pg, errs = H.open_mb_edit(ctx, companion=False, gm_xhr=True, view=view)
    pg.on('dialog', lambda d: d.accept())
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    log_has(pg, 'Import complete')
    H.wait_still(pg, "document.body.innerHTML", 15, 500)
    dm_apply(pg)
    return b, pg, errs


def add_source(pg, supp):
    """"＋ Source": 'bandcamp' (its album), 'discogs' (the release) or 'text' (the back of the box); the items compared, then taken as preselected."""
    H.open_supp(pg)
    if supp == 'text':
        pg.click('[data-act=supp-text]')
        pg.wait_for_timeout(300)
        pg.fill('[data-f=text-src]', D['cover_text'])
        pg.click('[data-act=supp-text-load]')
    else:
        pg.fill('[data-f=supp-url]', f"https://www.discogs.com/release/{D['discogs']['id']}" if supp == 'discogs' else D['bandcamp']['url'])
        pg.click('[data-act=supp-url]')
    log_has(pg, 'Added source: ', 120)
    H.wait_still(pg, "document.body.innerHTML", 15, 500)
    items = pg.evaluate(ITEMS)
    # (the reasons the table of the added source gives, before it is taken)
    add_source.why = pg.evaluate("[...document.querySelectorAll('[data-why]')].map(x => [x.dataset.why, x.textContent.trim()])")
    took = pg.evaluate("(() => { const b = document.querySelector('[data-act=supp-apply]'); if (!b || b.disabled) return false; b.click(); return true; })()")
    if took:
        H.wait_still(pg, "document.body.innerHTML", 20, 600)
    dm_apply(pg)
    return items


def norm_inst(row):
    """The instrument of a row as the target names it (MusicBrainz's name, the credit where it says more)."""
    t, c = row['primary'].lower(), row['credit'].lower()
    if 'reed trumpet' in c or 'reed trumpet' in t:
        return 'reed trumpet'
    if 'baroque violin' in c or 'baroque violin' in t:
        return 'baroque violin'
    if t:
        return {'drums (drum set)': 'drums', 'electric bass guitar': 'electric bass', 'cymbals': 'cymbal'}.get(t, t)
    if 'performer' in row['types'] or row['raw'].lower() == 'performer':
        return 'performer'
    return ''


def compare(rows):
    """The rows against the target: {'ok': [(track, person)], 'less': […], 'missing': […], 'extra': […], 'date': […]} – an instrument less precise or
    missing, a person missing or too many on a track, a relationship with another date (D022: the month or the period)."""
    T = {int(k): v for k, v in D['target']['tracks'].items()}
    dates = {int(k): v for k, v in D['target']['dates'].items()}
    alias = D['target']['names']
    groups = D['target'].get('groups', {})
    have = {}
    for r in rows:
        if r['company'] or r['level'] in ('skip', 'release', 'release_group', 'work') or not set(r['types']) & {'instrument', 'performer', 'vocal'}:
            continue
        who = alias.get(r['mb'] or r['name'], r['mb'] or r['name'])
        for t in r['tracks']:
            have.setdefault((t, who), {}).setdefault(norm_inst(r), []).append(r['date'])
    res = {'ok': [], 'less': [], 'missing': [], 'extra': [], 'date': []}
    for t, people in T.items():
        for who, insts in people.items():
            got = have.get((t, who), {})
            if not got:
                res['missing'].append((t, who, '/'.join(insts)))
                continue
            # (an alternative: "double bass|bass" – Discogs names only "Bass" there)
            miss = [i for i in insts if not any(x in got for x in i.split('|'))]
            (res['less'].append((t, who, '/'.join(miss), '/'.join(sorted(got)))) if miss else res['ok'].append((t, who)))
            for inst, ds in got.items():
                res['date'] += [(t, who, inst, d or '–') for d in ds if d not in dates[t]]
    for (t, who), got in have.items():
        if who not in T.get(t, {}) and t not in groups.get(who, []):
            res['extra'].append((t, who, '/'.join(sorted(got))))
    return res


def summary(rows):
    c = compare(rows)
    n = sum(len(v) for v in D['target']['tracks'].values())
    return f"{len(c['ok'])}/{n} right, {len(c['less'])} less precise, {len(c['missing'])} missing, {len(c['extra'])} too many, {len(c['date'])} dates", c
