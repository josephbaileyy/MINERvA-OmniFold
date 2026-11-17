#!/usr/bin/env python3
"""Local identity test of the family-5 fill/draw splits (note figure style, group C).

usage: python3 identity_family5.py <base sha> <scratch dir>     (run with the matplotlib the figures were made with)
With tools/fakeroot5/ROOT.py as PyROOT, for each case: the base commit's producer, the new producer with no flag, and
the new producer with --from-arrays on its own --dump-arrays must write byte-identical PNGs. Each base producer runs
from a copy of the base commit's tree (its imports resolve there). Prints IDENTITY-FAMILY5 :: PASS or FAIL."""
import hashlib, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOTDIR = HERE.parents[7]
base, scratch = sys.argv[1], Path(sys.argv[2]); scratch.mkdir(parents=True, exist_ok=True)
CASES = [  # (producer, argv without outputs, output flag, output name)
    ("nd-unfolding/fps_prior_envelope.py", ["--tune", "t_tune.root", "--genie", "t_genie.root", "--nuwro", "t_nuwro.root"],
     "--out-png", "fps_prior_envelope_MEFHC.png"),
    ("nd-unfolding/fps_pilot_compare.py", ["--fps-tune", "t_tune.root", "--fps-genie", "t_genie.root", "--ctrl", "t_ctrl.root"],
     "--out-png", "fps_pilot_compare_MEFHC.png"),
    ("nd-unfolding/fps_acceptance.py", ["--omnifile", "t_fps.root"], "--out-png", "fps_acceptance_MEFHC.png"),
    ("nd-unfolding/q3_excess_projection.py", [], "--out", "q3_excess_projection.png"),
]
# q3_excess_projection.py at the base commit takes no arguments and writes to its hard-coded _REPO (the cluster's tree);
# the base copy's _REPO line is pointed at the scratch tree so that it can run here, and its output is moved into place.
BASE_ONLY = {"nd-unfolding/q3_excess_projection.py": ('_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"', "q3_excess_projection.png")}
tree = scratch / "base"
if not tree.exists():
    tree.mkdir(parents=True)
    tar = subprocess.run(["git", "-C", str(ROOTDIR), "archive", base, "technote_style.py", "2d-unfolding", "nd-unfolding/fps_acceptance.py",
                          "nd-unfolding/fps_pilot_compare.py", "nd-unfolding/fps_prior_envelope.py", "nd-unfolding/q3_excess_projection.py",
                          "nd-unfolding/unfold_nd_omnifold_unbinned.py", "nd-unfolding/flux_universe.py", "nd-unfolding/xsec_nd.py"],
                         check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(tree)], input=tar, check=True)
env = dict(os.environ, PYTHONPATH=str(HERE / "fakeroot5"), MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
def run(script, argv):
    r = subprocess.run([sys.executable, str(script), *argv], env=env, capture_output=True, text=True, cwd=scratch)
    if r.returncode: print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(f"FAIL: {script} rc {r.returncode}")
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ok = True
for rel, argv, oflag, oname in CASES:
    d = scratch / Path(rel).stem; d.mkdir(exist_ok=True)
    if rel in BASE_ONLY:
        line, produced = BASE_ONLY[rel]; src = (tree / rel).read_text()
        assert src.count(line) == 1, line
        (tree / rel).write_text(src.replace(line, f'_REPO = "{tree}"'))
        (tree / "nd-unfolding").mkdir(exist_ok=True); run(tree / rel, [])
        (tree / "nd-unfolding" / produced).rename(d / ("base-" + oname))
    else:
        run(tree / rel, argv + [oflag, str(d / ("base-" + oname))])
    run(ROOTDIR / rel, argv + [oflag, str(d / ("new-" + oname)), "--dump-arrays", str(d / "dump.npz")])
    run(ROOTDIR / rel, [oflag, str(d / ("from-" + oname)), "--from-arrays", str(d / "dump.npz")])
    hb, hn, hf = (h(d / (k + oname)) for k in ("base-", "new-", "from-"))
    print(f"{'ok  ' if hb == hn else 'FAIL'} {oname}: base == new ({hb[:12]})"); print(f"{'ok  ' if hn == hf else 'FAIL'} {oname}: new == from")
    ok &= hb == hn == hf
print("IDENTITY-FAMILY5 ::", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
