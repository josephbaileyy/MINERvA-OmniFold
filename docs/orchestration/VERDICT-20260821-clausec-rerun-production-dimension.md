# 2026-08-21 — EXPIRY CLAUSE (c), RERUN: **THE COMPLETE GATE ADMITS A CORRECT PRESENT-SEED PRODUCT AND REFUSES EVERY BAD ONE — WITH ONE MEASURED HOLE, AND THE PAUSE IS NOT LIFTED**

**22 arms at PRODUCTION DIMENSION (n = 10694), real ROOT, on a clean detached worktree at
`00be534f`. Every arm matched its predeclared expectation. Sixteen refusal arms fired. One arm —
predeclared as a probe with its outcome recorded as unknown — PASSED, and that is Finding C: the gate
admits a wrong-length diagonal pair.**

**THIS VERDICT DOES NOT LIFT THE PAUSE.** Clause (c) is one of three, only Joseph lifts it, and the
launcher's own text says *"NOTHING ABOUT (c) IS SATISFIED BY THIS SCRIPT RUNNING SUCCESSFULLY."*

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
## The arms, and whether each fired

**22 arms. Every one matched its predeclared expectation.** Exit codes read UNPIPED from
`mii_anchor_comparator.main` (`PASS=0, INCOMPLETE=1, FAIL=2`) and from the extracted segment; the
disposition column is computed by the driver from the code, never typed in after seeing the output.

| # | arm | configuration | required | observed | fired? |
|---|---|---|---|---|---|
| **1** | **A1** | present seed both legs, declared `k=0`, legs `est_seed_offset_declared=1` | **COMPLETE gate PASSES** | segment **0**; gate **PASS / exit 0** | n/a (positive) |
| 1 | **A1C** | the cv-centered sibling the same segment builds | COMPLETE gate PASSES | gate **PASS / exit 0** | n/a (positive) |
| 1 | **A1R** | the same member vs the **REAL 892 MB archive** | FAIL on payload VALUES only, **0 uncovered** | **exit 2**, `uncovered=0`, `partial=0` | see below |
| **2** | **A2** | declared `k=0` adopter over two legs each `declared=0` | wrapper REFUSES | `DECLARATION MISMATCH on the g1 leg` — segment **exit 1** | **YES** |
| **3** | **A3a** | `hDiagCombinedOld[777]` altered | gate FAILS | `[diag] FAIL clip(...) vs ...` — **exit 2** | **YES** |
| 3 | **A3b** | `hDiagCombinedOld` dropped, raw kept | gate FAILS | `only ONE of the pair is present` — **exit 2** | **YES** |
| 3 | **A3c** | clipped shortened, raw not (shapes differ) | gate FAILS | `shapes differ` — **exit 2** | **YES** |
| 3 | **A3d** | **PROBE:** both diagonals zero-padded to **10695** | *unknown — measured* | **PASS / exit 0** | **DID NOT FIRE → Finding C** |
| 3 | **A3e** | **CONTROL:** both truncated to **10693** | gate FAILS | `sqrt_tr_old` recompute mismatch — **exit 2** | **YES** |
| **4** | **A4** | one legitimately **negative** raw diagonal entry | **PASSES**, clipped stays 0 | gate **PASS / exit 0**; `[diag] OK … 1 negative raw entr(ies) clipped to 0`; `sqrt_tr_old` recomputed `4.358004296350286e-38` **== stamped** | n/a (positive) |
| **5** | **A5a** | that negative entry **doubled** — clip unchanged, trace moves | gate FAILS | `[diag] OK` (clip still consistent) **and** `RECOMPUTED 4.3577350143027017e-38 != STAMPED 4.358004296350286e-38` — **exit 2** | **YES** |
| 5 | **A5b** | a **positive** raw bin changed (clip *and* trace move) | gate FAILS | **exit 2** | **YES** |
| **6** | **B1** | g1 leg at its baseline `42` while the process declares `k=1200` | wrapper REFUSES | `g1 leg's estimator_seed is 42 … i.e. 1242` — segment **exit 1** | **YES** |
| 6 | **B2** | the same in the other direction, g2 seed `1000` | wrapper REFUSES | segment **exit 1** | **YES** |
| 6 | **B3** | both legs built at `k=1100`, process declares `k=1200` | wrapper REFUSES | `Refusing to relabel another member's covariance as this one` — segment **exit 1** | **YES** |
| 6 | **C1** | `upstream_estimator_seed_g1_checked` → 0, seed still present | gate FAILS | `THE FLAG CONTRADICTS ITS OWN SEED` — **exit 2** | **YES** |
| 6 | **C2** | `upstream_estimator_seed_g2` deleted, flag still 1 | gate FAILS | `… is ABSENT -- THE FLAG CONTRADICTS ITS OWN SEED` — **exit 2** | **YES** |
| 6 | **D1** | stamped `upstream_estimator_seed_g1` → `9999` | gate FAILS | `RECOMPUTED 42 = baseline 42 + declared offset 0, but the member stamps … 9999` — **exit 2** | **YES** |
| 6 | **D2** | declared member, g1 leg carries **no** `estimator_seed` | wrapper admits, gate FAILS | segment **0**; `DECLARED member carries NO seed for this leg` **and** `ABSENT FROM MEMBER (PROVENANCE, MANDATORY)` — **exit 2** | **YES** |
| 6 | **E** | **UNDECLARED** adopter, seeds present | identity UNVERIFIABLE, gate FAILS | segment **0**; `UNVERIFIABLE` both legs **and** `est_seed_offset_declared == 0 -- … UNHOOKED launcher` — **exit 2** | **YES** |
| — | **P** | payload POWER control: A1's member vs A4's archive | gate FAILS | **exit 2** | **YES** |
| — | **G2** | `read_one_matrix_for_gate2` on the real 892 MB archive | ok | **exit 0** | n/a |

