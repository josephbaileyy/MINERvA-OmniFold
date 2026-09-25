"""The PROTOCOL-20260925 section-6 decision table as code (with the section-8 sequential rule).

Input: an evidence declaration (JSON) naming, per candidate, its iteration count k and the
`score_design.py` outputs of its runs (case read from each score file; replicate id declared), its
multi-seed runs (N2), its coverage output (`coverage.py`), its per-unfolding GPU-hour
measurements (section 6.7) and whether its provenance is complete (section 10).

Every verdict carries its rule id and numbers. Levels: every bound is one-sided at
`0.05 / m / looks_planned` (`inference.per_bound_alpha`), m = the declared Bonferroni count
(default: the size of the declared decision set). A candidate lacking required evidence for a rule
gets INCOMPLETE on that rule and is never eligible.

Rules (section ids):

* 6.1 U1 mean R_E0 >= floor and LB >= floor (floor = 0.8 x 0.6949731569, from the historical
  report). U2a each region's mean >= its historical regional floor (0.6 x regional reference;
  LBs reported). U2b moderate/good mean >= 0.50 and LB >= 0.40, low-acceptance mean >= 0.25 and
  LB > 0. U2c no E_avail bin with |mean injected| >= 0.01 has mean signed movement (unfolded -
  prior, signed along the injection) < -0.005. U3 (E3) and U4/U5 (E4/E5): mean >= 0.50/0.25 and
  LB >= 0.40 / LB > 0.10.
* 6.2 B1 pooled (case, replicate) units with a defined recovery on the case's natural histogram:
  Clopper-Pearson UB on P(R < 0) <= 0.10 and no case with mean R < 0. B2 cases whose mean
  E_avail injection < 3F: mean (E_avail residual - injected) <= 0.010. B3 null: mean spurious
  E_avail L1 <= 0.012 and mean spurious E_avail x proton L1 <= 3 x its null floor (the mean prior
  L1 to the target on the same null replicates = the oracle residual under the null). B4 |mean
  E8| <= 0.15 for both signs of R1, E8 = R_E0(R1 + D1) - R_E0(D1) paired by replicate.
* 6.3 N1 every run's truth-passing push finite and non-negative, max <= 100 in every run; over
  the E0 replicates median ESS/n (of w_truth x push) >= 0.20 and median 99.9th percentile push
  <= 10. N2 pooled within-draw estimator-seed sd of R_E0 <= 0.05 from >= 4 seeds x >= 2 draws.
* 6.4 C1-C5 from the candidate's coverage output.
* 6.5 non-inferiority of a smaller package; 6.6 ranking, tie-break, unresolved; 6.7 cost ratio.

    python decide.py --evidence evidence.json --out decision.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

HERE = Path(__file__).resolve().parent
CONFIRM = HERE.parents[1] / "improvement_campaign" / "confirm"
for p in (HERE, CONFIRM):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import inference as inf  # noqa: E402
from score_design import UNDEFINED_BELOW, canonical_case, classify_case  # noqa: E402

PROTOCOL_U1_FLOOR = 0.5559785255            # as printed in section 6.1 (10 decimals)
E0_CASE = "D1_p0.350"
E3_CASE = "D1_m0.350"
E4_CASE = "D4c_p_up"
E5_CASE = "D3_p0.35"
R1_SIGNS = ("R1_x1.05+D1_p0.350", "R1_x0.95+D1_p0.350")
REGIONS = ("low_acceptance", "moderate", "good")

# section 6.5 margins on LB(small - large) and the section 6.6 materiality margins
NI_MARGINS = {"E0": -0.02, "moderate": -0.04, "good": -0.04, "E3": -0.04, "E4": -0.05,
              "E5": -0.05}
COST_RATIO_MIN = 2.0
# Section 8 applies the two-look rule to FINAL (E0-E3) and coverage; the robustness library
# (n_S fixed), numerical stability and the pure point rules are decided once.
SEQUENTIAL_RULES_DEFAULT = ("U1", "U2b", "U3", "6.5", "6.6.1", "6.6.3")


def historical_floors() -> dict[str, Any]:
    """The predecessor's import of the historical floors (campaign_report.json + thresholds),
    checked against the value printed in the protocol."""
    import analyze_confirm
    fl = analyze_confirm.historical_floors()
    if abs(fl["aggregate"] - PROTOCOL_U1_FLOOR) > 5e-11:
        raise SystemExit(f"historical floor {fl['aggregate']} != protocol {PROTOCOL_U1_FLOOR}")
    return fl


# ------------------------------------------------------------------------------------------- #
# Evidence
# ------------------------------------------------------------------------------------------- #
class Candidate:
    """One candidate's scored runs at its k: {case: {replicate: record}}."""

    def __init__(self, name: str, decl: Mapping[str, Any]) -> None:
        self.name = name
        self.decl = decl
        self.k = int(decl["k"])
        self.cases: dict[str, dict[str, dict[str, Any]]] = {}
        self.problems: list[str] = []
        for run in decl.get("runs", []):
            rec = self._load(run)
            if rec is None:
                continue
            slot = self.cases.setdefault(rec["case"], {})
            if rec["replicate"] in slot:
                raise ValueError(f"{name}: duplicate ({rec['case']}, {rec['replicate']})")
            slot[rec["replicate"]] = rec
        self.seed_runs = [r for r in (self._load(s) for s in decl.get("seed_runs", [])) if r]
        self.coverage = (json.loads(Path(decl["coverage"]).read_text())
                         if decl.get("coverage") else None)

    def _load(self, run: Mapping[str, Any]) -> dict[str, Any] | None:
        doc = json.loads(Path(run["score"]).read_text())
        it = next((i for i in doc["iterations"] if i["k"] == self.k), None)
        if it is None:
            self.problems.append(f"{doc['run_name']}: k={self.k} not scored")
            return None
        rc = doc.get("provenance", {}).get("receipt", {})
        if rc.get("complete") is not True:
            self.problems.append(f"{doc['run_name']}: receipt not complete")
        ident = doc.get("identity", {})
        return {"case": canonical_case(doc["case"]["case"]), "replicate": str(run["replicate"]),
                "seed": run.get("seed"), "run": doc["run_name"], "it": it,
                "rows": (ident.get("prior_rows_sha256"), ident.get("pseudo_rows_sha256")),
                "natural": doc["case"]["natural"]}

    def values(self, case: str, getter) -> dict[str, float | None]:
        return {r: getter(rec) for r, rec in self.cases.get(case, {}).items()
                if rec["it"].get("histograms") is not None}


