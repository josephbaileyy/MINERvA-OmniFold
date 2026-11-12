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
import gzip
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
    # FD-PRR read (#1006, verdict COMPLETE); filled into the short paper by DECISION-20261109-joseph-abstract-length-prr-fill.md item 2
    "prr": (f"{FD}/fd/receipts-prr/read/cluster/readout.json", "9238f22b"),
    # V-HALF read (#1009); filled into the short paper as a diagnostic (the director, 2026-11-10: Joseph confirmed it)
    "vhalf": ("docs/orchestration/state/2d-closeout/valid-region-20261107/v-half/receipts/read/readout.json", "e7423390"),
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
    "cr": (f"{FD}/fd/gencmp-e/c-r/overlap_refined.json", "f1f2fb78"),
    "xk": (f"{FD}/fd/xcov/run/k/k.json", "f3dc2a34"),
    # the run-period diagnosis's readout (FD-RPD-DECLARATION.md sec. 5; DECISION-20261104-joseph-rpd-sentence.md item 2),
    # computed once from the per-playlist unfolds, so both arms read the same file
    "rpd": (f"{FD}/fd/receipts-rpd/run/readout/fd_rpd.json", "c0b06cfd"),
    # ENS1, the ensemble-averaged estimator (OUTCOME-20261109-ens1-stab-pass-bias-worse.md): stage 1's stability readout
    # (#940) and stage 2's bias readout (#957), each computed once, so both arms read the same files
    "ens1s1": (f"{FD}/fd/rounding-stability-20261106/ensemble/receipts/stage1-a1-analysis/ens1_stage1.json", "7f5a9ce4"),
    "ens1s2": (f"{FD}/fd/rounding-stability-20261106/ensemble/receipts/stage2-a1-analysis/ens1_stage2.json", "c2ee701d"),
    # s5e's assessment of candidate R, the reported estimator (e): the generator-sized change and the rounding probe
    "s5e": ("docs/orchestration/state/s5e/cand/assess_receipt.json", "84266e30"),
    # s5n's development receipt: the lower-capacity variant's GiBUU-to-GENIE experiments (the Supplement's figure S1)
    "s5ndev": ("docs/orchestration/state/s5n/stage1/dev_receipt.json", "1ef4096c"),
    # group B (#1025): the two-dimensional comparisons' read (REF-C2C1, read 2) and the sixteen-cell IBU comparison (REF-G1)
    "c2c1": (f"{FD}/fd/receipts-ref-c2c1/step2/read-2/readout.json", "0ee21301"),
    "refg1": (f"{FD}/fd/receipts-ref-g1/a1-read/readout.json", "4db170d3"),
    # group B3a: the synthetic q3 tilt's truth check (s5n stage 1) and its weight function (read as text, never imported)
    "s5ntruth": ("docs/orchestration/state/s5n/stage1/truth_check.json", "14ee2800"),
    "s5cpseudo": ("nd-unfolding/s5c_pseudo.py", "d81d4f46"),
    # group B3b: the held-out tunes' ratio gate (F1's prep config and its log of the gate's tiers and k, a text receipt)
    "f1config": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/prep/config-f1.json", "b0c7a0d9"),
    "f1prep": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/logs/prep.log", "f31a996a"),
    # group B2: the two coverage tests' designs, from their declarations, and the null's constants from its code (text)
    "cov2ddecl": (f"{FD}/COV2D-DECLARATION.md", "0328c916"),
    "ll5ddecl": (f"{FD}/LL5D-DECLARATION.md", "6748d418"),
    "nullcode": ("nd-unfolding/fd_1b_null.py", "ec1402db"),
    # group B1: the headline tests' tables. s5e's contract (C3's |t| cut), REF-G1's bars, the two-dimensional coverage
    # test's score records, and the declarations that alone state FD-STAB's pairs and the first 5D test's toys (text)
    "s5econtract": ("docs/orchestration/state/s5e/contract-amendment-3-candidate-R-and-assessment.json", "f6d3791c"),
    "refg1bars": (f"{FD}/fd/receipts-ref-g1/a1-connect1/bars.json", "ba4b6985"),
    "cov2dar23": (f"{FD}/fd/receipts-cov2d/readout/AR23/score_AR23.json", "fe5263e9"),
    "cov2dg18": (f"{FD}/fd/receipts-cov2d/readout/G18/score_G18.json", "84976694"),
    # T1-2: the two-dimensional test's draw-matched nulls (each score's null_digest is asserted to be its file's sha256)
    "cov2dnullar23": (f"{FD}/fd/receipts-cov2d/readout/AR23/null_AR23.json", "80274e52"),
    "cov2dnullg18": (f"{FD}/fd/receipts-cov2d/readout/G18/null_G18.json", "6bd5259d"),
    # T1-2: Tier 2 (a), the descriptive split of the two-dimensional test's chi2 (#1041; T2A declaration, T2-BINDING-1)
    # T1-3: Tier 2 (b), the fake-data biases against smaller matrices (#1039; T2B declaration, T2-BINDING-1: descriptive)
    "t2b": (f"{FD}/fd/tier2-20261110/t2b/t2b.json", "0e281a61"),
    # T1-3: the per-period two-dimensional benchmark's read (OUTCOME-20261107-per-period-2d-benchmark.md, #879)
    "ppbench": ("docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/receipts/read/readout.json", "4872df32"),
    "t2aar23": (f"{FD}/fd/tier2-20261110/t2a/t2a_AR23.json", "33b7fd40"),
    "t2ag18": (f"{FD}/fd/tier2-20261110/t2a/t2a_G18.json", "6757055e"),
    "stabdecl": (f"{FD}/FD-STAB-DECLARATION.md", "6c91c0cc"),
    "fd1bdecl": (f"{FD}/FD-1B-STAGED-DECLARATION.md", "50d9e883"),
    # group C (#1027): the Kish effective sample size of configuration (e)'s final weights on the sixteen cells
    "ess": (f"{FD}/fd/receipts-ess/cluster/ess/ess.json", "d4f1268d"),
    # the two validity rules' read (valid-region lane): V-ATLAS's per-cell effective number and statistical uncertainty
    # T1-1: RS1's R0 read, sigma_J/f on the sixteen cells over the data jitters (the paper's 0.133 % and its range)
    "rs1r0": (f"{FD}/fd/rounding-stability-20261106/receipts/full-a1/read/rs1_r0.json", "724f0c3a"),
    "vregion": ("docs/orchestration/state/2d-closeout/valid-region-20261107/receipts/read/readout.json", "91bb604e"),
    # B1 row 1 and section 3.2: the adopted 2D covariance Q's block sizes. S5's record (statistical replicas, seeds) and
    # Q's budget (its derived counts), both RE-2 part C r2; the run-period term's record (its period unfoldings)
    "s5q": ("docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/s5/s5.json.gz", "5c489837"),
    "budgetq": ("docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/outA/budget_Q.json.gz", "971e8a9d"),
    "plterm": ("docs/orchestration/state/2d-closeout/playlist-term/outputs/playlist_term.json", "5b023478"),
    # #977's L rows (RESPONSE.md 4.2/F4.3, 4.3, F5.3, F5.4, 3.3, m5/Fm7, s11c): one derived readout (l_rows.py) from the
    # read-only pscratch session's receipt (pscr-20261112, f70e805c) and committed sources
    "lrows": ("docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/l-rows-20261112/derived/l_rows.json", "dc3bf511"),
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
# The ratio uses carbon-only NuWro and GiBUU analysis predictions (fd/gencmp/carbon-figure/REPORT.md).
# The modes retain E-A2's with-arm source (FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2-REPORT.md).
FIGURES = {"fd_g_fig_ratio.pdf": ("fd/gencmp/carbon-figure", "1e6d550e"),
           "fd_g_fig_modes.pdf": ("fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2", "0d6fe57c")}
# the readouts that are text receipts, not JSON
TEXT_READOUTS = {"gprobe", "e2sens", "s1code", "s5cpseudo", "f1prep", "cov2ddecl", "ll5ddecl", "nullcode", "stabdecl", "fd1bdecl"}
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
    ("sec_fived16.tex", "truths meet the listing criterion ($p<", {"kind": "keys"}),
    ("sec_fived16.tex", "truths meet it: the GiBUU", {"kind": "without"}),
    ("sec_fived16.tex", "The fake-data bias therefore exceeds the stated thresholds", {"kind": "both"}),
    ("sec_fived16.tex", "so the GiBUU comparison carries that limitation", {"kind": "both", "family": "gibuu"}),
    ("main_paper.tex", "at a GiBUU-like truth and at a synthetic momentum-transfer tilt find", {"kind": "count", "gibuu": 1, "also": ["q3"]}),
    ("main_note.tex", "At a GiBUU-like truth and a synthetic momentum-transfer tilt", {"kind": "count", "gibuu": 1, "also": ["q3"]}),
]

