#!/usr/bin/env python3
"""Estimator-stability probe (STAB): evaluate the declared criteria on the candidates' products.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/FD-STAB-DECLARATION.md (§§4-6).

    estimator_stability_analyze.py --runs <OUT>/runs --s5c-contract J --sigma-receipt J --h2-definition J --out J
        [--repo R] [--receipt <OUT>/log-full/DONE]

COMPLETE RUNS ONLY (§6, §7). The receipt is derived from --runs (<OUT>/runs -> <OUT>/log-full/DONE), so a receipt
from another run cannot stand in; an explicit --receipt naming another file is refused. Nothing is graded unless
that DONE receipt says every queued task ended with
rc 0, and no STOP or FAILED lies beside it. Otherwise the outcome is INCOMPLETE: no product is read, no criterion
is evaluated, and no estimator is adopted. A run stopped for a reprice resumes only under an addendum the director
binds.

STABILITY (§4). Per candidate, one GiBUU-like pseudo-experiment unfolded unjittered (the base) and under 51 edge-safe
float32-ulp jitters. On s5e's 153 reported functionals, r_j = F_j / F_base - 1. s5e's statistic (amendment 3, A3) is,
per functional, the larger |r| of its TWO jitters over sigma, then the median and the maximum over functionals. A
maximum grows with the number of jitters, so the 51 are not pooled into one maximum: jitters (1,2), (3,4), ... (49,50)
give 25 disjoint pairs, s5e's statistic is computed on each, and the criterion reads its MEAN over the pairs:
mean median <= 0.3 and mean maximum <= 1.0 (s5e's bounds). sigma is the committed pseudo-data bootstrap sigma of
configuration (e) (s5e assess receipt ``sigma_rel_pct``: 100 refit-per-replica replicas of nominal experiment 700000),
as a relative sigma, so nothing here reads the data or an absolute central value.

G0 (§4.3): the probe is informative only if the CONTROL fails that bound on this input. If it passes, no candidate
can be shown to improve on it, and the verdict is UNINFORMATIVE.

BIAS (§5). Per candidate and F0b truth T, the noise-free closure's relative residual b = X / Xtrue - 1 on the 16
reporting cells (S1's integration rule, s1_assemble.functional_matrix over the pinned H2 definition). Two metrics,
RMS_T and MAX_T = max |b|. A candidate is NO WORSE at T if RMS_T(c) - RMS_T(control) <= Delta and MAX_T(c) -
MAX_T(control) <= Delta, each Delta = 3 x 1.20 x sqrt(s_c^2 + s_control^2), where s is the metric's rounding-noise SD
propagated from that candidate's own per-cell SD (``cell_sd``: the base and the 51 jitters mapped to the 16 cells, the
SD around their mean with ddof = 1; the base is one rounding realization like each jitter) and 1.20 is the 95% upper
factor of an SD estimated with about 50 degrees of freedom. The seed floor is zero (the estimator is seed-invariant).
A Delta of exactly zero means the floor model failed, not that a candidate is worse: that truth is INVALID, and so is
the verdict if a candidate that meets the stability bound has one. The closures ``nominal`` and ``A7_mnvtune`` are the
same closure (one hypothesis, no alternative, one split): each candidate's two products must be bitwise equal, a
determinism control, so 17 distinct truths are judged. Every closure carries the declared MC split (pseudo seed
991000, ``--mc-fraction half``), the same for each candidate as for the control.

VERDICT (§6). A candidate PASSES if it meets the stability bound and is no worse at all 17 distinct truths. Among passers the
lowest mean maximum ranks first; every passer within one combined standard error of it is a co-winner. Nothing here
reads the GiBUU-truth biases except to print them as a descriptive readout (§5.3).

MEASURES: the declared criteria on the products. CANNOT AUTHORIZE: the adoption of any estimator (Joseph's decision).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import estimator_stability_probe as probe  # noqa: E402

BOUND_MEDIAN, BOUND_MAX = 0.3, 1.0
N_PAIRS = 25
N_FUNCTIONALS = 153  # s5e's reported functionals; every candidate must use all of them
DETERMINISM_PAIR = ("nominal", "A7_mnvtune")
FLOOR_K, SD_UPPER = 3.0, 1.20
SIGMA_RECEIPT_SHA256 = "84266e309d1aae0d2db1db315750b8164413a7d0125fcaa4a6c9b25834261a2c"  # state/s5e/cand/assess_receipt.json, as committed
GIBUU_READOUT = ("A7_gibuu", "stage0c_gibuu")
INCOMPLETE_RC = 3


# --------------------------------------------------------------------------------------------- pure criteria
def stability_stats(rel: np.ndarray, sigma: np.ndarray) -> dict:
    """rel: (51, F) relative deviations of the jittered functionals from the base; sigma: (F,) relative sigma."""
    rel = np.asarray(rel, float)
    sigma = np.asarray(sigma, float)
    if rel.shape[0] < 2 * N_PAIRS:
        raise ValueError(f"need {2 * N_PAIRS} jitters, got {rel.shape[0]}")
    z = np.abs(rel) / sigma
    meds, maxs = [], []
    for p in range(N_PAIRS):
        m = np.maximum(z[2 * p], z[2 * p + 1])
        meds.append(float(np.median(m)))
        maxs.append(float(np.max(m)))
    meds, maxs = np.array(meds), np.array(maxs)
    sd = np.std(np.vstack([np.zeros(rel.shape[1]), rel]), axis=0, ddof=1) / sigma  # descriptive; base included
    return {"mean_median": float(meds.mean()), "mean_max": float(maxs.mean()),
            "se_median": float(meds.std(ddof=1) / math.sqrt(N_PAIRS)), "se_max": float(maxs.std(ddof=1) / math.sqrt(N_PAIRS)),
            "worst_pair_max": float(maxs.max()), "sd51_median": float(np.median(sd)), "sd51_max": float(np.max(sd)),
            "passes": bool(meds.mean() <= BOUND_MEDIAN and maxs.mean() <= BOUND_MAX)}


def cell_sd(base_cells: np.ndarray, jitter_cells) -> np.ndarray:
    """Per-cell rounding SD, relative: the base and every jitter as X / X_base, SD around their mean, ddof = 1."""
    base_cells = np.asarray(base_cells, float)
    rel = np.vstack([np.ones_like(base_cells)] + [np.asarray(x, float) / base_cells for x in jitter_cells])
    return np.std(rel, axis=0, ddof=1)


def g0_informative(control: dict) -> bool:
    """The control must FAIL the stability bound on the probe's input, or the probe cannot discriminate."""
    return not control["passes"]


