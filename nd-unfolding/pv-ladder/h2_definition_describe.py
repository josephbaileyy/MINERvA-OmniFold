#!/usr/bin/env python3
"""The H2 reporting definition's cells, described from simulation only (H2-DEFINITION-DECLARATION.md §1.3; numpy only).

Per reporting cell of h2_definition.json, as s2_h2_scope.py does per H2 cell: the prior's truth-weight share, each
vertex's truth-level departure d_k = sum(p r_k) / sum(p) - 1, GiBUU's r = 1 share at p_parallel >= 10 GeV/c, the share
beside a gate- or cut-drawn step in r > 0.1 (union over the vertices), and the NuWro closure bias and the closure floor.
These describe the cells; none of them entered the merge rule, which used purity alone.

Never opens a data product. MEASURES: arithmetic on the frozen reweights, two closure products and the definition.
CANNOT AUTHORIZE: the definition, any claim.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import pvl_lib as L  # noqa: E402
import s2_h2_scope as S2  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--definition", type=Path, default=_HERE / "readouts" / "h2_definition.json")
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios/L-5D-PV directory")
    ap.add_argument("--products", type=Path, required=True, help="a directory holding the two closure products")
    ap.add_argument("--prep-sums", type=Path, default=_HERE / "prep-SHA256SUMS")
    ap.add_argument("--receipts", type=Path, default=_HERE.parents[1] /
                    "docs/orchestration/state/measurement-scoping/pv-ladder/receipts/SHA256SUMS")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    prep = dict(ln.split()[::-1] for ln in a.prep_sums.read_text().splitlines() if ln.strip())
    rec = dict(ln.split()[::-1] for ln in a.receipts.read_text().splitlines() if ln.strip())
    inputs = {"h2_definition.json": L.sha256_path(a.definition)}
    for f in ["ratios.json"] + [f"{v}.json" for v in S2.VERTICES]:
        inputs[f"ratios/{S2.RUNG}/{f}"] = S2.check(a.ratios / f, prep[f"./ratios/{S2.RUNG}/{f}"], f)
    for c in S2.CLOSURES:
        inputs[f"products/{c}.npz"] = S2.check(a.products / f"{c}.npz", rec[f"products/{c}.npz"], c)
    D = L.load_json(a.definition)
    cell, _ = S2.h2_of_fine()
    lut = np.asarray(D["h2_to_reporting_cell"])
    rmap = lut[cell]
    n = int(D["n_reporting_cells"])
    ok = rmap >= 0

    def agg(v):
        return np.bincount(rmap[ok], weights=np.asarray(v, float)[ok], minlength=n)

    R = L.load_json(a.ratios / "ratios.json")
    shape = tuple(len(L.FINE[x]) - 1 for x in L.AXES5)
    p = np.asarray(R["prior_truth_weight"], float)
    P = agg(p)
    pz_hi = np.asarray(L.FINE["pz"][1:])[np.unravel_index(np.arange(p.size), shape)[1]]
    out = {"schema": "h2-definition-describe/1", "simulation_only": True, "inputs": inputs,
           "code": {"h2_definition_describe.py": L.sha256_path(__file__), "s2_h2_scope.py": L.sha256_path(S2.__file__),
                    "pvl_lib.py": L.sha256_path(L.__file__)},
           "prior_share": (P / p.sum()).tolist(), "departure": {}}
    near = np.zeros(p.size, bool)
    for v in S2.VERTICES:
        rv = R["vertices"][v]
        r = np.asarray(L.load_json(a.ratios / rv["ratio_file"])["r"], float)
        lab = np.asarray(rv["label"], dtype=object)
        near |= np.isin(L.classify_cells(r, lab, shape), ("gate", "cut"))
        out["departure"][v] = (agg(p * r) / P - 1.0).tolist()
        if v == "gibuu":
            out["gibuu_r1_pz_ge_10_share"] = (agg(p * (np.isin(lab, ("noisy", "off")) & (pz_hi > 10.0))) / P).tolist()
    out["step_adjacent_share_union"] = (agg(p * near) / P).tolist()
    for c in S2.CLOSURES:
        z = np.load(a.products / f"{c}.npz", allow_pickle=True)
        x, xt = agg(L.integrated(z["xsec_flat"], L.AXES5)), agg(L.integrated(z["xtrue_flat"], L.AXES5))
        out[f"bias_{c}"] = (x / xt - 1.0).tolist()
    b = np.asarray(out["bias_L-5D-PV_e_closure_nuwro"])
    out["n_abs_bias_gt_0.01"] = int((np.abs(b) > 0.01).sum())
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print("| cell | H2 cells | purity | stability | prior share | d GENIE+MEC / NuWro / GiBUU | GiBUU r=1, p∥≥10 | "
          "step-adjacent | NuWro closure bias |")
    print("|---|---|---:|---:|---:|---|---:|---:|---:|")
    for c in D["reporting_cells"]:
        i = c["id"]
        print(f"| R{i:02d} | {', '.join(map(str, c['h2_cells']))} | {c['purity']:.3f} | {c['stability']:.3f} | "
              f"{100 * out['prior_share'][i]:.1f} % | "
              + " / ".join(f"{100 * out['departure'][v][i]:+.1f} %" for v in S2.VERTICES)
              + f" | {100 * out['gibuu_r1_pz_ge_10_share'][i]:.0f} % | {100 * out['step_adjacent_share_union'][i]:.0f} % | "
                f"{100 * b[i]:+.2f} % |")
    f = np.asarray(out["bias_L-5D-PV_e_closure_tune_v1"])
    print(f"\ncells with |NuWro closure bias| > 1 %: {out['n_abs_bias_gt_0.01']} of {n}; closure floor max {np.abs(f).max():.1e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