# Pending verdicts of the short methods paper (stageF/methods/methods-short-20261109/variants.md). A sentence that
# depends on a pending verdict is written once per class, \fvcase{key}{class}{text}, inside \fvgroup{group}{...}. While a
# group is pending, the group prints one [PENDING: ...] and no variant; filling it means pinning the record's readout in
# READOUTS and giving every key of the group its class in VERDICTS, which prints exactly one variant per key and writes
# no prose. Each class set is the declaration's, at the line given (paths relative to FD unless they start with docs/).
PR1 = ("reduces", "increases", "both", "no-effect", "undefined")            # FD-PRR-DECLARATION.md:287-292
PR2A = ("less", "more", "same", "undefined")     # FD-PRR-DECLARATION.md:297-298; "undefined": prr_read.ibu_class @ cf76aec7 :308-311
PR2B = ("falls", "rises", "flat", "undefined")   # FD-PRR-DECLARATION.md:299-300; "undefined": prr_read.ibu_k_class @ cf76aec7 :314-317
PR3 = ("clears", "not")                                                    # FD-PRR-DECLARATION.md:307-309
LABEL = ("holds", "not")                                                   # FD-PRR-DECLARATION.md:321-330
# the abstract's IBU sentence, both flagged truths (the pre-read ruling 13, #998): one class per (GiBUU hybrid, q3 tilt)
PRR_ABS = tuple(f"{g}-{q}" for g in PR2A for q in PR2A)
# LL5D-DECLARATION.md §6 :469-481. COVERS / UNDER-COVERS / INVALID at (T, reading); UNDER-COVERS split by what :474
# names (the cells, and whether the joint fraction is under): under-cells (cells, not joint), under-joint (joint and
# cells), under-joint-only (joint, no cell). na: the campaign is not graded. A reading is INVALID when the Cholesky
# reading rule fails (ll5d_b.readout_reading @ ffbbb7455), or the whole step is (its "why").
LL5D_T = ("covers", "under-cells", "under-joint", "under-joint-only", "invalid", "na")
LL5D_FLAG = ("none", "some", "na")       # per (T, reading): weakened passes :478; over-coverage :477; clipping artefact :480-481
# the campaign: graded, or stopped at a gate (§5.2 :427), by the clipping-offset routing (§5.3 :439-440, :692, when the
# decision after it stops the test), or at another STOP trigger fixed in advance (§5.1 :333-335, §11 :684). What follows
# a STOP is decided after it (:66-71; DECISION-20261108-joseph-ll5d-stop-rule.md:28-35).
LL5D_C = ("graded", "gate-failed", "offset-stopped", "stop")
# how a graded campaign got there: directly; past the offset routing by a decision to proceed (:439-440); or with a
# repair chosen after an earlier run stopped (:71; the stop-rule decision item 4). Both of the latter make the readings
# descriptive (the pre-read ruling 8, pending Joseph). na: not graded.
LL5D_ROUTE = ("direct", "offset-proceeded", "repaired", "na")
# one variant's two tunes, unordered (the pre-read ruling 4: one abstract clause per variant, keeping the cell-versus-
# joint distinction): c covers, uc cells only, uj joint only, ujc joint and cells, i invalid
_TL = {"covers": "c", "under-cells": "uc", "under-joint-only": "uj", "under-joint": "ujc", "invalid": "i"}
_TO = ("c", "uc", "uj", "ujc", "i")
LL5D_PAIR = tuple(f"{a}-{b}" for i, a in enumerate(_TO) for b in _TO[i:]) + ("na",)
LL5D_SOME = ("some", "none", "na")
LL5D_CLOSE = ("scope", "none", "na")    # "none" when no reading was graded; the scope itself is stated once (the style pass)
LL5D_STATUS = ("graded", "descriptive", "invalid", "stopped")   # Table 1's status (its caption); no outcome summary: DECISION-20261109-joseph-coverage-case-wording.md item 3
VHALF_O = ("none-fail", "some-fail")                  # DECISION-20261109-joseph-bias-half-rule.md item 1 (counts below)
PENDING_GROUPS = {
    # printed inside [PENDING: ...]: descriptive names only, no internal study labels (round 6, the editor's C4)
    "prr": "the study of what changes the retained prior",
    "ll5d": "the second five-observable coverage test",
    "vhalf": "the per-cell bias-half validity rule",
}
PENDING = {}                                         # key -> (group, class set, or None for a printed value)
for _t in ("gibuu", "q3"):
    for _f in ("F1", "F2", "F3", "F4"):
        PENDING[f"prr-pr1-{_f}-{_t}"] = ("prr", PR1)
    PENDING[f"prr-pr2a-{_t}"] = ("prr", PR2A)
    PENDING[f"prr-pr2b-{_t}"] = ("prr", PR2B)
    for _l in ("fir", "info", "impl", "obs", "stat", "unattr"):
        PENDING[f"prr-label-{_l}-{_t}"] = ("prr", LABEL)
PENDING["prr-pr3-any"] = ("prr", PR3)               # "clears" if some level clears at these truths
PENDING["prr-pr3-ibu"] = ("prr", PR3)
PENDING["prr-pr3-levels"] = ("prr", None)           # the levels that clear, as printed words
PENDING["prr-ibu-bar"] = ("prr", None)              # the IBU's bar, prr_read floor.bars.IBU (the pre-read ruling 14)
PENDING["prr-abs"] = ("prr", PRR_ABS)               # derived: prr_derived()
PENDING["ll5d-campaign"] = ("ll5d", LL5D_C)
PENDING["ll5d-route"] = ("ll5d", LL5D_ROUTE)
PENDING["ll5d-stop-what"] = ("ll5d", None)          # the gate or check a STOP fired at (gate-failed; stop; repaired)
PENDING["ll5d-repair"] = ("ll5d", None)             # the repair, as the record names it (repaired)
PENDING["ll5d-offset"] = ("ll5d", None)             # clipcheck's largest |o_c|, its cell and the bound (offset routes)
PENDING["ll5d-clip-record"] = ("ll5d", None)        # the Supplement S9 clipping record (the director's option (a))
PENDING["ll5d-route-record"] = ("ll5d", None)       # S9, adaptive routes: the exceeded quantity and its bound, what was visible, the reason, every repair (DECISION-20261109-joseph-coverage-case-wording.md item 2)
for _t in ("g18", "ar23"):
    for _r in ("minus2", "all"):
        PENDING[f"ll5d-{_t}-{_r}"] = ("ll5d", LL5D_T)
        PENDING[f"ll5d-{_t}-{_r}-cells"] = ("ll5d", None)   # the flagged cells with their coverage fractions (counts/300)
        PENDING[f"ll5d-{_t}-{_r}-stats"] = ("ll5d", None)   # joint_count, k_joint, chi2_mean_over_ndf and its se, ndf
        PENDING[f"ll5d-{_t}-{_r}-why"] = ("ll5d", None)     # the failed control, for an invalid reading
        for _x in ("weak", "over", "clip"):
            PENDING[f"ll5d-{_t}-{_r}-{_x}"] = ("ll5d", LL5D_FLAG)
            PENDING[f"ll5d-{_t}-{_r}-{_x}-cells"] = ("ll5d", None)
for _r in ("minus2", "all"):
    PENDING[f"ll5d-abs-{_r}"] = ("ll5d", LL5D_PAIR)  # derived: ll5d_derived()
PENDING["ll5d-abs-close"] = ("ll5d", LL5D_CLOSE)    # derived
for _x in ("anypass", "cellflags", "anyweak", "anyover"):
    PENDING[f"ll5d-{_x}"] = ("ll5d", LL5D_SOME)     # derived
PENDING["ll5d-status"] = ("ll5d", LL5D_STATUS)      # derived
PENDING["vhalf-outcome"] = ("vhalf", VHALF_O)
for _c in ("valid", "notvalid", "notassessed", "unresolved"):
    PENDING[f"vhalf-n-{_c}"] = ("vhalf", None)
PENDING["vhalf-cells-notvalid"] = ("vhalf", None)
# The words \fvval prints for a class key (Table 1). A class key with no entry here cannot be printed by \fvval: its
# value is an \errmessage, so no raw class name reaches a build (round 6 pre-read, NOTES item 24; the director's item 8).
WORDS = {
    **{k: {"reduces": "reduces", "increases": "increases", "both": "reduces and increases", "no-effect": "no effect",
           "undefined": "undefined"} for k, (_, c) in PENDING.items() if c is PR1},
    # Table 1's entry per tune and variant (DECISION-20261109-joseph-coverage-case-wording.md item 3)
    **{k: {"covers": "no under-coverage detected", "under-cells": "under-coverage flagged",
           "under-joint": "under-coverage flagged", "under-joint-only": "under-coverage flagged", "invalid": "invalid",
           "na": ""} for k, (_, c) in PENDING.items() if c is LL5D_T},
}
# filled when a record lands: key -> class (or printed value); a group is filled only when every key has one
# The prior-retention group, from the FD-PRR readout (READOUTS["prr"]) by prr_verdicts() below; main() refuses any
# difference between these and a fresh mapping of the pinned readout. DECISION-20261109-joseph-abstract-length-prr-fill.md
# item 2: filled from the pre-written cases; the readings are descriptive and no level is adopted (BINDING 1 rulings 2-3).
VERDICTS = {
    "prr-pr1-F1-gibuu": "no-effect", "prr-pr1-F2-gibuu": "increases", "prr-pr1-F3-gibuu": "no-effect",
    "prr-pr1-F4-gibuu": "increases",
    "prr-pr1-F1-q3": "increases", "prr-pr1-F2-q3": "increases", "prr-pr1-F3-q3": "no-effect", "prr-pr1-F4-q3": "increases",
    "prr-pr2a-gibuu": "less", "prr-pr2a-q3": "less", "prr-pr2b-gibuu": "falls", "prr-pr2b-q3": "falls",
    "prr-label-fir-gibuu": "not", "prr-label-info-gibuu": "not", "prr-label-impl-gibuu": "holds",
    "prr-label-obs-gibuu": "holds", "prr-label-stat-gibuu": "not", "prr-label-unattr-gibuu": "not",
    "prr-label-fir-q3": "not", "prr-label-info-q3": "not", "prr-label-impl-q3": "holds",
    "prr-label-obs-q3": "holds", "prr-label-stat-q3": "not", "prr-label-unattr-q3": "not",
    "prr-pr3-any": "not", "prr-pr3-ibu": "not", "prr-pr3-levels": "none", "prr-ibu-bar": "0.05",
    "prr-abs": "less-less",
    # the per-cell bias-half rule, from the V-HALF readout (READOUTS["vhalf"]) by vhalf_verdicts(); main() refuses any
    # difference from a fresh mapping of the pinned readout
    "vhalf-outcome": "some-fail", "vhalf-n-valid": "5", "vhalf-n-notvalid": "9", "vhalf-n-notassessed": "0",
    "vhalf-n-unresolved": "2", "vhalf-cells-notvalid": "R03, R05, R07, R08, R10, R11, R12, R13, R15",
}
DERIVED = {"prr": ("prr-abs",),
           "ll5d": ("ll5d-abs-minus2", "ll5d-abs-all", "ll5d-abs-close", "ll5d-anypass", "ll5d-cellflags",
                    "ll5d-anyweak", "ll5d-anyover", "ll5d-status")}


def prr_derived(v):
    """The prior-retention group's derived key: the abstract's class, from both flagged truths' PR-2a classes."""
    return {"prr-abs": f"{v['prr-pr2a-gibuu']}-{v['prr-pr2a-q3']}"}


