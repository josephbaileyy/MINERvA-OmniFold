#!/usr/bin/env python3
"""Generate values_fived16.tex: every printed number of the sixteen-cell five-observable result, from committed readouts.

usage: make_values_fived16.py [--check | --self-test]     (run from the repository root or anywhere inside it)

Each readout is pinned by sha256 in READOUTS; a mismatch stops the run. Every number becomes one key of \\fvval{<key>},
formatted at its printed precision here, so no printed number is typed by hand.
The reported covariance is C_total + C_resp + C_PL,5D (DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md item 2;
PROPOSAL-20261031-5b-with-without.md): READOUTS pins the with-block readouts (fd/with-cpl/, FD-CT-5B-ADDITION-REPORT.md),
and NOPL_READOUTS the committed ones without the block. Every key whose value differs without the block is also written
with the suffix "-nopl", and a key outside the matrix-dependent families that differs stops the run. --check fails unless the committed
values_fived16.tex equals a fresh generation (the build and CI run it, as for records_entry_numbers.tex).
"""
import ast
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=Path(__file__).parent)
# outside a git checkout (an exported copy) the repository root is two levels above docs/analysis-note
ROOT = Path(_top.stdout.strip()) if _top.returncode == 0 else Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("values_fived16.tex")
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
RSN = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/referee-sensitivity-20261111/connect-post/run-20261112"
READOUTS = {
    "h2": ("nd-unfolding/pv-ladder/readouts/h2_definition.json", "b6790761"),
    "stage1": ("docs/orchestration/state/s5p/stage1/stage1_inspect.json", "def4c67c"),
    "cmodel": ("nd-unfolding/pv-ladder/readouts/cmodel_5d.json", "3cfdc6a5"),
    "s1": (f"{FD}/s1/readout/s1_assembly.json", "81e5ef3f"),
    "cresp": ("docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json", "19bb2ee1"),
    "f0": (f"{FD}/fd/readout/fd_f0_readout.json", "6e7d718b"),
    # with the run-period block: the with arm of FD-CT-5B-ADDITION-REPORT.md section 3
    "f0b": (f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json", "5f542830"),
    # Stage G's chain on Table IV's predictions (GENCMP amendment E, E-1 rerun1; FD-GENCMP-AMENDMENT-E-REPORT.md sec. 3.1)
    "g": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json", "a19009e0"),
    "diag": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_diag_readout.json", "522bfafa"),
    "fup": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_followup_readout.json", "586cd741"),
    "sens2": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_sens2_readout.json", "4bc21dfd"),
    "dp": (f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json", "d6752d2c"),
    "gagg": (f"{FD}/fd/readout/fd_gibuu_enu_aggregate.json", "66dcbd6d"),
    "fboot": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_flux_boot_readout.json", "5bb475ea"),  # 3D (PR #438), with the block
    "f1": (f"{FD}/fd/with-cpl/readout/fd_f1_readout.json", "5ccc89e5"),              # 1A (PR #446), with the block
    # the two tunes' generation records, for their names; their digests are the F1c pin's f1b3-SHA256SUMS
    "f1meta-g18": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/gen5d/genie_v3_g18_xsec5d.meta.json", "4fe333b8"),
    "f1meta-ar23": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/gen5d/genie_v3_ar23_xsec5d.meta.json", "d7d136e5"),
    # the pion-constant departure of Eq. (1), as full-covariance norms of its first-order shift under each arm's matrix
    # (ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md section 7.3; JSON despite the suffix)
    "eav": ("docs/orchestration/state/eavail-switch-pricing-20261031/step0/step0_metric.txt", "3e8bd546"),
    # the same switch at prior level on the analysis's seven fine E_avail bins (that record's section 7.2)
    "eav0": ("docs/orchestration/state/eavail-switch-pricing-20261031/step0/step0.json", "c284a6b3"),
    # the stopped 1B coverage test: gate D (FD-1B-STAGE2-REPORT.md section 4.1) and its diagnosis (FD-1B-DIAG-REPORT.md)
    "gated": (f"{FD}/fd/receipts-1b/stage2/run/score/gate-d.json", "e1838c0a"),
    "diag1b": (f"{FD}/fd/receipts-1b/diag/diag.json", "6fd6669e"),
    # why C_model's coverage is not validated (DECISION-20261024-joseph-5d-community-standard-route.md item 3): the binding
    # Stage 0 (5d-design-20261023/STAGE0-REPORT.md) and the reconstruction-information test R10 (measurement-scoping/r10)
    "stage0": ("docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/receipts-A/stage0-binding.json", "df70af43"),
    "r10": ("docs/orchestration/state/measurement-scoping/r10/outputs/r10_results.json", "dafcc55e"),
    # GENCMP (FD-GENCMP-REPORT.md; DECISION-20261101-joseph-gencmp-paper-adoption.md items 1-4): step B's 2 x 2 table,
    # whose corner "CH, analysis definitions" is Table IV's; step A's GENIE-hydrogen sensitivity; step D's native NuWro
    # on CH, with the probe's diagnostic (a text receipt); and step C's 3D quadrant sums (the note only)
    "gdefs": (f"{FD}/fd/gencmp/readout/defs.json", "544f4f43"),
    "gch": (f"{FD}/fd/gencmp/readout/ch.json", "cd111b8e"),
    "gnat": (f"{FD}/fd/gencmp/readout/native.json", "df48fbeb"),
    "gprobe": (f"{FD}/fd/gencmp/receipts/d_projection.txt", "2df2a897"),
    # the code that groups S1's blocks into the per-group columns (referee round 20261104, item 2: the paper's source
    # list), at fe5d79c61; read as text and parsed, never imported
    "s1code": ("nd-unfolding/s1_assemble.py", "b157250a"),
    # 3b's descriptive response-mismatch closures (FD-CT-3B-REPORT.md :79, :96-118; referee round 20261104, Joseph's
    # addition b0: printed as a bounded statement, descriptive, with no pass threshold)
    "ct3b": (f"{FD}/fd/readout/fd_ct_mismatch.json", "14399419"),
    "gover": (f"{FD}/fd/gencmp/readout/overlap.json", "82b3528a"),
    # Stage G as first made, on the predictions in their generator definitions with NuWro and GiBUU on carbon (the
    # with arm of FD-CT-5B-ADDITION-REPORT.md section 3), for the note's table of that comparison only
    "g0": (f"{FD}/fd/with-cpl/readout/fd_g_readout.json", "b55366b3"),
    # GENCMP addendum E2 (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md sec. 3 and 5;
    # DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md): the chi2 of Table IV's four predictions with C_model's
    # NuWro and GiBUU shape ratios from CH, and C_model removed and doubled, with the per-cell sigma (a text receipt). Each
    # holds both arms, so both arms read the same files
    "e2": (f"{FD}/fd/gencmp-e2/rerun1/chi2/e2.json", "0aa73ebf"),
    "e2sens": (f"{FD}/fd/gencmp-e2/rerun1/sens/x_e2_sens.out.txt", "223f3f88"),
    # the quadrant sums against the adopted 2D result (DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md
    # item 1): step C-R's bound rule (FD-GENCMP-AMENDMENT-E-REPORT.md sec. 3.2) and GENCMP X's cross-covariance test
    # (FD-GENCMP-X-REPORT.md sec. 1). Each is computed once, from the reported matrix, so both arms read the same files
    # cr under C_new (the director's XCOV ruling and approval of 2026-11-16): #1169's g2r arm, the same command on route A's
    # Q_R (fd/receipts-cov2d/g2r/cr/README.md; run/node/out.sha256.txt lists it). Before, GENCMP step C-R on partc-r2's
    # Q_R: fd/gencmp-e/c-r/overlap_refined.json (f1f2fb78)
    "cr": (f"{FD}/fd/receipts-cov2d/g2r/cr/run/node/g2r/overlap_refined.json", "0734cf4a"),
    # xk under C_new (the director's XCOV ruling, 2026-11-16): #1170's `k --products g2r`, GENCMP X step K on COV2D-G2R's
    # products (fd/receipts-cov2d/g2r/xk/README.md; run/node/out.sha256.txt lists it; its control reproduced f3dc2a34 byte
    # for byte). Before, step K as it ran: fd/xcov/run/k/k.json (f3dc2a34)
    "xk": (f"{FD}/fd/receipts-cov2d/g2r/xk/run/node/run/k/k.json", "204e4c89"),
    # the run-period diagnosis's readout (FD-RPD-DECLARATION.md sec. 5; DECISION-20261104-joseph-rpd-sentence.md item 2),
    # computed once from the per-playlist unfolds, so both arms read the same file
    "rpd": (f"{FD}/fd/receipts-rpd/run/readout/fd_rpd.json", "c0b06cfd"),
    # LL5D, the second five-observable coverage test (ported 2026-11-16 from the paper branch's make_values_fived16.py at
    # draft/methods-short-20261109 037431430, same paths and pins; ll5d_port_values below): its readout (#1157; job
    # 61272425; nd-unfolding/ll5d_b.py readout_reading) at each truth, and its declaration (text)
    "ll5dg18": (f"{FD}/fd/receipts-ll5d/readout/node/readout-g18.json", "7bd6d390"),
    "ll5dar23": (f"{FD}/fd/receipts-ll5d/readout/node/readout-ar23.json", "5b3fbbf5"),
    "ll5ddecl": (f"{FD}/LL5D-DECLARATION.md", "6748d418"),
    # The note's currency UPDATEs (the currency check of 2fe070fec, U1-U15; the combined plan section 6, Joseph's
    # approval of 2026-11-17): ported from the paper branch's make_values_fived16.py at draft/methods-short-20261109
    # 5bbb9d269, same paths and pins; currency_values() below
    "prr": (f"{FD}/fd/receipts-prr/read/cluster/readout.json", "9238f22b"),
    "vhalf": ("docs/orchestration/state/2d-closeout/valid-region-20261107/v-half/receipts/read/readout.json", "e7423390"),
    "ll5dmumax": (f"{FD}/fd/receipts-ll5d/mumax/run/node/mumax.json", "422db056"),
    "ens1s1": (f"{FD}/fd/rounding-stability-20261106/ensemble/receipts/stage1-a1-analysis/ens1_stage1.json", "7f5a9ce4"),
    "ens1s2": (f"{FD}/fd/rounding-stability-20261106/ensemble/receipts/stage2-a1-analysis/ens1_stage2.json", "c2ee701d"),
    "c2c1": (f"{FD}/fd/receipts-ref-c2c1/step2/read-2/readout.json", "0ee21301"),
    "refg1": (f"{FD}/fd/receipts-ref-g1/a1-read/readout.json", "4db170d3"),
    "t2b": (f"{FD}/fd/tier2-20261110/t2b/t2b.json", "0e281a61"),
    "t2aar23": (f"{FD}/fd/receipts-cov2d/g2r/t2a/run/t2a_g2r_AR23.json", "74fab014"),
    "t2ag18": (f"{FD}/fd/receipts-cov2d/g2r/t2a/run/t2a_g2r_G18.json", "b1310d44"),
    "cov2dar23": (f"{FD}/fd/receipts-cov2d/g2r/readout/AR23/score_g2r_AR23.json", "fb6d1f7f"),
    "cov2dg18": (f"{FD}/fd/receipts-cov2d/g2r/readout/G18/score_g2r_G18.json", "27374aab"),
    "rs1r0": (f"{FD}/fd/rounding-stability-20261106/receipts/full-a1/read/rs1_r0.json", "724f0c3a"),
    "rs1read": (f"{FD}/fd/rounding-stability-20261106/receipts/full-a1/read/rs1_read.json", "9938e168"),
    "runper": ("docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/lrows-g/g4-runperiod/runperiod_values.json", "f63074b1"),
    "rsn": (f"{RSN}/rsn_readout.json", "6291f48d"),
    "rsnregrade": (f"{RSN}/regrade.json", "cb5f5d17"),
    "e96d": (f"{FD}/fd/e96-data-20261110/receipts/a1-run-20261112/cluster/analysis/ANALYSIS.json.txt", "b42208ef"),
    # U6: the figure referee read's check A (on main by #1213, e13d98d55)
    "recov": ("docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-figure-deformation-20261112/check-a/a_recovery.json", "75db95a1"),
}
# the committed readouts without the run-period block, for the "-nopl" keys
NOPL_READOUTS = dict(READOUTS, **{
    "f0b": (f"{FD}/fd/readout/fd_f0b_readout.json", "b9db935a"),
    "g": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_readout.json", "d9a1ce38"),
    "diag": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_diag_readout.json", "4e77966e"),
    "fup": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_followup_readout.json", "748f3af6"),
    "sens2": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_sens2_readout.json", "6626cb73"),
    "dp": (f"{FD}/fd/data-product/fd_data_product.json", "b79556f0"),
    "fboot": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_flux_boot_readout.json", "24ff27f9"),
    "f1": (f"{FD}/fd/readout/fd_f1_readout.json", "cbe411a9"),
    "g0": (f"{FD}/fd/readout/fd_g_readout.json", "75a9ddee"),
})
# each arm's names for its reported matrix and for the block the chain adds to C_total
ARMS = {"with": {"dp": "C_total_plus_C_resp_plus_C_PL5D", "rep": "C_total + C_resp + C_PL5D", "x": "C_resp + C_PL5D",
                 "f1sig": "relative_sigma_plus_C_resp + C_PL5D"},
        "without": {"dp": "C_total_plus_C_resp", "rep": "C_total + C_resp", "x": "C_resp",
                    "f1sig": "relative_sigma_plus_C_resp"}}
# the key families whose values depend on the reported matrix; any other key must be equal in the two arms
MATRIX_KEYS = re.compile(r"^(g-|gs-|f0b-|f1-|fb-|sens-|diag-|r04-|corr-|eav-|sig(med|min|max)?1?-(reported|C_PL5D)|trig-)")
# the paper's precision (referee round 20261104, item 6): a fake-data chi2 as an integer, as Table IV prints its chi2
# (DECISION-20261027-joseph-chi2-table-format.md), and a p-value below 1e-3 as the power of ten it lies below; the note
# keeps the exact values. Keys: <key>int for "-chi2", "-pr" (the value) and "-prel" (with its relation) for "-p"
PAPER_PREC = re.compile(r"^(f0b?|f1)-.+-(chi2|p)(-nopl)?$")


def paper_prec(k, x):
    """The paper's form(s) of value x of key k: {new key: text}. A chi2 printed at a half (x.50) cannot be rounded from
    its print and gets no integer key, so a paper that prints one stops the build at the unknown key."""
    if re.search(r"-chi2(-nopl)?$", k):
        assert re.fullmatch(r"\d+\.\d\d", x), f"{k}: {x!r}"
        if x.endswith(".50"):
            return {}
        return {re.sub(r"-chi2(?=(-nopl)?$)", "-chi2int", k): f"{float(x):.0f}"}
    m = re.fullmatch(r"(\d\.\d)\\times10\^\{(-\d+)\}", x)
    if m:                # p = m x 10^e with 1 <= m < 10 lies below 10^(e+1)
        assert 1 <= float(m[1]) < 10, f"{k}: {x!r}"
        pr = rf"<10^{{{int(m[2]) + 1}}}"
    else:
        assert x.startswith("<") or float(x) >= 1e-3, f"{k}: {x!r}"
        pr = x
    base = re.sub(r"-p(?=(-nopl)?$)", "-pr", k)
    i = base.rfind("-pr")
    return {base: pr, base[:i] + "-prel" + base[i + 3:]: pr if pr.startswith("<") else "=" + pr}
# the figures the note and the paper print, copied into figures/: each must equal its committed source (with the block)
# and the digest its sidecar records (FD-G-FIGURES-REPORT.md section 1; FD-CT-5B-ADDITION-REPORT.md section 3)
# Both are E-1's with-arm figures as addendum E-A2 redrew them, from the same readouts, without the hydrogen flags on
# the legend (FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2-REPORT.md, #712; the caveat cut list's move MV07F)
FIGURES = {"fd_g_fig_ratio.pdf": ("fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2", "6214ed78"),
           "fd_g_fig_modes.pdf": ("fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2", "0d6fe57c")}
# the readouts that are text receipts, not JSON
TEXT_READOUTS = {"gprobe", "e2sens", "s1code", "ll5ddecl"}
CELLS = [f"R{i:02d}" for i in range(16)]
BLOCK = {"stat": "statistical", "interaction": "interaction", "flux": "flux", "detector": "detector",
         "lateral": "lateral", "normalization": "normalization", "seed": "training seed", "C_resp": r"$C_{\mathrm{resp}}$",
         "V_g": r"$V_g$", "C_model:genie_mec": r"$C_{\mathrm{model}}$ (GENIE + MEC)",
         "C_model:nuwro": r"$C_{\mathrm{model}}$ (NuWro)", "C_model:gibuu": r"$C_{\mathrm{model}}$ (GiBUU)"}
PRED = {"genie_cv": "gcv", "genie_mec": "gmec", "nuwro": "nuwro", "gibuu": "gibuu", "mnvtune_v1": "tune"}
# each graded fake-data truth's printed name (for the generated list) and the words a sentence uses for it (for the check)
TRUTH_LABEL = {"nominal": ("the simulation prior", "simulation prior"),
               "W1": (r"the NuWro $\Eavail$ shape", r"NuWro $\Eavail$ shape"),
               "W2": (r"the GENIE + MEC $(\Eavail,W)$ shape", r"$(\Eavail,W)$ shape"),
               "W3": (r"the NuWro $(\pT,\pPar,\Eavail)$ shape", r"$(\pT,\pPar,\Eavail)$ shape"),
               "q3": (r"the synthetic $q_3$ tilt", r"$q_3$ tilt"),
               "stage0c_gibuu": (r"the GiBUU $\Eavail$ shape", r"GiBUU $\Eavail$ shape"),
               "closure_nuwro": ("the NuWro closure", "NuWro closure"),
               "A7_mnvtune": (r"the Tune~v1 hybrid truth", r"Tune~v1 hybrid"),
               "A7_genie_cv": ("the GENIE CV hybrid truth", "GENIE CV hybrid"),
               "A7_genie_mec": ("the GENIE + MEC hybrid truth", "GENIE + MEC hybrid"),
               "A7_nuwro": ("the NuWro hybrid truth", "NuWro hybrid"),
               "A7_gibuu": ("the GiBUU hybrid truth", "GiBUU hybrid")}
# Every printed sentence that states which F0b truths are listed, under the reported covariance or without the run-period
# block. A re-pinned readout changes those sets while the hand-typed names stay, so generation and --check fail unless
# each sentence agrees with the pinned F0b readouts' triggers.listed (with the block: READOUTS; without: NOPL_READOUTS):
#   "keys": the truths its \fvval{f0b-<truth>-...} keys name, and the names it types, equal the listed set with the block;
#   "without": it names (types) every truth listed only without the block, and every truth it names or keys is listed
#              without the block;
#   "both": the truths it types (of the family, if given) equal the truths listed with or without the block;
#   "count": exactly `gibuu` GiBUU truths are listed with the block, and every truth in `also`.
#   "ctotal": the truths it types equal F0's listed set, under C_total alone (Table I's right-hand columns).
# The anchor is the sentence's distinguishing clause; a missing anchor fails, so a moved sentence must be re-declared.
LISTED_CLAIMS = [
    ("paper_body.tex", "the flagged truths ($p<", {"kind": "keys"}),
    ("paper_body.tex", "also meets the flagging criterion", {"kind": "without"}),
    ("paper_body.tex", "Thus the fake-data bias exceeds the stated thresholds", {"kind": "both"}),
    ("paper_body.tex", r"Under $C_{\mathrm{total}}$ alone, the right-hand columns", {"kind": "ctotal"}),
    ("sec_q3_fived16.tex", "truths meet the listing criterion ($p<", {"kind": "keys"}),
    ("sec_q3_fived16.tex", "truths meet it: the GiBUU", {"kind": "without"}),
    ("sec_q3_fived16.tex", "The fake-data bias therefore exceeds the stated thresholds", {"kind": "both"}),
    ("sec_fived16_gen.tex", "so the GiBUU comparison carries that limitation", {"kind": "both", "family": "gibuu"}),
    ("main_paper.tex", "at a GiBUU-like truth and at a synthetic momentum-transfer tilt find", {"kind": "count", "gibuu": 1, "also": ["q3"]}),
    # main_note.tex: the abstract sentence re-declared when the note was reframed and its fake-data sentence resynced to the
    # paper's (note round 1, N1 + N6; DECISION-20261108-joseph-note-framing-and-estimator-dependence.md, #947)
    ("main_note.tex", "Fake-data studies at a GiBUU-like truth and at a synthetic momentum-transfer tilt find", {"kind": "count", "gibuu": 1, "also": ["q3"]}),
]


def load(readouts=None):
    data = {}
    for key, (rel, pin) in (READOUTS if readouts is None else readouts).items():
        raw = (ROOT / rel).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if not sha.startswith(pin):
            sys.exit(f"make_values_fived16: {rel} has sha256 {sha[:12]}, pinned {pin}: refusing")
        data[key] = raw.decode() if key in TEXT_READOUTS else json.loads(raw)
    return data


def pct(x):              # a relative sigma (fraction) as a percent, two decimals
    return f"{100 * x:.2f}"


def pct1(x):             # the paper's precision (Appendix A tables; referee round 20261104, PRD read 1 R8): one decimal
    return f"{100 * x:.1f}"


def p_tex(p):            # a p-value: two significant figures, scientific below 1e-3
    if p == 0:           # underflow: F0's readout records it as below its 1e-30 floor (FD-F0-REPORT section 0)
        return r"<10^{-30}"
    if p >= 1e-3:
        return f"{p:.2g}" if p < 0.1 else f"{p:.2f}"
    m, e = f"{p:.1e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"

GENCMP4 = ("genie_cv", "genie_mec", "nuwro", "gibuu")      # the four predictions GENCMP rebuilt


def short_label(p):      # a Stage G readout's own name for a prediction, as the tables print it
    name = p["label"].split(";")[0].split(",")[0]
    return "MINERvA Tune~v1" if name == "MINERvA Tune v1" else name.replace(" ", "~", 1)


def table4(d, arm):
    """Table IV's five predictions in this arm's matrix, each with total, shape_only, cells, pulls and g_over_f_minus_1:
    for GENIE CV, GENIE + MEC, NuWro and GiBUU, GENCMP's corner "CH, analysis definitions" (defs.json), every sample of
    which passed B0, and B2 where it applies ("n/a" for the samples B2 does not test), and is complete; for MINERvA Tune v1, Stage G's record. The data side (cells, f, sigma, ndf)
    must be Stage G's, so only the predictions differ. Stage G's chain ran on these four records (GENCMP amendment E), so
    its g and chi2 must equal them (E-1's control XC)."""
    mat = "reported" if arm == "with" else "without_C_PL5D"
    gd = d["gdefs"]
    assert gd["schema"] == "fd-gencmp-defs/1" and gd["not_read"] == []
    assert all(st["B0"] is True and st["complete"] is True and st["B2"] in ("pass", "n/a") for st in gd["status"].values())
    sg = {p["name"]: p for p in d["g"]["predictions"]}
    out = {}
    for name in PRED:
        if name not in GENCMP4:
            out[name] = sg[name]
            continue
        rec = gd["generators"][name]["CH"]["analysis_definitions"]["chi2"][mat]
        corner = gd["table_2x2"][name]["CH"]["analysis_definitions"][mat]
        assert all(rec[part]["chi2"] == corner[part] for part in ("total", "shape_only")), f"{name}: not the 2 x 2 corner"
        s = sg[name]
        assert rec["cells"] == s["cells"], f"{name}: the cells differ from Stage G's"
        assert max(abs(a / b - 1) for a, b in zip(rec["f"], s["f"])) < 1e-12, f"{name}: f differs from Stage G's"
        assert max(abs(a / b - 1) for a, b in zip(rec["sigma_total_over_f"], s["sigma_total_over_f"])) < 1e-10, \
            f"{name}: the reported sigma differs from Stage G's"
        assert all(rec[part]["ndf"] == s[part]["ndf"] for part in ("total", "shape_only"))
        assert max(abs(a / b - 1) for a, b in zip(rec["g"], s["g"])) < 1e-12, f"{name}: Stage G's g is not the corner's"
        assert all(abs(rec[part]["chi2"] / s[part]["chi2"] - 1) < 1e-12 for part in ("total", "shape_only")), \
            f"{name}: Stage G's chi2 is not the corner's"
        out[name] = rec
    return out


def gencmp_values(d, arm):
    """The GENCMP numbers the text and the note print beside Table IV (DECISION-20261101-joseph-gencmp-paper-adoption.md
    items 1-4). Each fact a sentence states about them is asserted, so a changed readout stops the run."""
    mat = "reported" if arm == "with" else "without_C_PL5D"
    gd, gc, gn = d["gdefs"], d["gch"], d["gnat"]
    v = {}
    # Q10: the largest per-cell change from the generators' to the analysis definitions over Table IV's four rebuilt
    # predictions, in units of the cell's reported sigma, and the bound the sentence prints (ceiled); the decision fixed
    # both figures, so a re-pinned readout that moves them stops here
    dmax = max(abs(x) for n in GENCMP4 for x in gd["generators"][n]["CH"]["delta_over_sigma"])
    v["gdef-dmax"], v["gdef-dmax-bound"] = f"{dmax:.3f}", f"{math.ceil(100 * dmax) / 100:.2f}"
    assert (v["gdef-dmax"], v["gdef-dmax-bound"]) == ("0.063", "0.07"), "the method sentence's figures changed"
    assert not any(gd["generators"][n]["CH"]["seed_spread_flag"] for n in GENCMP4)
    v["gdef-seedmax"] = f"{max(x for n in GENCMP4 for x in gd['generators'][n]['CH']['seed_spread_over_sigma']):.3f}"
    # Q08: NuWro and GiBUU on carbon in the analysis definitions (the text and the note), and the change to CH
    ana = {(n, t): gd["generators"][n][t]["analysis_definitions"]["chi2"][mat] for n in ("nuwro", "gibuu")
           for t in ("carbon", "CH")}
    for n in ("nuwro", "gibuu"):
        for part in ("total", "shape_only"):
            x = ana[n, "carbon"][part]["chi2"]
            v[f"g-{PRED[n]}-carbon-{part}-chi2"], v[f"g-{PRED[n]}-carbon-{part}-chi2int"] = f"{x:.2f}", f"{x:.0f}"
            v[f"g-{PRED[n]}-carbon-{part}-chi2r1"] = f"{x:.1f}"
    rise = ana["gibuu", "CH"]["total"]["chi2"] - ana["gibuu", "carbon"]["total"]["chi2"]
    assert rise > 0 and ana["gibuu", "CH"]["shape_only"]["chi2"] < ana["gibuu", "carbon"]["shape_only"]["chi2"], \
        "the clause says GiBUU's total chi2 rises with the correction and its shape-only chi2 falls"
    assert ana["nuwro", "CH"]["total"]["chi2"] < ana["nuwro", "carbon"]["total"]["chi2"], "NuWro's total chi2 falls"
    v["g-gibuu-chrise"] = f"{rise:.1f}"
    # step A's GENIE-hydrogen sensitivity, in the generators' own definitions (never the primary): for GiBUU the sign of
    # the change follows the hydrogen sample, below carbon with GENIE's, above it with its own
    for n in ("nuwro", "gibuu"):
        g = gc["generators"][n]
        assert "never the primary" in g["CH_genie_hydrogen"]["label"]
        for t, tag in (("carbon", "gen-carbon"), ("CH", "gen-ch"), ("CH_genie_hydrogen", "genieh")):
            for part in ("total", "shape_only"):
                x = g[t]["chi2"][mat][part]["chi2"]
                v[f"g-{PRED[n]}-{tag}-{part}-chi2"], v[f"g-{PRED[n]}-{tag}-{part}-chi2r1"] = f"{x:.2f}", f"{x:.1f}"
    gg = {t: gc["generators"]["gibuu"][t]["chi2"][mat]["total"]["chi2"] for t in ("carbon", "CH", "CH_genie_hydrogen")}
    assert gg["CH_genie_hydrogen"] < gg["carbon"] < gg["CH"], "GiBUU's sign no longer depends on the hydrogen sample"
    # the hydrogen label of GiBUU's table note, parsed from the readout (MP3-C's label and binding addendum 9 sec. 4),
    # and the hydrogen weight. Only NuWro's combination label states the weight ("12:1 per nucleon"), so only it is
    # asserted here; GiBUU's is the same construction by FD-GENCMP-DECLARATION.md sec. 2, which no GiBUU readout states
    lab = gd["generators"]["gibuu"]["CH"]["label"]
    assert lab == gc["generators"]["gibuu"]["CH"]["label"]
    m = re.fullmatch(r"B3 \(sampling closure\) failed on hydrogen; a post-hoc bias check of its premise passed at <= "
                     r"([\d.]+) sigma_c; (\d+)% of the hydrogen sample is DIS that does not conserve energy "
                     r"\(binding addendum 9 section 4\)", lab)
    assert m, "GiBUU's hydrogen label changed"
    v["g-gibuu-hlab-sigc"], v["g-gibuu-hlab-dis"] = m.groups()
    m = re.search(r"(\d+):(\d+) per nucleon", gd["generators"]["nuwro"]["CH"]["label"])
    assert m and m.groups() == ("12", "1"), "NuWro's combination is not 12:1 per nucleon"
    v["g-ch-hweight"] = r"1/13"
    # Q08, step D: native NuWro on CH against the combination, on both routes, under the rule fixed in advance
    assert gn["agree"] is True
    for route, tag in (("generator_definitions", "gen"), ("analysis_definitions", "ana")):
        r = gn[route]["rule"]
        assert r["agree"] is True and len(r["z"]) == 16
        m = re.fullmatch(r"agree: sum z\^2 over the cells < ([\d.]+) \(chi2_16 0\.99 quantile\) and no \|z\| > ([\d.]+)",
                         r["rule"])
        assert m and r["sum_z2"] < float(m.group(1)) and r["max_abs_z"] <= float(m.group(2))
        v["gnat-rule-sumz2"], v["gnat-rule-zmax"] = m.groups()
        v[f"gnat-{tag}-sumz2"], v[f"gnat-{tag}-zmax"] = f"{r['sum_z2']:.1f}", f"{r['max_abs_z']:.1f}"
        for part in ("total", "shape_only"):
            v[f"g-nuwro-native-{tag}-{part}-chi2"] = f"{gn[route]['native_chi2'][mat][part]['chi2']:.2f}"
    # the primary route's combination is step A's NuWro on CH (the two runs agree to 3e-11, the shape-only fit's tolerance)
    comb = gn["generator_definitions"]["combination_chi2"][mat]
    assert all(abs(comb[part]["chi2"] / gc["generators"]["nuwro"]["CH"]["chi2"][mat][part]["chi2"] - 1) < 1e-9
               for part in ("total", "shape_only")), "step D's combination is not step A's NuWro on CH"
    # the probe's diagnostic, not a declared test (receipts/d_projection.txt): recomputed from its own three totals
    m = re.search(r"probe chunk c1's NuWro test-event total ([\d.e+-]+) per nucleon against\s+\(12 x ([\d.e+-]+) "
                  r"\[production C12 p1\] \+ ([\d.e+-]+) \[MP3-B H c01\]\) / 13 = ([\d.e+-]+), \+([\d.]+)%, mostly DIS",
                  d["gprobe"])
    assert m and "diagnostic, not a declared test" in d["gprobe"], "the probe receipt changed"
    tot, c12, h, comb = (float(x) for x in m.groups()[:4])
    assert abs((12 * c12 + h) / 13 / comb - 1) < 5e-4 and f"{100 * (tot / comb - 1):.1f}" == m.group(5)
    v["gnat-probe-pct"] = m.group(5)
    # Q26, 3D (the note only, descriptive): the quadrant sums against the three-observable central value, at the scale
    # of the sixteen-cell uncertainty; all four lie below it
    q = d["gover"]["quadrants"]
    assert sorted(q) == ["QA", "QB", "QC", "QD"]
    assert all(x["3D"]["outcome"] == "agree at the sigma_16 scale (descriptive)" for x in q.values())
    pcts = [x["3D"]["d_pct"] for x in q.values()]
    zs = [abs(x["3D"]["d_over_sigma16"]) for x in q.values()]
    assert max(pcts) < 0, "a quadrant sum is not below the 3D central value"
    v["g3d-pct-lo"], v["g3d-pct-hi"] = f"{min(-x for x in pcts):.1f}", f"{max(-x for x in pcts):.1f}"
    v["g3d-zmax"] = f"{max(zs):.2f}"                   # the largest, rounded: the note prints it as "the largest"
    m = re.fullmatch(r"(\d)\.(\d)\d*e-0?(\d+)", f"{q['QA']['unreported_share_P5']:.1e}")
    v["g3d-qa-unrep"] = rf"{m.group(1)}.{m.group(2)}\times10^{{-{m.group(3)}}}"
    assert q["QB"]["unreported_share_P5"] == 0 and all(q[x]["label"] == "complete" for x in ("QC", "QD"))
    return v


def e2_values(d, arm):
    """GENCMP addendum E2: Table IV's four predictions with C_model's NuWro and GiBUU shape ratios taken from CH instead
    of carbon, everything else fixed, and with C_model removed (x0) and doubled (x2), in both arms ("with", "nopl") and
    both kinds; and the per-cell sigma, carbon against CH. The reported covariance keeps C_model on carbon (x1). Every
    key holds both E2 arms, so the two calls of values() give equal keys; this arm's carbon chi2 must be Table IV's."""
    e2, s = d["e2"], d["e2sens"]
    head, _, body = s.partition("\n{")
    assert all(x.startswith(("PASS ", "[PASS ")) for x in head.splitlines()), "the sensitivity receipt's controls changed"
    s = json.loads("{" + body)
    assert e2["schema"] == "fd-gencmp-e2/2" and e2["predictions"] == list(GENCMP4) and s["all_pass"] is True
    assert e2["vertices"] == ["genie_mec", "nuwro", "gibuu"] and e2["S_carbon"][0] == e2["S_CH"][0], \
        "the note says only NuWro's and GiBUU's components change"
    assert all(e2["S_carbon"][i] != e2["S_CH"][i] for i in (1, 2)), "the note says NuWro's and GiBUU's components change"
    v = {}
    sgn = lambda x: f"{x:+.2f}"  # noqa: E731   printed in math mode, so "-" is a minus
    for a in ("with", "nopl"):
        for n in GENCMP4:
            for part in ("total", "shape_only"):
                r, q = e2["chi2"][a][n][part], s["chi2"][a][n][part]
                assert (q["carbon"], q["CH"]) == (r["carbon"], r["CH"]) and abs(r["delta"] - (r["CH"] - r["carbon"])) < 1e-9
                assert q["removed"] > q["carbon"] > q["doubled"], f"{a} {n} {part}: chi2 does not fall as C_model grows"
                k = f"e2-{a}-{PRED[n]}-{part}"
                for tag, x in (("x0", q["removed"]), ("x1", q["carbon"]), ("x2", q["doubled"]), ("ch", q["CH"])):
                    v[f"{k}-{tag}"] = f"{x:.2f}"
                v[f"{k}-dch"], v[f"{k}-dx2"] = sgn(r["CH"] - r["carbon"]), sgn(q["doubled"] - q["carbon"])
                v[f"{k}-dx0"] = sgn(q["removed"] - q["carbon"])
                # the paper's precision (PAPER_PREC; referee round 20261104, item 6): one decimal, from the raw values
                for tag, x in (("dch", r["CH"] - r["carbon"]), ("dx2", q["doubled"] - q["carbon"]),
                               ("dx0", q["removed"] - q["carbon"])):
                    v[f"{k}-{tag}r1"] = f"{x:+.1f}"
                assert r["CH"] != r["carbon"], f"{a} {n} {part}: the note says every prediction's chi2 moves"
    t4 = table4(d, arm)                               # x1 is the reported covariance: Table IV's chi2 in this arm
    a = "with" if arm == "with" else "nopl"
    assert all(abs(e2["chi2"][a][n][part]["carbon"] / t4[n][part]["chi2"] - 1) < 1e-10
               for n in GENCMP4 for part in ("total", "shape_only")), "E2's carbon chi2 is not Table IV's"
    # the largest |change| over both arms and kinds, which the note names: GENIE + MEC, shape-only, without C_PL,5D
    big = max(((abs(e2["chi2"][a][n][p]["delta"]), a, n, p) for a in ("with", "nopl") for n in GENCMP4
               for p in ("total", "shape_only")))
    assert big[1:] == ("nopl", "genie_mec", "shape_only") and abs(big[0] - e2["delta_max_abs"]) < 1e-12
    assert e2["chi2"]["nopl"]["genie_mec"]["shape_only"]["delta"] < 0, "the note prints that change as a fall"
    # removing C_model raises GiBUU's total most, in both arms (the note names it)
    assert all(max(GENCMP4, key=lambda n: s["chi2"][a][n]["total"]["removed"] - s["chi2"][a][n]["total"]["carbon"])
               == "gibuu" for a in ("with", "nopl"))
    v["e2-dmax"] = f"{big[0]:.2f}"
    # GiBUU: with C_model's shape ratios also from CH, its CH total lies below its carbon total (analysis definitions),
    # so more than half of the rise is the pairing of the CH prediction with C_model's carbon shape ratios
    mat = "reported" if arm == "with" else "without_C_PL5D"
    carb = d["gdefs"]["generators"]["gibuu"]["carbon"]["analysis_definitions"]["chi2"][mat]["total"]["chi2"]
    g = e2["chi2"][a]["gibuu"]["total"]
    # the text says the rise comes from that pairing: with CH shape ratios GiBUU's CH total falls below carbon
    assert carb < g["carbon"] and g["CH"] < carb, "GiBUU's rise no longer comes from C_model's carbon shape ratios"
    v["e2-with-gibuu-total-chr1"] = f"{e2['chi2']['with']['gibuu']['total']['CH']:.1f}"
    # per-cell sigma: the whole matrix, carbon against CH, and C_model's own (sigma/f, the column norms of S)
    for a in ("with", "nopl"):
        x = s["sigma"][f"{a}_total"]
        rel = x["per_cell_rel_change"]
        i = max(range(16), key=lambda j: abs(rel[j]))
        assert i == x["cell"] and rel[i] < 0
        v[f"e2-sig-{a}-cell"], v[f"e2-sig-{a}-fall"] = CELLS[i], f"{-100 * rel[i]:.1f}"
        v[f"e2-sig-{a}-carbon"], v[f"e2-sig-{a}-ch"] = f"{x['sigma_over_f_carbon']:.4f}", f"{x['sigma_over_f_CH']:.4f}"
    rel = s["sigma"]["with_total"]["per_cell_rel_change"]
    up = [CELLS[j] for j in range(16) if rel[j] > 0]
    assert len(up) == 1 and all(r != 0 for r in rel), "the note says the sigma falls in all cells but one"
    assert v["e2-sig-nopl-cell"] == v["e2-sig-with-cell"], "the note gives both arms' largest sigma fall in one cell"
    v["e2-sig-with-nfall"], v["e2-sig-with-upcell"] = str(16 - len(up)), up[0]
    v["e2-sig-with-up"] = f"{100 * max(rel):.1f}"
    m = s["sigma"]["C_model"]
    mc, mch = m["per_cell_sigma_over_f_carbon"], m["per_cell_sigma_over_f_CH"]
    assert m["n_cells"] == 16 and m["cells_with_zero_carbon_sigma"] == 0 and min(mc) > 0
    i = max(range(16), key=lambda j: abs(mch[j] - mc[j]))
    j = max(range(16), key=lambda j: abs(mch[j] / mc[j] - 1))
    assert (i, j) == (m["cell"], m["cell_rel"]) and mch[i] < mc[i] and mch[j] > mc[j]
    assert mc[j] < sorted(mc)[4], "the note says C_model is small in the cell of its largest relative change"
    v["e2-cm-cell"], v["e2-cm-carbon"], v["e2-cm-ch"] = CELLS[i], f"{mc[i]:.4f}", f"{mch[i]:.4f}"
    v["e2-cm-relcell"], v["e2-cm-relcarbon"], v["e2-cm-relch"] = CELLS[j], f"{mc[j]:.4f}", f"{mch[j]:.4f}"
    v["e2-cm-rel"] = f"{100 * (mch[j] / mc[j] - 1):.1f}"
    return v


def solve(A, b):
    """x with A x = b, by Gaussian elimination with partial pivoting (the quadrant matrices are 4 x 4)."""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            M[r] = [M[r][k] - f * M[c][k] for k in range(n + 1)]
    x = [0.0] * n
    for r in reversed(range(n)):
        x[r] = (M[r][n] - sum(M[r][k] * x[k] for k in range(r + 1, n))) / M[r][r]
    return x


def bound_up(x):
    """x rounded up to two decimals: an upper bound that prints true."""
    return f"{math.ceil(100 * x - 1e-9) / 100:.2f}"


def bound_down(x):
    """x rounded down to two decimals: a lower bound that prints true."""
    return f"{math.floor(100 * x + 1e-9) / 100:.2f}"


RPD_PL = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]


def rpd_playlists(names):
    """Playlists in run order, the six earliest joined as 1A--1F when all are present: "1A--1F and 1O"."""
    names = [x for x in RPD_PL if x in names]
    if set(RPD_PL[:6]) <= set(names):
        names = ["1A--1F"] + [x for x in names if x not in RPD_PL[:6]]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def rpd_values(d):
    """The run-period diagnosis (FD-RPD-DECLARATION.md sec. 5): R2's permutation test, its era test and its simulated
    null, and R1's classes. The note states the outcomes the declaration's rules give (SEES, OTHER, CLUSTERED, and the
    calibration within its bound), so each is asserted and a changed readout stops the run."""
    r = d["rpd"]
    assert r["schema"] == "fd-rpd-readout/1" and r["stage0"]["branch"] == "SEES"
    v = {}
    s0, sg = r["stage0"]["s0"], r["stage0"]["sigma0"]
    v["rpd-s0"], v["rpd-s0-sigma"], v["rpd-s0-z"] = f"{100 * s0:.2f}", f"{100 * sg:.2f}", f"{s0 / sg:.1f}"
    # R2: the flux-file grouping's F is the largest of the (6, 3, 3) partitions, so p_flux is 1/N, the smallest it can be
    r2, n0 = r["R2"], r["N0"]
    assert r2["outcome"] == "CLUSTERED" and not n0["SIZE_BIAS_g"] and not n0["SIZE_BIAS_t"] and not r["R3"]["read"]
    n, ne = r2["n_partitions"]["flux"], r2["n_partitions"]["era"]
    assert (n, ne) == (9240, 83160) and round(r2["p_flux"] * n) == 1 and abs(r2["p_flux"] * n - 1) < 1e-9
    v["rpd-npart-flux"], v["rpd-npart-era"] = f"{n:,}", f"{ne:,}"
    v["rpd-npart-flux-math"] = f"{n:,}".replace(",", "{,}")     # in math mode a bare comma adds a space
    v["rpd-fflux"] = f"{r2['F_flux']:.2f}"

    def sci(p):          # three significant figures, scientific
        m, e = f"{p:.2e}".split("e")
        return rf"{m}\times10^{{{int(e)}}}"
    v["rpd-pflux"], v["rpd-pera"] = sci(r2["p_flux"]), sci(r2["p_era"])
    # the simulated null: alpha at each scale of the exchangeable offsets' covariance, all within the gate (calibrated)
    al, thr = r2["alpha"], r2["calibration_threshold"]
    assert sorted(map(float, al)) == [0.0, 0.5, 1.0, 2.0] and all(a <= thr for a in al.values())
    assert r2["datasets"] == 2000 and abs(thr - (0.05 + 3 * math.sqrt(0.05 * 0.95 / 2000))) < 1e-12
    v["rpd-datasets"] = f"{r2['datasets']:,}"
    v["rpd-alpha-lo"], v["rpd-alpha-hi"] = f"{min(al.values()):.4f}", f"{max(al.values()):.4f}"
    v["rpd-alpha-gate"] = f"{thr:.4f}"
    # R1: every playlist resolved; the pattern is OTHER (neither PERIOD-WIDE nor SUBSET), so no localisation is drawn
    r1 = r["R1"]
    cls = r1["classes"]
    assert r1["outcome"] == "OTHER" and not r1["sentence_dropped_at_stage_D"] and not r1["forced_unresolved_by_N0"]
    assert sorted(cls) == sorted(RPD_PL) and set(cls.values()) <= {"FREE", "CARRIES", "PARTIAL"}
    for c in ("FREE", "CARRIES", "PARTIAL"):
        v[f"rpd-r1-{c.lower()}"] = rpd_playlists([x for x in cls if cls[x] == c])
    return v


def quadrant_values(d):
    """C-R's per-quadrant reading and GENCMP X's joint test, for the paper's quadrant sentence and the note's tables."""
    v, Q = {}, ["QA", "QB", "QC", "QD"]
    cr, k = d["cr"], d["xk"]
    q = cr["quadrants"]
    assert cr["schema"] == "fd-gencmp-overlap/1" and cr["result_2d"] == "E_R with Q_R" and sorted(q) == Q
    word = {"agree": "agree", "agree below a correlation": "agree below a correlation"}
    for n in Q:
        x, t = q[n], q[n]["2D"]
        assert x["cells"] == CELLS[4 * Q.index(n):4 * Q.index(n) + 4]
        assert abs(x["S16"] - t["S"] - t["d"]) <= 1e-12 * x["S16"] and abs(100 * t["d"] / t["S"] - t["d_pct"]) < 1e-9
        v[f"cr-{n}-cells"] = f"{x['cells'][0]}--{x['cells'][-1]}"
        v[f"cr-{n}-s16"], v[f"cr-{n}-sig16"] = f"{x['S16'] / 1e-39:.4f}", f"{x['sigma16_reported'] / 1e-39:.4f}"
        v[f"cr-{n}-s2"], v[f"cr-{n}-sig2"] = f"{t['S'] / 1e-39:.4f}", f"{t['sigma'] / 1e-39:.4f}"
        v[f"cr-{n}-dpct"], v[f"cr-{n}-z0"] = f"{t['d_pct']:+.3f}", f"{t['z_rho0']:+.3f}"
        v[f"cr-{n}-reading"], v[f"cr-{n}-rhostar"] = word[t["outcome"]], f"{t['rho_star']:.4f}"
        o = t["printed_only_without_C_PL5D"]
        v[f"cr-{n}-nopl-reading"], v[f"cr-{n}-nopl-rhostar"] = word[o["outcome"]], f"{o['rho_star']:.4f}"
        # "agree" is |d| within the any-correlation band (rho* above 1); "agree below a correlation", rho* at most 1
        assert (t["outcome"] == "agree") == (t["rho_star"] > 1) and (o["outcome"] == "agree") == (o["rho_star"] > 1)
    # sec_fived16.tex :47 names the readings by hand: "All four agree, QA at every rho and the others below correlations of
    # cr-QC-rhostar (QC) to cr-QB-rhostar (QB)". Guard each named choice, so a readout that changes one stops the run
    oc = {n: q[n]["2D"]["outcome"] for n in Q}
    assert oc["QA"] == "agree" and all(oc[n] == "agree below a correlation" for n in ("QB", "QC", "QD")), \
        "sec_fived16 :47's readings changed: QA at every rho, the others below a correlation"
    rs = {n: q[n]["2D"]["rho_star"] for n in ("QB", "QC", "QD")}
    assert min(rs, key=rs.get) == "QC" and max(rs, key=rs.get) == "QB", "sec_fived16 :47's rho* range (QC to QB) changed"
    # the paper: "the sums differ by -1.5 to +0.7 per cent"
    pct = [q[n]["2D"]["d_pct"] for n in Q]
    assert min(pct) < 0 < max(pct), "the paper prints a signed range of the quadrant differences"
    v["x-dpct-min"], v["x-dpct-max"] = f"{min(pct):+.1f}".replace("+", ""), f"{max(pct):+.1f}"
    # GENCMP X: K0 checked that its d is C-R's; asserted again here
    assert k["schema"] == "fd-xcov-k/1" and k["v1_source"] == "full" and all(k["controls"].values())
    assert all(abs(k["d"][i] - q[n]["2D"]["d"]) <= 1e-12 * q[n]["S16"] and abs(k["S16"][i] / q[n]["S16"] - 1) < 1e-12
               and abs(k["S2D"][i] / q[n]["2D"]["S"] - 1) < 1e-12 for i, n in enumerate(Q)), "X's d is not C-R's"
    v["x-ncontrols"] = str(len(k["controls"]))
    # "The statistical correlation, and that of four systematic terms that could not be evaluated directly, are bounded"
    assert k["route"] == "A" and k["route_reasons"] == ["K2 failed for the statistical block: falls back to route A"], \
        "the paper says the statistical correlation is bounded, not measured"
    bands = sorted(c for c in k["crosses"] if c.startswith("band:"))
    assert len(k["bounded"]) == 4 and all(b.startswith("band:") and b not in k["crosses"] for b in k["bounded"]), \
        "the paper says four systematic terms are bounded"
    v["x-nbands-paired"], v["x-nbands"] = str(len(bands)), str(len(bands) + len(k["bounded"]))
    v["x-nlat"] = str(sum(c.startswith("lat:") for c in k["crosses"]))
    v["x-bounded"] = ", ".join(b[len("band:"):] for b in k["bounded"])
    # the family: every bounded cross block enters as r * M (fd_xcov.route_a), so V_d(r) = V_d(0) - r (M + M^T).
    # V_d(0) is rebuilt from the readout's own and paired cross blocks, and must give its chi2 at r = 0
    own, cross = k["own"], [k["crosses"][c] for c in k["crosses"]]
    K = [[sum(c[i][j] for c in cross) for j in range(4)] for i in range(4)]
    V0 = [[own["C16q"][i][j] + own["C2q"][i][j] - K[i][j] - K[j][i] for j in range(4)] for i in range(4)]
    p = k["primary"]
    assert abs(sum(a * b for a, b in zip(k["d"], solve(V0, k["d"]))) / p["r0"]["chi2_4"] - 1) < 1e-9, \
        "V_d(0) rebuilt from the blocks does not give the readout's chi2"
    # Each |z| is d over the root of a diagonal entry linear in r, so it is monotone in r and its largest value on [0, 1]
    # is at r = 0 or r = 1. chi2(r) = d^T V_d(r)^-1 d is convex in r (its second derivative is
    # 2 d^T V^-1 D V^-1 D V^-1 d >= 0 with D = M + M^T and V positive definite), so its largest value, and the smallest p,
    # are at an end too. The readout records the two ends; it does not record chi2's smallest value inside [0, 1]
    for name, key in (("primary", "prim"), ("Q_R_alone", "qr"), ("C_PL_pair_zero", "nopair")):
        R = k[name]
        assert R["outcome"] == "agree" and R["r_star"] is None and R["changes_at"] == [], \
            f"{name}: the agreement holds over the family"
        for r in ("r0", "r1"):
            v[f"x-{key}-chi2-{r}"], v[f"x-{key}-p-{r}"] = f"{R[r]['chi2_4']:.3f}", f"{R[r]['p']:.3f}"
        v[f"x-{key}-zmax"] = f"{max(abs(z) for r in ('r0', 'r1') for z in R[r]['z']):.3f}"
    for i, n in enumerate(Q):
        z0, z1 = p["r0"]["z"][i], p["r1"]["z"][i]
        assert z0 * k["d"][i] > 0 and z1 * k["d"][i] > 0 and abs(z1) > abs(z0)
        assert abs(math.sqrt(V0[i][i]) - k["d"][i] / z0) <= 1e-9 * math.sqrt(V0[i][i])
        v[f"x-{n}-z0"], v[f"x-{n}-z1"] = f"{z0:+.3f}", f"{z1:+.3f}"
        v[f"x-{n}-rho0"], v[f"x-{n}-rho1"] = f"{k['rho_q']['r0'][n]:.2f}", f"{k['rho_q']['r1'][n]:.2f}"
    for r in ("r0", "r1"):                             # the note prints each end's range as QC's to QA's
        rho = k["rho_q"][r]
        assert min(rho, key=rho.get) == "QC" and max(rho.values()) == rho["QA"], "the correlations' range changed"
    # the paper: "chi2 <= 1.24 for four degrees of freedom (p >= 0.87), with no quadrant beyond one standard deviation"
    # (Joseph's answer on #695). chi2 is convex in r, so its largest value over [0, 1] is at an end: the r = 1 end, here.
    # Each printed bound must be true: chi2's rounded up, p's rounded down (the director's ruling on rounding, #695)
    c0, c1 = p["r0"]["chi2_4"], p["r1"]["chi2_4"]
    assert c1 > c0, "the paper prints the r = 1 chi2 as the family's largest"
    pmin = min(p["r0"]["p"], p["r1"]["p"])
    v["x-chi2-hi"], v["x-p-min"] = bound_up(c1), bound_down(pmin)
    assert float(v["x-chi2-hi"]) >= c1 and float(v["x-p-min"]) <= pmin, \
        "a printed bound is not a bound: chi2 <= x-chi2-hi and p >= x-p-min must hold"
    zmax = max(abs(z) for r in ("r0", "r1") for z in p[r]["z"])
    assert zmax < 1, "the paper says no quadrant lies beyond one standard deviation"
    # sec_fived16.tex names where it lies: "the largest |z| is x-zmax, in QC at r = 1"
    assert abs(p["r1"]["z"][Q.index("QC")]) == zmax, "the largest |z| is no longer QC's at r = 1, as sec_fived16 says"
    v["x-zmax"] = f"{zmax:.3f}"
    return v


def values(d, arm="with"):
    A = ARMS[arm]
    v = {}
    # Stage G's chain: each downstream readout names, by sha256, the upstream readouts this arm pins, so a re-pin of one
    # readout without the others stops here
    pins = (READOUTS if arm == "with" else NOPL_READOUTS)
    for key, field, up in (("diag", "g_readout", "g"), ("fup", "g_readout", "g"), ("fup", "g_diag_readout", "diag"),
                           ("sens2", "g_readout", "g"), ("sens2", "g_followup_readout", "fup"), ("fboot", "g_readout", "g")):
        assert d[key]["inputs_sha256"][field].startswith(pins[up][1]), f"{key} was not computed from the pinned {up}"
    # the cells: boxes and central values (f in 10^-40 cm^2/nucleon, three significant figures)
    p0 = d["g"]["predictions"][0]
    assert p0["cells"] == CELLS and d["g"]["cells"] == CELLS
    f = dict(zip(CELLS, p0["f"]))
    for p in d["g"]["predictions"]:   # GiBUU carries 8 of the 16 cells: compare by cell name
        assert max(abs(x / f[c] - 1) for c, x in zip(p["cells"], p["f"])) < 1e-12, "f differs across predictions"
    boxes = {f"R{c['id']:02d}": c["box"] for c in d["h2"]["reporting_cells"] if c["reported"]}
    assert sorted(boxes) == CELLS
    for c in CELLS:
        v[f"f-{c}"] = f"{f[c] / 1e-40:#.3g}".rstrip(".")      # three significant figures, trailing zeros kept
        for ax, (lo, hi) in boxes[c].items():
            v[f"box-{c}-{ax}"] = f"{lo:g}--{hi:g}"
    # the data product (FD-G-FIGURES-REPORT.md section 2) carries the same cells, boxes, f and reported sigma
    dp = d["dp"]
    assert [c["cell"] for c in dp["cells"]] == CELLS and dp["correlation_of"] == A["dp"]
    assert all(c["box"] == boxes[c["cell"]] for c in dp["cells"]), "the data product's boxes differ from H2's"
    assert max(abs(x / f[c] - 1) for c, x in zip(CELLS, dp["f"])) < 1e-12, "the data product's f differs"
    crt = d["cresp"]["relative_sigma"]["C_total_resp"]
    crt = [crt[c] for c in CELLS] if isinstance(crt, dict) else crt
    assert max(abs(a / b - 1) for a, b in zip(dp["relative_sigma"]["C_total_plus_C_resp"], crt)) < 1e-10
    for grp, key in (("reported", A["dp"]),) + ((("C_PL5D", "C_PL5D"),) if arm == "with" else ()):
        vals = dp["relative_sigma"][key]                 # the reported matrix's sigma, and the block's alone
        assert len(vals) == 16
        for c, x in zip(CELLS, vals):
            v[f"sig-{grp}-{c}"] = pct(x)
            v[f"sig1-{grp}-{c}"] = pct1(x)
        srt = sorted(vals)
        v[f"sigmed-{grp}"], v[f"sigmin-{grp}"], v[f"sigmax-{grp}"] = pct((srt[7] + srt[8]) / 2), pct(srt[0]), pct(srt[-1])
        v[f"sigmed1-{grp}"] = pct1((srt[7] + srt[8]) / 2)
    if arm == "with":                                     # the block's effect on the reported sigma (proposal section 1)
        wo, wi = dp["relative_sigma"]["C_total_plus_C_resp"], dp["relative_sigma"][A["dp"]]
        sw, so = sorted(wi), sorted(wo)
        v["pl-medrise"] = f"{100 * ((sw[7] + sw[8]) / (so[7] + so[8]) - 1):.1f}"      # of the median, about 7.8 %
        ratio = [b / a for a, b in zip(wo, wi)]
        r = sorted(ratio)
        v["pl-cellrise-med"] = f"{100 * ((r[7] + r[8]) / 2 - 1):.1f}"
        i = max(range(16), key=lambda j: ratio[j])
        v["pl-cellrise-max"], v["pl-cellrise-maxcell"] = f"{100 * (ratio[i] - 1):.1f}", CELLS[i]
        share = sorted(1 - (a / b) ** 2 for a, b in zip(wo, wi))
        v["pl-share-med"], v["pl-share-max"] = f"{100 * (share[7] + share[8]) / 2:.1f}", f"{100 * share[-1]:.1f}"
        # the block's own label, which travels with every use (FD-CT-5B-ADDITION-DECLARATION.md section 2)
        m = re.search(r"68% interval on sigma_true/sigma_hat is \[([\d.]+), ([\d.]+)\]\. Noise-dominated cells: "
                      r"((?:R\d\d(?:, )?)+)\. Rank (\d); undebiased", dp["labels"]["block"])
        assert m and "added after the data were seen" in dp["labels"]["block"], "the block's label changed"
        v["pl-sigratio-lo"], v["pl-sigratio-hi"], v["pl-noise-cells"], v["pl-rank"] = m.groups()
        assert min(range(16), key=lambda j: wi[j]) == CELLS.index("R04"), "R04 is no longer the smallest-sigma cell"
    rho = dp["correlation"]
    assert all(abs(rho[i][j] - rho[j][i]) < 1e-12 for i in range(16) for j in range(16))
    assert all(abs(rho[i][i] - 1) < 1e-12 for i in range(16))
    for i in range(16):                    # the correlation matrix of the reported covariance, two decimals
        for j in range(i):
            x = f"{rho[i][j]:.2f}"
            v[f"corr-{CELLS[i]}-{CELLS[j]}"] = ("$-$" + x[1:]) if x.startswith("-") else x
    # what GiBUU's sample cannot hold: GENIE CV's and NuWro's E_nu > 20 GeV shares, each a lower bound on the
    # full-flux share because both samples stop at 50 GeV (the readout's range label); never a GiBUU number
    ga = d["gagg"]
    assert "lower bound" in ga["labels"]["range"] and "not a GiBUU number" in ga["labels"]["not"]
    pz_edges = sorted({e for c in dp["cells"] for e in c["box"]["pz"]})
    for g in ("genie_cv", "nuwro"):
        gg = ga["generators"][g]
        assert gg["generation_range_gev"][1] == 50.0
        assert gg["pz_4.5_60"]["bands"][0][0] == pz_edges[1] and gg["pz_4.5_60"]["bands"][-1][1] == pz_edges[2]
        v[f"gagg-{g}-hi"] = f"{100 * gg['pz_4.5_60']['share_E_gt_20']:.2f}"
        v[f"gagg-{g}-lo"] = f"{100 * gg['pz_1.5_4.5']['share_E_gt_20']:.2f}"
    v["gagg-ecut"] = f"{ga['e_cut_gev']:g}"
    v["gagg-range-max"] = f"{ga['generators']['genie_cv']['generation_range_gev'][1]:g}"
    v["gagg-pz-lo"] = f"{pz_edges[0]:g}"
    v["f-unit"] = r"10^{-40}"     # f is printed in units of 10^-40 cm^2/nucleon
    # per-cell relative sigma by group, and the medians
    s1, cr = d["s1"]["relative_sigma"], d["cresp"]["relative_sigma"]
    for grp, src in [(k, s1) for k in ("stat", "interaction", "flux", "detector", "lateral", "normalization", "C_e",
                                       "C_model", "C_total")] + [(k, cr) for k in ("C_resp", "C_total_resp")]:
        vals = src[grp]
        vals = [vals[c] for c in CELLS] if isinstance(vals, dict) else vals
        assert len(vals) == 16
        for c, x in zip(CELLS, vals):
            v[f"sig-{grp}-{c}"] = pct(x)
            v[f"sig1-{grp}-{c}"] = pct1(x)
        srt = sorted(vals)
        v[f"sigmed-{grp}"] = pct((srt[7] + srt[8]) / 2)
        v[f"sigmed1-{grp}"] = pct1((srt[7] + srt[8]) / 2)
        v[f"sigmin-{grp}"] = pct(srt[0])
        v[f"sigmax-{grp}"] = pct(srt[-1])
    # the fake-data grades: each graded truth under C_total (F0) and C_total + C_resp (F0b)
    for tag in ("f0", "f0b"):
        n_cells = n_p = n_truth = 0
        for t in d[tag]["truths"]:
            k = f"{tag}-{t['name']}"
            for var in ("in_sample", "model_only"):          # descriptive variants, labelled in the readout
                if var in t:
                    v[f"{k}-{var}-chi2"] = f"{t[var]['chi2']:.2f}"
                    v[f"{k}-{var}-p"] = p_tex(t[var]["p"])
            if not t.get("graded"):                          # row 6: descriptive and ungraded (control 7 failed)
                v[f"{k}-chi2"], v[f"{k}-p"], v[f"{k}-n"] = (f"{t['grade']['chi2']:.2f}", p_tex(t["grade"]["p"]),
                                                            str(t["n_experiments"]))
                continue
            gr = t["grade"]
            n_truth += 1
            n_cells += len(gr["cells_abs_z_gt_2"])
            n_p += bool(gr["p_lt_0.01"])
            v[f"{k}-chi2"] = f"{gr['chi2']:.2f}"
            v[f"{k}-chi2int"] = f"{gr['chi2']:.0f}"        # the paper's precision (PAPER_PREC), from the raw value
            v[f"{k}-p"] = p_tex(gr["p"])
            v[f"{k}-cells"] = ", ".join(gr["cells_abs_z_gt_2"]) or "---"
            v[f"{k}-zmax"] = f"{max(abs(z) for z in gr['z']):.2f}"
            v[f"{k}-n"] = str(t["n_experiments"])
            v[f"{k}-listed"] = "yes" if t["listed"] else "no"
        v[f"{tag}-ncells"], v[f"{tag}-np"], v[f"{tag}-ntruths"] = str(n_cells), str(n_p), str(n_truth)
    # Stage G as first made (gs-): chi2 with ndf, shape-only, p, and the variant without C_resp, for the predictions in
    # the generators' own definitions with NuWro and GiBUU on carbon; the note prints that comparison in its own table
    for p in d["g0"]["predictions"]:
        k = f"gs-{PRED[p['name']]}"
        for part in ("total", "shape_only"):
            q = p[part]
            v[f"{k}-{part}-chi2"] = f"{q['chi2']:.2f}"
            v[f"{k}-{part}-chi2int"] = f"{q['chi2']:.0f}"
            v[f"{k}-{part}-ndf"] = str(q["ndf"])
            v[f"{k}-{part}-p"] = p_tex(q["p"])
        v[f"{k}-nocresp-chi2"] = f"{p['variant']['total']['chi2']:.2f}"
        v[f"{k}-nocresp-chi2int"] = f"{p['variant']['total']['chi2']:.0f}"
        v[f"gs-label-{PRED[p['name']]}"] = short_label(p)
    # Table IV (g-): GENCMP's corner "CH, analysis definitions" for GENIE CV, GENIE + MEC, NuWro and GiBUU
    # (DECISION-20261101-joseph-gencmp-paper-adoption.md items 1-2; FD-GENCMP-REPORT.md sec. 2.2), in this arm's matrix;
    # MINERvA Tune v1, already in the analysis definitions (MP-5 T3), is Stage G's unchanged
    for name, p in table4(d, arm).items():
        k = f"g-{PRED[name]}"
        for part in ("total", "shape_only"):
            q = p[part]
            v[f"{k}-{part}-chi2"] = f"{q['chi2']:.2f}"
            v[f"{k}-{part}-chi2int"] = f"{q['chi2']:.0f}"
            v[f"{k}-{part}-ndf"] = str(q["ndf"])
            v[f"{k}-{part}-p"] = p_tex(q["p"])
        for c, z, r in zip(p["cells"], p["pulls"], p["g_over_f_minus_1"]):
            v[f"{k}-pull-{c}"] = f"{z:.2f}"
            v[f"{k}-gf-{c}"] = f"{100 * r:.1f}"
        # NuWro and GiBUU carry their target, CH, in the label (the consult's Q5); the GENIE samples are CH as generated
        base = short_label(next(q for q in d["g"]["predictions"] if q["name"] == name))
        assert base == v[f"gs-label-{PRED[name]}"], f"{name}: the readouts name the prediction differently"
        v[f"label-{PRED[name]}"] = base + (" (CH)" if name in ("nuwro", "gibuu") else "")
        v[f"{k}-ncells"] = str(len(p["cells"]))
        WORDS = {7: "seven", 8: "eight", 9: "nine", 16: "sixteen"}   # the abstracts print the count in words
        v[f"{k}-ncells-word"] = WORDS[len(p["cells"])]
    v.update(gencmp_values(d, arm))
    v.update(e2_values(d, arm))
    v.update(quadrant_values(d))
    v.update(rpd_values(d))
    # G-SENS: chi2 at each alpha per family, and the sentence's bounds (16-cell predictions only)
    recs = d["sens2"]["sens"]["records"] + d["fup"]["sens"]["records"]
    for r in recs:
        v[f"sens-{r['family']}-{PRED[r['prediction']]}-a{r['alpha']:g}"] = f"{r['chi2']:.2f}"
    def ratios(fam, alpha):
        return [r["chi2"] / r["chi2_at_alpha_0"] for r in recs
                if r["family"] == fam and abs(r["alpha"] - alpha) < 1e-12 and len(r["cells"]) == 16]
    fl = ratios("flux", 0.1)
    other = ratios("detector", 0.1) + ratios("lateral", 0.1)
    assert len(fl) == 4 and len(other) == 8
    v["sens-flux-fall-lo"] = f"{100 * (1 - max(fl)):.0f}"
    v["sens-flux-fall-hi"] = f"{100 * (1 - min(fl)):.0f}"
    v["sens-detlat-fall-max"] = f"{math.ceil(100 * (1 - min(other))):.0f}"
    joint = [r["chi2"] for r in recs if r["family"] == "c_e_systematic" and r["alpha"] == 1.0 and len(r["cells"]) == 16]
    assert len(joint) == 4
    v["sens-joint-chi2-min"] = f"{math.floor(min(joint)):.0f}"
    # C_resp by species, the sigma ratio, and the trace shares
    for sp in ("C_resp_proton", "C_resp_meson", "C_resp_em", "C_resp_other", "C_resp_xtalk"):
        vals = [cr[sp][c] for c in CELLS] if isinstance(cr[sp], dict) else cr[sp]
        for c, x in zip(CELLS, vals):
            v[f"sig-{sp}-{c}"] = pct(x)
            v[f"sig1-{sp}-{c}"] = pct1(x)
        srt = sorted(vals)
        v[f"sigmed-{sp}"] = pct((srt[7] + srt[8]) / 2)
        v[f"sigmed1-{sp}"] = pct1((srt[7] + srt[8]) / 2)
    tot = [cr["C_total"][c] for c in CELLS] if isinstance(cr["C_total"], dict) else cr["C_total"]
    tr = [cr["C_total_resp"][c] for c in CELLS] if isinstance(cr["C_total_resp"], dict) else cr["C_total_resp"]
    rat = sorted(b / a for a, b in zip(tot, tr))
    v["sigratio-med"], v["sigratio-min"], v["sigratio-max"] = (f"{(rat[7] + rat[8]) / 2:.3f}", f"{rat[0]:.3f}",
                                                                f"{rat[-1]:.3f}")
    # declaration (v) at the sixteen-cell chi2 (app_statmethods_nd.tex:12; PROVENANCE-20261031-declaration-v-fd-16-cell-
    # blocks.md section 3): the statistical block's replicas and the flux block's effective number of weighted universes
    meta = d["s1"]["meta"]
    v["s1-stat-replicas"] = str(meta["stat_replicas"])
    v["s1-flux-neff"] = f"{meta['flux_weights']['n_eff']:.0f}"
    # the paper appendix's source list (referee round 20261104, item 2): S1's blocks counted by s1_assemble.py's own
    # grouping (group_of), whose constants are read from its pinned source. The appendix names the detector and lateral
    # bands in words, so their sets are asserted here, and the counts must be those of the readout's blocks
    con = {}
    for node in ast.parse(d["s1code"]).body:
        if isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if hasattr(t, "id")] or [e.id for e in node.targets[0].elts]
            if set(names) & {"FLUX", "MINOS", "DROPPED", "LATERAL_BANDS", "DETECTOR_BANDS"}:
                val = eval(compile(ast.Expression(node.value), "s1_assemble.py", "eval"), {"__builtins__": {}}, dict(con))
                con.update(zip(names, val) if len(names) > 1 else {names[0]: val})
    assert set(con["DETECTOR_BANDS"]) == {"GEANT_Neutron", "GEANT_Pion", "GEANT_Proton", "MinosEfficiency"}
    assert set(con["LATERAL_BANDS"]) == {"BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA",
                                         "Muon_Energy_MINOS"}
    assert con["FLUX"] == "Flux" and con["DROPPED"] == "Rvp1pi" and "Rvp1pi" in meta["not_included"]
    bands = [b[5:] for b in meta["blocks"] if b.startswith("band:")]
    lats = [b[4:] for b in meta["blocks"] if b.startswith("lat:")]
    assert set(lats) == set(con["LATERAL_BANDS"]) and con["FLUX"] in bands and set(con["DETECTOR_BANDS"]) <= set(bands)
    inter = [b for b in bands if b != con["FLUX"] and b not in con["DETECTOR_BANDS"]]
    assert {"stat", "normalization", "seed"} <= set(meta["blocks"]) and len(meta["blocks"]) == len(bands) + len(lats) + 3
    v["s1-n-interaction"], v["s1-n-detector"], v["s1-n-lateral"] = (str(len(inter)), str(len(con["DETECTOR_BANDS"])),
                                                                   str(len(lats)))
    assert {f"{100 * meta['normalization_fraction']:.2f}"} == {v[f"sig-normalization-{c}"] for c in CELLS}
    # 3b (b0): the species at their +-1 sigma and the whole recoil at +-4 %, noise-free closures at the nominal truth; |delta|
    # over the per-cell sigma of C_total + C_resp. The paper prints the bound over the species and W2b's median and
    # maximum, and says no pass threshold is set, so the readout's labels and design are asserted here
    ct = d["ct3b"]
    assert ct["schema"] == "fd-ct-mismatch/1" and ct["cells"] == CELLS and ct["controls_passed"] == ["S", "M0", "M1", "M2"]
    assert "no pass threshold is set" in ct["labels"]["no_threshold"]
    assert "nominal truth, noise-free and signal-only" in ct["labels"]["what"] and "whole recoil at +-4%" in ct["labels"]["what"]
    summ = {k: x["abs_delta_over_sigma_total_resp_summary"] for k, x in ct["variants"].items()}
    spec = [f"{s}_{m}" for s in ("proton", "meson", "em", "other") for m in ("m1", "p1")]
    assert set(summ) == set(spec) | {"xtalk_m1", "xtalk_p1", "w2b_rr0", "w2b_rr1"}
    v["ct3b-species-max"] = f"{max(summ[k]['max'] for k in spec):.2f}"
    v["ct3b-species-med-lo"] = f"{min(summ[k]['median'] for k in spec):.2f}"
    v["ct3b-species-med-hi"] = f"{max(summ[k]['median'] for k in spec):.2f}"
    v["ct3b-w2b-med"] = f"{max(summ[k]['median'] for k in ('w2b_rr0', 'w2b_rr1')):.2f}"
    v["ct3b-w2b-max"] = f"{max(summ[k]['max'] for k in ('w2b_rr0', 'w2b_rr1')):.2f}"
    for k, x in d["s1"]["trace_share"].items():
        v[f"trace-{k}"] = f"{x:.3f}"
    for k, x in d["cresp"]["trace_share_of_C_total_resp"].items():
        v[f"trace-resp-{k}"] = f"{x:.4f}"
    # the grid: H2's boxes before and after the purity merge
    h2 = d["h2"]
    v["h2-tau"] = f"{h2['tau']:g}"
    v["h2-nmerge"] = str(len(h2["steps"]))
    v["h2-nunreported"] = str(len(h2["unreported_boxes"]))
    v["h2-nboxes"] = str(sum(len(c["h2_cells"]) for c in h2["reporting_cells"]) + len(h2["unreported_boxes"]))
    for ax in ("pt", "pz", "eavail", "q3", "W"):
        edges = sorted({e for c in h2["reporting_cells"] for e in c["box"][ax]})
        v[f"h2-edges-{ax}"] = ", ".join(f"{e:g}" for e in edges)
    v["h2-nsupported"] = str(d["stage1"]["mc"]["H2"]["n_reported"])       # before the merge: the support rule
    # unsupported boxes absorbed into a reporting cell by the merge (box 17 into R09), and the others left unreported
    v["h2-nabsorbed"] = str(int(v["h2-nboxes"]) - int(v["h2-nsupported"]) - int(v["h2-nunreported"]))
    # the printed H2 counts come from the data product's h2 fields (director, 2026-10-27), and must equal the
    # definition's and Stage 1's
    dh = d["dp"]["h2"]
    from_dp = {"h2-nboxes": len(dh["h2_to_reporting_cell"]), "h2-nunreported": len(dh["unreported_boxes"]),
               "h2-nabsorbed": len(dh["absorbed"]),
               "h2-nsupported": len(dh["h2_to_reporting_cell"]) - len(dh["unsupported_stage1"])}
    for k, n in from_dp.items():
        assert v[k] == str(n), f"{k}: the data product gives {n}, the definition and Stage 1 {v[k]}"
        v[k] = str(n)
    assert sum(len(c["h2_boxes"]) for c in d["dp"]["cells"]) == len(dh["in_cells"])
    for ax in ("pt", "pz", "eavail", "q3", "W"):                             # H2 divides each axis at one interior edge
        edges = sorted({e for c in h2["reporting_cells"] for e in c["box"][ax]})
        assert len(edges) == 3
        v[f"h2-mid-{ax}"] = f"{edges[1]:g}"
    assert d["stage1"]["mc"]["H2"]["n_cells"] == int(v["h2-nboxes"])
    # The four low-stability cells, disclosed in the paper's limitations (DECISION-20261024-joseph-h2-16-cell-definition.md
    # item 3; DECISION-20261028-joseph-protections-remade-and-r21.md item 1). A cell's stability is the fraction of the
    # simulated signal events generated in it, and reconstructed, that are reconstructed in it (pv-ladder
    # h2_definition.py, Stats.of). The decided cells must be the four lowest and print the decided 0.16-0.25.
    lowstab = ("R02", "R06", "R10", "R15")
    stab = {f"R{c['id']:02d}": c["stability"] for c in h2["reporting_cells"]}
    assert set(sorted(stab, key=stab.get)[:len(lowstab)]) == set(lowstab), "the decided cells are not the lowest-stability cells"
    v["h2-lowstab-cells"] = ", ".join(lowstab[:-1]) + " and " + lowstab[-1]
    v["h2-lowstab-min"], v["h2-lowstab-max"] = (f"{min(stab[k] for k in lowstab):.2f}", f"{max(stab[k] for k in lowstab):.2f}")
    assert (v["h2-lowstab-min"], v["h2-lowstab-max"]) == ("0.16", "0.25"), "the printed range differs from the decision's"
    rest = [stab[k] for k in stab if k not in lowstab]                 # the note prints the other twelve's range beside them
    assert len(rest) == 12
    v["h2-stab-rest-min"], v["h2-stab-rest-max"] = f"{min(rest):.2f}", f"{max(rest):.2f}"
    # C_model,5D: its vertices' trace shares, and the numbers its labels state (parsed, so a changed label stops here)
    for k, x in d["cmodel"]["trace_share_by_vertex"].items():
        v[f"cmodel-trace-{k}"] = f"{x:.3f}"
    lab = d["cmodel"]["labels"]
    m = re.search(r"applied on p_parallel < (\d+) GeV/c.*At (\d+) <= p_parallel < \d+ GeV/c GiBUU's sample lacks the "
                  r"E_nu > (\d+) GeV part, ([\d.]+)-([\d.]+) %", lab["gibuu"])
    assert m, "cmodel_5d.json's gibuu label changed"
    (v["cmodel-gibuu-pz-max"], v["cmodel-gibuu-pz-lack"], v["cmodel-gibuu-enu"], v["cmodel-gibuu-lack-lo"],
     v["cmodel-gibuu-lack-hi"]) = m.groups()
    m = re.search(r"(\d+)-(\d+) % of the prior weight lies beside a step in r > ([\d.]+)", lab["step_adjacent"])
    assert m, "cmodel_5d.json's step_adjacent label changed"
    v["cmodel-step-lo"], v["cmodel-step-hi"], v["cmodel-step-r"] = m.groups()
    m = re.fullmatch(r"a cell with \|z\| > ([\d.]+), or a truth with P\(chi2_16 > chi2\) < ([\d.]+), against the grade matrix",
                     d["f0b"]["triggers"]["rule"])
    assert m and d["f0"]["triggers"]["rule"] == d["f0b"]["triggers"]["rule"], "the trigger rule changed"
    v["trig-z"], v["trig-p"] = m.groups()
    alphas = d["sens2"]["constants"]["alphas"]
    assert alphas == d["fup"]["constants"]["alphas"] and 0.1 in alphas
    v["sens-alpha-pct"] = f"{100 * 0.1:.0f}"      # the sentence's weakening: alpha = 0.1 of the declared grid
    for a in alphas:
        v["sens-alpha-" + f"{a:g}".replace(".", "p")] = f"{a:g}"
    fr = d["diag"]["constants"]["fractions"]
    assert len(fr) == 3
    v["diag-fractions"] = "/".join(f"{100 * x:g}" for x in fr)
    # the fake-data controls and the trigger counts by group, with their Gaussian references
    for tag in ("f0", "f0b"):
        ctl = d[tag]["controls"]
        v[f"{tag}-controls-passed"] = ", ".join(str(i) for i in ctl["passed"])
        v[f"{tag}-control7-chi2"] = f"{ctl['offset_control_7']['chi2']:.2f}"
        for grp, gt in d[tag]["triggers"]["by_group"].items():
            k = f"{tag}-grp-{grp}"
            v[f"{k}-truths"], v[f"{k}-cells"] = str(gt["truths"]), str(gt["cells"])
            v[f"{k}-zcells"], v[f"{k}-ptruths"] = str(gt["cells_abs_z_gt_2"]), str(gt["truths_p_lt_0.01"])
            v[f"{k}-refcells"], v[f"{k}-reftruths"] = (f"{gt['gaussian_reference_cells']:.2f}",
                                                       f"{gt['gaussian_reference_truths']:.2f}")
        ag = d[tag]["triggers"]["all_graded"]    # denominators only: the counts are read by group, never pooled
        v[f"{tag}-all-truths"], v[f"{tag}-all-cells"] = str(ag["truths"]), str(ag["cells"])
        v[f"{tag}-nlisted"] = str(len(d[tag]["triggers"]["listed"]))
        names = [TRUTH_LABEL[x["truth"]][0] for x in d[tag]["triggers"]["listed"]]
        v[f"{tag}-listed-names"] = (", ".join(names[:-1]) + " and " + names[-1]) if len(names) > 1 else "".join(names) or "none"
        v[f"{tag}-nunlisted"] = str(ag["truths"] - len(d[tag]["triggers"]["listed"]))
        v[f"{tag}-nungraded"] = str(sum(1 for t in d[tag]["truths"] if not t.get("graded")))
    # G-DIAG: per prediction and comparison, the modes carrying 50/90/99 % and the top mode
    for p in d["diag"]["predictions"]:
        for cmpn in p["comparisons"]:
            k = f"diag-{PRED[p['name']]}-{cmpn['comparison']}"
            rel = cmpn["relative_to_f"]
            for q, n in rel["modes_needed"].items():
                v[f"{k}-modes{q.rstrip('%')}"] = str(n)
            top = rel["top_modes"][0]
            v[f"{k}-top-share"] = f"{100 * top['fraction']:.1f}"
            v[f"{k}-top-sigma"] = f"{100 * top['sigma']:.2f}"
            v[f"{k}-top-block"] = BLOCK[top["dominant"]]
    # the R04 look
    r04 = d["fup"]["r04"]
    rs = r04["item2_relative_sigma"]["R04"]
    v["r04-sigma-flux"] = pct(rs["flux"])
    corr = list(r04["item3_correlation_with_R04"]["under"][A["rep"]].values())
    v["r04-ncorr"] = str(len(corr))
    v["r04-corr-min"], v["r04-corr-max"] = f"{min(corr):.2f}", f"{max(corr):.2f}"     # under C_total + C_resp
    cf = list(r04["item3_correlation_with_R04"]["under"]["flux"].values())            # under the flux block alone
    v["r04-corrflux-min"], v["r04-corrflux-max"] = f"{min(cf):.3f}", f"{max(cf):.3f}"
    v["r04-sigma-total"] = pct(rs[A["rep"]])
    assert min(range(16), key=lambda i: tr[i]) == CELLS.index("R04"), "R04 is no longer the smallest-sigma cell"
    assert v["gagg-ecut"] == v["cmodel-gibuu-enu"], "the aggregate's E_nu cut is not GiBUU's sample limit"
    # the abstracts' range: the three EXTERNAL predictions compared on all 16 cells. MINERvA Tune v1 is the unfolding's
    # own prior ("prior (not an independent prediction)", Stage G) and is not in the range; GiBUU, on 8 cells, is printed
    # on its own (director, 2026-10-27)
    ext = [k for k in ("gcv", "gmec", "nuwro") if v[f"g-{k}-total-ndf"] == "16"]
    assert len(ext) == 3 and v["g-gibuu-total-ndf"] == "8" and "tune" not in ext
    v["g-ext-chi2int-min16"] = str(min(int(v[f"g-{k}-total-chi2int"]) for k in ext))
    v["g-ext-chi2int-max16"] = str(max(int(v[f"g-{k}-total-chi2int"]) for k in ext))
    # F16-1 (2026-11-16): the ES prints this range "with NuWro and GiBUU on carbon" (the paper's primary comparison); it
    # is the same range with NuWro's carbon chi2 in place of the CH one, since NuWro sets neither end
    assert int(v["g-ext-chi2int-min16"]) < int(v["g-nuwro-carbon-total-chi2int"]) < int(v["g-ext-chi2int-max16"])
    assert int(v["g-ext-chi2int-min16"]) < int(v["g-nuwro-total-chi2int"]) < int(v["g-ext-chi2int-max16"])
    # 3D, the flux-correlation bootstrap (FD-FLUX-BOOT-REPORT.md; DECISION-20261027 limitation plan item 3). Under
    # FD-FLUX-BOOT-BINDING ruling 2 only the correlation variant's 16-84% percentile band of the total chi2 may be
    # described, beside Stage G's chi2 and the offset (median - chi2), as estimation scatter given these universes under
    # PPFX and the nu-e + IMD constraint: never as an interval for the true chi2, never the basic band. The summary keys
    # range over the four 16-cell predictions, as sens-flux-fall-lo/hi do; edges are floored/ceiled to bound the values.
    fb = d["fboot"]
    assert fb["schema"] == "fd-flux-boot-readout/1"
    band = fb["bands"]["correlation"]
    edge, off = [], []
    for name, k in PRED.items():
        b = band[name]; t = b["total"]; hat = b["chi2_stage_g"]
        sg = next(p for p in d["g"]["predictions"] if p["name"] == name)["total"]["chi2"]
        assert abs(hat - sg) < 1e-9 and abs(hat - float(v[f"g-{k}-total-chi2"])) < 0.005, \
            f"3D's chi2 for {name} is not Stage G's"
        lo, hi = t["percentiles"]["16"], t["percentiles"]["84"]
        assert lo < hat < hi
        v[f"fb-{k}-lo"], v[f"fb-{k}-hi"] = f"{lo:.0f}", f"{hi:.0f}"
        v[f"fb-{k}-offset"] = f"{t['offset_median_minus_centre']:.2f}"
        if b["ndf"] == 16:
            edge.append(max(hat - lo, hi - hat) / hat)
            off.append(t["offset_median_minus_centre"] / hat)
    assert len(edge) == 4 and min(off) > 0, "expected the four 16-cell predictions, each with a positive offset"
    v["fb-edge-min"] = f"{math.floor(1000 * min(edge)) / 10:.1f}"
    v["fb-edge-max"] = f"{math.ceil(1000 * max(edge)) / 10:.1f}"
    v["fb-offset-relmax"] = f"{math.ceil(1000 * max(off)) / 10:.1f}"
    v["fb-replicates"] = str(fb["constants"]["replicates"])
    v["fb-universes"] = str(fb["constants"]["universes"])
    pcts = fb["constants"]["percentiles"]
    assert 16 in pcts and 84 in pcts, "the 16-84% band is not in the readout's percentiles"
    v["fb-plo"], v["fb-phi"] = "16", "84"                  # the band ruling 2 allows (FD-FLUX-BOOT-BINDING.md section 2)
    # 1A, the GENIE v3 held-out bias test (FD-F1-REPORT.md; DECISION-20261027 limitation plan item 1): "a bias test at
    # two held-out GENIE v3 truths, not a coverage test" (the readout's labels.f1). Per tune, the ensemble (row 7) and the
    # noise-free closure (row 8) are graded against the full C_total + C_resp; the leave-out-GENIE+MEC and model-only
    # grades are descriptive (FD-F1-BINDING.md ruling 2). The held-out group is never pooled with the F0b groups.
    f1 = d["f1"]
    assert f1["schema"] == "fd-f1-readout/1" and "not a coverage test" in f1["labels"]["f1"]
    assert f1["triggers"]["rule"] == d["f0b"]["triggers"]["rule"], "F1's trigger rule is not F0b's"
    f0b_truths = {t["name"]: t for t in d["f0b"]["truths"]}
    rest = {t["name"]: t for t in f1["truths"] if t["group"] != "held-out"}
    assert 9 in f1["controls"]["passed"] and rest == f0b_truths, "control 9: F1 does not re-grade F0b's truths as recorded"
    held = {t["name"]: t for t in f1["truths"] if t["group"] == "held-out"}
    sig = f1[A["f1sig"]]["C_total"]          # the per-cell relative sigma of the reported matrix
    zmax, bsig, mo = [], [], []
    for tune in ("g18", "ar23"):
        v[f"f1-tune-{tune}"] = d[f"f1meta-{tune}"]["generator"].removeprefix("genie_v3_").replace("_", r"\_")
        for rec, k in ((f"F1_genie_v3_{tune}", f"f1-{tune}"), (f"F1_closure_genie_v3_{tune}", f"f1-closure-{tune}")):
            t = held.pop(rec)
            assert t["graded"] and t["own_vertex"] is None and t["grade_matrix"] == A["rep"]
            gr, se, md = t["grade"], t["sensitivity"], t["model_only"]
            assert gr["cells"] == CELLS and se["matrix"] == "C_total minus genie_mec + " + A["x"]
            assert not t["listed"] and not gr["cells_abs_z_gt_2"] and not gr["p_lt_0.01"], f"{rec} is listed"
            v[f"{k}-chi2"], v[f"{k}-p"] = f"{gr['chi2']:.2f}", p_tex(gr["p"])
            i = max(range(16), key=lambda j: abs(gr["z"][j]))
            v[f"{k}-zmax"], v[f"{k}-zcell"] = f"{abs(gr['z'][i]):.2f}", CELLS[i]
            v[f"{k}-sens-chi2"], v[f"{k}-sens-p"] = f"{se['chi2']:.2f}", p_tex(se["p"])
            v[f"{k}-mo-chi2"] = f"{md['chi2']:.2f}"
            v[f"{k}-mo-cells"] = ", ".join(md["cells_abs_z_gt_2"]) or "---"
            v[f"{k}-n"] = str(t["n_experiments"])
            zmax.append(max(abs(z) for z in gr["z"]))
            bsig.append(max(abs(b) / s for b, s in zip(t["bias"], sig)))
            assert bsig[-1] < 1, f"{rec}: a cell's bias is not below its reported sigma"
            v[f"{k}-bsig"] = f"{math.ceil(100 * bsig[-1]) / 100:.2f}"   # per record, ceiled: the ledger probes all four
            mo.append(md["chi2"])
    assert not held, f"unexpected held-out records: {sorted(held)}"
    assert v["f1-g18-n"] == v["f1-ar23-n"] and v["f1-closure-g18-n"] == v["f1-closure-ar23-n"] == "1"
    v["f1-n"] = v["f1-g18-n"]
    # the note prints the model-only cells once, for AR23's "both its records", and none at G18 (review of 589f0780, SF2)
    assert v["f1-ar23-mo-cells"] == v["f1-closure-ar23-mo-cells"] != "---", "AR23's two records differ in model-only cells"
    assert v["f1-g18-mo-cells"] == v["f1-closure-g18-mo-cells"] == "---", "a G18 record has a model-only cell beyond 2 sigma"
    # "below the reported uncertainty in every cell": |b| / sigma, sigma from C_total + C_resp alone, under one in all
    # four records; z's denominator also carries the noise of the mean, so |b| / sigma >= |z|. Ceiled to bound them.
    assert max(bsig) < 1 and max(bsig) >= max(zmax)
    v["f1-zmax-ceil"] = f"{math.ceil(100 * max(zmax)) / 100:.2f}"
    v["f1-bsig-ceil"] = f"{math.ceil(100 * max(bsig)) / 100:.2f}"
    v["f1-mo-chi2-min"], v["f1-mo-chi2-max"] = f"{math.floor(min(mo))}", f"{math.ceil(max(mo))}"
    gt = f1["triggers"]["by_group"]["held-out"]
    v["f1-grp-truths"], v["f1-grp-cells"] = str(gt["truths"]), str(gt["cells"])
    v["f1-grp-zcells"], v["f1-grp-ptruths"] = str(gt["cells_abs_z_gt_2"]), str(gt["truths_p_lt_0.01"])
    v["f1-grp-refcells"] = f"{gt['gaussian_reference_cells']:.2f}"
    v["f1-grp-reftruths"] = f"{gt['gaussian_reference_truths']:.2f}"
    # the held-out group stays out of all_graded, so F0b's pooled denominators are unchanged
    assert gt["truths"] == 4 and f1["triggers"]["all_graded"] == d["f0b"]["triggers"]["all_graded"]
    # Eq. (1)'s pion constant against the charged-pion mass, first order in the unfolding, under this arm's matrix:
    # "at most" the largest |shift| / sigma over the cells (ceiled), and the shift's full-covariance norm
    em = d["eav"]["first_order_unfolded"][ARMS[arm]["dp"]]
    v["eav-cellmax"] = f"{math.ceil(100 * em['max_abs_over_sigma']) / 100:.2f}"
    v["eav-coherent"] = f"{em['norm_sqrt_dCinvd']:.2f}"
    # at prior level, on the completeness denominator (control C1: bitwise the 135 denom_nd): the weight share that
    # changes fine E_avail bin, and "no bin by more than" the largest |relative change| of the seven (ceiled)
    td = d["eav0"]["truth_denom"]
    assert d["eav0"]["control_C1"]["bitwise_equal"] and len(td["ebins_all_rel_change"]) == 7
    v["eavbin-share"] = f"{100 * td['weight_share_changing_fine_eavail_bin']:.2f}"
    v["eavbin-max"] = f"{math.ceil(10000 * max(abs(x) for x in td['ebins_all_rel_change'])) / 100:.2f}"
    # the stopped 1B test: the sentence says gate D failed, the diagnosis localized nothing within its K_MAX bands, and
    # the count of cells whose sigma ratio lies outside the window; each is asserted so a changed readout stops the run
    gd, dg = d["gated"], d["diag1b"]
    lo, hi = gd["window"]
    assert gd["verdict"] == "FAIL" and dg["verdict"] == "NOT LOCALIZED" and dg["L1_named_bands"]["n_sets"] == 0
    assert dg["rho"] == gd["rho"] and dg["window"] == gd["window"] and len(gd["rho"]) == 16
    v["cov1b-ncells-out"] = str(sum(not lo <= r <= hi for r in gd["rho"]))
    v["cov1b-win-lo"], v["cov1b-win-hi"] = f"{lo:.1f}", f"{hi:.1f}"
    v["cov1b-rho-min"], v["cov1b-rho-max"] = f"{min(gd['rho']):.2f}", f"{max(gd['rho']):.2f}"
    v["cov1b-kmax-word"] = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}[dg["k_max"]]
    v["cov1b-nbands"] = str(len(dg["per_band"]))
    # Stage 0 stopped: both definitions fail 0a and pass 0b. The note names the families below the per-family bar and
    # says whether each pooled value meets its bar, so both are asserted here
    s0 = d["stage0"]
    rl, rs = s0["rules"], s0["results"]
    assert s0["mode"] == "binding" and s0["verdict"] == "STOP" and rl["form"] == "M2"
    assert all(not rs[k]["0a"]["pass"] and rs[k]["0b"]["pass"] for k in ("J", "H2"))
    v["s0-cfam-min"], v["s0-pooled-min"] = f"{rl['c_family_min']:.2f}", f"{rl['pooled_min']:.2f}"
    low = {"J": ("NuWro", "GiBUU"), "H2": ("GiBUU",)}
    for k, fams in low.items():
        c = {f: x["c_M2"] for f, x in rs[k]["0a"]["families"].items()}
        assert {f for f in c if c[f] < rl["c_family_min"]} == set(fams), f"Stage 0 {k}: the families below the bar changed"
        for f in fams:
            v[f"s0-{k.lower()}-{f.lower()}"] = f"{c[f]:.3f}"
        v[f"s0-{k.lower()}-pooled"] = f"{rs[k]['0a']['pooled_M2']:.3f}"
    assert rs["J"]["0a"]["pooled_M2"] < rl["pooled_min"] <= rs["H2"]["0a"]["pooled_M2"], "the pooled clauses changed"
    # the note calls Stage 0's sets the J (109) and H2 (27) cells of sec_5d.tex; GiBUU's one fold departs in every cell
    assert (rs["J"]["0a"]["families"]["GiBUU"]["n_pairs"], rs["H2"]["0a"]["families"]["GiBUU"]["n_pairs"]) == (109, 27)
    # R10 ended INCOMPLETE: no configuration passed, and none met the residual leg at any departure
    rv = d["r10"]["verdict"]
    assert rv["verdict"] == "INCOMPLETE" and rv["passing"] == [] and rv["n_decisive"] == len(rv["per_config"])
    assert all(x["leg_b_departures"] == 0 for x in rv["per_config"].values())
    v["r10-nconfig"] = str(rv["n_decisive"])
    v.update(ll5d_port_values(d))
    return v


