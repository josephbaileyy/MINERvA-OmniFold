#!/usr/bin/env python3
"""FD-PRR reader: completeness, the controls, the quantities of §4 and the readings of §5, fixed before any number.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-DECLARATION.md (rev 2).

    prr_read.py --run OUT --repo R --out DIR

OUT is the study's cluster directory, copied whole: runs/, queues/, stage.json, route2/ and log-{dry,iter,cap,misc,ibu}/.

COMPLETE RUNS ONLY (§10.3). Nothing is read unless every job's DONE receipt says each of its queued tasks ended with
rc 0, with no STOP or FAILED beside it. Otherwise the readout is INCOMPLETE: no product is opened.

CONTROLS (§7), each a STOP (exit 1, no reading written) on failure: C-PINS (each product's runner digest, and every
committed input's), C-PAIR (the dry run's record), C-MASK (recomputed on the products), C-COLS, C-SPLIT, C-CAP, C-FIN,
C-IBU (route 2's record, and its truths against (e)'s at every experiment), and C-CT: the grade matrices, rebuilt from
the committed data product, C_model,5D's S and the committed C_resp + C_PL5D block, reproduce F0b's committed relative
sigmas and its noise-free closure_nuwro grade.

QUANTITIES (§4), on R00-R15 by S1's integration rule: X_hat = U x, X = U x_true, P = the nominal truth's X at the same
split. d = (X - P)/P, b = (X_hat - X)/P, rho = -sum_S b d / sum_S d^2 over S = {|d| >= 0.01}, undefined if |S| < 2.
The Table II analogue grades r = X_hat/X - 1 against F0b's matrix for the truth (``fd_f0_regrade.grade``, the noise
term zero): flagged if p < 0.01 or some |z| > 2.

READINGS (§5): PR-1 (each factor's class at each flagged truth, bar max(0.05, T_Q s_F)), PR-2a and PR-2b (IBU against
(e), and IBU against K), PR-3 (does a level clear the flagged truths at these truths; descriptive) and the composite
labels of §5.4, each worded "consistent with". R-ID and R-SUP are printed beside them and enter none.

MEASURES: the declared readings on the study's products. CANNOT AUTHORIZE: an estimator change (no level is adopted,
whatever PR-3 shows: FD-STAB §6's rule, the director's ruling of 2026-11-08), a held-out claim, or any wording.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (HERE, ND):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import prr_probe as P  # noqa: E402

SCHEMA = "prr-readout/1"
D_MIN = 0.01  # |d_c| >= 0.01 enters rho
BAR_FLOOR = 0.05
T_Q = 9.02936702750999  # Student t, 4 dof, two-sided 0.01/12: t.ppf(1 - 0.01/24, 4); test_prr recomputes it
K_PRIMARY, K_LONG = 5, 200
INCOMPLETE_RC, STOP_RC = 3, 1
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
INPUT_PINS = {
    f"{FD}/with-cpl/block/cpl_block.npz": "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f",
    f"{FD}/with-cpl/data-product/fd_data_product_cpl.json": "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50",
    f"{FD}/with-cpl/readout/fd_f0b_readout.json": "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6",
    "nd-unfolding/pv-ladder/readouts/cmodel_5d.json": "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60",
    "nd-unfolding/pv-ladder/readouts/h2_definition.json": "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
    "nd-unfolding/fd_f0_regrade.py": "0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2",
    "nd-unfolding/s1_assemble.py": "b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7",
}
BLOCK_KEY = "C_resp_plus_C_PL5D"
CT_TOL = 1e-12
LABELS = {
    "what": "FD-PRR: the retained prior of configuration (e) on R00-R15 at F0b's 12 graded truths, one factor at a time, "
            "and binned IBU on the same pseudo-data; noise-free, one MC split, simulation only",
    "not": ["a cause: the labels say which factors move the retained prior over the tested levels, not why",
            "an estimator change: no level is adopted, whatever PR-3 shows (FD-STAB section 6's rule)",
            "a held-out claim, or that any level would pass: F0b's truths are the simulation's own",
            "Table II or its grades: these are noise-free closures at one MC split",
            "coverage, an interval, a measurement or any data quantity",
            "paper or note wording"],
    "pr3": "clears / does not clear at these truths, on the noise-free analogue only",
}


class Stop(SystemExit):
    def __init__(self, control: str, why: str):
        super().__init__(f"STOP {control}: {why}")
        self.control, self.why = control, why


# ------------------------------------------------------------------------------------------- completeness
def queue_count(run: Path, job: str) -> int:
    return sum(1 for l in (run / "queues" / f"{job}.tsv").read_text().splitlines() if l and not l.startswith("#"))


def incomplete(run: Path) -> str | None:
    for job in (*P.JOBS, "ibu"):
        log = run / f"log-{job}"
        for name in ("STOP", "FAILED"):
            if (log / name).exists():
                return f"log-{job} holds {name}"
        if not (log / "DONE").is_file():
            return f"log-{job} has no DONE receipt"
        d = json.loads((log / "DONE").read_text())
        if d.get("mode") != job or d.get("rc") != 0:
            return f"log-{job}/DONE is not a clean {job} run: {d}"
        if job != "ibu":
            n = queue_count(run, job)
            if d.get("tasks") != n or d.get("ended") != n:
                return f"log-{job}/DONE ended {d.get('ended')} of {d.get('tasks')} tasks, the queue holds {n}"
    return None


# ------------------------------------------------------------------------------------------- products and controls
def expected_truth(truth: str, repo: Path) -> dict:
    """The hypothesis and alternative a truth's product must carry, by FD-STAB's bound rule (``expected_pin``)."""
    import estimator_stability_analyze as an
    import estimator_stability_probe as esp
    name, hyp, alt, kind, amp = P.closure_spec(truth)
    want = {"hyp": an.expected_pin(hyp, repo), "alt": None}
    if alt is not None:
        want["alt"] = {"sha256": an.expected_pin(alt, repo), "amplitude": float(amp),
                       "truth": esp.PVL_TRUTH if kind == "SCHEMA" else kind}
    return want


def meta_problems(meta: dict, level: str, truth: str, seed: int, want: dict) -> list[str]:
    bad = []
    pr = meta.get("prior_retention") or {}
    L = P.LEVELS[level]
    declared = {"iters": L["iters"], "capacity": None if L["capacity"] is None else list(L["capacity"]),
                "mc_fraction": L["mc_fraction"], "mask": L["mask"]}
    if pr.get("schema") != P.SCHEMA or pr.get("level") != level or pr.get("truth") != truth:
        bad.append("not this task's FD-PRR product")
    if pr.get("declared") != declared:
        bad.append(f"C-CAP: declared {pr.get('declared')} is not level {level}'s")
    rec = {"iters": meta.get("iters"), "capacity": None if meta.get("capacity") is None else list(meta["capacity"]),
           "mc_fraction": (meta.get("development") or {}).get("mc_fraction")}
    if rec != {k: declared[k] for k in rec} or pr.get("recorded") != rec:
        bad.append(f"C-CAP: the runner recorded {rec}")
    m = pr.get("mask") or {}
    if L["mask"] is None:
        if m.get("calls") not in (0, None) or m.get("gen_columns") is not None:
            bad.append("an unmasked level went through a mask")
    else:
        g, r = P.MASKS[L["mask"]]
        if m.get("calls") != 1 or m.get("gen_columns") != list(g) or m.get("reco_columns") != list(r):
            bad.append(f"the mask record {m} is not mask {L['mask']}'s, applied once")
    if pr.get("input_columns") != list(P.AXES):
        bad.append(f"C-COLS: input columns {pr.get('input_columns')}")
    if not (meta.get("development") or {}).get("expectation") or (meta.get("nuisance_draw") is not None):
        bad.append("not a noise-free expectation closure")
    if meta.get("pseudo_seed") != seed or meta.get("split_key") is None:
        bad.append(f"seed {meta.get('pseudo_seed')} / split {meta.get('split_key')} is not seed {seed}'s")
    if (meta.get("hypothesis") or {}).get("sha256") != want["hyp"]:
        bad.append("C-PINS: the hypothesis is not the truth's file")
    alt = meta.get("alternative")
    if want["alt"] is None:
        if alt is not None:
            bad.append("an alternative the truth does not name")
    elif alt is None or alt.get("sha256") != want["alt"]["sha256"] or float(alt.get("amplitude")) != \
            want["alt"]["amplitude"] or alt.get("truth") != want["alt"]["truth"]:
        bad.append("C-PINS: the alternative is not the truth's")
    code = meta.get("code_sha256") or {}
    pins = {Path(rel).name: d for rel, d in P.CODE_PINS.items()}
    if code.get("s5p_nullexp.py") != pins["s5p_nullexp.py"] or \
            code.get("unfold_2d_omnifold_unbinned.py") != pins["unfold_2d_omnifold_unbinned.py"]:
        bad.append("C-PINS: the runner or the refinement is not the bound file")
    moved = sorted(n for n, d in code.items() if n in pins and d != pins[n])
    if moved:
        bad.append(f"C-PINS: the product's code digests {moved} are not the bound files'")
    if pr.get("code_sha256") is None:
        bad.append("no probe digest")
    return bad


def load_product(path: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    with np.load(path, allow_pickle=False) as z:
        return np.asarray(z["xsec_flat"]), np.asarray(z["xtrue_flat"]), json.loads(str(z["meta"]))


def products(run: Path, repo: Path) -> dict:
    """Every declared product, checked; {(level, truth, seed): (xsec, xtrue, meta)}."""
    import s5c_pseudo
    out, want = {}, {t: expected_truth(t, repo) for t in P.TRUTHS}
    for lv, t, s in P.all_tasks():
        p = P.product_path(run / "runs", lv, t, s)
        files = sorted(p.parent.glob(f"prr_{lv}_{t}_s{s}*.npz"))
        if files != [p]:
            raise Stop("completeness", f"{p.parent}: expected exactly {p.name}, found {[f.name for f in files]}")
        x, xt, m = load_product(p)
        bad = meta_problems(m, lv, t, s, want[t])
        if bad:
            raise Stop("product", f"{p.name}: {'; '.join(bad)}")
        if not (np.all(np.isfinite(x)) and np.all(np.isfinite(xt))):
            raise Stop("C-FIN", f"{p.name}: a non-finite cell")
        out[(lv, t, s)] = (x, xt, m)
    for s in (P.PRIMARY_SEED, *P.FLOOR_SEEDS):
        keys = {m["split_key"] for (lv, t, ss), (_, _, m) in out.items() if ss == s}
        if keys != {s5c_pseudo.split_key_for(s)}:
            raise Stop("C-SPLIT", f"seed {s}: split keys {keys}")
    return out


def c_mask(prods: dict) -> dict:
    a = prods[("B0", "nominal", P.PRIMARY_SEED)][0]
    b = prods[("O5", "nominal", P.PRIMARY_SEED)][0]
    return {"pass": bool(a.dtype == b.dtype and np.array_equal(a, b))}


def c_pair(run: Path) -> dict:
    p = run / "log-dry" / "pair.json"
    if not p.is_file():
        raise Stop("C-PAIR", "the dry run left no pair record")
    rec = json.loads(p.read_text())
    if not (rec.get("pass") and set(rec.get("C-PAIR", {})) == set(P.FD_STAB_CONTROL)):
        raise Stop("C-PAIR", f"the dry run's pair record does not pass: {rec}")
    return rec


# ------------------------------------------------------------------------------------------- C-CT
def check_inputs(repo: Path, pins: dict = INPUT_PINS) -> None:
    for rel, want in pins.items():
        if P.sha256_path(repo / rel) != want:
            raise Stop("C-PINS", f"{rel} is not its pin")


def grade_matrices(repo: Path) -> tuple[dict, np.ndarray, dict]:
    """F0b's grade matrix for each graded truth, C_e/ff + sum_{j != own} s_j s_j^T + (C_resp + C_PL5D)/ff, by
    ``fd_f0_regrade.leave_out`` on committed inputs; f enters only as the divisor. Returns (matrices, f, C-CT)."""
    import fd_f0_regrade as F
    dp = json.loads((repo / f"{FD}/with-cpl/data-product/fd_data_product_cpl.json").read_text())
    f = np.asarray(dp["f"], float)
    Ce = np.asarray(dp["matrices"]["C_e"], float)
    with np.load(repo / f"{FD}/with-cpl/block/cpl_block.npz", allow_pickle=False) as z:
        Cx, fb = np.asarray(z[BLOCK_KEY], float), np.asarray(z["f"], float)
    S = np.asarray(json.loads((repo / "nd-unfolding/pv-ladder/readouts/cmodel_5d.json").read_text())["S"], float)
    ro = json.loads((repo / f"{FD}/with-cpl/readout/fd_f0b_readout.json").read_text())
    ff = np.outer(f, f)
    Cer, Cxr = Ce / ff, Cx / ff
    mats = {"C_total": F.leave_out(Cer, S, None), **{f"minus_{v}": F.leave_out(Cer, S, v) for v in F.VERTICES}}
    want = ro[f"relative_sigma_plus_{ro['extra_block']['name']}"]
    ct = {"f_same_in_block": bool(np.array_equal(f, fb))}
    for k, M in mats.items():
        ct[f"sigma_{k}"] = float(np.max(np.abs(np.sqrt(np.diag(M + Cxr)) / np.asarray(want[k], float) - 1)))
    own = {t["name"]: t["own"] for t in F.TRUTHS}
    out = {}
    for t in P.TRUTHS:
        out[t] = (mats["C_total"] if own[t] is None else mats[f"minus_{own[t]}"]) + Cxr
        if np.linalg.eigvalsh(out[t]).min() <= 0:
            raise Stop("C-FIN", f"{t}'s grade matrix is not positive definite")
    ref = next(x for x in ro["truths"] if x["name"] == "closure_nuwro")
    g = F.grade(np.asarray(ref["bias"], float), np.zeros((P.N_CELLS, P.N_CELLS)), out["closure_nuwro"])
    ct["closure_nuwro_chi2_rel"] = abs(g["chi2"] / ref["grade"]["chi2"] - 1)
    ct["closure_nuwro_z_abs"] = float(np.max(np.abs(np.asarray(g["z"]) - np.asarray(ref["grade"]["z"]))))
    ct["pass"] = bool(ct["f_same_in_block"] and all(ct[f"sigma_{k}"] <= CT_TOL for k in mats)
                      and ct["closure_nuwro_chi2_rel"] <= 1e-10 and ct["closure_nuwro_z_abs"] <= 1e-10)
    ct["table_ii_flags"] = {x["name"]: {"p": x["grade"]["p"], "cells_abs_z_gt_2": x["grade"]["cells_abs_z_gt_2"]}
                            for x in ro["truths"] if x["name"] in P.TRUTHS}
    if not ct["pass"]:
        raise Stop("C-CT", f"the rebuilt grade matrices do not reproduce F0b's: {ct}")
    return out, f, ct


# ------------------------------------------------------------------------------------------- quantities (§4)
def rho(xhat: np.ndarray, x: np.ndarray, p: np.ndarray) -> tuple[float | None, int]:
    d, b = (x - p) / p, (xhat - x) / p
    S = np.abs(d) >= D_MIN
    if int(S.sum()) < 2:
        return None, int(S.sum())
    return float(-np.sum(b[S] * d[S]) / np.sum(d[S] ** 2)), int(S.sum())


def table_ii(r: np.ndarray, C: np.ndarray) -> dict:
    import fd_f0_regrade as F
    g = F.grade(np.asarray(r, float), np.zeros((P.N_CELLS, P.N_CELLS)), C)
    return {"chi2": g["chi2"], "p": g["p"], "p_below_floor": g["p_below_floor"], "max_abs_z": float(np.max(np.abs(g["z"]))),
            "cells_abs_z_gt_2": g["cells_abs_z_gt_2"], "flagged": bool(g["p_lt_0.01"] or g["cells_abs_z_gt_2"])}


def quantities(X: dict, mats: dict) -> dict:
    """X: {(level, truth, seed): (X_hat, X)} on R00-R15, with B0's nominal at every seed."""
    out = {}
    for (lv, t, s), (xh, x) in X.items():
        p = X[("B0", P.PRIOR, s)][1]
        r_, n_s = rho(xh, x, p)
        b = (xh - x) / p
        out[(lv, t, s)] = {"rho": r_, "n_S": n_s, "b": b.tolist(), "rms_b": float(np.sqrt(np.mean(b ** 2))),
                           "r": (xh / x - 1).tolist(), "grade": table_ii(xh / x - 1, mats[t])}
    return out


