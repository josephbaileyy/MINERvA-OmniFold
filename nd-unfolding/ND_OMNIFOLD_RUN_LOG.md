# N-D OmniFold run log

## 2026-10-05 — PET final-design study: terminal outcome NO_ELIGIBLE_DESIGN (frozen rules; independent review closed)

- **Coverage of H2S1T24 K5** (Amendments 5, 6; 720 development-tilt members, B = 6): **C1 FAIL, C4 FAIL** — the
  interval procedure is over-conservative (pooled 68 % coverage 0.896, LB 0.858, vs ≤ 0.80; 95 % 0.990; half-widths
  1.3–1.7 × the calibrated limit in six of seven E_avail bins); C2, C3 PASS. Not uniformly conservative: the
  low-acceptance region under-covers (68 % 0.257, 95 % 0.789), ungated by C3. Same against the FB population target;
  mechanism not established. Reproduced from the raw member histograms.
- **Terminal:** with L128S1T24 K4 ineligible on B2 (look 1), `decide.py` gives **NO_ELIGIBLE_DESIGN**; C5 skipped
  (3a.5), D4c compute stopped. H2S1T24's point estimator passes every §6.1–6.3 rule (R_E0 0.895, +0.589 over CTL).
  The §11 repair (DEV-calibrated interval, RB revalidation, ≈ 3.2 k A100-h) is an owner decision. Study total
  3,376.6 A100-h. Evidence `pet/final_design/results/final/`; report §6–8; decision record.
- **Independent review** (Astra High, read-only, 2 cycles): every number and the outcome reproduced; the provenance
  gate was repaired (it had been declared, not checked) and five reporting statements corrected, with no verdict
  change (`pet/final_design/REVIEW_DISPOSITION-DECISION-20261005.md`). VALIDATION_LEDGER VL164–VL167 (added at integration with `main`).

## 2026-10-01 — PET final-design study: look 1 decided; coverage of H2S1T24 K5 running (blinded; in progress)

- **Look 1 (Amendment 4 UNBLIND after 944/944 rows; decision `pet/final_design/results/final/decision_look1.json`,
  commit `96e6a412`):** L128S1T24 K4 **INELIGIBLE on B2 — point-decided, statistically unresolved** (D4d n down,
  residual − injected L1 0.0122, 95 % 0.0064–0.0181, vs ≤ 0.010; every other rule passes). H2S1T24 K5 passes every
  §6.1–6.3 rule (R_E0 0.895, simultaneous LB 0.876; its own B2 0.0097 is also unresolved); coverage pending. The B2
  difference between the finalists is not resolved by this comparison; neither superiority nor equivalence is claimed.
  No look 2. FB cost 1.768 / 1.517 A100-h per unfolding (compact not cheaper).
- **Report-only additions after a coordinating review (two cycles, closed):** B1 common-panel dependence analysis
  (a dependence-aware ≤ 0.10 per-unit failure probability is not established); FB population targets (designated
  endpoints within 0.0021 of like-for-like); unblinding bound to each group (Amendment 5b, controls in
  `test_pfd_unblind_gate.py`); terminal review brief `REVIEW_BRIEF-DECISION-20261001.md`.
- **Coverage (Amendment 5):** 720 development-tilt + 360 D4c-up members of H2S1T24 K5 (B = 6), blinded; ≈ 1.9 k
  A100-h. 648/720 at 2026-10-05 03:42Z. Study total 2,087 A100-h at 2026-09-30 23:22Z.

## 2026-09-27 — PET final-design study: finalists re-frozen after the reproducibility repair; final bank running (blinded; in progress)

- **Reproducibility repair (Amendments 3b, 3b-bis):** the estimator-seed sd of the primary recovery at fixed events is
  0.054–0.095 for every design with the 8-epoch truth step and for both 16-epoch designs (limit 0.05); the 24-epoch
  truth step brings it to **0.037 (H2S1T24 K5)** and **0.043 (L128S1T24 K4)**. PET2 is closed on its screens (the
  annealed pretrained arm is stable but its proton topology stays ≤ 0.225 < 0.25). The step-2 ensemble fallback was
  smoke-tested and started early, then stopped unneeded.
- **Finalists (Amendments 3c, 3d; before any final-bank score):** compact H2S1T24 K5, large L128S1T24 K4; anchors CTL
  K3, C K3. Measured cost 1.77 / 1.49 A100-h per unfolding: the compact design is not cheaper.