# LL5D (ported 2026-11-16, DECISION-20261116-joseph-paper-batch.md items 14 and 24; the coordinator's go): only the
# keys sec_fived16.tex's LL5D paragraph prints, computed as the paper branch's make_values_fived16.py computes them
# (draft/methods-short-20261109 037431430: ll5d_verdicts' class mapping and magnitude clause, the ll5d-ntoys and
# ll5d-cellres lines of its declaration-text values, and ll5d_repair_words, verbatim in substance). No readout changes.
# check_ll5d_port.py compares every key here with the paper branch's values_fived16.tex.
LL5D_PORTED = ("ll5d-a1a2-keys", "ll5d-a1a2-at", "ll5d-ntoys", "ll5d-cellres", "ll5d-njoint-min", "ll5d-njoint-max",
               "ll5d-kjoint-all", "ll5d-chi2ndf-min", "ll5d-chi2ndf-max", "ll5d-ar23-minus2-names", "ll5d-ar23-all-names")
_LL5D_CLASS = {(True, True): "under-joint", (True, False): "under-joint-only", (False, True): "under-cells"}
# the paragraph's hand-typed reading of each (truth, reading)'s class, asserted against the readout below
LL5D_PRINTED_CLASS = {("g18", "minus2"): "under-joint-only", ("g18", "all"): "under-joint-only",
                      ("ar23", "minus2"): "under-joint", ("ar23", "all"): "under-joint"}


