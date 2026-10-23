"""Sample marker instances for a precision check: python3 -I marker_sample.py SEED K_OURS K_CORPUS ours.txt corpus..."""
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcount import markers
seed, ko, kc = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
ours, corpus = sys.argv[4], sys.argv[5:]
def inst(paths):
    out = []
    for p in paths:
        for i, l in enumerate(x.strip() for x in open(p) if x.strip()):
            for st, en, c, g in markers(l):
                out.append((p.rsplit('/', 1)[-1], i, c, g, l[max(0, st - 90):st] + '[' + g + ']' + l[en:en + 70]))
    return out
rng = random.Random(seed)
pick = rng.sample(inst([ours]), ko) + rng.sample(inst(corpus), kc)
for j, (p, i, c, g, ctx) in enumerate(pick):
    print(f"M{j+1:02d} {p}:{i} {c}: ...{ctx}...")