# ------------------------------------------------------------------------------------------- readings (§5)
def floor_sd(deltas: list[float]) -> float:
    if len(deltas) != 1 + len(P.FLOOR_SEEDS) or any(v is None for v in deltas):
        raise Stop("floor", f"the floor needs {1 + len(P.FLOOR_SEEDS)} defined differences, got {deltas}")
    return float(np.std(np.asarray(deltas, float), ddof=1))


def bar(s: float) -> float:
    return max(BAR_FLOOR, T_Q * s)


def factor_class(rho0: float | None, rhos: list[float | None], delta: float) -> str:
    if rho0 is None or any(v is None for v in rhos):
        return "undefined"
    lo = any(v <= rho0 - delta for v in rhos)
    hi = any(v >= rho0 + delta for v in rhos)
    return "both" if lo and hi else "reduces" if lo else "increases" if hi else "no effect"


def ibu_class(d: float | None, delta: float) -> str:
    if d is None:
        return "undefined"
    return "IBU retains less" if d <= -delta else "IBU retains more" if d >= delta else "same"


def ibu_k_class(r5: float | None, r200: float | None) -> str:
    if r5 is None or r200 is None:
        return "undefined"
    return "falls" if r200 <= r5 - BAR_FLOOR else "rises" if r200 >= r5 + BAR_FLOOR else "flat"


