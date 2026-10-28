"""Text from cover art (beta; Credits Importer 3.34.1, collected item E3): ⚙ Settings → Beta, "Source ▾ → Text from cover art …",
the images of the Cover Art Archive, the text recognition (a stand-in of Tesseract.js served as from jsDelivr), the text
corrected and imported.

Cases: ocrsetting, ocrpick, ocrrun, ocrerror, [3.34.2] ocrframes, [3.34.5] ocrown, [3.34.6] ocrpdf, [3.34.7] ocrdiscogs, [3.34.8] ocrstart, [3.34.9] ocrpeek, [3.34.10] ocrload, [3.34.11] ocrzoom; `python3 t_coverart.py <case> …` runs only those."""
import json
import re

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
    run: (el.querySelector('[data-ocr=run], [data-ocr=frames]') || {}).textContent, body: el.querySelector('.dci-ocr-body').innerText.replace(/\\s+/g, ' ').trim() }; })()"""


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
                       and a['langs'] == ['en'] and a['run'] == 'Next: frames for 3 images →' and '5 images on the Cover Art Archive' in a['head'])
        pg.click('#dci-ocr [data-ocr-sel="4"]')
        pg.wait_for_timeout(150)
        b1 = pg.evaluate(DIALOG)
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(200)
        gone = pg.evaluate("!document.getElementById('dci-ocr')")
        print('B) Medium dazu:', b1['run'], '| Escape:', gone)
        results.append(b1['run'] == 'Next: frames for 4 images →' and gone)
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
        pg.uncheck('#dci-ocr [data-ocr-framefirst]')  # [3.34.2] no frames: the whole images
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
        sel = pg.evaluate("(() => { const t = document.querySelector('#dci-ocr [data-ocr-text=\"2:0\"]'); return [document.activeElement === t, t.value.slice(t.selectionStart, t.selectionEnd)]; })()")
        pg.fill('#dci-ocr [data-ocr-text="2:0"]', 'Produced by Bob Producer')
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
        pg.uncheck('#dci-ocr [data-ocr-framefirst]')
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



def case_ocrframes():
    """[3.34.2] Frames around the credits (maintainer: "Rahmen Standardmäßig aber mit Option auf komplettes Bild lesen"): "Draw a
    frame around the credits on each image" is ticked – "Next: frames for 3 images →". The Back (1500 px) in a view of 560 px: a
    frame dragged across it (1200 × 300 px), its corner moved (1200 × 375), a second frame (600 × 225) moved by dragging inside it;
    the image says "2 frames". The Booklet turned right and read whole; the Tray left out – "Recognize text in 2 images". Read:
    the two frames of the Back in their order, then the whole turned Booklet (1634 × 1246); the Tray not. "← Images": the Tray
    is ticked again, the frames of the Back stay."""
    results = []
    STATE = """(() => { const el = document.getElementById('dci-ocr'); const v = el.querySelector('[data-ocr-view]');
      return { head: el.querySelector('.dci-ocr-head .dci-sub').textContent.trim(), view: v ? [v.width, v.height] : null,
        thumbs: [...el.querySelectorAll('.dci-ocr-thumb')].map(t => t.innerText.replace(/\\s+/g, ' ').trim()),
        mode: (el.querySelector('[data-ocr-mode]:checked') || {}).dataset?.ocrMode, run: (el.querySelector('[data-ocr=run]') || {}).textContent }; })()"""
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
        a0 = [pg.locator('#dci-ocr [data-ocr-framefirst]').is_checked(), pg.locator('#dci-ocr [data-ocr=frames]').inner_text()]
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)
        a1 = pg.evaluate(STATE)

        def drag(x0, y0, x1, y1):
            box = pg.locator('#dci-ocr [data-ocr-view]').bounding_box()
            w = pg.evaluate("document.querySelector('#dci-ocr [data-ocr-view]').width")
            f = box['width'] / w
            pg.mouse.move(box['x'] + x0 * f, box['y'] + y0 * f)
            pg.mouse.down()
            for k in range(1, 6):
                pg.mouse.move(box['x'] + (x0 + (x1 - x0) * k / 5) * f, box['y'] + (y0 + (y1 - y0) * k / 5) * f)
            pg.mouse.up()
            pg.wait_for_timeout(150)
        drag(56, 336, 504, 448)
        drag(504, 448, 504, 476)
        drag(56, 56, 280, 140)
        drag(150, 100, 178, 100)
        b1 = pg.evaluate(STATE)
        print('A) vorher:', a0, '| Rückseite:', a1)
        print('B) zwei Rahmen:', b1)
        results.append(a0 == [True, 'Next: frames for 3 images →'] and a1['view'] == [560, 560] and a1['head'] == 'frames · image 1 of 3 · Back'
                       and a1['mode'] == 'frames' and b1['thumbs'][0] == 'Back 2 frames' and b1['mode'] == 'frames')
        pg.click('#dci-ocr [data-ocr=next]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)
        pg.wait_for_timeout(200)
        c0 = pg.evaluate(STATE)
        pg.click('#dci-ocr [data-ocr=rotr]')
        pg.wait_for_timeout(150)
        pg.check('#dci-ocr [data-ocr-mode=whole]')
        pg.wait_for_timeout(150)
        c1 = pg.evaluate(STATE)
        pg.click('#dci-ocr [data-ocr=next]')
        pg.wait_for_timeout(600)
        pg.check('#dci-ocr [data-ocr-mode=skip]')
        pg.wait_for_timeout(150)
        c2 = pg.evaluate(STATE)
        print('C) Booklet:', c0['view'], '→ gedreht:', c1['view'], c1['thumbs'], '| Tray:', c2['thumbs'][2], c2['run'])
        results.append(c0['view'] == [473, 620] and c1['view'] == [560, 427] and c1['thumbs'][1] == 'Booklet the whole image'
                       and c2['thumbs'][2] == 'Tray left out' and c2['run'] == 'Recognize text in 2 images')
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=20000)
        d = pg.evaluate("[window.__ocr.calls, [...document.querySelectorAll('#dci-ocr .dci-ocr-res h3')].map(h => h.textContent.trim())]")
        pg.click('#dci-ocr [data-ocr=back]')
        pg.wait_for_timeout(200)
        e1 = pg.evaluate(DIALOG)['cards']
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr .dci-ocr-thumb', timeout=10000)
        e2 = pg.evaluate(STATE)['thumbs']
        print('D) gelesen:', d, '| zurück:', e1, e2)
        results.append(d[0] == [[1200, 375], [600, 225], [1634, 1246]] and d[1] == ['Back', 'Booklet “p. 4–5”']
                       and [c[1] for c in e1] == [False, True, True, True, False] and e2[0] == 'Back 2 frames' and e2[2].startswith('Tray'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrown():
    """[3.34.5] "All images" and own images (collected items 125, 123; maintainer: "wir brauchen einen knopf im bilderkennungsmenü,
    der alles abwählt oder alles anwählt", "bei der Bilderkennung soll auch die Möglichkeit bestehen eigene Files oder Bilder per
    URL zu analysieren", "ja alle drei möglichkeiten").
    A) "All images (5)" half ticked (3 of 5); a click ticks all (Next: frames for 5 images), again none (the button off), again all.
    B) Files chosen: an image is a card of its own (its name, "your file", ticked); a text file is left out with a message.
    C) An image pasted (Ctrl+V) and one dropped onto the window: cards "pasted image 1" and "drop.png"; "remove" takes the pasted
       one out again (its card not ticked by the click).
    D) An address: Enter adds it ("images.example.org/…/back cover.png", "by its address"); a wrong one and the same one twice
       are refused with a message.
    E) An address whose site does not let the script read it: reading says so ("save the image and choose it as a file").
    F) The own images read (the release's unticked): the file whole, the dropped 800 px image enlarged ×3, the address' image;
       imported, the source names "own image files (booklet-scan.png, drop.png); images from https://…, read with text recognition".
       Without images on the Cover Art Archive the window says so and offers the own images."""
    import base64
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        texts = [{'text': 'Music by Ann Lee\n', 'words': []}, {'text': 'Drums – Drum Guy\n', 'words': []}, {'text': 'Mastered by Bob Producer\n', 'words': []}]
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps(texts))
        ctx.route('https://images.example.org/**', lambda r: r.fulfill(body=H.png_of(1200, 1200), content_type='image/png', headers={'Access-Control-Allow-Origin': '*'}))
        ctx.route('https://nocors.example.org/**', lambda r: r.abort())  # (the tests' browser does not check CORS: a site that refuses)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        ALL = "(() => { const a = document.querySelector('#dci-ocr [data-ocr-all]'); const r = document.querySelector('#dci-ocr [data-ocr=run], #dci-ocr [data-ocr=frames]'); return [a.parentElement.textContent.trim(), a.checked, a.indeterminate, r.textContent, r.disabled]; })()"
        a0 = pg.evaluate(ALL)
        pg.click('#dci-ocr [data-ocr-all]')
        a1 = pg.evaluate(ALL)
        pg.click('#dci-ocr [data-ocr-all]')
        a2 = pg.evaluate(ALL)
        pg.click('#dci-ocr [data-ocr-all]')
        a3 = pg.evaluate(ALL)
        print('A) alle:', a0, a1, a2, a3)
        results.append(a0 == ['All images (5)', False, True, 'Next: frames for 3 images →', False] and a1[1:] == [True, False, 'Next: frames for 5 images →', False]
                       and a2[1:] == [False, False, 'Next: frames for 0 images →', True] and a3[1] is True)
        CARDS = "[...document.querySelectorAll('#dci-ocr .dci-ocr-owncard')].map(c => [c.querySelector('.dci-ocr-type').textContent.trim(), c.querySelector('input').checked, c.querySelector('.dci-sub').textContent.replace(/\\s+/g, ' ').trim()])"
        ERR = "(document.querySelector('#dci-ocr .dci-ocr-err[role=alert]') || {}).textContent || ''"
        pg.set_input_files('#dci-ocr [data-ocr-files]', files=[{'name': 'booklet-scan.png', 'mimeType': 'image/png', 'buffer': H.png_of(1400, 1800)},
                                                              {'name': 'notes.txt', 'mimeType': 'text/plain', 'buffer': b'credits'}])
        pg.wait_for_timeout(300)
        b1 = [pg.evaluate(CARDS), pg.evaluate(ERR)]
        print('B) Dateien:', b1)
        results.append(b1[0] == [['booklet-scan.png', True, 'your file remove']] and b1[1] == 'Not an image or a PDF, left out: notes.txt')
        png = base64.b64encode(H.png_of(800, 600)).decode()
        pg.evaluate("""(b64) => { const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); const dt = new DataTransfer();
          dt.items.add(new File([bytes], 'image.png', { type: 'image/png' })); document.body.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true })); }""", png)
        pg.wait_for_timeout(300)
        dt = pg.evaluate_handle("""(b64) => { const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); const d = new DataTransfer();
          d.items.add(new File([bytes], 'drop.png', { type: 'image/png' })); return d; }""", png)
        pg.dispatch_event('#dci-ocr', 'dragover', {'dataTransfer': dt})
        pg.dispatch_event('#dci-ocr', 'drop', {'dataTransfer': dt})
        pg.wait_for_timeout(300)
        c1 = pg.evaluate(CARDS)
        pg.click('#dci-ocr .dci-ocr-owncard:nth-child(7) [data-ocr-remove]')
        pg.wait_for_timeout(200)
        c2 = pg.evaluate(CARDS)
        print('C) eingefügt, gezogen:', c1, '| entfernt:', c2)
        results.append([x[0] for x in c1] == ['booklet-scan.png', 'pasted image 1', 'drop.png'] and all(x[1] for x in c1)
                       and [x[0] for x in c2] == ['booklet-scan.png', 'drop.png'])
        pg.fill('#dci-ocr [data-ocr-url]', 'https://images.example.org/scans/back%20cover.png')
        pg.press('#dci-ocr [data-ocr-url]', 'Enter')
        pg.wait_for_timeout(200)
        d1 = pg.evaluate(CARDS)
        pg.fill('#dci-ocr [data-ocr-url]', 'ftp://example.org/x.png')
        pg.click('#dci-ocr [data-ocr=url]')
        pg.wait_for_timeout(200)
        d2 = pg.evaluate(ERR)
        pg.fill('#dci-ocr [data-ocr-url]', 'https://images.example.org/scans/back%20cover.png')
        pg.click('#dci-ocr [data-ocr=url]')
        pg.wait_for_timeout(200)
        d3 = pg.evaluate(ERR)
        print('D) Adresse:', d1[-1], '| falsch:', d2, '| doppelt:', d3)
        results.append(d1[-1] == ['images.example.org/…/back cover.png', True, 'by its address remove'] and d2.startswith('Not the address of an image: ftp://example.org/x.png')
                       and d3 == 'This address is in the list already.')
        # E) a site without permission: only that image, no frames
        pg.fill('#dci-ocr [data-ocr-url]', 'https://nocors.example.org/x.png')
        pg.press('#dci-ocr [data-ocr-url]', 'Enter')
        pg.wait_for_timeout(200)
        pg.uncheck('#dci-ocr [data-ocr-framefirst]')
        pg.click('#dci-ocr [data-ocr-all]')  # all ticked → none
        if pg.evaluate("document.querySelector('#dci-ocr [data-ocr-all]').checked"):
            pg.click('#dci-ocr [data-ocr-all]')
        pg.check('#dci-ocr .dci-ocr-owncard:last-child input')
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_timeout(1500)
        e1 = pg.evaluate("(document.querySelector('#dci-ocr .dci-ocr-err') || {}).textContent || ''")
        print('E) ohne Erlaubnis:', e1)
        results.append(e1 == 'The image at https://nocors.example.org/x.png could not be read – the site does not let the script read it. Save the image and choose it as a file.')
        pg.click('#dci-ocr .dci-ocr-owncard:last-child [data-ocr-remove]')
        pg.wait_for_timeout(200)
        # F) the own images read and imported
        for k in range(pg.locator('#dci-ocr .dci-ocr-owncard').count()):
            pg.check(f'#dci-ocr .dci-ocr-owncard >> nth={k} >> input')
            pg.wait_for_timeout(100)
        f0 = pg.evaluate("[...document.querySelectorAll('#dci-ocr .dci-ocr-card input')].map(i => i.checked)")
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=20000)
        f1 = pg.evaluate("""[[...document.querySelectorAll('#dci-ocr .dci-ocr-res h3')].map(h => h.textContent.trim()), window.__ocr.calls,
          [...document.querySelectorAll('#dci-ocr .dci-ocr-warn')].length]""")
        pg.click('#dci-ocr [data-ocr=import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        f2 = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').trim()")
        print('F) gewählt:', f0, '| gelesen:', f1, '| Quelle:', f2[:260])
        results.append(f0 == [False] * 5 + [True] * 3 and f1[0] == ['booklet-scan.png', 'drop.png', 'images.example.org/…/back cover.png']
                       and f1[1] == [[1400, 1800], [2400, 1800], [1200, 1200]] and f1[2] == 1
                       and 'own image files (booklet-scan.png, drop.png); images from https://images.example.org/scans/back%20cover.png, read with text recognition' in f2)
        # without images on the Cover Art Archive
        H.COVER_ART = []
        ctx2 = H.new_context(b)
        beta_on(ctx2)
        pg2, errs2 = H.open_mb_edit(ctx2, companion=False)
        pg2.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg2)
        H.src_menu(pg2, 'ocr-open')
        pg2.wait_for_selector('#dci-ocr [data-ocr-files]', state='attached', timeout=10000)
        g = pg2.evaluate("[document.querySelector('#dci-ocr .dci-ocr-body > p').textContent, !!document.querySelector('#dci-ocr [data-ocr-url]'), !!document.querySelector('#dci-ocr [data-ocr-size]')]")
        print('G) ohne Bilder im CAA:', g)
        results.append(g == ['This release has no images on the Cover Art Archive.', True, False])
        print('Fehler:', errs, errs2)
        results.append(not errs and not errs2)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrpdf():
    """[3.34.6] A booklet as PDF (collected item 123; maintainer: "und auch pdf booklets!"), with the real pdf.js (a local copy
    served as from jsDelivr).
    A) A PDF chosen: pdf.js loaded from jsDelivr (and its worker); each page a card – "booklet.pdf · p. 1" "PDF page with its own
       text", p. 2 (a drawing only) "PDF page (an image)", p. 3 with its own text.
    B) Frames: p. 1 and p. 2 without, on p. 3 (two columns) a frame around the left one.
    C) Read: p. 1 from its own text, in its order, the dash corrected ("Marc D. Rusch – double bass"), "Read from the PDF's own
       text"; p. 2 by the text recognition (the page at 2400 px); p. 3 from its own text, only the left column, line by line. The
       text recognition is started once, only for p. 2.
    D) Imported: the source "PDF booklet.pdf (p. 1, 2, 3), read with text recognition".
    E) A PDF by its address: its pages "images.example.org/…/booklet.pdf · p. 1" …; a file that is no PDF named "bad.pdf" is
       named as not opened."""
    import base64
    results = []
    pdf = H.pdf_of([[(40, 380, 14, 'Booklet'), (40, 350, 12, 'Credits'), (40, 330, 12, 'Marc D. Rusch - double bass'), (40, 310, 12, 'Recorded at the Iridium, New York')],
                    None,
                    [(30, 300, 12, 'Drums - Drum Guy'), (230, 300, 12, 'Piano - Keys Guy'), (30, 280, 12, 'Bass - Bass Man'), (230, 280, 12, 'Organ - Org Guy')]])
    CARDS = "[...document.querySelectorAll('#dci-ocr .dci-ocr-owncard')].map(c => [c.querySelector('.dci-ocr-type').textContent.trim(), c.querySelector('input').checked, c.querySelector('.dci-sub').textContent.replace(' remove', '').trim()])"
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = []
        ctx = H.new_context(b)
        beta_on(ctx)
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps([{'text': 'Producer - Bob Producer\n', 'words': []}]))
        ctx.route('https://images.example.org/**', lambda r: r.fulfill(body=pdf, content_type='application/pdf', headers={'Access-Control-Allow-Origin': '*'}))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr [data-ocr-files]', state='attached', timeout=10000)
        pg.set_input_files('#dci-ocr [data-ocr-files]', files=[{'name': 'booklet.pdf', 'mimeType': 'application/pdf', 'buffer': pdf}])
        H.wait_for(pg, "document.querySelectorAll('#dci-ocr .dci-ocr-owncard').length === 3 && !document.querySelector('#dci-ocr [data-ocr-pdfstatus]')", 30)
        a = [pg.evaluate(CARDS), sorted({u.split('/legacy/build/')[-1] for u in H.PDFJS_REQUESTS if '/legacy/build/' in u})]
        print('A) Seiten:', a)
        results.append(a[0] == [['booklet.pdf · p. 1', True, 'PDF page with its own text'], ['booklet.pdf · p. 2', True, 'PDF page (an image)'],
                                ['booklet.pdf · p. 3', True, 'PDF page with its own text']] and a[1] == ['pdf.min.mjs', 'pdf.worker.min.mjs'])
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=20000)
        pg.click('#dci-ocr [data-ocr=next]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=20000)
        pg.click('#dci-ocr [data-ocr=next]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=20000)
        pg.wait_for_timeout(300)
        box = pg.locator('#dci-ocr [data-ocr-view]').bounding_box()
        vw = pg.evaluate("document.querySelector('#dci-ocr [data-ocr-view]').width")
        f = box['width'] / vw
        x0, y0, x1, y1 = 23, 140, 280, 198
        pg.mouse.move(box['x'] + x0 * f, box['y'] + y0 * f)
        pg.mouse.down()
        for k in range(1, 6):
            pg.mouse.move(box['x'] + (x0 + (x1 - x0) * k / 5) * f, box['y'] + (y0 + (y1 - y0) * k / 5) * f)
        pg.mouse.up()
        pg.wait_for_timeout(200)
        b1 = pg.evaluate("[...document.querySelectorAll('#dci-ocr .dci-ocr-thumb')].map(t => t.innerText.replace(/\\s+/g, ' ').trim())")
        print('B) Rahmen:', b1, '| Ansicht:', vw)
        results.append(vw == 560 and b1[2].endswith('1 frame'))
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=30000)
        c = pg.evaluate("""(() => { const el = document.getElementById('dci-ocr');
          return { texts: [...el.querySelectorAll('[data-ocr-text]')].map(t => t.value), heads: [...el.querySelectorAll('.dci-ocr-res h3')].map(h => h.textContent.trim()),
            direct: [...el.querySelectorAll('.dci-ocr-res')].map(r => r.innerText.includes("Read from the PDF's own text")), ocr: window.__ocr }; })()""")
        print('C) Texte:', c['texts'], '| direkt:', c['direct'], '| Erkennung:', c['ocr'])
        results.append(c['texts'] == ['Booklet\nCredits\nMarc D. Rusch – double bass\nRecorded at the Iridium, New York', 'Producer – Bob Producer', 'Drums – Drum Guy\nBass – Bass Man']
                       and c['heads'] == ['booklet.pdf · p. 1', 'booklet.pdf · p. 2', 'booklet.pdf · p. 3'] and c['direct'] == [True, False, True]
                       and c['ocr']['created'] == 1 and c['ocr']['calls'] == [[2400, 2400]])
        pg.click('#dci-ocr [data-ocr=import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        d = pg.evaluate("document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').trim()")
        print('D) Quelle:', d[:200])
        results.append('PDF booklet.pdf (p. 1, 2, 3), read with text recognition' in d)
        # E) by its address; a file that is no PDF
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr [data-ocr-url]', timeout=10000)
        pg.fill('#dci-ocr [data-ocr-url]', 'https://images.example.org/scans/booklet.pdf')
        pg.press('#dci-ocr [data-ocr-url]', 'Enter')
        H.wait_for(pg, "document.querySelectorAll('#dci-ocr .dci-ocr-owncard').length === 3 && !document.querySelector('#dci-ocr [data-ocr-pdfstatus]')", 30)
        e1 = pg.evaluate(CARDS)
        pg.set_input_files('#dci-ocr [data-ocr-files]', files=[{'name': 'bad.pdf', 'mimeType': 'application/pdf', 'buffer': b'no pdf at all'}])
        H.wait_for(pg, "!!document.querySelector('#dci-ocr .dci-ocr-err[role=alert]')", 30)
        e2 = pg.evaluate("document.querySelector('#dci-ocr .dci-ocr-err[role=alert]').textContent")
        print('E) Adresse:', e1, '| kaputt:', e2)
        results.append([x[0] for x in e1] == ['images.example.org/…/booklet.pdf · p. 1', 'images.example.org/…/booklet.pdf · p. 2', 'images.example.org/…/booklet.pdf · p. 3']
                       and e2.startswith('bad.pdf could not be opened as a PDF:'))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def discogs_image(rel, n, size):
    """[3.34.7] An address of i.discogs.com as Discogs writes them: options, then the file "R-<release>-…" in base64, in parts."""
    import base64
    b64 = base64.urlsafe_b64encode(f'discogs-database-images/R-{rel}-1600000000-{1000 + n}.jpeg'.encode()).decode().rstrip('=')
    parts = '/'.join(b64[i:i + 16] for i in range(0, len(b64), 16))
    return f'https://i.discogs.com/sig{n}{size}/rs:fit/g:sm/q:90/h:{size}/w:{size}/{parts}.jpeg'


def case_ocrdiscogs():
    """[3.34.7] Discogs images only on request (collected item 123; maintainer: "nur wenn eingegeben. nicht automatisch. evtl einen
    button mit "load discogs artworks" oder ähnlich").
    A) Opened: nothing of Discogs is fetched; "Load Discogs images (r<id>)" for the release linked to this one.
    B) A click: the release's page on discogs.com is read – its two images, each once at its largest size (600 px, not the 150 px
       thumbnails), not the image of another release on the page; cards "Discogs r<id> · 1" "from Discogs", ticked; the button off.
    C) The address of another Discogs release typed: its image; the same again refused.
    D) Read: the 600 px images enlarged ×3 (1800 × 1800) with the warning; imported, the source names
       "images of Discogs release https://www.discogs.com/release/<id>"."""
    results = []
    rel = H.DISCOGS_ID
    page = ('<html><body><img src="%s"><img src="%s"><img src="%s"><img src="%s"><a><img src="%s"></a></body></html>'
            % (discogs_image(rel, 1, 150), discogs_image(rel, 1, 600), discogs_image(rel, 2, 600), discogs_image(rel, 2, 150), discogs_image(999, 1, 600)))
    other = '<html><body><img src="%s"></body></html>' % discogs_image(4242, 1, 600)
    pages = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps([{'text': 'Credits by Discogs\n', 'words': []}] * 3))

        def dg_page(route):
            pages.append(route.request.url)
            body = page if route.request.url.endswith(f'/release/{rel}') else other
            return route.fulfill(body=body, content_type='text/html', headers={'Access-Control-Allow-Origin': '*'})
        ctx.route('https://www.discogs.com/release/**', dg_page)
        ctx.route('https://i.discogs.com/**', lambda r: r.fulfill(body=H.png_of(600, 600), content_type='image/png', headers={'Access-Control-Allow-Origin': '*'}))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 60)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        a = [pg.evaluate("[...document.querySelectorAll('#dci-ocr [data-ocr-discogs]')].map(x => x.textContent.trim())"), list(pages)]
        print('A) Knopf:', a)
        results.append(a == [[f'Load Discogs images (r{rel})'], []])
        CARDS = "[...document.querySelectorAll('#dci-ocr .dci-ocr-owncard')].map(c => [c.querySelector('.dci-ocr-type').textContent.trim(), c.querySelector('input').checked, c.querySelector('.dci-sub').textContent.replace(' remove', '').trim()])"
        pg.click('#dci-ocr [data-ocr-discogs]')
        H.wait_for(pg, "document.querySelectorAll('#dci-ocr .dci-ocr-owncard').length === 2", 20)
        b1 = [pg.evaluate(CARDS), pg.evaluate("[...document.querySelectorAll('#dci-ocr .dci-ocr-owncard img')].map(i => i.getAttribute('src').match(/h:(\\d+)/)[1])"),
              pg.evaluate("document.querySelector('#dci-ocr [data-ocr-discogs]').disabled"), list(pages)]
        print('B) Discogs:', b1)
        results.append(b1[0] == [[f'Discogs r{rel} · 1', True, 'from Discogs'], [f'Discogs r{rel} · 2', True, 'from Discogs']] and b1[1] == ['600', '600'] and b1[2]
                       and b1[3] == [f'https://www.discogs.com/release/{rel}'])
        pg.fill('#dci-ocr [data-ocr-url]', 'https://www.discogs.com/de/release/4242-Other-Band-Other-Album')
        pg.press('#dci-ocr [data-ocr-url]', 'Enter')
        H.wait_for(pg, "document.querySelectorAll('#dci-ocr .dci-ocr-owncard').length === 3", 20)
        pg.fill('#dci-ocr [data-ocr-url]', 'https://www.discogs.com/release/4242')
        pg.press('#dci-ocr [data-ocr-url]', 'Enter')
        pg.wait_for_timeout(300)
        c1 = [pg.evaluate(CARDS)[-1], pg.evaluate("(document.querySelector('#dci-ocr .dci-ocr-err[role=alert]') || {}).textContent || ''")]
        print('C) andere Adresse:', c1)
        results.append(c1 == [['Discogs r4242 · 1', True, 'from Discogs'], 'This address is in the list already.'])
        # D) read the release's two Discogs images
        pg.uncheck('#dci-ocr [data-ocr-framefirst]')
        if pg.evaluate("document.querySelector('#dci-ocr [data-ocr-all]').checked"):
            pg.click('#dci-ocr [data-ocr-all]')
        else:
            pg.click('#dci-ocr [data-ocr-all]')
            pg.click('#dci-ocr [data-ocr-all]')
        for k in range(2):
            pg.check(f'#dci-ocr .dci-ocr-owncard >> nth={k} >> input')
            pg.wait_for_timeout(100)
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=20000)
        d1 = pg.evaluate("[window.__ocr.calls, document.querySelectorAll('#dci-ocr .dci-ocr-warn').length]")
        pg.click('#dci-ocr [data-ocr=supp]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Text from cover art: .*images of Discogs release/.test(li.textContent))", 30)
        d2 = pg.evaluate("[...document.querySelectorAll('#dci-log li')].map(li => li.textContent).filter(t => /Text from cover art: .*images of Discogs release/.test(t))")
        print('D) gelesen:', d1, '| Log:', d2)
        results.append(d1 == [[[1800, 1800], [1800, 1800]], 2] and any(f'images of Discogs release https://www.discogs.com/release/{rel}, read with text recognition' in t for t in d2))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrstart():
    """[3.34.8] "… from cover art" beside "Import credits …" (collected item 124; maintainer: "der dann die Bilderkennung triggert
    bevor bspw. von discogs importiert wird", "nur wenn beta an ist", "A").
    A) Beta off: no such button; beta on: "… from cover art" with "beta", joined to "Import credits …".
    B) A click: the dashboard without the import (nothing asked of Discogs, nothing imported), a message that offers "Start
       import", and the window of the text recognition with the release's images; "Load Discogs images (r1234)" from the
       release's links (asked of MusicBrainz).
    C) Read and "Import this text": the release is loaded with the text as its source ("Cover Art Archive images (Back, Booklet,
       Tray), read with text recognition") – still nothing of Discogs; the message is gone.
    D) The beta switched off in ⚙ Settings → Beta: the button goes."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx0 = H.new_context(b)
        pg0, errs0 = H.open_mb_edit(ctx0, companion=False)
        pg0.wait_for_selector('#dci-open', timeout=20000)
        a0 = pg0.evaluate("(() => { const b = document.getElementById('dci-open-ocr'); return !!b && !b.hidden && b.offsetParent !== null; })()")
        ctx = H.new_context(b)
        beta_on(ctx)
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps(TEXTS))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        reqs = []
        pg.on('request', lambda r: reqs.append(r.url))
        pg.wait_for_selector('#dci-open-ocr', state='visible', timeout=20000)
        a1 = pg.evaluate("""(() => { const o = document.getElementById('dci-open'), b = document.getElementById('dci-open-ocr'); const r1 = o.getBoundingClientRect(), r2 = b.getBoundingClientRect();
          return [b.firstChild.textContent.trim(), !!b.querySelector('.dci-beta-tag'), Math.round(r2.left - r1.right), getComputedStyle(o).borderTopRightRadius]; })()""")
        print('A) Beta aus – Knopf:', a0, '| an:', a1)
        results.append(not a0 and a1 == ['… from cover art', True, -1, '0px'])
        pg.click('#dci-open-ocr')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=15000)
        pg.wait_for_selector('#dci-ocr [data-ocr-discogs]', timeout=15000)
        b1 = pg.evaluate("""[!document.getElementById('dci-overlay').hidden, [...document.querySelectorAll('[data-el=msgs] .dci-msg')].map(m => [m.textContent.replace(/\\s+/g, ' ').trim().slice(0, 120), !!m.querySelector('[data-act=start-import]')]),
          [...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent)), document.querySelectorAll('#dci-ocr .dci-ocr-card').length,
          [...document.querySelectorAll('#dci-ocr [data-ocr-discogs]')].map(x => x.textContent.trim())]""")
        dg = [u for u in reqs if 'discogs.com' in u]
        print('B) Dashboard:', b1, '| Discogs:', dg[:3])
        results.append(b1[0] and len(b1[1]) == 1 and b1[1][0][0].startswith('The import of this release has not started – the text read from the cover art') and b1[1][0][1]
                       and not b1[2] and b1[3] == 5 and b1[4] == ['Load Discogs images (r%s)' % H.DISCOGS_ID] and not dg)
        pg.uncheck('#dci-ocr [data-ocr-framefirst]')
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=20000)
        c0 = pg.evaluate("!!document.querySelector('#dci-ocr [data-ocr=supp]')")
        pg.click('#dci-ocr [data-ocr=import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].some(li => /Import complete/.test(li.textContent))", 90)
        pg.wait_for_timeout(1000)
        c1 = pg.evaluate("""[document.querySelector('[data-el=source]').innerText.replace(/\\s+/g, ' ').trim(), [...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim()),
          [...document.querySelectorAll('[data-el=msgs] .dci-msg')].some(m => /has not started/.test(m.textContent))]""")
        dg = [u for u in reqs if 'discogs.com' in u]
        print('C) Quelle:', c1[0][:120], '| Einträge:', c1[1][:6], '| Hinweis noch da:', c1[2], '| Ergänzen vorher:', c0, '| Discogs:', dg[:3])
        results.append('Cover Art Archive images (Back, Booklet, Tray), read with text recognition' in c1[0] and 'j4vaman' in c1[1] and not c1[2] and not c0 and not dg)
        H.open_settings(pg, 'beta')
        pg.uncheck('[data-el=settings] [data-set=beta-ocr]')
        pg.wait_for_timeout(300)
        d1 = pg.evaluate("document.getElementById('dci-open-ocr').hidden")
        print('D) Beta aus – Knopf weg:', d1)
        results.append(d1)
        print('Fehler:', errs0, errs)
        results.append(not errs0 and not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrpeek():
    """[3.34.9] Images in their proportions, larger on mouse-over (collected item 129; maintainer: "nicht alle Bilder sind
    quadratisch! alle Bildverhältnisse müssen angezeigt werden. und bei Mouseover etwas größere darstellung.", "gleich hohe /
    breite kacheln").
    A) The tiles of the images are alike (square), each image whole in its tile (contain, nothing cut off).
    B) The mouse rests on the Booklet (1246 × 1634): after a short pause (300 ms) its larger view beside the tile – the 1200 px image of
       the Cover Art Archive, in its proportions, its longer side 480 px; the mouse leaves: gone.
    C) In the frames step the small images beside the view are whole too and show the larger view; an own file (300 × 800)
       is shown larger (480 px high)."""
    results = []
    PEEK = """(() => { const el = document.getElementById('dci-ocr-peek'); if (!el || el.hidden) return null; const i = el.querySelector('img'); const r = el.getBoundingClientRect();
      return { src: i.getAttribute('src'), w: Math.round(i.getBoundingClientRect().width), h: Math.round(i.getBoundingClientRect().height), left: Math.round(r.left), right: Math.round(r.right),
        label: el.querySelector('span').textContent }; })()"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card img', timeout=10000)
        pg.wait_for_timeout(500)
        a = pg.evaluate("""[...document.querySelectorAll('#dci-ocr .dci-ocr-card img')].map(i => { const r = i.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), getComputedStyle(i).objectFit]; })""")
        print('A) Kacheln:', a)
        results.append(len(a) == 5 and len({(w, h) for w, h, _ in a}) == 1 and a[0][0] == a[0][1] and all(f == 'contain' for _, _, f in a))
        card = pg.locator('#dci-ocr .dci-ocr-card img').nth(2)
        card.hover()
        pg.wait_for_timeout(100)
        b0 = pg.evaluate(PEEK)
        pg.wait_for_timeout(700)
        b1 = pg.evaluate(PEEK)
        cr = card.bounding_box()
        pg.mouse.move(5, 5)
        pg.wait_for_timeout(200)
        b2 = pg.evaluate(PEEK)
        print('B) sofort:', b0, '| nach der Pause:', b1, '| Kachel rechts:', round(cr['x'] + cr['width']), '| weg:', b2)
        # (b0: right after the mouse came – not checked, a slow machine may need longer than the pause to get there)
        results.append(b1 and b1['src'].endswith('/13-1200.jpg') and b1['h'] == 480 and abs(b1['w'] - round(480 * 1246 / 1634)) <= 2
                       and (b1['left'] >= cr['x'] + cr['width'] or b1['right'] <= cr['x']) and b1['label'] == 'Booklet' and b2 is None)
        # C) an own file and the frames step
        pg.set_input_files('#dci-ocr [data-ocr-files]', files=[{'name': 'narrow.png', 'mimeType': 'image/png', 'buffer': H.png_of(300, 800)}])
        pg.wait_for_timeout(300)
        pg.locator('#dci-ocr .dci-ocr-owncard img').hover()
        pg.wait_for_timeout(800)
        c1 = pg.evaluate(PEEK)
        pg.mouse.move(5, 5)
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)
        th = pg.locator('#dci-ocr .dci-ocr-thumb img').nth(1)
        th.hover()
        pg.wait_for_timeout(800)
        c2 = pg.evaluate(PEEK)
        c3 = pg.evaluate("getComputedStyle(document.querySelector('#dci-ocr .dci-ocr-thumb img')).objectFit")
        print('C) eigene Datei:', c1, '| Rahmen-Schritt:', c2, c3)
        results.append(c1 and c1['src'].startswith('blob:') and c1['h'] == 480 and c1['w'] == 180 and c2 and c2['src'].endswith('-1200.jpg') and c3 == 'contain')
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrload():
    """[3.34.10] Loading the images: how far, and ahead (collected item 128; maintainer: "Fortschrittsanzeige beim Laden der
    Bilder", "überall", "ja, aber wenn etwas abgehakt wird und noch nicht geladen wird soll das natürlich aus der queue raus",
    "das vorladen soll ein und ausstellbar sein in den einstellungen").
    A) The window opened: the previews counted ("Previews: 0 of 5 loaded") until they are there; the three images ticked are
       loaded ahead, two at a time – Back and Booklet "loading …", Tray "waiting to load"; Front and Medium nothing.
    B) Tray unticked: out of the queue, never asked for; Booklet unticked while it loads ahead: it stops; Back comes: "loaded".
    C) ⚙ Settings → Beta "Load the images ticked ahead" off (stored): opened again, nothing is loaded ahead; the frames step
       loads the image itself and shows it loading in the view, then draws it."""
    results = []
    held = []
    CARD = "(() => Object.fromEntries([...document.querySelectorAll('#dci-ocr .dci-ocr-card')].map(c => [c.querySelector('.dci-ocr-type').textContent.trim(), (c.querySelector('.dci-ocr-load:not([hidden]) .dci-ocr-loadtext') || {}).textContent || ''])))()"
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        ctx.route(re.compile(r'https://coverartarchive\.org/release/[^/]+/\d+(-250)?\.jpg$'), lambda r: held.append(r))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        pg.wait_for_timeout(600)
        orig = lambda: sorted(r.request.url.rsplit('/', 1)[1] for r in held if not r.request.url.endswith('-250.jpg'))
        a = [pg.evaluate("(document.querySelector('#dci-ocr [data-ocr-previews]:not([hidden])') || {}).textContent || ''"), pg.evaluate(CARD), orig()]
        print('A) Vorschau:', a[0], '| Kacheln:', a[1], '| Originale angefragt:', a[2])
        results.append(a[0] == 'Previews: 0 of 5 loaded' and a[1] == {'Front': '', 'Back': 'loading …', 'Booklet': 'loading …', 'Tray': 'waiting to load', 'Medium': ''}
                       and a[2] == ['12.jpg', '13.jpg'])
        pg.uncheck('#dci-ocr [data-ocr-sel="3"]')
        pg.wait_for_timeout(200)
        pg.uncheck('#dci-ocr [data-ocr-sel="2"]')
        pg.wait_for_timeout(300)
        b1 = pg.evaluate(CARD)
        for r in [r for r in held if r.request.url.endswith('/12.jpg') or r.request.url.endswith('-250.jpg')]:
            r.fallback()
        pg.wait_for_timeout(800)
        b2 = [pg.evaluate(CARD), orig(), pg.evaluate("(document.querySelector('#dci-ocr [data-ocr-previews]:not([hidden])') || {}).textContent || ''")]
        print('B) abgehakt:', b1, '| Back da:', b2)
        results.append(b1 == {'Front': '', 'Back': 'loading …', 'Booklet': '', 'Tray': '', 'Medium': ''} and b2[0]['Back'] == 'loaded' and b2[0]['Booklet'] == ''
                       and b2[1] == ['12.jpg', '13.jpg'] and b2[2] == '')
        pg.click('#dci-ocr [data-ocr=close]')
        # C) loading ahead off
        held.clear()
        H.open_settings(pg, 'beta')
        c0 = pg.evaluate("[!!document.querySelector('[data-el=settings] [data-set=ocr-preload]'), document.querySelector('[data-el=settings] [data-set=ocr-preload]').checked]")
        pg.uncheck('[data-el=settings] [data-set=ocr-preload]')
        pg.wait_for_timeout(200)
        stored = pg.evaluate("localStorage.getItem('dci-ocr-preload')")
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        pg.wait_for_timeout(600)
        c1 = [orig(), pg.evaluate(CARD)]
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr .dci-ocr-viewwait .dci-ocr-load:not([hidden])', timeout=10000)
        c2 = [pg.evaluate("document.querySelector('#dci-ocr .dci-ocr-viewwait').innerText.replace(/\\s+/g, ' ').trim()"), orig()]
        for r in list(held):
            r.fallback()
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)
        print('C) Schalter:', c0, stored, '| geöffnet:', c1, '| Rahmen-Schritt:', c2)
        results.append(c0 == [True, True] and stored == 'false' and c1[0] == [] and set(c1[1].values()) == {''}
                       and c2[0] == 'Loading the image … loading …' and c2[1] == ['12.jpg'])
        print('Fehler:', errs)
        results.append(not errs)
        for r in held:
            try:
                r.abort()
            except Exception:
                pass
        # requests the page gave up while held: no handler left waiting for them
        ctx.unroute_all(behavior='ignoreErrors')
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)


def case_ocrthumbs():
    """[3.34.13] The images beside the frames clicked (collected item 132; maintainer: "im draw a frame screen möchte ich die
    bilder oben durch anklicken anwählen zum frame drawen können"; before, a click on them went nowhere).
    A) Frames for the Back, Booklet, Tray: a click on the Tray shows it ("image 3 of 3 · Tray", marked as current); a frame drawn
       on it.
    B) The Booklet chosen with the keyboard (Enter on its small image), then the Back by a click: each shown; the Tray keeps its
       frame.
    C) Read: the Back and the Booklet whole, of the Tray only its frame (×3: a small image)."""
    results = []
    HEAD = "[document.querySelector('#dci-ocr .dci-ocr-head .dci-sub').textContent.trim(), [...document.querySelectorAll('#dci-ocr .dci-ocr-thumb')].map(t => [t.getAttribute('aria-current'), t.innerText.replace(/\\s+/g, ' ').trim()])]"
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
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)

        def shown(what):
            H.wait_for(pg, "(() => { const h = document.querySelector('#dci-ocr .dci-ocr-head .dci-sub'); return h && h.textContent.includes(%s) && !!document.querySelector('#dci-ocr [data-ocr-view]'); })()" % json.dumps(what), 15)
            pg.wait_for_timeout(150)
            return pg.evaluate(HEAD)
        a0 = pg.evaluate(HEAD)
        pg.click('#dci-ocr [data-ocr-cur="2"]')
        a1 = shown('Tray')
        box = pg.locator('#dci-ocr [data-ocr-view]').bounding_box()
        f = box['width'] / pg.evaluate("document.querySelector('#dci-ocr [data-ocr-view]').width")
        pg.mouse.move(box['x'] + 50 * f, box['y'] + 50 * f)
        pg.mouse.down()
        for k in range(1, 6):
            pg.mouse.move(box['x'] + (50 + 400 * k / 5) * f, box['y'] + (50 + 100 * k / 5) * f)
        pg.mouse.up()
        pg.wait_for_timeout(150)
        a2 = pg.evaluate(HEAD)
        print('A) zuerst:', a0, '| Tray angeklickt:', a1, '| Rahmen:', a2[1][2])
        results.append(a0[0] == 'frames · image 1 of 3 · Back' and a1[0] == 'frames · image 3 of 3 · Tray'
                       and [x[0] for x in a1[1]] == ['false', 'false', 'true'] and a2[1][2][1] == 'Tray 1 frame')
        pg.focus('#dci-ocr [data-ocr-cur="1"]')
        pg.keyboard.press('Enter')
        b1 = shown('Booklet')
        pg.click('#dci-ocr [data-ocr-cur="0"]')
        b2 = shown('Back')
        print('B) Tastatur:', b1[0], '| Klick:', b2[0], '| Tray:', b2[1][2])
        results.append(b1[0] == 'frames · image 2 of 3 · Booklet' and b2[0] == 'frames · image 1 of 3 · Back' and b2[1][2][1] == 'Tray 1 frame')
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-text]', timeout=20000)
        c = pg.evaluate('window.__ocr.calls')
        print('C) gelesen:', c)
        results.append(c == [[1500, 1500], [1246, 1634], [1200, 300]])
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

def case_ocrzoom():
    """[3.34.11] Each part read beside its text, with zoom (collected item 130; maintainer: "kann der vergrößerte Bildbereich
    nach der Auswahl neben dem erkannten text dargestellt werden? mit zoom in funktion?", "je Rahmen").
    A) The Back with two frames, the Booklet whole: in "check the text" the window is wider; the Back has two parts ("Frame 1",
       "Frame 2"), each its part of the image (fitted, the image there) beside its own text; the Booklet one part.
    B) + zooms in (×1.5), − back, Ctrl + wheel and a double click zoom in at the mouse, ⤢ fits again.
    C) A part's text changed: imported with the others in their order."""
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        texts = [{'text': 'Music by Ann Lee\n', 'words': []}, {'text': 'Drums – Drum Guy\n', 'words': []}, {'text': 'Mastered by Bob Producer\n', 'words': []}]
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps(texts))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        pg.uncheck('#dci-ocr [data-ocr-sel="3"]')
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)

        def drag(x0, y0, x1, y1):
            box = pg.locator('#dci-ocr [data-ocr-view]').bounding_box()
            w = pg.evaluate("document.querySelector('#dci-ocr [data-ocr-view]').width")
            f = box['width'] / w
            pg.mouse.move(box['x'] + x0 * f, box['y'] + y0 * f)
            pg.mouse.down()
            for k in range(1, 6):
                pg.mouse.move(box['x'] + (x0 + (x1 - x0) * k / 5) * f, box['y'] + (y0 + (y1 - y0) * k / 5) * f)
            pg.mouse.up()
            pg.wait_for_timeout(150)
        drag(56, 56, 504, 168)
        drag(56, 336, 280, 448)
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-zoom]', timeout=20000)
        pg.wait_for_timeout(300)
        A = """(() => { const el = document.getElementById('dci-ocr'); const parts = [...el.querySelectorAll('[data-ocr-part]')];
          return { wide: el.classList.contains('dci-ocr-wide'), width: Math.round(el.getBoundingClientRect().width),
            parts: parts.map(p => { const c = p.querySelector('canvas'); const t = p.querySelector('textarea'); const g = c.getContext('2d');
              const d = g.getImageData(Math.round(c.width / 2), Math.round(c.height / 2), 1, 1).data; const cr = c.getBoundingClientRect(), tr = t.getBoundingClientRect();
              return [p.dataset.ocrPart, (p.querySelector('.dci-ocr-parttext strong') || {}).textContent || '', t.value, [d[0], d[1], d[2]], Math.round(cr.right) <= Math.round(tr.left), Number(c.dataset.k).toFixed(3)]; }) }; })()"""
        a = pg.evaluate(A)
        print('A) breit:', a['wide'], a['width'], '| Teile:', a['parts'])
        results.append(a['wide'] and a['width'] > 1100 and [x[:3] for x in a['parts']] == [['0:0', 'Frame 1', 'Music by Ann Lee'], ['0:1', 'Frame 2', 'Drums – Drum Guy'], ['1:0', '', 'Mastered by Bob Producer']]
                       and all(x[3] == [240, 236, 228] and x[4] for x in a['parts']))
        K = "Number(document.querySelector('#dci-ocr [data-ocr-zoom=\"1:0\"]').dataset.k)"
        k0 = pg.evaluate(K)
        pg.click('#dci-ocr [data-ocr-z=in][data-ocr-zfor="1:0"]')
        k1 = pg.evaluate(K)
        pg.click('#dci-ocr [data-ocr-z=out][data-ocr-zfor="1:0"]')
        k2 = pg.evaluate(K)
        c = pg.locator('#dci-ocr [data-ocr-zoom="1:0"]')
        bb = c.bounding_box()
        pg.mouse.move(bb['x'] + bb['width'] / 3, bb['y'] + bb['height'] / 3)
        pg.keyboard.down('Control')
        pg.mouse.wheel(0, -100)
        pg.keyboard.up('Control')
        pg.wait_for_timeout(150)
        k3 = pg.evaluate(K)
        c.dblclick(position={'x': bb['width'] / 2, 'y': bb['height'] / 2})
        k4 = pg.evaluate(K)
        pg.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)
        pg.mouse.down()
        pg.mouse.move(bb['x'] + bb['width'] / 2 + 60, bb['y'] + bb['height'] / 2 + 40, steps=4)
        pg.mouse.up()
        pg.click('#dci-ocr [data-ocr-z=fit][data-ocr-zfor="1:0"]')
        k5 = pg.evaluate(K)
        print('B) Zoom: Einpassen', round(k0, 3), '| +', round(k1, 3), '| −', round(k2, 3), '| Strg+Rad', round(k3, 3), '| Doppelklick', round(k4, 3), '| ⤢', round(k5, 3))
        results.append(abs(k1 - k0 * 1.5) < 1e-6 and abs(k2 - k0) < 1e-6 and abs(k3 - k0 * 1.25) < 1e-6 and abs(k4 - k0 * 2.5) < 1e-6 and abs(k5 - k0) < 1e-6)
        pg.fill('#dci-ocr [data-ocr-text="0:1"]', 'Drums – Drum Guy\nBass – Bass Man')
        pg.click('#dci-ocr [data-ocr=import]')
        H.wait_for(pg, "[...document.querySelectorAll('#dci-log li')].filter(li => /Import complete/.test(li.textContent)).length >= 2", 90)
        pg.wait_for_timeout(800)
        c1 = pg.evaluate("[...document.querySelectorAll('section.dci-group .dci-gname strong')].map(x => x.textContent.trim())")
        print('C) Einträge:', c1)
        results.append(all(n in c1 for n in ('Ann Lee', 'Drum Guy', 'Bass Man', 'Bob Producer')))
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)



