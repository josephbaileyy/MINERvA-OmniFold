#!/usr/bin/env python3
"""C_model,5D on the 16 H2 reporting cells, from L-5D-PV's (e) unfolds (numpy only).

The construction is H2-DEFINITION-DECLARATION.md §3, approved in DECISION-20261024-joseph-h2-16-cell-definition.md, with
GiBUU's domain as H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md option (i). M2, kappa = 1:

    X_k,c = sum_{f in c} x_k,f vol_f,   s_k,c = X_k,c / X_0,c - 1,   C_model = sum_k s_k s_k^T,

over the reporting cells c of readouts/h2_definition.json, for k in (GENIE+MEC, NuWro, GiBUU); X_0 is L-5D-PV_e_tune_v1.
C_model is fractional; C_abs = diag(x) C_model diag(x) with x = P5's integrals on the same cells.

Refuses, writing nothing, unless:
  the definition's sha256 and its expanded fine map's sha256 are the approved ones, and the Stage-1 receipt (the 27 base
      cells) is the declared one;
  every product's sha256 is the declared one, and its provenance passes pvl_analyze.check_meta against the ladder's
      config, tasks and prep-SHA256SUMS (rung, arm, closure, inputs, ratio, features, seed, refinement, prior guards,
      the same code and estimator parameters across the products);
  P5's sha256 is the declared one;
  the NC holds: L-5D-PV_e_tune_v1 equals P5 bitwise on the full grid and on the reporting cells, and the cell integrals
      by pvl_lib.integrated equal those by s5p_stage1_inspect.fine_volume.
The PC at NuWro (pv2d_lib.positive_control, rule unchanged) is graded on the 27 base H2 cells; its 16-cell readout is
labelled "not powered" whatever it returns. A PC that does not PASS labels the product; it does not stop the build.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: any claim, the total with S1's covariance, or a change
to the cells.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
for _p in (str(_HERE), str(_HERE.parent), str(_ROOT / "2d-unfolding" / "pv2d"), str(_ROOT / "2d-unfolding" / "pv2d" / "cmodel")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import build_cmodel as B2  # noqa: E402  (the 2D builder: cmodel, absolute, matrix_sha256)
import pv2d_lib as P  # noqa: E402
import pvl_analyze as A  # noqa: E402
import pvl_lib as L  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402

RUNG = "L-5D-PV"
VERTICES = ("genie_mec", "nuwro", "gibuu")
PC_VERTEX = "nuwro"
EXPECT = {
    "definition": "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
    "fine_map": "930326a3a7c0852d4047b5468d8ea3b63d046b896e4a4de1557e29f95102e18c",
    "stage1": "def4c67cfb59f5ae917f86d2745416b172be6aca3764eba11f3d116db4621d9d",
    "p5": "e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2",
    "products": {
        "L-5D-PV_e_tune_v1": "dbe9a95e746fba127811182e9a352f6dc243d78ff699e803611b5deedbcb0f4f",
        "L-5D-PV_e_genie_mec": "bdff9193b04f17c4aa9d97e7d9c26221b03dc8c9b0d2376cd775e6b195b749c5",
        "L-5D-PV_e_nuwro": "caf6eee726ddb128d26cf74fad2a2b4e69273607a2a0e1e4a48750766bddc66f",
        "L-5D-PV_e_gibuu": "bdf331570daeb3dc56d6096e2c39ca3e7a6091339680eb58034ee9a14c82f3c3",
        "L-5D-PV_e_closure_nuwro": "fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182",
        "L-5D-PV_e_closure_tune_v1": "eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08",
    },
}
LABELS = {
    "component": "generator-shape model dependence; not a calibrated bound (M2, kappa = 1, unscaled)",
    "coverage": "coverage at held-out truths was not validated (DECISION-20261024-joseph-5d-community-standard-route.md "
                "item 3); the paper states this as a limitation",
    "gibuu": "GiBUU's shape is applied on p_parallel < 10 GeV/c; above it the prior is unchanged. At 6 <= p_parallel < "
             "10 GeV/c GiBUU's sample lacks the E_nu > 20 GeV part, 4.9-5.3 % of the cross section there. The paper's "
             "joint tests use the narrower p_parallel < 6 GeV/c (H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md)",
    "step_adjacent": "in every reporting cell 77-100 % of the prior weight lies beside a step in r > 0.1 drawn by the noise "
                     "gate or a cut, where PV-2D found the large-shift tail; the shifts go in as measured "
                     "(H2-DEFINITION-DECLARATION.md §1.3, §3.4)",
}
PC_LABEL = {"PASS": "positive control passed on the 27 base H2 cells",
            "FAIL": "positive control failed on the 27 base H2 cells: not evidence",
            "NOT_POWERED": "positive control not powered on the 27 base H2 cells: not evidence"}


def sha_bytes(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def load_definition(path, stage1_path, expect):
    """Fine cell -> reporting cell (-1 = not reported), the reporting cells' records, and fine cell -> base H2 cell
    among s5p's 27 reported ones. Refuses on any digest mismatch."""
    if L.sha256_path(path) != expect["definition"]:
        raise SystemExit(f"[FAIL] {path}: sha256 is not the approved definition's")
    if L.sha256_path(stage1_path) != expect["stage1"]:
        raise SystemExit(f"[FAIL] {stage1_path}: sha256 is not the declared Stage-1 receipt's")
    D = json.loads(Path(path).read_text())
    cell, n32 = s1.coarse_map(s1.H2_EDGES)
    lut = np.asarray(D["h2_to_reporting_cell"], int)
    rmap = lut[cell].astype("<i4")
    got = sha_bytes(rmap)
    if got != D["fine_map_sha256_int32le"] or got != expect["fine_map"]:
        raise SystemExit(f"[FAIL] the expanded fine map's sha256 {got} is not the approved one")
    n = int(D["n_reporting_cells"])
    if sorted(c["id"] for c in D["reporting_cells"]) != list(range(n)) or set(lut[lut >= 0]) != set(range(n)):
        raise SystemExit("[FAIL] the definition's reporting cells are not 0..n-1")
    reported = np.asarray(json.loads(Path(stage1_path).read_text())["mc"]["H2"]["reported"], bool)
    if reported.size != n32 or int(reported.sum()) != 27:
        raise SystemExit("[FAIL] the Stage-1 receipt does not report 27 of the 32 H2 cells")
    base_lut = -np.ones(n32, int)
    base_lut[reported] = np.arange(27)
    return rmap.astype(int), n, D["reporting_cells"], base_lut[cell], np.flatnonzero(reported).tolist()