**SIXTEEN REFUSAL ARMS, ALL SIXTEEN FIRED, each with the specific message its own invariant owns.**
The one arm that did not refuse is **A3d**, which is Finding C, and it was predeclared as a probe with
its outcome recorded as *unknown — measured* before the run.

**D1 AND ARM P ARE THE TWO ARMS THAT MAKE ARM 1 NON-VACUOUS**, and they act on different axes. Delete
the baseline recomputation from `verify_leg_identity` and D1 goes green — so `[identity] OK` in arm 1
is a real check, not a tautology. Arm 1's archive is a clone of arm 1's member, so its payload
agreement is true by construction; arm P shows that two *different* production-dimension payloads are
distinguished, so `PASS` in arm 1 is not a comparison that compares nothing.

## What arm 1 establishes, and it is the thing that had never happened

```
[b2] VERDICT: PASS
  [coverage] hCov_combined5d_total_uthrow: compared 114361636 of 114361636 elements (100.0000%)
  [coverage] hInflation_g:                 compared 10694 of 10694 elements (100.0000%)
  [identity] OK  g1: upstream_estimator_seed_g1 = 42   = baseline 42   + declared offset 0
  [identity] OK  g2: upstream_estimator_seed_g2 = 1000 = baseline 1000 + declared offset 0
  [config]   OK  upstream_n_throws = 160 == predeclared ensemble size
  [config]   OK  centering_convention = 'mean-centered' matches adopted_uthrow.root
  [diag]     OK  clip(hDiagCombinedOldRaw) vs hDiagCombinedOld: 10694 bins
  [recompute] OK sqrt_tr_new: recomputed 6.891461280320583e-38 == stamped
  [recompute] OK sqrt_tr_old: recomputed 4.358542810534632e-38 from hDiagCombinedOldRaw == stamped
```

**THE COMPLETE GATE CAN PASS A CORRECT PRESENT-SEED `k=0` PRODUCT AT PRODUCTION DIMENSION.** Both
prior runs failed this necessarily — one because `OI-147`'s eight keys were covered by nothing, and
both because a sub-production fixture cannot satisfy `EXPECTED_ELEMENTS`. Coverage is now
**100.0000%** on both asserted keys, so the previous run's two `PARTIAL COMPARISON` findings were
purely its fixture and are gone.

