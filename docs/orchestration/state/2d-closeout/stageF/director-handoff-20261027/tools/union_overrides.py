#!/usr/bin/env python3
"""Resolve MANIFEST-overrides.tsv as the sorted union of two sides' rows, keyed on path.

usage: union_overrides.py <ours-rev> <theirs-rev> <out-path>
Refuses (exit 4) when one path carries different rows on the two sides: an edited row needs a hand resolution.
"""
import subprocess, sys
P = 'docs/orchestration/MANIFEST-overrides.tsv'
def rows(rev):
    t = subprocess.run(['git', 'show', f'{rev}:{P}'], capture_output=True, text=True, check=True).stdout
    lines = t.split('\n'); return lines[0], [l for l in lines[1:] if l]
h1, a = rows(sys.argv[1]); h2, b = rows(sys.argv[2])
if h1 != h2: print('HEADER DIFFERS'); sys.exit(4)
by = {}
for l in a + b:
    k = l.split('\t')[0]
    if k in by and by[k] != l: print(f'EDITED ROW: {k}'); sys.exit(4)
    by[k] = l
out = [h1] + [by[k] for k in sorted(by)]
open(sys.argv[3], 'w').write('\n'.join(out) + '\n')
print(f'union: {len(a)} + {len(b)} -> {len(by)} rows')
