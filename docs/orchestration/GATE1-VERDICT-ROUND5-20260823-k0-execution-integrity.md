# GATE-1 VERDICT (ROUND 5) 2026-08-23 — pre-submission readiness for the k=0 M(ii) member

**GATE 1 DOES NOT PASS.**

Stated in the words §7.0.6 requires: **Gate 1 DOES NOT PASS.** Fifteen of the eighteen
pre-submission halves pass; **three fail** — `F-2(a)`, `F-14` and `F-17(a)`. No criterion is
recorded NOT-EVALUABLE. Under §F's no-partial-credit rule as scoped by §7.0.6, any single miss at a
gate is a FAIL of that gate.

**What this blocks.** The seven jobs of logical legs 1–5 for k=0 are **not** authorized for
submission. Gate 2 is not graded and legitimately cannot be.

**The decisive finding, in one sentence.** The round-5 repair genuinely fixes the round-4 boundary
for **seven** of the eight launchers, but `sbatch_unfold_5d_detector_bkgaware_gpu.sh` invokes both
preflight integrity tools at `:139`/`:148` while sourcing its activator only at `:227` — and both
tools are a `SyntaxError` under the un-activated interpreter — so that launcher aborts at exit 3,
before any guard and any science invocation, with a message that misattributes the cause. Measured
by execution on `saul`, with a same-interpreter control on a sibling launcher that exits 0.

---

## 0. Eligibility, the objects graded, and hygiene

**Eligibility (F-18, §7.0.10, ruling 23).** I am a fresh third party. **I did not build this
repair**: I authored no part of `f3c27870` or any predecessor `PR-01`…`PR-06`, no code in this
repository, and no part of the k=0 plan. **I am not the round-4 verifier**: I did not write
`GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md` or any earlier verdict. **I did not author
the review contract or its §7.0 split**, nor §7.0.11–§7.0.16. I read the round-4 verdict, the
builder's confirmation and the round-5 packet as *claims to be checked*, and inherited no PASS from
round 4; every criterion below was re-graded at `f3c27870` from first-hand measurement. I did not
treat the packet's "all green" statements as evidence — two of them are contradicted below.

| object | value |
|---|---|
| **RUBRIC** | `main` @ `a8f79c9aebb594ded88c2986a5a98735ff18a29c`, `docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md`, **1160 lines** (carries §7.0 and rulings 20–22) |
| **CODE** | `origin/build-k0-execution-integrity` @ `f3c27870aa775b8a4ceb77a2e081169e80e76e5d` (branch head is exactly this sha) |
| **DEPLOYED** | `/pscratch/sd/j/josephrb/k0r2/clean` @ `f3c27870…`, `git status --porcelain` = **0** lines |
| **ENV ROOT** | `/pscratch/sd/j/josephrb/k0env` (real directory; `readlink -f` = itself) |
| **CONDA PREFIX** | `/global/homes/j/josephrb/.conda/envs/root_6_28` (Python 3.11.14, ROOT 6.28/12) |
| **env-manifest digest** | `499e923aaabfcf310e0abdc4a5bdd877cf58d3a9c52bd41d76fa0a05eb131392` — **REPRODUCED**, locally and on the deployed root |
| **source listing** | **778** tracked source files, `70fb59d4ce5b6ebbc005dcefa716c44d3c7cda8f6779118fdf094bebbdfba922` — **REPRODUCED** |
| **hosts** | local `Josephs-MacBook-Pro-9.local` (bash 3.2 / zsh); cluster `saul.nersc.gov` → `login34` (bash **4.4.23**) |
| **window (UTC)** | start `2026-08-23T03:39:58Z`, end `2026-08-23T04:10:00Z` |

### Required first verifications — all four hold

```
$ git rev-parse HEAD                                   # primary checkout
a8f79c9aebb594ded88c2986a5a98735ff18a29c
$ git rev-parse origin/build-k0-execution-integrity
f3c27870aa775b8a4ceb77a2e081169e80e76e5d               # branch head == the repair sha
$ ssh saul 'cd /pscratch/sd/j/josephrb/k0r2/clean && git rev-parse HEAD; git status --porcelain | wc -l'
f3c27870aa775b8a4ceb77a2e081169e80e76e5d
0
$ python3 docs/orchestration/generate_live_state.py --check-freshness ; echo $?
FRESH :: Git: 141cac09 is HEAD's parent (a8f79c9a) -- the normal born-stale-by-one state
0
$ shasum -a 256 nd-unfolding/mnv_env_manifest.tsv
499e923aaabfcf310e0abdc4a5bdd877cf58d3a9c52bd41d76fa0a05eb131392
$ ssh saul '<conda py> mnv_source_manifest.py --repo $C --write /tmp/…'
[srcman] …: 778 tracked source files, listing sha256 70fb59d4ce5b…dbba922, HEAD f3c27870…, dirty 0
```

**Hygiene BEFORE.** Primary checkout `a8f79c9a`; `git status --porcelain` showed exactly two
untracked files, `PROJECT_STATE_PILOT_PROPOSAL.tmp.md` and `log_test.txt`. I did not touch either.

**Hygiene AFTER.** Primary checkout still `a8f79c9a`; porcelain still exactly those two untracked
files and nothing else. All work was done read-only in **two isolated detached worktrees** outside
`.claude/worktrees/` (`scratchpad/g5-code` @ `f3c27870`, `scratchpad/g5-main` @ `a8f79c9a`), both
`porcelain = 0` when removed, and both removed. Deployed code root porcelain **0** at the end;
canonical checkout porcelain **721**, unchanged. Cluster writes confined to `/tmp` (all temp dirs
removed). Deployed root unchanged: `nd-unfolding/_t_direct.sh` does not exist.

