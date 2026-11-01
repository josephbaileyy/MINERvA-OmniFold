# ASSESSMENT — the price of switching truth E_avail's charged-pion term from 135 MeV to 139.57 MeV

**Filed 2026-10-31 by the session `coverage-5b-audit`, for the director, under
[`DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md`](DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md)
item 1.** Joseph's answer was "Price a switch to 139.57". UD-002 is reopened for pricing, not reversed, and 135 MeV
stays the defined constant until Joseph decides. The director takes this to an independent read before Joseph.

**Measured at** `origin/main` = `c7c3ab210dd347d8ca8fdbd4118ff3b332f59d27`. Every `file:line` is at that commit.

**MEASURES:**
- every code site that sets the charged-pion term of truth E_avail;
- which committed products depend on it, and the rerun each needs;
- the measured walls and node-h of the runs that made them, with what is not measured;
  <!-- absence-ok: scoping statement of what this record measures; the unmeasured items are scoped to the Search line in §3.1 -->
- a per-charged-pion size estimate on the 16 reported cells and the fine E_avail bins, from committed arrays only;
- the records, macros, figures and text a switch would change.

**CANNOT AUTHORIZE:**
- the switch itself. That is Joseph's decision (UD-002);
- any job, connection, storage action or code change. No cluster was contacted;
- any change to the paper, the note or a register.

**CITABLE FOR:** the site list, the dependency map, the cost table as sourced, and the committed-array estimate with
its stated assumptions.

**NOT CITABLE FOR:**
- the effect of the switch on the 16 cells. §4's numbers are a per-charged-pion first-order estimate under named
  assumptions, which span a factor of about 3 between them, and they are not a measurement;
- the cost of the steps marked *unmeasured*.
  <!-- absence-ok: scoping statement; "unmeasured" is scoped to the Search line in §3.1 -->

**How it was done.** Read-only.
- Two delegated searches (the measured walls; the downstream records and text) were spot-checked line by line against
  the ledgers and sources they cite.
- §4 is arithmetic on committed arrays on the session's own machine, with its script and output committed
  (`state/eavail-switch-pricing-20261031/`). No cluster was contacted.

---

## 0. Summary

**What the switch is.** For every simulated event, truth E_avail falls by **4.57 MeV × n_π±**, the number of
final-state charged pions. Since E_π − 139.57 = (E_π − 135) − 4.57, it is an exact per-event shift.
- Reco E_avail and the data do not change: the reco side is calorimetric (`NewEavail`), not `GetEAvailableTrue`.
- The 2D result does not use E_avail (§2).

**Where it enters:** seven constant sites, in one event-loop function and six generator converters (§1).

**What it touches:**
- every result on an E_avail axis: the 16-cell 5D result and all its covariance blocks, including C_PL,5D;
- the 3D and 4D central values that the paper prints;
- Stage G's predictions, the fake-data studies, the flux bootstrap and 1B;
- E_avail-binned validation studies that the paper also prints: the joint test, and the closure figures.

**What it costs, if no event loop is rerun:** about **15 node-h of CPU**, measured, for the 16-cell result, its
covariance and the 3D/4D central values. The cap total is about **35**, with no GPU (§3).
- Three dumps have no measured wall.
- **This route depends on the stored per-event truth.** The event-loop ROOT files carry `MC_eavail` and the
  charged-pion count `MC_npip` on every row of both truth trees, so the shift can be applied at the dump.
- **Those files are at risk:** the per-playlist 5D universe event loops become exposed to pscratch purge from
  **2026-11-09**, and their merge from 2026-11-22. Neither is on HPSS or CFS (`FD-CT-RETENTION.md:64-65`).
- If the files are lost, the event loops must be rerun, and their CPU cost is not on record.

**Optional, priced separately:**
- re-making the A7 calibration and power products, which back F0's grade and the joint test: **207.9** node-h measured;
- completing 1B on the new definition.

**Size before any rerun (§4).** From committed fine-grid unfolded arrays:
- **per charged pion,** the 11 cells that border E_avail = 0.8 GeV move by **0.1–1.9 %**, which is **up to 0.32 σ** of
  the reported uncertainty, in R06;
- the other five cells (R01, R05, R09, R13, R14) do not move;
- the result scales with the unknown charged-pion multiplicity near 0.8 GeV. Two density models differ by up to about
  3×.

