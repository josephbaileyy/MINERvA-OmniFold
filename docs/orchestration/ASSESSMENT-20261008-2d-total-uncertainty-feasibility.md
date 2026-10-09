# Assessment — 2D total-uncertainty feasibility (uncertainty preparation, lane C)

**Status: FINAL (lane C FREEZE, plus E's repair 1).** Reconciled once after A's FREEZE (`9fab26e8`, `f762749d`). Also reconciled with
A's CONTRACT (`acb338a2`), and with B's PROVISIONAL and its later estimator-specification commit (`f19084f4`,
`ea6a154e`; B's counts unchanged: 719 / 1,116). B's final document was not available at this freeze.

**CITABLE FOR:**
- the component inventory and dispositions in `state/uncertainty-preparation-20261008/c/components.tsv`;
- the four audits in §3;
- the executable cost model `c/costs.py` and its output `c/costs.json`, with operands labelled MEASURED,
  DOCUMENTED, EXTRAPOLATED or ASSUMED;
- the staged route in §8, and what blocks each transition.

**NOT CITABLE FOR:**
- any uncertainty value, coverage result or adoption;
- a change to the quoted 2D construction (`VL170`/`VL172`) or to the quoted central estimator;
- any compute request or release;
- a publication-scope decision;
- lifting the `KNOWN_ISSUES.md` 85 deferral;
- restarting 5D, PET or any terminal campaign.

A statistical PASS from lane B cannot become a total-uncertainty claim.

- **Base:** `f8e2bf85` on `prep/uncertainty-c-total-20261008`, with no rebase.
- **Owner:** lane C (Claude Opus 5.5). The single independent review happens in E.

## 1. Decision and disposition

**Decision asked.** Beyond the proposed statistical test, can a complete, matched uncertainty procedure be built
and validated at defensible cost? What specifically prevents it today?

**Disposition: NO-GO.** Four independent obstacles stand today. Each one alone blocks a validated total.

1. **The quoted central and its uncertainty come from two different estimators** (A, CONTRACT §1–2).
   - The central is exact-split GBT, `E_C`. Every uncertainty block is LightGBM:
     - `E_S`, seed 1, the statistical band;
     - `E_U`, seed 42, the systematic universes and their matched CV;
     - `E_ML`, seeds 1–10, the ML block.
   - The two centrals differ by a median 1.3 σ_stat per bin.
   - The transfers to `E_C` and the seed 1 ↔ seed 42 relation are unmeasured. Pairing ids below are A's FREEZE
     numbering, with `P09` split into `P09a`/`P09b` by A's REPAIR 1; A's CONTRACT text used earlier ids.
   - A's FREEZE recorded 4 of 17 pairings DISPROVED and 3 UNRESOLVED. A's REPAIR 1 (`cc9eed27`) split `P09` into
     `P09a` and `P09b`, giving 4 of 18 DISPROVED and 4 UNRESOLVED:
     - the band, the systematics and the ML block were produced by LightGBM, not by `E_C` (`P02`, `P04`, `P09a`);
     - their transfer to `E_C` is unmeasured (`P03`, `P05`, `P09b`), and so is the seed 1 ↔ seed 42 relation (`P07`).
     So validating the LightGBM band does not, by itself, validate the uncertainty attached to the quoted
     central.
   - The cost consequence: a validation that keeps `E_C` must also run a single-threaded exact unfold in every
     experiment. A measured that unfold at 69,523 s and MaxRSS 16.8 GB. The cheapest route then costs 5,728 node-h
     if A's memory packing at about 0.68 node-h holds (contention unmeasured), and 268,936 if the jobs run as the
     central did.
   - A defined route exists only after one of two things:
     - measured transfers to `E_C` (A's `P03`, `P05` and `P09b` operands);
     - Joseph's decision to make a LightGBM-class estimator the quoted central. That is a change of central
       estimator, which A §2.4(2) and this assessment cannot make.
2. **Independent populations do not exist** (B, PROVISIONAL §1, §17).
   - The production omnifile carries no event identity, so an event-loop rebuild (R0) is needed.
   - The one MC production (MC/data 4.708) yields zero disjoint pairs of a production-size bank and a data-size
     reservoir.
   - This binds every total procedure below, not only B's test. Pseudo-data drawn on the training MC under-scatter
     (`KNOWN_ISSUES.md` 85, and B's §3).
   - A second production cannot be priced by this project. B's generative-law route G is undeveloped and unpriced.
3. **Missing methods and constructions.**
   - background-template statistics are not propagated at all (C03);
   - the 2D lateral detector bands have CV-selected support only (C05a), and no continuous-shift generator exists
     for nuisance-drawn pseudo-data (M1);
   - the flux × muon-energy cross block is omitted from the adopted sum (X01);
   - response departures outside the simulated family have no method (C10);
   - model dependence can only be given a finite-set allowance, never a guaranteed bound (C09).
4. **Resource.** Admitted totals at 4 cases × 1,250 experiments include a protected 20% reserve (§6). The counts
   are B's criteria, sized for a 4-case family.
   - **P1**, validating the procedure as performed, with every data-dependent width recomputed per experiment:
     **0.29–1.21 million node-h**.
   - **P3**, with two unvalidated shortcuts: 20,000–85,000.
   - **P2**, calibrating the quoted band as a fixed band: 575–3,518.
   - Scale: B measured 3,040.6 node-h remaining on `m3246` for all users (iris, 2026-10-09T06:15Z). That is B's
     same-day measurement, not a resource C carries forward or requests.
   - The 2D accounting receipts read here record 18.1 (`VL170`), 13.3 (`VL169`) and 7.1 (`KNOWN_ISSUES.md` 85)
     node-h. The whole s5p pool used 253.

**Classification.**

| Route | Disposition | Why |
|---|---|---|
| P1 | **INFEASIBLE** | demonstrated unaffordability |
| P2 | **INCONCLUSIVE** | finite and modest in compute, but an operand is unavailable: obstacle 2 has no priced population construction, and obstacles 1 and 3 are prerequisites |
| P3 | admits no savings | its shortcuts are unvalidated (§7) |

No route is FEASIBLE: none has both a defined method and a costed evidence path.

## 2. What "total uncertainty" would mean here

The successor proposal (§4) offers a probabilistic covariance **plus** a signed, bounded model allowance B∓. This
assessment makes the claim explicit, so that validation tests a stated proposition.

- **Probabilistic part: nuisance-averaged frequentist calibration.**
  - Nuisances θ are flux, detector and interaction-model universes. They are drawn from a *declared* law. The MAT
    convention treats ±1σ endpoints as the σ of an implicit Gaussian, and PPFX universes as draws.
  - Data and MC fluctuate by Poisson draws on independent populations (B).
  - The claim is that the interval covers the fixed truth at the nominal rate, **averaged over θ under that law**.
    It is not coverage conditional on the actual θ.
  - It is also not a probability statement about the cross section.
- **Model allowance: a sensitivity envelope.** B∓ is the cellwise maximum signed bias, with simultaneous upper
  confidence limits, over a finite, declared development truth set at the fixed simulated response.
  - It is not a probability.
  - It is not a guaranteed bias bound over a truth hull.
  - It is not a bound at the actual data truth.
  - Prior variations stay sensitivity diagnostics and never become a covariance.
- **Response departures** outside the universe parametrization are an explicit, stated assumption (C10). Repeated
  truths under one response do not test them.
- **Two validation claims, of different strength.**

| | P1: reconstructed-interval coverage | P2: fixed-band calibration |
|---|---|---|
| Per experiment | central fit, inner replicas, seeds and all universes are recomputed on the pseudo-data | one unfold; scored against a band and B∓ frozen before validation |
| What it validates | the procedure | the quoted band, at the declared truths and under the declared law |
| Does not validate | — | that the procedure gives correct widths for other data, or the band's bytes (B §15) |

  P2 must declare whether the frozen band is transferred in absolute or relative form. `VL169` used per-bin
  σ/mean × fixed truth and disclosed the transfer ratio.
- **Conditioning differences.** A procedure that recomputes purity per experiment, or resamples background MC,
  measures a different conditional variance from the adopted band's (A §2.4(5)). The fixed purity and the
  unresampled background are recorded as conditioning (C01, C03); they are not silently absorbed.

## 3. Component inventory and the four audits

`c/components.tsv` has 14 rows: ten components (C01–C10, with C05 split into a and b) and three dependence rows
(X01–X03). Each row records estimand, conditioning, source law, existing bytes, matching CV, support limitations,
covariance convention, correlation partners, required evidence, disposition and evidence.

| Disposition | Rows |
|---|---|
| REUSABLE | C07 |
| MATCHING NEEDED | C01, C02, C04, C05b, C06, C08 (seed), X02, X03 |
| NEW CONSTRUCTION | C03, C05a, C09 (scope-limited) |
| UNRESOLVED | C08 (exact-backend seed variation and backend definition), C10, X01 |

Every MATCHING NEEDED row inherits A's finding that no block was produced by `E_C`. The rows stay MATCHING NEEDED,
not UNRESOLVED, because the route to matching is defined: either measured transfers (`P03`, `P05`, `P09b`), or Joseph's choice of central followed by
setup item S-a.

**Audit 1 — target normalization is counted once: CONFIRMED for the standalone construction.**
- The 1.4% rank-1 band is added at one site: `--add-norm 0.014` in `uq/rollup_vl170_adoption.sh:38,48`, built in
  `uq/analyze_universes.py:248-253`.
- None of the 44 bands in `uq/universes_full_list.txt` is a target or normalization band. `NormDISCC` and
  `NormNCRES` are GENIE interaction normalizations.
- Neither the bootstrap nor the ML block adds it.
- The nucleon count 3.2352943e30 is one constant (A §2.2; D `D07`).
- It is entered twice only in the paper+ours combined-covariance χ², which is already documented as
  double-counting.

**Audit 2 — flux-universe index identity: NOT ESTABLISHED as an identity.**
- The correction divides flux universe *u*'s cross section by Φ_u from `hFluxUniv[:, u]`.
- That *u* is the same PPFX throw as `w_{truth,reco}_Flux_u` is asserted in three docstrings
  (`build_flux_universe_band.py:25-28`, `rescale_flux_universes.py:20-22`, `unfold_2d_omnifold_unbinned.py:156`),
  "verified by flux-integral vs event-weight ratio correlation, Pearson 0.96".
- `git grep 'Pearson 0.96'` finds only those docstrings and the 2D status. No committed receipt carries the
  computation.
- A permuted map would give a correlation near zero, so 0.96 is strong evidence of alignment. It is not an
  identity proof.
- Required: a by-construction proof that both come from the same `MnvVertErrorBand` universe ordering, or an exact
  numeric identity test. Both are zero-compute reads of existing per-universe flux MnvH1Ds and omnifile weights.

**Audit 3 — selection-changing universe support: SUPPORT-LIMITED.**
- The 187-universe omnifile was built with `MNV101_DUMP_UNIVERSES="1"` (`sbatch_evloop_array_universes_full.sh:43`).
  That mode writes CV-selected shadow branches (`runEventLoopOmniFold.cpp:104-107,218-235`).
- The 2D reference itself (`2D_OMNIFOLD_REFERENCE.md:236-241`) says this support is limited when a shift moves
  events into or out of the sample, and it names the five kinematic bands.
- `Muon_Energy_MINOS`, at 2.31% median, is the second-largest systematic band.
- The selection-complete mode (`MNV101_ACTIVE_UNIVERSE`) was run for 5D (120 per-playlist loops,
  `nd-unfolding/sbatch_evloop_array_5d_active_laterals.sh`). Its outputs carry muon kinematics. Reusing them for 2D
  needs a selection and phase-space equality check that has not been done.

**Audit 4 — bootstrap/ML overlap: PRESENT; bounded small on medians.**
- Each VL170 replica retrains at the pinned seed 1 on resampled weights. Each universe unfold retrains at seed 42.
- GBDT retraining noise is therefore inside the statistical block (X02) and inside every universe delta (X03).
  The separate ML block (C08) adds it again.
- Different RNG streams do not establish independence of these sources.
- Order-of-magnitude bounds (`costs.json` `overlap_bounds`), assuming iid retraining noise at the seedscan median
  of 0.166%:
  - removing C08 entirely moves the median total from 6.8707% to 6.8687%;
  - the noise implied inside the systematic median is about 0.79% in quadrature, which moves 6.830% to 6.784%.
- These are illustrative medians, not per-bin values. A measures σ_ML/σ_S per bin as median 0.26, p84 0.42 and
  max 0.73 (CONTRACT §2.4(4)). So in the bins where ML noise is largest, the overlap is a larger share of the
  statistical block, but still small against the total.
- The 2026-05-29 seed-varying → pinned-seed bootstrap swap moved √tr C_boot from 1.828e-40 to 1.817e-40, a
  ratio of 1.006. Independent addition of the ML block (√tr 5.061e-41) would predict about 1.038. The observed
  ratio is consistent with overlap. Its sampling resolution, which depends on whether the two sets shared
  bootstrap seeds, was not computed here, so this does not establish the overlap.

**Estimator identity (from A; not re-derived here).** These cells were provisional at `9204a390` and are now
settled by A.

| Block | Estimator | Configuration |
|---|---|---|
| Quoted central | `E_C` | exact GBT, `random_state=None`, ~19 h per unfold, product `142a45b0…` |
| Statistical band | `E_S` | lgbm, seed 1 (`VL170` replicas) |
| Systematic sweep and matched CV | `E_U` | lgbm, seed 42 |
| ML block | `E_ML` | lgbm, seeds 1–10 (`seedscan_lgbm/run_seedscan_lgbm_interactive.sh`; not the `--estimator hist` sbatch launcher beside it) |

- All four share the 205-bin mask, order and normalization.
- The seed-42 CV and the seed-1 run differ by a median 0.30 σ_S (max 1.28).
- The exact backend's own seed variation has never been measured. That is why C08 is UNRESOLVED for `E_C`.

**A's FREEZE row outcomes that change C's rows** (`a/pairings.tsv`: 10 VERIFIED, 4 DISPROVED, 3 UNRESOLVED):
- `P06`: the background template is bitwise frozen at CV in all 87 non-Flux universes. Background-model variation
  is therefore absent from the systematic block. This is added to C06, and a zero-compute comparison with the
  background-aware sweep (`uq/purity_newomni/`) is listed.
- `P14`: the printed 6.87% budget divides by the LightGBM seed-42 CV. With `E_C` as the denominator, the same
  covariance gives 6.83%. The §3 overlap medians use 6.87% and are illustrative either way.
- `P17`: no coverage measurement of `VL170` exists. That agrees with `KNOWN_ISSUES.md` 84.
- A's 2D-driver edit (`971fc00c`) only writes provenance records (`runConfig`, driver and helper digests). It
  changes no workload, so no timing operand moves.

## 4. Dependence and joint propagation

The adopted total is a block sum. The status says it "assumes independence (different RNGs / physics sources)".
Where blocks depend, this assessment proposes the following instead of a sum:

- **X01, flux × muon-energy scale.**
  - The paper carries a cross block (Bashyal low-recoil constraint). `analyze_universes.py:17-19` states the
    adopted sum omits it.
  - Proposed: coherent joint throws of (flux universe, muon-energy shift). This needs the M1 continuous lateral
    generator.
  - Fallback: a rank-2 cross term from the paper-derived correlation, scaled to our own band vectors
    (`rederive_flux_muonE_cross.py` route B), with its transfer assumption stated.
  - This is a missing method in the adopted construction, not a negligible-by-assertion term.
- **X02/X03, retraining noise.**
  - Measured route: a factorial, either 50 replicas × 4 seeds or a band subset repeated at two seeds (S-f).
  - Bounded route: carry the §3 bound.
- **C06 × C09.** The interaction knobs reweight MC truth and reco together. Each knob's delta therefore mixes a
  response/background change with a prior change. It is part of C06 and is not a substitute for the C09 allowance.
- **Statistical × systematic.** Universe deltas are differences at fixed data, so data-statistical noise cancels
  to first order. P1 recomputes them per experiment. P2 freezes them, so their own statistical noise is part of
  what P2 calibrates.

## 5. Procedures priced per experiment

Counts follow B's criteria (`f19084f4` `assurance.py`: κ ∈ [0.80, 1.25], β = 0.10, α = 0.04 for coverage and
0.01 for bias).
- C reran B's own functions with the family set to 4 cases × 206 functionals = 824.
- The result is N_required 823 and N_design 1,250 per case.
- At 206 functionals B's 719 / 1,116 reproduce exactly.
- The four cases are the successor proposal's: nominal, two perturbations, one combined.
- Costs are billed CPU node-h, computed as elapsed × billing/256.

| Procedure | Unfolds per experiment | Optimistic node-h per experiment | Conservative node-h per experiment |
|---|---:|---:|---:|
| P1, reconstructed full: central + 300 inner replicas + 10 seeds + 187 universes, all on the pseudo-data | 498 | 43.2 | 160.9 |
| P2, fixed band: one unfold of nuisance-drawn pseudo-data | 1 | 0.069 | 0.374 |
| P3, shortcut S1+S2: central + 50 inner replicas; systematic and ML blocks transferred | 51 | 3.03 | 11.2 |

All three assume a LightGBM-class central; §6 gives the `E_C` branch. A nested 300-replica experiment is not
priced as one unfold.

**Measured operands** (`costs.json` `measured`, from committed sacct receipts):

| Workload | node-h per unfold | n |
|---|---:|---:|
| Production bootstrap replica, shared 64 CPUs (ki84 `59410433`) | 0.0591 | 300 |
| Fixed-truth toy, shared 64 CPUs (ki85) | 0.0700 | 98 |
| Fixed-truth toy pilot, regular full node (`VL169`) | 0.198 | 3 |
| Bootstrap replica, regular full node | 0.216 | 1 |

Across all three receipts there are 508 completed jobs and no billed failures. The 95% Clopper–Pearson upper bound
on the failure rate is 0.59%.

**Cross-lane check.** C's model reproduces B's primary figure: 719 × 301 runs × 0.0591 × 1.05 gives 13,440.6
against B's 13,440 (`costs.json` `cross_check_B_primary`).

**Documented, not accounting:**
- a universe unfold is "~30 min on a full Milan node", which is 0.5 node-h (2D run-log archive, 2026-05-26, at the
  evidence tag);
- exact-GBT central: about 19 h on a full node;
- lgbm CV unfold: 13 min 24 s at 128 CPUs.

**Extrapolations and assumptions.** These product-rebuild timings are not full-training timings for new
workloads:

| Item | Optimistic | Conservative |
|---|---|---|
| Universe unfold, shared rate | 0.0591 × the documented universe/CV wall ratio 2.24 | — (DOCUMENTED full-node rate used) |
| Pseudo-data overhead for nuisance draws | 1.0 | 1.5 |
| Extraction per experiment (node-h) | 0.01 | 0.05 |
| Retry rate | 2% | 10% |
| Independent re-run fraction for verification | 5% | 10% |

Storage is 0.06 MB per unfold output (measured: 300 outputs = 18 MB). At 5,000 experiments P1 needs 146 GB, P3
15 GB and P2 0.3 GB.

**Memory.** The receipts record only allocated memory: 121,920 MB at 64 CPUs and 487,802 MB at 128. MaxRSS is not
in any receipt, so no peak-memory figure is claimed. Concurrency is set by the historical `%30` array caps: 7.5
node-equivalents on shared, 30 on regular.

## 6. Total cost

`total = setup + development + N_experiments × per_experiment + independent_verification + retry_allowance`,
then `admitted = total / 0.8`. The quoted production figures contain no margin; the 20% protected reserve is
applied to the whole total.

Admitted node-h at 4 × 1,250 = 5,000 experiments, with pairing not established (S-a included):

| | P1 | P2 | P3 |
|---|---:|---:|---:|
| Optimistic | 288,793 | 575 | 20,353 |
| Conservative | 1,207,226 | 3,518 | 84,560 |
| Wall days at 30 node-eq (optimistic / conservative) | 401 / 1,677 | 0.8 / 4.9 | 28 / 117 |

**One-time setup** (`costs.json` `setup_items`):

| Item | What | node-h (optimistic / conservative) |
|---|---|---:|
| S-r | B's identity-carrying R0, with universe columns, priced here because B left it unpriced: 12 playlists × 2.5 h or the 24 h limit × billing 24/256 (billing ASSUMED) | 2.8 / 27.0 |
| S-a | Matched LightGBM sweep at the central's seed | 24.8 / 93.7 |
| S-b | Selection-complete laterals | 1.3 / 23.8 |
| S-d | M1 generator (ASSUMED) | 2 / 20 |
| S-e | Background statistics | 0 / 64.8 |
| S-f | Overlap factorial | 11.8 / 43.2 |
| S-j | Model-allowance calibration: 3 truths × 202 runs | 35.8 / 196.4 |
| | **Sum** | **78.6 / 469.0** |

- A CV-only R0, without universe columns, at the CV loop's 2 CPU / 8 GB request is 0.4–2.3 node-h.
- None of these items includes the population construction of obstacle 2, which is unpriced.

**Why setup reuse is valid.**
- For P2 and P3 the systematic deltas, event-level support, template statistics and B∓ do not depend on any one
  validation experiment's data draw, once the central recipe is frozen.
- P1 recomputes them per experiment, because the reported procedure does.
- Development is the successor proposal's stage-B pilot, at most 6 node-h of work.

**Sensitivities** (admitted node-h, optimistic / conservative):

| Experiments per case | P1 | P2 | P3 |
|---|---:|---:|---:|
| 300 | 69,396 / 290,275 | 224 / 1,385 | 4,970 / 20,835 |
| 719 (B, 1 case's family) | 166,161 / 694,699 | 379 / 2,326 | 11,755 / 48,941 |
| 1,116 (B's N_design) | 257,846 / 1,077,888 | 526 / 3,217 | 18,183 / 75,571 |
| 1,250 (4-case family) | 288,793 / 1,207,226 | 575 / 3,518 | 20,353 / 84,560 |
| 2,400 (successor proposal) | 554,378 / 2,317,219 | 1,001 / 6,100 | 38,973 / 161,700 |

- **Inner replicas.**

| Inner replicas | P1 optimistic / conservative | P3 optimistic / conservative |
|---:|---:|---:|
| 50 | 189,906 / 802,018 | 20,353 / 84,560 |
| 100 | 209,683 / 883,060 | 40,130 / 165,601 |
| 300 | 288,793 / 1,207,226 | 119,239 / 489,768 |

- **Central-estimator branch** (A §2.4(2); exact unfold from A's FREEZE).
  - Keeping `E_C` adds one exact unfold per experiment, plus a one-time exact rebuild of the matched sweep, its CV
    and a 10-seed exact scan. The exact sweep replaces the LightGBM S-a, which is dropped from this branch's setup.

| | Per exact unfold | One-time rebuild | P2 admitted |
|---|---:|---:|---:|
| Optimistic: A's memory-packed extrapolation | 0.68 | 292 | 5,728 |
| Conservative: as run | 19.31 | 8,298 | 268,936 |

  - Exact universe unfolds carry the same documented universe/CV wall ratio (2.24) as the LightGBM ones. For a
    compute-bound single-threaded job that multiplicative ratio is an upper-side choice; an additive I/O overhead
    of about 0.28 h per unfold would be smaller. (Repair 1, E finding F9: the freeze had 135 / 3,824 and
    5,566 / 263,513, which double-counted S-a and priced exact universes at the CV rate.)

  - A's own prices for the missing transfer operands (`price_for_C`):
    - `P03`, an exact bootstrap: N = 50 about 34–39 node-h; N = 300 about 205–215;
    - `P05`, the exact universes: about 128 node-h if each exact universe unfold costs what the exact CV unfold
      does. At this assessment's universe/CV ratio (2.24, as in the branch above) it is about 285 node-h
      (187 × 0.68 × 2.24 + 0.68). Both are forecasts on A's 0.68 node-h packed extrapolation; no exact
      universe unfold has run (closeout correction 2026-10-09, focused review N2);
    - `P09b`, the exact seed scan: about 7 node-h packed, or 193 unpacked.
- **Pairing.** With a LightGBM central, pairing established versus not changes P2 by 33–141 node-h.

**Range.**
- P1 has a finite range, and it is unaffordable.
- P2 has a finite compute range, but its preconditions are not all priced: obstacle 2's population construction
  (a second production or route G) is not. So its total is INCONCLUSIVE.
- No range exists for an unscoped claim. A guaranteed model-dependence bound (C09) or a response-departure guarantee
  outside the simulated family (C10) has no method, so no finite computation prices it.

## 7. Cost-saving proposals (at most two; neither is admitted)

**S1 — transfer the systematic and ML blocks.**
- *Proposal.* Compute them once per truth case and apply them to every experiment in that case.
- *Populations.* Development experiments for the comparison, separate from validation.
- *Comparison.* On 20 development experiments per case, recompute the full universe and seed blocks.
- *Acceptance limit.* The simultaneous per-functional width ratio ρ = σ_transfer/σ_full stays within [0.95, 1.05].
- *Interval effect* (`costs.json` `shortcut_analytics`):

| ρ | I68 coverage | I95 coverage |
|---|---:|---:|
| 0.95 | 0.658 | 0.937 |
| 1.05 | 0.706 | 0.960 |

  Both stay inside the windows [0.60, 0.80] and [0.90, 0.99].
- *Scope.* Valid only within the compared cases.
- *Cost to establish.* 2,028–7,653 node-h.
- *Admitted savings.* Zero until established.

**S2 — reduce the inner statistical replicas from 300 to 50, with a corrected multiplier.**
- *Proposal.* For σ̂ estimated from N replicas, Gaussian multipliers lose coverage. At N = 50:
  - I68 coverage falls to 0.6778 and I95 to 0.9443;
  - z = 1.0103 and z = 2.0096 restore nominal under normal replicas.
  These are exact integrals over χ²_{N−1}, in `costs.py`. They equal the Student-t results 2F_t(z; N−1) − 1
  and t-quantiles, which scipy 1.15.2 reproduces to within 3e-5 in a local check.
- *Populations and comparison.* The replica normality and χ² scaling must be checked on development replica sets.
  The existing VL170 replicas are a zero-compute candidate.
- *Covariance effect.* A 50-replica covariance has rank ≤ 49. Only per-functional intervals are valid with it, not
  inverse-covariance statistics.
- *Scope.* Data-statistical interval width only. It does not repair the `KNOWN_ISSUES.md` 85 question.
- *Relation to B.* B prices a 50-replica variant as a separate procedure (P-B50, 2,277 node-h).
- *Admitted savings.* Zero until the check is committed.

## 8. Staged route

| Stage | Admission evidence | Authority | Budget | Terminal stop |
|---|---|---|---|---|
| 0. Central estimator | Either measured transfers `E_S → E_C` with declared observables and tolerances (A's `P03`, `P05`, `P09b`), or a recorded change of the quoted central estimator | Joseph: a change of central estimator is reserved to him; the transfer measurements need compute admission | transfers: about 170–350 node-h at A's packed prices with exact universes at the CV rate, or about 330–510 node-h with them at this assessment's universe/CV ratio (`P03` at N = 50 or 300, plus `P05` and `P09b`; forecasts, not timings); the change of estimator costs none | without one of them, no claim about the uncertainty attached to the quoted central (`E_C`), or about the total, is admissible: **stop** for those claims. Work explicitly labelled as about `E_S` (the LightGBM band itself), such as B's N2 diagnostic, does not need stage 0; it needs Joseph's choice to pursue `E_S`-scoped work plus the KI-85 lift |
| 1. Matching | A's FREEZE row outcomes; Audit 2 identity proof; matched sweep at the chosen central (S-a) | none for reads; Joseph for S-a compute | 0 node-h locally; S-a 25–94 node-h (LightGBM) | PAIRING NOT ESTABLISHED, which carries S-a into every later stage |
| 2. Statistical validation | B's frozen design; R0; independent populations (a second production or a validated route G); KI 85 deferral lifted | Joseph | B's figures (13,440–20,862 node-h primary; 7.4 node-h plus R0 for N2) | B's terminal states. A PASS stays statistical-only. NO-GO while obstacle 2 stands |
| 3. Missing-source and method qualification | Constructions for C03 (bound or stream), C05a (selection-complete laterals), M1 generator, X01 (joint throws or cross term), X02/X03 (factorial or bound), C09 development truths | Joseph for compute; A for code under its ownership | setup 79–469 node-h, plus 20% reserve | INCONCLUSIVE if any construction fails its own closure; NO-GO if C05a support cannot be made selection-complete |
| 4. Total-procedure development | Frozen nuisance law, frozen band and B∓, the 24-run pilot, and S1/S2 checks if claimed | Joseph | ≤ 8 node-h pilot (6 work + 2 reserve), or S1's 2,000–7,700 node-h if pursued | pilot failure terminates; no automatic repair |
| 5. Untouched total validation | Custodian-frozen cases, independent populations, seed manifest, ≥ 20% reserve funded | Joseph (an allocation decision) | P2: 575–3,518 node-h at 4 × 1,250, plus the unpriced population construction; P1 not admissible | one final look; validation failure consumes the samples |

## 9. The B↔C exchange

This is the table C supplied at `9204a390`. B adopted the same rates in its §14. These are statistical-only costs
per experiment, with no nuisance overhead (`costs.json` `for_B_statistical_per_experiment_node_h`).

| Per experiment | Optimistic node-h | Conservative node-h |
|---|---:|---:|
| Fixed band, 1 unfold | 0.069 | 0.266 |
| Reconstructed, 1 + 50 unfolds | 3.03 | 11.1 |
| Reconstructed, 1 + 100 unfolds | 5.98 | 21.9 |
| Reconstructed, 1 + 300 unfolds | 17.8 | 65.1 |

**Agreement.**
- B's 13,440 node-h primary reproduces in C's model.
- Both lanes use 0.0591 node-h per production run as the measured optimistic rate.
- Both exclude background-template statistics from the statistical claim. B conditions them out; C carries them
  as C03.

**Differing assumptions, exposed rather than merged:**
1. **Retry and reserve.** B adds a 5% retry and no reserve. C adds a 2–10% retry, 5–10% verification and a
   20% reserve. B's figures are therefore lower bounds on C's admitted totals.
2. **Rate.** B prices at the optimistic rate only. B quotes C's conservative per-experiment figure, which is
   3.7× higher.
3. **Family size.** B sizes for one case (206 functionals). C's total design is four cases, which raises N per
   case from 719 / 1,116 to 823 / 1,250 under B's own criteria.
4. **R0.** C prices it here (S-r). It does not change either verdict.

## 10. Inputs still pending

| From | Item | Effect on C |
|---|---|---|
| A | FREEZE (`9fab26e8`) | **Reconciled**: §2 unchanged; rows `P06`, `P14` and `P17` incorporated; the exact-unfold timing is adopted with its evidence class |
| B | Final (`00f7cff1`, read at repair 1) | **No C row changes.** B's counts (719 / 1,116) and criteria are unchanged. B adds N2 (§16.1: 100 runs, 7.4 node-h) and uses C's CV-only R0 price (0.4–2.3 node-h), for 7.8–9.7 node-h in total. N2 is `E_S`-scoped and statistical-only. It enters no C component and no total |

## 11. Reproduction

```
cd <repo root at this branch>
export TMPDIR=/private/tmp/minerva-uncprep-c-20261008/tmp OMP_NUM_THREADS=4
python3 docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py --check   # exit 0
python3 docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py --n-per-case 1116 --n-cases 1 --out /tmp/x.json
```

- **Environment.** Python 3.12.2 (miniconda), standard library only. It ran in about 5 s on one core.
- **Inputs read.** The three sacct receipts, whose sha256 digests are in `costs.json` `receipts.*.digest`.
- **Not read.** No ROOT product and no cluster resource.
- **Four-case family sizing.** B's `assurance.py` at `f19084f4` was copied to scratch and imported. Its own
  functions (`levels`, `per_test_alpha`, `edges`, `required_n`, `bias_sizing`) were run with
  `DESIGN["n_functionals"]` set to 206 and to 824. B's file was not edited.

## 12. Session record

**Session.**
- Owner model: Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code. Its effort level is not exposed to the session
  as a named level.
- Session id: `17a03aa3-50b8-473b-9903-18bb9b949544`.
- Setup: one owner. No reviewer or worker agent was spawned. The single independent review is in E
  (CAMPAIGN-REVIEW-20260929 §1).

**Commits.**
- Base: `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c`.
- Outputs:
  - `9204a390`, `[uncprep-C] PROVISIONAL`;
  - `d07a3d33`, reconciled with B's PROVISIONAL and A's CONTRACT;
  - this `[uncprep-C] FREEZE` commit.
- Worktree: `MINERvA-OmniFold-uncprep-c-20261008`.
- Branch: `prep/uncertainty-c-total-20261008`, pushed without force, with no PR and no merge.

**Commands and exit codes.**

| Command | Exit | Note |
|---|---|---|
| `costs.py` (writes `costs.json`) | 0 | |
| `costs.py --check` | 0 | before each commit |
| scipy cross-check of the S1/S2 analytics | 0 | max difference 3.0e-5 |
| scratch import of B's `assurance.py` at 206 and 824 functionals | 0 | |
| pre-commit hook on each commit | 0 | 13 of 13 checks passed |

No test suite was run, because C changed no tested code; no skipped test is counted as a pass.

**Environment.** Python 3.12.2 (miniconda, macOS), numpy 1.26.4 and scipy 1.15.2 (the latter only for the
cross-check). `TMPDIR=/private/tmp/minerva-uncprep-c-20261008/tmp`, with the thread cap at 4.

**Resources against C's budget row.**

| Resource | Used | Budget |
|---|---:|---:|
| Active time (06:09Z → 07:00Z, including two waits on peer handoffs) | about 0.9 h | 4 h |
| Local CPU core-hours | < 0.02 | 1 |
| Peak RAM | < 0.2 GiB | 4 GiB |
| New output (C files 132 KB, scratch 84 KB) | < 0.25 MB | 0.5 GiB |
| Cluster node-h, GPU-h, training, toys | 0 | 0 |

- Free disk: 45 GiB at dispatch, 41 GiB at freeze. The volume is shared with other sessions.
- Repair allowance used: 0 of 2.

**Limitations.**
- No ROOT product was read. Per-bin values (the overlaps, `C_U` against the background-aware sweep, flux index
  identity) are specified, not measured.
- Universe-unfold timing is DOCUMENTED, not receipted. Memory packing of exact unfolds is A's extrapolation.
- The R0 billing is ASSUMED.
- The development effort for M1 (analyst time) is not costed.

## For E

Each item below stays deferred. C continues with the rest.

1. **Arithmetic check.** Independently recompute `costs.json`:
   - run `costs.py --check`;
   - re-derive at least one P1, one P2 and one setup row by hand from the receipts;
   - rerun B's `assurance.py` with 824 functionals.
2. **Status wording conflicts** (E routes them; C changes nothing):
   - the 2D status headline says "MEFHC 5-iter lgbm", while the quoted central is `E_C`, exact GBT (A's CONTRACT;
     D's D06);
   - the status lists GEANT among "6 lateral" bands, while the reference calls GEANT weight-only (row C05b);
   - "PPFX index alignment verified (Pearson 0.96)" has no committed receipt (Audit 2).
3. **No governing record is proposed by C.** C supplies no receipt binding, and none of its digests is a
   path+sha256 pair. The receipt digests in `costs.json` are `sha256:`-prefixed strings under a `digest` key.
4. **Joseph's next decision for any claim about the quoted central's uncertainty, or about the total:** the
   central estimator (stage 0). No such claim is admissible before it. An `E_S`-labelled statistical diagnostic
   (B's N2) does not wait on stage 0; it needs Joseph's choice of `E_S`-scoped work plus the KI-85 lift. E composes
   the single next decision.
