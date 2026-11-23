#!/usr/bin/env python3
"""Local identity test of the family-4 split of 3d-unfolding/plot_eavail_spectrum.py (note figure style, group C).

usage: python3 identity_family4.py <base sha> <scratch dir>     (run with the matplotlib the figure was made with)
With tools/fakeroot4/ROOT.py as PyROOT: the base commit's producer, the new producer with no flag, and the new producer
with --from-arrays on its own --dump-arrays must write byte-identical PNGs. Prints IDENTITY-FAMILY4 :: PASS or FAIL."""
import hashlib, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOTDIR = HERE.parents[7]
base, scratch = sys.argv[1], Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
rel = "3d-unfolding/plot_eavail_spectrum.py"
old = scratch / "base" / rel; old.parent.mkdir(parents=True, exist_ok=True)
old.write_bytes(subprocess.run(["git", "-C", str(ROOTDIR), "show", f"{base}:{rel}"], check=True, capture_output=True).stdout)
(scratch / "base" / "technote_style.py").write_bytes(subprocess.run(["git", "-C", str(ROOTDIR), "show", f"{base}:technote_style.py"], check=True, capture_output=True).stdout)
env = dict(os.environ, PYTHONPATH=str(HERE / "fakeroot4"), MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
def run(script, *a):
    r = subprocess.run([sys.executable, str(script), "--infile", "x.root", *a], env=env, capture_output=True, text=True, cwd=scratch)
    if r.returncode: print(r.stdout, r.stderr); raise SystemExit(f"FAIL: {script} rc {r.returncode}")
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
new = ROOTDIR / rel
run(old, "--out", str(scratch / "base.png"))
run(new, "--out", str(scratch / "new.png"), "--dump-arrays", str(scratch / "dump.npz"))
run(new, "--out", str(scratch / "from.png"), "--from-arrays", str(scratch / "dump.npz"))
hb, hn, hf = h(scratch / "base.png"), h(scratch / "new.png"), h(scratch / "from.png")
ok = hb == hn == hf
print(f"{'ok  ' if hb == hn else 'FAIL'} eavail_spectrum.png: base == new ({hb[:12]})")
print(f"{'ok  ' if hn == hf else 'FAIL'} eavail_spectrum.png: new == from ({hf[:12]})")
print("IDENTITY-FAMILY4 ::", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
