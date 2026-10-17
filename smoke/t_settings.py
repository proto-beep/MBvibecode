"""Import 3.16.0: the menu "Settings" and the stored works of the artists.
A) "⚙ Settings" in the head opens the menu: six topics, folded; "Works" shows its defaults (on, 4000 with "= 40 requests,
   about 44 s per artist", 10 seconds, 900 entries, 7 days).
B) Shared switches: "apply automatically" ticked in the menu ticks the switch below the date matrix (and is stored);
   "add role credits" ticked in the footer shows ticked in the menu.
C) A value: 2,000 per artist is stored (with the new cost), 2,050 becomes 2,100 (steps of 100); a topic's "↺" asks and
   sets the topic back (the stored keys go).
D) The works read are kept beyond reloading the page: loaded again, the release artist is not asked again ("from the
   store", the work is offered again); the menu says "7 artists stored" (release artist, writers, musicians); "Clear the
   stored works" asks and empties it –
   loaded again, the artist is asked again.
E) Switched off ("Compare …" unticked, stored): after loading again nothing is asked, no hit is offered.
F) A button of the Discogs view in the menu ("Track highlight") switches the same setting as the one in the head."""
from playwright.sync_api import sync_playwright
import harness as H

TB = H.uid('dddddddd', 60)
W4 = H.uid('cccccccc', 94)
H.RELEASE_AC[:] = [(TB, 'Test Band', 'Test Band', '')]
H.ARTIST_WORKS.update({TB: [{'id': W4, 'title': H.TITLES[3], 'type': 'Song', 'aliases': []}]})
LOGS = "[...document.querySelectorAll('#dci-log li')].map(li => li.textContent.slice(9))"
SET = "document.querySelector('[data-el=settings]')"
results = []


def open_set(pg, *topics):
    if pg.evaluate(f"{SET}.hidden"):
        pg.locator('.dci-head [data-act=settings-open]').evaluate('b => b.click()'); pg.wait_for_timeout(300)
    for t in topics:
        if pg.locator(f'[data-act=settings-topic][data-topic={t}]').get_attribute('aria-expanded') != 'true':
            pg.locator(f'[data-act=settings-topic][data-topic={t}]').evaluate('b => b.click()'); pg.wait_for_timeout(200)


def load(pg, wait_compare=True):
    """Loads the page again (the log of the release is kept: the lines of this load are the ones after those before)."""
    word = 'Works of the artists compared' if wait_compare else 'Checks complete'
    n = len([x for x in pg.evaluate(LOGS) if word in x])
    pg.reload(); pg.add_script_tag(content=H.MAIN)
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.filter(x => x.includes('{word}')).length > {n}", 90)
    pg.wait_for_timeout(500)


def offered(pg):
    return pg.evaluate("[...document.querySelectorAll('tr[data-work=\"3\"] .dci-same [data-act=work-pick]')].map(b => b.dataset.gid)")


