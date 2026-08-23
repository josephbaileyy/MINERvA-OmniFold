# GATE 1 — ROUND-8 TERMINAL REGRADE, k=0 EXECUTION INTEGRITY

**Grader:** independent non-builder session (`minerva-omnifold-6d`). **Read-only throughout.**
**Date:** 2026-08-23. **Host:** `login02` (`saul.nersc.gov`). **Window:** 2026-08-23T15:01Z – 16:0xZ.

---

## 1. ELIGIBILITY

I did not build any commit in the `build-k0-execution-integrity` history, did not author the
operative §7.0 split, and did not author the round-8 repair `1d2b795d` or the packet edit `a54038b2`.
Under **§7.0.10** that is the whole of the disqualification, and prior service as the round-5,
round-6 and round-7 grader does not disqualify me — the coordinator has ruled so three times and
the contract's text is about authorship, not repetition. I graded rounds 5, 6 and 7; I inherit
nothing from them, and where this verdict contradicts one of my own earlier ones I say so explicitly
(§9).

**What I did not do:** no repository edit, commit, push, merge, deployment or repair; no Slurm
submission; no rehearsal, science or covariance work; no artifact altered or deleted; no `set -u`
added or invoked; no new acceptance criterion; no request for another grader.

---

## 2. FROZEN OBJECTS, EACH VERIFIED

| object | declared | measured by me | verdict |
|---|---|---|---|
| operative rubric | 1160 lines, `e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173` | **identical at four `main` shas** (see below) | **CONFIRMED** |
| candidate / deployed tree | `a54038b21fdebfc975bec452a05866ffa571a36c` | `git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD` → `a54038b2…` | **CONFIRMED** |
| deployment hygiene | porcelain 0, 0 writable | porcelain **0**; `find . -path ./.git -prune -o -type f -writable -print \| wc -l` → **0** | **CONFIRMED** |
| graded predecessor | `14980486` (round 7) | 2 commits behind HEAD | **CONFIRMED** |
| canonical checkout | `b2d7d4ca…`, 722 dirty | `b2d7d4ca24707344cf12f99c0aa51381b81dd445`, porcelain **722** | **CONFIRMED** |

### 2.1 The rubric by digest, not by branch — and this mattered

`main` moved **eleven commits** under me during this pass (nine by mid-pass, two more by close) (peer lanes: a note restructure, an
ISSUE-57 fix, a process-instrumentation lane). I therefore verified the rubric digest at every head
I saw:

```
1ed5e8b6    lines=1160  e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173
origin/main lines=1160  e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173
c73be5e1    lines=1160  e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173
9948da58    lines=1160  e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173
d3cdc6d3    lines=1160  e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173   (cmp: IDENTICAL)
482ec086    lines=1160  e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173   <- final head at close
```

I also confirmed **none of the peer commits touched any filing I grade** —
`git diff --name-only 1ed5e8b6..d3cdc6d3 -- docs/orchestration/` contains no review contract, no
round-7 packet, no M-1…M-6 filing, no instrument, no ruling record. Main moving did not shift the
grading basis.

**The deployed tree carries a superseded rubric and I did not grade from it.** In the candidate tree,
`docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md` is **575 lines**,
`80402f75057aa58c99825916bf67ac55643a6a88ff4f171b2eb7a1fd3872fb3e`. Grading from the branch would
have been void. The builder disclosed this; I verified it independently.

### 2.2 The three freeze points

| froze at | claim | my measurement |
|---|---|---|
| `60cf728d` | eight launchers + `test_k0_launcher_two_roots.py` | `git diff --name-only 60cf728d..HEAD -- 'nd-unfolding/**'` → **0 lines**. Also **0** for `14980486..HEAD`. |
| `1d2b795d` | `measure_m1_m6.py` + `test_measure_m1_m6.py` — the only executable change since round 7 | `git diff --name-status 14980486..HEAD` → `M MANIFEST.tsv`, `M MEASUREMENT-…md`, `M PACKET-…md`, `M measure_m1_m6.py`, `A test_measure_m1_m6.py`. **CONFIRMED** |
| `a54038b2` | packet, filing, regenerated views | 2 commits: `1d2b795d`, `a54038b2`. **CONFIRMED** |

The builder adopted my round-7 framing correction (that `e93364d1` touched only `MANIFEST.tsv`) and
then found a worse version of the same error in its own note. The packet now carries the
three-point table and the sentence **"`docs/orchestration/` is not a synonym for 'not executable'"**.
Both verified present in the deployed bytes.

---

## 3. F-1(a) … F-18(a) — CLAUSE BY CLAUSE

| # | pre-submission requirement (§7.0.5) | verdict |
|---|---|---|
| **F-1(a)** | code root at a **named sha**; A-2(a)–(g) measured **and filed** incl. the A-2(f) digest; (d)(e)(g) fail-closed; both preflight tools in the manifest | **FAIL** — §4 |
| **F-2(a)** | both counts zero; ordering settled by running | **PASS** — §5 |
| **F-3(a)** | `--allow` in no production invocation; publish the command | **PASS** |
| **F-4(a)** | denominator fixed on the bench and `> 0`; 14 science invocations | **PASS** |
| **F-5(a)** | generator + comparator exist, each with a fires-on-mismatch and silent-on-match test | **PASS** |
| **F-6(a)** | `build_child_argv` emits guard + inventory; a test asserts a flagged `repo_origin_count: 0` | **PASS** |
| **F-7(a)** | P-4 mechanism: per-entrypoint pin, both-direction comparator, absent/undeclared pin fails closed | **PASS** |
| **F-8(a)** | P-6 re-run at the pinned sha with full output and reconciled; P-5 inventory produced | **PASS** (flagged) |
| **F-9** | N-1 exit 3 *through B-4*, `outcome`, both roots, `checked==0` **and** `guard_installed==false`, no `seed_offset_policy` | **PASS** |
| **F-10** | N-2 exit 3 through the child wrapper on the `build_child_argv` template, O-1…O-4 | **PASS** |
| **F-11** | N-3 for each of the six B-1 files, both directions | **PASS** |
| **F-12** | N-1 restated (§7.0.12); N-2/N-3 on `__file__`; U/U′ names `seed_offset_policy` | **PASS** |
| **F-13** | B-4 script-containment refusal implemented and covered both directions | **PASS** |
| **F-14** | every §6 row discharged in the same commit as the repair; **plus** §7.0.7 `generate_manifest --check` = 0 | **PASS** |
| **F-15** | the two named suites green under `unittest`, counts **as measured**, explicit `TMPDIR` | **PASS** |
| **F-16** | `verify_hash_bindings.py` exits 0, `ALL BINDINGS INTACT`, after all edits | **PASS** |
| **F-17(a)** | M-1…M-6 re-measured on the code root **and** the canonical checkout; differences reported as findings | **PASS** — §6 |
| **F-18(a)** | a fresh non-builder records the pre-submission verdict clause by clause | **PASS** (this document) |