# prr_read's strings (nd-unfolding/prior_retention/prr_read.py @ db0e801f1: factor_class :300-306, ibu_class :309-312,
# ibu_k_class :315-318, labels_for :321-333, clears :336-340) -> the declared classes of PR1, PR2A, PR2B, LABEL, PR3
PRR_TRUTHS = {"gibuu": "A7_gibuu", "q3": "q3"}
PRR_LABELS = {"fir": "consistent with finite-iteration regularization",
              "info": "consistent with an information limit at these settings",
              "impl": "consistent with an implementation-specific share",
              "obs": "sensitive to the observable set", "stat": "sensitive to training statistics", "unattr": "unattributed"}
PRR_PR2A = {"IBU retains less": "less", "IBU retains more": "more", "same": "same", "undefined": "undefined"}
PRR_PR3 = {"clears at these truths": "clears", "does not clear at these truths": "not"}


def prr_verdicts(r):
    """Every key of the prior-retention group from the FD-PRR readout alone (readout keys only; no number is computed)."""
    assert r["schema"] == "prr-readout/1" and r["verdict"] == "COMPLETE", "the FD-PRR readout is not a COMPLETE prr-readout/1"
    rd, v = r["readings"], {}
    for t, T in PRR_TRUTHS.items():
        for f in ("F1", "F2", "F3", "F4"):
            v[f"prr-pr1-{f}-{t}"] = rd["PR-1"][T][f].replace(" ", "-")
        v[f"prr-pr2a-{t}"] = PRR_PR2A[rd["PR-2a"][T]]
        v[f"prr-pr2b-{t}"] = rd["PR-2b"][T]
        got = set(rd["labels"][T])
        assert got <= set(PRR_LABELS.values()), f"an unknown label at {T}: {got}"
        for k, text in PRR_LABELS.items():
            v[f"prr-label-{k}-{t}"] = "holds" if text in got else "not"
    levels = {k: PRR_PR3[x["reading"]] for k, x in rd["PR-3"].items()}
    v["prr-pr3-ibu"] = levels.pop("IBU_K5")
    v["prr-pr3-any"] = "clears" if "clears" in levels.values() else "not"
    v["prr-pr3-levels"] = ", ".join(k for k, c in levels.items() if c == "clears") or "none"
    v["prr-ibu-bar"] = f"{rd['floor']['bars']['IBU']:g}"
    v.update(prr_derived(v))
    for k, x in v.items():
        cls = PENDING[k][1]
        assert cls is None or x in cls, f"{k}: {x!r} is not a declared class {cls}"
    return v


# the V-HALF readout's per-cell classes (readings.cells[c].class, counts) -> the paper's printed keys
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
    return {"vhalf-outcome": "some-fail" if notvalid else "none-fail",
            **{f"vhalf-n-{v}": str(n[v]) for v in ("valid", "notvalid", "notassessed", "unresolved")},
            "vhalf-cells-notvalid": ", ".join(notvalid) if notvalid else "none"}


def check_vhalf_verdicts(d):
    """VERDICTS' bias-half keys equal a fresh mapping of the pinned V-HALF readout."""
    want = vhalf_verdicts(d["vhalf"])
    have = {k: x for k, x in VERDICTS.items() if PENDING.get(k, ("",))[0] == "vhalf"}
    return [f"{k}: VERDICTS {have.get(k)!r}, the readout {want.get(k)!r}" for k in sorted(set(want) | set(have))
            if have.get(k) != want.get(k)]


def check_prr_verdicts(d):
    """VERDICTS' prior-retention keys equal a fresh mapping of the pinned readout."""
    want = prr_verdicts(d["prr"])
    have = {k: x for k, x in VERDICTS.items() if PENDING.get(k, ("",))[0] == "prr"}
    return [f"{k}: VERDICTS {have.get(k)!r}, the readout {want.get(k)!r}" for k in sorted(set(want) | set(have))
            if have.get(k) != want.get(k)]


def ll5d_derived(v):
    """The like-for-like group's derived keys, from the campaign and the four (tune, reading) classes (variants.md)."""
    camp = v["ll5d-campaign"]
    tr = [(t, r) for t in ("g18", "ar23") for r in ("minus2", "all")]
    if camp != "graded":
        assert all(v[f"ll5d-{t}-{r}"] == "na" for t, r in tr), "a per-tune class on an ungraded campaign"
        assert v["ll5d-route"] == "na", "a route on an ungraded campaign"
        assert all(v[f"ll5d-{t}-{r}-{x}"] == "na" for t, r in tr for x in ("weak", "over", "clip")), "a flag, ungraded"
        return {**{k: "na" for k in DERIVED["ll5d"]}, "ll5d-status": "stopped"}
    assert v["ll5d-route"] != "na" and all(v[f"ll5d-{t}-{r}"] != "na" for t, r in tr), "a graded campaign with na"
    for t, r in tr:                                  # the flags read only where the (tune, reading) was graded
        c = v[f"ll5d-{t}-{r}"]
        for x in ("weak", "over", "clip"):
            assert (v[f"ll5d-{t}-{r}-{x}"] == "na") == (c == "invalid"), f"{t}/{r}: the {x} flag against {c}"
        if c in ("covers", "under-joint-only"):
            assert v[f"ll5d-{t}-{r}-clip"] == "none", "a clipping-artefact reading with no flagged cell"
    out = {}
    for r in ("minus2", "all"):
        a, b = sorted((_TL[v[f"ll5d-{t}-{r}"]] for t in ("g18", "ar23")), key=_TO.index)
        out[f"ll5d-abs-{r}"] = f"{a}-{b}"
    cls = [v[f"ll5d-{t}-{r}"] for t, r in tr]
    some = lambda cond: "some" if cond else "none"  # noqa: E731
    out["ll5d-abs-close"] = "none" if all(c == "invalid" for c in cls) else "scope"
    out["ll5d-anypass"] = some("covers" in cls)
    out["ll5d-cellflags"] = some(any(c in ("under-cells", "under-joint") for c in cls))
    out["ll5d-anyweak"] = some(any(v[f"ll5d-{t}-{r}-weak"] == "some" for t, r in tr))
    out["ll5d-anyover"] = some(any(v[f"ll5d-{t}-{r}-over"] == "some" for t, r in tr))
    # an adaptive route is Descriptive whatever its readings; otherwise no outcome is summarized (the decision, items 2-3)
    out["ll5d-status"] = ("descriptive" if v["ll5d-route"] in ("offset-proceeded", "repaired") else
                          "invalid" if all(c == "invalid" for c in cls) else "graded")
    return out


def ll5d_case(campaign, per=None, route="direct", flags=None, cells=None, text=None):
    """One consistent filling of the like-for-like group, with its derived keys (fill tests and the pre-read pack).

    per[(tune, reading)] -> class (graded only); flags[(tune, reading, x)] -> "some" (x in weak, over, clip), else
    "none" on a graded reading and "na" otherwise; cells[(tune, reading)] or cells[(tune, reading, x)] -> printed
    text; text[key] overrides a printed value (stop-what, repair, offset, -stats, -why).
    """
    per, flags, cells, text = per or {}, flags or {}, cells or {}, text or {}
    graded = campaign == "graded"
    v = {"ll5d-campaign": campaign, "ll5d-route": route if graded else "na",
         "ll5d-stop-what": text.get("stop-what", "[the gate or check]"), "ll5d-repair": text.get("repair", "[the repair]"),
         "ll5d-offset": text.get("offset", "[the largest offset, its cell, and the bound]"),
         "ll5d-clip-record": text.get("clip-record", "[the clipping record]"),
         "ll5d-route-record": text.get("route-record", "[the exceeded quantity and its bound, what was visible when the decision was made, its reason, and every repair]")}
    for t in ("g18", "ar23"):
        for r in ("minus2", "all"):
            c = per.get((t, r), "covers") if graded else "na"
            v[f"ll5d-{t}-{r}"] = c
            v[f"ll5d-{t}-{r}-cells"] = cells.get((t, r), "[cells R.., with their coverage fractions]")
            v[f"ll5d-{t}-{r}-stats"] = text.get((t, r, "stats"), "[joint region: n of 300, flagged at k or fewer, mean chi2/ndf]")
            v[f"ll5d-{t}-{r}-why"] = text.get((t, r, "why"), "[the failed control]")
            for x in ("weak", "over", "clip"):
                v[f"ll5d-{t}-{r}-{x}"] = "na" if c in ("na", "invalid") else flags.get((t, r, x), "none")
                v[f"ll5d-{t}-{r}-{x}-cells"] = cells.get((t, r, x), "[cells R..]")
    v.update(ll5d_derived(v))
    return v


def ll5d_fill_cases():
    """Consistent fillings that between them give every class of every like-for-like key (check_round --fill-test)."""
    out, seen = [], set()
    order = list(_TL)
    for i, a in enumerate(order):                    # every per-variant pair, in each variant, with mixed partners
        for b in order[i:]:
            j = len(out)
            pm = (a, b) if j % 2 else (b, a)
            pa = (order[(j + 1) % 5], order[(j + 3) % 5])
            per = {("g18", "minus2"): pm[0], ("ar23", "minus2"): pm[1], ("g18", "all"): pa[0], ("ar23", "all"): pa[1]}
            flags = {}
            for (t, r), c in per.items():
                if c != "invalid":
                    flags[(t, r, "weak")] = "some" if (j + len(t)) % 2 else "none"
                    flags[(t, r, "over")] = "some" if (j + len(r)) % 3 == 0 else "none"
                    if c in ("under-cells", "under-joint"):
                        flags[(t, r, "clip")] = "some" if j % 2 else "none"
            route = LL5D_ROUTE[j % 3]
            out.append(ll5d_case("graded", per, route, flags))
            for r in ("minus2", "all"):                # the same pair in the other variant
                seen.add((r, out[-1][f"ll5d-abs-{r}"]))
    for a in order:                                  # the pairs each variant has not yet had
        for b in order[order.index(a):]:
            pr = f"{_TL[a]}-{_TL[b]}" if _TO.index(_TL[a]) <= _TO.index(_TL[b]) else f"{_TL[b]}-{_TL[a]}"
            for r, o in (("minus2", "all"), ("all", "minus2")):
                if (r, pr) not in seen:
                    per = {("g18", r): a, ("ar23", r): b, ("g18", o): "covers", ("ar23", o): "covers"}
                    out.append(ll5d_case("graded", per))
                    seen.add((r, pr))
    out.append(ll5d_case("graded", {(t, r): "covers" for t in ("g18", "ar23") for r in ("minus2", "all")}))
    out.append(ll5d_case("graded", {(t, r): "invalid" for t in ("g18", "ar23") for r in ("minus2", "all")}))
    out.append(ll5d_case("graded", {(t, r): "under-cells" for t in ("g18", "ar23") for r in ("minus2", "all")}))
    out += [ll5d_case("gate-failed"), ll5d_case("offset-stopped"), ll5d_case("stop")]
    return out