- **Sizing (3e):** n_F = 60 (capped; the finalists' E0 non-inferiority needs ≈ 250 draws: a quantified limit).
  FINAL draws 0–59 and the 21-case library are running blinded. Study total 683 A100-h (2026-09-27 14:14Z).

## 2026-09-26 — PET final-design study: stages S2–S3 (large designs, reviews, sizing, N2 finding; in progress)

Development and sizing evidence only (DEV bank); final-bank runs execute blinded and nothing is scored on FB.
- **Reviews:** implementation (1 BLOCK + 5 MAJOR fixed), statistical design (1 BLOCK + 7 MAJOR fixed; Amendment 2c),
  scientific scope (`final_design/REVIEW_DISPOSITION-SCOPE-20260926.md`; Amendment 3a: terminal practical default,
  cost at declared packing, N1 scope ruled on E9's text, E4/E5 sizing group, coverage order, futility, bank-effect
  bound, cost-part repair; finalist-rule addendum with completeness, S-N1 at K\* and the between-design step in code).
- **Larger/pretrained designs:** enlarged step-1 PETs (0.25 M, 0.97 M parameters) match the 47 k one at 8 epochs;
  PET2-small pretrained is unstable in the loop from k = 4 under the declared constant rate (step-1 weights 334–1,217
  at k = 4, divergence at k = 5) while PET2-scratch is stable but fails the topology screen; a matched annealed-rate
  arm is running. AUSSIE closed by its matched test (12/12 losses). Measured costs per unfolding: H2S1 K5 0.88,
  L128S1 K5 ≈ 1.0, P2preS1 K4 2.23 A100-h.
- **Post-hoc recomputation:** 15 stale dev1 files recomputed; predecessor files reproduce exactly; the compact choice
  (H2S1 K = 5) holds on complete evidence.
- **Sizing pilot** (`final_design/sizing/SIZING-20260926.md`, provisional): n_F = 30; E4/E5 library draws at the cap 60
  (E4 non-inferiority H2S1 − L128S1 would need 1,770 draws: a quantified limit).
- **N2 finding (Amendment 3b):** estimator-seed sd of the primary recovery at fixed events 0.095 (H2S1) / 0.091
  (L128S1) against the frozen 0.05, located in the 8-epoch truth step; a bounded repair arm (24-epoch truth step,
  16-epoch designs; 64 runs) runs before both packages are re-frozen with an S-N2 screen. Study total 314.8 A100-h.

## 2026-09-26 — PET final-design study: stages S0–S1 (capacity, banks, diagnostics, development screen; in progress)

Authorization `docs/orchestration/AUTHORIZATION-20260925-pet-final-design.md` (Joseph's 2026-09-25 grant,
verbatim); protocol `nd-unfolding/pet/final_design/PROTOCOL-20260925.md` (decision table frozen before any
successor run; Amendment 1: DEV-bank q3 quartiles). Branch `pet-final-design-20260925` from
`pet-improvement-20260922` @ `9368ec9e`. Simulation only; PET stays diagnostic; nothing adopted; historical
thresholds, verdicts and the predecessor's disposition unchanged. **All results below are development
evidence (DEV bank), not confirmatory.**

- **Capacity** (`final_design/CAPACITY-20260925.md`): 4,061,737 inventory rows were never drawn into a scored
  predecessor run (3.4 historical-size replicates); no further same-model simulation exists. Frozen banks
  (`banks/BANK_MANIFEST.json`, job 58880785; 46/46 predecessor draw digests reproduced): DEV 45,089,191,
  FB 2,646,891 (final bank, sealed), RB 1,414,846 (reserve, sealed). Final inference will be conditional on
  the banks.
- **Failure localization** (`final_design/DIAGNOSTICS-20260925.md`; post-hoc analysis of the predecessor's 81
  runs, job 58879830, reproducing every committed score to 1e-9; 19 bounded step-2 fits, jobs 58880466/
  58886796): the multiplicity injections barely move `E_avail` (D4d 0.011 L1), so C's "neutron failure" is a
  near-zero-injection artifact while B's is real; under the proton change the baseline detector step does not
  transmit the hadron-content change (stored reco cloud capped at 12 clusters in 85.5 % of selected events);
  given the exact weights the truth step learns it (categorical PDG 0.87–0.97) and extrapolates to misses, and
  given C's real pull it recovers only what the pull carries (≈0.02).
- **Development screen** (dev1: 64 runs; dev2L: 12; dev2S partial; seed-paired with the predecessor on the same
  events): C + categorical truth PDG + detector reco summaries with a constant per-iteration learning rate
  (H2S1) passes the committed development screens at k = 5 (dev tilt 0.906, proton topology 0.39, neutron-case
  `E_avail` residual 0.020 ≤ 0.021); with the forced 1e-5 schedule (H2) the same inputs fail the neutron screen
  from k = 3; enlarging the step-1 PET to 0.25 M / 0.97 M parameters at 8 epochs changes nothing resolvable.
  AUSSIE closed at scalar level by its matched stress test (loses robustness and stability in 12/12 matched
  comparisons; `scalar/SCALAR_AUSSIE_MATCHED-20260925.md`).
- **In progress:** PET2-small pretrained vs scratch (path verified: 176/176 pretrained tensors at the first
  optimizer step; materialization byte-identical to the historical cache), 16-epoch arms, sizing pilot S3P.
- **Resources so far:** 123.9 A100-h, 0.23 CPU node-h (`final_design/resources/RESOURCE_LEDGER.tsv`, 08:45Z).

## 2026-09-25 — PET improvement campaign: confirmatory stage complete (FINAL, STRESS; coverage not run)

Same campaign and authorization as the entry below. Simulation only; PET stays diagnostic; the historical thresholds
and `NEITHER_ELIGIBLE / NO_SELECTION` verdict are unchanged; nothing is adopted.

- **FINAL** (fresh pool F, 12 independent replicates × CTL/A, B, C = 36 A100 runs, debug-queue chains
  58808974 … 58839336; `improvement_campaign/confirm/CONFIRM_RESULTS.md`): mean recovery CTL 0.316, A (k = 10) 0.505,
  B (C2 inputs, k = 10) 0.569, **C (efficiency-corrected step 2, k = 10) 0.786** (lower 95 % 0.763). All three
  superior to CTL, non-inferior and past the +0.04 switching margin after Holm (largest p 1.8e-9). Adequate by the
  protocol's mean rule: B@10, C@10, C@3; only C@10's lower bound clears the 0.556 floor.
- **STRESS** (pool T, 6 cases × 2 replicates × 3 runs = 36): C@10 moves away from the target under proton
  multiplicity ×1.3 on both replicates (R −0.19) and under neutron multiplicity ×1.3 on one; B@10 under neutron
  multiplicity on both (−1.59, −0.90). The five truth cases are reco-identifiable (E1); the R1+D1 case was not
  measured. Two replicates per case. C at k = 3 never moves away.
- **Coverage: not run** — amendment 2's condition (adequate at K* = 10 and no moves-away on an identifiable case) is
  met by no frozen candidate. C at k = 3 would pass both as observed but is not the declared coverage point.
- **Provenance:** 81 run directories strict-audited CLEAN (`confirm/results/audit_locks-20260925T1244Z.json`); two
  concurrently scored FINAL runs re-scored identically (CPU job 58843833). Independent review round 2 (codex-school
  lane, approved by Joseph): FINAL part 3 MAJOR + 1 MINOR, all dispositioned without changing a number; STRESS part 4 MAJOR + 2 MINOR (claims scoped, no number changed)
  (`improvement_campaign/REVIEW_DISPOSITION-ROUND2-20260925.md`).
- **Resources:** campaign total 268.3 GPU-h and 9,221 CPU-core-h on m3246 / m3246_g
  (`improvement_campaign/RESOURCE_LEDGER.tsv`).
- **Conclusion** (report §12): the historical shortfall is recoverable within the closure, but the large gain rests
  on a configuration (C at K*) that moves away under identifiable hadron-content changes, cause not established on
  the PET path; no frozen candidate at K* is both adequate and robust.

## 2026-09-24 — PET improvement campaign: diagnosis complete, confirmatory stage running

Campaign `nd-unfolding/pet/improvement_campaign/` on branch `pet-improvement-20260922` (Joseph's 2026-09-22
authorization, `docs/orchestration/AUTHORIZATION-20260922-pet-improvement-campaign.md`). PET stays diagnostic;
the historical comparison's thresholds and `NEITHER_ELIGIBLE / NO_SELECTION` verdict are unchanged. Development
evidence (DEV halves), not confirmatory:

- **Runtime audit** (jobs 58742194/58742195, `phase_a/INTENDED_VS_EXECUTED-20260922.md`): both suspected recipe
  discrepancies CONFIRMED — Gregor's arm ran Horovod-wrapped Keras Adam, not the declared TorchAdamW recipe; the
  declared-identical step 2 ran at batch 2048 vs 512, lr 1e-4 vs 4e-4, on a different validation subset. Every fit
  after iteration 0 ran at 1e-5; early stopping was inert (last-epoch weights handed on); the truth cloud carries
  raw PDG codes.
- **Scalar references** (`phase_b/scalar/SCALAR_REFERENCES-20260922.md`): no carry-misses estimator reaches the
  0.556 floor at k = 3 (IBU + reco E_avail 0.472, GBDT 0.412); recovery still rising at k = 3; the 0.695 reference
  is computed on (pT, p‖) cells, not the scored seven-bin spectrum (its own model on the scored object: 0.523).
- **PET diagnostics** (`phase_b/pet/PET_DIAGNOSTICS-20260922.md`, 35+ A100-h): driver reproduces the historical
  result (0.311 ± 0.028 vs 0.304 ± 0.014); truth PET learns the supplied tilt to 0.90–0.95; step 1 closes 94 % of
  the reco E_avail marginal by k = 10; historical recipe 0.334 (k=3) → 0.506 (k=10); efficiency-corrected step 2
  0.608 → 0.817 (+0.310 paired); reco energy summaries at step 1 +0.112 at k = 3; best-validation epoch −0.054.
- **Robustness** (`phase_e/PHASE_E_SCALAR-20260922.md`): efficiency correction wins on E_avail tilts and fails when
  a distortion changes the event mix inside a truth bin (NuWro variant −0.20); the neutron hidden-variable test
  defeats every estimator; ±5 % hadronic scale moves recovery ±0.06.
- **Confirmatory stage** (protocol amendments 2–3): candidates frozen before any fresh-pool row was read; PILOT
  (pool P) done and reported separately; FINAL (pool F, n = 12, sized before pool F was read) and the PET stress set
  (pool T) running. An independent cross-model review found a non-atomic run lock (fixed with flock; one suspect run
  quarantined and rerun) and nine over-strong or unprovenanced claims (all corrected;
  `improvement_campaign/REVIEW_DISPOSITION-20260924.md`).

## 2026-09-17 — per-arm inference cost measured

First attempt `58461843` FAILED on `timeout` (exit 124, 35 min, no receipt) from a
sizing error of mine: four 250k-row fixture builds at ~100 s each plus 78 full passes.
Matrix receipts verified untouched and the `NO_PASS` result re-reduced identically.
Resized on Joseph's decision to 50,000 rows with a single shared fixture build.

Second attempt `58467879` **COMPLETED** (`0:0`, 408 s) with **all five acceptance
criteria passing** on a real GPU at the bound precision. Individual tokens cost
**1.283x** pooled at inference (12,676 vs 9,882 events/s), consistent to three decimals
across three trained models, worst coefficient of variation 0.0203. Preprocessing
(18.7 s, once) and model loading (~0.17-0.25 s) are reported separately and excluded
from throughput. Cost only: it gates nothing and says nothing about accuracy.

## 2026-09-17 — frozen routing matrix complete: NO_PASS, and underpowered

Array `58397664` completed all 24 tasks `COMPLETED 0:0`. 24 receipts, 144 artifacts with
matching digests, 24 guard records with no allowances, and `covered_geometry` confirming
zero padded positions in every job. A Perlmutter maintenance outage paused the array
mid-run without requeueing or cancelling anything.

Frozen criteria: **NO_PASS**, 142 of 146 checks passing. The paired injected improvement
favouring individual-object tokens is median **+9.7%**, mean **+0.8%**, six of eight
seeds favourable, 95% interval **[-20.7%, +22.4%]**, paired t **p = 0.50**. Two criteria
failed (`favorable_seeds`, `material_paired_gain`) and, separately, `shuffle-71` failed
both projection-difference checks marginally (0.0119 against a 0.01 limit; absolute
errors well inside 0.05).

**The design is underpowered for its own criterion**: with the observed seed-to-seed sd
of 25.8 percentage points, detecting the required +5% effect at 80% power needs about
**209 paired seeds**, not eight. Training cost is the one clean result: direct costs
**1.118x** pooled (median over 24 jobs, 1.026-1.137, Wilcoxon `p = 1.2e-07`). Per-arm
inference is not instrumented by the frozen producer and is not reported.
[Result, statistics and safeguard detail](pet/direct_token_comparison/REPORT_FOR_BEN.md).

## 2026-09-16 — calibration passed; frozen 24-job matrix released and submitted

Job `58395631` COMPLETED (ExitCode `0:0`, 426 s). The amended GPU preflight ran all
eight case/routing pairs on a real GPU: seven PASS, and `variable/direct` recorded as
`FAILED-STRESS` under Joseph's 2026-09-16 gate-scope decision, with the receipt verdict
`PASS-WITH-RECORDED-STRESS-FAILURE` so the word itself carries the failure. `masked` and
`empty` had never been reached before and pass on both routes. The recorded stress
discrepancy is bit-identical to `58354898`'s, so it is deterministic. Cluster tests
`69 passed, 10 subtests passed` and `40 passed`.

`evaluate_calibration.py` returned **PASS** on all seven 20% headroom gates: job 2.533 h
against 9.6, campaign 60.79 GPU-hours, host 30.98 GiB against 44.8, per job 1.344 GiB
against 3.2. Charge is now 1,447 conservative seconds. The frozen matrix was therefore
deployed at `d98d94cc` — scientific code byte-identical to the calibrated `a0f5c274` —
and submitted as array `58396676`, 24 real rows. No learning result exists yet.
[Calibration evidence](pet/direct_token_comparison/CALIBRATION_RESULT-20260916.md).

## 2026-09-15 — amended GPU preflight failed; calibration never started

Job `58354898` FAILED (ExitCode `1:0`, 279 parent seconds). The cluster suite
(69 tests, 10 subtests, 25 adversarial), the eight-pair original-sequence CPU
initialization capture and every import-guard record passed first. The GPU preflight
reached four of eight pairs: `nominal/pooled`, `nominal/direct` and `variable/pooled`
passed; `variable/direct` failed at `weight_24`, recorded by the run's own inventory
as `multi_head_attention/query/kernel`, `max_abs=1.443e-04` (step 1) and `1.549e-04`
(step 2). That tensor is not the approved key-bias exemption, whose rationale is
softmax shift invariance the query kernel does not have. Calibration did not start,
so no 20% headroom verdict exists, the frozen 24-job matrix stays unreleased and the
specified overflow contrast cannot execute. No retry was submitted or authorized.
Conservative charge is now 1,021 seconds (742 prior + 279).
[Terminal evidence](pet/direct_token_comparison/AMENDED_RESULT-20260915.md).

## 2026-09-15 — amended comparison preflight prepared

Complete CPU preflight/reload and original-sequence initialization readback pass;
69 regression tests, 10 subtests and 25 adversarial tests pass. The next bounded
GPU attempt is covered by the continuation authorization. Six prior allocations
remain 742 conservative seconds; no new job has launched at this preparation
point. [Bound preparation](pet/direct_token_comparison/AMENDED_PREPARATION-20260915.md).

## 2026-09-15 — optimizer diagnostic completed; gate amendment proposed

Job `58320923` completed (216 parent / 219 conservative seconds). All eight
instrumentation and same-device replay checks are exact. The captured masked/direct
failure is two attention key-bias components: Adam amplifies tiny native gradient
differences; common-operand CPU/GPU replay and all predictions pass unchanged
thresholds. The historical variable/pooled failure remains unverified because
initialization/checkpoint interleaving differs after the first model pair.
[Exact result and verified evidence](pet/direct_token_comparison/OPTIMIZER_RESULT-20260915.md).
Six allocations total 742 conservative seconds (0.206111 GPU-hours / 6.595556
reserved CPU-hours), before preparation/accounting. No allocation is running,
no calibration/matrix was launched, and the [gate amendment](pet/direct_token_comparison/OPTIMIZER_GATE_PROPOSAL-20260915.md)
is proposed only. The current acceptance rule and training block remain.


## 2026-09-15 — PET optimizer diagnostic authorized and submitted

Job `58320923`, clean standalone `98fde50e`, follows the user's explicit new
allocation approval. Capture-first instrumentation matches all eight CPU cases
exactly; 69 tests, 10 subtests and two arithmetic tests pass. The 20-minute
A100 diagnostic preserves unchanged scientific code and acceptance tolerances.
[Authorization](pet/direct_token_comparison/OPTIMIZER_AUTHORIZATION-20260915.md)
and [submission](pet/direct_token_comparison/execution_runs/20260915-optimizer/submission.json).
No learning comparison or calibration is released.


## 2026-09-15 — full-FP32 attempt failed; execution stopped

Job `58301971` passed 69 tests plus 10 subtests and both nominal GPU model cases,
then failed an updated-weight comparison in variable/pooled (inferred from loop
order). Maximum reported difference: `1.204535385568306e-5`; cause unresolved.
Calibration and full matrix were not reached. No retry is authorized.
[Terminal result and verified evidence](pet/direct_token_comparison/FP32_RESULT-20260915.md).
All five allocations total 523 conservative seconds, 0.145278 GPU-hours and
4.648889 reserved CPU-hours, before preparation/accounting CPU.


## 2026-09-14 — PET full-FP32 policy prepared

Implemented uniform precision setup/verification for the synthetic runner,
preflight, reload and calibration. Local 69-test/10-subtest validation and all
eight CPU model/case comparisons pass; exact evidence and the pending 110-minute
GPU proposal are routed from `pet/direct_token_comparison/FP32_PREPARATION-20260914.md`.
No new allocation, source access, calibration or learning comparison occurred.


## 2026-09-14 — PET numerical diagnostic completed

Authorized job `58277208`, clean execution revision `6298efc2`, completed in
105 seconds. TF32-on reproduces the failed pooled maximum; TF32-off passes the
unchanged component tolerance. Exact measurements, historical-weight qualification,
float64 comparisons and verified CFS/archive inventory are recorded in
`pet/direct_token_comparison/NUMERICAL_RESULT-20260914.md`. All four allocations
sum to 395 conservative seconds. No calibration, training, precision-policy
adoption, real-source access, covariance or Gate-6 work occurred.


## 2026-09-13 — PET pooled numerical diagnostic prepared locally

Completed the numerical capture/reduction setup following GPU failure `58240587`.
The source-bound CPU rehearsal, exact archived-fixture provenance, reconstructed
weight qualification, test results and read-back archive are routed from
`pet/direct_token_comparison/NUMERICAL_PREPARATION-20260913.md`. No GPU allocation,
calibration, scientific matrix or source access occurred. The separate 20-minute
diagnostic proposal remains pending and has no automatic training continuation.


## 2026-09-11 — CFS preservation and documentary follow-up

The completed PET source-audit output at `30de7f64` now has a verified CFS copy.
All 16,915 files (283,225,129 bytes) were copied after checking all 16,899
receipt-bound artifacts and four accounting-bound auxiliary files. Destination
readback hashes equal the complete source inventory both before and after the
copy. Scratch was retained; no ROOT source was opened. Exact paths, executable
preserver, inventory hashes and recovery procedure are in
`pet/SOURCE_AUDIT_PRESERVATION-20260911.md` and its linked committed records.

`pet/SOURCE_AUDIT_SEMANTIC_FOLLOWUP-20260911.md` traces the 10,000 ns premise to
the curated correspondence and notes that the existing proposed group split
already keeps repeated keys together. It includes an unsent producer inquiry
for time semantics, row granularity, release and object provenance. No bounds,
verdicts, grouping rule, selection, normalization or training changed. Mapping
PASS, semantic DISCREPANCY and the unresolved release/object-family gates stand.


## 2026-09-10 — repaired PET real-source audit

Under Joseph's single-attempt grant, recorded verbatim in
`pet/SOURCE_AUDIT_REPAIRED_AUTHORIZATION-20260910.md`, the audit ran from a clean detached clone
of `ca34a03a` (bindings `fea412de…`, authorization JSON `4e1b9b85…`). It ran on Perlmutter
allocation `58186616`: `shared_interactive`, 2 CPUs requested and 6 reserved, 8 GiB, 15 minutes.
The step used two CPUs. Allocation and step are both `COMPLETED 0:0`, elapsed 7 minutes 55
seconds. Before source access, cluster-main freshness was `FRESH`, the queue was empty,
`--check-preparation` passed, and the runtime pins and output-root absence were verified.

The audit read the data and MC sources over entries `[0,4096)` with 75 branches: 8,192 rows and
512 chunks, no exceptions, empty logs. Peak observed usage was four threads and 1,219,506,176
bytes RSS; output was 283,206,787 bytes. Verdicts:

- `mapping=PASS`: all six mandatory checks.
- `semantic=DISCREPANCY`: five finite `prong_time` values above 10,000, at data entries 2121,
  2704, 3418 and 3867 and at MC entry 3654. Every other correspondence check passes.
- `release=RELEASE_UNVERIFIED`.
- All four object families `UNRESOLVED`.

Records:

- `accounting.json` SHA-256: `3bb911e6be1e83209c94a0d47ed6f79ddaddd85d84998444913cfcd591a49543`.
- `receipt.json` SHA-256: `5e8d545b6a8b45ed1872852417c13518472b0fbb07832faf78c39406e153b3da`.
- All 16,899 receipt-bound artifacts were rehashed remotely with no mismatch.
- The transferred subset matches its remote digests. It is preserved under
  `pet/source_audit_runs/20260910-repaired/` with `preservation-manifest.json`.

This is fixed-source diagnostic telemetry. No normalization, training, covariance, retry or
Gate-6 action followed. The grant is consumed. `VALIDATION_LEDGER.md` is unchanged because no
ledger-class quantity was measured.

## 2026-09-10 — complete synthetic runtime preflight

Preparation `ca34a03a` installs the authorized four-thread ceiling and compares
identical prepared features and weights against float64 rounding budgets. Linux
allocation `58178592` and its two-CPU step both complete with exit `0:0`; all
8,192 fake rows and 512 typed chunks pass. Peak observed process resources are
four threads and 993,112,064 bytes RSS. The scheduler rounds the two-CPU request
to six reserved CPUs with 8 GiB memory, within the standing reservation ceiling.
Elapsed allocation time is 5 minutes 11 seconds. The unchanged import guard
reports no foreign-checkout imports. ROOT is imported but no ROOT source opens.

`pet/runtime_runs/20260910/linux-roundoff/preservation-manifest.json` binds the
closed receipts, runtime summary, launcher scripts, scheduler and clean-checkout
records. Transfer digests and complete contiguous entry lists were checked;
`verification.json` records that scope. The source launcher's final accounting
writer is not exercised by this fake-reader probe. The 67-test audit suite and
source lint, formatting and targeted strict typing checks pass. This completes
synthetic runtime validation only; another source run still needs a separately
bound authorization. PET pairing, covariance and Gate-6 restrictions are unchanged.


## 2026-09-10 — synthetic runtime investigation

`f59d8170` adds a full fake-reader runtime preflight; `10deb714` reports
numerical differences and samples resources after failed forward checks. The
local SciPy 1.16.3 environment completes all 8,192 synthetic rows. Linux job
`58168872` clears imports but fails forward agreement; job `58174544` measures
the same discrepancy with both oneDNN settings and four process threads against
the two-thread ceiling. Both allocations are terminal. The original thresholds
and guard remain intact; no source-read or scientific acceptance follows.

`pet/SOURCE_AUDIT_RUNTIME-20260910.md` records the diagnosis, exact synthetic
qualification and pending contract decision. Receipts, guard inventories and
scheduler observations are preserved under `pet/runtime_runs/20260910/`, bound
by its preservation manifest. No ROOT source access, fitting or training occurred.


## 2026-09-10 — bounded PET v2 source audit interrupted

The attempt at `58832843`, authorized by
`pet/SOURCE_AUDIT_EXECUTION-20260910.md`, stopped at the first data row when the
import guard refused NumPy testing utilities launching `lscpu`. No complete
receipt, accounting file or typed shard exists. Allocation `58164405` is
`COMPLETED`; source step `.2` is `FAILED`, exit `3:0`.

The original partial artifacts, remote hash comparison and scheduler observation
are bound by `pet/source_audit_runs/20260910/recovery-manifest.json` and explained
in `pet/SOURCE_AUDIT_INTERRUPTION-20260910.md`. The runtime repair and its tests
are local software preparation; there was no additional ROOT read, allocation,
normalization or training. Further source execution requires a newly bound grant.


The complete pre-compaction chronology is frozen at
`evidence/prepublication-2026-08-20-0b329e8a` under this exact path:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:nd-unfolding/ND_OMNIFOLD_RUN_LOG.md
```

Read `ND_OMNIFOLD_STATUS.md` for current scalar/PET/FPS state,
`PET_UQ_REMEDIATION_STATUS.md` for the live PET DAG, and `VALIDATION_LEDGER.md` for verified
numbers. The tag is historical evidence, not scientific adoption.

## Post-freeze chronology

Append only committed post-2026-08-20 events here; keep current state in the owning STATUS file.

### 2026-09-10 — Prong correspondence and typed-descriptor continuation

Recorded Carlos Pernas's reconstruction-side explanation in
[PRONG_BRANCH_SEMANTICS.md](pet/PRONG_BRANCH_SEMANTICS.md), preserving the
difference between stated definitions and tentative expected code support,
hypothesis selection and release applicability. The record explains the PID
and charge conflict, missing-value handling, score/mass interpretation,
primary-lepton role, dedicated particle branches and P7/P8 provenance.

[TYPED_DESCRIPTOR_STATUS.md](pet/TYPED_DESCRIPTOR_STATUS.md) routes the next
proposed task: repair the prong contract and validate it locally with synthetic
fixtures before source validation or training. The older fixed-sample packet
gains a forward pointer; its measurements and scope remain unchanged. The
adapter and semantic-evidence branches were measured as already integrated at
base `d147880f`, so the documentation continues on `pet-prong-semantics` from
that base.

Documentation only: no source access, probe, training, covariance construction,
schema implementation or scientific result. No validation-ledger row is added.
The scalar publication task and the `OI-126` PET disposition are unchanged.

### 2026-09-10 — Prong contract v2 local repair

Implemented the next task recorded at `ae9dfee5` on `pet-prong-semantics`:
muon-only raw charge applicability, charge categories `0/1/2`, independent
undefined-mass/unfilled-score masks, documented prong units and native score
scaling alongside PID. Raw-row membership, raw PID storage and the default
51-column descriptor contribution are preserved. Schema v2 rejects v1 shards,
normalization and saved-model semantics instead of silently reinterpreting them.

The synthetic suite passes 52 tests and 10 subtests, including NumPy/Keras
agreement, mask behavior, matched controls, gradients and fresh-process model
reload. Test command, environment and static-check limitations are recorded in
[the typed-descriptor status](pet/TYPED_DESCRIPTOR_STATUS.md). Strict source
mypy has 54 diagnostics both at the parent and after repair, with none added.
No ROOT data were read and no scientific training or compute was launched.

The next proposed preparation is the v2 source-validation and normalization
protocol. This software result does not alter scalar results, the existing
PET statistical pairing decision or publication adoption. No numerical physics
result is added to the validation ledger.

### 2026-09-10 — Typed-descriptor source and normalization protocol

Prepared [SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md](pet/SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md)
from software base `529f26ae` on `pet-prong-semantics`. It binds the two
historical source identities, proposes 4,096 entries per file, separates
mapping acceptance from semantic/release evidence, and states the remaining
photon/blob, hypothesis and overlap questions. The normalization pilot specifies
a single-file reco-MC inventory, historical-anchor reservation, deterministic
event-group split, valid-only fitting and frozen score identity scaling.

The required detector-selection sidecar does not yet have a bound producer;
the 75-branch source mapper cannot supply `pass_reco`. Current raw counts and
sum pooling remain implemented. The proposed mean/log-count representation
needs separate implementation and validation. Source, normalization and later
matched C0/C1 stages have explicit proposed resource ceilings and terminal
non-claims; no execution authorization is inferred from this preparation.

Local checks confirmed the two manifest SHA-256 values, source bindings,
ordered 75-branch digest, v2 schema digest, document links and exact Gate-6
restriction keys. The existing five-file synthetic suite passed 52 tests and
10 subtests in 6.56 seconds in the repair's CPU test environment. These test
results validate the existing adapter, not the proposed pooling implementation
or an inventory-aware fitter. No ROOT file was opened, scientific training
performed or cluster job submitted. Documentation only; no new physics result
or validation-ledger row, and no change to OI-126 or Gate 6.

### 2026-09-10 — Bounded PET source-audit implementation preparation

Implemented the raw-preserving checker and launcher from `34fec047` on
`pet-prong-semantics`. [SOURCE_AUDIT_RUNBOOK.md](pet/SOURCE_AUDIT_RUNBOOK.md)
contains the exact future command, separate authorization-file contract,
metadata acceptance rules, resource limits, digest framing and terminal receipt
specification. [SOURCE_AUDIT_BINDINGS.json](pet/SOURCE_AUDIT_BINDINGS.json)
freezes the implementation dependencies, protocol, branch/schema/source identities,
structural metadata contract and synthetic tests.

The checker enforces the two pinned sources, ordered 75 branches and entries
`[0,4096)` per source. It archives numeric observations before mapping, retains
malformed rows and exceptions, checks typed values/masks against a separate
field table, and keeps mapping, semantic, release and object-family verdicts
separate. Diagnostic forward checks use identity normalization and fixed
reference projectors, with no fitting. A partial failure never backfills,
retries, filters rows or promotes an incomplete shard.

Local CPU synthetic validation: 112 tests and 10 subtests passed across the new
checker tests and the five existing typed-descriptor suites. This includes the
complete 8,192-entry fake-reader path, pre-payload identity/metadata failures,
raw non-finite bytes, malformed counts/vectors/keys, v2 masks, serialization,
NumPy/Keras C0/C1 checks, resource failures and launcher accounting. Black and
Ruff pass for all three new Python files; targeted mypy with
`--follow-imports=silent` passes for the two new source modules. This is not a
whole-package strict-typing claim. The preparation-only launcher check also
passes against the committed-manifest bytes.

No ROOT source was accessed, scientific training performed, GPU used or cluster
compute launched. Native ROOT compatibility and the combined dependency
footprint under the proposed ceilings remain unmeasured. Source execution still
requires its named authorization; normalization and later training retain their
separate prerequisites. No physics result or validation-ledger row is added.
OI-126 and all five exact Gate-6 prohibition keys remain unchanged.


## 2026-09-11 — PET pooled/direct representation preparation

Prepared from remote `pet-prong-semantics` at `57b707b737ce817c1ef8d8bd0f0a39ce4becb7ba`
in a separate checkout, preserving the occupied local branch and its staged changes.
The [report for Ben](pet/direct_token_comparison/REPORT_FOR_BEN.md) separates
measured source telemetry and historical synthetic receipts from proposed choices.
The evidence reproducer verifies 30 historical signal-arm receipt digests.

The new Keras candidate and pooled attention bridge reuse the current family
encoders, field masks and normalization, with identical trainable parameter
shapes. A separate synthetic runner exercises two-step unfolding with ordinary,
injected and shuffled targets. The [setup](pet/direct_token_comparison/README.md)
and preparation validation record bind the local software checks; those checks
are not a scientific closure acceptance or a real-input performance result.

The [bounded execution proposal](pet/direct_token_comparison/EXECUTION_PROPOSAL.md)
is pending approval. No ROOT payload, cluster allocation, real-source fitting,
correspondence, covariance, publication adoption or Gate-6 work occurred.
Release applicability and all four object-family questions remain unresolved.


## 2026-09-11 — PET execution grant recorded; scheduler preflight blocks allocation

Joseph approved the synthetic campaign and the preparation commit/push. The
reviewed package was frozen and pushed at `9d598c083bca742944e30b4079c7390ece2be9d1`
on `pet-direct-token-comparison`, with 12 commit checks passing.

The [preflight evidence](pet/direct_token_comparison/execution_runs/20260911-preflight/)
records that Perlmutter rejects one GPU/eight CPUs/64 GiB, adjusts memory to 38
CPUs, and requires exactly 32 CPUs per GPU for this queue. An eight-CPU control
with lower memory also fails. One GPU/32 CPUs/56 GiB passes `sbatch --test-only`;
no test-only number is a submitted job. No calibration or training allocation
was submitted; campaign GPU spend remains zero.

[Execution status](pet/direct_token_comparison/EXECUTION_STATUS-20260911.md) holds
execution for the [specific resource amendment](pet/direct_token_comparison/RESOURCE_AMENDMENT-20260911.md).
The GPU limit, events, seeds, algorithm and acceptance criteria remain frozen.
The original CPU reservation estimate was wrong; it has not been silently
reinterpreted as an application-thread limit. No source access, covariance,
adoption, real-input training or Gate-6 work occurred.


## 2026-09-11 — Corrected PET resource envelope authorized

Joseph explicitly approved the amendment at `41a21654`: one A100, 32 reserved
CPUs, 56 GiB, total ceilings 290 GPU-hours / 9,296 CPU-hours / 200 GiB, and two
concurrent full jobs. [Exact authorization](pet/direct_token_comparison/RESOURCE_AUTHORIZATION-20260911.md).
Calibration is next; full jobs remain conditional on the existing integrity and
20% headroom gates. All scientific restrictions and no-retry stops remain.


## 2026-09-11 — PET calibration 58198332: technical stop before training

Executed the authorized corrected profile from `106ba9a8`: one A100, 32 reserved
CPUs and 56 GiB. Slurm records `FAILED`, exit `1:0`, 79 seconds: 0.021944 GPU-hours
and 0.702222 reserved CPU-hours. The Linux suite passed 49 tests and 10 subtests
in 39.64 seconds. The calibration process then failed at package metadata lookup
under the unchanged import guard, before GPU validation or training.

[Terminal evidence and accounting](pet/direct_token_comparison/execution_runs/20260911-calibration/terminal.json).
All 13 files / 51,619 bytes were preserved on CFS with matching source-before,
source-after and destination hashes, then independently verified in the local
committed copy. A guard-compatible imported-module version check passes locally.
No full jobs or retry were submitted. The [118-minute retry proposal](pet/direct_token_comparison/RETRY_PROPOSAL-20260911.md)
requires an explicit exception to the agreed no-retry stop. No synthetic learning
comparison, real-data representation conclusion, source access, covariance,
adoption or Gate-6 action resulted.


## 2026-09-11 — One calibration retry explicitly authorized

Joseph approved the retry proposal at `c9def5d2`, granting one exception for
`58198332`. [Exact authorization](pet/direct_token_comparison/RETRY_AUTHORIZATION-20260911.md).
One A100 / 32 CPUs / 56 GiB / 118 minutes; prior 79 seconds charged to the same
aggregate limits. A second technical failure stops; full jobs remain conditional
on the unchanged integrity and 20% headroom gates.


## 2026-09-12 — Retry 58201775 verified: second technical failure, stop

The one authorized retry ran from `46fe3d7c` on 2026-09-11 (scheduler Pacific
11:01:49–11:03:40). It passed 49 tests plus 10 subtests in 38.80 s, the package
pins and an A100 operation check. The pooled arm saved two models and an NPZ;
the direct arm then failed in `RaggedTensor.from_value_rowids` because GPU
`DenseBincount` does not support the required deterministic mode. No paired
receipt or timing profile completed. No full jobs or third attempt were submitted.

[Terminal result](pet/direct_token_comparison/RETRY_RESULT-20260912.md) binds logs,
partial artifacts, preservation and accounting. The parent allocation was 111 s;
including the first failure gives 190 s = 0.052778 GPU-hours / 1.688889 reserved
CPU-hours. The retry extern cleanup lasted 114 s; a conservative longest-step
sum is 193 s, reported separately without double-counting overlapping steps.
All 19 files / 511,304 bytes were preserved and hash-verified on CFS and in the
committed archive. No headroom gate, routing-performance conclusion, real-data
training, covariance, publication adoption or Gate-6 action resulted.

## 2026-09-13 — Deterministic packing repair, local validation only

The [compatibility repair](pet/direct_token_comparison/COMPATIBILITY_REPAIR-20260913.md)
replaces direct-token value-row-ID packing with explicit CPU integer row splits,
retaining all stored slots, masks and floating gradients. The frozen CPU model
is an exact oracle: all eight model/case combinations match outputs, gradients
and updated weights; 16/16 low-level packing comparisons are exact. The guarded
local suite passes 73 tests plus 10 subtests in 16.74 s; the complete local
preflight takes 50.484469 s and includes a fresh-process reload of both arms.
Evidence and readback inventory are committed under `local_validation/20260913/`.

GPU preflight must now exercise construction, forward, gradients, eager/traced
Adam updates and save/reload before calibration in a fresh process. A new
[110-minute proposal](pet/direct_token_comparison/COMPATIBILITY_PROPOSAL-20260913.md)
is pending approval. No allocation was submitted; both failed attempts and their
partial pooled outputs remain preserved and excluded from learning comparisons.
GPU compatibility and paired calibration remain unverified. No source-semantic
resolution, real-data performance, publication adoption, covariance or Gate-6
conclusion follows. Scientific criteria and original campaign samples are unchanged.

## 2026-09-13 — Single compatibility/calibration attempt approved

Joseph approved the proposal and bound repair at `21c0d163`.
[Authorization](pet/direct_token_comparison/COMPATIBILITY_AUTHORIZATION-20260913.md)
covers one A100 / 32 reserved CPUs / 56 GiB / 110 minutes, with separate
20-minute preflight and 90-minute calibration caps. All prior charges remain
included; full-matrix execution requires every unchanged prerequisite and
headroom gate. No retry, tolerance relaxation, scientific-design change or
extension beyond diagnostic synthetic method development is authorized.

## 2026-09-13 — GPU compatibility 58240587 failed; stop applied

The single approved attempt ran clean `7673b2de` on the approved A100 / 32 CPUs /
56 GiB profile. It passed 60 tests plus 10 subtests in 42.58 s, then failed the
first nominal pooled-model CPU/GPU routed-embedding comparison at fixed atol
1e-5 / rtol 1e-4; logged maximum absolute difference 0.0004892349243164062.
Full-model gradient/update/reload checks and direct-model GPU validation were
not reached. Calibration did not start, and no full job or retry was submitted.

[Terminal evidence](pet/direct_token_comparison/COMPATIBILITY_RESULT-20260913.md)
binds the executed revision and complete 29-file / 76,082-byte preserved bundle,
including the 9-file / 58,406-byte job output. Source/destination and committed
archive readbacks pass. Parent allocation time was 95 s; all attempts total
285 s = 0.079167 GPU-hours / 2.533333 reserved CPU-hours. Using longest overlapping
steps once gives 290 s = 0.080556 GPU-hours / 2.577778 reserved CPU-hours.
The named cluster footprint measured 5.116897 GiB with exclusions in the receipt.
The numerical cause remains unresolved; no tolerance/determinism/scientific
change was made. No learning-performance or real-data conclusion follows.

### 2026-09-14 — prospective Z precursor campaign `z_precursor_20260914` COMPLETE (construction evidence only)

Authorized by Joseph 2026-09-14 as a 62-task measurement-only campaign, max additional admitted
exposure 393.5 CPU task-hours, no GPU, no ceiling extension. **Successful execution adopts nothing.**

- **Deployment** `/pscratch/sd/j/josephrb/zdeploy-e09513d8` at `e09513d842ad3acc1964c1af740696f02eaed7d9`
  (immutable, `dr-xr-x---`; A-2(f) listing `b25953573962d94650c40bee6190a8d27b08fa059e0668b3bd6c67556a777b7b`
  over 886 tracked files).
- **Campaign manifest digest** `e6426e25ec06798739730d4a2e7f9c31cbbd04f1a61b8a9f2b8e62646d0ff993`,
  namespace established by an exclusive create.
- **Jobs** `58302605` (block, 21 tasks `0-20%10`), `58302608` (run, 40 tasks `0-39%40`),
  `58302610` (combine, `afterok` on both). All tasks `COMPLETED 0:0`.
  `Requeue=0` asserted per job (status-, identity- and value-aware) AND verified after the fact:
  `sacct --duplicates` returned 62 rows with no JobID appearing twice, so no requeue occurred.
- **Population** 62/62 by identity — 21 `block5d_*.npz`, 40 `uthrow5d_slab_*.npz`, 1
  `unified_throw_cov_5d.root`. 62 claims, 62 receipts, every receipt `attempt: 1`;
  `_campaign/evidence/` and `_campaign/recovery/` both empty, so no recovery ran.
  `z_precursor.require_campaign_complete` passes for all three declared arms.
- **Receipt-last** verified independently of the producer's own log line, by mtime: the combine's
  product is `1789426386` and its receipt `1789426395` (+9 s); no receipt on any arm predates the
  product it names; exact bijection with the products on disk (0 undeclared, 0 missing).
- **Product** `unified_throw_cov_5d.root`, 2,668,265,910 B, sha256
  `09a029ed2a7de0ffd144b1ad0ad8d3e0bf8e8b9788797b0af58693c753795560`. Opens with
  `Recovered: False`; `C_unified` is 10694×10694.
- **Seeds** draw 1000, estimator 1000, `MNV_EST_SEED_OFFSET` unset (`est_seed_offset 0`,
  `est_seed_offset_declared 0`) — recorded in the product and identically in all 40 run slabs.
- **Support** reported bins **10694 of 65856** under `x_cv > 0`; 55162 genuinely zero, **0 negative**
  (10694 + 55162 = 65856). Bank: 12 knob bands, 100 flux universes, 32,849,103 events,
  edges `[14, 16, 7, 7, 6]`. 160 throws from 40 slabs; 124 band donors.
- **THE NULL'S PERSISTENCE OBLIGATION IS NOW DISCHARGED BY THE PRODUCER.** `Z_BUILD.md`
  requirement 3 asks for "both same-run internal fixed-seed CV vectors and the predicate in the
  throw producer", and the combine persisted `hCvExecution0`, `hCvExecution1` and
  `hCvSupportMask` with `cv_support_predicate = "x_cv > 0"`, bound by `cv_code_revision`,
  `cv_producer_file` and `cv_producer_sha256`
  (`dbf423052e23854d61e8c420ad33a4ec33eae36edc215f8779119456d1cee884`).
  `n_cv_executions = 2`; the two vectors are **NOT bitwise identical** (max abs difference
  2.584e-51, relative L2 over the support 4.452e-14), which is what distinguishes two executions
  from one result written twice. The mask equals `x_cv > 0` recomputed from the persisted CV
  elementwise, and its sum is 10694 = `n_cv_support`. `fixed_seed_null_norm = 1.430183e-50`
  against the producer's 1e-12 tolerance.
  **`B`, `S`, `B <= S` and `epsilon` in `[B, S]` remain UNAPPROVED — the persistence half is
  discharged, the approval half is not, and no tolerance was invented here.**
- **Invalid-ratio handling, preserved and unchanged** (tallied over exactly this campaign's 61
  producer logs, 61-of-61 positive control): 897 `[ratio][WARN]` lines across 45 of 61 tasks, in
  two distinct policies. (A) non-finite or `<= 0` ratios replaced with **neutral ratio 1** on 9
  physical operands — `LowQ2:+1` 576/437/437, `HighQ2:+1` 117/94/94, `MFP_N:-1` 1/1/1 — worst
  576/32,849,103. (B) clipping to `(0.01, 100.0)` on flux universes 9/41/57/73 and the same three
  knobs, worst 387/32,849,103. **Rarity is not validation**; the neutral-1 substitution is a
  policy choice whose scientific justification is a separate decision and was not taken here.
- **Measured construction scalars** (the producer's own, non-quotable): `sqrt_tr_unified`
  4.443674e-38, `sqrt_tr_block` 3.750055e-38, ratio 1.185; per-bin sigma ratio unified/block
  median 0.919; `joint_mean_shift_norm` 1.878697e-38.
- **Accounting** (`r5_meter measure`, 2026-09-14T23:00:43Z): CPU 95.7617 / 500, GPU 0.1439 / 500,
  no stop fired. This campaign drew ~77.0 CPU task-hours of the 393.5 authorized — block 30.321 h
  (21 tasks), run 45.871 h (40 tasks), combine 0.818 h.

**Nothing here is quotable, nothing is promoted, no covariance is adopted, and no significance is
authorized.** The campaign establishes that the operands EXIST and are BOUND; the scientific
criteria in `Z_BUILD.md`'s remaining requirements are untouched by it.

### 2026-09-14 — Stage-1 assembly/spectrum pilot implementation (code and tests only)

Authorized by Joseph as implementation, synthetic tests and independent review; **no cluster
allocation, retry, grading, adoption or publication use.** Four added files, no existing module
changed:

- `nd-unfolding/z_null_bridge.py` — transcribes the producer's ROOT null operands into the
  versioned NPZ slab `z_build` requires, reusing `z_build.Source` (digest-bound read),
  `z_receipt.persist_null_operands` (write), `z_statistics.support_mask` (predicate recomputation)
  and `z_build_path.preservation_guard` (overwrite refusal). It transcribes and never repairs: the
  mask's values must be exactly `{0, 1}` BEFORE any bool cast, the predicate is recomputed and must
  agree, the producer's four recorded counts are checked against the arrays, and the slab carries
  the **PRODUCER's** code identity rather than the assembling revision.
- `nd-unfolding/z_pilot.py` — digest-bound manifest builder, spectrum persistence, and an
  exit-aware runner. Exit 2 means "construction complete, science NON-PASSING" and is **preserved,
  never converted to 0**; it is also not accepted as proof of anything until both products, both
  receipts and the null slab exist and each receipt's recorded product digest matches the file
  beside it, matched **by path** rather than by position.
- `nd-unfolding/z_pilot_manifest_cli.py` — the manifest entry point, separate so declaring inputs
  and consuming them are not one invocation.
- `nd-unfolding/sbatch_z_pilot_5d.sh` — guarded launcher: explicit `--time`/`--mem`/
  `--cpus-per-task`, `#SBATCH --no-requeue` (safe here because this launcher is new and unshared,
  unlike the four precursor launchers), the existing env preflight/pathcheck/source-manifest/
  env-provenance closure, a fresh-output directory that **refuses rather than cleans**, and a
  receipt-last check performed against the filesystem after the exit code.