def _ll5d_cells(cs):
    return cs[0] if len(cs) == 1 else ", ".join(cs[:-1]) + " and " + cs[-1]


def ll5d_repair_words():
    """The repair's two precisions, from amendment A1a.2's own statement of the defect and the fix
    (LL5D-AMENDMENT-A1A2.md :11-13, :59-60), asserted present there (the paper's ll5d_repair_words)."""
    a = (ROOT / f"{FD}/LL5D-AMENDMENT-A1A2.md").read_text()
    assert "is float64 and the bank's tdw is float32" in " ".join(a.split())
    assert "rounds both sides' key columns to float32" in " ".join(a.split())
    return {"ll5d-a1a2-keys": "float64 and float32", "ll5d-a1a2-at": "float32"}


def ll5d_port_values(d):
    """LL5D's printed keys from the two pinned readout records and the pinned declaration text."""
    v, per, nj, cn, ks = {}, {}, [], [], set()
    for t in ("g18", "ar23"):
        x = d["ll5d" + t]
        assert x["schema"] == "ll5d-b/1" and x["step"] == "readout" and x["truth"] == t, (t, x["schema"], x["step"])
        assert set(x["evaluations"]) == {f"{t}/all", f"{t}/minus2"} and x["clipcheck_sha256"].startswith("9632540e")
        for r in ("minus2", "all"):
            e = x["evaluations"][f"{t}/{r}"]
            assert x["verdicts"][f"{t}/{r}"] == e["verdict"] and all(q["passes"] for q in e["reading_rule"].values())
            g = e["grade"]
            assert g["ndf"] == 16 and len(g["cell_flag"]) == len(g["counts"]) == len(g["k_cell"]) == 16
            fl = [f"R{c:02d}" for c, f in enumerate(g["cell_flag"]) if f]
            assert all(g["counts"][c] <= g["k_cell"][c] for c, f in enumerate(g["cell_flag"]) if f)
            assert g["joint_flag"] == (g["joint_count"] <= g["k_joint"])
            if e["verdict"] == "COVERS":
                assert not g["joint_flag"] and not fl
                per[(t, r)] = "covers"
            else:
                assert e["verdict"] == "UNDER-COVERS", e["verdict"]
                per[(t, r)] = _LL5D_CLASS[(bool(g["joint_flag"]), bool(fl))]
            if t == "ar23":
                v[f"ll5d-{t}-{r}-names"] = ("cell " if len(fl) == 1 else "cells ") + _ll5d_cells(fl) if fl else "none"
            nj.append(g["joint_count"]); cn.append(g["chi2_mean_over_ndf"]); ks.add(g["k_joint"])
    assert per == LL5D_PRINTED_CLASS, f"the paragraph's hand-typed classes differ from the readout: {per}"
    assert len(ks) == 1 and max(nj) <= min(ks), "one joint threshold, every reading at or below it"
    v["ll5d-njoint-min"], v["ll5d-njoint-max"], v["ll5d-kjoint-all"] = str(min(nj)), str(max(nj)), str(ks.pop())
    v["ll5d-chi2ndf-min"], v["ll5d-chi2ndf-max"] = f"{min(cn):.1f}", f"{max(cn):.1f}"
    l5 = d["ll5ddecl"]
    (res,) = re.findall(r"by §6's per-cell resolution, ([0-9.]+)", l5)
    v["ll5d-cellres"] = res
    ((lo, hi),) = re.findall(r"\| toys \(both readings, shared\) \| ([0-9,]+)–([0-9,]+) \|", l5)
    v["ll5d-ntoys"] = str(int(hi.replace(",", "")) - int(lo.replace(",", "")) + 1)
    v.update(ll5d_repair_words())
    assert set(v) == set(LL5D_PORTED), sorted(set(v) ^ set(LL5D_PORTED))
    return v