**AND `sqrt_tr_old` RECOMPUTES BIT-EXACTLY, WHICH WAS THE OPEN QUESTION AND NOT A FORMALITY.** The
child stamps `sqrt(np.trace(C_comb))` — a **strided** diagonal reduction — while
`_sqrt_trace_from_diag` recomputes `sqrt(np.sum(...))` over a **contiguous** TH1D read-back, compared
at `rtol=0.0`. `_sqrt_trace_from_diag`'s own docstring says the bit-exactness is a property of the
summation route, not of the mathematics, and OI-147's unit tests build both sides in one process so
they cannot exercise that crossing. It holds, measured on the artifact at n=10694, and **it also holds
with a negative raw entry present** (arm 4: `4.358004296350286e-38`, recomputed == stamped, with the
clipped histogram correctly 0 at that bin). That pair — arm 4 passing and arm 5a failing on the same
fixture with the clip check still green — is the whole of OI-147 Option 1 working as ruled.

## `OI-147`'s blocker is closed, measured against the REAL archive

Arm A1R, the direct successor to the previous run's arm A:

| cause | previous run | **this run** |
|---|---|---|
| `audit_uncomparable` — archive-absent, covered by nothing | **8** | **0** |
| coverage `PARTIAL COMPARISON` | 2 | **0** |
| `[identity]` failures | 0 | **0** |
| `compare()` PAYLOAD inequality vs the real archive | 4 | 4 |

The four payload inequalities are the synthetic member differing from the real archive's physics —
`sqrt_tr_old` member `4.358542810534632e-38` vs archive `4.357790406860002e-38`, and two differing
digests — which is what a synthetic member MUST do and I claim nothing from them. **The eight are
gone.** Confirmed by a second, independent route: executing the archive-absent sweep over
`ARCHIVE_KEY_MAP` for both adopted artifacts returns **NONE uncovered**, and
`declared_unrecomputable()` is now exactly `{fixed_seed_null_norm, globalCompleteness}`.

`OI-140`'s caveat that "nobody has run the gate end-to-end on a real artifact" was already spent by
the previous run. What is newly spent here is stronger: **nobody had ever built a product through the
new writer at all**, so `hDiagCombinedOldRaw` had never been read back off any artifact. It has now,
at production dimension, in five arms.

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

## Finding C — the gate ADMITS a wrong-length diagonal pair, and the check that looks like cover cannot see it

**Reported to me as a missing assertion by the `publication closeout` lane, which built OI-147.** I
re-derived it from the source before accepting it, then measured whether it was REACHABLE, because a
missing assertion is not automatically a defect. It is reachable.

`classes.EXPECTED_ELEMENTS` holds exactly `hXSecND_flat`, `hJointMeanShift`, `hInflation_g`,
`C_unified`, `C_blocksum`, `C_cross` and `hCov_combined5d_total_uthrow`. **Neither `hDiagCombinedOld`
nor `hDiagCombinedOldRaw` is in it** — so `mii_anchor_comparator.py:448`'s
`expected = classes.EXPECTED_ELEMENTS.get(name)` returns `None` for both and the coverage branch
prints *"NO DERIVED EXPECTATION, so completeness is reported and NOT asserted"* and moves on. Their
sibling per-bin histograms are both pinned at 10694; the one histogram OI-147 shipped is not.

**MEASURED, ARM A3d.** Starting from the product that passes the complete gate, both diagonals
rewritten at **10695** bins with the appended bin exactly `0.0`, pair kept mutually consistent:

```
mii_anchor_comparator.py  EXIT 0   -- the COMPLETE gate PASSED
  [coverage] hDiagCombinedOld:    compared 10695 elements; NO DERIVED EXPECTATION ...
  [coverage] hDiagCombinedOldRaw: compared 10695 elements; NO DERIVED EXPECTATION ...
  [diag] OK   clip(hDiagCombinedOldRaw) vs hDiagCombinedOld: 10695 bins
  [recompute] OK   sqrt_tr_old: recomputed <v> from hDiagCombinedOldRaw == stamped <v>
```