- `nd-unfolding/tests/test_z_pilot.py` — 40 controls passing under the repository default
  interpreter plus 4 PyROOT-gated ROOT round-trip controls. **Quote the interpreter with the
  count**: the 4 gated controls SKIP without PyROOT and were run separately under
  ROOT 6.28/12 / Python 3.11.14 on Perlmutter (23 of 23 OK in that class selection).
  Three mutants were introduced and each was killed by its intended control: deleting the
  `{0, 1}` mask-value check, converting exit 2 to 0, and matching a receipt digest by first-found
  instead of by path.

The spectrum is **reported, never clipped, floored or regularized**, and it is a deliberate second
independent `eigvalsh` on the closed artifact rather than a harvest of the PSD gate's internal
decomposition — the cost is priced in the execution request, per `Z_BUILD.md` requirement 8.
`z_assembly.gate_symmetry_psd` keeps sole ownership of the PSD verdict.

**INDEPENDENT REVIEW, 2026-09-14: three blockers, five should-fixes, all landed.** The reviewer
verified the "no pre-existing module modified" claim independently (`git diff --numstat`: 9 files,
all 4 deletions in `Z_BUILD.md`) and killed 11 of 14 mutants. The three that SURVIVED were all
launcher-side and all real:

1. **The job exited 0 for a NON-PASSING construction.** The script's last statement was an `echo`,
   so `sacct` would record `COMPLETED 0:0`. `z_pilot.py` takes care to preserve 2 and the launcher
   discarded it at the last hop — worse than never preserving it, because the inner discipline made
   the outer artifact look trustworthy. Fixed with `exit "$PILOT_RC"`. The guard test asserted
   `"exit 0" not in text`, a SPELLING check blind to falling off the end; it is replaced by one
   that executes the launcher's own `case` block, which also kills a `PILOT_RC=0`-inside-the-arm
   mutant that survived the first repair.