**An exact prior-level number costs minutes on a login node** (§4.3).

**Recommendation (§6):**
1. First, measure the exact size (step 0, read-only, no node-h). It needs the director's leave to connect.
2. Decide now whether to keep the event-loop files past 2026-11-09, since that keeps the cheap route open.
3. Then let Joseph choose between two options:
   - keeping 135 with the departure sentence, quoting the measured size;
   - a **scoped switch**: the 16-cell result, its covariance, Stage G and the 3D/4D central values on 139.57, with the
     validation studies labelled as on 135.

## 1. Where 135 enters: every code site that sets the charged-pion term

**The search:**
- `git grep -n '135'` over `*.py *.h *.C *.cxx *.cpp *.cc`, filtered to pion, E_avail or mass lines;
- `git grep` for `GetEAvailableTrue`, `eavail_true`, `MASS_PI_PM`, `MASS_PI`, `MPI` and `M_PION_EAVAIL`, and for every
  importer of `genie_to_xsec3d`.

| # | site | role | constant | its use |
|---|---|---|---|---|
| 1 | `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:364` | the event loop's `GetEAvailableTrue()` (`:361-374`) | `double mass_pion = 135;` (MeV) | `:369`. The loop stores it as `MC_eavail` at `runEventLoopOmniFold.cpp:589` (signal) and `:1140` (truth denominator). Every dump, unfold input, MP-1, W2 and 5B event loop builds on it |
| 2 | `3d-unfolding/genie/genie_to_xsec3d.py:42` | GENIE `eavail_true` (`:47-55`) | `MASS_PI_PM = 0.135` (GeV) | `:53`. Imported by `gen_to_xsec5d.py:57,98` (the Stage G and C_model generator grids, injected into C++ at `:90-98`), `gen_to_xsec_eavailW.py:37`, `genie_mec_to_xsec3d.py:41`, `fsi_variation_xsec3d.py:35` and `mode_decomp_eavail.py:41` |
| 3 | `3d-unfolding/genie/nuwro_to_flat_5d.C:44` | the NuWro 5D flattener | `const double MPI = 0.135` | `:65`. It is baked into the flat files that `gen_to_xsec5d.py` reads |
| 4 | `3d-unfolding/genie/nuwro_to_flat.C:31` | the NuWro 3D flattener | `MPI = 0.135` | `:52` |
| 5 | `3d-unfolding/genie/gibuu_to_xsec3d.py:53` | GiBUU 3D | `MASS_PI = 0.135` | `:113` |
| 6 | `3d-unfolding/genie/gibuu_to_xsec_eavailW.py:38` | GiBUU (E_avail, W), also used by `gen_to_xsec5d.py` | `MASS_PI = 0.135` | `:81` |
| 7 | `nd-unfolding/pet/pointcloud_projection.py:51` | the PET cloud projection (not on the reported path) | `M_PION_EAVAIL = 135.0` | `:109`. `M_PI = 139.57` sits four lines below. `docs/EAVAIL_DEFINITION.md` §3 warns that setting both to 139.57 hides the distinction, so rename or comment |

**`docs/EAVAIL_DEFINITION.md:135-141` lists six sites; this list has seven,** because NuWro has two flatteners (sites 3
and 4).
- Sites 2, 3, 5 and 6 are bound to `CVUniverse` by comment ("match CVUniverse") or not at all.
- They must move in one commit with site 1, or the generator comparison compares two observables.

**Not production sites:** research scripts that restate the rule under `docs/orchestration/state/` (for example
`inelastic-high-region-20261011/code/r5_genie_events.py:38`, `valencia-feasibility-20261011/code/analyze_dump.py:23`).

**Python recomputation and controls that would need to follow:** MP-2's `mp2_s1_dump.py:118` re-derives MAT's
function for its join control, and `gen_to_xsec5d.py:181` checks against `eavail_true`. Neither is a reported product.

## 2. Which products depend on it, and what each needs

**The shift acts on MC truth coordinates only:**
- `MCgen` column 2 and the completeness denominator `denom_nd` of each unfold's inputs (`nn_dump_inputs.py:84,89-90`);
- the universe bank's truth and truth-denominator coordinates (`s5p_universe.py:3-25`; row alignment is checked
  against the npz);
- the generator grids.

