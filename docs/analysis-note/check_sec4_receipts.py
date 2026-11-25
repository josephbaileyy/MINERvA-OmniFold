#!/usr/bin/env python3
"""Tie the paper's Sec. IV printed values, and the note values moved from it, to their committed receipts (PRD release
audit ea939701, G11).

Each check finds one printed value in the note's values.tex, sec3_twod.tex, sec4_higherdim.tex, sec_validation.tex,
sec_5d.tex or app_devhistory.tex, or in the primer's primer_body.tex, recomputes it
from the committed receipt that backs it, and compares at the printed precision: |computed - printed| <= half a unit in
the printed last digit ("round"), or printed - one unit <= computed < printed ("below", for "below X%": true, and tight
to one unit). "round-3dp-source" is "round" for a record that prints only 3 dp: the whole interval the record's value
stands for (+-0.0005) must round to the printed value, so a record on a rounding boundary fails instead of guessing. LaTeX comments are removed first, so a sentence kept only in a comment is not found. A value that cannot
be located, or a receipt key that is missing, is a failure. Release-reproducible values are checked by
publication/release/figs/fig_numbers.py instead; this covers the Sec. IV values the release cannot recompute.

Register round r18 (DECISION-20261025-joseph-r18-history-to-note.md item 1) moved the history of the two superseded
2D statistical bands out of the paper. Its bound values are now found where they print, in the note: the two-sigma
nominal of the earlier band's test in sec_validation.tex (erf(2/sqrt 2), as a fraction); the post hoc rescoring against
the rebuilt band, in sec_validation.tex until the deep restructure (DECISION-20261118) moved it verbatim to App. I's
app:devhistory-band in app_devhistory.tex (move rows CV-VA02..VA04; the same receipt, rescore_vl169_toys_vl170.json, as
fractions); and the earlier
band's C2 as \\covTwoDCTwo in values.tex (the macro the note prints; the paper's percent form is no longer printed).
The targeted round of 2026-11-03 moved the paper's background-closure paragraph (Sec. IV D) to the note, so its four
bound values (VL149, VL151, VL152) are now found in sec_5d.tex's sec:val-negweight, with the residual of the other
(E_avail, W) cells that the note now prints too.

The short paper (main_paper.tex, paper_body.tex) was retired on 2026-11-21 (docs/POST_PUBLICATION_REORG_PLAN.md, family
"short paper"). Its five values bind where they still print, from the same receipts: the statistical block median in
the note's Table tab:uq (sec3_twod.tex); the high-W regularization bias in sec:val-departure and the earlier
estimator's lowest 68% coverage under the rate reduction (s5c tier S) in sec:coverage-5d (both sec4_higherdim.tex); the
withheld-shape range and its "about half of the cells" in the primer (primer_body.tex).

  python3 check_sec4_receipts.py              # exit 0 only if every check passes
  python3 check_sec4_receipts.py --self-test  # each printed value perturbed by one unit must be rejected

The receipts live in the canonical repository (docs/orchestration/state/). In the canonical layout
(<repo>/docs/analysis-note/) a missing receipts directory is a FAILURE. Anywhere else (the standalone note repository,
where this file sits at the repository root) the check reports SKIP and exits 0; the canonical build enforces it.
"""
from __future__ import annotations

import gzip
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Only the canonical layout <repo>/docs/analysis-note/ has receipts at <repo>/docs/orchestration/state/, and there they
# are required. Anywhere else (the standalone note repository) there is nothing to check, and no unrelated directory may
# be picked up instead.
CANONICAL = HERE.name == "analysis-note" and HERE.parent.name == "docs"
STATE = HERE.parents[1] / "docs/orchestration/state" if CANONICAL else HERE / ".no-receipts-outside-the-canonical-layout"


def receipt(rel: str) -> dict:
    """A committed JSON receipt; a `.json.gz` one (the Stage F rebuild commits its budget gzipped) is read by suffix."""
    path = STATE / rel
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    return json.loads(path.read_text())


