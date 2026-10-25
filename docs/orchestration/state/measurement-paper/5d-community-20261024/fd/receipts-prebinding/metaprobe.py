"""Meta-only probe: fd_f0_regrade.meta_problems (control 2's check, headers and meta only, no array read) over every
real product, plus listing anomalies. Prints counts and problem strings only."""
import collections, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import fd_f0_regrade as F
P = Path("/pscratch/sd/j/josephrb")
sets = []
for t in F.TRUTHS:
    if t["row"] == 1: sets.append(("s5e", t, P / "s5e-20260925/runs/cand/assess" / t["set"]))
    elif t["row"] == 2: sets.append(("s5e", t, P / "5d-stage0-20261023/runs" / t["set"]))
    elif t["row"] == 3: sets.append(("closure", {"ratio": F.RATIO["closure_nuwro"]}, P / "pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz"))
    elif t["row"] == 4:
        sets.append(("f4", {"hyp": F.HYP[t["d16"]]}, P / "s5p-20260926/runs/s3r/f4" / f"{t['f4']}_half"))
        sets.append(("cal", {"hyp": F.HYP[t["d16"]]}, P / "s5p-20260926/runs/prod/cal" / t["cal"]))
    else:
        ref = next(r for r in F.TRUTHS if r["name"] == t["ref"])
        sets.append(("pow", {"hyp": F.HYP[ref["d16"]], "alt": t["alt"]}, P / "s5p-20260926/runs/prod/pow" / t["pow"]))
sets.append(("closure", {"ratio": F.RATIO["floor"]}, P / "pv-ladder-20261024/products/L-5D-PV_e_closure_tune_v1.npz"))
total = 0
for kind, spec, d in sets:
    paths = [d] if d.suffix == ".npz" else sorted(d.glob("*.npz"))
    odd = [] if d.suffix == ".npz" else sorted(p.name for p in d.iterdir() if p.is_dir() or ".partial" in p.name or not p.name.endswith(".npz"))
    probs = collections.Counter()
    ran = collections.Counter()
    for p in paths:
        m = F.read_meta(p)
        ran[(m.get("refinement") or {}).get("ran")] += 1
        for b in F.meta_problems(p, m, kind, spec):
            probs[b] += 1
    total += len(paths)
    print(f"{d.name}: {len(paths)} products, refinement.ran {dict(ran)}, other entries {odd[:5]}{'...' if len(odd) > 5 else ''} ({len(odd)}), problems {dict(probs) or 'none'}")
print("total", total)
