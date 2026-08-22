# 2026-08-21 — EXPIRY CLAUSE (c): **PASS ON THE IDENTITY AXIS, WITH TWO FINDINGS AND A STATED SCOPE**

**Clause (c) of the B1 steps 4-5 pause**, quoted from
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh` (anchored on content; the block sits at `:276-291`
in `28b68af4` and has moved three times):

> *(c) A FRESH NON-BUILDER has verified the REAL steps (4)/(5) path on a PRESENT-SEED artifact,
> INCLUDING A NEGATIVE CONTROL.*

**THE SCOPE, in one sentence a later reader cannot widen:** *the launcher's own adopt segment, run
byte-for-byte, drives `mii_adopt_unified_5d_stamped.py` -> `adopt_unified_5d.py` -> a stamped adopted
root that `mii_anchor_comparator.py` then reads, and on the **upstream-seed identity axis** that
chain **admits a present-seed declared member correctly and refuses every bad one I could
manufacture** — and this verifies **nothing about the payload at production dimension, nothing about
the 41.44 GB intermediate, and nothing about whether the gate can pass.***

**THIS VERDICT DOES NOT LIFT THE PAUSE.** Only Joseph does that. Clause (a) and (b) are not mine to
judge and I did not judge them. **THIS VERDICT DOES NOT TOUCH THE 41.44 GB INTERMEDIATE** — it was
never opened, read, moved or regenerated, and no sentence here may be read as permission to.

## Verifier eligibility

Fresh session, no prior commit in this repository. `git log` over
`mii_adopt_unified_5d_stamped.py`, `mii_anchor_comparator.py`, `mii_root_payload_classes.py`,
`adopt_unified_5d.py` and the finalize launcher shows authors `lane-b` / `Claude lane B` /
`publication closeout` / `MINERvA-OmniFold agent` / `Joseph Bailey` — none of them this session. I am
not the author of the governing ruling. The `publication closeout` lane (author of `a7bcc2f6` and
`3cb46337`) messaged me mid-run with a builder's account; I checked its three factual claims rather
than adopting them, and one of them is corrected below.

## Host, revision, and what actually executed

| | |
|---|---|
| Host | `login34`, `saul.nersc.gov` (Perlmutter login) |
| Interpreter | `python3` 3.11.14, ROOT 6.28/12, from `setup_salloc_env.sh` at the repo root |
| Executing tree | clean detached worktree `/pscratch/sd/j/josephrb/expiry-c-verify-20260821` @ `ab5710f2`, `git status --short` = 0 lines |
| Verdict binds to | `28b68af4` (local `main` tip at write time; the launcher, the adopt segment digest and the expiry block are unchanged from `fc4293ef`) |

**The five modules under test are byte-identical at `ab5710f2` (executed), `54432a5e`, `d71d3e3f`,
`fc4293ef` and `28b68af4`**, verified by `git rev-parse <rev>:<path>` blob comparison, so the result binds to current
`main` and not merely to the revision I happened to run:

```
401d8845566da6cae28d1d7aaf79a263ccfa6a99f885ecca81c45cd9883bf9fe  mii_adopt_unified_5d_stamped.py
d6d2b9fd339143e2a9a8f99f9ada13ec81a7d9c8ac9bef7f07d8952ae7032044  mii_anchor_comparator.py
d44a03273f6a1f70546771565e833d02eedda82b0885c2d211c9a8d854afd987  mii_root_payload_classes.py
e1260e8dec2d39cb4653a8b4b02a198d04ea103d548a2d90b5f003f0b8044c35  adopt_unified_5d.py
dffa622ea5639db7abc9aa13e6e97db81464ce7389db626ec4c37751ef2742fe  seed_offset_policy.py
```

The launcher itself DID change between `ab5710f2` and `fc4293ef` (`80ebc990`, OI-142). **The change is
comment-only and confined to the undeclared marker branch.** Measured, not assumed: the adopt segment
and the expiry-clause block are byte-identical across both revisions —

```
adopt segment (set-line + adopt-start..EOF)  d4bf8aa28f2dea6f78e775e30eee777aaec021ef9e9d1e36581c88a0df160cc4   (both)
expiry-clause block                          fa4d0b9cf9788febfc5293274e33222b6ce42345df303c64531436aefdf4e9c9   (both)
```

and the segment file that **actually executed on the cluster** hashes to that same
`d4bf8aa2…`. `main` moved twice more while this was being written (`fc4293ef` -> `28b68af4`); the
launcher blob is identical across both, so all three digests above are unchanged. The adopt segment's start line moved `320 -> 332`, which is exactly why it is anchored on
content.

### How "the real path" was made real, and where it stops being the launcher

The adopt invocation was **never retyped**. It was extracted from the launcher by content
(`grep -n 'adopt (mean-centered)'`, then `sed` to EOF) so the `--` split, the flag set, the flag
order and the two output names are the launcher's own bytes.

**One harness bug found and fixed before any conclusion was drawn, and it mattered:** the launcher's
`set -eo pipefail` is at `:12`, *above* the extraction point. My first extraction lost it, and the
segment then **exited 0 while both wrapper invocations had refused** — i.e. the harness would have
reported the launcher swallowing a refusal that the launcher does not swallow. The `set` line is now
re-inserted from the launcher by content, and every negative control below propagates a non-zero exit.

**Where this stops being the launcher, stated plainly.** The launcher hardcodes
`REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"` at `:15` and `cd "${REPO}/nd-unfolding"` at `:17`.
I ran the segment against my clean worktree instead. **So a real `sbatch` submission today would
execute the primary checkout, which carries 722 dirty entries, not the bytes verified here.** That is
a property of the launcher, not of this verification, and it is the OI-136 hazard in its
`${REPO}`-hardcoded form.