# Q_R, the refined 2D covariance adopted with E_R (DECISION-20261024-joseph-adopt-re2-2d-refined.md item 1): RE-2 part C's
# budget, committed gzipped (RE2-PARTC-REPORT.md sec. 3; gunzip -c gives bbe13622..., as partc-r2/SHA256SUMS lists).
# Repointed at integration as RE2-DECLARATION-C sec. 6.4 says; before, the Stage F rebuild's Q budget
# (2d-closeout/stageF/rebuild/outputs/outA/budget_Q.json.gz).
# G2R (DECISION-20261114-joseph-d1-g2r-adopted.md; the director's ruling of 2026-11-15, re-key every printed Q_R value):
# repointed to RE-2-shapes run 2 (C_new), merged at main d58d0d18 by #1167; its SHA256SUMS lists ./outA/budget_Q.json
# (gunzip of the committed .gz gives 7ed733c6...); g2r-integration/README.md. Before, RE-2 part C's budget:
# 2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/outA/budget_Q.json.gz.
BUDGET_Q = "measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes/run2/g2r/outA/budget_Q.json.gz"


def ev(name: str) -> bool:
    return bool(re.fullmatch(r"EW\d+", name))


def highest_w(name: str) -> bool:  # the W catch column of the 7 x 6 (E_avail, W) grid: EW5, EW11, ..., EW41
    return ev(name) and int(name[2:]) % 6 == 5


def stat_median():
    # Q_R's statistical block (S1, 300 replicas at seed 42, refined arm), RE-2 part C
    return receipt(BUDGET_Q)["stat"]["median_pct"]


def total_median():
    # Q_R = S5_R total + C_PL_R (adopted 2026-10-24, DECISION-20261024-joseph-adopt-re2-2d-refined.md)
    return receipt(BUDGET_Q)["Q"]["median_pct"]


def total_integral():
    # Q_R's width-weighted total sigma on the integrated cross section (same definition as Q's, J3 C2, DECISION-20261018)
    return receipt(BUDGET_Q)["Q"]["integral_sigma_pct"]


def rescore(key):
    return 100.0 * receipt("ki84-rebuild-20261006/rescore_vl169_toys_vl170.json")["vl170"][key]


def interim(key):
    return receipt("coverage-2d-20261005/interim_score.json")["result"][key]


def purity_bias_range():  # VL149: purity-method nominal-truth bias, the highest-W column without its corner cell EW41
    worst = receipt("s5c/d1/d1_summary.json")["groups"]["split_F2"]["worst"]
    v = [abs(c["mean_rel_pct"]) for c in worst if highest_w(c["name"]) and c["name"] != "EW41"]
    assert len(v) == 6, "the receipt's worst list no longer holds the six other highest-W cells"
    return min(v), max(v)


def tilt_coverage68_min():  # s5c tier S (OUTCOME-20260925-s5c-tier-s-futility-fail.md): the E_avail tilt's lowest 68% coverage
    return next(g for g in receipt("s5c/tier_s/interim_400.json")["grid"] if g["truth"] == "eavail_tilt")["coverage68_min"]


def dev():
    return receipt("s5n/stage1/dev_receipt.json")


def negweight_highw_range():  # VL151: negative-weight treatment, the highest-W column (its corner cell included)
    v = [abs(c["mean_rel_pct"]) for c in dev()["grid"]["C3_nominal"]["high_W"].values()]
    return min(v), max(v)


def negweight_other_ew_max():  # VL151: negative-weight treatment, the other (E_avail, W) cells
    d = dev()
    pf, names = d["grid"]["C3_nominal"]["per_functional"]["mean_rel"], d["functional_names"]
    return max(100.0 * abs(v) for v, n in zip(pf, names) if ev(n) and not highest_w(n))


def negweight_joint_max():  # VL151: largest residual over the joint (J) cells; per_functional.mean_rel is a fraction
    d = dev()
    pf, names = d["grid"]["C3_nominal"]["per_functional"]["mean_rel"], d["functional_names"]
    hw = d["grid"]["C3_nominal"]["high_W"]
    i = names.index("EW41")
    assert abs(100.0 * pf[i] - hw["EW41"]["mean_rel_pct"]) < 1e-9, "per_functional.mean_rel is not a fraction"
    return max(100.0 * abs(v) for v, n in zip(pf, names) if n.startswith("J"))


def data_method_diff():  # VL152: negweight minus purity on data
    return dev()["controls"]["C7"]["rel_diff_max_abs_pct"]


