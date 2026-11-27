#!/usr/bin/env python3
"""Tie the paper's Sec. IV printed values, and the note values moved from it, to their committed receipts (PRD release
audit ea939701, G11).

Each check finds one printed value in the note's values.tex, sec3_twod.tex, appC_supplementary.tex, sec_validation.tex,
sec_5d.tex, or in the primer's primer_body.tex, recomputes it
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
fractions), whose check was dropped on 2026-11-27 with that file, which no built document inputs (DECISION-20261127,
option (c)); and the earlier
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

import ast
import gzip
import hashlib
import json
import math
import re
import struct
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
# Every printed copy of the edge step: "$p_T$ edges", an optional parenthetical (sec3's edge list), an optional
# "differ by"/"shifted by", then the step. Pinned per file, so a reworded or dropped copy also fails.
EDGE_STEP_COPY = r"\$p_T\$ edges(?: \([^)]*\))?(?: differ by| shifted by)? \\SI\{([0-9.]+)\}\{GeV/c\}"
EDGE_STEP_COPIES = {"sec2_method.tex": 1, "sec3_twod.tex": 1, "appC_supplementary.tex": 2, "appD_reproducibility.tex": 1}
EDGE_STEP_ALL = "pT edge step, all 5 printed copies (sec2, sec3, appC x2, appD) equal sec3's, exactly"

# EVW5D (#1353, #1355): App. D's paragraph on the 5D per-event weights in the release (DECISION-20261125b sec. 3;
# C-COMPLETE option (a), DECISION-20261126). Every number and claim in it is bound to EVW5D attempt 2's receipts and to
# eavail step 0b (the denominator's tuples equal the saved rows' as multisets).
EVW5D = "measurement-paper/5d-community-20261024/fd/evw5d-20261125/receipts/attempt2"
EVW5D_OVERRIDE = None  # the self-test plants altered receipts here
# The sources of the two App. D claims Joseph worded on 2026-11-26: the truth selection (in_truth_phase_space and the
# edges nn_dump_inputs.py defaults to), the command that built the input npz, the record naming it, and fine_index's rule
EVW5D_CODE = {"u2d": "2d-unfolding/unfold_2d_omnifold_unbinned.py", "dump": "nd-unfolding/nn_dump_inputs.py",
              "sbatch": "nd-unfolding/sbatch_nn_dump_5d.sh",
              "inputs": "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-5B-INPUTS.md",
              "decl": "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/evw5d-20261125/EVW5D-DECLARATION.md"}


def evw5d() -> dict:
    """run.json, constants.json, step0b.json, and the lane's readings of constants.npz (c32.txt, c1effect.txt)."""
    if EVW5D_OVERRIDE is not None:
        return EVW5D_OVERRIDE
    lane = STATE / EVW5D / "lane"
    cells = re.findall(r"^\((\d+(?:, \d+){4})\) denom=\S+ ofin=\S+ diff=([+-][0-9.e+-]+) ", (lane / "c32.txt").read_text(),
                       re.M)
    c1 = re.findall(r"^f max rel change if c:=1 ([0-9.e+-]+) per cell", (lane / "c1effect.txt").read_text(), re.M)
    if len(c1) != 1:
        raise ValueError(f"{EVW5D}/lane/c1effect.txt: the c := 1 line matched {len(c1)} times (expected 1)")
    return {"run": receipt(f"{EVW5D}/post/evw5d/run.json"), "constants": receipt(f"{EVW5D}/post/evw5d/constants.json"),
            "step0b": receipt("eavail-switch-pricing-20261031/step0/step0b.json"),
            "cells": [(tuple(int(i) for i in idx.split(", ")), float(d)) for idx, d in cells], "c1": float(c1[0]),
            "code": {k: (HERE.parents[1] / v).read_text() for k, v in EVW5D_CODE.items()}}


def _edges_from_source(src: str) -> dict[str, list[float]]:
    """PT_EDGES and PZ_EDGES as unfold_2d_omnifold_unbinned.py assigns them (read with ast, not imported)."""
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], "id", "") in ("PT_EDGES", "PZ_EDGES"):
            out[node.targets[0].id] = [float(x) for x in ast.literal_eval(node.value)]
    return out


def evw5d_outside_axes(d: dict, sources: dict[str, str]) -> bool:
    """The rows outside the fine grid can be outside only on E_avail, q3 or W: every row passes the truth selection
    (C-FLOW), whose pT and p_par limits are inclusive (in_truth_phase_space) and are the default edges' ends, which are the
    grid's outer edges (constants.json); fine_index includes the last edge, and the four edges are exact in float32."""
    c, flow, code = d["constants"]["edges"], d["run"]["controls"]["C-FLOW"], d["code"]
    e = _edges_from_source(code["u2d"])
    ends = (c["pt"][0], c["pt"][-1], c["pz"][0], c["pz"][-1])
    return (flow["pass"] is True and flow["n_rows_equal_pass_truth"] is True
            and "if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):" in code["u2d"]
            and "pt_lo, pt_hi, pz_lo, pz_hi = pt_edges[0], pt_edges[-1], pz_edges[0], pz_edges[-1]" in code["dump"]
            and "--pt-edges" not in code["sbatch"] and "--pz-edges" not in code["sbatch"]
            and (e["PT_EDGES"][0], e["PT_EDGES"][-1], e["PZ_EDGES"][0], e["PZ_EDGES"][-1]) == ends
            and all(struct.unpack("f", struct.pack("f", x))[0] == x for x in ends)
            and "last edge inclusive" in code["decl"])


def evw5d_phase_space(d: dict, sources: dict[str, str]) -> bool:
    """The input npz (07fccc1a) was dumped without --full-phase-space, so the Sec. 2 truth phase space applies, theta_mu
    < 20 deg included, and Eq. (muon-fiducial) prints the grid's pT and p_par range."""
    code, c = d["code"], d["constants"]
    eq = (r"\theta_\mu<20^\circ,\quad 1.5<p_\parallel<\SI{60}{GeV/c},\quad p_T<\SI{4.5}{GeV/c} . \label{eq:muon-fiducial}"
          in text("sec2_method.tex", sources))
    return (c["input_npz_sha256"].startswith("07fccc1a")
            and "(`07fccc1a…`) was written by `nn_dump_inputs.py`" in code["inputs"]
            and "sbatch_nn_dump_5d.sh:13-15" in code["inputs"]
            and "nn_dump_inputs.py" in (cited := " ".join(code["sbatch"].splitlines()[12:15]))
            and "--axes eavail,q3,W --out of_inputs_5d.npz" in cited
            and "--full-phase-space" not in code["sbatch"]
            and "MAX_MUON_THETA_RAD = math.radians(20.0)" in code["u2d"]
            and "return math.atan2(pt, pz) < MAX_MUON_THETA_RAD" in code["u2d"]
            and eq and (c["edges"]["pz"][0], c["edges"]["pz"][-1], c["edges"]["pt"][-1]) == (1.5, 60.0, 4.5))


def evw5d_pairs() -> int:
    """C-COMPLETE's cells (lane/c32.txt) in pairs adjacent along one axis with equal and opposite ofin - denom. Raises
    unless there are as many cells as run.json counts and each is in exactly one such pair."""
    d = evw5d()
    cells = d["cells"]
    if len(cells) != d["run"]["controls"]["C-COMPLETE"]["n_cells_beyond_atol"]:
        raise ValueError(f"c32.txt lists {len(cells)} cells, run.json C-COMPLETE counts "
                         f"{d['run']['controls']['C-COMPLETE']['n_cells_beyond_atol']}")
    left, pairs = list(range(len(cells))), 0
    while left:
        i = left.pop(0)
        match = [j for j in left if cells[j][1] == -cells[i][1]
                 and sum(abs(a - b) for a, b in zip(cells[i][0], cells[j][0])) == 1]
        if len(match) != 1:
            raise ValueError(f"c32.txt cell {cells[i][0]} has {len(match)} adjacent equal-and-opposite partners")
        left.remove(match[0])
        pairs += 1
    return pairs


EVW5D_CLAIMS = (
    ("EVW5D: byte for byte (run.json C-BIND, controls PASS)",
     "The run that wrote the weights reproduced the reported cross section byte for byte.",
     lambda d, s: d["run"]["controls"]["C-BIND"]["pass"] is True and d["run"]["controls_verdict"] == "PASS"
     and d["run"]["controls"]["C-BIND"]["xsec_flat_bytes_equal"] is True),
    ("EVW5D: sixteen integrals from the rows to double-precision rounding (C-F, below 1e-14)",
     "Summed with the normalization, the weights reproduce the sixteen cell integrals to double-precision rounding.",
     lambda d, s: d["run"]["controls"]["C-F"]["pass"] is True and d["run"]["controls"]["C-F"]["f_from_rows_max_rel"] < 1e-14),
    ("EVW5D: completeness 1 in any binning (step0b tuple multisets equal; no unmatched fine cell)",
     "The completeness denominator is the deposited events themselves, so the completeness is 1 in any binning.",
     lambda d, s: d["step0b"]["c_tuple_multiset_equal"] is True
     and d["run"]["controls"]["C-COMPLETE"]["n_signal_without_denominator"] == 0
     and d["run"]["controls"]["C-COMPLETE"]["n_denominator_without_signal"] == 0),
    ("EVW5D: one integrated flux (constants.json, every pT bin's within 1e-15)",
     "The flux enters as a single integrated value.",
     lambda d, s: max(f := d["constants"]["flux_per_m2_per_POT_by_pt_bin"]) - min(f) <= 1e-15 * max(f)),
    ("EVW5D: the rows outside the grid are outside on E_avail, q3 or W only (the selection's limits are the grid's edges)",
     "lie outside the fine grid's $E_{\\mathrm{avail}}$, $q_3$ or $W$ range and enter no cell integral.", evw5d_outside_axes),
    ("EVW5D: the Sec. 2 truth phase space applies (input npz dumped without --full-phase-space)",
     "Readers can therefore choose any binning inside the truth phase space of Sec.~\\ref{sec:selection} "
     "[Eq.~\\eqref{eq:muon-fiducial}], within the fine grid's range.", evw5d_phase_space),
)