def all_values(d=None, d_nopl=None):
    """The with-block values, and each matrix-dependent value without the block under the suffix "-nopl"."""
    v = values(load() if d is None else d, "with")
    w = values(load(NOPL_READOUTS) if d_nopl is None else d_nopl, "without")
    assert set(w) <= set(v), f"keys only without the block: {sorted(set(w) - set(v))[:5]}"
    moved = sorted(k for k in w if w[k] != v[k])
    stray = [k for k in moved if not MATRIX_KEYS.match(k)]
    assert not stray, f"values outside the matrix-dependent families differ without the block: {stray[:8]}"
    # every matrix-dependent key, moved or not, so a table printing both arms never lacks a key
    v.update({f"{k}-nopl": w[k] for k in w if MATRIX_KEYS.match(k)})
    # tab:fived16-sens prints no alpha = 0 column: its caption sends the reader to the unshrunk chi2 of tab:fived16-gen
    # and tab:fived16-gen-target (duplicate routing at 1acece939, Joseph 2026-11-19), so each group's alpha = 0 value
    # must stay the total chi2 those tables print, under both arms
    for k in sorted(k for k in v if re.fullmatch(r"sens-[a-z_]+-[a-z]+-a0(-nopl)?", k)):
        m = re.fullmatch(r"sens-[a-z_]+-([a-z]+)-a0(-nopl)?", k)
        ref = f"g-{m.group(1)}-total-chi2{m.group(2) or ''}"
        assert v[k] == v[ref], f"{k} = {v[k]} is not {ref} = {v[ref]}, which tab:fived16-sens' caption points to"
    for part in ("total", "shape_only"):              # ndf is printed once per block of Table IV and Table 16
        ndf16 = {v[f"g-{k}-{part}-ndf"] for k in PRED.values() if k != "gibuu"}
        assert len(ndf16) == 1, f"the 16-cell predictions' {part} ndf differ: {ndf16}"
    # the total and shape-only chi2 falls with the block, over the five predictions (the referee's corrections, #610)
    gw = table4(load() if d is None else d, "with")                      # Table IV's predictions, both arms
    go = table4(load(NOPL_READOUTS) if d_nopl is None else d_nopl, "without")
    for part in ("total", "shape_only"):
        fall = [1 - gw[n][part]["chi2"] / go[n][part]["chi2"] for n in PRED]
        assert min(fall) > 0, f"a {part} chi2 rises with the block"
        v[f"pl-chi2fall-{part}-lo"], v[f"pl-chi2fall-{part}-hi"] = f"{100 * min(fall):.1f}", f"{100 * max(fall):.1f}"
    v.update(currency_values(load() if d is None else d, v))     # the note's currency UPDATEs (new keys only)
    for k in sorted(k for k in v if PAPER_PREC.match(k)):
        for nk, x in paper_prec(k, v[k]).items():
            assert v.get(nk, x) == x, f"{nk}: {v[nk]!r} against the paper form {x!r}"
            v[nk] = x
    return v


