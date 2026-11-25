#!/usr/bin/env python3
"""Tie the paper's Sec. IV printed values, and the note values moved from it, to their committed receipts (PRD release
audit ea939701, G11).

Each check finds one printed value in the note's values.tex, sec3_twod.tex, appC_supplementary.tex, sec_validation.tex,
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
estimator's lowest 68% coverage under the rate reduction (s5c tier S) in sec:coverage-5d (appA_methods.tex); the
withheld-shape range and its "about half of the cells" in the primer (primer_body.tex).

  python3 check_sec4_receipts.py              # exit 0 only if every check passes
  python3 check_sec4_receipts.py --self-test  # each printed value perturbed by one unit must be rejected

The receipts live in the canonical repository (docs/orchestration/state/). In the canonical layout
(<repo>/docs/analysis-note/) a missing receipts directory is a FAILURE. Anywhere else (the standalone note repository,
where this file sits at the repository root) the check reports SKIP and exits 0; the canonical build enforces it.
"""
from __future__ import annotations

import gzip
import hashlib
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


def regen_a2_ratios() -> dict:
    """A2 (#1323): the 1D projection ratios ours/published on the paper's pT edges, compare_to_models.project()."""
    r = receipt("ibu-chi2-20261123/regenA2/out/e_projratio.json")
    assert r["n_reported"] == 205 and len(r["ratios"]["pt"]) == 14 and len(r["ratios"]["pz"]) == 16, "A2 shape changed"
    return r["ratios"]


def regen_a2_edge_ratios():  # the four edge bins sec3_twod.tex:11 names: lowest and highest pT, two highest p_par
    r = regen_a2_ratios()
    return r["pt"][0], r["pt"][-1], r["pz"][-2], r["pz"][-1]


def regen_a2_max_dev_pct() -> float:
    """Largest |ratio - 1| in percent over every projection bin except those four, computed from the bins (the stored
    max_abs_dev_other_bins is only cross-checked)."""
    r = regen_a2_ratios()
    other = r["pt"][1:-1] + r["pz"][:-2]
    dev = 100.0 * max(abs(x - 1.0) for x in other)
    stored = 100.0 * receipt("ibu-chi2-20261123/regenA2/out/e_projratio.json")["literals"]["max_abs_dev_other_bins"]
    assert abs(dev - stored) < 1e-9, f"computed {dev} != stored {stored}"
    return dev


def pt_edges() -> tuple[list[float], list[float]]:
    """(published, ours) muon pT bin edges in GeV/c. Published: the release's pt_pl_cross_section TH2D axis, as read
    in ibu-chi2-20261123/edges/root_axis.out (release sha256 6c6dce72...). Ours: MINERvA101's util/Binning.h."""
    txt = (STATE / "ibu-chi2-20261123/edges/root_axis.out").read_text()
    m = re.findall(r"(?m)^Y p_\{t\} \(GeV/c\) \[([0-9., ]+)\]$", txt)
    if len(m) != 1 or "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3" not in txt:
        raise ValueError("edges/root_axis.out: the release's pT axis (sha 6c6dce72...) not found exactly once")
    published = [float(x) for x in m[0].split(",")]
    h = (HERE.parents[1] / "MINERvA101/MINERvA-101-Cross-Section/util/Binning.h").read_text()
    o = re.findall(r"ptmu_bins = \{([0-9., \n]+)\};", h)
    if len(o) != 1:
        raise ValueError("Binning.h: ptmu_bins not found exactly once")
    ours = [float(x) for x in o[0].replace("\n", " ").split(",")]
    if len(published) != 15 or len(ours) != 15:
        raise ValueError("expected 14 pT bins on both grids")
    return published, ours


def pt_edges_that_differ() -> tuple[list[float], list[float]]:
    published, ours = pt_edges()
    i = [k for k in range(15) if abs(published[k] - ours[k]) > 1e-12]
    return [published[k] for k in i], [ours[k] for k in i]