def regularization_max():  # VL151: GiBUU/GENIE E_avail shape, largest high-W departure
    return max(abs(v["mean_rel_pct"]) for v in dev()["grid"]["C4_eavail_shape"]["high_W"].values())


def shapes_range():  # VL154 A4: worst (E_avail, W) cell for each withheld shape, joint-test estimator
    pts = receipt("s5e/cand/assess_receipt.json")["points"]
    v = [pts[w]["ew_max_abs_pct"] for w in ("W1", "W2", "W3")]
    return min(v), max(v)


def half_of_cells():  # VL154 A4: cells whose model dependence is within the adopted sigma, of 42
    return receipt("s5e/cand/assess_receipt.json")["A4"]["n_useful_cells"] / 42.0


# Option (i) (Joseph, 2026-11-24): our 2D grid stays the analysis grid, and every comparison with the published result is
# made on the paper's pT edges (0.075/0.325/0.475). ibu-chi's regenA (PR #1322, merge 7c7a3cfb) regenerated those
# comparisons as records; READINGS.md maps each value to where the note prints it. The checks below bind the printed
# values to the regenA records of E (E_R on the paper's edges), so a later regeneration that moves one fails here.
REGEN_A = "ibu-chi2-20261123/regenA"


def regen_a_number(rel: str, pattern: str) -> float:
    """One number from a committed regenA text record: the pattern must match exactly once."""
    m = re.findall(pattern, (STATE / REGEN_A / rel).read_text())
    if len(m) != 1:
        raise ValueError(f"{REGEN_A}/{rel}: {pattern!r} matched {len(m)} times (expected 1)")
    return float(m[0])


def regen_a_pull(which: str) -> float:  # P1a: per-bin pull mean or RMS against the published TotalCovariance
    mean, rms = (regen_a_number("out/e_P1a_chi2_paperonly.log", r"pull mean / rms\s*:\s*([0-9.]+) / [0-9.]+"),
                 regen_a_number("out/e_P1a_chi2_paperonly.log", r"pull mean / rms\s*:\s*[0-9.]+ / ([0-9.]+)"))
    return {"mean": mean, "rms": rms}[which]


def regen_a_tension(pattern: str) -> float:  # P4: tension_report.txt (diagonal-only distance; norm/shape split)
    return regen_a_number("out/e/tension_report.txt", pattern)


def regen_a_windows() -> dict:  # P7: agreement_windows_receipt.py on E
    return receipt(f"{REGEN_A}/out/e/RECEIPT-agreement-windows.json")


def regen_a_median() -> float:
    """The median per-bin ratio at full precision. The P7 receipt stores it rounded to 4 dp, which sits on the 3-dp
    printing boundary (1.0075); receipts/median_fullprec.py recomputes it with the producer's definition and checks
    that its 4-dp rounding equals the stored value. Both are required here."""
    full = regen_a_number("receipts/median_fullprec.out", r"(?m)^e: median=([0-9.]+) ")
    stored = regen_a_windows()["results"]["median_bin_ratio"]
    if round(full, 4) != stored:
        raise ValueError(f"median_fullprec.out ({full}) does not round to the P7 receipt's {stored}")
    return full


def regen_a_within(pct: int) -> float:  # percent of the 205 reported bins within pct%, from the count (not the 1-dp %)
    w = regen_a_windows()["results"][f"within_{pct}_percent"]
    assert abs(100.0 * w["count"] / 205 - w["percent"]) < 0.05, "count and percent disagree in the P7 receipt"
    return 100.0 * w["count"] / 205


def regen_a_ratio_tot() -> float:  # P7: integral ratio ours/published over the reported cells (\ratioTot)
    return regen_a_windows()["headline_totals_oi130"]["values"]["ratio_integrals_reported"]


