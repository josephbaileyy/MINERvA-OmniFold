#!/usr/bin/env python3
"""Executable cost model for the 2D total-uncertainty feasibility assessment (lane C).

Reads only committed accounting receipts, then prices candidate validation procedures as

    total = setup + development + N_experiments * per_experiment
            + independent_verification + retry_allowance

with a protected verification/repair reserve of at least 20% of the admitted total.
Nothing here launches compute, reads scientific products, or requests an allocation.

Every operand carries a ``basis`` label:

    MEASURED     summed from a committed sacct receipt
    DOCUMENTED   a wall time stated in a committed record without an accounting receipt
    EXTRAPOLATED derived from MEASURED/DOCUMENTED values by a stated ratio
    ASSUMED      a planning choice; the sensitivity tables show its effect

Usage (from the repository root):

    python3 docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py \
        [--n-per-case N] [--n-cases K] [--n-inner R] [--out costs.json] [--check]

``--check`` recomputes and compares against the committed ``costs.json`` byte for byte.
Standard library only, deterministic, no network, no ROOT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
STATE = REPO / "docs" / "orchestration" / "state"

NODE_BILLING = 256  # billed units per Perlmutter CPU node (regular_1 billing=256 on one node)
RESERVE_FRACTION = 0.20

# Column layouts differ between the three receipts; each is read with its own map.
RECEIPTS = {
    "ki84_rebuild": {
        "source": "docs/orchestration/state/ki84-rebuild-20261006/sacct_all.txt",
        "columns": {"id": 0, "qos": 1, "state": 2, "elapsed": 3, "tres": 4},
        "workload": "production 2D bootstrap replica: unfold_2d_omnifold_unbinned.py "
                    "--iters 5 --use-weights --estimator lgbm --bootstrap-seed N --seed 1 "
                    "(sbatch_ki84_replicas.sh), CV omnifile",
    },
    "ki85_diag": {
        "source": "docs/orchestration/state/ki85-diag-20261006/sacct_ki85.txt",
        "columns": {"id": 0, "state": 1, "elapsed": 2, "tres": 3, "qos": 4},
        "workload": "fixed-truth pseudo-data toy: coverage_fixed_truth/fixed_truth_toy.py "
                    "--iters 5 --estimator lgbm --seed 1 (sbatch_ki85_arms.sh, 64 CPUs)",
    },
    "vl169_coverage": {
        "source": "docs/orchestration/state/coverage-2d-20261005/sacct_all.txt",
        "columns": {"id": 0, "name": 1, "state": 2, "qos": 3, "elapsed": 4, "tres": 5},
        "workload": "fixed-truth closure toy with MC bootstrap stream "
                    "(sbatch_fixed_truth_toys.sh, 128 CPUs) and equivalence runs",
    },
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_receipt(key: str) -> dict:
    """Group sacct rows by (array job, qos, billing) and return per-group timing."""
    spec = RECEIPTS[key]
    path = REPO / spec["source"]
    cols = spec["columns"]
    groups: dict[tuple, list[int]] = {}
    unbilled = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        f = line.split("|")
        m = re.search(r"billing=(\d+)", f[cols["tres"]])
        if m is None:
            unbilled.append({"id": f[cols["id"]], "state": f[cols["state"]],
                             "elapsed_s": int(f[cols["elapsed"]])})
            continue
        job = f[cols["id"]].split("_")[0]
        name = f[cols["name"]] if "name" in cols else ""
        gkey = (job, name, f[cols["qos"]], int(m.group(1)), f[cols["state"]])
        groups.setdefault(gkey, []).append(int(f[cols["elapsed"]]))
    out = []
    for (job, name, qos, billing, state), el in sorted(groups.items()):
        node_h = [e / 3600 * billing / NODE_BILLING for e in el]
        out.append({
            "array_job": job, "name": name, "qos": qos, "billing": billing, "state": state,
            "n": len(el), "elapsed_s_min": min(el), "elapsed_s_median": statistics.median(el),
            "elapsed_s_mean": round(statistics.fmean(el), 3), "elapsed_s_max": max(el),
            "node_h_per_job_mean": round(statistics.fmean(node_h), 6),
            "node_h_sum": round(sum(node_h), 4),
        })
    return {"source": spec["source"], "digest": "sha256:" + sha256_of(path),
            "workload": spec["workload"], "groups": out, "rows_without_billing": unbilled}


def pick(rec: dict, job: str) -> dict:
    return next(g for g in rec["groups"] if g["array_job"] == job)


def measured_operands(receipts: dict) -> dict:
    ki84 = receipts["ki84_rebuild"]
    ki85 = receipts["ki85_diag"]
    cov = receipts["vl169_coverage"]
    boot_shared = pick(ki84, "59410433")          # 300 replicas, shared, 64 CPUs
    boot_regular = pick(ki84, "59409026")         # 1 replica, regular, full node
    toy_regular = pick(cov, "59358992")           # 3 pilot toys, regular, full node
    ki85_arrays = [g for g in ki85["groups"] if g["array_job"] in ("59469539", "59469543")]
    n85 = sum(g["n"] for g in ki85_arrays)
    toy_shared = sum(g["node_h_per_job_mean"] * g["n"] for g in ki85_arrays) / n85
    completed = sum(g["n"] for r in receipts.values() for g in r["groups"]
                    if g["state"] == "COMPLETED")
    failed = sum(g["n"] for r in receipts.values() for g in r["groups"]
                 if g["state"] not in ("COMPLETED",))
    return {
        "unfold_shared64_bootstrap_node_h": {
            "value": boot_shared["node_h_per_job_mean"], "basis": "MEASURED",
            "n": boot_shared["n"], "from": "ki84_rebuild 59410433 (shared, billing 64)"},
        "unfold_regular128_bootstrap_node_h": {
            "value": boot_regular["node_h_per_job_mean"], "basis": "MEASURED",
            "n": boot_regular["n"], "from": "ki84_rebuild 59409026 (regular_1, billing 256)"},
        "toy_regular128_node_h": {
            "value": toy_regular["node_h_per_job_mean"], "basis": "MEASURED",
            "n": toy_regular["n"], "from": "vl169_coverage pilot 59358992 (regular_1, billing 256)"},
        "toy_shared64_node_h": {
            "value": round(toy_shared, 6), "basis": "MEASURED", "n": n85,
            "from": "ki85_diag arrays 59469539 + 59469543 (shared, billing 64)"},
        "completed_2d_unfold_jobs": {"value": completed, "basis": "MEASURED",
                                     "from": "all three receipts"},
        "non_completed_billed_records": {"value": failed, "basis": "MEASURED",
                                         "from": "all three receipts"},
    }


def cp_upper(k: int, n: int, alpha: float = 0.05) -> float:
    """One-sided Clopper-Pearson upper bound; closed form for k == 0."""
    if k != 0:
        raise ValueError("only k == 0 is needed here")
    return 1.0 - alpha ** (1.0 / n)


# ----------------------------------------------------------------------------------------
# Scenarios. Each per-unfold rate states its basis; documented wall times are not receipts.
# ----------------------------------------------------------------------------------------
DOC_UNIVERSE_WALL_FULLNODE_H = 0.5    # "Per-task wall ~30 min on a full Milan node", 187-universe
                                      # sweep 53441839, 2D RUN_LOG_ARCHIVE 2026-05-26 (evidence tag)
DOC_LGBM_CV_WALL_FULLNODE_H = 804 / 3600   # "5-iter MEFHC unfold, lgbm | 128 CPU | 13m24s",
                                           # 2D_OMNIFOLD_STUDY_STATUS.md runtime table
DOC_EXACT_GBT_WALL_FULLNODE_H = 19.0  # "5-iter MEFHC unfold, exact GBT | regular, 128 CPU | ~19 h"
# Lane A FREEZE (9fab26e8, a/verification.md and a/pairings.tsv P03): the quoted central's job
# 53116554 ran 69,523 s on regular_1 at billing 256 (MEASURED by A from sacct) with batch MaxRSS
# 16.8 GB and one busy core (sklearn exact is single-threaded). A extrapolates ~0.68 node-h per
# exact unfold when packed by memory on shared nodes; packing contention is unmeasured.
EXACT_AS_RUN_NODE_H = 69523 / 3600
EXACT_PACKED_NODE_H = 0.68


def scenarios(m: dict) -> dict:
    shared = m["unfold_shared64_bootstrap_node_h"]["value"]
    regular = max(m["unfold_regular128_bootstrap_node_h"]["value"],
                  m["toy_regular128_node_h"]["value"])
    io_ratio = DOC_UNIVERSE_WALL_FULLNODE_H / DOC_LGBM_CV_WALL_FULLNODE_H
    return {
        "optimistic": {
            "c_cv_unfold": {"value": shared, "basis": "MEASURED",
                            "why": "production replica workload, shared 64 CPUs, n=300"},
            "c_universe_unfold": {"value": round(shared * io_ratio, 6), "basis": "EXTRAPOLATED",
                                  "why": f"shared rate x documented universe/CV wall ratio "
                                         f"{io_ratio:.3f} (119 GB universe omnifile I/O); "
                                         f"universe unfolds at 64 CPUs are unmeasured"},
            "nuisance_pseudodata_overhead": {"value": 1.0, "basis": "ASSUMED",
                                             "why": "in-process reweighting, as fixed_truth_toy.py"},
            "c_extraction_per_experiment": {"value": 0.01, "basis": "ASSUMED",
                                            "why": "rollup of one experiment's outputs"},
            "retry_rate": {"value": 0.02, "basis": "ASSUMED",
                           "why": "about 3x the measured 0-failure CP95 upper bound"},
            "verification_fraction": {"value": 0.05, "basis": "ASSUMED",
                                      "why": "independent re-run of 5% of experiments"},
            "storage_mb_per_unfold": {"value": 0.06, "basis": "MEASURED",
                                      "why": "ki84 budget.json: 300 ROOT + .done = 18M"},
        },
        "conservative": {
            "c_cv_unfold": {"value": regular, "basis": "MEASURED",
                            "why": "largest measured full-node (regular, 128 CPU) unfold"},
            "c_universe_unfold": {"value": DOC_UNIVERSE_WALL_FULLNODE_H, "basis": "DOCUMENTED",
                                  "why": "~30 min per universe task on a full node, no receipt"},
            "nuisance_pseudodata_overhead": {"value": 1.5, "basis": "ASSUMED",
                                             "why": "lateral shifts and support re-evaluation"},
            "c_extraction_per_experiment": {"value": 0.05, "basis": "ASSUMED",
                                            "why": "rollup incl. 188-file universe read"},
            "retry_rate": {"value": 0.10, "basis": "ASSUMED",
                           "why": "time-limit losses as seen in larger campaigns"},
            "verification_fraction": {"value": 0.10, "basis": "ASSUMED",
                                      "why": "independent re-run of 10% of experiments"},
            "storage_mb_per_unfold": {"value": 0.06, "basis": "MEASURED",
                                      "why": "ki84 budget.json: 300 ROOT + .done = 18M"},
        },
    }


def v(s: dict, k: str) -> float:
    return s[k]["value"]


# ----------------------------------------------------------------------------------------
# Procedures priced per experiment.
# ----------------------------------------------------------------------------------------
N_UNIVERSES = 187   # uq/universes_full_list.txt (44 bands)
N_SEEDS = 10        # seedscan_lgbm/run_seedscan_lgbm_interactive.sh, seeds 1..10
N_BOOT_CURRENT = 300


def per_experiment(proc: str, s: dict, n_inner: int) -> dict:
    cv, uni = v(s, "c_cv_unfold"), v(s, "c_universe_unfold")
    ovh, ext = v(s, "nuisance_pseudodata_overhead"), v(s, "c_extraction_per_experiment")
    if proc == "P1_reconstructed_full":
        # every data-dependent width recurs: central + inner stat replicas + ML seeds on the
        # pseudo-data, and every systematic universe re-unfolded on the same pseudo-data.
        units = {"central": 1, "inner_stat": n_inner, "ml_seeds": N_SEEDS,
                 "universes": N_UNIVERSES}
        node_h = (cv * ovh + n_inner * cv + N_SEEDS * cv + N_UNIVERSES * uni + ext)
    elif proc == "P2_fixed_band":
        # one unfold of nuisance-drawn pseudo-data, scored against a band frozen beforehand
        units = {"central": 1, "inner_stat": 0, "ml_seeds": 0, "universes": 0}
        node_h = cv * ovh + ext
    elif proc == "P3_shortcut_S1_S2":
        # systematic and ML blocks transferred (S1); inner stat replicas reduced (S2)
        units = {"central": 1, "inner_stat": n_inner, "ml_seeds": 0, "universes": 0}
        node_h = cv * ovh + n_inner * cv + ext
    else:
        raise KeyError(proc)
    n_unfolds = sum(units.values())
    return {"unfolds": units, "n_unfolds": n_unfolds, "node_h": round(node_h, 6),
            "storage_gb": round(n_unfolds * v(s, "storage_mb_per_unfold") / 1024, 6)}


def setup_items(s: dict, pairing_established: bool) -> list[dict]:
    cv, uni = v(s, "c_cv_unfold"), v(s, "c_universe_unfold")
    cons = uni == DOC_UNIVERSE_WALL_FULLNODE_H
    items = [
        {"id": "S-r", "what": "identity-carrying event-loop rebuild with universe columns (B's R0, "
                              "needed by every independent-population option): 12 playlists at the "
                              "full-universe loop's 8 CPU / 48G request (billing 24 ASSUMED); "
                              "optimistic 2.5 h per task (documented vertical-universe maximum), "
                              "conservative the 24 h time limit",
         "node_h": 12 * (24.0 if cons else 2.5) * 24 / NODE_BILLING, "basis": "EXTRAPOLATED",
         "reusable_because": "event identity and universe weights do not depend on any experiment",
         "conditional_on": "B: populations"},
        {"id": "S-a", "what": "matched systematic sweep at the central estimator's seed/backend "
                              "(187 universes + matched CV)",
         "node_h": 0.0 if pairing_established else N_UNIVERSES * uni + cv,
         "basis": "EXTRAPOLATED", "reusable_because": "deltas depend on the MC model, not on a "
         "single experiment, once the central recipe is fixed (valid only for P2/P3; P1 recomputes)",
         "conditional_on": "A: PAIRING NOT ESTABLISHED"},
        {"id": "S-b", "what": "selection-complete lateral support: reuse 5D active-universe "
                              "event loops (optimistic) or rerun 120 per-playlist loops "
                              "(conservative ceiling: 120 x 5 h x 8/256), then 10 lateral unfolds",
         "node_h": (120 * 5 * 8 / NODE_BILLING if cons else 0.0) + 10 * uni,
         "basis": "EXTRAPOLATED", "reusable_because": "event-level support does not depend on "
         "the experiment's data draw", "conditional_on": "M1 / component C05a"},
        {"id": "S-d", "what": "continuous lateral nuisance generator (relaxed-selection event "
                              "pass with shifted muon kinematics)",
         "node_h": 20.0 if cons else 2.0, "basis": "ASSUMED",
         "reusable_because": "per-event shift vectors are experiment independent",
         "conditional_on": "M1"},
        {"id": "S-e", "what": "background-template statistics: analytic sum-w2 bound "
                              "(optimistic) or a 300-replica rebuild with a background stream",
         "node_h": 300 * cv if cons else 0.0, "basis": "EXTRAPOLATED",
         "reusable_because": "template statistics are fixed MC populations",
         "conditional_on": "M2 / component C03"},
        {"id": "S-f", "what": "bootstrap x estimator-seed factorial (50 replicas x 4 seeds)",
         "node_h": 200 * cv, "basis": "EXTRAPOLATED",
         "reusable_because": "measures the overlap of two blocks at the central recipe",
         "conditional_on": "M3 / component C08"},
        {"id": "S-j", "what": "model-allowance calibration: 3 development truths x 200 "
                              "fixed-band experiments + 2 expectation runs each",
         "node_h": 3 * (200 + 2) * cv * v(s, "nuisance_pseudodata_overhead"),
         "basis": "EXTRAPOLATED", "reusable_because": "B is frozen before validation and "
         "does not depend on validation data", "conditional_on": "component C09"},
    ]
    for it in items:
        it["node_h"] = round(it["node_h"], 4)
    return items


DEVELOPMENT_NODE_H = 6.0   # successor proposal sec. 6 stage B: <= 6 node-h work for 24 runs,
                           # plus >= 2 node-h held for verification (the reserve is applied below)


def total(proc: str, s: dict, n_exp: int, n_inner: int, pairing_established: bool) -> dict:
    pe = per_experiment(proc, s, n_inner)
    setup = setup_items(s, pairing_established)
    setup_sum = sum(i["node_h"] for i in setup)
    production = n_exp * pe["node_h"]
    verification = v(s, "verification_fraction") * (production + setup_sum)
    retry = v(s, "retry_rate") * (production + setup_sum + DEVELOPMENT_NODE_H)
    subtotal = setup_sum + DEVELOPMENT_NODE_H + production + verification + retry
    admitted = subtotal / (1.0 - RESERVE_FRACTION)
    return {
        "procedure": proc, "n_experiments": n_exp, "n_inner": n_inner,
        "per_experiment": pe,
        "setup_node_h": round(setup_sum, 3), "development_node_h": DEVELOPMENT_NODE_H,
        "production_node_h": round(production, 3), "verification_node_h": round(verification, 3),
        "retry_node_h": round(retry, 3), "subtotal_node_h": round(subtotal, 3),
        "protected_reserve_node_h": round(admitted - subtotal, 3),
        "admitted_total_node_h": round(admitted, 3),
        "storage_gb_all_experiments": round(n_exp * pe["storage_gb"], 3),
        "unfold_count": n_exp * pe["n_unfolds"],
    }


def wall_days(node_h: float, node_equivalents: float) -> float:
    return node_h / node_equivalents / 24.0


# ----------------------------------------------------------------------------------------
# Analytic checks for the two cost-saving proposals (no data).
# ----------------------------------------------------------------------------------------
def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def coverage_scaled(z: float, rho: float) -> float:
    """Coverage of X +- z*rho*sigma for Gaussian X (S1: transferred width ratio rho)."""
    return 2.0 * phi(z * rho) - 1.0


def coverage_estimated_sigma(z: float, nu: int, steps: int = 20000) -> float:
    """E[2 Phi(z sqrt(V)) - 1], V ~ chi2_nu / nu (S2: sigma estimated from nu+1 replicas)."""
    k = nu / 2.0
    lo, hi = 0.0, 1.0 + 12.0 * math.sqrt(2.0 / nu)
    h = (hi - lo) / steps
    tot = 0.0
    for i in range(steps + 1):
        x = lo + i * h
        if x <= 0.0:
            dens = 0.0
        else:
            y = nu * x  # chi2 variate
            logp = (k - 1) * math.log(y) - y / 2 - k * math.log(2) - math.lgamma(k)
            dens = math.exp(logp) * nu
        w = 1 if i in (0, steps) else (4 if i % 2 else 2)
        tot += w * dens * (2.0 * phi(z * math.sqrt(x)) - 1.0)
    return tot * h / 3.0


def z_for_coverage(p: float, nu: int) -> float:
    lo, hi = 0.5, 4.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if coverage_estimated_sigma(mid, nu) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def shortcut_analytics() -> dict:
    nominal = {"I68": (1.0, 0.682689), "I95": (1.959964, 0.95)}
    s1 = {f"rho={r}": {k: round(coverage_scaled(z, r), 5) for k, (z, _) in nominal.items()}
          for r in (0.90, 0.95, 1.00, 1.05, 1.10)}
    s2 = {}
    for n in (25, 50, 100, 300):
        nu = n - 1
        s2[f"N={n}"] = {
            "coverage_gaussian_z": {k: round(coverage_estimated_sigma(z, nu), 5)
                                    for k, (z, _) in nominal.items()},
            "z_restoring_nominal": {k: round(z_for_coverage(p, nu), 4)
                                    for k, (_, p) in nominal.items()},
        }
    return {"S1_transferred_width": s1, "S2_reduced_inner_replicas": s2,
            "windows_from_successor_proposal_sec5": {"I68": [0.60, 0.80], "I95": [0.90, 0.99]}}


def for_b_per_experiment(sc: dict) -> dict:
    """Statistical-only per-experiment costs B can price against (no nuisance overhead)."""
    out = {}
    for name, s in sc.items():
        cv, ext = v(s, "c_cv_unfold"), v(s, "c_extraction_per_experiment")
        out[name] = {"fixed_band_1_unfold": round(cv + ext, 6)}
        for r in (50, 100, 300):
            out[name][f"reconstructed_1_plus_{r}_unfolds"] = round((1 + r) * cv + ext, 6)
    return out


# Ledger medians (VL172 / 2D status Stage-2 table), used only for an order-of-magnitude bound.
MEDIAN_REL_SIGMA_PCT = {"ml": 0.166, "stat": 0.674, "syst": 6.830, "total": 6.8707}
BAND_SIZES = [100] + [3] + [2] * 42   # Flux, 2p2h, 42 two-universe bands = 187 universes


def overlap_bounds() -> dict:
    """Bounds on the two retraining-noise overlaps, from ledger medians (illustrative only).

    Medians of different bins do not add in quadrature exactly; per-bin values need the
    covariance files, which are not read here.
    """
    ml, stat, syst, tot = (MEDIAN_REL_SIGMA_PCT[k] for k in ("ml", "stat", "syst", "total"))
    # X02: if every bootstrap replica already carries one retraining-noise draw, the separate
    # ML block is counted twice. Its full removal bounds the effect.
    without_ml = math.sqrt(max(tot ** 2 - ml ** 2, 0.0))
    # X03: under MAT 1/N mean-centred covariance, an iid retraining-noise draw of variance
    # s^2 per universe adds s^2 * (N_b - 1)/N_b per band.
    k = sum((n - 1) / n for n in BAND_SIZES)
    noise_in_syst = math.sqrt(k) * ml
    syst_clean = math.sqrt(max(syst ** 2 - noise_in_syst ** 2, 0.0))
    return {
        "assumption": "retraining noise per unfold is iid with the seedscan median sigma "
                      f"({ml}%); unmeasured for bootstrap replicas and universe unfolds",
        "X02_bootstrap_ml": {"total_with_ml_pct": tot, "total_without_ml_pct": round(without_ml, 4),
                             "max_change_pct_points": round(tot - without_ml, 4)},
        "X03_universe_retraining": {"sum_over_bands_(N_b-1)/N_b": round(k, 3),
                                    "implied_noise_in_syst_pct": round(noise_in_syst, 3),
                                    "syst_without_noise_pct": round(syst_clean, 4),
                                    "change_pct_points": round(syst - syst_clean, 4)},
    }


def b_primary_check(m: dict) -> dict:
    """Reproduce B's primary figure (f19084f4 sec. 14): 719 x 301 runs x 0.0591 x 1.05."""
    rate = m["unfold_shared64_bootstrap_node_h"]["value"]
    val = 719 * 301 * rate * 1.05
    return {"B_quoted_node_h": 13440, "C_recomputed_node_h": round(val, 1),
            "agrees_to_1_node_h": abs(val - 13440) < 1.0}


