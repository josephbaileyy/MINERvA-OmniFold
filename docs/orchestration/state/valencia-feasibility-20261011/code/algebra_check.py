#!/usr/bin/env python3
"""Diagnostic: does the explicit four-vector contraction equal NuWro's w1..w5 expression?

Random tensor components and kinematic points; prints the maximum relative
difference for each beam. Not a frozen benchmark: it localizes any B3 failure to
either the algebra or NuWro's sampler.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valencia_tensor_xsec as vx  # noqa: E402

rng = np.random.default_rng(20261011)
E = 1000.0
omega = rng.uniform(20, 850, 20000)
Ep = E - omega
kp = np.sqrt(Ep ** 2 - vx.M_MU ** 2)
q = rng.uniform(np.abs(E - kp) + 1e-6, np.minimum(E + kp, 1200) - 1e-6)
ok = q > np.abs(E - kp)
w = {c: rng.normal(size=omega.size) for c in vx.COMPONENTS}
sym, anti = vx.lepton_contraction(E, omega, q, w, "nu")
anti = -anti  # repair API shim: old raw term 2 W12 (E q - omega k_z) = -(nu interference)
for beam, nu_sign in (("nu", -1.0), ("nubar", -1.0)):
    ours = sym + (nu_sign if beam == "nu" else -nu_sign) * anti
    theirs = vx.nuwro_formula_contraction(E, omega, q, w, beam)
    rel = np.abs(ours - theirs) / (np.abs(ours) + np.abs(theirs) + 1e-30)
    print(f"{beam}: max rel diff {rel[ok].max():.3e} median {np.median(rel[ok]):.3e} n={ok.sum()}")
