#!/usr/bin/env python3
"""RSN C_model variants and the WR shifts (RSN-DECLARATION.md §3), from the RSN products and L-5D-PV's frozen ones.
Numpy only; runs on a login node.

    rsn_cmodel.py nc    --product <OUT>/products/rsn_nc.npz --products <frozen> --p5 <P5> --out <OUT>/nc.json
    rsn_cmodel.py build --rsn-products <OUT>/products --rsn-prep-sums rsn-prep-SHA256SUMS --products <frozen>
                        --p5 <P5> --out-json <OUT>/cmodel/rsn_cmodel.json --out-npz <OUT>/cmodel/rsn_cmodel.npz

nc     The NC (§2.4): rsn_nc equals P5 and the frozen L-5D-PV_e_tune_v1 bitwise on the full grid and on the reporting
       cells (build_cmodel5d.nominal_control). Refuses otherwise; J2 is not submitted without its PASS.
build  Refuses, writing nothing, unless the NC holds again; the frozen products pass build_cmodel5d's own checks and
       rebuild cmodel_5d.json's S bitwise (NC-S); and every RSN product's meta is the declared task's (rung, arm,
       features, closure, ratio sha256, seed 42, 5 iterations, 32 threads, inputs, estimator and refinement
       parameters equal to the frozen tune_v1 product's, the regressor weight and its fit count).
       Then, with X_0 = rsn_nc's integrals on the 16 cells:
         G6: S^G6 = (s_genie_mec, s_nuwro, s'_gibuu), with s'_gibuu = X(G6_gibuu) / X_0 - 1 and the other two rows
             cmodel_5d.json's own;
         SM: S^SM = (X(SM_k) / X_0 - 1 for each k), only if the prep built SM;
         WR: delta = X(WR_data) / X_0 - 1, and each WR closure's bias X / X_true - 1 beside the frozen closure's.
       C^V = S^V^T S^V. Writes S per arm, its per-cell sqrt-diagonal, trace and trace shares. It prints no absolute
       cell value.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: any claim, or a change to C_model.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
_ROOT = _ND.parent
_PVL = _ND / "pv-ladder"
for _p in (str(_PVL), str(_ND), str(_ROOT / "2d-unfolding" / "pv2d"), str(_ROOT / "2d-unfolding" / "pv2d" / "cmodel")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import build_cmodel5d as B5  # noqa: E402
import pv2d_lib as P  # noqa: E402
import pvl_lib as L  # noqa: E402

VERTICES = B5.VERTICES
TASKS = _HERE / "rsn_tasks.tsv"
CMODEL_JSON = _PVL / "readouts" / "cmodel_5d.json"
STAGE1 = _ROOT / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
FEATURES = list(L.AXES5)
SEED, ITERS, THREADS = 42, 5, 32
CLOSURES = {"tune_v1": "L-5D-PV_e_closure_tune_v1", "nuwro": "L-5D-PV_e_closure_nuwro"}


def tasks(path: Path = TASKS) -> dict:
    out = {}
    for ln in path.read_text().splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        task, job, arm, ratio, closure, weight, _ = ln.split("\t")
        if job == "J2n":
            continue
        out[task] = {"job": job, "arm": arm, "ratio": ratio, "closure": closure == "yes", "regressor_weight": weight}
    return out


def ratio_sha(spec: str, pvl_sums: dict, rsn_sums: dict) -> str:
    src, rel = spec.split(":", 1)
    if src == "frozen":
        return pvl_sums[f"./ratios/{B5.RUNG}/{rel}.json"]
    if src == "rsn":
        return rsn_sums[f"./{rel}.json"]
    raise SystemExit(f"[FAIL] unknown ratio source {spec}")


def sums(path: Path) -> dict:
    return dict(ln.split()[::-1] for ln in Path(path).read_text().splitlines() if ln.strip())


def read_product(path: Path) -> tuple[dict, np.ndarray, np.ndarray | None]:
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    x = np.asarray(z["xsec_flat"], float)
    xt = np.asarray(z["xtrue_flat"], float) if "xtrue_flat" in z.files else None
    return meta, x, xt


def meta_problems(meta: dict, spec: dict, want_ratio: str, ref: dict) -> list[str]:
    """The declared task's identity, against the frozen tune_v1 product's meta (ref) for what must not change."""
    bad = []
    ident = {"schema": "pvl-unfold/1", "rung": B5.RUNG, "arm": "e", "features": FEATURES, "closure": spec["closure"],
             "ratio_sha256": want_ratio, "estimator_seed": SEED, "iters": ITERS, "threads": THREADS}
    for k, v in ident.items():
        if meta.get(k) != v:
            bad.append(f"{k} {meta.get(k)!r} != {v!r}")
    for k in ("input_npz_sha256", "bkg_dump_sha256", "estimator_params"):
        if meta.get(k) != ref.get(k):
            bad.append(f"{k} differs from the frozen tune_v1 product's")
    ref_refine = ref.get("refinement") or {}
    refine = meta.get("refinement") or {}
    if spec["closure"]:
        if refine.get("ran") is not False:
            bad.append("a closure must record that the refinement did not run")
    elif refine.get("classifier_params") != ref_refine.get("classifier_params") or refine.get("ran") is not True:
        bad.append("refinement parameters differ from the frozen tune_v1 product's")
    rsn = meta.get("rsn") or {}
    if rsn.get("regressor_weight") != spec["regressor_weight"]:
        bad.append(f"regressor weight {rsn.get('regressor_weight')!r} != {spec['regressor_weight']!r}")
    want_calls = ITERS if spec["regressor_weight"] == "w_truth" else None
    if rsn.get("fit_calls") != want_calls:
        bad.append(f"weighted regressor fits {rsn.get('fit_calls')!r} != {want_calls!r}")
    return bad


def frozen(a) -> tuple:
    rmap, n, _, _, _ = B5.load_definition(a.definition, a.stage1, B5.EXPECT)
    cfg, T, ratios = B5.provenance_refs(_PVL / "config.json", _PVL / "tasks.tsv", _PVL / "prep-SHA256SUMS")
    prod = B5.load_products(a.products, B5.EXPECT, cfg, T, ratios)
    if L.sha256_path(a.p5) != B5.EXPECT["p5"]:
        raise SystemExit(f"[FAIL] {a.p5}: sha256 is not P5's")
    p5 = np.asarray(np.load(a.p5, allow_pickle=True)["xsec_flat"], float)
    return rmap, n, prod, p5


def nominal(x_nc: np.ndarray, p5: np.ndarray, rmap: np.ndarray, n: int) -> dict:
    """build_cmodel5d's NC (a)-(c) on rsn_nc against P5. The frozen L-5D-PV_e_tune_v1 equals P5 bitwise
    (cmodel_5d.json nominal_control), so rsn_nc then equals it too."""
    rec, _ = B5.nominal_control(x_nc, p5, rmap, n)
    return rec


def run_nc(a) -> dict:
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    rmap, n, prod, p5 = frozen(a)
    meta, x, _ = read_product(a.product)
    ref = json.loads(str(np.load(Path(a.products) / "L-5D-PV_e_tune_v1.npz", allow_pickle=True)["meta"]))
    spec = tasks()["rsn_nc"]
    bad = meta_problems(meta, spec, sums(_PVL / "prep-SHA256SUMS")[f"./ratios/{B5.RUNG}/tune_v1.json"], ref)
    if bad:
        raise SystemExit(f"[FAIL] rsn_nc: {'; '.join(bad)}")
    rec = {"schema": "rsn-nc/1", "product_sha256": L.sha256_path(a.product), "nominal_control": nominal(x, p5, rmap, n),
           "verdict": "PASS", "code_sha256": {"rsn_cmodel.py": L.sha256_path(__file__)}}
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    print("[rsn] NC PASS: rsn_nc equals P5 and L-5D-PV_e_tune_v1 bitwise")
    return rec


def describe(S: np.ndarray) -> dict:
    C = S.T @ S
    tr = float(np.trace(C))
    return {"S": S.tolist(), "sqrt_diag": np.sqrt(np.diag(C)).tolist(), "trace": tr,
            "trace_share_by_vertex": dict(zip(VERTICES, ((S ** 2).sum(axis=1) / tr).tolist())),
            "psd_min_eigenvalue": float(np.linalg.eigvalsh(C).min())}


def run_build(a) -> dict:
    for p in (a.out_json, a.out_npz):
        if p.exists():
            raise SystemExit(f"[FAIL] refusing to overwrite {p}")
    rmap, n, prod, p5 = frozen(a)
    S0 = B5.factor(prod, rmap, n)
    committed = json.loads(Path(a.cmodel_json).read_text())
    if not np.array_equal(S0, np.asarray(committed["S"], float)):
        raise SystemExit("[FAIL] NC-S: the frozen products do not rebuild cmodel_5d.json's S bitwise")
    pvl_sums, rsn_sums = sums(_PVL / "prep-SHA256SUMS"), sums(a.rsn_prep_sums)
    ref = json.loads(str(np.load(Path(a.products) / "L-5D-PV_e_tune_v1.npz", allow_pickle=True)["meta"]))
    T = tasks()
    sm_built = any(k.startswith("./SM/") for k in rsn_sums)
    got, shas = {}, {}
    for task, spec in T.items():
        if spec["arm"] == "SM" and not sm_built:
            continue
        path = Path(a.rsn_products) / f"{task}.npz"
        meta, x, xt = read_product(path)
        bad = meta_problems(meta, spec, ratio_sha(spec["ratio"], pvl_sums, rsn_sums), ref)
        if bad:
            raise SystemExit(f"[FAIL] {task}: {'; '.join(bad)}")
        got[task], shas[task] = (x, xt), L.sha256_path(path)
    nc = nominal(got["rsn_nc"][0], p5, rmap, n)

    def X(task):
        return B5.integrals(got[task][0], rmap, n)

    X0 = X("rsn_nc")
    arms = {"nominal": S0}
    arms["G6"] = np.vstack([S0[0], S0[1], P.rel_shift(X("G6_gibuu"), X0)])
    if sm_built:
        arms["SM"] = np.vstack([P.rel_shift(X(f"SM_{v}"), X0) for v in VERTICES])
    wr = {"delta": P.rel_shift(X("WR_data"), X0).tolist(), "closures": {}}
    for truth, name in CLOSURES.items():
        task = f"WR_closure_{truth}"
        b_w = P.rel_shift(X(task), B5.integrals(got[task][1], rmap, n))
        b_0 = P.rel_shift(B5.integrals(prod[name]["x"], rmap, n), B5.integrals(prod[name]["xtrue"], rmap, n))
        wr["closures"][truth] = {"bias_weighted": b_w.tolist(), "bias_frozen": b_0.tolist()}
    out = {"schema": "rsn-cmodel/1", "nominal_control": nc, "nc_s": "the frozen products rebuild cmodel_5d.json's S bitwise",
           "products_sha256": shas, "sm_built": sm_built, "vertices": list(VERTICES),
           "arms": {k: describe(S) for k, S in arms.items()}, "wr": wr,
           "inputs": {"cmodel_json": L.sha256_path(a.cmodel_json), "rsn_prep_sums": L.sha256_path(a.rsn_prep_sums)},
           "code_sha256": {"rsn_cmodel.py": L.sha256_path(__file__), "build_cmodel5d.py": L.sha256_path(B5.__file__)}}
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(out, indent=1) + "\n")
    np.savez(a.out_npz, **{f"S_{k}": S for k, S in arms.items()})
    print(f"[rsn] built {', '.join(arms)}; GiBUU trace share "
          + ", ".join(f"{k} {out['arms'][k]['trace_share_by_vertex']['gibuu']:.3f}" for k in arms))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("nc", "build"):
        s = sub.add_parser(name)
        s.add_argument("--products", type=Path, required=True, help="the frozen L-5D-PV products")
        s.add_argument("--p5", type=Path, required=True)
        s.add_argument("--definition", type=Path, default=_PVL / "readouts" / "h2_definition.json")
        s.add_argument("--stage1", type=Path, default=STAGE1)
    sub.choices["nc"].add_argument("--product", type=Path, required=True)
    sub.choices["nc"].add_argument("--out", type=Path, required=True)
    b = sub.choices["build"]
    b.add_argument("--rsn-products", type=Path, required=True)
    b.add_argument("--rsn-prep-sums", type=Path, default=_HERE / "rsn-prep-SHA256SUMS")
    b.add_argument("--cmodel-json", type=Path, default=CMODEL_JSON)
    b.add_argument("--out-json", type=Path, required=True)
    b.add_argument("--out-npz", type=Path, required=True)
    a = ap.parse_args(argv)
    (run_nc if a.cmd == "nc" else run_build)(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
