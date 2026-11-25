#!/usr/bin/env python3
"""The V_F input check's overlap check: b5d_overlap.py's composition and rule (S2R's prefix match, IBUB's "theirs",
s2r and rdx), plus the ended b5d root, against ours: the 9,877 read paths in inputs.tsv (read once through O_NOATIME)
and no writes. Every hit is listed with its owner; nothing is allowed automatically, so each hit needs that owner's
ack naming the paths. usage: vf_overlap.py <repo at main>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    repo = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(repo / "docs/orchestration/state/ben-b-20261124/blocks5d-20261124/connect"))
    import b5d_overlap as B  # the bound tool, imported unchanged
    th, mo, rpd = B.theirs(repo)
    th = th + [("b5d write root (ended, on record)", "/pscratch/sd/j/josephrb/b5d-20261124")]
    us = []
    for line in (HERE / "inputs.tsv").read_text().splitlines():
        p = line.split("\t")[3]
        if p.startswith("hpss:"):
            continue
        us.append(("read", p))
    over = lambda a, b: (mo.overlaps_prefix(rpd, a, b)  # noqa: E731
                         or (b.endswith(("-", ".")) and a.startswith(b)) or (a.endswith(("-", ".")) and b.startswith(a)))
    hits = [(o, t) for o in us for t in th if over(o[1], t[1])]
    print(f"OVERLAP vf-check: ours {len(us)} reads, 0 writes; theirs {len(th)}; pairs {len(us) * len(th)}; hits {len(hits)}")
    owners = {}
    for (ok, op), (tk, tp) in hits:
        owners.setdefault(tk.split(" ")[0], []).append((op, tk, tp))
    for o, v in sorted(owners.items()):
        print(f"OWNER {o}: {len(v)} hits")
        for op, tk, tp in v:
            print(f"OVERLAP HIT: ours read {op}  ~  theirs {tk} {tp}")
    return 0 if not hits else 3


if __name__ == "__main__":
    sys.exit(main())