def prr_fill_cases():
    """Every PR-2a pair (and so every abstract class), with PR-2b cycled."""
    out = []
    for i, cls in enumerate(PRR_ABS):
        g, q = cls.split("-")
        out.append({"prr-pr2a-gibuu": g, "prr-pr2a-q3": q, "prr-pr2b-gibuu": PR2B[i % 4], "prr-pr2b-q3": PR2B[(i + 1) % 4],
                    "prr-abs": cls})
    return out


def pending_lines(verdicts=None):
    """The TeX for the pending groups and keys: a group's state, each key's class (\\fvcase) and printed value."""
    verdicts = VERDICTS if verdicts is None else verdicts
    out = []
    for g in PENDING_GROUPS:
        keys = [k for k, (gg, _) in PENDING.items() if gg == g]
        have = [k for k in keys if k in verdicts]
        assert not have or len(have) == len(keys), f"group {g} is part-filled: {sorted(set(keys) - set(have))[:4]}"
        if have and g in DERIVED:
            want = (ll5d_derived if g == "ll5d" else prr_derived)(verdicts)
            assert all(verdicts[k] == x for k, x in want.items()), f"{g} derived keys {want} disagree with the verdicts"
        out.append(rf"\@namedef{{fvg@{g}}}{{{'FILLED' if have else 'PENDING'}}}")
        out.append(rf"\@namedef{{fvgd@{g}}}{{{PENDING_GROUPS[g]}}}")
    for k, (g, classes) in sorted(PENDING.items()):
        x = verdicts.get(k)
        if x is None:
            out.append(rf"\@namedef{{fvc@{k}}}{{PENDING}}")
            out.append(rf"\@namedef{{fv@{k}}}{{\fvpending{{{k}}}}}")
        elif classes is None:
            out.append(rf"\@namedef{{fvc@{k}}}{{{x}}}")
            out.append(rf"\@namedef{{fv@{k}}}{{{x}}}")
        else:
            assert x in classes, f"{k}: {x!r} is not a declared class {classes}"
            out.append(rf"\@namedef{{fvc@{k}}}{{{x}}}")
            if k in WORDS:
                out.append(rf"\@namedef{{fv@{k}}}{{{WORDS[k][x]}}}")
            else:
                out.append(rf"\@namedef{{fv@{k}}}{{\errmessage{{values_fived16: the class key '{k}' has no printed words}}}}")
    return out

def load(readouts=None):
    data = {}
    for key, (rel, pin) in (READOUTS if readouts is None else readouts).items():
        raw = (ROOT / rel).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if not sha.startswith(pin):
            sys.exit(f"make_values_fived16: {rel} has sha256 {sha[:12]}, pinned {pin}: refusing")
        if rel.endswith(".gz"):          # pinned as the committed .gz bytes, read decompressed
            raw = gzip.decompress(raw)
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
    # group B5 (#1025; the director's ruling (b)): the same bound over the predictions the Supplement's comparison keeps,
    # GENIE CV and GENIE + MEC on CH (as generated) and NuWro and GiBUU on carbon only, from the same readout's fields
    b5 = [x for n in ("genie_cv", "genie_mec") for x in gd["generators"][n]["CH"]["delta_over_sigma"]] + \
         [x for n in ("nuwro", "gibuu") for x in gd["generators"][n]["carbon"]["delta_over_sigma"]]
    d5 = max(abs(x) for x in b5)
    v["gdef-b5-dmax"], v["gdef-b5-dmax-bound"] = f"{d5:.3f}", f"{math.ceil(100 * d5) / 100:.2f}"
    v["gdef-seedmax"] = f"{max(x for n in GENCMP4 for x in gd['generators'][n]['CH']['seed_spread_over_sigma']):.3f}"
    # Q08: NuWro and GiBUU on carbon in the analysis definitions (the text and the note), and the change to CH
    ana = {(n, t): gd["generators"][n][t]["analysis_definitions"]["chi2"][mat] for n in ("nuwro", "gibuu")
           for t in ("carbon", "CH")}
    for n in ("nuwro", "gibuu"):
        for part in ("total", "shape_only"):
            x = ana[n, "carbon"][part]["chi2"]
            v[f"g-{PRED[n]}-carbon-{part}-chi2"], v[f"g-{PRED[n]}-carbon-{part}-chi2int"] = f"{x:.2f}", f"{x:.0f}"
            v[f"g-{PRED[n]}-carbon-{part}-chi2r1"] = f"{x:.1f}"
            v[f"g-{PRED[n]}-carbon-{part}-ndf"] = str(ana[n, "carbon"][part]["ndf"])   # group B5: Table S7's block headings
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
        if name in ("nuwro", "gibuu"):   # group B5 (#1025): the Supplement shows them on carbon only
            v[f"label-{PRED[name]}-carbon"] = base + " (carbon only)"
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
    # group B5 (#1025; the director's ruling (b)): the same bounds over the 16-cell predictions without the CH-corrected
    # NuWro (GENIE CV, GENIE + MEC, Tune v1), from the same records; the readouts hold no carbon-only NuWro record
    def ratios5(fam, alpha):
        return [r["chi2"] / r["chi2_at_alpha_0"] for r in recs if r["family"] == fam and abs(r["alpha"] - alpha) < 1e-12
                and len(r["cells"]) == 16 and r["prediction"] != "nuwro"]
    fl5, other5 = ratios5("flux", 0.1), ratios5("detector", 0.1) + ratios5("lateral", 0.1)
    assert len(fl5) == 3 and len(other5) == 6
    v["sens-b5-flux-fall-lo"], v["sens-b5-flux-fall-hi"] = f"{100 * (1 - max(fl5)):.0f}", f"{100 * (1 - min(fl5)):.0f}"
    v["sens-b5-detlat-fall-max"] = f"{math.ceil(100 * (1 - min(other5))):.0f}"
    joint5 = [r["chi2"] for r in recs if r["family"] == "c_e_systematic" and r["alpha"] == 1.0 and len(r["cells"]) == 16
              and r["prediction"] != "nuwro"]
    assert len(joint5) == 3
    v["sens-b5-joint-chi2-min"] = f"{math.floor(min(joint5)):.0f}"
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
    # the paper's compact cell table (the interim referee round, #1025, group A item 6; the director: purity and the
    # diagonal fraction, the record's "stability", only): per reported cell, from the pinned record, two decimals
    for c in h2["reporting_cells"]:
        if c["reported"]:
            v[f"cell-purity-R{c['id']:02d}"] = f"{c['purity']:.2f}"
            v[f"cell-diag-R{c['id']:02d}"] = f"{c['stability']:.2f}"
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
    # group B5 (#1025; the director's ruling (b)): over the 16-cell predictions without the CH-corrected NuWro
    e5 = [max(band[n]["chi2_stage_g"] - band[n]["total"]["percentiles"]["16"], band[n]["total"]["percentiles"]["84"]
              - band[n]["chi2_stage_g"]) / band[n]["chi2_stage_g"] for n in ("genie_cv", "genie_mec", "mnvtune_v1")]
    o5 = [band[n]["total"]["offset_median_minus_centre"] / band[n]["chi2_stage_g"] for n in ("genie_cv", "genie_mec", "mnvtune_v1")]
    assert all(band[n]["ndf"] == 16 for n in ("genie_cv", "genie_mec", "mnvtune_v1")) and min(o5) > 0
    v["fb-b5-edge-max"], v["fb-b5-offset-relmax"] = f"{math.ceil(1000 * max(e5)) / 10:.1f}", f"{math.ceil(1000 * max(o5)) / 10:.1f}"
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
        # in \mbox, so that a tune name never breaks at a hyphenation point (journal-editor, 2026-11-10)
        v[f"f1-tune-{tune}"] = r"\mbox{" + d[f"f1meta-{tune}"]["generator"].removeprefix("genie_v3_").replace("_", r"\_") + "}"
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
    # ENS1 (OUTCOME-20261109-ens1-stab-pass-bias-worse.md): stage 1 STAB_PASS against FD-STAB's bars; stage 2 BIAS_WORSE at
    # exactly one truth, Stage 0c GiBUU, by its RMS (the MAX within its floor). Each clause the sentence states is asserted
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
    v["ens1-rms-ratio"] = f"{(bw['rms'] - bw['rms_control']) / bw['delta_rms']:.2f}"
    # s5e's assessment of the reported estimator, candidate R = (e) (OUTCOME-20260926-s5e-oi192:68,85; the director's
    # ruling of 2026-11-10 on the interim round's row 2): at the GiBUU-to-GENIE E_avail change, (e)'s largest (E_avail,W)
    # residual and that of the lower-capacity variant (the s5n reference), both in EW29, the cell 0.8 <= E_avail < 1.5 GeV,
    # W >= 3 GeV that the text names; and EW7, the record's "largest cells", several percent off (fig_m3_deformation.py's
    # own test, -10 < r < -2). Then the data rounding probe's median and largest shift, in data sigma (paper and Fig 5)
    a = d["s5e"]
    assert a["candidate"] == "R"
    eg, lc = a["points"]["eavail_gibuu"], a["B0_reference_s5n"]["eavail"]
    assert eg["ew_argmax"] == lc["ew_argmax"] == "EW29"
    assert -10 < 100 * eg["per_functional"]["mean_rel"][7] < -2
    v["s5e-gibuu-ewmax"], v["s5e-gibuu-ewmax-lowcap"] = f"{eg['ew_max_abs_pct']:.0f}", f"{lc['ew_max_abs_pct']:.0f}"
    assert eg["n"] == 20 and lc["n"] == 60
    # the figures' standard errors of the mean, largest over the 42 (E_avail,W) cells (the director's ruling on the batch 2
    # read, M019/M089): Fig 3's three shapes for (e), and Fig S1's GiBUU-to-GENIE experiments for the variant
    se_e = max(100 * x for w in ("W1", "W2", "W3") for x in a["points"][w]["per_functional"]["se_rel"][:42])
    se_lc = max(100 * x for x in d["s5ndev"]["grid"]["C4_eavail_shape"]["per_functional"]["se_rel"][:42])
    # an upper bound is rounded UP (#977 fig3-read: 0.2246 had printed as "at most 0.22")
    up2 = lambda x: f"{math.ceil(100 * x - 1e-9) / 100:.2f}"  # noqa: E731
    v["s5e-shapes-semax"], v["s5n-gibuu-semax"] = up2(se_e), up2(se_lc)
    assert float(v["s5e-shapes-semax"]) >= se_e and float(v["s5n-gibuu-semax"]) >= se_lc
    # #977 s11c: Fig 3 now also draws (e) at the GiBUU-to-GENIE change; its caption's one bound must cover that series too
    assert max(100 * x for x in eg["per_functional"]["se_rel"][:42]) <= se_e
    v.update(groupb_values(d))
    v.update(ess_values(d))
    rp = a["A3"]["data_rounding_probe_over_data_sigma"]
    v["s5e-round-median"], v["s5e-round-max"] = f"{rp['median']:.1f}", f"{rp['max']:.1f}"
    return v