# (label, source file, regex with one or two captured printed values, computed value(s), mode)
CHECKS = [
    ("median per-bin ratio (regenA P7, paper's pT edges)", "values.tex",
     r"\\newcommand\{\\medianBinRatio\}\{([0-9.]+)\}", regen_a_median, "round"),
    ("bins within 5% (regenA P7)", "values.tex", r"\\newcommand\{\\binsFive\}\{([0-9.]+)\}",
     lambda: regen_a_within(5), "round"),
    ("bins within 10% (regenA P7)", "values.tex", r"\\newcommand\{\\binsTen\}\{([0-9.]+)\}",
     lambda: regen_a_within(10), "round"),
    ("bins within 20% (regenA P7)", "values.tex", r"\\newcommand\{\\binsTwenty\}\{([0-9.]+)\}",
     lambda: regen_a_within(20), "round"),
    ("integral ratio, reported cells (regenA P7)", "values.tex", r"\\newcommand\{\\ratioTot\}\{([0-9.]+)\}",
     regen_a_ratio_tot, "round"),
    ("pull mean vs published TotalCovariance (regenA P1a)", "values.tex",
     r"\\newcommand\{\\pullMean\}\{([0-9.]+)\}", lambda: regen_a_pull("mean"), "round"),
    ("pull RMS vs published TotalCovariance (regenA P1a)", "values.tex",
     r"\\newcommand\{\\pullRMS\}\{([0-9.]+)\}", lambda: regen_a_pull("rms"), "round"),
    ("pull RMS, prose rounding (regenA P1a)", "values.tex",
     r"\\newcommand\{\\pullRMSr\}\{([0-9.]+)\}", lambda: regen_a_pull("rms"), "round-3dp-source"),
    ("chi2/ndf vs published on OUR pT edges, \\chiPaperOurEdges (regenA OLD P1a)", "values.tex",
     r"\\newcommand\{\\chiPaperOurEdges\}\{([0-9.]+)\}",
     lambda: regen_a_number("out/old_P1a_chi2_paperonly.log", r"PAPER \(stat\+syst\)\s+chi2 =\s*([0-9.]+)\s+ndf = 205") / 205,
     "round"),
    ("diagonal-only distance per bin (regenA P4)", "sec3_twod.tex",
     r"gives a quadratic distance per bin of ([0-9.]+)\.",
     lambda: regen_a_tension(r"diagonal-only chi2/ndf =\s*([0-9.]+)"), "round"),
    ("tension split: chi2_norm (regenA P4)", "sec3_twod.tex", r"\$\\chi\^2_\{\\mathrm\{norm\}\}=([0-9.]+)\$",
     lambda: regen_a_tension(r"chi2_norm\s*=\s*([0-9.]+)"), "round"),
    ("tension split: chi2_shape (regenA P4)", "sec3_twod.tex",
     r"\$\\chi\^2_\{\\mathrm\{shape\}\}\\simeq([0-9.]+)\$",
     lambda: regen_a_tension(r"chi2_shape\s*=\s*([0-9.]+)"), "round"),
    ("total median uncertainty (Q_R)", "values.tex", r"\\newcommand\{\\uqMedian\}\{([0-9.]+)\}", total_median, "round"),
    ("total integral uncertainty (Q_R)", "values.tex", r"\\newcommand\{\\uqIntegral\}\{([0-9.]+)\}", total_integral, "round"),
    ("closure toys (VL169)", "values.tex", r"\\newcommand\{\\covTwoDNtoy\}\{([0-9.]+)\}", lambda: interim("n_toys"), "round"),
    ("first-built band, within 2 sigma (VL169; the note's \\covTwoDCTwo)", "values.tex",
     r"\\newcommand\{\\covTwoDCTwo\}\{([0-9.]+)\}", lambda: interim("C2"), "round"),
    ("first-built band, within 1 sigma (VL169)", "values.tex", r"\\newcommand\{\\covTwoDCOne\}\{([0-9.]+)\}",
     lambda: interim("C1"), "round"),
    ("two-sigma nominal of the earlier band's test (note sec:coverage)", "sec_validation.tex",
     r"lies entirely below its window \(Gaussian ([0-9.]+)\)", lambda: math.erf(2.0 / math.sqrt(2.0)), "round"),
    ("statistical block median (Q_R, S1)", "sec3_twod.tex", r"Statistical bootstrap & ([0-9.]+) &", stat_median, "round"),
    ("rescoring against the rebuilt (VL170) band, 2 and 1 sigma (note app:devhistory-band)", "app_devhistory.tex",
     r"removes the tail undercoverage: \$C_2=([0-9.]+)\$ \$\[[0-9.,]+\]\$ and \$C_1=([0-9.]+)\$",
     lambda: (rescore("C2") / 100.0, rescore("C1") / 100.0), "round"),
    # The background-closure values bind in the note since the targeted round (DECISION-20261103-joseph-retire-density-
    # gate.md item 3b) moved the paper's Sec. IV D closure paragraph there: sec_5d.tex sec:val-negweight prints them
    ("purity bias, highest-W cells (VL149)", "sec_5d.tex",
     r"return the highest-\$W\$ column of \$\(\\Eavail,W\)\$ \\SIrange\{([0-9.]+)\}\{([0-9.]+)\}\{\\percent\} low",
     purity_bias_range, "round"),
    ("negative-weight residual, highest-W cells (VL151)", "sec_5d.tex",
     r"brings the highest-\$W\$ column to \\SIrange\{([0-9.]+)\}\{([0-9.]+)\}\{\\percent\}", negweight_highw_range, "round"),
    ("negative-weight residual, other (E_avail, W) cells (VL151)", "sec_5d.tex",
     r"every other \$\(\\Eavail,W\)\$ cell to at most \\SI\{([0-9.]+)\}\{\\percent\}", negweight_other_ew_max, "round"),
    ("negative-weight residual, joint cells (VL151)", "sec_5d.tex",
     r"Some joint cells remain up to \\SI\{([0-9.]+)\}\{\\percent\} high", negweight_joint_max, "round"),
    ("treatments on data (VL152)", "sec_5d.tex", r"and at most \\SI\{([0-9.]+)\}\{\\percent\} over the reported functionals",
     data_method_diff, "round"),
    ("regularization bias at high W (VL151)", "sec4_higherdim.tex",
     r"reaches \$([0-9.]+)\\%\$ in the highest-\$W\$ column", regularization_max, "round"),
    ("an earlier estimator's 68% coverage under the rate reduction (s5c tier S)", "sec4_higherdim.tex",
     r"The lowest empirical coverage for the \$68\\%\$ intervals is ([0-9.]+)\.", tilt_coverage68_min, "round"),
    ("other fixed shapes, most affected cell (VL154)", "primer_body.tex",
     r"the effect is \\SIrange\{([0-9.]+)\}\{([0-9.]+)\}\{\\percent\} in the worst cell", shapes_range, "round"),
]
VERBAL = [("about half of those cells (VL154: 20 of 42)", "primer_body.tex",
           r"smaller than the quoted uncertainty in about half of the \$\(\\Eavail,W\)\$ cells", half_of_cells, 0.40, 0.60)]


