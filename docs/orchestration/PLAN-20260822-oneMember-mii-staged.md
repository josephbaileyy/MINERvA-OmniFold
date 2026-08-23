# PLAN 2026-08-22 — staged ONE-MEMBER M(ii) run, for authorization

**Required by [Joseph's ruling 12](DECISION-20260822-joseph-b1-lift-and-clause-c.md) of 2026-08-22,
which selected option (a), the M(ii) member scan, and selected only that.** Ruling 12 authorizes **no**
production: not the 151 A100-hour family, not `C_ML` production, not a full member scan. Marker
backfill remains unauthorized.

**THIS DOCUMENT IS A REQUEST, NOT AN AUTHORIZATION. Nothing here is submitted until Joseph approves
it.** Under ruling 14 the first complete member **is** the real Slurm rehearsal — a production
submission, not a stub test.

Every number below is **measured**, with the command that produced it. Nothing is carried forward.

---

## 1. The exact jobs, and per-leg resource estimates

Six legs, all **member-aware** (they source `lib_member_resume.sh` and namespace their output under
`mii/member_kNNNNNN/`). Verified by `grep -l lib_member_resume.sh *.sh`, which returns nine launchers;
these are the six on this path.

| # | launcher | job name | array | mean/task | per-member cost | billing |
|---|---|---|---|---|---|---|
| 1 | `sbatch_bootstrap_5d_gpu.sh` | `boot5dG` | 1‑100 | **8.4 min** | **14.0 A100‑h** | 32 |
| 2 | `sbatch_seedscan_split_5d.sh` | `ssplit5d` | 1‑24 | 9.3 min | 3.72 CPU‑h | 36 |
| 3 | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | `det5dBKG` | 24 | 35.6 min | **14.23 A100‑h** | 32 |
| 4 | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | `sweep5dBKGrun` | 1‑169 | 8.5 min | **23.84 A100‑h** | 32 |
| 5 | `sbatch_uthrow_run_5d_fast.sh` + `sbatch_uthrow_block_5d.sh` | `uthrow5d_runF`/`_blkF` | 30 + 31 | 42.8 / 42.6 min | 43.4 CPU‑h | 50 |
| 6 | `sbatch_finalize_5d_bkgaware_gpu.sh` | `fin5dBKG` | — | ≤ 1.5 h walltime | ≤ 1.5 A100‑h | 32 |

**Totals per member: ≈ 53.6 A100‑h + 47.1 CPU‑h ≈ 31.4 node‑h** (node‑h = elapsed × billing/128).

**Every leg is individually under 12 h**, so each falls inside the standing walltime grant — but the
grant is about walltime only and does not authorize this scan. Longest single task measured: 77.1 min
(`uthrow5d_blkF`).

**Provenance of these numbers.** Legs 2–5 from `sacct` over the July archive build
(`-S 2026-07-12 -E 2026-07-16`, `COMPLETED` only). Leg 1 uses **8.4 min from the 2026‑08‑18 member run**
(`57252337–9`, nine `COMPLETED` tasks at 8:17–8:51) rather than the July archive mean of 1.6 min — same
code, member namespace, recent, and the archive mean is diluted by short partial runs whose max was
8.7 min. **Using the archive mean would understate leg 1 by 5×.**

**A `sacct` trap that produced a false zero, recorded so it is not repeated:** `sacct -S now-60days`
fails with *"Too wide of a date range in query"* onto **stderr**, while the piped row count returns
**0**. My first pass read that as "no completed records exist." It is a failed query, not an empty
world. Use windows of a few days and read the exit status separately.

## 2. Scratch quota and the disposition of member outputs

`myquota`, 2026‑08‑22: **pscratch 15.99 / 20.00 TiB = 79.9%**; home 22.66 / 40 GiB.

Per-member storage, measured from the archive's own equivalents (`du -sh`, `ls -la`):

| artifact | size |
|---|---|
| `boot_nd_5d/` (100 replicas) | 9.8 MB |
| `seedscan_split_5d/` (24) | 2.4 MB |
| `uq_5d/universe_sweep_bkgaware/` | 27 MB |
| `uq_5d/unified_throw_cov_5d.root` | 2.677 GB |
| `uq_cov_stat_5d.root` | 891.7 MB |
| `uq_cov_mlsplit_5d.root` | 892.1 MB |
| **combined intermediate** | **41.437 GB** |
| 2 × adopted root | 1.784 GB |
| **total** | **≈ 47.7 GB** |

**One member: 15.99 → 16.03 TiB = 80.2%.** Comfortably below the runbook's ~90% abort threshold.

**Disposition:** everything stays in `mii/member_k000000/` until the gate has run. **The 41.44 GB
combined intermediate is NOT deleted** — §11g gates deletion on `MVFINAL_j`, and `MVFINAL_j` has **no
producer, reader or deleter anywhere in the tree** (five occurrences across two files, all prose). So
the protection is procedural. Nothing in this plan deletes anything.

## 3. The exact member and offset for the first submission

**`MNV_EST_SEED_OFFSET=0` → `mii/member_k000000/`.**

k=0 is the **anchor**: it is *declared*, so it writes to `member_k000000/` like every other member, and
the published archive is a **read-only comparand that is not in that directory to be handed back**.
That is what makes bit-exactness checkable at all — it distinguishes *"reproduced the archive"* from
*"was handed the archive"* (`lib_member_resume.sh` header). It is also the only member for which stage
1 has a defined verdict.

Canonical integer, **no leading zeros** — a padded value is octal to bash and decimal to Python and
would seed the estimator from one number, name the directory from a second, and stamp a third as
provenance (`lib_member_resume.sh:63`).

### A blocker inside the chosen member that must be settled first

`member_k000000/boot_nd_5d/` already holds **3 replicas (ids 1, 2, 3) from 2026‑08‑18, with 3 matching
`.done` markers.** They are four days stale and the tree has moved 20+ commits since.

**This is not a detail: the resume guard will SKIP them.** A re-run produces ids 4–100 and reuses 1–3,
so the member's `C_stat` would mix two code revisions — and `--expected-ids 1-100` would **pass**,
because it validates the population, not the provenance. A green gate over a mixed-revision ensemble
is precisely the failure shape this campaign keeps filing.

**Recommended: delete those 9 files (3 `.npz` + 3 `.done`) and regenerate all 100 under one revision.**
Cost is 3 × 8.4 min. **This is a deletion, so it is Joseph's call and is NOT taken here.** The
alternative — reuse — needs an explicit finding that the 08‑18 revision is equivalent for this leg, and
nobody has produced one.

## 4. Terminal success and abort conditions

**Success** — all of:

1. Each leg's array completes with the **exact** expected population: 100 / 24 / 24 / 169 / 61.
2. `sbatch_finalize_5d_bkgaware_gpu.sh` prints `100 replicas` and `24 replicas`, then reaches
   `[fin-bkg] done`, with both adopted roots present.
3. The stage‑1 gate exits **0**: `[b2] VERDICT: PASS`, coverage `114361636 of 114361636` (= 10694²),
   both diagonals at **10694**, both `[identity] OK` lines, both `[recompute] OK`, and
   `grep -c "EXCUSED BY THE ARCHIVE'S AGE AND NOT VERIFIED BY ANYTHING"` = **0**.
4. `verify_hash_bindings.py` still reports **ALL BINDINGS INTACT** afterwards.

**Abort immediately, do not work around** — the full table is §6 of
[`RUNBOOK-20260822-b1-lift-preflight.md`](RUNBOOK-20260822-b1-lift-preflight.md). The ones specific to
this run:

| signal | do |
|---|---|
| `exit 5` from the launcher | **stop.** Never set `RESUME_ADOPT_LEGACY=1` or `RESUME_FORCE=1`. |
| `exit 3` | wrong-member marker — a product from another `k`. **stop.** |
| `replica id mismatch` | population short. **Do not relax `--expected-ids`.** |
| gate `INCOMPLETE` (exit 1) | **do not** pass `--acknowledge-unrecomputable` to green it. |
| gate `OVER-LENGTH` | the artifact was altered after the wrapper finished. **stop.** |
| any refusal naming the 41.44 GB intermediate as corrupt | the `D1` false-corruption shape. **Stop; do not touch that file.** |
| pscratch > 90% | stop and resize. |

**Because this is also the Slurm rehearsal (ruling 14),** three things untested by any prior harness
must be watched and reported whether or not they fail: the `lib_member_resume.sh` **resolver** under a
real spool copy (`BASH_SOURCE` is the spool path, not the script's home — set `MNV_LAUNCHER_DIR`
explicitly); the **executing-tree digests** against `main` before submission; and the `${REPO}`
hardcode's real effect, given the deploy tree carries 721 dirty entries.

## 5. What a one-member pass CANNOT authorize

Stated in the negative, because a green run reads as broader permission than it is:

- **Not the remaining 49 members**, and not the family's cost (§6 shows why that is a separate call).
- **Not `C_ML` production**, which ruling 12 excludes by name.
- **Not the 151 A100‑hour family**, which ruling 12 also excludes by name — and see §6.
- **Not marker backfill**, and not the undeclared re-adoption route. Still unauthorized.
- **Not deletion of the 41.44 GB intermediate.** `MVFINAL_j` has no implementation.
- **Not removal of the launcher's pause branch** — ruling 13 defers that until a member is runnable,
  and one member being runnable is not the same as the branch being safe to delete.
- **Nothing about members k≠0.** k=0 is the anchor and the only member with an archive comparand; a
  pass there says nothing about a member whose products cannot be compared to anything.

## 6. Remaining cost and storage for the full family — AND A DISCREPANCY TO SETTLE FIRST

Linear extrapolation from §1 and §2, for 50 members:

| | one member | ×50 |
|---|---|---|
| A100‑h | 53.6 | **2 680** |
| CPU‑h | 47.1 | 2 355 |
| node‑h | 31.4 | **1 570** |
| storage | 47.7 GB | **2.17 TiB** |

**Storage puts pscratch at 15.99 + 2.17 = 18.16 TiB = 90.8%, which is OVER the runbook's ~90% abort
threshold.** The family does not fit as-is. Either members are archived to HPSS as they complete, or
the intermediate is released per member once `MVFINAL_j` exists — and `MVFINAL_j` does not exist. **That
is a prerequisite for the family, not a detail of it.**

**~~THE DISCREPANCY~~ — WITHDRAWN 2026-08-22, AND THE HYPOTHESIS BELOW WAS WRONG.** This section read:
*"The figure on record for the M(ii) family is 151 A100‑h. This plan measures 2 680 A100‑h — 17.8×
larger … the likely explanation is that 151 covers a subset of legs (plausibly the training legs
alone …)."* **There is no discrepancy, and the subset hypothesis is false.** The two figures count
**different populations**: 151 A100‑h counts **50 Gate-5 PET `C_stat` training replicas**; 2 680
counts **50 M(ii) members**. They were never the same quantity, so no measurement of an M(ii) member
could ever have reconciled them — the one-member run does **not** settle this, and citing it as a
reason to run one was wrong.

**The tell was available without any run.** `2680/151.175 = 17.728` and `53.6/3.0235 = 17.728`
*identically*, because the 50 cancels on both sides. A ratio invariant under population size is a
**per-unit** comparison wearing a total's clothing. Against the correct in-family prior of
**1 961.2 GPU‑h** the real gap is **1.37×** — one leg re-priced, not an order of magnitude.

**What survives as a live question is SIZING, not cost:** 50 members at 2.17 TiB cross the pscratch
operational line, and 46 do not. That is `PR-J3` in `PUBLICATION-READINESS-20260822.md`, and it is a
policy call on a soft quota, not a physical limit — see that row for the soft/hard figures.

---

## What I am asking for

Approval to submit **legs 1–6 for `MNV_EST_SEED_OFFSET=0` only**, after a decision on the three stale
replicas in §3. No other member, no family, nothing deleted except — if Joseph so rules — those nine
stale files.


---

# AMENDMENT 1, 2026-08-22 — corrections required by Joseph before submission

## A. The file count was wrong: SIX, not nine

**My error, caught by Joseph.** `member_k000000` holds **3 `.npz` + 3 `.done` = 6 files.** I wrote
"nine" by taking the **9 `.npz` across all three members** and reporting it as one member's file count
— two right measurements of different populations, quoted as one. The same axis as the 18-vs-9
confusion earlier the same day, and I made it in the document correcting that one.

**Authorized disposition (Joseph, 2026-08-22): quarantine, do not delete and do not reuse.** Move
exactly those six files to a recoverable location outside every production and resume glob, after
recording for each: original path, sha256, size, mtime, **complete marker contents**, and Slurm job
identity. Then regenerate ids 1–3 with the new production set. **No other file may be moved or removed
under this authorization.**

Slurm identities already located for the receipt: `57252337_{1,2,3}`, `57252338_{1,2,3}`,
`57252339_{1,2,3}` — nine `COMPLETED` tasks at 8:17–8:51 on 2026-08-18, three per member.

## B. SIX LOGICAL LEGS, SEVEN SBATCH SUBMISSIONS — the structure, corrected

`uthrow` is **three** submissions, not two. `sbatch_uthrow_combine_5d_fast.sh:10` states it:
*"Submit with `--dependency=afterok:<throwjob>:<blockjob>`. Writes the SAME target."* I had counted
`runF` and `blkF` and missed `combF`.

| # | launcher | job name | array | measured cost |
|---|---|---|---|---|
| 1 | `sbatch_bootstrap_5d_gpu.sh` | `boot5dG` | `1-100` | 8.4 min/task → 14.0 A100‑h |
| 2 | `sbatch_seedscan_split_5d.sh` | `ssplit5d` | `1-24%24` | 9.3 min/task → 3.72 CPU‑h |
| 3 | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | `det5dBKG` | 24 | 35.6 min/task → 14.23 A100‑h |
| 4 | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | `sweep5dBKGrun` | `1-169%48` | 8.5 min/task → 23.84 A100‑h |
| 5a | `sbatch_uthrow_run_5d_fast.sh` | `uthrow5d_runF` | `0-39%40` | 21.38 CPU‑h total |
| 5b | `sbatch_uthrow_block_5d.sh` | `uthrow5d_blkF` | `0-20%10` | 22.02 CPU‑h total |
| 5c | `sbatch_uthrow_combine_5d_fast.sh` | `uthrow5d_combF` | single | **UNMEASURED — see below** |
| 6 | `sbatch_finalize_5d_bkgaware_gpu.sh` | `fin5dBKG` | single | ≤ 1.5 h walltime |

**`uthrow5d_combF` has no measured cost and I am not estimating one.** `sacct` over the July archive
window returns no `COMPLETED` record for that name. This is a **real null**, not the failed-query kind:
the identical query form returned data for the other four names in the same window. Its walltime
request is **3 h, 1 node, 16 CPUs, 90 GB**, so the budget ceiling is 3 CPU‑h; the actual figure comes
out of the k=0 run itself.

**The array sizes and the completed counts do not match** (`runF` requests 40 and 30 completed;
`blkF` requests 21 and 31 completed). That is consistent with reruns in the July window. The **cost**
figures above are the summed `COMPLETED` elapsed, which is the right operand for a budget; the array
sizes are what gets submitted. They are different quantities and are listed separately on purpose.

## C. Exact submission commands and dependency order

All from `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding` on a login node, after
`source ../setup_salloc_env.sh`, with the member declared in the submitting shell:

```bash
export MNV_EST_SEED_OFFSET=0          # canonical integer, NO leading zeros
export MNV_LAUNCHER_DIR="$PWD"        # sbatch runs a spool COPY; BASH_SOURCE is not the script's home
```

**Independent roots — submit together:**

```bash
JB=$(sbatch --parsable sbatch_bootstrap_5d_gpu.sh)                    # leg 1
JS=$(sbatch --parsable sbatch_seedscan_split_5d.sh)                   # leg 2
JD=$(sbatch --parsable sbatch_unfold_5d_detector_bkgaware_gpu.sh)     # leg 3  -> the member CV
JR=$(sbatch --parsable sbatch_uthrow_run_5d_fast.sh)                  # leg 5a
JK=$(sbatch --parsable sbatch_uthrow_block_5d.sh)                     # leg 5b
```

**Dependent:**

```bash
JW=$(sbatch --parsable --dependency=afterok:$JD sbatch_sweep_bank_5d_run_bkgaware_gpu.sh)   # leg 4
JC=$(sbatch --parsable --dependency=afterok:$JR:$JK sbatch_uthrow_combine_5d_fast.sh)       # leg 5c
# LEG 6 IS NOT SUBMITTED HERE -- it is gated on the staged review (see D).
```

**Why leg 4 waits on leg 3, established from the code rather than assumed:** leg 3 writes
`5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` into `uq_5d/universe_sweep_bkgaware/` (`:85`), which is
both the member's CV — the value the finalize launcher reads as `CV` under `mr_declared` — and the
same directory leg 4's 169 universes populate. Legs 1, 2, 5a and 5b reference nothing the others
produce; grepping `sbatch_uthrow_{run,block}_5d.sh` for the sweep returns **nothing**, so the unified
throw is independent of the sweep and can start immediately.

**Leg 6 is deliberately absent from this block.** Under Joseph's staging it is submitted only after
legs 1–5 validate, the declared-member pause branch is removed, and a fresh non-builder reviews that
removal.

## D. Correction 2/3/4 — the execution-integrity requirement, and why the parent-only wrapper fails

**The mechanism already exists and its own author documented the hole Joseph named.**
`nd-unfolding/mnv_guarded_run.py` wraps the stdlib `PathFinder` in `sys.meta_path` and exits **3** when
any import resolves inside a MINERvA-OmniFold checkout other than `--expect-root`. It is already wired
into two Gate-5 launchers, and it carries 21 tests whose first assertion is that the fixture
**genuinely hijacks when unguarded** — a guard test whose fixture does not hijack passes vacuously.

Its docstring states the limit in capitals, measured rather than suspected:

> **IT DOES NOT CROSS A SUBPROCESS BOUNDARY, AND THAT IS MEASURED, NOT SUSPECTED.** […] a child started
> with `subprocess.run([sys.executable, ...])` gets a fresh interpreter with a clean `sys.meta_path`
> […] Both halves are asserted in `tests/test_mnv_guarded_run.py::TheSubprocessBoundaryIsNotCovered`.

and it names this exact path as the live instance:

> `mii_adopt_unified_5d_stamped.py` […] runs it AS A SUBPROCESS, deliberately, so that the bytes whose
> sha256 is pinned are the bytes that execute. `adopt_unified_5d.py` is one of the fail-open 59. So
> wrapping that adoption path in this guard would print a clean banner and refuse nothing.

Confirmed at the source: `adopt_unified_5d.py:35-38` sets `_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"`
and inserts two paths under it at `sys.path[0]`. **`PYTHONPATH` cannot outrank position 0.**

**THE MINIMUM SUFFICIENT FIX, and it does not touch a pinned science file.** Guard the **child**, not
the parent: have `build_child_argv` (`mii_adopt_unified_5d_stamped.py:287`, separated out *"so a test
can read it"*) emit

```
[python, mnv_guarded_run.py, --expect-root <clean tree>, --, adopt_unified_5d.py, ...]
```

The child interpreter then installs the guard **before** importing anything, so
`adopt_unified_5d.py`'s rooted `insert(0, …)` is caught **at import resolution**, which is where the
guard acts — not at path-insert time. Fail-closed, exit 3, before any scientific work.

**Why not the alternatives.** Editing `adopt_unified_5d.py` to resolve from `__file__` is the correct
END state that `OI-136` asks for, and Joseph's correction 4 does authorize *"their necessary hash
bindings"* — but that file's sha256 is bound by `ben106-stamp-verify-active-56695424.json`, which
`mii_adopt_unified_5d_stamped.assert_pinned_writer_is_intact` reads **every run**, so the change
requires re-issuing the receipt of the owning gate. Wrapping the child leaves the pinned bytes
executing unchanged and keeps that safety argument intact. Setting `PYTHONPATH` cannot work at all.

**What still has to be built, and it is not done yet:**

1. the `build_child_argv` change plus its `--expect-root` plumbing;
2. the same guard on every other Python entrypoint on the k=0 path;
3. **a negative control proving an import from another checkout is refused before scientific work
   begins** — modelled on the existing suite's rule that the fixture must genuinely hijack unguarded;
4. binding and verifying the actual executing and imported files against the approved clean tree, and
   **not executing from the 721-entry dirty canonical checkout**;
5. a **fresh non-builder** verification of all of the above.

**None of this is verified by me and none of it authorizes submission.** Item 5 is the gate.


---

# AMENDMENT 2, 2026-08-22 — Joseph's three clarifications to corrections 2–4

## 1. Six logical legs, seven submissions — and the combine cost stays unmeasured

The structure is **six logical legs requiring seven `sbatch` submissions**: the unified-throw leg is one
logical leg delivered by three jobs (`uthrow5d_runF`, `uthrow5d_blkF`, and `uthrow5d_combF` on
`--dependency=afterok:<run>:<block>`). Amendment 1 said "seven jobs, not six" and Joseph's framing is the
right one — it keeps the dependency graph and the leg count from being confused for each other.

**`uthrow5d_combF`'s cost remains UNMEASURED and is to be recorded from the k=0 run**, not estimated
now. Its walltime request bounds it at 3 CPU-h. Carrying an unmeasured field as unmeasured is the point:
a plausible placeholder becomes a quoted number the moment someone reads past the caveat.

## 2. THE GUARD CATCHES A RESOLUTION, NOT AN INSERTION — and a green production arm may be vacuous

**Correcting my own Amendment 1 wording before anyone relies on it.** I wrote that the child-wrap means
`adopt_unified_5d.py`'s rooted `insert(0, …)` "is caught at import resolution". **Do not say that.**
`mnv_guarded_run.py` fires when an import **resolves** inside a checkout other than `--expect-root`. A
`sys.path.insert()` that no import ever traverses is invisible to it and always will be.

**The consequence, which is the real risk and which I had not stated:** if the production k=0 arm inserts
the canonical root but imports **no repository module through it**, the guard refuses nothing and exits 0
— and that zero is **indistinguishable from a clean run**. "No refusals" is exactly what a guard that
never saw a repository import produces. A green arm is therefore **not** evidence on its own.

Joseph's requirement, verbatim, and it is now the specification:

> "For the pinned adopter, demonstrate that the production arm imports no repository code from another
> checkout. The negative control must introduce or select a genuine repository-local import resolving
> from the wrong checkout and prove exit 3 before any scientific output is opened or written. Do not
> claim that the path insertion itself was caught."

So two separate obligations, and the first is **positive evidence**, not an absence:

- **Production arm:** demonstrate — by enumerating what `adopt_unified_5d.py` actually imports and where
  each resolves from — that **no repository module resolves outside the approved clean tree**. A refusal
  count of zero does not establish this. **What that module imports is UNMEASURED as of this writing, and
  deliberately so:** the review contract is being agreed before the builder measures it, so the controls
  cannot be shaped around the answer.
- **Negative control:** a **genuine repository-local import** resolving from the wrong checkout, proving
  **exit 3**, with evidence that the refusal preceded any scientific output being **opened or written** —
  ordering evidence, not just an exit code. Inherits the existing suite's rule that the fixture must
  **genuinely hijack when unguarded**, since a control whose fixture does not hijack passes vacuously.

## 3. The submission commands must name the approved clean tree

Amendment 1 §C shows the working directory as
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding`. **That is the 721-entry dirty canonical
checkout and it is NOT the approved execution tree.** The final commands must name the clean tree, and
the `--expect-root` passed to the guard must be that same tree. Amendment 1 §C stands only as the
dependency graph and argument shape; **its paths are superseded here** and will be rewritten once the
clean tree is designated in the review contract.

**`--allow` for the dirty canonical checkout is FORBIDDEN.** It would make the guard green by declaring
the problem acceptable, which is the "re-point a receipt-bound file to make a check pass" move in
another costume.

**Where a wrapper is not enough, a scoped source repair is authorized:** *"For entrypoints whose
hardcoded insert would actually resolve repository imports from the canonical checkout, make the minimum
authorized scoped repair needed for clean-tree execution."* Bounded by correction 4 — this k=0 path's
launchers and entrypoints and their necessary hash bindings only. **Not** the repository-wide 59-file
`OI-136` migration, and no scientific-model change.

## Review contract status

A fresh non-builder has been engaged **before implementation**, on Joseph's instruction, so the controls
are agreed before the builder selects the evidence. The reviewer has been asked to specify the positive
arm, the negative control and its ordering evidence, the clean-tree definition and binding method, any
entrypoint needing a scoped repair rather than a wrapper, and written PASS/FAIL criteria. **Nothing is
built until that contract exists, and nothing is submitted until the reviewer records a clean PASS.**

On a clean PASS the conditional authorization becomes operative without a further permission round:
quarantine the six files, regenerate ids 1–3, and submit the seven jobs of logical legs 1–5 for k=0.