def evw5d_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    t, d = text("appD_reproducibility.tex", sources), evw5d()
    return [(lab, t.count(s) == 1 and fact(d, sources), f"sentence found {t.count(s)} time(s) | receipt {fact(d, sources)}")
            for lab, s, fact in EVW5D_CLAIMS]


# EVW2D (#1377, #1393): App. D's sentences on the 2D per-event weights (a PROPOSAL for Joseph, 2026-11-26). Every number
# and claim is bound to the run's receipts, the committed config and references it was bound to, and the records naming
# the two references: E_R (the adopted 2D refined result) and Tier 1's e (regenA's input on the published pT edges).
EVW2D = "2d-closeout/evw2d-20261124"
EVW2D_OVERRIDE = None  # the self-test plants altered receipts here
EVW2D_CODE = {"config": "2d-unfolding/evw2d/config.json",
              "decision": "docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md",
              "regenA": "docs/orchestration/state/ibu-chi2-20261123/regenA/README.md",
              "decl": "docs/orchestration/state/2d-closeout/evw2d-20261124/EVW2D-DECLARATION.md"}


def _npz_text(path: Path, name: str) -> str:
    """A 0-d unicode array of an .npz, read with zipfile and the .npy header (this checker does not import numpy)."""
    import zipfile
    with zipfile.ZipFile(path) as z:
        raw = z.read(f"{name}.npy")
    if raw[:6] != b"\x93NUMPY":
        raise ValueError(f"{path}:{name}.npy is not an .npy array")
    hl = struct.unpack("<H", raw[8:10])[0] if raw[6] == 1 else struct.unpack("<I", raw[8:12])[0]
    start = (10 if raw[6] == 1 else 12)
    header = ast.literal_eval(raw[start:start + hl].decode("latin1"))
    if not (header["descr"].startswith("<U") and header["shape"] == ()):
        raise ValueError(f"{path}:{name}.npy is not a 0-d little-endian unicode array: {header}")
    return raw[start + hl:].decode("utf-32-le").rstrip("\x00")


def evw2d() -> dict:
    """run.json and constants.json of the accepted run, the committed config and references.npz (its sha256 and meta),
    the deposit receipt, and the records naming the references."""
    if EVW2D_OVERRIDE is not None:
        return EVW2D_OVERRIDE
    out = f"{EVW2D}/receipts/run-20261126/post/out"
    ref = HERE.parents[1] / "2d-unfolding/evw2d/references.npz"
    return {"run": receipt(f"{out}/run.json"), "constants": receipt(f"{out}/constants.json"),
            "done": receipt(f"{out}/evw2d.done"),
            "deposit": (STATE / EVW2D / "receipts/deposit-20261126/README.md").read_text(),
            "same": (STATE / "release-zenodo-20261127/same-events/same_events.out").read_text(),
            "upload": (STATE / "release-zenodo-20261127/UPLOAD-MANIFEST.md").read_text(),
            "evw5d_hpss": (STATE / "measurement-paper/5d-community-20261024/fd/evw5d-20261125/receipts/attempt2-hpss/README.md").read_text(),
            "log": (STATE / EVW2D / "receipts/run-20261126/post/logs/evw2d-run-62022231.log").read_text(),
            "config_sha256": hashlib.sha256((HERE.parents[1] / EVW2D_CODE["config"]).read_bytes()).hexdigest(),
            "config": json.loads((HERE.parents[1] / EVW2D_CODE["config"]).read_text()),
            "ref_sha256": hashlib.sha256(ref.read_bytes()).hexdigest(), "ref_meta": json.loads(_npz_text(ref, "meta")),
            "code": {k: (HERE.parents[1] / v).read_text() for k, v in EVW2D_CODE.items()}}


def evw2d_refs(d: dict) -> bool:
    """The run used the committed config (by digest), which pins the committed references.npz, whose er is E_R's
    xsec.root a5c13fc3 (adopted, DECISION-20261024; regenA's OLD input) and whose paper is Tier 1's er.root 5171c7b8
    (regenA's E input, the unfolding on the published pT edges)."""
    m, code = d["ref_meta"], d["code"]
    return (d["run"]["config_sha256"] == d["config_sha256"] == d["constants"]["config_sha256"]
            and d["config"]["references"]["sha256"] == d["ref_sha256"]
            and m["er"]["sha256"].startswith("a5c13fc3") and m["er"]["histogram"] == "hXSec2D"
            and m["paper"]["sha256"].startswith("5171c7b8") and m["paper"]["histogram"] == "hXSec2D"
            and "adopt the refined 2D result E_R and Q_R" in code["decision"]
            and "partb/out/ER/xsec.root (a5c13fc3)" in code["regenA"]
            and "E: tier1/units_e/er.root (5171c7b8)." in code["regenA"])


def evw2d_exact(d: dict, key: str) -> bool:
    c = d["run"]["controls"][key]
    return c["pass"] is True and c["cells"] == 205 and c["zero_cells_zero"] is True and evw2d_refs(d)


def evw2d_pass(d: dict) -> bool:
    """The run's verdict and its acceptance: every control passed, with no finding."""
    r, done = d["run"], d["done"]
    return (r["controls_verdict"] == "PASS" and done["verdict"] == "PASS" and done["acceptance"]["pass"] is True
            and r["findings"] == [] and done["findings"] == [] and all(c["pass"] is True for c in r["controls"].values())
            and len(r["controls"]) == 12 and "ACCEPTED" in d["deposit"]
            and f"{r['files_sha256']['weights.npz']}  weights.npz" in d["deposit"])


def evw2d_same_rows(d: dict, sources: dict[str, str]) -> bool:
    """same_events.out (#1413): the verdict line, the T4 lines, and its JSON line; its T0 digests are the two runs'
    weights files; rows match exactly only after a float32 cast (so the text says single precision)."""
    lines = d["same"].splitlines()
    js = [ln[5:] for ln in lines if ln.startswith("JSON ")]
    if len(js) != 1:
        return False
    j = json.loads(js[0])
    n = d["run"]["rows"]
    t4 = j["T4"]
    return (lines.count("VERDICT SAME-ROWS-SAME-ORDER") == 1 and j["verdict"] == "SAME-ROWS-SAME-ORDER"
            and f"T4 truth_pt: exact {n}/{n} after float32 cast" in d["same"]
            and f"T4 truth_pz: exact {n}/{n} after float32 cast" in d["same"]
            and "T4 all rows exact in float32 (pT and p||): True" in lines
            and j["T2"]["pass"] is True and j["T2"]["n_evw2d"] == j["T2"]["n_evw5d"] == n
            and j["T3"]["entries_equal"] is True and j["T3"]["rows_differing"] == 0
            and t4["all_rows_exact_float32"] is True
            and all(t4[k]["exact_equal_float32"] == t4[k]["rows"] == n and t4[k]["rows_over_1_ulp"] == 0
                    and t4[k]["nan_evw2d"] == t4[k]["nan_evw5d"] == 0 for k in ("truth_pt", "truth_pz"))
            and max(t4[k]["max_abs_delta_float64"] for k in ("truth_pt", "truth_pz")) > 0
            and j["files"]["evw2d_weights"]["sha256"] == j["files"]["evw2d_weights"]["expected"]
            == d["run"]["files_sha256"]["weights.npz"]
            and j["files"]["evw5d_weights"]["sha256"] == j["files"]["evw5d_weights"]["expected"]
            and f"{j['files']['evw5d_weights']['sha256']}  weights.npz" in d["evw5d_hpss"])


def evw2d_deposited(d: dict, sources: dict[str, str]) -> bool:
    """The upload manifest (#1417) lists result_2d.npz as current, and its tie to E_R says the file's 205 central values
    equal references.npz's er bit for bit, through the config and references this run used (evw2d_refs)."""
    u, m = d["upload"], d["ref_meta"]
    return (evw2d_refs(d) and evw2d_exact(d, "C-EXACT-ER")
            and "| `package-rc10/result-products-2d/result_2d.npz` | "
                "`9ab08a9f7d57c786f422f7f03bb7810625c243d804d588ad504bb5b77eaa2e47` | 2,696,218 | current |" in u
            and f"`2d-unfolding/evw2d/config.json` (sha256 `{d['config_sha256']}`) pins `references.npz` at "
                f"`{d['ref_sha256']}`;" in u
            and f"records its `er` vector as `hXSec2D` from `xsec.root` `{m['er']['sha256']}`" in u
            and "- `result_2d.npz` `x`, the 205 reported 2D central values, equals `er` at its 205 cells **bit for bit**: "
                "yes (`np.array_equal`);" in u)