Reco coordinates, data and weights are unchanged. The unfold changes in two ways:
- **directly,** events cross fine E_avail edges, of which only 0.8 GeV bounds the 16 cells (`s5p_stage1_inspect.py:41,47`);
- **at second order,** step 2 trains on the shifted truth feature.

| product | depends? | what it needs |
|---|---|---|
| **2D result** (p_T, p∥) | **no** | Nothing. The 2D unfold reads no truth E_avail: `unfold_2d_omnifold_unbinned.py` has no `avail` term but "unavailable", and the FPS launcher passes `--axes ""` (`nd-unfolding/sbatch_unfold_active_fps.sh:56-61`). The 2D C_model integrates the generators over the whole E_avail axis (`2d-unfolding/pv2d/make_ratios.py:5-13`), which no relabelling changes. That last point is reasoned, not measured. **One adjacent number moves:** the 3D marginal's 0.141 % agreement with 2D (`paper_body.tex:122`), via the 3D rerun |
| **3D and 4D central values** (printed without uncertainties, `paper_body.tex:264`; `sec_3d.tex`) | yes | re-dump plus re-unfold (RE-1) |
| **16-cell result: C_stat, C_seed, the universe bands, the laterals** (S1) | yes | re-dump of `of_inputs_5d.npz`, the bank's truth coordinates, the detector dump and the lateral dumps; all S1 unfolds; S1 assembly |
| **C_model** (L-5D-PV) | yes, twice | the generator grids (§1, sites 2–6) and the prior-variation unfolds |
| **C_resp** (MP-1) | yes | MP-1 dumps and unfolds, then `build_cresp.py` |
| **C_PL,5D** (5B) | yes | 5B job A (merges, dumps, ALL unfold) and job B (33 period unfolds), then the 5B readers and the addition chain |
| **Stage G, G-DIAG, G-FOLLOWUP, G-SENS2, the flux bootstrap, figures, data product, deposit** | yes | login-node reruns on the new inputs, plus the generator grids for Stage G |
| **F0b, F1** (fake data) | yes | F1's pseudo-data (F1a, F1b′ reconversion, F1c unfolds). F0b re-grades A7 products, so a consistent F0b needs A7 (optional row) |
| **1B** (running, no report yet) | yes | its stage 2 on the new inputs |
| **CT-3b closures** | yes | 13 closures |
| **Joint test** (`values_inference.tex`; `\jtNcells` at `paper_body.tex:41,70`) and **closure figures** (`paper_fig_bkg_residual`, `paper_fig_deformation`, `paper_body.tex:130,142`) | yes (fine grid with 7 E_avail bins) | A7 products (optional row). **The two figures' producers are not in the tracked tree** (`state/2d-closeout/stageF/figure-diagnosis-20261030/FIGURE-DIAGNOSIS-REPORT.md:233-234`), so they cannot be regenerated as things stand |
| **Scalar-5D adopted covariance** (`values.tex:182-221`) and **PET** (`values.tex:101-130`) | yes | **not priced here.** Neither is on the director's list. The note prints both (`sec_5d`, `sec_pet`) |

## 3. The rerun plan, job by job

Sources are the ledgers and reports cited in each row, spot-checked. Node-h are as billed; *derived* marks arithmetic
on recorded figures.

**No GPU is needed.** Every unfold and dump below ran on CPU nodes.

### 3.1 Route A: no new event loop

The shift is applied at the dump, from each event loop's own `MC_eavail` and `MC_npip`:
- **The branches:** `MC_npip` is written in the signal tree (`runEventLoopOmniFold.cpp:437,593`) and in the truth
  denominator (`:642-643,1144`), and has been since `eb344265` (2026-06-06).
- **On the universe omnifile:** MP-1's receipt lists it among the 5D universe omnifile's `mc_signal_reco` columns
  (`state/measurement-paper/phase1/mp1/receipts/checks/r4_prod_vs_base_cv.json`).
- **Why it equals the switch:** `MC_npip` counts π± with E − 139.57 > 0 (`CVUniverse.h:257-265`). So
  `MC_eavail − 0.00457 × MC_npip` equals the event loop with 139.57 for every pion except one with stored E ≤ 139.57
  MeV.
- **A control for that pion:** MP-2's particle-level join (`mp2_s1_dump.py`; its admission requires bitwise equality
  with `MCgen`) can count such pions on the analysis rows.