**TALLY: 17 PASS / 1 FAIL / 0 NOT-EVALUABLE.**

§F's no-partial-credit rule applies within each gate: any single miss is a FAIL of that gate.

---

## 4. F-1(a) — THE FAILED CRITERION

**The requirement, verbatim (§7.0.5, F-1 PRE-SUBMISSION cell):** *"code root constituted at a **named
sha**; A-2(a)–(g) all measured and filed, including the A-2(f) source-manifest digest — and (d), (e),
(g) as executable FAIL-CLOSED checks, not documentation (ruling 22, §7.0.14); both preflight tools
present in the manifest (§7.0.13)."*

**Seven of the nine limbs pass, measured by me at `a54038b2`:**

```
(b) porcelain                     0 lines (counted on a redirected file, not via $?-after-a-pipe)
(c) --require-checkout            rc=0
(d) --require-no-nested-checkout  rc=0
(e) --require-not-nested          rc=0
(g) --require-readonly            rc=0   AND independently: 0 writable files by filesystem walk
    both preflight tools in the A-2(f) listing:
        nd-unfolding/lib_mnv_env_preflight.sh
        nd-unfolding/lib_mnv_env_pathcheck.sh     (§7.0.13(2) — manifest membership)
```

**Two limbs fail.**

### 4.1 A-2(f): the source-manifest digest is not filed at the candidate sha

Measured by the contract's own instrument, in the deployed tree, at `a54038b2`:

```
$ python3 nd-unfolding/mnv_source_manifest.py --repo /pscratch/sd/j/josephrb/k0r2/clean \
      --write /tmp/r8_srcman.json --require-readonly --require-checkout \
      --require-no-nested-checkout --require-not-nested
rc=0
[srcman] /pscratch/sd/j/josephrb/k0r2/clean: 780 tracked source files,
         listing sha256 1b45da558929b0ec6eedbc56504a440252e39a9270e6d8f9796c02eb3d2895ad,
         HEAD a54038b21fdebfc975bec452a05866ffa571a36c, dirty 0
```

The **filed** value is from the round-5 packet §0: **778** files, `70fb59d4…`, at `f3c27870`. The
count has moved twice, by exactly the amount its cause predicts:

```
f3c27870 -> 778     (the filed figure)
60cf728d -> 779     +1  measure_m1_m6.py
0b556379 -> 779
14980486 -> 779     <- the ROUND-7 candidate
1d2b795d -> 780     +1  test_measure_m1_m6.py
a54038b2 -> 780     <- the ROUND-8 candidate
```

**A covering search, in both trees, for anything declaring the current figures:**

```
$ git grep -l -E '779 tracked|780 tracked|1b45da55|a54038b2' <main> -- docs/     -> 0 files
$ grep -rl 'a54038b2\|1b45da55' /pscratch/sd/j/josephrb/k0r2/clean               -> (nothing outside .git)
$ grep -rn 'listing sha256' <candidate>/docs/
    RECEIPT-20260822-k0-n1-and-guarded-arms.md:196:  [srcman] $CLEAN: 771 tracked source files, …
```

The only `listing sha256` in the candidate's docs is **771** — older still. Nothing on `main`,
nothing in the deployed tree, tracked or untracked, declares 780, `1b45da55…`, or `a54038b2`.

The round-5 declaration's own expiry clause is *"falsified by … any `.py`/`.sh` add or delete (moves
`file_count`)"*. Two `.py` files were added. **The filing is expired by its own terms.**

**The self-reference excuse does not apply here, and that is the load-bearing point.** A document
cannot name its own commit — true, and the packet says so. But **A-2(f) covers only tracked `*.py`
and `*.sh`**. A Markdown-only commit cannot move the listing. So `780` and `1b45da55…` were exactly
declarable *inside* `a54038b2`, and remain declarable inside any doc-only commit made now. The
impossibility that excuses the sha does not extend to the digest.

### 4.2 A-2(a): the named sha is named, and it is the wrong one

The packet's own SHAs table at `a54038b2` reads:

```
| **FINAL CANDIDATE** | `e93364d158ab16c109f124c54199caaad28c0708` |
| **DEPLOYED AT**     | /pscratch/sd/j/josephrb/k0r2/clean, HEAD `e93364d1…`, porcelain=0, 0 writable |
```

