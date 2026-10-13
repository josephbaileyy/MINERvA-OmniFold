#!/usr/bin/env python3
"""Diagnostic: is NuWro's lepton-mass W4 term (sin^2 theta) the whole algebra difference?

Replaces sin^2(theta) by 2 sin^2(theta/2) = 1 - cos(theta) in the transcribed NuWro
expression, re-tests the random-component comparison, and integrates the 1 GeV
nu and nubar cross sections with (a) the explicit contraction, (b) NuWro's
expression as written, (c) NuWro's expression with the substitution.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valencia_tensor_xsec as vx  # noqa: E402


def nuwro_fixed(E, omega, q, w, beam):
    base = vx.nuwro_formula_contraction(E, omega, q, w, beam)
    Ep = E - omega
    lp = np.sqrt(np.maximum(Ep ** 2 - vx.M_MU ** 2, 0.0))
    ct = (E ** 2 + lp ** 2 - q ** 2) / (2 * E * lp)
    w4 = 0.5 * (w["W33"] - w["W11"]) / q ** 2
    pref = 4 * E * Ep * vx.M_MU ** 2 / ((Ep + lp) * Ep) * 0.5 * w4 * 2 * Ep * (Ep + lp)
    return base - pref * (1 - ct ** 2) + pref * (1 - ct)


rng = np.random.default_rng(7)
E = 1000.0
om = rng.uniform(20, 850, 20000)
Ep = E - om
kp = np.sqrt(Ep ** 2 - vx.M_MU ** 2)
q = rng.uniform(np.abs(E - kp) + 1e-3, np.minimum(E + kp, 1200) - 1e-3)
w = {c: rng.normal(size=om.size) for c in vx.COMPONENTS}
sym, anti = vx.lepton_contraction(E, om, q, w, "nu")
anti = -anti  # repair API shim: old raw term 2 W12 (E q - omega k_z) = -(nu interference)
for beam in ("nu", "nubar"):
    ours = sym + (-1.0 if beam == "nu" else 1.0) * anti
    fixed = nuwro_fixed(E, om, q, w, beam)
    scale = np.abs(ours).mean()
    print(f"{beam}: max |ours - nuwro_fixed| / mean|ours| = {np.abs(ours - fixed).max() / scale:.2e}")

tables = vx.load_tables(Path(sys.argv[1]), "C12")
for beam in ("nu", "nubar"):
    B = vx.B_SHIFT[("C12", beam)]
    h = 1.25
    omega = np.arange(B + h / 2, E - vx.M_MU, h)
    qs = np.arange(h / 2, vx.QMAX, h)
    Om, Q = np.meshgrid(omega, qs, indexing="ij")
    kpp = np.sqrt(np.maximum((E - Om) ** 2 - vx.M_MU ** 2, 0.0))
    allowed = (Q > np.abs(E - kpp)) & (Q < E + kpp)
    pref = (vx.GF_MEV * vx.VUD) ** 2 / (2 * np.pi) * Q / E ** 2 * h * h * vx.HBARC2_CM2_MEV2 * 12 / 1e-38
    tot = {"explicit": 0.0, "nuwro_as_written": 0.0, "nuwro_sin2half": 0.0}
    for ch in vx.CHANNELS:
        ww = {c: vx.interp(tables[ch][c], Om - B, Q) for c in vx.COMPONENTS}
        s, a = vx.lepton_contraction(E, Om, Q, ww, "nu")
        a = -a  # repair API shim: old raw term 2 W12 (E q - omega k_z) = -(nu interference)
        tot["explicit"] += float(np.where(allowed, pref * (s + (-1.0 if beam == "nu" else 1.0) * a), 0).sum())
        tot["nuwro_as_written"] += float(np.where(allowed, pref * vx.nuwro_formula_contraction(E, Om, Q, ww, beam), 0).sum())
        tot["nuwro_sin2half"] += float(np.where(allowed, pref * nuwro_fixed(E, Om, Q, ww, beam), 0).sum())
    print(beam, {k: round(v, 5) for k, v in tot.items()},
          f"as-written/explicit - 1 = {tot['nuwro_as_written'] / tot['explicit'] - 1:+.4%}")
