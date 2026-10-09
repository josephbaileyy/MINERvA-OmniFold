# Assessment — 2D total-uncertainty feasibility (uncertainty preparation, lane C)

**Status: PROVISIONAL.** It is pushed for the one B↔C exchange. The A-dependent and B-dependent cells are
marked and get reconciled once, after A freezes.

**CITABLE FOR:**
- the component inventory and dispositions in `state/uncertainty-preparation-20261008/c/components.tsv`;
- the four audits in §3;
- the executable cost model `c/costs.py` and its output `c/costs.json`, with operands labelled MEASURED,
  DOCUMENTED, EXTRAPOLATED or ASSUMED;
- the staged route in §8, and what blocks each transition.

**NOT CITABLE FOR:**
- any uncertainty value, coverage result or adoption;
- a change to the quoted 2D construction (`VL170`/`VL172`);
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

**Disposition: NO-GO today.** There are two independent reasons.

1. **Missing methods and constructions.** These are named in §3–§4 and in the TSV:
   - background-template statistics are not propagated at all (C03);
   - the 2D lateral detector bands have CV-selected support only (C05a), and no continuous-shift generator exists
     for nuisance-drawn pseudo-data (M1);
   - the flux × muon-energy cross block is omitted from the adopted sum (X01);
   - response departures outside the simulated family have no method (C10);
   - model dependence can only be given a finite-set allowance, never a guaranteed bound (C09).
2. **Resource.** Validating the procedure as it is actually performed costs **0.55–2.3 million billed CPU
   node-hours** at the provisional experiment count, with every data-dependent width recomputed in every
   experiment (P1 in §5). That is unaffordable by orders of magnitude. For scale, the 2D accounting receipts read
   here record 18.1 (`VL170`), 13.3 (`VL169`) and 7.1 (`KNOWN_ISSUES.md` 85) node-h, and the whole s5p pool used
   253 node-h.

**A finite, defined, scoped route does exist (P2).** It calibrates the quoted total band as a fixed band:
- pseudo-data are drawn under a declared nuisance law at declared truths, scored against a covariance and
  model allowance frozen beforehand;
- its admitted total is **1.0–6.1 thousand node-h**, including a protected 20% reserve, at 4 × 2400
  experiments;
- it is **NOT FEASIBLE today**, because its inputs are the missing constructions above. Their one-time compute
  is small: 76–442 node-h in total. Their method development is not yet done.

P2 validates a narrower claim than P1. That claim is spelled out in §2.

The total disposition is **provisional on A and B**:
- A's pairing decides whether a matched systematic sweep must be rebuilt (setup item S-a);
- B's counts replace the provisional 4 × 2400.

Neither input can turn the P1 conclusion into FEASIBLE: P1 stays above 69,000 node-h even at 300 experiments per
case.

## 2. What "total uncertainty" would mean here

The successor proposal (§4) offers a probabilistic covariance **plus** a signed, bounded model allowance B∓. This
assessment makes the claim explicit, so that validation tests a stated proposition.