`git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD` is **`a54038b2`**. A-2(a) requires *"`git
rev-parse HEAD` equals the declared sha"*. Declared `e93364d1`; actual `a54038b2`. **This is not a
missing declaration — it is a present and false one**, and it is false about the row a reader would
use to decide which bytes were graded.

The mitigating sentence — *"the deployed sha is whatever `git … rev-parse HEAD` returns, and it is
the one to grade"* — is a **definite description, not a citation**. It re-points on every commit and
nothing can falsify it; it also silently contradicts the table two paragraphs above it. This
campaign has already paid for that distinction once.

### 4.3 Materiality, stated plainly

This is a **filing** defect, not an execution defect. The tree itself is correctly constituted: I
measured every A-2 clause and all seven measurable ones pass. Nothing about the executing bytes is
wrong, and no science is endangered by it.

But F-1(a) is precisely and only the criterion that the constitution be **measured *and filed***
against a **named** sha. It is the referent criterion — the one that exists so a later reader can
tell which tree was approved. As filed, a reader following the packet would verify `e93364d1` against
a listing of 778 files and a digest that no longer matches, and would get three wrong answers in a
row. That is the failure mode F-1(a) was written for, so I record it as a FAIL rather than a note.

### 4.4 Minimal repair — one doc-only commit, no code change

1. In the packet's SHAs table, replace the `DEPLOYED AT` / `FINAL CANDIDATE` sha with the deployed
   value, or state the row as *unresolved until the post-deploy receipt* and stop naming a sha there.
2. File the A-2(a)–(g) table at the deployed tree with **`780` files, listing sha256
   `1b45da558929b0ec6eedbc56504a440252e39a9270e6d8f9796c02eb3d2895ad`**, and the seven rc=0
   receipts. Because A-2(f) covers only `.py`/`.sh`, this commit cannot invalidate its own figure.
3. Since a doc-only commit *does* move `MANIFEST.tsv`, regenerate it in the same commit — F-14's
   coupling — and re-run `generate_manifest --check` after.

I did not implement any of this.

---

## 5. F-2(a) — PASSES, RE-MEASURED NOT INHERITED

The launchers are **byte-identical** to the round-7 candidate (`git diff 14980486..HEAD --
'nd-unfolding/**'` → 0 files), so the subject did not move. I re-measured anyway.

### 5.1 Structure, measured

One gate, in all eight, `for _mnv_rel in …` through `done`:

```
launcher                                   gate     first source   files named
sbatch_bootstrap_5d_gpu.sh                 81-97    102            3
sbatch_finalize_5d_bkgaware_gpu.sh         74-90     95            3
sbatch_seedscan_split_5d.sh                68-84     89            3
sbatch_sweep_bank_5d_run_bkgaware_gpu.sh   76-92     97            3
sbatch_unfold_5d_detector_bkgaware_gpu.sh  82-98    103            3
sbatch_uthrow_block_5d.sh                  71-87     92            3
sbatch_uthrow_combine_5d_fast.sh           72-88     93            3
sbatch_uthrow_run_5d_fast.sh               75-91     96            3
```

- **One distinct gate digest across all eight:** `480faeb987cb2352334ee1d17e8eaca4e5532973e5230d6be9b4fdc50561112c`.
- The gate **ends before the first `source`** in every launcher, with nothing sourced above it.
- **No sourced parity helper exists** — the check is inline in all eight (a helper would itself
  execute unbound, which is F-2(a) one level down).
- The three covered files are `lib/resume_guard.sh`, `nd-unfolding/lib_mnv_env_preflight.sh`,
  `nd-unfolding/lib_mnv_env_pathcheck.sh`.

### 5.2 Count 1 = 0

```
$ python3 nd-unfolding/mnv_preflight_census.py            rc=0
[preflight-census] 8 launcher(s): 14 guarded + 16 declared-preflight + 16 interpreter-probe
                   + 0 unclassified = 46 non-comment python3 invocation(s); 18 commented out
[preflight-census] OK: every python3 invocation is guarded or declared
```

The 14 re-derives against ruling 21 with the comment filter §7.0.13 warns about:
`1 5 1 1 2 2 1 1 = 14`. The unfiltered command returns **29** here — an adjacent subject, not the
answer.

### 5.3 Count 2 = 0

Every `.sh` a launcher sources is either gate-covered, outside the code root by design, or covered by
an A-3 `--pair`:

| sourced file | disposition |
|---|---|
| `lib_mnv_env_preflight.sh`, `lib_mnv_env_pathcheck.sh` | **gate-covered before use** |
| `${CODE_ROOT}/lib/resume_guard.sh` | **gate-covered before use** |
| `${ENV_ROOT}/setup_salloc_env.sh` | outside every checkout by design; its 14-member closure is digest-verified in pure bash before it is sourced |
| `${_mr_lib}/lib_member_resume.sh` | tracked, and **covered by an A-3 `--pair` in all eight** |
| `$_mr_rg` (finalize only) | containment-bound to `${CODE_ROOT}/lib/resume_guard.sh` before the source |

### 5.4 My own five-arm control battery, run against a clone of the deployed bytes

I re-implemented the gate's logic myself rather than trusting the repository's test, and ran it on a
`git clone` of the deployed tree:

```
ARM 1  clean clone                     rc=0, output ''            -> SILENT ON GOOD
ARM 2  mutate lib/resume_guard.sh      rc=3, REFUSE(mismatch) lib/resume_guard.sh HEAD=a89f72d3 work=7e53a64c
       mutate lib_mnv_env_preflight.sh rc=3, REFUSE(mismatch) …preflight.sh  HEAD=f5abad89 work=bd0643ef
       mutate lib_mnv_env_pathcheck.sh rc=3, REFUSE(mismatch) …pathcheck.sh  HEAD=bad2010e work=addda6d7
ARM 3  mutate combine_cov_nd.py        rc=0, output ''            -> correctly does NOT fire
ARM 4  remove lib_mnv_env_pathcheck.sh rc=3, REFUSE(unhashable)   -> absence refuses
ARM 5  restore everything              rc=0, output ''            -> POWER: returns to silence
```

Arm 5 is what makes arms 2–4 evidence: an instrument that always refuses would have produced the same
red as arms 2–4. Arm 3 is the narrowing direction — an over-broad gate would have fired there and
would be the wrong gate (whole-tree cleanliness is A-2(g)'s job, and the later source-manifest
comparison does refuse that tree).

### 5.5 The repository's own suite, re-run

`python3 -m unittest tests.test_k0_launcher_two_roots -v` → **Ran 48 tests, OK, rc=0**, including
`test_a_mutation_to_ANY_of_the_three_is_REFUSED_by_name`,
`test_no_launcher_sources_ANY_of_the_three_before_the_parity_loop`,
`test_the_gate_covers_EXACTLY_the_three_and_names_them`,
`test_the_parity_block_is_BYTE_IDENTICAL_in_all_eight`,
`test_the_parity_check_is_INLINE_and_not_delegated_to_a_sourced_helper`, and the dynamic
`NoPythonRunsBeforeTheActivator` arms with their negative control.

**Ordering is settled by running, not by reading** (§7.0.13(3)): the dynamic arms execute each
launcher under stubs and observe emitted argv order.

---

## 6. F-17(a) — PASSES

### 6.1 The fix, read and adversarially tested

`canonical_form()` replaces the round-7 exact-equality test. Bounded at
**exact-or-followed-by-a-separator**:

```python
if not value.startswith(CANONICAL_LITERAL): return None
rest = value[len(CANONICAL_LITERAL):]
if rest == "":            return "exact"
if rest.startswith("/"):  return "subpath"
return None            # a longer sibling path such as ...-Analysis-Note
```

The literal scan now walks **every** `ast.Constant` string, not only assignment right-hand sides,
with `assigned_to` built first so an inline path is still attributed.

**Both power checks, run by me on writable clones:**

```
A  revert canonical_form to exact equality      -> Ran 9, FAILED (failures=3)
      test_the_SUBPATH_form_is_detected__the_round_7_defect
      test_the_SUBPATH_assignment_shape_is_counted_and_named
      test_an_INLINE_literal_with_no_variable_is_still_counted