# ---- the note's currency UPDATEs: producers ported from the paper branch (draft/methods-short-20261109 5bbb9d269) ----
def sci(x, sig=2):
    """A number as the paper prints it in scientific form: mantissa \\times10^{exponent}."""
    m, e = f"{x:.{sig - 1}e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"

PRR_TRUTHS = {"gibuu": "A7_gibuu", "q3": "q3"}
PRR_LEVELS = {"F1": (["K2"], ["K10", "K20", "K50"]), "F2": (["C25"], ["C400", "C1000"]),
              "F3": (["MCq"], []), "F4": (["O4r", "O4", "O3", "O2"], [])}
PRR_FACTOR = {"F1": "iterations", "F2": "capacity", "F3": "training statistics", "F4": "observables"}
PRR_LEVEL_PARAMS = {"B0": {"iters": 5, "trees": 100, "leaves": 8}, "K2": {"iters": 2}, "C25": {"trees": 25, "leaves": 4}}
PRR_NUMBER_WORDS = {2: "two", 4: "four", 5: "five", 10: "ten"}
VHALF_CLASSES = {"valid": "valid", "not valid": "notvalid", "rule applies at no truth": "notassessed",
                 "unresolved (noise)": "unresolved"}


def vhalf_verdicts(r):
    """Every key of the bias-half group from the V-HALF readout alone (its per-cell classes; no number computed)."""
    assert r["schema"] == "v-half-readout/1", "the V-HALF readout is not a v-half-readout/1"
    cells = r["readings"]["cells"]
    assert len(cells) == 16, f"the V-HALF readout has {len(cells)} cells"
    cls = {c: x["class"] for c, x in cells.items()}
    bad = sorted(c for c, k in cls.items() if k not in VHALF_CLASSES)
    assert not bad, f"V-HALF cells with a class the paper does not print: {[(c, cls[c]) for c in bad]}"
    n = {v: sum(1 for k in cls.values() if VHALF_CLASSES[k] == v) for v in VHALF_CLASSES.values()}
    counts = r["readings"]["counts"]
    assert all(counts.get(k, 0) == n[v] for k, v in VHALF_CLASSES.items()) and counts.get("no d", 0) == 0, \
        f"the V-HALF readout's counts {counts} disagree with its cells"
    notvalid = sorted(c for c, k in cls.items() if k == "not valid")
    # the paper no longer prints the not-assessed class or its count (Joseph's read of 2026-11-12, item 1): it is empty
    assert n["notassessed"] == 0, "a V-HALF cell is not assessed: §5.2 must print the class and its definition again"
    return {"vhalf-outcome": "some-fail" if notvalid else "none-fail",
            **{f"vhalf-n-{v}": str(n[v]) for v in ("valid", "notvalid", "notassessed", "unresolved")},
            "vhalf-cells-notvalid": ", ".join(notvalid) if notvalid else "none"}


