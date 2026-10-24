# Declaration: R10, more reconstructed information on D-ID's binned setting (2026-10-24)

**By** the validation lane, for the director, who assigned R10 after 5D Stage 0 reported STOP
(`state/measurement-paper/5d-design-20261023/STAGE0-REPORT.md`; DESIGN §9 needs R10 as well). The test is the one
proposed in the scoping memo, [`../SCOPING.md`](../SCOPING.md) §4.2.

**Status: awaiting the director's binding.**
- The read-only preflight (§2) computed no R10 quantity, and nothing else has been run.
- The admission review returned REJECT (repairable), then ADMIT-WITH-REPAIRS on the repairs. Every finding and its
  repair are in §12.

**CITABLE FOR:** the R10 configurations, readouts, controls, pass rule and compute, fixed before any output.
**NOT CITABLE FOR:** any R10 result, any interval or coverage statement, or a decision. Claims are Joseph's.

## 1. The question and the fixed rule

**Question.** On D-ID's binned setting, does reconstructed information beyond the five binned reco scalars narrow the
J Cramér–Rao width floor **and** cut the departure residual? Two kinds of added information are tested:
- (i) finer reco bins of the five scalars;
- (ii) a sixth reco axis from whole-event tuple branches.

A pass justifies a GBDT run with the added features (SCOPING.md §4.2 item 1), and DESIGN §9 then redoes Stage 0 with
them. A STOP, together with Stage 0's STOP, is DESIGN §9's stop condition.