EVW2D_CLAIMS = (
    ("EVW2D: the same rows, in the same order, as the 5D weights; pT and p_par exact in float32 (same_events.out)",
     "They are the same rows, in the same order, as those of the sixteen-cell weights below, and their truth $p_T$ and "
     "$p_\\parallel$ agree exactly in single precision.", evw2d_same_rows),
    ("EVW2D: the deposited 2D refined central values are E_R bit for bit (UPLOAD-MANIFEST.md, #1417)",
     "they reproduce the deposited 2D refined central values in every bin", evw2d_deposited),
    ("EVW2D: keyed by the entry in the one input file, whose sha256 the weights file holds (constants.json key, C-KEY)",
     "Each event is keyed by its entry number in the input file, which the weights file identifies by its SHA-256 digest.",
     lambda d, s: (d["constants"]["key"]["column"] == "entry"
                   and d["constants"]["key"]["omnifile_sha256"] == d["run"]["inputs_sha256"]["CV"]
                   and d["run"]["controls"]["C-KEY"]["strictly_increasing"] is True
                   and d["run"]["controls"]["C-FILE"]["meta"] is True and evw2d_pass(d))),
    ("EVW2D: each row carries its prior weight (constants.json columns, C-FILE w_prior)",
     "It also carries its prior weight.",
     lambda d, s: "w_prior" in d["constants"]["columns"] and d["run"]["controls"]["C-FILE"]["w_prior"] is True),
    ("EVW2D: a rerun of E_R's driver, unchanged code and inputs (declaration sec. 2, C-PINS, inputs, argv)",
     "The weights come from a rerun of the two-dimensional unfolding with unchanged code and inputs.",
     lambda d, s: ("**One run of E_R's driver, unchanged:** E_R's argv, its 64 CPUs and thread environment, and its two "
                   "inputs." in d["code"]["decl"]
                   and d["run"]["controls"]["C-PINS"]["pass"] is True and d["run"]["controls"]["C-PINS"]["caches_after_run"] == []
                   and d["run"]["inputs_sha256"]["CV"].startswith("43f8cc16") and d["run"]["inputs_sha256"]["MC"].startswith("d40aea69")
                   and d["run"]["argv"] == d["constants"]["argv"] and evw2d_pass(d))),
    ("EVW2D: completeness 1 in any binning, one integrated flux (C-COMPLETE multisets, C-FLUX one ulp)",
     "Their completeness denominator is these same events, so the completeness is 1 in any binning, and the flux is a "
     "single integrated value.",
     lambda d, s: (d["run"]["controls"]["C-COMPLETE"]["pass"] is True
                   and d["run"]["controls"]["C-COMPLETE"]["signal_rows"] == d["run"]["controls"]["C-COMPLETE"]["denominator_rows"]
                   == d["run"]["rows"] and d["run"]["findings"] == []
                   and d["run"]["controls"]["C-FLUX"]["pass"] is True
                   and d["run"]["controls"]["C-FLUX"]["spread"] <= d["run"]["controls"]["C-FLUX"]["ulp"]
                   and d["constants"]["constants"]["phi_m2_per_POT"] in d["constants"]["constants"]["flux_bins_m2_per_POT"])),
    ("EVW2D: binning in pT and p_par inside the Sec. 2 truth phase space (constants.json phase_space: 0-4.5, 1.5-60, 20 deg)",
     "Readers can therefore choose any binning in $p_T$ and $p_\\parallel$ inside the truth phase space of "
     "Sec.~\\ref{sec:selection} [Eq.~\\eqref{eq:muon-fiducial}].",
     lambda d, s: ((ps := d["constants"]["constants"]["phase_space"])["pt"] == [0, 4.5] and ps["pz"] == [1.5, 60.0]
                   and ps["theta_max_deg"] == 20.0
                   and (r"\theta_\mu<20^\circ,\quad 1.5<p_\parallel<\SI{60}{GeV/c},\quad p_T<\SI{4.5}{GeV/c} . "
                        r"\label{eq:muon-fiducial}") in text("sec2_method.tex", s))),
    ("EVW2D: only the two grids compared with unfoldings (constants.json validity and validated_grids)",
     "Only these two grids were compared with full unfoldings.",
     lambda d, s: (sorted(d["constants"]["constants"]["validated_grids"]) == ["ours", "paper"]
                   and d["constants"]["constants"]["validity"]
                   == "the central value; validated for observables of (pT, p||) only, on the two grids above"
                   and [d["constants"]["constants"]["validated_grids"]["paper"][i] for i in (1, 4, 6)] == [0.075, 0.325, 0.475])),
    ("EVW2D: central values only",
     "The weights give central values only, so they give no uncertainty for a new binning.",
     lambda d, s: d["constants"]["constants"]["validity"].startswith("the central value;")),
)


# Sec. 2.3's clipping sentence (Joseph 2026-11-27): EVW2D reruns E_R's driver on the data with unchanged code and inputs
# (EVW2D_CLAIMS above), and its committed log prints the refinement's score range and clipped count.
def clip2d_gmin(d: dict) -> float:
    m = re.findall(r"Stay-Positive refine: [0-9]+ pos / [0-9]+ neg events; g in \[([0-9.]+),([0-9.]+)\]; "
                   r"clipped\(2g-1<0\) ([0-9]+) events;", d["log"])
    if len(m) != 1:
        raise ValueError(f"EVW2D log: {len(m)} refinement lines")
    return float(m[0][0]) if int(m[0][2]) == 0 and float(m[0][0]) > 0.5 else -1.0


CLIP2D_CLAIMS = (
    ("clip 2D: the score is at least 0.53 for every event (EVW2D log: g in [0.533, ...], a rerun of E_R)",
     "In the two-dimensional unfolding of the data, the sign classifier's score is at least 0.53 for every event,",
     lambda d: clip2d_gmin(d) >= 0.53 and f"{clip2d_gmin(d):.2f}" == "0.53" and evw2d_pass(d)),
    ("clip 2D: no weight is clipped (EVW2D log: clipped(2g-1<0) 0 events, clipped frac=0.0000)",
     "so no weight is clipped.",
     lambda d: clip2d_gmin(d) > 0.5 and d["log"].count("clipped frac=0.0000;") == 1 and evw2d_pass(d)),
)


def clip2d_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    t, d = text("sec2_method.tex", sources), evw2d()
    return [(lab, t.count(s) == 1 and fact(d), f"sentence found {t.count(s)} time(s) | log {fact(d)}")
            for lab, s, fact in CLIP2D_CLAIMS]


# Sec. 5.3.5's REGRADE-VF sentences (Joseph 2026-11-27): the bias/fluctuation split of the sixteen-cell held-out-tune
# closures under C_rep with C_e^infl (rule (i)) against REGRADE's C' without it ("before"), at the primary minus2
# evaluations. The note's first tune is AR23 and its second G18. The record's sha256 is read from the run's SHA256SUMS.
REGRADE_VF = "measurement-paper/5d-community-20261024/fd/regrade-vf-20261127"
REGRADE_VF_OVERRIDE = None


def regrade_vf() -> dict:
    if REGRADE_VF_OVERRIDE is not None:
        return REGRADE_VF_OVERRIDE
    run = STATE / REGRADE_VF / "run"
    sums = dict(reversed(l.split()) for l in (run / "SHA256SUMS").read_text().splitlines() if l.strip())
    return {"sha256": hashlib.sha256((run / "regrade_vf.json").read_bytes()).hexdigest(), "sums": sums,
            "rec": json.loads((run / "regrade_vf.json").read_text()),
            "decl": (STATE / REGRADE_VF / "REGRADE-VF-DECLARATION.md").read_text()}


def regrade_vf_ok(d: dict) -> bool:
    """The record is the committed run's (SHA256SUMS, and the director's 9f0e46e7 prefix), of declaration rev 1, with
    the two minus2 evaluations primary and every control within tolerance."""
    r = d["rec"]
    return (d["sha256"] == d["sums"]["regrade_vf.json"] and d["sha256"].startswith("9f0e46e7")
            and r["declaration"] == "REGRADE-VF-DECLARATION.md rev 1"
            and sorted(r["primary"]) == ["ar23/minus2", "g18/minus2"])


def rvf(d: dict, tune: str, rule: str) -> dict:
    return d["rec"]["evaluations"][f"{tune}/minus2"][rule]


def rvf_fall(d: dict, tune: str) -> float:
    return 1.0 - rvf(d, tune, "rule_i")["B"] / rvf(d, tune, "before")["B"]


def rvf_resolved(e: dict) -> bool:
    return e["readings"]["bias_resolved"] == "yes" and e["B"] > 3 * e["se_boot"]["B"]


def rvf_before_is_crep0(d: dict, sources: dict[str, str]) -> bool:
    """'this covariance' follows C_rep,0 on the same draws: "before"'s mean chi2/ndf at the two tunes are the printed
    rg-16-full-min/max."""
    v = dict(re.findall(r"\\@namedef\{fv@(rg-16-full-(?:min|max))\}\{([0-9.]+)\}", sources["values_fived16.tex"]))
    m = sorted(rvf(d, t, "before")["M_full"] for t in ("ar23", "g18"))
    return len(v) == 2 and f"{m[0]:.1f}" == v["rg-16-full-min"] and f"{m[1]:.1f}" == v["rg-16-full-max"]


REGRADE_VF_CLAIMS = (
    ("REGRADE-VF: the mean offset is still resolved at both tunes (bias_resolved yes, B > 3 SE_boot, rule (i))",
     "With $V_{\\mathrm{stat+syst}}^{\\mathrm{infl}}$ in place of $V_{\\mathrm{stat+syst}}$, the mean offset of the cells from "
     "the truth is still clearly nonzero at both tunes.",
     lambda d, s: regrade_vf_ok(d) and all(rvf_resolved(rvf(d, t, "rule_i")) for t in ("ar23", "g18"))),
    ("REGRADE-VF: offset larger than scatter at AR23, smaller at G18 (bias_vs_fluctuation, rule (i), 3 SE_boot)",
     "It makes up more of the mean $\\chi^2/\\mathrm{ndf}$ than the scatter of the draws at the first tune, and less at the second.",
     lambda d, s: regrade_vf_ok(d)
     and rvf(d, "ar23", "rule_i")["readings"]["bias_vs_fluctuation"] == "bias larger"
     and rvf(d, "ar23", "rule_i")["B"] - rvf(d, "ar23", "rule_i")["F"] > 3 * rvf(d, "ar23", "rule_i")["se_boot"]["B_minus_F"]
     and rvf(d, "g18", "rule_i")["readings"]["bias_vs_fluctuation"] == "fluctuation larger"
     and rvf(d, "g18", "rule_i")["F"] - rvf(d, "g18", "rule_i")["B"] > 3 * rvf(d, "g18", "rule_i")["se_boot"]["B_minus_F"]),
    ("REGRADE-VF: B falls by about two thirds at AR23 and about half at G18 (rule (i) vs before, which is C_rep,0 on the same draws)",
     "Compared with $\\CrepFiveDzero$, its contribution to the mean $\\chi^2/\\mathrm{ndf}$ falls by about two thirds at the first tune and by about half at the second.",
     lambda d, s: regrade_vf_ok(d) and 0.62 <= rvf_fall(d, "ar23") <= 0.71 and 0.45 <= rvf_fall(d, "g18") <= 0.58
     and rvf_before_is_crep0(d, s)),
    ("REGRADE-VF: circular by construction (declaration sec. 5: same draws; cannot show coverage of C_rep)",
     "Because the inflation was chosen using these same tunes, this is a consistency check, not a coverage test.",
     lambda d, s: regrade_vf_ok(d) and "The draws here are the same draws C_e^infl was fitted to." in d["decl"]
     and "- Coverage or calibration of C_rep." in d["decl"]),
)