2. **`--no-requeue` was satisfied by its own prose comment**, so deleting the real `#SBATCH`
   directive passed. Now anchored on the directive line, with a negative control proving the
   comment alone does not satisfy it.
3. **The fresh-output guard asserted its MESSAGE, not its predicate**, so replacing the predicate
   with `[ -e /nonexistent-sentinel ]` passed. Now executed as a fragment against five cases:
   empty, non-empty, a regular file, an unlistable directory, and a dangling symlink.

Should-fixes landed: exact `TNamed` class check; 40-hex producer revision (it had a weaker standard
than the assembling revision); `OMP_NUM_THREADS` cap (measured 0.480 s vs 4.248 s at n=2800, ~9×);
`ls` status read directly instead of `2>/dev/null`; the guard's CANNOT-LOOK exit 2 distinguished
from the pilot's completion 2 by requiring the receipt; `json.loads` on a receipt wrapped so a torn
file raises `ZContractError` rather than escaping; the bridge record written atomically behind the
preservation guard; and scope item 7 enforced in code for the first time.

**THE LAUNCHER-COUNT RATCHET FIRED, AND MY FIRST READING OF IT WAS WRONG.** I reported that the
count was "still 217 before and after, so the new launcher does not enter that population" — I had
compared the wrong assertion. Measured properly: at `e09513d8` `SubstitutionFenceS1` fails
`217 != 216` (the standing total); at the first pilot commit it failed `199 != 198`, a DIFFERENT
assertion, because `sbatch_z_pilot_5d.sh` landed in the unclassified remainder. The ratchet exists
for exactly that event, and leaving it would have **masked** the standing finding behind a new one.
Classified rather than incremented: the pilot is not `hooked` (that set is closed at the seven
driver legs plus declared consumers), and not `fenced` (nine frozen substitution hazards; the pilot
writes only into a refusing fresh namespace and never a canonical product), so `neither` at 199 is
the honest bucket, pinned with a positive membership assertion so a count that moved for the wrong
reason cannot pass. **The total pin is deliberately left at 216**: it is a standing finding, not
this change's to close, and the arithmetic is recorded instead — 216 pinned + 1 pre-existing and
unexplained + 1 this pilot = 218.

