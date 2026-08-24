# DECLARATION — the repaired k=0 candidate sha, and A-2(a)–(g) filed against it

**CITABLE FOR:** the constitution of the execution tree at `aa67c426`, measured 2026-08-23.

**NOT CITABLE FOR:** a Gate-1 pass. **Gate 1 does NOT pass at this sha and has not been graded here.**

**SUPERSEDES** [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md),
which declared `a54038b2`. That declaration was **true when made and remains historically valid**;
it is superseded because the tree it declared cannot execute legs 5a/5b.

---

## 1. THE DECLARED SHA

```
sha     = aa67c426afaa9b6ca91c9996637a6bade950da9a
branch  = build-k0-execution-integrity
tree    = /pscratch/sd/j/josephrb/k0r2/clean
```

**Why this branch and not `main`.** `main` does not carry the Gate-1 apparatus — no
`lib_mnv_env_preflight.sh`, no `lib_mnv_env_pathcheck.sh`, no parity gate in any launcher. The
repair was authored on `main` and **cherry-picked here**, because deploying `main` would have
deployed a tree without the thing round 9 graded.

**This document does not name its own commit**, by the same convention as its predecessor and
`DECLARATION-20260822`: a declaration is paperwork *about* an execution tree and lives where the
paperwork lives.

> **⚠ THIS SENTENCE WAS FALSE FOR ~21 HOURS AND IS NOW TRUE AGAIN. Read the correction before
> citing it.** As written it says *"the deployment is at the declared sha, so A-2(a) holds
> exactly."* It was true when written. It became false the moment the commit carrying this very
> file — `9db42a6d`, docs-only — was **deployed on top of the candidate**, which is what the
> builder (me) then did. Round 10 graded the tree in that state and returned **DOES NOT PASS,
> 13 PASS / 5 FAIL**, `F-1(a)`: declared `aa67c426`, deployed `9db42a6d`. The falsifier printed
> immediately below this paragraph is the command that catches it, and it was in the file the
> whole time. **Restored 2026-08-24T11:36:43Z** — see §6. Do not read this paragraph without §6.

**The deployment is at the declared sha**, so A-2(a) holds exactly. Falsifier:

```bash
git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD     # must be aa67c426…
```

## 2. A-2(a)–(g), EACH MEASURED SEPARATELY

| # | requirement | result | evidence |
|---|---|---|---|
| **a** | `rev-parse HEAD` equals the declared sha | **MET** | `aa67c426afaa9b6ca91c9996637a6bade950da9a` |
| **b** | `git status --porcelain` emits zero lines | **MET** | `0` |
| **c** | a checkout by the guard's own definition | **MET** | `--require-checkout` **rc=0** |
| **d** | no nested checkout beneath it | **MET** | `--require-no-nested-checkout` **rc=0** |
| **e** | not nested inside another checkout | **MET** | `--require-not-nested` **rc=0** |
| **f** | full source manifest over tracked `*.py`/`*.sh` | **MET** | **782** files, listing sha256 `fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420` |
| **g** | write protection applied | **MET** | `--require-readonly` **rc=0**, and independently `find … -type f -writable \| wc -l` → **0** |

**Every rc taken with `--write` or `--compare`.** Run bare, `mnv_source_manifest.py` returns **rc=2,
"COULD NOT LOOK"**, which is never "clean".

**A-2(f) as a gate:** `--compare` **rc=0**, `SOURCE MANIFEST IDENTICAL (782 files, fa3489e2…)`.

Manifest at `/pscratch/sd/j/josephrb/k0r2/declarations/aa67c426/source-manifest.json`, file sha256
`622ddc0ada33234d5b420130cd6e60e17ead8b2669b6e77436f0f57a89e2a405`, made read-only.

## 3. WHY 782, AND THE EXPIRY CLAUSE

`a54038b2` → 780; `aa67c426` → **782**. The two additions are
`nd-unfolding/tests/test_k0_5ab_separated_roots.py` and
`nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py`. **`compare_unified_throw.py` was modified,
not added, and a modification is count-neutral** — stated because the last declaration's provenance
gloss counted renames as adds and had to be corrected.

**Falsified by any add or removal of a tracked `*.py` or `*.sh`, and by nothing else.** Re-run before
the first `sbatch` and again after the last leg. **Do not inherit these numbers.**

## 4. WHAT THIS DOES NOT DO

- It does **not** pass Gate 1, and **round 9's PASS does not transfer to this sha** — see the packet.
- It authorizes **no** Slurm submission. None was made.
- The 415 products of the failed run at `a54038b2` are quarantined and are **not** reusable
  components of any accepted member — receipt `dfef7871`.


