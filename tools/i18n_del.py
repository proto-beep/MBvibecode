"""Removes texts from the embedded translations of the main script (all languages).

Usage: python3 i18n_del.py <key> [<key> …]   (a key without ".one"/".other" also removes its plural forms)
"""
import re
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'mb-vibecode-credits-importer.user.js'


def main(keys):
    s = SCRIPT.read_text()
    start = s.index('  const I18N = {')
    end = s.index('\n  };', start)
    body = s[start:end]
    n = 0
    for k in keys:
        pat = re.compile(r'^      "' + re.escape(k) + r'(?:\.(?:zero|one|two|few|many|other))?": .*,\n', re.M)
        body, c = pat.subn('', body)
        n += c
    SCRIPT.write_text(s[:start] + body + s[end:])
    print('lines removed:', n)


if __name__ == '__main__':
    main(sys.argv[1:])
