#!/usr/bin/env python3
"""MP4-A, the P0-OSB diagnostic (PLAN section 5.3, frozen by BINDING-PHASE1-20261019 section 2).

Stages, in the frozen order (each refuses to run unless the previous one's record exists):

* ``gate``: positivity off, the OSB half-width of every reported functional against D-ID's committed
  T2 nominal ``sigma_rel`` (and the hole sets). Needs DECLARATION.json with matching code digests.
* ``osb``: positivity on, J (RD1) and H2 (RD2) reported functionals, the PASS rule. Needs a passing gate.

Operands come from ``build_problem.py`` (D-ID's own code). The Fisher is D-ID's ``fisher``; the
reduction and the solver are ``osb.py``. Hole functionals (null fraction > 1e-6) get only the exact
reductions declared in DECLARATION.json:

* Z (weight on a zero-efficiency truth cell j, h_j > 0): lam_j enters neither the ball nor any other
  constraint, so max = +inf exactly and the min has lam_j = 0 (the functional with those entries zeroed);
* P (exactly proportional response columns R[:, i] = alpha_i R[:, c]): only w = sum alpha_i lam_i is
  constrained, and over {lam_i >= 0, sum alpha_i lam_i = w} the functional's part ranges over
  w [min_i h_i / alpha_i, max_i h_i / alpha_i]; the class is merged into one cell with the min (lower
  endpoint) or max (upper endpoint) coefficient;
* anything else with null fraction > 1e-6 after Z and P: unresolved (+inf in the hole-inclusive
  statistics, never solved by another method).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import norm as sparse_norm
from scipy.stats import chi2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_problem  # noqa: E402
import osb  # noqa: E402

REPO = HERE.parents[2]
OUT = REPO / "docs/orchestration/state/measurement-paper/phase1/mp4a"
TABLES = REPO / "docs/orchestration/state/next-preparation-20261009/d-id/outputs/tables.npz"
CODE = ("osb.py", "run_mp4a.py", "build_problem.py")
PSI2 = float(chi2.ppf(0.6827, 1))
GATE_RTOL = 1e-6


def sha256(path: Path) -> str:
    return build_problem.sha256(path)


def code_digests() -> dict:
    return {name: sha256(HERE / name) for name in CODE}


def rss() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def cpu_all() -> float:
    a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def quantile_inf(v: np.ndarray, p: float) -> float:
    """numpy's default (linear) quantile, with +inf allowed: a neighbour carrying weight that is +inf
    gives +inf; a zero weight on it does not."""
    v = np.sort(np.asarray(v, float))
    pos = p * (v.size - 1)
    i = int(np.floor(pos))
    g = pos - i
    if g == 0 or i + 1 >= v.size:
        return float(v[i])
    if np.isinf(v[i]) or np.isinf(v[i + 1]):
        return float(np.inf)
    return float(v[i] + g * (v[i + 1] - v[i]))


def stats(v: np.ndarray) -> dict:
    v = np.asarray(v, float)
    fin = v[np.isfinite(v)]
    return {"n": int(v.size), "n_finite": int(fin.size), "n_inf": int(np.isinf(v).sum()),
            "median": quantile_inf(v, 0.5) if v.size else None, "p90": quantile_inf(v, 0.9) if v.size else None,
            "p90_numpy_variants": {m: float(np.quantile(v, 0.9, method=m)) for m in ("lower", "higher", "nearest")}
            if v.size else None,
            "min": float(v.min()) if v.size else None, "max": float(v.max()) if v.size else None}


# ------------------------------------------------------------------------------- operands


def load_operands(path: Path, expect: str):
    if sha256(path) != expect:
        raise RuntimeError("operands digest differs from the declaration")
    z = np.load(path, allow_pickle=False)
    r = sparse.csr_matrix((z["T2/R_data"], z["T2/R_indices"], z["T2/R_indptr"]), shape=tuple(z["T2/R_shape"]))
    return z, r


def whitened(r: sparse.csr_matrix, t: np.ndarray, b: np.ndarray) -> sparse.csr_matrix:
    """D-ID's fisher() factor: diag(1/sqrt(R t + b)) R on reco cells with positive expectation."""
    e = r @ t + b
    keep = e > 0
    return (sparse.diags(1.0 / np.sqrt(e[keep])) @ r[keep]).tocsr()