def s1_establishment(s: dict, n_cmp_per_case: int, n_cases: int) -> float:
    """Full recomputation of the systematic block on development experiments to validate S1."""
    return round(n_cmp_per_case * n_cases * (N_UNIVERSES * v(s, "c_universe_unfold")
                                             + N_SEEDS * v(s, "c_cv_unfold")), 3)


# ----------------------------------------------------------------------------------------
def build(n_per_case: int, n_cases: int, n_inner: int) -> dict:
    receipts = {k: read_receipt(k) for k in RECEIPTS}
    m = measured_operands(receipts)
    sc = scenarios(m)
    n_exp = n_per_case * n_cases
    procs = ("P1_reconstructed_full", "P2_fixed_band", "P3_shortcut_S1_S2")
    main = {name: {p: total(p, s, n_exp, N_BOOT_CURRENT if p == "P1_reconstructed_full"
                            else n_inner, pairing_established=False)
                   for p in procs}
            for name, s in sc.items()}
    sens_n = {}
    for name, s in sc.items():
        sens_n[name] = {}
        for npc in (300, 719, 1116, 1250, 2400):
            ne = npc * n_cases
            sens_n[name][f"N_per_case={npc}"] = {
                p: total(p, s, ne, N_BOOT_CURRENT if p == "P1_reconstructed_full" else n_inner,
                         False)["admitted_total_node_h"] for p in procs}
    sens_inner = {}
    for name, s in sc.items():
        sens_inner[name] = {f"n_inner={r}": {
            "P1_reconstructed_full": total("P1_reconstructed_full", s, n_exp, r, False)[
                "admitted_total_node_h"],
            "P3_shortcut_S1_S2": total("P3_shortcut_S1_S2", s, n_exp, r, False)[
                "admitted_total_node_h"]} for r in (50, 100, 300)}
    exact_backend = {}
    for name, s in sc.items():
        s2 = json.loads(json.dumps(s))
        exact = EXACT_PACKED_NODE_H if name == "optimistic" else EXACT_AS_RUN_NODE_H
        s2["c_cv_unfold"] = {
            "value": exact,
            "basis": "EXTRAPOLATED (lane A, memory-packed)" if name == "optimistic"
                     else "MEASURED (lane A, job 53116554 as run)",
            "why": "exact sklearn GBT, the quoted central's backend"}
        # Branch X (A's CONTRACT sec. 2.4(2): the quoted central E_C is exact GBT): the matched
        # sweep (187 universes + CV) and an exact-backend seed scan (10) are rebuilt at ~19 h each.
        # The exact sweep REPLACES the LightGBM matched sweep S-a (pairing_established=True drops
        # it), and exact universe unfolds carry the same documented universe/CV wall ratio as the
        # LightGBM ones. For a compute-bound single-threaded job a multiplicative ratio is an
        # upper-side choice; an additive I/O overhead would be smaller.
        io_ratio = DOC_UNIVERSE_WALL_FULLNODE_H / DOC_LGBM_CV_WALL_FULLNODE_H
        extra_setup = N_UNIVERSES * exact * io_ratio + (1 + N_SEEDS) * exact
        p2x = total("P2_fixed_band", s2, n_exp, n_inner, True)
        exact_backend[name] = {
            "P2_fixed_band_per_experiment_central_only": p2x["admitted_total_node_h"],
            "exact_unfold_node_h": round(exact, 4),
            "extra_one_time_exact_matched_sweep_and_seedscan_node_h": round(extra_setup, 3),
            "P2_fixed_band_with_exact_setup_admitted": round(
                p2x["admitted_total_node_h"] + extra_setup / (1.0 - RESERVE_FRACTION), 3)}
    pairing = {name: {"pairing_established": total("P2_fixed_band", s, n_exp, n_inner, True)[
        "admitted_total_node_h"], "pairing_not_established": total(
        "P2_fixed_band", s, n_exp, n_inner, False)["admitted_total_node_h"]}
        for name, s in sc.items()}
    concurrency = {
        "historical_caps": "sbatch arrays used %30 concurrency; 30 shared 64-CPU tasks = 7.5 node "
                           "equivalents, 30 regular full-node tasks = 30 node equivalents",
        "wall_days": {name: {p: {
            "at_7.5_node_eq": round(wall_days(main[name][p]["admitted_total_node_h"], 7.5), 1),
            "at_30_node_eq": round(wall_days(main[name][p]["admitted_total_node_h"], 30), 1)}
            for p in procs} for name in sc},
        "memory": "sacct receipts record only ALLOCATED memory (121920M at 64 CPUs; 487802M at "
                  "128); MaxRSS is not in any receipt, so no peak-memory figure is quoted",
    }
    m_completed = m["completed_2d_unfold_jobs"]["value"]
    return {
        "schema": "uncertainty-preparation-20261008/c/costs v1",
        "not_authorized": "no allocation is requested or released; no compute is launched; "
                          "historical allocation balances are not carried forward",
        "formula": "total = setup + development + N_experiments * per_experiment + "
                   "independent_verification + retry_allowance; admitted = total / (1 - 0.20)",
        "inputs": {"n_per_case": n_per_case, "n_cases": n_cases, "n_experiments": n_exp,
                   "n_inner_for_P3": n_inner, "n_inner_for_P1": N_BOOT_CURRENT,
                   "n_universes": N_UNIVERSES, "n_ml_seeds": N_SEEDS,
                   "provenance_of_counts": "B's assurance.py criteria (f19084f4: kappa [0.80, 1.25], "
                                           "beta 0.10, alpha 0.04 coverage / 0.01 bias) rerun by C "
                                           "with n_functionals = 4 x 206 = 824: N_required 823, "
                                           "N_design 1250 per case; B's single-case values 719 / "
                                           "1116 reproduce at 206"},
        "receipts": receipts,
        "measured": m,
        "retry_evidence": {"completed": m_completed,
                           "non_completed_billed": m["non_completed_billed_records"]["value"],
                           "cp95_upper_failure_rate": round(cp_upper(0, m_completed), 5)},
        "documented_walls_h": {"universe_unfold_full_node": DOC_UNIVERSE_WALL_FULLNODE_H,
                               "lgbm_cv_unfold_full_node": round(DOC_LGBM_CV_WALL_FULLNODE_H, 4),
                               "exact_gbt_unfold_full_node": DOC_EXACT_GBT_WALL_FULLNODE_H},
        "scenarios": sc,
        "setup_items": {name: setup_items(s, False) for name, s in sc.items()},
        "totals": main,
        "sensitivity_n_per_case": sens_n,
        "sensitivity_n_inner": sens_inner,
        "sensitivity_exact_gbt_central": exact_backend,
        "sensitivity_pairing": pairing,
        "concurrency": concurrency,
        "shortcut_analytics": shortcut_analytics(),
        "S1_establishment_node_h": {name: s1_establishment(s, 20, n_cases)
                                    for name, s in sc.items()},
        "for_B_statistical_per_experiment_node_h": for_b_per_experiment(sc),
        "overlap_bounds": overlap_bounds(),
        "cross_check_B_primary": b_primary_check(m),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--n-per-case", type=int, default=1250)
    ap.add_argument("--n-cases", type=int, default=4)
    ap.add_argument("--n-inner", type=int, default=50)
    ap.add_argument("--out", type=Path, default=HERE / "costs.json")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = json.dumps(build(a.n_per_case, a.n_cases, a.n_inner), indent=1, sort_keys=False) + "\n"
    if a.check:
        same = a.out.read_text() == text
        print("costs.json reproduces" if same else "costs.json DIFFERS from recomputation")
        return 0 if same else 1
    a.out.write_text(text)
    print(f"wrote {a.out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