- **Probabilistic part: nuisance-averaged frequentist calibration.**
  - Nuisances θ are flux, detector and interaction-model universes. They are drawn from a *declared* law. The MAT
    convention treats ±1σ endpoints as the σ of an implicit Gaussian, and PPFX universes as draws.
  - Data and MC fluctuate by Poisson draws on independent populations (B's design).
  - The claim is that the interval covers the fixed truth at the nominal rate, **averaged over θ under that law**.
    It is not coverage conditional on the actual θ, which no construction here can supply.
  - It is also not a probability statement about the cross section.
- **Model allowance: a sensitivity envelope.** B∓ is the cellwise maximum signed bias, with simultaneous upper
  confidence limits, over a finite, declared development truth set at the fixed simulated response.
  - It is not a probability.
  - It is not a guaranteed bias bound over a truth hull.
  - It is not a bound at the actual data truth.
  - Prior variations remain sensitivity diagnostics and never become a covariance.
- **Response departures** outside the universe parametrization are an explicit, stated assumption (C10). Repeated
  truths under one response do not test them.
- **Two validation claims, of different strength.**

| | P1: reconstructed-interval coverage | P2: fixed-band calibration |
|---|---|---|
| Per experiment | central fit, inner replicas, seeds and all universes are recomputed on the pseudo-data | one unfold; scored against a band frozen before validation |
| What it validates | the procedure | the quoted band, at those truths and under that law |
| Does not validate | — | that the procedure gives correct widths for other data |

  P2 must declare whether the frozen band is transferred in absolute or relative form. `VL169` used per-bin
  σ/mean × fixed truth and disclosed the band-transfer ratio.

## 3. Component inventory and the four audits

`c/components.tsv` has 14 rows: ten components (C01–C10, with C05 split into a and b) and four dependence rows
(X01–X03 and C05's split). Each row records estimand, conditioning, source law, existing bytes, matching CV,
support limitations, covariance convention, correlation partners, required evidence, disposition and evidence.

| Disposition | Rows |
|---|---|
| REUSABLE | C07 |
| MATCHING NEEDED | C01, C02, C04, C05b, C06, C08 (seed), X02, X03 |
| NEW CONSTRUCTION | C03, C05a, C09 (scope-limited) |
| UNRESOLVED | C08 (backend definition, pending A), C10, X01 |

**Audit 1 — target normalization is counted once: CONFIRMED for the standalone construction.**
- The 1.4% rank-1 band is added at one site: `--add-norm 0.014` in `uq/rollup_vl170_adoption.sh:38,48`, built in
  `uq/analyze_universes.py:248-253`.
- None of the 44 bands in `uq/universes_full_list.txt` is a target or normalization band. `NormDISCC` and
  `NormNCRES` are GENIE interaction normalizations.
- Neither the bootstrap nor the ML block adds it.
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
- Each VL170 replica retrains its classifiers at the pinned seed 1 on resampled weights. Each universe unfold
  retrains at seed 42.
- GBDT retraining noise is therefore inside the statistical block (X02) and inside every universe delta (X03).
  The separate ML block (C08) adds it again.
- Different RNG streams do not establish independence of these sources.
- Order-of-magnitude bounds (`costs.json` `overlap_bounds`), assuming iid retraining noise at the seedscan median
  of 0.166%:
  - removing C08 entirely moves the median total from 6.8707% to 6.8687%;
  - the retraining noise implied inside the systematic median is about 0.79% in quadrature, which moves 6.830% to
    6.784%.
- These are illustrative medians, not per-bin values. Neither overlap can explain a material change in the total.
  Both need either a measured factorial (setup S-f) or a written argument carrying this bound.
- The 2026-05-29 seed-varying → pinned-seed bootstrap swap moved √tr C_boot from 1.828e-40 to 1.817e-40, a
  ratio of 1.006. Independent addition of the ML block (√tr 5.061e-41) would predict about 1.038. The observed
  ratio is consistent with overlap. Its sampling resolution, which depends on whether the two sets shared
  bootstrap seeds, was not computed here, so this does not establish the overlap.

**Matching (depends on A).** The quoted blocks come from three estimator configurations:

| Block | Producer | Estimator configuration |
|---|---|---|
| Frozen central | `sbatch_unfold_2d_MEFHC.sh` | no `--estimator`, no `--seed`; driver default `exact` (sklearn GBT, ~19 h per unfold) |
| Statistical replicas | ki84 rebuild | lgbm, `--seed 1` |
| Systematic sweep and its matched CV | `sbatch_unfold_2d_MEFHC_5iter_universes_full{,_CV}.sh` | lgbm, `--seed 42` |
| ML block | `seedscan_lgbm/run_seedscan_lgbm_interactive.sh` | lgbm, seeds 1–10 |

- The ML block's producer is not the `--estimator hist` sbatch launcher that sits beside it.
- D's inventory records the same facts (`d/dependencies.tsv` N09, N12, N13, D05, D06).
- The status headline's "MEFHC 5-iter lgbm" label conflicts with the central launcher. This assessment does not
  pick a label. A's pairing decides which matching cells become REUSABLE.
- Backend choice moves the paper-covariance χ² by about one unit (status, "Methodological band"). It is therefore
  either a definitional choice of the estimator or an unresolved component. Seed scatter does not cover it.

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
  - This is a missing method in the adopted construction. It is not a negligible-by-assertion term.
- **X02/X03, retraining noise.**
  - Measured route: a factorial, either 50 replicas × 4 seeds or a band subset repeated at two seeds (S-f).
  - Bounded route: carry the §3 bound.
- **C06 × C09.** The interaction knobs reweight MC truth and reco together. Each knob's delta therefore mixes a
  response/background change with a prior change. It is part of C06 and is not a substitute for the C09 allowance.
- **Statistical × systematic.** Universe deltas are differences at fixed data, so data-statistical noise cancels
  to first order. In P1 each experiment recomputes them, so no separate cross term is needed. In P2 the band is
  frozen, so the frozen deltas' own statistical noise is part of what P2 calibrates.

## 5. Procedures priced per experiment

The successor proposal's §5 design is 4 cases × 2400 experiments, giving 206 functionals × 4 cases × 2 intervals.
Those are the provisional counts until B's arrive. Costs are billed CPU node-hours, computed as
elapsed × billing/256.

| Procedure | Unfolds per experiment | Optimistic node-h per experiment | Conservative node-h per experiment |
|---|---:|---:|---:|
| P1, reconstructed full: central + 300 inner replicas + 10 seeds + 187 universes, all on the pseudo-data | 498 | 43.2 | 160.9 |
| P2, fixed band: one unfold of nuisance-drawn pseudo-data | 1 | 0.069 | 0.374 |
| P3, shortcut S1+S2: central + 50 inner replicas; systematic and ML blocks transferred | 51 | 3.03 | 11.2 |

- These are complete-procedure counts. A nested 300-replica experiment is not priced as one unfold.

**Measured operands** (`costs.json` `measured`, from committed sacct receipts):

| Workload | node-h per unfold | n |
|---|---:|---:|
| Production bootstrap replica, shared 64 CPUs (ki84 `59410433`) | 0.0591 | 300 |
| Fixed-truth toy, shared 64 CPUs (ki85) | 0.0700 | 98 |
| Fixed-truth toy pilot, regular full node (`VL169`) | 0.198 | 3 |
| Bootstrap replica, regular full node | 0.216 | 1 |

Across all three receipts there are 508 completed jobs and no billed failures. The 95% Clopper–Pearson upper bound
on the failure rate is 0.59%.

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

Storage is 0.06 MB per unfold output (measured: 300 outputs = 18 MB). P1 at 9600 experiments therefore needs
280 GB; P2 needs 0.6 GB.

**Memory.** The receipts record only allocated memory: 121,920 MB at 64 CPUs and 487,802 MB at 128. MaxRSS is not
in any receipt, so no peak-memory figure is claimed. Concurrency is set by the historical `%30` array caps: 7.5
node-equivalents on shared, 30 on regular.

## 6. Total cost

`total = setup + development + N_experiments × per_experiment + independent_verification + retry_allowance`,
then `admitted = total / 0.8`. The quoted production figures contain no margin; the 20% protected reserve is
applied to the whole total.

Admitted node-h at 4 × 2400, with pairing not established (S-a included):

| | P1 | P2 | P3 |
|---|---:|---:|---:|
| Optimistic | 554,374 | 997 | 38,969 |
| Conservative | 2,317,179 | 6,059 | 161,659 |
| Wall days at 30 node-eq (optimistic / conservative) | 770 / 3,218 | 1.4 / 8.4 | 54 / 225 |

**One-time setup** (`costs.json` `setup_items`):

| Item | What | node-h (optimistic / conservative) |
|---|---|---:|
| S-a | Matched sweep, if A finds the pairing not established | 24.8 / 93.7 |
| S-b | Selection-complete laterals | 1.3 / 23.8 |
| S-d | M1 generator (ASSUMED) | 2 / 20 |
| S-e | Background statistics | 0 / 64.8 |
| S-f | Overlap factorial | 11.8 / 43.2 |
| S-j | Model-allowance calibration: 3 truths × 202 runs | 35.8 / 196.4 |
| | **Sum** | **75.8 / 442.0** |

**Why setup reuse is valid.**
- For P2 and P3 the systematic deltas, event-level support, template statistics and B∓ do not depend on any one
  validation experiment's data draw, once the central recipe is frozen.
- For P1 the universes are deliberately recomputed per experiment, because the reported procedure recomputes them.
- Development is the successor proposal's stage-B pilot, at most 6 node-h of work.

**Sensitivities** (admitted node-h, optimistic / conservative):

| Experiments per case | P1 | P2 | P3 |
|---|---:|---:|---:|
| 300 | 69,392 / 290,235 | 220 / 1,345 | 4,967 / 20,795 |
| 1000 | 231,053 / 965,883 | 479 / 2,916 | 16,301 / 67,750 |
| 2400 | 554,374 / 2,317,179 | 997 / 6,059 | 38,969 / 161,659 |

- **Inner replicas.** P1 at 50 / 100 / 300 costs 364,512 / 402,485 / 554,374 optimistic. P3 at 100 costs
  76,942 / 317,259.
- **Central backend.** If the central must be the exact-GBT backend (~19 h per unfold), even P2 costs
  264,642–451,519 node-h. Only an lgbm-class central makes any validation affordable.
- **Pairing.** Pairing established versus not changes P2 by 33–141 node-h.

**Range.**
- P1 has a finite range, and it is unaffordable.
- P2 has a finite range, *conditional on* M1, C03 and X01 being constructed, and on accepting the §2 scoped claim.
  The development effort for M1 is a bounded engineering item, but it is not costed as analyst time here.
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
  These are exact integrals over χ²_{N−1}, in `costs.py`.
- *Populations and comparison.* The replica normality and χ² scaling must be checked on development replica sets.
  The existing VL170 replicas are a zero-compute candidate.
- *Covariance effect.* A 50-replica covariance has rank ≤ 49. Only per-functional intervals are valid with it, not
  inverse-covariance statistics.
- *Scope.* Data-statistical interval width only. It does not repair the `KNOWN_ISSUES.md` 85 question.
- *Admitted savings.* Zero until the check is committed.

## 8. Staged route

| Stage | Admission evidence | Authority | Budget | Terminal stop |
|---|---|---|---|---|
| 1. Matching | A's FREEZE: central backend and seed, the pairings and row maps for C01–C08; Audit 2 identity proof; reported-mask equality across producers (D01) | none beyond this preparation | 0 node-h; local only | PAIRING NOT ESTABLISHED, which adds S-a to every later stage |
| 2. Statistical validation | B's frozen design; independent populations; KI 85 deferral lifted | Joseph (lifts the KI 85 deferral; admits B's experiment and resources) | B's own figure, using `for_B_statistical_per_experiment_node_h` | B's terminal states. A PASS stays statistical-only |
| 3. Missing-source and method qualification | Constructions for C03 (bound or stream), C05a (selection-complete laterals), M1 generator, X01 (joint throws or cross term), X02/X03 (factorial or bound), C09 development truths | Joseph for compute; A for code under its ownership | setup 76–442 node-h, plus 20% reserve | INCONCLUSIVE if any construction fails its own closure; NO-GO if C05a support cannot be made selection-complete |
| 4. Total-procedure development | Frozen nuisance law, frozen band and B∓, the 24-run pilot, and S1/S2 checks if claimed | Joseph | ≤ 8 node-h pilot (6 work + 2 reserve), or S1's 2–7.7k node-h if pursued | pilot failure terminates; no automatic repair |
| 5. Untouched total validation | Custodian-frozen cases, independent populations, seed manifest, ≥ 20% reserve funded | Joseph (an allocation decision) | P2: 1.0–6.1k node-h at 4 × 2400; P1 not admissible | one final look; validation failure consumes the samples |

## 9. Provisional table for B (the one exchange)

These are the per-experiment costs B can price its statistical-only experiment against. They carry no nuisance
overhead (`costs.json` `for_B_statistical_per_experiment_node_h`).

| Per experiment | Optimistic node-h | Conservative node-h |
|---|---:|---:|
| Fixed band, 1 unfold | 0.069 | 0.266 |
| Reconstructed, 1 + 50 unfolds | 3.03 | 11.1 |
| Reconstructed, 1 + 100 unfolds | 5.98 | 21.9 |
| Reconstructed, 1 + 300 unfolds | 17.8 | 65.1 |

- **Consequence.** At 2400 experiments per case and 4 cases, a reconstructed 300-replica statistical test alone
  costs 171,000–625,000 node-h before margins. A fixed-band statistical test costs 660–2,550 node-h.
- **C's procedure assumptions.**
  - The central is lgbm-class. Exact GBT (~19 h per unfold) multiplies every row by 88–321.
  - Pseudo-data are generated in-process, as in `fixed_truth_toy.py`.
  - 206 functionals.
- **Reconciliation.** Run `costs.py --n-per-case N --n-cases K --n-inner R` with B's counts.

## 10. Inputs still pending

| From | Item | Used for | If it does not arrive within budget |
|---|---|---|---|
| A | CONTRACT, then FREEZE: central backend and seed; pairing verdict | C01–C08 matching cells; S-a | Close the matching cells as UNRESOLVED. The P1 NO-GO is unaffected |
| B | PROVISIONAL, then final: procedure, counts and populations | N, the inner replica count, the populations | Keep the successor-proposal counts and label the totals provisional |

## 11. Reproduction

```
cd <repo root at this branch>
export TMPDIR=/private/tmp/minerva-uncprep-c-20261008/tmp OMP_NUM_THREADS=4
python3 docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py --check   # exit 0
python3 docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py --n-per-case 1000 --out /tmp/x.json
```

- **Environment.** Python 3.12.2 (miniconda), standard library only. It ran in about 5 s on one core.
- **Inputs read.** The three sacct receipts, whose sha256 digests are in `costs.json` `receipts.*.digest`.
- **Not read.** No ROOT product and no cluster resource.