B  revert the scan to assignment-RHS-only       -> Ran 9, FAILED (failures=1)
      test_an_INLINE_literal_with_no_variable_is_still_counted
```

Arm A reproduces the builder's claim of 3-of-9. **Arm B is mine, and it is the one the builder did
not claim:** it proves the *second* half of the fix is independently load-bearing rather than
carried by the first. Each half has at least one arm that dies when only that half is reverted.

`test_measure_m1_m6.py` on the shipped bytes: **Ran 9 tests, OK, rc=0** under CPython 3.11.14. The
arms pin both directions, including `…-Analysis-Note`, `…-gregor-pet2`, `…2`, `…_old` as **non**-matches
and the B-1 derived-root shape as silent-on-good.

### 6.2 Candidate M-1 — ten rows, four literals, verified twice

```
=== CANDIDATE: /pscratch/sd/j/josephrb/k0r2/clean
--- M-1 (10 files)
    bootstrap_nd.py                  literal=-                    insert=28   repo_mods_after=3
    seedscan_split.py                literal=-                    insert=37   repo_mods_after=3
    unified_throw_cov.py             literal=_DATA_ROOT@69(exa)    insert=61   repo_mods_after=5
    unified_throw_cov_5d.py          literal=-                    insert=42   repo_mods_after=3
    unfold_nd_omnifold_unbinned.py   literal=_DATA_ROOT@73(exa)    insert=77   repo_mods_after=4
    sweep_bank_5d.py                 literal=_DATA_ROOT@59(exa)    insert=51   repo_mods_after=6
    combine_cov_nd.py                literal=-                    insert=None repo_mods_after=0
    analyze_universes_5d.py          literal=-                    insert=None repo_mods_after=0
    mii_adopt_unified_5d_stamped.py  literal=-                    insert=149  repo_mods_after=2
    adopt_unified_5d.py              literal=_REPO@35(exa)        insert=38   repo_mods_after=0
--- M-2  importable=127 stdlib_collisions=0 py=3.11.14
--- M-3  {'present': True, 'rc': 0, 'all_intact': True}
--- M-4  head a54038b2…, dirty 0, untracked 0, modified 0, behind 0, ahead 73
--- M-5  n=8, missing=[], repo_assign=[], activator_from_code_root=[], activator_from_env_root=[all 8]
--- M-6  WRITTEN BUT DEFAULTED
```

Ten rows, `unified_throw_cov.py` present as the tenth. **3 `_DATA_ROOT` + 1 inert `_REPO`**, all
`exact` form.

**Instrument-independent cross-check by grep** — 4 lines on the candidate, 7 on the canonical,
matching the instrument on both trees:

```
CANDIDATE   unified_throw_cov.py:69  _DATA_ROOT = ".../MINERvA-OmniFold"
            unfold_nd_omnifold_unbinned.py:73  _DATA_ROOT = …
            sweep_bank_5d.py:59                _DATA_ROOT = …
            adopt_unified_5d.py:35             _REPO      = …          TOTAL 4
CANONICAL   bootstrap_nd.py:10   _ND  = ".../MINERvA-OmniFold/nd-unfolding"   [subpath]
            seedscan_split.py:21 _ND  = ".../MINERvA-OmniFold/nd-unfolding"   [subpath]
            + 5 × _REPO exact                                          TOTAL 7
```

The candidate carries **no canonical subpath literal at all**, so the round-7 blind spot never
touched the candidate column — which the filing now states.

**I verified the disclosed limit rather than accepting it.** The filing discloses that the instrument
counts literals, not computed paths, and claims no such construction exists in the ten files on
either tree. My covering search for that hazard — any `josephrb` string that is *not* the full root,
which is what a `join`/concatenation would need — returns **empty on both trees**. The f-strings
present all interpolate `{_REPO}` / `{_DATA_ROOT}`, i.e. they derive from an already-counted literal.
The claim is true, and it is now checked rather than asserted.

### 6.3 Canonical M-1 — SEVEN, and the reporting obligation is discharged

The filing's canonical section now reports **seven**, names `bootstrap_nd.py:10` and
`seedscan_split.py:21` as `_ND` **subpath** with inserts at `:11`/`:23` and three repository modules
after each, and carries a ⚠ banner recording that the count *was* five, that five was wrong, and that
the error **understated** the hazard. Its differences table marks both the instrument defect (2b) and
the canonical M-3 result (3) **"against the builder"**.

That is exactly what F-17(a) asks for: differences reported as findings, including the ones that make
the builder look worse. The round-7 failure is repaired at its root, with the root cause named
correctly (the same exact-match class had been fixed in `m6` earlier the same day in the same file,
and the sibling function was never swept; the instrument shipped with no tests).

### 6.4 Canonical M-3

I ran the canonical measurement myself, on the canonical tree's **own** instrument
(`/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/verify_hash_bindings.py`, confirmed by
`ps`), twice by two routes: standalone, and through `measure_m1_m6.py --tree <canonical>`. Wall time
~42 minutes each. Both return **`rc=1`**, and the mismatch set is **exactly one**, reproducing the
filing's three quoted lines byte for byte:

```
MISMATCH nd-unfolding/pet/train_fullevent_nominal.py
  want 66aa1f8f62087e6ef6ca79928aca954ed25aea1bb304d71e8dbf159ec417dadd
  got  91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc
  from nd-unfolding/pet/step1_iteration_dynamics/cold_fresh_split/slurm-56534116_2/STEP1_DYNAMICS.json
