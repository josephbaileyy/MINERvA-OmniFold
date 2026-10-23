"""Verify that every quote in a notes file occurs verbatim in the paper's extracted prose.

Notes format: any line containing  Q[<id>]: "<quote>"  is checked against prose/<id>.txt
(and, if not found there, against the full extracted text of the source incl. appendices/supplement/floats,
prose_full/<id>.txt, if present). Inline math in a quote must be written as MATH, display math as EQ,
citations as [N], reference numbers as N -- exactly as in the prose file. Comparison ignores case,
whitespace runs, and curly-vs-straight quotes/dashes.
Exit 1 if any quote is not found.
Usage: python3 -I verify_quotes.py notes/*.md
"""
import re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
base = os.path.dirname(here)
def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace('--', '-')
    return re.sub(r'\s+', ' ', s).strip().lower()
cache = {}
def text(pid, kind):
    k = (pid, kind)
    if k not in cache:
        p = os.path.join(base, kind, pid + '.txt')
        cache[k] = norm(open(p, encoding='utf-8').read().replace('\n', ' ')) if os.path.exists(p) else ''
    return cache[k]
bad = n = 0
for f in sys.argv[1:]:
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'Q\[([0-9.]+|ours)\]:\s*"(.+?)"(?=\s*(?:\(|$|;|,|\.|\s—|\s-))', line):
            pid, q = m.group(1), m.group(2)
            n += 1
            where = 'body' if norm(q) in text(pid, 'prose') else ('full' if norm(q) in text(pid, 'prose_full') else None)
            if where is None:
                bad += 1
                print(f'NOT FOUND {f}:{ln} [{pid}] "{q[:100]}"')
            elif where == 'full':
                print(f'ok-outside-body {f}:{ln} [{pid}] "{q[:60]}"')
print(f'{n} quotes checked, {bad} not found')
sys.exit(1 if bad else 0)