def groupb_values(d):
    """Group B of the interim round (#1025): the numbers limitation-resolver's drafts print, each from its record.
    B6 and section 4.1: the IBU-to-2D distance ratio kappa (the readout's rho; renamed so that rho is only the retained
    fraction), its interval over the paired replicas and the comparisons' statistics (REF-C2C1 read 2). B4a: IBU at five
    iterations against (e), Delta = f_IBU - f_(e) (REF-G1-DECLARATION.md:76), per cell as a fraction of f_(e) and in units
    of sqrt((C_Delta)_cc) (printed_beside_R1, the declared fold_K5). B4b: the retained fractions at the two flagged
    truths (the FD-PRR readout, B0 and IBU K5 and K200 at split s991000) and the noise floor."""
    v = {}
    c = d["c2c1"]
    assert c["schema"] == "ref-c2c1-readout/1" and c["controls"]["done"]["pass"]
    k10, c1 = c["K10"], c["C1-R1"]
    assert k10["C2-R1"]["reading"] == "differ" and c1["reading"] == "equivalent"
    v["c2c1-kappa"] = f"{k10['rho']:.3f}"
    v["c2c1-kappa-lo"], v["c2c1-kappa-hi"] = (f"{x:.3f}" for x in k10["rho_interval"])
    assert k10["rho"] < k10["rho_interval"][0], "the text says the point estimate lies below the interval"
    v["c2c1-nrep"] = str(k10["C2-R1"]["n_replicas"])
    v["c2c1-T"], v["c2c1-q95"], v["c2c1-max"] = (f"{k10['C2-R1'][x]:.1f}" for x in ("T", "q95", "max"))
    v["c1-T"], v["c1-q95"] = f"{c1['T']:.2f}", f"{c1['q95']:.2f}"
    # the fresh referee read (2026-11-11, RESPONSE.md F4.2): the IBU's own distance from the published result, beside the
    # 2D result's, as the record prints them ("printed and read by nothing"; descriptive, no attribution)
    v["c2c1-dibu"], v["c2c1-dibu-k5"], v["c2c1-der"] = f"{k10['D_IBU']:.2f}", f"{c['K5']['D_IBU']:.2f}", f"{c['D_E_R']:.2f}"
    assert abs(k10["D_IBU"] / c["D_E_R"] - k10["rho"]) < 1e-9, "D_IBU / D_E_R is the record's rho"
    assert v["c2c1-der"] == "2.27", "D_E_R is the paper's chi2/ndf against the published covariance"
    # the K scan (the director's ruling on the PRD read of the D_IBU paragraph, 2026-11-11): K = 1, 2-15 and 20
    ek = {int(k): x for k, x in c["D_IBU_every_K"].items()}
    assert sorted(ek) == [1, 2, 3, 4, 5, 10, 15, 20] and abs(ek[10] - k10["D_IBU"]) < 1e-12
    mid = [ek[k] for k in ek if 2 <= k <= 15]
    v["c2c1-dibu-k1"], v["c2c1-dibu-k20"] = f"{ek[1]:.2f}", f"{ek[20]:.2f}"
    v["c2c1-dibu-mid-lo"], v["c2c1-dibu-mid-hi"] = f"{min(mid):.2f}", f"{max(mid):.2f}"
    assert max(mid) < c["D_E_R"], "the text says IBU stays below the 2D result's distance for two to fifteen iterations"
    v["c1-nrep"] = str(c1["n_replicas"])
    v["c1-below-pct"] = f"{100 * (1 - c1['T'] / c1['q95']):.0f}"
    g = d["refg1"]
    assert g["schema"] == "ref-g1-readout/1" and g["R1"]["reading"] == "differ"
    pb = g["printed_beside_R1"]
    assert pb["delta_over_e"] == pb["every_k_and_variant_delta_over_e"]["fold_K5"] and len(pb["pulls"]) == 16
    for i, (x, z) in enumerate(zip(pb["delta_over_e"], pb["pulls"])):
        v[f"ibu16-dof-R{i:02d}"], v[f"ibu16-pull-R{i:02d}"] = f"{100 * x:+.1f}", f"{z:+.2f}"
    v["ibu16-T"] = f"{g['R1']['T']:.1f}"
    r = d["prr"]
    for t, T in PRR_TRUTHS.items():
        e, i5, i200 = r["table"][f"B0/{T}/s991000"], r["ibu"][f"K5/{T}/s991000"], r["ibu"][f"K200/{T}/s991000"]
        assert e["n_S"] == 16
        v[f"prr-rho-e-{t}"], v[f"prr-rho-ibu-{t}"], v[f"prr-rho-ibu200-{t}"] = (f"{x['rho']:.3f}" for x in (e, i5, i200))
        v[f"prr-rms-e-{t}"], v[f"prr-rms-ibu-{t}"] = f"{e['rms_b']:.3f}", f"{i5['rms_b']:.3f}"
        v[f"prr-chi2-e-{t}"], v[f"prr-chi2-ibu-{t}"] = f"{e['grade']['chi2']:.1f}", f"{i5['grade']['chi2']:.1f}"
        assert i5["rho"] < e["rho"], "the text says IBU at five iterations retains less"
    v.update(tier1_values(d))
    v.update(t2a_values(d))
    v.update(period_values(d))
    v.update(t2b_values(d))
    v.update(lrows_values(d))
    # B3a: the synthetic q3 tilt, r = 1 + a z~ (s5c_pseudo.py truth_weight "q3_given_eavail_w"); a and the clip from the
    # code, the event count, the range and in-cell spread of the weight and the two preservation checks from the truth check
    q = d["s5ntruth"]["departures"]["q3_given_eavail_w"]
    m = re.search(r"z = np\.clip\(\(q - mu\[cell\]\) / np\.sqrt\(np\.where\(var > 0, var, 1\.0\)\)\[cell\], -([0-9.]+), ([0-9.]+)\)",
                  d["s5cpseudo"])
    assert m and m.group(1) == m.group(2), "the q3 tilt's clip changed"
    v["q3tilt-clip"] = f"{float(m.group(1)):g}"
    v["q3tilt-a"] = f"{q['amplitude']:g}"
    assert q["rows_outside_grid_with_r_not_1"] == 0 and q["weight_marginal_preserved_1e-6"]
    n = d["s5ntruth"]["rows_in_grid"]
    v["q3tilt-nrows"] = rf"{n / 10 ** 7:.2f}\times10^{{7}}"
    assert 1e7 <= n < 1e8
    v["q3tilt-rmin"], v["q3tilt-rmax"] = f"{q['r_min']:.3f}", f"{q['r_max']:.3f}"
    v["q3tilt-std-lo"], v["q3tilt-std-hi"], v["q3tilt-std-med"] = (f"{q[k]:.2f}" for k in ("in_cell_r_std_min", "in_cell_r_std_max",
                                                                                   "in_cell_r_std_median"))
    def sci(x):
        e = math.floor(math.log10(x)); return rf"{x / 10 ** e:.0f}\times10^{{{e}}}" if round(x / 10 ** e) < 10 else rf"1\times10^{{{e + 1}}}"
    def sci1(x):
        e = math.floor(math.log10(x)); return rf"{x / 10 ** e:.1f}\times10^{{{e}}}"
    v["q3tilt-ewdev"] = sci(q["weight_marginal_EW_ratio_max_abs_dev"])
    m1 = [abs(x - 1) for x in q["M1_ratio"][:42]]
    assert len(q["M1_ratio"]) == 43
    v["q3tilt-m1dev"], v["q3tilt-nfunc"] = sci1(max(m1)), str(len(m1))
    # B3b: the held-out tunes' gated shape ratio (pvl_ratios.py, run unchanged by F1's prep): the gate (stat_max), each
    # tune's events, its tiers and prior-weight shares and the normalization k, as the prep logged them; the region is the
    # sum of the tiers, the same for both tunes
    v["f1-statmax"] = f"{d['f1config']['ratio']['stat_max']:g}"
    nev = {d[f"f1meta-{t}"]["normalisation"]["N_events_in_file"] for t in ("g18", "ar23")}
    assert len(nev) == 1
    v["f1-nevents"] = rf"{nev.pop() / 10 ** 6:.2f}\times10^{{6}}"
    region = set()
    for t in ("g18", "ar23"):
        lm = re.search(r"genie_v3_%s: tiers (\{.*\}), k=([0-9.]+)," % t, d["f1prep"])
        tiers, k = json.loads(lm.group(1)), float(lm.group(2))
        cells = [tiers[x]["cells"] for x in ("own ratio", "coarse cell", "r = 1")]
        share = [tiers[x]["prior_weight_share"] for x in ("own ratio", "coarse cell", "r = 1")]
        assert abs(sum(share) - 1) < 1e-9
        region.add(sum(cells))
        for x, c, sh in zip(("own", "pooled", "one"), cells, share):
            v[f"f1-{t}-tier-{x}"], v[f"f1-{t}-share-{x}"] = f"{c:,}".replace(",", "{,}"), f"{sh:.3f}"
        v[f"f1-{t}-k"] = f"{k:.5f}"
    assert len(region) == 1
    v["f1-region-cells"] = f"{region.pop():,}".replace(",", "{,}")
    # B2: each design number from its declaration's table row, each null constant from fd_1b_null.py (unchanged since
    # cf0505d9); a declaration or code edit that moves one stops here
    def one(pat, txt, what):
        m = re.findall(pat, txt)
        assert len(m) == 1, f"{what}: found {len(m)} times"
        return m[0]
    c2, l5, nc = d["cov2ddecl"], d["ll5ddecl"], d["nullcode"]
    nb, nu, fx, pp, tp = one(r"(\d+) bands, (\d+) universes \(Flux (\d+), 2p2h (\d+), (\d+) bands at 2\)", c2, "COV2D's bank")
    assert int(nb) == 2 + int(tp) and int(nu) == int(fx) + int(pp) + 2 * int(tp)
    v["cov2d-nbands"], v["cov2d-fluxu"], v["cov2d-2p2h"], v["cov2d-twopt"] = nb, fx, pp, tp
    v["cov2d-statrep"] = one(r"\| statistical \| (\d+) three-stream bootstrap replicas", c2, "COV2D's statistical block")
    nrm = {one(r"x̂ × \(1 \+ ([0-9.]+) z\), z ~ N\(0, 1\)", t, w) for t, w in ((c2, "COV2D"), (l5, "LL5D"))}
    assert len(nrm) == 1
    v["cov-norm"] = nrm.pop()
    wk = {one(r"variance ratio from C2 is below ([0-9.]+)", c2, "COV2D weakened"),
          one(r"a pass in a cell whose clipped variance ratio is below ([0-9.]+)", l5, "LL5D weakened")}
    assert len(wk) == 1
    v["cov-weak"] = wk.pop()
    v["ll5d-nint"] = one(r"\| \*\*interaction\*\* \| each of the (\d+) bands", l5, "LL5D interaction")
    v["ll5d-ndet"] = one(r"\| \*\*detector\*\* \| each of the (\d+) bands", l5, "LL5D detector")
    v["ll5d-statrep"] = one(r"replicas b = 1–(\d+) by `s5n_pseudo\.bootstrap_replica`", l5, "LL5D statistical block")
    const = {}
    for k in ("P0", "N_TOYS", "ALPHA_CELLS", "ALPHA_JOINT", "N_MC", "SE_MARGIN", "MATCH_TOL"):
        m = re.findall(r"^%s = ([^#\n]+)" % k, nc, re.M)
        assert len(m) == 1, f"fd_1b_null.py's {k}: found {len(m)} times"
        const[k] = m[0].strip()
    assert const["P0"] == "math.erf(1 / math.sqrt(2))"
    v["null-p0"] = f"{math.erf(1 / math.sqrt(2)):.4f}"
    v["null-ntoys"] = str(int(const["N_TOYS"]))
    a_c, a_j = float(const["ALPHA_CELLS"]), float(const["ALPHA_JOINT"])
    assert a_c == a_j
    v["null-alpha"], v["null-size"] = f"{a_c:g}", f"{a_c + a_j:g}"
    nmc = int(const["N_MC"].replace("_", ""))
    assert nmc == 2 * 10 ** 6
    v["null-nmc"] = rf"{nmc // 10 ** 6}\times10^{{6}}"
    se = float(const["SE_MARGIN"])
    v["null-se-word"] = {3.0: "three"}[se]
    tol = float(const["MATCH_TOL"])
    v["null-tol"] = rf"10^{{{round(math.log10(tol))}}}"
    # B1 (and the paper's sentences that print the same numbers): s5e's closure at the prior and its changed truths
    a = d["s5e"]
    pts, ct = a["points"], d["s5econtract"]["criteria"]["C3"]
    assert pts["nominal"]["n_abs_t_gt_3.6"] == 0 and ct["t_crit"] == 3.6
    v["s5e-tcrit"] = f"{ct['t_crit']:g}"
    v["s5e-nom-n"] = str(pts["nominal"]["n"])
    assert {pts[w]["n"] for w in ("W1", "W2", "W3", "q3", "eavail_gibuu")} == {20}
    v["s5e-shape-n"] = "20"
    v["s5e-nquant"] = str(len(a["functional_names"]))
    v["s5e-nom-tmax"], v["s5e-nom-ewmax"] = f"{pts['nominal']['max_abs_t']:.1f}", f"{pts['nominal']['ew_max_abs_pct']:.2f}"
    sh = [pts[w]["ew_max_abs_pct"] for w in ("W1", "W2", "W3")]
    v["s5e-shapes-ewmax-lo"], v["s5e-shapes-ewmax-hi"] = f"{min(sh):.0f}", f"{max(sh):.0f}"
    v["s5e-q3-ewmax"] = f"{pts['q3']['ew_max_abs_pct']:.0f}"     # whole percent, as the other residuals of Table S10's row 2 (journal-editor, 2026-11-10)
    # REF-G1's thresholds (bars.json: the parametric bootstrap's 0.95 and 0.997 quantiles) and replicas
    b = d["refg1bars"]
    assert b["schema"] == "ref-g1-bars/1" and b["quantile_levels"] == [0.95, 0.997] and b["norm_fraction"] == 0.014
    v["ibu16-q95"], v["ibu16-q997"] = (f"{x:.2f}" for x in b["bars"])
    v["ibu16-nrep"] = str(b["n_replicas"])
    # FD-PRR's tested levels per factor (PR-3's levels: iterations K*, capacity C*, statistics MC*, observables O*)
    lv = set(r["readings"]["PR-3"]) - {"B0", "IBU_K5"}       # the tested levels (the table also holds O5, F4's baseline)
    for f, pre in (("iter", "K"), ("cap", "C"), ("stat", "MC"), ("obs", "O")):
        v[f"prr-nlev-{f}"] = str(sum(1 for x in lv if x.startswith(pre)))
    assert sum(int(v[f"prr-nlev-{f}"]) for f in ("iter", "cap", "stat", "obs")) == len(lv)
    # FD-STAB's disjoint pairs (its declaration) and ENS1's pairs (its stage-1 readout)
    v["stab-npairs"] = one(r"form (\d+) disjoint pairs", d["stabdecl"], "FD-STAB's pairs")
    v["ens1-pairs"] = str(d["ens1s1"]["pairs"])
    # the two-dimensional coverage test: each tune's joint count and flagged cells (score records), its ndf
    for t, key in (("ar23", "cov2dar23"), ("g18", "cov2dg18")):
        gr = d[key]["grade"]
        assert gr["joint_flag"] if "joint_flag" in gr else True
        v[f"cov2d-joint-{t}"] = str(gr["joint_count"])
        fc = gr["flagged_cells"]
        v[f"cov2d-flags-{t}"] = " and ".join(str(c) for c in fc) if len(fc) <= 2 else ", ".join(str(c) for c in fc)
        v[f"cov2d-nflags-{t}"] = {1: "one", 2: "two", 3: "three"}[len(fc)]
        # T1-2: the section 6.2 paragraph's numbers, read from the same score record (were typed at r5:202)
        assert gr["verdict"] == "UNDER-COVERS" and len(gr["counts"]) == len(gr["k_cell"]) == 205
        v[f"cov2d-kjoint-{t}"], v[f"cov2d-ndf-{t}"] = str(gr["k_joint"]), str(gr["ndf"])
        v[f"cov2d-chi2ndf-{t}"], v[f"cov2d-chi2ndf-se-{t}"] = f"{gr['chi2_mean_over_ndf']:.2f}", f"{gr['chi2_mean_over_ndf_se']:.2f}"
        v[f"cov2d-size-{t}"] = f"{gr['size']['per_truth_union_bound']:.4f}"
        v[f"cov2d-kcell-lo-{t}"], v[f"cov2d-kcell-hi-{t}"] = str(min(gr["k_cell"])), str(max(gr["k_cell"]))
        v[f"cov2d-count-lo-{t}"], v[f"cov2d-count-hi-{t}"] = str(min(gr["counts"])), str(max(gr["counts"]))
        v[f"cov2d-nover-{t}"] = str(sum(1 for x in gr["over_covers"] if x))
        v[f"cov2d-nunder-{t}"] = str(sum(1 for c, k in zip(gr["counts"], gr["k_cell"]) if c <= k))
        assert int(v[f"cov2d-nunder-{t}"]) == len(fc), "the flagged cells are those at or below their threshold"
        # the median count beside the median draw-matched expectation (the director, 2026-11-10: the test's reference is
        # the draw-matched content p_c, not P0); the graded null is "null" ("null_minus" serves leave_out_mec only,
        # COV2D-ADDENDUM-A4.md:40, :190)
        nk = "cov2dnull" + t
        nf = ROOT / READOUTS[nk][0]
        assert hashlib.sha256(nf.read_bytes()).hexdigest() == d[key]["null_digest"], "the score was graded on another null"
        nl = d[nk]["null"]
        assert len(nl["p_cell"]) == 205 and nl["ndf"] == gr["ndf"]
        nt = int(one(r"### 5\.1 Statistics per tune, over its (\d+) toys", d["cov2ddecl"], "COV2D's toys"))
        assert max(gr["counts"]) <= nt
        c, pc = sorted(gr["counts"]), sorted(nl["p_cell"])
        v[f"cov2d-count-med-{t}"] = str(c[102])
        v[f"cov2d-pexp-med-{t}"] = f"{nt * pc[102]:.1f}"
        v[f"cov2d-jexp-{t}"] = f"{nt * nl['q_joint']:.1f}"
    assert (v["cov2d-ndf-ar23"], v["cov2d-ndf-g18"]) == ("204", "205"), "the text says the rank drops one direction at AR23"
    # the first five-observable coverage test's declared toys
    v["fd1b-ntoys"] = one(r"\*\*Toys:\*\* (\d+) per truth", d["fd1bdecl"], "FD-1B's toys")
    v["cov2d-ntoys"] = one(r"### 5\.1 Statistics per tune, over its (\d+) toys", d["cov2ddecl"], "COV2D's toys")
    # the nominal Gaussian content of the 300 toys, P0 = erf(1/sqrt 2) (fd_1b_null.py:42-52), printed only beside the
    # draw-matched expectation
    v["cov2d-nominal"] = f"{int(v['cov2d-ntoys']) * math.erf(2 ** -0.5):.0f}"
    assert {d[k]["grade"]["joint_count"] for k in ("cov2dar23", "cov2dg18")} == {0}, "B1 row 8 says no error lies in the region"
    v["prr-floor"] = f"{r['readings']['floor']['bar_floor']:g}"
    # F0b's repetitions as B1 row 3a states them: 20 at each shape change and the q3 tilt, 16 at each hybrid
    f0t = {t["name"]: t["n_experiments"] for t in d["f0b"]["truths"]}
    assert {f0t[t] for t in ("W1", "W2", "W3", "stage0c_gibuu", "q3")} == {20}
    assert {f0t[t] for t in f0t if t.startswith("A7_")} == {16} and len([t for t in f0t if t.startswith("A7_")]) == 5
    fl = r["readings"]["floor"]
    v["prr-sibu"], v["prr-tq"] = f"{fl['s_IBU']:.4f}", f"{fl['T_Q']:.2f}"
    assert f"{fl['bars']['IBU']:g}" == f"{max(fl['bar_floor'], fl['T_Q'] * fl['s_IBU']):g}" and "a transfer" in fl["transfer"]
    return v


