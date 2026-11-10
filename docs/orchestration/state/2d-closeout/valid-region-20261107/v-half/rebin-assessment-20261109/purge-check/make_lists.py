"""Build the explicit path lists for the purge check from committed records only (no cluster contact, no listing).
Usage: python3 -B make_lists.py <clean clone at main> <out dir>"""
import json, sys
from pathlib import Path
C, O = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(C / "nd-unfolding"))
import fd_f0_regrade as F0
import s1_assemble as sa
FD = C / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
ro = json.loads((FD / "with-cpl/readout/fd_f0b_readout.json").read_text())
av = ro["argv"]; arg = {av[i]: av[i + 1] for i in range(1, len(av) - 1) if av[i].startswith("--")}
REPO = "/pscratch/sd/j/josephrb/fd-ct-5b-addition-20261031/deploy/3b12c451/"
loc = lambda p: C / p[len(REPO):] if p.startswith(REPO) else Path(p)
inv = sa.load_manifest(loc(arg["--stage0-inventory"]))
s0c = F0.relative_manifest(loc(arg["--stage0c-sums"]), Path(arg["--stage0c-root"]))
s5p = F0.relative_manifest(loc(arg["--s5p-sums"]), Path(arg["--s5p-root"]))
def listed(man, d):
    return sorted(p for p in man if Path(p).parent == Path(d) and p.endswith(".npz"))
sets = {}
for t in F0.TRUTHS:
    r = t["row"]
    if r == 1: sets[t["name"]] = listed(inv, Path(arg["--s5e-assess"]) / t["set"])
    elif r == 2: sets[t["name"]] = listed(s0c, Path(arg["--stage0c-root"]) / "runs" / t["set"])
    elif r == 3: sets[t["name"]] = [str(Path(arg["--pvl-products"]) / f"{t['product']}.npz")]
    elif r == 4:
        sets[t["name"]] = [str(p) for p, _ in F0.f4_inputs(loc(arg["--d16-dir"]), Path(arg["--f4-root"]), t["d16"])]
        sets["cal:" + t["name"]] = listed(s5p, Path(arg["--s5p-root"]) / "runs/prod/cal" / t["cal"])
    elif r == 6: sets[t["name"]] = listed(s5p, Path(arg["--s5p-root"]) / "runs/prod/pow" / t["pow"])
    else: raise SystemExit(f"unexpected row {r}")
sets["floor"] = [str(Path(arg["--pvl-products"]) / "L-5D-PV_e_closure_tune_v1.npz")]
nexp = {k: v["n_experiments"] for k, v in ((t["name"] if isinstance(t, dict) else t, t) for t in []) }
f0b = sorted({p for v in sets.values() for p in v})
for k, v in sets.items():
    print(f"  {k}: {len(v)}")
print("F0b unique paths:", len(f0b))
want = {t["name"]: t["n_experiments"] for t in (ro["truths"] if isinstance(ro["truths"], list) else [])} if isinstance(ro["truths"], list) else {}
print("readout n_experiments:", {t.get("name"): t.get("n_experiments") for t in ro["truths"]} if isinstance(ro["truths"], list) else "")
(O / "f0b.txt").write_text("\n".join(f0b) + "\n")
# FD-PRR route-1 products: the misc job's log SHA256SUMS lists every product after the four jobs (committed receipt)
prr = []
for line in (FD / "receipts-prr/misc/cluster/log-misc/SHA256SUMS").read_text().splitlines():
    if line.strip():
        prr.append("/pscratch/sd/j/josephrb/fd-prr-20261108/" + line.split(None, 1)[1].strip())
(O / "prr.txt").write_text("\n".join(sorted(prr)) + "\n"); print("FD-PRR products:", len(prr))
D = "/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data"
(O / "central.txt").write_text(f"{D}/data_b-_j-.npz\n")
(O / "cstat.txt").write_text("\n".join(f"{D}/data_b{b}_j{100 + b}.npz" for b in range(21, 51)) + "\n")
B = "/pscratch/sd/j/josephrb/fd-ct-5b-20261030"
per = json.loads((FD / "readout/fd_ct_5b_periods.json").read_text())["inputs_sha256"]["unfolds"]
cpl = [f"{B}/unf/{P}/5b_{P}_b{'-' if b == 'None' else b}_j-.npz" for P, bs in per.items() for b in bs]
cpl += [f"{B}/truth/truth_{P}.npz" for P in ("PA", "PB", "PC", "ALL")]
(O / "cpl.txt").write_text("\n".join(sorted(cpl)) + "\n"); print("C_PL files:", len(cpl))