def g_hist(name: str, field: str = "recovery"):
    return lambda rec: rec["it"]["histograms"][name][field]


def g_natural(field: str = "recovery"):
    return lambda rec: rec["it"]["histograms"][rec["natural"]][field]


# ------------------------------------------------------------------------------------------- #
# Per-candidate eligibility rules
# ------------------------------------------------------------------------------------------- #
class Rules:
    def __init__(self, ev: Mapping[str, Any], floors: Mapping[str, Any]) -> None:
        self.ev = ev
        self.floors = floors
        self.look = int(ev.get("look", 1))
        self.looks = int(ev.get("looks_planned", 2))
        self.m = int(ev.get("bonferroni_m", len(ev["decision_set"])))
        self.alpha = inf.per_bound_alpha(self.m, self.looks)
        self.alpha_fixed = inf.per_bound_alpha(self.m, 1)
        self.sequential = set(ev.get("sequential_rules", SEQUENTIAL_RULES_DEFAULT))
        self.n_final = int(ev["n_final"])
        self.n_stress = int(ev["n_stress"])
        self.n_required = {E0_CASE: self.n_final, E3_CASE: self.n_final,
                           E4_CASE: self.n_final, E5_CASE: self.n_final}
        self.n_required.update({canonical_case(k): int(v)
                                for k, v in ev.get("n_required", {}).items()})

    def alpha_for(self, rule: str) -> float:
        return self.alpha if rule in self.sequential else self.alpha_fixed

    def decide(self, rule, parts, numbers=None) -> inf.Verdict:
        if rule in self.sequential:
            return inf.decide(rule, parts, self.look, self.looks, numbers)
        return inf.decide(rule, parts, 1, 1, numbers)

    def _vals(self, rule: str, c: Candidate, case: str, getter, need: int
              ) -> tuple[np.ndarray | None, inf.Verdict | None, dict[str, Any]]:
        v = c.values(case, getter)
        nums = {"case": case, "n": len(v), "required_n": need,
                "per_replicate": dict(sorted(v.items()))}
        if len(v) < need:
            return None, inf.incomplete(rule, f"{len(v)} scored replicates of {case} < {need}",
                                        nums), nums
        undefined = [r for r, x in v.items() if x is None]
        if undefined:
            return None, inf.incomplete(rule, f"recovery undefined (injected L1 < 3F) on "
                                              f"replicates {undefined}", nums), nums
        return np.array(list(v.values()), float), None, nums

    def mean_and_lb(self, rule: str, c: Candidate, case: str, getter, mean_thr: float,
                    lb_op: str, lb_thr: float, need: int, label: str) -> inf.Verdict:
        x, bad, nums = self._vals(rule, c, case, getter, need)
        if bad:
            return bad
        tb = inf.t_bounds(x, self.alpha_for(rule))
        nums["t"] = tb.as_dict()
        return self.decide(rule, [
            inf.Part(f"mean {label}", ">=", mean_thr, "point", tb.mean, tb.lb, tb.ub),
            inf.Part(f"LB {label}", lb_op, lb_thr, "bound", tb.mean, tb.lb, tb.ub)], nums)

    # 6.1 --------------------------------------------------------------------------------- #
    def U1(self, c):
        fl = self.floors["aggregate"]
        return self.mean_and_lb("U1", c, E0_CASE, g_hist("eavail"), fl, ">=", fl,
                                self.n_required[E0_CASE], "R_E0")

    def U2a(self, c):
        parts, nums = [], {}
        for r in REGIONS:
            x, bad, n = self._vals("U2a", c, E0_CASE, g_hist(f"eavail@{r}"), self.n_final)
            if bad:
                return inf.Verdict("U2a", bad.verdict, [], {r: n}, f"{r}: {bad.reason}")
            tb = inf.t_bounds(x, self.alpha_for("U2a"))
            nums[r] = {"t": tb.as_dict(), "floor": self.floors["regions"][r]}
            parts.append(inf.Part(f"{r} mean", ">=", self.floors["regions"][r], "point", tb.mean))
        return self.decide("U2a", parts, nums)

    def U2b(self, c):
        parts, nums = [], {}
        spec = {"moderate": (0.50, ">=", 0.40), "good": (0.50, ">=", 0.40),
                "low_acceptance": (0.25, ">", 0.0)}
        for r, (mthr, op, lthr) in spec.items():
            x, bad, n = self._vals("U2b", c, E0_CASE, g_hist(f"eavail@{r}"), self.n_final)
            if bad:
                return inf.Verdict("U2b", bad.verdict, [], {r: n}, f"{r}: {bad.reason}")
            tb = inf.t_bounds(x, self.alpha_for("U2b"))
            nums[r] = tb.as_dict()
            parts += [inf.Part(f"{r} mean", ">=", mthr, "point", tb.mean, tb.lb, tb.ub),
                      inf.Part(f"{r} LB", op, lthr, "bound", tb.mean, tb.lb, tb.ub)]
        return self.decide("U2b", parts, nums)

    def U2c(self, c):
        recs = {r: rec for r, rec in c.cases.get(E0_CASE, {}).items()
                if rec["it"].get("histograms") is not None}
        if len(recs) < self.n_final:
            return inf.incomplete("U2c", f"{len(recs)} E0 replicates < {self.n_final}")
        inj = np.array([rec["it"]["histograms"]["eavail"]["injected_per_bin"]
                        for rec in recs.values()])
        mov = np.array([rec["it"]["histograms"]["eavail"]["moved_per_bin"]
                        for rec in recs.values()])
        mi = inj.mean(axis=0)
        parts, nums = [], {"mean_injected_per_bin": mi.tolist(), "bins": {}}
        for j in np.flatnonzero(np.abs(mi) >= 0.01):
            along = np.sign(mi[j]) * mov[:, j]
            tb = inf.t_bounds(along, self.alpha_for("U2c"))
            nums["bins"][int(j)] = tb.as_dict()
            parts.append(inf.Part(f"bin {j} mean movement along injection", ">=", -0.005,
                                  "point", tb.mean))
        return self.decide("U2c", parts, nums)

    def U3(self, c):
        return self.mean_and_lb("U3", c, E3_CASE, g_natural(), 0.50, ">=", 0.40,
                                self.n_required[E3_CASE], "R_E3")

    def U4(self, c):
        return self.mean_and_lb("U4", c, E4_CASE, g_natural(), 0.25, ">", 0.10,
                                self.n_required[E4_CASE], "R_E4")

    def U5(self, c):
        return self.mean_and_lb("U5", c, E5_CASE, g_natural(), 0.25, ">", 0.10,
                                self.n_required[E5_CASE], "R_E5")

    # 6.2 --------------------------------------------------------------------------------- #
    def library(self) -> list[str]:
        return [canonical_case(x) for x in self.ev["library"]]

    def B1(self, c):
        units, per_case, parts = 0, {}, []
        fails = 0
        for case in self.library():
            v = c.values(case, g_natural())
            if len(v) < self.n_stress:
                return inf.incomplete("B1", f"{case}: {len(v)} replicates < {self.n_stress}",
                                      {"per_case": per_case})
            d = np.array([x for x in v.values() if x is not None], float)
            per_case[case] = {"n_scored": len(v), "n_defined": int(d.size),
                              "n_fail": int((d < 0).sum()),
                              "mean_R": float(d.mean()) if d.size else None}
            units += d.size
            fails += int((d < 0).sum())
            if d.size:
                tb = inf.t_bounds(d, self.alpha_for("B1"))
                per_case[case]["t"] = tb.as_dict()
                parts.append(inf.Part(f"{case} mean R", ">=", 0.0, "point", tb.mean, tb.lb,
                                      tb.ub))
        if units == 0:
            return inf.incomplete("B1", "no unit with a defined recovery", {"per_case": per_case})
        lo, hi = inf.clopper_pearson(fails, units, self.alpha_for("B1"))
        lo0, hi0 = inf.clopper_pearson(fails, units, 0.05)
        nums = {"units": units, "failures": fails, "cp_upper": hi, "cp_lower": lo,
                "cp_upper_unadjusted_0.05": hi0, "alpha_one_sided": self.alpha_for("B1"),
                "per_case": per_case}
        parts.insert(0, inf.Part("CP upper bound on P(R<0)", "<=", 0.10, "bound",
                                 fails / units, lo, hi))
        return self.decide("B1", parts, nums)

    def B2(self, c):
        parts, nums = [], {}
        for case in self.library():
            inj = c.values(case, g_hist("eavail", "injected_l1"))
            if len(inj) < self.n_stress:
                return inf.incomplete("B2", f"{case}: {len(inj)} replicates < {self.n_stress}")
            if np.mean(list(inj.values())) >= UNDEFINED_BELOW:
                continue
            res = c.values(case, g_hist("eavail", "residual_l1"))
            d = np.array([res[r] - inj[r] for r in inj])
            tb = inf.t_bounds(d, self.alpha_for("B2"))
            nums[case] = {"mean_injected_l1": float(np.mean(list(inj.values()))),
                          "residual_minus_injected": tb.as_dict()}
            parts.append(inf.Part(f"{case} mean(residual - injected)", "<=", 0.010, "point",
                                  tb.mean))
        nums["cases_below_3F"] = sorted(k for k in nums)
        return self.decide("B2", parts, nums)

    def B3(self, c):
        null = [canonical_case(x) for x in self.ev.get("null_cases", ["null"])]
        recs = {}
        for case in null:
            recs.update({(case, r): rec for r, rec in c.cases.get(case, {}).items()
                         if rec["it"].get("histograms") is not None})
        if len(recs) < self.n_stress:
            return inf.incomplete("B3", f"{len(recs)} null replicates < {self.n_stress}")
        h = [rec["it"]["histograms"] for rec in recs.values()]
        e = np.array([x["eavail"]["residual_l1"] for x in h])
        j = np.array([x["eavail_x_proton"]["residual_l1"] for x in h])
        floor = float(np.mean([x["eavail_x_proton"]["injected_l1"] for x in h]))
        nums = {"n": len(h), "mean_eavail_spurious_l1": float(e.mean()),
                "mean_eavail_x_proton_spurious_l1": float(j.mean()),
                "eavail_x_proton_null_floor": floor,
                "eavail_prior_l1_mean": float(np.mean([x["eavail"]["injected_l1"] for x in h]))}
        return self.decide("B3", [
            inf.Part("mean E_avail spurious L1", "<=", 0.012, "point", float(e.mean())),
            inf.Part("mean E_avail x proton spurious L1", "<=", 3 * floor, "point",
                     float(j.mean()))], nums)

    def B4(self, c):
        parts, nums = [], {}
        for rcase in R1_SIGNS:
            if rcase not in self.library():
                return inf.incomplete("B4", f"{rcase} not in the declared library "
                                            "(B4 needs both signs of R1)")
            r1 = c.values(rcase, g_hist("eavail"))
            d1 = c.values(E0_CASE, g_hist("eavail"))
            common = sorted(set(r1) & set(d1))
            bad = [r for r in common if c.cases[rcase][r]["rows"] != c.cases[E0_CASE][r]["rows"]]
            if bad:
                raise ValueError(f"{c.name}: {rcase} and {E0_CASE} replicates {bad} are not "
                                 "event-paired (row digests differ)")
            if len(common) < self.n_stress:
                return inf.incomplete("B4", f"{rcase}: {len(common)} matched replicates "
                                            f"< {self.n_stress}")
            if any(r1[r] is None or d1[r] is None for r in common):
                return inf.incomplete("B4", f"{rcase}: undefined recovery")
            e8 = np.array([r1[r] - d1[r] for r in common])
            tb = inf.t_bounds(e8, self.alpha_for("B4"))
            nums[rcase] = {"E8": tb.as_dict(), "replicates": common}
            parts.append(inf.Part(f"|mean E8| {rcase}", "<=", 0.15, "point", abs(tb.mean)))
        return self.decide("B4", parts, nums)

    # 6.3 --------------------------------------------------------------------------------- #
    def N1(self, c):
        allrecs = [rec for case in c.cases.values() for rec in case.values()]
        e0 = [rec for rec in c.cases.get(E0_CASE, {}).values()]
        if len(e0) < self.n_final:
            return inf.incomplete("N1", f"{len(e0)} E0 replicates < {self.n_final}")
        st = [rec["it"]["stability"] for rec in allrecs]
        bad = [rec["run"] for rec, s in zip(allrecs, st)
               if s["n_nonfinite_truth_passing"] or s["n_negative_truth_passing"]]
        wmax = max(s.get("push_max", math.inf) for s in st)
        e0s = [rec["it"]["stability"] for rec in e0]
        ess = [s.get("final_truth_weight_ess_over_n") for s in e0s]
        p999 = [s.get("push_p999") for s in e0s]
        nums = {"runs_checked": len(st), "runs_nonfinite_or_negative": bad,
                "max_push_over_runs": wmax, "e0_ess_over_n": ess, "e0_push_p999": p999}
        if bad or any(x is None for x in ess + p999):
            return self.decide("N1", [inf.Part("all weights finite and non-negative", ">=", 1,
                                               "point", 0.0)], nums)
        nums.update({"median_ess_over_n": float(np.median(ess)),
                     "median_p999": float(np.median(p999))})
        return self.decide("N1", [
            inf.Part("all weights finite and non-negative", ">=", 1, "point", 1.0),
            inf.Part("median ESS/n", ">=", 0.20, "point", float(np.median(ess))),
            inf.Part("median p99.9 truth weight", "<=", 10.0, "point", float(np.median(p999))),
            inf.Part("max weight in every run", "<=", 100.0, "point", wmax)], nums)

    def N2(self, c):
        groups: dict[str, list[dict[str, Any]]] = {}
        for rec in c.seed_runs:
            if rec["case"] != E0_CASE:
                raise ValueError(f"{c.name}: seed run {rec['run']} is {rec['case']}, not E0")
            groups.setdefault(rec["replicate"], []).append(rec)
        nums: dict[str, Any] = {"draws": {}}
        ok = {g: v for g, v in groups.items() if len({r["seed"] for r in v}) >= 4}
        if len(ok) < 2:
            return inf.incomplete("N2", f"{len(ok)} event draws with >= 4 seeds (need >= 2)",
                                  {"draws": {g: len(v) for g, v in groups.items()}})
        ss, df = 0.0, 0
        for g, v in ok.items():
            if len({r["rows"] for r in v}) != 1:
                raise ValueError(f"{c.name}: seed runs of draw {g} differ in events")
            x = np.array([r["it"]["histograms"]["eavail"]["recovery"] for r in v], float)
            nums["draws"][g] = {"n_seeds": int(x.size), "sd": float(x.std(ddof=1)),
                                "values": x.tolist()}
            ss += float(((x - x.mean()) ** 2).sum())
            df += x.size - 1
        sd = math.sqrt(ss / df)
        nums["pooled_within_draw_sd"] = sd
        return self.decide("N2", [inf.Part("estimator-seed sd of R_E0", "<=", 0.05, "point",
                                           sd)], nums)

    # 6.4 --------------------------------------------------------------------------------- #
    def C(self, c) -> list[inf.Verdict]:
        cov = c.coverage
        rules = ("C1", "C2", "C3", "C4", "C5")
        if cov is None:
            return [inf.incomplete(r, "no coverage output") for r in rules]
        if cov.get("candidate") not in (None, c.name) or int(cov["k"]) != c.k:
            raise ValueError(f"{c.name}: coverage file is for {cov.get('candidate')} k={cov['k']}")
        out = []
        for r in rules:
            v = cov["rules"][r]
            out.append(inf.Verdict(r, v["verdict"], [], {"coverage_rule": v}, v.get("reason")))
        return out

    def provenance(self, c) -> inf.Verdict:
        nums = {"declared_provenance_complete": bool(c.decl.get("provenance_complete")),
                "problems": c.problems}
        if not nums["declared_provenance_complete"] or c.problems:
            return inf.incomplete("P(section 10)", "provenance incomplete", nums)
        return inf.Verdict("P(section 10)", inf.PASS, [], nums)

    def eligibility(self, c: Candidate) -> dict[str, Any]:
        verdicts = [self.provenance(c), self.U1(c), self.U2a(c), self.U2b(c), self.U2c(c),
                    self.U3(c), self.U4(c), self.U5(c), self.B1(c), self.B2(c), self.B3(c),
                    self.B4(c), self.N1(c), self.N2(c), *self.C(c)]
        vs = {v.rule: v.verdict for v in verdicts}
        if inf.FAIL in vs.values():
            status = "INELIGIBLE"
        elif inf.INCOMPLETE in vs.values():
            status = "INCOMPLETE"
        elif inf.CONTINUE in vs.values():
            status = "CONTINUE"
        else:
            status = "ELIGIBLE"
        return {"status": status, "verdicts": {v.rule: v.as_dict() for v in verdicts},
                "failed": sorted(r for r, x in vs.items() if x == inf.FAIL),
                "incomplete": sorted(r for r, x in vs.items() if x == inf.INCOMPLETE),
                "continue": sorted(r for r, x in vs.items() if x == inf.CONTINUE)}