*** BINDINGS BROKEN ***
RC=1
```

I independently confirm every load-bearing claim the filing makes about it: the script is
byte-identical on both trees (`91144bee…`) at the same blob, the **receipt is untracked** and is one
of that tree's 718 `??` entries, it exists only on the canonical checkout, and it therefore **cannot
be resolved from the candidate** — which is why the candidate's `rc=0` is not hiding it. My run also
printed the checker's *"1 known pre-existing drift (submit-time provenance)"* line naming
`sbatch_dump_g2_mefhc.sh`, which is the allowlist category the filing correctly observes this
mismatch is **not** in. This is canonical-tree drift and I do not read it as candidate corruption.

**The full canonical table from the instrument, my run** — the third independent confirmation of the
count, after my grep and the filing:

```
=== CANONICAL: /pscratch/sd/j/josephrb/MINERvA-OmniFold
    bootstrap_nd.py                  literal=_ND@10(sub)     insert=11   repo_mods_after=3
    seedscan_split.py                literal=_ND@21(sub)     insert=23   repo_mods_after=3
    unified_throw_cov.py             literal=_REPO@42(exa)   insert=45   repo_mods_after=5
    unified_throw_cov_5d.py          literal=_REPO@24(exa)   insert=27   repo_mods_after=3
    unfold_nd_omnifold_unbinned.py   literal=_REPO@47(exa)   insert=52   repo_mods_after=4
    sweep_bank_5d.py                 literal=_REPO@32(exa)   insert=35   repo_mods_after=6
    combine_cov_nd.py                literal=-               insert=None repo_mods_after=0
    analyze_universes_5d.py          literal=-               insert=None repo_mods_after=0
    mii_adopt_unified_5d_stamped.py  literal=-               insert=149  repo_mods_after=2
    adopt_unified_5d.py              literal=_REPO@35(exa)   insert=38   repo_mods_after=0
--- M-2  importable=125 stdlib_collisions=0        (candidate: 127)
--- M-3  rc=1, all_intact=False
--- M-4  b2d7d4ca…, dirty 722 = 718 ?? + 4 M
--- M-5  repo_assign = ALL EIGHT; activator_from_env_root = []      (the unrepaired world)
--- M-6  NO INVENTORY WRITE -- "the vacuity question cannot even be asked of this tree"
```

**Seven literals, two of them subpath-form `_ND` with active inserts and three repository modules
after each.** This is exactly what I found in round 7 and exactly what the repaired instrument now
prints. The two rows that were positively false at round 7 are now correct, and the count that was
five is seven.

**The canonical hazards are reported separately and are real.** On that tree all eight launchers
assign the repository root unconditionally (`repo_assign` = 8/8), no launcher sources the activator
from an env root, and the guard emits no inventory at all — so `M-6`'s vacuity question *cannot be
asked* there, which the filing records as a difference **against the builder**. None of this reaches
the candidate, and I state that as a separation of subjects, not as reassurance.

**One omission, recorded as a future finding rather than a failure (§10.8).** My canonical run also
printed a second, co-reported condition the filing does not mention: `*** RECEIPT BINDING INVENTORY
CHANGED *** expected 118 / b16e9e8e…, observed 120 / deb46900…`, with the instrument's own warning
*"Do not update these constants merely to make this pass."* Two bindings were **added** on that tree,
which is not a broken binding — so the filing's *"exactly one binding"* is **true** of the mismatch
set, and nothing it states is false. But it introduces the block with *"the inventory is now
captured"*, and this part of the inventory is not. That is an incompleteness about a tree nothing
executes from, it changes no Gate-1 decision, and it is a different kind of thing from round 7's
failure, where two of ten rows were positively **false**. I fail false statements; I flag incomplete
ones about the data-role tree.

### 6.5 M-6 — measured first-hand, and it is not a Gate-1 failure

Measured on the candidate: `n_lines=557`, `counts_resolutions=True`, `inventory_write_lines=[369]`,
`else_zero_default_lines=[369]`, state **"WRITTEN BUT DEFAULTED — a containment-path zero is a
default, not a measurement"**. The residual vacuity hole is open and unchanged, exactly as disclosed.

I checked this against the rubric rather than accepting "out of scope", and equally declined to
manufacture a criterion for it:

- **F-5's `checked > 0` is its POST-REHEARSAL half** — not gradable at Gate 1.
- **F-4(a)'s anti-vacuity is the bench denominator**, fixed at 14 and `> 0`. Met.
- **§7.0.11 already names this exact default** and prescribes the remedy: F-9 is read off the
  **triple**, never off `checked` alone. Verified implemented in `mnv_guarded_run.py`:

```
:369  "checked":             (guard.checked if guard is not None else 0),
:370  "checked_provenance":  (CHECKED_MEASURED if guard is not None else CHECKED_NOT_MEASURED),
:371  "guard_installed":     guard is not None,
:383  "outcome":             outcome,
      "refusal_site":        site,
