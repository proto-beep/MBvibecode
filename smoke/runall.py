#!/usr/bin/env python3
"""Runs the whole suite and says truthfully how it went (Credits Importer 3.160.0, review run 3).

    python3 runall.py [-j 5] [--timeout 2700] [--out DIR] [t_file.py …]

Each t_*.py runs as a process of its own (five at a time, the longest first), its output goes to <out>/<file>.log.
A file counts as passed only when all of this holds:
  - the process ended by itself (not by the time limit) with exit code 0,
  - its last line "Ergebnis: …" says OK,
  - no case of it ended "== name: FEHLER (…)",
  - a file of cases (caserun.py) printed its summary "Fälle: n in … s" – without it the file was cut off.
Until 3.159.0 the suite was run by a script that took the last "Ergebnis" line of a log as the file's result: a file cut
off by the time limit then counted as passed with the result of its last finished case (t_entries.py and t_ui_settings.py
were cut off for weeks, ten failing cases unseen).

The cases that failed run once more at the end, one file at a time with nothing else running (five browsers at a time can make
a case of timing fail): green then, they are named "WACKELIG" and the file passes.

The end: one line per file that did not pass (its failed cases, or why), then "Suite: OK" or "Suite: FEHLER" (with the
cases that were wackelig), and the exit code says the same (0 / 1).
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LONG_FIRST = ['t_entries.py', 't_ui_settings.py', 't_companion_discogs.py', 't_works_more.py', 't_dates_matrix.py', 't_works_matrix.py', 't_notes_dates.py']


def run_one(name, out, limit):
    log = os.path.join(out, f'{name}.log')
    start = time.time()
    with open(log, 'w', encoding='utf-8') as f:
        try:
            code = subprocess.run([sys.executable, name], cwd=HERE, stdout=f, stderr=subprocess.STDOUT, timeout=limit).returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    text = open(log, encoding='utf-8', errors='replace').read()
    last = (re.findall(r'^Ergebnis: .*$', text, re.M) or [''])[-1]
    failed = re.findall(r'^== (\S+): FEHLER \(', text, re.M)
    cases = len(re.findall(r'^== \S+ =+$', text, re.M))
    summary = bool(re.search(r'^Fälle: \d+ in ', text, re.M))
    uses_cases = 'run_cases(' in open(os.path.join(HERE, name), encoding='utf-8').read()
    why = []
    if code == 'timeout':
        why.append(f'cut off after {limit} s ({cases} cases started)')
    elif code != 0:
        why.append(f'exit code {code}')
    if failed:
        why.append('failed: ' + ', '.join(failed))
    if not last.startswith('Ergebnis: OK'):
        why.append('last result: ' + (last[:80] or 'none'))
    if uses_cases and not summary and code != 'timeout':
        why.append('no summary line')
    return name, why, cases, round(time.time() - start), failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-j', type=int, default=5)
    ap.add_argument('--timeout', type=int, default=2700)
    ap.add_argument('--out', default=os.path.join(HERE, 'out'))
    ap.add_argument('files', nargs='*')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = a.files or sorted(f for f in os.listdir(HERE) if re.match(r'^t_\w+\.py$', f))
    files.sort(key=lambda f: (LONG_FIRST.index(f) if f in LONG_FIRST else len(LONG_FIRST), f))
    bad = []
    again = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.j) as ex:
        for name, why, cases, secs, failed in ex.map(lambda f: run_one(f, a.out, a.timeout), files):
            print(f'{name}: {"OK" if not why else "FEHLER"} ({cases} cases, {secs} s)' + (f' – {"; ".join(why)}' if why else ''), flush=True)
            if why:
                bad.append(name)
                if failed and not any(w.startswith(('cut off', 'exit code 2')) for w in why):
                    again.append((name, failed))
    # the failed cases once more, one file at a time with nothing else running: five browsers at a time can make a case of timing fail.
    # A case green then is named "WACKELIG" – the suite counts as passed, and says so.
    flaky = []
    for name, failed in again:
        log = os.path.join(a.out, f'{name}.again.log')
        with open(log, 'w', encoding='utf-8') as f:
            try:
                code = subprocess.run([sys.executable, name] + failed, cwd=HERE, stdout=f, stderr=subprocess.STDOUT, timeout=a.timeout, env={**os.environ, 'DCI_RETRY': '0'}).returncode
            except subprocess.TimeoutExpired:
                code = 'timeout'
        text = open(log, encoding='utf-8', errors='replace').read()
        still = re.findall(r'^== (\S+): FEHLER \(', text, re.M)
        if code == 0 and not still and re.search(r'^Fälle: \d+ in ', text, re.M):
            bad.remove(name)
            flaky.append(f'{name} ({", ".join(failed)})')
            print(f'{name}: WACKELIG – alone the cases passed: {", ".join(failed)}', flush=True)
        else:
            print(f'{name}: FEHLER also alone – {", ".join(still) or code}', flush=True)
    print(f'Suite: {"OK" if not bad else "FEHLER"} – {len(files) - len(bad)} of {len(files)} files passed' + (f'; not passed: {", ".join(bad)}' if bad else '')
          + (f'; wackelig: {"; ".join(flaky)}' if flaky else ''))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