## Fixtures

Small synthetic `(uthrow, combined, prod)` inputs at **N = 4 bins**, built with the **producers' own
call forms** — `unified_throw_cov.py:520-555` for the throw leg, `analyze_universes_5d.py:274-287`
for the combined leg, `hXSecND_flat` as read at `adopt_unified_5d.py:116-120`. Magnitudes were chosen
so `sqrt_tr_old` lands at `4.3589e-38`, the VL1 order, and so `g = 2` everywhere (the writer does
real work rather than taking a `g == 1` no-op path). The 41.44 GB intermediate was not touched.

Present-seed values are the ones `tests/test_remedy_a_adopt_wrapper.py:833-834` pins, re-derived from
`seed_offset_policy.LEG_BASELINES` rather than copied: `g1 = 42 + 1200 = 1242`,
`g2 = 1000 + 1200 = 2200`, `est_seed_offset = 1200`.

## Arms, and whether each control fired

| Arm | Configuration | Expected | Observed | Fired? |
|---|---|---|---|---|
| **A** | present seed both legs, declared `k=1200` | wrapper stamps; stage 1 admits identity | segment **exit 0**; stamped `g1=1242 g2=2200 checked=1/1 offset=1200 declared=1` + `hDiagCombinedOld[4]`; stage 1 **FAIL/exit 2** with `[identity] OK g1` **and** `[identity] OK g2` | n/a (positive) |
| **B1** | g1 seed `= 42`, its own baseline, while `k=1200` declared — **the unhooked leg** | wrapper REFUSES | `[FAIL] g1 leg's estimator_seed is 42 but this process declares offset 1200 against baseline 42, i.e. 1242.` segment **exit 1** | **YES** |
| **B2** | same in the other direction, g2 seed `= 1000` | wrapper REFUSES | `[FAIL] g2 leg's estimator_seed is 1000 … i.e. 2200.` **exit 1** | **YES** |
| **B3** | both legs built at `k=1100`, process declares `k=1200` — cross-member | wrapper REFUSES | `[FAIL] this process declares est_seed_offset=1200 but its g1 leg was built at 1100. Refusing to relabel another member's covariance as this one.` **exit 1** | **YES** |
| **C1** | stamped product, then `upstream_estimator_seed_g1_checked` flipped to 0 with the seed still present | stage 1 REFUSES | `[identity] … = 0 but upstream_estimator_seed_g1 is 1242 -- THE FLAG CONTRADICTS ITS OWN SEED` — and **`g2` still reports OK**, so it is per-leg, not a blanket fail | **YES** |
| **C2** | the same in the other direction: flag `= 1`, `upstream_estimator_seed_g2` deleted | stage 1 REFUSES | `[identity] … = 1 but upstream_estimator_seed_g2 is ABSENT -- THE FLAG CONTRADICTS ITS OWN SEED` | **YES** |
| **D1** | stamped `upstream_estimator_seed_g1` mutated to `9999` | stage 1 RECOMPUTES and refuses | `[identity] g1: RECOMPUTED 1242 = baseline 42 + declared offset 1200, but the member stamps upstream_estimator_seed_g1 = 9999.` | **YES** |
| **D2** | g1 leg carries **no** `estimator_seed`; member declared | wrapper admits (absence is a readable state), stage 1 refuses on completeness | wrapper stamps `g1_checked=0` with no `g1` key; `[identity] g1: DECLARED member carries NO seed for this leg` | **YES** |
| **E** | **undeclared** route, seeds present | identity UNVERIFIABLE, still FAIL | `[identity] g1: UNVERIFIABLE -- est_seed_offset_declared = 0 … '_checked' is absence, not a pass.` (both legs) | **YES** |
| **F** | `k=0` anchor, legs hooked (`leg_declared=1`) | identity OK | `[identity] OK g1 = 42 = baseline 42 + declared offset 0`; same for g2 | n/a |
| **G** | `k=0`, **both legs genuinely unhooked** (`leg_declared=0`) | *(see Finding 2)* | **`[identity] OK` for both legs** | **DID NOT FIRE — this is Finding 2** |