Suites after the fixes: `test_z_pilot.py` 50 passed / 4 skipped (default `python3`); 29 of 29 OK
under ROOT 6.28/12 / Python 3.11.14 on Perlmutter; all Z suites 276 passed / 7 skipped;
`test_uq_remediation` 3 failed / 232 passed — the same three test IDs as at `e09513d8`.

### 2026-09-17 — the Z assembly/spectrum pilot RAN. Job `58454524`: construction COMPLETE, science NON-PASSING, adoption WITHHELD

**CLOSED as completed construction. Not a validation, not a grade, not an adoption.** Authorized by
Joseph as one fourth pilot attempt at ≤1.5 CPU task-hours on the reviewed `fb9ec356` deployment; the
authorization is **consumed** and **no replacement submission is authorized or sought.**

**Judge this by the artifact and receipt contract, not by `sacct`.** `sacct` labels any nonzero exit
`FAILED`, and **2 is this CLI's completion code** — `z_build.py` returns 1 for failed, 2 for
"completed, non-passing", and 0 only for `--help`. The guard's CANNOT-LOOK exit is also 2, which is
why the pilot's own validator additionally **requires the receipt** before reading 2 as completion.

```
58454524 | z_pilot5d | ExitCode 2:0 | ElapsedRaw 1037 s | AllocCPUS 36 | nid004093
         | 2026-09-17T00:21:56 -> 00:39:13 | build_seconds 760.767
```