```

And exercised: the N-1 receipt records `checked=0`,
`checked_provenance=not-measured-no-guard-was-installed`, `guard_installed=false`,
`outcome=refused:script-outside-expect-root`, `refusal_site=b4-script-containment`. The defaulted
zero is therefore **interpretable**, which is what §7.0.11 requires. No existing criterion is
breached; I create none.

---

## 7. THE OTHER SIXTEEN, WITH THEIR EVIDENCE

**F-3(a) PASS.** Non-comment `--allow` count across the eight: `0 0 0 0 0 0 0 0`. A raw grep returns
**1** hit in `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:11` — inside a comment that reads
*"FAIL-CLOSED: no --allow-cv-background"*. Counting that would have been counting an adjacent
subject; the published command filters comments first.

**F-4(a) PASS.** Denominator fixed on the bench at **14** and `> 0`; re-derived per launcher as
`1 5 1 1 2 2 1 1` with the comment filter, reproducing ruling 21's *"finalize 5, detector 2,
uthrow-block 2, one each elsewhere"*. Census `rc=0`, 0 unclassified.

**F-5(a) PASS.** `mnv_source_manifest.py` and `mnv_import_set_ratchet.py` both present.
`test_source_manifest_constitution.py` carries matched FIRES/SILENT pairs per A-2 clause — fires on a
nested checkout and *names* it, fires on the recorded `.claude/worktrees` instance, silent on a clean
root; fires on a writable tree, silent once protection is applied; one writable file is enough to
refuse; undo restores and the check refuses again. **Ran 71 tests, OK, rc=0** (with
`test_p4_ratchet_fail_closed` and `test_k0_preflight_exclusion_census`) — see §8.6 on where.

**F-6(a) PASS.** `test_mnv_guarded_run.py` asserts `repo_origin_count` **present, not absent**
(`assertIn`) and `== 0` for the child argv shape, and `> 0` on the arms that must be non-zero. P-3's
disclosure is written unconditionally; a zero is a reportable state, never a pass.

**F-7(a) PASS.** `test_p4_ratchet_fail_closed.py` exists and is green;
`test_oi136_failopen_inventory_ratchet.py` pins the fail-open set exactly
(`test_the_fail_open_set_is_EXACTLY_the_recorded_one`), asserts its own negative control still
rejects something, and carries the anti-vacuity arm
`test_this_ratchet_cannot_pass_over_an_empty_set`.

**F-8(a) PASS, flagged.** P-6 re-run by me at the candidate reproduces the published output exactly —
`4+2+2+2+1+1+1+1 = 14` invocations over **8 distinct entrypoints**, every one addressed through
`${CODE_ROOT}`. P-5's inventory is produced with the subprocess enumeration and each child marked
(one real child, `mii_adopt_unified_5d_stamped.py:788`, **WRAPPED**).
**Flag:** the fifth blind spot (`PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH`) lives in the round-5 packet §5
and in the P5-P6 document's *banner*, while that document's own blind-spot **table still lists four**.
The inventory is complete across two documents but not in the one a reader would open. Recorded as a
future finding, not a failure: F-8(a) requires the inventory produced, and it is.

**F-9 / F-10 / F-11 / F-12 PASS.** `RECEIPT-20260822-k0-n1-and-guarded-arms.md` records, for N-1:
`outcome = refused:script-outside-expect-root`; `refusal_site = b4-script-containment` (*"exit 3
alone cannot say which protection fired"*); `checked = 0` **as expected** with
`checked_provenance=not-measured-no-guard-was-installed` and `guard_installed=false`; and
`seed_offset_policy` appearing **0 times, recorded as an observation, not as a mechanism** — which is
what §7.0.11 requires, since F-9 now *forbids* naming it. The U/U′ arm retains and names
`seed_offset_policy` as counterfactual origin evidence (F-12). The parent/child P-3 records show
`checked=9`/`repo_origin_count=1` and the child at `checked=213`. Mechanisms green in the 57-test run.

**F-13 PASS.** `VERDICT_REFUSED_SCRIPT` and `SITE_SCRIPT_CONTAINMENT = "b4-script-containment"` in
`mnv_guarded_run.py`; `ScriptContainment` test class present and green; both directions covered
(script-outside refused 3, script-inside not refused).

**F-14 PASS.** The §6 rows the round-8 repair moves are the `verify_hash_bindings` postcondition
(rc=0 `ALL BINDINGS INTACT`, re-run **after** the edits at `a54038b2`) and the RUNBOOK/PLAN §C
rewrite (verified in §8.1). §7.0.7's addition, `generate_manifest.py --check` exiting 0 **in a clean
worktree**, I measured in a fresh clone at **both** commits, because round 5's F-14 failure was
exactly a generated artifact stale in the commit that moved it:

```
1d2b795d : rc=0  OK: MANIFEST.tsv; rows=429 …  porcelain=0
a54038b2 : rc=0  OK: MANIFEST.tsv; rows=429 …  porcelain=0
```

Rows moved 428 → **429**, matching the one added `.py`. Not carried forward from round 7.

**F-15 PASS.** The two named suites under `unittest` with an explicit `TMPDIR`:

```
TMPDIR=/tmp/r8_tmpdir python3 -m unittest tests.test_mnv_guarded_run \
                                          tests.test_oi136_failopen_inventory_ratchet