# ------------------------------------------------------------------------------------------- #
# Paired contrasts, non-inferiority (6.5), ranking (6.6)
# ------------------------------------------------------------------------------------------- #
ENDPOINT_GETTERS = {"E0": (E0_CASE, g_hist("eavail")),
                    "moderate": (E0_CASE, g_hist("eavail@moderate")),
                    "good": (E0_CASE, g_hist("eavail@good")),
                    "E3": (E3_CASE, g_natural()), "E4": (E4_CASE, g_natural()),
                    "E5": (E5_CASE, g_natural())}


def paired_diff(a: Candidate, b: Candidate, endpoint: str) -> dict[str, Any]:
    """a - b per replicate, on replicates both scored, refusing pairs that are not event-paired."""
    case, getter = ENDPOINT_GETTERS[endpoint]
    va, vb = a.values(case, getter), b.values(case, getter)
    common = sorted(set(va) & set(vb))
    bad = [r for r in common if a.cases[case][r]["rows"] != b.cases[case][r]["rows"]]
    if bad:
        raise ValueError(f"{a.name} vs {b.name} {endpoint}: replicates {bad} are not event-paired")
    common = [r for r in common if va[r] is not None and vb[r] is not None]
    return {"replicates": common, "diff": np.array([va[r] - vb[r] for r in common], float)}


