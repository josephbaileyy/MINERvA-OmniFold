#!/usr/bin/env python3
"""Local identity test of the family-6 split of docs/analysis-note/figures/plot_joint_null_distributions_physlabels.py.

usage: python3 identity_family6.py <base sha> <scratch dir>     (run with the matplotlib the figure was made with)
A synthetic sufficient-inputs extract and manifest (five nulls, two with an m1 variant) and tools/fakereplay6/
replay_inference.py stand in for the frozen extract and the replay. The base commit's producer, the new producer with no
flag, and the new producer with --from-arrays on its own --dump-arrays (each copied beside the fake replay, as the
producer expects to run beside replay_inference.py) must write byte-identical PDFs once the PDF date fields are fixed.
Prints IDENTITY-FAMILY6 :: PASS or FAIL."""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOTDIR = HERE.parents[7]
base, scratch = sys.argv[1], Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
rel = "docs/analysis-note/figures/plot_joint_null_distributions_physlabels.py"
for tag, src in (("base", subprocess.run(["git", "-C", str(ROOTDIR), "show", f"{base}:{rel}"], check=True, capture_output=True).stdout),
                 ("new", (ROOTDIR / rel).read_bytes())):
    d = scratch / tag; d.mkdir(exist_ok=True)
    (d / "plot.py").write_bytes(src); shutil.copy(HERE / "fakereplay6" / "replay_inference.py", d / "replay_inference.py")
r = np.random.default_rng(7); n, m = 40, 120
keys = ["MnvTune_v1", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"]
z = {"V": np.eye(n), "f_data": r.normal(1.0, 0.3, n)}
man = {"shift_coefficients": [0.0, 0.5, 1.0], "nulls": {}}
for i, k in enumerate(keys):
    z[f"F__{k}"] = r.normal(1.0, 0.25 + 0.03 * i, (m, n)); z[f"seeds__{k}"] = np.arange(m)
    z[f"mu__{k}"] = np.ones(n); z[f"var__{k}"] = np.full(n, 0.06); z[f"dom__{k}"] = (np.arange(n) % 5 != 0).astype(np.int8)
    z[f"S__{k}"] = r.normal(0, 0.05, n)
    mm = None
    if i in (1, 2):
        z[f"d1__{k}"] = r.normal(0, 0.02, n); mm = {"kappa": 3}
    man["nulls"][k] = {"m1": mm, "surrogate_seed0": 100 + i}
np.savez(scratch / "extract.npz", **z); (scratch / "extract.npz.manifest.json").write_text(json.dumps(man))
env = dict(os.environ, MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1", SOURCE_DATE_EPOCH="0")
def run(script, *a):
    p = subprocess.run([sys.executable, str(script), *a], env=env, capture_output=True, text=True, cwd=scratch)
    if p.returncode: print(p.stdout[-1500:], p.stderr[-1500:]); raise SystemExit(f"FAIL: {script} rc {p.returncode}")
run(scratch / "base" / "plot.py", "--npz", str(scratch / "extract.npz"), "--out", str(scratch / "base.pdf"))
run(scratch / "new" / "plot.py", "--npz", str(scratch / "extract.npz"), "--out", str(scratch / "new.pdf"), "--dump-arrays", str(scratch / "dump.npz"))
run(scratch / "new" / "plot.py", "--from-arrays", str(scratch / "dump.npz"), "--out", str(scratch / "from.pdf"))
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
hb, hn, hf = (h(scratch / f"{t}.pdf") for t in ("base", "new", "from"))
print(f"{'ok  ' if hb == hn else 'FAIL'} paper_joint_nulls.pdf: base == new ({hb[:12]})"); print(f"{'ok  ' if hn == hf else 'FAIL'} paper_joint_nulls.pdf: new == from")
ok = hb == hn == hf
print("IDENTITY-FAMILY6 ::", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
