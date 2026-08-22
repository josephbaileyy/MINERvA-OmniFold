# 2026-08-21 — EXPIRY CLAUSE (c), RERUN: **DRAFT — ARMS PENDING**

**Status: DRAFT. The arm table is not yet filled and this file carries no verdict.** It exists so the
scope, eligibility and provenance are fixed BEFORE the results are seen, which is the only order in
which a stated scope can constrain a conclusion.

## What this is

The **rerun** of expiry clause (c) of the B1 steps 4-5 pause, quoted verbatim from
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:285-291` at `00be534f` (anchored on content; the
block has moved repeatedly):

> *(c) A FRESH NON-BUILDER has verified the REAL steps (4)/(5) path on a PRESENT-SEED artifact,
> INCLUDING A NEGATIVE CONTROL. "Fresh non-builder" is a property of the verifier, not a name:
> whoever it is must not have written the code under review and must not be the author of the
> governing ruling. "Present-seed" matters because the identity check has never once run against a
> seed that exists — every available leg records `upstream_estimator_seed_g{1,2}_checked=0`, which is
> ABSENCE, not a pass. "Real path" excludes invoking the wrapper directly: job 57294218 did that and
> never ran stage 1.*

The launcher's own next line, which this file honours: *"NOTHING ABOUT (c) IS SATISFIED BY THIS
SCRIPT RUNNING SUCCESSFULLY. Only Joseph lifts the pause."*

**THIS VERDICT DOES NOT LIFT THE PAUSE, AND NOTHING IN IT MAY BE READ AS AUTHORIZING THE LIFT.**
Clauses (a) and (b) are not mine to judge and I did not judge them.

**THE 41.44 GB COMBINED INTERMEDIATE WAS NEVER OPENED, READ, MOVED OR REGENERATED.** Its directory
was listed once. No sentence here may be read as permission to touch it.

## Why this rerun exists, and what the first run could not do

The first clause (c) run (`33c0e0fa`, branch `verdict/expiry-c-20260821`) verified the **identity
axis** and is spent as certification for two independent reasons, both structural rather than
faults of that run:

1. It **necessarily FAILED on OI-147's keys**, so it could not certify ADMISSION. Eight keys came out
   of `audit_uncomparable` as *"EXCUSED BY THE ARCHIVE'S AGE AND NOT VERIFIED BY ANYTHING"* in every
   arm, each setting `class_failed` on its own.
2. It **predates OI-149**, whose fix changed what stage 1 admits.

And a third the first run named itself: its fixture was **N = 4**, so it explicitly claimed nothing
about the payload axis.

**THAT THIRD POINT IS STRONGER THAN THE FIRST RUN STATED, AND IT IS WHY THIS RERUN IS AT PRODUCTION
DIMENSION.** `mii_root_payload_classes.EXPECTED_ELEMENTS` asserts 10694 and 10694² = 114,361,636;
`mii_anchor_comparator.DECLARED_REDUCTIONS` is **empty**; and `assert_reduction_is_declared` refuses
PAYLOAD-class reduction outright. So a product at any dimension other than 10694 fails the coverage
branch, and **no reduced product can ever pass the complete gate** — not before OI-147 and not after.
Arm 1 is required to pass the COMPLETE gate, so N = 10694 is forced, not chosen.

## Verifier eligibility

Fresh session, **no commit of any kind in this repository**. Measured, not asserted: every commit
touching `mii_adopt_unified_5d_stamped.py`, `mii_anchor_comparator.py`,
`mii_root_payload_classes.py`, `adopt_unified_5d.py`, `seed_offset_policy.py` and the finalize
launcher was authored by one of `Lane B (OI-126)` (10), `Claude lane B` (9), `publication closeout`
(5), `Joseph Bailey` (4), `lane-b` (3), `MINERvA-OmniFold agent` (3) or
`MINERvA-OmniFold agent (unattributed)` (1) — **none of them this session**. I am not the author of
the governing ruling.

The five disqualifying commits the ruling names, with their measured authors:

| commit | author | subject |
|---|---|---|
| `a7bcc2f6` | `MINERvA-OmniFold agent` | finalize launcher: restore the missing resume_guard dependency |
| `3cb46337` | `publication closeout` | OI-141 + OI-140: the gate's verdict becomes structured |
| `89e0c62f` | `publication closeout` | OI-149: compare each leg's own declared flag |
| `fdc0792a` | `publication closeout` | OI-147 option 1: ship both diagonals |
| `aa989794` | `publication closeout` | OI-147 complete: the remaining seven keys |

**The `publication closeout` lane messaged me twice mid-run with a builder's account of its own
work.** I checked its claims rather than adopting them: two of its factual points I confirmed
independently from the code before using them, one of its arguments I corrected (below), and its
report of a third defect I re-derived from the source myself and then measured rather than reporting
on its reading. It also placed a voluntary hold on `nd-unfolding/`; I asked it to widen that hold by
one path it had missed, `docs/orchestration/state/ben106-stamp-verify-active-56695424.json`, because
`assert_pinned_writer_is_intact` reads that receipt on every run and it is therefore a gate operand
rather than documentation.

## Host, revision, and the bytes that executed

| | |
|---|---|
| Host | Perlmutter (`saul.nersc.gov`), CPU node under Slurm job `57398910` |
| Login node used for setup | `login34` |
| Interpreter | python 3.11.14, numpy 1.26.4, ROOT 6.28/12, from `setup_salloc_env.sh` at the repo root |
| Executing tree | clean detached worktree `/pscratch/sd/j/josephrb/clausec-rerun-20260821` @ `00be534f`, `git status --porcelain` = **0 lines**, measured in the run's own log before any arm |
| Verdict binds to | the per-file digests below, never to "main" |

**PER-FILE DIGESTS OF WHAT ACTUALLY EXECUTED** (`sha256` of the file, and the git blob id at
`00be534f`) — cited this way because `docs/orchestration/` was moving under three other lanes
throughout, and a tree-level claim would have been falsified by work that never touched my subject:

| file | sha256 (16) | git blob (`00be534f`) |
|---|---|---|
| `mii_adopt_unified_5d_stamped.py` | `fc520bfd09a564f3` | `14e651241134f324` |
| `mii_anchor_comparator.py` | `7cadf61b86c59ebd` | `dfbf177f2c934061` |
| `mii_root_payload_classes.py` | `52cbd04231a0231e` | `b27125c4140a557d` |
| `adopt_unified_5d.py` | `e1260e8dec2d39cb` | `f11b0c6da934b88c` |
| `seed_offset_policy.py` | `dffa622ea5639db7` | `023ec710831c9480` |
| `receipt_candidate_stamps_5d.py` | `1628c76b3008780b` | `5baefe7fc0b43a21` |
| `sbatch_finalize_5d_bkgaware_gpu.sh` | `f7ce66451109271e` | `765c58754465c62d` |
| `state/ben106-stamp-verify-active-56695424.json` | `063cad0ce8cdb17c` | — |

The receipt binds `nd-unfolding/adopt_unified_5d.py` at `e1260e8dec2d39cb`, which is exactly the
digest that executed — so `assert_pinned_writer_is_intact`'s claim, that the subprocess form runs the
bytes the receipt names, is **true on this run** rather than merely asserted.
## What the fixtures are, and what a pass therefore means

Built at **N = 10694** from the producers' own call forms, with **synthetic VALUES**: every matrix is
DIAGONAL with a chosen spectrum. Stated plainly because it bounds every positive arm below —

* `sum(diag(C_comb))` is tuned so `sqrt_tr_old` lands on the **VL1 order 4.36e-38**, i.e. the anchor's
  real magnitude. That is not cosmetic: `_read_int_scalars`' truncation defect (`int(4.36e-38) == 0`)
  is only reachable at that magnitude, so a fixture at O(1) would exercise a different arithmetic
  regime from the one the wrapper's guards were written for.
* `vu = 4*vb`, which makes the inflation factor **exactly `g = 2.0`** for every bin — `sqrt(4x)` and
  `2*sqrt(x)` agree bit-for-bit in IEEE — so `adopt_unified_5d` takes its real inflation path and not
  a `g == 1` no-op.
* `hJointMeanShift = 1e-50` per bin: nonzero, so `joint_mean_shift_norm` is a real norm of a real
  histogram, and small enough that `vu + ms**2 == vu` bit-exactly, so the launcher's **second**
  (cv-centered) invocation gets `g = 2` too and is not silently a different test.

**THE ARCHIVE FOR THE POSITIVE ARMS IS SYNTHETIC, AND THIS IS THE SHARPEST LIMIT ON ARM 1.** Stage 1
asks whether the k=0 member reproduces the archive. For a positive arm the member's payload must
EQUAL the archive's, and there are exactly two ways to get that: reproduce the real 892 MB archive's
payload, which requires the real inputs and therefore the 41.44 GB intermediate this verification will
not touch; or clone the member's own payload into an archive. This does the second.

So **arm 1 is a control on the GATE, not on the archive.** It establishes that every check in the
complete gate can be satisfied simultaneously by a product the real path produced. It establishes
**nothing** about whether any real member reproduces the real archive's physics, and no reader may
take it that way. The clone is faithful in the one respect that governs the key map: the real archive
carries **exactly four keys** — `hCov_combined5d_total_uthrow`, `hInflation_g`, `sqrt_tr_old`,
`sqrt_tr_new`, measured by listing it, at 10694x10694 with
`sqrt_tr_old = 4.357790406860002e-38` — so the clone carries exactly four too, and every other
classified key goes down the `PREDATES_ARCHIVE` branch exactly as it does against the real file. That
branch is the one OI-147 is about.

**AND BECAUSE A CLONE AGREES WITH ITSELF BY CONSTRUCTION, THE PAYLOAD COMPARISON NEEDS ITS OWN POWER
CONTROL.** Arm P gates arm 1's member against arm 4's archive — two production-dimension payloads that
differ — so "PASS" in arm 1 can be distinguished from a comparison that compares nothing. Without arm
P, arm 1's payload agreement would be the single weakest claim in this file.

## The harness, and the bug in it that had to be fixed first

The adopt invocation was **never retyped.** `extract_segment.sh` locates the launcher's
`set -eo pipefail` line and its `adopt (mean-centered)` anchor **by content**, then emits that options
line plus everything from the anchor to EOF — so the `--` split, the flag set, the flag order and both
output names are the launcher's own bytes, and the extraction survives the block moving again.

**THE PREVIOUS RUN'S HARNESS BUG IS GUARDED BY A NEGATIVE CONTROL THAT RUNS BEFORE ANY ARM.** That run
lost the `set -eo pipefail` line, and its segment then exited 0 while both wrapper invocations had
refused — a harness that reports the launcher swallowing a refusal the launcher does not swallow.
`selftest_segment.sh` builds a fragment from the extracted options line plus a failing command and
asserts a non-zero exit AND that execution did not reach the end. It is a **precondition**: if it does
not pass, no arm below is readable, and the driver aborts.

Two bugs were found in my own harness, neither in the code under test, and both are recorded because
each would have produced a *false* result rather than an error:

1. **`h.Delete()` on a histogram the fixture builder created is a double free** on ROOT 6.28/12 /
   python 3.11.14 — cppyy frees it again at dealloc and it SIGSEGVs inside
   `CPyCppyy::op_dealloc_nofree`. `read_keys_pyroot` calls the same method safely because its objects
   come from `key.ReadObj()`, a different ownership. Fixed by `del`, which under
   `ROOT.TH1.AddDirectory(False)` releases the buffer by refcount and keeps peak memory at one live
   915 MB TH2D.
2. **A value read out of a ROOT file and piped back into a mutation produced an EMPTY argument**, with
   stderr suppressed and `tail -1` swallowing the failure — and the arm then gated a **stale artifact
   from a concurrent rehearsal run** and recorded FIRED. Two fixes: mutations are now relative
   (`--scale-bin`) so no value crosses the shell, `mutate.py` fails closed if a targeted bin does not
   actually move, and the driver takes a **lock** so two runs cannot share a sandbox. A negative
   control that mutates nothing and reports a refusal is the worst arm in any suite.

## Finding A — a real submission today would run PRE-FIX code, and the previous statement of this was imprecise in the way that matters

The launcher hardcodes `REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"` (`:15`) and
`cd "${REPO}/nd-unfolding"` (`:17`), so **`sbatch`ing it executes the primary checkout, not any
reviewed tree.** The previous clause (c) verdict recorded this as *"the primary checkout, which
carries 722 dirty entries, not the bytes verified here."* True, and it points at the wrong operand.
Measured here per path, because "the cluster checkout" is not one object:

| file | primary checkout | this verification | |
|---|---|---|---|
| `mii_adopt_unified_5d_stamped.py` | `401d8845566da6ca` | `fc520bfd09a564f3` | **DIFFERS** |
| `mii_anchor_comparator.py` | `6092410b069b7a8f` | `7cadf61b86c59ebd` | **DIFFERS** |
| `mii_root_payload_classes.py` | `d44a03273f6a1f70` | `52cbd04231a0231e` | **DIFFERS** |
| `adopt_unified_5d.py` | `e1260e8dec2d39cb` | `e1260e8dec2d39cb` | same |
| `seed_offset_policy.py` | `dffa622ea5639db7` | `dffa622ea5639db7` | same |
| `receipt_candidate_stamps_5d.py` | `1628c76b3008780b` | `1628c76b3008780b` | same |
| `sbatch_finalize_5d_bkgaware_gpu.sh` | `f7ce66451109271e` | `f7ce66451109271e` | same |
| `state/ben106-stamp-verify-active-56695424.json` | `063cad0ce8cdb17c` | `063cad0ce8cdb17c` | same |

**THE THREE THAT DIFFER ARE EXACTLY THE THREE OI-147 AND OI-149 CHANGED**, and
`mii_adopt_unified_5d_stamped.py`'s primary digest `401d8845…` is *the digest the previous clause (c)
run recorded as executing* — i.e. the pre-OI-149 file.