def bias_metrics(b: np.ndarray) -> tuple[float, float, int]:
    b = np.asarray(b, float)
    return float(np.sqrt(np.mean(b ** 2))), float(np.max(np.abs(b))), int(np.argmax(np.abs(b)))


def metric_noise(b: np.ndarray, s: np.ndarray) -> tuple[float, float]:
    """Rounding-noise SD of (RMS, MAX), first order, from per-cell SDs s."""
    b, s = np.asarray(b, float), np.asarray(s, float)
    rms, _, kmax = bias_metrics(b)
    s_rms = float(np.sqrt(np.sum((b * s) ** 2)) / (b.size * rms)) if rms > 0 else float(np.sqrt(np.mean(s ** 2)))
    return s_rms, float(s[kmax])


def no_worse(b_c, s_c, b_ctrl, s_ctrl) -> dict:
    rc, mc, _ = bias_metrics(b_c)
    r0, m0, _ = bias_metrics(b_ctrl)
    nrc, nmc = metric_noise(b_c, s_c)
    nr0, nm0 = metric_noise(b_ctrl, s_ctrl)
    d_rms = FLOOR_K * SD_UPPER * math.hypot(nrc, nr0)
    d_max = FLOOR_K * SD_UPPER * math.hypot(nmc, nm0)
    out = {"rms": rc, "rms_control": r0, "delta_rms": d_rms, "max": mc, "max_control": m0, "delta_max": d_max}
    if not (d_rms > 0 and d_max > 0):
        return {**out, "valid": False, "no_worse": None}
    return {**out, "valid": True, "no_worse": bool(rc - r0 <= d_rms and mc - m0 <= d_max)}