def labels_for(pr1: dict, pr2a: str, pr2b: str) -> list[str]:
    out = []
    if pr1["F1"] == "reduces" and pr2b == "falls":
        out.append("consistent with finite-iteration regularization")
    if pr1["F1"] in ("no effect", "increases") and pr1["F2"] in ("no effect", "increases") and pr2b in ("flat", "rises"):
        out.append("consistent with an information limit at these settings")
    if pr2a == "IBU retains less" or pr1["F2"] == "reduces":
        out.append("consistent with an implementation-specific share")
    if pr1["F4"] in ("reduces", "increases", "both"):
        out.append("sensitive to the observable set")
    if pr1["F3"] in ("reduces", "increases", "both"):
        out.append("sensitive to training statistics")
    return out or ["unattributed"]


def clears(flags: dict, b0_flags: dict) -> dict:
    """PR-3 at one level: flags {truth: flagged} at the level, b0_flags at B0."""
    c = not any(flags[t] for t in P.FLAGGED)
    new = sorted(t for t in P.TRUTHS if flags[t] and not b0_flags[t])
    return {"reading": "clears at these truths" if c else "does not clear at these truths",
            "without_new_flags": bool(c and not new), "new_flags": new}


def spearman(a, b) -> float | None:
    a, b = np.asarray(a, float), np.asarray(b, float)

    def ranks(v):
        order = np.argsort(v, kind="stable")
        r = np.empty(v.size)
        r[order] = np.arange(v.size, dtype=float)
        for val in np.unique(v):  # average ties
            m = v == val
            r[m] = r[m].mean()
        return r
    ra, rb = ranks(a), ranks(b)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def readings(q: dict, qi: dict) -> dict:
    """q: (e)'s quantities by (level, truth, seed); qi: IBU's by (K, truth, seed)."""
    S0 = P.PRIMARY_SEED
    seeds = (S0, *P.FLOOR_SEEDS)
    rho_ = lambda lv, t, s=S0: q[(lv, t, s)]["rho"]  # noqa: E731
    s_F = {F: floor_sd([None if rho_(P.FLOOR_LEVEL[F], P.FLOOR_TRUTH, s) is None or rho_("B0", P.FLOOR_TRUTH, s) is None
                        else rho_(P.FLOOR_LEVEL[F], P.FLOOR_TRUTH, s) - rho_("B0", P.FLOOR_TRUTH, s) for s in seeds])
           for F in P.FACTORS}
    di = [None if qi[(K_PRIMARY, P.FLOOR_TRUTH, s)]["rho"] is None or rho_("B0", P.FLOOR_TRUTH, s) is None
          else qi[(K_PRIMARY, P.FLOOR_TRUTH, s)]["rho"] - rho_("B0", P.FLOOR_TRUTH, s) for s in seeds]
    s_ibu = floor_sd(di)
    out = {"floor": {"s_F": s_F, "s_IBU": s_ibu, "dof": len(seeds) - 1, "T_Q": T_Q, "bar_floor": BAR_FLOOR,
                     "bars": {**{F: bar(v) for F, v in s_F.items()}, "IBU": bar(s_ibu)},
                     "transfer": f"s is measured at {P.FLOOR_TRUTH} and applied at {[t for t in P.FLAGGED if t != P.FLOOR_TRUTH]}"
                                 " (a transfer), and each factor's measured level's s is applied to all its levels"},
           "PR-1": {}, "PR-2a": {}, "PR-2b": {}, "labels": {}}
    for T in P.FLAGGED:
        pr1 = {F: factor_class(rho_("B0", T), [rho_(lv, T) for lv in lvs], bar(s_F[F])) for F, lvs in P.FACTORS.items()}
        r5, r200 = qi[(K_PRIMARY, T, S0)]["rho"], qi[(K_LONG, T, S0)]["rho"]
        pr2a = ibu_class(None if r5 is None or rho_("B0", T) is None else r5 - rho_("B0", T), bar(s_ibu))
        pr2b = ibu_k_class(r5, r200)
        out["PR-1"][T], out["PR-2a"][T], out["PR-2b"][T] = pr1, pr2a, pr2b
        out["labels"][T] = labels_for(pr1, pr2a, pr2b)
    b0 = {t: q[("B0", t, S0)]["grade"]["flagged"] for t in P.TRUTHS}
    levels = [lv for lv in P.LEVELS if lv not in ("B0", "O5")]
    out["PR-3"] = {lv: clears({t: q[(lv, t, S0)]["grade"]["flagged"] for t in P.TRUTHS}, b0) for lv in ["B0", *levels]}
    out["PR-3"]["IBU_K5"] = clears({t: qi[(K_PRIMARY, t, S0)]["grade"]["flagged"] for t in P.TRUTHS}, b0)
    out["PR-3_label"] = LABELS["pr3"]
    return out