| step | what | measured | node-h | cap | source |
|---|---|---|---:|---:|---|
| A0 | code: the seven sites (§1) and a dump-side shift with its control | — | 0 | — | — |
| A1 | re-dump `of_inputs_5d.npz` (MCgen, denominator) | **unmeasured.** Analogue: 5B's ALL `nn_dump` lane, 7:12 on a shared node | — | 4:00 declared | `sbatch_nn_dump_5d.sh:4`; `FD-CT-5B-REPORT.md:84-94` |
| A2 | re-dump the universe bank's truth coordinates (`sweep_bank_5d.py --dump`) | **unmeasured** | — | — | `S1-DECLARATION.md:180` |
| A3 | detector dump | one of two jobs (58947238, 58953705) | 0.152 or 0.158 | — | `state/s5p` meter records |
| A4 | lateral dumps (9) | 710 s mean, derived | 0.430 | 2.18 | `state/s5p/diag/meter-measure-batch1-report-20260930T1947Z.json:186` |
| A5 | S1: pilot, P1, P2, seed (256 unfolds) | jobs 722 / 7,232 / 7,226 / 6,570 s | **6.042** | 15.5 | `5d-community-20261024/s1/LEDGER.tsv:2-5` |
| A6 | S1 set A, 50 replicas; the (e) CV | unfold 638–667 s each | ≤ 2.593 (whole allocation) | 4.0 | `state/s5p/stage2/meter-measure-stage2-exit.json:51-61` |
| A7 | 10 lateral unfolds | 967 s mean, derived | 0.336 | 1.25 | meter `:234` |
| A8 | MP-1: dumps, 11 unfolds | jobs 353–369 s; 704–722 s | 0.301 + 0.593 | not committed | `phase1/LEDGER.tsv:31-36` |
| A9 | generator grids (GENIE CV, GENIE+MEC, NuWro, GiBUU, Tune v1) | login, "15-140 s" per build | 0 | — | `state/s5p/gen5d/README-gen5d-build.md:152-154`. Needs the raw samples; NuWro needs re-flattening (site 3) |
| A10 | L-5D-PV: J5 and J1 | 811 s; 861 s | 0.225 + 0.239 | 0.42 + 0.5 | `measurement-scoping/pv-ladder/LEDGER.tsv:4,8` |
| A11 | 5B jobs A and B | 2,078 s; 1,149 s | 0.577 + 0.319 | 1.0 + 1.5 | `5d-community-20261024/fd/LEDGER.tsv:50,52` |
| A12 | F1: F1a, F1b′, F1c | 377 s; 1,116 s; 2,193 s | 0.105 (derived) + 0.310 + 0.609 | 2.5 | `FD-F1-REPORT.md:125-195`; `fd/LEDGER.tsv:20-31` |
| A13 | RE-1: 3D and 4D central values | 428 s; 913 s | 1.627 (run total) | 6.0 | `state/2d-closeout/stageF/methods/re1/run2/ledger.tsv:2-3` |
| A14 | CT-3b closures (13) | 26:08 | 0.436 | 0.75 | `FD-CT-3B-REPORT.md:36-64` |
| A15 | the login chain: S1 assembly, C_resp, C_model, Stage G, G-DIAG, followups, flux bootstrap, F0b re-grade, 5B readers, addition chain, data product, deposit, figures | seconds each (the addition chain 273 s) | 0 | — | `fd/LEDGER.tsv` |
| A16 | values macros, supplemental CSVs, note and paper rebuild | — | 0 | — | §5 |
| | **total measured, A3–A14** | | **≈ 14.9** (derived) | **≈ 35** | plus A1 and A2, unmeasured |
Search: measured wall or node-h for the `of_inputs_5d.npz` dump, the universe-bank dump and the 5D, lateral and 5B event loops, over every `LEDGER.tsv`/`LEDGER.psv` under `docs/orchestration/state/`, the FD-*, S1-, MP-1, RE-1 and CT reports, the `state/s5p` meter records and `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md` @ c7c3ab21

**Optional rows:**

