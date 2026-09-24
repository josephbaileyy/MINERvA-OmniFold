"""Tables and decisions of the confirmatory stage (PROTOCOL sections 5, 7; amendments 2-3).

Reads the committed per-run score files `results/<stage>/<run>.scores.json` (copied from the run
directories) and writes `results/confirm_results.json` plus the tables printed into
`CONFIRM_RESULTS.md`. Nothing is re-scored here.

* Runs: CTL/A is ONE run (CTL = its k = 3, A = its k = 10); B and C are scored at k = 3 and K* = 10.
* Paired differences per replicate: candidate - CTL(k = 3), candidates at K* = 10 (the headline)
  and at k = 3 (like-for-like).
* PILOT sizing (section 5.3): n = max(8, the n giving 80 % power, at one-sided alpha, to reject
  "mean difference <= -0.02" when the true difference is 0, using the 80 % upper confidence bound
  of the pilot sd), capped at 12. alpha is taken as 0.05/3 (Holm's first step across A, B, C: the
  conservative choice), and the largest n over the candidate differences is used.
* FINAL decisions (section 5.4): one-sided t tests on the paired differences, Holm-adjusted across
  A, B, C separately for each inequality: superiority (> 0), non-inferiority (> -0.02), switching
  (> +0.04); the lower 95 % one-sided confidence bound is reported beside each mean. Adequacy:
  mean aggregate recovery >= the historical floor AND every scoreable region's mean >= its
  historical regional floor, floors IMPORTED from the historical report
  (`configuration_comparison/campaign_report.json`); thresholds checked by
  `authorization_scope.check_like_for_like_thresholds`. Evaluated at k = 3 and at K* = 10.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
sys.path.insert(0, str(CAMPAIGN))
import authorization_scope as scope  # noqa: E402

REPORT = CAMPAIGN.parent / "configuration_comparison" / "campaign_report.json"
NAME = re.compile(r"^(?P<stage>[a-z]+)-(?P<cand>CTL|B|C)-(?P<pool>[A-Z])(?P<rep>\d+)"
                  r"(?:-(?P<dist>.+))?$")
REGIONS = ("low_acceptance", "moderate", "good")
KSTAR = 10


def historical_floors() -> dict[str, Any]:
    rep = json.loads(REPORT.read_text())
    thresholds = scope.check_like_for_like_thresholds(
        {k: v for k, v in scope.historical_thresholds().items()})
    return {"aggregate": rep["absolute_adequacy"]["floor"],
            "aggregate_reference": rep["absolute_adequacy"]["reference"],
            "regions": dict(rep["regional_safeguard"]["floor_by_region"]),
            "non_inferiority": thresholds["non_inferiority_delta"],
            "switching": thresholds["switching_delta"], "source": str(REPORT.name)}


def at_k(scores: dict, k: int) -> dict[str, Any] | None:
    for it in scores["iterations"]:
        if it["k"] == k:
            p, pop = it["push"], it.get("push_vs_population")
            return {"R": p["recovery"], "regions": p["recovery_by_region"],
                    "R_pop": None if pop is None else pop["recovery"],
                    "regions_pop": None if pop is None else pop["recovery_by_region"],
                    "signed_residual_per_bin": p["aggregate"]["signed_residual_per_bin"],
                    "injected_per_bin": p["aggregate"]["injected_per_bin"],
                    "moves_away": it.get("moves_away"),
                    "ess_over_n": it["final_truth_weights_ess"]["ess"]
                    / it["final_truth_weights_ess"]["n"],
                    "w_max": it["push_weights_on_truth_passing"]["max"],
                    "w_p999": it["push_weights_on_truth_passing"]["p99.9"]}
    return None


def load_stage(directory: Path) -> dict[str, dict]:
    runs = {}
    for path in sorted(directory.glob("*.scores.json")):
        name = path.name[:-len(".scores.json")]
        m = NAME.match(name)
        if not m:
            continue
        s = json.loads(path.read_text())
        c = s["constants"]
        runs[name] = {**m.groupdict(), "rep": int(m["rep"]),
                      "k3": at_k(s, 3), f"k{KSTAR}": at_k(s, KSTAR),
                      "iterations_scored": len(s["iterations"]),
                      "oracle": c["oracle_vs_replicate_target"]["recovery"],
                      "oracle_pop": (c.get("oracle_vs_population_target") or {}).get("recovery"),
                      "replicate_minus_population_l1": c.get(
                          "replicate_target_minus_population_l1"),
                      "provenance": {k: s["provenance"].get(k) for k in
                                     ("config_hash", "code_commit", "receipt_sha256")}}
    return runs


def observations(runs: dict[str, dict], dist: str | None = None) -> dict[str, dict[int, dict]]:
    """{estimator: {replicate: point}} with CTL = CTL k3, A = CTL k10, B3/B10, C3/C10."""
    out: dict[str, dict[int, dict]] = {}
    for r in runs.values():
        if r["dist"] != dist:
            continue
        for label, cand, k in (("CTL", "CTL", 3), ("A", "CTL", KSTAR), ("B@3", "B", 3),
                               (f"B@{KSTAR}", "B", KSTAR), ("C@3", "C", 3),
                               (f"C@{KSTAR}", "C", KSTAR), ("A@3", "CTL", 3)):
            if r["cand"] == cand and r[f"k{k}"] is not None:
                out.setdefault(label, {})[r["rep"]] = r[f"k{k}"]
    return out


def paired(obs: dict, label: str) -> np.ndarray:
    reps = sorted(set(obs.get(label, {})) & set(obs.get("CTL", {})))
    return np.array([obs[label][r]["R"] - obs["CTL"][r]["R"] for r in reps])


def ucb80_sd(sd: float, df: int) -> float:
    return sd * math.sqrt(df / stats.chi2.ppf(0.20, df))


def n_for_power(sigma: float, margin: float = 0.02, alpha: float = 0.05 / 3,
                power: float = 0.80, cap: int = 200) -> int:
    for n in range(2, cap + 1):
        df = n - 1
        # noncentral t: P(T > t_{1-alpha}) with noncentrality margin*sqrt(n)/sigma
        crit = stats.t.ppf(1 - alpha, df)
        if 1 - stats.nct.cdf(crit, df, margin * math.sqrt(n) / sigma) >= power:
            return n
    return cap


def sizing(pilot: dict[str, dict]) -> dict[str, Any]:
    obs = observations(pilot)
    out = {"alpha_one_sided": 0.05 / 3, "power": 0.80, "margin": 0.02, "differences": {}}
    need = []
    for label in ("A", f"B@{KSTAR}", f"C@{KSTAR}", "B@3", "C@3"):
        d = paired(obs, label)
        if d.size < 2:
            continue
        sd = float(d.std(ddof=1))
        ucb = ucb80_sd(sd, d.size - 1)
        n = n_for_power(ucb) if ucb > 0 else 2
        need.append(n)
        out["differences"][f"{label} - CTL"] = {"per_replicate": d.tolist(), "mean": float(d.mean()),
                                               "sd": sd, "df": int(d.size - 1),
                                               "sd_ucb80": ucb, "n_for_80pct_power": n}
    out["n_final"] = int(min(12, max([8] + need))) if need else None
    out["n_uncapped"] = int(max([8] + need)) if need else None
    return out


def holm(pvals: dict[str, float]) -> dict[str, dict[str, float | bool]]:
    order = sorted(pvals, key=pvals.get)
    m, out, stop = len(order), {}, False
    for i, key in enumerate(order):
        level = 0.05 / (m - i)
        reject = (not stop) and pvals[key] <= level
        stop = stop or not reject
        out[key] = {"p": pvals[key], "holm_level": level, "reject_H0": reject}
    return out


def decisions(final: dict[str, dict], floors: dict[str, Any]) -> dict[str, Any]:
    obs = observations(final)
    out: dict[str, Any] = {"floors": floors, "tests": {}, "adequacy": {}}
    for kk in (KSTAR, 3):
        # at k = 3, A IS the CTL run (identical by construction): it is not tested there
        labels = ({"A": "A"} if kk == KSTAR else {}) | {"B": f"B@{kk}", "C": f"C@{kk}"}
        diffs = {c: paired(obs, lab) for c, lab in labels.items()}
        block = {}
        for test, delta in (("superiority", 0.0), ("non_inferiority", -floors["non_inferiority"]),
                            ("switching", floors["switching"])):
            pv, est = {}, {}
            for c, d in diffs.items():
                if d.size < 2:
                    continue
                se = d.std(ddof=1) / math.sqrt(d.size)
                t = ((d.mean() - delta) / se if se > 0
                     else (math.inf if d.mean() > delta else -math.inf))
                pv[c] = float(1 - stats.t.cdf(t, d.size - 1))
                est[c] = {"mean": float(d.mean()), "se": float(se), "n": int(d.size),
                          "lower_95_one_sided": float(d.mean() - stats.t.ppf(0.95, d.size - 1) * se)}
            block[test] = {"threshold": delta, "estimates": est, "holm": holm(pv) if pv else {}}
        out["tests"][f"K={kk}"] = block
    for label in ("CTL", "A", f"B@{KSTAR}", f"C@{KSTAR}", "B@3", "C@3"):
        pts = obs.get(label, {})
        if len(pts) < 2:
            continue
        vals = np.array([p["R"] for p in pts.values()])

        def lcb(v: np.ndarray) -> float:
            return float(v.mean() - stats.t.ppf(0.95, v.size - 1) * v.std(ddof=1) / math.sqrt(v.size))
        reg = {}
        for name in REGIONS:
            rv = np.array([p["regions"][name] for p in pts.values()])
            reg[name] = {"mean": float(rv.mean()), "lower_95": lcb(rv),
                         "floor": floors["regions"][name],
                         "meets_floor": bool(rv.mean() >= floors["regions"][name])}
        out["adequacy"][label] = {
            "n": int(vals.size), "mean": float(vals.mean()), "lower_95": lcb(vals),
            "floor": floors["aggregate"], "meets_floor": bool(vals.mean() >= floors["aggregate"]),
            "regions": reg,
            "adequate": bool(vals.mean() >= floors["aggregate"]
                             and all(r["meets_floor"] for r in reg.values()))}
    return out


def stress_table(stress: dict[str, dict]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for r in stress.values():
        for label, k in (("CTL" if r["cand"] == "CTL" else f"{r['cand']}@3", 3),
                         ("A" if r["cand"] == "CTL" else f"{r['cand']}@{KSTAR}", KSTAR)):
            p = r[f"k{k}"]
            if p is None:
                continue
            cell = out.setdefault(r["dist"], {}).setdefault(label, {})
            cell[str(r["rep"])] = {"R": p["R"], "R_pop": p["R_pop"], "regions": p["regions"],
                                   "moves_away": p["moves_away"],
                                   "signed_residual_per_bin": p["signed_residual_per_bin"],
                                   "oracle": r["oracle"], "oracle_pop": r["oracle_pop"]}
    return out


def fmt(x: Any, nd: int = 3) -> str:
    return "—" if x is None else f"{x:.{nd}f}"


def markdown(res: dict[str, Any]) -> str:
    lines = []
    if res.get("pilot"):
        lines += ["### PILOT (pool P; reported separately, never enters FINAL)", "",
                  "| replicate | CTL (k=3) | A (k=10) | B k=3 | B k=10 | C k=3 | C k=10 | oracle |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
        obs = res["pilot"]["observations"]
        for rep in sorted({int(r) for lab in obs.values() for r in lab}):
            row = [obs.get(lab, {}).get(str(rep), {}).get("R") for lab in
                   ("CTL", "A", "B@3", f"B@{KSTAR}", "C@3", f"C@{KSTAR}")]
            lines.append(f"| P{rep} | " + " | ".join(fmt(v) for v in row) +
                         f" | {fmt(res['pilot']['oracle'].get(str(rep)))} |")
        sz = res["pilot"]["sizing"]
        lines += ["", "| paired difference | per replicate | mean | sd (df) | 80 % UCB of sd | n for 80 % power |",
                  "|---|---|---:|---:|---:|---:|"]
        for k, v in sz["differences"].items():
            lines.append(f"| {k} | {', '.join(f'{x:+.3f}' for x in v['per_replicate'])} | "
                         f"{v['mean']:+.3f} | {v['sd']:.4f} ({v['df']}) | {v['sd_ucb80']:.4f} | "
                         f"{'>= ' if v['n_for_80pct_power'] >= 200 else ''}{v['n_for_80pct_power']} |")
        lines += ["", f"**n for FINAL = {sz['n_final']}** (uncapped {sz['n_uncapped']}; cap 12).", ""]
    if res.get("stress"):
        lines += ["### PET stress set (pool T; mean of replicates; * = moves away from the target "
                  "on some replicate)", "",
                  "| case | CTL k=3 | A k=10 | B k=3 | B k=10 | C k=3 | C k=10 |", "|---|---:|---:|---:|---:|---:|---:|"]
        for case, cells in sorted(res["stress"].items()):
            row = []
            for lab in ("CTL", "A", "B@3", f"B@{KSTAR}", "C@3", f"C@{KSTAR}"):
                c = cells.get(lab, {})
                if not c:
                    row.append("—")
                    continue
                m = np.mean([v["R"] for v in c.values()])
                away = any((v["moves_away"] or {}).get("replicate_target") for v in c.values())
                row.append(f"{m:.3f}{'*' if away else ''} ({len(c)})")
            lines.append(f"| {case} | " + " | ".join(row) + " |")
        lines.append("")
    if res.get("final_progress"):
        fp = res["final_progress"]
        lines += [f"### FINAL: {fp['runs_scored']} of {fp['runs_expected']} runs scored -- no decision "
                  "statistic is computed until all are in (fixed-n design)", ""]
    if res.get("final"):
        d = res["final"]["decisions"]
        lines += ["### FINAL (pool F): decision inequalities vs CTL (k=3), Holm across A, B, C", ""]
        for kk, block in d["tests"].items():
            lines += [f"Candidates at {kk}:", "",
                      "| candidate | mean diff | lower 95 % | superiority | non-inferiority (-0.02) | switching (+0.04) |",
                      "|---|---:|---:|---|---|---|"]
            for c in ("A", "B", "C"):
                e = block["superiority"]["estimates"].get(c)
                if e is None:
                    continue
                cells = [("reject" if block[t]["holm"][c]["reject_H0"] else "not shown") +
                         f" (p={block[t]['holm'][c]['p']:.3g})" for t in
                         ("superiority", "non_inferiority", "switching")]
                lines.append(f"| {c} | {e['mean']:+.4f} | {e['lower_95_one_sided']:+.4f} | " +
                             " | ".join(cells) + " |")
            lines.append("")
        lines += ["Adequacy (historical floors imported unchanged):", "",
                  "| estimator | n | mean R | lower 95 % | floor | low | moderate | good | adequate |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for lab, a in d["adequacy"].items():
            regs = " | ".join(f"{a['regions'][r]['mean']:.3f}{'' if a['regions'][r]['meets_floor'] else ' (<floor)'}"
                              for r in REGIONS)
            lines.append(f"| {lab} | {a['n']} | {a['mean']:.4f} | {a['lower_95']:.4f} | "
                         f"{a['floor']:.4f} | {regs} | {'yes' if a['adequate'] else 'no'} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, default=HERE / "results")
    args = ap.parse_args()
    floors = historical_floors()
    res: dict[str, Any] = {"floors": floors}
    pilot = load_stage(args.results / "pilot") if (args.results / "pilot").is_dir() else {}
    if pilot:
        obs = observations(pilot)
        res["pilot"] = {"runs": pilot,
                        "observations": {k: {str(r): v for r, v in d.items()} for k, d in obs.items()},
                        "oracle": {str(r["rep"]): r["oracle"] for r in pilot.values()
                                   if r["cand"] == "CTL"},
                        "sizing": sizing(pilot)}
    stress = load_stage(args.results / "stress") if (args.results / "stress").is_dir() else {}
    if stress:
        res["stress"] = stress_table(stress)
    final = load_stage(args.results / "final") if (args.results / "final").is_dir() else {}
    n_expected = 3 * 12
    if final and len(final) >= n_expected:
        res["final"] = {"runs": final, "decisions": decisions(final, floors)}
    elif final:
        # fixed-n design: no decision statistic is computed or shown before FINAL is complete
        res["final_progress"] = {"runs_scored": len(final), "runs_expected": n_expected}
    (args.results / "confirm_results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(markdown(res))


if __name__ == "__main__":
    main()
