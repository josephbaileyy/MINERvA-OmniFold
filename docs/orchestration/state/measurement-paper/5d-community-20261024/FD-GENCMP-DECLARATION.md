# DECLARATION GENCMP: three generator-comparison limitations of the sixteen-cell paper (Q08, Q10, Q26) (2026-11-01)

**By** the limitation-resolver lane (Claude), for the director to bind.

**Under:**
- [`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`](../../../DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md)
  item 2: compute needed to resolve a limitation is approved, "still declared, priced and bound before it runs", with the
  director's reading (CPU only, jobs under 12 h, regular QOS, nothing written to CFS; a campaign above half the group's
  remaining balance goes back to Joseph);
- the director's brief to this lane of 2026-11-01 (by message), which assigns Q08, Q10 and Q26 and fixes the process
  below: declaration, binding, run, report; any Table IV number, claim or abstract change goes to Joseph first; the paper
  rewrite lane makes the manuscript edits.

**After:**
- the qualifications inventory and both referee reports in
  [`../../2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/`](../../2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/REPORT.md):
  inventory rows Q08, Q10 and Q26 and its §4; Sonnet M8; Gemini item 7 ("Uncorrected Target Differences");
- [`FD-G-DECLARATION.md`](FD-G-DECLARATION.md) and [`FD-G-REPORT.md`](FD-G-REPORT.md), which produced Table IV, and
  the with-block readout `fd/with-cpl/readout/fd_g_readout.json` (`b55366b3…`) that `make_values_fived16.py` reads;
- the phase-1 target and convention studies on the 109 joint-test cells: MP3-A, MP3-B, MP3-C and MP-5
  (`../phase1/mp3a/`, `../phase1/mp3b/REPORT.md`, `../phase1/mp3c/REPORT.md`, `../phase1/mp5/REPORT.md`).

**Director's rulings of 2026-11-01 on this declaration (by message), applied here:**
1. the code and its tests land on this branch before the binding, which pins them by blob digest; an independent
   read-only review of the declaration and the code (a fresh Sonnet subagent, not sol) is recorded verbatim beside this
   file, `FD-GENCMP-REVIEW-PROMPT.txt` and `FD-GENCMP-REVIEW-ANSWER.txt`;
2. Q26's 3D side uses σ₁₆ only, with PROJ3D as a labelled descriptive row, and its outcome reads only "agree / differ at
   the σ₁₆ scale, descriptive" (§4, §7);
3. the inventory's 0.47% is the coarse joint grid's off-support share (`paper_body.tex:44`), not the unreported boxes;
   step C prints the four boxes' own share;
4. step D is bound, with the 0.25 node-h probe first and the 4.0 node-h cap; which route the paper uses if the two
   disagree is fixed in §5 now.

**Declares:**
- step 0, input verification;
- step A (Q08), the CH correction of NuWro and GiBUU on the sixteen cells;
- step B (Q10), the predictions rebuilt from their event records in the analysis definitions of W and pT;
- step C (Q26), the sixteen-cell result against the 2D and 3D results where they overlap;
- step D (Q08, second route), native CH generation for NuWro, bound by ruling 4 with a probe first;
- the inputs (`fd/gencmp/INPUTS.sha256`), controls, readouts, price, stop rules, and what the paper would say in every
  outcome.

**MEASURES:** nothing. No step has run and no comparison quantity has been formed. The reads made for this declaration
were directory listings, `stat`, the build receipts' JSON, and one O_NOATIME sha256 of the 3D central file, which equals
its committed digest; every pscratch read left the file's atime unchanged.
<!-- absence-ok: a scoping statement about this lane's own work, listed exhaustively in the sentence -->

**CANNOT AUTHORIZE:**
- running anything, which needs the director's binding;
- any change to a Table IV number, a claim, the abstract or printed wording. These go to Joseph with the report, and the
  paper rewrite lane makes the edits;
- any change to the reported covariance, the cells, or the decisions of the joint test (Table VI of the note).

**CITABLE FOR:** what GENCMP will compute, from which inputs, at what cost, under which stop rules, and the paper wording
fixed in advance for each outcome.

**NOT CITABLE FOR:** any result; any statement that a generator is or is not excluded; any validation of the reported
covariance, of C_model, or of the 2D covariance Q.

## 0. Summary

| step | limitation | what it computes | where | price (CPU node-h) |
|---|---|---|---|---|
| 0 | all | every input against `fd/gencmp/INPUTS.sha256`, opened with O_NOATIME, atime checked | login node | 0 (login node) |
| A | Q08 | NuWro and GiBUU corrected to CH, x_CH = (12/13) x_C + (1/13) x_H, from the committed fine-grid products, on Table IV's cells and covariances | local (committed inputs) | 0 |
| B | Q10 | all four external predictions, both targets, rebuilt from their event records with the analysis W and the beam-axis pT | one regular CPU node | ≤ 2.0 (cap) |
| C | Q26 | the sixteen cells summed over each (pT, p∥) quadrant, against the 2D result and the 3D result there | login node | 0 (login node) |
| D | Q08 | NuWro generated natively on CH (its `CH.txt` mixture), then step B's chain | regular CPU nodes | ≤ 4.0 (cap), after a 0.25 probe |

**Campaign cap:** 6.0 node-h: 2.0 for steps 0–C and 4.0 for D. The last recorded group balance is 2,074.5 node-h
(`FD-1B-STAGE2-REPORT.md:47`, as quoted in the inventory §1), so half of it is about 1,037. No step comes near it.

