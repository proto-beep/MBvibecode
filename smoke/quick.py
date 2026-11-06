"""[3.72.0] The quick tier (collected item Z-TST): the checks that need no browser (but one page for the register) – a few
minutes instead of the whole suite, for a first look after a change.

- `t_static.py` (all its cases: the texts, the connections, the mapping file …),
- `t_register.py` (the rules' register against its golden file; one page),
- every case of the other files that only runs the script in Node (its body, or a helper of its file it calls, runs `node`;
  it opens no browser).

`python3 quick.py` runs them; `python3 quick.py --list` only names them. The last line is "Ergebnis: OK [n Dateien]" or
"Ergebnis: FEHLER [files]", as the suite's runner reads it. The whole suite still decides (see README-tests.md).
"""
import ast
import pathlib
import subprocess
import sys
import time
import warnings

HERE = pathlib.Path(__file__).resolve().parent
WHOLE = ['t_static.py', 't_register.py']


BROWSER = ('sync_playwright', 'open_mb_edit', 'launch_own')


def node_cases(path):
    """The cases of a file that only run Node: `['node'` in the body or in a helper of the file it calls, no browser."""
    src = path.read_text()
    out = []
    warnings.filterwarnings('ignore', category=SyntaxWarning)  # (escapes in the test files' JS strings)
    tree = ast.parse(src)
    funcs = [fn for fn in tree.body if isinstance(fn, ast.FunctionDef)]
    helpers = {fn.name for fn in funcs if not fn.name.startswith('case_') and "['node'" in (ast.get_source_segment(src, fn) or '')}
    for fn in funcs:
        if not fn.name.startswith('case_'):
            continue
        body = ast.get_source_segment(src, fn) or ''
        calls = {n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        if ("['node'" in body or calls & helpers) and not any(b in body for b in BROWSER):
            out.append(fn.name[5:])
    return out


def plan():
    runs = [[f] for f in WHOLE if (HERE / f).exists()]
    for path in sorted(HERE.glob('t_*.py')):
        if path.name in WHOLE:
            continue
        cases = node_cases(path)
        if cases:
            runs.append([path.name, *cases])
    return runs


def main():
    runs = plan()
    if '--list' in sys.argv:
        for r in runs:
            print(' '.join(r))
        return
    failed = []
    t0 = time.time()
    for r in runs:
        try:
            p = subprocess.run([sys.executable, *r], cwd=HERE, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            print(f'{" ".join(r)}: Ergebnis: FEHLER [timeout]')
            failed.append(r[0])
            continue
        last = [x for x in p.stdout.splitlines() if x.startswith('Ergebnis')]
        verdict = last[-1] if last else f'Ergebnis: FEHLER [exit {p.returncode}]'
        print(f'{" ".join(r)}: {verdict}')
        if not verdict.startswith('Ergebnis: OK') or p.returncode:
            failed.append(r[0])
            print((p.stdout + p.stderr)[-1500:])
    print(f'Zeit: {round(time.time() - t0)} s')
    print('Ergebnis:', f'FEHLER {failed}' if failed else f'OK [{len(runs)} Dateien]')


if __name__ == '__main__':
    main()