def ess_values(d):
    """Group C: the Kish n_eff = (sum w)^2 / sum w^2 of the reported result's simulated events in each of R00-R15
    (fd/receipts-ess README; CITABLE FOR the per-cell and global numbers, NOT CITABLE FOR an uncertainty, coverage or
    validity statement). The printed definition is (B), each event's contribution to the cell integral; (A), the final
    weight wpush * w_truth, must agree with it to the printed figures, so the text may name both."""
    e = d["ess"]
    assert e["schema"] == "ess-e-central/1" and e["verdict"].startswith("PASS"), e["verdict"]
    assert e["binding"]["xsec_flat_bytes_equal"] and e["checks"]["events_in_cells_with_zero_denominator"] == 0
    cells = e["cells"]
    assert sorted(cells) == [f"R{i:02d}" for i in range(16)]
    g = e["global"]["reported_16_cells"]
    for c in list(cells.values()) + [g]:
        a, b = c["A_final_weight"], c["B_contribution"]
        assert a["n_negative"] == b["n_negative"] == 0 and a["n_zero"] == b["n_zero"] == 0, "the text says every weight is positive"
        assert f"{a['n_eff_over_n']:.3f}" == f"{b['n_eff_over_n']:.3f}" and abs(a["n_eff"] / b["n_eff"] - 1) < 1e-6
        assert f"{a['max_share']:.1e}" == f"{b['max_share']:.1e}"
    fr = {k: c["B_contribution"]["n_eff_over_n"] for k, c in cells.items()}
    v = {}
    # the cells split at 0.9 with a gap: the two low cells are below 0.7, every other cell is at least 0.9
    low = sorted((k for k in fr if fr[k] < 0.9), key=lambda k: fr[k])
    high = [k for k in fr if fr[k] >= 0.9]
    assert len(low) == 2 and max(fr[k] for k in low) < 0.7, low
    v["ess-low1-cell"], v["ess-low1"] = low[0], f"{fr[low[0]]:.3f}"
    v["ess-low2-cell"], v["ess-low2"] = low[1], f"{fr[low[1]]:.3f}"
    v["ess-nhigh"] = str(len(high))
    v["ess-high-min"] = f"{min(fr[k] for k in high):.3f}"
    kmax = max(fr, key=fr.get)
    v["ess-max-cell"], v["ess-max"] = kmax, f"{fr[kmax]:.3f}"
    ne = {k: c["B_contribution"]["n_eff"] for k, c in cells.items()}
    kmin = min(ne, key=ne.get)
    assert round(cells[kmin]["A_final_weight"]["n_eff"]) == round(ne[kmin]), "the smallest n_eff prints the same under (A)"
    v["ess-neff-min-cell"], v["ess-neff-min"] = kmin, f"{round(ne[kmin]):,}".replace(",", "\\,")
    ms = max(c["B_contribution"]["max_share"] for c in cells.values())
    mant, ex = f"{ms:.1e}".split("e")
    v["ess-maxshare"] = f"{mant}\\times10^{{{int(ex)}}}"
    v["ess-global"] = f"{g['B_contribution']['n_eff_over_n']:.3f}"
    v["ess-global-prior"] = f"{g['prior_w_truth']['n_eff_over_n']:.3f}"
    nrp = [100 * c["no_reco_partner"]["share_of_sum_B"] for c in cells.values()]
    v["ess-nrp-min"], v["ess-nrp-max"] = f"{min(nrp):.1f}", f"{max(nrp):.1f}"
    # V-ATLAS's first condition (S11) read the prior weights' n_eff; the ESS record's prior_w_truth is the same quantity
    # on the same events, so the two records must agree cell by cell before S11 sets them side by side
    r = d["vregion"]
    assert r["schema"] == "valid-region-readout/1"
    va = r["readings"]["V-ATLAS"]["cells"]
    assert sorted(va) == sorted(cells)
    for k in cells:
        assert abs(va[k]["mc_neff_truth"] / cells[k]["prior_w_truth"]["n_eff"] - 1) < 1e-9, k
    kp = min(va, key=lambda k: va[k]["mc_neff_truth"])
    v["vatlas-neff-min-cell"], v["vatlas-neff-min"] = kp, f"{round(va[kp]['mc_neff_truth']):,}".replace(",", "\\,")
    ks = max(va, key=lambda k: va[k]["stat_rel"])
    v["vatlas-stat-max-cell"], v["vatlas-stat-max"] = ks, f"{100 * va[ks]['stat_rel']:.3f}"
    # the guide's threshold, 5000 effective events, holds under both definitions in every cell
    assert min(ne.values()) > 5000 and va[kp]["mc_neff_truth"] > 5000
    v.update(cov2d_block_values(d))
    return v