def pt_edges_printed_exact(printed_ours: str, printed_published: str, printed_step: str) -> tuple[bool, str]:
    """sec3_twod.tex:11 prints our three differing pT edges, the published three and their difference. All must match
    the records exactly, and each pair must differ by exactly the printed step in decimal arithmetic (not float)."""
    from decimal import Decimal
    published, ours = pt_edges_that_differ()
    want_p = [Decimal(repr(x)) for x in published]
    want_o = [Decimal(repr(x)) for x in ours]
    got_o = [Decimal(x) for x in printed_ours]
    got_p = [Decimal(x) for x in printed_published]
    step = Decimal(printed_step)
    ok = (got_o == want_o and got_p == want_p and all(abs(p - o) == step for p, o in zip(want_p, want_o)))
    return ok, f"printed ours {printed_ours}, published {printed_published}, step {printed_step} | records ours {ours}, published {published}"


EDGE_SENTENCE = (r"Three of our \$p_T\$ edges \(([0-9.]+), ([0-9.]+) and \\SI\{([0-9.]+)\}\{GeV/c\}\) differ by "
                 r"\\SI\{([0-9.]+)\}\{GeV/c\} from the published ([0-9.]+), ([0-9.]+) and ([0-9.]+)\.")
EDGE_STEP_APPC = r"with three interior \$p_T\$ edges \\SI\{([0-9.]+)\}\{GeV/c\} from the published ones"


