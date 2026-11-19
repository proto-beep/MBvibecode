"""The storage keys of the Credits Importer, read from its code (F-STORAGEDOC, 3.171.0).

Usage: python3 tools/storage_keys.py            prints the table (Markdown)
       python3 tools/storage_keys.py --write    writes it into the README, between the two marks
       python3 tools/storage_keys.py --check    exit code 1 when the README's table is not the one of the code

The table lists every key the main script reads or writes in the browser's storage for musicbrainz.org – found where the code calls
readJson / writeJson / getItem / setItem / removeItem with a literal key or a constant "…_KEY" –, where it is kept, the tab of
⚙ Settings whose "↺ Defaults of this topic" resets it (TOPIC_KEYS), and the constant the code names it by. What a key does is said where
the README describes its setting; the table is the index.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'mb-vibecode-credits-importer.user.js')
BEGIN = '<!-- storage-keys:begin (written by tools/storage_keys.py – do not edit by hand) -->'
END = '<!-- storage-keys:end -->'
CALL = re.compile(r"\b(readJson|writeJson|getItem|setItem|removeItem)\(\s*(?:'(localStorage|sessionStorage)',\s*)?(?:'(dci-[a-z0-9:-]+)'|`(dci-[^`]+)`|([A-Z][A-Z0-9_]*_KEY)\b)")
STORE_OF_OBJECT = re.compile(r"\b(localStorage|sessionStorage)\.(?:getItem|setItem|removeItem)\(\s*(?:'(dci-[a-z0-9:-]+)'|`(dci-[^`]+)`|([A-Z][A-Z0-9_]*_KEY)\b)")


def shown(key):
    """A key built at run time: what is filled in, in angle brackets."""
    return re.sub(r'\$\{(\w+)[^}]*\}', lambda m: '<release>' if m.group(1) == 'releaseMbid' else f'<{m.group(1)}>', key)


def read_keys(src=None):
    """{key: {'store': set, 'const': name or '', 'topic': name or ''}} – as the code has them."""
    src = src if src is not None else open(SCRIPT, encoding='utf-8').read()
    consts = {}
    for name, a, b in re.findall(r"const ([A-Z][A-Z0-9_]*_KEY) = (?:'(dci-[a-z0-9:-]+)'|`(dci-[^`]+)`)", src):
        consts[name] = a or shown(b)
    keys = {}

    def add(key, store, const=''):
        k = keys.setdefault(key, {'store': set(), 'const': '', 'topic': ''})
        if store:
            k['store'].add(store)
        if const:
            k['const'] = const
    for _fn, store, lit, tpl, const in CALL.findall(src):
        key = lit or (shown(tpl) if tpl else consts.get(const))
        if key:
            add(key, store, const if const in consts else '')
    for store, lit, tpl, const in STORE_OF_OBJECT.findall(src):
        key = lit or (shown(tpl) if tpl else consts.get(const))
        if key:
            add(key, store, const if const in consts else '')
    # a constant the code only lists (reset, export): a key too
    for name, key in consts.items():
        add(key, '', name)
    m = re.search(r'\n  const TOPIC_KEYS = \{\n(.*?)\n  \};', src, re.S)
    if m:
        for topic, body in re.findall(r"^    (\w+): \[(.*?)\],?(?=\s*(?://[^\n]*)?\n    (?:\w+: \[|//)|\s*(?://[^\n]*)?$)", m.group(1) + '\n', re.S | re.M):
            for lit, const in re.findall(r"'(dci-[a-z0-9:-]+)'|\b([A-Z][A-Z0-9_]*_KEY)\b", re.sub(r'//[^\n]*', '', body)):
                key = lit or consts.get(const)
                if key in keys:
                    keys[key]['topic'] = topic
    for k in keys.values():
        if not k['store']:
            k['store'].add('localStorage')
    return keys


def table(keys=None):
    keys = keys if keys is not None else read_keys()
    rows = ['| Key | Kept in | ⚙ Settings tab | Constant in the code |', '|---|---|---|---|']
    for key in sorted(keys):
        k = keys[key]
        rows.append(f"| `{key}` | {', '.join(sorted(k['store']))} | {k['topic'] or '–'} | {('`' + k['const'] + '`') if k['const'] else '–'} |")
    return '\n'.join(rows)


def readme_path():
    found = [p for p in glob.glob(os.path.join(ROOT, 'mb-vibecode-credits-importer-v*-README.md')) if 'companion' not in p]
    return found[0] if found else None


def block():
    keys = read_keys()
    return f'{BEGIN}\n{len(keys)} keys.\n\n{table(keys)}\n{END}'


def check():
    """'' when the README's table is the one of the code, else what differs."""
    path = readme_path()
    text = open(path, encoding='utf-8').read() if path else ''
    if BEGIN not in text or END not in text:
        return 'the README has no table of the storage keys'
    have = text[text.index(BEGIN):text.index(END) + len(END)]
    if have == block():
        return ''
    a = set(re.findall(r'^\| `([^`]+)`', have, re.M))
    b = set(read_keys())
    return f'the table of the storage keys is not the one of the code – missing: {sorted(b - a)[:8]}, gone: {sorted(a - b)[:8]} (python3 tools/storage_keys.py --write)'


def main(argv):
    if '--check' in argv:
        diff = check()
        print(diff or 'OK')
        return 1 if diff else 0
    if '--write' in argv:
        path = readme_path()
        text = open(path, encoding='utf-8').read()
        if BEGIN not in text or END not in text:
            print('the README has no marks for the table')
            return 1
        new = text[:text.index(BEGIN)] + block() + text[text.index(END) + len(END):]
        open(path, 'w', encoding='utf-8').write(new)
        print('written:', os.path.basename(path), len(read_keys()), 'keys')
        return 0
    print(block())
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