class Contrasts:
    def __init__(self, rules: Rules, cands: Mapping[str, Candidate]) -> None:
        self.r = rules
        self.c = cands

    def lb_parts(self, a: str, b: str, margins: Mapping[str, float], rule: str
                 ) -> tuple[list[inf.Part], dict[str, Any], str | None]:
        label = f"({rule})"
        parts, nums = [], {}
        for ep, m in margins.items():
            d = paired_diff(self.c[a], self.c[b], ep)
            need = self.r.n_required[ENDPOINT_GETTERS[ep][0]]
            nums[ep] = {"n": int(d["diff"].size), "margin": m, "replicates": d["replicates"]}
            if d["diff"].size < need:
                return [], nums, f"{ep}: {d['diff'].size} paired replicates < {need}"
            tb = inf.t_bounds(d["diff"], self.r.alpha_for(rule))
            nums[ep]["t"] = tb.as_dict()
            parts.append(inf.Part(f"LB({a} - {b}) {ep} {label}", ">", m, "bound", tb.mean,
                                  tb.lb, tb.ub))
        return parts, nums, None

    def cost_part(self, large: str, small: str) -> tuple[inf.Part | None, dict[str, Any]]:
        cl, cs = self.c[large].decl.get("cost"), self.c[small].decl.get("cost")
        if not cl or not cs:
            return None, {"reason": "cost measurements missing"}
        cr = inf.cost_ratio_lb(cl["gpu_hours_per_unfolding"], cs["gpu_hours_per_unfolding"],
                               self.r.alpha_for("6.5"), cl.get("unfoldings_per_result", 1),
                               cs.get("unfoldings_per_result", 1),
                               cl.get("inference_gpu_hours", 0.0),
                               cs.get("inference_gpu_hours", 0.0))
        return inf.Part(f"LB cost_{large}/cost_{small}", ">=", COST_RATIO_MIN, "bound",
                        cr["ratio"], cr["lb"], None), cr

    def non_inferior(self, small: str, large: str, status: Mapping[str, str]) -> inf.Verdict:
        """Section 6.5: select `small` over `large` on cost."""
        parts, nums, why = self.lb_parts(small, large, NI_MARGINS, "6.5")
        if why:
            return inf.incomplete("6.5", why, nums)
        cp, cr = self.cost_part(large, small)
        nums["cost"] = cr
        if cp is None:
            return inf.incomplete("6.5", cr["reason"], nums)
        parts.append(cp)
        for name in (small, large):
            parts.append(inf.Part(f"{name} eligible (6.1-6.4)", ">=", 1, "point",
                                  1.0 if status[name] == "ELIGIBLE" else 0.0))
        return self.r.decide("6.5", parts, nums)

    def materially_better(self, a: str, b: str) -> inf.Verdict:
        margins = {"E0": 0.0, **{k: v for k, v in NI_MARGINS.items() if k != "E0"}}
        parts, nums, why = self.lb_parts(a, b, margins, "6.6.1")
        if why:
            return inf.incomplete("6.6.1", why, nums)
        return self.r.decide("6.6.1", parts, nums)

    def equivalent(self, a: str, b: str) -> inf.Verdict:
        p1, n1, w1 = self.lb_parts(a, b, NI_MARGINS, "6.6.3")
        p2, n2, w2 = self.lb_parts(b, a, NI_MARGINS, "6.6.3")
        if w1 or w2:
            return inf.incomplete("6.6.3", w1 or w2, {"ab": n1, "ba": n2})
        return self.r.decide("6.6.3", p1 + p2, {f"{a}-{b}": n1, f"{b}-{a}": n2})