**The question for each limitation, and what this does not try to answer:**
- **Q08.** How much of each NuWro and GiBUU χ² in Table IV comes from comparing a carbon prediction with CH data? Not
  whether the hydrogen components are right: GiBUU's hydrogen carries its failed sampling-closure check and its
  energy-non-conserving DIS (`docs/analysis-note/sec_joint.tex:327`, from MP3-C and binding addendum 9), and step A
  carries that label in every output.
- **Q10.** How much do the predictions change when W uses the struck-nucleon mass and the massless-muon Q² with the
  muon angle from the fixed beam axis, and pT is measured from that axis? Not whether the analysis definitions are the
  right ones; those are the paper's (note Table `tab:observables-impl`).
- **Q26.** Does the sixteen-cell result agree with the lower-dimensional results where both are defined? Not which one
  is right if they differ.

## 1. Step 0: the inputs

**The file** `fd/gencmp/INPUTS.sha256` (in this PR) lists 253 inputs in eight families, each line `sha256  path`:

| family | what | lines | where the digest comes from |
|---|---|---:|---|
| A | the five frozen 5D predictions of Table IV and `phi_t.npz` | 6 | committed manifests (`SHA256SUMS-s5p-archive-20261006.txt` and the FD-G pins) |
| B | the generator event records and their flux files: two GENIE gst files, two GENIE 50–100 GeV supplements, NuWro `nuwro_flat5d_p1..p8.root` and its supplement, 80 GiBUU `FinalEvents.dat`, GiBUU's cvmfs flux file | 101 | the build receipts `gen5d/gen5d-build.json` and `gen5d_fluxfix/gen5d-fluxfix*.json`, read with O_NOATIME |
| C | the analysis-MC neutrino-direction pools `pool_b0..b5.npy` (MP-5 §2) | 6 | the MP-5 receipt `mp5_genie.json`, read with O_NOATIME |
| D | the hydrogen event records: 30 MP3-B NuWro chunk files (k1) and 80 MP3-C GiBUU tasks | 110 | the committed `phase1/mp3b/runA/gen/output_sha256.txt` and `phase1/mp3c/prod/output_sha256.txt` |
| E | S1's assembly, C_resp, the run-period block, and P5 (the fine-grid result whose cell integrals are f) | 4 | committed records (FD-G-REPORT, `cmodel_5d.json` `inputs.p5_sha256`) |
| F | the 2D central value, Q and `playlist_term.npz` (Q's 205-cell index, `cells`); the 3D central value and the trunk-projected 3D covariance | 5 | `DECISION-20261011-joseph-2d-central-lightgbm-seed42.md`, `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md` §1, `RESULT-20260923-issue26-issue5.md:23`, `OUTCOME-20260922-3d-covariance-projected-from-the-adopted-trunk.md` |
| H | the frozen code tree the rebuild imports (`s5p-20260926/gen5d/code/tree`, its 12 `.py` files), copied through O_NOATIME before import (§9) | 12 | O_NOATIME sha256 on 2026-11-01 |
| G | the committed fine-grid target products (MP3-A GENIE, MP3-B NuWro, MP3-C GiBUU frozen and alt), the data product, both G readouts, the cell definition and `cmodel_5d.json` | 9 | `shasum -a 256` of the committed files |

**The rule.** Each step opens every input it reads, computes its sha256, and stops if any digest differs. An input no
step reads is not opened. Pscratch files are opened with `os.open(path, O_RDONLY | O_NOATIME)`, and `stat` before and after must show
the same atime; a moved atime is reported as a deviation. ROOT files are read into memory through that descriptor and
opened as `TMemFile`, so the frozen ROOT code paths run unchanged. Nothing is copied to a new location except the
outputs.

**Purge.** Every pscratch input was present on 2026-11-01 (listing above). The run must start before 2026-11-09, when
the per-playlist event loops become exposed
([`DECISION-20261101-joseph-abstracts-approved-and-event-loop-retention.md`](../../../DECISION-20261101-joseph-abstracts-approved-and-event-loop-retention.md),
inventory §7). GENCMP does
**not** need the per-playlist event-loop files.

## 2. Step A (Q08): NuWro and GiBUU corrected to CH, in the generators' own definitions

**Construction.** Per fine cell f of the 65,856-cell 5D grid:
- x_CH = (12/13) x_C + (1/13) x_H and sumw2_CH = (12/13)² sumw2_C + (1/13)² sumw2_H, as in MP3-B and MP3-C
  (`../phase1/mp3b/REPORT.md` §1; `sec_joint.tex:309`).
- NuWro: `mp3b_fine_nuwro.npz` keys `xsec_CH`, `sumw2_CH` (k1, the primary card).
- GiBUU: `mp3c_fine_gibuu_frozen.npz` keys `xsec_CH`, `sumw2_CH` (the frozen weight; MP3-C's primary).

**The data side** comes from the committed with-block product: f, C_resp and C_PL,5D from `fd/with-cpl/block/cpl_block.npz`
(`d9aa32fd…`), and C_e and C_model_abs from `fd/with-cpl/data-product/fd_data_product_cpl.json`, so C_total = C_e +
C_model_abs. Control R: f equals `cmodel_5d.json`'s x to 1e-12, and C_total + C_resp + C_PL,5D equals the block's
stored sum to 1e-12 of the largest variance.

**The comparison** is FD-G's, unchanged: cell integrals X = Σ_f x_f vol_f with S1's functional matrix U
(`s1_assemble.fine_map` on the H2 definition, map `930326a3…`), the total and shape-only χ² against
C_total + C_resp + C_PL,5D + V_g and against C_total + C_resp + V_g, with V_g = U² sumw2 (each fine cell's volume squared) as FD-G defines it.
NuWro on R00–R15 (ndf 16, shape-only 15); GiBUU on R00–R03 and R08–R11 (ndf 8, shape-only 7), with no GiBUU value
above p∥ = 4.5 GeV/c formed, exactly as FD-G §2.

**Controls.**
- **A0.** From the same npz files, the keys `xsec_C12_frozen` and `sumw2_C12_frozen` must give, through this step's
  code, NuWro's and GiBUU's committed χ² in both readouts (`fd/with-cpl/readout/fd_g_readout.json` and
  `fd/readout/fd_g_readout.json`; total and shape-only, both covariances) to a relative 1e-9. If A0 fails, step A stops
  and reports; it does not search for the difference.
- **A1.** `xsec_C12_frozen` and `sumw2_C12_frozen` equal the frozen products `nuwro_cv_xsec5d_full.npz` (`475a2871…`)
  and `gibuu_cv_xsec5d_fluxfix.npz` (`48917692…`) bitwise on all 65,856 cells. `fd_gencmp.py a1` reads them on a login
  node with O_NOATIME and writes a readout; `fd_gencmp.py ch` refuses unless that readout passed on the same npz digests.
- **A (CH).** (12/13) `xsec_C12_frozen` + (1/13) `xsec_H`, in `mp3b_build.py`'s floating-point order, equals the
  committed `xsec_CH` bitwise, and likewise for sumw2.
- **A2.** Every CH cell integral is positive on the cells compared.

**Readouts, per generator:** total and shape-only χ², ndf and p, in both covariances, for carbon (A0's) and CH; Δχ²;
the per-cell ratio r_c = X_CH/X_C and the pull (g − f)/σ in each cell, carbon and CH.

**One sensitivity, declared now and printed beside the primary, never in its place:**
- **A-H.** The hydrogen component swapped for GENIE CV's (13 × MP3-A's `xsec_H1`, the "mixed" construction of MP3-B
  variant (C)), for both NuWro and GiBUU. The spread between own-hydrogen and GENIE-hydrogen χ² is reported as the
  correction's model sensitivity. It answers Gemini's "appropriate systematic uncertainty" only descriptively: it adds
  no block to any covariance. GENIE's hydrogen sample is thin: MP3-B's B4 was not met for it, with 21 cells above 1/3
  and a worst case of 1.41 (`../phase1/mp3b/REPORT.md` §6). So this spread is largely that sample's own noise, and its
  label says so. GiBUU's alt weight (`mp3c_fine_gibuu_alt.npz`) is a second printed row, for GiBUU only. Neither row is
  ever promoted to the primary.

**Labels carried in every output.** NuWro CH: "NuWro 21.09 C12 + NuWro free-proton, 12:1 per nucleon; four hydrogen
chunks rerun on alternate seeds, supplement FLAGGED (MP3-B §2)". GiBUU CH: MP3-C's required label verbatim, "B3
(sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at ≤ 0.1 σ_c", plus "46% of the
hydrogen sample is DIS that does not conserve energy (binding addendum 9 §4)".

## 3. Step B (Q10): the predictions in the analysis definitions, from the event records

**The analysis definitions** (note `sec_eavailw.tex`, Table `tab:observables-impl`; MAT `GetThetalepTrue`,
`CVUniverse::GetTrueExperimentersW`, `MINERvA101/.../CVUniverse.h:392-410`):
- θ_μ is measured from the fixed beam axis, RotateX(−0.05887) of the detector axis; pT = p_μ sin θ_μ, p∥ = p_μ cos θ_μ;
- W = √(M² + 2M(E_ν − E_μ) − Q²), Q² = 4 E_ν E_μ sin²(θ_μ/2), with M the struck nucleon's mass: M_n for 2112, M_p for
  2212, and otherwise M_nucleon = (1.5 M_n + M_p)/2.5 (`3d-unfolding/genie/gen_to_xsec5d.py:85-86`, :123-130);
- events with W² < 0 are excluded from the truth sample (no cell), where the generators' converters place them at W = 0;
- q3 (exact Q²) and E_avail do not depend on the axis or on M and are unchanged.

**The beam axis for a generator event.** Every generator sample has its neutrino along +z (MP-5 G1 for GENIE; the
NuWro and GiBUU converters assume it). The analysis truth instead measures θ_μ from a fixed axis about 1 mrad from the
true neutrino (MP-5 §1: median 1.03 mrad, maximum 6.9). Step B uses MP-5's declared method (`../phase1/mp5/PREP.md` §1–§2):
each event's lepton is rotated by a neutrino direction n drawn from the analysis MC's pool in the event's E_ν bin
([0,3), [3,5), [5,8), [8,15), [15,30), [30,∞) GeV), w_truth-weighted, by the Rodrigues rotation that maps ẑ onto n.
- **NuWro** stores pT and p∥, not the lepton azimuth (`nuwro_to_flat_5d.C:30-41`). Its lepton azimuth about the
  neutrino is uniform, so step B draws it uniformly with a declared seed and rebuilds the 3-vector before the rotation.
  The same argument is MP-5's for the twist about n (PREP §2).
- **GiBUU** carbon records no struck nucleon, so M is M_nucleon, the analysis code's own branch for an unidentified
  nucleon. A variant uses M_n (the present convention) to bound that choice. It is printed only, in carbon and in CH
  (combined with hydrogen's first-seed product), and is never the primary. GiBUU hydrogen uses M_p.
- **GENIE and NuWro** use the recorded `hitnuc`. For GENIE 2p2h, whose `hitnuc` is a cluster code, M is M_nucleon by
  the same rule.

**Draws.** Five seeds, 202611011 to 202611015, each drawing one n per event (and, for NuWro, one azimuth). The primary
prediction is the mean over the five fine-grid products, with sumw2 the mean of the five seeds' sumw2 (the
events and weights are the same in every seed; only their bins move), and the five-seed spread recorded per cell. **If the five-seed spread of any cell integral exceeds 0.2 of that cell's reported σ, this is
reported, and the mean is still the primary.**

**Samples rebuilt:** GENIE CV and GENIE + MEC (main and 50–100 GeV supplement), NuWro C12 (p1–p8 and supplement), NuWro
hydrogen (MP3-B k1 chunks), GiBUU C12 (80 tasks), GiBUU hydrogen (80 MP3-C tasks). The normalisation, flux-fix weights
and supplement combination are the frozen converters' (`gen_to_xsec5d.py`, `gen5d_flux_reweight.py`,
`gen5d_flux_supplement.py`, `mp3b_build.py`, `mp3c_build.py`), imported, not restated. MnvTune v1 is already in the
analysis definitions (MP-5 T3, bitwise) and is not rebuilt.

**Controls (each failure stops that sample only, and is reported):**
- **B0.** With n = ẑ, no azimuth draw where the converter used none, and the generators' own W, the rebuild reproduces
  the frozen product bitwise: the four Table IV files of family A, NuWro's and GiBUU's `xsec_H` in family G, and the
  CH combinations of step A. This is MP-5's G1, extended to every sample. A sample that fails B0 is not rebuilt, and the
  paper keeps the present sentence for that generator.
- **B1 (printed, not gated).** The pools' α summary (median and 68% interval of the ν-to-beam angle) is printed beside
  MP-5's REPORT figures (median 1.03 mrad, [0.50, 1.92]). MP-5's pool-level summary file is not committed, and the
  REPORT's figures are for a different population, so no tolerance can be declared honestly. The pools' identity is
  gated instead, by their pins (family C).
- **B2.** The fraction of events with W² < 0 under the analysis W, per sample, is printed. For GENIE CV and NuWro it
  must lie within a factor 2 of M4-W's measurement (`probe_gen.json`: 29 of 938,141 GENIE CV events). In addition,
  the in-phase-space count of the `wonly` main sample (n = ẑ) must equal M4-W's population exactly (938,141 for
  GENIE CV; NuWro's from the same record). Either failure STOPs that sample, which then writes no analysis product,
  and its status in `rebuild.json` reads "B2 stop", which the readers `defs` and `native` honour.

**Readouts.** For each of the four generators, in carbon and in CH where it applies (NuWro, GiBUU):
- the per-cell change, (X_ana − X_gen)/σ_c with σ_c the reported σ, and in per cent;
- the total and shape-only χ² in both covariances, before and after;
- the five-seed spread;
- the W-only and axis-only parts, by rebuilding once with each change alone (seed 202611011), so the two effects are
  not mixed (MP-5 §5 item 2).

**The 2 × 2 table.** For NuWro and GiBUU: {carbon, CH} × {generator definitions, analysis definitions}. For GENIE CV and
GENIE + MEC (CH already): {generator, analysis} definitions. The corner "CH, analysis definitions" is the candidate for
Table IV, which only Joseph can adopt.

## 4. Step C (Q26): the sixteen-cell result against the 2D and 3D results

**Where they overlap.** A region can be compared only if it is a union of sixteen-cell boxes and a region of the
lower-dimensional result. Every reported cell has pT and p∥ edges on {0, 0.7, 4.5} × {1.5, 4.5, 60}, and splits in
E_avail, q3 and W inside those. So the overlaps are the four (pT, p∥) quadrants:

| quadrant | pT (GeV/c) | p∥ (GeV/c) | reported cells | H2 boxes not reported |
|---|---|---|---|---|
| QA | 0–0.7 | 1.5–4.5 | R00–R03 | 2 and 6 |
| QB | 0–0.7 | 4.5–60 | R04–R07 | 10 and 14 |
| QC | 0.7–4.5 | 1.5–4.5 | R08–R11 | none |
| QD | 0.7–4.5 | 4.5–60 | R12–R15 | none |

(From `h2_definition.json`: `unreported_boxes` [[2],[6],[10],[14]] and `h2_to_reporting_cell`.) Step C's code
enumerates every (pT, p∥, E_avail) box on the H2 edges that spans all q3 and W, has an E_avail edge inside the axis,
and is a union of reported cells (unreported boxes allowed). If any exists, step C stops, and the region needs an
amendment before it is compared. On the committed definition the test suite finds none (`test_enumeration_on_the_definition`), and finds
some on a synthetic definition where every box is its own cell, so the enumeration can find one. Unions of quadrants
are not separate regions. The 4D result is not part of this declaration.

**The sixteen-cell side.** S_q = Σ_{c∈q} f_c, with σ² = aᵀ C a for the reported matrix C_total + C_resp + C_PL,5D, and
for the matrix without C_PL,5D.
- **QC and QD** are complete.
- **QA and QB** lack two unreported boxes each. Their content is taken from P5 (`k1_p5_rerun.npz`, `e36f3b25…`, the
  fine-grid result whose cell integrals are f; control C0 below) over those boxes, with a 100% uncorrelated uncertainty
  added in quadrature. The readout prints each unreported box's share of its quadrant in P5 and in MnvTune v1's truth.
  QA and QB are labelled "includes unreported boxes at their central value, ±100%".

**The 2D side.** The seed-42 matched CV (`4f5a1b6d…`, `hXSec2D`) integrated over each quadrant with its bin areas, and
σ² = aᵀ Q a from Q (`s5_plus_playlist.npz`, `8ccb4d72…`, key `total_plus_C_PL`) over the same bins. Q's 205 cells are
the flat C-order (pT, p∥) indices in `playlist_term.npz` key `cells` (`c1723cb5…`), the index `combine_s5.py` checked
Q against. Two structural checks: Q's `area` equals the 2D bin areas on those cells to 1e-12, and the median of
√diag(Q)/x lies in [0.01, 0.5], so Q is in the units of x. The largest |CV/`cells_x_EU` − 1| (Q's own central value,
the E_U estimator) is printed as a diagnostic.

**The 3D side.** The 3D central value (`xsec_3d_MEFHC_5iter_lgbm.root`, `0dd94830…`) integrated over each quadrant
and over all E_avail. No 3D covariance is adopted. The trunk projection `20c16e16…` exists but is not adopted, and its
destination population is not paired with the 3D central value (`OUTCOME-20260922-…` §4–§5). So:
- the primary 3D readout is d and d/S with the sixteen-cell σ alone;
- one descriptive row aggregates `20c16e16…` over each quadrant, labelled "unadopted trunk projection, receiving-cells
  population, not paired with the 3D central value".

**Controls.**
- **C0.** P5's integrals over the sixteen cells equal f to a relative 1e-12 (FD-G's G2 test, repeated).
- **C1.** The quadrant edges (0.7, 4.5 in pT; 1.5, 4.5, 60 in p∥) are bin edges of the 2D and 3D grids.
- **C2.** Each quadrant's 2D bins are all among Q's 205 cells. A quadrant that fails C2 gets the 2D central value only,
  labelled "Q does not cover this quadrant", and no z.
- **C3.** The 2D central value summed over the four quadrants reproduces its recorded integral, 3.0730e-38 cm²/nucleon
  over 205 bins (`VALIDATION_LEDGER.md` VL173), to those five figures. The 3D central value's integral reproduces the
  3D status headline, 3.079e-38 (`3d-unfolding/3D_OMNIFOLD_STATUS.md`, "Total σ (3D integral)"), to four figures. If
  either fails, step C stops and reports.
- **Structural checks.** Each quadrant's cells and unreported boxes are those of the table above. PROJ3D's row index is
  unique and inside the 14 × 16 × 7 grid. A quadrant that Q does not cover forms no 2D comparison at all.
- The 5D fine grid has these edges (pT edges include 0.7 and 4.5; p∥ edges include 1.5, 4.5 and 60), and C1 checks
  the 2D and 3D files themselves.

**The readout and its rule.** For each quadrant q and each comparison (2D, 3D): d_q = S_q(16) − S_q(lower), and d_q/S_q
in per cent. The two results share the data events, flux and most systematics, so their correlation ρ is unknown and
almost surely positive. Over ρ ∈ [0, 1], the variance of d_q lies between (σ₁₆ − σ_low)² and σ₁₆² + σ_low². The
outcome is fixed now, read from the reported sixteen-cell matrix C_total + C_resp + C_PL,5D, which is primary. The
matrix without C_PL,5D is printed only: against Q, which includes the 2D run-period block, it is not a like-for-like
pair, and no outcome is read from it.
- **Agree:** |d_q| ≤ 2|σ₁₆ − σ_low|, which holds for every ρ in [0, 1].
- **Agree below a correlation:** 2|σ₁₆ − σ_low| < |d_q| ≤ 2√(σ₁₆² + σ_low²). The readout prints ρ*, the correlation at
  which |d_q| = 2σ_d.
- **Differ:** |d_q| > 2√(σ₁₆² + σ_low²), which is beyond 2σ for every non-negative correlation. This is a new problem.
  It is reported, and it goes to the director and Joseph before any paper text. Its investigation is not part of this
  declaration.

For the 3D comparison no adopted covariance exists, so the outcome is only "agree at the σ₁₆ scale (descriptive)" if
|d_q| ≤ 2σ₁₆, or "differ at the σ₁₆ scale (descriptive)" otherwise. Neither reads as a validation, and neither is a new
problem by itself. The PROJ3D row has no outcome.

## 5. Step D (Q08, second route): native CH generation for NuWro (ruling 4)

**Why it is separate.** For an incoherent target, the CH cross section per nucleon is (12 σ_C + σ_H)/13, so step A's
combination and a native CH generation predict the same quantity. A native run checks the combination's code and
normalisation from an independent sample, and it is literally what both referees asked for ("generate CH samples",
Sonnet M8; "Re-run NuWro and GiBUU on CH target mixtures", Gemini 7).

**Which generators support it.**
- **NuWro 21.09:** yes. Its install ships `data/target/CH.txt` (`target_type=1`, `target_content = 6 6 1x` and
  `+= 1 0 1x`), in `/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie/nuwro_home/data/target/`.
- **GiBUU 2019:** the production jobcard's `&target` namelist sets a single `target_Z`, `target_A` (6, 12). I found no
  mixture option in that jobcard. I did not search GiBUU's source, so this is not a claim that none exists. GiBUU's CH
  is step A's combination only.
  <!-- absence-ok: scoped to the jobcard read, as the sentence states -->

**What it would run.** The MP3-B card set with only the target keys changed to `CH.txt`'s, at the production C12
sample's size (1,352,546 events in grid in the frozen product), in chunks of the MP3-B form, then the 50–100 GeV
supplement, then step B's chain (generator definitions and analysis definitions).

**Price.** MP3-B generated and built 275,000 hydrogen events for 0.156 node-h on debug, including two failed attempts
(`../phase1/mp3b/REPORT.md` §7). Carbon events cost more per event (the cascade). **Cap 4.0 node-h**, on regular QOS,
with one 0.25 node-h probe first that measures the per-event cost; if the probe projects above the cap, step D stops
and returns with the measured projection.

**Its control and rule.** Per cell, the native CH integral against step A's CH integral, with z_c = Δ_c / √(var_A +
var_D) from their sumw2. **Agree:** Σ z_c² over the sixteen cells below the 0.99 quantile of χ²₁₆ (32.0), and no
|z_c| > 3.5. The same comparison is made in the analysis definitions, against step B's CH combination.

**Which route the paper uses, fixed now (director's ruling 4).** Step A's combination, in every outcome.
- **If they agree,** the paper adds the clause in §7.
- **If they disagree,** the report gives both χ² and the per-cell z. The paper's CH numbers stay step A's, and the
  disagreement goes to the director and Joseph, who may change that before any text.
- **The reason for choosing A.** Each component of step A passed its own gates as a separate product (MP3-B B1–B4),
  and the same products are already the note's CH re-evaluation (`sec_joint.tex`). A native mixture adds one
  normalisation this lane has not yet checked: how NuWro weights a multi-isotope target. So a disagreement points
  first at that step.
- **No frozen product exists for the native sample.** Step B's B0 therefore has no target for it. Its rebuild is
  checked only through this rule.

## 6. Price, QOS and storage

| step | host | QOS | wall limit | cap (node-h) |
|---|---|---|---|---|
| 0, C | login node | none | — | 0 |
| A | local, from committed files (plus A1's O_NOATIME reads on a login node) | none | — | 0 |
| B | 1 node | regular | 3 h | 2.0 |
| D (bound) | ≤ 2 nodes | regular | 3 h | 4.0, after a 0.25 probe (enforced by the job scripts, below) |

- **The B projection.** MP-5's GENIE CV rotation rebuild ran in 451 s on 32 cores (0.0157 node-h on shared,
  `../phase1/mp5/REPORT.md` §6). Step B rebuilds about ten samples, each six times (n = ẑ for B0, then five draws), plus
  two single-change rebuilds. GiBUU's ASCII parsing dominates (MP3-C's build and evaluation took 0.095 node-h). On one
  regular node this projects to under 1 node-h of wall clock. The cap is 2.0.
- **Charge** is read from `sacct` (`ElapsedRaw × billing / 256` per job, with `billing` from `AllocTRES`). It is
  reported against these caps.
- **Writes** go only under `/pscratch/sd/j/josephrb/gencmp-20261101/`. Nothing is written to CFS. Q is read from CFS.
- **CPU only;** no GPU; every job is under 12 h.
- **Step D's probe and cap are enforced by its job scripts, not by the Python code.** The probe job asks for one node
  for at most 15 minutes (0.25 node-h). Its per-event cost is read from `sacct` and its projection written to the
  receipts before the production job is submitted. The production job's `--nodes` × `--time` is set so that the probe's
  charge plus the production job's cannot exceed 4.0 node-h. If the projection is above that, step D stops and returns
  with it.

## 7. What the paper would say, in every outcome

The paper rewrite lane makes no edit from these until Joseph rules on the report. The wording below is the lane's
proposal, fixed before the numbers so that no outcome is chosen because it looks better.

| limitation | outcome | proposed paper change (`paper_body.tex` loci) |
|---|---|---|
| Q08 | A0 and A1 pass, whatever the sign of Δχ² | :42 and :232: "NuWro and GiBUU are on carbon, with no correction to CH" becomes "NuWro and GiBUU, generated on carbon, are corrected to CH by adding each generator's free-proton prediction with weight 1/13 per nucleon". Table IV shows the CH rows. The carbon rows and the GENIE-hydrogen sensitivity go to the note. The GiBUU row carries its hydrogen label (§2) in a table note. If a χ² rises, the text says so, with the size |
| Q08 | A0 or A1 fails | The present sentences stay. Minimum note text, fixed now: "The correction of NuWro and GiBUU to CH did not reproduce its inputs (control A0 or A1), so the comparison remains on carbon." |
| Q08 | step D agrees (the primary, generator-definitions route) | One clause: "a native CH generation of NuWro agrees with the combination". If the analysis-definitions route disagrees, the clause adds "in the generators' definitions; in the analysis definitions they differ (Σz² = …, largest \|z\| = …)" |
| Q08 | step D disagrees (primary route) | The paper keeps step A's CH rows (§5). Minimum text, fixed now: "A native CH generation of NuWro differs from the combination (Σz² = …, largest \|z\| = …); the cause has not been established." The director and Joseph may add to it, not remove it |
| Q10 | B0 passes for a generator | :42: "Unlike the analysis definitions, the predictions compute W with the neutron mass … and measure pT about their own neutrino axis" is removed for that generator, and a sentence states the method: "The predictions use the analysis definitions of W and of the muon angle, with the neutrino direction drawn from the analysis simulation". Table IV uses the rebuilt values. In every outcome the sentence gives the largest per-cell change, in units of the cell's σ |
| Q10 | B0 or B2 fails for a sample | A generator is rebuilt only if all its samples are complete. GENIE CV or GENIE + MEC incomplete: that generator keeps its present sentence, naming it alone. NuWro or GiBUU with its carbon sample complete and its hydrogen not: Table IV keeps step A's CH value in the generator's definitions for it, the present sentence names it, and the carbon analysis-definition readout goes to the note only. Its carbon sample incomplete: the same as GENIE. Minimum note text, fixed now: "For [generator], the rebuild in the analysis definitions failed control [B0/B2], so its comparison uses the generator's own definitions." |
| Q10 | the five-seed spread exceeds 0.2 σ in a cell | The size is reported; the paper wording is unchanged by it, and the note gets the spread |
| Q26 | every quadrant "agree" against 2D | :119: "only the three-observable marginal has been compared with the lower-dimensional result" becomes "Summed over each of the four (pT, p∥) quadrants, the sixteen-cell result agrees with the two-dimensional result to between X and Y per cent, within the uncertainties of the two for any non-negative correlation between them". QA and QB carry their unreported-box label |
| Q26 | 3D, either outcome | One descriptive clause only: "and agrees with (or differs from) the three-observable central value by X′–Y′ per cent at the scale of the sixteen-cell uncertainty; no 3D covariance is adopted". It reads as no validation in either direction |
| Q26 | some quadrant "agree below a correlation" | As above, with that quadrant's ρ* stated: "… agrees if the correlation between the two results is below ρ*" |
| Q26 | some quadrant "differ" | A new problem, which goes to the director and Joseph. Minimum text, fixed now, for :119: "Summed over each of the four (pT, p∥) quadrants, the sixteen-cell result differs from the two-dimensional result in quadrant(s) [list] by [d] per cent, more than twice the combined uncertainty for any non-negative correlation between them; the cause has not been established." They may add to it, not remove it |

<!-- absence-ok: a paper sentence fixed in advance for the outcome in which no cause is found -->

In every outcome the report gives the numbers, including any that make a comparison worse.

## 8. Stop rules

- Step 0: a digest mismatch stops the steps that read that input.
- A0, A1 (step A), B0, B2 (that sample), C0, C3 (step C), D's probe projection above its cap (step D): as stated above.
- A pscratch input whose atime moves: reported as a deviation. The step continues, because the read has already
  happened.
- A job above its cap, or any QOS other than regular: the job is cancelled and reported.
- Nothing in this declaration is changed after the binding except by an amendment that the director binds.

## 9. The code, and what the binding should name

The code and its tests are on this branch (director's ruling 1). The binding pins each file by blob digest.

| file | what |
|---|---|
| `nd-unfolding/fd_gencmp.py` | steps 0, A (`a1`, `ch`), C (`overlap`), D (`native`) and step B's readout (`defs`); imports FD-G's `compare`, `GIBUU_CELLS` and `Stop`, and `s1_assemble.fine_map` and `functional_matrix` |
| `nd-unfolding/fd_gencmp_kin.py` | step B kinematics, pure numpy; imports MP-5's `rotate` and `draw_directions` |
| `nd-unfolding/fd_gencmp_rebuild.py` | step B and D rebuild driver (ROOT); imports the frozen extractors and builders (`gen_to_xsec5d`, `gen5d_flux_reweight`, `gen5d_flux_supplement`, `mp3b_build`, `mp3c_build`) |
| `nd-unfolding/tests/test_fd_gencmp.py` | 52 tests, synthetic inputs; each control in this file is tested where it refuses as well as where it passes |
| `nd-unfolding/tests/test_fd_gencmp_rebuild.py` | 47 tests, synthetic inputs, including a TMemFile round trip that needs PyROOT; each control is tested where it refuses |

**Test runs** (after the review's fixes).
- Locally (numpy 1.26.4, no ROOT): `python3 -m unittest discover -s tests -p 'test_fd_gencmp*.py'` gives 99 run, OK,
  3 skipped (the ROOT round trip, and two O_NOATIME cases that need Linux).
- On a Perlmutter login node, from a copy of these files under `/pscratch/sd/j/josephrb/gencmp-tests-20261101/`, with
  synthetic inputs only:
  - `root_6_28` (ROOT 6.28/12): `test_fd_gencmp_rebuild.py`, 47 OK, none skipped, including the TMemFile round trip
    and the atime case;
  - `omnifold_py310` (numpy 2.2.6, uproot 5.6.9): `test_fd_gencmp.py`, 52 OK.

**How the frozen code reads inputs without moving their atime.**
- **Data.** `fd_gencmp_rebuild.py` reads every input's bytes through O_NOATIME and checks its pin. For the frozen
  modules, which open ROOT files by path, it puts a `MemROOT` proxy in place of their `ROOT` global. The proxy serves
  `TFile.Open` and `RDataFrame(tree, path)` from `TMemFile`s over the verified bytes, and it refuses any path not
  verified this way and any write-mode open. No frozen file is edited.
- **Code.** Before ROOT or any frozen module is imported, the frozen code tree `s5p-20260926/gen5d/code/tree` is copied
  through O_NOATIME into `<OUT>/frozen_tree/` (`.py` files only). The copy refuses, exit 2, on any digest that differs
  from INPUTS family H, on an unpinned `.py`, or on a pinned file the tree lacks. The driver then imports from the copy
  and records its digests (`--gen5d-tree-src`). 11 of its 12 `.py` files
  are byte-identical to the repository's copies. `2d-unfolding/unfold_2d_omnifold_unbinned.py` has changed since, so
  the frozen copy, not the repository's, is the one imported.
- **The GiBUU flux file** (cvmfs `MINERvA_MEflux.dat`) is pinned in INPUTS family B. Its digest, `37b56a0a…`, is the
  frozen build receipt's, and equals a direct sha256 on 2026-11-01. The driver's `--allow-meta-pin` is not used.

**What the driver restates, and the control on each.**
- MP-5's lepton, phase-space and W statements, generalised to every sample. Tested against `mp5_genie.events` itself.
- GiBUU's per-file event statements, because the frozen reader drops px, py and E_mu after its phase-space mask.
  Checked at runtime and in tests against `extract_gibuu`.
- `mp3c_build.gibuu_density`, which opens its files by path. Checked by test parity.
- The two-line GENIE supplement formula, and the flux-fix constants A and B, which live only in the unpinned main
  product's meta. Checked by B0.

**The independent review** (ruling 1) is `FD-GENCMP-REVIEW-PROMPT.txt` and `FD-GENCMP-REVIEW-ANSWER.txt` beside this file,
with the head it reviewed named in the answer's header.

## 10. Not established, and known limits

- **The hydrogen physics.** Step A changes the target, not the hydrogen model. The A-H sensitivity is descriptive.
- **The pT axis transfer.** Step B draws the neutrino direction from the analysis MC, which assumes the beam-to-ν angle
  does not depend on the interaction model. MP-5 made this assumption and found its own check limited by GENIE's
  MC statistics at p∥ ≥ 6 GeV/c (`../phase1/mp5/REPORT.md` §3.2).
- **The struck-nucleon mass** is unknown for GiBUU carbon, and step B uses the analysis code's fallback.
- **Correlations in step C.** Step C does not estimate the correlation between the sixteen-cell and 2D results. Its rule
  is stated over ρ ∈ [0, 1] for that reason.
- **Step C's power.** The strict "agree" band, 2|σ₁₆ − σ_low|, widens as the two uncertainties differ. QA and QB carry
  their unreported boxes at ±100%, which widens σ₁₆, so they reach "agree" more easily. The readout prints both bands
  for every quadrant, so this is visible. No power is computed.
- **The inputs' purge.** Families B and D sit on pscratch. A delay past about 2026-11-09 raises their exposure.

## 11. The independent review, and the lane's response to each finding

The review is `FD-GENCMP-REVIEW-ANSWER.txt`, of head `98d6a839`. Every "should fix" finding was fixed before the binding.

| finding | response | where |
|---|---|---|
| A1, asymmetric wording | Every adverse branch now has minimum text fixed in advance, which the director and Joseph may add to but not remove: step A failing, step D disagreeing, a sample failing B0 or B2, a quadrant that differs | §7 |
| A2, step D's "agree" across two routes | The generator-definitions route is primary and decides "agree". The analysis route is always formed when its samples are complete. If it disagrees, the clause names that too. `--analysis` is removed | §5, §7; `fd_gencmp.py` `cmd_native` |
| A3, partial or stopped samples | Rows per sample; a generator is rebuilt only if all its samples are complete. A B2 stop counts as a B0 failure | §7; `rebuild.json` `status`, read by `defs` and `native` |
| A4, which step-C matrix governs | The reported matrix is primary. The one without C_PL,5D is printed only, labelled as not like-for-like against Q | §4; `cmd_overlap` |
| A5, one-sided "may say so" | The sentence gives the largest per-cell change in σ in every outcome | §7 |
| A6, the agree band widens with σ₁₆ | Stated as a limit, with both bands printed per quadrant | §10 |
| A7, M_n variant and the thin GENIE hydrogen | M_n is printed only, in carbon and in CH. The A-H row's label and §2 state that GENIE's hydrogen sample did not meet B4 | §2, §3; `LABELS["genie_H"]` |
| B1, the α summary cannot fail | Reworded: printed, not gated. The pools' identity is gated by their pins | §3 |
| B2, readers ignore B0 and B2 | The driver writes no variant before B0 passes, and nothing after a B2 stop, and records per-sample `status`. `defs` reads only complete samples and lists the rest. `native` refuses an incomplete native sample | `fd_gencmp_rebuild.py` `Run.sample`; `fd_gencmp.py` `rebuild_status` |
| B3, weak atime guard | `read_noatime` refuses a pscratch file where O_NOATIME does not exist. Both atime branches are tested. A moved atime stays a recorded deviation, as §8 says | `fd_gencmp.py` `read_noatime`; `NoAtimeRefusals` |
| B4, controls untested in the refusing direction | Added refusing tests for C1 (2D and 3D), the area and units checks, the quadrant check, the PROJ3D index, R's f half, A2's V_g half, A0's shape-only half, the A1 frozen digests, `defs` and `native` end to end, the E_avail-region gate, and, in the driver, B0's target branch, `ch_b0`, the B2 stop path, the population gate and the code-tree copy | both test files |
| B5, no 3D control | C3 now also gates the 3D integral against the status headline, 3.079e-38. A quadrant that Q does not cover forms no comparison, rather than one against an incomplete sum | §4; `cmd_overlap` |
| B6, step D's probe and cap not in code | Enforced by the job scripts' `--nodes` × `--time` and the probe's `sacct` projection, as stated | §6 |
| B7, code-tree identity not gated | The copy is gated on family H's pins and refuses | §9; `--gen5d-tree-src` |
| B8, B2 population not gated | Gated exactly, against M4-W's 938,141 (GENIE CV) and 1,261,997 (NuWro) | §3 |
| S1, A1 bound to a path | A1 is now matched by digest, both the npz files and the frozen products | `cmd_ch` |
| S2, V_g notation | Corrected to U² sumw2 | §2 |
| S3, "step 0 re-verifies every line" | Corrected: each step verifies what it reads | §1; INPUTS header |
| S4, regions listed but not compared | Any such region now stops step C for an amendment. None exists on the committed definition | §4 |
| S5, M_n missing from CH | Added | `cmd_defs` |
| S6, clipped PROJ3D variance | No clip. A negative variance is recorded and flagged | `cmd_overlap` |
| S7, a hard-coded `controls_passed` | Kept: a failing control stops the run before the write | — |
<!-- absence-ok: the table quotes the review's finding titles and describes this lane's code changes; it claims no result absent -->