**AND THE CONTROL IS WHAT MAKES THIS A FINDING RATHER THAN A GUESS.** Arm A3e truncates the same pair
to **10693** and is REFUSED (exit 2) on `sqrt_tr_old`'s recomputation. So the trace check has power
against a length error **only when the length error moves the sum** — and zero-padding does not: the
raw sum came back **bit-identical** across 10694 -> 10695, so `_clip_consistency` sees equal shapes,
both recomputations agree, and nothing in the gate looks at the length at all.

I had predicted the opposite outcome as the more likely one — that appending an element would perturb
numpy's pairwise blocking and refuse A3d by arithmetic accident. It does not, and the distinction
mattered: a refusal by accident would have read as coverage while leaving the hole open.

**SCOPE, so the fix is not over-landed.** A3d mutates a FINISHED product, i.e. it models corruption or
hand-editing after the wrapper has run. It does **not** show the wrapper can emit a mismatched pair:
`_stamp_output` writes both histograms from the same `_read_diagonal` return, so on today's path they
are the same length by construction. What it shows is that **the gate would admit one** — and the gate
is precisely what stands between a corrupted or hand-edited artifact and stage 1, which is
`audit_uncomparable`'s own stated reason for existing (*"the member could carry it wrong and this gate
would pass"*).

### The remedy, MEASURED — and the obvious fix does not work

The obvious repair is two rows in `classes.EXPECTED_ELEMENTS` pinning both diagonals at
`REPORTED_NBINS`. **It does not close this.** Measured on patched COPIES outside any commit — a
forward-looking probe of a proposed remedy, and **not part of the clause (c) certification**:

| run | patch | A3d |
|---|---|---|
| `base` | none; `00be534f` as committed | **exit 0** — reproduces arm A3d, so the rest is readable |
| **`A`** | the two `EXPECTED_ELEMENTS` rows ONLY | **exit 0 — STILL ADMITTED** |
| **`B`** | `A` + `m_mx` completeness asserts EQUALITY, with a distinct over-length message | **exit 2 — refused** |
| **`B_on_good`** | `B` against the PASSING product | **exit 0 — no false positive** |

**WHY `A` FAILS, AND IT IS A POLARITY ERROR RATHER THAN A MISSING ROW.** The coverage check is
one-directional: `mii_anchor_comparator.py:885` is `if frac < 1.0:` and it is the ONLY thing in that
loop that sets `class_failed`; the flag above it is `"" if frac >= 1.0`; and
`assert_reduction_is_declared` returns `None` on `coverage >= 1.0` (`:525-526`). At
`10695/10694 = 1.0000935` an over-length array is `>= 1.0` and falls on the unguarded side of all
three. So `A` closes only the SHORT direction — which `sqrt_tr_old`'s recomputation already closed, as
arm A3e shows — and leaves the LONG direction, which is the reachable one.

**THE DEFECT NAMED PROPERLY:** one module, two readers of the same quantity, opposite polarity. The
TH2D discharge path at `:448-480` asserts `int(arr.size) == expected` — **equality**. The `m_mx`
coverage path asserts `frac < 1.0` — **partiality**. The gate rests on the permissive one. That is
verbatim the failure the comment at `:452-460` already records about `r.get("complete", True)` failing
open, recurring one function away.

**RECOMMENDED, NOT LANDED:** candidate `B` — both rows AND the equality assertion, with an over-length
branch carrying its own message, because "PARTIAL COMPARISON" is the wrong words for a 10695-bin array
and reusing them would misreport the defect. `B_on_good` is why this is offered as a fix at all: the
polarity change touches a branch **every** key in the table traverses, so a version that reddened good
products would be a new unavoidable FAIL — and `identity_is_checkable`'s own docstring records that an
unavoidable FAIL at stage 1 is the thing most likely to get the gate routed around. It does not redden
them.

