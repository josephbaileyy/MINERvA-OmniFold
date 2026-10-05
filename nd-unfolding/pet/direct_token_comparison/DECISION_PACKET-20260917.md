# Decision packet: PET representation experiment

**Nothing is launched.** Design in `COMPARISON_PROPOSAL-20260917.md` (revision 2). This
page is the whole set of approvals needed to start, and nothing here commits the pilot
or the campaign — those are separate decisions after the probe returns.

## What changed since revision 1

* **The arms were wrong and are replaced.** The cap that binds in production is on the
  **generic cluster cloud** (mean 11.09 data / 11.15 MC against a cap of 12), not on a
  typed family, and typed families are uncapped in our code. Revision 1 also omitted the
  actual incumbent. Arms are now four single-factor changes from production: **A**
  generic-only truncated (incumbent), **B** +typed pooled, **C** +typed individual,
  **D** generic aggregate-overflow. Full receive/discard trace in §2.3.
* **"Structural null" is replaced by an argument.** At $K=2$ with distinct `raw_pid`
  features and width 32, the pooled family token represents $(t_0,t_1)$ exactly, so the
  injected target is exactly representable in **both** arms; the sum-decomposition bound
  (Wagstaff et al. 2019, latent dim $\geq$ set size) is satisfied up to $K=32$, so
  expressivity is not the obstruction at production multiplicities either. What differs
  is sequence length (16 vs 17) and per-object attention weighting. The falsifiable
  signature — train-loss parity versus closure gap — is now recorded by the pilot.
* **"A non-tie invalidates the fixture" is replaced by a diagnosis ladder** (§4.3): noise
  envelope, then cap-binding/target-contribution check, then a tail-reshuffle
  re-evaluation of the trained models, then train-loss parity, then width. The fixture is
  only declared wrong if all of them fail.
* **Endpoint, margin and sizing are now one scale.** Relative paired improvement
  throughout, $\delta=10$ points, equivalence band $[-10,+10]$, Bonferroni
  $\alpha=0.0167$ over three co-primary contrasts, and $n$ solved iteratively from the
  **$t$** quantiles at the pilot's between-training-seed sd — 21 seeds if $s$ reaches the
  design target of 12.9 points, 73 at the sd we actually measured. Test-sample uncertainty is capped first
  ($\sigma_{\rm test}\leq2.5$ points, bought with inference) so seeds are not spent
  fixing an evaluation problem.
* **Cost is remeasured at the proposed multiplicities** (local CPU, real model, 5
  interleaved replicates): direct/pooled **training** 1.061 at $K=4$, **1.232** at $K=8$,
  **1.420** at $K=14$, 2.099 at $K=32$; inference 1.281 / 1.283 / 1.382 / 1.646. The
  anchor validates it — the GPU-measured 1.118 training ratio at $K=4$ falls inside the
  local interval and the 1.283 inference ratio sits on the local median. **Pooling's cost
  is nearly flat in $K$** (27.2 → 30.0 ms per step over an eightfold object increase);
  individual routing's is not (27.8 → 65.1 ms), so arm C gets more expensive with exactly
  the multiplicity that would justify it. One caveat recorded in §7: the first version of
  the probe ran replicates in blocks and inverted the $K=14$ point, so ordering had to be
  fixed before any of it was quotable.

## Approvals needed

| # | approval | cost | if declined |
|---|---|---|---|
| **A1** | **Source read, counts + cluster energy.** Two already-pinned manifests (`1B_Data.txt`, `1A_MC.txt`), same fail-closed reader, entries `0..min(200k, tree)` instead of `0..15`. Branches: `cluster_energy_sz`, `cluster_isMuontrack`, `cluster_energy`, `MasterAnaDev_BlobTotalE_sz`, `n_prongs`, `gamma{1,2}_energy`, event keys. Emits histograms only. | ~2 CPU core-h, <50 MiB | fixture multiplicities become assumptions |
| **A1′** | **Or strictly counts-only** — drop `cluster_energy`. | ~1 CPU core-h | the cap contrast reports direction, not production-transferable magnitude (§4.2) |
| **A2** | **Variable-geometry route.** Recommended: **bucketing** — batches of identical typed counts, so every batch is uniform and unpadded and the existing gate applies as-is, no re-scoping. Fallback: re-scope the gate with a gradient-magnitude tolerance. | Route 1: implementation + tests, no compute. Route 2: ~0.5 GPU-h **and a gate change** | Stage 1 stays blocked |
| **A3** | **One bounded GPU probe, 2 jobs:** per-arm cost at the measured production $K$, and the bucketed-geometry preflight. No training to convergence, no closure number. | **≤1 GPU-h** | Stage 2 sizing stays an estimate |
| **A4** | **Ratify the design parameters:** $\delta=10$ points; co-primary B−A, C−A, D−A at $\alpha=0.0167$; equivalence band $\pm10$; $n$ from the pilot rule; $\sigma_{\rm test}\leq2.5$ points. | none | — |
| **A5** | **Implementation, no compute:** write the aggregate-overflow token (cap 12, top 11 + summed four-momentum + tail-mean auxiliary + distinct type code + explicit merged count) with mutation controls; extend the geometry guard to accept a declared all-families-disabled arm A. Frozen matrix artifacts untouched. | none | arms D and A cannot be built |

## Not requested here

* **Stage 1 pilot** — 15 jobs, ceiling **30 GPU-h**. Requested after A1-A3 land, with the
  probe's measured per-job cost.
* **Stage 2 campaign** — ceiling **130 GPU-h**, sized by the pilot's measured $s$. If the
  required $n$ exceeds the ceiling we do not run it and report the question as
  unresolvable at this budget.
* Anything on real-data closure, adoption, covariance, or Gate-6. Rung R6 of the ladder
  — our pipeline against Gregor's — remains unauthorised and is not what this measures.

## Standing constraints I am holding to

No compute launched. The frozen matrix stays frozen — no receipt, criterion or artifact
of it is modified or re-reduced. Synthetic findings stay separate from real-data
adoption. Nothing is sent to Ben or anyone else.