def half_ulp(printed: str) -> float:
    return 0.5 * 10.0 ** -(len(printed.split(".")[1]) if "." in printed else 0)


def text(name: str, sources: dict[str, str]) -> str:
    """The source with LaTeX comments (an unescaped % to the end of the line) removed and whitespace collapsed."""
    return re.sub(r"\s+", " ", re.sub(r"(?<!\\)%[^\n]*", "", sources[name]))


def evaluate(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    rows = []
    for label, src, pat, fn, mode in CHECKS:
        m = re.findall(pat, text(src, sources))
        if len(m) != 1:
            rows.append((label, False, f"printed value found {len(m)} times in {src} (expected 1)"))
            continue
        printed = m[0] if isinstance(m[0], tuple) else (m[0],)
        comp = fn()
        comp = comp if isinstance(comp, tuple) else (comp,)
        if mode == "round":
            good = all(abs(c - float(p)) <= half_ulp(p) for c, p in zip(comp, printed))
        elif mode == "round-3dp-source":  # the record prints 3 dp: every value it can stand for must round to `printed`
            good = all(abs(c - float(p)) + 0.0005 <= half_ulp(p) + 1e-12 for c, p in zip(comp, printed))
        else:  # below: true, and no looser than one unit of the printed precision
            good = all(float(p) - 2 * half_ulp(p) <= c < float(p) for c, p in zip(comp, printed))
        rows.append((label, good, f"printed {'/'.join(printed)} | receipt {'/'.join(f'{c:.6g}' for c in comp)} | {mode}"))
    for label, src, pat, fn, lo, hi in VERBAL:
        found = len(re.findall(pat, text(src, sources))) == 1
        c = fn()
        rows.append((label, found and lo <= c <= hi, f"phrase found={found} | receipt {c:.3f} in [{lo}, {hi}]"))
    return rows


def load() -> dict[str, str]:
    return {n: (HERE / n).read_text() for n in ("values.tex", "sec3_twod.tex", "sec4_higherdim.tex", "sec_validation.tex",
                                               "sec_5d.tex", "app_devhistory.tex", "primer_body.tex")}


def gzip_self_test() -> bool:
    """receipt() reads a `.json.gz` by suffix: the same dict as its plain twin, and a missing one raises."""
    import tempfile
    global STATE
    saved = STATE
    payload = {"Q": {"median_pct": 6.4479}, "nested": [1, 2.5, "x"]}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            STATE = Path(tmp)
            (STATE / "r.json").write_text(json.dumps(payload))
            with gzip.open(STATE / "r.json.gz", "wt", encoding="utf-8") as fh:
                json.dump(payload, fh)
            same = receipt("r.json.gz") == receipt("r.json") == payload
            try:
                receipt("absent.json.gz")
                missing_fails = False
            except FileNotFoundError:
                missing_fails = True
    finally:
        STATE = saved
    print(f"  gzip receipt: {'PASS' if same and missing_fails else 'FAIL'} (equal to plain={same}, "
          f"missing raises={missing_fails})")
    return same and missing_fails


def self_test() -> int:
    """Every printed value, moved by one unit in its last digit in the direction that must fail, is rejected."""
    base = load()
    ok = all(g for _, g, _ in evaluate(base))
    caught = 0
    if not gzip_self_test():  # a reader check, reported on its own line, not counted as a perturbation
        ok = False
    for idx, (label, src, pat, fn, mode) in enumerate(CHECKS):
        s = text(src, base)
        m = re.search(pat, s)
        if m is None:  # nothing to perturb: the plain check already fails on this; say so instead of crashing
            print(f"  NOT FOUND   {label}: the printed value is not in {src}")
            ok = False
            continue
        for gi in range(1, (m.lastindex or 0) + 1):
            p = m.group(gi)
            step = 2 * half_ulp(p)
            # "round" fails one way at least; "below" must fail both ways (untrue, and looser than one unit)
            for sign in ((-1, +1) if mode == "below" else (+1,)):
                bad = p
                for k in (1, 2, 5, 10, 50):  # the smallest perturbation that leaves the tolerance
                    cand = float(p) + sign * k * step
                    bad = f"{cand:.{len(p.split('.')[1]) if '.' in p else 0}f}"
                    trial = dict(base)
                    trial[src] = s[:m.start(gi)] + bad + s[m.end(gi):]
                    if not dict((r[0], r[1]) for r in evaluate(trial))[label]:
                        break
                else:
                    print(f"  NOT CAUGHT  {label}: {p} -> {bad}")
                    ok = False
                    continue
                caught += 1
                print(f"  caught      {label}: {p} -> {bad}")
    trial = dict(base)
    trial["primer_body.tex"] = text("primer_body.tex", base).replace("in about half of the", "in about a third of the")
    if dict((r[0], r[1]) for r in evaluate(trial))[VERBAL[0][0]]:
        print("  NOT CAUGHT  verbal phrase removal"); ok = False
    else:
        caught += 1; print("  caught      verbal phrase changed")
    print(f"SELF-TEST :: {'PASS' if ok else 'FAIL'} ({caught} perturbations rejected)")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if not STATE.is_dir():
        if CANONICAL:
            print(f"SEC4-RECEIPTS :: FAIL -- the canonical layout has no receipts at {STATE}")
            return 1
        print(f"SEC4-RECEIPTS :: SKIP -- no receipts at {STATE} (standalone checkout); enforced by the canonical build")
        return 0
    if "--self-test" in argv:
        return self_test()
    rows = evaluate(load())
    for label, good, info in rows:
        print(f"  {'ok  ' if good else 'FAIL'} {label}: {info}")
    ok = all(g for _, g, _ in rows)
    print(f"SEC4-RECEIPTS :: {'PASS' if ok else 'FAIL'} ({sum(g for _, g, _ in rows)}/{len(rows)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