def regrade_vf_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    t, d = text("sec5_multidim.tex", sources), regrade_vf()
    return [(lab, t.count(s) == 1 and fact(d, sources), f"sentence found {t.count(s)} time(s) | record {fact(d, sources)}")
            for lab, s, fact in REGRADE_VF_CLAIMS]


def evw2d_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    t, d = text("appD_reproducibility.tex", sources), evw2d()
    return [(lab, t.count(s) == 1 and fact(d, sources), f"sentence found {t.count(s)} time(s) | receipt {fact(d, sources)}")
            for lab, s, fact in EVW2D_CLAIMS]


# The high-p_par open issue in sec3_twod.tex (Joseph 2026-11-26, via the director; a PROPOSAL for his wording). Every
# number and reading is bound to the precharge study's committed outputs (state/precharge-20261125/). The sentence states
# no cause: the study's declarations make no cause determination.
PRECHARGE = "precharge-20261125"
HIGHPZ_OVERRIDE = None  # the self-test plants altered records here


def highpz() -> dict:
    """merged-comparison.csv and signed-qp.csv (reco yields), test1 (the E_vis table and the held-out fold), and the
    readings of tests A, B and C."""
    if HIGHPZ_OVERRIDE is not None:
        return HIGHPZ_OVERRIDE
    import csv
    base = STATE / PRECHARGE

    def rows(name):
        with open(base / name, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    return {"merged": rows("merged-comparison.csv"), "signed": rows("signed-qp.csv"),
            "evis": (base / "test1/evis-by-pz.txt").read_text(),
            "evis_readme": (base / "test1/README.md").read_text(), "test1": receipt(f"{PRECHARGE}/test1/test1.json"),
            "testb": receipt(f"{PRECHARGE}/testAB/test-b.json"), "testc": receipt(f"{PRECHARGE}/testC/test-c.json"),
            "atxt": (base / "testAB/test-a.txt").read_text(), "btxt": (base / "testAB/test-b.txt").read_text(),
            "ctxt": (base / "testC/test-c.txt").read_text(), "cdecl": (base / "testC/DECLARATION.md").read_text(),
            "creadme": (base / "testC/README.md").read_text()}


def highpz_excess() -> float:
    """Data minus the fold at reco p_par >= 60 (the 60-80 and >=80 rows), both signs, before the charge requirement."""
    r = [x for x in highpz()["merged"] if x["reco_p_parallel_GeV_c"] in ("60–80", "≥80")]
    if sorted((x["reco_p_parallel_GeV_c"], x["sign"]) for x in r) != sorted(
            [("60–80", "-"), ("60–80", "+"), ("≥80", "-"), ("≥80", "+")]):
        raise ValueError(f"{PRECHARGE}/merged-comparison.csv: the reco >= 60 rows are not the four sign rows")
    return sum(float(x["data_minus_all_selected"]) for x in r)


def highpz_tails() -> float:
    """Data minus the fold in the |q/p| >= 1/60 (GeV/c)^-1 curvature cells of the reco >= 60 bands (2: 60-80, 3: >= 80)."""
    cells = {}
    for x in highpz()["signed"]:
        if x["band"] in ("2", "3") and (float(x["qp_high"]) <= -1 / 60 + 1e-12 or float(x["qp_low"]) >= 1 / 60 - 1e-12):
            cells.setdefault((x["band"], x["qbin"]), {})[x["sample"]] = float(x["fold"])
    if not cells or any(set(v) != {"Data", "MC"} for v in cells.values()):
        raise ValueError(f"{PRECHARGE}/signed-qp.csv: a tail cell lacks its Data or MC row")
    return sum(v["Data"] - v["MC"] for v in cells.values())


def highpz_b_share() -> float:
    """Test B's primary held-out epsilon prediction at 50-60 and 60-80 (S2), as a percentage of data minus the fold there
    (the fold from Test 1's primary held-out bands, the same six held-out playlists)."""
    d = highpz()
    b = [x for x in d["testb"] if x["direction"] == "primary"]
    f = [x for x in d["test1"] if x["train"] == b[0]["train"]] if b and "train" in b[0] else \
        [x for x in d["test1"] if x["train"] == ["1A", "1C", "1E", "1G", "1M", "1O"]]
    if len(b) != 1 or not f:
        raise ValueError(f"{PRECHARGE}: test B's primary direction or test 1's matching fold is missing")
    t, bands = b[0]["epsilon"]["terms"], f[0]["bands"]
    num = den = 0.0
    for k, band in (("S2|50", "-|all|50-60"), ("S2|60", "-|all|60-80")):
        data, eps = t[k][0], t[k][1]
        if data != bands[band][0]:
            raise ValueError(f"{PRECHARGE}: test B's {k} data {data} differs from test 1's {band} {bands[band][0]}")
        num += eps - bands[band][1]
        den += data - bands[band][1]
    return 100 * num / den


def highpz_rises(d: dict) -> bool:
    """test1/evis-by-pz.txt's data/fold table (good negative tracks, |sigma(q/p)/(q/p)| < 0.30, all playlists): in the
    20-40, 40-50, 50-60 and 60-80 bands, every listed cell exceeds the one before it along E_vis (at fixed p_par, rising
    E_vis is rising E_avail)."""
    if "(`evis_by_pz.py` → `evis-by-pz.txt`, good negative tracks, all playlists)" not in d["evis_readme"]:
        return False
    blk = d["evis"].split("data/fold (cells with fold >= 5)", 1)
    if len(blk) != 2:
        return False
    rows = {}
    for ln in blk[1].splitlines():
        m = re.match(r"\[(\d+\.\d), (\d+\.\d|inf)\)\s+(.*)$", ln.strip())
        if m:
            vals = [float(v) for v in m.group(3).split() if v != "NaN"]
            rows[(m.group(1), m.group(2))] = vals
    want = [("20.0", "40.0"), ("40.0", "50.0"), ("50.0", "60.0"), ("60.0", "80.0")]
    return all(k in rows and len(rows[k]) >= 2 and all(b > a for a, b in zip(rows[k], rows[k][1:])) for k in want)


HIGHPZ_CLAIMS = (
    ("high p_par: data/fold rises with visible energy, reco p_par + E_avail, in each reco band from 20 to 80 GeV/c",
     r"For negative tracks with well-measured curvature, the ratio of data to this prediction rises with visible energy, "
     r"$p_\parallel + E_{\mathrm{avail}}$, in each reconstructed $p_\parallel$ band from 20 to 80~GeV/$c$.",
     lambda d: highpz_rises(d) and "The fit variable is E_vis = reco p∥ + E_avail" in d["evis_readme"]),
    ("high p_par: A (one muon-independent recoil function) does not reproduce it",
     "A recoil-energy correction independent of the muon does not reproduce this rise.",
     lambda d: "primary: H_A (A1) contradicts" in d["atxt"] and "swap: H_A (A1) contradicts" in d["atxt"]),
    # C was fitted at reco p_par 20-40 and transferred upward. Its declaration leaves open a change where that fit has
    # no lever, such as one confined to true muon p_par >= 60 (DECLARATION.md "Contradicts", README.md "What follows").
    ("high p_par: C (a smooth true-E_nu rate change fitted at reco 20-40) does not, and a change where that fit has no "
     "lever stays open",
     r"Nor does a smooth dependence of the event rate on neutrino energy fitted at lower $p_\parallel$, although a "
     r"change confined to the highest muon momenta remains possible.",
     lambda d: (d["testc"]["reading"] == "contradicts"
                and "Reading for H_C (primary form, both directions): contradicts" in d["ctxt"]
                and "The fit sample is the training playlists, reco p∥ 20–40" in d["cdecl"]
                and "or that live where the 20–40 fit has no lever, such as an unanchored change confined to true ≥60"
                in d["cdecl"]
                and "**C** contradicts a smooth Eν rate change that is fitted at 20–40 and transferred upward"
                in d["creadme"]
                and "or that are confined to where 20–40 has no lever" in d["creadme"])),
    ("high p_par: B, a constant curvature offset, is inconclusive (it carries part of the excess, not all)",
     "A constant offset in the fitted curvature accounts for about",
     lambda d: "primary: H_B inconclusive" in d["btxt"] and "swap: H_B inconclusive" in d["btxt"]),
)


# OOFVC (#1420): the 2D distances under MINERvA's counting convention (a PROPOSAL for Joseph, 2026-11-27), bound to r3's
# score.json and the declaration's sec. 1.1 (the conventions) and sec. 2.3-2.4 (the operands at K = 10, the readings).
OOFVC = "oofv-convention-20261126"
OOFVC_OVERRIDE = None  # the self-test plants altered records here


def oofvc() -> dict:
    if OOFVC_OVERRIDE is not None:
        return OOFVC_OVERRIDE
    return {"score": json.loads((STATE / OOFVC / "receipts/attempt3-r3/score.json.txt").read_text()),
            "decl": (STATE / OOFVC / "OOFVC-DECLARATION.md").read_text()}


def _fv(sources: dict[str, str], name: str) -> str:
    """A values_fived16.tex macro's printed value."""
    m = re.findall(r"\\@namedef\{fv@" + re.escape(name) + r"\}\{([^}]*)\}", sources["values_fived16.tex"])
    return m[0] if len(m) == 1 else "<missing>"


def oofvc_ok(d: dict) -> bool:
    sc = d["score"]
    return sc["controls_pass"] is True and all(c["pass"] is True for c in sc["controls"].values())


def oofvc_before(d: dict, sources: dict[str, str]) -> bool:
    """The printed 'instead of' values are the production distances r3 reproduced (C-BASE), as the macros print them."""
    o = d["score"]["operands"]
    return (oofvc_ok(d) and _fv(sources, "c2c1-dibu") == f"{o['D_IBU_0']:.2f}" and _fv(sources, "c2c1-der") == f"{o['D_ER_0']:.2f}"
            and d["score"]["controls"]["C-BASE"]["D_IBU_vs_regenA3_max_rel"] < 1e-9
            and d["score"]["controls"]["C-BASE"]["D_ER_vs_tier1_rel"] < 1e-6
            and d["score"]["descriptive"]["D_IBU_every_K"]["R"]["10"] == o["D_IBU_R"]
            and d["score"]["descriptive"]["D_IBU_every_K"]["off"]["10"] == o["D_IBU_0"]
            and "- D_IBU^0 and D_IBU^R at K = 10;" in d["decl"])


OOFVC_CLAIMS = (
    ("OOFVC: the new sentences follow the existing IBU distance sentence (whose 0.54 is D_IBU_0)",
     "sec3_twod.tex",
     "Relative to the published result, ten-iteration IBU gives \\fvval{c2c1-dibu} per bin using the same "
     "published-covariance metric. The MINERvA Analysis Toolkit counts", lambda d, s: oofvc_before(d, s)),
    ("OOFVC: MINERvA's code (MAT's Cutter) counts selected nu_mu CC events outside the phase space as signal, and "
     "non-nu_mu-CC events as background (decl. 1.1)",
     "sec3_twod.tex",
     "The MINERvA Analysis Toolkit counts the selected $\\nu_\\mu$ charged-current events that fall outside the truth "
     "phase space as signal.",
     lambda d, s: ("| selected ν_μ CC event failing the phase space (true vertex outside the fiducial volume, or θ_μ ≥ 20°, "
                   "or p∥ outside 1.5–60 GeV/c, or p_T ≥ 4.5 GeV/c) |" in d["decl"]
                   and "| **signal**: it fills the efficiency numerator at its true (p_T, p∥) and the migration |" in d["decl"]
                   and "| selected event that is not ν_μ CC (NC, ν̄_μ, ν_e) | background | background |" in d["decl"]
                   and "1. **`MAT/PlotUtils/Cutter.cxx` @ 0111c79de**" in d["decl"] and oofvc_ok(d))),
    ("OOFVC: only those with a true muon in the reported range are counted (decl. 1.3 step 3); the two distances "
     "(operands at K = 10; the 'instead of' macros are the production ones)",
     "sec3_twod.tex",
     "If we count as signal those of these events whose true muon is in the reported $p_T$--$p_\\parallel$ range, "
     "ten-iteration IBU gives 0.20 per bin instead of \\fvval{c2c1-dibu}, and the two-dimensional OmniFold result gives "
     "2.21 instead of \\fvval{c2c1-der}.",
     lambda d, s: (oofvc_before(d, s)
                   and "Only rows whose true muon is in the grid are included (step 3)." in d["decl"]
                   and d["score"]["controls"]["C-MOVE"]["pass"] is True)),
    ("OOFVC: so it does not account for the 2D shape difference (r_IBU LOWER, r_ER LITTLE CHANGE; decl. 2.4's statement)",
     "sec3_twod.tex", "This convention therefore does not account for the 2D shape difference with the published result.",
     lambda d, s: (oofvc_ok(d) and d["score"]["bands"]["r_IBU"] == "LOWER"
                   and d["score"]["bands"]["r_ER"] == "LITTLE CHANGE"
                   and d["score"]["ratios"]["r_IBU"] <= 0.80 and 0.95 <= d["score"]["ratios"]["r_ER"] <= 1 / 0.95
                   and d["score"]["statements"]["primary"] == "The reclassification moves the binned IBU's distance; at "
                   "this scale it does not move the OmniFold central value's"
                   and "| LOWER | LITTLE CHANGE or INTERMEDIATE | The reclassification moves the binned IBU's distance; at "
                   "this scale it does not move the OmniFold central value's |" in d["decl"])),
    ("OOFVC: Sec. 6's sentence (r_ER LITTLE CHANGE)", "sec6_conclusions.tex",
     "The MINERvA Analysis Toolkit's signal convention does not account for the 2D shape difference with the published "
     "result (Sec.~\\ref{sec:results-benchmarks}).",
     lambda d, s: d["score"]["bands"]["r_ER"] == "LITTLE CHANGE" and oofvc_ok(d)),
)


def oofvc_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    d = oofvc()
    out = []
    for lab, f, sent, fact in OOFVC_CLAIMS:
        n = text(f, sources).count(sent)
        out.append((lab, n == 1 and fact(d, sources), f"sentence found {n} time(s) | record {fact(d, sources)}"))
    return out


def highpz_claims(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    t, d = text("sec3_twod.tex", sources), highpz()
    return [(lab, t.count(s) == 1 and fact(d), f"sentence found {t.count(s)} time(s) | record {fact(d)}")
            for lab, s, fact in HIGHPZ_CLAIMS]


# (label, source file, regex with one or two captured printed values, computed value(s), mode)
CHECKS = [
    # OOFVC (oofv-convention-20261126, r3 score.json), sec3_twod.tex
    ("OOFVC: D_IBU under the convention, K = 10, and D_E_R under it (score.json operands D_IBU_R, D_ER_R)", "sec3_twod.tex",
     r"ten-iteration IBU gives ([0-9.]+) per bin instead of \\fvval\{c2c1-dibu\}, and the two-dimensional OmniFold "
     r"result gives ([0-9.]+) instead of \\fvval\{c2c1-der\}\.",
     lambda: (oofvc()["score"]["operands"]["D_IBU_R"], oofvc()["score"]["operands"]["D_ER_R"]) if oofvc_ok(oofvc())
     else (-1.0, -1.0), "round"),
    # The high-p_par open issue (precharge-20261125), sec3_twod.tex
    ("high p_par: the reco edge of the excess (merged-comparison.csv rows 60-80 and >=80)", "sec3_twod.tex",
     r"above the reported range, at reconstructed \$p_\\parallel \\geq ([0-9]+)\$~GeV/\$c\$\.",
     lambda: 60.0 if {x["reco_p_parallel_GeV_c"] for x in highpz()["merged"]} >= {"60–80", "≥80"} else -1.0, "round"),
    ("high p_par: the curvature-tail excess (signed-qp.csv) and the excess at reco >= 60, both signs (merged-comparison.csv)",
     "sec3_twod.tex",
     r"About ([0-9]+) of the roughly ([0-9]+) excess tracks, counting both charges, lie in the tails of the fitted muon curvature",
     lambda: (highpz_tails(), highpz_excess()), "round"),
    ("high p_par: test B's share of the 50-80 excess (test-b.json epsilon S2, test1.json fold)", "sec3_twod.tex",
     r"A constant offset in the fitted curvature accounts for about \$([0-9]+)\\%\$ of the excess between 50 and 80~GeV/\$c\$",
     highpz_b_share, "round"),
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
     r"The direct inverse of \$\\CrepTwoD\$ gives a quadratic distance of ([0-9.]+) per reported bin",
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
    ("regularization bias at high W (VL151), sec_5d's copy", "sec_5d.tex",
     r"They reach \\SI\{([0-9.]+)\}\{\\percent\} in the highest-\$W\$ column", regularization_max, "round"),
    ("an earlier estimator's 68% coverage under the rate reduction (s5c tier S)", "appA_methods.tex",
     r"The lowest empirical coverage for the \$68\\%\$ intervals is ([0-9.]+)\.", tilt_coverage68_min, "round"),
    ("other fixed shapes, most affected cell (VL154)", "primer_body.tex",
     r"the effect is \\SIrange\{([0-9.]+)\}\{([0-9.]+)\}\{\\percent\} in the worst cell", shapes_range, "round"),
    # EVW5D, App. D. The exponents are fixed in the patterns, so a changed exponent is not found and fails.
    ("EVW5D rows in weights.npz (run.json C-KEY n_rows)", "appD_reproducibility.tex",
     r"per-event OmniFold weights on the \\num\{([0-9]+)\} simulated events that pass the truth selection",
     lambda: float(evw5d()["run"]["controls"]["C-KEY"]["n_rows"]), "round"),
    ("EVW5D rows outside the fine grid (run.json C-FLOW n_outside_grid)", "appD_reproducibility.tex",
     r"Of these, \\num\{([0-9]+)\} lie outside the fine grid's",
     lambda: float(evw5d()["run"]["controls"]["C-FLOW"]["n_outside_grid"]), "round"),
    ("EVW5D stored completeness: cells off 1, and the largest |c - 1| (run.json C-COMPLETE)", "appD_reproducibility.tex",
     r"The stored completeness differs from 1 in ([0-9]+) fine cells, by at most \\num\{([0-9.]+)e-4\}\.",
     lambda: (float(evw5d()["run"]["controls"]["C-COMPLETE"]["n_cells_beyond_atol"]),
              1e4 * evw5d()["run"]["controls"]["C-COMPLETE"]["max_abs_c_minus_1"]), "round"),
    # One event per pair is a reading ("consistent with", DECISION-20261126 sec. 1), not a count: both 16s bind to the pairs.
    ("EVW5D adjacent equal-and-opposite pairs, and the events they are consistent with (lane/c32.txt)",
     "appD_reproducibility.tex",
     r"These cells form ([0-9]+) adjacent pairs with equal and opposite differences\. This pattern is consistent with "
     r"([0-9]+) events that lie within single-precision rounding of a cell edge\.",
     lambda: (float(evw5d_pairs()), float(evw5d_pairs())), "round"),
    # EVW2D, App. D. The exponents are fixed in the patterns, so a changed exponent is not found and fails.
    ("EVW2D rows in weights.npz (run.json C-KEY rows, = rows = constants.json rows)", "appD_reproducibility.tex",
     r"The weights cover the \\num\{([0-9]+)\} simulated events that pass the truth selection\.",
     lambda: float(evw2d()["run"]["controls"]["C-KEY"]["rows"]) if evw2d()["run"]["controls"]["C-KEY"]["rows"]
     == evw2d()["run"]["rows"] == evw2d()["constants"]["rows"] else -1.0, "round"),
    ("EVW2D re-histogram on our grid against E_R (run.json C-EXACT-ER max_rel)", "appD_reproducibility.tex",
     r"Histogrammed on our analysis grid, they reproduce the deposited 2D refined central values in every bin to "
     r"\\num\{([0-9.]+)e-12\} of their values\.",
     lambda: 1e12 * evw2d()["run"]["controls"]["C-EXACT-ER"]["max_rel"] if evw2d_exact(evw2d(), "C-EXACT-ER") else -1.0,
     "round"),
    ("EVW2D re-histogram on the published pT edges against Tier 1's e (run.json C-EXACT-PAPER max_rel)",
     "appD_reproducibility.tex",
     r"Histogrammed on MINERvA's published \$p_T\$ edges, they reproduce the unfolding on those edges that the "
     r"central-value comparisons of Sec\.~\\ref\{sec:results-xsec\} use, to \\num\{([0-9.]+)e-12\}\.",
     lambda: 1e12 * evw2d()["run"]["controls"]["C-EXACT-PAPER"]["max_rel"] if evw2d_exact(evw2d(), "C-EXACT-PAPER")
     else -1.0, "round"),
    ("EVW5D sixteen integrals, change if c := 1 (lane/c1effect.txt)", "appD_reproducibility.tex",
     r"changes the sixteen cell integrals by at most \\num\{([0-9.]+)e-6\} of their values", lambda: 1e6 * evw5d()["c1"],
     "round"),
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
        found = {f: re.findall(EDGE_STEP_COPY, text(f, sources)) for f in EDGE_STEP_COPIES}
        good = all(len(found[f]) == n for f, n in EDGE_STEP_COPIES.items()) and \
            all(x == step for v in found.values() for x in v)
        rows.append((EDGE_STEP_ALL, good, f"printed {found} | expected counts {EDGE_STEP_COPIES} | sec3 step {step}"))
    rows += mode_split_claims(sources)
    rows += ibub_claims(sources)
    rows += evw5d_claims(sources)
    rows += evw2d_claims(sources)
    rows += clip2d_claims(sources)
    rows += regrade_vf_claims(sources)
    rows += highpz_claims(sources)
    rows += oofvc_claims(sources)
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
                                               "sec_5d.tex", "primer_body.tex", "appA_methods.tex",
                                               "appC_supplementary.tex", "records_r03_twod.tex", "sec2_method.tex",
                                               "appD_reproducibility.tex", "sec5_multidim.tex", "sec6_conclusions.tex", "values_fived16.tex")}


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
    # The high-p_par claims: each sentence reworded, and each planted record, must be rejected
    # The OOFVC claims: each sentence reworded, and each planted record, must be rejected.
    for f, old_s, new_s in (("sec3_twod.tex", "charged-current events that fall outside the truth phase space as signal.",
                             "charged-current events that fall outside the truth phase space as background."),
                            ("sec3_twod.tex", "counts the selected $\\nu_\\mu$ charged-current events", "counts the selected events"),
                            ("sec3_twod.tex", "whose true muon is in the reported", "whose true muon is anywhere outside the reported"),
                            ("sec3_twod.tex", "This convention therefore does not account for", "This convention therefore accounts for"),
                            ("sec3_twod.tex", "instead of \\fvval{c2c1-dibu}", "instead of 0.54"),
                            ("sec3_twod.tex", "per bin using the same published-covariance metric. The MINERvA",
                             "per bin using the same published-covariance metric. Ten-iteration IBU gives 0.54 per bin. The MINERvA"),
                            ("sec6_conclusions.tex", "convention does not account for the 2D shape", "convention accounts for the 2D shape")):
        t = text(f, base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   OOFVC mutation {old_s!r}"); ok = False; continue
        trial = dict(base)
        trial[f] = t.replace(old_s, new_s)
        if all(r[1] for r in evaluate(trial)):
            print(f"  NOT CAUGHT  OOFVC: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      OOFVC: {old_s} -> {new_s}")
    trial = dict(base)
    trial["values_fived16.tex"] = base["values_fived16.tex"].replace(r"\@namedef{fv@c2c1-der}{2.12}", r"\@namedef{fv@c2c1-der}{2.13}")
    if all(r[1] for r in evaluate(trial)):
        print("  NOT CAUGHT  OOFVC: c2c1-der printed 2.13"); ok = False
    else:
        caught += 1; print("  caught      OOFVC: c2c1-der printed 2.13")

    def plant_of(what, fn):
        global OOFVC_OVERRIDE
        nonlocal ok, caught
        import copy as copy_mod
        data = copy_mod.deepcopy(oofvc())
        fn(data)
        OOFVC_OVERRIDE = data
        try:
            rows = dict((r[0], r[1]) for r in evaluate(base))
        except (ValueError, KeyError, TypeError):
            rows = {"refused": False}
        finally:
            OOFVC_OVERRIDE = None
        if all(rows.values()):
            print(f"  NOT CAUGHT  OOFVC planted: {what}"); ok = False
        else:
            caught += 1; print(f"  caught      OOFVC planted: {what}")
    sc = lambda d: d["score"]
    plant_of("a control failing", lambda d: sc(d)["controls"]["C-MOVE"].__setitem__("pass", False))
    plant_of("controls_pass false", lambda d: sc(d).__setitem__("controls_pass", False))
    plant_of("r_ER INTERMEDIATE", lambda d: sc(d)["bands"].__setitem__("r_ER", "INTERMEDIATE"))
    plant_of("r_ER 1.06", lambda d: sc(d)["ratios"].__setitem__("r_ER", 1.06))
    plant_of("r_IBU LITTLE CHANGE", lambda d: sc(d)["bands"].__setitem__("r_IBU", "LITTLE CHANGE"))
    plant_of("another primary statement", lambda d: sc(d)["statements"].__setitem__("primary", "No statement; the numbers are reported"))
    plant_of("D_IBU_R 0.21", lambda d: sc(d)["operands"].__setitem__("D_IBU_R", 0.21))
    plant_of("D_ER_R 2.22", lambda d: sc(d)["operands"].__setitem__("D_ER_R", 2.22))
    plant_of("D_IBU_R not the K = 10 entry", lambda d: sc(d)["descriptive"]["D_IBU_every_K"]["R"].__setitem__("10", 0.3))
    plant_of("D_ER_0 off Tier 1", lambda d: sc(d)["controls"]["C-BASE"].__setitem__("D_ER_vs_tier1_rel", 1e-3))
    plant_of("MINERvA's code counts non-CC events as signal", lambda d: d.__setitem__("decl", d["decl"].replace("| selected event that is not ν_μ CC (NC, ν̄_μ, ν_e) | background | background |", "| selected event that is not ν_μ CC (NC, ν̄_μ, ν_e) | background | signal |")))
    plant_of("MINERvA's code calls them background", lambda d: d.__setitem__("decl", d["decl"].replace("| **signal**: it fills the efficiency numerator", "| background: it fills the efficiency numerator")))
    plant_of("the declaration's K not 10", lambda d: d.__setitem__("decl", d["decl"].replace("- D_IBU^0 and D_IBU^R at K = 10;", "- D_IBU^0 and D_IBU^R at K = 5;")))
    plant_of("the moved rows not limited to the grid", lambda d: d.__setitem__("decl", d["decl"].replace("Only rows whose true muon is in the grid are included (step 3).", "All rows are included.")))
    for old_s, new_s in (("rises with visible energy", "falls with visible energy"),
                         ("band from 20 to 80~GeV", "band from 20 to 100~GeV"),
                         ("independent of the muon does not", "depending on the muon does not"),
                         ("muon does not reproduce this rise", "muon reproduces this rise"),
                         ("Nor does a smooth dependence", "So does a smooth dependence"),
                         ("fitted at lower $p_\\parallel$", "fitted at higher $p_\\parallel$"),
                         ("highest muon momenta remains possible", "highest muon momenta is excluded"),
                         ("confined to the highest muon momenta", "confined to the highest energies")):
        t = text("sec3_twod.tex", base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   high p_par mutation {old_s!r}"); ok = False; continue
        trial = dict(base)
        trial["sec3_twod.tex"] = t.replace(old_s, new_s)
        if all(r[1] for r in highpz_claims(trial)):
            print(f"  NOT CAUGHT  high p_par: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      high p_par: {old_s} -> {new_s}")

    def plant_hp(what, fn):
        global HIGHPZ_OVERRIDE
        nonlocal ok, caught
        import copy as copy_mod  # self_test imports copy locally further down, so the module name is not bound yet
        data = copy_mod.deepcopy(highpz())
        fn(data)
        HIGHPZ_OVERRIDE = data
        try:
            good = all(r[1] for r in evaluate(base))
        except (ValueError, KeyError, IndexError):
            good = False
        finally:
            HIGHPZ_OVERRIDE = None
        if good:
            print(f"  NOT CAUGHT  high p_par planted: {what}"); ok = False
        else:
            caught += 1; print(f"  caught      high p_par planted: {what}")
    plant_hp("test A reads supports", lambda d: d.__setitem__("atxt", d["atxt"].replace("primary: H_A (A1) contradicts", "primary: H_A (A1) supports")))
    plant_hp("test B reads supports", lambda d: d.__setitem__("btxt", d["btxt"].replace("swap: H_B inconclusive", "swap: H_B supports")))
    plant_hp("test C reads inconclusive", lambda d: d["testc"].__setitem__("reading", "inconclusive"))
    plant_hp("test C fitted at 20-60", lambda d: d.__setitem__("cdecl", d["cdecl"].replace("reco p∥ 20–40, negative", "reco p∥ 20–60, negative")))
    plant_hp("test C declaration leaves no region open", lambda d: d.__setitem__("cdecl", d["cdecl"].replace("where the 20–40 fit has no lever", "anywhere")))
    plant_hp("test C's open region not in muon p_par", lambda d: d.__setitem__("cdecl", d["cdecl"].replace("confined to true ≥60", "confined to true Eν ≥ 60 GeV")))
    plant_hp("test C README leaves no region open", lambda d: d.__setitem__("creadme", d["creadme"].replace("or that are confined to where 20–40 has no lever", "and nothing else")))
    plant_hp("E_vis defined without E_avail", lambda d: d.__setitem__("evis_readme", d["evis_readme"].replace("The fit variable is E_vis = reco p∥ + E_avail", "The fit variable is E_vis = reco p∥")))
    plant_hp("a 60-80 E_vis cell that falls", lambda d: d.__setitem__("evis", d["evis"].replace("1.78          2.12", "1.78          1.12")))
    plant_hp("a 60-80 sign row missing", lambda d: d.__setitem__("merged", [x for x in d["merged"] if not (x["reco_p_parallel_GeV_c"] == "60–80" and x["sign"] == "+")]))
    plant_hp("a tail cell without its MC row", lambda d: d.__setitem__("signed", [x for x in d["signed"] if not (x["band"] == "2" and x["qbin"] == "2" and x["sample"] == "MC")]))
    plant_hp("test B's S2|60 data not test 1's", lambda d: [x for x in d["testb"] if x["direction"] == "primary"][0]["epsilon"]["terms"]["S2|60"].__setitem__(0, 1180.0))
    plant_hp("test B's epsilon S2|60 prediction 10% higher", lambda d: [x for x in d["testb"] if x["direction"] == "primary"][0]["epsilon"]["terms"]["S2|60"].__setitem__(1, 922.3))
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
            ("appC_supplementary.tex", "edges \\SI{0.005}{GeV/c} from", "edges \\SI{0.006}{GeV/c} from", edge_labels[1]),
            # each printed copy of the step, changed or reworded out of the pattern, fails the all-copies row
            ("sec2_method.tex", "edges differ by \\SI{0.005}{GeV/c}", "edges differ by \\SI{0.006}{GeV/c}", EDGE_STEP_ALL),
            ("sec3_twod.tex", "differ by \\SI{0.005}{GeV/c} from", "differ by \\SI{0.006}{GeV/c} from", EDGE_STEP_ALL),
            ("appC_supplementary.tex", "edges \\SI{0.005}{GeV/c} from the published ones",
             "edges \\SI{0.006}{GeV/c} from the published ones", EDGE_STEP_ALL),
            ("appC_supplementary.tex", "shifted by \\SI{0.005}{GeV/c}", "shifted by \\SI{0.006}{GeV/c}", EDGE_STEP_ALL),
            ("appD_reproducibility.tex", "edges \\SI{0.005}{GeV/c} from the published values",
             "edges \\SI{0.006}{GeV/c} from the published values", EDGE_STEP_ALL),
            ("appC_supplementary.tex", "edges shifted by \\SI", "edges moved by \\SI", EDGE_STEP_ALL),
            ("appD_reproducibility.tex", "three $p_T$ edges \\SI{0.005}", "three $p_T$ bin edges \\SI{0.005}", EDGE_STEP_ALL)):
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
    # The EVW5D claims (not in CHECKS): each sentence reworded, and each planted receipt, must be rejected.
    for old_s, new_s in (("cross section byte for byte.", "cross section to rounding."),
                         ("to double-precision rounding.", "to single-precision rounding."),
                         ("the completeness is 1 in any binning.", "the completeness is 1 in the published binning."),
                         ("The flux enters as a single integrated value.", "The flux enters as a binned value."),
                         ("$q_3$ or $W$ range and enter", "$q_3$, $W$, $p_T$ or $p_\\parallel$ range and enter"),
                         ("choose any binning inside the truth phase space of Sec.~\\ref{sec:selection}",
                          "choose any binning inside the fiducial region of Sec.~\\ref{sec:selection}")):
        t = text("appD_reproducibility.tex", base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   EVW5D mutation {old_s!r}"); ok = False; continue
        trial = dict(base)
        trial["appD_reproducibility.tex"] = t.replace(old_s, new_s)
        if all(r[1] for r in evw5d_claims(trial)):
            print(f"  NOT CAUGHT  EVW5D: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      EVW5D: {old_s} -> {new_s}")

    def plant5(what, fn):
        global EVW5D_OVERRIDE
        nonlocal ok, caught
        data = copy.deepcopy(evw5d())
        fn(data)
        EVW5D_OVERRIDE = data
        try:
            rows = dict((r[0], r[1]) for r in evaluate(base))
        except ValueError:
            rows = {"refused": False}
        finally:
            EVW5D_OVERRIDE = None
        if all(rows.values()):
            print(f"  NOT CAUGHT  EVW5D planted: {what}"); ok = False
        else:
            caught += 1; print(f"  caught      EVW5D planted: {what}")
    plant5("C-BIND xsec_flat bytes differ", lambda d: d["run"]["controls"]["C-BIND"].__setitem__("xsec_flat_bytes_equal", False))
    plant5("controls verdict FAIL", lambda d: d["run"].__setitem__("controls_verdict", "FAIL"))
    plant5("C-F from the rows 1e-12", lambda d: d["run"]["controls"]["C-F"].__setitem__("f_from_rows_max_rel", 1e-12))
    plant5("step0b tuple multisets differ", lambda d: d["step0b"].__setitem__("c_tuple_multiset_equal", False))
    plant5("a signal cell without denominator",
           lambda d: d["run"]["controls"]["C-COMPLETE"].__setitem__("n_signal_without_denominator", 1))
    plant5("one pT bin's flux 0.1% high",
           lambda d: d["constants"]["flux_per_m2_per_POT_by_pt_bin"].__setitem__(3, 1.001 * d["constants"]["flux_per_m2_per_POT_by_pt_bin"][3]))
    plant5("a c32 cell's difference sign flipped", lambda d: d["cells"].__setitem__(0, (d["cells"][0][0], -d["cells"][0][1])))
    plant5("a c32 cell dropped", lambda d: d["cells"].pop())
    plant5("c := 1 effect 4.0e-6", lambda d: d.__setitem__("c1", 4.0e-6))
    plant5("max |c - 1| 4.2e-4", lambda d: d["run"]["controls"]["C-COMPLETE"].__setitem__("max_abs_c_minus_1", 4.2e-4))
    # Joseph's two sentences of 2026-11-26: the outside-grid count, the code argument for its axes, and the phase space
    plant5("n_outside_grid 2802", lambda d: d["run"]["controls"]["C-FLOW"].__setitem__("n_outside_grid", 2802))
    plant5("C-FLOW rows not the truth-selected set",
           lambda d: d["run"]["controls"]["C-FLOW"].__setitem__("n_rows_equal_pass_truth", False))
    plant5("the grid's top pT edge 4.4", lambda d: d["constants"]["edges"]["pt"].__setitem__(-1, 4.4))
    plant5("a strict pT limit in the truth selection",
           lambda d: d["code"].__setitem__("u2d", d["code"]["u2d"].replace("pt_lo <= pt <= pt_hi", "pt_lo <= pt < pt_hi")))
    plant5("the dump given --pt-edges",
           lambda d: d["code"].__setitem__("sbatch", d["code"]["sbatch"].replace("--axes eavail", "--pt-edges 0,4.4 --axes eavail")))
    plant5("fine_index's last edge exclusive",
           lambda d: d["code"].__setitem__("decl", d["code"]["decl"].replace("last edge inclusive", "last edge exclusive")))
    plant5("the dump run with --full-phase-space",
           lambda d: d["code"].__setitem__("sbatch", d["code"]["sbatch"].replace("--axes eavail", "--full-phase-space --axes eavail")))
    plant5("another input npz", lambda d: d["constants"].__setitem__("input_npz_sha256", "00" + d["constants"]["input_npz_sha256"][2:]))
    plant5("no theta_mu gate in the selection",
           lambda d: d["code"].__setitem__("u2d", d["code"]["u2d"].replace("return math.atan2(pt, pz) < MAX_MUON_THETA_RAD", "return True")))
    trial = dict(base)        # Eq. (muon-fiducial) loses the muon-angle cut: the phase-space claim must fail
    trial["sec2_method.tex"] = base["sec2_method.tex"].replace(r"\theta_\mu<20^\circ,\quad", "")
    if all(r[1] for r in evw5d_claims(trial)):
        print("  NOT CAUGHT  EVW5D: Eq. (muon-fiducial) without the theta_mu cut"); ok = False
    else:
        caught += 1; print("  caught      EVW5D: Eq. (muon-fiducial) without the theta_mu cut")
    # The EVW2D claims: each sentence reworded, and each planted receipt, must be rejected.
    for old_s, new_s in (("reproduce the deposited 2D refined central values", "reproduce the deposited 2D central values"),
                         ("in the same order, as those of the sixteen-cell", "in another order, as those of the sixteen-cell"),
                         ("agree exactly in single precision.", "agree exactly."),
                         ("They are the same rows,", "They are the same physical events,"),
                         ("keyed by its entry number in the input file", "keyed by its run and event number"),
                         ("It also carries its prior weight.", "It also carries its uncertainty."),
                         ("with unchanged code and inputs.", "with updated code and inputs."),
                         ("so the completeness is 1 in any binning, and", "so the completeness is 1 on our grid, and"),
                         ("and the flux is a single integrated value.", "and the flux is binned in $p_T$."),
                         ("any binning in $p_T$ and $p_\\parallel$ inside", "any binning in $p_T$, $p_\\parallel$ and $E_{\\mathrm{avail}}$ inside"),
                         ("Only these two grids were compared", "Many grids were compared"),
                         ("The weights give central values only,", "The weights give central values and uncertainties,")):
        t = text("appD_reproducibility.tex", base)
        if t.count(old_s) != 1:
            print(f"  NOT FOUND   EVW2D mutation {old_s!r}"); ok = False; continue
        trial = dict(base)
        trial["appD_reproducibility.tex"] = t.replace(old_s, new_s)
        if all(r[1] for r in evaluate(trial)):
            print(f"  NOT CAUGHT  EVW2D: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      EVW2D: {old_s} -> {new_s}")

    def plant2(what, fn):
        global EVW2D_OVERRIDE
        nonlocal ok, caught
        data = copy.deepcopy(evw2d())
        fn(data)
        EVW2D_OVERRIDE = data
        try:
            rows = dict((r[0], r[1]) for r in evaluate(base))
        except (ValueError, KeyError, TypeError):
            rows = {"refused": False}
        finally:
            EVW2D_OVERRIDE = None
        if all(rows.values()):
            print(f"  NOT CAUGHT  EVW2D planted: {what}"); ok = False
        else:
            caught += 1; print(f"  caught      EVW2D planted: {what}")
    ctl = lambda d, k: d["run"]["controls"][k]
    plant2("controls verdict FAIL", lambda d: d["run"].__setitem__("controls_verdict", "FAIL"))
    plant2("upload manifest: result_2d.npz stale", lambda d: d.__setitem__("upload", d["upload"].replace("| 2,696,218 | current |", "| 2,696,218 | **STALE** |")))
    plant2("upload manifest: another result_2d.npz", lambda d: d.__setitem__("upload", d["upload"].replace("`9ab08a9f7d57c786", "`0ab08a9f7d57c786")))
    plant2("upload manifest: x not equal to er", lambda d: d.__setitem__("upload", d["upload"].replace("**bit for bit**: yes", "**bit for bit**: no")))
    plant2("upload manifest: er from another xsec.root", lambda d: d.__setitem__("upload", d["upload"].replace("from `xsec.root` `a5c13fc3", "from `xsec.root` `05c13fc3")))
    plant2("upload manifest: config pins other references", lambda d: d.__setitem__("upload", d["upload"].replace("pins `references.npz` at `1b214582", "pins `references.npz` at `0b214582")))
    plant2("same-events verdict DIFFERENT", lambda d: d.__setitem__("same", d["same"].replace("VERDICT SAME-ROWS-SAME-ORDER", "VERDICT DIFFERENT")))
    plant2("same-events one row off in float32", lambda d: d.__setitem__("same", d["same"].replace('"rows_over_1_ulp": 0}}', '"rows_over_1_ulp": 1}}')))
    plant2("same-events entries differ", lambda d: d.__setitem__("same", d["same"].replace('"entries_equal": true', '"entries_equal": false')))
    plant2("same-events exact in float64 too", lambda d: d.__setitem__("same", d["same"].replace('"max_abs_delta_float64": 2.381347563584768e-07', '"max_abs_delta_float64": 0.0').replace('"max_abs_delta_float64": 1.9073474462061313e-06', '"max_abs_delta_float64": 0.0')))
    plant2("same-events on another 5D weights file", lambda d: d.__setitem__("evw5d_hpss", d["evw5d_hpss"].replace("0fceefcd", "00ceefcd")))
    plant2("same-events T4 pT line short", lambda d: d.__setitem__("same", d["same"].replace("T4 truth_pt: exact 32849103/32849103", "T4 truth_pt: exact 32849102/32849103")))
    plant2("refinement clipped events", lambda d: d.__setitem__("log", d["log"].replace("clipped(2g-1<0) 0 events", "clipped(2g-1<0) 7 events")))
    plant2("refinement score below 0.5", lambda d: d.__setitem__("log", d["log"].replace("g in [0.533,", "g in [0.473,")))
    plant2("refinement score 0.54", lambda d: d.__setitem__("log", d["log"].replace("g in [0.533,", "g in [0.543,")))

    def plant3(what, fn):
        global REGRADE_VF_OVERRIDE
        nonlocal ok, caught
        data = copy.deepcopy(regrade_vf())
        fn(data)
        REGRADE_VF_OVERRIDE = data
        try:
            rows = dict((r[0], r[1]) for r in evaluate(base))
        except (ValueError, KeyError, TypeError):
            rows = {"refused": False}
        finally:
            REGRADE_VF_OVERRIDE = None
        if all(rows.values()):
            print(f"  NOT CAUGHT  REGRADE-VF planted: {what}"); ok = False
        else:
            caught += 1; print(f"  caught      REGRADE-VF planted: {what}")
    ev = lambda d, k, r: d["rec"]["evaluations"][k][r]
    plant3("record not the committed one", lambda d: d.__setitem__("sha256", "0" * 64))
    plant3("another declaration revision", lambda d: d["rec"].__setitem__("declaration", "REGRADE-VF-DECLARATION.md rev 2"))
    plant3("G18 bias not resolved", lambda d: ev(d, "g18/minus2", "rule_i")["readings"].__setitem__("bias_resolved", "not resolved"))
    plant3("AR23 bias within 3 SE", lambda d: ev(d, "ar23/minus2", "rule_i").__setitem__("B", 2.9 * ev(d, "ar23/minus2", "rule_i")["se_boot"]["B"]))
    plant3("AR23 not separated", lambda d: ev(d, "ar23/minus2", "rule_i")["readings"].__setitem__("bias_vs_fluctuation", "not separated"))
    plant3("G18 bias larger", lambda d: ev(d, "g18/minus2", "rule_i")["readings"].__setitem__("bias_vs_fluctuation", "bias larger"))
    plant3("AR23 fall 0.80", lambda d: ev(d, "ar23/minus2", "rule_i").__setitem__("B", 0.20 * ev(d, "ar23/minus2", "before")["B"]))
    plant3("G18 fall 0.30", lambda d: ev(d, "g18/minus2", "rule_i").__setitem__("B", 0.70 * ev(d, "g18/minus2", "before")["B"]))
    plant3("before is not C_rep,0 (M_full 3.0)", lambda d: ev(d, "ar23/minus2", "before").__setitem__("M_full", 3.0))
    plant3("declaration drops the circularity", lambda d: d.__setitem__("decl", d["decl"].replace("The draws here are the same draws C_e^infl was fitted to.", "")))
    for old_s, new_s in (("about two thirds at the first", "about three quarters at the first"),
                         ("by about half at the second", "by about a third at the second"),
                         ("at the first tune, and less at the second", "at the second tune, and less at the first"),
                         ("still clearly nonzero at both tunes", "consistent with zero at both tunes"),
                         ("this is a consistency check, not a coverage test", "this is a coverage test")):
        t5 = base["sec5_multidim.tex"]
        if t5.count(old_s) != 1:
            print(f"  NOT FOUND   REGRADE-VF mutation {old_s!r}"); ok = False; continue
        trial = dict(base)
        trial["sec5_multidim.tex"] = t5.replace(old_s, new_s)
        if all(r[1] for r in evaluate(trial)):
            print(f"  NOT CAUGHT  REGRADE-VF: {old_s} -> {new_s}"); ok = False
        else:
            caught += 1; print(f"  caught      REGRADE-VF: {old_s} -> {new_s}")
    plant2("evw2d.done verdict FAIL", lambda d: d["done"].__setitem__("verdict", "FAIL"))
    plant2("a finding recorded", lambda d: d["run"].__setitem__("findings", ["C-COMPLETE"]))
    plant2("deposit copy not accepted", lambda d: d.__setitem__("deposit", d["deposit"].replace("ACCEPTED", "REFUSED")))
    plant2("another weights.npz in the deposit", lambda d: d["run"]["files_sha256"].__setitem__("weights.npz", "00" + d["run"]["files_sha256"]["weights.npz"][2:]))
    plant2("C-KEY rows one more", lambda d: ctl(d, "C-KEY").__setitem__("rows", ctl(d, "C-KEY")["rows"] + 1))
    plant2("key in another file", lambda d: d["constants"]["key"].__setitem__("omnifile_sha256", "00" + d["constants"]["key"]["omnifile_sha256"][2:]))
    plant2("no w_prior column", lambda d: d["constants"].__setitem__("columns", [c for c in d["constants"]["columns"] if c != "w_prior"]))
    plant2("a pinned file changed", lambda d: ctl(d, "C-PINS").__setitem__("pass", False))
    plant2("another CV input", lambda d: d["run"]["inputs_sha256"].__setitem__("CV", "00" + d["run"]["inputs_sha256"]["CV"][2:]))
    plant2("another argv", lambda d: d["run"].__setitem__("argv", d["run"]["argv"][:-2]))
    plant2("the declaration's unchanged-driver line edited", lambda d: d["code"].__setitem__("decl", d["code"]["decl"].replace("**One run of E_R's driver, unchanged:**", "**One run of E_R's driver, modified:**")))
    plant2("denominator rows differ", lambda d: ctl(d, "C-COMPLETE").__setitem__("denominator_rows", ctl(d, "C-COMPLETE")["denominator_rows"] - 1))
    plant2("flux spread two ulp", lambda d: ctl(d, "C-FLUX").__setitem__("spread", 2 * ctl(d, "C-FLUX")["ulp"]))
    plant2("phase space without the angle cut", lambda d: d["constants"]["constants"]["phase_space"].__setitem__("theta_max_deg", 90.0))
    plant2("a third validated grid", lambda d: d["constants"]["constants"]["validated_grids"].__setitem__("other", [0.0, 4.5]))
    plant2("validity says any grid", lambda d: d["constants"]["constants"].__setitem__("validity", "the central value; validated on any grid"))
    plant2("C-EXACT-ER max_rel 1.2e-11", lambda d: ctl(d, "C-EXACT-ER").__setitem__("max_rel", 1.2e-11))
    plant2("C-EXACT-PAPER on 204 cells", lambda d: ctl(d, "C-EXACT-PAPER").__setitem__("cells", 204))
    plant2("the run under another config", lambda d: d["run"].__setitem__("config_sha256", "00" + d["run"]["config_sha256"][2:]))
    plant2("config pins other references", lambda d: d["config"]["references"].__setitem__("sha256", "00" + d["config"]["references"]["sha256"][2:]))
    plant2("references er not E_R", lambda d: d["ref_meta"]["er"].__setitem__("sha256", "00" + d["ref_meta"]["er"]["sha256"][2:]))
    plant2("references paper not Tier 1's e", lambda d: d["ref_meta"]["paper"].__setitem__("sha256", "00" + d["ref_meta"]["paper"]["sha256"][2:]))
    plant2("E_R not the adopted result", lambda d: d["code"].__setitem__("decision", d["code"]["decision"].replace("adopt the refined 2D result E_R", "keep the earlier 2D result E_U")))
    plant2("regenA's E from another file", lambda d: d["code"].__setitem__("regenA", d["code"]["regenA"].replace("E: tier1/units_e/er.root (5171c7b8).", "E: tier1/units_e/er.root (00000000).")))
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