**Shell notes, because two of them changed a number.** My tool shell is **zsh**, which does not
word-split unquoted variables: my first multi-file `shasum` passed eight filenames as one argument
("File name too long") and my first `grep --include=*.py` was eaten by zsh globbing. Every
multi-file command below therefore runs under `bash -c`. I also read `$?` after a `| tail` once and
re-ran the suite unpiped; both figures agreed, but only the second is evidence. `TMPDIR` explicit on
every suite.

---

## 1. The Gate-1 column, criterion by criterion

| # | verdict | first-hand basis |
|---|---|---|
| F-1(a) | PASS | A-2(a)–(g) each measured separately on the deployed root, all rc=0; 778 files / `70fb59d4…` reproduces the declaration; (d)(e)(g) exercised as **refusals**, incl. the attempted-write arm round 4 was owed; both preflight tools IN the manifest |
| F-2(a) | **FAIL** | `unfold_detector` runs both preflight tools **before** its activator; both are a `SyntaxError` on the pre-conda interpreter → **exit 3 before any guard or science**, reproduced by execution with a passing sibling control (§2) |
| F-3(a) | PASS | non-comment `--allow` = **0** in all eight launchers; `build_child_argv` emits none (`test_no_allow_is_ever_emitted`) |
| F-4(a) | PASS (flagged) | bench denominator **14** science invocations + the pinned-writer child, > 0, reproduced three independent ways |
| F-5(a) | PASS | generator + comparator exist; `test_source_manifest_constitution` **28** and `test_p4_ratchet_fail_closed` **30** green, incl. fires-on-mismatch **and** silent-on-match |
| F-6(a) | PASS | code root's `build_child_argv` emits `[py, guard, --expect-root, --inventory, --, writer, …]`, fail-closed twice (`:333`, `:337`); `repo_origin_count` written unconditionally; both directions pinned |
| F-7(a) | PASS | identity-not-floor comparator, undeclared pin fails closed, 30 arms; §7.0.13 exclusion pinned, 13 census arms green; census `14+16+0=30` rc=0 |
| F-8(a) | PASS (flagged) | P-6 re-run by me at `f3c27870`, output reproduces the filed table **exactly** (8 entrypoints / 14 invocations); P-5's fifth blind spot published (packet §5) and it does name all three channels; subprocess enumeration = 1 child, **WRAPPED** |
| F-9 | PASS | **re-run first-hand** (round 4 did not): all six rows of §7.0.11 discharged, incl. `guard_installed=false` + `checked=0` + `outcome=refused:script-outside-expect-root` + `refusal_site=b4-script-containment` |
| F-10 | PASS | `test_n2_child_boundary.py`, **7** arms rc=0: unguarded hijack real, guarded exits 3, refusal precedes output, real `build_child_argv` argv, no `--allow`, pinned writer neither copied nor executed |
| F-11 | PASS | `test_n3_rooted_import_repair.py`, **8** arms rc=0, both directions + power + silence; all six B-1 prologues verified `__file__`-derived with **no absolute fallback** |
| F-12 | PASS | N-1's three restated clauses discharged first-hand (§3.4); N-2/N-3 `__file__` anchors green |
| F-13 | PASS | `test_a_script_in_another_checkout_is_refused_3` **and** `test_the_SAME_script_inside_expect_root_is_NOT_refused`, plus the `--allow`-cannot-launder and outside-every-checkout arms |
| F-14 | **FAIL** | `generate_manifest.py --check` exits **1** at the graded sha in a clean worktree (packet §6 claims rc 0); and the `SubstitutionFenceS1` remainder ratchet is **201 ≠ 199**, broken by this commit's own two new `.sh` files, in a file this same commit edited (§3.2) |
| F-15 | PASS | `TMPDIR=/private/tmp python3 -m unittest test_mnv_guarded_run test_oi136_failopen_inventory_ratchet` → **`Ran 57 tests … OK`, rc=0**, status read unpiped; counts as measured at the graded sha: **50 and 7** |
| F-16 | PASS | `verify_hash_bindings.py` → **rc=0, `ALL BINDINGS INTACT`**, run **after** all other observations |
| F-17(a) | **FAIL** | M-5's re-measurement again reports the quantities that were repaired and reads as though the `.sh` route is fit; the fifth quantity — that one launcher cannot execute its preflight — is unreported. Plus M-1 omits `unified_throw_cov.py` and states three remaining literals where there are **four** (§3.3) |
| F-18(a) | PASS | this document, clause by clause, by an eligible fresh third party |

**TALLY: 15 PASS / 3 FAIL / 0 NOT-EVALUABLE.**