**Evidence route (all preserved):** `/pscratch/sd/j/josephrb/zpilot-20260916/outcome-58454524/` —
both logs, `submission-a5.txt` with the exact command and exported settings, `scontrol-a5.txt`,
`source-manifest-a5.json`, `env-provenance-a5.json`, all four guard inventory records under
`inv-a5/`, every receipt, `product-digests.txt`, `r5-receipt-20260917.json`, and
`sacct-all-nine.txt`. Products remain in place at
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/`.

#### The contract, re-checked 2026-09-17 against the files

- **Products, digests re-measured on the cluster today and identical to the receipts:** `z-cv.npz`
  **890,500,272 B** `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`; `z-mean.npz`
  **890,383,062 B** `61b7a4939bd40459452e232d4a5cec3c0b19ad7a21715452f7bb3bc9e0c72dd2`; `z-null.npz`
  **190,817 B** `cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e`.
- **The pilot receipt names 5 artifacts and every recorded digest re-measures — 5 of 5 MATCH.** It
  names five and not six because **a receipt cannot digest itself**. The two build-receipt digests
  (`9f8f91d9be69d767…`, `5bdc9a1830dc183a…`) were re-computed again from the preserved copies during
  this close-out: **2 of 2 MATCH**.
- **The output directory holds ten files, not six** — the six the contract covers plus
  `bridge.json`, `z-manifest.json`, `z-provenance.json` and `z-null-source.npz` (189,794 B,
  `2ac9d087…`, written by the **bridge**, distinct from the build's `z-null.npz`). Stated because
  "six artifacts" is the contract's population, not the directory's.
- **Each build receipt describes the file beside it**: two matching path entries per product,
  digests agree, matched **by path** and not by position.
- **RECEIPT-LAST holds**, visible in the mtimes: `z-cv` 463 → `z-mean` 492 → `z-null` 585 → both
  build receipts 681 → pilot receipt 749 (seconds into the job).
- `construction_status` **CHECKED**; `scientific_acceptance` **NON-PASSING**; `adoptable` **false**;
  `build_returncode` **2**; `notes.input_kind` **real**; `revisions_distinct` **true** with producer
  `e09513d842ad3acc1964c1af740696f02eaed7d9` and assembling
  `fb9ec3560fd6d62295dffc81b5694c9e26667d5b` — the two roles did not collapse.
- **Deployment parity** at `zdeploy-fb9ec356`: 895 tracked files, listing sha256
  `f2333fb32876363d12c2c5aebfe50e2a986504845affd5721f4c04fedee23e61`, `dirty 0`, **15 of 15
  CURRENT**; `code_identity.worktree_files_differing_from_revision` empty; 15 import-closure digests.

#### Both harness repairs are confirmed on real inputs at production scale

**The `git show --no-ext-diff` repair.** Attempt 3 (`58358282`) died with the depth-1 `z_build`
guard record reading `refused:launch-unmodelled-launch-grammar`, `offending_flag: git show without
--no-ext-diff`. That same record is now clean. All four guarded processes:

```
depth=0  z_pilot_manifest_cli.py   REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=219
depth=0  z_null_bridge.py          REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=219
depth=1  z_build.py                REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=234
depth=0  z_pilot.py                REPOSITORY-ORIGINS-INSPECTED  launch_refusal None  checked=138
```

Every record: `expect_root /pscratch/sd/j/josephrb/zdeploy-fb9ec356`,
**`repo_origins_outside_expect_root` empty (0)**, `violation None`, `guard_installed true`,
`shell restricted`. **OI-136 containment held on all four**, and `z_pilot.py`'s `outcome` is
`child-systemexit:2` — the guard observed and propagated the completion code rather than masking it.
(Read the containment from these records, **not** from the `15 of 15 CURRENT` parity line: parity
can be true and blind when an earlier import owns `sys.path[0]`. The guard's `expect_root` check is
the evidence.)

**The stderr-preservation repair, and it earned its place.** The child's stderr is preserved intact:
`chars 2424`, `abridged false`, `sha256 9c780d4101c4c3cea5f12cbe589b4ddfcd1873b2575788242c49841bb879519c`
(the 4000-char cap did not engage). It carries nine ROOT `TInterpreter::ReadRootmapFile` warnings —
the in-situ evidence that the **real** PyROOT environment was the one used — **and the depth-1
`z_build` guard's own `[oi136] inventory: checked=234 repo_origin_count=12 outside_expect_root=0`
line, which appears nowhere else.** Without this repair that line would have been discarded with the
child's stderr, and the depth-1 containment evidence would have had to be taken from the JSONL
alone.

#### Measurements — RECORDED, NOT GRADED

**PSD gate, `fb9ec356:nd-unfolding/z_assembly.py:512-561`.** Fail-closed and it returns no boolean:
`require()` raises `ZContractError`, so a populated `G4_symmetry_psd` block **is** the pass. The
criterion is scale-free by deliberate design (the clamp was deleted): `asym <= rtol` and
`lam_min >= -rtol * lam_max`, via `eigvalsh` on `0.5*(C+Cᵀ)`. `rtol = IDENTITY_RTOL = 1e-9`
(`fb9ec356:nd-unfolding/z_contract.py:125`) and it is **arithmetic, not scientific** —
`z_assembly.py:49-51`: *"NO ACCEPTANCE BOUNDARY APPEARS IN THIS MODULE."*

| object | `lambda_min` | `lambda_max` | `neg_fraction_of_max` | `rel_asymmetry` | `rtol` |
|---|---|---|---|---|---|
| cv (inflated) | `-1.2750516323643892e-90` | `2.229223998752954e-75` | `5.719710684424999e-16` | `2.1641333629718972e-16` | `1e-09` |
| mean (inflated) | `-5.146659106575015e-91` | `1.9272637183054823e-75` | `2.670448811800462e-16` | `1.0927533323421377e-16` | `1e-09` |
| block-sum reference | `-4.6860865778129674e-91` | `1.205970554862754e-75` | `3.885738800933054e-16` | `0.0` | `1e-09` |

The cv object's negative excursion is **`5.72e-16` of `lambda_max` — `1.75e6`× inside the
tolerance.** **No clipping, flooring, regularization or replacement threshold was applied, and none
is proposed here.**

**Spectra, persisted separately by the pilot** as a deliberate *second independent* `eigvalsh` on
the closed artifact, each bound to its product's digest, `verdict: None` in both because
`gate_symmetry_psd` keeps sole ownership of the PSD decision: cv `n_negative` **5214**, 33.503 s;
mean `n_negative` **5215**, 16.516 s. **A count is not the gate's criterion** — the gate is on the
extremal eigenvalue relative to `lambda_max` — and nothing grades these counts.

**Other gates:** `G1_closure_identity` `max_rel_residual` **0.0**; `G3_g_reconstruction`
`max_rel_diff` **0.0**; `active_total_eq_sum5` **0.0**; `G2_g_domain` `g_min 1.0`, `g_median
1.0473565738188244`, `g_max 17.653141714565614`, `n_gt_one 6528`, `n_pinned 0`;
`G3R_raw_operand_reconstruction` **`discriminating: true`** (`n_separated 6527`,
`n_saturated_v_uni_below_v_blk 4166`, `n_shift_below_tolerance 1`, `max_separation
0.6270761129833259`), `n_clipped_blocksum 0`, `n_clipped_unified 0`; `G5_band_partition` exhaustive,
`5 + 13 + 27 = 45`. Inflation: `sqrt_tr_before 4.3576468306957044e-38` →
`sqrt_tr_after 5.674200780785609e-38`, ratio **1.302125**.

**Null, as the build reconstructed it:** `r_null 4.4520002137582904e-14`,
`num_norm 1.4301832847122437e-50`, `cv_norm 3.2124510692799616e-37`, `n_rep 10694` — **identical to
the precursor's own record at § 2026-09-14 to every digit**, which is the expected result, not an
independent confirmation: `z-null.npz` transcribes that campaign's two persisted CV vectors. New
here is the **per-bin** statistic `max_i |Δ_i/x_i|` = **`1.7552716191735518e-12`** at
`argmax_grid_index 31499`, flagged `grades_nothing: true` by its own writer. `null.assessment`
records `verdict` **NOT ASSESSABLE**, `reject_conditions ["4c", "11"]`; the receipt's `outcome` is
`assessable: false`, `reject_conditions ["4c"]`, reason *"Scientific criteria and real-input
evidence remain unresolved."*

**Two named non-checks inside an otherwise-closed gate set, recorded and not repaired:**
`G3R.stored_cv_cross_checked` **false** (`stored_cv_deviation`, `stored_cv_discriminating` both
`null`), and `null.declared_cv_crosscheck.external_crosscheck_status` **UNPERFORMED**, `verdict
UNRESOLVED` — its own stated reason being that the compared object is this build's declared
`central` source, not an external production ROOT. Neither is the precursor persistence question.

**A digest that differs for a good reason, stated so it is not read as a disagreement:** the ROOT
object `hCvSupportMask` digests `ea0059ed…` while the persisted `sha256_support_mask` is
`eed021e9…`. The bridge **recomputes** the predicate and stores its own array; agreement is
established by the four counts matching exactly (`n_cv_bins_total 65856`, `n_cv_support 10694`,
`n_cv_genuine_zero 55162`, `n_cv_negative 0`, `recorded == measured`), not by digest equality of two
different representations.

#### Why NON-PASSING, and what the fourteen-key list does and does not mean

`notes.remaining_requirements` is a **fixed fourteen-key list** emitted unconditionally, so
"fourteen remain" is not a measurement. The reconciliation — completed subrequirements, unresolved
scientific criteria, independent verification, and work needing new compute, plus `authorization`
which belongs to none of them — is at
**`docs/orchestration/DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md` §10**, with the
recommended next action at **§11**. In one line: `withheld_boundaries` carries four entries, all
`status: WITHHELD`, `value: null` — `null_epsilon`, `cause3_agg`, `cause3_med`, `cause3_corr` — and
the `null` requirement's own text is *"Persist both internal same-run fixed-seed CVs and predicate
at throw creation; approve B, S, B <= S and epsilon in [B, S] before production."* **The
persistence half was already discharged; the approval half is untouched by construction**, and
`cause5` says it outright: *"construction alone does not dispose of this cause."*

#### Resource sizing — one figure was wrong and it is the one that mattered

```
58454524.batch   MaxRSS 52146232K = 49.73 GiB   ReqMem 64G   ->  77.7% of the request
                 ElapsedRaw 1037 s of a 5400 s wall          ->  19.2% of the wall
                 TotalCPU 02:17:02 across AllocCPUS 36
