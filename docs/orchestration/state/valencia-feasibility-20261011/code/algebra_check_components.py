#!/usr/bin/env python3
"""Diagnostic: per-component comparison of the two contractions (one W component at a time)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valencia_tensor_xsec as vx  # noqa: E402

E = 1000.0
for omega, q in ((100.0, 400.0), (300.0, 600.0), (500.0, 1000.0), (50.0, 900.0), (700.0, 800.0)):
    om, qq = np.array([omega]), np.array([q])
    row = []
    for c in vx.COMPONENTS:
        w = {k: np.array([1.0 if k == c else 0.0]) for k in vx.COMPONENTS}
        sym, anti = vx.lepton_contraction(E, om, qq, w, "nu")
        anti = -anti  # repair API shim: old raw term 2 W12 (E q - omega k_z) = -(nu interference)
        ours = sym - anti  # neutrino with the integrator's selected sign (-1)
        theirs = vx.nuwro_formula_contraction(E, om, qq, w, "nu")
        row.append(f"{c}: ours {ours[0]:+.6e} nuwro {theirs[0]:+.6e}")
    print(f"omega={omega} q={q}"); print("   " + "\n   ".join(row))
