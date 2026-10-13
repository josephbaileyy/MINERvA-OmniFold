#!/usr/bin/env python3
"""Count 3p3h events and their primary-vertex energy loss (in - out) in a dump."""
import sys

for path in sys.argv[1:]:
    loss = []
    for line in open(path):
        if line.startswith("#"):
            continue
        head, *g = line.split("|")
        if float(head.split()[1]) <= 0:
            continue
        ins = [list(map(float, p.split()[1:5])) for p in g[0].split(";") if p.strip()]
        outs = [list(map(float, p.split()[1:5])) for p in g[1].split(";") if p.strip()]
        if len(outs) - 1 == 3:
            loss.append(sum(p[0] for p in ins) - sum(p[0] for p in outs))
    print(f"{path.split('/')[-2]}: n_3p3h={len(loss)} loss_MeV min={min(loss):.3f} max={max(loss):.3f}")
