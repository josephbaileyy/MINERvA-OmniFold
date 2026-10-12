"""Dry run of analyze_p5.confirm() branches on synthetic inputs (no job outputs read)."""
import sys
import numpy as np
import os
sys.path.insert(0, os.environ["P5"])   # P5=<dir holding analyze_p5.py>; needs ROOT (setup_salloc_env.sh)
import analyze_p5 as A

rng = np.random.default_rng(0)
n = 205
sig = np.full(n, 1.0)            # sigma_band
sml = np.full(n, 0.3)            # sigma_ML
floor = np.ones(n, bool); floor[:17] = False
def run(name, d42, d43, r42, o42="MEASURED", o43="MEASURED"):
    try:
        c = A.confirm(d43 / sml, d42 / sml, floor, o43, o42, r42, d43, d42, sig)
        print(f"{name:52s} r={c['pearson_z43_z42_floored']:.3f} r1mean_med={c['r1_seed_mean']['median']:.3f} "
              f"-> {c['final_routing']}")
    except SystemExit as e:
        print(f"{name:52s} -> {e}")
NR, MAT = "NOT RESOLVED ABOVE TRAINER NOISE", "MATERIAL"
big = rng.normal(0, 0.3, n); small = rng.normal(0, 0.04, n)
noise = lambda: rng.normal(0, 0.3, n)
run("coherent big, after MATERIAL", big + 0.05 * noise(), big + 0.05 * noise(), MAT)
run("noise, after MATERIAL", noise(), noise(), MAT)
run("coherent big, after NOT RESOLVED", big + 0.05 * noise(), big + 0.05 * noise(), NR)
run("coherent small, after NOT RESOLVED", small + 0.002 * noise(), small + 0.002 * noise(), NR)
# seed-42 inflated by noise above the rule, seed-43 coherent: mean falls below
c = rng.uniform(-0.12, 0.12, n); e = rng.uniform(-0.18, 0.18, n)
run("coherent, d42 inflated, mean below rule, after NR", c + e, c, NR)
run("constant z43 (exact zero)", noise(), np.zeros(n), NR)
run("noise, after NOT RESOLVED", noise(), noise(), NR)
run("seed 42 NOT MATERIAL", noise(), noise(), "NOT MATERIAL")
run("constant z43", noise(), np.full(n, 0.1), NR)
run("seed-43 pair INCONCLUSIVE", big, big, NR, o43="INCONCLUSIVE")
