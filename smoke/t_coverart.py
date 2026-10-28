"""Text from cover art (beta; Credits Importer 3.34.1, collected item E3): ⚙ Settings → Beta, "Source ▾ → Text from cover art …",
the images of the Cover Art Archive, the text recognition (a stand-in of Tesseract.js served as from jsDelivr), the text
corrected and imported.

Cases: ocrsetting, ocrpick, ocrrun, ocrerror; `python3 t_coverart.py <case> …` runs only those."""
import json

import harness as H  # noqa: F401 – used by the cases
from caserun import run_cases, sync_playwright  # noqa: F401 – the shared browser

# the images of the release: Front, Back, Booklet (a page in portrait), Tray (only 500 px), Medium
ART = [(11, ['Front'], '', 1500, 1500), (12, ['Back'], '', 1500, 1500), (13, ['Booklet'], 'p. 4–5', 1246, 1634),
       (14, ['Tray'], '', 500, 500), (15, ['Medium'], '', 1200, 1200)]
# what the stand-in reads, piece by piece (Back, Booklet, Tray), as Tesseract gives it: empty lines, © for ℗, "-" for "–"
TEXTS = [
    {'text': 'Music and cover art by j4vaman\n\nMastered by Ann Lee at Calyx Mastering, Berlin\n\n© & © 2017 Vivarium Recordings\n',
     'words': [{'text': 'Music', 'confidence': 95}, {'text': 'Calyx', 'confidence': 88}]},
    {'text': 'Marc D. Rusch - double bass\n\nDrum Guy — drums\n', 'words': [{'text': 'Rusch', 'confidence': 91}]},
    {'text': 'PRODUCED BY 808 PRODUCER\n', 'words': [{'text': '808', 'confidence': 31}, {'text': ':', 'confidence': 10}]},
]
DIALOG = """(() => { const el = document.getElementById('dci-ocr'); if (!el) return null;
  return { head: el.querySelector('.dci-ocr-head').innerText.replace(/\\s+/g, ' ').trim(),
    cards: [...el.querySelectorAll('.dci-ocr-card')].map(c => [c.querySelector('.dci-ocr-type').textContent.trim(), c.querySelector('input').checked, c.innerText.includes('rarely has credits')]),
    langs: [...el.querySelectorAll('[data-ocr-lang]')].filter(x => x.checked).map(x => x.dataset.ocrLang),
    run: (el.querySelector('[data-ocr=run]') || {}).textContent, body: el.querySelector('.dci-ocr-body').innerText.replace(/\\s+/g, ' ').trim() }; })()"""


def beta_on(ctx):
    ctx.add_init_script("localStorage.setItem('dci-beta-ocr', 'true');")


