# DECLARATION: d1 and d2. Reconstruction-level data/MC per playlist, and the flux-swap test (2026-11-04, revision 2)

**Commissioned by** Joseph, `DECISION-20261104-joseph-referee-analysis-commission.md` item 1 (#759, merged at
`1a87d209a9fc337c49d40ae3114d51312a45e132`; his answer's sha256 begins `1b4d8a744aad9c24`).
- The designs are d1 and d2 of `state/2d-closeout/stageF/methods/secondary-results/scope-referee-analysis-20261104/REPORT.md`
  §5 (#758).
- d1 is the Codex diagnosis lane's C-R, and its design points are folded in here:
  `secondary-results/diagnosis-three-items-20261104/REPORT.md` §C3 (#760, merged `0e1dd76a`).
- d2 is a narrower form of that report's C-H.
- The per-playlist flux and POT provenance inventory is that lane's C-N, not this declaration's.

**Owner:** limitation-resolver. **Route:** this declaration, then the audit (`FD-RPD-RECO-AUDIT-1-SONNET-{PROMPT,ANSWER}.txt`,
answered in §9), then the director's binding, then each connect's sha256 to the director for a go. The run goes after
B4's cluster work.

**Frozen before any comparison is read.**
- No data/MC ratio, offset or step in this declaration's sense has been computed from these inputs.
  <!-- absence-ok: scoped to the readers of these 24 files: RPD's check and readout read `measured` only to recompute measured_weights, to count rows and to unfold (nd-unfolding/fd_rpd.py:789-812, :867-877), and the mwdiag runs compared measured_weights shares; none forms a data/MC ratio -->
- What has already been read is listed in §6.
- The recipe, readings and licences change only by a new declaration.

**CITABLE FOR, once run under a binding:** the per-playlist reconstruction-level offsets, the swap fractions and the
size-test statistics, as defined here, and the outcome each produced.

**NOT CITABLE FOR:**
- which period or which flux is correct;
- a correction or an exclusion (scope §5 d3, not commissioned);
- any change to the result, C_PL,5D or any covariance;
- "validated", "covers" or "coverage".

## 1. Inputs, pinned

**The run-period diagnosis's own per-playlist dumps**, written by its job A 60786801 on 2026-11-04. They are 24 files
under `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps/`:
- `lat_<PL>.npz` and `lat_<PL>_bkg.npz`, for PL ∈ {1A … 1G, 1L, 1M, 1N, 1O, 1P}.
- Their sha256 are in `fd/rpd-reco/INPUTS.sha256`, from job A's lane logs (`fd/receipts-rpd/run/jobA/line*-60786801.log`).
- **The pin check refuses three cases:** a missing file, an extra file in the set, or a digest mismatch.

**Their weights.** In each `lat_<PL>`, the MC weights are scaled to that playlist's own data POT
(`FD-RPD-DECLARATION.md:274-288`). RPD's control C1 passed that predicate (`fd/receipts-rpd/run/controls/controls.json`,
`C1`).

**Keys read, and only these:**
- from `lat_<PL>`: `MCreco`, `MCgen`, `w_reco`, `pass_reco`, `pass_truth`, `measured`, `data_pot`, `axes`;
- from `lat_<PL>_bkg`: `bkg_reco`, `bkg_w`.

**How they are read:**
- Each key is read alone, with `allow_pickle=True`, because `axes` is an object array.
- Every read is O_NOATIME on Linux. A local test guards the flag on other platforms.
- The tests load real `.npz` files in this format.
- The columns are [p_T, p_∥, E_avail, q₃, W]. Rows that are not `pass_reco` carry the −9999 sentinel in `MCreco`
  (`unfold_nd_omnifold_unbinned.py:447-451`).

**What the dumps do not hold.** They store only the five reconstructed and true observables, weights, POT and flux
integrals (`s5p_input_dumps.py:171-183`; `nn_dump_inputs.py:92-103`). So:
- MINOS matching category, muon curvature, vertex position and true Eν are not available;
- d1 compares none of the first three;
- d2 recovers Eν from truth (§4);
- no new dump is made under this declaration.

**d2's flux spectra.** These are the files MAT's `FluxReweighter` maps to the playlists:
- 1A–1F → 1D;
- {1G, 1L, 1M} → 1M;
- 1N–1P → 1N.

The mapping is from `2d-closeout/playlist-spread-20261014/REPORT.md:154-161`.
- **Their identities come from the Codex lane's C-N inventory** when it exists. Otherwise they come from P0, a 0
  node-h login listing.
- **P0 records, before binding:**
  - each file's path, sha256, CV flux histogram name and Eν binning;
  - the `FluxReweighter` source lines, at the cluster MAT checkout's sha, that establish §4's premise P-F;
  - one open of each histogram with the run's own Python environment.
- These are simulation inputs, not data.

## 2. The d1 recipe

**Prediction and ratio.** For playlist X and bin b:
- data count: N_X(b) is the number of `measured` rows in b;
- prediction: P_X(b) = Σ `w_reco` over the `pass_reco` rows in b, plus Σ `bkg_w` over the background rows in b;
- ratio: r_X(b) = N_X(b) / P_X(b).
- **Assertions, each a STOP on failure:** every `pass_reco` row has `pass_truth` true (in job A's logs `dropped_phase=0`);
  and every `measured` row has finite values.
- The rows job A excluded for non-finite truth support, 33–511 per playlist, are disclosed. They are about 10⁻⁴ of the
  weight.

**The exposure treatment, fixed:**
- **absolute:** the weights are already per data POT;
- **shape:** each playlist's offsets minus its σ-weighted mean on the axis;
- **rate per POT:** Σ_b N_X / `data_pot`_X against Σ_b P_X / `data_pot`_X, overall and in the p_∥ strata below.

**Reference and offset.**
- The reference is leave-one-out: r_ref,−X(b) = Σ_{Y≠X} N_Y(b) / Σ_{Y≠X} P_Y(b).
- The offset is o_X(b) = r_X(b) / r_ref,−X(b) − 1.

**Noise. Every σ comes from one paired bootstrap, B = 200.**
- Each replica draws Poisson(1) weights for every data row and every MC and background row.
- The seeds are `SeedSequence([20261104, 11, k + 1])`, k = 0 … 199. The nonzero words avoid numpy's zero padding.
- The same draws serve every axis, both swaps and the reference. Correlations between quantities sharing rows,
  including s_obs and s_swap, are therefore carried.
- Analytic σ is not used.

**Sparse bins** (a simulation-only rule):
- a (X, bin) enters a χ² only if P_X(b) ≥ 25;
- excluded bins are listed;
- no row is cut.

**Axes and bins.** These are written by step 0 from MC keys alone. Step 1 refuses to open `measured` without step 0's
record.
- **p_∥ and p_μ** (GeV/c): 1.5, 2, 3, 4, 5, 6, **8**, 10, 15, 20, 60.
  - These are the 2D comparison's edges (`playlist-spread-20261014/REPORT.md:143-144`).
  - 8 GeV/c, the boundary of the step, is a common edge in every playlist and comparison.
- **p_T** (GeV/c): 0, 0.15, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5. These are a subset of the analysis's
  `PT_EDGES`.
- **θ_μ = atan2(p_T, p_∥):** ten bins at the pooled-MC weighted deciles.
- **E_avail (the recoil), q₃ and W:** ten bins each at the pooled-MC weighted deciles of `pass_reco` rows.
  - Duplicate decile edges are merged, and step 0 records it.
  - The outer bins are open, (−∞, d₁) and [d₉, +∞), so no data row is unbinned.
- **The 16 cells:** `nd-unfolding/pv-ladder/readouts/h2_definition.json`'s `reporting_cells[].box` and
  `h2_to_reporting_cell`, applied to reconstructed values. Rows in `unreported_boxes` (2, 6, 10 and 14) are counted
  and reported, not used.
- **Edge convention:** every bin is [lo, hi). Rows outside the p_T and p_∥ ranges go to an overflow bin, which is
  counted and kept.
- **Muon strata, for conditioning:** p_∥ < 8 and p_∥ ≥ 8, crossed with θ_μ below and above its pooled-MC weighted
  median. That gives 4 strata.

**Shape statistic.** For each (X, axis a) and each (X, hadronic axis a, muon stratum m):
- χ² = Σ_b (o_X(b) − ō_X)² / σ_X(b)², with ndf = n_b(used) − 1;
- the p-value is the χ² tail, its calibration checked by C-0.

**The null control C-0.** It runs before any reading. It is a STOP on failure, and on a STOP no d1 or d2 reading is
computed.
- **R = 20 independent random partitions** (seeds `SeedSequence([20261104, 13, r + 1])`). Each splits the data rows and
  the MC and background rows of the pooled sample into 12 pseudo-playlists.
  - The data counts and MC weight fractions are the real playlists' own.
  - Each pseudo-playlist therefore has independent data and MC noise.
- The same code and bootstrap give 8 axes × 12 pseudo-playlists = 96 p-values per partition, 1,920 in all.
- **Gates:**
  - the fraction with p < 0.05 lies in [0.03, 0.075];
  - the fraction with p < 0.001 is at most 0.004;
  - in no partition does the family-wise rule below fire on any axis.
- An understated or overstated σ fails the first gate. The tests plant both (§7).

## 3. d1 readings, fixed

The family-wise firing rule is the same everywhere: **an axis fires if some playlist has p < 0.001 / 12 on it.**

- **R-d1.0, the p_∥ step at reco.**
  - The statistic: s_G = [R_G(8–15) / R_G(1.5–8)] / [R_PA(8–15) / R_PA(1.5–8)] − 1. R_G is Σ_{X∈G} N_X / Σ_{X∈G} P_X,
    with PA = 1A–1F, PB = {1G, 1L, 1M} and PC = 1N–1P.
  - It is **SEEN** if |s_PB| ≥ 3σ, with its sign and size; otherwise **NOT-SEEN-AT-3σ**.
  - It is two-sided.
- **R-d1.1, the muon axes.** For each of p_∥, p_μ, θ_μ and p_T: whether the axis fires, and which playlists exceed
  p < 0.001.
- **R-d1.2, rate per POT.** Per playlist and per group, with σ. Descriptive.
- **R-d1.3, the recoil and hadronic axes, conditioned on the muon.** For E_avail, q₃ and W:
  - **UNCONDITIONAL:** does the axis fire over the full sample?
  - **CONDITIONAL:** does it fire within any of the 4 muon strata, at p < 0.001 / (12 × 4)?
  - **The outcomes:**
    - **HADRONIC-CONDITIONAL** if any axis fires conditionally;
    - **HADRONIC-VIA-MUON** if some axis fires unconditionally and none conditionally;
    - **HADRONIC-NOT-DETECTED** if neither, at this sensitivity.
  - Only HADRONIC-CONDITIONAL licenses saying that a recoil-side difference exists beyond the muon distribution.
- **R-d1.4, carriers.** For each axis, the firing playlists ∩ {1L, 1M} (RPD's CARRIES set) and the rest. Descriptive.

## 4. d2, the flux swap

**Eν per MC row**, by inverting the simulation's truth W (`CVUniverse.h:385-409`):
- the forward map: W² = M² + 2(Eν − Eμ)M − 4EνEμ sin²(θ/2);
- inverted: Eν = (W² − M² + 2EμM) / (2M − 4Eμ sin²(θ/2));
- θ = atan2(p_T, p_∥) and Eμ = √(p_T² + p_∥² + m_μ²), from `MCgen` in GeV.

The constants are M_p = 0.938272013 and M_n = 0.93956536 GeV, which a test reads from `CVUniverse.h:39-40` (in MeV),
and m_μ = 0.1056583755 GeV.
- The struck nucleon is not in the dumps, so Eν is the mean of the M_p and M_n values. Their spread is reported.
- **This departs from the scope's design**, which priced an event-loop pass for Eν (scope §5, d2). The inversion
  costs 0 node-h. C-E3 is its check. If C-E3 fails, the event-loop route returns to the director, priced.

**Controls, each evaluated separately in the p_∥ strata [1.5, 8), [8, 15) and [15, 60]. Each is a STOP on failure.**
- **C-E1:** the denominator is > 0 and Eν ≥ Eμ for at least 99.9% of the `pass_reco` weight in each stratum.
- **C-E3:** q₃′ = √(4EνEμ sin²(θ/2) + (Eν − Eμ)²), against `MCgen`'s q₃ (MAT `Getq3True`, from the generator Q²,
  `runEventLoopOmniFold.cpp:590-591`).
  - In each stratum the weighted median |q₃′/q₃ − 1| is ≤ 0.002, and the 99th percentile ≤ 0.03.
  - A 1% Eν scale error moves the median by about 2% (audit M7), so the median gate detects errors of about 0.1%.
- **C-E2,** the M_n against M_p spread, is reported, not a gate. The audit shows it cannot discriminate.

**The premise P-F,** checked at P0. MAT's CV flux weight for a playlist is φ_file(E) over a generation flux that does
not depend on the target file. In that case the swap factor is exactly φ_T(E) / φ_own(E), in the files' common units
(per POT).
- If the source shows otherwise, d2 STOPs before any swap.
- The factor is applied as a step function in the files' Eν bins.
- If more than 0.1% of PB's `pass_reco` weight in p_∥ 1.5–15 lies outside the common Eν range, d2 STOPs. Rows outside
  it keep weight 1.

**The swaps:**
- **the primary swap:** PB's signal MC from its own file to 1D;
- **descriptive only:** the mirror (PA to 1M), which carries mostly the same information (audit m2), and PC to 1D.

**Background.** It has no truth.
- The classification uses background unswapped.
- It is repeated with background scaled by the file integral ratio, as a bracket.
- If the two classifications differ, the outcome is INCONCLUSIVE.

**The prediction, fixed before data (the C-H size test).**
- Step d2-predict uses MC only, after P0 and before any `measured` key is opened.
- For each playlist X it records s_pred,X: the change in X's reco p_∥ step from moving X's MC from its own file to 1D.
  It is 0 for PA members by construction.
- Group values are recorded too.

**Data-side statistics:**
- s_obs, as R-d1.0;
- s_swap, the same with PB swapped;
- f = 1 − s_swap / s_obs;
- per playlist, s_obs,X: X's step against the PA pool, leave-one-out for PA members;
- χ²_pred = Σ_X (s_obs,X − s_pred,X)² / σ_X², with 12 dof.

Every σ, including σ_f, comes from the paired bootstrap of §2.

**Outcomes, evaluated in this order, so that exactly one applies:**
1. **NOT-SEEN:** R-d1.0 is NOT-SEEN-AT-3σ. d2 makes no further reading.
2. **DOES-NOT-TRACK:**
   - f + 2σ_f < 0.25;
   - or sign(s_pred,PB) ≠ sign(s_obs) with |s_pred,PB| ≥ 2σ_pred.
3. **TRACKS,** all of:
   - f − 2σ_f ≥ 0.5 and f ≥ 0.75;
   - sign(s_pred,PB) = sign(s_obs);
   - P(χ²₁₂ > χ²_pred) ≥ 0.01.
4. **PARTIAL:** f − 2σ_f ≥ 0.25.
5. **INCONCLUSIVE:** anything else, including the background bracket changing the outcome.

## 5. Code, price, calendar

**Code.** One new script, `nd-unfolding/fd_rpd_reco.py`, with these steps, in order:
1. `pins`;
2. `p0`;
3. `step0` (MC-only bins and strata);
4. `c0`;
5. `d2-predict` (MC only);
6. `d1`;
7. `d2`.

**What each step enforces:**
- Each refuses unless the previous step's record exists and passed.
- Each record carries its inputs' sha256, the code's sha256 and the argv.
- The script imports only committed modules.

**Price: 0 node-h.**
- Everything runs on a login node, with threads 1, nice 19 and O_NOATIME, from a fresh clone at the bound sha.
- The inputs are about the size of `lat_zero` (1.55 GB, `FD-RPD-DECLARATION.md:158`).
- The bootstrap is about 32.8M MC rows plus 4,091,707 data rows (job A's lane logs) × 200, done in chunks. The wall-clock is unmeasured and
  expected under two hours.
  <!-- absence-ok: a price estimate for an unrun step, not a claim that a result is absent -->
- No job, and nothing is written to CFS.

**Calendar.**
- The dumps were written on 2026-11-04, so their exposure is not before about 2026-12-30 (arithmetic).
- The flux files' retention is recorded at P0.
- The run follows B4's cluster work.

## 6. Admissibility

- **It is a reconstruction-level read of the data.** The recipe is frozen and bound before any ratio is computed
  (`FD-DIRECTOR-RULINGS.md:63-68`).
- **No new cuts,** and no change to any reported number, estimator or covariance in any outcome. This is a post hoc
  diagnostic, class D in #760's terms.
- **What has already been read, so is not blind:**
  - p_T and p_∥ at reco level, in 2D (`playlist-spread-20261014/REPORT.md:126-148`);
  - the p_∥ step, unfolded, in 2D (`period-unfold-20261014/REPORT.md:50-60`);
  - the 5D per-playlist results, unfolded on the 16 cells, including the hadronic cells (RPD's readout: CARRIES
    {1L, 1M}).
- **Not read before:** E_avail, q₃, W, p_μ and θ_μ at reconstruction level, per playlist.
  <!-- absence-ok: scoped to the two reco-level period studies above, which compare p_T and p_∥ only, and to RPD, which reads unfolded cells -->
- **The flux swap and the Eν inversion are simulation only.** d2-predict fixes the predicted size before data.

## 7. Tests (`nd-unfolding/tests/test_fd_rpd_reco.py`)

**Fixtures:** real `.npz` fixtures with object arrays, in the dumps' own format.

**Each refusal tested in the direction it acts:**
- pins: missing file, extra file, digest mismatch;
- each step without its predecessor's passing record, in particular d1 without a passing C-0;
- the `pass_truth` and finite-value assertions;
- C-E1 on a fixture with a negative denominator;
- C-E3 on a fixture whose Eν is scaled by 1%;
- P-F's STOP;
- the out-of-range STOP.

**C-0 calibration:**
- it passes on a structure-free fixture with independent noise;
- it fails with σ halved;
- it fails with σ doubled;
- it fails with a planted 5% shape offset in one pseudo-playlist.

**Arithmetic, against hand calculations:**
- the leave-one-out offset and its bootstrap σ;
- ndf after the weighted-mean subtraction, and the P ≥ 25 rule;
- the bin-edge convention, open outer bins, the overflow bin, and merged duplicate deciles;
- the `unreported_boxes` exclusion.

**The d2 classifier:**
- each outcome reached, including the revision-1 gap (f = 0.8, s_swap = 4σ, s_obs = 20σ), which must now give exactly
  one outcome;
- negative s_obs;
- s_obs = 0, where f is undefined and the outcome is NOT-SEEN;
- the background bracket.

**Eν:**
- the round trip against the forward map to 10⁻⁹. This is algebra only, and labelled so;
- the constants parsed from `CVUniverse.h:39-41`.

## 8. What each outcome licenses

Every licence covers a statement in the note first. Any paper use goes to Joseph through the PRD-referee read
(`DECISION-20261104-joseph-referee-analysis-commission.md` item 4). **No outcome names a cause except TRACKS, which
names only a coincidence with the simulation's flux-file assignment.** RPD's rule for removing the unknown-cause clause
is not met by any outcome here alone (#760 §C1).

| outcome | may be stated | may not |
|---|---|---|
| a STOP (pins, C-0, C-E, P-F, out-of-range) | that the declared test stopped, at which control | any reading |
| R-d1.0 SEEN | the p_∥ step is present at reconstruction level before unfolding, with its sign, s ± σ | that the unfolding plays no part |
| R-d1.0 NOT-SEEN-AT-3σ | not seen at reco level at this sensitivity, with s ± σ | that it is absent |
| R-d1.1, R-d1.2 | the firing axes and playlists, and the rates per POT, with χ², p and σ | any localisation in the detector |
| HADRONIC-CONDITIONAL | a recoil-side data/MC difference between playlists within common muon bins, with its axes and playlists | its cause |
| HADRONIC-VIA-MUON | the hadronic-axis differences are not detected once the muon distribution is held fixed | that the recoil response is the same |
| HADRONIC-NOT-DETECTED | none detected at this sensitivity | that none exists |
| TRACKS | reweighting the 1G–1M simulation to the 1A–1F flux file removes the fraction f ± σ_f of the reco-level step, and the simulation's predicted per-playlist steps agree with the observed ones (χ²_pred). **The step coincides with the difference between the flux files the simulation assigns to these periods** | which flux or period is correct; that a flux is wrong; "explained" or "corrected"; that the unknown-cause clause can go |
| PARTIAL | f ± σ_f, descriptively | any mechanism wording |
| DOES-NOT-TRACK | the flux-file difference does not reproduce the step (f ± σ_f, or the opposite sign) | anything beyond excluding that candidate |
| INCONCLUSIVE | that the test did not decide | any of the above |

**In every outcome:**
- "The cause is not known" stays. A change to it is Joseph's, and RPD §6.1 requires a named mechanism whose localisation
  and size are both tested.
- C_PL,5D, its wording and RPD's licensed sentence are unchanged.

## 9. Audit 1 (Sonnet), and what this revision changed

The audit is verbatim in `FD-RPD-RECO-AUDIT-1-SONNET-ANSWER.txt`, at revision 1 (`b0de7ef6`), with its prompt beside
it.

**Blocking and major:**

| finding | change |
|---|---|
| B1: d2's outcome table had a gap; f was not compared with σ_f | §4: an ordered, exhaustive table, an INCONCLUSIVE outcome, and σ_f in every threshold; tested (§7) |
| M1: one-sided R-d1.0 | two-sided, with the sign stated |
| M2: σ_f ignored the shared MC | one paired bootstrap over data, MC and background rows serves every statistic |
| M3: C-N could not test the MC term | C-0 partitions MC and data independently, has R = 20 partitions, and gates on calibration both ways; tested with σ halved and doubled |
| M4: the C-N tolerance contradicted the firing rule | one family-wise rule (p < 0.001/12 per axis, /48 conditional), with C-0 requiring it never fires in the null |
| M5: sparse bins | bootstrap σ; P ≥ 25 simulation-only rule; no row cut |
| M6: bin edges | [lo, hi), open outer bins, overflow bins kept, duplicates merged |
| M7: aggregate C-E controls | per p_∥ stratum; C-E3 median and 99th percentile; C-E2 report-only |
| M8: the swap premise | P-F checked at P0, a STOP if unmet; an out-of-range cap |
| M9: the tests | §7, as listed |

**Minor:**
- m1: the shape-against-normalisation split is replaced by rate per POT (R-d1.2) and the background bracket.
- m2: the mirror is descriptive only.
- m3: the background bracket.
- m4: the `pass_truth` assertion and the excluded rows are disclosed.
- m5: Q² is cited at `CVUniverse.h:385-409`, and the constants are pinned.
- m6: §6's disclosure, and no bare "flat".
- m7: the h2 keys and `unreported_boxes`.
- m8: the departure is stated in §4.
- m9: the O_NOATIME guard; the calendar now reads 11-04.

**From #760 §C3, C-R:**
- common bins at the 8 GeV/c boundary;
- the exposure treatment frozen;
- muon momentum and angle;
- recoil and rate per POT;
- conditioning on the muon before recoil attribution;
- the missing branches stated;
- no new cuts.

**From #760 C-H:** the size test fixed in simulation before data (d2-predict, χ²_pred).
