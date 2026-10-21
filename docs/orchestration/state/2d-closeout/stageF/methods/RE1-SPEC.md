# RE-1: the higher-dimensional central values with the refined estimator, and a 2D closure check (specification, frozen before any run)

**Owner:** the paper-tighten lane, as director, 2026-10-20, under
[`DECISION-20261020-joseph-refined-estimator-shorten-delta`](../../../../DECISION-20261020-joseph-refined-estimator-shorten-delta.md).

**CITABLE FOR:** what RE-1 produces, its controls, and its grant.
**NOT CITABLE FOR:**
- any result before its report;
- a change to the adopted 2D result (Joseph's decision);
- any covariance or coverage for configuration (e), which RE-1 does not build.

## 1. Products

- **(P5) Five observables.** The data unfold with configuration (e): deterministic LightGBM OmniFold, 5 iterations,
  100 trees and 8 leaves, with the unbinned negative-weight refinement at 400 trees and 31 leaves, as used for the
  joint tests' observed statistic (methods paper Table IV).
  - **If the existing data product is the full fine-grid result of configuration (e),** it is reused, after its
    configuration and sha256 are verified against its record. That is the s5p data unfold
    (`runs/s2/num/data/data_b-_j-.npz` or the record's equivalent; `s5n_pseudo.py:189-204`).
  - **Otherwise** it is rerun with the frozen code path.
- **(P3, P4) Three and four observables.** Data unfolds with the same refinement settings, by the frozen 3D/4D code
  paths, if those paths support the refinement unchanged. If they do not, RE-1 reports that, and the 3D/4D central
  values stay in configuration (a), with their purity bias stated.
- **(F) Figures.** The deliverables' higher-dimensional central-value figures and quoted numbers are regenerated from
  P3–P5 by their existing producers, changing only the input product.
- **(C2) 2D closure check (descriptive).** Pseudo-experiments at nominal truth, background included, unfolded in two
  dimensions:
  - (i) with the adopted 2D estimator and purity subtraction;
  - (ii) with the same estimator and the refinement (400/31).

  Seeds, count and code are declared in a file before running: at least 20 pseudo-experiments per arm, the same seeds
  in both arms, and pseudo-data drawn as in the s5c/s5n studies.
  - Readout: the per-bin mean residual and its SE for each arm, and the difference between the arms in units of the
    adopted 2D statistical σ and of the total σ.

## 2. Controls (each before its product is used)

- **(K1)** Each rerun of configuration (e) on the frozen code reproduces a recorded configuration (e) product bitwise,
  or to the recorded rounding level, for one declared case.
- **(K2)** Arm (i) of C2 reproduces the recorded purity 2D closure behaviour, where a record exists. Otherwise it is
  reported only.
- **(K3)** The figure producers reproduce the current figures bitwise from the current input product before the
  input is swapped.

## 3. Outcomes

- **P3–P5 and F:** these become the central-value inputs for the next deliverables pass. No decision is attached.
- **C2 is descriptive.** If any 2D bin's arm difference exceeds 1 statistical σ, or the integrated difference
  exceeds 0.5%, the report flags it for Joseph's decision on the adopted 2D result. Below those, the report says the
  refinement does not change the 2D result at that level.

## 4. Grant

- **Ceiling:** at most 30 CPU node-h on m3246, regular or debug QOS, each job under 12 h.
- **Delta:** may be used after a reproduction control there (K1 on Delta).
- **Deadline:** Perlmutter work must finish before the 2026-10-21 04:00 PDT cutoff, otherwise it is deferred.
- **Ledger:** every job id with its charge.
- **Outputs:** pscratch `/pscratch/sd/j/josephrb/methods-paper/re1-20261020/`, or Delta scratch, with nothing written
  to CFS.