# (label, source file, regex with one or two captured printed values, computed value(s), mode)
CHECKS = [
    # One printed 1.04 stands for both pT edge bins, so it is bound twice: once to each bin.
    ("projection ratio, lowest pT bin, and the two highest p_par bins (regenA2)", "sec3_twod.tex",
     r"the ratio is ([0-9.]+) in both the lowest and the highest \$p_T\$ bins, and ([0-9.]+) and ([0-9.]+) in the two "
     r"highest \$p_\\parallel\$ bins", lambda: tuple(regen_a2_edge_ratios()[i] for i in (0, 2, 3)), "round"),
    ("projection ratio, highest pT bin (regenA2)", "sec3_twod.tex",
     r"the ratio is ([0-9.]+) in both the lowest and the highest \$p_T\$ bins", lambda: regen_a2_edge_ratios()[1],
     "round"),
    ("projection ratios elsewhere, the bound (regenA2)", "sec3_twod.tex",
     r"agree with the published result to within \$([0-9.]+)\\%\$, except at the edges of the phase space",
     regen_a2_max_dev_pct, "below"),
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
    # appC's IBU bias sentence (Joseph's wording, 2026-11-25), bound to IBUB's committed readouts at both held-out tunes
    ("IBUB IBU median absolute bias, range over the tunes and K = 5, 10", "appC_supplementary.tex",
     r"its median absolute bias is ([0-9.]+)--([0-9.]+)\\%, against", lambda: ibub_median_range("IBU"), "round"),
    ("IBUB OmniFold median absolute bias, range over the tunes", "appC_supplementary.tex",
     r"against ([0-9.]+)--([0-9.]+)\\% for OmniFold", lambda: ibub_median_range("OF"), "round"),
    ("IBUB cells where IBU's bias is smaller, range, of the reported cells", "appC_supplementary.tex",
     r"it is smaller in ([0-9]+)--([0-9]+) of the ([0-9]+) cells", lambda: ibub_smaller_cells(), "round"),
    ("IBUB pseudo-experiments (C-COMPLETE units, both tunes)", "appC_supplementary.tex",
     r"over the same ([0-9]+) pseudo-experiments", lambda: ibub_units(), "round"),
    ("A5 ten smallest-lambda modes' share, appC:7", "appC_supplementary.tex",
     r"The ten smallest-eigenvalue modes carry \$([0-9.]+)\\%\$ of the distance", lambda: 100 * regen_a45("5")["share10_smallest"],
     "round"),
    ("A5 ten smallest-lambda modes' share, records_r03:18", "records_r03_twod.tex",
     r"The 10 smallest-\$\\lambda\$ modes carry \\SI\{([0-9.]+)\}\{\\percent\}", lambda: 100 * regen_a45("5")["share10_smallest"],
     "round"),
    ("A5 largest standardized component and the next nine, records_r03:18", "records_r03_twod.tex",
     r"The largest mode has a paper-covariance-standardized component of magnitude \$([0-9.]+)\$, and the next nine "
     r"\$([0-9.]+)\$--\$([0-9.]+)\$",
     lambda: (regen_a45("5")["largest_abs_z"], min(regen_a45("5")["next_nine_abs_z"]), max(regen_a45("5")["next_nine_abs_z"])),
     "round"),
    ("chi2/ndf vs published on the published pT edges, \\chiPaper (regenA E P1a)", "values.tex",
     r"\\newcommand\{\\chiPaper\}\{([0-9.]+)\}",
     lambda: regen_a_number("out/e_P1a_chi2_paperonly.log", r"PAPER \(stat\+syst\)\s+chi2 =\s*([0-9.]+)\s+ndf = 205") / 205,
     "round"),
    ("chi2/ndf vs published on OUR pT edges, \\chiPaperOurEdges (regenA OLD P1a)", "values.tex",
     r"\\newcommand\{\\chiPaperOurEdges\}\{([0-9.]+)\}",
     lambda: regen_a_number("out/old_P1a_chi2_paperonly.log", r"PAPER \(stat\+syst\)\s+chi2 =\s*([0-9.]+)\s+ndf = 205") / 205,
     "round"),
    # appA_methods.tex:74's Q_R direct-inverse distance: G2R run 2's ours-only step oo_Q (re2c_run.sh; spec row oo-q).
    # It stays on our pT edges (KNOWN_ISSUES 103), next to \\chiPaperOurEdges. The RE-2 spec row oo-q
    # (2d-unfolding/re2/partc/re2c_values_spec.tsv) still cites N/app_statmethods.tex:782 with 23.23, on purpose: the
    # spec is the frozen input of the bound run and describes the note at its deploy, 903fb78b (test_re2c.py checks it
    # there, #1325). The sentence prints here now, and this row is the live binding.
    ("Q_R direct-inverse distance per bin vs the published central value (G2R run 2, oo-q)", "appA_methods.tex",
     r"The direct inverse of \$Q_R\$ gives a quadratic distance of ([0-9.]+) per reported bin",
     lambda: float(re.search(r"\[universe-only\] direct inverse: chi\^2 = [0-9.]+,\s+ndf = 205,\s+chi\^2/ndf = ([0-9.]+)",
                             (STATE / "measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes/run2/g2r/chi2/"
                              "ours_only_Q.txt").read_text()).group(1)), "round"),
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
    ("regularization bias at high W (VL151)", "appC_supplementary.tex",
     r"reaches \$([0-9.]+)\\%\$ in the highest-\$W\$ column", regularization_max, "round"),
    ("an earlier estimator's 68% coverage under the rate reduction (s5c tier S)", "appA_methods.tex",
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
    m = re.findall(EDGE_SENTENCE, text("sec3_twod.tex", sources))
    if len(m) != 1:
        rows.append(("pT edges, ours vs published (edges/root_axis.out, Binning.h)", False,
                     f"edge sentence found {len(m)} times in sec3_twod.tex (expected 1)"))
    else:
        o1, o2, o3, step, p1, p2, p3 = m[0]
        good, info = pt_edges_printed_exact([o1, o2, o3], [p1, p2, p3], step)
        rows.append(("pT edges, ours vs published (edges/root_axis.out, Binning.h)", good, info))
        m2 = re.findall(EDGE_STEP_APPC, text("appC_supplementary.tex", sources))
        rows.append(("pT edge step in appC_supplementary.tex equals sec3's, exactly", len(m2) == 1 and m2[0] == step,
                     f"appendix C prints {m2} | sec3 step {step}"))
    rows += mode_split_claims(sources)
    rows += ibub_claims(sources)
    for label, src, pat, fn, lo, hi in VERBAL:
        found = len(re.findall(pat, text(src, sources))) == 1
        c = fn()
        rows.append((label, found and lo <= c <= hi, f"phrase found={found} | receipt {c:.3f} in [{lo}, {hi}]"))
    return rows


def regen_a45(which: str) -> dict:
    """regenA A4's or A5's readout on the published pT edges (#1329, #1330)."""
    return json.loads((STATE / f"ibu-chi2-20261123/regenA{which}/out/readout_e.json").read_text())


NUM_WORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
ORDINAL = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}
# The eigenmode sentences on the published pT edges (Joseph's wording, 2026-11-25), bound to A4 and A5
MODE_CAPTION = (r"(\w+) of the six published-covariance eigenvectors with the largest contributions to the descriptive "
                r"\$\\chi\^2\$, in panels (\([a-f]\)(?:--\([a-f]\))?(?:(?:, | and )\([a-f]\)(?:--\([a-f]\))?)*), concentrate "
                r"at the highest")
MODE_APPC7 = (r"The ten smallest-eigenvalue modes carry \$([0-9.]+)\\%\$ of the distance\. Among the six largest contributors, "
              r"(\w+) are concentrated in the highest-\$p_\\parallel\$ bins and have "
              r"\$\\lambda_k/\\lambda_\{\\max\}\\lesssim10\^\{(-\d+)\}\$, while the (\w+) lies at lower \$p_\\parallel\$ "
              r"and has a relative eigenvalue of \$(\d)\\times10\^\{(-\d+)\}\$")
MODE_REC18 = (r"Of the five largest contributors, (\w+) lies? in the smallest-\$\\lambda\$ tenth of the spectrum\. Of the six "
              r"leading modes, the (\w+) in the highest-\$\\pPar\$ bins are all poorly determined directions "
              r"\(\$\\lambda/\\lambda_\{\\max\}\\lesssim10\^\{(-\d+)\}\$\)\. The (\w+) is a moderate-\$\\lambda\$ mode "
              r"\(\$\\lambda/\\lambda_\{\\max\}\\approx(\d)\\times10\^\{(-\d+)\}\$\)")


def panel_letters(spec: str) -> list[str]:
    out = []
    for a, b in re.findall(r"\(([a-f])\)(?:--\(([a-f])\))?", spec):
        out += [chr(c) for c in range(ord(a), ord(b or a) + 1)]
    return out


def mode_split_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    """Fig. 14's caption, appC:7 and records_r03_twod.tex:18 against A4/A5: count words, panel letters, the decade bound on
    the high-p_par modes' lambda/lambda_max (true, and no looser than one decade), and the other mode's value at 1 s.f."""
    a4, a5 = regen_a45("4"), regen_a45("5")
    high, low = a5["six_split"]["high_pz"], a5["six_split"]["lower_pz"]
    lam = [m["lam_rel"] for m in sorted(a5["modes"], key=lambda m: m["rank"])]
    high_letters = [chr(ord("a") + i) for i in high]
    hmax = max(lam[i] for i in high)
    other = f"{lam[low[0]]:.0e}" if len(low) == 1 else None

    def decade(e: str) -> bool:
        return 10.0 ** (int(e) - 1) < hmax <= 10.0 ** int(e)

    def rest(word: str) -> bool:  # "the sixth" names the one remaining mode
        return len(low) == 1 and word == ORDINAL[len(high) + 1]

    rows = []
    m = re.findall(MODE_CAPTION, text("appC_supplementary.tex", sources))
    lab = "A5/A4 Fig. 14 caption: count and panels at the highest p_par"
    if len(m) != 1:
        rows.append((lab, False, f"caption found {len(m)} times (expected 1)"))
    else:
        word, spec = m[0][0], m[0][1]
        letters = panel_letters(spec)
        good = (NUM_WORD.get(word.lower()) == len(letters) and letters == a4["modes_share_gt_half"] == high_letters)
        rows.append((lab, good, f"printed {word} {letters} | A4 {a4['modes_share_gt_half']} A5 {high_letters}"))
    m = re.findall(MODE_APPC7, text("appC_supplementary.tex", sources))
    lab = "A5 appC:7: count, decade bound, the other mode"
    if len(m) != 1:
        rows.append((lab, False, f"sentence found {len(m)} times (expected 1)"))
    else:
        _, word, e1, rword, c, e2 = m[0]
        good = NUM_WORD.get(word) == len(high) and decade(e1) and rest(rword) and other == f"{c}e{int(e2):+03d}"
        rows.append((lab, good, f"printed {word}, <~1e{e1}, the {rword} {c}e{e2} | A5 {len(high)} high, max {hmax:.3g}, other {other}"))
    m = re.findall(MODE_REC18, text("records_r03_twod.tex", sources))
    lab = "A5 records_r03:18: top five in the smallest tenth, count, decade bound, the other mode"
    if len(m) != 1:
        rows.append((lab, False, f"sentence found {len(m)} times (expected 1)"))
    else:
        tword, word, e1, rword, c, e2 = m[0]
        good = (NUM_WORD.get(tword) == a5["top5_in_smallest_tenth"] and NUM_WORD.get(word) == len(high) and decade(e1)
                and rest(rword.lower()) and other == f"{c}e{int(e2):+03d}")
        rows.append((lab, good, f"printed {tword}/{word}, <~1e{e1}, the {rword} {c}e{e2} | A5 top5 "
                                f"{a5['top5_in_smallest_tenth']}, {len(high)} high, max {hmax:.3g}, other {other}"))
    return rows


IBUB_DIR = "measurement-paper/5d-community-20261024/fd/receipts-ibub/connect/readout-20261125"
IBUB_TUNES = ("G18", "AR23")
IBUB_OVERRIDE: dict | None = None  # the self-test's planted readouts


def ibub_verified(tune: str) -> dict:
    """IBUB's committed readout at one held-out tune, refused unless its sha256 is the one RECORDS.SHA256SUMS.txt holds."""
    d = STATE / IBUB_DIR
    raw = (d / tune / f"ibub_{tune}.json").read_bytes()
    want = [ln.split()[0] for ln in (d / "RECORDS.SHA256SUMS.txt").read_text().splitlines()
            if ln.split()[1:] == [f"out-{tune}/ibub_{tune}.json"]]  # the fetch recorded it under out-<tune>/
    if len(want) != 1 or hashlib.sha256(raw).hexdigest() != want[0]:
        raise ValueError(f"IBUB readout {tune} is not the recorded file")
    return json.loads(raw)


def ibub() -> dict:
    return IBUB_OVERRIDE if IBUB_OVERRIDE is not None else {t: ibub_verified(t) for t in IBUB_TUNES}


def ibub_summaries() -> list[dict]:
    return [r["readings"][k]["summary"] for r in ibub().values() for k in ("K5", "K10")]


def ibub_one(values: list) -> float:
    """A value every readout must share (the unit count, the cell count): refuse if they differ."""
    if len(set(values)) != 1:
        raise ValueError(f"IBUB readouts disagree: {values}")
    return float(values[0])


def ibub_units() -> float:
    rs = ibub().values()
    if any(r["C-COMPLETE"]["missing"] for r in rs):
        raise ValueError("an IBUB readout has missing units")
    return ibub_one([r["C-COMPLETE"]["units"] for r in rs])


def ibub_cells() -> float:
    return ibub_one([sum(lab.startswith("cell:") for lab in r["readings"][k]["labels"])
                     for r in ibub().values() for k in ("K5", "K10")])


def ibub_median_range(method: str) -> tuple[float, float]:
    x = [s[method]["median_abs_rel_pct"] for s in ibub_summaries()]
    return min(x), max(x)


def ibub_smaller_cells() -> tuple[float, float, float]:
    x = [s["cells_ibu_smaller_abs_bias"] for s in ibub_summaries()]
    return float(min(x)), float(max(x)), ibub_cells()


ITER_WORD = {"five": "K5", "ten": "K10"}
IBUB_SENTENCE = (r"At (\w+) held-out GENIE v3 tunes, the method bias of binned IBU at (\w+) and (\w+) iterations (\w+ \w+) "
                 r"from that of the refined OmniFold estimator over the same [0-9]+ pseudo-experiments\. IBU's bias is "
                 r"somewhat (\w+) on average:")


def ibub_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    """appC's IBUB sentence (Joseph's wording, 2026-11-25): "both" tunes are the readouts' truths, "five and ten" their
    iterations, "differs significantly" is reading == DIFFER at each, and "smaller on average" is IBU's median absolute
    bias below OmniFold's at each tune and iteration count."""
    lab = "IBUB appC: tunes, iterations, DIFFER at each, IBU's median below OmniFold's"
    m = re.findall(IBUB_SENTENCE, text("appC_supplementary.tex", sources))
    if len(m) != 1:
        return [(lab, False, f"sentence found {len(m)} times (expected 1)")]
    both, w1, w2, verb, side = m[0]
    rs = ibub()
    ks = [ITER_WORD.get(w1), ITER_WORD.get(w2)]
    ok_tunes = both == "both" and sorted(rs) == sorted(IBUB_TUNES) and all(rs[t]["truth"] == t for t in rs)
    ok_k = ks == ["K5", "K10"] and all(sorted(r["readings"]) == ["K10", "K5"] for r in rs.values())
    readings = {(t, k): rs[t]["readings"][k]["reading"] for t in rs for k in ("K5", "K10")}
    ok_differ = verb == "differs significantly" and all(v == "DIFFER" for v in readings.values())
    below = [rs[t]["readings"][k]["summary"]["IBU"]["median_abs_rel_pct"] < rs[t]["readings"][k]["summary"]["OF"]["median_abs_rel_pct"]
             for t in rs for k in ("K5", "K10")]
    ok_side = side == "smaller" and all(below)
    ok_runs = all(r["verdict"] == "PASS" and not r["controls_failed"] and not r["stop"] for r in rs.values())
    return [(lab, ok_tunes and ok_k and ok_differ and ok_side and ok_runs,
             f"printed {both}/{w1},{w2}/{verb}/{side} | truths {sorted(rs)}, readings {sorted(set(readings.values()))}, "
             f"IBU median below OF {sum(below)}/{len(below)}, runs PASS {ok_runs}")]


def load() -> dict[str, str]:
    return {n: (HERE / n).read_text() for n in ("values.tex", "sec3_twod.tex", "sec_validation.tex",
                                               "sec_5d.tex", "app_devhistory.tex", "primer_body.tex", "appA_methods.tex",
                                               "appC_supplementary.tex", "records_r03_twod.tex")}


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
    # The pT-edge rows (not in CHECKS): each printed edge or step, changed, must be rejected.
    edge_labels = ("pT edges, ours vs published (edges/root_axis.out, Binning.h)",
                   "pT edge step in appC_supplementary.tex equals sec3's, exactly")
    for src, old_s, new_s, lab in (
            ("sec3_twod.tex", "(0.07, 0.33 and", "(0.08, 0.33 and", edge_labels[0]),
            ("sec3_twod.tex", "and \\SI{0.47}{GeV/c})", "and \\SI{0.48}{GeV/c})", edge_labels[0]),
            ("sec3_twod.tex", "the published 0.075, 0.325 and 0.475.", "the published 0.075, 0.325 and 0.48.", edge_labels[0]),
            ("sec3_twod.tex", "differ by \\SI{0.005}{GeV/c}", "differ by \\SI{0.006}{GeV/c}", edge_labels[0]),
            ("appC_supplementary.tex", "edges \\SI{0.005}{GeV/c} from", "edges \\SI{0.006}{GeV/c} from", edge_labels[1])):
        t = text(src, base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   edge mutation {old_s!r} in {src}"); ok = False; continue
        trial = dict(base)
        trial[src] = t.replace(old_s, new_s)
        if dict((r[0], r[1]) for r in evaluate(trial)).get(lab, True):
            print(f"  NOT CAUGHT  {lab}: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      {lab}: {old_s} -> {new_s}")
    # The eigenmode-split rows (not in CHECKS): each word, letter or exponent changed must be rejected.
    for src, old_s, new_s in (
            ("appC_supplementary.tex", "Five of the six published-covariance", "Four of the six published-covariance"),
            ("appC_supplementary.tex", "in panels (a) and (c)--(f), concentrate", "in panels (a) and (c)--(e), concentrate"),
            ("appC_supplementary.tex", "in panels (a) and (c)--(f), concentrate", "in panels (a), (b) and (d)--(f), concentrate"),
            ("appC_supplementary.tex", "contributors, five are concentrated", "contributors, four are concentrated"),
            ("appC_supplementary.tex", "\\lambda_{\\max}\\lesssim10^{-8}$, while", "\\lambda_{\\max}\\lesssim10^{-9}$, while"),
            ("appC_supplementary.tex", "\\lambda_{\\max}\\lesssim10^{-8}$, while", "\\lambda_{\\max}\\lesssim10^{-7}$, while"),
            ("appC_supplementary.tex", "while the sixth lies", "while the fifth lies"),
            ("appC_supplementary.tex", "eigenvalue of $6\\times10^{-5}$", "eigenvalue of $5\\times10^{-5}$"),
            ("records_r03_twod.tex", "contributors, one lies in", "contributors, two lie in"),
            ("records_r03_twod.tex", "modes, the five in the", "modes, the three in the"),
            ("records_r03_twod.tex", "\\lesssim10^{-8}$). The", "\\lesssim10^{-9}$). The"),
            ("records_r03_twod.tex", "The sixth is a moderate", "The fourth is a moderate"),
            ("records_r03_twod.tex", "\\approx6\\times10^{-5}$", "\\approx6\\times10^{-6}$")):
        t = text(src, base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   mode mutation {old_s!r} in {src}"); ok = False; continue
        trial = dict(base)
        trial[src] = t.replace(old_s, new_s)
        bad_rows = [r[0] for r in mode_split_claims(trial) if not r[1]]
        if not bad_rows:
            print(f"  NOT CAUGHT  mode split: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      mode split ({bad_rows[0][:24]}...): {old_s} -> {new_s}")
    # The IBUB sentence (not in CHECKS): each word changed, and each planted readout, must be rejected.
    global IBUB_OVERRIDE
    for old_s, new_s in (("At both held-out GENIE v3", "At one held-out GENIE v3"),
                         ("at five and ten iterations", "at five and twenty iterations"),
                         ("iterations differs significantly from", "iterations differs slightly from"),
                         ("somewhat smaller on average", "somewhat larger on average")):
        t = text("appC_supplementary.tex", base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   IBUB mutation {old_s!r}"); ok = False; continue
        trial = dict(base)
        trial["appC_supplementary.tex"] = t.replace(old_s, new_s)
        if ibub_claims(trial)[0][1]:
            print(f"  NOT CAUGHT  IBUB: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      IBUB: {old_s} -> {new_s}")
    import copy

    def plant(what, fn):
        global IBUB_OVERRIDE
        nonlocal ok, caught
        data = copy.deepcopy({t: ibub_verified(t) for t in IBUB_TUNES})
        fn(data)
        IBUB_OVERRIDE = data
        try:
            rows = dict((r[0], r[1]) for r in evaluate(base))
        except ValueError:
            rows = {"refused": False}
        finally:
            IBUB_OVERRIDE = None
        if all(rows.values()):
            print(f"  NOT CAUGHT  IBUB planted: {what}"); ok = False
        else:
            caught += 1; print(f"  caught      IBUB planted: {what}")
    plant("G18 K5 reading NOT RESOLVED APART", lambda d: d["G18"]["readings"]["K5"].__setitem__("reading", "NOT RESOLVED APART"))
    plant("AR23 K10 IBU median above OmniFold's",
          lambda d: d["AR23"]["readings"]["K10"]["summary"]["IBU"].__setitem__("median_abs_rel_pct", 0.9))
    plant("AR23 K5 IBU median 0.62 (range top moves)",
          lambda d: d["AR23"]["readings"]["K5"]["summary"]["IBU"].__setitem__("median_abs_rel_pct", 0.62))
    plant("G18 K10 smaller-cell count 118", lambda d: d["G18"]["readings"]["K10"]["summary"].__setitem__("cells_ibu_smaller_abs_bias", 118))
    plant("AR23 units 299", lambda d: d["AR23"]["C-COMPLETE"].__setitem__("units", 299))
    plant("AR23 one unit missing", lambda d: d["AR23"]["C-COMPLETE"].__setitem__("missing", ["u0007"]))
    plant("a tune's readout absent", lambda d: d.pop("AR23"))
    plant("G18 run verdict FAIL", lambda d: d["G18"].__setitem__("verdict", "FAIL"))
    import tempfile
    global STATE
    saved = STATE
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / IBUB_DIR
        (dst / "G18").mkdir(parents=True)
        (dst / "RECORDS.SHA256SUMS.txt").write_bytes((saved / IBUB_DIR / "RECORDS.SHA256SUMS.txt").read_bytes())
        (dst / "G18" / "ibub_G18.json").write_bytes((saved / IBUB_DIR / "G18" / "ibub_G18.json").read_bytes() + b" ")
        STATE = Path(tmp)
        try:
            ibub_verified("G18")
            print("  NOT CAUGHT  IBUB: a readout byte-changed from its recorded sha256 was read"); ok = False
        except ValueError:
            caught += 1; print("  caught      IBUB: a readout byte-changed from its recorded sha256 is refused")
        finally:
            STATE = saved
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