**I did not land it**, on two grounds: the fix belongs to the lane that owns OI-147, and landing
anything mid-verification would have invalidated this file's own digest binding — so `00be534f` is
verified as-is and the hole is REPORTED with its remedy measured. Arm A3d is the power control for
whoever lands it: it must flip from exit 0 to exit 2, and `B_on_good` must stay 0.

**PROVENANCE, because this finding was not mine alone and the sequence matters.** The
`publication closeout` lane — the builder of OI-147 — reported the missing rows to me from a source
reading. I re-derived them and then measured whether they were REACHABLE, rather than reporting a
missing assertion as a defect. That lane then **self-corrected**: it worked out that its own proposed
fix would not fire and told me before I could write it in as the remedy. Its correction is why the
polarity error is named here instead of two ineffective rows being recommended.

**AND ONE MORE INSTANCE OF THE SAME PATTERN, RECORDED AT THAT LANE'S OWN REQUEST.** It asked me to
measure whether the new guard FIRES. It did not ask whether the guard stays SILENT on a good product —
the direction a polarity change actually acts in, and the one that decides whether the remedy is a fix
or a new unavoidable FAIL. So it caught a one-directional check in the comparator and then authored a
one-directional verification request for the repair, minutes after naming the pattern. `B_on_good`
exists because of that gap, and it is the arm that makes `B` recommendable rather than merely
refusing. The inherited instance in the code is the weaker example; this one was authored fresh by
someone who had just named it.

## The answer to the question clause (c) asks

**A fresh non-builder has run the REAL steps (4)/(5) path on a PRESENT-SEED artifact, at production
dimension, with real ROOT, and the complete gate ADMITS a correct product and REFUSES every bad one I
could manufacture — sixteen refusal arms, all sixteen fired, with one measured exception that is
Finding C.**

Stated as narrowly as the evidence allows, because the clause is one of three and the lift is not
mine: on the **upstream-seed identity axis, the configuration-identity axis, and the raw/clipped
diagonal axis**, the chain
`launcher adopt segment -> mii_adopt_unified_5d_stamped.py -> adopt_unified_5d.py -> stamped adopted
root -> mii_anchor_comparator.py stage 1` behaves as its authors claim, on artifacts of the size the
real product has. **`OI-149`'s hole is closed and its closure fires. `OI-147`'s eight-key blocker is
gone, measured against the real archive.** Both of those were the stated preconditions for this rerun
and both hold.

**WHAT THIS DOES NOT SAY.** It does not say the payload is right — the fixtures are diagonal and
synthetic. It does not say any real member reproduces the real archive. It does not say clauses (a) or
(b) hold. It does not say the gate is free of defects: **Finding C is a hole in it that I found and
measured, and it is open.** And it does not lift the pause.

**THE ONE THING I WOULD PUT IN FRONT OF JOSEPH BEFORE ANY LIFT**, because it is not recorded anywhere
else and it is not a matter of judgement: **Finding A.** The launcher hardcodes `REPO` and cds there,
and that tree is 6 commits behind with the **pre-`OI-149`, pre-`OI-147` bytes** of the three modules
this whole exercise is about. Submitting the launcher today would run the code that ADMITS the product
arm 2 refuses. The remedy is one `git pull` in the primary checkout, and it is a precondition of the
lift rather than a consequence of it.

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

## Evidence, committed rather than cited

**THE EVIDENCE TRAVELS WITH THIS FILE.** An earlier draft cited it only by `/pscratch` path, which is
at 79.9% of 20 TiB and is PURGED — a verdict whose only evidence is a purgeable path degrades to an
assertion the moment the purge runs. So it is in the commit, at
`docs/orchestration/runs/clausec-rerun-20260821/`:

| | |
|---|---|
| `results.tsv` | the 22-row arm table, written by the driver from exit codes |
| `production.log.txt` | the full run transcript, including the provenance and self-test sections |
| `logs/gate_<ARM>.log.txt` | all 20 per-arm gate transcripts |
| `logs/probe_{base,A,B,B_on_good}.log.txt`, `probe_remedy.log.txt` | Finding C's remedy probe |
| `harness/` | every script that ran, so the arms can be re-derived rather than re-imagined |

