# PREDECLARE 2026-08-12 — stamped, hashable footing candidate for the Cause 2 discharge

**Authorization path.** Joseph → Session A (orchestrator, direct typed decision) → Session B. Item 1 of
five routed 2026-08-12: *"Declare Cause 2 discharged only for the footing-matched, stamp-verified J28
candidate, identified by exact artifact path/hash."* Recorded per BEN-082(v). Standing authorization
covers any single job under 12 h; this one is bounded at 3 h.

## Why a job is needed at all — the artifact the instruction names does not yet exist

Measured 2026-08-12 against the cluster, not inferred:

| artifact | footing-matched | stamped | hashed | usable |
|---|---|---|---|---|
| `adopted_bkgaware_meancentered_20260811_footing.root` (A1, 16:18) | yes | **NO** | yes (`bf941c61…`) | no |
| `adopted_bkgaware_cvcentered_20260811_footing.root` (A2, 16:20) | yes | **NO** | yes (`89d024bf…`) | no |
| `STAMPTEST2_bkgaware_meancentered.root` (17:31) | yes | yes | **NO** | no |
| CV-centered **stamped** twin | — | **does not exist** | — | no |

A1/A2 were written at 16:18–16:20, before BEN-106's stamp propagation landed; `STAMPTEST2` is stamped
but was written after the 16:44 hash job, is mean-centered only, and is named as a test. **No single
artifact is simultaneously footing-matched, stamp-verified and hashed**, so the instruction cannot be
satisfied by reading what is on disk. Declaring on A1/A2 and citing stamps verified on a *different*
file would be inventing the success condition after the fact — the exact failure
`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` exists to prevent.

**This does not change any value.** `STAMPTEST2` already reproduced A1 digit for digit
(`5.2696e-38`, `x1.209`, `13.36% → 13.57%`, min-eig ratio `-3.19e-16`), so re-running adopt with the
stamping code produces the same numbers plus provenance. Joseph's *"do not change the value"* holds.

## Pre-registered numbers

From `VALIDATION_LEDGER.md:87-88` and the 56693207 whole-stream log, fixed before this run:

| arm | centering | predicted `sqrt_tr_new` | predicted ratio | predicted median frac/bin |
|---|---|---|---|---|
| A1′ | mean-centered | **5.2696e-38** | 1.209 | 13.36% → 13.57% |
| A2′ | CV-centered | **5.6743e-38** | 1.302 | 13.36% → 14.02% |

Upstream stamps that must read back, from job `56695424`: `n_throws = 160`,
`joint_mean_shift_norm = 1.878696733368378e-38`, `fixed_seed_null_norm = 5.8223488501140625e-50`.

## Branch set — declared before the run, UNRESOLVED is a real outcome

- **S1 — IDENTIFIED.** Both arms complete, both print their predicted `sqrt_tr_new` to the four
  significant figures above, all nine stamp keys read back from each product, and the hash receipt
  covers both. → the Cause 2 discharge proceeds, scoped to these two paths and hashes.
- **S2 — REPRODUCTION FAILURE.** Either arm prints a `sqrt_tr_new` differing from its prediction at the
  quoted precision. → **the discharge does NOT proceed.** A candidate that does not reproduce is not a
  candidate, and this would reopen the footing result rather than merely delay the declaration.
- **S3 — UNRESOLVED.** Job fails, walltime exceeded, stamps absent (adopt now raises `SystemExit`
  rather than printing success — BEN-112), hashing cannot complete, or any source changes while being
  read. → no declaration, no partial adoption, report the state and stop.

S2 and S3 are **different outcomes and are not to be merged**; S3 says nothing about the physics.

## Scope

`values.tex` is untouched. Nothing is adopted into the note by this run. The four `\gbdtFive*` macros
remain quarantined. A discharge of Cause 2 for this candidate leaves the **overall quarantine standing**
and the count at **1 of 7 for this candidate, 0 of 7 for the artifact `values.tex` quotes** — both
numbers to be written, per the instruction, so that this cannot be read as *"one down, six to go."*

## Deployment note

The cluster tree is `683bdcc`, 114 commits behind `origin/main`, so this launcher is not there. It is
committed here first, then copied to the canonical tree, and **the executed file's sha256 is verified
against the committed blob** before submission — rather than pulling 114 commits into a tree three other
lanes are using. Both hashes go into the receipt.