def cov2d_block_values(d):
    """B1 row 1 and section 3.2: the sizes of the adopted 2D covariance Q's blocks. The universe block (the director's
    ruling, option (i), 2026-11-10): S5's check refined_j2_38_bands_175_universes gives the weight bands and their
    universes; S5's production outputs 2dc_P_S3_<band><i> give the lateral bands, two universes each; Q's budget lists
    the 43 bands plus the flat normalization. 187 was the July sweep's count (may_44_bands_187_universes), Rvp1pi
    included."""
    s5, bq, pl = d["s5q"], d["budgetq"], d["plterm"]
    assert s5["arm"] == "refined" and bq["arm"] == "refined"
    po = s5["inputs"]["production_outputs"]
    chk = s5["checks"]["refined_j2_38_bands_175_universes"]
    assert chk["ok"] and s5["checks"]["universe_bands_43_plus_norm"]["ok"]
    nwb, nwu = chk["value"]
    wbands = {re.match(r"U_(.+)_\d+$", k).group(1) for k in po if k.startswith("U_")}
    assert len(wbands) == nwb and sum(1 for k in po if k.startswith("U_")) == nwu
    lat = {}
    for k in po:
        m = re.fullmatch(r"2dc_P_S3_(.+?)(\d)", k)
        if m:
            lat.setdefault(m.group(1), set()).add(m.group(2))
    assert all(u == {"0", "1"} for u in lat.values()), lat
    nlu = sum(len(u) for u in lat.values())
    qb = {b.replace("_", "") for b in bq["bands"]} - {"Normalizationflat"}
    assert "__Normalization_flat" in bq["bands"] and len(bq["bands"]) == bq["s5_copied"]["derived_counts_not_copied"]["bands_in_npz"]
    assert qb == {b.replace("_", "") for b in wbands | set(lat)}, "Q's bands are the weight bands and the laterals"
    assert (nwb, nwu, len(lat), nlu) == (38, 175, 5, 10) and nwu + nlu == 185 and nwb + len(lat) == 43 == len(qb)
    nstat = sum(1 for k in po if re.fullmatch(r"2dc_P_S1_\d{3}", k))
    dc = bq["s5_copied"]["derived_counts_not_copied"]
    assert nstat == dc["stat_replicas_S1"] == 300
    seeds = {re.match(r"2dc_P_S4B_s(\d+)_\d+$", k).group(1) for k in po if k.startswith("2dc_P_S4B_")}
    assert len(seeds) + 1 == dc["seed_triplets_S4B_seeds_plus_seed42"], seeds   # the S4B seeds and seed 42
    periods = {m.group(1) for k in pl["runs"] for m in [re.search(r"/pu_(P[A-Z])_s42/", k)] if m}
    assert pl["checks_passed"] and pl["npz"]["sha256"].startswith("c1723cb5")      # C_PL as Q adopted it
    words = {3: "three", 5: "five"}
    return {"cov2d-nuniv": str(nwu + nlu), "cov2d-nunivbands": str(nwb + len(lat)),
            "cov2d-nstat": str(nstat),
            "cov2d-nseed-word": words[dc["seed_triplets_S4B_seeds_plus_seed42"]],
            "cov2d-nperiod-word": words[len(periods)]}


# T1-1 (the confirming round): FD-PRR's levels (FD-PRR-DECLARATION.md:165-172) in the order "reduced, B0, more"
PRR_LEVELS = {"F1": (["K2"], ["K10", "K20", "K50"]), "F2": (["C25"], ["C400", "C1000"]),
              "F3": (["MCq"], []), "F4": (["O4r", "O4", "O3", "O2"], [])}
PRR_FACTOR = {"F1": "iterations", "F2": "capacity", "F3": "training statistics", "F4": "observables"}


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
    v["ens1-g-drms"], v["ens1-g-floor"] = f"{bw['rms'] - bw['rms_control']:.6f}", f"{bw['delta_rms']:.6f}"
    v["ens1-g-ratio"] = f"{(bw['rms'] - bw['rms_control']) / bw['delta_rms']:.2f}"
    v["ens1-g-dmax"], v["ens1-g-maxfloor"] = f"{bw['max'] - bw['max_control']:.6f}", f"{bw['delta_max']:.6f}"
    assert (v["ens1-g-drms"], v["ens1-g-ratio"], v["ens1-g-dmax"], v["ens1-g-maxfloor"]) == ("0.000512", "1.23", "0.000929", "0.001783")
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
        top = sum(b[:ntop]) / sum(b)
        assert top < 0.01, "the text says under 1 %"
        r1, r2 = sorted(int(k) for k in tr)
        assert (r1, r2) == (73, 139)
        v[f"t2a-beyond1-{t}"] = f"{100 * sum(b[r1:]) / sum(b):.0f}"
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