def tier1_values(d):
    """T1-1's keys. (i) PR-1's classes with their direction: FD-PRR section 5.1 classes a factor "increases" when some
    level raises rho by at least the bar and none lowers it by the bar, so the class names no direction of "more". Here
    every "increases" is asserted to come from a reduced setting (fewer iterations, lower capacity, fewer observables or a
    quarter of the training statistics), and every higher iteration count and capacity is asserted to lower rho, by less
    than the bar; the summary and the largest such fall are printed. (ii) IBU at five iterations against (e): its rho is
    asserted negative at both truths, and the root-mean-square bias and the chi2 asserted to move the same way, so one word
    per truth says which way. (iii) RS1 R0's sixteen-cell rounding spread. (iv) ENS1's one deficit, under the amended
    licence (DECISION-20261110-joseph-ens1-deficit-licence.md item 1): every number of its one sentence."""
    v, r = {}, d["prr"]
    rd = r["readings"]
    bar = {f: rd["floor"]["bars"][f] for f in PRR_FACTOR}
    cls = {t: rd["PR-1"][T] for t, T in PRR_TRUTHS.items()}
    falls = []
    for t, T in PRR_TRUTHS.items():
        b0 = r["table"][f"B0/{T}/s991000"]["rho"]
        for f, (reduced, more) in PRR_LEVELS.items():
            dl = {L: r["table"][f"{L}/{T}/s991000"]["rho"] - b0 for L in reduced + more}
            up = [L for L, x in dl.items() if x >= bar[f]]
            down = [L for L, x in dl.items() if x <= -bar[f]]
            assert not down, (f, T, down)
            assert (cls[t][f] == "increases") == bool(up) and (cls[t][f] == "no effect") == (not up), (f, T, cls[t][f])
            assert set(up) <= set(reduced), (f, T, up)
            for L in more:
                assert -bar[f] < dl[L] < 0, (f, T, L, dl[L])
                falls.append(-dl[L])
    v["prr-more-dmax"] = f"{max(falls):.3f}"
    # the summary, grouped by class: "both truths" when the two agree
    parts = {}
    for c in ("increases", "no effect"):
        items = []
        for f in PRR_FACTOR:
            on = (cls["gibuu"][f] == c, cls["q3"][f] == c)
            if any(on):
                items.append(f"{PRR_FACTOR[f]} " + {(True, True): "at both truths", (True, False): "at the GiBUU hybrid truth",
                                                  (False, True): "at the $q_3$ tilt"}[on])
        parts[c] = items
    assert {c for t in cls for c in cls[t].values()} <= {"increases", "no effect"}
    join = lambda xs: xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    v["prr-pr1-increases"], v["prr-pr1-noeffect"] = join(parts["increases"]), join(parts["no effect"])
    kinds = {"F1": "fewer iterations", "F2": "lower capacity", "F3": "a quarter of the training statistics", "F4": "fewer observables"}
    inc = [f for f in PRR_FACTOR if "increases" in (cls["gibuu"][f], cls["q3"][f])]
    v["prr-pr1-reduced-kinds"] = join([kinds[f] for f in inc]).replace(" and ", " or ") if len(inc) > 1 else kinds[inc[0]]
    # (ii) IBU at five iterations against (e)
    for t, T in PRR_TRUTHS.items():
        e, i5 = r["table"][f"B0/{T}/s991000"], r["ibu"][f"K5/{T}/s991000"]
        assert i5["rho"] < 0 < e["rho"], "the text says IBU's rho is negative: it moves past the truth"
        sr, sc = i5["rms_b"] > e["rms_b"], i5["grade"]["chi2"] > e["grade"]["chi2"]
        assert sr == sc, "the root-mean-square bias and the chi2 must move the same way for one word to say it"
        v[f"prr-cmp-{t}"] = "larger" if sr else "smaller"
    # (iii) RS1 R0
    r0 = d["rs1r0"]
    assert r0["controls"]["sigma_J_over_f_pct_reproduces"] == [0.133, 0.055, 0.252] and len(r0["sigma_J_over_f"]) == 16
    # the fresh referee read (RESPONSE.md F6.1): the sixteen cells' rounding spread over each cell's statistical sigma (R0a)
    ra = r0["R0a_summary"]
    v["rnd16-r0a-median"], v["rnd16-r0a-min"], v["rnd16-r0a-max"] = (f"{ra[k]:.2f}" for k in ("median", "min", "max"))
    assert sorted(r0["R0a"])[0] == ra["min"] and len(r0["R0a"]) == 16
    sj = sorted(r0["sigma_J_over_f"])
    v["rnd16-median"] = f"{100 * (sj[7] + sj[8]) / 2:.3f}"
    v["rnd16-min"], v["rnd16-max"] = f"{100 * sj[0]:.3f}", f"{100 * sj[-1]:.3f}"
    assert (v["rnd16-median"], v["rnd16-min"], v["rnd16-max"]) == ("0.133", "0.055", "0.252")
    # (iv) ENS1's one deficit
    bw = d["ens1s2"]["bias"]["stage0c_gibuu"]
    v["ens1-g-rms"], v["ens1-g-rmsc"] = f"{bw['rms']:.6f}", f"{bw['rms_control']:.6f}"
    # the paper's rounded pair (the fresh referee round's minor 8, the director's Gm8 ruling of 2026-11-12); the
    # six-decimal pair stays in the Supplement
    v["ens1-g-rms-r"], v["ens1-g-rmsc-r"] = f"{bw['rms']:.4f}", f"{bw['rms_control']:.4f}"
    v["ens1-g-rms-dpct"] = f"{100 * (bw['rms'] / bw['rms_control'] - 1):.0f}"
    assert (v["ens1-g-rms-r"], v["ens1-g-rmsc-r"], v["ens1-g-rms-dpct"]) == ("0.0565", "0.0560", "1")
    v["ens1-g-drms"], v["ens1-g-floor"] = f"{bw['rms'] - bw['rms_control']:.6f}", f"{bw['delta_rms']:.6f}"
    v["ens1-g-ratio"] = f"{(bw['rms'] - bw['rms_control']) / bw['delta_rms']:.2f}"
    v["ens1-g-dmax"], v["ens1-g-maxfloor"] = f"{bw['max'] - bw['max_control']:.6f}", f"{bw['delta_max']:.6f}"
    assert (v["ens1-g-drms"], v["ens1-g-ratio"], v["ens1-g-dmax"], v["ens1-g-maxfloor"]) == ("0.000512", "1.23", "0.000929", "0.001783")
    return v


def prr_levels_values(d):
    """S8.2's settings table, tab:prr-levels (the codex referee read at 3d75ed5d4, Major 1). Each FD-PRR level
    (FD-PRR-DECLARATION.md:165-172): its rho at the two flagged truths and its change from B0 (table.*.rho, split 991000),
    each setting's PR-1 class, the threshold, and PR-3's newly flagged graded truths, recomputed from the table's grades
    and asserted equal to the readout's own list. Nothing is typed."""
    r, v = d["prr"], {}
    rd, t = r["readings"], r["table"]
    fl = rd["floor"]
    # every setting's threshold is the floor (sec. 5.1 :282): T_Q s_F stays below it, so one number serves all four
    tqs = {f: fl["T_Q"] * fl["s_F"][f] for f in PRR_FACTOR}
    assert all(fl["bars"][f] == fl["bar_floor"] == max(fl["bar_floor"], tqs[f]) for f in PRR_FACTOR)
    # printed as an upper bound ("below"): the maximum rounded up at the third decimal, asserted above the maximum
    v["prr-lev-tqs-max"] = f"{math.ceil(1000 * max(tqs.values())) / 1000:.3f}"
    assert max(tqs.values()) < float(v["prr-lev-tqs-max"]) < fl["bar_floor"]
    levels = [L for f in PRR_FACTOR for part in PRR_LEVELS[f] for L in part]
    assert sorted(levels) == sorted(set(rd["PR-3"]) - {"B0", "IBU_K5"}), "the table's rows are PR-3's levels"
    graded = sorted({k.split("/")[1] for k in t if k.startswith("B0/") and k.endswith("/s991000")})
    flagged0 = {T for T in graded if t[f"B0/{T}/s991000"]["grade"]["flagged"]}
    # Fable's fresh cold read of 7264f975a, 3.1 (the director, 2026-11-16): IBU at five iterations removes the q3-tilt
    # flag (p just above the criterion), keeps the GiBUU hybrid's, and newly flags PR-3's four other truths
    ib = r["ibu"]
    assert not ib[f"K5/{PRR_TRUTHS['q3']}/s991000"]["grade"]["flagged"]
    assert ib[f"K5/{PRR_TRUTHS['gibuu']}/s991000"]["grade"]["flagged"]
    q3k = f"K5/{PRR_TRUTHS['q3']}/s991000"
    v["prr-ibu5-q3-p"] = f"{ib[q3k]['grade']['p']:.3f}"
    assert float(v["prr-ibu5-q3-p"]) > 0.01
    new5 = {T for T in graded if ib[f"K5/{T}/s991000"]["grade"]["flagged"]} - flagged0
    assert new5 == set(rd["PR-3"]["IBU_K5"]["new_flags"]), (new5, rd["PR-3"]["IBU_K5"]["new_flags"])
    v["prr-ibu5-nnew-word"] = PRR_NUMBER_WORDS[len(new5)]
    assert len(graded) == 12 and flagged0 == set(PRR_TRUTHS.values()), "B0 flags exactly the two flagged truths"
    v["prr-lev-nother"] = str(len(graded) - len(flagged0))
    names = {"no effect": "no detected change", "increases": "increases", "reduces": "reduces", "both": "both"}
    for f in PRR_FACTOR:
        for tt, T in PRR_TRUTHS.items():
            v[f"prr-lev-cls-{f}-{tt}"] = names[rd["PR-1"][T][f]]
    for L in levels:
        p3 = rd["PR-3"][L]
        # the caption: no level clears either flagged truth (PR-3's "does not clear at these truths", read per truth)
        assert p3["reading"] == "does not clear at these truths"
        assert all(t[f"{L}/{T}/s991000"]["grade"]["flagged"] for T in PRR_TRUTHS.values()), L
        new = {T for T in graded if t[f"{L}/{T}/s991000"]["grade"]["flagged"]} - flagged0
        assert new == set(p3["new_flags"]), (L, new, p3["new_flags"])
        v[f"prr-lev-{L}-nnew"] = str(len(new))
        for tt, T in PRR_TRUTHS.items():
            x, b0 = t[f"{L}/{T}/s991000"]["rho"], t[f"B0/{T}/s991000"]["rho"]
            v[f"prr-lev-{L}-rho-{tt}"] = f"{x:.3f}"
            v[f"prr-lev-{L}-d-{tt}"] = f"{x - b0:+.3f}"
            assert v[f"prr-lev-{L}-d-{tt}"] not in ("+0.000", "-0.000"), (L, tt)
    return v


def prr_s53_values(d):
    """Section 5.3's four sentences. Each settings claim is recomputed from the readout's table: the (level, truth)
    pairs whose rho rises by more than the threshold are exactly K2 at the q3 tilt and C25 and O2 at both flagged
    truths; dropping W (O4r, O4) or W and q3 (O3) moves rho by less than the printed bound at both truths."""
    r, v = d["prr"], {}
    t, floor = r["table"], r["readings"]["floor"]["bar_floor"]
    lp = PRR_LEVEL_PARAMS
    assert lp["K2"]["iters"] == int("K2"[1:]) and lp["C25"]["trees"] == int("C25"[1:]) and PRR_LEVELS["F1"][0] == ["K2"]
    assert PRR_LEVELS["F2"][0] == ["C25"] and PRR_LEVELS["F4"][0] == ["O4r", "O4", "O3", "O2"]
    levels = [L for f in PRR_FACTOR for part in PRR_LEVELS[f] for L in part]
    dr = {(L, tt): t[f"{L}/{T}/s991000"]["rho"] - t[f"B0/{T}/s991000"]["rho"] for L in levels for tt, T in PRR_TRUTHS.items()}
    up = {k for k, x in dr.items() if x >= floor}
    assert up == {("K2", "q3"), ("C25", "gibuu"), ("C25", "q3"), ("O2", "gibuu"), ("O2", "q3")}, up
    assert all(dr[k] > floor for k in up), "beyond the threshold"
    w = max(abs(dr[(L, tt)]) for L in ("O4r", "O4", "O3") for tt in PRR_TRUTHS)
    v["prr-s53-w-dmax"] = f"{math.ceil(100 * w) / 100:.2f}"
    assert w < float(v["prr-s53-w-dmax"]) <= floor
    v["prr-s53-b0-iters"] = PRR_NUMBER_WORDS[lp["B0"]["iters"]]
    v["prr-s53-k2-iters"] = PRR_NUMBER_WORDS[lp["K2"]["iters"]]
    v["prr-s53-c25-trees"] = str(lp["C25"]["trees"])
    v["prr-s53-c25-leaves"] = PRR_NUMBER_WORDS[lp["C25"]["leaves"]]
    graded = sorted({k.split("/")[1] for k in t if k.startswith("B0/") and k.endswith("/s991000")})
    v["prr-lev-nother-word"] = PRR_NUMBER_WORDS[len(graded) - len(PRR_TRUTHS)]
    return v


def vhalf_band_values(d):
    """S10's bias-half noise band (the codex referee read at 3d75ed5d4, minor 8): its multiplier K, from the V-HALF
    readout's own rule record (readings.rule; v-half/DECLARATION.md sec. 4 :134-142), with the bound's 0.5 asserted."""
    rule = d["vhalf"]["readings"]["rule"]
    assert rule["half"] == 0.5 and rule["floor"] == 0.01 and rule["b"] == "r (1 + d)"
    assert rule["sigma_m"] == "sqrt(((1 + d) nu)^2 + (0.5 sgn(d) - |r|)^2 sigma_d^2)", "S10's sentence states these two terms"
    return {"vhalf-k": f"{rule['K']:g}"}


def mumax_values(d):
    """D2: the bound on how much the two GEANT4 bands' block in LL5D's graded covariance can change a chi2, per tune, from
    the primary matrix C_T (all): 1/(1 - mu_max), with mu_max the largest generalized eigenvalue of (G, M)."""
    r, v = d["ll5dmumax"], {}
    assert r["schema"] == "ll5d-mumax/1" and r["verdict"] == "PASS" and not r["stop"]
    for t in ("g18", "ar23"):
        x = r["truths"][t]
        assert x["products_match"] and x["made_from_match"] and x["removal_control_on_G"]["passes"]
        assert x["removal_control_ll5d_b"]["passes"]
        p = x["primary C_T (all)"]
        assert abs(p["chi2_ratio_bound"] - 1 / (1 - p["mu_max"])) < 1e-12
        v[f"ll5d-mumax-{t}"] = f"{p['mu_max']:.3f}"
        v[f"ll5d-mumax-bound-{t}"] = f"{math.ceil(1000 * p['chi2_ratio_bound']) / 1000:.3f}"   # an upper bound, rounded up
        assert p["chi2_ratio_bound"] <= float(v[f"ll5d-mumax-bound-{t}"])
    return v


def t2a_values(d):
    """Tier 2 (a): where the two-dimensional coverage test's chi2 sits, at each tune (descriptive; its label: no new
    verdict, no cause, no coverage statement at the data's point). split.*: mean chi2 = ebar' C+ ebar + tr(C+ S). by_rank:
    b_k, f_k in C_T's eigenbasis by decreasing eigenvalue; the shares and per-rank means are sums of the recorded
    components. truncated.*: the joint test at the 73 and 139 largest-eigenvalue directions. precision.*: two solvers."""
    v = {}
    ntop = 32          # the director's reading of 2026-11-10: "the 32 largest-eigenvalue directions"
    v["t2a-ntop"] = str(ntop)
    dmax = []
    for t, key in (("ar23", "t2aar23"), ("g18", "t2ag18")):
        x = d[key]
        assert x["schema"] == "t2a/1" and all(c["pass"] for c in x["controls"].values())
        assert x["inputs_sha256"]["score"].startswith(READOUTS["cov2d" + t][1])
        sp, br, tr, pr = x["split"], x["by_rank"], x["truncated"], x["precision"]
        b, f, lam = br["b_k"], br["f_k"], br["lambda_over_lambda1"]
        n = len(b)
        assert n == sp["ndf"] and all(lam[i] >= lam[i + 1] for i in range(n - 1))
        assert abs(sum(b) - sp["ebar_Cplus_ebar"]) < 1e-9 * sp["ebar_Cplus_ebar"] and abs(sum(f) - sp["trace_Cplus_S"]) < 1e-9 * sp["trace_Cplus_S"]
        v[f"t2a-bias-share-{t}"] = f"{100 * sp['share_of_ebar_Cplus_ebar']:.0f}"
        v[f"t2a-bias-ndf-{t}"], v[f"t2a-spread-ndf-{t}"] = f"{sp['ebar_Cplus_ebar_over_ndf']:.1f}", f"{sp['trace_Cplus_S_over_ndf']:.2f}"
        # D1: at C_T' the top-32 share is 1.2 % at AR23, so "under 1 %" no longer holds; it is printed per tune
        top = sum(b[:ntop]) / sum(b)
        v[f"t2a-top-{t}"] = f"{100 * top:.1f}"
        r1, r2 = sorted(int(k) for k in tr)
        assert (r1, r2) == (73, 139)
        beyond = sum(b[r1:]) / sum(b)
        assert abs(beyond - (1 - br["cumulative_at"][str(r1)]["b"] / sp["ebar_Cplus_ebar"])) < 1e-9, "the record's own sum"
        # section 6.2's "dominated by mean bias concentrated in the poorly determined directions ..., with the spread
        # also exceeding C_T's prediction" (the director's ruling 3, 2026-11-14): each word's plain reading
        assert sp["share_of_ebar_Cplus_ebar"] > 0.5 and beyond > 0.5 and sp["trace_Cplus_S_over_ndf"] > 1, t
        assert top < beyond
        v[f"t2a-beyond1-{t}"] = f"{100 * beyond:.0f}"
        v[f"t2a-flow-{t}"] = f"{sum(f[:r1]) / r1:.1f}"
        v[f"t2a-fmid-{t}"] = f"{sum(f[r1:r2]) / (r2 - r1):.1f}"
        v[f"t2a-fhigh-{t}"] = f"{sum(f[r2:]) / (n - r2):.1f}"
        for r in (r1, r2):
            z = tr[str(r)]
            assert z["in_region_count"] == 0 and z["of"] == 300 and z["at_or_below_k_joint"]
            v[f"t2a-kj{r}-{t}"] = str(z["k_joint"])
        assert pr["n_unresolved"] == 0 and all(c["agree"] for c in pr["truncated_counts"].values())
        dmax.append(pr["max_d"])
    v["t2a-r1"], v["t2a-r2"] = "73", "139"
    m, e = f"{max(dmax):.1e}".split("e")
    v["t2a-dmax"] = f"{m}\\times10^{{{int(e)}}}"
    return v


def e96d_values(d):
    """E96D's data result (descriptive; E96D-DECLARATION.md Licence: how the ensemble average and the float64 change move
    the data result; no adoption, no uncertainty or bias, no ranking). §6.1 prints the two maxima."""
    r = d["e96d"]
    assert r["schema"] == "e96-data/1/analysis" and r["label"].startswith("descriptive")
    assert all(c["pass"] for c in r["controls"].values()), "an E96D control failed"
    t = r["sixteen"]
    assert "relative_sigma.C_e alone" in t["label"], "the record's sigma is not C_e's relative sigma"
    rel, z = [abs(x) for x in t["E96_over_e_minus_1"]], [abs(x) for x in t["E96_minus_e_over_sigma_Ce"]]
    cells = [c["cell"] for c in r["cells"]]
    assert len(rel) == len(z) == len(cells) == 16
    assert cells[rel.index(max(rel))] == "R05" and cells[z.index(max(z))] == "R06"
    assert abs(r["quotable"]["E96_max_abs_over_sigma_Ce"]["value"] - max(z)) < 1e-15
    # the float64 copy: every cell's ratio to (e) is exactly 1 in double precision (not a bitwise comparison of the
    # products; hence the text's "the same result to double precision")
    assert all(x == 0.0 for x in t["F64_over_e_minus_1"]) and r["quotable"]["F64_max_abs_over_sigma_Ce"]["value"] == 0.0
    v = {"e96d-maxpct": f"{100 * max(rel):.2f}", "e96d-maxsig": f"{max(z):.2f}"}
    assert v == {"e96d-maxpct": "0.24", "e96d-maxsig": "0.05"}, v
    return v


