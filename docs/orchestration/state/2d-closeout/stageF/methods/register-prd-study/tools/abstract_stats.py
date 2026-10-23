"""Abstract-only counts: python3 -I abstract_stats.py ID=TEXFILE ...  (same converter and lexicon as the body table)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tex2prose as T
from qcount import markers, WORD
print('| doc | abstract words | sentences | Q markers | Q /1k | STATUS+COND+SCOPE markers | sentences with >=1 of those |')
print('|---|---|---|---|---|---|---|')
for arg in sys.argv[1:]:
    pid, path = arg.split('=', 1)
    s = T.read_expanded(path, os.path.dirname(os.path.abspath(path)))
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', s, re.S)
    if m: a = m.group(1)
    else:
        i = re.search(r'\\abstract\s*\{|\\AtlasAbstract\s*\{', s).end() - 1
        a = s[i + 1:T.find_group(s, i) - 1]
    sents = T.sentences(T.convert(a))
    w = sum(len(WORD.findall(x)) for x in sents)
    ms = [markers(x) for x in sents]
    q = sum(len(x) for x in ms)
    core = sum(1 for x in ms for y in x if y[2] in ('STATUS', 'COND', 'SCOPE'))
    ns = sum(1 for x in ms if any(y[2] in ('STATUS', 'COND', 'SCOPE') for y in x))
    print(f'| {pid} | {w} | {len(sents)} | {q} | {1000*q/w:.0f} | {core} | {ns} of {len(sents)} |')