def period_values(d):
    """T1-3: the per-period benchmark's two readings of the run-period groups against the published result. R5: in the
    73 best-determined directions, removing 1G-1M changes nothing beyond noise (3 sigma resolved, and its share of the
    three-group distance). R5bar: in the other 132, the combination without 1G-1M is farther, by delta per direction (a
    fraction of the three-group value). Both noise models must print the same figures. The licensed "about 15 %" share
    of the resolved change stays typed: it is 14 % or 15 % by noise model (OUTCOME-20261107-per-period-2d-benchmark.md)."""
    r = d["ppbench"]
    assert r["verdict"] == "READ" and r["readings"]["n_replicas"] == 10
    out = []
    for m, x in r["readings"]["by_model"].items():
        a, b = x["R5"], x["R5bar"]
        assert a["class"] == "no change" and b["class"] == "farther without 1G-1M" and b["delta"] < 0
        out.append({"pp-k": str(a["ABC"]["k"]), "pp-kbar": str(b["ABC"]["k"]), "pp-res": f"{a['resolved_3sigma']:.2f}",
                    "pp-dbar": f"{-b['delta']:.2f}",
                    "pp-fbar": f"{-b['fraction']:.2f}"})
    assert all(o == out[0] for o in out), out
    v = dict(out[0])
    v["pp-nrep"] = str(r["readings"]["n_replicas"])
    assert int(v["pp-k"]) + int(v["pp-kbar"]) == r["readings"]["n_cells"]
    return v


def lrows_values(d):
    """#977's L rows from l_rows.json (descriptive). F5.3: weighted fractions of the selected simulated signal (pass_reco,
    w_reco) reconstructed outside the window and with truth outside the grid. F5.4: the four unreported H2 boxes' share
    of the truth weight and of the expected reconstructed signal. 4.2/F4.3: the background template subtracted before
    unfolding over the selected data in the 2D grid, full sample and per playlist (its split into genuine background
    and out-of-phase-space signal is not recorded). 4.3: the same fraction on the largest contributors to the
    published-covariance chi2 (the cells, in decreasing order, until their sum first reaches half of it), and its rank
    correlation with the contribution over the 205 cells. 3.3: the fake-data grades with only GiBUU left out of
    C_model."""
    r = d["lrows"]
    assert r["schema"] == "methods-short-l-rows/1"

    def sci2(x):         # two significant figures, scientific
        m, e = f"{x:.1e}".split("e")
        return rf"{m}\times10^{{{int(e)}}}"
    f, b, t, q, h = r["f53"], r["bkg_42"], r["bkg_43"], r["r33"], r["f54"]
    v = {"f53-win": sci2(f["weighted_outside_reco_window"]), "f53-grid": sci2(f["weighted_gen_outside_grid"])}
    assert (v["f53-win"], v["f53-grid"]) == (r"2.0\times10^{-5}", r"1.1\times10^{-4}")
    assert h["boxes"] == [2, 6, 10, 14]
    v["f54-truth"], v["f54-reco"] = sci2(h["share_truth_weight"]), sci2(h["share_expected_reco_signal"])
    v["bkg42-frac"] = f"{100 * b['fraction_full_sample']:.2f}"
    pl = b["per_playlist"].values()
    v["bkg42-pl-lo"], v["bkg42-pl-hi"] = f"{100 * min(pl):.2f}", f"{100 * max(pl):.2f}"
    assert b["compare_E_U"]["data_equal"] and abs(b["compare_E_U"]["background_rel_diff"]) < 0.005
    assert f"{100 * b['compare_E_U']['E_U_fraction']:.2f}" == v["bkg42-frac"] == "2.91"
    assert t["chi2"] == 465.41527219152636 and t["rule"].startswith("largest contributors")
    v["bkg43-n"], v["bkg43-share"] = str(t["n_cells_T"]), f"{100 * t['chi2_share_T']:.0f}"
    v["bkg43-frac"], v["bkg43-rho"] = f"{100 * t['fraction_T']:.2f}", f"{t['spearman_fraction_vs_contribution_205']:.2f}"
    assert t["fraction_T"] > b["fraction_full_sample"] and abs(t["spearman_fraction_vs_contribution_205"]) < 0.2
    assert q["records_count_moved"] == {"q3": [0, 1]} and q["chi2_rise_max_record"] == "q3"
    assert q["q3_cells_abs_z_gt_2_added"] == ["R15"]   # the text: the same one cell as without C_model (t2b-n2-cell)
    v["r33-dchi2-max"] = f"{q['chi2_rise_max']:.1f}"
    v["r33-z-from"], v["r33-z-to"] = (f"{z:.2f}" for z in q["q3_max_abs_z"])
    assert sorted(q["unchanged_own_gibuu"]) == ["A7_gibuu", "stage0c_gibuu"]
    # Fm7: fig:deformation shades the (E_avail, W) cells failing the support rule; the caption names them by edges
    # (EW11: E_avail 0.1-0.2 GeV, W >= 3 GeV; EW36, EW37: E_avail >= 3 GeV, W < 1.4 GeV) and gives their truth weights
    m = r["m5"]
    assert m["unsupported_EW"] == ["EW11", "EW36", "EW37"] and all(x < 1000 for x in m["unsupported_truth_weight"])
    v["fm7-tw-lo"], v["fm7-tw-hi"] = f"{min(m['unsupported_truth_weight']):.0f}", f"{max(m['unsupported_truth_weight']):.0f}"
    assert m["controls_pass"] == [True, True] and set(m["support_cells_empty_in_every_seed"].values()) == {0}
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
    # group B5 (#1025; the director's ruling (b)): the same falls over Table S7's rows after B5, GENIE CV, GENIE + MEC and
    # Tune v1 (Table IV's chi2, both arms) and NuWro and GiBUU on carbon only (defs.json, reported and without_C_PL5D)
    for part in ("total", "shape_only"):
        fall5 = [1 - gw[n][part]["chi2"] / go[n][part]["chi2"] for n in ("genie_cv", "genie_mec", "mnvtune_v1")]
        fall5 += [1 - float(v[f"g-{k}-carbon-{part}-chi2"]) / float(v[f"g-{k}-carbon-{part}-chi2-nopl"]) for k in ("nuwro", "gibuu")]
        assert min(fall5) > 0, f"a {part} chi2 rises with the block"
        v[f"pl-chi2fall-b5-{part}-lo"], v[f"pl-chi2fall-b5-{part}-hi"] = f"{100 * min(fall5):.1f}", f"{100 * max(fall5):.1f}"
    for k in sorted(k for k in v if PAPER_PREC.match(k)):
        for nk, x in paper_prec(k, v[k]).items():
            assert v.get(nk, x) == x, f"{nk}: {v[nk]!r} against the paper form {x!r}"
            v[nk] = x
    return v


def render(v):
    lines = ["% Generated by make_values_fived16.py from the committed readouts it pins by sha256. Do not edit.",
             "% Regenerate: python3 docs/analysis-note/make_values_fived16.py",
             "% \\fvval{key} prints a value and stops the build on an unknown key. \\fvpending{what} marks an input that has",
             "% not landed; it prints [PENDING: what], which build_all.sh refuses (the PDF text check), so it never ships.",
             r"\makeatletter",
             r"\providecommand{\fvval}[1]{\@ifundefined{fv@#1}{\errmessage{values_fived16: no value '#1'}}{\@nameuse{fv@#1}}}",
             r"\providecommand{\fvpending}[1]{\textbf{[PENDING: #1]}}",
             "% \\fvgroup{group}{text} prints text once the group's record has landed, else one [PENDING: ...]; inside it,",
             "% \\fvcase{key}{class}{text} prints text only when key has that class (methods-short-20261109/variants.md).",
             "% \\fvgroupalt{group}{pending text}{filled text} prints the first while the group is pending, with no marker.",
             "% \\fvlist{...\\fvitem{a}...\\fvitem{b}...} prints the items that print, separated by '; ' (a list of \\fvcase items).",
             r"\newif\iffv@listfirst",
             r"\providecommand{\fvlist}[1]{\fv@listfirsttrue#1}",
             r"\providecommand{\fvitem}[1]{\iffv@listfirst\fv@listfirstfalse\else; \fi#1}",
             r"\def\fv@PENDING{PENDING}",
             r"\providecommand{\fvgroup}[2]{\@ifundefined{fvg@#1}{\errmessage{values_fived16: no group '#1'}}{\expandafter\ifx\csname fvg@#1\endcsname\fv@PENDING\fvpending{\@nameuse{fvgd@#1}}\else#2\fi}}",
             r"\providecommand{\fvgroupalt}[3]{\@ifundefined{fvg@#1}{\errmessage{values_fived16: no group '#1'}}{\expandafter\ifx\csname fvg@#1\endcsname\fv@PENDING#2\else#3\fi}}",
             r"\providecommand{\fvcase}[3]{\@ifundefined{fvc@#1}{\errmessage{values_fived16: no verdict key '#1'}}{\def\fv@tmp{#2}\expandafter\ifx\csname fvc@#1\endcsname\fv@tmp#3\fi}}"]
    for k in sorted(v):
        lines.append(rf"\@namedef{{fv@{k}}}{{{v[k]}}}")
    lines.extend(pending_lines())
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
            ("drops the truth listed only without the block", "sec_fived16.tex",
             "The fake-data bias therefore exceeds the stated thresholds",
             lambda t: t.replace(r"and also at the GiBUU $\Eavail$ shape without $C_{\mathrm{PL,5D}}$; the bias", "; the bias", 1)),
            ("drops a GiBUU truth of its family", "sec_fived16.tex", "so the GiBUU comparison carries that limitation",
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
    bad = check_prr_verdicts(d) + check_vhalf_verdicts(d)
    if bad:
        sys.exit("VALUES-FIVED16 :: FAIL (VERDICTS differ from a pinned readout (FD-PRR or V-HALF))\n  "
                 + "\n  ".join(bad))
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