---

## 6. THE DEPLOYMENT EXCURSION, AND ITS RESTORATION — added 2026-08-24

**CITABLE FOR:** the state of `/pscratch/sd/j/josephrb/k0r2/clean` from 2026-08-24T11:36:43Z onward,
and for the fact that it was at the wrong sha before that.

**NOT CITABLE FOR:** a Gate-1 pass. Gate 1 has **not** been graded at the restored state. This
section closes `F-1(a)`'s cause; whether it closes the clause is the grader's call, not mine.

### 6.1 What went wrong, stated as a mechanism and not as an oversight

The convention this document uses — a declaration is paperwork *about* a tree and does not name its
own commit — is not optional. **No commit can contain its own sha**; that is a fixed point over
sha256, not a stylistic choice. The convention's other half is the load-bearing one, and its
predecessor `DECLARATION-20260823-k0-candidate-sha.md` states it outright: *"Consequently this commit
does NOT move the deployment."* That arrangement is what round 9 graded **18 PASS / 0 FAIL**.

I broke the second half. The deployed tree was **on the branch** `build-k0-execution-integrity`, so
it could be fast-forwarded, and it was — to `9db42a6d`, the commit that added this file. The failure
did not need a wrong belief, only a branch ref and a routine update. **A convention enforced by prose
and defended by a tree that can fast-forward is not enforced.**

### 6.2 The restoration, with every pre- and postcondition

Preconditions checked and required before touching anything: `HEAD == 9db42a6d` exactly, target
object present in the local store, `git status --porcelain` **0 lines** (counted with `wc -l` on a
file, never `$?` after a pipe), and **no Slurm jobs of mine other than the long-held cron
`57275989`**. The script refuses with a distinct exit code on each.

| step | action |
|---|---|
| 1 | `chmod -R u+w` over the tree — A-2(g) deliberately suspended, 1584 files writable |
| 2 | `git -c advice.detachedHead=false checkout aa67c426` — **detach**, see §6.3 |
| 3 | re-lock: `find … -path ./.git -prune -o -print0 \| xargs -0 chmod a-w` |
| 4 | re-apply with the tool that owns the rule: `--apply-readonly --require-readonly` |

Step 4 is not redundant. `mnv_source_manifest.py` says of hand recipes that *"a recipe a reader
retypes is a second implementation of the rule"*, and records that the recipe it used to print was
itself wrong. Its verdict on my hand-applied state: **`0 of 931 protected path(s) changed mode, plus
0 non-tracked writable file(s)`** — the hand lock was exactly what the tool would have applied, and
now the protection is tool-attested rather than argued.

Mode round-trip was faithful because `a-w` removes write bits without touching execute bits:
`files550=161` and `dirs550=150` before and after, **120 executable `.sh` before and after**. Files
at mode 440 went 1423 → 1421, which is the three `.md`/`.tsv` paths the checkout removed.

### 6.3 A deliberate deviation: the deployed HEAD is now DETACHED

The graded round-8/9 state had HEAD **on a branch** whose ref simply lagged `origin`. I did not
restore that, and the difference is the point: **a detached HEAD cannot be fast-forwarded**, so the
mechanism of §6.1 is unavailable rather than merely discouraged. `refs/heads/build-k0-execution-integrity`
is left **unmoved at `9db42a6d`**, still equal to `origin`, so nothing was rewound.

Measured before relying on it: **no file on the run path reads a branch name** — `git grep -E
'abbrev-ref|show-current|symbolic-ref'` over `nd-unfolding`, `lib` and `*.sh` at `aa67c426` returns
**0 matches**. The only repo-wide hit is a 2026-08-10 verifier transcript.

### 6.4 A-2(a)–(g) RE-MEASURED at the restored deployment

Interpreter **named, not assumed**: `/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`,
**3.11.14**. The login `/usr/bin/python3` is **3.6.15** and cannot run these tools at all — it exits
**1** with a `SyntaxError` on `from __future__ import annotations`, which is neither the documented
`rc=2` nor a clause result. Round 10 flagged that this declaration named no interpreter. It does now.