| step | what | node-h | source |
|---|---|---:|---|
| O1 | A7 calibration and power products, for F0's grade and the joint test | **207.899** measured (shared arrays of 34 tasks, 2.0 h each) | `DELIVERY-20261006-s5p-campaign-terminal.md:102`; `state/s5p/prod/queues/pow.q:2` |
| O2 | 1B stage 2 on the new definition | 5.261 spent so far; 2a-r 1.0, 2b 5.0 and 2c 9.0 capped, not yet run | `fd/receipts-1b/stage2/LEDGER.psv:2-5` |
| O3 | the scalar-5D adopted covariance and PET | not priced | — |

**Wall time and order.** The critical path, without queue waits:
1. A1–A4, the dumps: unmeasured, about an hour by the analogue.
   <!-- absence-ok: "unmeasured" is scoped to the Search line under the cost table above -->
2. A5–A14 in parallel. The longest job is S1's P1 at 7,232 s.
3. A15, minutes.
4. A16.

That is about three to four hours of compute plus queue time, which cannot be estimated. A5's four jobs ran
concurrently before.

### 3.2 Route B: if the event-loop files are gone

**The files the shift is applied to:**
- the 5D omnifile behind `of_inputs_5d.npz` (`runEventLoopOmniFold_5D_MEFHC.root`, `b6d2651c…`, per `mp2_s1_dump.py`);
- the 12 per-playlist universe loops and their merge;
- the lateral, MP-1 and 5B period loops.

**Their retention:**
- The per-playlist universe loops are exposed from **2026-11-09** and their merge from **2026-11-22**. Only a
  non-`bkgaware` merge is on HPSS (`FD-CT-RETENTION.md:64-65`).
- The MP-1 loops are exposed from 2026-12-15 (`:63`).
- I found no retention entry for the 5D omnifile, `of_inputs_5d.npz` or the bank in the retention records searched
  (`FD-CT-RETENTION.md`, `RECORD-20261030-director-pscratch-retention-additions.md`,
  `FD-PSCRATCH-RETENTION-PROPOSAL.md`). Their state is unknown without an `ls`.

**If they are lost, Route B adds the event loops:**
- MP-1's measured **3.913** node-h for 132 CPU passes (`phase1/LEDGER.tsv:25-30`);
- the 12 universe loops and merge, **with no measured wall**. The only figure is a status log's "about 3 h on 3 GPU
  nodes", with no sacct (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:554,563`). A CPU pilot would have to measure
  it;
- the lateral and 5B period loops, also unmeasured.
  Search: measured wall or node-h for the `of_inputs_5d.npz` dump, the universe-bank dump and the 5D, lateral and 5B event loops, over every `LEDGER.tsv`/`LEDGER.psv` under `docs/orchestration/state/`, the FD-*, S1-, MP-1, RE-1 and CT reports, the `state/s5p` meter records and `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md` @ c7c3ab21

## 4. The size, before any rerun

### 4.1 What committed information allows

**No committed record gives the charged-pion multiplicity as a function of E_avail.** The one recorded figure is a
mean over all signal events: 1.0563 π± per event, giving 4.827 MeV per event, with 439 of 65,911 events changing truth
bin and the worst bin +1.049 % (`OPEN_ITEMS.md:159`, OI-30(c); `EAVAIL_DEFINITION.md` §3). That record does not
identify its binning or its sample beyond the count, so it is not the 16-cell number.

**What is committed** is the fine-grid unfolded data (`xsec_flat`, 65,856 cells) for 20 bootstrap replicas at seed 42
(`5d-community-20261024/s1/readout/s1_assembly/data_b*_j*.npz`). From those, the script
`state/eavail-switch-pricing-20261031/bracket_16cell.py` (`752135ab…`; output `bracket_16cell.txt`, `b0139e26…`)
estimates the first-order move. Its assumptions:
1. **The density inside the fine bin [0.8, 1.5) GeV**, which every 16-cell boundary at 0.8 GeV borders, is taken two
   ways:
   - (a) uniform;
   - (b) linearly interpolated at 0.8 between the two adjacent bins' mean densities.
2. **Exactly one charged pion per event at E_avail ≈ 0.8 GeV.** Everything scales linearly with the true conditional
   multiplicity, which is unknown here.
3. **The unfolded result moves as its truth coordinate does.** The step-2 retraining effect is neglected.

The operand is the mean of the 20 committed replicas. Cells are mapped by the committed definition (`b6790761…`) through
`s1_assemble.fine_map`.

### 4.2 The estimate, per charged pion

Positive means the cell gains. σ is the reported relative σ of C_total + C_resp (`fd_data_product.json`).