**A NOTE ON `.log` FILES, because it nearly cost this verdict its per-arm evidence silently.**
`.gitignore:15` is `*.log`, so `production.log` and all 20 gate logs **did not stage and nothing
errored** — I noticed only because the commit reported 12 files when I had staged 31. They are
committed as `.log.txt`, which is this repo's existing convention (`MANIFEST.tsv` already carries five
`.log.txt` rows). A peer swept the committed `docs/**` for other receipts whose evidence had been
eaten this way and found none it could substantiate, so this appears to be an instance rather than a
pattern — recorded because the failure mode is silent absence, not error.

**`MANIFEST.tsv` IS NOT UPDATED HERE, DELIBERATELY.** It is GENERATED (`generate_manifest.py`), only 3
of the 14 previously-tracked files under `runs/` carry rows, and this commit passed all 12 pre-commit
checks without one. It is also a shared file that three other lanes were editing while this ran, and
hand-editing a generated view concurrently is the `OI-152` collision exactly.

**CORRECTED 2026-08-21, AND THE CORRECTED CLAUSE WAS MINE.** This paragraph originally ended *"whoever
regenerates it will pick these files up; the absence of rows is not an omission."* **The first half is
FALSE.** `generate_manifest.py` scopes over `git ls-files`, i.e. the tree it runs in — and these 35
files are on `verdict/clausec-rerun-20260821`, with **0** of them on `main`. Measured after the owning
lane reconciled the manifest and reported that **zero paths were added or removed**: my files were
never in the inventory's scope, so no regeneration on `main` can ever pick them up. They enter it only
if this branch is merged and the manifest is regenerated from a tree that contains them.

The conclusion survives and the reasoning that reached it does not: not hand-editing a generated view
was right, but for a reason I did not check rather than the one I gave. **The absence of rows is still
not an omission — it is a consequence of this evidence living on an unmerged branch**, which is a
different fact and the one a later reader needs.

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

---

# ADDENDUM, 2026-08-21, after filing: FINDINGS A AND C ARE BOTH REMEDIED, AND I RE-MEASURED RATHER THAN ACCEPTING THE REPORT

**THE BODY OF THIS VERDICT IS UNCHANGED AND STILL BINDS TO `00be534f`.** This addendum exists because
two of its three findings were acted on within the hour, and a reader arriving later would otherwise
be sent to fix things that are already fixed — Finding A in particular is written as a gating
precondition for the lift.

**The `publication closeout` lane reported both remediations to me. I verified both by measurement, on
the tree that executes, because that lane is one of the five disqualified authors this file names and
its report is not evidence here.**

## Finding A — REMEDIED, verified on the tree the launcher actually cds to

| | at filing | now |
|---|---|---|
| HEAD of `/pscratch/sd/j/josephrb/MINERvA-OmniFold` | `9bf92bde` (6 behind) | **`b2d7d4ca`** |
| `mii_adopt_unified_5d_stamped.py` | `401d8845…` (pre-OI-149) | **`fc520bfd…`** — byte-identical to the digest this verdict certifies |
| OI-149's `DECLARATION MISMATCH` guard in the executing bytes | **absent** | **present** |
| dirty entries | 721 | 721 — **unchanged, so no lane's work was disturbed** |

**So the operative sentence of Finding A is spent: submitting the launcher no longer runs code that
admits the product arm 2 refuses.** What survives from it is the mechanism, and it is the part worth
keeping: **a `${REPO}` hardcode means the tree you review is not the tree that runs, and "6 commits
behind, clean" is a different remedy from "721 dirty entries".** That distinction is why the fix was
one fast-forward and not a reconciliation. The finding's *class* recurs on every future submission and
should be re-measured then, not assumed from this row.

## Finding C — REMEDIED by candidate `B`, and I re-ran my own power controls against it