def provenance_refs(config_path, tasks_path, prep_sums_path):
    """What pvl_analyze.check_meta compares a product against, from the ladder's committed config, tasks and sums."""
    cfg = json.loads(Path(config_path).read_text())["rungs"][RUNG]
    T = A.tasks(tasks_path)
    sums = dict(ln.split()[::-1] for ln in Path(prep_sums_path).read_text().splitlines() if ln.strip())
    ratios = {"vertices": {v: {"ratio_sha256": sums[f"./ratios/{RUNG}/{v}.json"]} for v in ("tune_v1",) + VERTICES}}
    return cfg, T, ratios


def load_products(products_dir, expect, cfg, T, ratios):
    out, ref = {}, None
    for name, want in expect["products"].items():
        p = Path(products_dir) / f"{name}.npz"
        got = L.sha256_path(p)
        if got != want:
            raise SystemExit(f"[FAIL] {p.name}: sha256 {got} is not the declared {want}")
        z = np.load(p, allow_pickle=True)
        meta = json.loads(str(z["meta"]))
        A.check_meta(p.name, meta, T[name], ratios, cfg, ref)
        if ref is None:
            ref = dict(meta, _name=p.name)
        out[name] = {"x": np.asarray(z["xsec_flat"], float), "sha256": got}
        if "xtrue_flat" in z.files:
            out[name]["xtrue"] = np.asarray(z["xtrue_flat"], float)
    return out


def integrals(x, cmap, n):
    xi = L.integrated(x, L.AXES5)
    ok = cmap >= 0
    return np.bincount(cmap[ok], weights=xi[ok], minlength=n)


def integrals_s5p(x, cmap, n):
    """The same cell integrals through s5p_stage1_inspect's own fine volumes (NC c)."""
    ok = cmap >= 0
    return np.bincount(cmap[ok], weights=(np.asarray(x, float) * s1.fine_volume())[ok], minlength=n)


def nominal_control(x0, p5, rmap, n):
    """NC (a)-(c). Refuses unless all hold bitwise."""
    X0, X5 = integrals(x0, rmap, n), integrals(p5, rmap, n)
    rec = {"a_full_grid_bitwise": bool(np.array_equal(x0, p5)),
           "b_cells_bitwise": bool(np.array_equal(X0, X5)),
           "b_cells": P.nominal_control(X0, X5),
           "c_integration_routes_bitwise": bool(np.array_equal(X0, integrals_s5p(x0, rmap, n)))}
    if not (rec["a_full_grid_bitwise"] and rec["b_cells_bitwise"] and rec["c_integration_routes_bitwise"]):
        raise SystemExit(f"[FAIL] nominal control: {rec}")
    return rec, X5


