#!/usr/bin/env python3
"""The committed-format 3D and (E_avail, W) generator prediction files, from a 5D prediction npz (s5p Stage 7).

``KNOWN_ISSUES.md`` 83: the committed ``*_xsec3d.root`` and ``*_xsec_eavailW.root`` of GENIE CV, GENIE+MEC and
NuWro were built from a mis-sampled flux. The flux-repaired 5D predictions (``state/s5p/gen5d/gen5d-fluxfix*.json``)
share the truth phase space and the (pT, p_parallel, E_avail) and (E_avail, W) edges, so their marginals ARE the
repaired 3D and (E_avail, W) predictions. This writes them in the committed format so the unchanged figure
producers (``overlay_eavailW_band.py``, ``overlay_generators_band.py``, ``compare_3d_fullcov.py``,
``compare_mec_eavail.py``) read them:

* ``--kind 3d``: hXSec3D (pT, p_parallel, E_avail), hXSec2D (pT, p_parallel), hXSec_pt, hXSec_pz, hXSec_eavail;
* ``--kind eavailW``: hXSec_eavailW, hXSec_eavail, hXSec_W.

Every density is the 5D density integrated over the dropped axes (content x their widths). The normalization is
the 5D product's own: for GENIE+MEC that is the 3D convention (sigma_nonMEC / N_nonMEC), which also removes the
(E_avail, W) file's 2.87% error of ``KNOWN_ISSUES.md`` 81. A sidecar JSON records the input's sha256 and totals.

MEASURES: marginals of a fixed prediction. CANNOT AUTHORIZE: any comparison verdict.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE.parent), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

AXES = ("pt", "pz", "eavail", "q3", "W")


def load(path):
    z = np.load(path, allow_pickle=True)
    edges = [np.asarray(z[f"edges_{a}"], float) for a in AXES]
    x = np.asarray(z["xsec_flat"], float).reshape([len(e) - 1 for e in edges])
    return x, edges


def integrate(x, edges, keep):
    """Density on the kept axes: sum over the dropped axes of density x their widths."""
    out = x
    for ax in sorted(set(range(5)) - set(keep), reverse=True):
        out = np.tensordot(out, np.diff(edges[ax]), axes=([ax], [0]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--kind", choices=("3d", "eavailW"), required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    import ROOT
    import unfold_3d_omnifold_unbinned as u3d
    ROOT.gROOT.SetBatch(True)
    x, e = load(a.npz)
    total = float((x * np.einsum("a,b,c,d,f->abcdf", *[np.diff(k) for k in e])).sum())
    f = ROOT.TFile.Open(str(a.out), "RECREATE")
    if a.kind == "3d":
        x3 = integrate(x, e, (0, 1, 2))
        u3d.numpy_to_th3d(x3, None, "hXSec3D", f"{a.label} d^{{3}}#sigma", e[0], e[1], e[2]).Write()
        u3d.numpy_to_th2d((x3 * np.diff(e[2])).sum(axis=2), None, "hXSec2D", f"{a.label} d^{{2}}#sigma", e[0], e[1]).Write()
        u3d.numpy_to_th1d(e[0], integrate(x, e, (0,)), "hXSec_pt", f"{a.label} d#sigma/dp_{{T}}").Write()
        u3d.numpy_to_th1d(e[1], integrate(x, e, (1,)), "hXSec_pz", f"{a.label} d#sigma/dp_{{||}}").Write()
        u3d.numpy_to_th1d(e[2], integrate(x, e, (2,)), "hXSec_eavail", f"{a.label} d#sigma/dE_{{avail}}").Write()
        check = float((x3 * np.einsum("a,b,c->abc", *[np.diff(k) for k in e[:3]])).sum())
    else:
        x2 = integrate(x, e, (2, 4))
        u3d.numpy_to_th2d(x2, None, "hXSec_eavailW", f"{a.label} d^{{2}}#sigma/(dE_{{avail}}dW);E_{{avail}} (GeV);W (GeV)",
                          e[2], e[4]).Write()
        u3d.numpy_to_th1d(e[2], integrate(x, e, (2,)), "hXSec_eavail", f"{a.label} d#sigma/dE_{{avail}}").Write()
        u3d.numpy_to_th1d(e[4], integrate(x, e, (4,)), "hXSec_W", f"{a.label} d#sigma/dW").Write()
        check = float((x2 * np.outer(np.diff(e[2]), np.diff(e[4]))).sum())
    f.Close()
    if abs(check / total - 1) > 1e-10:
        raise SystemExit(f"marginal total {check} differs from the 5D total {total}")
    side = {"schema": "gen5d-rootpred/1", "label": a.label, "kind": a.kind,
            "input": {"path": str(a.npz.resolve()), "sha256": hashlib.sha256(a.npz.read_bytes()).hexdigest()},
            "total_sigma_cm2_per_nucleon": total, "out": str(a.out.resolve()),
            "out_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest(),
            "code_sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()}
    a.out.with_suffix(".json").write_text(json.dumps(side, indent=1) + "\n")
    print(json.dumps({k: side[k] for k in ("label", "kind", "total_sigma_cm2_per_nucleon")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