**Eight refusal arms, all eight fired, each with the specific message its invariant owns** -- the seven negative controls B1-B3/C1-C2/D1-D2 plus arm E, whose required behaviour is also a refusal (`UNVERIFIABLE`, not `OK`). **Arm G is the one arm that did NOT fire, and it is Finding 2.** D1 is the arm
that establishes power over the substantive check: deleting the baseline recomputation would turn D1
green, so the `OK` in arm A is not vacuous.

## Answer to the question clause (c) asks

**The identity axis admits a present-seed artifact and refuses a bad one, correctly, through the real
path.** `verify_leg_identity` recomputes `42 + 1200` and `1000 + 1200` from
`seed_offset_policy.LEG_BASELINES` — derived, not retyped — and all three of its invariants fire
against manufactured violations. This is the **first execution of stage 1 on an adopted root produced
by the wrapper**; `OI-140` records that "nobody has run the gate end-to-end on a real artifact", and
that sentence is now spent. Job `57294218` remains what it was: plumbing on absent-identity inputs.

**Arm A's FAIL is fully accounted for, and identity is not in it.** Every contributor, tallied from
the run:

| Cause | Count | Keys |
|---|---|---|
| `audit_uncomparable` — member-present / archive-absent, covered by neither `IN_FILE` nor `DECLARED_UNVERIFIED` | **8** | `centering_convention`, `combined_source`, `fixed_seed_null_norm_checked`, `joint_mean_shift_norm_checked`, `n_throws_checked`, `upstream_n_throws`, `uthrow_source`, **`hDiagCombinedOld`** |
| `compare()` PAYLOAD inequality vs the real archive | 4 | `hCov_combined5d_total_uthrow`, `hInflation_g`, `sqrt_tr_old`, `sqrt_tr_new` |
| coverage PARTIAL COMPARISON | 2 | `hCov_combined5d_total_uthrow`, `hInflation_g` |
| `[identity]` failures | **0** | — (2 × `OK`) |
| `recompute` BLOCKED (INCOMPLETE-level, not FAIL) | 1 | `sqrt_tr_old` |

The 4 payload inequalities and 2 coverage findings are **artifacts of a 4-bin fixture compared against
the real 10694-bin archive** and I claim nothing from them. The 8 are the real blocker.

## Finding 1 — `OI-147` undercounts: it is **EIGHT** keys, not seven

`OI-147` states that `hDiagCombinedOld` "is the eighth and its own map row records that no adopted
root in existence carries it, **so it does not fire**."

**Measured: it fires.** Against the real archive
(`uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root`,
892 MB, written 2026-07-14), arm A produced:

```
hDiagCombinedOld: PAYLOAD EXCUSED BY THE ARCHIVE'S AGE AND NOT VERIFIED BY ANYTHING.
```

The mechanism is the same `audit_uncomparable` branch as the other seven: `hDiagCombinedOld` is
`PAYLOAD`, its `ARCHIVE_KEY_MAP` row (`mii_root_payload_classes.py:373-374`) has `derive: None`, it
has **no** `RECOMPUTABILITY` row so `how` is `None` rather than `IN_FILE`, and it is not in
`DECLARED_UNVERIFIED` — so `class_failed = True`.

**`OI-147` is right about today's products and wrong about the products clause (c) is about.** Its
premise holds for the six pre-wrapper adopted roots, which lack the key. It is falsified by the very
artifact the real path produces, because the wrapper stamps `hDiagCombinedOld` unconditionally. The
same dated premise appears twice more in code and expires the same way:

- `mii_anchor_comparator.py:107-116` — *"no adopted root in existence carries `hDiagCombinedOld`. The
  remedy has landed as a WRITER … but not as a PRODUCT — **the cluster is down** and nothing has been
  rebuilt through it."* The cluster is not down; this ran on it today.
- `mii_anchor_comparator.py:126` — `sqrt_tr_old`'s `WRITER_GAP` rationale, *"but NO PRODUCT CARRIES IT
  YET, so `no` stands."*

**Consequence for whoever holds `OI-147`:** the decision is over **eight** keys, and `hDiagCombinedOld`
is not the cheap one to leave out — it is `sqrt_tr_old`'s only retained ingredient, i.e. the
predeclared bar's operand. Its `derive`/`RECOMPUTABILITY` rows and `sqrt_tr_old`'s `WRITER_GAP` row
are **one coupled change**, as `:107-116` already warns, and the flip also shrinks
`declared_unrecomputable()`, which every `--acknowledge-unrecomputable` call site must equal exactly.

## Finding 2 — at `k=0`, the member stage 1 is DECLARED to gate, an **unhooked** product is admitted

`mii_anchor_comparator.py:4`: *"Stage 1's gate: does the `k=0` member reproduce the archive?"*

`seed_offset_policy.declared_offset()`'s own docstring (`:205-208`) makes `est_seed_offset_declared`
the key that separates the two states the seed value cannot:

```
declared = 0            this leg did not go through a hooked launcher … NOTHING can be concluded
declared = 1, value = 0 this leg ran hooked, at the archive anchor, deliberately
```

**Arm G measured what the legs said and what the product claims:**

| | g1 leg (combined) | g2 leg (uthrow) | PRODUCT |
|---|---|---|---|
| `estimator_seed` | 42 | 1000 | — (`upstream_*` 42 / 1000, `checked` 1 / 1) |
| `est_seed_offset` | 0 | 0 | 0 |
| `est_seed_offset_declared` | **0** | **0** | **1** |

Both legs declared themselves **unhooked**. The product asserts **hooked, deliberate anchor**. Stage 1
reports `[identity] OK` for both legs.

**Cause, verified by a covering search rather than inferred.** `est_seed_offset_declared` **is** read
from both legs — it is in `LEG_IDENTITY_KEYS` (`mii_adopt_unified_5d_stamped.py:163`) and both legs are
read at `:671-672`. `g1_keys`/`g2_keys` are then passed to exactly three functions (`:679`, `:680`,
`:682`), and inside them the only keys ever consulted are `est_seed_offset` (`:297-298`) and
`estimator_seed` (`:325`, `:348`). **The legs' `est_seed_offset_declared` is read and consulted by
nothing.** The product's value comes from `off_declared` at `:345`, which is
`seed_offset_policy.declared_offset()` at `:656` — i.e. **the adopt process's environment, not the
legs' provenance**.

**This is not a defect in `verify_leg_identity`, which is correct in its own scope**: it recomputes
from the member's own scalars, and the member's scalars say `declared=1, offset=0`. It is a defect in
the **composition** — the wrapper overwrites the legs' declaration with adopt-time environment, and
the gate downstream can only read what the wrapper wrote. It is the two-lanes-compose pattern: each
side right, the precondition removed by the other.