def total_cost(c: Candidate) -> float | None:
    cost = c.decl.get("cost")
    if not cost:
        return None
    return (cost.get("unfoldings_per_result", 1) * float(np.mean(cost["gpu_hours_per_unfolding"]))
            + cost.get("inference_gpu_hours", 0.0))


def rank(rules: Rules, cands: Mapping[str, Candidate], status: Mapping[str, str]
         ) -> dict[str, Any]:
    """Section 6.6 among ELIGIBLE candidates of the decision set."""
    decision = [n for n in rules.ev["decision_set"]]
    eligible = [n for n in decision if status[n] == "ELIGIBLE"]
    pending = [n for n in decision if status[n] in ("INCOMPLETE", "CONTINUE")]
    out: dict[str, Any] = {"eligible": eligible, "pending_not_eligible": pending,
                           "provisional": bool(pending)}
    if not eligible:
        out["outcome"] = ("NO_ELIGIBLE_DESIGN" if not pending else
                          "NO_ELIGIBLE_DESIGN_YET (candidates pending: " + ", ".join(pending) + ")")
        return out
    con = Contrasts(rules, cands)
    mean_e0 = {n: float(np.nanmean([x for x in cands[n].values(E0_CASE, g_hist("eavail")).values()
                                    if x is not None])) for n in eligible}
    order = sorted(eligible, key=lambda n: -mean_e0[n])
    leader = order[0]
    out.update({"mean_R_E0": mean_e0, "order_by_mean_R_E0": order, "leader": leader,
                "pairs": {}})
    if len(eligible) == 1:
        out.update({"outcome": "SELECTED", "selected": leader, "by": "6.6.1 (only eligible)"})
        return out
    better, equiv, unresolved, cont = [], [], [], []
    for other in order[1:]:
        mb = con.materially_better(leader, other)
        pair = {"materially_better": mb.as_dict()}
        if mb.verdict == inf.PASS:
            better.append(other)
        else:
            eq = con.equivalent(leader, other)
            pair["equivalent"] = eq.as_dict()
            if eq.verdict == inf.PASS:
                equiv.append(other)
            elif inf.CONTINUE in (mb.verdict, eq.verdict):
                cont.append(other)
            else:
                unresolved.append(other)
        out["pairs"][f"{leader} vs {other}"] = pair
    # 6.6.2: a smaller (cheaper) package on cost only under 6.5, against the leader
    ni = {}
    for other in order[1:]:
        tl, to = total_cost(cands[leader]), total_cost(cands[other])
        if tl is not None and to is not None and to < tl:
            v = con.non_inferior(other, leader, status)
            ni[other] = v.as_dict()
    out["non_inferiority_6.5"] = ni
    cheaper_ok = [o for o, v in ni.items() if v["verdict"] == inf.PASS]
    cont += [f"6.5 {o} vs {leader}" for o, v in ni.items() if v["verdict"] == inf.CONTINUE]
    if cont:
        out.update({"outcome": "CONTINUE", "by": "section 8 (look 2 needed)",
                    "straddling_pairs": cont})
        return out
    if unresolved:
        out.update({"outcome": "UNRESOLVED", "by": "6.6.4",
                    "discriminating_contrasts": [f"{leader} vs {o}" for o in unresolved]})
        return out
    if cheaper_ok:
        pick = max(cheaper_ok, key=lambda n: mean_e0[n])
        out.update({"outcome": "SELECTED", "selected": pick,
                    "by": f"6.6.2 (smaller package, 6.5 non-inferior to {leader})"})
        return out
    if not equiv:
        out.update({"outcome": "SELECTED", "selected": leader, "by": "6.6.1 (materially better)"})
        return out
    # 6.6.3: equivalent set, saving < 2x -> tie-break: N2 sd, coverage width, cost
    tied = [leader] + equiv
    key = {}
    for n in tied:
        c = cands[n]
        n2 = rules.N2(c).numbers.get("pooled_within_draw_sd", math.inf)
        cov = (c.coverage or {}).get("dev_eavail") or {}
        width = (np.mean(cov["levels"]["0.95"]["per_bin_mean_half_width"])
                 if cov else math.inf)
        key[n] = (n2, float(width), total_cost(c) or math.inf)
    pick = min(tied, key=lambda n: key[n])
    out.update({"outcome": "EQUIVALENT_TIE_BROKEN", "selected": pick, "by": "6.6.3",
                "equivalent_set": tied,
                "tie_break_keys (N2 sd, mean 95% half-width, cost)": key})
    return out