def bias_status(per_truth: list) -> bool | None:
    """A candidate's bias status over the judged truths: None (INVALID) if ANY truth's floor is zero, else whether it
    is no worse at all of them."""
    return None if any(v is None for v in per_truth) else all(per_truth)


def verdict(stab: dict, bias_ok: dict) -> dict:
    """stab: candidate -> stability_stats; bias_ok: candidate -> True / False (no worse at all 17 distinct truths) or
    None (a zero floor at some truth). Control excluded from winners."""
    if not g0_informative(stab["control"]):
        return {"verdict": "UNINFORMATIVE", "winners": [], "passers": []}
    invalid = sorted(c for c in stab if c != "control" and stab[c]["passes"] and bias_ok.get(c, False) is None)
    if invalid:
        return {"verdict": "INVALID", "winners": [], "passers": [], "invalid_floor": invalid}
    passers = [c for c in stab if c != "control" and stab[c]["passes"] and bias_ok.get(c, False) is True]
    if not passers:
        return {"verdict": "NONE_PASS", "winners": [], "passers": []}
    best = min(passers, key=lambda c: stab[c]["mean_max"])
    winners = sorted(c for c in passers
                     if stab[c]["mean_max"] - stab[best]["mean_max"] <= math.hypot(stab[c]["se_max"], stab[best]["se_max"]))
    return {"verdict": "WINNER" if len(winners) == 1 else "CO_WINNERS", "winners": winners, "passers": sorted(passers),
            "ranked_by": "mean_max (lowest first); co-winners within one combined standard error"}


# --------------------------------------------------------------------------------------------- products
def load(path: Path) -> tuple[np.ndarray, np.ndarray | None, dict]:
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    xt = np.asarray(z["xtrue_flat"], float) if "xtrue_flat" in z.files else None
    return np.asarray(z["xsec_flat"], float), xt, meta


def check_probe_meta(meta: dict, candidate: str, path: Path) -> None:
    sp = meta.get("stability_probe") or {}
    if sp.get("schema") != probe.SCHEMA or sp.get("candidate") != candidate or sp.get("override") != probe.CANDIDATES[candidate]:
        raise SystemExit(f"{path.name}: not a {candidate} product of this probe")


def stability_products(d: Path, candidate: str) -> tuple[np.ndarray, list[np.ndarray]]:
    base, jit = None, {}
    for p in sorted(d.glob("*.npz")):
        x, _, m = load(p)
        check_probe_meta(m, candidate, p)
        if (m.get("construction"), m.get("truth"), m.get("eavail_ratio_sha256"), m.get("pseudo_seed")) != (
                "pseudo", probe.STABILITY_TRUTH["truth"], probe.STABILITY_TRUTH["ratio_sha256"], probe.STABILITY_PSEUDO_SEED):
            raise SystemExit(f"{p.name}: not the declared stability input")
        if m.get("bootstrap_seed") is not None:
            raise SystemExit(f"{p.name}: a bootstrap replica is not part of the probe")
        if m.get("jitter_seed") is None:
            base = x
        else:
            jit[int(m["jitter_seed"])] = x
    if base is None or sorted(jit) != list(probe.JITTER_SEEDS):
        raise SystemExit(f"{candidate}: stability set incomplete (base {base is not None}, jitters {sorted(jit)})")
    return base, [jit[j] for j in probe.JITTER_SEEDS]


def expected_pin(path: str, repo: Path) -> str:
    """The sha256 a closure's hypothesis or alternative must carry: the committed file's, or for the cluster-held
    pv-ladder closure ratio the digest fd_f0_regrade pins (F0's own identity check)."""
    if path.startswith("CLUSTER:"):
        import fd_f0_regrade
        return fd_f0_regrade.RATIO["closure_nuwro"]
    return probe.sha256_path(repo / path)