**AND IT IS "BEHIND", NOT "DIRTY", WHICH IS A DIFFERENT REMEDY.** The primary checkout is **6 commits
behind** `main` and all four modules are **clean at its HEAD** (`git status --porcelain` over those
paths is empty; each working blob equals its tracked blob). So the 721 dirty entries are real and
**touch none of the bytes under test**. Naming them as the hazard would have sent a reader to
reconcile 721 files when the actual remedy is one `git pull`.

**CONSEQUENCE FOR THE LIFT, and it is the operative sentence of this finding:** submitting the
launcher today would run `assert_legs_are_one_member` WITHOUT OI-149's per-leg declaration check —
i.e. it would ADMIT exactly the product arm 2 refuses — and the gate WITHOUT OI-147's coverage of the
eight archive-absent keys. **The primary checkout must be advanced to a revision containing
`89e0c62f`, `aa989794` and `fdc0792a` before the lift is executed, and that is a precondition nobody
has recorded.** I am not advancing it: it is a shared checkout with 721 dirty entries owned by other
lanes, and moving it is not mine to do.

## Finding B — clause (c)'s configuration is still unreachable through the launcher, so arm 1 is the post-lift state

Re-measured at `00be534f`, because the previous run established this at a different revision.
`mr_declared()` is `[[ -n "${MNV_EST_SEED_OFFSET:-}" ]]` (`lib_member_resume.sh:230`) — the same
variable `seed_offset_policy.declared_offset()` reads (`OFFSET_ENV = "MNV_EST_SEED_OFFSET"`,
`:193`). The `if mr_declared; then … fi` block that carries the expiry (`:256`–`:331`) is
**straight-line with no conditional** and terminates in `exit 0` at `:330`, before the two adopt calls
at `:347` and `:352`.

