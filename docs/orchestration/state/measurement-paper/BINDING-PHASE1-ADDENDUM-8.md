# Binding addendum 8: the MP-2 S2/S3 feature contract, frozen with rulings (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §2
(MP2-A).

**The contract under review:** `phase1/mp2/FEATURE-CONTRACT-DRAFT.md` and `feature_contract_draft.json`, sha256
`98141c2f…`, from the session's PR #184.

**CITABLE FOR:** the frozen MP-2 S2/S3 specification and the rulings below.
**NOT CITABLE FOR:** any result. S4 belongs to the combined campaign, under its own contract.

The director reviewed the draft against the six conditions he set. They are met:
- V1–V5 are kept as drafted, with no weight cap. The single fallback feature set is justified by the per-species
  response, not by S0.
- The use of S0 is disclosed.
- Training is on C and H only, and the other nuclei keep r_h, stated as a limitation.
- The analysis conventions apply to the whole rotated final state.
- The support is reported and not redistributed, with no per-cell anchoring.
- The folds are nested for the S3 split, and every seed is declared.

## Rulings on the draft's open items (§9)

| # | item | ruling |
|---|---|---|
| a | S4 nesting | Deferred to the combined-campaign contract. Cross-fitting is the expected choice; that contract states it as a limitation and declares a leakage diagnostic. It does not affect S2 or S3 |
| b | V3 threshold | V2's rule, **declared here before any fit**: χ²/ndf ≤ 1.5 over the bins with at least 20 entries on both sides, and no bin beyond 3σ |
| c | N in V4 | The strict row count, as drafted |
| d | δ_fine in V5 | Per cell, \|δ_M1\| from the frozen `m1_shift` declaration, as drafted |
| e | Primary Δ_hyb reference | H_CH,an, the harmonized-CH hybrid, as drafted. It isolates hybridization from the target and convention effects. H_A7 is reported beside it |
| f | Bagging, subsample 0.8 | Approved. It was added before any real fit, so that V5's seed replicas are informative |
| g | Generator details | An S2 **preflight report**: pseudo-particles, remnants, de-excitation photons, thresholds and the GiBUU ID map on all four samples. It comes before the fits but has no gate. The GiBUU 2p2h struck nucleon is **declared here**: the default mass (1.5 M_n + M_p)/2.5, the analysis's convention for events that are not single-nucleon (`CVUniverse.h:39-44, 397-404`) |

## Other rulings

- **Freeze.** The contract is frozen at the draft's sha256 together with these rulings. Any further change needs a
  committed record before the affected output exists.
- **Cost.** S2 and S3 together, about 2–3.5 CPU node-h, are granted within the phase-1 ceiling (35 CPU and 3 GPU in
  total). They run after the maintenance window: Perlmutter returns 2026-10-27 23:00 PDT at the earliest.
- **Receipts held out of git.** Four receipts cite large cluster-only arrays by bare name, and are held out because
  `verify_receipt_artifacts.py` treats such a citation as missing before it looks at the declared off-area
  directories. Option (i), **keep them held out with their shas recorded**, is chosen. The ordering in the verifier is
  reported to the coordination-tooling owner. It is not changed here.