| cell | (a) uniform | (b) interpolated | σ | (a)/σ | (b)/σ |
|---|---:|---:|---:|---:|---:|
| R00 | +0.187 % | +0.306 % | 7.10 % | +0.03 | +0.04 |
| R02 | −0.648 % | −1.418 % | 14.00 % | −0.05 | −0.10 |
| R03 | −0.468 % | −0.243 % | 12.64 % | −0.04 | −0.02 |
| R04 | +0.106 % | +0.229 % | 4.20 % | +0.03 | +0.05 |
| R06 | −0.652 % | **−1.872 %** | 5.89 % | −0.11 | **−0.32** |
| R07 | −0.480 % | −0.247 % | 7.98 % | −0.06 | −0.03 |
| R08 | +0.468 % | +0.604 % | 6.25 % | +0.07 | +0.10 |
| R10 | −0.624 % | −0.939 % | 8.59 % | −0.07 | −0.11 |
| R11 | −0.288 % | −0.186 % | 13.69 % | −0.02 | −0.01 |
| R12 | +0.319 % | +0.537 % | 6.63 % | +0.05 | +0.08 |
| R15 | −0.622 % | −1.046 % | 7.94 % | −0.08 | −0.13 |

R01, R05, R09, R13 and R14 do not move: no 0.8 GeV edge bounds them inside the reported cells. Under (a), the total
moved is 0.081 % of the 16-cell sum.

**The fine E_avail bin populations,** under (a), summed over reported fine cells:

| bin (GeV) | share | net change per π± |
|---|---:|---:|
| [0, 0.1) | 6.84 % | **+4.39 %** |
| [0.1, 0.2) | 6.57 % | −0.35 % |
| [0.2, 0.4) | 12.14 % | −0.75 % |
| [0.4, 0.8) | 16.30 % | −0.45 % |
| [0.8, 1.5) | 17.39 % | −0.30 % |
| [1.5, 3) | 20.27 % | −0.30 % |
| [3, 100) | 20.48 % | −0.005 % |

**Read it at its strength.**
- The two density models differ by up to about 3× (R06).
- Assumption 2 is wrong in opposite directions at the two ends: there are fewer than one π± per event at the lowest
  E_avail, which inflates the +4.39 %, and plausibly more than one near 0.8 GeV.
- So this bounds the scale, about 0.1–2 % per pion on the cells and up to about 0.3 σ, and nothing finer.

### 4.3 What an exact number would take

**A login-node read,** minutes and 0 node-h, with no Slurm:
- **inputs:** the 5D omnifile's `mc_signal_reco` and `mc_truth_denom` trees (`MC_eavail`, `MC_npip`, the truth
  coordinates, `w_truth`);
- **output:** the exact prior-level population of each 16-cell and fine E_avail bin under both constants;
- **plus,** MP-2's per-row particle lists to count the π± with E ≤ 139.57 MeV.

**That is the full effect at prior level.** The unfolded effect follows it to first order, with the retraining effect
second order. It needs the files to exist, which §3.2 cannot confirm, and the director's leave to connect.

## 5. Records, macros, figures and text that would change

**The paper:**
- Eq. (1), `paper_body.tex:31` (`E_π − 135 MeV`);
- the sentence at `:35` ("a defined constant of 135 MeV … used consistently by the analysis and every prediction");
- the departure sentence that the decision's item 3 adds, which is not yet in the paper at this commit;
- every 16-cell number, through `values_fived16.tex`;
- the 3D/4D comparisons at `:264`;
- the 0.141 % at `:122`;
- the joint-test macros (`values_inference.tex`; `\jtNcells` at `:41,70`), if O1 runs;
- Figs. `fd_g_fig_ratio` (`:237`), `paper_fig_bkg_residual` (`:130`) and `paper_fig_deformation` (`:142`). The last two
  have no tracked producer.

**The note:**
- the definition at `sec_3d.tex:22-31` (`:26`);
- the 135 vs 139.57 paragraph at `sec_3d.tex:42` (0.67 %, 1.05 %);
- the comparison with the published definitions at `:40`;
- Ascencio's 11.0 % at `:206`, which is measured against the current definition;
- `sec_eavailw.tex:47,49` (`tab:observables-impl`);
- `primer_body.tex:164`;
- about 134 hand-typed `\SI` numbers in `sec_3d` (81) and `sec_eavailw` (53);
- the 5D validation rows in `sec_validation.tex:88-129`;
- `sec_method.tex:197`;
- the figures listed in the note sections above.