**Why the hole is exactly `k=0`-shaped.** At `k=1200` an unhooked leg stamps 42 against an expected
1242 and the refusal fires — arm B1 proves it. At `k=0`, `expect = baseline + 0 = baseline`, which is
precisely what an unhooked leg stamps. `assert_seeds_match_their_baselines`'s own docstring says so:
*"indistinguishable from `k = 0` — unless the process declares a non-zero `k`."* **So the substantive
identity invariant has discriminating power for every member except the one stage 1 is declared to
gate.** `anchor_identity` does not close it either: it checks that the *product's*
`est_seed_offset_declared` is truthy, and the wrapper manufactured that value.

**Cheapest fix, costed but not made** (it touches a receipt-bound chain and the ruling is not mine):
compare each leg's own `est_seed_offset_declared` against the process's in
`assert_legs_are_one_member` — the dicts already carry it, so it is a read, not a new ROOT open. That
converts arm G from admitted to refused. A `verify_leg_identity`-side fix cannot work: by then the
legs' flags are gone from the artifact.

## Corrections to the framing I was given

1. **"Seven further keys."** Eight — see Finding 1.
2. **"Real path means launcher -> wrapper -> writer -> stage 1."** As committed, **the launcher cannot
   reach the wrapper in the declared regime at all.** `mr_declared()` is
   `[[ -n "${MNV_EST_SEED_OFFSET:-}" ]]` (`lib_member_resume.sh:230`) — the same variable
   `seed_offset_policy.declared_offset()` reads — and the `if mr_declared; then … fi` block that holds
   the expiry is **straight-line with no conditional**, terminating in `exit 0`. So the only route to
   the adopt call is the **undeclared** one, where `declared_offset()` returns `(0, 0)`,
   `assert_seeds_match_their_baselines` returns immediately, and stage 1 reports both legs
   `UNVERIFIABLE` (arm E, measured). **The present-seed declared configuration clause (c) asks about
   is not reachable through the launcher as committed** — it becomes reachable at the moment the pause
   is lifted. Arm A *is* that post-pause configuration: same env var, same segment bytes.
3. **"Expect stage 1 to FAIL for that reason."** It does, and identity contributes zero of the
   findings — but the count is 8, and 6 further findings in arm A are my fixture's dimension, not the
   gate's.

## What I did NOT verify — name it so nobody reads it as covered

- **The payload axis at production dimension.** N = 4, not 10694. Every `PAYLOAD member differs` and
  `PARTIAL COMPARISON` line in arm A is a fixture artifact and proves nothing either way.
- **Anything about the 41.44 GB intermediate.** Never opened. Its `hCov_combined5d_total` was not read
  and `sqrt_tr_old`'s real value was not reproduced.
- **Clauses (a) and (b).** Not mine; not assessed.
- **Whether the gate can pass.** It cannot, and making it pass was explicitly not the task.
- **A real `sbatch` submission.** I ran the adopt segment, not the whole launcher, and not through
  Slurm — so `BASH_SOURCE`/spool-path behaviour, the `mr_*` locate-and-source block (`:18-100`), and
  the `${REPO}` hardcode's real effect are untested here.
- **Whether an unhooked leg can actually reach adopt in production.** Finding 2 shows the *gate*
  cannot tell; it does not show that any real leg ran unhooked.
- **`mii_root_payload_classes.STAMP_COVERAGE`'s claims**, and the six pre-wrapper adopted roots.

## Reproduce

Harness retained at `/pscratch/sd/j/josephrb/expiry-c-sandbox-20260821/`
(`build_fixtures.py`, `mutate_stamped.py`, `run_arms.sh`, `launcher_adopt_segment.sh`);
clean executing worktree at `/pscratch/sd/j/josephrb/expiry-c-verify-20260821` @ `ab5710f2`.
`bash run_arms.sh {A|B|C|D|E|F|all}` from a Perlmutter login node. Nothing under the repo's
`uq_5d/` was written; the only in-tree write was a 4-bin fixture at
`nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root` **inside that scratch worktree**, because
`adopt_unified_5d.py`'s `--prod` default is relative and the launcher's segment passes no `--prod`.