def closure_products(d: Path, candidate: str, repo: Path) -> dict[str, tuple[np.ndarray, np.ndarray, int]]:
    out = {}
    for name, hyp, alt, kind, amp in probe.CLOSURES:
        files = sorted((d / name).glob("*.npz"))
        if len(files) != 1:
            raise SystemExit(f"{candidate}/{name}: expected one closure product, found {len(files)}")
        x, xt, m = load(files[0])
        check_probe_meta(m, candidate, files[0])
        if not (m.get("development") or {}).get("expectation"):
            raise SystemExit(f"{files[0].name}: not a noise-free (expectation) closure")
        if (m.get("hypothesis") or {}).get("sha256") != expected_pin(hyp, repo):
            raise SystemExit(f"{files[0].name}: hypothesis is not the declared file")
        got_alt = m.get("alternative")
        if alt is None:
            if got_alt is not None:
                raise SystemExit(f"{files[0].name}: an alternative the declaration does not name")
        elif got_alt is None or got_alt.get("sha256") != expected_pin(alt, repo) or float(got_alt.get("amplitude")) != amp \
                or (kind != "SCHEMA" and got_alt.get("truth") != kind):
            raise SystemExit(f"{files[0].name}: alternative is not the declared truth")
        if m.get("pseudo_seed") != probe.CLOSURE_SEED or (m.get("development") or {}).get("mc_fraction") != \
                probe.CLOSURE_MC_FRACTION or m.get("split_key") is None:
            raise SystemExit(f"{files[0].name}: not the declared MC split (pseudo seed {probe.CLOSURE_SEED}, "
                             f"mc_fraction {probe.CLOSURE_MC_FRACTION})")
        if xt is None:
            raise SystemExit(f"{files[0].name}: no truth array")
        out[name] = (x, xt, m["split_key"])
    return out


def functionals(contract: dict):
    """s5e's 153 reported functionals (s5c_coverage.reported_functionals): rows over the fine grid, and names."""
    import s5c_coverage
    return s5c_coverage.reported_functionals(contract)


def cell_matrix(h2_definition: str) -> np.ndarray:
    """The 16 reporting cells over the fine grid by S1's integration rule, from the pinned H2 definition."""
    import s1_assemble
    return s1_assemble.functional_matrix(s1_assemble.fine_map(Path(h2_definition)))


def n_tasks() -> int:
    """The full queue's task count, from the probe's own task list."""
    import types
    a = types.SimpleNamespace(npz="n", bkg="b", bank="k", detector_dir="d", expect_npz_sha256="-", expect_bkg_sha256="-",
                              closure_ratio_dir="r", runs="o")
    return sum(len(probe.candidate_tasks(a, c)) for c in probe.CANDIDATES)


def incomplete(receipt: Path) -> str | None:
    """Why the run is not complete, or None: the full run's DONE receipt must exist, say every task ended with rc 0,
    and have no STOP or FAILED beside it."""
    if not receipt.is_file():
        return f"no DONE receipt at {receipt}"
    for name in ("STOP", "FAILED"):
        if (receipt.parent / name).exists():
            return f"the run left {name}"
    d = json.loads(receipt.read_text())
    n = n_tasks()
    if d.get("mode") != "full" or d.get("rc") != 0 or d.get("tasks") != n or d.get("ended") != n:
        return f"the receipt is not a completed full run of {n} tasks: {d}"
    return None


def receipt_path(a) -> Path:
    """The full run's DONE receipt, derived from --runs: <OUT>/runs -> <OUT>/log-full/DONE. An explicit --receipt must
    name that same file."""
    derived = Path(a.runs).resolve().parent / "log-full" / "DONE"
    if a.receipt is not None and Path(a.receipt).resolve() != derived:
        raise SystemExit(f"--receipt {a.receipt} is not this run's receipt {derived}")
    return derived


