# MP1-A S1–S3: report (G3 FAIL for em and other; S2 and S3 stopped)

**Status, 2026-10-20 21:15 PDT.**
- The S1 event loops, merges, lateral dumps and data unfolds all completed, and unfold verification passes.
- **G3 fails for em and other** (and for the xtalk variant). Under the frozen rule, S2 stops. No band number and no
  decision exists.
- The G3 result went to the director before anything else. The director ruled (binding addendum 10):
  - MP1-A is recorded as not calibrated, and MP1-A-full is priced (≈ 230–320 CPU node-h);
  - a descriptive noise-floor study was run: the unfold is seed-invariant, so training-seed noise is ruled out;
  - a descriptive partial S2 with proton and meson only was run, labelled post hoc: no decision moves.
- Cluster access, lost at 15:04 PDT when the NERSC certificate expired, returned at 17:24 PDT after Joseph renewed it.
  That was before the maintenance drain, so no job was exposed to it (§ "On resumption").

**By** the measurement session, under PLAN §2.3, BINDING-PHASE1 §2 and ADDENDUM-2 R1–R5. **Cutoff:** 04:00 PDT
2026-10-21; anything unfinished then is cancelled cleanly and recorded as deferred.

## G0 per playlist, recorded 2026-10-20 13:25 UTC, before any S1 pass was submitted: **PASS for all 12**

Receipts: `s1-receipts/g0/G0_<PL>.json` and `F_<PL>.txt`. Each table was built from the playlist's first MC file
and tested on its second, using the selected-like events of each.

**One change to the tabulation, made before any S1 pass.** In 1B, 1E, 1N and 1O the intersection of two
near-parallel neighbouring segments was ill-conditioned (slopes 1.530447 and 1.530537 near 2.23 GeV) and fell outside
the gap between them. `s0_g0_ftable.py` now places such a knot at the gap's midpoint, on the mean of the two lines.
The tables of the other eight playlists are unchanged.

| PL | train / held-out events | knots (midpoint) | max \|F − q0\|/q0 on held-out | held-out events beyond the last knot |
|---|---|---|---:|---:|
| 1A | 42,436 / 42,298 | 13 (0) | 2.1e-14 | 0 |
| 1B | 41,856 / 42,825 | 13 (1) | 3.3e-09 | 0 |
| 1C | 42,820 / 42,644 | 13 (0) | 3.3e-14 | 0 |
| 1D | 42,092 / 42,430 | 13 (0) | 2.0e-14 | 1 |
| 1E | 42,604 / 42,133 | 14 (1) | 5.9e-14 | 0 |
| 1F | 40,432 / 40,691 | 13 (0) | 8.0e-14 | 6 |
| 1G | 40,579 / 40,096 | 13 (0) | 6.0e-14 | 0 |
| 1L | 37,017 / 38,218 | 13 (0) | 9.7e-15 | 1 |
| 1M | 37,577 / 37,604 | 13 (0) | 2.2e-14 | 1 |
| 1N | 62,823 / 62,450 | 13 (1) | 1.6e-09 | 1 |
| 1O | 34,616 / 33,996 | 13 (1) | 4.9e-10 | 0 |
| 1P | 34,285 / 33,285 | 13 (0) | 1.9e-14 | 1 |

- Every playlist passes the 1e-4 tolerance by at least four orders of magnitude, so no fractional fallback is
  needed.
- Held-out events beyond the training range use the last segment's slope; they are included in the maxima above.

## S1 submission (2026-10-20 13:29 UTC) and what is frozen before any S1 result