Ran 57 tests in 6.694s        OK        RC=0
```

**Count quoted as measured at the graded sha: 57.** Not M-8's 24, not round 7's figure — §7.0.7(2)
forbids carrying it forward and the suite has moved again.

**F-16 PASS.** `verify_hash_bindings.py` → **rc=0**, `ALL BINDINGS INTACT`, run in the deployed tree
at `a54038b2` after all edits. Status read from an unpiped command.

**F-18(a) PASS.** This document, clause by clause, by a fresh non-builder, citing the artifact and
command for each F-number. A summary attesting "all controls passed" would itself be a FAIL of F-18;
that is why §4 and §9 exist.

---

## 8. THE FOUR ADDITIONAL VERIFICATION ITEMS

**8.1 Runbook and plan §C export `MNV_ENV_ROOT` and `MNV_CONDA_PREFIX` correctly — YES.**

```
RUNBOOK:424  export MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env
RUNBOOK:428  export MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28
PLAN:438     export MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env         # OUTSIDE every checkout; no default
PLAN:439     export MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28   # no default
```

Both are declared with **no default**, and the runbook states the reason: *"binding the activator's
bytes does not determine which conda runs"*. I checked the prefix path resolves, since two spellings
are in circulation: `/global/homes/j/josephrb -> /global/u2/j/josephrb` is a symlink and both
spellings resolve to `/global/u2/j/josephrb/.conda/envs/root_6_28`. Interpreter there: **3.11.14**.
`MNV_LAUNCHER_DIR` is documented at RUNBOOK:437 / PLAN:442 with the `sbatch`-spool-copy reason.

**8.2 The activation source no longer points into `MNV_CODE_ROOT` — CONFIRMED.**
M-5 measured on the candidate: `activator_from_code_root = []`, `activator_from_env_root =` **all
eight**, `repo_assign = []`, `missing = []`. PLAN:451-453 records that
`source "${MNV_CODE_ROOT}/setup_salloc_env.sh"` was the round-4 `F-2(a)` defect and that each
launcher now sources the activator from `${MNV_ENV_ROOT}`. Text and measurement agree.

**8.3 Required suites and postconditions run in the correct tree after the final commit — YES.**
Everything in §7 was run inside `/pscratch/sd/j/josephrb/k0r2/clean` at `a54038b2`, i.e. the deployed
tree after the final commit, not in a checkout of my own. The one exception is stated at 8.6.

**8.4 Matched-tree regression: identical failure sets, no new failure — CONFIRMED.**
`test_k0_launcher_two_roots.py` is byte-identical to the round-7 candidate (0 files changed under
`nd-unfolding/`), and it runs **48 tests, OK** at `a54038b2` — the same 48 arms and the same **empty**
failure set as at `14980486`. The only delta is the **+9** new arms in `test_measure_m1_m6.py`, all
passing. Identical failure sets, no new failure, no arm lost.

**8.5 The `--check-freshness` postcondition is RED, and it is not the candidate's.**
`python3 docs/orchestration/generate_live_state.py --check-freshness` → **rc=1**,
`STALE :: Git: 85f6762e, HEAD d3cdc6d3` (and the lag persists at `482ec086`). This is `main`'s
generated view lagging the **peer-lane commits** that landed during my pass, not anything about `a54038b2`. I attribute it to those lanes
explicitly and do not charge it against the candidate — misattributing another tree's drift to the
graded one is the error round 7 turned on. The generator prints its own caveat that regeneration
fixes the sha and timestamp but does **not** revalidate the authored `Declared state`; on that basis
regenerating would convert a visible STALE flag into an invisible false-current claim, so it should
not be done as a reflex. I did not regenerate anything.

**8.6 One suite cannot run against the tree it is meant to protect.**
`test_k0_preflight_exclusion_census.py` copies the launchers into `TMPDIR` preserving mode, so
against the **A-2(g)-protected** deployed tree its 13 power arms die on
`PermissionError: … sbatch_bootstrap_5d_gpu.sh`. From a writable clone of the **same bytes**:
**71 tests, OK, rc=0**. So the arms do fire and §7.0.13(1)'s "a test must fail when an unguarded
invocation appears" is demonstrably satisfied — but only off the protected tree.
`test_k0_launcher_two_roots.py` handles the same protection correctly (48/48 from the read-only
tree). Future finding, not a Gate-1 failure: F-15 names the two suites that pass, and this
repository has already lost five days once to a read-only sandbox faking failures.

---

## 9. WHERE THIS VERDICT CORRECTS MY OWN EARLIER ONES

**I passed F-1(a) in round 7 and I should not have.** At `14980486` the tracked source listing was
**779** files, the filed figure was 778 at `f3c27870`, and the packet named `e93364d1` as `DEPLOYED
AT` while the deployed HEAD was `14980486`. Both limbs of §4 were true then, one commit smaller. I
verified the freshness, generated-manifest and binding postconditions the round-7 commission named,
and did not think to ask whether the A-2(f) digest had been re-filed after the count moved. The
builder did not regress this; **I missed it**, and it is the second time in this campaign that a
criterion about *filing a referent* has survived a clause-by-clause pass because the underlying tree
was in good order.

The general shape, since it is the transferable part: **a stale declaration and a missing declaration
look identical from the inside of a green tree.** Every A-2 clause I could execute returned rc=0, and
that is exactly what made the filing question easy to skip — the measurements were all available, so
whether anyone had *written them down against this sha* felt like bookkeeping. F-1(a) is the
criterion that says it is not.

I also record that the campaign's two long-running failures are now genuinely closed. `F-2(a)`
survived a control battery I wrote myself, and `F-17(a)`'s instrument survived a power check the
builder did not claim. Gate 1 fails on a filing clause, not on execution integrity.

---

## 10. FUTURE FINDINGS — recorded, and they do NOT expand Gate 1

Per the standing instruction, these are outside the operative rubric's pre-submission halves and are
**not** folded into the tally.

1. **`lib_member_resume.sh` is sourced before its parity check in `finalize` alone.** It is tracked
   and executed. In seven launchers its A-3 `--pair` precedes the source (e.g. bootstrap: pair `:191`,
   source `:267`). In `sbatch_finalize_5d_bkgaware_gpu.sh` the source is at **`:181`** and the
   `--pair` at **`:303`** — so it executes before its bytes are git-verified. It *is* containment-bound
   before use (`:175-180`, canonicalised against `${CODE_ROOT}/nd-unfolding`, fail-closed), which
   proves *which* file, not *which bytes*. Count 2 remains **0** on the rubric's letter, which asks
   only whether a `--pair` covers the file, and Joseph's 2026-08-23 ruling named the two environment
   libraries specifically — so extending it here would be me adding a criterion. Minimal repair if
   wanted: add `nd-unfolding/lib_member_resume.sh` as a fourth entry in the byte-identical gate,
   which keeps all eight identical, or hoist finalize's `--pair` block above `:181`.
2. **The packet publishes a gate-block digest I cannot reproduce.** It states
   `sha256(gate block) = 3e211fe6831aeb8d93522c6cbd2d72375a09a42ad5440eb9bac2e32e839a4142`. Five
   natural extents give `480faeb9…` (`for`…`done` inclusive), `917015ce…`, `a6523783…`, `9d60c839…`,
   `63d5e971…`; the extent the repository's own test uses (`# (1) EVERY TRACKED FILE` →
   `unset _mnv_rel …`) gives `fdc87463…`. A published digest whose extent is not stated is not a
   receipt — nobody can falsify it. The *claim* it supports (one distinct block across eight) is
   independently true; only the number is unusable.
3. **`test_measure_m1_m6.py` is in no declared suite list.** It is not named in the runbook, the plan,
   or the packet's evidence section, and there is no `pytest.ini`/`pyproject.toml` `testpaths`. It
   passes when invoked directly; nothing invokes it by default. The instrument it protects is now the
   committed mechanism for every future M-1…M-6 re-measurement.
