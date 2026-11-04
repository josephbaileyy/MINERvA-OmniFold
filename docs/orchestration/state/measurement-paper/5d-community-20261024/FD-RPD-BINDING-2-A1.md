# BINDING 2, addendum A1: the run-period diagnosis's MAT environment for `flux` (director, 2026-11-04)

**Binds** [`FD-RPD-DECLARATION-PART2.md`](FD-RPD-DECLARATION-PART2.md), revision 4, sha256
`0afd24bf5291771303d3b02adcf36697364a6b599bee20d2761fcedcb95b1cff`, as merged in PR #739 at
**M′ = `8727c63e1d32599039ea977d833c5de25a9089d6`** (PR head `7d6fecc2`; code commit `66b2f47e`).

**Under** [`FD-RPD-BINDING-2.md`](FD-RPD-BINDING-2.md) (#727) and [`FD-RPD-BINDING-1.md`](FD-RPD-BINDING-1.md)
(#703).

## What led to it

- **Stage S stopped at `flux`,** with rc 1 and `TypeError: 'PlotUtils' is not a known C++ class`.
  - The per-playlist flux histogram is a `PlotUtils::MnvH1D`.
  - Part 2's declared environment, root_6_28 by prefix, has no MAT dictionaries.
  - The 5 ROOT tests used plain-TH1D fixtures and could not see it.
- **5B's jobs ran without MAT.** The lane measured it: `s5c_array.sh` sources the deploy clone's
  `setup_salloc_env.sh`, whose MAT sources are untracked build artifacts that a fresh clone lacks. All 12 of 5B's job
  env logs show those sources failing, and nothing 5B read needed them.

## What the director checked

- **The digest.** The declaration's sha256 at M′ is the one above.
- **The pinned bytes.** All 23 rows of §7 equal `git rev-parse M′:<path>`, with 0 mismatches.
- **The mutation receipt.** "killed 145 of 145; survived 0; not applied 0; files restored True", rc 0, run in a fresh
  throwaway clone at `66b2f47e`. 31 of the mutants are on A1's code.
- **The cluster test receipt** (`fd/receipts-rpd/root_tests_login.log`) was run on login35 at the final code:
  - root_6_28: 287 OK, plus ZeroLoops under `-I`;
  - `check-mat-setup` before sourcing: 6 scripts, 0 mismatches;
  - MATENV: `test_fd_rpd` 125 OK and `test_fd_rpd_mat` 3 OK, with `mat_environment` passing in flux's own invocation;
    mapped MAT files exactly `{libMAT.so}`, and `libMATDict.so → libMAT.so` resolved;
  - no skip and no refusal; porcelain and `squeue --me` empty before and after.
- **The Sonnet check of A1** (1 MAJOR, 5 MINOR, 3 NIT) is committed verbatim, and §9 disposes of each finding.

## Rulings

1. **A1 is bound at M′.** The per-step environment table of §2 governs:
   - `stage`, `verify-staged` and the readers run in root_6_28 by prefix;
   - `flux` runs in the cluster shared checkout's MAT environment, refusing before any staged read unless
     `mat_environment` passes at the pinned digests;
   - job A uses `s5c_array.sh`'s environment, root_6_28 only, as 5B ran.

   The MAT environment is the shared checkout's mutable state, pinned by digest at run time, not by git. Nothing is
   written to the shared checkout.
2. **`$R` is reused** (amending binding 2 ruling 5, as ruled on 2026-11-03):
   - "$R must not exist" applied to stage S's first connect only;
   - every later connect requires `$R` with stage's receipt, runs `verify-staged` (all 79 staged copies against their
     pins and the staging record), and refuses on any mismatch;
   - the second connect deploys to `deploy-2`.
3. **The audit's MAJOR is approved as the lane proposes.** The second connect checks that `$R/flux` is empty and
   `$R/flux-stop1` absent, renames `$R/flux` to `flux-stop1`, and logs to `flux-2.out`. The stop's `flux.out` is left
   untouched.
4. **The committing-tree check is accepted as scoped.**
   - `git diff --stat 66b2f47e`, restricted to the code paths, is empty, and hash-object agrees over all 6,306 tracked
     files.
   - The unscoped diff names only the declaration and the mutation log, which carry later text by design.
   - The in-place subset run killed by the memory reaper was restored, sha `200bc0ac` verified. Every later mutation
     run used a throwaway clone.
5. **Unchanged:** the price (at most 3.0 node-h), the order (stage S, then stage 0 and stage D records to the
   director before job A), the deadline (before 2026-12-15) and what may be claimed (binding 1 ruling 5).
6. **Connects.** The stage-S second connect, then stage 0 (`deploy-3`) and stage D (`deploy-4`), each from a fresh
   clone at M′, with its sha256 sent to the director before it runs.

Nothing is submitted, deposited or tagged.
