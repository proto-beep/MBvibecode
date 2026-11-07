"""[3.31.1] Cases of a test file (collected item 103).

A test file of a topic holds several cases, each a function `case_<name>()` – the body of what was one test file before,
unchanged. `run_cases(globals())` at the end of the file runs them one after another:

- one browser for the whole file: `sync_playwright()` in a case gives a stand-in whose `chromium.launch()` returns the
  shared browser (its `close()` closes only the contexts the case opened);
- what a case changes in the harness (Discogs data, MusicBrainz search results, relationship types, the shared storage of
  the userscript manager …) is set back after it, so no case sees what another one set;
- each case reports on its own ("== name: OK" / "== name: FEHLER", from its last line with "Ergebnis: …", as the suite's
  runner reads a test file); an exception ends only its case (the traceback is printed);
- the last line is "Ergebnis: OK [n cases]" or "Ergebnis: FEHLER [names]" (the suite's runner reads it);
- [3.77.0] a case that failed runs once more on its own: green then, it is "WACKELIG" (and named in the last line), not hidden
  (`DCI_RETRY=0`: no second run).

Only some cases: `python3 t_text_basics.py freetext names` (names without "case_").
"""
import copy
import os
import io
import sys
import time
import traceback
import types

import harness as H
from playwright.sync_api import sync_playwright as _real_sync_playwright

_STATE = {'pw': None, 'browser': None}


def _browser():
    if not _STATE['browser']:
        _STATE['pw'] = _real_sync_playwright().start()
        _STATE['browser'] = _STATE['pw'].chromium.launch(args=H.LAUNCH_ARGS)
    return _STATE['browser']


def launch_own(**kw):
    """[3.40.8] A browser of its own for a case that needs other launch options (overlay scroll bars, say); the case closes it."""
    _browser()
    return _STATE['pw'].chromium.launch(**kw)


class _BrowserProxy:
    """The shared browser as one case sees it: the contexts it opens are closed with `close()`."""

    def __init__(self, real):
        self._real = real
        self._contexts = []

    def new_context(self, *args, **kw):
        ctx = self._real.new_context(*args, **kw)
        self._contexts.append(ctx)
        return ctx

    def new_page(self, *args, **kw):
        ctx = self.new_context()
        return ctx.new_page(*args, **kw)

    @property
    def contexts(self):
        return [c for c in self._contexts if c in self._real.contexts]

    def close(self):
        for ctx in self._contexts:
            try:
                ctx.close()
            except Exception:
                pass
        self._contexts = []

    def __getattr__(self, name):
        return getattr(self._real, name)


class _BrowserType:
    def __init__(self, opened):
        self._opened = opened

    def launch(self, *args, **kw):
        proxy = _BrowserProxy(_browser())
        self._opened.append(proxy)
        return proxy

    def __getattr__(self, name):
        _browser()
        return getattr(_STATE['pw'].chromium, name)


class _Playwright:
    def __init__(self, opened):
        self.chromium = _BrowserType(opened)
        self._opened = opened

    def stop(self):
        """`PW.stop()` of a case: closes what the case opened – the shared browser keeps running."""
        for proxy in self._opened:
            proxy.close()
        self._opened.clear()

    def __getattr__(self, name):
        _browser()
        return getattr(_STATE['pw'], name)


class sync_playwright:  # noqa: N801 – stands in for playwright's own in the cases
    """`with sync_playwright() as p:` in a case: the shared browser (see above)."""

    opened = []

    def __enter__(self):
        return _Playwright(sync_playwright.opened)

    def __exit__(self, *exc):
        for proxy in sync_playwright.opened:
            proxy.close()
        sync_playwright.opened.clear()
        return False

    # `PW = sync_playwright().start()` … `PW.stop()` (some cases start it so)
    def start(self):
        return self.__enter__()

    def stop(self):
        self.__exit__(None, None, None)


# --- what the cases change in the harness -------------------------------------------------------------------------

def _snapshot():
    snap = {}
    for name, val in vars(H).items():
        if name.startswith('__'):
            continue
        saved = copy.deepcopy(val) if isinstance(val, (dict, list, set)) and not isinstance(val, types.ModuleType) else None
        snap[name] = (val, saved)
    return snap


