"""Robustness variant: drop the low-precision markers found in calibration (all NEG, CONCESS, HEDGE; 'within', 'if',
'depend* on', 'in this <noun>', 'in general', 'other than') and count the rest per 1k words.
python3 -I strict_index.py prose/*.txt"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcount import markers, WORD
LOW = re.compile(r'^(within|if|depend\w* (on|upon)|in this \w+|in general|other than)$', re.I)
for p in sys.argv[1:]:
    L = [l.strip() for l in open(p) if l.strip()]
    w = sum(len(WORD.findall(l)) for l in L)
    k = 0; s = 0
    for l in L:
        ms = [m for m in markers(l) if m[2] in ('STATUS', 'SCOPE', 'COND') and not LOW.match(m[3])]
        k += len(ms); s += bool(ms)
    print(f'{os.path.basename(p)[:-4]:12s} strict/1k={1000*k/w:5.1f}  sentences with >=1 strict = {100*s/len(L):4.0f}%')
