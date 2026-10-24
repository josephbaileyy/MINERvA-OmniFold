#!/usr/bin/env python3
"""5D design Stage 0, Part A (STAGE0-PARTA-DECLARATION.md): Stages 0a and 0b, read-only, on existing products.

0a  calibration transfer. For each held-out generator family F, build the M2 envelope component
    u^(-F)_f = (sum over vertices outside F of s_k,f^2)^(1/2) from the study-P data shifts s_k = J_k / J_CV - 1,
    calibrate kappa^(-F) as the smallest kappa covering >= 0.68 of the OTHER families' (fold, cell) pairs
    (|b_f| <= kappa u_f, cells with |departure| > 1%), and score c_F, the covered fraction of F's own pairs.
0b  usefulness. kappa* is calibrated on all folds with all vertices; the J (or H2) median over reported cells of
    u*_f = kappa* (sum_k s_k,f^2)^(1/2) must be <= 8.6%; and the noise-corrected expected shape-only
    Delta-chi^2 between each stage-1 generator pair's R-unfolded mean and nominal must be >= 9 for >= 2 pairs.
    GRADED covariance (DESIGN section 8 literally): C_stat(e) from the 50 R data bootstrap replicas + C_model
    (kappa*^2 sum_{k != own vertex} s_k s_k^T) + the (a) z-cv total, projected to the cells and made relative.
    z-cv's total already holds (a)'s statistical block, so statistics count twice here: the graded variant is the
    conservative one. The z-cv-only variant (no C_stat(e)) is reported, not graded.

M2 is the declared form (DECISION-20261023 fifth, item 8); M1 (h = max_k |s_k|) is reported, not graded.
b = mean over the R ensemble of (f_hat / f_true - 1); departure = mean truth / mean nominal truth - 1.
The reporting rule (item 1): RD1 if J passes 0a and 0b, otherwise RD2 if H2 passes, otherwise STOP.

Usage (login node; numpy only; reads products, writes one JSON, refuses to overwrite):
  python3 -I stage0_analysis.py --repo DIR --inventory INVENTORY.sha256 --mode provisional|binding \
      --prior-dir DIR --assess-dir DIR --data-dir DIR --zcv FILE --out JSON \
      [binding: --d1-new FILE --gibuu-new-dir DIR --ratio-new JSON --ctl-prior FILE --ctl-gibuu FILE]
Exit: 0 written (the verdict is inside); 3 a control failed (STOP, written with the failing control); 2 usage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

KAPPA_Q_PCT = 68          # integer percent: the rank is ceil(68 n / 100) in integer arithmetic
KAPPA_Q95_PCT = 95
C_FAMILY_MIN = 0.60
POOLED_MIN = 0.68
U_BAR_PCT = 8.6            # W = 10% minus the 1.4% normalization floor (DECISION-20261023 fifth, item 2)
DCHI2_MIN = 9.0
N_PAIRS_MIN = 2
DEPARTURE_MIN = 0.01
SHAPE_LAMBDA = 1.0e2       # variance of the free normalization mode added for shape-only (relative units)
SETS = ("J", "H2")          # graded
REPORT_SETS = ("J", "H2", "EW")   # EW reported, not graded (RD3 is not a reporting option, DECISION-20261023 fifth item 1)
D0_TOL = 1e-5               # stage2-exit:106-107: d0 equals the CV path to < 1e-5 relative, not bitwise
# vertex -> prior product; folds -> (family, assess subdir); own vertex of each stage-1 pair
FAMILIES_PROVISIONAL = {"NuWro": {"vertices": ("d2", "d4", "d5"), "folds": ("W1", "W3", "q3")},
                        "GENIE_MEC": {"vertices": ("d3",), "folds": ("W2",)}}
FAMILIES_BINDING = dict(FAMILIES_PROVISIONAL, GiBUU={"vertices": ("d1new",), "folds": ("GiBUU_new",)})
PAIRS = {"W2": "d3", "W3": "d4", "W1": "d2", "GiBUU_new": "d1new"}   # stage-1 pair truth -> its own vertex
# q3 is a fold but not a pair: the stage-1 use-case pairs are the four fixed-generator differences (amendment-1:10)
NEW_SEEDS = tuple(range(801000, 801020))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def kappa_q(ratios: np.ndarray, qpct: int) -> float:
    """Smallest kappa with at least qpct% of the ratios |b|/u <= kappa (rank ceil(qpct n / 100), integer arithmetic)."""
    r = np.sort(np.asarray(ratios, float))
    if r.size == 0:
        raise ValueError("empty population")
    k = -(-qpct * r.size // 100)
    return float(r[max(0, k - 1)])


def ratios(b: np.ndarray, u: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(u > 0, np.abs(b) / np.where(u > 0, u, 1.0), np.where(b == 0, 0.0, np.inf))


def dchi2(d: np.ndarray, C: np.ndarray, Cnoise: np.ndarray, shape_only: bool) -> dict:
    n = d.size
    if shape_only:
        C = C + SHAPE_LAMBDA * np.ones((n, n))
    ev = np.linalg.eigvalsh(C)
    if ev.min() <= 0:
        raise FloatingPointError(f"covariance not positive definite (min eigenvalue {ev.min():.3e})")
    raw = float(d @ np.linalg.solve(C, d))
    noise = float(np.trace(np.linalg.solve(C, Cnoise)))
    return {"raw": raw, "noise_expectation": noise, "corrected": raw - noise, "min_eigenvalue": float(ev.min())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for k in ("repo", "inventory", "prior-dir", "assess-dir", "data-dir", "zcv", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    ap.add_argument("--mode", choices=("provisional", "binding"), required=True)
    for k in ("d1-new", "gibuu-new-dir", "ratio-new", "ctl-prior", "ctl-gibuu"):
        ap.add_argument(f"--{k}", type=Path)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    if a.mode == "binding" and None in (a.d1_new, a.gibuu_new_dir, a.ratio_new, a.ctl_prior, a.ctl_gibuu):
        raise SystemExit("binding mode needs --d1-new, --gibuu-new-dir, --ratio-new, --ctl-prior and --ctl-gibuu")
    sys.path.insert(0, str(a.repo / "nd-unfolding"))
    import s5p_stage2_analyze as s2  # noqa: E402

    res = {"schema": "5d-design-stage0/1", "mode": a.mode, "rules": {
        "kappa_q_pct": KAPPA_Q_PCT, "c_family_min": C_FAMILY_MIN, "pooled_min": POOLED_MIN, "u_bar_pct": U_BAR_PCT,
        "dchi2_min": DCHI2_MIN, "n_pairs_min": N_PAIRS_MIN, "departure_min": DEPARTURE_MIN, "form": "M2",
        "graded_covariance": "C_stat(e) + C_model + z-cv total (relative)", "d0_tol": D0_TOL},
        "code_sha256": sha256(Path(__file__).resolve()), "controls": {}, "inputs": {}}

    def stop(name, detail):
        res["controls"][name] = {"pass": False, "detail": detail}
        res["verdict"] = f"STOP: control {name} failed"
        a.out.write_text(json.dumps(res, indent=1, default=float) + "\n")
        print(res["verdict"], detail, flush=True)
        return 3

    # C1: every inventoried input has its recorded sha256
    inv = {}
    for line in a.inventory.read_text().splitlines():
        h, p = line.split(None, 1)
        inv[p.strip()] = h
    used = []

    def take(p: Path) -> Path:
        used.append(str(p))
        return p

    stage1 = a.repo / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
    contract = a.repo / "docs/orchestration/state/s5c/contract.json"
    cells = s2.Cells(json.loads(stage1.read_text()), json.loads(contract.read_text()))
    res["inputs"]["stage1_sha256"], res["inputs"]["s5c_contract_sha256"] = sha256(stage1), sha256(contract)

    # shifts
    prior = {"CV": take(a.prior_dir / "prior_R5fix_CV.npz")}
    for k in ("d0", "d1", "d2", "d3", "d4", "d5"):
        prior[k] = take(a.prior_dir / f"prior_R5fix_prior_{k}.npz")
    J = {k: cells.of(s2.load(p)["xsec_flat"]) for k, p in prior.items()}
    if a.mode == "binding":
        # 0c controls (DECLARATION section 4 step 4): the reruns with the committed ratio reproduce the old products
        old_d1 = take(a.prior_dir / "prior_R5fix_prior_d1.npz")
        old_g = take(a.assess_dir / "eavail_gibuu" / "eavail_shape_a1_s801000.npz")
        cp = {"prior_d1_xsec": bool(np.array_equal(np.load(a.ctl_prior)["xsec_flat"], np.load(old_d1)["xsec_flat"]))}
        zg, zo = np.load(a.ctl_gibuu), np.load(old_g)
        cp["gibuu_801000_xsec"] = bool(np.array_equal(zg["xsec_flat"], zo["xsec_flat"]))
        cp["gibuu_801000_xtrue"] = bool(np.array_equal(zg["xtrue_flat"], zo["xtrue_flat"]))
        if not all(cp.values()):
            return stop("C0c_reruns_reproduce_old_products", cp)
        res["controls"]["C0c_reruns_reproduce_old_products"] = {"pass": True, **cp}
        rsha = sha256(a.ratio_new)
        m1 = s2.load(a.d1_new)["meta"]
        if m1.get("ratio_sha256", m1.get("eavail_ratio_sha256")) not in (rsha, None) or m1.get("prior") != "d1":
            return stop("C6_binding_inputs_valid", {"d1_new_meta": {k: m1.get(k) for k in ("prior", "ratio_sha256", "eavail_ratio_sha256")}})
        J["d1new"] = cells.of(s2.load(a.d1_new)["xsec_flat"])
        res["inputs"]["d1_new"] = {"path": str(a.d1_new), "sha256": sha256(a.d1_new), "meta_prior": m1.get("prior")}
        res["inputs"]["ratio_new"] = {"path": str(a.ratio_new), "sha256": rsha}
    s = {k: {P: np.where(J["CV"][P] > 0, J[k][P] / np.where(J["CV"][P] > 0, J["CV"][P], 1) - 1.0, 0.0)
             for P in cells.maps} for k in J if k != "CV"}

    # ensembles: R bias folds and nominal
    fold_dirs = {"W1": "W1", "W2": "W2", "W3": "W3", "q3": "q3", "nominal": "nominal"}
    ens = {}
    for name, sub in fold_dirs.items():
        files = sorted((a.assess_dir / sub).glob("*.npz"))
        [take(f) for f in files]
        rel, T, n = s2.ensemble(files, cells)
        A = cells.stack([np.load(f)["xsec_flat"] for f in files])
        ens[name] = {"b": {P: rel[P].mean(0) for P in rel}, "T": T, "n": n, "A": A}
    if a.mode == "binding":
        files = [a.gibuu_new_dir / f"eavail_shape_a1_s{sd}.npz" for sd in NEW_SEEDS]
        missing = [str(f) for f in files if not f.exists()]
        oldcode = json.loads(str(np.load(old_g)["meta"]))["code_sha256"]
        badm = []
        for f in files:
            if f.exists():
                mm = json.loads(str(np.load(f)["meta"]))
                if mm.get("eavail_ratio_sha256") != rsha or mm.get("code_sha256") != oldcode:
                    badm.append(f.name)
        if missing or badm:
            return stop("C6_binding_inputs_valid", {"missing": missing, "bad_meta": badm})
        res["controls"]["C6_binding_inputs_valid"] = {"pass": True, "n_gibuu_new": len(files)}
        rel, T, n = s2.ensemble(files, cells)
        A = cells.stack([np.load(f)["xsec_flat"] for f in files])
        ens["GiBUU_new"] = {"b": {P: rel[P].mean(0) for P in rel}, "T": T, "n": n, "A": A}
        res["inputs"]["gibuu_new"] = {"dir": str(a.gibuu_new_dir), "n": n,
                                      "sha256": {f.name: sha256(f) for f in files}}

    bad = [p for p in used if inv.get(p) != sha256(Path(p))]
    if bad:
        return stop("C1_inputs_match_inventory", {"n_mismatch": len(bad), "first": bad[:5]})
    res["controls"]["C1_inputs_match_inventory"] = {"pass": True, "n_files": len(used)}

    # C2: the CV path equals the N1 base data unfold bitwise; the nominal-prior control d0 equals the CV path to
    # < 1e-5 relative on every reported cell (as recorded: stage2_receipt study_P.controls; stage2-exit:106-107)
    base = take(a.data_dir / "data_b-_j-.npz")
    if inv.get(str(base)) != sha256(base):
        return stop("C1_inputs_match_inventory", {"file": str(base)})
    xb = np.load(base)["xsec_flat"]
    cv_eq = bool(np.array_equal(np.load(prior["CV"])["xsec_flat"], xb))
    d0dev = {P: float(np.max(np.abs(s["d0"][P][cells.reported[P]]))) for P in cells.maps}
    if not cv_eq or max(d0dev.values()) >= D0_TOL:
        return stop("C2_controls", {"CV_equals_N1_base": cv_eq, "d0_max_rel_dev": d0dev})
    res["controls"]["C2_controls"] = {"pass": True, "CV_equals_N1_base": cv_eq, "d0_max_rel_dev": d0dev}

    # C3: reproduce the committed envelope receipt's h medians (with and without D1)
    rec = json.loads((a.repo / "docs/orchestration/state/s5p/stage3/envelope-receipt.json").read_text())
    c3 = {}
    for key, use in (("envelope_D1_D5", ("d1", "d2", "d3", "d4", "d5")), ("envelope_without_D1", ("d2", "d3", "d4", "d5"))):
        for P in ("J", "H2", "EW"):
            m = cells.reported[P]
            h = np.max([np.abs(s[k][P]) for k in use], axis=0)
            got, want = 100 * float(np.median(h[m])), float(rec[key][P]["h_median_pct"])
            c3[f"{key}/{P}"] = [got, want]
    if any(abs(g - w) > 1e-9 * max(1.0, abs(w)) for g, w in c3.values()):
        return stop("C3_envelope_receipt_reproduced", c3)
    res["controls"]["C3_envelope_receipt_reproduced"] = {"pass": True, "h_median_pct": c3}

    # z-cv, projected to the reporting cells (relative to the (a) central), with the C4 identity check
    z = np.load(take(a.zcv), allow_pickle=False)
    if inv.get(str(a.zcv)) != sha256(a.zcv):
        return stop("C1_inputs_match_inventory", {"file": str(a.zcv)})
    rows, Cz, xa = z["hRowIndex5D"], z["hCov_combined5d_total_uthrow"], z["hXSecND_flat"]
    Jb = cells.of(xb)
    c4 = {"rows_equal_support_mask": bool(np.array_equal(rows, np.flatnonzero(z["hSupportMask"] > 0))),
          "shape": list(Cz.shape)}
    for P in REPORT_SETS:
        cm, n = cells.maps[P]
        hit = np.bincount(cm[rows][cm[rows] >= 0], minlength=n) > 0
        c4[f"{P}_reported_cells_without_rows"] = int(np.sum(cells.reported[P] & ~hit))
    ja, jb = cells.of(xa)["J"][cells.reported["J"]], Jb["J"][cells.reported["J"]]
    c4["J_median_a_over_e_data"] = float(np.median(ja / jb))
    if not (c4["rows_equal_support_mask"] and Cz.shape == (rows.size, rows.size)
            and all(c4[f"{P}_reported_cells_without_rows"] == 0 for P in REPORT_SETS)
            and 0.8 <= c4["J_median_a_over_e_data"] <= 1.25):
        return stop("C4_zcv_indexing", c4)
    Zrel = {}
    for P in REPORT_SETS:
        cm, n = cells.maps[P]
        M = np.zeros((n, rows.size))
        ok = cm[rows] >= 0
        M[cm[rows][ok], np.nonzero(ok)[0]] = cells.vol[rows][ok]
        xm = np.zeros_like(xa)
        xm[rows] = xa[rows]
        c4[f"{P}_projection_identity_max_rel_dev"] = float(np.max(np.abs(M @ xa[rows] - cells.of(xm)[P])) / max(1e-300, np.max(np.abs(cells.of(xm)[P]))))
        Ja = cells.of(xa)[P]
        with np.errstate(divide="ignore", invalid="ignore"):
            inv_ja = np.where(Ja > 0, 1.0 / Ja, 0.0)
        Zrel[P] = (M @ Cz @ M.T) * np.outer(inv_ja, inv_ja)
    res["controls"]["C4_zcv_indexing"] = {"pass": True, **c4}

    # C_stat(e) from the 50 jittered data bootstrap replicas (sensitivity variant only)
    boot = [take(a.data_dir / f"data_b{i}_j{100 + i}.npz") for i in range(1, 51)]
    bad = [str(p) for p in boot if inv.get(str(p)) != sha256(p)]
    if bad:
        return stop("C1_inputs_match_inventory", {"first": bad[:3]})
    B = cells.stack([np.load(p)["xsec_flat"] for p in boot])

    fam = FAMILIES_BINDING if a.mode == "binding" else FAMILIES_PROVISIONAL
    V = sorted({v for f in fam.values() for v in f["vertices"]})
    res["vertices"], res["families"] = V, fam
    out = {}
    for P in REPORT_SETS:
        m = cells.reported[P]
        Tn = ens["nominal"]["T"][P]

        def pairs(folds, vertices, P=P, m=m, Tn=Tn):
            u2 = np.sqrt(np.sum([s[k][P] ** 2 for k in vertices], axis=0))
            uh = np.max([np.abs(s[k][P]) for k in vertices], axis=0)
            rr2, rrh = [], []
            for t in folds:
                with np.errstate(divide="ignore", invalid="ignore"):
                    dep = np.where(Tn > 0, ens[t]["T"][P] / np.where(Tn > 0, Tn, 1) - 1.0, 0.0)
                sel = m & (np.abs(dep) > DEPARTURE_MIN)
                rr2.append(ratios(ens[t]["b"][P][sel], u2[sel]))
                rrh.append(ratios(ens[t]["b"][P][sel], uh[sel]))
            return np.concatenate(rr2), np.concatenate(rrh)

        # 0a
        a0 = {"families": {}}
        cov_all, n_all = 0, 0
        for F, spec in fam.items():
            outside = [v for v in V if v not in spec["vertices"]]
            others = [t for G, g in fam.items() if G != F for t in g["folds"]]
            cal2, calh = pairs(others, outside)
            sc2, sch = pairs(spec["folds"], outside)
            k2, kh = kappa_q(cal2, KAPPA_Q_PCT), kappa_q(calh, KAPPA_Q_PCT)
            c2 = float(np.mean(sc2 <= k2))
            a0["families"][F] = {"kappa_M2": k2, "c_M2": c2, "n_pairs": int(sc2.size), "n_cal_pairs": int(cal2.size),
                                 "kappa_M1": kh, "c_M1": float(np.mean(sch <= kh)), "vertices_in_envelope": outside}
            cov_all += int(np.sum(sc2 <= k2))
            n_all += int(sc2.size)
        a0["pooled_M2"] = cov_all / n_all
        a0["pass"] = bool(all(v["c_M2"] >= C_FAMILY_MIN for v in a0["families"].values()) and a0["pooled_M2"] >= POOLED_MIN)
        # 0b
        folds_all = [t for g in fam.values() for t in g["folds"]]
        r2, rh = pairs(folds_all, V)
        kstar = kappa_q(r2, KAPPA_Q_PCT)
        u_star = kstar * np.sqrt(np.sum([s[k][P] ** 2 for k in V], axis=0))
        med_u = 100 * float(np.median(u_star[m]))
        idx = np.nonzero(m)[0]
        An = ens["nominal"]["A"][P][:, idx]
        mu_n = An.mean(0)
        Cs = np.cov(B[P][:, idx] / Jb[P][idx], rowvar=False)
        pair_res = {}
        for t, own in PAIRS.items():
            if t not in ens:
                continue
            Ag = ens[t]["A"][P][:, idx]
            d = Ag.mean(0) / mu_n - 1.0
            # Var(mean_g / mean_n), first order: Var(mean_g)/mu_n^2 + (mu_g/mu_n^2)^2 Var(mean_n)
            Cn = np.cov(Ag / mu_n, rowvar=False) / Ag.shape[0] + np.cov(An * (Ag.mean(0) / mu_n ** 2), rowvar=False) / An.shape[0]
            Cm = kstar ** 2 * np.sum([np.outer(s[k][P][idx], s[k][P][idx]) for k in V if k != own], axis=0)
            Cp = Zrel[P][np.ix_(idx, idx)] + Cm
            try:
                pair_res[t] = {"own_vertex": own,
                               "graded_shape": dchi2(d, Cp + Cs, Cn, True), "graded_total": dchi2(d, Cp + Cs, Cn, False),
                               "zcv_only_shape": dchi2(d, Cp, Cn, True)}
            except FloatingPointError as e:
                if P in SETS:
                    return stop("C5_covariance_positive_definite", {"set": P, "pair": t, "error": str(e)})
                pair_res[t] = {"own_vertex": own, "error": str(e)}   # EW is reported only; it never stops the run
        n_ok = sum(1 for v in pair_res.values() if "graded_shape" in v and v["graded_shape"]["corrected"] >= DCHI2_MIN)
        b0 = {"kappa_star_M2": kstar, "kappa_star_M1": kappa_q(rh, KAPPA_Q_PCT), "median_u_pct_M2": med_u,
              "kappa95_star_M2": kappa_q(r2, KAPPA_Q95_PCT), "kappa95_star_M1": kappa_q(rh, KAPPA_Q95_PCT),
              "n_pairs_available": len(pair_res), "n_pairs_dchi2_ge_min": n_ok, "pairs": pair_res,
              "pass": bool(med_u <= U_BAR_PCT and n_ok >= N_PAIRS_MIN)}
        out[P] = {"0a": a0, "0b": b0, "pass": bool(a0["pass"] and b0["pass"])}
    res["controls"]["C5_covariance_positive_definite"] = {"pass": True}
    res["results"] = out
    rd = "RD1" if out["J"]["pass"] else ("RD2" if out["H2"]["pass"] else None)
    v = f"PASS ({rd})" if rd else "STOP"
    res["verdict"] = v if a.mode == "binding" else f"PROVISIONAL, decides nothing: {v}"
    a.out.write_text(json.dumps(res, indent=1, default=float) + "\n")
    for P in REPORT_SETS:
        print(P, "0a", {F: (round(x["kappa_M2"], 3), round(x["c_M2"], 3)) for F, x in out[P]["0a"]["families"].items()},
              "pooled", round(out[P]["0a"]["pooled_M2"], 3), "| 0b kappa*", round(out[P]["0b"]["kappa_star_M2"], 3),
              "median u %", round(out[P]["0b"]["median_u_pct_M2"], 2), "pairs >= 9:", out[P]["0b"]["n_pairs_dchi2_ge_min"],
              flush=True)
    print("VERDICT", res["verdict"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
