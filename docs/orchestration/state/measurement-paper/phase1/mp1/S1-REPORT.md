# MP1-A S1–S3: report (PARTIAL: stages after the unfolds deferred)

**Status, 2026-10-20 16:05 PDT.** The S1 event loops, merges, lateral dumps and data unfolds all completed. Unfold
verification, G3, S2 and S3 are NOT done: cluster access was lost when the NERSC certificate expired at 15:04 PDT
(renewal is Joseph's act). No band number and no decision exists. On resumption, the state of every job is recorded
from sacct first, and any job the maintenance drain killed is treated as failed, never as a result (the director, 2026-10-20).

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
- **Charges.** Assuming exclusive debug nodes bill the whole node (AllocTRES not captured): dumps 0.301, unfolds 0.593.
  **S1 total 4.81 CPU node-h**, ledger rows in `LEDGER-rows-mp1-s1.tsv`. Together with S0 that is about 5.2 of the
  phase-1 35.

## NOT DONE, DEFERRED: cluster access was lost (the NERSC ssh certificate expired at 15:04 PDT; renewal is Joseph's act)

1. **Unfold verification**: product digests against the table, the s5c inventories, and the steps' logs read in
   full.
2. **G3** (linearity per species and per null domain, tolerance 0.2). It is to be sent to the director **before any S2
   number**; S2 stops if any species fails.
3. **S2**: design copies and `s5p_joint_mp1` evaluate of all five nulls, primary plus the cross-talk variant.
4. **S3**: `s5p_recompute_mp1` and compare, which must AGREE.

**On resumption** (after access returns, or after the maintenance of 10-21 06:00 to 10-27 23:00 PDT):
- Steps 1–4 are login-node work, 0 node-h: about 1 min for G3 and about 2–3 min per design for S2 and S3, measured on
  the code test. The scripts are prepared.
- First re-confirm that the pscratch outputs survived the maintenance (purge policy), and check every digest against
  the tables before reading anything.
- **Not touched:** no G3 or S2 number exists, and no decision has been computed.

## UNCONFIRMED (S1)

- Debug billing is assumed to be the whole node, and the ledger start/end times were not captured; both were left in
  sacct on the cluster.
- The per-step sacct annex (130 event-loop steps, 22 dump and unfold steps) is on the cluster only:
  `s1/sacct_evloop.txt` and sacct.
- G0 holds on selected-like events only. See the selection-handling note above.
