# A pin one hop away is still a pin, and the gate-pin check cannot see it

**BEN-270. Filed 2026-08-14 by the Gate-6 Leg 0 lane (BEN block `270-279`, claimed in the same commit).**

`PLAN-20260813-gate6-cml-retry-design.md:156-161` authorizes Leg 0's code change and prices it:

> a `--checkpoint-tier {auto,best-epoch,final}` control on `step1_increment_trajectory.py`, defaulting to
> `auto` (today's behaviour). That file is **not** in the Gate-4 code gate's pin list — verified against
> `p3f-pet-gate4-launch-code-gate-20260813.json`, whose `files` block names 19 distinct paths and does not
> include it — so this is a code change with **no gate re-issue**, only a new launcher pin, because the
> trajectory launcher hardcodes its sha256 (`48f8353d…`).

Both halves were re-derived rather than trusted, because the lane brief required it. **The first half is
correct. The second half is wrong, and the way it is wrong is the finding.**

## 1. The Gate-4 half, and how it was made a covering search

A null grep is evidence about the search, not about the world, so the check was built to fail loudly if it
had gone blind:

- The receipt was **parsed**, and **every** leaf walked — not just the `files` block. 138 string leaves.
- `files` holds 19 entries resolving to **19 distinct paths**. 19 == 19, so no duplicate is concealing a
  twentieth entry, and the PLAN's count is right.
- Zero of the 138 leaves contain `step1_increment_trajectory`.
- **Aliasing was ruled out on the raw bytes, not the parsed tree.** `trajectory` occurs in the file.
  `step1` occurs in the file. `increment` occurs **zero** times. So the null is not the signature of a
  search that would have missed a hit under a different spelling — two of the three tokens do hit.
- All 31 path-like (`.py`/`.sh`) strings anywhere in the document were enumerated: the 19 pins plus prose
  mentions, none of them this file.

**Verdict: no Gate-4 re-issue. The PLAN is right.** That is worth stating plainly, because the rest of this
note is a correction and the correction does not touch this part.

## 2. The half that was wrong

`git grep` on the pinned sha, run because the PLAN named a launcher and a *count of one* is exactly the
kind of claim that is cheap to check:

| launcher | line | frozen by |
|---|---:|---|
| `sbatch_gate6_member_trajectory_array.sh` | 66 | `state/gate6-trajectory-array-active-56847059.json` @ `13a598f2` |
| `sbatch_pet_fullevent_floor_replicate_array.sh` | 116 | `state/gate6-floor-replication-active-56863958.json` @ `b0308f24` |
| `sbatch_pet_fullevent_legx_2x2_array.sh` | 177 | — |

**Three launchers, not one. And two of those three launchers are themselves hash-bound by active run
receipts.**

So the dependency chain that freezes the `.py` is two hops long:

```
step1_increment_trajectory.py          <- edited
  pinned by sbatch_*_array.sh          (hop 1: the PLAN saw this one, and undercounted it 1-for-3)
    pinned by state/*-active-*.json    (hop 2: nothing in the PLAN or the brief looked here)
```

A gate-pin check answers *"is this file frozen?"* by looking one hop out, at the receipts that name the file
directly. It is structurally incapable of seeing hop 2, because at hop 2 the file's name does not appear
anywhere — what appears is the launcher's digest.

## 3. It was caught by running the verifier, not by reading

Worth recording precisely, because the reading order was wrong and the outcome was still correct:

1. The in-place re-pin was made in **all three** launchers, `48f8353d` → `ca2128ac`, and verified by
   `git grep` to have hit exactly three sites and left zero occurrences of the old sha.
2. `docs/orchestration/verify_hash_bindings.py` was then re-run. **rc=1**, two `MISMATCH` blocks, and
   `nd-unfolding/tests/test_hash_bindings.py::test_no_new_broken_hash_bindings` red.
3. The edit was reverted with `git checkout --`, and the restored digests were compared against the values
   the two receipts freeze: `13a598f2…` and `b0308f24…`, both exact. Verifier back to
   `ALL BINDINGS INTACT`.

The verifier had been run **before** the edit too, as a baseline. That is the only reason step 2's rc=1 was
attributable to this lane rather than inherited: the baseline was already `rc=0` with the same four known
drift entries. **A verifier run only after a change tells you the tree is broken, not who broke it.**

## 4. Why the receipts were not updated, and why the allowlist was not used either

Two escapes were available and both are wrong.

**Editing the receipts' hashes.** Forbidden by the instrument's own docstring, which is unusually direct
about it (`verify_hash_bindings.py:34-36):

> A stale pin is not repaired by editing the hash. The constant records what the gate ran against; moving it
> to match the working tree converts the guard into a no-op and destroys the evidence. Re-issue the owning
> gate and record the move.

Both receipts are submit-time provenance of runs that **COMPLETED** — 56847059 (five trajectory tasks,
00:13:44–00:14:00 each) and 56863958 (the floor replication). The bytes that ran were `13a598f2` and
`b0308f24`. Rewriting the receipts so a later code change fits would make them describe a run that never
happened.

**Appending to `KNOWN_PREEXISTING`.** Also rejected, and this one is more tempting because the set exists
and the mechanism works. But it is explicitly scoped:

> Bindings known to have drifted **before 2026-07-28** and deliberately not "fixed"

Its stated purpose is *"Listed so real regressions stay visible above the noise."* Putting a regression
created tonight into the set that exists to distinguish tonight's regressions from historical noise inverts
the instrument. A four-entry allowlist that grows whenever it fires is a five-entry allowlist that never
fires again.

## 5. What was done instead

**No existing launcher is touched.** All three keep pinning `48f8353d`, and that pin remains **correct**,
because they read the code out of `/pscratch/sd/j/josephrb/gate6-reconcile-56834281` and that tree is left
byte-identical — verified on the cluster in the same turn: `48f8353d…`, git HEAD `4d96acf`.

The new pin lives in a new file, `nd-unfolding/pet/sbatch_gate6_leg0_tier_calibration_array.sh`, which:

- pins `step1_increment_trajectory.py` at `ca2128ac` and every other file at the 56847059 values, so the
  two arms differ in exactly one file;
- takes its code tree from a **mandatory** `G6_LEG0_CODE_REPO` with **no default**, and refuses both
  `gate6-reconcile-56834281` and the frozen `gate6traj-reconcile-56847059` by name, testing the raw **and**
  canonicalized path. An unresolvable canonicalization falls back to the raw string, not to `""` — a `case`
  over the empty string matches no pattern, so testing the canonical form alone makes the guard fail **open**
  in exactly the situation it exists to catch. Exercised against a trailing slash and against a symlink
  whose own name is innocent and whose target is frozen.

This is the precedent `sbatch_pet_fullevent_ml_ensemble.sh` already sets for "why a new launcher", and it is
what the PLAN itself prescribes for Leg F.

## 6. The transferable check

**Before editing a file, `git grep` its sha256 — and then ask whether the files that turned up are
themselves pinned.** One hop is not enough. The cheap form:

```
git grep -l "$(shasum -a 256 <file> | awk '{print $1}')"        # hop 1: who pins me
# for each hit H:
git grep -l "$(shasum -a 256 H | awk '{print $1}')"             # hop 2: who pins H
```

and then, non-negotiably, **run `verify_hash_bindings.py` before and after the edit**, because the
transitive closure is what that script computes and hand-tracing it is how a hop gets missed. The baseline
run is not optional: without it, rc=1 afterwards is ambiguous between your change and inherited drift.

## 7. What is left open

`OI-123`. The three launchers all die with `code hash mismatch: step1_increment_trajectory.py` the moment
the new `.py` is synced into `gate6-reconcile-56834281`. Leg 0 dodges this by construction, but the hazard is
real for anyone else who syncs, and the durable fix — re-issuing the floor-replicate and legx launchers with
their owning receipts — belongs to those receipts' owners. `legx_2x2` is the cheap half: it is bound by no
receipt, so it can be re-pinned as soon as its code tree is decided.

## 8. What this finding is not

It is **not** a claim that the PLAN was careless. The PLAN checked the gate that the repo tells you to check,
named the file it checked, and gave the digest it relied on — which is precisely why the error was findable
in ten minutes. **A wrong claim that ships its ingredients is worth more than a right one that does not**
(`CONVENTION-receipt-ingredients.md`, BEN-077). The failure is in the *check*, which has no hop-2 arm, not in
the person running it.

It also does **not** bear on Leg 0's physics. Nothing here says anything about the tier systematic, member
3's verdict, or the Gate-6 family. Those are unmeasured; no job has been submitted.