def switching_report(rules: Rules, cands: Mapping[str, Candidate], ref: str) -> dict[str, Any]:
    """Section 6.5 last sentence: the historical +0.04 switching margin over CTL, reported."""
    out = {}
    for n in rules.ev["decision_set"]:
        d = paired_diff(cands[n], cands[ref], "E0")
        if d["diff"].size >= 2:
            tb = inf.t_bounds(d["diff"], rules.alpha_for("6.6.1"))
            out[n] = {"t": tb.as_dict(), "switching_margin": rules.floors["switching"],
                      "lb_exceeds_switching": bool(tb.lb > rules.floors["switching"])}
    return out


def evaluate(ev: Mapping[str, Any], floors: Mapping[str, Any] | None = None) -> dict[str, Any]:
    floors = floors or historical_floors()
    rules = Rules(ev, floors)
    for case in rules.library():
        classify_case(case)                         # refuses an unknown case id
    cands = {n: Candidate(n, d) for n, d in ev["candidates"].items()}
    missing = [n for n in ev["decision_set"] if n not in cands]
    if missing:
        raise ValueError(f"decision-set members without evidence: {missing}")
    elig = {n: rules.eligibility(cands[n]) for n in ev["decision_set"]}
    prev = ev.get("previous")
    if prev:                                         # section 8: resolved look-1 verdicts stay
        before = json.loads(Path(prev).read_text())["eligibility"]
        for n, e in elig.items():
            for rule, v in before.get(n, {}).get("verdicts", {}).items():
                if v["verdict"] in (inf.PASS, inf.FAIL):
                    e["verdicts"][rule] = {**v, "carried_from_look": 1}
            vs = [v["verdict"] for v in e["verdicts"].values()]
            e["status"] = ("INELIGIBLE" if inf.FAIL in vs else "INCOMPLETE"
                           if inf.INCOMPLETE in vs else "CONTINUE" if inf.CONTINUE in vs
                           else "ELIGIBLE")
    status = {n: e["status"] for n, e in elig.items()}
    res = {"schema": "pet-final-design/decision/1", "stage": ev.get("stage"),
           "look": rules.look, "looks_planned": rules.looks, "bonferroni_m": rules.m,
           "alpha_one_sided_per_bound": {"sequential_rules": rules.alpha,
                                         "fixed_rules": rules.alpha_fixed},
           "sequential_rules": sorted(rules.sequential), "n_required": rules.n_required,
           "n_final": rules.n_final,
           "n_stress": rules.n_stress, "floors": floors, "eligibility": elig,
           "ranking": rank(rules, cands, status)}
    if ev.get("reference") and ev["reference"] in cands:
        res["switching_vs_reference"] = switching_report(rules, cands, ev["reference"])
    return inf.jsonable(res)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    res = evaluate(json.loads(a.evidence.read_text()))
    a.out.write_text(json.dumps(res, indent=1, allow_nan=False) + "\n")
    for n, e in res["eligibility"].items():
        print(f"{n}: {e['status']}  failed={e['failed']} incomplete={e['incomplete']} "
              f"continue={e['continue']}")
    print(f"ranking: {res['ranking'].get('outcome')} {res['ranking'].get('selected', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