def proportional_classes(r: sparse.csr_matrix, eff: np.ndarray, rtol: float = 1e-12) -> list[dict]:
    """Classes of >= 2 non-zero response columns that are exactly proportional (same sparsity pattern,
    constant ratio to rtol)."""
    c = r.tocsc()
    groups: dict = {}
    for j in np.flatnonzero(eff > 0):
        lo, hi = c.indptr[j], c.indptr[j + 1]
        idx, val = c.indices[lo:hi], c.data[lo:hi]
        groups.setdefault(tuple(idx.tolist()), []).append((j, val))
    out = []
    for pattern, members in groups.items():
        if len(members) < 2:
            continue
        rep_j, rep_v = members[0]
        cls = [(rep_j, 1.0)]
        for j, v in members[1:]:
            ratio = v / rep_v
            if np.all(np.abs(ratio / ratio[0] - 1) <= rtol):
                cls.append((j, float(ratio[0])))
        if len(cls) >= 2:
            out.append({"cells": [int(j) for j, _ in cls], "alpha": [a for _, a in cls], "rep": int(rep_j)})
    return out


def merged_problem(r, t, b, classes):
    """Merge each proportional class into its representative column; returns R_m, t_m, the kept cell
    list (representatives stand for their class) and the class map."""
    n = t.size
    drop = np.zeros(n, bool)
    t_m = t.copy()
    for cl in classes:
        t_m[cl["rep"]] = sum(a * t[j] for j, a in zip(cl["cells"], cl["alpha"]))
        for j in cl["cells"]:
            if j != cl["rep"]:
                drop[j] = True
    keep = np.flatnonzero(~drop)
    r_m = r[:, keep]
    if not np.allclose(r_m @ t_m[keep], r @ t, rtol=1e-12, atol=0):
        raise RuntimeError("the merged fold differs from the original fold")
    return r_m.tocsr(), t_m[keep], keep


def merged_functional(h, classes, keep, sense):
    hm = h.copy()
    for cl in classes:
        q = [h[j] / a for j, a in zip(cl["cells"], cl["alpha"])]
        hm[cl["rep"]] = min(q) if sense == "min" else max(q)
    return hm[keep]


# ------------------------------------------------------------------------------- worker


_W: dict = {}


def _init(path: str, settings: dict) -> None:
    z = np.load(path, allow_pickle=False)
    for key in ("base", "merged"):
        if f"{key}/g" in z.files:
            _W[key] = osb.Reduced(g=z[f"{key}/g"], coef=z[f"{key}/coef"], vectors_null=z[f"{key}/vnull"],
                                  values=z[f"{key}/values"], t=z[f"{key}/t"])
    _W["settings"] = osb.Settings(**settings)


def _solve(task: tuple) -> dict:
    tid, problem_key, h, sense, positivity = task
    red = _W[problem_key]
    # positivity floor (declared): for a min with h >= 0, h . lam >= 0, i.e. h . delta >= -h . t
    floor = -float(h @ red.t) if (sense == "min" and positivity and np.all(h >= 0)) else None
    ep = osb.endpoint(red, h, sense, _W["settings"], positivity=positivity, floor=floor)
    return {"tid": tid, "value": ep.value, "s": ep.s, "g": ep.g, "evals": ep.evals, "converged": ep.converged,
            "status": ep.status, "feasible_value": ep.feasible_value, "dual_value": ep.dual_value,
            "n_active": ep.n_active, "lsq_status": ep.lsq_status, "lsq_nit_total": ep.lsq_nit_total,
            "kkt_rel": ep.kkt_rel, "kkt_sign_rel": ep.kkt_sign_rel, "cpu_s": ep.cpu_s, "wall_s": ep.wall_s,
            "nominal_part": float(h @ red.t)}


# ------------------------------------------------------------------------------- stages


def read_declaration() -> dict:
    p = OUT / "DECLARATION.json"
    if not p.exists():
        raise SystemExit("refusing: DECLARATION.json is absent")
    dec = json.loads(p.read_text())
    if dec["code_sha256"] != code_digests():
        raise SystemExit(f"refusing: code digests differ from DECLARATION.json: {code_digests()}")
    if abs(dec["settings"]["psi2"] - PSI2) > 0:
        raise SystemExit("refusing: psi2 differs")
    return dec


