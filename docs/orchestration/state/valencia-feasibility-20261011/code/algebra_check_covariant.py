#!/usr/bin/env python3
"""Diagnostic: both contractions against covariant identities.

For W^{mu nu} = q^mu q^nu (W00 = w^2, W03 = w|q|, W33 = |q|^2) the exact result is
L_{mu nu} q^mu q^nu = 2 (k.q)(k'.q) - q^2 (k.k'). For W^{mu nu} = -g^{mu nu}
(W00 = -1, W11 = W33 = 1) it is 2 k.k'. For W^{mu nu} = e_z^mu e_z^nu (W33 = 1)
it is 2 k_z k'_z + k.k' with k_z, k'_z the components along q.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valencia_tensor_xsec as vx  # noqa: E402

E = 1000.0
for omega, q in ((100.0, 400.0), (50.0, 900.0), (700.0, 800.0)):
    om, qq = np.array([omega]), np.array([q])
    Ep = E - omega
    kp = np.sqrt(Ep ** 2 - vx.M_MU ** 2)
    kz = (E ** 2 - kp ** 2 + q ** 2) / (2 * q)
    kpz = kz - q
    q4sq = omega ** 2 - q ** 2
    kdotkp = (vx.M_MU ** 2 - q4sq) / 2
    kdotq = E * omega - kz * q
    kpdotq = Ep * omega - kpz * q
    cases = {
        "q^mu q^nu": ({"W00": omega ** 2, "W03": omega * q, "W11": 0.0, "W12": 0.0, "W33": q ** 2},
                      2 * kdotq * kpdotq - q4sq * kdotkp),
        "-g^{mu nu}": ({"W00": -1.0, "W03": 0.0, "W11": 1.0, "W12": 0.0, "W33": 1.0}, 2 * kdotkp),
        "e_z e_z": ({"W00": 0.0, "W03": 0.0, "W11": 0.0, "W12": 0.0, "W33": 1.0}, 2 * kz * kpz + kdotkp),
    }
    for name, (w, exact) in cases.items():
        w = {k: np.array([v]) for k, v in w.items()}
        sym, _ = vx.lepton_contraction(E, om, qq, w, "nu")
        nuwro = vx.nuwro_formula_contraction(E, om, qq, w, "nu")
        print(f"w={omega:5.0f} q={q:5.0f} {name:11s} exact {exact:+.6e} ours {sym[0]:+.6e} nuwro {nuwro[0]:+.6e}")