# ------------------------------------------------------------------------------------------- route 2
def route2(run: Path, X: dict, mats: dict) -> tuple[dict, dict]:
    """IBU's quantities by (K, truth, seed), and C-IBU: route 2's committed-value check passed, and its truths on
    R00-R15 equal (e)'s B0 truths at every experiment to 1e-12 relative."""
    import prr_ibu as R
    rec = json.loads((run / "route2" / "route2.json").read_text())
    if not rec.get("C-IBU", {}).get("pass"):
        raise Stop("C-IBU", f"route 2's adapter did not reproduce REF-G1: {rec.get('C-IBU')}")
    with np.load(run / "route2" / "route2.npz", allow_pickle=False) as z:
        arr = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
    ks = [int(k) for k in rec["ks"]]
    q, worst = {}, 0.0
    for t, s in R.experiments():
        key = f"{t}_s{s}"
        F, xt = arr[f"{key}__F_{R.VARIANT}"], arr[f"{key}__X_true"]
        xe = X[("B0", t, s)][1]
        worst = max(worst, float(np.max(np.abs(xt / xe - 1))))
        p = X[("B0", P.PRIOR, s)][1]
        for i, k in enumerate(ks):
            xh = np.asarray(F[i], float)
            if not np.all(np.isfinite(xh)):
                raise Stop("C-FIN", f"IBU {key} K={k}: a non-finite cell")
            r_, n_s = rho(xh, xe, p)
            q[(k, t, s)] = {"rho": r_, "n_S": n_s, "rms_b": float(np.sqrt(np.mean(((xh - xe) / p) ** 2))),
                            "grade": table_ii(xh / xe - 1, mats[t])}
    if worst > 1e-12:
        raise Stop("C-IBU", f"route 2's truths differ from (e)'s by {worst:.3g} relative")
    return q, {"C-IBU": rec["C-IBU"], "truths_max_rel": worst, "R-ID": rec.get("R-ID"), "R-SUP": rec.get("R-SUP"),
               "ks": ks}


