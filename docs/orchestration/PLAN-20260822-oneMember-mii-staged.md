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

**THE DISCREPANCY, AND IT SHOULD BE SETTLED BEFORE ANY FAMILY AUTHORIZATION.** The figure on record for
the M(ii) family is **151 A100‑h**. This plan measures **2 680 A100‑h** — **17.8× larger**. I have not
reconciled them and I am not going to guess: the likely explanation is that 151 covers a *subset* of
legs (plausibly the training legs alone, excluding the 169‑task sweep at 23.84 A100‑h/member and the
detector leg at 14.23), but **that is a hypothesis, not a finding.** Both numbers cannot be quoted as
the same quantity. **The one-member run settles it by measurement**, which is a further argument for
running one before authorizing fifty.

---

## What I am asking for

Approval to submit **legs 1–6 for `MNV_EST_SEED_OFFSET=0` only**, after a decision on the three stale
replicas in §3. No other member, no family, nothing deleted except — if Joseph so rules — those nine
stale files.