def factor(prod, rmap, n):
    X0 = integrals(prod["L-5D-PV_e_tune_v1"]["x"], rmap, n)
    return np.array([P.rel_shift(integrals(prod[f"L-5D-PV_e_{v}"]["x"], rmap, n), X0) for v in VERTICES])


def check_factor(S, C):
    """NC (d): C is S^T S, and h = max_k |s_k| is what the envelope gives."""
    if not np.allclose(C, S.T @ S, rtol=1e-12, atol=0.0):
        raise SystemExit("[FAIL] C_model is not S^T S")
    h, _ = P.envelope(dict(zip(VERTICES, S)))
    if not np.array_equal(h, np.abs(S).max(axis=0)):
        raise SystemExit("[FAIL] h is not max_k |s_k|")
    return h


def positive_control(prod, rmap16, n16, base_map, n27):
    """The declared PC on the 27 base cells, and the same arithmetic on the 16 reporting cells, labelled; with the
    closure floor (L-5D-PV_e_closure_tune_v1 against its truth) on each."""
    cl, fl = prod["L-5D-PV_e_closure_nuwro"], prod["L-5D-PV_e_closure_tune_v1"]
    out, sh = {}, {}
    for name, cmap, n in (("base27", base_map, n27), ("reporting16", rmap16, n16)):
        bias = P.rel_shift(integrals(cl["x"], cmap, n), integrals(cl["xtrue"], cmap, n))
        shift = P.rel_shift(integrals(prod[f"L-5D-PV_e_{PC_VERTEX}"]["x"], cmap, n),
                            integrals(prod["L-5D-PV_e_tune_v1"]["x"], cmap, n))
        rec = P.positive_control(shift, bias)
        rec["bias_cells"], rec["shift_cells"] = bias.tolist(), shift.tolist()
        rec["closure_floor_max_abs"] = float(np.max(np.abs(P.rel_shift(integrals(fl["x"], cmap, n),
                                                                      integrals(fl["xtrue"], cmap, n)))))
        big = np.abs(bias) > rec["min_abs_bias"]
        rec["shift_ge_bias_frac"] = float(np.mean(np.abs(shift)[big] >= np.abs(bias)[big])) if big.any() else None
        out[name], sh[name] = rec, shift
    out["graded"] = "base27"
    out["verdict"] = out["base27"]["verdict"]
    out["label"] = PC_LABEL[out["verdict"]]
    out["reporting16"]["label"] = "not powered: the 16 reporting cells cannot carry the declared rule (ungraded)"
    return out


def coverage(S, bias, min_abs_bias, vertex=PC_VERTEX):
    """C_model,2D's descriptive counts on the PC's cells (S on the same cells as the bias)."""
    k = VERTICES.index(vertex)
    others = [i for i in range(len(VERTICES)) if i != k]
    big = np.abs(bias) > min_abs_bias
    sig = {"own_vertex_shift": np.abs(S[k]), "leave_own_vertex_out": np.sqrt((S[others] ** 2).sum(axis=0)),
           "sqrt_diag_in_sample": np.sqrt((S ** 2).sum(axis=0))}
    return {"vertex": vertex, "cells": int(big.sum()),
            "reach": {name: int((s[big] >= np.abs(bias[big])).sum()) for name, s in sig.items()},
            "note": "sqrt_diag_in_sample includes the bias's own vertex: not evidence of coverage"}


