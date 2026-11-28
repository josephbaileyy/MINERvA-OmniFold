"""Test B epsilon scans from test-b.json: deviance above the minimum, and sqrt(delta dev) at eps = 0."""

import json
from pathlib import Path

import numpy as np

for r in json.loads((Path(__file__).resolve().parent / "test-b.json").read_text()):
    e, d = np.array(r["eps_scan"]).T
    d = d - d.min()
    zero = d[np.argmin(np.abs(e))]
    print(f"{r['direction']}: best eps {e[np.argmin(d)]:+.4f}; declared parabola sigma {r['sigma_eps']:.5f}"
          f" ({r['eps'] / r['sigma_eps']:+.1f} sigma); delta deviance at eps=0 {zero:.1f} (sqrt {np.sqrt(zero):.1f} sigma)")
    print("  eps x 1e4 : delta deviance  " + " ".join(f"{x * 1e4:+.0f}:{y:.1f}" for x, y in zip(e, d) if -5e-4 <= x <= 2e-3))