def prepare(dec: dict, scratch: Path) -> dict:
    """Fisher (D-ID's function), reduction, null-mode checks; saved for the workers."""
    did = build_problem.load_did()
    z, r = load_operands(Path(dec["inputs"]["operands_path"]), dec["inputs"]["operands_sha256"])
    t, b, eff = z["T2/t"], z["T2/b"], z["T2/eff"]
    f = did.fisher(r, t, b)
    red = osb.reduce(f, t)
    a = whitened(r, t, b)
    anorm = float(sparse_norm(a))
    null_resid = np.linalg.norm(a @ red.vectors_null, axis=0) / anorm
    classes = proportional_classes(r, eff)
    rec = {"reduction": red.info, "null_mode_resid_rel_frobenius": null_resid.tolist(),
           "n_zero_eff": int(np.sum(eff <= 0)), "proportional_classes": classes,
           "reduction_check_rel": None}
    # ||A d||^2 == ||G d||^2 on random directions (the reduction is exact on the kept space)
    rng = np.random.default_rng(0)
    dev = 0.0
    for _ in range(20):
        d = rng.normal(size=t.size) * t
        d -= red.vectors_null @ (red.vectors_null.T @ d)
        ad, gd = a @ d, red.g @ d
        dev = max(dev, abs(gd @ gd / (ad @ ad) - 1))
    rec["reduction_check_rel"] = dev
    arrays = {"base/g": red.g, "base/coef": red.coef, "base/vnull": red.vectors_null, "base/values": red.values,
              "base/t": red.t}
    if classes:
        r_m, t_m, keep = merged_problem(r, t, b, classes)
        f_m = did.fisher(r_m, t_m, b)
        red_m = osb.reduce(f_m, t_m)
        rec["merged_reduction"] = red_m.info
        arrays.update({"merged/g": red_m.g, "merged/coef": red_m.coef, "merged/vnull": red_m.vectors_null,
                       "merged/values": red_m.values, "merged/t": red_m.t, "merged/keep": keep})
    path = scratch / "reduced_T2.npz"
    np.savez(path, **arrays)
    rec["reduced_path"] = str(path)
    rec["reduced_sha256"] = sha256(path)
    return rec, z, red, arrays


def reported_rows(z, groups=("J", "H2", "EW")):
    f183, g183, rep = z["f183"], z["groups183"], z["reported183"]
    rows = []
    for grp in groups:
        for pos in np.flatnonzero((g183 == grp) & rep):
            rows.append({"group": grp, "pos183": int(pos), "row185": int(f183[pos]), "name": str(z["names"][f183[pos]])})
    return rows


