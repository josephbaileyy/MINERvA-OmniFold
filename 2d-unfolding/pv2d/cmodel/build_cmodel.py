#!/usr/bin/env python3
"""C_model,2D: the 2D generator-shape model-dependence covariance, from PV-2D's refined-arm shifts (numpy only).

The form is DECISION-20261024-joseph-2d-model-dependence-component.md item 2: M2, kappa = 1,

    C_model = sum_k s_k s_k^T,   k in (GENIE+MEC, NuWro, GiBUU),

with s_k the refined arm's per-cell relative shift for vertex k (readout_ref.json, PV-2D, PR #300). Each vertex is one
fully correlated mode at its measured size, and the three are summed as if independent. C_model is fractional: it
multiplies the central value on both sides. C_abs = diag(x) C_model diag(x) uses Q's own x (E_U), so that Q + C_abs is
a sum of two covariances of the same vector.

Writes
  --out-json  the committed summary: the factor S (3 x 205, so C_model = S^T S exactly), the sqrt-diagonal, Q's and
              the total's per-cell sigma, the rank and singular values, conditioning, coverage against the PV-2D
              positive control's bias, and the sha256 of both matrices as built;
  --out-npz   (optional) the matrices themselves: C_model, C_abs, S, cells, x. *.npz is gitignored in this repo.

Also prints the director's envelope total sqrt(sigma_Q^2 + h^2), h = max_k |s_k| (COMPARISON-2D-5D.md), which is not
M2's: diag(C_model) = sum_k s_k^2 >= h^2.

Refuses unless the readouts are the refined arm and configuration (a), both made against the given projections.json
and on its cells; the refined readout's envelope h is max_k |s_k| of its own shifts; Q's sha256 is the one the readout
names, Q's cells are the readout's and Q's sigma reproduces the readout's sigma_Q.

MEASURES: arithmetic on the committed readouts and Q. CANNOT AUTHORIZE: any claim, or any change to Q.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pv2d_lib as L  # noqa: E402
import report_tables as RT  # noqa: E402

VERTICES = RT.VERTICES
LABEL = "generator-shape model dependence; not a calibrated bound"
CAVEAT = ("kappa = 1, unscaled. Not a per-cell bias bound: on the 127 PV-2D positive-control cells (|bias| > 1 %, the "
          "NuWro closure bias of configuration (a)), the refined arm's NuWro |shift| reaches |bias| in 67, and "
          "sqrt(s_GENIE+MEC^2 + s_GiBUU^2), which leaves the bias's own vertex out, in 72. sqrt(diag C_model) reaches "
          "it in 116, but that includes the NuWro shift the bias was made from, so it is not evidence of coverage. "
          "The cells beside a step in r drawn by the noise gate or a cut (PV-2D REPORT §5, post hoc) go in as "
          "measured; they carry most of the large shifts.")


def factor(readout):
    """S, the (vertices x cells) relative shifts of the refined arm."""
    if readout.get("arm") != "refined":
        raise ValueError(f"readout arm {readout.get('arm')!r}, expected 'refined'")
    n = len(readout["cells"])
    if any(len(readout["vertices"][v]["shift"]) != n for v in VERTICES):
        raise ValueError("a vertex's shift array does not have one entry per cell")
    S = np.array([readout["vertices"][v]["shift"] for v in VERTICES], float)
    if not np.array_equal(np.abs(S).max(axis=0), np.asarray(readout["envelope"]["h"], float)):
        raise ValueError("the readout's envelope h is not max_k |s_k| of its own shifts")
    return S


def cmodel(S):
    """sum_k s_k s_k^T as elementwise products and sums in a fixed order, not BLAS, so its sha256 is the same on
    every platform."""
    C = np.zeros((S.shape[1], S.shape[1]))
    for s in S:
        C += np.outer(s, s)
    return C


def absolute(C, x):
    return C * np.outer(x, x)


def matrix_sha256(C):
    return hashlib.sha256(np.ascontiguousarray(C, dtype="<f8").tobytes()).hexdigest()


def quantiles(a):
    a = np.asarray(a, float)
    return {"median": float(np.median(a)), "p84": float(np.percentile(a, 84)),
            "p84_weibull": float(np.percentile(a, 84, method="weibull")), "p90": float(np.percentile(a, 90)),
            "max": float(np.max(a))}


def totals(S, sig_q):
    """Per-cell relative sigma of Q + C_model (M2) and the envelope form, and C_model's own sqrt-diagonal."""
    m2 = np.sqrt((S ** 2).sum(axis=0))
    h = np.abs(S).max(axis=0)
    return {"sqrt_diag": m2, "total_m2": np.sqrt(sig_q ** 2 + m2 ** 2), "h": h,
            "total_envelope": np.sqrt(sig_q ** 2 + h ** 2)}