def case_ocrsetting():
    """⚙ Settings → Beta (between "Dates & tracks" and "ⓘ Connections"; maintainer: "Die Beta Funktion muss im Einstellungsmenü
    aktiviert werden"): "Text from cover art (beta)" is off – "Source ▾" has no item for it; switched on (stored): the item
    "Text from cover art … beta"; off again: gone. The connections name the Cover Art Archive (X013) and Tesseract.js (X014)."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        ctx = H.new_context(b)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        item = "(() => { const b = document.querySelector('#dci-overlay .dci-srcmenu [data-act=ocr-open]'); return b ? b.textContent.trim() : null; })()"
        H.open_settings(pg)
        tabs = pg.evaluate("[...document.querySelectorAll('[data-el=settings] .dci-set-tab')].map(t => t.dataset.topic)")
        H.open_settings(pg, 'beta')
        sw = pg.locator('[data-el=settings] [data-set=beta-ocr]')
        a = [tabs[-2:], sw.is_checked(), pg.evaluate(item)]
        sw.check()
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate("localStorage.getItem('dci-beta-ocr')"), pg.evaluate(item)]
        sw.uncheck()
        pg.wait_for_timeout(300)
        c1 = [pg.evaluate("localStorage.getItem('dci-beta-ocr')"), pg.evaluate(item)]
        H.open_settings(pg, 'connections')
        conn = pg.evaluate("[...document.querySelectorAll('[data-conn=X013], [data-conn=X014]')].map(r => r.innerText.replace(/\\s+/g, ' ').slice(0, 60))")
        print('A) Reiter:', a, '| an:', b1, '| aus:', c1, '| Verbindungen:', conn)
        results.append(a == [['beta', 'connections'], False, None] and b1 == ['true', 'Text from cover art …beta'] and c1[0] is None and c1[1] is None
                       and len(conn) == 2 and conn[0].startswith('Cover Art Archive') and conn[1].startswith('Tesseract.js'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrpick():
    """The images of the release (maintainer: "die Vorauswahl klingt gut"): in the order of the Cover Art Archive, Back,
    Booklet and Tray ticked, Front and Medium not ("rarely has credits"); English ticked (German too with a German
    dashboard); "Recognize text in 3 images"; a click on a card ticks it. A release without images says so."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        a = pg.evaluate(DIALOG)
        print('A)', a)
        results.append(a['cards'] == [['Front', False, True], ['Back', True, False], ['Booklet', True, False], ['Tray', True, False], ['Medium', False, True]]
                       and a['langs'] == ['en'] and a['run'] == 'Recognize text in 3 images' and '5 images on the Cover Art Archive' in a['head'])
        pg.click('#dci-ocr [data-ocr-sel="4"]')
        pg.wait_for_timeout(150)
        b1 = pg.evaluate(DIALOG)
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(200)
        gone = pg.evaluate("!document.getElementById('dci-ocr')")
        print('B) Medium dazu:', b1['run'], '| Escape:', gone)
        results.append(b1['run'] == 'Recognize text in 4 images' and gone)
        # German dashboard: German ticked too; no images
        H.COVER_ART = []
        ctx2 = H.new_context(b)
        beta_on(ctx2)
        ctx2.add_init_script("localStorage.setItem('dci-lang', JSON.stringify('de'));")
        pg2, errs2 = H.open_mb_edit(ctx2, companion=False)
        pg2.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg2)
        H.src_menu(pg2, 'ocr-open')
        pg2.wait_for_timeout(1200)
        c1 = pg2.evaluate(DIALOG)
        print('C) ohne Bilder:', c1['body'])
        results.append(c1['body'] == 'This release has no images on the Cover Art Archive.' or 'Cover Art Archive' in c1['body'])
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrrun():
    """Reading (the test of 2026-10-28): Tesseract.js loaded once from jsDelivr, one worker for English; Back, Booklet and
    Tray read whole – the Tray (500 px) enlarged ×3 (1500 × 1500 read) with a warning; the text corrected: "© & ©" → "℗ & ©",
    "-" and "—" between name and role → "–", no empty lines – and the corrections named; "808" listed as read with little
    certainty, a click selects it in the text; the worker ends. The text changed by hand ("808" → "Bob") and imported: the
    source is the text "Cover Art Archive images (Back, Booklet, Tray), read with text recognition" with j4vaman, Vivarium
    Recordings and Bob Producer."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps(TEXTS))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=20000)
        res = pg.evaluate("""(() => { const el = document.getElementById('dci-ocr');
          return { texts: [...el.querySelectorAll('[data-ocr-text]')].map(t => t.value), heads: [...el.querySelectorAll('.dci-ocr-res h3')].map(h => h.textContent.trim()),
            warn: [...el.querySelectorAll('.dci-ocr-warn')].map(w => w.textContent.trim()), unsure: [...el.querySelectorAll('[data-ocr-word]')].map(w => w.textContent),
            fixed: [...el.querySelectorAll('.dci-ocr-res .dci-sub')].map(x => x.textContent.trim()).filter(t => t.startsWith('Corrected')),
            ocr: window.__ocr }; })()""")
        libs = [u for u in H.TESSERACT_REQUESTS if u.endswith('tesseract.min.js')]
        print('A) Texte:', res['texts'])
        print('   Köpfe:', res['heads'], '| Warnung:', res['warn'], '| unsicher:', res['unsure'], '| korrigiert:', res['fixed'])
        print('   Aufrufe:', res['ocr'], '| Bibliothek:', libs)
        results.append(res['texts'] == ['Music and cover art by j4vaman\nMastered by Ann Lee at Calyx Mastering, Berlin\n℗ & © 2017 Vivarium Recordings',
                                        'Marc D. Rusch – double bass\nDrum Guy – drums', 'PRODUCED BY 808 PRODUCER']
                       and res['heads'][:2] == ['Back', 'Booklet “p. 4–5”'] and res['warn'] == ['Only 500 × 500 px – read enlarged; names can come out wrong.']
                       and res['unsure'] == ['808'] and res['fixed'] == ['Corrected after reading: ℗ read as © (1)', 'Corrected after reading: dash between a name and a role (2)']
                       and res['ocr']['calls'] == [[1500, 1500], [1246, 1634], [1500, 1500]] and res['ocr']['langs'] == ['eng'] and res['ocr']['created'] == 1
                       and res['ocr']['terminated'] == 1 and len(libs) == 1 and libs[0] == 'https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js')
        pg.click('#dci-ocr [data-ocr-word="808"]')
        sel = pg.evaluate("(() => { const t = document.querySelector('#dci-ocr [data-ocr-text=\"2\"]'); return [document.activeElement === t, t.value.slice(t.selectionStart, t.selectionEnd)]; })()")
        pg.fill('#dci-ocr [data-ocr-text="2"]', 'Produced by Bob Producer')
        pg.click('#dci-ocr [data-ocr=import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(1000)
        c = pg.evaluate("""[!document.getElementById('dci-ocr'), document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').trim(),
          [...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())]""")
        print('B) Auswahl:', sel, '| übernommen:', c)
        results.append(sel == [True, '808'] and c[0] and 'Cover Art Archive images (Back, Booklet, Tray), read with text recognition' in c[1]
                       and all(n in c[2] for n in ('j4vaman', 'Vivarium Recordings', 'Bob Producer', 'Marc D. Rusch')))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrerror():
    """Tesseract.js cannot be loaded (jsDelivr answers 404): the window says so ("The text recognition could not be loaded
    (…tesseract.min.js) – the page or the browser may not allow it.") and stays at the images; the log names it."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        H.TESSERACT_FAKE = False
        ctx = H.new_context(b)
        beta_on(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr .dci-ocr-err', timeout=20000)
        a = [pg.evaluate("document.querySelector('#dci-ocr .dci-ocr-err').textContent"), pg.locator('#dci-ocr .dci-ocr-card').count(),
             pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /Text from cover art: The text recognition/.test(t)).length")]
        print('A)', a)
        results.append(a[0].startswith('The text recognition could not be loaded (https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js)') and a[1] == 5 and a[2] == 1)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


run_cases(globals())