def _restore(snap):
    for name in [n for n in vars(H) if not n.startswith('__') and n not in snap]:
        delattr(H, name)
    for name, (val, saved) in snap.items():
        if getattr(H, name, None) is not val:
            setattr(H, name, val)
        if saved is None:
            continue
        fresh = copy.deepcopy(saved)
        if isinstance(val, dict):
            val.clear()
            val.update(fresh)
        elif isinstance(val, list):
            val[:] = fresh
        elif isinstance(val, set):
            val.clear()
            val.update(fresh)
    # the shared storage of the userscript manager (the local server keeps it between pages)
    with H.STORE.lock:
        H.STORE.data.clear()
        H.STORE.changes.clear()


class _Tee(io.TextIOBase):
    def __init__(self, out):
        self.out = out
        self.lines = []
        self.buf = ''

    def write(self, s):
        self.out.write(s)
        self.buf += s
        while '\n' in self.buf:
            line, self.buf = self.buf.split('\n', 1)
            self.lines.append(line)
        return len(s)

    def flush(self):
        self.out.flush()


def run_cases(ns):
    """Runs the functions case_<name> of a test file (all, or those named on the command line)."""
    cases = [(n[5:], f) for n, f in ns.items() if n.startswith('case_') and callable(f)]
    want = [a.replace('case_', '') for a in sys.argv[1:]]
    if want:
        unknown = [w for w in want if w not in [n for n, _ in cases]]
        if unknown:
            print('Unbekannte Fälle:', unknown, '– vorhanden:', [n for n, _ in cases])
            sys.exit(2)
        cases = [(n, f) for n, f in cases if n in want]
    failed = []
    flaky = []
    t0 = time.time()

    def once(name, fn):
        """One run of a case: (OK, page errors in it)."""
        snap = _snapshot()
        tee = _Tee(sys.stdout)
        old = sys.stdout
        sys.stdout = tee
        ok = False
        n0 = len(H.PAGE_ERRORS)
        perr = 0
        try:
            fn()
            # as the suite's runner reads a test: its last line with "Ergebnis" (some say "[part] Ergebnis: OK …")
            result = [l for l in tee.lines + [tee.buf] if 'Ergebnis' in l]
            ok = bool(result) and 'Ergebnis: OK' in result[-1]
            if not result:
                print('(nichts zum Auswerten ausgegeben)')
        except Exception:
            traceback.print_exc(file=old)
        finally:
            sys.stdout = old
            for proxy in sync_playwright.opened:
                proxy.close()
            sync_playwright.opened.clear()
            perr = len(H.PAGE_ERRORS) - n0
            _restore(snap)
        return ok, perr

    retry_on = os.environ.get('DCI_RETRY', '1').strip().lower() not in ('0', 'false', 'no', 'off')
    retries_left = 3

    for name, fn in cases:
        print(f'\n== {name} ' + '=' * max(3, 70 - len(name)), flush=True)
        t1 = time.time()
        ok, perr = once(name, fn)
        # [3.77.0] (collected item Z-FLK) a case that failed runs once more on its own; green then: "wackelig", shown as such
        # (DCI_RETRY=0 / false / no / off: no second run). ((review) Not again: a case with an error of the page (a fault of the
        # script, not of the timing), one that took over 150 s, and after three second runs in a file.)
        if not ok and retry_on:
            took = time.time() - t1
            why = ('Fehler der Seite' if perr else f'{took:.0f} s – zu lang' if took > 150 else 'schon 3 Wiederholungen in der Datei' if retries_left <= 0 else '')
            if why:
                print(f'== {name}: nicht wiederholt ({why})', flush=True)
            else:
                retries_left -= 1
                print(f'== {name}: FEHLER beim 1. Lauf ({took:.0f} s) – noch einmal allein', flush=True)
                ok, perr = once(name, fn)
                if ok:
                    flaky.append(name)
                    print(f'== {name}: WACKELIG – beim 2. Lauf OK ({time.time() - t1:.0f} s für beide Läufe)', flush=True)
                    continue
        print(f'== {name}: {"OK" if ok else "FEHLER"} ({time.time() - t1:.0f} s)', flush=True)
        if not ok:
            failed.append(name)
    if _STATE['browser']:
        try:
            _STATE['browser'].close()
            _STATE['pw'].stop()
        except Exception as e:  # a case stopped playwright itself: reported, the results stand
            print('Browser beim Schließen:', e)
    print(f'\nFälle: {len(cases)} in {time.time() - t0:.0f} s')
    if flaky:
        print('Wackelig (beim 2. Lauf OK):', flaky)
    # (a file with failed cases: its last line names those only; the unsteady ones stand in the line "Wackelig" above it)
    print('Ergebnis:', 'OK' if not failed else 'FEHLER', (f'[{len(cases)} Fälle' + (f', wackelig: {", ".join(flaky)}' if flaky else '') + ']') if not failed else failed)