with sync_playwright() as p:
    b = p.chromium.launch(args=H.LAUNCH_ARGS)
    ctx = H.new_context(b)
    pg, errs = H.open_mb_edit(ctx, companion=False)
    DIALOGS = []
    pg.on('dialog', lambda d: (DIALOGS.append(d.message), d.accept()))
    pg.wait_for_selector('#dci-open', timeout=20000)
    H.open_dashboard(pg)
    H.wait_for(pg, f"{LOGS}.some(x => /Works of the artists compared/.test(x))", 90)
    pg.wait_for_timeout(300)
    # A) the menu
    open_set(pg)
    topics = pg.evaluate(f"[...{SET}.querySelectorAll('[data-act=settings-topic]')].map(b => [b.dataset.topic, b.getAttribute('aria-expanded')])")
    open_set(pg, 'works')
    vals = pg.evaluate(f"""(() => {{ const s = {SET}; const v = (k) => s.querySelector('[data-set=' + k + ']');
      return [v('aw-on').checked, v('awMax').value, v('awSlowSec').value, v('awSlowN').value, v('awDays').value, s.querySelector('[data-el=aw-cost]').textContent]; }})()""")
    print('A) Themen:', topics, '| Werke:', vals)
    results.append([t for t, _ in topics] == ['general', 'sources', 'discogs', 'works', 'staging', 'dates'] and all(e == 'false' for _, e in topics)
                   and vals == [True, '4000', '10', '900', '7', '= 40 requests, about 44 s per artist'])
    # B) shared switches
    open_set(pg, 'dates', 'staging')
    pg.locator('[data-el=settings] [data-f=dm-auto]').check(); pg.wait_for_timeout(400)
    below = pg.evaluate("[...document.querySelectorAll('[data-f=dm-auto]')].filter(x => !x.closest('[data-el=settings]')).map(x => x.checked)")
    stored = pg.evaluate("localStorage.getItem('dci-dm-auto')")
    pg.locator('footer [data-f=fill-credits]').evaluate('x => x.click()'); pg.wait_for_timeout(400)
    menu_fill = pg.evaluate(f"{SET}.querySelector('[data-f=fill-credits]').checked")
    print('B) „automatisch anwenden“ unter der Matrix:', below, '| gespeichert:', stored, '| „Rollen-Credits“ im Menü nach Klick unten:', menu_fill)
    results.append(below == [True] and stored == 'true' and menu_fill is True)
    # C) a value, steps, a topic's reset
    f = pg.locator('[data-el=settings] [data-set=awMax]')
    f.fill('2000'); f.press('Enter'); pg.wait_for_timeout(300)
    v1 = [pg.evaluate("localStorage.getItem('dci-aw-max')"), pg.evaluate(f"{SET}.querySelector('[data-el=aw-cost]').textContent")]
    f = pg.locator('[data-el=settings] [data-set=awMax]')
    f.fill('2050'); f.press('Enter'); pg.wait_for_timeout(300)
    v2 = pg.evaluate("localStorage.getItem('dci-aw-max')")
    DIALOGS.clear()
    pg.locator('[data-el=settings] [data-act=settings-reset][data-topic=works]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
    v3 = [pg.evaluate("localStorage.getItem('dci-aw-max')"), pg.evaluate(f"{SET}.querySelector('[data-set=awMax]').value")]
    asked = list(DIALOGS)
    print('C) 2000:', v1, '| 2050 →', v2, '| ↺ Werke:', asked, v3)
    results.append(v1 == ['2000', '= 20 requests, about 22 s per artist'] and v2 == '2100' and asked and '“Works”' in asked[0] and v3 == [None, '4000'])
    # D) kept beyond reloading
    n0 = len([1 for k, a, _ in H.BROWSES if a == TB])
    load(pg)
    n1 = len([1 for k, a, _ in H.BROWSES if a == TB])
    stored_log = [x for x in pg.evaluate(LOGS) if 'Test Band' in x and 'from the store' in x]
    hit = offered(pg)
    open_set(pg, 'works')
    pg.wait_for_timeout(500)
    count = pg.evaluate(f"({SET}.querySelector('[data-act=aw-clear]').parentElement.textContent || '').replace(/\\s+/g, ' ').trim()")
    DIALOGS.clear()
    pg.locator('[data-el=settings] [data-act=aw-clear]').evaluate('b => b.click()'); pg.wait_for_timeout(600)
    asked = list(DIALOGS)
    cleared = [x for x in pg.evaluate(LOGS) if 'Stored works cleared' in x]
    load(pg)
    n2 = len([1 for k, a, _ in H.BROWSES if a == TB])
    print('D) Anfragen an Test Band:', n0, '→ nach Neuladen', n1, '→ nach Leeren und Neuladen', n2, '|', stored_log, '| Treffer:', hit == [W4])
    print('   Menü:', count, '| Frage:', asked, '|', cleared)
    results.append(n0 == 2 and n1 == 2 and n2 == 4 and len(stored_log) == 1 and 'Test Band: 1 work from the store' in stored_log[0]
                   and hit == [W4] and '7 artists stored' in count and asked and 'of 7 artists' in asked[0] and cleared == ['Stored works cleared (7 artists)'])
    # E) switched off
    open_set(pg, 'works')
    pg.locator('[data-el=settings] [data-set=aw-on]').uncheck(); pg.wait_for_timeout(300)
    off_stored = pg.evaluate("localStorage.getItem('dci-aw-on')")
    nb = len(H.BROWSES)
    load(pg, wait_compare=False)
    pg.wait_for_timeout(2500)
    print('E) aus – gespeichert:', off_stored, '| neue Anfragen:', len(H.BROWSES) - nb, '| Treffer Track 4:', offered(pg))
    results.append(off_stored == 'false' and len(H.BROWSES) == nb and offered(pg) == [])
    # F) a button of the Discogs view in the menu
    open_set(pg, 'discogs')
    before = pg.evaluate("localStorage.getItem('dci-dg-hover')")
    pg.locator('[data-el=settings] [data-dg-hover]').evaluate('b => b.click()'); pg.wait_for_timeout(400)
    after = [pg.evaluate("localStorage.getItem('dci-dg-hover')"), pg.evaluate("[...document.querySelectorAll('[data-dg-hover]')].map(b => b.getAttribute('aria-pressed'))")]
    print('F) Track-Hervorhebung:', before, '→', after)
    results.append(after[0] == 'false' and after[1] and all(x == 'false' for x in after[1]))
    print('Fehler:', errs)
    results.append(not errs)
    b.close()
print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)