def run(a) -> int:
    why = incomplete(receipt_path(a))
    if why:
        out = {"schema": "estimator-stability-analysis/1",
               "label": "FD-STAB: the run is not complete, so nothing was graded and no estimator is adopted",
               "verdict": {"verdict": "INCOMPLETE", "winners": [], "passers": [], "why": why}}
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps({"verdict": out["verdict"]}))
        return INCOMPLETE_RC
    contract = json.loads(Path(a.s5c_contract).read_text())
    U, names = functionals(contract)
    receipt = json.loads(Path(a.sigma_receipt).read_text())
    if probe.sha256_path(Path(a.sigma_receipt)) != SIGMA_RECEIPT_SHA256:
        raise SystemExit("sigma receipt is not the pinned file")
    if list(receipt["functional_names"]) != list(names):
        raise SystemExit("the receipt's functionals are not s5c's reported functionals")
    sigma = np.asarray(receipt["sigma_rel_pct"], float) / 100.0
    M16 = cell_matrix(a.h2_definition)
    stab, sds, closures, splits = {}, {}, {}, {}
    for c in probe.CANDIDATES:
        base, jits = stability_products(Path(a.runs) / c / "stability", c)
        Fb = U @ base
        ok = (Fb != 0) & np.isfinite(sigma) & (sigma > 0)
        if int(ok.sum()) != N_FUNCTIONALS:
            raise SystemExit(f"{c}: {int(ok.sum())} usable functionals, not s5e's {N_FUNCTIONALS}")
        rel = np.array([(U @ x)[ok] / Fb[ok] - 1.0 for x in jits])
        stab[c] = {**stability_stats(rel, sigma[ok]), "functionals_used": int(ok.sum())}
        sds[c] = cell_sd(M16 @ base, [M16 @ x for x in jits])
        prods = closure_products(Path(a.runs) / c / "closure", c, Path(a.repo))
        x0, x1 = prods[DETERMINISM_PAIR[0]][0], prods[DETERMINISM_PAIR[1]][0]
        if not np.array_equal(x0, x1):
            raise SystemExit(f"{c}: the determinism pair {DETERMINISM_PAIR} differs; the estimator is not deterministic")
        splits[c] = {name: k for name, (_, _, k) in prods.items()}
        closures[c] = {name: (M16 @ x) / (M16 @ xt) - 1.0 for name, (x, xt, _) in prods.items()}
    for c in probe.CANDIDATES:
        if splits[c] != splits["control"]:
            raise SystemExit(f"{c}: a closure's MC split differs from the control's at the same truth")
    judged = [t for t, *_ in probe.CLOSURES if t != DETERMINISM_PAIR[1]]
    bias, bias_ok = {}, {}
    for c in probe.CANDIDATES:
        if c == "control":
            continue
        bias[c] = {t: no_worse(closures[c][t], sds[c], closures["control"][t], sds["control"]) for t in judged}
        bias_ok[c] = bias_status([v["no_worse"] for v in bias[c].values()])
    v = verdict(stab, bias_ok)
    readout = {c: {t: {"rms": bias_metrics(closures[c][t])[0], "max": bias_metrics(closures[c][t])[1],
                       "per_cell": np.round(closures[c][t], 6).tolist()} for t in GIBUU_READOUT} for c in probe.CANDIDATES}
    out = {"schema": "estimator-stability-analysis/1",
           "label": "FD-STAB criteria on the probe's products; relative quantities only; no data read",
           "stability": stab, "g0_informative": g0_informative(stab["control"]), "bias": bias, "bias_no_worse_all": bias_ok,
           "cell_sd": {c: np.round(v, 8).tolist() for c, v in sds.items()}, "truths_judged": judged,
           "verdict": v,
           "gibuu_readout_descriptive": {"note": "never used by a criterion or the tie-break (declaration §5.3)", **readout},
           "data_sigma_equivalent_factor": receipt.get("data", {}).get("data_sigma_over_pseudo_sigma_EW_median")}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"verdict": v, "g0_informative": out["g0_informative"]}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for opt in ("--runs", "--s5c-contract", "--sigma-receipt", "--h2-definition", "--out"):
        ap.add_argument(opt, required=True)
    ap.add_argument("--receipt", help="optional: must be <runs>/../log-full/DONE, the receipt derived from --runs")
    ap.add_argument("--repo", default=".", help="repository root (the closures' committed truth files)")
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