def build(a, expect=EXPECT):
    for p in (a.out_json, a.out_npz):
        if p is not None and Path(p).exists():
            raise SystemExit(f"[FAIL] refusing to overwrite {p}")
    rmap, n, cells, base_map, base_cells = load_definition(a.definition, a.stage1, expect)
    cfg, T, ratios = provenance_refs(a.config, a.tasks, a.prep_sums)
    prod = load_products(a.products, expect, cfg, T, ratios)
    if L.sha256_path(a.p5) != expect["p5"]:
        raise SystemExit(f"[FAIL] {a.p5}: sha256 is not P5's")
    p5 = np.asarray(np.load(a.p5, allow_pickle=True)["xsec_flat"], float)
    nc, x = nominal_control(prod["L-5D-PV_e_tune_v1"]["x"], p5, rmap, n)
    S = factor(prod, rmap, n)
    C = B2.cmodel(S)
    h = check_factor(S, C)
    C_abs = B2.absolute(C, x)
    pc = positive_control(prod, rmap, n, base_map, 27)
    S27 = factor(prod, base_map, 27)
    sv = np.linalg.svd(S, compute_uv=False)
    out = {"schema": "cmodel5d/1", "labels": dict(LABELS, positive_control=pc["label"]),
           "form": "C_model = sum_k s_k s_k^T (M2), kappa = 1; fractional. C_abs = diag(x) C_model diag(x), x = P5's "
                   "integrals on the reporting cells",
           "records": ["docs/orchestration/state/measurement-scoping/pv-ladder/H2-DEFINITION-DECLARATION.md",
                       "docs/orchestration/state/measurement-scoping/pv-ladder/H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md",
                       "docs/orchestration/DECISION-20261024-joseph-h2-16-cell-definition.md"],
           "inputs": {"definition_sha256": expect["definition"], "fine_map_sha256": expect["fine_map"],
                      "stage1_sha256": expect["stage1"], "p5_sha256": expect["p5"],
                      "products_sha256": {k: v["sha256"] for k, v in prod.items()},
                      "config_sha256": L.sha256_path(a.config), "tasks_sha256": L.sha256_path(a.tasks),
                      "prep_sums_sha256": L.sha256_path(a.prep_sums)},
           "code_sha256": {f.name: L.sha256_path(f) for f in
                           (Path(__file__).resolve(), Path(B2.__file__).resolve(), Path(P.__file__).resolve(),
                            Path(A.__file__).resolve(), Path(L.__file__).resolve(), Path(s1.__file__).resolve())},
           "argv": sys.argv,
           "cells": [{"id": c["id"], "h2_cells": c["h2_cells"], "box": c["box"]} for c in sorted(cells, key=lambda c: c["id"])],
           "vertices": list(VERTICES), "S": S.tolist(), "x": x.tolist(), "sqrt_diag": np.sqrt(np.diag(C)).tolist(),
           "h": h.tolist(), "matrix_sha256": {"C_model": B2.matrix_sha256(C), "C_abs": B2.matrix_sha256(C_abs)},
           "rank": int(np.linalg.matrix_rank(C)), "singular_values_S": sv.tolist(),
           "trace_share_by_vertex": dict(zip(VERTICES, ((S ** 2).sum(axis=1) / np.trace(C)).tolist())),
           "psd_min_eigenvalue": float(np.linalg.eigvalsh(C).min()),
           "nominal_control": nc, "positive_control": pc,
           "coverage_vs_pc_bias_base27": dict(coverage(S27, np.asarray(pc["base27"]["bias_cells"]),
                                                       pc["base27"]["min_abs_bias"]), base_h2_cells=base_cells),
           "summary": {"sqrt_diag": B2.quantiles(np.sqrt(np.diag(C))), "h": B2.quantiles(h)}}
    Path(a.out_json).write_text(json.dumps(out, indent=1) + "\n")
    if a.out_npz:
        np.savez(a.out_npz, C_model=C, C_abs=C_abs, S=S, x=x, cells=np.arange(n))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--products", type=Path, required=True, help="the directory holding the six L-5D-PV products")
    ap.add_argument("--p5", type=Path, required=True, help="RE-1's out/5d/k1_p5_rerun.npz")
    ap.add_argument("--definition", type=Path, default=_HERE / "readouts" / "h2_definition.json")
    ap.add_argument("--stage1", type=Path, default=_ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json")
    ap.add_argument("--config", type=Path, default=_HERE / "config.json")
    ap.add_argument("--tasks", type=Path, default=_HERE / "tasks.tsv")
    ap.add_argument("--prep-sums", type=Path, default=_HERE / "prep-SHA256SUMS")
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-npz", type=Path)
    a = ap.parse_args(argv)
    out = build(a)
    s, pc = out["summary"], out["positive_control"]
    print(f"[c5d] NC {out['nominal_control']}")
    print(f"[c5d] PC (27 base cells) {pc['verdict']}: n {pc['base27']['n_cells']}, corr {pc['base27']['corr']}, "
          f"slope {pc['base27']['slope']}; 16-cell readout n {pc['reporting16']['n_cells']} ({pc['reporting16']['label']})")
    print(f"[c5d] rank {out['rank']}; sqrt diag median {100 * s['sqrt_diag']['median']:.2f} %, max "
          f"{100 * s['sqrt_diag']['max']:.2f} %; h median {100 * s['h']['median']:.2f} %")
    print(f"[c5d] coverage {out['coverage_vs_pc_bias_base27']['reach']} of {out['coverage_vs_pc_bias_base27']['cells']}")
    print(f"[c5d] sha256 C_model {out['matrix_sha256']['C_model']}  C_abs {out['matrix_sha256']['C_abs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