**A grading discipline I applied on purpose, stated so it is not read as softening.** The §2 defect
would also let me fail `F-1(a)` (A-2 green on a tree one launcher cannot run its preflight from),
`F-4(a)` (that launcher's realized guarded count is 0, not 2) and `F-8(a)` (P-5 does not name it). I
graded each of those **as written** and PASS, with the flag recorded in its row, and carried the
defect once at `F-2(a)`. I did **not** extend that courtesy to `F-17(a)`, and the reason is
principled rather than convenient: `F-17(a)`'s M-5 has the fitness of the `.sh` route **as its own
subject matter**, so an unreported defect in that route is a failure of M-5 itself, not a
consequence of another criterion's failure. A grader who carried it once would report **16/2**; the
choice is mine and is recorded here so it can be attacked.

---

## 2. THE DECISIVE FINDING — one launcher of eight cannot execute its own preflight

### 2.1 What the repair got right, measured before I looked for anything wrong

The round-4 boundary is genuinely repaired, and most of it is good work.

**The closure, enumerated independently rather than read off the manifest.** I parsed `source`/`.`
lines hop by hop from the activator's own bytes:

```
HOP1 (activator):   :18 unbinned_unfolding/build/setup.sh      :21 MINERvA101/opt/bin/setup.sh
HOP2 (via hop-1):   :5 setup_MAT.sh  :6 setup_MAT-MINERvA.sh  :7 setup_UnfoldUtils.sh
HOP3:               (none) -- HOP 3 IS EMPTY, measured on all three hop-2 files
conda limb:         8 *.sh in etc/conda/activate.d
TOTAL = 1 + 2 + 3 + 8 = 14        == the manifest's 14, independently derived
```

**The `8` is right and round 4's `12` was not.** `activate.d` holds **12** entries but only **8**
`*.sh`; the other four are `.csh`/`.fish`, which bash conda does not glob. Round 4's "12
`activate.d` scripts" counted files, not executed files.

**The manifest binds the real deployed bytes.** All 14 digests recomputed against the live files:
`MEMBERS_CHECKED=14 MISMATCH=0`.

**Zero canonical-checkout references in all six named closure members** (activator + 2 hop-1 + 3
hop-2): `TOTAL_CANONICAL_REFS=0`. `unbinned_unfolding/build/setup.sh` is genuinely regenerated
self-locating; the four latent `${VAR:-<canonical>}` defaults are now `${MINERVA_PREFIX:?…}`.

**Three roots, distinct, with the separation checked on the canonical target.** `MNV_ENV_ROOT` and
`MNV_CONDA_PREFIX` are `:?` mandatory in **8 of 8** launchers with **0** defaulted forms. The env
root is a real directory outside every checkout — it carries no `VALIDATION_LEDGER.md`, and the four
`.git` directories under it belong to `UnfoldUtils`/`GENIEXSecExtract`/`MAT`/`MAT-MINERvA`, which are
not MINERvA-OmniFold checkouts by the guard's own two-marker definition.

**The packet §3 positive control reproduces exactly, on the shipped bytes**, and I confirmed all four
sub-claims first-hand — preflight verifies 14 members *before* the source (`:85` vs `:87`), the
**actual** activator returns, `[env-pathcheck] OK` is reached after it (`:94`), and the preamble exits
0:

```
[env-preflight] OK: 14 closure member(s) verified against mnv_env_manifest.tsv; env root /pscratch/sd/j/josephrb/k0env
[env-pathcheck] OK: 45 search-path entr(ies) checked; none inside a checkout, none outside the declared environment
EXIT=0
```

**The activator really activates** (not a no-op that merely returns): `CONDA_PREFIX=…/root_6_28`,
`python3 → …/root_6_28/bin/python3`, **3.11.14**, `import ROOT → 6.28/12`, `MINERVA_PREFIX` under the
env root. **All three channels independently inspected after activation**: PATH 30 entries,
PYTHONPATH 4, LD_LIBRARY_PATH 11 — **45 total, reconciling the pathcheck's own count** — with **0**
canonical-checkout entries and **0** entries resolving inside any checkout by my own upward walk.

**Every refusal arm fires, and each is silent in the opposite direction.** Run against the shipped
`mnv_env_preflight.sh`, entirely from `/tmp`, with no mutation of the env root or the conda env:

| arm | result |
|---|---|
| positive (real env root) | `OK: 14 …` rc=**0** |
| faithful copy of the env tree | `OK: 14 …` rc=**0** (silent on good) |
| MISSING member | `VIOLATION: MISSING closure member (hop2)` rc=**3** |
| DIGEST MISMATCH (one byte) | `VIOLATION: DIGEST MISMATCH (hop2)` + want/got rc=**3** |
| EXTRA `activate.d` script | `VIOLATION: EXTRA unbound activate.d script — conda GLOBS this directory` rc=**3** |
| same fake prefix, extra removed | `OK: 14 …` rc=**0** (the opposite direction) |
| UNREADABLE member (`chmod 000`) | rc=**2**, refuses (message inaccurate — see §5) |
| env root INSIDE a checkout | `VIOLATION: … resolves inside a repository checkout` rc=**3** |
| env root == canonical data root | `VIOLATION: … INSIDE another declared root` rc=**3** |
| unreadable / empty manifest | rc=**2** both, `COULD NOT LOOK` |
| **directory symlink onto a checkout** | `VIOLATION: … resolves inside a repository checkout` rc=**3** |

That last arm answers the question directly: a symlinked *view* back into a checkout is refused,
because separation is checked on the `cd -P`/`pwd -P` target.

**Each pathcheck channel's mutation arm fires**, and it is silent on clean input: injecting the
canonical checkout into `PATH`, then `PYTHONPATH`, then `LD_LIBRARY_PATH` produced
`VIOLATION: <VAR> carries a REPOSITORY CHECKOUT path` rc=3 in all three; injecting a non-checkout
path outside the declared environment produced the outside-the-environment refusal in all three.

**Launcher ordering, all eight, real file line numbers.** 0 unguarded activator sources; **8 of 8**
sourced from `ENV_ROOT`; `_mr_lib` containment-checked **before** first use in **8 of 8** (gap
exactly 36 in every one) by a real canonicalized `pwd -P` comparison that exits 2; `--expect-root`
non-comment **14** (raw **22** — the trap reproduces); `REPO=` **0 of 8**; A-3 `--pair` covers every
executing `.py`/`.sh` plus `mnv_guarded_run.py` and both preflight tools in every launcher.

### 2.2 And then the one that does not run

`sbatch_unfold_5d_detector_bkgaware_gpu.sh` is the only launcher whose activator does **not** precede
its preflight tools:

```
LAUNCHER                                       ACTIVATOR   SRCMAN   PARITY  VERDICT
sbatch_bootstrap_5d_gpu.sh                           87      146      155  OK (activator first)
sbatch_seedscan_split_5d.sh                          74      133      142  OK
sbatch_unfold_5d_detector_bkgaware_gpu.sh           227      139      148  *** INVERTED ***
sbatch_sweep_bank_5d_run_bkgaware_gpu.sh             82      142      151  OK
sbatch_uthrow_run_5d_fast.sh                         81      143      152  OK
sbatch_uthrow_block_5d.sh                            77      137      146  OK
sbatch_uthrow_combine_5d_fast.sh                     78      153      162  OK
sbatch_finalize_5d_bkgaware_gpu.sh                   80      255      264  OK
```

Both tools carry `from __future__ import annotations`, and the un-activated `python3` on `saul` is
**3.6.15** (`env -i HOME=$HOME bash -lc 'command -v python3; python3 -V'` → `/usr/bin/python3`,
`Python 3.6.15`), where that line is a **`SyntaxError`**. Every launcher invokes bare `python3` (6
occurrences in this file); none names an explicit interpreter.

**Reproduced by execution, with a control that discriminates.** A valid A-2(f) manifest was generated
first with the conda interpreter, so the interpreter is the only variable:

```
# ARM 1 -- unfold_detector preamble :1-157, login-default interpreter
[env-preflight] OK: 14 closure member(s) verified …
  File ".../nd-unfolding/mnv_source_manifest.py", line 35
    from __future__ import annotations
SyntaxError: future feature annotations is not defined
[oi136] FAIL: the execution tree is not the tree that was approved (see above).
REPRO_EXIT=3

# ARM 2 -- SAME preamble, conda already on PATH
[srcman] SOURCE MANIFEST IDENTICAL (778 files, 70fb59d4…)   6 of 6 CURRENT
CONTROL_EXIT=0

# ARM 3 -- bootstrap (non-inverted) preamble, SAME login-default interpreter
[env-preflight] OK …  [env-pathcheck] OK …  6 of 6 CURRENT
BOOTSTRAP_EXIT=0
```

Arm 3 is the fixture rule applied to my own instrument: the identical un-activated interpreter runs a
sibling launcher's preamble to exit 0, so arm 1's failure is attributable to the **ordering
inversion**, not to the interpreter, my harness, or the tree.

**Three things make this a Gate-1 failure rather than a nit.**

1. **It is the round-4 defect class, not a new one.** Round 4's decisive finding was "every launcher
   aborts at the activator, before any preflight tool, any guard, or any science invocation." Seven
   launchers are repaired. The eighth still aborts before any guard and any science invocation — by a
   different mechanism (interpreter unavailability rather than file absence), at a different line.
2. **The refusal misattributes its own cause.** It prints `[oi136] FAIL: the execution tree is not
   the tree that was approved`. The tree *is* the approved tree — 778 files, digest identical,
   porcelain 0. A reader of that `.out` would go looking for a tampered deployment. This is the same
   class as the `EMPTY-REPOSITORY-ORIGIN-SET` string §7.0.11 had to fix.
3. **The documented procedure does not rescue it.** `#SBATCH --export=ALL` means the job inherits the
   submitting shell, so a submitter who happened to have conda active would not see this. But the
   runbook of record (`RUNBOOK-20260822-b1-lift-preflight.md:409-419`) exports the roots and calls
   `sbatch` **without activating conda** — and exports neither `MNV_ENV_ROOT` nor `MNV_CONDA_PREFIX`
   at all (0 occurrences of each in that file). Following the procedure of record, all eight
   launchers refuse at `${MNV_ENV_ROOT:?}`; supply those two and `unfold_detector` still dies at its
   preflight. Depending on ambient interpreter state is precisely what a mandatory env root exists to
   eliminate.

### 2.3 Why 34 green launcher arms are silent about it

`test_k0_launcher_two_roots.py` is **34 arms, rc=0** at this sha, and its fixture is a real repair of
round 4's stub — a genuine multi-hop closure outside the code root. But `good_env()` builds the
launcher's environment as `dict(os.environ, …)`, so the launcher inherits the **test runner's** PATH,
which already carries a modern `python3`. **The fixture supplies the very interpreter the activator
exists to supply**, so the dependency of the preflight tools on activation order cannot be expressed
in this fixture at all. And the ordering arm is explicitly
`test_the_preflight_is_textually_BEFORE_every_guarded_science_invocation` — textual, while ruling 21
requirement 3 says the ordering "must be settled by **running** each launcher under stubs …, **not**
by reading the file."

So the run-under-stubs ordering requirement graded in `F-2(a)` is met in form and not in substance:
the dynamic arms vary the *refusal preconditions*, never the *interpreter*. This is the round-4
fixture finding recurring one level down — the shape the builder's own confirmation §8 calls "the
normal case here, not an unlucky one."

---

## 3. The other two FAILs, and the PASSes that carry flags

### 3.1 F-2(a) — the counting halves, recorded because they DO pass

For completeness, the two counts `F-2(a)` also requires are **zero**, and I record that plainly so
the failure is not read more broadly than it is:

* unguarded production `python3` invocations other than the enumerated 16-call preflight set: **0**
  (`mnv_preflight_census.py` → `14 guarded + 16 declared-preflight + 0 unclassified = 30`, rc=0,
  measured on the deployed root);
* executing `.py`/`.sh` not covered by an A-3 `--pair`: **0** among files under the code root. The
  five environment-closure files and the eight `activate.d` scripts — round 4's "count ≥ 5, not
  zero" — are no longer unbound: they are digest-bound by `mnv_env_manifest.tsv`, verified before
  use, which is the mechanism substitution round 4's own repair item 2 prescribed ("git cannot bind
  these bytes, so substitute the mechanism rather than relocating it"). I accept that substitution on
  the same reasoning ruling 25 accepted the pure-git gate for `setup_salloc_env.sh`.

`F-2(a)` fails on the **ordering clause** of §7.0.13 requirement 3, not on either count.

### 3.2 F-14 — FAIL. Two independent grounds, both at the graded sha.

**(i) `generate_manifest.py --check` exits 1.** §7.0.7(1) makes this an explicit pre-submission
requirement of `F-14`, "measured in a clean worktree". Measured in a clean detached worktree
(`porcelain = 0`) and again on the deployed root:

```
@ f3c27870   rc=1   OUT OF DATE: docs/orchestration/MANIFEST.tsv; rows=425 …
@ a8f79c9a   rc=0   OK:          docs/orchestration/MANIFEST.tsv; rows=434 …
```

**The packet §6 claims `-> rc 0`. It is rc 1.** I diffed the committed table against the generated
one rather than arguing from the exit code: four rows differ, and every difference is *caused by this
repair* — the generated table adds `nd-unfolding/mnv_env_preflight.sh` and
`nd-unfolding/mnv_env_manifest.py` to reference-source lists and adds the eight launchers, moving
counts `36→46`, `197→206`, `43→44`. `MANIFEST.tsv` is not in `f3c27870`'s changed-file list. Note the
row *count* is unchanged at 425, which is likely how this passed inspection — and the branch-vs-main
split is likely how rc=0 was obtained: on `main` it is genuinely 0.

**(ii) A coupled ratchet the repair breaks, in a file the repair edited.**
`test_uq_remediation.SubstitutionFenceS1.test_the_UNCLASSIFIED_REMAINDER_IS_PINNED_because_it_is_the_real_exposure`
fails **201 != 199**. The two new members of the unclassified remainder are exactly
`nd-unfolding/mnv_env_pathcheck.sh` and `nd-unfolding/mnv_env_preflight.sh` — measured by driving the
test's own `_partition()`. That ratchet exists to force precisely this: *"a new launcher lands in
NEITHER and this test reddens, which forces a classification rather than letting the default be
'unfenced'."*

This is not an arguable coupling. `git diff --name-status f3c27870^ f3c27870` shows
`M nd-unfolding/tests/test_uq_remediation.py` — the commit **edited that very file**, moving
`LibraryResolverSurvivesSbatch`'s extraction window to the new `END RESOLVER` marker, while leaving
the sibling ratchet in the same file red. §6's rule is that every coupled row is discharged *in the
same commit as the repair that moves it*.

**Confirmed platform-independent.** `201 != 199` reproduces on Linux, at the deployed root, under the
conda interpreter with `TMPDIR=/tmp`.

**(iii) Recorded, weaker, and flagged as weaker.** The §6 rows for
`RUNBOOK-20260822-b1-lift-preflight.md` and `PLAN-20260822-oneMember-mii-staged.md` carry **0**
occurrences of `MNV_ENV_ROOT` and **0** of `MNV_CONDA_PREFIX`, so the operator procedure of record
cannot start any launcher. I note this as a finding but do **not** rest `F-14` on it: those rows'
literal text names only the two roots, because it was written before the third existed, and failing a
row for omitting something its own text does not name is the move round 4 correctly declined.
Grounds (i) and (ii) are sufficient and unarguable.

### 3.3 F-17(a) — FAIL. The `.sh` route is again reported by the quantities that were fixed.

`F-17(a)` requires M-1…M-6 re-measured on both trees and **every difference reported as a finding**.
I re-measured all six independently. Four reproduce exactly and are recorded as such:

* **M-2** — **125** importable top-level names on the canonical checkout; **zero** collisions against
  `sys.stdlib_module_names` (3.11.14) and a third-party set, **in both directions**. Reproduces.
* **M-3** — `verify_hash_bindings.py` rc=0, `ALL BINDINGS INTACT`. Reproduces.
* **M-4** — `b2d7d4ca24707344cf12f99c0aa51381b81dd445`, **721** dirty = **717 `??` + 4 ` M`**.
  Reproduces exactly. (The behind-count is a drifting quantity; I did not quote one.)
* **M-6** — repaired: `checked` written at `:369` with `checked_provenance` at `:370`, and the
  `guard_installed`/`checked`/`outcome` triple is present. Reproduces, including the `else 0` residual
  the filed document honestly records.

Two differences are **unreported**:

**(a) M-5 answers about the four quantities that were repaired, not about the route.** Packet §4
reports `REPO=` 0/8, unguarded activator sources 0/8, `ENV_ROOT` sources 8/8, `_mr_lib`
bind-after-use 0/8 — all four of which I independently confirm. But the `.sh` route carries a fifth
property that decides whether the path runs at all, and §2 measures it adversely: one of eight
launchers aborts before any guard or science invocation. As filed, M-5 reads as though the shell route
is fit. **This is the identical finding round 4 recorded against M-5, one round later against a
broader but still incomplete quantity set** — the cheap, greppable properties were re-measured and
reported as the whole, which is the error this campaign has a name for.

**(b) M-1 dropped a row and under-counts the surviving literals.** The contract's M-1 table has ten
rows, including `unified_throw_cov.py` ("imported, not an entrypoint"). The filed re-measurement
omits that row entirely, and lists **three** remaining canonical literals. There are **four**:

```
unfold_nd_omnifold_unbinned.py:73   _DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
sweep_bank_5d.py:59                 _DATA_ROOT = …
unified_throw_cov.py:69             _DATA_ROOT = …          <-- ABSENT from the filed table
adopt_unified_5d.py:35              _REPO      = …
```

**The substance is benign and I say so plainly**: the missing one is a `_DATA_ROOT`, the data role the
two-root design explicitly permits, and all six B-1 files are genuinely repaired — I verified every
prologue derives from `Path(__file__).resolve().parents[N]` with **no absolute fallback**. The defect
is the enumeration, not the code. But "three literals remain" is the sentence the filed document
itself warns would mislead, and it is wrong by one.

### 3.4 F-9 and F-12(N-1) — discharged FIRST-HAND, which round 4 explicitly did not do

Round 4 flagged that it verified the mechanism and bytes but "did not re-run N-1 myself." I ran all
three arms, each to its own inventory path and its own capture file, all paths throwaway under `/tmp`.

**Arm A — F-9 refused** (`--expect-root` = clean tree), `A_EXIT=3` captured unpiped:

```
[oi136] SCRIPT OUTSIDE THE EXPECTED TREE -- REFUSING BEFORE THE FIRST IMPORT.
[oi136]   script        /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py
[oi136]   which is in   /pscratch/sd/j/josephrb/MINERvA-OmniFold
[oi136]   expected      /pscratch/sd/j/josephrb/k0r2/clean

outcome              'refused:script-outside-expect-root'
verdict              'REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT --expect-root; …'
guard_installed      False        checked  0
checked_provenance   'not-measured-no-guard-was-installed'
refusal_site         'b4-script-containment'
expect_root          /pscratch/sd/j/josephrb/k0r2/clean
script_checkout_root /pscratch/sd/j/josephrb/MINERvA-OmniFold
repo_origin_count    0            violation  None
```

9.1 exit 3 ✓ · 9.2 exact `outcome`, never empty/green ✓ · 9.3 all three named ✓ · 9.4 the **pair**
`guard_installed=false` **and** `checked=0`, with provenance and refusal site making the zero a
measurement rather than a bare default ✓ · 9.5 `[remedyA]` absent (0), `[adopt5d]` absent (0),
`--out` fails `test -e`, witness directory empty before **and** after, one merged stream per arm,
status captured unpiped ✓ · 9.6 graded on the triple, **not** by grepping for a token — and reported
rather than graded: the token occurs **0** times in the record and **0** in the log.

**Arm B — O-1 paired** (`--expect-root` = the canonical tree it was launched from): reaches
`[remedyA] running the PINNED writer as a subprocess:` (count 1), `guard_installed=True`,
`checked=9`, `expect_root == script_checkout_root`, verdict `REPOSITORY-ORIGINS-INSPECTED`. So the arm
**could** have succeeded — `F-12(N-1)(ii)` discharged, and arm A's silence is containment rather than
breakage. (Its exit is 1 because the child segfaulted on the deliberately nonexistent throwaway ROOT
inputs, which happens *after* the marker and is exactly what throwaway paths produce.)

**Arm C — U/U' unguarded**, no wrapper, no inventory record written:

```
UUPRIME seed_offset_policy.__file__ = /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/seed_offset_policy.py
```

`F-12(N-1)(iii)` discharged: the arm retains and names `seed_offset_policy` as counterfactual origin
evidence, asserted on `__file__`. `F-12(N-1)(i)` is arm A's `script_checkout_root` ≠ `expect_root`,
read off the path the guard resolved.

### 3.5 F-1(a) — PASS, with A-2(g)'s attempted-write arm now supplied

A-2(a)–(g) each measured as a separate observation on the deployed root, every status read unpiped:
`HEAD f3c27870…`; porcelain **0** (counted with `wc -l` on a redirected file); `--require-checkout`,
`--require-no-nested-checkout`, `--require-not-nested`, `--require-readonly` each **rc=0**; A-2(f)
**778** files / `70fb59d4…`. Both preflight tools, both new env `.sh` tools and the guard are all
**IN** the 778-entry manifest, satisfying §7.0.13 requirement 2.

**(g) now has the third instrument round 4 said was owed.** §7.0.14: *"verified means an attempted
write, as the job's own user, fails."*

```
mode bits   nd-unfolding dr-xr-x---   mnv_source_manifest.py -r--r-----
walk        find . -path ./.git -prune -o -type f -writable -print | wc -l  ->  0
ATTEMPT     : > $C/nd-unfolding/.g5_write_probe
            bash: …/.g5_write_probe: Permission denied      -> write REFUSED, no file created
```

The refusal arms for (d) and (e) are exercised in §2.1 (env root inside a checkout, env root inside
another declared root, symlinked view) and by the launcher suite's nesting arms, so (c)(d)(e)(g) are
fail-closed **checks** rather than documentation, per ruling 22.

### 3.6 F-8(a) — PASS, and it is the weakest PASS in this column

P-6 re-run by me on the deployed root at `f3c27870`, full output, and it reproduces the filed table
**exactly**: `4+2+2+2+1+1+1+1 = 14` across 8 distinct entrypoints, every one addressed through
`${CODE_ROOT}`. P-5's fifth blind spot is published (packet §5) and does name all three channels
explicitly. The subprocess enumeration reconciles: **0** executing spawn sites in eight of the nine
files, exactly **1** in `mii_adopt_unified_5d_stamped.py:788`, and that child is **WRAPPED** — the
code root's `build_child_argv` emits the guard and a mandatory inventory, fail-closed twice.

**Flag.** The `P5-P6` document of record is bound to the superseded sha `6113a34d` and banner-marked
"re-measured, never inherited"; the packet defers the re-run to the grader rather than publishing
P-5/P-6 at `f3c27870`. I graded the criterion on content I measured myself, which reproduces. A
cleaner package would re-publish both at the graded sha, and a stricter grader could call the filing
half NOT-EVALUABLE and therefore a FAIL. I judged that too harsh given the content reproduces
exactly, and I record the choice so it can be attacked.

### 3.7 The broader packet suite — the exact result, and one claim withdrawn on the builder's behalf

Packet §6 claims `-> 390 passed, 2 skipped`. Measured, `TMPDIR=/private/tmp`, six modules as listed:

```
2 failed, 388 passed, 2 skipped in 117.73s
```

The two failures are **not** equivalent, and I settled each on the target platform rather than
reporting both:

1. `SubstitutionFenceS1…UNCLASSIFIED_REMAINDER` — **201 != 199**. **Real**, and it reproduces on
   Linux at the deployed root. This is §3.2(ii).
2. `LibraryResolverSurvivesSbatch.test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT`
   — `'RESOLVED=/private/tmp/…' not found in 'RESOLVED=/tmp/…'`. **A macOS artifact, not a defect**:
   the assertion normalizes stdout with `.replace("/private/", "/")` but compares against an
   un-normalized `os.path.realpath(td)`, and on macOS `/tmp` is a symlink to `/private/tmp`. It
   **passes on Linux** (`Ran 1 test … OK`, conda interpreter, `TMPDIR=/tmp`). I am not counting it
   against the package.

So the honest figure on the target platform is **389 passed / 1 failed / 2 skipped**, and the one
failure is the coupled ratchet. Also recorded: running the whole `LibraryResolverSurvivesSbatch` class
*from the protected deployment* raises `PermissionError` writing `nd-unfolding/_t_direct.sh` — a
consequence of A-2(g), not a defect, and incidentally the attempted-write evidence in §3.5. No file
was created and the deployed porcelain stayed 0.

---

## 4. THE MINIMAL REQUIRED REPAIR — and then stop

Four parts. **No submission, no rehearsal, and no downstream work is authorized by this verdict.** I
diagnosed these; I did not implement any of them.

1. **Move `unfold_detector`'s activator above its preflight tools.** In
   `sbatch_unfold_5d_detector_bkgaware_gpu.sh`, relocate `source "${ENV_ROOT}/setup_salloc_env.sh"`
   (`:227`) and the `mnv_env_pathcheck` call (`:233`) to sit immediately after
   `mnv_env_preflight` (`:86`) and **before** `python3 "$SRCMAN"` (`:139`) — i.e. adopt the shape the
   other seven already have. This is the one-hunk fix; nothing else in that launcher needs to move.
   **Then add the arm that would have caught it**: `LauncherFixture` must run at least one launcher
   with a `PATH` that does **not** already contain a modern `python3`, and assert the launcher still
   reaches its parity line — because the interpreter is currently supplied by the fixture rather than
   by the activator, and no existing arm can fail on this defect. Consider also failing closed
   explicitly: have the launcher assert the interpreter it is about to use can parse the tools,
   rather than letting a `SyntaxError` be reported as "the execution tree is not approved."
2. **Regenerate `docs/orchestration/MANIFEST.tsv`** at the graded sha so
   `generate_manifest.py --check` exits 0 **on the branch**, and re-measure it there rather than on
   `main`.
3. **Discharge the `SubstitutionFenceS1` remainder ratchet**: classify
   `nd-unfolding/mnv_env_preflight.sh` and `nd-unfolding/mnv_env_pathcheck.sh` as hooked, fenced, or
   explicitly out of scope, and take the new constant **from the test's own output**, never by hand.
   199 is not a target.
4. **Restate M-5 against the route, and restore M-1's tenth row.** M-5 must report whether each of
   the eight launchers can *execute* its preflight, not only the four greppable properties; M-1 must
   carry `unified_throw_cov.py` and say **four** surviving literals, with the `_DATA_ROOT`-vs-`_REPO`
   distinction that makes three of them benign. Also update
   `RUNBOOK-20260822-b1-lift-preflight.md` and the plan's §C to export `MNV_ENV_ROOT` and
   `MNV_CONDA_PREFIX`, or no operator can start any launcher.

**Then re-declare and re-grade.** Parts 1–4 change `.py`/`.sh` and docs, so the `f3c27870`
declaration expires on its own terms and the 778/`70fb59d4…` pair must be re-taken. The next grader
must be a fresh non-builder who is not me.

---

## 5. Findings recorded but NOT counted against any criterion

Each is real, none is a criterion miss, and each is stated so it is not rediscovered.

1. **`ROOT628_CONDA` is still `${VAR:-default}`** (`setup_salloc_env.sh:11`), pointing at
   `/global/common/software/nersc/pe/conda/…/bin/conda`. Round 4's repair item 2 asked for **both**
   `ROOT628_PREFIX` and `ROOT628_CONDA` to be pinned; only the prefix became mandatory (as
   `MNV_CONDA_PREFIX`). The exposure is bounded — the *prefix* is mandatory, so the digest-bound
   `activate.d` set is determined, and `mnv_env_pathcheck` would refuse a rogue conda that put a
   checkout on any channel — and the default is a declared system prefix, not the canonical checkout.
   Worth closing; not a violation of any of the eighteen.
2. **The unreadable-member arm refuses with the wrong reason.** A closure member that exists but
   cannot be read reports `COULD NOT LOOK: no sha256 tool for <path>` (rc=2). It fails closed, which
   is what matters, but the message names a missing tool when the cause is a permission. One-line fix:
   distinguish "the tool is absent" from "this file could not be hashed."
3. **`MNV_ENV_MANIFEST` is defaulted** (`${MNV_ENV_MANIFEST:-${CODE_ROOT}/…}`) where the three roots
   are mandatory. The default is inside the read-only, manifest-covered code root, so it is not the
   hardcode-wearing-a-flag A-1 forbids — and it is what let me run the adverse arms without touching
   `pscratch`. Recorded for symmetry only.
4. **`repo_origin_count=1` on the O-1 paired arm** while my printout of the origin list was empty:
   that is my instrument guessing a JSON key name, not a discrepancy in the record. Recorded so
   nobody reads a contradiction into §3.4.
5. **Round 4's "12 `activate.d` scripts" was an over-count** (12 files, 8 `*.sh`). The manifest's 8 is
   correct for bash activation. Recorded because the 12 appears in a canonical verdict on `main`.

## 6. The parts of this verdict most likely to be wrong

1. **Failing `F-17(a)` rather than carrying the §2 defect once.** I argue M-5's subject *is* the
   route's fitness; a grader who disagrees reports **16/2** and Gate 1 still does not pass. The tally
   is sensitive to this choice; the conclusion is not.
2. **Passing `F-8(a)`** when the P-5/P-6 artifacts of record are bound to a superseded sha and the
   packet deferred the re-run to me. A stricter grader calls the filing half NOT-EVALUABLE — a FAIL
   under §7.0.8 — and reports **14/4**.
3. **Accepting the digest manifest as discharging A-3's `--pair` obligation** for the thirteen
   unpairable environment files. It is the substitution round 4's own repair prescribed and the
   analogue of ruling 25, but it is a mechanism swap and Joseph may want it ruled on explicitly.
4. **The §2 severity depends on the submitting shell.** A submitter with conda already active would
   not see the `unfold_detector` abort. I hold that this makes it *latent*, not *absent* — the
   documented procedure does not activate conda, and a mandatory env root exists precisely so that
   ambient state cannot decide the run. If Joseph rules that submitters may be assumed to have the
   environment active, part 1 of the repair shrinks to the missing test arm and the misleading
   message, and `F-2(a)` becomes arguable.
5. **`generate_manifest.py --check` on a feature branch.** If the convention is that `MANIFEST.tsv`
   is regenerated only on `main` at merge time, §7.0.7(1)'s "measured in a clean worktree" would be
   satisfied by main's rc=0 and my `F-14` ground (i) falls. Ground (ii) — the broken ratchet — stands
   independently and is enough on its own.

---

## 7. What this verdict does and does not authorize

**Nothing.** §G is unchanged. The k=0 rehearsal is **not** launched and no downstream work is
authorized. Gate 2 is not graded and cannot be. `OI-136` is not closed. No member `k≠0`, no leg 6, no
scientific verdict of any kind. The two-gate split, the 14/30 boundary and rulings 12–25 are
untouched by this document.

## 8. Explicit confirmation of non-mutation

* **No Slurm job was submitted.** `squeue -u josephrb` shows exactly one job, `57275989`, submitted
  `2026-08-20T15:02:55` — three days before this session — `PENDING (user env retrieval failed
  requeued held)`. `sacct -S 2026-08-22T00:00` returns that same single row and nothing else.
* **No science was run**, no covariance constructed or adopted, no rehearsal started, no leg launched.
* **No scientific artifact** was created, opened for write, moved, renamed or deleted. The negative
  controls used only nonexistent throwaway paths under `/tmp`; the `--out` witness directory was empty
  before and after; the 41.44 GB combined intermediate and every archive product were never named.
* **No deployment was changed.** `/pscratch/sd/j/josephrb/k0r2/clean` is still `f3c27870…` with
  porcelain **0**; A-2(g) protection intact and demonstrated by a refused write; the canonical
  checkout is still `b2d7d4ca…` with **721** dirty entries, unchanged.
* **No repository edit, commit, push or merge.** Primary checkout still `a8f79c9a`, with exactly the
  two pre-existing untracked files (`PROJECT_STATE_PILOT_PROPOSAL.tmp.md`, `log_test.txt`), which I
  did not touch. Both of my detached worktrees had `porcelain = 0` and were removed. My one `--write`
  attempt on `generate_manifest.py` was rejected as an unrecognized argument (rc=2) and wrote nothing;
  the regenerated table exists only in memory and in `/tmp`.
* **`set -u` was neither added nor invoked** anywhere.
* Cluster writes were confined to `/tmp` and every temporary directory was removed.

---

*Recorded by the fresh third-party Gate-1 grader, 2026-08-23. This is a PRE-SUBMISSION verdict only.
It grades the Gate-1 column of §F and nothing else.*