**The rule** (the director's assignment, 2026-10-24, restating SCOPING.md §4.2; fixed now, before any output). It is
applied on **split-half figures only**, to **any of 11 decisive configurations** (§3). For a decisive configuration X
and its null twin X̃ (§4.3):
- **Leg A, the width.** The J CR 68% half-width at T2, nominal truth, has median ≤ 10% and p90 ≤ 25%; **or** its
  median is at most half the f = 1 split-half median.
- **Leg B, the residual.** The J median |r_IBU(K = 5)| is cut by at least a third against f = 1 (X ≤ ⅔ × f = 1) at
  three or more of GiBUU, W1, W2 and W3.

**Each X gets one state:**
- **UNDETERMINED** if X̃ satisfies leg A, or leg B at three or more departures. The instrument then reads noise as
  information at X's occupancy.
- **PASS** if X satisfies leg A and leg B, X's width median is below X̃'s, and X's residual is below X̃'s at three or
  more of the four departures.
- **FAIL** otherwise.

**R10's verdict:**
- **INCOMPLETE** if the global null fails (§4.3), a control of §5 fails, a cap is reached, or a stage errors;
- otherwise **PASS** if any X passes;
- **STOP** if every X fails;
- otherwise (no pass, and at least one X undetermined) **INCOMPLETE**.

**Reporting multiplicity (the director's condition).**
- The report names every configuration that passes, with its margin over its own twin on each leg: X/X̃ width
  median, and X/X̃ residual per departure. `verdict()` computes both, with the ratios to f = 1.
- If only one of the 11 passes, and only narrowly over its twin, the report's first paragraph says so.
- No multiplicity correction enters the rule: the twins already play that role.

## 2. Preflight (read-only, login node, 0 node-h, 2026-10-24; no R10 quantity was computed)

| fact | how measured | result |
|---|---|---|
| D-ID's driver, config, tables and results are the committed bytes | sha256 against MP-4A's pins | equal (`did.py` `d918c816…`, `config.json` `aebd8c8e…`, `tables.npz` `2aab2270…`) |
| D-ID's 14 pinned `nd-unfolding` modules, its records, operands and ratio files are unchanged on main | sha256 against `d-id/config.json` | all equal |
| the rows of `of_inputs_5d.npz` carry no event identity | its 18 arrays listed | no identity array and no E_ν array |
| MP-2 S1 gives every row its identity, MAD file index and `mc_incomingE`, in MCgen order | `measurement-paper/phase1/mp2/S0-S1-REPORT.md:19-30`; S1 file keys | 12 files on pscratch, sha256 listed in `state/measurement-paper/phase1/mp2/s1_npz_sha256.txt` |
| G2's reco selection and `of_inputs_5d`'s, playlist 1A | S1's `in_ps` on G2 1A, against the 1A slice | 2,682,267 rows, identity equal to S1. Every `of_inputs_5d` reco-passing row (1,729,050) is G2-passing; 7,783 rows pass G2 only. On the 1,729,050, G2's five reco scalars equal `MCreco` bitwise |
| the reco tree joins by identity within a file | `MasterAnaDev_mc_AnaTuple_run00110000` (1A), against G2's first 400,000 rows | 186,439 reco entries, identities unique. All 96 reco-passing G2 rows of that file join once, with vertex difference 0.0 mm |
| the candidate branches exist in FHC MC and data | the 10-22 survey's branch lists (`state/data-survey-20261022/outputs/followup/branches_fhc_{mc,data}_1B.json`); the 1A file above | all present; scalar |
| reco-cell occupancy at f = 2 and f = 4 | the admission reviewer, read-only, on `of_inputs_5d.npz` | over rows with reco and truth both on the grid: f = 2, 112,995 occupied cells (MP-4A: 113,062), 181 rows per cell; f = 4, 990,356 cells, 21 rows per cell. Over all reco-on-grid rows, f = 4 has 990,594 cells, and its permutation twin the same 990,594, with 10,140,138 distinct (reco, truth) pairs against f = 4's 9,228,311 |

The full extraction repeats every row of this table on all twelve playlists as admission (§5.4).

## 3. Configurations

**Reco binnings.**
- f = 1: D-ID's 65,856-cell fine reco grid.
- f = 2: every bin split at its midpoint once, 2,107,392 cells (MP-4A extra (c)'s construction).
- f = 4: every bin split twice.

**The sixth axis (ii).** Four whole-event variables from branches in the official MAD branch documentation
(`MinervaExpt/Tuple-Documentation`, `MAD_tuple_MainDoc.csv` at `da1087cc`, sha256 `cbf34b1c…`; rows by CSV line,
header as row 1). They are computed in `r10.py` `derived_variable`. A negative or non-finite branch value is missing.

| | variable | branches | doc rows |
|---|---|---|---|
| **C1** | in-time non-muon cluster count: tracker + ECAL + HCAL | `part_response_recoil_allNonMuonClusters_{tracker,ecal,hcal}_nClus` | 4 |
| **C2** | the tracker's share of the calibrated, passive-corrected recoil energy: tracker / (tracker + ECAL + HCAL); missing if the sum is 0 | `part_response_total_recoil_passive_allNonMuonClusters_{tracker,ecal,hcal}` | 7 |
| **C3** | charged primary hadrons tracked to the vertex, inner detector | `part_response_container_total_recoil_passive_primaryHadrons_id_sz` | 30 |
| **C4** | neutron candidates | `MasterAnaDev_BlobNClusters_sz` | 229 |

**Binning of the sixth axis.**
- Three bins at the tertiles, weighted by the nominal reco weight, over the reco-passing in-grid rows: v ≤ q₁,
  q₁ < v ≤ q₂, v > q₂. Ties stay together, so a bin may be empty.
- A fourth bin holds the missing rows.
- The edges, the categories present and each bin's weight share are reported.

**The 11 decisive configurations:** f = 2; f = 4; each Cₖ at f = 1 and at f = 2; and the declared pair C2 × C3 at
f = 1. **The baseline:** f = 1, D-ID's own binning.

**Null twins.** Each decisive X has a twin X̃: X's own reco-cell labels permuted at random among the rows of each
f = 1 cell (`r10.py` `permuted_within`, seeded `[20261024, i]`).
- X̃ keeps exactly X's occupancy: every cell keeps its row count.
- Which row lands in which sub-cell is independent of everything about the row, so X̃ carries no information beyond
  f = 1.
- For Cₖ at f = 2 and for the pair, the permutation acts on the full label: refinement and sixth axis together.

**The global null.** `null3@f1` is a three-bin seeded uniform axis at f = 1 (§4.3).

**Order of evaluation** (`config.json` `order`): f1, null3@f1, then each decisive configuration followed by its twin,
with f = 4 and its twin last. f = 4 is the heaviest for memory.

## 4. What is computed

### 4.1 Setting (D-ID's, unchanged)
- **Events and truth.** The same events (`of_inputs_5d.npz`, `07fccc1a…`); D-ID's admission, rows, truth reweights,
  truth grids T1 (134 cells) and T2 (1,383 cells), and the 185 functional rows. The J group is D-ID's 109 reported J
  functionals.
- **Weight sets.** nominal, GiBUU, W1, W2 and W3, which carry the rule; q3, descriptive.
- **Roles** (D-ID's `problem`, with the nominal weighting):
  - **split, which decides:** the response, prior and known term from half A; the data and truth from half B. The
    split key is D-ID's, 798985164084644.
  - **same, descriptive and optimistic:** everything from the full sample.
  - **swap:** the halves exchanged. Used for f = 1 and the global null only: it gives the noise band of §4.3.
- **Residual.** Exact binned IBU from the nominal prior (`did.ibu`), recorded at K = 1, 2, 3, 5, 10, 20 and 200.
  - The residual is f̂/f_true − 1 per functional.
  - A group's figure is the median of |r| over its finite values (D-ID's `summaries` rule).
- **Width.** `did.fisher` and `did.widths_from_eig` at the nominal truth, unit radius, relative.
  - split: the Fisher of R_A at half B's binned nominal truth, with half A's known term.
  - same: D-ID's `widths`.
  - Quantiles count acceptance holes and non-finite widths as +∞ (MP-4A's primary convention,
    `run_mp4a.quantile_inf`). Finite-only figures are reported beside them.

### 4.2 Readouts, all reported
For every configuration and every role it runs:
- residual medians and p90s per weight set, K and group (J, EW, H2);
- width statistics at T1 and T2 per group;
- the number of occupied reco cells.

Per-functional arrays are kept for the K2 control and for the widths.

### 4.3 The null controls
- **The twins.** Defined in §3 and used in §1's states.
  - **Why they are needed.** With an exact response, a proportional split of a reco cell adds no Fisher information
    and leaves IBU unchanged. With a finite response, any split's sampling noise can only add apparent information
    (Cauchy–Schwarz per reco row, at any truth). Both facts are tested synthetically (§5.5). The split-half Fisher has
    no protection against this: R_A's noise reads as resolution as R's does.
  - **What a twin measures.** At X's own occupancy, X̃ gives the size of that spurious gain, and the spurious change
    in the residual, for a split that carries no information. **(inference)** It is the yardstick MP-4A §6a lacked
    when it called its 2× figure optimistic (`state/measurement-paper/phase1/mp4a/REPORT.md:140-146`).
- **The global null, the memo's own criterion** ("must leave every width and residual unchanged within split-half
  noise").
  - **What must hold.** On split-half figures, `null3@f1` must leave five quantities within their band: the J T2
    width median, and the J median |r(5)| at each of the four departures.
  - **The band** for a quantity q is max(2 × |q_split(f1) − q_swap(f1)|, 1% × |q_split(f1)|).
  - **If it fails,** R10 is INCOMPLETE.
  - **The likely failure mode, stated before the result.** The band is one draw and two-sided, while a null split can
    only narrow the widths (the Cauchy–Schwarz argument above). A spurious INCOMPLETE is therefore plausible, in the
    safe direction: it withholds a verdict, never invents one.
- **The swap role** mirrors the split role by construction, and a synthetic test checks it: swap equals split with
  the half mask negated, bitwise (§5.5).

### 4.4 Departures from the memo (SCOPING.md §4.2), each for the director to accept or refuse in the binding
<!-- absence-ok: each item scopes what this declared test computes; none claims that a result is absent from the repository -->
1. **K = 200 replaces "at convergence"**, descriptively. 10⁵ iterations per configuration are not affordable at
   f = 4.
2. **C4 uses the candidate count only.** The memo also named `MasterAnaDev_BlobTotalE` (row 204). That is one value
   per candidate; its sum over candidates would be a whole-event value, but it is a further choice. **The director is
   asked to accept or refuse this explicitly.**
3. **A fourth, missing bin** on the sixth axis. The memo said "3 bins".
4. **OSB widths are not computed.** The memo computed them only at a configuration whose CR widths pass. Here, OSB
   for a passing configuration is a follow-up, after the report.
5. **The null criterion is made operational** as the twins plus the global null (§4.3). The memo's text was the
   global null alone.
6. **P1r–P3r are not run.** They had no vote in D-ID.
7. **X0 runs on debug QOS** (§7), as a 20-minute smoke test. The assignment says regular QOS. X itself is regular.

## 5. Controls (any failure makes R10 INCOMPLETE)

1. **K0, plumbing.**
   - The f = 1 reco rows built here equal D-ID's `rf_fine`.
   - The f = 2 and f = 4 rows on the grid are exactly the f = 1 rows on the grid. This is MP-4A's assertion.
2. **K1, D-ID reproduced, bitwise, on full per-functional arrays.**
   - D-ID's own machinery, on this run's inputs, reproduces its committed `tables.npz` widths at T1 and T2 (nominal,
     nominal weighting) over the 183 committed functionals.
   - It reproduces the committed K = 5 same-sample trajectory row (`traj/T2/same/nom/<ws>/r`, float64) for all six
     weight sets.
   - It reproduces the committed J medians in `results.json` `summaries`: GiBUU 0.08300, W1 0.05424, W2 0.00595,
     W3 0.04860, q3 0.05305, nominal ≈ 0.
3. **K2, the generic path equals D-ID at f = 1, bitwise, on full arrays.**
   - The K = 5 residual of every functional, for every weight set, in the same and split roles.
   - The same-role widths at T1 and T2, against D-ID's `widths`.
   - The split-role widths at T1 and T2, against this file's Fisher applied to D-ID's own split problem.
4. **Extraction admission and join** (`r10_extract.py`, all twelve playlists).
   - **Input sha256:**
     - `of_inputs_5d.npz`;
     - the S1 files, against MP-2's list;
     - the G2 files, against their receipts;
     - each MC manifest, against the sha256 S1's receipt recorded (`state/measurement-paper/phase1/mp2/s1_receipt.json`).
   - **Per playlist:**
     - G2's in-phase-space count equals S1's;
     - identity and truth scalars equal S1's bitwise;
     - G2's truth, cast as `nn_dump_inputs` casts it, equals `MCgen` bitwise;
     - `pass_reco` ⊆ G2's `sim_pass`;
     - G2's reco scalars equal `MCreco` bitwise on `pass_reco` rows.
   - **The join.** Every reco-passing row joins to a reco-tree entry in its own file. No joined row's identity is
     repeated in that file; repeats among unjoined keys are counted and reported. The vertex equals G2's within
     10⁻⁶ mm.
   - **On failure:** exit 7, distinct from the guard's own codes, and nothing is written.
5. **Synthetic tests** (`test_r10.py`, 35, all pass at this commit):
   - **Binning and twins:** binning and tertiles; the twin keeps every group's label multiset and the occupancy,
     shuffles, is seeded, and destroys a label correlated with a row property; derived variables.
   - **The rule's branches:**
     - a pass, with margins;
     - a pass by halving;
     - width alone is a FAIL and gives STOP;
     - two departures are not enough;
     - a twin on either leg makes X undetermined and R10 incomplete;
     - X must beat its twin;
     - a failed global null is incomplete;
     - one pass among undetermined configurations is still a pass;
     - the cut either side of ⅔;
     - the global-null band;
     - the zero guard.
   - **Information:** an exact split keeps Fisher and IBU; a noisy split inflates Fisher.
   - **The swap role** equals the split role with the half mask negated, bitwise (residuals and widths).
   - **The join:** a pass, a missing entry, a vertex mismatch, a duplicate needed key, a duplicate unneeded key, a
     wrong file.
   - **End to end,** on D-ID's synthetic world (real grid, rows and reweight code):
     - a clean run with K0, K1 and K2 passing, against D-ID tables written in the committed 183 layout. Every twin
       has exactly its configuration's occupancy;
     - **K1 refuses one ulp changed in one functional's K = 5 residual;**
     - **K2 refuses a wrong prior in the generic path;**
     - the extraction-receipt check refuses each of seven defects;
     - `--controls-only` records K0–K2 and keeps no readout.
   - **The configuration.**

## 6. GiBUU restricted to E_ν < 20 GeV (descriptive; decides nothing)

GiBUU's sample stops at E_ν ≈ 20 GeV (`KNOWN_ISSUES.md` row 82). For every configuration, the GiBUU and nominal
residuals are also computed with every row (truth, data and response, both halves) restricted to S1's
`mc_incomingE` < 20,000 MeV.
- They are reported as values, and in the report as a ratio to f = 1 within that population, beside the
  full-population figure.
- They enter no rule.

## 7. Compute (grant: ≤ 4 CPU node-h under the measurement phase-1 grant)

**Remainder before this test.** The phase-1 ledger (`state/measurement-paper/phase1/LEDGER.tsv`) charges 11.03 of 35
CPU node-h, read 2026-10-24.

**Deploy.** A clean checkout of the bound commit at `/pscratch/sd/j/josephrb/r10-20261024/deploy/<sha>`. The launcher
refuses a dirty tree or another HEAD. The step runs under `mnv_guarded_run.py --expect-root <deploy>` with the
`omnifold_py310` interpreter.

**X0, smoke** (debug QOS, 1 node, limit 0:20, projected ≈ 5 min).
- Playlist 1L only, output to `r10-20261024/smoke/`.
- It proves the guard, the environment and the join on the smallest playlist.
- Its receipt records the time to hash inputs, to load them, and per playlist.

**X, extraction** (regular QOS, 1 node).
- All twelve playlists. Output `r10-20261024/run/extract/r10_extra.npz` (≈ 2.4 GB) and its receipt.
- **Projection:** X0's hash time scaled by the bytes hashed, plus its load time, plus its per-row playlist time
  × 32,849,103 / 1L's rows.
- **Limit:** 1.25 × the projection, rounded up to the minute, with no floor.
- **Cross-check:** the closest measured analogue is S1's whole twelve-playlist pass, which took 0.102 CPU node-h
  (`state/measurement-paper/phase1/mp2/S0-S1-REPORT.md:70-76`).

**Y, the binned computation.**
- **Where:** local, in a detached worktree of the bound commit, with 2 BLAS threads as in D-ID's run record. This
  keeps K1's bitwise reproduction meaningful: D-ID and MP-4A both ran on this machine.
- **Inputs:** `of_inputs_5d.npz`, copied read-only once, and `r10_extra.npz`. Both are sha256-checked, and `r10.py`
  refuses an extract whose receipt is not a complete admitted run of that file, by this `r10_extract.py`, on this
  `of_inputs_5d.npz`.
- **Results:** written after every configuration and on any failure.
- **Hard caps:** 16 core-h of process CPU and 14 GiB RSS, checked by D-ID's `Budget`.
- **Projected CPU:** ≈ 3 core-h **(inference: D-ID's whole diagnostic took 0.81 core-h at f = 1, and R10 runs 24
  configurations without D-ID's 10⁵-iteration convergence)**.
- **Projected memory:** ≈ 9–11 GB at peak **(inference: ≈ 5.4 GB of row arrays held throughout, and f = 4's
  histograms ≈ 3 GB; the twin has f = 4's occupancy and 10% more distinct pairs, measured by the reviewer)**.
- **The 1.25 × rule applies to the cluster jobs.** Y is stopped by its caps, and its use is reported against the
  projection.

**Charge.** Worst case X0 0.33 + X ≤ 2.0 = **≤ 2.33 CPU node-h**, inside the 4 granted. Y charges no node-hour.

**Limits.** Every job under 12 h, never premium, on account m3246. A cluster job past 1.25 × its projection is
stopped and reported. Each job goes in [`LEDGER.tsv`](LEDGER.tsv) (ElapsedRaw × billing/256/3600).

**Storage.** pscratch only (68% full), ≈ 3 GB under `r10-20261024/`. Nothing goes to CFS.

## 8. Order after binding

0. **Controls first, locally, 0 node-h.** Run `r10.py --controls-only --inputs <copy> --out <dir>`. It needs no
   extraction. It runs K0, K1 and K2 on the real events, at f = 1, and records only their outcomes; no R10 readout
   is kept or printed. If it fails, stop and report before any node-hour.
1. **X0.** Deploy the bound commit; submit X0. When it is terminal, check sacct, the receipt and the controls. Set X's
   limit by §7 and record its projection in LEDGER-NOTES before submitting X.
2. **X.** When X is terminal, check sacct, the receipt (every playlist admitted, the join controls passing), the guard
   inventory and the output sha256. Copy `r10_extra.npz` locally.
3. **Y.** Run locally:

   ```
   OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 python3 r10.py --inputs <copy> \
       --extra r10_extra.npz --extract-receipt r10_extract_receipt.json --out <dir>
   ```

4. **Review.** Have an independent read-only reviewer check the result in both directions (nothing lost, nothing
   strengthened).
5. **Report.** Commit REPORT.md, the receipts and the ledger; open a PR and message the director. This lane does not
   merge.

**Any defect in the code found after binding stops the run before any output is looked at, and goes to the
director.**

## 9. Evidence committed with the report
- `r10_results.json` and `r10_tables.npz`;
- the extraction receipt with its admission table;
- `LEDGER.tsv`, sacct and the guard inventory;
- the sha256 of `r10_extra.npz` (cluster and local copy). The file itself stays on pscratch.

## 10. Not tested
<!-- absence-ok: scoping statement of what this declared test covers, not a claim that a result is absent -->
- Information finer than 4× per axis, or in branches other than C1–C4.
- An unbinned estimator.
- Response-MC noise beyond what the split halves, the twins and the global null measure.
- Departures in the added variables' own truth correlates. SCOPING.md §4.2 requires one before any coverage claim
  after a pass.
- Background, and real data.

## 11. Files (this directory)

| file | role |
|---|---|
| `r10.py` | the binned computation, controls K0–K2, the global null and the verdict |
| `r10_extract.py` | the extraction pass (§5.4) |
| `sbatch_r10_extract.sh` | the guarded launcher for X0 and X |
| `config.json` | pins, configurations, rule constants, caps |
| `test_r10.py` | the 35 synthetic tests |
| `LEDGER.tsv` | the compute ledger (empty until X0) |

Their sha256 are recorded in the binding.

## 12. Admission review (before binding)

**Reviewer.** A fresh, read-only Claude subagent (Opus 5.5), the same model family as the author, so the review is
not cross-provider independent. It was given the assignment, the memo, D-ID's and MP-2's code, this directory, and a
prioritised review brief.

**Verdict: REJECT (repairable).** Every finding and its repair:

<!-- absence-ok: the review's findings describe this lane's own draft code at review time, not results in the repository -->
| # | finding | repair |
|---|---|---|
| 1 | BLOCKING: K1 compared D-ID's 185-entry widths with the committed 183-entry table, so it would fail on real data after the extraction was spent. The synthetic suite bypassed K1 | K1 compares on `f183`, and adds the full K = 5 trajectory row per weight set. A synthetic K1 runs against tables written in the committed layout, and refuses a one-ulp change |
| 2 | BLOCKING: a twin meeting a leg made its configuration fail, so a broken instrument could produce STOP | the UNDETERMINED state; STOP only if every X fails determinately; otherwise INCOMPLETE (§1) |
| 3 | MAJOR: the twins (uniform sub-cells) were 2.3–3.9× more fragmented than their X, measured on the real file. The memo's null criterion was replaced without saying so. An overclaim about what the twin measures | twins by permutation of X's own labels within f = 1 cells (exact occupancy). The global null `null3@f1` within the split/swap noise band. Both stated as departure 5. The overclaim is rewritten (§4.3) |
| 4 | MAJOR: memory near 16 GiB at f = 4, and nothing written before the end | the restricted histograms are built after the full ones are freed; bins are int8; f = 4 runs last; results are written after every configuration and on any failure; a memory projection is given (§7) |
| 5 | MAJOR: the K2 power claim had no committed test, and the split widths had no control | K2 refuses a wrong prior in a committed test. K2 now covers the split-role widths |
| 6 | MINOR: X0 on debug QOS | stated as departure 7 |
| 7 | MINOR: X's 0:15 floor could exceed 1.25 ×; X0 scaling multiplied fixed costs; Y's cap was 5× its projection | per-stage projection with no floor; S1's 0.102 node-h as the cross-check; the 1.25 × rule stated for cluster jobs, with Y's hard caps |
| 8 | MINOR: undeclared departures (the missing bin, OSB), and a weak reason for C4 | departures 2–4, with C4 put to the director explicitly |
| 9 | MINOR: the manifest was not pinned; duplicates were counted over the whole tree; exit 3 was ambiguous; no direct MCgen check; `r10.py` did not check the receipt's code or input digest | all repaired (§5.4, §7) |
| 10 | MINOR: K0 was close to a tautology, and `resid_stats` could raise on an empty group | K0 is described as plumbing and gains the nested-rows assertion; `resid_stats` returns NaN on an empty set |

**Second pass: ADMIT-WITH-REPAIRS.** The reviewer verified all ten repairs at their lines and found no blocking or
major defect. Its seven minor points, and what was done:
<!-- absence-ok: these points describe this lane's own draft code at review time, not results in the repository -->
1. swap had no control: the bitwise test above;
2. K1/K2 could not run before X: `--controls-only`, step 0 of §8;
3. the tables were lost on INCOMPLETE: written on the failure path too;
4. the receipt's input-digest branch was untested: tested;
5. the likely INCOMPLETE mode: stated in §4.3;
6. wording: the occupancy rows and twin pairs in §2 and §7, and the brief here;
7. a stray `__pycache__`: removed, and commits add explicit paths only.
