"""Coverage of the section-9 uncertainty procedure and the C1-C5 rules (PROTOCOL-20260925 6.4).

Input: coverage replicates, each with B = 6 bootstrap-member run directories already scored by
`score_design.py` (one `*.design_scores.json` per member). For each replicate and histogram:

* estimate = member mean of the unit-normalized unfolded histograms; member sd (ddof 1);
* interval = mean +/- t_{(1+L)/2}(B - 1) x member sd per bin, L = 0.68 and 0.95 (section 9 as
  written: the member sd, not the sd of the mean);
* covered = |target - estimate| <= half-width, target = the replicate's OWN pseudodata truth
  (unit-normalized; identical across the members, refused otherwise), and, reported only, the
  population target when the member scores carry `vs_population`.

Reported per bin: marginal coverage, mean half-width, the empirical sd of the estimates across
replicates, width / sd, bias (mean estimate - target), pull mean and sd ((estimate - target) /
member sd). Pooled over bins: coverage with replicate-cluster bootstrap bounds
(`inference.cluster_bootstrap_bounds`, at the declared per-bound level). Per region: the same on
each scoreable historical region's 7 bins.

Rules (section 6.4), each with its numbers:

* C1 (development tilt, 7 E_avail bins): pooled 95 % coverage LB >= 0.90 and point <= 0.99; pooled
  68 % coverage LB >= 0.60 and point <= 0.80.
* C2: no bin's 95 % coverage point estimate < 0.85.
* C3: moderate and good regions, pooled 95 % coverage LB >= 0.85 (each region).
* C4: every bin's mean 95 % half-width <= 2.5 x the empirical sd of the estimates; and the top
  E_avail bin's (3-100 GeV) mean 95 % half-width <= 0.5 x its injected displacement (mean over
  replicates of |target - prior| in that bin; the protocol quotes 0.068 for this bound).
* C5 (D4c up, 60 replicates, natural histogram E_avail x proton class): pooled 95 % LB >= 0.85.

    python coverage.py --spec coverage_spec.json --out coverage.json

Spec: {"candidate", "k", "bonferroni_m", "look", "looks_planned", "B": 6,
       "dev": [{"replicate": id, "members": [score json, ...]}, ...],
       "d4c": [...], "previous": optional look-1 output (resolved rules carry over)}
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inference as inf  # noqa: E402
from score_design import SCOREABLE_REGIONS, canonical_case  # noqa: E402

B_MEMBERS = 6
LEVELS = (0.68, 0.95)
C4_TOP_BIN_BOUND_QUOTED = 0.068
TARGET_TOL = 1e-12


def c4(n: int) -> float:
    """E[sample sd] / sigma for n normal draws."""
    return math.sqrt(2.0 / (n - 1)) * math.exp(math.lgamma(n / 2.0) - math.lgamma((n - 1) / 2.0))


def t_factor(level: float, b: int) -> float:
    return float(stats.t.ppf(0.5 + level / 2.0, b - 1))


def coverage_arrays(members: np.ndarray, target: np.ndarray, alpha: float,
                    prior: np.ndarray | None = None) -> dict[str, Any]:
    """Coverage statistics from members (R, B, nbins) and targets (R, nbins), unit-normalized."""
    members = np.asarray(members, np.float64)
    target = np.asarray(target, np.float64)
    R, B, nb = members.shape
    if target.shape != (R, nb):
        raise ValueError(f"target shape {target.shape} != {(R, nb)}")
    est = members.mean(axis=1)
    sd = members.std(axis=1, ddof=1)
    dev = est - target
    empty = (np.abs(members).sum(axis=1) == 0) & (target == 0)       # excluded cells
    out: dict[str, Any] = {"n_replicates": R, "B": B, "n_bins": nb, "levels": {}}
    emp_sd = est.std(axis=0, ddof=1) if R > 1 else np.full(nb, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        pull = np.where(sd > 0, dev / (sd * math.sqrt(1.0 + 1.0 / B)), np.nan)
    # the reported estimate is the MEAN of B members, so the prediction interval for its error adds
    # the members' Monte-Carlo variance sd^2/B to the sampling variance sd^2 the member spread
    # estimates: half-width = t(B-1) x sd x sqrt(1 + 1/B) (statistical review 8d9aaf8d, item 2;
    # PROTOCOL Amendment 2c)
    inflate = math.sqrt(1.0 + 1.0 / B)
    out["interval_inflation_sqrt_1_plus_1_over_B"] = inflate
    rms = np.sqrt(np.nanmean(np.where(empty, np.nan, dev) ** 2, axis=0))
    out["per_bin_rms_error"] = rms.tolist()
    out["per_bin_calibrated_mean_half_width_95"] = (t_factor(0.95, B) * c4(B) * inflate * rms).tolist()
    for level in LEVELS:
        hw = t_factor(level, B) * sd * inflate
        hits = (np.abs(dev) <= hw).astype(np.float64)
        hits[empty] = np.nan
        pooled = inf.cluster_bootstrap_bounds(hits, alpha)
        out["levels"][f"{level:.2f}"] = {
            "t_factor": t_factor(level, B),
            "per_bin_coverage": np.nanmean(hits, axis=0).tolist(),
            "per_bin_mean_half_width": hw.mean(axis=0).tolist(),
            "pooled": pooled}
    hw95 = t_factor(0.95, B) * sd * inflate
    with np.errstate(divide="ignore", invalid="ignore"):
        width_ratio = hw95.mean(axis=0) / emp_sd
    out.update({
        "per_bin_empirical_sd_of_estimates": emp_sd.tolist(),
        "per_bin_width95_over_empirical_sd": width_ratio.tolist(),
        "per_bin_bias": dev.mean(axis=0).tolist(),
        "per_bin_pull_mean": np.nanmean(pull, axis=0).tolist(),
        "per_bin_pull_sd": (np.nanstd(pull, axis=0, ddof=1) if R > 1
                            else np.full(nb, np.nan)).tolist(),
        "n_excluded_empty_cells": int(empty.sum())})
    if prior is not None:
        inj = np.abs(target - np.asarray(prior, np.float64).mean(axis=1))
        out["per_bin_mean_injected_abs"] = inj.mean(axis=0).tolist()
    return out


# ------------------------------------------------------------------------------------------- #
# Loading member scores
# ------------------------------------------------------------------------------------------- #
def _iteration(doc: Mapping[str, Any], k: int) -> Mapping[str, Any]:
    for it in doc["iterations"]:
        if it["k"] == k:
            if it.get("histograms") is None:
                raise ValueError(f"{doc['run_name']} k={k} was not scored: {it.get('not_scored')}")
            return it
    raise ValueError(f"{doc['run_name']}: k={k} not scored")


def load_replicates(entries: Sequence[Mapping[str, Any]], k: int, histogram: str,
                    expect_case: str, B: int = B_MEMBERS) -> dict[str, Any]:
    """(R, B, nbins) members, (R, nbins) targets and priors, and population targets if present."""
    mem, tgt, pri, pop, ids = [], [], [], [], []
    for e in entries:
        docs = [json.loads(Path(p).read_text()) for p in e["members"]]
        if len(docs) != B:
            raise ValueError(f"replicate {e['replicate']}: {len(docs)} members, protocol B = {B}")
        cases = {d["case"]["case"] for d in docs}
        if cases != {canonical_case(expect_case)}:
            raise ValueError(f"replicate {e['replicate']}: cases {cases} != {expect_case}")
        rows = {d.get("identity", {}).get("pseudo_rows_sha256") for d in docs}
        if len(rows) > 1:
            raise ValueError(f"replicate {e['replicate']}: members differ in pseudodata rows")
        prows = {d.get("identity", {}).get("prior_rows_sha256") for d in docs}
        if len(prows) > 1:
            raise ValueError(f"replicate {e['replicate']}: members differ in prior rows")
        # distinct members (review ec475e7b): a duplicated member would shrink the spread
        boots = [json.dumps(d.get("identity", {}).get("bootstrap"), sort_keys=True) for d in docs]
        if None in [d.get("identity", {}).get("bootstrap") for d in docs] or \
                len(set(boots)) != len(boots) or len({str(p) for p in e["members"]}) != len(docs):
            raise ValueError(f"replicate {e['replicate']}: members are not {B} distinct bootstrap "
                             "members")
        its = [_iteration(d, k)["histograms"][histogram] for d in docs]
        t = np.array([h["target_norm"] for h in its])
        if np.abs(t - t[0]).max() > TARGET_TOL:
            raise ValueError(f"replicate {e['replicate']}: member targets differ (a member's "
                             "target includes its bootstrap weights?)")
        mem.append([h["unfolded_norm"] for h in its])
        pri.append([h["prior_norm"] for h in its])
        tgt.append(t[0])
        vp = [_iteration(d, k).get("vs_population", {}).get(histogram) for d in docs]
        pop.append(vp[0]["target_norm"] if all(v is not None for v in vp) else None)
        ids.append(e["replicate"])
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate replicate ids")
    return {"replicates": ids, "members": np.array(mem), "target": np.array(tgt),
            "prior": np.array(pri),
            "population": (np.array(pop) if pop and all(p is not None for p in pop) else None)}


# ------------------------------------------------------------------------------------------- #
# C1-C5
# ------------------------------------------------------------------------------------------- #
def _pooled_part(label: str, pooled: Mapping[str, Any], op: str, thr: float, kind: str
                 ) -> inf.Part:
    return inf.Part(label, op, thr, kind, estimate=pooled["point"], lb=pooled["lb"],
                    ub=pooled["ub"])


def rules(dev: Mapping[str, Any] | None, regions: Mapping[str, Mapping[str, Any]] | None,
          d4c: Mapping[str, Any] | None, look: int, looks_planned: int) -> dict[str, Any]:
    out: dict[str, inf.Verdict] = {}
    if dev is None:
        for r in ("C1", "C2", "C4"):
            out[r] = inf.incomplete(r, "no development-tilt coverage replicates")
    else:
        p95, p68 = dev["levels"]["0.95"]["pooled"], dev["levels"]["0.68"]["pooled"]
        out["C1"] = inf.decide("C1", [
            _pooled_part("pooled 95% coverage LB", p95, ">=", 0.90, "bound"),
            _pooled_part("pooled 95% coverage point", p95, "<=", 0.99, "point"),
            _pooled_part("pooled 68% coverage LB", p68, ">=", 0.60, "bound"),
            _pooled_part("pooled 68% coverage point", p68, "<=", 0.80, "point")],
            look, looks_planned, {"pooled_95": p95, "pooled_68": p68})
        cov = dev["levels"]["0.95"]["per_bin_coverage"]
        out["C2"] = inf.decide("C2", [inf.Part(f"bin {j} 95% coverage point", ">=", 0.85, "point",
                                               estimate=c) for j, c in enumerate(cov)],
                               look, looks_planned, {"per_bin_coverage_95": cov})
        hw = dev["levels"]["0.95"]["per_bin_mean_half_width"]
        esd = dev["per_bin_empirical_sd_of_estimates"]
        # C4 as amended (Amendment 2c; statistical review 8d9aaf8d, BLOCK): per bin, the mean 95 %
        # half-width may exceed a CALIBRATED interval's expected half-width,
        # t(B-1) c4(B) sqrt(1+1/B) x RMS(estimate - target), by at most 25 %
        cal = dev["per_bin_calibrated_mean_half_width_95"]
        parts = [inf.Part(f"bin {j} mean 95% half-width <= 1.25 x calibrated", "<=",
                          1.25 * c, "point", estimate=h) for j, (h, c) in enumerate(zip(hw, cal))]
        inj_top = dev.get("per_bin_mean_injected_abs", [None])[-1]
        numbers = {"per_bin_mean_half_width_95": hw, "per_bin_empirical_sd": esd,
                   "top_bin_injected_abs": inj_top, "top_bin_bound_quoted": C4_TOP_BIN_BOUND_QUOTED}
        if inj_top is None:
            out["C4"] = inf.incomplete("C4", "no prior spectra for the injected displacement",
                                       numbers)
        else:
            parts.append(inf.Part("top-bin mean 95% half-width <= 0.5 x injected", "<=",
                                  0.5 * inj_top, "point", estimate=hw[-1]))
            numbers["top_bin_bound_from_rule"] = 0.5 * inj_top
            numbers["top_bin_verdict_against_quoted_0.068"] = bool(hw[-1] <= C4_TOP_BIN_BOUND_QUOTED)
            out["C4"] = inf.decide("C4", parts, look, looks_planned, numbers)
    if not regions or any(r not in regions for r in ("moderate", "good")):
        out["C3"] = inf.incomplete("C3", "no regional coverage")
    else:
        out["C3"] = inf.decide("C3", [
            _pooled_part(f"{r} pooled 95% coverage LB", regions[r]["levels"]["0.95"]["pooled"],
                         ">=", 0.85, "bound") for r in ("moderate", "good")],
            look, looks_planned, {r: regions[r]["levels"]["0.95"]["pooled"]
                                  for r in ("moderate", "good")})
    if d4c is None:
        out["C5"] = inf.incomplete("C5", "no D4c-up coverage replicates")
    else:
        p = d4c["levels"]["0.95"]["pooled"]
        out["C5"] = inf.decide("C5", [_pooled_part("D4c pooled 95% coverage LB", p, ">=", 0.85,
                                                   "bound")], look, looks_planned, {"pooled_95": p})
    return {k: v.as_dict() for k, v in sorted(out.items())}


def carry_over(current: dict[str, Any], previous: Mapping[str, Any] | None) -> dict[str, Any]:
    """Section 8: a rule resolved (PASS/FAIL) at look 1 keeps its look-1 verdict."""
    if previous is None:
        return current
    for rule, v in previous.items():
        if v["verdict"] in (inf.PASS, inf.FAIL):
            current[rule] = {**v, "carried_from_look": 1}
    return current


def run(spec: Mapping[str, Any]) -> dict[str, Any]:
    k, B = int(spec["k"]), int(spec.get("B", B_MEMBERS))
    look, looks = int(spec.get("look", 1)), int(spec.get("looks_planned", 2))
    alpha = inf.per_bound_alpha(int(spec["bonferroni_m"]), looks)
    res: dict[str, Any] = {"schema": "pet-final-design/coverage/1",
                           "candidate": spec.get("candidate"), "k": k, "B": B, "look": look,
                           "looks_planned": looks, "alpha_one_sided_per_bound": alpha,
                           "bonferroni_m": int(spec["bonferroni_m"])}
    dev = regions = d4c = None
    if spec.get("dev"):
        L = load_replicates(spec["dev"], k, "eavail", "D1_p0.350", B)
        dev = coverage_arrays(L["members"], L["target"], alpha, L["prior"])
        dev["replicates"] = L["replicates"]
        if L["population"] is not None:
            dev["vs_population"] = coverage_arrays(L["members"], L["population"], alpha)
        regions = {}
        for r in SCOREABLE_REGIONS:
            Lr = load_replicates(spec["dev"], k, f"eavail@{r}", "D1_p0.350", B)
            regions[r] = coverage_arrays(Lr["members"], Lr["target"], alpha, Lr["prior"])
    if spec.get("d4c"):
        L = load_replicates(spec["d4c"], k, "eavail_x_proton", "D4c_p_up", B)
        d4c = coverage_arrays(L["members"], L["target"], alpha, L["prior"])
        d4c["replicates"] = L["replicates"]
    res.update({"dev_eavail": dev, "regions": regions, "d4c_eavail_x_proton": d4c})
    prev = None
    if spec.get("previous"):
        prev = json.loads(Path(spec["previous"]).read_text())["rules"]
    res["rules"] = carry_over(rules(dev, regions, d4c, look, looks), prev)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    res = run(json.loads(a.spec.read_text()))
    a.out.write_text(json.dumps(inf.jsonable(res), indent=1, allow_nan=False) + "\n")
    for r, v in res["rules"].items():
        print(f"{r}: {v['verdict']}" + (f" ({v['reason']})" if v.get("reason") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