def stage_gate(args) -> int:
    dec = read_declaration()
    c0, w0 = cpu_all(), time.time()
    prep, z, red, _ = prepare(dec, args.scratch)
    tables = np.load(TABLES)
    if sha256(TABLES) != dec["inputs"]["did_tables_sha256"]:
        raise SystemExit("tables.npz digest differs")
    did_sig = tables["T2/nominal/widths_nom/sigma_rel"]
    h_all, t = z["T2/H"], z["T2/t"]
    rows = reported_rows(z)
    out_rows = []
    worst = {"unit_radius": 0.0, "frozen_radius_normalized": 0.0, "frozen_radius_literal": 0.0}
    hole_agree = True
    for row in rows:
        h = h_all[row["row185"]]
        nominal = float(h @ t)
        nf = osb.null_fraction(red, h)
        mine_hole = nf > osb.NULL_TOL
        want = float(did_sig[row["pos183"]])
        rec = {**row, "null_fraction": nf, "did_sigma_rel": want, "hole_mine": bool(mine_hole),
               "hole_did": bool(np.isinf(want))}
        if mine_hole != np.isinf(want):
            hole_agree = False
        if not mine_hole:
            for label, psi2 in (("unit_radius", 1.0), ("frozen_radius", PSI2)):
                st = osb.Settings(**{**dec["settings"], "psi2": psi2})
                lo = osb.endpoint(red, h, "min", st, positivity=False)
                hi = osb.endpoint(red, h, "max", st, positivity=False)
                hw = 0.5 * (hi.value - lo.value) / abs(nominal)
                rec[label] = {"half_width_rel": hw, "lo_status": lo.status, "hi_status": hi.status,
                              "lsq_status": sorted(set(lo.lsq_status + hi.lsq_status)), "evals": lo.evals + hi.evals}
            d_unit = abs(rec["unit_radius"]["half_width_rel"] / want - 1)
            d_norm = abs(rec["frozen_radius"]["half_width_rel"] / np.sqrt(PSI2) / want - 1)
            d_lit = abs(rec["frozen_radius"]["half_width_rel"] / want - 1)
            rec.update({"dev_unit_radius": d_unit, "dev_frozen_radius_normalized": d_norm,
                        "dev_frozen_radius_literal": d_lit})
            worst["unit_radius"] = max(worst["unit_radius"], d_unit)
            worst["frozen_radius_normalized"] = max(worst["frozen_radius_normalized"], d_norm)
            worst["frozen_radius_literal"] = max(worst["frozen_radius_literal"], d_lit)
        out_rows.append(rec)
    finite_ok = all(r.get("dev_unit_radius", 0.0) <= GATE_RTOL and r.get("dev_frozen_radius_normalized", 0.0) <= GATE_RTOL
                    for r in out_rows)
    statuses_ok = all(r[k]["lo_status"] == "converged" and r[k]["hi_status"] == "converged"
                      for r in out_rows if not r["hole_mine"] for k in ("unit_radius", "frozen_radius"))
    res = {"schema": "mp4a-gate/1", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "code_sha256": code_digests(), "psi2": PSI2, "psi": float(np.sqrt(PSI2)), "psi_minus_1": float(np.sqrt(PSI2) - 1),
           "tolerance": GATE_RTOL, "prepare": prep, "n_rows": len(out_rows),
           "n_by_group": {g: sum(1 for r in out_rows if r["group"] == g) for g in ("J", "H2", "EW")},
           "worst_rel_dev": worst, "hole_sets_agree": hole_agree, "all_endpoints_converged": statuses_ok,
           "pass_unit_radius_reading": bool(finite_ok and hole_agree and statuses_ok),
           "pass_literal_reading": bool(worst["frozen_radius_literal"] <= GATE_RTOL and hole_agree and statuses_ok),
           "rows": out_rows,
           "resources": {"cpu_s": cpu_all() - c0, "wall_s": time.time() - w0, "peak_rss_bytes": rss()}}
    (OUT / "gate.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "prepare")}, indent=1, default=float))
    return 0 if res["pass_unit_radius_reading"] else 4


def stage_osb(args) -> int:
    dec = read_declaration()
    gate = json.loads((OUT / "gate.json").read_text())
    if not gate["pass_unit_radius_reading"] or gate["code_sha256"] != code_digests():
        raise SystemExit("refusing: the gate did not pass (or ran on other code)")
    c0, w0 = cpu_all(), time.time()
    red_path = Path(gate["prepare"]["reduced_path"])
    if sha256(red_path) != gate["prepare"]["reduced_sha256"]:
        raise SystemExit("reduced operands differ from the gate's")
    z, r = load_operands(Path(dec["inputs"]["operands_path"]), dec["inputs"]["operands_sha256"])
    zr = np.load(red_path)
    base = osb.Reduced(g=zr["base/g"], coef=zr["base/coef"], vectors_null=zr["base/vnull"], values=zr["base/values"],
                       t=zr["base/t"])
    merged = None
    classes = gate["prepare"]["proportional_classes"]
    if "merged/g" in zr.files:
        merged = osb.Reduced(g=zr["merged/g"], coef=zr["merged/coef"], vectors_null=zr["merged/vnull"],
                             values=zr["merged/values"], t=zr["merged/t"])
        keep = zr["merged/keep"]
    h_all, t, eff = z["T2/H"], z["T2/t"], z["T2/eff"]
    rows = reported_rows(z, groups=("J", "H2"))
    tasks, plan = [], []
    for i, row in enumerate(rows):
        h = h_all[row["row185"]]
        nominal = float(h @ t)
        zcells = np.flatnonzero((eff <= 0) & (h != 0))
        entry = {**row, "nominal": nominal, "null_fraction": osb.null_fraction(base, h),
                 "zero_eff_cells": zcells.tolist(), "endpoints": {}}
        for sense in ("min", "max"):
            hs = h.copy()
            if zcells.size:
                sign_bad = (h[zcells] > 0) if sense == "max" else (h[zcells] < 0)
                if np.any(sign_bad):
                    entry["endpoints"][sense] = {"route": "Z", "abs": np.inf if sense == "max" else -np.inf,
                                                 "status": "proved-infinite"}
                    continue
                hs[zcells] = 0.0  # lam_j = 0 at this endpoint (h_j has the endpoint's sign)
            nf = osb.null_fraction(base, hs)
            if nf <= osb.NULL_TOL:
                route, key, hv, offset = ("Z+base" if zcells.size else "base"), "base", hs, float(hs @ t)
            elif merged is not None:
                hm = merged_functional(hs, classes, keep, sense)
                nfm = osb.null_fraction(merged, hm)
                if nfm > osb.NULL_TOL:
                    entry["endpoints"][sense] = {"route": "unresolved", "abs": np.inf if sense == "max" else -np.inf,
                                                 "status": "unresolved", "null_fraction_after_P": nfm}
                    continue
                route, key, hv, offset = ("Z+P" if zcells.size else "P"), "merged", hm, float(hm @ merged.t)
            else:
                entry["endpoints"][sense] = {"route": "unresolved", "abs": np.inf if sense == "max" else -np.inf,
                                             "status": "unresolved", "null_fraction_after_Z": nf}
                continue
            entry["endpoints"][sense] = {"route": route, "offset": offset, "null_fraction_solved": nf}
            tasks.append((len(plan), key, hv, sense, True))
            plan.append((i, sense))
        rows[i] = entry
    cap_s = 3600.0 * dec["budget"]["osb_stage_cpu_core_hours_cap"]
    spent = 0.0
    results = {}
    ctx = mp.get_context("spawn")
    with ctx.Pool(args.workers, initializer=_init, initargs=(str(red_path), dec["settings"])) as pool:
        for res in pool.imap_unordered(_solve, tasks):
            results[res["tid"]] = res
            spent += res["cpu_s"]
            if spent > cap_s:
                pool.terminate()
                print(f"CAP: {spent:.0f} CPU-s > {cap_s:.0f}", file=sys.stderr)
                break
            print(f"[{len(results)}/{len(tasks)}] {res['status']} evals={res['evals']} cpu={res['cpu_s']:.1f}s", flush=True)
    for tid, (i, sense) in enumerate(plan):
        ep = rows[i]["endpoints"][sense]
        res = results.get(tid)
        if res is None:
            ep.update({"status": "not-run-cap", "abs": np.inf if sense == "max" else -np.inf})
            continue
        ep.update({k: v for k, v in res.items() if k != "tid"})
        ep["abs"] = ep["offset"] + res["value"] if res["converged"] else (np.inf if sense == "max" else -np.inf)
        if not res["converged"]:
            ep["route"] = ep["route"] + "/unresolved"
    group_vals: dict = {}
    for e in rows:
        lo, hi = e["endpoints"]["min"], e["endpoints"]["max"]
        e["lo_abs"], e["hi_abs"] = lo["abs"], hi["abs"]
        e["half_width_rel"] = 0.5 * (hi["abs"] - lo["abs"]) / abs(e["nominal"])
        e["class"] = ("finite" if np.isfinite(e["half_width_rel"]) else
                      ("proved-infinite" if any(x.get("status") == "proved-infinite" for x in (lo, hi))
                       else "unresolved"))
        group_vals.setdefault(e["group"], []).append(e)
    summary = {}
    for grp, es in group_vals.items():
        hw = np.array([e["half_width_rel"] for e in es])
        is_hole_did = np.array([e["null_fraction"] > osb.NULL_TOL for e in es])
        unresolved = np.array([e["class"] == "unresolved" for e in es])
        summary[grp] = {"holes_as_inf": stats(hw),
                        "excluding_did_holes": stats(hw[~is_hole_did]),
                        "excluding_unresolved_only": stats(hw[~unresolved]),
                        "n_did_holes": int(is_hole_did.sum()), "n_unresolved": int(unresolved.sum()),
                        "n_proved_infinite": int(sum(e["class"] == "proved-infinite" for e in es)),
                        "n_holes_made_finite": int(np.sum(is_hole_did & np.isfinite(hw)))}
    j = summary["J"]

    def verdict(s):
        return "PASS" if (s["median"] <= 0.10 and s["p90"] <= 0.25) else "FAIL"

    v_inc, v_exc = verdict(j["holes_as_inf"]), verdict(j["excluding_did_holes"])
    out = {"schema": "mp4a-osb/1", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "code_sha256": code_digests(), "psi2": PSI2, "settings": dec["settings"],
           "verdict_J_T2": {"holes_as_inf": v_inc, "excluding_holes": v_exc,
                            "depends_on_hole_treatment": v_inc != v_exc},
           "summary": summary, "n_tasks": len(tasks), "n_solved": len(results),
           "resources": {"cpu_s_parent_and_children": cpu_all() - c0, "cpu_s_sum_endpoints": spent,
                         "wall_s": time.time() - w0, "peak_rss_bytes_parent": rss(), "workers": args.workers}}
    (OUT / "osb_summary.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    (OUT / "osb_functionals.json").write_text(json.dumps(rows, indent=1, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("gate", "osb"))
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(argv)
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        if os.environ.get(var) is None:
            raise SystemExit(f"refusing: set {var}")
    return {"gate": stage_gate, "osb": stage_osb}[a.stage](a)


if __name__ == "__main__":
    sys.exit(main())