4. **Item 8.6** — the census suite cannot run against an A-2(g)-protected tree.
5. **Item 8.5** — `main`'s LIVE-STATE view is STALE from peer-lane commits, and regenerating it
   without revalidating `Declared state` would stamp a fresh sha onto unvalidated prose.
6. **The P-5 blind-spot table still lists four**, with the fifth only in a banner and in the round-5
   packet (§7, F-8(a) flag).
8. **Canonical M-3's co-reported inventory delta is unmentioned** (§6.4): the same run that yields
   the one mismatch also reports `expected 118 / observed 120` receipt bindings on the canonical tree.
   Nothing in the filing is false and the mismatch count is right; the phrase "the inventory is now
   captured" is simply wider than what was captured.
7. **The candidate branch still carries the 575-line superseded rubric** (`80402f75…`). The builder
   flagged this and left it unrepaired as out of scope; I concur that repairing it unasked would be
   scope-widening, and note that it is a live trap for any future grader who reads from the branch.

---

## 11. MY OWN INSTRUMENT ERRORS THIS ROUND, REPORTED AGAINST MYSELF

Seven, each of which could have become a false finding:

1. **`shutil.copy2` preserved A-2(g) read-only mode**, so my power-check harness died on
   `PermissionError` before mutating anything. Fixed with an explicit `chmod`. Failed loudly, which
   is the good direction.
2. **`cd X && nohup … &` backgrounded the `cd`**, so a foreground `git rev-parse` ran in `$HOME` and
   printed *"fatal: not a git repository"*. I nearly recorded that the canonical checkout was not a
   repository. Twice. Re-measured with the cwd set: `b2d7d4ca…`, 722.
3. **A script that `cd`'d into `nd-unfolding` then used a repo-root-relative path** reported
   *"No such file or directory"* for the M-1…M-6 filing. I nearly recorded the filing as **deleted**.
   `git ls-tree` and `git diff --name-status` show it as `M` at every commit; it exists, 239 lines.
4. **I grepped for the phrase `"freeze point"`** and got 0 hits on a packet that carries a
   three-freeze-point table worded *"three points, not one"*. I nearly recorded that the correction
   had not landed. A null grep is evidence about the search, not the world.
5. **I ran the launcher suite with conda's `python3` for `unittest` while PATH's `python3` was
   3.6.15**, producing **78 subTest failures** that were the launcher's interpreter-capability probe
   working exactly as designed and saying so (*"This is an ENVIRONMENT fault, not a wrong-tree fault.
   Do not read it as one."*). With a capable PATH: **48 tests, OK**. The fixture supplies the
   interpreter the activator exists to supply — the same trap I documented in round 5.
6. **I ran three suites from the read-only deployed tree** and got 13 `PermissionError`s (§8.6);
   71/71 from a writable clone of identical bytes.
7. **I invoked `mnv_source_manifest.py` without `--write`/`--compare`** and got `rc=2`, *"COULD NOT
   LOOK … measuring nothing and exiting 0 is exactly the shape this file exists to prevent"*. `2` is
   never "clean". Re-run correctly: rc=0 with the figures in §4.1.

Also: I initially read the packet-vs-`main` packet comparison as a divergence before measuring both
sides — they are byte-identical (221 lines, `53a2589bf5a66f3564f9…`).

---

## 12. HYGIENE — BEFORE AND AFTER

**Primary checkout `/Users/josephbailey/local-research/MINERvA-OmniFold`:**

```
BEFORE (2026-08-23T15:01Z)  HEAD 1ed5e8b6   10 porcelain lines:
    8 × ' M docs/analysis-note/*.tex'   (peer note-restructure lane, in flight, NOT mine)
    ?? PROJECT_STATE_PILOT_PROPOSAL.tmp.md
    ?? log_test.txt
AFTER  (2026-08-23T16:0xZ)   HEAD 482ec086    2 porcelain lines:
    ?? PROJECT_STATE_PILOT_PROPOSAL.tmp.md
    ?? log_test.txt
```

The eleven intervening commits and the disappearance of the eight modified `.tex` files are the peer
lane's work, confirmed with that lane directly; the two pre-existing untracked files were **not
touched**. I made **no** edit, stage, commit, push or checkout in this repository.

**Deployed tree** `/pscratch/sd/j/josephrb/k0r2/clean`: `a54038b2` before and after, porcelain **0**
before and after, **0** writable files before and after, no probe residue. A-2(g) protection intact —
demonstrated by the fact that it *blocked* two of my own harness attempts (§11.1, §11.6).

**Canonical checkout**: `b2d7d4ca…`, porcelain **722**, unchanged. Read only.

**Temporary artifacts**, all outside every checkout and all disposable: `/tmp/r8_*` on both hosts,
`/tmp/r8_wt` (a clone used for the mutation arms), `/tmp/r8_powerA`, `/tmp/r8_powerB`,
`/tmp/r8_tmpdir`, `/tmp/r8_tmpdir2`. Nothing was written into `pscratch` outside `/tmp`.

**Slurm:** no submission. `squeue -u josephrb` shows exactly one job, `57275989`, PENDING, submitted
**2026-08-20T15:02:55** — three days before this pass. No rehearsal, no science, no covariance work,
no artifact adopted, quoted or deleted.

---

## 13. CONCLUSION

**Failed criterion: `F-1(a)`** — the code root is not constituted at a *named* sha in any filing, and
the A-2(f) source-manifest digest is filed only at `f3c27870`/778/`70fb59d4…` while the candidate is
`a54038b2`/**780**/`1b45da55…`. Seven of the nine limbs pass; the two that fail are the two that make
the filing a referent. The repair is one documentation commit and no code change (§4.4).

`F-2(a)` and `F-17(a)` — the two criteria this campaign has been chasing since round 5 — **both
pass**, on measurements I took myself, with controls I wrote myself, including a power check the
builder did not claim.

**GATE 1 DOES NOT PASS.**

This is a terminal handoff to Joseph. I have implemented no repair, initiated no further repair, and
requested no further grader. Whether `F-1(a)`'s filing gap warrants a one-commit repair or a
materiality waiver is his call, not mine; I note only that unlike round 7's failure, this one is
cheap to close and closing it requires touching no executable byte.