def rsn_values(d, share_nominal):
    """The RSN readings (RSN-DECLARATION.md rev 3, §2 and §9) as the approved text prints them: §3.1, §3.2, §5.2, Table 3's
    caption, §7.1 item 3 and Supplement S4 and S5. The classes the text states in words are asserted here."""
    a, rg = d["rsn"]["arms"], d["rsnregrade"]["arms"]
    g6, sm, wr, tr = a["G6"], a["SM"], a["WR"], a["TR"]["P8"]
    v = {}
    # G6, GiBUU's ratio on the common phase space p_par < 6 GeV/c; SM, the radius-R prior-weighted moving average
    for arm, x in (("g6", g6), ("sm", sm)):
        assert f"{x['P4']['gibuu_trace_share_nominal']:.3f}" == share_nominal, "the nominal share is cmodel-trace-gibuu"
        assert x["P3"]["both_criteria_met_at_the_four_held_out_records"], "the held-out tunes still satisfy both bias criteria"
        q, s = x["P4"]["q"], x["P5"]
        v[f"rsn-{arm}-share"] = f"{x['P4']['gibuu_trace_share']:.3f}"
        v[f"rsn-{arm}-sig-med"], v[f"rsn-{arm}-sig-lo"], v[f"rsn-{arm}-sig-hi"] = (f"{s[k]:.3f}" for k in ("median", "min", "max"))
        assert abs(sorted(s["reported_sigma_ratio"])[8] + sorted(s["reported_sigma_ratio"])[7] - 2 * s["median"]) < 1e-12
    v["rsn-g6-trace"] = f"{g6['P4']['trace_ratio']:.2f}"
    v["rsn-g6-qmed"], v["rsn-g6-qlo"], v["rsn-g6-qhi"] = (f"{x:.2f}" for x in (g6["P4"]["q_median"], min(g6["P4"]["q"]), max(g6["P4"]["q"])))
    v["rsn-sm-trace"] = f"{sm['P4']['trace_ratio']:.3f}"
    v["rsn-sm-qmed"] = f"{sm['P4']['q_median']:.2f}"
    v["rsn-sm-qlo"], v["rsn-sm-qhi"] = f"{min(sm['P4']['q']):.2g}", f"{max(sm['P4']['q']):.3g}"
    assert sm["radius"] == 2
    v["rsn-sm-radius"] = "two"
    # the flag lists: G6 unchanged; SM adds the NuWro hybrid truth, by p alone
    assert g6["P1"]["class"] == "unchanged" and g6["P1"]["listed"] == g6["P1"]["listed_nominal"]
    assert sm["P1"]["class"] == "more flagged" and set(sm["P1"]["listed"]) - set(sm["P1"]["listed_nominal"]) == {"A7_nuwro"}
    nw = next(x for x in rg["SM"]["records"] if x["name"] == "A7_nuwro")["grade"]
    assert nw["p_lt_0.01"] and not nw["cells_abs_z_gt_2"], "flagged by p alone, no cell beyond 2 sigma"
    v["rsn-sm-nuwro-p"] = f"{nw['p']:.2g}"
    # WR: the data shift (P6, class W1) and the four noise-free closures (P7)
    p6, p7 = wr["P6"], wr["P7"]
    fl, sg = [abs(x) for x in p6["delta_over_floor"]], [abs(x) for x in p6["delta_over_sigma"]]
    assert p6["class"] == "W1" and max(sg) < 0.5 and any(x > 2 for x in fl), "at least one cell above 2 floors, every cell below half sigma"
    v["rsn-wr-floor-max"], v["rsn-wr-sig-max"] = f"{max(fl):.1f}", f"{max(sg):.2f}"
    assert not p7["floor"]["breaks_the_prior_closure"] and p7["nuwro"]["rms_class"] == "comparable"
    for t in ("gibuu", "q3"):
        c = p7[t]
        assert c["class"] == "immaterial" and c["flag_weighted"] == c["flag_equal_weights"]
        assert abs(c["chi2_weighted"] - c["chi2_equal_weights"]) <= 0.25 * c["chi2_equal_weights"], "within a quarter"
    assert "does not attribute F0b's flags" in wr["scope"]
    # TR: the matched-event transfer probe's classes (T1 within half sigma, T0 within twice the floor)
    assert (tr["data"]["class"], tr["gibuu"]["class"], tr["q3"]["class"]) == ("T1", "T1", "T0")
    approved = {"rsn-g6-trace": "1.41", "rsn-g6-share": "0.923", "rsn-g6-qmed": "1.12", "rsn-g6-qlo": "0.54",
                "rsn-g6-qhi": "1.77", "rsn-g6-sig-med": "1.002", "rsn-g6-sig-lo": "0.864", "rsn-g6-sig-hi": "1.338",
                "rsn-sm-radius": "two", "rsn-sm-trace": "0.112", "rsn-sm-share": "0.664", "rsn-sm-qmed": "0.50",
                "rsn-sm-qlo": "0.098", "rsn-sm-qhi": "2.23", "rsn-sm-sig-med": "0.934", "rsn-sm-sig-lo": "0.595",
                "rsn-sm-sig-hi": "1.028", "rsn-sm-nuwro-p": "0.0049", "rsn-wr-floor-max": "2.9", "rsn-wr-sig-max": "0.09"}
    assert v == approved, f"the RSN values differ from the approved draft: {sorted(k for k in v if v[k] != approved.get(k))}"
    return v


def t2b_values(d):
    """Tier 2 (b): each of the 16 fake-data records' mean bias against M1 = C_e + C_resp (no C_model), M2 = the statistical
    block and M3 = the statistical block + C_resp, each with the record's own noise of its mean, beside the existing grade's
    matrix. Descriptive: no p-value, no grade or criterion changes. The two closures at the prior (the simulation prior and
    the Tune v1 hybrid, group "prior") are named apart, as the record's own rows."""
    t = d["t2b"]
    assert t["schema"] == "t2b/1" and all(c.get("pass") for c in t["controls"].values())
    R = t["records"]
    assert len(R) == 16
    prior = [k for k, r in R.items() if r["group"] == "prior"]
    assert sorted(prior) == ["A7_mnvtune", "nominal"]
    v = {}
    dz = {k: r["M1"]["max_abs_z"] - r["existing"]["max_abs_z"] for k, r in R.items()}
    kz = max(dz, key=dz.get)
    assert kz == "F1_genie_v3_g18", kz          # the text names the tune
    v["t2b-dz-max"] = f"{dz[kz]:.2f}"
    v["t2b-dz-from"], v["t2b-dz-to"] = f"{R[kz]['existing']['max_abs_z']:.2f}", f"{R[kz]['M1']['max_abs_z']:.2f}"
    moved = {k: (set(r["M1"]["cells_abs_z_gt_2"]), set(r["existing"]["cells_abs_z_gt_2"])) for k, r in R.items()}
    moved = {k: (a, b) for k, (a, b) in moved.items() if a != b}
    assert list(moved) == ["q3"] and moved["q3"][0] - moved["q3"][1] == {"R15"} and moved["q3"][1] <= moved["q3"][0]
    v["t2b-n2-cell"] = "R15"
    for m in ("M2", "M3"):
        x = {k: r[m]["chi2"] for k, r in R.items() if k not in prior}
        lo, hi = min(x, key=x.get), max(x, key=x.get)
        assert (lo, hi) == ("W2", "A7_gibuu"), (m, lo, hi)
        v[f"t2b-{m.lower()}-lo"] = f"{x[lo]:,.0f}".replace(",", "\\,")
        v[f"t2b-{m.lower()}-hi"] = f"{x[hi]:,.0f}".replace(",", "\\,")
    v["t2b-lo-name"], v["t2b-hi-name"] = TRUTH_LABEL["W2"][0], TRUTH_LABEL["A7_gibuu"][0]
    assert all(R[k][m]["chi2"] < 0.5 for k in prior for m in ("existing", "M1", "M2", "M3"))
    v["t2b-prior-max"] = "0.5"
    return v


def recov_values(d):
    """The figure referee read's check A (secondary-results/referee-figure-deformation-20261112): per truth, over the
    supported (E_avail, W) cells with |injected| > 2 %, the recovered fraction f = [(1+r)(1+i) - (1+r_nom)]/i and the
    counts of cells moving opposite to the change (f < 0), partially (0 <= f <= 1) and overshooting (f > 1), with the
    cells lying within three standard errors of a class boundary. Descriptive."""
    r = d["recov"]
    assert r["schema"] == "figure-referee-check-a/1"
    S = r["shapes"]
    v = {"rec-thr": "2"}
    for k, tag in (("GiBUU", "g"), ("W1", "w1"), ("W2", "w2"), ("W3", "w3")):
        s = S[k]
        assert s["n_opposite"] + s["n_partial"] + s["n_overshoot"] == s["n_cells"]
        v[f"rec-{tag}-n"], v[f"rec-{tag}-opp"] = str(s["n_cells"]), str(s["n_opposite"])
        v[f"rec-{tag}-part"], v[f"rec-{tag}-over"] = str(s["n_partial"]), str(s["n_overshoot"])
        v[f"rec-{tag}-fmed"], v[f"rec-{tag}-near"] = f"{100 * s['f_median']:.0f}", str(s["n_within_3sigma_of_a_class_boundary"])
    # the text names EW29 (E_avail 0.8-1.5 GeV, W >= 3 GeV) as opposite at GiBUU and at W1 and W3
    assert all("EW29" in S[k]["opposite_cells"] for k in ("GiBUU", "W1", "W3")) and S["W2"]["n_opposite"] == 0
    w = [S[k] for k in ("W1", "W2", "W3")]
    v["rec-w-fmed-lo"], v["rec-w-fmed-hi"] = f"{100 * min(s['f_median'] for s in w):.0f}", f"{100 * max(s['f_median'] for s in w):.0f}"
    v["rec-w-opp-lo"], v["rec-w-opp-hi"] = str(min(s["n_opposite"] for s in w)), str(max(s["n_opposite"] for s in w))
    v["rec-near-total"] = str(sum(s["n_within_3sigma_of_a_class_boundary"] for s in S.values()))
    assert (v["rec-g-fmed"], v["rec-g-opp"], v["rec-g-n"], v["rec-w-fmed-lo"], v["rec-w-fmed-hi"], v["rec-w-opp-hi"]) == ("63", "12", "39", "56", "88", "10")
    sfm = max(s["sigma_f_max"] for s in S.values())
    v["rec-sigf-max"] = f"{math.ceil(100 * sfm - 1e-9) / 100:.2f}"      # an upper bound, rounded up
    assert sfm < 0.05 and float(v["rec-sigf-max"]) >= sfm
    v["rec-all-opp-max"] = str(max(s["n_opposite"] for s in S.values()))
    assert max(S, key=lambda k: S[k]["n_opposite"]) == "GiBUU"   # the limitation prints "up to rec-all-opp-max of rec-g-n"
    for k, tag in (("GiBUU", "g"), ("W1", "w1"), ("W2", "w2"), ("W3", "w3")):
        v[f"rec-{tag}-near0"], v[f"rec-{tag}-near1"] = str(S[k]["n_within_3sigma_of_f0"]), str(S[k]["n_within_3sigma_of_f1"])
        assert S[k]["n_within_3sigma_of_f0"] + S[k]["n_within_3sigma_of_f1"] == S[k]["n_within_3sigma_of_a_class_boundary"]
    v["rec-w-over-lo"], v["rec-w-over-hi"] = str(min(s["n_overshoot"] for s in w)), str(max(s["n_overshoot"] for s in w))
    # the withheld shapes' most affected SUPPORTED cell (the meaning read: s5e-shapes-ewmax-lo's 16 % is W2's EW37, unsupported)
    sup = [100 * s["max_abs_residual_supported"] for s in w]
    v["rec-w-supmax-lo"], v["rec-w-supmax-hi"] = f"{min(sup):.0f}", f"{max(sup):.0f}"
    assert (v["rec-w-supmax-lo"], v["rec-w-supmax-hi"]) == ("9", "31")
    e = S["GiBUU"]["EW29"]
    v["rec-g-ew29-inj"], v["rec-g-ew29-unf"] = f"{100 * e['injected']:.0f}", f"{100 * e['unfolded_vs_nominal']:.0f}"
    assert (v["rec-g-ew29-inj"], v["rec-g-ew29-unf"]) == ("-30", "21") and e["f"] < 0
    return v


def currency_values(d, base):
    """The note's currency UPDATEs (currency check of 2fe070fec; the combined plan section 6): the keys the paper prints
    for the same records, computed by the paper's own producers (ported above from make_values_fived16.py at
    draft/methods-short-20261109 5bbb9d269, unchanged but for the note's precision checks) and by the inline blocks below,
    copied from that file's values() and groupb_values(). base: this file's other values, which no key here may change."""
    v = {}
    # ENS1 (OUTCOME-20261109-ens1-stab-pass-bias-worse.md), as values() at 5bbb9d269
    e1, e2 = d["ens1s1"], d["ens1s2"]
    st = e1["stability_E96"]
    assert e1["verdict"] == "STAB_PASS" and e1["g0_informative"] and st["passes"] and e1["N"] == 96
    assert st["mean_median"] <= e1["bars"]["median"] and st["mean_max"] <= e1["bars"]["max"]
    assert not e1["stability_F_P10"]["passes"]
    v["ens1-n"] = str(e1["N"])
    v["ens1-median"], v["ens1-max"] = f"{st['mean_median']:.2f}", f"{st['mean_max']:.2f}"
    v["ens1-bar-median"], v["ens1-bar-max"] = f"{e1['bars']['median']:.1f}", f"{e1['bars']['max']:.1f}"
    assert e2["verdict"] == "BIAS_WORSE" and e2["worse"] == ["stage0c_gibuu"] and len(e2["truths_judged"]) == 17
    bw = e2["bias"]["stage0c_gibuu"]
    assert bw["valid"] and not bw["no_worse"] and bw["max"] - bw["max_control"] <= bw["delta_max"]
    assert all(e2["bias"][t]["no_worse"] and e2["bias"][t]["valid"] for t in e2["truths_judged"] if t != "stage0c_gibuu")
    v["ens1-ntruths"] = str(len(e2["truths_judged"]))
    v["ens1-nnoworse"] = str(len(e2["truths_judged"]) - len(e2["worse"]))
    # REF-C2C1 read 2 and REF-G1, as groupb_values() at 5bbb9d269
    c = d["c2c1"]
    assert c["schema"] == "ref-c2c1-readout/1" and c["controls"]["done"]["pass"]
    k10, c1 = c["K10"], c["C1-R1"]
    assert k10["C2-R1"]["reading"] == "differ" and c1["reading"] == "equivalent"
    v["c2c1-nrep"] = str(k10["C2-R1"]["n_replicas"])
    v["c2c1-T"], v["c2c1-q95"], v["c2c1-max"] = (f"{k10['C2-R1'][x]:.1f}" for x in ("T", "q95", "max"))
    v["c1-T"], v["c1-q95"] = f"{c1['T']:.2f}", f"{c1['q95']:.2f}"
    v["c2c1-dibu"], v["c2c1-dibu-k5"], v["c2c1-der"] = f"{k10['D_IBU']:.2f}", f"{c['K5']['D_IBU']:.2f}", f"{c['D_E_R']:.2f}"
    assert abs(k10["D_IBU"] / c["D_E_R"] - k10["rho"]) < 1e-9, "D_IBU / D_E_R is the record's rho"
    assert v["c2c1-der"] == "2.27", "D_E_R is the 2D result's chi2/ndf against the published covariance"
    ek = {int(k): x for k, x in c["D_IBU_every_K"].items()}
    assert sorted(ek) == [1, 2, 3, 4, 5, 10, 15, 20] and abs(ek[10] - k10["D_IBU"]) < 1e-12
    mid = [ek[k] for k in ek if 2 <= k <= 15]
    v["c2c1-dibu-k1"], v["c2c1-dibu-k20"] = f"{ek[1]:.2f}", f"{ek[20]:.2f}"
    v["c2c1-dibu-mid-lo"], v["c2c1-dibu-mid-hi"] = f"{min(mid):.2f}", f"{max(mid):.2f}"
    assert max(mid) < c["D_E_R"], "IBU stays below the 2D result's distance for two to fifteen iterations"
    v["c1-nrep"] = str(c1["n_replicas"])
    assert c1["rank"] == c1["n_replicas"] // 4
    v["c1-rank-word"] = {12: "twelve"}[c1["rank"]]
    v["c1-below-pct"] = f"{100 * (1 - c1['T'] / c1['q95']):.0f}"
    g = d["refg1"]
    assert g["schema"] == "ref-g1-readout/1" and g["R1"]["reading"] == "differ"
    pb = g["printed_beside_R1"]
    assert pb["delta_over_e"] == pb["every_k_and_variant_delta_over_e"]["fold_K5"] and len(pb["pulls"]) == 16
    for i, x in enumerate(pb["delta_over_e"]):
        v[f"ibu16-dof-R{i:02d}"] = f"{100 * x:+.1f}"
    v["ibu16-T"] = f"{g['R1']['T']:.1f}"
    # the note prints REF-G1's T as \lrval{rg1-T} (values_landed.tex, make_values_landed.py): the two must agree
    landed = (OUT.parent / "values_landed.tex").read_text()
    assert re.search(r"\\@namedef\{lr@rg1-T\}\{" + re.escape(v["ibu16-T"]) + r"\}", landed), "rg1-T differs from REF-G1's T"
    # the size of the algorithm dependence in units of each cell's reported sigma (all_values() at 5bbb9d269, item B4)
    cells16 = [f"R{i:02d}" for i in range(16)]
    big = sorted(cells16, key=lambda x: -abs(float(v[f"ibu16-dof-{x}"])))[:3]
    assert big == ["R11", "R06", "R05"], ("the text names R11, R06 and R05", big)
    rat = {x: abs(float(v[f"ibu16-dof-{x}"])) / float(base[f"sig-reported-{x}"]) for x in cells16}
    for x in big:
        v[f"ibu16-dsig-{x}"] = f"{rat[x]:.1f}"
    v["ibu16-dsig-max"] = f"{max(rat.values()):.1f}"
    assert max(rat, key=rat.get) == "R06", "the largest in units of sigma is R06"
    # FD-PRR: the retained fractions at the two flagged truths, as groupb_values() at 5bbb9d269, and IBU's bar
    r = d["prr"]
    assert r["schema"] == "prr-readout/1" and r["verdict"] == "COMPLETE"
    for t, T in PRR_TRUTHS.items():
        e, i5, i200 = r["table"][f"B0/{T}/s991000"], r["ibu"][f"K5/{T}/s991000"], r["ibu"][f"K200/{T}/s991000"]
        assert e["n_S"] == 16
        v[f"prr-rho-e-{t}"], v[f"prr-rho-ibu-{t}"], v[f"prr-rho-ibu200-{t}"] = (f"{x['rho']:.3f}" for x in (e, i5, i200))
        v[f"prr-rms-e-{t}"], v[f"prr-rms-ibu-{t}"] = f"{e['rms_b']:.3f}", f"{i5['rms_b']:.3f}"
        v[f"prr-chi2-e-{t}"], v[f"prr-chi2-ibu-{t}"] = f"{e['grade']['chi2']:.1f}", f"{i5['grade']['chi2']:.1f}"
        assert i5["rho"] < e["rho"], "IBU at five iterations retains less"
    v["prr-ibu-bar"] = f"{r['readings']['floor']['bars']['IBU']:g}"
    fl = r["readings"]["floor"]
    assert all(fl["bars"][f] == fl["bar_floor"] for f in PRR_FACTOR), "one threshold serves the four settings"
    v["prr-floor"] = f"{fl['bar_floor']:g}"
    v.update(tier1_values(d))
    v.update(prr_levels_values(d))
    v.update(prr_s53_values(d))
    v.update({k: x for k, x in vhalf_verdicts(d["vhalf"]).items() if k != "vhalf-outcome"})   # a class, not printed words
    v.update(vhalf_band_values(d))
    v.update(t2a_values(d))
    v.update(mumax_values(d))
    v.update(t2b_values(d))
    v.update(e96d_values(d))
    v.update(rsn_values(d, base["cmodel-trace-gibuu"]))
    # U10's TR sentence (sec_method.tex): no cell beyond half its reported sigma at the data or at the two flagged truths
    tr = d["rsn"]["arms"]["TR"]["P8"]
    assert all(tr[t]["cells_beyond_half_sigma"] == [] for t in ("data", "gibuu", "q3")), "a TR cell lies beyond half sigma"
    # RS1's arm ratios (supp_literal_values() at 5bbb9d269, S8.4) and the tie-keeping residual (literal_values())
    st, ro = d["rs1read"]["statistics"]["ratio"], d["rs1read"]["readouts"]
    for arm, tag in (("S_ref", "sref"), ("S_omni", "somni"), ("B1023", "b1023")):
        v[f"rs1-ratio-{tag}-153"] = f"{st[arm]['functionals_153']['M']:.3f}"
        v[f"rs1-ratio-{tag}-16"] = f"{st[arm]['cells_16']['M']:.3f}"
    v["rs1-ratio-v153"], v["rs1-ratio-v16"] = sci(st["V"]["functionals_153"]["M"]), sci(st["V"]["cells_16"]["M"], 3)
    assert (v["rs1-ratio-sref-153"], v["rs1-ratio-somni-153"], v["rs1-ratio-somni-16"]) == ("0.959", "0.947", "0.857")
    # G4, the run-period figure's steps against 1A-1F (lrows_values() at 5bbb9d269); the unfolded 1G-1M step is the one
    # sec_systematics.tex already prints, typed, as (+6.89 +- 0.46) %
    rp = d["runper"]
    for k, tag in (("PB", "pb"), ("PC", "pc")):
        q = rp["panels"][k]
        assert q["reference"] == "1A\u20131F"
        v[f"rp-{tag}-reco"] = f"{q['reco_step_pct']:.2f}"
        v[f"rp-{tag}-unf"], v[f"rp-{tag}-unf-se"] = f"{q['unfolded_step_pct']:.2f}", f"{q['unfolded_step_noise_pct']:.2f}"
    assert (v["rp-pb-unf"], v["rp-pb-unf-se"]) == ("6.89", "0.46")
    assert (v["rp-pb-reco"], v["rp-pc-reco"], v["rp-pc-unf"], v["rp-pc-unf-se"]) == ("5.99", "1.26", "1.85", "0.64")
    e = rp["pz_edges_GeV"]
    lo = [i for i in range(len(e) - 1) if e[i] >= 1.5 and e[i + 1] <= 8.0]
    for lvl, tag in (("reco_ratio", "reco"), ("unfolded_ratio", "unf")):
        x = [rp["panels"]["PC"][lvl][i] for i in lo]
        assert min(x) > 1, "every 1N-1P bin below 8 GeV/c lies above 1A-1F"
        v[f"rp-pc-lev-{tag}-lo"], v[f"rp-pc-lev-{tag}-hi"] = f"{100 * (min(x) - 1):.1f}", f"{100 * (max(x) - 1):.1f}"
    v.update(recov_values(d))                                   # U6
    clash = sorted(k for k in v if k in base and base[k] != v[k])
    assert not clash, f"a currency key would change an existing value: {clash[:8]}"
    return {k: x for k, x in v.items() if k not in base}