| # | requirement | result | evidence |
|---|---|---|---|
| **a** | `rev-parse HEAD` equals the declared sha | **MET** | `aa67c426afaa9b6ca91c9996637a6bade950da9a` |
| **b** | `git status --porcelain` emits zero lines | **MET** | `rc=0`, `lines=0`, counted on a file |
| **c** | a checkout by the guard's own definition | **MET** | `--require-checkout` **rc=0** |
| **d** | no nested checkout beneath it | **MET** | `--require-no-nested-checkout` **rc=0** |
| **e** | not nested inside another checkout | **MET** | `--require-not-nested` **rc=0** |
| **f** | full source manifest over tracked `*.py`/`*.sh` | **MET** | `--compare` **rc=0**, `SOURCE MANIFEST IDENTICAL (782 files, fa3489e2…)`, `HEAD aa67c426…, dirty 0` |
| **g** | write protection applied | **MET** | `--require-readonly` **rc=0**, plus a scoped filesystem walk, plus a firing control |

**THE INSTRUMENT IS NAMED THIS TIME, BECAUSE I MIS-READ MY OWN TABLE.** The `--require-*` flags live
in **`nd-unfolding/mnv_source_manifest.py`**, not in `mnv_guarded_run.py`. My first re-measurement
pass sent all four to `mnv_guarded_run.py`, which requires `--expect-root` and therefore **exited 2
from argparse before measuring anything**. Four clauses appeared to fail and none had been tested.
That is the trap this document already warns about in the opposite direction: **rc=2 is "could not
look", so it is not a pass — and equally, it is not a fail.** An evidence cell that gives a flag but
not the file it belongs to invites exactly this, so the flags above are now attributed.

**Every rc was taken with `--compare`.** Run bare, the tool answers
`COULD NOT LOOK: give --write and/or --compare; measuring nothing and exiting 0 is exactly the shape
this file exists to prevent` at **rc=2** — re-confirmed here as a live control, not quoted from
history. Each clause was measured in a **separate invocation** so that one rc means one clause.

**A-2(f) numbers are unchanged from the original filing**, as they must be: `aa67c426..9db42a6d`
touches **6 files, all under `docs/orchestration/`, 0 `.py`, 0 `.sh`** (measured in the deployed tree
itself), and A-2(f) covers only those two suffixes. Filed manifest file sha256 re-hashed on disk:
`622ddc0ada33234d5b420130cd6e60e17ead8b2669b6e77436f0f57a89e2a405`, matching this document's §2.

### 6.5 (g) HAS A CONTROL THAT FIRES, AND ONE THAT STAYS SILENT

A protection clause that has only ever been observed passing is decoration. Both arms, run on the
live tree:

- **fires on bad:** `chmod u+w nd-unfolding/compare_unified_throw.py` (440 → 640) →
  `--require-readonly` **rc=2**, `REFUSING: A-2(g): 1 tracked source path(s) still carry a write
  bit, e.g. ['nd-unfolding/compare_unified_throw.py']`. One bit on one file is enough.
- **silent on good:** `chmod a-w` restores 440 → **rc=0**, and the tree returns to
  porcelain 0, HEAD `aa67c426`, 0 writable outside `.git`.

### 6.6 A DEVIATION I INTRODUCED AND CANNOT UNDO

`.git` now holds **1939** writable files where the graded tree held **30**. My unlock in step 1 was
tree-wide and the re-lock scoped `.git` out, so user-write persists on objects the original lock had
left read-only. **I cannot restore the original state exactly, because I never recorded which 30 files
they were** — the count was measured, the membership was not.

Why this is disclosed rather than repaired: A-2(g) is contracted over **the source** (*"`chmod -R
a-w` over the source, or a read-only bind"*), `.git` is not source, and the clause's own instrument
returns **rc=0**. The scoped walk — the scoping round 10 asked for — gives **0** writable files and
**0** writable directories outside `.git`. Unscoped it gives **1939**, and **every one of them is
inside `.git`** (`grep -vc '^./.git/'` → 0). Both numbers are printed here precisely because the
unscoped one is the misleading one and was already misread once, at **30**.

### 6.7 WHAT THIS SECTION DOES NOT DO

- It does **not** pass Gate 1 and does not assert `F-1(a)` is closed.
- It authorizes **no** Slurm submission. The seven-job k=0 rerun remains gated on an independent
  regrade at this restored state.
- It does not touch an executable byte. The source manifest is bit-identical to the original filing.
- It does **not** put the missing mechanical check in place. The declared-vs-deployed comparison still
  exists only as prose, and prose has now failed twice — round 8 and round 10. A deploy step that
  refuses when the sha it is about to check out is not the sha the declaration names cannot be added
  to this branch above `aa67c426`, because a new tracked `.py`/`.sh` would falsify A-2(f) and the
  docs-only invariant this whole arrangement rests on. **It therefore belongs after this candidate
  retires, and it is being tracked rather than quietly dropped.**
