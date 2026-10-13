#!/usr/bin/env python3
"""Diagnostic for B1/B2: sensitivity of the 1 GeV 12C result to the energy shift B (and an extra V_ud^2).

B = 0 (no shift), NuWro's B, and 27.41 MeV (the corrected paper's carbon separation
energy, used by Kasturi et al.). Reported per nucleus in 1e-38 cm^2. Not a benchmark.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valencia_tensor_xsec as vx  # noqa: E402

tables = vx.load_tables(Path(sys.argv[1]), "C12")
out = []
for beam in ("nu", "nubar"):
    nominal = vx.B_SHIFT[("C12", beam)]
    for B in (0.0, nominal, 27.41):
        vx.B_SHIFT[("C12", beam)] = B
        s = vx.sigma(tables, 1000.0, beam, "C12", 8)
        tot = 12 * sum(s.values()) / 1e-38
        out.append({"beam": beam, "B_MeV": B, "per_nucleus_1e38": round(tot, 4),
                    "with_extra_Vud2": round(tot * vx.VUD ** 2, 4)})
        print(json.dumps(out[-1]))
    vx.B_SHIFT[("C12", beam)] = nominal