def render(v):
    lines = ["% Generated by make_values_fived16.py from the committed readouts it pins by sha256. Do not edit.",
             "% Regenerate: python3 docs/analysis-note/make_values_fived16.py",
             "% \\fvval{key} prints a value and stops the build on an unknown key. \\fvpending{what} marks an input that has",
             "% not landed; it prints [PENDING: what], which build_all.sh refuses (the PDF text check), so it never ships.",
             r"\makeatletter",
             r"\providecommand{\fvval}[1]{\@ifundefined{fv@#1}{\errmessage{values_fived16: no value '#1'}}{\@nameuse{fv@#1}}}",
             r"\providecommand{\fvpending}[1]{\textbf{[PENDING: #1]}}"]
    for k in sorted(v):
        lines.append(rf"\@namedef{{fv@{k}}}{{{v[k]}}}")
    lines.append(r"\makeatother")
    return "\n".join(lines) + "\n"


def check_figures():
    """The figures the note and the paper print equal their committed sources and the sidecars' digests."""
    bad = []
    for name, (src_dir, pin) in FIGURES.items():
        got = OUT.parent / "figures" / name
        src = ROOT / FD / src_dir / name
        side = json.loads(src.with_suffix(".json").read_text())["pdf_sha256"]
        h = [hashlib.sha256(x.read_bytes()).hexdigest() if x.exists() else "missing" for x in (got, src)]
        if not (h[0] == h[1] == side and side.startswith(pin)):
            bad.append(f"{name}: installed {h[0][:12]}, source {h[1][:12]}, sidecar {side[:12]}, pinned {pin}")
    return bad


def _sentence(text, anchor):
    """The sentence of `text` that contains `anchor` (sentences end at a full stop followed by a space and a capital)."""
    i = text.index(anchor)
    # a full stop before the anchor ends the previous sentence; the lookahead reads the whole text, so an anchor that
    # opens its sentence is found (a search of text[:i] cannot see the capital at i)
    start = max([m.end() for m in re.finditer(r"\.\s+(?=[A-Z\\])", text) if m.end() <= i] + [text.rfind("\n", 0, i) + 1])
    m = re.search(r"\.(\s+(?=[A-Z\\])|\s*$)", text[i:], re.M)
    return text[start:i + (m.start() + 1 if m else len(text) - i)]


def check_listed_claims(f0b, texts, f0b_nopl=None, f0=None):
    """Each LISTED_CLAIMS sentence agrees with these F0b readouts' listed truths (and a "ctotal" sentence with F0's);
    returns the failures."""
    f0b_nopl = load(NOPL_READOUTS)["f0b"] if f0b_nopl is None else f0b_nopl
    f0 = load()["f0"] if f0 is None else f0
    listed_f0 = {x["truth"] for x in f0["triggers"]["listed"]}
    listed = {x["truth"] for x in f0b["triggers"]["listed"]}
    without = {x["truth"] for x in f0b_nopl["triggers"]["listed"]}
    graded = {t["name"] for t in f0b["truths"] if t.get("graded")}
    bad = []
    for name, anchor, rule in LISTED_CLAIMS:
        text = texts[name]
        if text.count(anchor) != 1:
            bad.append(f"{name}: {anchor!r} occurs {text.count(anchor)} times, not once; re-declare the sentence")
            continue
        sent = _sentence(text, anchor)
        keyed = set(re.findall(r"\\fvval\{f0b-([A-Za-z0-9_]+)-(?:zmax|p|pr|prel|cells|chi2|chi2int)\}", sent))
        keyed_nopl = set(re.findall(r"\\fvval\{f0b-([A-Za-z0-9_]+)-(?:zmax|p|pr|prel|cells|chi2|chi2int)-nopl\}", sent))
        typed = {t for t in graded if TRUTH_LABEL[t][1] in sent}
        unknown = (keyed | keyed_nopl) - graded
        if unknown:
            bad.append(f"{name}: {anchor!r} keys truths the readout does not grade: {sorted(unknown)}")
        got = {"keyed": sorted(keyed), "keyed without": sorted(keyed_nopl), "typed": sorted(typed),
               "listed with": sorted(listed), "listed without": sorted(without)}
        kind = rule["kind"]
        if kind == "keys":
            ok = keyed == listed and typed == listed and not keyed_nopl
        elif kind == "without":
            ok = (without - listed) <= typed and (typed | keyed | keyed_nopl) <= without
        elif kind == "ctotal":
            ok = typed == listed_f0
        elif kind == "both":
            fam = (lambda t: rule["family"] in t.lower()) if "family" in rule else (lambda t: True)
            ok = typed == {t for t in listed | without if fam(t)}
        else:
            ok = sum("gibuu" in t for t in listed) == rule["gibuu"] and all(t in listed for t in rule["also"])
        if not ok:
            bad.append(f"{name}: {anchor!r} ({kind}) disagrees with the pinned F0b readouts: {got}")
    return bad


def read_claim_texts():
    return {name: (OUT.parent / name).read_text() for name in {c[0] for c in LISTED_CLAIMS}}


def check_file(path, text):
    """--check's comparison: the committed file equals a fresh generation."""
    return path.exists() and path.read_text() == text


def self_test():
    """A wrong pin must be refused, and a committed file differing in one value must fail --check."""
    ok = True
    key = next(iter(READOUTS))
    rel, pin = READOUTS[key]
    READOUTS[key] = (rel, "0" * 8)
    try:
        load()
        print("  FAIL a wrong sha256 pin was not refused"); ok = False
    except SystemExit:
        print("  ok   a wrong sha256 pin is refused")
    READOUTS[key] = (rel, pin)
    text = render(all_values())
    stale = text.replace(r"\@namedef{fv@f0b-stage0c_gibuu-zmax}{1.76}", r"\@namedef{fv@f0b-stage0c_gibuu-zmax}{1.8}")
    if stale == text:
        print("  FAIL the plant did not apply (R06's z is not 1.76)"); ok = False
    else:
        with tempfile.TemporaryDirectory() as tmp:          # run --check's own comparison against the stale file
            f = Path(tmp) / OUT.name
            f.write_text(stale)
            if check_file(f, text):
                print("  FAIL --check passed a file with R06's z printed as 1.8"); ok = False
            else:
                print("  ok   --check fails on a file with R06's z printed as 1.8")
            f.write_text(text)
            if not check_file(f, text):
                print("  FAIL --check failed a fresh file"); ok = False
            else:
                print("  ok   --check passes a fresh file")
    d = load()                                               # the data product's H2 counts must agree with H2's
    d["dp"]["h2"]["unreported_boxes"] = d["dp"]["h2"]["unreported_boxes"][:-1]
    try:
        values(d)
        print("  FAIL a data product with one unreported box fewer was accepted"); ok = False
    except AssertionError:
        print("  ok   a data product whose H2 counts differ from the definition's is refused")
    d = load()
    d["dp"]["cells"][3]["box"] = dict(d["dp"]["cells"][3]["box"], W=[0.0, 1.8])
    try:
        values(d)
        print("  FAIL a data product with a changed box was accepted"); ok = False
    except AssertionError:
        print("  ok   a data product whose boxes differ from H2's is refused")
    # 1A: an F1 readout that re-grades an F0b truth differently (control 9), or lists a held-out record, is refused
    for what, plant in (("re-grades an F0b truth differently",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "A7_gibuu")["grade"].update(chi2=1.0)),
                        ("lists a held-out record",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_genie_v3_ar23").update(listed=True)),
                        ("gives AR23's closure no model-only cell beyond 2 sigma",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_closure_genie_v3_ar23")["model_only"]
                         .update(cells_abs_z_gt_2=[])),
                        ("gives a G18 record a model-only cell beyond 2 sigma",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_genie_v3_g18")["model_only"]
                         .update(cells_abs_z_gt_2=["R00"])),
                        ("has a held-out cell with |b| above its sigma",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_closure_genie_v3_g18")["bias"]
                         .__setitem__(11, 2 * d["f1"][ARMS["with"]["f1sig"]]["C_total"][11]))):
        d = load()
        plant(d)
        try:
            values(d)
            print(f"  FAIL an F1 readout that {what} was accepted"); ok = False
        except AssertionError:
            print(f"  ok   an F1 readout that {what} is refused")
    d = load()                                               # a fifth cell below the decided four must be refused
    next(c for c in d["h2"]["reporting_cells"] if c["id"] == 11)["stability"] = 0.15
    try:
        values(d)
        print("  FAIL an H2 definition whose four lowest-stability cells differ from the decided ones was accepted"); ok = False
    except AssertionError:
        print("  ok   an H2 definition whose four lowest-stability cells differ from the decided ones is refused")
    # GENCMP: each fact the text states about Table IV's predictions is asserted, so each plant must be refused
    for what, plant in (("has a sample that failed B0", lambda d: d["gdefs"]["status"]["gibuu_H"].update(B0=False)),
                        ("gives a Table IV chi2 that is not its 2 x 2 corner",
                         lambda d: d["gdefs"]["table_2x2"]["nuwro"]["CH"]["analysis_definitions"]["reported"].update(total=1.0)),
                        ("moves a cell by 0.08 sigma", lambda d: d["gdefs"]["generators"]["genie_cv"]["CH"]["delta_over_sigma"]
                         .__setitem__(0, 0.08)),
                        ("gives GiBUU's GENIE-hydrogen total above carbon",
                         lambda d: d["gch"]["generators"]["gibuu"]["CH_genie_hydrogen"]["chi2"]["reported"]["total"]
                         .update(chi2=46.0)),
                        ("has native NuWro disagree", lambda d: d["gnat"]["generator_definitions"]["rule"].update(agree=False)),
                        ("puts a quadrant sum above the 3D central value",
                         lambda d: d["gover"]["quadrants"]["QA"]["3D"].update(d_pct=0.1)),
                        ("has a diag readout computed from another Stage G readout",
                         lambda d: d["diag"]["inputs_sha256"].update(g_readout="0" * 64)),
                        ("ran Stage G's chain on another NuWro",
                         lambda d: next(p for p in d["g"]["predictions"] if p["name"] == "nuwro")["total"].update(chi2=1.0))):
        d = load()
        plant(d)
        try:
            values(d)
            print(f"  FAIL a GENCMP readout that {what} was accepted"); ok = False
        except AssertionError:
            print(f"  ok   a GENCMP readout that {what} is refused")
    # E2: each fact the text states about C_model's target is asserted, so each plant must be refused
    def e2_set(d, n, field, x):       # one chi2 changed in e2.json and in the receipt alike, its delta kept consistent
        r = d["e2"]["chi2"]["with"][n]["total"]
        assert d["e2sens"].count(repr(r[field])) == 1
        d["e2sens"] = d["e2sens"].replace(repr(r[field]), repr(x))
        r[field] = x
        r["delta"] = r["CH"] - r["carbon"]
    for what, plant, why in (("gives a carbon chi2 that is not Table IV's", lambda d: e2_set(d, "nuwro", "carbon", 128.0),
                              "not Table IV's"),
                             ("puts GiBUU's CH total with CH shape ratios above its carbon value",
                              lambda d: e2_set(d, "gibuu", "CH", 46.0), "comes from C_model's"),
                             ("changes GENIE + MEC's component", lambda d: d["e2"]["S_CH"][0].__setitem__(0, 0.0),
                              "only NuWro's and GiBUU's"),
                             ("leaves NuWro's component unchanged",
                              lambda d: d["e2"]["S_CH"].__setitem__(1, list(d["e2"]["S_carbon"][1])),
                              "NuWro's and GiBUU's components change"),
                             ("leaves NuWro's chi2 unmoved",
                              lambda d: e2_set(d, "nuwro", "CH", d["e2"]["chi2"]["with"]["nuwro"]["total"]["carbon"] + 0.0),
                              "every prediction's chi2 moves"),
                             ("records a failed control",
                              lambda d: d.update(e2sens=d["e2sens"].replace("PASS control C0", "FAIL control C0", 1)),
                              "controls changed")):
        d = load()
        plant(d)
        try:
            values(d)
            print(f"  FAIL an E2 readout that {what} was accepted"); ok = False
        except AssertionError as e:
            if why in str(e):
                print(f"  ok   an E2 readout that {what} is refused")
            else:
                print(f"  FAIL an E2 readout that {what} was refused by another guard: {e}"); ok = False
    # the quadrant sentence: each fact it states is asserted, so each plant must be refused
    def xz(d, i, z):                                  # one r = 1 z changed in k.json
        d["xk"]["primary"]["r1"]["z"][i] = z
    for what, plant, why in (("puts a quadrant beyond one standard deviation", lambda d: xz(d, 2, -1.01),
                              "no quadrant lies beyond one standard deviation"),
                             ("measures the statistical correlation", lambda d: d["xk"].update(route="B"),
                              "bounded, not measured"),
                             ("bounds a fifth band", lambda d: d["xk"]["bounded"].append("band:Extra"),
                              "four systematic terms are bounded"),
                             ("changes its reading inside the family",
                              lambda d: d["xk"]["primary"].update(changes_at=[0.5]), "agreement holds over the family"),
                             ("has a d that is not C-R's", lambda d: d["xk"]["d"].__setitem__(0, 1.01 * d["xk"]["d"][0]),
                              "X's d is not C-R's"),
                             ("gives a chi2 at r = 0 that its blocks do not",
                              lambda d: d["xk"]["primary"]["r0"].update(chi2_4=1.2), "rebuilt from the blocks"),
                             ("gives a chi2 at r = 1 below that at r = 0",
                              lambda d: d["xk"]["primary"]["r1"].update(chi2_4=1.0), "the family's largest")):
        d = load()
        plant(d)
        try:
            values(d)
            print(f"  FAIL a quadrant readout that {what} was accepted"); ok = False
        except AssertionError as e:
            if why in str(e):
                print(f"  ok   a quadrant readout that {what} is refused")
            else:
                print(f"  FAIL a quadrant readout that {what} was refused by another guard: {e}"); ok = False
    # the printed bounds: rounding chi2 to nearest (1.2402 -> 1.24) or p up (0.8714 -> 0.88) must be refused
    for name, wrong, what in (("bound_up", lambda x: f"{x:.2f}", "the chi2 bound rounded to nearest"),
                              ("bound_down", lambda x: f"{math.ceil(100 * x) / 100:.2f}", "the p bound rounded up")):
        keep = globals()[name]
        globals()[name] = wrong
        try:
            values(load())
            print(f"  FAIL {what} was accepted"); ok = False
        except AssertionError as e:
            if "a printed bound is not a bound" in str(e):
                print(f"  ok   {what} is refused")
            else:
                print(f"  FAIL {what} was refused by another guard: {e}"); ok = False
        finally:
            globals()[name] = keep
    # the listed-truth sentences: silent on the committed tree, and each plant must fail at the sentence it changed
    d, dn, texts = load(), load(NOPL_READOUTS), read_claim_texts()
    if check_listed_claims(d["f0b"], texts, dn["f0b"]):
        print("  FAIL the committed listed-truth sentences disagree with the pinned F0b readouts"); ok = False
    else:
        print(f"  ok   the {len(LISTED_CLAIMS)} committed listed-truth sentences agree with the pinned F0b readouts")
    # the world fixture: the two arms' readouts exchanged, as a re-pin to the wrong arm would leave them. The sentences
    # that state the reported list, the without-only addition or the abstracts' single GiBUU truth must fail; the
    # sentences that name the union cannot tell the arms apart and must stay silent
    fails = check_listed_claims(dn["f0b"], texts, d["f0b"])
    swapped = {f"{n}: {a!r}" for n, a, r in LISTED_CLAIMS if any(b.startswith(f"{n}: {a!r}") for b in fails)}
    want = {f"{n}: {a!r}" for n, a, r in LISTED_CLAIMS if r["kind"] not in ("both", "ctotal")}  # ctotal reads F0
    if swapped == want:
        print(f"  ok   the arms' readouts exchanged fail exactly the {len(want)} sentences that tell them apart")
    else:
        print(f"  FAIL the arms' readouts exchanged failed {sorted(swapped)}, not {sorted(want)}"); ok = False
    for what, name, anchor, edit in (
            ("keys a truth the readout does not list", "paper_body.tex", "the flagged truths ($p<",
             lambda t: t.replace(r"by $p$ alone ($p\fvval{f0b-q3-prel}$)", r"by $p$ alone ($p\fvval{f0b-q3-prel}$, $\fvval{f0b-W3-pr}$)", 1)),
            ("drops a listed truth's keys", "paper_body.tex", "the flagged truths ($p<",
             lambda t: t.replace(r"($p\fvval{f0b-A7_gibuu-prel}$; cells \fvval{f0b-A7_gibuu-cells})", "", 1)),
            ("names the wrong truth as listed only without the block", "paper_body.tex", "also meets the flagging criterion",
             lambda t: t.replace(r"the GiBUU $\Eavail$ shape also meets", r"the NuWro $\Eavail$ shape also meets", 1)),
            ("drops the truth listed only without the block", "sec_q3_fived16.tex",
             "The fake-data bias therefore exceeds the stated thresholds",
             lambda t: t.replace(r"and also at the GiBUU $\Eavail$ shape without $C_{\mathrm{PL,5D}}$; the bias", "; the bias", 1)),
            ("drops a GiBUU truth of its family", "sec_fived16_gen.tex", "so the GiBUU comparison carries that limitation",
             lambda t: t.replace(r"thresholds at the GiBUU hybrid truth under the reported covariance, and also",
                                 r"thresholds under the reported covariance, and also", 1)),
            ("omits a truth F0 lists", "paper_body.tex", r"Under $C_{\mathrm{total}}$ alone, the right-hand columns",
             lambda t: t.replace(r"the synthetic $q_3$ tilt and the NuWro $(\pT,\pPar,\Eavail)$ shape, the last by $p$ alone",
                                 r"and the synthetic $q_3$ tilt, the last by $p$ alone", 1)),
            ("loses its anchor", "main_paper.tex", "at a GiBUU-like truth and at a synthetic momentum-transfer tilt find",
             lambda t: t.replace("at a GiBUU-like truth and at a synthetic", "at GiBUU-like truths and at a synthetic", 1))):
        planted = dict(texts, **{name: edit(texts[name])})
        if planted[name] == texts[name]:
            print(f"  FAIL the plant that {what} did not apply"); ok = False
            continue
        hit = [b for b in check_listed_claims(d["f0b"], planted, dn["f0b"]) if b.startswith(f"{name}: {anchor!r}")]
        if hit:
            print(f"  ok   a {name} sentence that {what} fails")
        else:
            print(f"  FAIL a {name} sentence that {what} passed"); ok = False
    d = load()                                               # a readout listing one more truth fails the "keys" sentences
    d["f0b"]["triggers"]["listed"].append({"truth": "W3", "cells": [], "p_lt_0.01": True})
    if len([b for b in check_listed_claims(d["f0b"], texts, dn["f0b"]) if "(keys)" in b]) == 2:
        print("  ok   a readout that lists one more truth fails both enumerating sentences")
    else:
        print("  FAIL a readout that lists one more truth did not fail both enumerating sentences"); ok = False
    v = all_values()
    if (v["f0b-listed-names"], v["f0b-listed-names-nopl"]) != (r"the synthetic $q_3$ tilt and the GiBUU hybrid truth",
                                                                r"the synthetic $q_3$ tilt, the GiBUU $\Eavail$ shape and the GiBUU hybrid truth"):
        print(f"  FAIL f0b-listed-names are {v['f0b-listed-names']!r} and {v['f0b-listed-names-nopl']!r}"); ok = False
    else:
        print("  ok   f0b-listed-names name the listed truths with and without the block, in the readouts' order")
    dn = load(NOPL_READOUTS)                                 # a value outside the matrix-dependent families must not move
    dn["s1"]["trace_share"] = {k: x * 1.01 for k, x in dn["s1"]["trace_share"].items()}
    try:
        all_values(load(), dn)
        print("  FAIL a without-block value outside the matrix-dependent families that differs was accepted"); ok = False
    except AssertionError:
        print("  ok   a without-block value outside the matrix-dependent families that differs is refused")
    name = next(iter(FIGURES))                               # a figure that is not its source must fail --check
    with tempfile.TemporaryDirectory() as tmp:
        fig = OUT.parent / "figures" / name
        keep = Path(tmp) / name
        keep.write_bytes(fig.read_bytes())
        try:
            fig.write_bytes(keep.read_bytes() + b"%")
            if check_figures():
                print("  ok   an installed figure that differs from its committed source fails --check")
            else:
                print("  FAIL a changed installed figure passed"); ok = False
        finally:
            fig.write_bytes(keep.read_bytes())
    if check_figures():
        print("  FAIL the installed figures do not equal their sources"); ok = False
    print("VALUES-FIVED16 SELF-TEST ::", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if not (ROOT / "docs/orchestration").is_dir():   # the standalone note repository carries no readouts
        print("VALUES-FIVED16 :: SKIP (no docs/orchestration: the standalone note repository; the canonical build enforces it)")
        return 0
    if argv[:1] == ["--self-test"]:
        return self_test()
    d = load()
    text = render(all_values(d))
    bad = check_listed_claims(d["f0b"], read_claim_texts())
    if bad:
        sys.exit("VALUES-FIVED16 :: FAIL (a sentence's listed fake-data truths disagree with the pinned F0b readout)\n  "
                 + "\n  ".join(bad))
    if argv[:1] == ["--check"]:
        if not check_file(OUT, text):
            sys.exit("VALUES-FIVED16 :: FAIL (values_fived16.tex differs from a fresh generation; regenerate it)")
        bad = check_figures()
        if bad:
            sys.exit("VALUES-FIVED16 :: FAIL (a printed figure differs from its committed source)\n  " + "\n  ".join(bad))
        print(f"VALUES-FIVED16 :: PASS ({sum(1 for l in text.splitlines() if l.startswith(chr(92) + "@namedef"))} values, "
              f"readouts pinned, {len(FIGURES)} figures equal their sources, {len(LISTED_CLAIMS)} listed-truth sentences agree)")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT.name}: {sum(1 for l in text.splitlines() if l.startswith(chr(92) + "@namedef"))} values")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
