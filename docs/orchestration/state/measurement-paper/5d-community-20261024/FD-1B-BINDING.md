# Binding: 1B with 4A, stage 1, the coverage protocol (2026-10-30)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261030-joseph-fund-1b-with-4a.md` (#540).

**Binds** [`FD-1B-DECLARATION.md`](FD-1B-DECLARATION.md), merged in PR #545. Its file sha256 begins `07d0e0b6b722c7de`.

**AUTHORIZES:** stage 1 only, the declaration's §8. That covers the toy mode's code and tests, and the derivation of
the expected spread, on a login node at 0 node-h.

**CANNOT AUTHORIZE:** any Slurm job. Stages 2 and 3 each need their own declaration and binding, within §7's ceilings.

## 1. What the director accepts as the protocol

- **The test:** the reported C_total + C_resp as on `main` when declared (`fd_data_product.json` `b79556f0…`). It
  has no run-period block, which is still under audit (#552). Every report says which matrix was tested.
- **The statistics, fixed before any toy (§4):**
  - per-cell coverage ĉ_c(k) with its binomial SE and Wilson 95 % interval;
  - the control arm two-sided in VL169's windows, where anything but PASS is a STOP;
  - the test arms one-sided against nominal;
  - the reading "no undercoverage detected at the study's sensitivity", with undercoverage reported as measured.
- **Gate D:** the toys must reproduce S1's blocks within [0.9, 1.1] before any coverage toy runs.
- **Price (§7):** 33.5 node-h projected, with 49.50 the enforced cap across all jobs, inside the funded 44.5–145. It is
  not padded.

## 2. Rulings on §10

1. **The estimator is full MC, as in production.** Half MC runs only as the paired correspondence measurement of
   stage 2a, and is never scored.
2. **The laterals use the declared surrogate,** x̂ += Σ_b s_b Δ_b / 2 from S1's lateral unfolds, because the 5D lateral
   dumps no longer exist.
   - Every report states that the surrogates carry 29.0 % of C_e's trace, that the control carries them but does not
     test them, and that only 71.0 % is tested through the estimator.
3. **Gate D is the stop before any coverage toy.** It includes the prior-part gap of §3, which is sized in stage 2a.
4. **4A gates nothing.** It is graded at the control only.
5. **The stage ceilings of §7 are accepted:** stage 2 capped at 23.0 node-h and stage 3 at 26.5, 49.50 in all. Each
   stage's binding re-states its own.

## 3. Conditions

- **Stage 1's code** comes as a PR, with tests in both directions and a mutation receipt, and with the derivation's
  outputs labelled as derivation, not results.
- **Stage 2's declaration** follows it, with pins, exact commands and its own binding.
- **CPU only:** QOS regular, `--exclusive --no-requeue`, every job under 12 h, nothing to CFS.

## Not changed

- The reported covariance, every claim and number. Nothing is submitted, deposited or tagged.