# ------------------------------------------------------------------------------------------- the run
def read(run: Path, repo: Path) -> tuple[dict, int]:
    why = incomplete(run)
    if why:
        return {"schema": SCHEMA, "labels": LABELS, "verdict": "INCOMPLETE", "why": why}, INCOMPLETE_RC
    import estimator_stability_analyze as an
    check_inputs(repo)
    controls = {"C-PAIR": c_pair(run)}
    prods = products(run, repo)
    controls["C-MASK"] = c_mask(prods)
    if not controls["C-MASK"]["pass"]:
        raise Stop("C-MASK", "the five-column mask is not B0 bitwise")
    mats, f, ct = grade_matrices(repo)
    controls["C-CT"] = {k: v for k, v in ct.items() if k != "table_ii_flags"}
    M16 = an.cell_matrix(str(repo / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
    X = {k: (M16 @ np.asarray(x, float), M16 @ np.asarray(xt, float)) for k, (x, xt, _) in prods.items()}
    for k, (xh, x) in X.items():
        if not (np.all(np.isfinite(xh)) and np.all(x > 0)):
            raise Stop("C-FIN", f"{k}: a non-finite estimate or a non-positive truth on R00-R15")
    q = quantities(X, mats)
    qi, r2 = route2(run, X, mats)
    controls["C-IBU"] = {"adapter": r2["C-IBU"], "truths_max_rel": r2["truths_max_rel"]}
    rd = readings(q, qi)
    S0 = P.PRIMARY_SEED
    sup = {}
    for t, v in (r2["R-SUP"] or {}).items():
        sup[t] = {**v, "spearman_abs_b_vs_kish": spearman(np.abs(q[("B0", t, S0)]["b"]), v["kish"])}
    out = {"schema": SCHEMA, "labels": LABELS, "verdict": "COMPLETE", "controls": controls, "readings": rd,
           "table": {f"{lv}/{t}/s{s}": {k: v for k, v in rec.items()} for (lv, t, s), rec in q.items()},
           "ibu": {f"K{k}/{t}/s{s}": rec for (k, t, s), rec in qi.items()},
           "table_ii_committed_beside_B0": {"note": "read by nothing (§4.2)", "committed": ct["table_ii_flags"],
                                             "B0": {t: q[("B0", t, S0)]["grade"] for t in P.TRUTHS}},
           "R-ID": r2["R-ID"], "R-SUP": sup,
           "R-ID_R-SUP_label": "descriptive, read by nothing: no label or class uses them"}
    import fd_f0_regrade as F
    integrals = [v for pair in X.values() for v in pair]
    guard = F.LeakGuard(f, integrals)
    guard.check("readout", out)
    return out, 0


def text(out: dict) -> str:
    lines = [f"FD-PRR readout: {out['verdict']}"]
    if out["verdict"] != "COMPLETE":
        return "\n".join(lines + [out.get("why", "")]) + "\n"
    rd = out["readings"]
    lines.append(f"floor: s_F {rd['floor']['s_F']}, s_IBU {rd['floor']['s_IBU']:.4g}, bars {rd['floor']['bars']}")
    for T in P.FLAGGED:
        lines.append(f"{T}: PR-1 {rd['PR-1'][T]}; PR-2a {rd['PR-2a'][T]}; PR-2b {rd['PR-2b'][T]}; labels {rd['labels'][T]}")
    for lv, v in rd["PR-3"].items():
        lines.append(f"PR-3 {lv}: {v['reading']}; without new flags {v['without_new_flags']} {v['new_flags']}")
    for k, v in out["table"].items():
        g = v["grade"]
        lines.append(f"{k}: rho {v['rho']} (|S| {v['n_S']}), rms b {v['rms_b']:.4g}, chi2 {g['chi2']:.4g}, p {g['p']:.3g}, "
                     f"max|z| {g['max_abs_z']:.3g}, flagged {g['flagged']}")
    for k, v in out["ibu"].items():
        lines.append(f"IBU {k}: rho {v['rho']}, chi2 {v['grade']['chi2']:.4g}, p {v['grade']['p']:.3g}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0], allow_abbrev=False)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=REPO)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        a.out.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    try:
        out, rc = read(a.run, a.repo)
    except Stop as e:
        print(f"STOP {e.control}: {e.why}", file=sys.stderr)
        (a.out / "STOP").write_text(json.dumps({"control": e.control, "why": e.why}) + "\n")
        return STOP_RC
    (a.out / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    (a.out / "readout.txt").write_text(text(out))
    print(json.dumps({"verdict": out["verdict"]}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
