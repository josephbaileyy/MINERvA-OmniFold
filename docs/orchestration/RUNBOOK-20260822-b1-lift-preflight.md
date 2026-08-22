# RUNBOOK 2026-08-22 — B1 steps 4–5 preflight, for the first submission after the lift

**Required by [Joseph's ruling 4](DECISION-20260822-joseph-b1-lift-and-clause-c.md) of 2026-08-22.
No production submission before this document is on `main`.**

Written by the publication close-out lane. Everything numeric here was **measured on the cluster on
2026-08-22**, not carried forward; every measurement carries the command that produced it so a later
reader can falsify it rather than trust it.

---

## 0. THE HEADLINE, AND IT IS NOT WHAT THIS RUNBOOK WAS EXPECTED TO SAY

**Do not submit `sbatch_finalize_5d_bkgaware_gpu.sh` yet. Both of its routes refuse today, for
reasons that have nothing to do with the pause, and lifting the pause does not change either.**

| route | where it stops | why |
|---|---|---|
| **declared** (`MNV_EST_SEED_OFFSET` set) | **two** back-to-back `mr_run` calls, `sbatch_finalize_5d_bkgaware_gpu.sh:167` **and** `:168` | `:167` wants **100** bootstrap replicas and finds **3**; `:168` wants **24** seedscan splits and finds **0**, with `seedscan_split_5d/` **absent entirely**. Clearing the first does not clear the second. |
| **undeclared** (offset unset) | `:253`, `exit 5` | the 41.44 GB intermediate has **no completion marker** |

Neither is a defect. Both are guards working as designed. But it means **the first production
submission is not this launcher**, and a submission made on the strength of the lift alone would fail
in a way that reads as a broken lift.

This is the finding the runbook exists to produce. Section 3 has the evidence; section 6 says what
the first submission actually is.

## 0b. THE EXECUTION TREE IS NOW A PARAMETER, AND IT HAS NO DEFAULT

**Added 2026-08-22 on [Joseph's ruling 17](DECISION-20260822-joseph-b1-lift-and-clause-c.md), which
supersedes every working-directory instruction written before it in this file and in
[`PLAN-20260822-oneMember-mii-staged.md`](PLAN-20260822-oneMember-mii-staged.md) Amendment 1 section C.**

All eight launchers on this path used to open with an unconditional
`REPO="<the canonical checkout>"`. That decides the executing tree before any interpreter or guard
starts, so no Python-side work reaches it. They now take **two mandatory variables with no default**:

| variable | what it is | rule |
|---|---|---|
| `MNV_CODE_ROOT` | the approved clean execution tree | every `.sh` sourced and every `.py` executed or imported resolves under it; immutable and `git status --porcelain`-empty for the run, at a **named sha** recorded in the receipt |
| `MNV_DATA_ROOT` | inputs and products | the canonical checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold` is acceptable **in this role only**; nothing is executed or imported from it |
| `MNV_GUARD_INVENTORY_DIR` | run-scoped directory for the OI-136 resolved-origin records | added round 2. One file per guarded process. A guarded run that emits no record establishes nothing, so this is REQUIRED |
| `MNV_SOURCE_MANIFEST` | the A-2(f) source manifest recorded from `MNV_CODE_ROOT` **before the first `sbatch`** | added round 2. Compared on every leg; a moved source byte aborts before any Python starts |

**A-2(c)(d)(e)(g) ARE ENFORCED FROM ROUND 3, not documented.** Every launcher runs, before anything
else and failing closed at each step:

```bash
python3 "${MNV_CODE_ROOT}/nd-unfolding/mnv_source_manifest.py" --repo "${MNV_CODE_ROOT}" \
  --compare "${MNV_SOURCE_MANIFEST}" --require-clean --require-checkout \
  --require-no-nested-checkout --require-not-nested --require-readonly
```

Constitute and protect the code root with the SAME tool, in one command, before the first `sbatch`:

```bash
python3 "${MNV_CODE_ROOT}/nd-unfolding/mnv_source_manifest.py" --repo "${MNV_CODE_ROOT}" \
  --apply-readonly --require-clean --require-checkout --require-no-nested-checkout \
  --require-not-nested --require-readonly --write "${MNV_SOURCE_MANIFEST}"
```

`--undo-readonly` lifts it when the tree must be refreshed. **Do not hand-roll the `chmod`** — the
recipe this runbook nearly carried was wrong in a way that silently protected only half the tree
(receipt §7.2), and the flag chmods exactly the set the check verifies.

(d) and (e) are one hazard from two sides: `checkout_root_of` returns the INNERMOST match, so a
checkout nested inside the code root resolves to itself, is not `--expect-root`, and every module
under it is refused on a tree that looks approved. A peer's live `.claude/worktrees/` audit checkout
is the recorded instance — it made the OI-136 ratchet read 369 instead of 58.

**Why two and not one.** A clean checkout cannot simultaneously host ~47.7 GB of gitignored member
products and remain clean, and `of_inputs_5d.npz` is absent from a fresh clone, so a clean tree
cannot serve as the working directory at all.

### 0b-0. ROUND 2, 2026-08-22: EVERY PRODUCTION PYTHON INVOCATION IS GUARDED

Joseph, round 2: *"every production Python invocation across the eight k=0 launchers is to be routed
through `mnv_guarded_run.py`, with a required inventory ... including the contract-required
executing-file parity calls, source-manifest comparison, and P-4 import-set mechanism."*

**FOURTEEN invocations, not eight.** Re-derived with `grep -nE 'python[0-9]*'` over the eight
launchers: bootstrap 1, seedscan 1, detector 2 (CV and universe branches), sweep 1, uthrow run 1,
uthrow block 2 (knobs and flux), uthrow combine 1, finalize 5. Do not assume one per launcher.

Each now runs as `python3 "$GUARD" --expect-root "$CODE_ROOT" --inventory "$(mnv_inv <tag>)" --
<entrypoint>`, and every launcher first runs, in this order and failing closed at each step:

1. `mnv_source_manifest.py --repo "$CODE_ROOT" --compare "$MNV_SOURCE_MANIFEST" --require-clean`
2. `verify_executing_copy_is_committed.py --repo "$CODE_ROOT" --pair ...` over the files it executes
   plus the guard, the parity checker and the manifest tool
3. a containment check that `lib_member_resume.sh` resolved under `${MNV_CODE_ROOT}/nd-unfolding`

**Why this became worth doing between round 1 and round 2, and it is not a change of mind.** The
contract's B-1 held that a wrapper "cannot help them and would block the run" — true of the
PRE-REPAIR bytes, where `import xsec_nd` resolved under the canonical checkout and the guard
correctly exited 3. That argument expired with the six source repairs. Measured on the cluster
2026-08-22 (`RECEIPT-20260822-k0-n1-and-guarded-arms.md` §3): the guarded parent reports
`checked = 9`, `repo_origin_count = 1`, `seed_offset_policy` resolved **under the code root**. Green
AND non-vacuous, which a bare exit 0 never was.

**After the last leg**, read the verdict off the records rather than off any exit code:

```bash
python3 "${MNV_CODE_ROOT}/nd-unfolding/mnv_import_set_ratchet.py" \
  --inventory-dir "${MNV_GUARD_INVENTORY_DIR}" --pins <the pins> \
  --source-manifest "${MNV_SOURCE_MANIFEST}"
```

It checks P-2 (every origin under the code root, every sha256 in the manifest, `checked > 0`), P-3
(the emptiness flags PRESENT, and a zero only where declared with its disclosure) and P-4 (the
per-entrypoint import set as an IDENTITY, not a floor). Pins come from `--write-pins` on the first
clean run; there is no hand-authored expected list.

**`${VAR:-<hardcode>}` IS FORBIDDEN.** A default is the hardcode wearing a flag, and a defaulted
variable that is silently empty makes every path below name a different subject without erroring.
The form is `"${MNV_CODE_ROOT:?<message>}"`, the same as
`pet/sbatch_gate6_leg0_tier_calibration_array.sh:64`. Measured 2026-08-22: with either variable unset
**or empty**, all eight launchers exit non-zero before sourcing anything
(`nd-unfolding/tests/test_k0_launcher_two_roots.py`).

### 0b-i. Constituting `MNV_CODE_ROOT`, before the first `sbatch` and again after the last leg

`git clone` or `git worktree add` at a named sha. Record all of it; any difference between the two
measurements aborts the run.

| # | requirement | instrument |
|---|---|---|
| a | `git rev-parse HEAD` equals the declared sha | quote the sha, never "main" |
| b | `git status --porcelain` emits **zero lines** | count lines; never read `$?` after a pipe |
| c | it is a checkout by the guard's definition — `VALIDATION_LEDGER.md` **and** `nd-unfolding/` both present | otherwise the guard exits **2**, and 2 is "we could not look", never "clean" |
| d | **no nested MINERvA-OmniFold checkout anywhere beneath it**, in particular no `.claude/worktrees/` content | `checkout_root_of` returns the innermost match, so a nested checkout resolves to itself and is refused |
| e | it is **not** nested inside another checkout | same reason, opposite direction |
| f | `sha256` of every tracked `*.py` and `*.sh`, sorted, plus one digest over that list | re-verified after every leg |
| g | write protection (`chmod -R a-w`, or a read-only bind) | (f) detects a change; (g) prevents it |

`MNV_LAUNCHER_DIR` must be exported to `${MNV_CODE_ROOT}/nd-unfolding` in the submitting shell.
`$0`, `${BASH_SOURCE[0]}` and `SLURM_SUBMIT_DIR` are all unusable for this — `sbatch` runs a spool
copy. The launchers now **assert** that whichever directory the resolver picked is
`${MNV_CODE_ROOT}/nd-unfolding` and exit 2 if it is not.

### 0b-ii. EVERY `:NNN` LINE NUMBER IN THIS FILE THAT NAMES `sbatch_finalize_5d_bkgaware_gpu.sh` HAS MOVED

The two-root header and the member-library containment check add **39 lines above the body**, so
every reference below written against `8c156a37` is **+39** today. Measured file-by-file with
`grep -n` on the content, not computed from the offset:

| what it is | cited here as | now at |
|---|---|---|
| `STAT_COV` `mr_run` (`--expected-ids 1-100`) | `:167` | **`:206`** |
| `ML_COV` `mr_run` (`--expected-ids 1-24`) | `:168` | **`:207`** |
| `RESUME_ADOPT_LEGACY` refusal | `:188` | **`:227`** |
| `RESUME_FORCE` refusal | `:211` | **`:250`** |
| undeclared marker comparison | `:238` | **`:277`** |
| undeclared `exit 5` | `:253` | **`:292`** |
| `if mr_declared` opening the pause branch | `:256` | **`:295`** |
| `[fin-bkg] MEMBER PAUSE` | `:314` | **`:353`** |
| the two adopt calls (steps 4/5) | `:347`, `:352` | **`:386`, `:391`** |

**Anchor on the content, not on these numbers.** They moved once and will move again; the clause (c)
text inside the pause branch is unchanged and unreworded, per ruling 1.

## 1. The lift, and exactly what it did and did not change

The B1 steps 4–5 pause is **LIFTED** by Joseph's ruling 3, recorded at
[`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md).
All three expiry clauses are discharged: (a) and (b) at `3cb46337`, (c) at `81905bba` with Joseph's
ruling 1 that the `srun` execution of the launcher's exact steps 4–5 segment satisfies it.

**THE LAUNCHER'S CODE IS UNCHANGED AND THE PAUSE BRANCH IS STILL IN IT.** That is deliberate and it
is a decision, not an oversight:

- Ruling 1 says **do not reword the clause**, and the clause text lives inside the pause branch's
  comment block. Deleting the branch deletes the clause.
- The declared route **cannot reach the pause branch today** (it dies 89 lines earlier, at
  `sbatch_finalize_5d_bkgaware_gpu.sh:167`), so
  removing it buys nothing now.
- `nd-unfolding/` is on the publication critical path and the edit deserves its own review when a
  member is actually ready to run.

**So the lift is a POLICY state recorded in a decision document, and the code change implementing it
is a separate step that has NOT been taken.** Whoever takes it should quote the clause into the
decision record first — it is already quoted there — and should expect the byte-identity pin across
the eight launchers carrying the resolver block to be checked.

## 2. Control flow of `nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh`, at `c7f27ec0`

**Every bare `:NNN` in this document refers to that file** unless another path is named. Line numbers
in this launcher **have moved three times** and the file's own comments say so; these are current as
of `c7f27ec0`, and if they disagree with what you read, **anchor on content, not on the number**. A
reviewer reasonably read `:167` as a line in `combine_cov_nd.py` — which is 27 lines long — so the
file is now named at each citation rather than left to a definite description.

```
:162  if mr_declared; then
:167    mr_run "${STAT_COV}" python3 combine_cov_nd.py ... --expected-ids 1-100 ...
:168    mr_run "${ML_COV}"   python3 combine_cov_nd.py ... --expected-ids 1-24  ...
:169  else  (undeclared: reuse the archive's C_stat/C_ML)
:171  fi
:188  if RESUME_ADOPT_LEGACY=1        -> exit 5     FORBIDDEN in both regimes
:196  if mr_declared; then
:197    mr_skip_if_complete "${COMB}" -> reuse
:201    else mr_run "${COMB}" python3 analyze_universes_5d.py ...
:209  else  (undeclared)
:211    if RESUME_FORCE=1             -> exit 5
:238    marker bound to size+mtime AND matching -> reuse
:253    else                          -> exit 5
:256  if mr_declared; then
:330    exit 0                        <- THE PAUSE
:331  fi
:347  python3 mii_adopt_unified_5d_stamped.py ... uthrow.root            <- STEP 4/5
:352  python3 mii_adopt_unified_5d_stamped.py ... uthrow_cvcentered.root <- STEP 4/5
```

**Read `:256`–`:331` carefully, because it inverts the intuition.** The pause branch is entered when
`mr_declared` is TRUE. So **the adopt calls are on the UNDECLARED fall-through**, and the declared —
present-seed — route is the one that exits before them. That is why requiring a real `sbatch` of this
launcher would have made clause (c) circular, and it is what ruling 1 turns on.

`mr_declared()` is `[[ -n "${MNV_EST_SEED_OFFSET:-}" ]]` — `nd-unfolding/lib_member_resume.sh:230`.

## 3. Preflight measurements — the state of the world on 2026-08-22

### 3a. The executing tree

```bash
ssh saul.nersc.gov
# THE DATA ROOT, measured as a fact about the world -- NOT the tree anything executes from.
cd "${MNV_DATA_ROOT:?}" && git rev-parse HEAD && git status --porcelain | wc -l
# THE CODE ROOT, which is what the digests below must be taken from.
cd "${MNV_CODE_ROOT:?}" && git rev-parse HEAD && git status --porcelain | wc -l
```

Measured `b2d7d4ca`. **Do not gate on HEAD equality with `main`** — main has moved for
documentation-only commits since. Gate on the digests of the files that execute:

```bash
for f in nd-unfolding/mii_anchor_comparator.py \
         nd-unfolding/mii_root_payload_classes.py \
         nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh; do
  sha256sum "$f"
done
```

| file | sha256 (first 16) | matches `main` |
|---|---|---|
| `mii_anchor_comparator.py` | `3488894b19f266af` | yes |
| `mii_root_payload_classes.py` | `d363a3b28ee1701c` | yes |
| `sbatch_finalize_5d_bkgaware_gpu.sh` | `f7ce664511092712` | yes |

Compare against `git show <the declared sha>:<path> | shasum -a 256`. **The digest is the check; the
commit is not.**

**The `REPO=` hardcode this paragraph used to describe is GONE as of 2026-08-22** — see section 0b.
The launcher now refuses to start unless `MNV_CODE_ROOT` and `MNV_DATA_ROOT` are both set, and
sources and executes only from the code root. What has NOT changed is the reason the paragraph
existed: the canonical checkout carried **721** dirty entries at the last measurement, which is why
it may serve only as `MNV_DATA_ROOT`. Take these digests from `${MNV_CODE_ROOT}`, and re-measure the
dirty count on the data root at submission time — it is the most perishable number in this file.

### 3b. Member readiness — THIS IS THE BLOCKER

```bash
ls mii/member_k000000/boot_nd_5d/res_boot_*.npz      | wc -l   # need 100
# NOT `ls ... | wc -l` for this one: it prints 0 for an EMPTY directory and 0 for an
# ABSENT one, and here the directory is absent. Ask the two questions separately.
[ -d mii/member_k000000/seedscan_split_5d ] && echo PRESENT || echo ABSENT
ls mii/member_k000000/seedscan_split_5d/res_split_*.npz 2>/dev/null | wc -l   # need 24
ls mii/member_k000000/uq_5d/universe_sweep_bkgaware/5d_xsec_*_uni_full_*.root | wc -l
```

Measured, identically for **all three existing members** (`member_k000000`, `member_k001200`,
`member_k002400`):

| input | required | present |
|---|---|---|
| `boot_nd_5d/res_boot_*.npz` | 100 | **3** |
| `seedscan_split_5d/res_split_*.npz` | 24 | **0 — and the directory itself is ABSENT** |
| vertical sweep roots | ≥1 | **0** |
| the member's own CV | 1 | **absent** |
| `uq_5d/unified_throw_cov_5d.root` | 1 | **absent UNDER `mii/` — see the warning below** |
| `uq_cov_stat_5d.root`, `uq_cov_mlsplit_5d.root` | produced at `sbatch_finalize_5d_bkgaware_gpu.sh:167`/`:168` | absent |

**`--expected-ids` is an EXACT-POPULATION validator, not a minimum.** Verified in the code rather
than from the flag name: `replica_manifest.py:44-48` computes `got != expected_ids` and raises
`ValueError(f"replica id mismatch: missing=... extra=...")`. The launcher's own comment at `:163-165`
says this is deliberate — *"a member with a partial replica set must REFUSE rather than quietly
combine what it has."*

**EVERY ABSENCE IN THAT TABLE IS SCOPED TO `mii/member_kNNNNNN/`, AND ONE OF THEM MUST NOT BE READ
WIDER.** `unified_throw_cov_5d.root` is **not** missing from the repository — there are **23 copies on
pscratch**, including the main-line `nd-unfolding/uq_5d/unified_throw_cov_5d.root` that the adopted 5D
covariance depends on, plus `_fluxfix_20260806`, `_rescaledhalf`, and the clause (c) sandbox copies.
What is absent is a **member-local** copy. Unqualified, that row would read as "the publication
critical path's covariance is gone," which is false. Caught in review by the verifying lane; the first
draft of this table was unscoped.

**A COVERING SEARCH, because a null from my query was evidence about my query.** I named two ways I
could be wrong — a member tree outside `mii/`, and inputs staged on a filesystem I did not check — and
both are now closed by the verifying lane rather than by me. A full-depth `find` (no `maxdepth`,
unpiped, exit code and stderr counted separately) across **all four `josephrb` roots** —
`/pscratch/sd/j`, `/global/homes/j`, `/global/cfs/cdirs/gt`, `/global/cfs/cdirs/m3246` — returns
**exactly three `member_k*` directories, all under `mii/`**, with `find_exit=0` and `stderr_lines=0` on
every root. A separate search **by filename** rather than by directory finds 609 `res_boot_*.npz`
across nine locations: **five complete 100-replica sets exist and none of them is a member.** So the
population really is 3, and it is not hiding behind a naming convention either of us assumed.

**THE REFUSAL IS EXECUTED, NOT READ — and it has a positive control.** Run on the cluster under the
ROOT environment against the real member files, on bytes verified byte-identical to `main`
(`replica_manifest.py` `82fc5afe…`, `combine_cov_nd.py` `fc8514d8…`, matching `git show 01b88de9:`):

```
--expected-ids 1-100  ->  EXIT 1
    combine_cov_nd.py:18 -> replica_manifest.py:48
    ValueError: replica id mismatch: missing=[4, 5, ... 100] extra=[]

--expected-ids 1-3    ->  EXIT 0   (positive control, same files)
    [refusal_probe] 3 replicas, reported 10694 bins, sqrt-trace=1.674e-39 median rel=0.738%
```

**The control is what makes the first line mean anything**: it proves the refusal is about
**population**, not about the member `.npz` being malformed or unreadable. The ids present are exactly
`{1,2,3}`, so the failure signature below is the right one. Also measured rather than assumed: the id
key in those files is **`seed`**, not `replica_id`, and `xsec_flat` is 65856 long (10694 after the
`cv>0` mask).

**Provenance of the partial, stated without a motive attached:** all three replicas were written
**2026-08-18, 17:50–18:13**, and nothing has been written under `mii/` since except `member_k001200`'s
`uq_5d/` on 08-20. There are **no logs, `.out` or `.err` anywhere under `mii/`**. So this is a
four-day-stale partial rather than a completed three-replica pilot — but absence of a log is not proof
of intent, and nothing here should be read as one.

So a declared submission today dies at `sbatch_finalize_5d_bkgaware_gpu.sh:167` with

```
[member] producer FAILED (rc=1) for .../uq_cov_stat_5d.root -- no completion marker written
ValueError: replica id mismatch: missing=[...97 ids...] extra=[]
```

and `set -eo pipefail` (`:11`) kills the job there. **It never reaches the pause branch, let alone the
adopt calls.**

### 3c. The undeclared route

```bash
ls -la uq_5d/universe_stage2_5d_bkgaware/*.done
```

Measured: **no marker of any kind.** The undeclared branch requires a marker carrying **both** `size`
and `mtime`, both present and both matching (`:238`), and refuses otherwise at `:253` with exit 5.

**Do not set `RESUME_ADOPT_LEGACY=1` and do not set `RESUME_FORCE=1`.** Both are hard refusals (`:188`,
`:211`), and the first would adopt the 41.44 GB intermediate on a bare size check and write a marker —
`resume_guard.sh` names that branch the `BEN-023` defect. **Marker backfill is a separate ruling and is
not authorized.**

### 3d. The 41.44 GB intermediate

```
41,436,632,945 bytes   mtime 2026-07-14 13:59:17
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root
```

Unchanged, and never opened by the clause (c) verification. Beside it, from the same July run:

```
892,195,314 bytes  ..._uthrow.root             mtime 2026-07-14 14:02:04
892,241,032 bytes  ..._uthrow_cvcentered.root  mtime 2026-07-14 14:04:46
```

**Those two are the PRE-WRAPPER, UNSTAMPED adopted roots.** They carry no identity keys, so the
current gate fails closed on them. Do not mistake their existence for steps 4–5 having run.

### 3e. Disk

`myquota`: pscratch **15.99 / 20.00 TiB = 79.9%**, home 22.66 / 40 GiB. A member's own combined
intermediate is ~41 GB plus two ~892 MB adopted roots, so one member is comfortable and **a full
50-member scan is ~2.09 TiB, which would put pscratch over 90%.** Size the scan against the quota
before launching it, not after.

## 4. The disposition rule for the intermediate — and it is enforced by nothing

**DO NOT DELETE `uq_universe_5d_covariance_combined_bkgaware.root` until `MVFINAL_j` exists and
validates.** Joseph's ruling 4 states this; §11g of the governing spec states it; the launcher states
it at `:311-313` and `:324`.

**Verified 2026-08-22, and this is the part a reader should not assume:** `MVFINAL_j` appears in
**exactly two files** on `main`, and in neither of them is it code —
`sbatch_finalize_5d_bkgaware_gpu.sh` (three comment lines) and `tests/test_uq_remediation.py:3993-3998`
(a test asserting that comment's string is present). **There is no producer, no reader, and no
deleter.** `git grep 'MVFINAL' -- '*.py' '*.sh'` returns 5 lines across 2 files, all prose.

Two consequences, and they point in opposite directions:

1. **Nothing will delete the intermediate automatically.** The forge-then-delete chain is not live.
2. **The protection is procedural, not enforced.** Whoever implements either half of §11g ends that,
   and if a deleter lands before a producer it destroys 41.44 GB whose regeneration costs 2.087 TiB.
   `OI-133` records the ordering constraint: **land the identity binding before anything that removes
   bytes.**

## 5. When the launcher IS run: expected output at every gate

### 5a. Submission

```bash
ssh saul.nersc.gov
# BOTH ROOTS ARE MANDATORY AND NEITHER IS DEFAULTED. Set them in the SUBMITTING shell; sbatch
# propagates the environment, and the launcher refuses to start without them.
export MNV_CODE_ROOT=<the approved clean tree at the declared sha>   # section 0b-i
export MNV_DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold        # DATA ROLE ONLY
export MNV_GUARD_INVENTORY_DIR=<a run-scoped directory>              # one record per process
export MNV_SOURCE_MANIFEST=<the A-2(f) manifest, written BEFORE this> # see 0b-0
# Written once, before the first submission, from the code root itself:
#   python3 "${MNV_CODE_ROOT}/nd-unfolding/mnv_source_manifest.py" --repo "${MNV_CODE_ROOT}" \
#     --require-clean --write "${MNV_SOURCE_MANIFEST}"
export MNV_LAUNCHER_DIR="${MNV_CODE_ROOT}/nd-unfolding"   # sbatch runs a spool COPY; see 5b
export MNV_EST_SEED_OFFSET=0          # canonical integer, NO leading zeros
cd "${MNV_DATA_ROOT}/nd-unfolding"    # products land here; nothing is executed from here
sbatch "${MNV_CODE_ROOT}/nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh"
```

**Submit the launcher BY ABSOLUTE PATH UNDER THE CODE ROOT.** `sbatch <name>` from the data
directory would spool the data root's copy, and that copy is not the approved bytes.

Directives already in the file: `--account=m3246_g`, `--qos=shared --constraint=gpu --nodes=1
--ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00`, output to `uq_4d/fin5dBKG_%j.{out,err}`.
**90 minutes is inside the standing 12-hour approval; no further authorization is needed for the
walltime.**

`MNV_EST_SEED_OFFSET` must be `0` or a non-zero integer with **no leading zeros**
(`lib_member_resume.sh:63`). A padded value is octal to bash and decimal to Python and would seed the
estimator from one number, name the directory from a second, and stamp a third as provenance.

### 5b. Why `MNV_LAUNCHER_DIR`

`sbatch` copies the script to `/var/spool/slurmd/job<N>/slurm_script` and runs the **copy**, so
`BASH_SOURCE[0]` is the spool path and `lib_member_resume.sh` is not beside it. The resolver tries
`MNV_LAUNCHER_DIR`, then `dirname $BASH_SOURCE`, then `scontrol show job … Command=`. Setting it
explicitly is the deterministic option. **`SLURM_SUBMIT_DIR` is deliberately not a candidate** — it
would resolve to the canonical checkout's library instead of the deployed one, invisibly.

Failure signature if it cannot resolve: `[member] FAIL: cannot locate lib_member_resume.sh` and
**exit 2** within ~12 s.

### 5c. Expected stdout, in order

```
[fin-bkg] MEMBER mii/member_k000000: building this member's OWN C_stat and C_ML
[stat5d]  100 replicas, reported 10694 bins, sqrt-trace=... median rel=...%
[wrote]   .../uq_cov_stat_5d.root
[mlsplit5d] 24 replicas, ...
[wrote]   .../uq_cov_mlsplit_5d.root
[fin-bkg] analyze start <UTC> on <host>
...
[fin-bkg] adopt (mean-centered) <UTC>
[fin-bkg] adopt (CV-centered, F7) <UTC>
[fin-bkg] done <UTC>
```

**`100 replicas` and `24 replicas` are the numbers to read.** Anything else means the population check
did not do what you think.

If the pause branch is still in place, expect instead `[fin-bkg] MEMBER PAUSE (not a boundary)` and
**exit 0** — a clean exit that has produced no adopted roots. **A stage-1 NOT ATTEMPTED and a stage-1
awaiting paperwork read identically in a status table**; the launcher's own comment at `:308-310` says
so. Check for the two `.root` files, not the exit code.

### 5d. The stage-1 gate

Run **after** the job, in the ROOT environment (`source setup_salloc_env.sh` first — `import ROOT`
segfaults on a bare login shell):

```bash
cd "${MNV_DATA_ROOT:?}/nd-unfolding"          # the artifacts are here
PYTHONUNBUFFERED=1 python3 "${MNV_CODE_ROOT:?}/nd-unfolding/mii_anchor_comparator.py" \
  --artifact adopted_uthrow.root \
  --archive  <the archive product> \
  --member   <the member's adopted root> \
  --offset   0 \
  --archive-date 2026-07-14
GATE_RC=$?      # read UNPIPED, before anything else touches it
```

Exit map: **0 = PASS, 1 = INCOMPLETE, 2 = FAIL** (`mii_anchor_comparator.py:1112`). `--archive-date`
is the archive's mtime and is **required** — every `PREDATES_ARCHIVE` excuse is void without its
operand. `--rtol` defaults to `0.0`, which is bit-exact; **a tolerance is a decision, do not pass one
casually.**

Lines that must appear, from lane A's arm A1 which passed at production dimension:

```
[b2] VERDICT: PASS
[b2]   [coverage] hCov_combined5d_total_uthrow: compared 114361636 of 114361636 elements (100.0000%)
[b2]   [identity] OK   g1: upstream_estimator_seed_g1 = 42 = baseline 42 + declared offset 0
[b2]   [identity] OK   g2: upstream_estimator_seed_g2 = 1000 = baseline 1000 + declared offset 0
[b2]   [config] OK   upstream_n_throws = 160 == predeclared ensemble size
[b2]   [recompute] OK   sqrt_tr_new: recomputed ... == stamped ...
[b2]   [recompute] OK   sqrt_tr_old: recomputed ... == stamped ...
```

`114361636 = 10694²`. The diagonals must read **10694**, not 10695 — that is the OI-147 hole closed at
`b2d7d4ca`, and an over-length pair now produces `OVER-LENGTH` and **exit 2** where it previously
passed.

Two counts worth grepping, because they are the OI-147 measurement and they are falsifiable from the
log rather than from prose:

```bash
grep -c "EXCUSED BY THE ARCHIVE'S AGE AND NOT VERIFIED BY ANYTHING" gate.log   # expect 0
grep -c "PARTIAL COMPARISON" gate.log                                          # expect 0
```

Before the OI-147 fix every arm measured **eight** excused-but-unverified keys. Zero is the target and
`0` was achieved against the real archive.

## 6. Abort conditions

Stop and report rather than working around, in every one of these:

| signal | meaning | do |
|---|---|---|
| **exit 5** | a resume refusal at `:188`, `:211` or `:253` | **stop.** Do not set `RESUME_ADOPT_LEGACY` or `RESUME_FORCE`. Marker backfill is unauthorized. |
| **exit 3** | wrong-member marker — a product from another `k` | **stop.** Reserved for exactly this; do not conflate with 5. |
| **exit 2 from the launcher** | resolver failed, or a malformed `MNV_EST_SEED_OFFSET` | fix the variable or set `MNV_LAUNCHER_DIR`; do not pad the offset |
| **`replica id mismatch`** | the population is short | **stop.** This is section 3b. Do not relax `--expected-ids`. |
| **exit 0 with no `.root` files** | the pause branch is still live | expected today; not an error |
| **gate exit 1 (INCOMPLETE)** | the gate could not decide | **do not pass `--acknowledge-unrecomputable` to make it green.** The flag takes an exact key list and is for a declared closed set. |
| **gate exit 2 with `OVER-LENGTH`** | a diagonal is not 10694 | **stop.** The artifact was altered after the wrapper finished; extra zero bins leave the trace and the clip check bit-identical, so nothing else in the gate can see it. |
| **any refusal naming the 41.44 GB intermediate as corrupt** | the `D1` false-corruption shape | **stop and do not touch that file.** It has been a false report before. |
| **pscratch above ~90%** | see 3e | stop and resize |

## 6b. Two measured claims in this document that EXPIRE, and what to do instead of inheriting them

Handed forward by the clause (c) reachability lane on close-out, and recorded here rather than in a
message because **this is where the question gets asked** — a lane about to submit is reading section
6, not a peer's transcript.

**Every measurement in sections 3 and 6 is an INVENTORY CLAIM, which is the most perishable kind this
campaign produces.** An inventory claim is falsified by exactly the work it is meant to authorize, so
the moment it becomes useful is the moment it may already be wrong. Two specific ones:

1. **"The archive legs carry no `estimator_seed`."** True as measured on 2026-08-22 against those two
   exact paths — the g2 throw leg (9 keys, only `n_throws` as `TParameter<int>`) and the 41.44 GB g1
   intermediate (47 keys, zero `TParameter<int>`). **Any authorized re-production of either leg
   falsifies it.** If a later lane cites it to justify skipping an identity check, that is the reading
   it will not survive: **re-measure the keys, do not inherit the row.**
2. **"No member is runnable."** Measured 2026-08-22 and confirmed by a second lane with an executed
   refusal. It becomes false the instant member production starts, which is the first thing anyone
   acting on this runbook would do. **AND IT IS TWO INDEPENDENT REFUSALS, NOT ONE — fixing the first
   does not clear the second:**

   | call | validator | found |
   |---|---|---|
   | `:167` `STAT_COV` | `--expected-ids 1-100` over `<member>/boot_nd_5d/res_boot_*.npz` | **3** of 100 |
   | `:168` `ML_COV` | `--expected-ids 1-24` over `<member>/seedscan_split_5d/res_split_*.npz` | **0** of 24, and `seedscan_split_5d/` is **absent entirely** |

   Verified across all three members 2026-08-22: the only subdirectory under each is `boot_nd_5d`
   (plus a `uq_5d/` under `member_k001200`). **Re-measure BOTH. A member is runnable only when both
   pass.** A lane that reads "3 of 100", produces the hundred replicas and resubmits will clear `:167`
   and die at `:168` on a directory that does not exist — and will read that as a regression, because
   the runbook told it what was missing and it fixed exactly that.

   **This is the failure §6b exists to prevent, one level up, and it was in this document until
   2026-08-22:** a stated blocker that is one of two reads as sufficient. Same family as the
   one-directional coverage guard that let an over-length array through — **satisfying the named
   condition implies nothing about the unnamed one.** Caught by the reachability lane reading the
   section I had just written about perishable claims.

**The general form, and the reason this section exists at all:** the clause (c) reachability finding
went from open question to confirmatory in **eight minutes** when Joseph ruled. **A measurement can go
stale faster than the document describing it.** Treat every number in sections 3 and 6 as carrying its
date, and re-run the command beside it rather than quoting the result.

## 7. So what IS the first submission?

Not this launcher. On the measurements in section 3, the ordered prerequisites are:

1. **Decide the target.** Either (a) the M(ii) member scan, which needs member inputs built from
   scratch, or (b) a stamped re-adoption of the archive products, which needs a marker-backfill ruling
   that does not exist. **These are different pieces of work and only Joseph can pick.**
2. **If (a):** produce, per member, 100 bootstrap replicas, 24 seedscan splits, the vertical sweep and
   its CV, and `unified_throw_cov_5d.root`. Only then does `sbatch_finalize_5d_bkgaware_gpu.sh` have
   anything to consume. Size against 3e first.
3. **If (b):** the marker-backfill ruling comes first, and it should be its own decision record,
   because the guard refusing it was written deliberately and names a specific defect.
4. **Either way, the launcher's pause branch is removed as its own reviewed change** — see section 1.

**This runbook does not choose between them and no lane should.**