def coverage(S, pc):
    """How often each sigma reaches |bias| on the PC's cells (|bias| > its min_abs_bias), with the PC's vertex."""
    bias = np.asarray(pc["bias_cells"], float)
    big = np.abs(bias) > pc["min_abs_bias"]
    k = VERTICES.index(pc["vertex"])
    others = [i for i in range(len(VERTICES)) if i != k]
    sig = {"own_vertex_shift": np.abs(S[k]), "leave_own_vertex_out": np.sqrt((S[others] ** 2).sum(axis=0)),
           "sqrt_diag_in_sample": np.sqrt((S ** 2).sum(axis=0))}
    return {"vertex": pc["vertex"], "cells": int(big.sum()),
            "reach": {name: int((s[big] >= np.abs(bias[big])).sum()) for name, s in sig.items()}}


def conditioning(Q, C, x):
    """Smallest eigenvalue and condition number of Q and Q + C_model, both in fractional units."""
    q = Q / np.outer(x, x)
    out = {}
    for name, M in (("Q", q), ("Q_plus_C_model", q + C)):
        e = np.linalg.eigvalsh(M)
        out[name] = {"min_eigenvalue": float(e.min()), "condition_number": float(e.max() / e.min())}
    return out


def load_q(path, readout):
    if L.sha256_path(path) != readout["inputs"]["Q"]["sha256"]:
        raise ValueError(f"{path}: sha256 differs from the readout's inputs.Q")
    z = np.load(path, allow_pickle=False)
    if list(z["cells"]) != list(readout["cells"]):
        raise ValueError("Q's cells differ from the readout's")
    x, Q = np.asarray(z["x"], float), np.asarray(z["Q"], float)
    sig_q = np.sqrt(np.diag(Q)) / x
    if np.max(np.abs(sig_q / np.asarray(readout["sigma_Q"]["cells"]) - 1.0)) > 1e-12:
        raise ValueError("Q's sigma does not reproduce the readout's sigma_Q")
    return Q, x, sig_q


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--readout", required=True, help="2d-unfolding/pv2d/readouts/readout_ref.json")
    ap.add_argument("--readout-a", required=True, help="2d-unfolding/pv2d/readouts/readout_a.json (the PC's bias)")
    ap.add_argument("--q", required=True, help="cov2d_Q_205.npz, the adopted Q")
    ap.add_argument("--projections", required=True, help="2d-unfolding/pv2d/ratios/projections.json")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-npz")
    a = ap.parse_args(argv)

    X, A = json.load(open(a.readout)), json.load(open(a.readout_a))
    I = RT.Inputs(a.projections, os.path.dirname(os.path.abspath(a.projections)))
    I.check(X, "refined")
    I.check(A, "a")
    S = factor(X)
    Q, x, sig_q = load_q(a.q, X)
    C = cmodel(S)
    C_abs = absolute(C, x)
    t = totals(S, sig_q)
    sv = np.linalg.svd(S, compute_uv=False)
    rank = int(np.linalg.matrix_rank(C))
    near = I.near["h"]
    trace_share = float(np.diag(C)[near].sum() / np.trace(C))

    out = {"schema": "pv2d-cmodel/1", "label": LABEL, "caveat": CAVEAT,
           "form": "C_model = sum_k s_k s_k^T (M2), kappa = 1; fractional. C_abs = diag(x) C_model diag(x), x = Q's x",
           "decision": "docs/orchestration/DECISION-20261024-joseph-2d-model-dependence-component.md",
           "inputs": {"readout": {"path": a.readout, "sha256": L.sha256_path(a.readout)},
                      "readout_a": {"path": a.readout_a, "sha256": L.sha256_path(a.readout_a)},
                      "Q": {"path_given": a.q, "path_recorded_by_readout": X["inputs"]["Q"]["path"],
                            "sha256": L.sha256_path(a.q)},
                      "projections": {"path": a.projections, "sha256": I.sha}},
           "cells": X["cells"], "vertices": list(VERTICES), "S": S.tolist(),
           "matrix_sha256": {"C_model": matrix_sha256(C), "C_abs": matrix_sha256(C_abs)},
           "rank": rank, "singular_values_S": sv.tolist(),
           "trace_share_by_vertex": dict(zip(VERTICES, ((S ** 2).sum(axis=1) / np.trace(C)).tolist())),
           "psd_min_eigenvalue": float(np.linalg.eigvalsh(C).min()),
           "conditioning_fractional": conditioning(Q, C, x),
           "coverage_vs_pc_bias": coverage(S, A["controls"]["PC"]["primary"]),
           "sqrt_diag": t["sqrt_diag"].tolist(), "sigma_Q": sig_q.tolist(), "total_m2": t["total_m2"].tolist(),
           "summary": {k: quantiles(t[k]) for k in ("sqrt_diag", "total_m2", "h", "total_envelope")},
           "sigma_Q_summary": quantiles(sig_q),
           "post_hoc": {"rule": "PV-2D REPORT §5: cells beside a construction-drawn step in r > 0.1, any vertex",
                        "cells": int(near.sum()), "trace_share": trace_share,
                        "sqrt_diag_rest": quantiles(t["sqrt_diag"][~near]),
                        "total_m2_rest": quantiles(t["total_m2"][~near]),
                        "sigma_Q_rest": quantiles(sig_q[~near])}}
    with open(a.out_json, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    if a.out_npz:
        np.savez(a.out_npz, C_model=C, C_abs=C_abs, S=S, cells=np.asarray(X["cells"]), x=x)

    s = out["summary"]
    pc = lambda v: f"{100 * v:.2f} %"  # noqa: E731
    print(f"C_model,2D: rank {rank}, singular values of S {', '.join(f'{v:.4f}' for v in sv)}")
    for k, name in (("sqrt_diag", "sqrt diag C_model"), ("total_m2", "sqrt(sigma_Q^2 + diag C_model)"),
                    ("h", "h = max_k |s_k|"), ("total_envelope", "sqrt(sigma_Q^2 + h^2)")):
        print(f"{name}: median {pc(s[k]['median'])}, p84 {pc(s[k]['p84'])} (weibull {pc(s[k]['p84_weibull'])}), "
              f"p90 {pc(s[k]['p90'])}, max {pc(s[k]['max'])}")
    print(f"sigma_Q: median {pc(out['sigma_Q_summary']['median'])}")
    cov = out["coverage_vs_pc_bias"]
    print(f"coverage on {cov['cells']} PC cells: " + ", ".join(f"{k} {v}" for k, v in cov["reach"].items()))
    print(f"conditioning (fractional): {out['conditioning_fractional']}")
    print(f"post hoc: {int(near.sum())} step-adjacent cells hold {100 * trace_share:.1f} % of tr C_model; rest: "
          f"sqrt diag median {pc(out['post_hoc']['sqrt_diag_rest']['median'])}, "
          f"total median {pc(out['post_hoc']['total_m2_rest']['median'])}, "
          f"sigma_Q median {pc(out['post_hoc']['sigma_Q_rest']['median'])}")
    print(f"sha256 C_model {out['matrix_sha256']['C_model']}  C_abs {out['matrix_sha256']['C_abs']}")


if __name__ == "__main__":
    main()
