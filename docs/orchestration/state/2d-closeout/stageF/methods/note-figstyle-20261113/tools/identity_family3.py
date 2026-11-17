#!/usr/bin/env python3
"""Local identity test of the family-3 split of 2d-unfolding/uq/plot_bootstrap_figs.py (note figure style, group C).

usage: python3 identity_family3.py <base sha> <scratch dir>     (run with the matplotlib the figures were made with)
With tools/fakeroot3/ROOT.py as PyROOT: the base commit's producer, the new producer with no flag, and the new producer
with --from-arrays on its own --dump-arrays must write byte-identical PNGs of both figures. Prints
IDENTITY-FAMILY3 :: PASS or FAIL."""
import hashlib, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOTDIR = HERE.parents[7]
base, scratch = sys.argv[1], Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
rel = "2d-unfolding/uq/plot_bootstrap_figs.py"
old = scratch / "base" / rel; old.parent.mkdir(parents=True, exist_ok=True)
def show(path): return subprocess.run(["git", "-C", str(ROOTDIR), "show", f"{base}:{path}"], check=True, capture_output=True).stdout
old.write_bytes(show(rel)); (scratch / "base" / "technote_style.py").write_bytes(show("technote_style.py"))
env = dict(os.environ, PYTHONPATH=str(HERE / "fakeroot3"), MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
def run(script, outdir, *a):
    (scratch / outdir).mkdir(exist_ok=True)
    r = subprocess.run([sys.executable, str(script), "--cov", "x.root", "--outdir", str(scratch / outdir), *a],
                       env=env, capture_output=True, text=True, cwd=scratch)
    if r.returncode: print(r.stdout, r.stderr); raise SystemExit(f"FAIL: {script} rc {r.returncode}")
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
new = ROOTDIR / rel
run(old, "base"); run(new, "new", "--dump-arrays", str(scratch / "dump.npz")); run(new, "from", "--from-arrays", str(scratch / "dump.npz"))
ok = True
for f in ("uq_spread_2d.png", "uq_corr_2d.png"):
    hb, hn, hf = (h(scratch / d / f) for d in ("base", "new", "from"))
    print(f"{'ok  ' if hb == hn else 'FAIL'} {f}: base == new ({hb[:12]})"); print(f"{'ok  ' if hn == hf else 'FAIL'} {f}: new == from")
    ok &= hb == hn == hf
print("IDENTITY-FAMILY3 ::", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