```

The decision-support record's §4 predicted *"peak memory a few GB … 64G have large margin"*. The
**wall** had large margin; the **memory had 22.3% headroom**, against a prediction low by more than
an order of magnitude. Runtime went the other way: `eigvalsh` at n=10694 was predicted ~59 s per
variant and measured **33.503 s** and **16.516 s**. Any future sizing starts from **49.73 GiB
measured**. `MaxRSS` is a **step-level** field: `sacct -X`, or any JobName filter that drops the
`.batch` row, returns it empty and reads as "not recorded".

#### The nine-job census for this campaign, preserved (`sacct-all-nine.txt`)

| JobID | name | State | Exit | Elapsed | stage reached |
|---|---|---|---|---|---|
| 58347943 | z_pilot5d | FAILED | 1:0 | 4 s | operand guards voided by an apostrophe inside a `${VAR:?…}` message |
| 58354056 | z_pilot5d | FAILED | 3:0 | 13 s | input declaration |
| 58356573 | z_pilot5d | FAILED | 12:0 | 160 s | input declaration |
| 58358282 | z_pilot5d | FAILED | 1:0 | 162 s | **`z_build` refused at launch** — `git show` without `--no-ext-diff` |
| 58398465 | z_e2e_validate | FAILED | 28:0 | 79 s | small-fixture validation; `copy2` preserved `r--r-----`, 7 of 9 controls passed |
| 58403382 | z_e2e_validate | COMPLETED | 0:0 | 95 s | **small-fixture validation PASSED**, all controls |
| 58403491 | z_pilot5d | FAILED | 0:53 | 6 s | **before the script started** — relative `--output` against a read-only CWD, `.batch` CANCELLED |
| 58403564 | z_pilot5d | FAILED | 3:0 | 8 s | `mnv_env_pathcheck` refused five `$HOME` PATH entries |
| **58454524** | z_pilot5d | FAILED | **2:0** | **1037 s** | **completed construction, NON-PASSING science** |

`58403491` is recorded as a **consumed attempt**: Joseph ruled that *"the script never started"* is
not an automatic exception to the no-retry condition. Five submission-side and harness defects were
found and fixed between `58403564` and `58454524` — an IFS-contaminated allowlist loop, an allowlist
that deferred to the environment, an `errexit` enabled after the `sbatch` call that would have lost
the record of a consumed authorization, and two assemble-versus-record ordering faults.

#### Accounting, measured 2026-09-17T07:41:55Z

```
cpu_task_hours  96.196111 / 500    headroom 403.803889
gpu_task_hours  10.210833 / 500    fired: none      58454524 in metered_task_ids
```

The pilot drew **1037 s = 0.288** of its authorized **1.5** CPU task-hours. `stop_date_utc`
**2026-09-30T00:00:00Z — 13 days.** Storage, per-user and not the filesystem's:
**pscratch 16.02 / 20.00 TiB = 80.1%** (`showquota`), inodes 380.67 K / 10.00 M; the 1.7 GB of
products sit inside that. **An earlier report of "pscratch 67%" was `df` on the shared Lustre mount
— the wrong denominator, and it understated the constraint.**

#### No `VALIDATION_LEDGER.md` row is created, deliberately

Nothing here is a verified-for-quotation number: `scientific_acceptance` is NON-PASSING,
`outcome.assessable` is false, and every boundary that would grade any of it is WITHHELD. This
entry and the receipts are the route; a ledger row would read as validation. **Nothing here is
quotable, promoted, adopted or projected. `B`, `S` and `ε` remain open. Successful construction
authorizes no grading, adoption or publication use.**

### 2026-09-25 — s5c campaign (OI-190): pilots, F1 screen, frozen contract, construction and Tier-S launch

Authority `docs/orchestration/AUTHORIZATION-20260924-scalar5d-campaign-activation.md`; index
`docs/orchestration/CAMPAIGN-s5c-20260924-index.md`; all jobs admitted and priced by
`nd-unfolding/s5c_meter.py` (ledger `/pscratch/sd/j/josephrb/s5c-20260924/ledger/admissions.jsonl`).

- `58855902` (xfer): D3 HPSS backup of the nine sole-copy objects, restore SHA-256 9/9 —
  `docs/orchestration/RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md`.
- `58856439` (interactive, 0.789 CPU node-h): pilots P1 (18 unfolds), P2 (background dump, exact
  reproduction of the npz purity weights), P3/P4 (three end-to-end pseudo-experiments), the
  projection reproduction and the development-MC partition scans. `58856170`, `58856255`,
  `58856256` were batch submissions cancelled while pending (queue depth), zero spend.
- F1 two-member screen and P1: `VALIDATION_LEDGER.md` `VL146`–`VL148`.
- Contract frozen at `c29dde25`; feasibility receipt
  `docs/orchestration/FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md`.
- `58857016` (interactive): Tier-S σ bootstrap, 200 replicas. `58857523` (interactive): F2
  construction, real-data bootstrap and first 40 vertical universes. `58857600` (cancelled 15 min
  in: detector arm without `--closure-slack 5000`), `58857791` (interactive GPU node): F2 detector
  weight-only bands and matched CV.

### 2026-09-25 (later) — s5c campaign (OI-190): Tier-S futility FAIL, final disposition

- Reviews: round 2 (`4bdfa75e`) confirmed the purity-background bias and found amendment 3's
  allowance inflating every interval → amendment 4 (bias correction, `95d0e87c`, frozen with 22
  unread validation products on disk). Round 3 (`f511dcd6`): the evaluator is correct, but a pass
  would cover only the corrected construction and development data predict failure →
  `docs/orchestration/state/s5c/review-3-disposition.json`; construction beyond running
  allocations HELD, all slots to validation lines 0-119.
- Unattended lanes: `nd-unfolding/s5c_queue.sh`, `s5c_launch.sh`, `s5c_valid_next.sh` (claims),
  `s5c_futility_watch.sh`; queues under `docs/orchestration/state/s5c/queues/`. Two defects found
  and fixed in flight: GPU-node steps inherited all 4 GPUs (serialized, `3683a4af`); the claim
  lock was inherited by the launched steps runner (CPU lane blocked 46 min, `83b16c16`).
- Validation allocations: `58861566`, `58862360`, `58863216`, `58865811`, then `58868867`,
  `58870274`, `58872289` (cancelled by the futility watcher at 17:40:55Z). Construction:
  `58857523` (bootstrap 100/100, sweep lines 0-39), `58857791` (detector lines 0-4).
- **Futility look 17:40:55Z: FAIL** — `VALIDATION_LEDGER.md` `VL150`,
  `docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md`; independently reproduced
  (review round 4, `83b16c16`), which also found the q3-truth sentinel defect (fixed in
  `s5c_pseudo.py`, `KNOWN_ISSUES.md` 76).
- Spend (meter, 17:49Z): 20.09 CPU + 9.79 GPU node-h (39.2 A100-h) of the 500/500 envelope;
  `docs/orchestration/state/s5c/tier_s/meter-measure-20260925T1749Z.json`. No s5c job remains.

### 2026-09-25 (evening) — s5n successor (OI-191): Stage 1, STAGE1_FAIL, campaign closed

- Authority `75bd22c0` (Joseph's /goal, attachments byte-identical); contract `state/s5n/contract.json`;
  meter generalized (`6412f8ad`: campaign key and `s5n-` prefix from the budget, carried-forward cap
  guard); budget revision 1: CPU 325.184, GPU 115.2138 node-h (unspent s5c envelope binds).
- Code: `nd-unfolding/s5n_pseudo.py` (negweight-refined measured side calling the driver's
  `refine_stay_positive` with the F2 parameters; background source/template split; per-event Poisson(k)
  bootstrap, template Poisson(1), refinement refit per replica), `s5n_truth_check.py`,
  `s5n_eavail_ratio.py`, `s5n_analyze_dev.py`, `s5n_feasibility.py`; `s5c_with_estimator.py` patches
  and verifies the refinement for driver arms.
- Allocations (all stage `development`, all released by their runners): `58874450` (controls + grid,
  2.627 CPU node-h), `58874451` (σ bootstrap, 1.974), `58875242` (prior-equals-truth diagnostic, 0.096
  GPU node-h), `58876649` (signal-only departure diagnostic, 0.213 GPU node-h). Deploys `bd0faf0b`,
  `82dc1517`, `cac87ced`, `e76cb126` (analysis). One hand fix recorded in the state file (output
  directories created before any task wrote).
- Results: `VALIDATION_LEDGER.md` `VL151`–`VL152`; `docs/orchestration/OUTCOME-20260925-s5n-stage1-development-fail.md`;
  independent review rounds 1–2 (`state/s5n/stage1/review-round-1.md`), which refuted two of the
  author's interpretations (withdrawn) and confirmed every number.
- Spend (meter 22:06:24Z): 4.601 CPU + 0.309 GPU node-h; envelope totals with s5c 24.687 / 345.27 CPU and
  10.095 / 125 GPU node-h. No s5n job remains.



## 2026-10-03 — Existing-data model-dependence synthesis (VL163)

Reduced 376 distinct saved products into conserved cell integrals in a separate analysis
namespace; no extraction, training, unfolding, ensemble generation or allocation. The
[package](gbdt_model_dependence/README.md) records identities, 697 available exclusions,
partial-checkpoint limits, receipt reproductions, four figure families, fixed-width
coverage diagnostics and the [costed next panel](gbdt_model_dependence/PROPOSAL.md).
The relationship across estimator settings remains unresolved: repeat variance exists
at five iterations only, while noise-free recovery is truth- and functional-dependent.
The paper/primer rounding statement is narrowed to containment in the tested R bootstrap.
Historical A_FAIL, measurement NOT ADMITTED, adoption boundaries and NOT READY remain.
New results are same-analyst reductions, not a newly independent scientific review.
Delivery/build evidence and both pushed branch heads: package DELIVERY.md.