**Generated values:**
- `make_values_fived16.py` emits 1,416 keys, by prefix classification. About **1,243** come from E_avail-dependent
  readouts, and **938** of the printed ones depend on them. 147 of those are used in the paper.
- Its hard asserts that a rerun could trip are at `:267-272` (the low-stability cells), `:341` (R04 smallest σ),
  `:347` and `:387,415-416,429`.
- `make_supplemental.py` (`SUPP_PINS` at `:35`) rewrites all three supplemental CSVs.
- `check_sec4_receipts.py:130-157` guards `paper_body.tex:124,138` against 5D receipts.

**Records:**
- the data product and deposit candidate, and the `fd/with-cpl/` set;
- every FD-* report's digests;
- `docs/EAVAIL_DEFINITION.md` §3 (`:89-148`, including the site list at `:135-141`) and §1 (`:16-17`);
- UD-002 (`USER-DECISIONS.md:30-56`);
- OI-30 and OI-59 (`OPEN_ITEMS.md:159,188`);
- `VALIDATION_LEDGER.md:1731`;
- the claim-to-evidence ledger (`docs/publication/CLAIMS-20261005-claim-to-evidence.md:31,49,51,52,123`);
- the paper's fact ledger (`state/2d-closeout/stageF/methods/r21/fact-ledger.md:114,115,118` and its E_avail-number
  rows), and the 16-cell ledger `.../methods/fived16/ledger.md`;
- the release package README (`main_paper.tex:77`);
- the three Ben presentation scripts.

## 6. Recommendation

**This is for the director's independent read, then Joseph.**

1. **Measure the exact size first** (§4.3, step 0).
   - **Cost:** minutes on a login node, 0 node-h, read-only.
   - **Why:** it replaces a factor-of-3 bracket with the prior-level number per cell and per fine bin, which is what
     the choice turns on.
   - **What it needs:** the director's leave to connect. I have not connected.
2. **Decide now whether to keep the event-loop files past 2026-11-09.**
   - **The trade:** Route A costs about 15 node-h. Route B adds event loops whose CPU cost is unmeasured.
     <!-- absence-ok: "unmeasured" is scoped to the Search line in §3.1 and §3.2 -->
   - **The files:** the 12 per-playlist universe loops (159.4 GiB, exposed from 11-09), their merge (159.4 GiB, from
     11-22), and the unconfirmed 5D omnifile.
   - **Who decides:** keeping 320 GiB on pscratch, CFS or HPSS is a storage decision for the director or Joseph. It is
     only flagged here.
3. **Then Joseph's choice, with the measured size in hand:**
   - **(a) Keep 135,** with the departure sentence (decision item 3) and the measured size quoted. This costs nothing.
     The observable stays one we define, 4.57 MeV per charged pion away from MINERvA's published E_avail.
   - **(b) A scoped switch.** The 16-cell result and its covariance, Stage G, F1, C_PL,5D and the 3D/4D central values
     move to 139.57 by Route A (about 15 node-h measured, cap about 35, CPU only), with the seven sites changed in one
     commit.
     - The E_avail-binned validation studies (A7 joint test, closure figures, the scalar-5D covariance, PET) are
       labelled as on the 135 definition rather than rerun. They characterize the estimator, and a 4.57 MeV-per-pion
       relabelling of the truth coordinate does not bear on what they test.
     - The two closure figures cannot be regenerated anyway without their producers.
   - **(c) A full switch:** (b) plus O1 (207.9 node-h) and O2. That is the only option with no mixed definitions in the
     note.

**My recommendation is 1 and 2 now, then (a) unless step 0 shows a cell moving by more than a few tenths of σ.**
- **Why (a):** the case for 139.57 is definitional alignment, not precision.
- **Why (b) and (c) cost more than node-h:** (b) leaves two definitions in one document, and (c) costs 208 node-h for
  the alignment.
- **If Joseph prefers alignment anyway, (b) is the economical form,** provided the files survive.

---

Paths beginning `state/` are under `docs/orchestration/state/`. Paths beginning `FD-`, `S1-` or `fd/` are under
`docs/orchestration/state/measurement-paper/5d-community-20261024/`.