def case_ocrlocate():
    """[3.34.12] Where a line or a word is in the image (collected item 130b; maintainer: "klingt gut, bitte einbauen").
    A) The Back with a frame (on its canvas at 150, 150; read as it is), the Tray whole (500 px: read ×3). "Bob", read
       uncertainly twice, clicked: its first place selected in the text, marked in the image and zoomed in on; clicked again:
       its second place.
    B) The caret in the Back's text: Ctrl + Home – the first line marked where Tesseract read it (moved into sight in the zoomed
       view), ↓ – the second (wider than the view: its start in sight); ⤢: fitted, the mark still drawn there; a letter taken away: still the line; the line replaced by
       other words: no mark.
    C) A click into the Tray's text: its line marked, its place read ×3 brought back to the canvas; the dash corrected in the
       text ("Drums – Drum Guy") and the line still found.
    D) A PDF page read from its own text: the caret in its third line marks that line's place on the page drawn."""
    results = []
    ZQ = """((key) => { const c = document.querySelector(`#dci-ocr [data-ocr-zoom="${key}"]`); const ta = document.querySelector(`#dci-ocr [data-ocr-text="${key}"]`);
      const n = (x) => (x || '').split(',').map(Number);
      const out = { mark: c.dataset.mark ? n(c.dataset.mark) : null, kind: c.dataset.markKind || '', k: Number(c.dataset.k), view: n(c.dataset.view), box: n(c.dataset.box),
        sel: [ta.selectionStart, ta.selectionEnd], active: document.activeElement === ta };
      if (out.mark) { const [mx, my, mw, mh] = out.mark; const [vx, vy] = out.view; const dpr = c.width / c.clientWidth;
        const px = c.getContext('2d').getImageData(Math.round((mx + mw / 2 - vx) * out.k * dpr), Math.round((my + mh / 2 - vy) * out.k * dpr), 1, 1).data;
        out.px = [px[0], px[1], px[2]]; }
      return out; })"""
    inside = lambda z: z['mark'] and z['view'] and z['mark'][0] >= z['view'][0] - 1 and z['mark'][1] >= z['view'][1] - 1 and z['mark'][0] + z['mark'][2] <= z['view'][0] + z['view'][2] + 1 and z['mark'][1] + z['mark'][3] <= z['view'][1] + z['view'][3] + 1
    # a line wider than the view: its start in sight
    start = lambda z: z['mark'] and z['view'] and z['view'][0] - 1 <= z['mark'][0] < z['view'][0] + z['view'][2] and z['mark'][1] >= z['view'][1] - 1 and z['mark'][1] + z['mark'][3] <= z['view'][1] + z['view'][3] + 1
    with sync_playwright() as p:
        b = p.chromium.launch(args=H.LAUNCH_ARGS)
        H.COVER_ART = list(ART)
        ctx = H.new_context(b)
        beta_on(ctx)
        texts = [{'text': 'Music by Bob Lee\nMastered by Bob Producer\n',
                  'lines': [{'text': 'Music by Bob Lee\n', 'bbox': {'x0': 20, 'y0': 30, 'x1': 600, 'y1': 80}},
                            {'text': 'Mastered by Bob Producer\n', 'bbox': {'x0': 20, 'y0': 150, 'x1': 900, 'y1': 200}}],
                  'words': [{'text': 'Music', 'confidence': 95, 'bbox': {'x0': 20, 'y0': 30, 'x1': 200, 'y1': 80}},
                            {'text': 'Bob', 'confidence': 40, 'bbox': {'x0': 300, 'y0': 30, 'x1': 380, 'y1': 80}},
                            {'text': 'Bob', 'confidence': 45, 'bbox': {'x0': 400, 'y0': 150, 'x1': 480, 'y1': 200}}]},
                 {'text': 'Drums - Drum Guy\n', 'lines': [{'text': 'Drums - Drum Guy\n', 'bbox': {'x0': 300, 'y0': 600, 'x1': 900, 'y1': 690}}], 'words': []}]
        ctx.add_init_script('window.__ocrTexts = %s;' % json.dumps(texts))
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr .dci-ocr-card', timeout=10000)
        pg.uncheck('#dci-ocr [data-ocr-sel="2"]')
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=10000)
        box = pg.locator('#dci-ocr [data-ocr-view]').bounding_box()
        f = box['width'] / pg.evaluate("document.querySelector('#dci-ocr [data-ocr-view]').width")
        pg.mouse.move(box['x'] + 56 * f, box['y'] + 56 * f)
        pg.mouse.down()
        for k in range(1, 6):
            pg.mouse.move(box['x'] + (56 + 448 * k / 5) * f, box['y'] + (56 + 112 * k / 5) * f)
        pg.mouse.up()
        pg.wait_for_timeout(150)
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-zoom="1:0"]', timeout=20000)
        pg.wait_for_timeout(300)
        z0 = pg.evaluate(ZQ, '0:0')
        pg.click('#dci-ocr [data-ocr-word="Bob"][data-ocr-in="0:0"]')
        z1 = pg.evaluate(ZQ, '0:0')
        pg.click('#dci-ocr [data-ocr-word="Bob"][data-ocr-in="0:0"]')
        z2 = pg.evaluate(ZQ, '0:0')
        print('A) Teil', z0['box'], 'Einpassen', round(z0['k'], 3), '| Bob 1:', z1['sel'], z1['kind'], z1['mark'], round(z1['k'], 3), inside(z1), z1['px'],
              '| Bob 2:', z2['sel'], z2['mark'], inside(z2))
        results.append(z0['box'] == [150, 150, 1200, 300] and z0['mark'] is None
                       and z1['active'] and z1['sel'] == [9, 12] and z1['kind'] == 'word' and z1['mark'] == [450, 180, 80, 50] and z1['k'] > z0['k'] * 1.5 and inside(z1)
                       and z1['px'] != [240, 236, 228] and z2['sel'] == [29, 32] and z2['mark'] == [550, 300, 80, 50] and inside(z2))
        ta = '#dci-ocr [data-ocr-text="0:0"]'
        pg.focus(ta)
        pg.keyboard.press('Control+Home')
        b1 = pg.evaluate(ZQ, '0:0')
        pg.keyboard.press('ArrowDown')
        b2 = pg.evaluate(ZQ, '0:0')
        pg.click('#dci-ocr [data-ocr-z=fit][data-ocr-zfor="0:0"]')
        b3 = pg.evaluate(ZQ, '0:0')
        pg.focus(ta)
        pg.keyboard.press('Control+End')
        pg.keyboard.press('Backspace')
        b4 = pg.evaluate(ZQ, '0:0')
        pg.keyboard.press('Shift+Home')
        pg.keyboard.type('Liner notes by somebody else')
        b5 = pg.evaluate(ZQ, '0:0')
        print('B) Zeile 1:', b1['kind'], b1['mark'], inside(b1), '| Zeile 2:', b2['mark'], b2['view'], start(b2), '| ⤢:', round(b3['k'], 3), b3['mark'], b3['px'],
              '| ohne r:', b4['mark'], '| andere Wörter:', b5['mark'])
        results.append(b1['kind'] == 'line' and b1['mark'] == [170, 180, 580, 50] and inside(b1) and b2['mark'] == [170, 300, 880, 50] and not inside(b2) and start(b2)
                       and abs(b3['k'] - z0['k']) < 1e-6 and b3['mark'] == [170, 300, 880, 50] and b3['px'] != [240, 236, 228]
                       and b4['mark'] == [170, 300, 880, 50] and b5['mark'] is None)
        pg.click('#dci-ocr [data-ocr-text="1:0"]', position={'x': 12, 'y': 8})
        c1 = pg.evaluate(ZQ, '1:0')
        tv = pg.input_value('#dci-ocr [data-ocr-text="1:0"]')
        print('C) Tray:', repr(tv), c1['kind'], c1['mark'], c1['box'])
        results.append(tv == 'Drums – Drum Guy' and c1['kind'] == 'line' and c1['mark'] == [100, 200, 200, 30] and c1['box'] == [0, 0, 500, 500])
        print('Fehler:', errs)
        results.append(not errs)
        pg.close()
        # D) a PDF page with its own text
        pdf = H.pdf_of([[(40, 380, 14, 'Booklet'), (40, 350, 12, 'Credits'), (60, 330, 12, 'Marc D. Rusch - double bass')]])
        H.COVER_ART = []
        pg, errs = H.open_mb_edit(ctx, companion=False)
        pg.on('dialog', lambda d: d.accept())
        pg.wait_for_selector('#dci-open', timeout=20000)
        H.open_dashboard(pg)
        H.src_menu(pg, 'ocr-open')
        pg.wait_for_selector('#dci-ocr [data-ocr-files]', state='attached', timeout=10000)
        pg.set_input_files('#dci-ocr [data-ocr-files]', files=[{'name': 'credits.pdf', 'mimeType': 'application/pdf', 'buffer': pdf}])
        H.wait_for(pg, "document.querySelectorAll('#dci-ocr .dci-ocr-owncard').length === 1 && !document.querySelector('#dci-ocr [data-ocr-pdfstatus]')", 30)
        pg.click('#dci-ocr [data-ocr=frames]')
        pg.wait_for_selector('#dci-ocr [data-ocr-view]', timeout=20000)
        pg.click('#dci-ocr [data-ocr=run]')
        pg.wait_for_selector('#dci-ocr [data-ocr-zoom="0:0"]', timeout=20000)
        pg.wait_for_timeout(300)
        pg.focus('#dci-ocr [data-ocr-text="0:0"]')
        pg.keyboard.press('Control+End')
        d1 = pg.evaluate(ZQ, '0:0')
        tv = pg.input_value('#dci-ocr [data-ocr-text="0:0"]')
        k = d1['box'][2] / 420
        m = d1['mark'] or [0, 0, 0, 0]
        print('D) PDF:', repr(tv), '| Seite', d1['box'], 'Maßstab', round(k, 3), '| Zeile 3:', d1['kind'], m, '| erwartet x', round(60 * k), 'Grundlinie', round(90 * k))
        results.append(tv == 'Booklet\nCredits\nMarc D. Rusch – double bass' and d1['kind'] == 'line' and abs(m[0] - 60 * k) < 2 * k and m[1] < 90 * k < m[1] + m[3]
                       and 10 * k < m[3] < 16 * k and m[2] > 100 * k)
        print('Fehler:', errs)
        results.append(not errs)
        b.close()
    print('Ergebnis:', 'OK' if all(results) else 'FEHLER', results)

run_cases(globals())