**Jobs.** 132 shared jobs, ids 60034037–60034191 (`/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/submitted.tsv`).
- 12 playlists × 11 variants: `zero`; proton, meson, em and other at ±1σ; xtalk ±1σ (the R3 variant only).
- q0 by F-propagation with each playlist's table; fuzz pro-rata; binary md5 `15b4789f…` (the S0 species build).
- Time limits per playlist are max(3 h, 1.8 × W2b's slowest pass): 1M 6.5 h, 1F 5 h, 1N 4.5 h, 1D and 1G 4 h, 1E 3.5 h,
  the rest 3 h. The worst-case reservation is 19.55 node-h; the central projection is about 10.5 node-h for the event
  loops and about 1 for the dumps and unfolds.

**Frozen before any S1, S2 or S3 output exists** (sha256 of what will run, in `s1/tools-v3/TOOLS.sha256`
`e793dbf6…`):
- event-loop patch `1ab5e084…`; universe header `a87cb157…`;
- `s5p_joint_mp1.py` `0906f997…`, a copy of `nd-unfolding/s5p_joint.py` (blob `51d3424f`, the same as the W2 evaluate
  deploy `e9372b75`). The only change is the keyed species z_s = default_rng([pseudo_seed, 0x4D31, i_s]);
- `s5p_recompute_mp1.py` `52311916…`, a copy of `nd-unfolding/s5p_recompute.py` (`81b879ae…`, the version W2's
  recompute check used). It implements the same keyed draw independently from the R5 text;
- `mp1_s2.py` `ff2f79ec…`: G3 tolerance 0.2, evaluated on each null's domain (all 109 cells; GiBUU p∥ < 6 GeV/c).
  The design copies change only `lateral_endpoints/SpeciesResponse_*`, `species_bands` and `species_z_key`. The
  primary design has proton, meson, em and other; the variant adds xtalk;
- `mp1_s1_tables.py` `80b32172…` and `mp1_s1_pipeline.sh` `71fc5191…`: merge, dump and unfold the W2b way, on the W2
  frozen deploys `c1cba7bf` (dump), `4e4b4f56` (unfold) and `e9372b75` (merge and evaluate).

**Code test of S2/S3, not a result.** The test design used W2b's rr0/rr1 unfolds as fake proton endpoints.
`s5p_joint_mp1` evaluate took 71 s and `s5p_recompute_mp1` took 59 s (`--no-sequential`, as W2's check). Compare:
**AGREE, 1379 of 1379 items.** Output is in `s1/codetest/`; the fake band is not reported.

**How rows that fail selection are handled (director's question).**
- The universe shifts every reco row the event loop evaluates. Selection never reads the recoil (vertex, apothem,
  muon angle, MINOS match, dead time, charge), so the pass flags are identical in every pass; this was verified for
  all seven S0 passes.
- Rows that fail selection keep `sim_pass` = 0 and carry shifted q3, W and E_avail values. The J-cell readout and
  `s5p_input_dumps.py lateral` use passing rows only.
- `mc_background` holds only passing rows, and `mc_truth_denom` holds truth variables, which are never shifted.
- So no row that fails selection reaches a J cell, the background tree or the truth tree through the shift.
- G0 validates F on selected-like events only. For any passing row that is off F, the difference form
  q0 + F(pc') − F(pc) still applies F's local response. At S0, |Δq0| ≤ 1.067·δ·q0 on all passing rows.

## Event loops: what ran (the shared submission was superseded)

- **Shared was starved.** 1.5 h after submission only 2 of the 132 shared jobs were running, with shared draining for
  `maintenance_20261021`. The coordinator cancelled the 130 PENDING copies (sacct: CANCELLED, none ran, 0 node-h).
- **Packed on regular instead.** The coordinator submitted the reviewed packed launcher (`tools-v4`
  `sbatch_mp1_s1_packed.sh`, sha256 `b19bc6f9…`): one exclusive node per 3 playlists, all 11 variants, one srun step
  per pass at `--mem=14G`.

| job | qos | content | ElapsedRaw (s) | node-h |
|---|---|---|---:|---:|
| 60034037 `mp1s1_zero_1A` | shared | δ = 0, 1A | 5,242 | 0.0569 |
| 60034038 `mp1s1_proton_m1_1A` | shared | proton −1σ, 1A | 5,568 | 0.0604 |
| 60034995 `mp1s1_pack_g1` | regular (whole node) | 1M, 1L, 1B × 11 (33 steps) | 4,932 | 1.3700 |
| 60034996 `mp1s1_pack_g2` | regular | 1F, 1O, 1C × 11 (33 steps) | 3,725 | 1.0347 |
| 60034998 `mp1s1_pack_g3` | regular | 1N, 1P, 1A (31 steps; the two shared 1A passes skipped) | 2,200 | 0.6111 |
| 60034999 `mp1s1_pack_g4` | regular | 1D, 1G, 1E × 11 (33 steps) | 2,808 | 0.7800 |
| **event loops** | | 132 passes | | **3.913** |

- All 4 packed jobs and both shared passes are COMPLETED 0:0, and the packed logs say "passes done, rc=0" (33, 33, 31
  and 33 passes).
- 132 outputs exist, 12 per variant.
- **Steps** (coordinator's sacct summary; the per-step annex is `s1/sacct_evloop.txt` on the cluster, not copied
  before access was lost): all 148 job and step records are COMPLETED. Step ElapsedRaw runs 220–4,927 s and MaxRSS is
  ≤ 14,678,660K. That is the 14G cap, which counts page cache; no step was OOM-killed.

**Packing deviation, under the director's three conditions.** The approval was 8 passes per node at 16G; what ran was
33 per node at 14G.
1. Every step's State and MaxRSS were checked. Nothing failed and nothing was OOM, so nothing needed a rerun.
2. **No I/O slowdown was seen; the packed passes ran faster.**
   - Every packed pass ended within its node's job time, 2,200–4,932 s.
   - The 1M passes ran in at most 4,932 s, against 12,697 s for W2b's 1M on shared.
   - The 1A passes in g3 ran in at most 2,200 s, against 5,242 and 5,568 s for the two concurrent shared 1A passes.
     S0's 1A species passes on shared took 3,203–6,686 s.
   - Per-pass ElapsedRaw is in the cluster annex only.
3. The 04:00 PDT 10-21 rule was kept.

## Per-pass checks and G1 per playlist

- **G1, per playlist: PASS for all 12** (`s1/checks/g1/`). Each zero pass equals W2b's rrzero pass of its playlist
  under W2's `equal` rule, on the latest TTree cycles (`omnifile_io.py`).
- **Per-pass checks** (`check_species_pass.py`, 120 shifted passes, each against its playlist's zero pass;
  `s1/checks/species/`):
  - All unshifted branches, the pass flags and the data tree are identical in every pass.
  - The q0 shift never has the wrong sign. max |Δq0|/(δ·q0) = 1.071, which is F's local slope over its secant.
  - No pro-rata row has |ΔE| > δ·E.
  - The only flags are E_avail sign-rule rows: 1,382 in all. In every pass their count is ≤ the playlist's number of
    passing rows with E_avail < 0 (313 in all, 3–79 per playlist). That is the S0 mechanism: pro-rata moves negative
    NewEavail away from zero, and those rows lie outside the J grid.
  - Not read as failures.

## Merges, dumps, unfolds (last seen 2026-10-20 12:05 PDT)

- **Merges** (login node, W2b order; frozen deploy `e9372b75`): all 11 endpoints, about 4.84 GB each, under
  `s1/merged/`.
- **Dumps** (`s5p_input_dumps.py lateral`, deploy `c1cba7bf`, through its `s5c_array.sh`).
  - Shared had 7,019 pending jobs, so the dumps ran packed 4 per node on debug (approved under the same three
    conditions).
  - Jobs 60045768, 60045769 and 60045770 are COMPLETED 0:0, at 369, 353 and 363 s. The 11 steps ran 340–359 s with
    MaxRSS 20.9–21.0 GB against a 110G limit.
  - The 11 s5c tasks have rc = 0, and the 22 dump files exist.
- **Unfolds** (`s5p_numerics.py` R, 5 iterations, `--construction data --pairs=-:-`, deploy `4e4b4f56`, debug, 4 per
  node).
  - Jobs 60046417, 60046419 and 60046421 are COMPLETED 0:0, at 704, 709 and 722 s. The 11 steps ran 688–711 s with
    MaxRSS 17.3–17.8 GB against a 56G limit.
  - The 11 tasks have rc = 0, and the 11 products `s1/unf/mp1s1_<variant>_b-_j-.npz` exist.
- **Charges.** Debug nodes bill the whole node (sacct AllocTRES billing=256, confirmed on resumption): dumps 0.301,
  unfolds 0.593. **S1 total 4.81 CPU node-h**, ledger rows in `LEDGER-rows-mp1-s1.tsv`. Together with S0 that is about 5.2 of the
  phase-1 35.

## On resumption (2026-10-20 17:24 PDT)

- **Job state from sacct, recorded first.**
  - The queue is empty, and every phase-1 job is in a terminal state matching the ledger.
  - No job ran into the maintenance drain (10-21 06:00 PDT).
  - The 130 cancelled shared copies show ElapsedRaw 0.
- **Debug billing is confirmed.** sacct AllocTRES gives billing=256 for every debug job, so the whole-node assumption
  behind the dump and unfold charges holds.
- **Outputs are intact** on pscratch.
- **Per-step annex** copied to [`s1-receipts/sacct_evloop.txt`](s1-receipts/sacct_evloop.txt): 148 records (6 jobs, 6
  batch, 6 extern, 130 srun steps), all COMPLETED 0:0. Step ElapsedRaw runs 220–4,927 s.

## Unfold verification: PASS for all 11 tasks

Script `measurement-paper/phase1/mp1/verify_s1_unfolds.py` (sha256 `bd594178…`), login node, read-only. Receipt
[`s1-receipts/verify/unfold_verify.json`](s1-receipts/verify/unfold_verify.json).
- Each task's two lateral inputs still hash to the `--expect-*-sha256` in `tables/unfold-all.tsv`.
- Each s5c log, read in full, holds only:
  - the known sklearn feature-name warning pairs;
  - one result line with rc 0, naming the expected product;
  - the oi136 inventory receipt;
  - the s5c start and end lines, with rc=0.
- Each env.log is identical to W2b's. Both carry the same two missing optional setup scripts.
- Each inventory names the deploy's `s5p_numerics.py` by its on-disk sha256 (`7ad8ca0f…`), with an empty allow-list, the
  guard installed, and nothing outside the expected root.
- All 11 products load and are finite. Their sha256 are in the receipt (zero `f1d5178a…`, …).

## G3: FAIL for em and other

Run on the login node with the frozen `mp1_s2.py g3` (`ff2f79ec…`) and the frozen design (`404446eb…`, deploy
`e9372b75`). Receipt [`s1-receipts/g3/g3.json`](s1-receipts/g3/g3.json) (sha256 `3487bbd6…`).

The gate: ‖f(+1) + f(−1) − 2f(0)‖₂ ≤ 0.2 ‖f(+1) − f(−1)‖₂ over each null's J domain, with f = U x of the real-data
unfolds.

| species | role | curvature norm | span norm | ratio, all 109 | ratio, GiBUU p∥ < 6 | median \|half-span\|/f0 | G3 |
|---|---|---:|---:|---:|---:|---:|---|
| proton | primary | 2.30e-41 | 1.34e-40 | 0.172 | 0.157 | 1.0% | PASS |
| meson | primary | 2.35e-41 | 2.26e-40 | 0.104 | 0.106 | 1.5% | PASS |
| em | primary | 2.19e-41 | 8.84e-41 | **0.248** | **0.258** | 0.5% | **FAIL** |
| other | primary | 1.90e-41 | 7.87e-41 | **0.241** | **0.250** | 0.6% | **FAIL** |
| xtalk | R3 variant | 1.71e-41 | 5.64e-41 | **0.302** | **0.318** | 0.5% | **FAIL** |

**Consequence (frozen).** S2 stops if any species fails, so S2 and S3 were not run. The designs were not built and no
band was evaluated.

**Descriptive diagnostic, not a re-reading of the gate** ([`s1-receipts/g3/g3_diag.txt`](s1-receipts/g3/g3_diag.txt)):
- **The curvature norm is nearly constant across species** (1.7–2.3e-41) while the span varies 4×. The three failures
  are the three smallest spans.
- **W2b's own band** (rr0/rr1 around rrzero) has curvature 4.0e-41 against span 4.8e-40 (ratio 0.084), a curvature of
  the same order.
- **Identical inputs reproduce exactly.** The MP-1 zero lateral dump is bitwise W2b's rrzero dump; its bkg arrays are
  bitwise equal, with only the `meta` string differing. The MP-1 zero unfold equals W2b's rrzero unfold in U space,
  with difference norm 0.
- **Reading, as first sent to the director.** The pattern seemed to fit a floor of unfold response to perturbed inputs
  better than a physical nonlinearity. The noise-floor study below has **refuted this reading in its training-seed form**:
  the unfold is seed-invariant, so the curvature is deterministic. Its other form, a non-smooth response to small input
  changes, has not been tested.

## The director's ruling on G3 (2026-10-20; binding addendum 10)

1. **G3 is recorded as FAIL** for em and other, with proton and meson PASS; the xtalk variant also fails.
   - Under PLAN §2.3, **MP1-A is not reported as a calibrated result**: no band and no decision.
   - S2 and S3, the designs and evaluation of all five nulls and the independent recompute, are **not run**.
   - MP1-A-full is priced below, as the rule requires.
2. **A descriptive noise-floor study** is approved (§ "Noise-floor study"). It cannot revive MP1-A.
3. **A descriptive partial S2** is approved, with only the two bands that passed (§ "Partial S2"). It carries the label
   "not the MP-1 result; species restricted after the G3 outcome; post hoc".

## Noise-floor study (DESCRIPTIVE; no gate, no re-gating)

**What was declared.** The design is in `measurement-paper/phase1/mp1/noisefloor/DECLARATION-noisefloor.json` (sha256
`8e02bc44…`, recorded 00:34Z, before any submission):
- K = 5 estimator seeds, 1001–1005, for each of zero, em±1σ and other±1σ;
- the S1 all-playlist lateral dumps, re-verified by sha;
- the S1 unfold command, unchanged except for `--estimator-seed` (S1 used 42);
- the readout fixed in the file.

**How it ran.**
- Jobs 60063770–60063774 on regular, so that debug stayed free for the director's re1 jobs (the director agreed). One
  node per seed, 17:36–17:48 PDT, all COMPLETED 0:0, about 700 s each. Total 0.972 CPU node-h, under the 4 node-h cap
  and well before the 04:00 PDT cutoff (the director's; the declaration's 05:30 was superseded).
- The verifier (now taking a table and a count; `080a49da…`) passes for all 25 tasks
  (`noisefloor-receipts/verify_nf.json`). Each product's meta records its own seed.

**Result** ([`noisefloor-receipts/noisefloor.json`](noisefloor-receipts/noisefloor.json), sha256 `4d48d7fc…`):

| species, domain | G3 curvature (seed 42) | curvature at seeds 1001–1005 | seed-noise expectation N | curvature / N |
|---|---:|---:|---:|---:|
| em, all 109 | 2.193e-41 | 2.193e-41 (all five) | 1.1e-54 | ≈ 2e13 |
| em, GiBUU p∥ < 6 | 2.007e-41 | 2.007e-41 (all five) | 5.5e-55 | ≈ 4e13 |
| other, all 109 | 1.896e-41 | 1.896e-41 (all five) | 9.7e-55 | ≈ 2e13 |
| other, GiBUU p∥ < 6 | 1.721e-41 | 1.721e-41 (all five) | 4.9e-55 | ≈ 4e13 |

- **The seed scatter is at float-rounding level.** The median per-cell relative SD of the δ = 0 control is exactly 0,
  and the spans agree to four digits at every seed. The seed-mean G3 form reproduces S1's ratios (0.248 and 0.241),
  as it must when the seed has no effect.
- **Why the seed has no effect** (read from the deploy's code, 4e4b4f56):
  - The estimator runs LightGBM with `deterministic=True`, `force_row_wise=True`, no bagging and no feature
    subsampling, and `bin_construct_sample_cnt` = all rows (`s5c_unfold.config_params`, `omnifold_nn_core.make_estimators`).
  - So `random_state` has nothing to randomize, and the data construction draws no other random split.

**Reading.**
- **Training-seed noise is ruled out as the cause of the G3 failure.** The curvature is a deterministic property of how
  the unfold responds to the shifted inputs.
- That means **my earlier "noise floor" reading is refuted in its seed form.**
- The study cannot separate the two remaining explanations:
  - a physical nonlinearity of the em and other responses;
  - a deterministic but non-smooth response of the binned tree estimator to small input changes. The histogram bin
    edges are built from all rows, so shifting rows moves them.
  - The second is a hypothesis only; it has not been tested.
- **The declared ratios divide by a quantity at rounding level, so they carry no information beyond curvature ≫ N.**

## Partial S2: proton and meson only (DESCRIPTIVE)

**Label, required by the ruling:** "not the MP-1 result; species restricted after the G3 outcome; post hoc".

**CITABLE FOR:** how the ten A7 decisions respond to the two G3-passing species bands alone, beside A7.

**NOT CITABLE FOR:** an MP-1 result, a calibrated species band, or any claim.

**How it was run.** Login node, 0 node-h, 2026-10-21 00:37–00:41 UTC.
- Runner `measurement-paper/phase1/mp1/partial/run_partial.sh` (`bd27fe83…`); builder and comparison
  `mp1_s2_partial.py` (`ecb3e2c8…`). Receipts are in [`partial-receipts/`](partial-receipts/).
- The machinery is S2/S3's, frozen in `tools-v3`: `s5p_joint_mp1` evaluate, `s5p_robust_labels`, then
  `s5p_recompute_mp1` evaluate and compare.
- The design copy is built the way `mp1_s2.py designs` builds the primary copy, but with only proton (i_s = 1) and
  meson (i_s = 2). The z key is 0x4D31, and the endpoints are the S1 unfolds. The key diff holds only the species
  additions (`design-mp1-partial_pm.json.keydiff.json`).

**Controls.**
- **The unmodified frozen design, evaluated in the same run, reproduces A7's `decisions`, `decisions_robust_kappa` and
  `holm_point` bitwise** (`joint-evaluate.json` sha256 `b9604502…`).
  - In `tests`, every non-float leaf is equal.
  - 131 of 932 float leaves differ in the last digits, at most 6.4e-12 relative. The worst leaf is a difference
    quantity, `median_shift_in_null_sd`.
- **The independent recompute of the partial design AGREEs** with the partial evaluate: 1,379 of 1,379 items.

**Result. No decision moves.** All ten tests stay "rejected", in both the frozen family and the κ = 3 robust family
(`partial-vs-A7.json`).

| test | A7 p (k) | partial p (k) | null SD, partial / A7 | (T − median)/SD, A7 → partial |
|---|---:|---:|---:|---:|
| MnvTune total | 7.3e-4 (0) | 7.3e-4 (0) | 6.15 | 206.8 → 33.2 |
| MnvTune shape | 7.3e-4 (0) | 7.3e-4 (0) | 3.98 | 39.6 → 9.4 |
| GENIE CV total | 7.3e-4 (0) | 7.3e-4 (0) | 1.32 | 22.0 → 16.5 |
| GENIE CV shape | 7.3e-4 (0) | 1.46e-3 (1) | 1.11 | 5.30 → 4.55 |
| GENIE MEC total | 7.4e-4 (0) | 7.4e-4 (0) | 1.46 | 32.1 → 21.6 |
| GENIE MEC shape | 7.4e-4 (0) | 1.49e-3 (1) | 1.17 | 6.19 → 5.04 |
| NuWro total | 5.7e-4 (0) | 5.7e-4 (0) | 1.15 | 6.33 → 5.41 |
| NuWro shape | 1.14e-3 (1) | 5.7e-4 (0) | 1.01 | 2.86 → 2.81 |
| GiBUU total | 7.4e-4 (0) | 7.4e-4 (0) | 1.27 | 12.1 → 9.5 |
| GiBUU shape | 7.4e-4 (0) | 7.4e-4 (0) | 1.03 | 6.83 → 6.59 |

- **The median-based column is not a decision-boundary margin.** The boundary margins of
  [`../a7margins/RECEIPT.md`](../a7margins/RECEIPT.md) were not recomputed for the partial nulls.
- **T_obs is unchanged** (bands act on the nulls only). The null widens most for MnvTune, whose A7 null is the
  narrowest.
- **NuWro shape's single exceedance in A7 is absent here.** With the z draws, individual pseudo-experiments move both
  ways, so k can fall when a band is added.

## MP1-A-full, priced (PLAN §2.2 rank 3: event-level response-varied nulls)

**What it is.** Each frozen pseudo-experiment draws z_s per species and builds its pseudo-data from the shifted source
rows. This needs a new `s5p_nullexp` mode, and every pseudo-experiment is re-unfolded. The linear surrogate that G3
tests is therefore never used.

| component | basis | CPU node-h |
|---|---|---:|
| endpoints (species-shifted rows) | the S1 event-loop outputs and lateral dumps exist and are reusable, so nothing new is needed unless the species set changes | 0 (4.81 already spent) |
| development and admission of the new mode | s5p's development 23.93 plus stage-3 design and repair 14.48 (`DELIVERY-20261006-s5p-campaign-terminal.md` §4) | 15–40 |
| production: five nulls at the frozen B (1,343–1,751 pseudo-experiments each), the same estimator and iterations | s5p production **207.90**, measured | ≈ 208 |
| verification and repair | s5p used 6.89 of the 68.29 it was allocated | 7–70 |
| **total** | | **≈ 230–320** (PLAN's estimate was 215–290) |

- **GPU:** 0.
- **Wall time.** At s5p's 2-node concurrency cap, production alone is about 104 h, so roughly a week with development.
- **Budget.** About 6.5–9× the phase-1 ceiling of 35 CPU node-h. It needs a new budget decision; this session has not
  started it.
- **Design consequence.** The noise-floor study found no training-seed noise, so a seed-averaged MP1-A would change
  nothing, and that cheap redesign is closed.
  - MP1-A-full replaces the linear surrogate. So whichever cause holds, physical nonlinearity or a non-smooth estimator
    response, it enters each pseudo-experiment's calibration rather than failing a gate.
  - The two causes would still read differently: a non-smooth response would be estimator structure carried into the
    nulls, not hadronic physics.
  - The design choice belongs to the director.

## UNCONFIRMED (S1)

- G0 holds on selected-like events only. See the selection-handling note above.
- The cause of the G3 failures is unmeasured. Training-seed noise is ruled out; physical nonlinearity and a non-smooth
  estimator response remain.