So the only route to adopt through the launcher as committed is the **UNDECLARED** one, where
`declared_offset()` returns `(0, 0)` — which is arm E, and it is correctly refused. **The present-seed
declared configuration clause (c) asks about is not reachable through the launcher today; it becomes
reachable at the moment the pause is lifted.** Arm 1 *is* that post-lift configuration: same env var,
same segment bytes, same wrapper.

This is not a defect and it is not a way around the clause. It is the reason a present-seed arm has to
be constructed rather than observed, and it is why "run the launcher and see" cannot satisfy (c).

## What I did NOT verify — named, so nothing here reads as covered

* **That any real member reproduces the real archive.** The positive arms compare against a CLONE of
  their own member's payload. Arm 1R compares the member against the real archive and FAILS on payload
  values, exactly as a synthetic member must. Nothing here is evidence about the real covariance.
* **The physics of the payload.** The matrices are DIAGONAL by construction. Dimension, coverage,
  digest sensitivity and the raw/clipped pair are exercised at 10694; correlation structure is not
  exercised at all, and `project_cov_nd.py`-style ordering questions are untouched.
* **The 41.44 GB combined intermediate.** Never opened. Its directory was listed once, to read the
  real archive's size and mtime. `sqrt_tr_old`'s real value was not reproduced from it and must not be
  said to have been.