Landed at `b2d7d4ca`: both `EXPECTED_ELEMENTS` rows **and** `m_mx` completeness asserting equality
with a distinct `OVER-LENGTH` branch — i.e. candidate `B`, not `A`. Re-measured by me on the **real
production-dimension artifacts**, from a clean detached worktree at `b2d7d4ca`:

```
A3d  (the hole: diagonals zero-padded to 10695)      EXIT = 2   VERDICT: FAIL
     [coverage] hDiagCombinedOld:    10695 of 10694 elements (100.0094%)   <-- OVER-LENGTH
     [coverage] hDiagCombinedOldRaw: 10695 of 10694 elements (100.0094%)   <-- OVER-LENGTH
A1   (the good product, unchanged)                   EXIT = 0   VERDICT: PASS
     [coverage] hDiagCombinedOld:    10694 of 10694 elements (100.0000%)
     [coverage] hDiagCombinedOldRaw: 10694 of 10694 elements (100.0000%)
```

**Both power controls behave as specified: A3d flips 0 -> 2 and A1 stays 0.** The remedy fires on the
defect and is silent on a correct product, which is the pair that separates a fix from a new
unavoidable FAIL. Finding C is closed, and it is closed on the artifact rather than in a unit test.

**Finding B is NOT remedied and was never a defect** — it is a property of the launcher, and it stays
true: the declared regime still cannot reach adopt, so arm 1 remains the post-lift configuration.

## What this addendum does NOT change

**THE PAUSE IS STILL NOT LIFTED, AND NOTHING HERE MOVES IT.** Clause (c) was one of three before these
remediations and it is one of three after them. The arm table above stands as measured at `00be534f`;
the two re-measurements in this addendum are at `b2d7d4ca` and are labelled as such, so no reader can
merge the two revisions into one claim. **I did not land either fix and I did not move the primary
checkout** — both were done by the lane that owns the code, which is the correct division, and I
verified rather than performed them.

---

## ADDENDUM 2, 2026-08-21: THE PREDECESSOR THIS VERDICT CITES WAS SINGLE-COPY WHEN I CITED IT

This file's opening section cites the first clause (c) run as *"`33c0e0fa`, branch
`verdict/expiry-c-20260821`"*. **At the moment I wrote that, `33c0e0fa` was reachable from ZERO remote
refs.** It existed on one branch in one local checkout and nowhere else — its 267-line verdict
included. One `git branch -D`, or the loss of that checkout, and the record this rerun is built on top
of would have been gone, **and nothing would have reported it, because a missing branch is not an
error.**

Found by the `publication closeout` lane while checking my own warning that this verdict sits on an
unmerged branch. It pushed `verdict/expiry-c-20260821` to origin — additive, `main` untouched, not
merged. **Verified here across every ref namespace rather than taken on report:** origin now carries 44
refs where it carried 33; `git for-each-ref --contains 33c0e0fa` returns exactly
`refs/heads/verdict/expiry-c-20260821` and its new remote-tracking ref; and
`git merge-base --is-ancestor 33c0e0fa origin/main` is still **false** — pushed, not merged.

**THE POINT THAT GENERALISES, and it is a correction to how I framed my own warning.** I wrote that
putting this evidence on `main` "is a merge decision someone has to take", as though the cost of not
taking it were merely inconvenience. It is not. **The last time this decision went untaken, the
verification record became single-copy and silently so** — for a repo whose own integrity rule is that
*a result is live only after its evidence and required records land in a commit*, a commit reachable
from one local branch satisfies the letter and not the purpose.

**Both verdict branches remain unmerged and that is deliberate.** The owning lane will not merge a
verdict about its own code, and I will not merge my own verdict. It is Joseph's, and the measurement
above is the argument for putting it in front of him rather than leaving it implied. The cost of
merging, stated so the decision is informed: 35+ evidence files enter the inventory's scope, so
`MANIFEST.tsv` must be regenerated **from a tree containing them** — which is exactly what the
corrected clause in the Evidence section above now says, and the reason that correction mattered.
