# SCOPING (c): 2D method coverage on 1B's staged design, priced from RE-2's measured costs (2026-11-02)

**By** the `limitation-resolver` lane, for the director. The scoping costs nothing.

**Under** [`DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md`](../../../DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md)
(#690) item 3(c): "A held-out-tune coverage ensemble for the 2D covariance, on 1B's staged design, with the covariance
remade at each truth. It is priced first." The director's message of 2026-11-02 adds:
- price it from RE-2's measured per-unfold costs;
- fix the grading in advance with a simulated null;
- name what it can and cannot license, given `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`;
- check the composite weights before the bulk (1B's lesson).

**MEASURES:** nothing. It reads records at `origin/main` `7bac3c63`. A read-only subagent (claude-school) gathered the
facts, and this lane re-read the ones below.

**CANNOT AUTHORIZE:** a declaration, a binding, a run, or a paper edit.

**CITABLE FOR:** the price range, the prerequisites, and what such a campaign could and could not license.

**NOT CITABLE FOR:** any coverage result.

Paths are as in 5B's declaration. `RE2` = `2d-closeout/stageF/methods/re2/`. `1B` =
`measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md`.

## 1. What is being tested

- **The adopted 2D result** is E_R, with Q_R as its headline uncertainty. C_model stays beside it (`DECISION-20261024-joseph-adopt-re2-2d-refined.md:30-32`).
- **Q_R is S5_R + C_PL_R** (`2d-unfolding/re2/partc/re2c_combine.py:7`), where S5 is universe + statistical + seed.
- **Per-cell median σ, %**, from `RE2/run/partc_r2/partc-r2/outA/budget_Q.json.gz`:

  | block | median σ | median share of the cell variance |
  |---|---|---|
  | Q_R | 6.41 | — |
  | universe | 5.93 | 0.866 |
  | statistical | 0.676 | 0.009 |
  | run period, C_PL_R | 2.09 | 0.107 |
  | seed | 0.048 | — |

  The universe block carries most of the variance.

**1B's design, applied to 2D:**
- two fixed held-out tunes, G18_10a_02_11b and AR23_20i_00_000, and optionally a plug-in truth;
- 300 drawn natures per truth, each unfolded once by the production procedure;
- the covariance remade at each truth from its pseudo-data at their means;
- grading per truth against a simulated null matched to the draw laws (1B §4.3, §5.2).

## 2. Prerequisites before a declaration can be priced firmly

**P1. No 2D held-out-tune truth exists.** `grep -rlE 'G18_10a|AR23_20i' 2d-unfolding` returns nothing (rc 1; 275 tracked
files).
- 1B's truths are 5D F1 products: the gated, k-normalized, bridged ratio, applied through `s5n_pseudo.truth_weight`
  (1B `:174-178`).
- A 2D truth needs that ratio evaluated on the 2D simulation's events. Two things are unchecked:
  - whether those events carry the truth variables the ratio reads;
  - whether a projection onto (p_T, p_∥) would still be the tune. A projection would not be the same truth.
- Settling this needs a read of the 2D event-loop trees. That is 0 node-h, on a login node.

<!-- absence-ok: "Connect 34 has not run" rests on the commit message of 1ef3d855 ("Connect 34, not run: attrib/n1_attrib.py, the descriptive attribution") and the director's (c) ruling that P2 waits for (a)'s attribution -->
**P2. The composite weights, before anything else (1B's lesson).**
- 1B stage 1 stopped at its N1 guard, at 0 node-h, before any job. On the declared draws the composite weight reached
  about 255, against a bound of 10.
- That is recorded on the unmerged branch `origin/report/1b-staged-stage1-20261102` (`1ef3d855`), in
  `connect32-s1-0.out:28-33`. On main, only `DECISION-20261102-…:29` records it.
- The cause: composing about 40 bands' ratios to the CV weight blows up on rows whose CV weight is small (AMENDMENT-1
  §3). Connect 34, the attribution, has not run.
- **So a 2D design that composes universes per toy carries the same exposure.**
  - Its first step must be the exact composite-weight receipt (the all-draws bound and the declared-draw pass) over the
    real 2D bank, on a login node.
  - It runs at declaration time, before the price is fixed, not at binding 2.
  - If (a)'s redesign changes the composition rule, (c) inherits it. **So (c)'s declaration should follow (a)'s
    N1 attribution, not precede it.**

**P3. Whether the 2D inputs still exist.**
- RE-2 part B's staged inputs were deleted (`RE2/RE2-PARTB-REPORT.md:10`).
- Whether the 2D universe, lateral and period inputs survive on pscratch or HPSS (`RE2-HPSS-RECEIPT.md`) needs a
  read-only cluster check.
- If the laterals are gone, the lateral block is carried rather than remade, as 1B does for 5D (1B `:292`).

**P4. The same-sample limit.**
- 1B's natures are drawn on the same simulated rows the unfolding trains on.
- The note attributes VL170's over-coverage to toys "built on the training MC events" (`docs/analysis-note/sec_validation.tex:163`).
- An earlier 2D design found that no independent population exists, and that the production omnifile carries no event
  identity (`DESIGN-20261008-2d-independent-statistical-validation.md:44-63`).
- A held-out tune moves the truth. It does not make the pseudo-data independent of the training rows. The declaration
  must state this as a limit and must not grade around it.

## 3. Price, from RE-2's measured charges

**The units.** Each is an RE-2 part B job's charge divided by its runs (`RE2/RE2-PARTB-REPORT.md:56-64`; arithmetic):

| run class | job | runs | charge, node-h | per run |
|---|---|---:|---:|---:|
| central | J1 60195820 | 3 | 0.2528 | 0.0843 |
| universe | J2a–d | 175 | 21.3538 | 0.1220 |
| lateral | J3 60195838 | 10 | 1.7150 | 0.1715 |
| statistical replica | J4a–c | 300 | 14.6609 | 0.0489 |
| period | J8 60195845 | 37 | 1.1358 | 0.0307 |

**Per truth**, with the covariance remade as 1B remakes its blocks (1B §4.3):
- **Universe block, 175 runs: about 21.4.** This dominates. A design that remakes fewer universes is cheaper, but it
  no longer remakes the reported procedure.
- **Statistical block, 50 runs** (1B's 50): about 2.4. With Q_R's own 300 runs, it is about 14.7.
- **Lateral, 10 runs:** about 1.7, if the inputs exist (P3). Otherwise it is carried.
- **Central, 1 run:** 0.08.
- **Seed:** carried. Its median is 0.048%, and a single check unfold is priced in the central run.
- **C_PL_R: carried.** No simulation draw produces a run-period difference.
- **300 toys, one unfold each:** about 14.7 at the statistical-replica rate, or 25.3 at the central rate. The two
  bracket the packing.

**Totals** (all arithmetic):

| scope | node-h |
|---|---|
| per truth, with the remade blocks | about 40–51 |
| two tunes | about 80–102 |
| with the plug-in truth | about 120–153 |
| with Q_R's full 300-run statistical block | about +12 per truth |
| receipts, pilot and development | a few, to be priced in the declaration |

**Against the rules:**
- Every job fits under 12 h by lane packing, as RE-2's did.
- The latest group balance on record is 2,050.9 node-h, so half is 1,025.5 (on the unmerged branch above; main's latest
  is 2,069.4). The campaign is under half, so the price rule (`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md:52-59`)
  does not send it back to Joseph.
- It is roughly 60–100 times campaign (b)'s price.

## 4. Grading, in outline

The rule follows 1B §5.2, re-derived for 205 cells:
- **The null:** each block's centred shift vectors at T, with their draw probabilities. The Gaussian parts must sum to
  C_T to 10⁻¹², and the null is evaluated before any toy error is read.
- **Per cell:** cell c fails if #{|e_tc| ≤ σ_c} ≤ k_c, the largest k with P(Bin(300, p_c) ≤ k) < 0.025/205.
- **Jointly:** a joint χ² region at < 0.025.
- **Size:** at most 0.05 per truth.
- **Power:** the declaration must compute the power at 205 cells. With the Bonferroni divisor at 205 rather than 16,
  the per-cell resolution is coarser than 1B's 0.10.

## 5. What it can license, and what it cannot

<!-- absence-ok: quotes the paper's own qualifier at paper_body.tex:109 and :287; no absence is asserted here -->
**If both tunes COVER**, the paper's "has not been tested" (`paper_body.tex:109, :287`) could give way to a sentence
scoped like this:

> at two held-out generator tunes, the analysis procedure's covariance, remade at each tune's truth, covered pseudo-data
> drawn about that truth at the nominal rate, per bin and jointly

The scope carries the run-period block as carried, not tested.

<!-- absence-ok: scoping statements about what the design draws and what a pass can license, not claims that a result does not exist -->
**It cannot license:**
- **Removing the earlier fail.** The fixed-truth test of the earlier statistical band (VL162) failed: C2 = 0.9121
  against the window [0.9281, 0.9722] at 100 toys (`OUTCOME-20261005-2d-fixed-truth-coverage-fail.md:35-42`).
  - The current band differs in four ways: the completeness division was removed, the seed went 1 → 42, the background
    stream was added, and the estimator was refined.
  - #690 item 2 keeps that fail in the consolidated Limitations statement. A pass of (c) is a different test of a
    different procedure. It does not overturn the earlier result, and it does not re-test that band.
- **Coverage of the reported Q_R at the data's point.** Q_R is made at the data, not at T (1B `:284-286`, the same
  limit for 5D).
- **A coverage rate.** "With two truths there is no coverage rate" (1B `:70`).
- **Simultaneous coverage** beyond the declared joint region.
- **Independence from the training rows** (P4). In the director's words, to be carried verbatim into the declaration:
  "A held-out tune moves the truth, not the sample."
- **Anything about C_PL_R or C_model.** Neither is drawn, so it carries no coverage test of them.

**If a tune fails,** the paper states the failure: the wording is Joseph's, and it is fixed in the declaration before
any toy is read, as 1B §12 does.

## 6. Recommended order

1. **(a)'s N1 attribution and redesign** (connect 34). It decides the composition rule (P2).
2. **The 0 node-h checks:** P1 (truth variables on the 2D events) and P3 (do the inputs exist), then P2's composite
   receipt on the 2D bank.
3. **The (c) declaration,** with its price fixed from step 2, then a fresh Sonnet audit and the director's binding.

**Campaign (b) does not wait on any of this.**

## 7. Receipts: P1 and P3 (login23, 2026-11-02T19:56:50Z, 0 node-h)

**Approval:** the director's message of 2026-11-02 allowed metadata reads only: O_NOATIME, tree and branch listings, and
`stat`, with no event content beyond branch names and entry counts.

**The probe:**
- Script `fd/receipts-cov2d/scoping/p1p3_probe.py` (sha256 `122d727f…`), run by `omnifold_py310`'s Python (uproot 5.6.9)
  from `/dev/shm` and deleted afterwards. The deletion is confirmed by `ls`.
- Its output, verbatim: `fd/receipts-cov2d/scoping/p1p3_probe.out`.
- Each ROOT file was opened through an `os.open(…, O_RDONLY | O_NOATIME)` descriptor. `stat` before and after shows
  atime unchanged on both files read.

**What the tune ratio reads.** F1's G18 and AR23 ratios are s5e-shape-ratio/1 files on **all five axes** (p_T, p_∥,
E_avail, q3, W) over the 5D fine edges (`nd-unfolding/fd_f1_prep.py:10, 67`).
- `s5e_deform.ratio_weight` looks up each simulated event's cell from its truth coordinates on every listed axis
  (`nd-unfolding/s5e_deform.py:50-71`).

**P1, the answer.** The two 2D omnifiles differ:

| file (RE-2 role) | `mc_signal_reco` branches | `mc_truth_denom` branches | entries (signal / truth / data) |
|---|---|---|---|
| CV, `$CV`: `/global/cfs/…/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root`. 387 of RE-2 part B's run argv name it (`run/partb_runs.tsv`), E_R's among them | `sim, sim_pz, sim_pass, w_reco, MC, MC_pz, w_truth` | `MC, MC_pz, w_truth` | 32,849,103 / 32,849,103 / 4,119,797 |
| universe, `$UNI`: `$P/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root`. 210 run argv name it | 470 branches, including truth `MC_eavail, MC_q3, MC_W` | 236, including `MC_eavail, MC_q3, MC_W` | 32,849,103 / 32,849,103 / 4,119,797 |

- **The CV omnifile does not carry the truth variables the tune ratio reads,** so G18 and AR23 cannot be applied to the
  events E_R is unfolded from.
- **The universe omnifile does carry them,** with the same entry counts in all three trees.
- A 2D held-out-tune truth is therefore possible only if one of two things holds:
  - **(i)** the universe omnifile's CV columns are shown equal, row for row, to the CV omnifile's. That is a content
    check, outside this probe's approval;
  - **(ii)** a 2D design draws its pseudo-data from the universe omnifile, with a control that its CV-only unfold
    reproduces E_R.
- The (c) declaration must choose between them and declare the check. A projection of the 5D ratio onto (p_T, p_∥)
  would not be the tune, and it is not offered.

**P3, the answer** (`stat` only; no sha256 was taken):

| input | where | present | last access (atime, UTC) |
|---|---|---|---|
| CV omnifile | CFS | yes, 2,144,008,221 B | 2026-10-23 |
| universe omnifile | pscratch | yes, 171,117,087,867 B | 2026-10-24 |
| production flux and universe flux integral | pscratch | yes | 2026-10-30 / later |
| 10 active laterals (5D-format, merged) and SHA256SUMS | CFS | yes, about 53.8 GB each | 2026-10-24 |
| period inputs PA, PB, PC, ALL | pscratch | yes | 2026-10-24 |
| RE-2 part B's staged copies | pscratch | **no** (deleted under B9, as recorded) | — |
| 12 per-playlist CV omnifiles and 12 per-playlist universe omnifiles (2D) | pscratch | yes | 2026-10-14/15 |

- The pscratch inputs (the universe omnifile, the period inputs and the per-playlist files) were last accessed
  2026-10-14 to 10-24. §8 gives their exposure dates.
- The CFS inputs are not purged.
- The per-playlist 2D omnifiles are also what campaign (b)'s §9 alternative would read.

## 8. The director's rulings for the (c) declaration (2026-11-02, by message)

**1. Two controls, in this order, both declared:**
- **(1) A content check** (login node, 0 node-h, O_NOATIME). `$UNI`'s CV columns must equal `$CV`'s row for row on
  every shared branch: `sim`, `sim_pz`, `sim_pass`, `w_reco`, `MC`, `MC_pz` and `w_truth` in `mc_signal_reco`, and
  `MC`, `MC_pz` and `w_truth` in `mc_truth_denom`. The data and background trees' shared branches are compared too.
  This check makes `$UNI` a valid basis.
  - It belongs to the declaration. Today's approval did not cover it.
  - **If it fails, (c) stops and returns to the director.**
- **(2) Pseudo-data drawn from `$UNI`,** with an end-to-end gate before any toy: the CV-only unfold from `$UNI` must
  reproduce E_R.

**2. No projection** of the 5D ratio onto (p_T, p_∥) is offered.

**3. A retention section is required.** (c) must finish before the earliest exposure date of the inputs it reads,
and the declaration states each date and size.
- The exposure date is atime plus 8 weeks, as `FD-CT-RETENTION.md` §2 computes it. The atimes are from §7's probe.
- **Files are never touched to reset atime.** NERSC policy forbids circumventing the purge.
- HPSS cannot hold `$UNI` (about 66 GiB free), and CFS is over Joseph's rule. The director takes long-term storage to
  Joseph.

| input | size | atime | exposed from | (c) reads it? |
|---|---:|---|---|---|
| `$UNI`, the 2D universe omnifile | 159.4 GiB | 2026-10-24 | **2026-12-19** | yes, the basis |
| the 2D period inputs PA, PB, PC, ALL | 4.0 GiB | 2026-10-24 | 2026-12-19 | no, while C_PL_R is carried |
| the production flux and the universe flux integral | < 1 MiB | 2026-10-30 | 2026-12-25 | yes |
| the 12 per-playlist 2D universe omnifiles | 159.4 GiB in all | 2026-10-14 | **2026-12-09** | no; (b) §9 would |
| the 12 per-playlist 2D CV omnifiles | 2.0 GiB in all | 2026-10-15 | 2026-12-10 | no; (b) §9 would |
| `$CV`, the 10 laterals | — | — | not purged (CFS) | yes |

**For (c), the deadline is 2026-12-19,** set by `$UNI`. (c)'s order puts (a)'s attribution first, so the declaration
must show its schedule fits before that date, or state that it does not.