* **Clauses (a) and (b).** Not mine; not assessed. I did not evaluate whether OI-141's structured
  verdict or OI-140's recomputation are correct beyond observing them execute.
* **A REAL `sbatch` SUBMISSION OF THE LAUNCHER.** I extracted and ran the adopt segment, under `srun`,
  from a mirror — not the whole launcher, and not through the launcher's own locate-and-source block
  (`:18`–`:100`). So `BASH_SOURCE`/spool-path behaviour, `mr_prefix`/`mr_dir_prefix` member scoping,
  the `resume_guard` dependency and the COMB guard are **untested here**. Finding A is a statement
  about which bytes such a submission would execute, not a test of the submission.
* **Whether an unhooked leg can actually reach adopt in production.** Arm 2 shows the wrapper now
  REFUSES one. It does not show that any real leg ran unhooked.
* **The six pre-wrapper adopted roots**, `STAMP_COVERAGE`'s capability claims, and the cv-centered
  product against the real cv-centered archive.
* **Any statement about whether the pause SHOULD be lifted.** That is Joseph's, and clause (c) is one
  of three.

## Reproduce

Harness at `/pscratch/sd/j/josephrb/clausec-rerun-20260821-sandbox/harness/`
(`build_base.py`, `make_variant.py`, `make_archive.py`, `mutate.py`, `inspect_diag.py`,
`extract_segment.sh`, `selftest_segment.sh`, `run_arms.sh`, `submit_clausec.sh`); clean executing
worktree at `/pscratch/sd/j/josephrb/clausec-rerun-20260821` @ `00be534f`. Per-arm gate logs under
`.../logs/gate_<ARM>.log`, the arm table at `.../results.tsv`, the full transcript at
`.../production.log`.

`MNV_N=<n>` rehearses the whole suite at a smaller dimension; **only `MNV_N=10694` may be quoted**,
and the driver prints which it used and labels anything else `HARNESS REHEARSAL -- NOT A VERDICT`.

Nothing was written inside any git checkout: the mirror is a symlink tree over the worktree with only
`products/` and `uq_5d/` as real directories in the sandbox, and the worktree's
`git status --porcelain` was 0 lines before the run and is re-checked after it.
