# GATE-1 VERDICT (ROUND 7, TERMINAL) 2026-08-23 — pre-submission readiness for the k=0 M(ii) member

**GATE 1 DOES NOT PASS.**

Seventeen of the eighteen pre-submission halves pass; **one fails — `F-17(a)`.** No criterion is
recorded NOT-EVALUABLE. Under §F's no-partial-credit rule as scoped by §7.0.6, any single miss at a
gate is a FAIL of that gate.

**Exact failed criterion: `F-17(a)`.**

**`F-2(a)` PASSES.** Joseph's ruling that A-2(f) does not substitute for A-3 is satisfied: all eight
launchers now carry one byte-identical inline gate that git-binds **all three** tracked files the
preamble sources, **before any of them is sourced**, with no helper. I exercised every control
first-hand on the deployed bytes — clean/silent, mutation refusal on each of the three across all
eight, missing/unhashable, opposite-direction, and dynamic-before-source — and I proved the controls
can fail rather than trusting their green result.

**`F-17(a)` fails for a reason confined to the canonical checkout, and I state its materiality
plainly so it can be waived on the facts rather than on my judgement.** The candidate's M-1 — the
tree Gate 1 authorizes execution from — is complete and correct: ten rows, and the 3 `_DATA_ROOT` /
1 inert `_REPO` split Joseph predicted, which I verified with two independent instruments. The defect
is that the canonical M-1 enumeration reports **five** surviving literals when there are **seven**,
because the committed instrument matches the canonical root by **exact equality** and therefore
cannot see canonical **subpath** literals. It prints `literal=-` for `bootstrap_nd.py` and
`seedscan_split.py` on a tree where both carry `_ND=".../MINERvA-OmniFold/nd-unfolding"` feeding
`sys.path.insert(0, _ND)` with three repository modules after it. **Two of ten rows are positively
false for that tree, and the blind spot is undisclosed.** It changes no Gate-1 decision.

---

## 0. Eligibility, frozen objects, preconditions, hygiene

**Eligibility.** As previously ruled: I did not build the candidate, authored no part of the §7.0
split, and prior service as round-6 grader does not disqualify me. **Disclosure:** `F-2(a)` and
`F-17(a)` are my own round-6 findings, so I have a standing incentive to find them unrepaired. I
therefore tried hardest to break the `F-2(a)` repair and could not — I record it as a PASS, and I
correct one of my own earlier statements against my interest in §5.4.

| object | value |
|---|---|
| **RUBRIC / filings** | `main` @ `d3a63bbc15300cb407263cfd6eeacd0ae8cfea31` |
| **contract** | `REVIEW-CONTRACT-20260822-k0-execution-integrity.md`, **1160 lines**, sha256 `e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173` — **byte-identical to rounds 5 and 6** |
| **CANDIDATE / DEPLOYED** | `149804868443c0f5348a4ba8c5c778fad642828f` |
| **deployment** | `/pscratch/sd/j/josephrb/k0r2/clean`, HEAD `14980486`, porcelain **0**, **0** writable files |
| **A-2(f)** | **779** tracked source files, `8865684660b78b2c63989f0e12f98480470f718ce6ee46ec3246f6fef88eadbf` |
| **env manifest** | `mnv_env_manifest.tsv` sha256 `499e923aaabfcf310e0abdc4a5bdd877cf58d3a9c52bd41d76fa0a05eb131392` |
| **graded predecessor** | `fabeedc2bf78c81d2931ff4876d161c0abfbdbc4` (round 6, 16/2) |
| **hosts** | local `Josephs-MacBook-Pro-9.local`; cluster `saul.nersc.gov` → `login02`/`login34` (bash 4.4.23) |
| **window (UTC)** | `2026-08-23T10:46:59Z` → `2026-08-23T11:40:00Z` |

### Preconditions — all verified, with one correction to the framing

```
$ git rev-parse HEAD                                    d3a63bbc…            (main, exact)
$ ssh saul 'cd /pscratch/…/k0r2/clean && git rev-parse HEAD; git status --porcelain | wc -l'
149804868443c0f5348a4ba8c5c778fad642828f   0            (deployed, exact)
$ ssh saul '… find . -path ./.git -prune -o -type f -writable -print | wc -l'   0
$ ssh saul '( : > …/nd-unfolding/.g7probe )'            Permission denied — no file created
$ git diff --name-only e93364d1..14980486 | grep -v '^docs/orchestration/'      (none)
$ git diff --name-only e93364d1..14980486 | grep -E '\.(py|sh)$'                (none)
$ git diff --stat e93364d1 14980486 -- nd-unfolding lib 2d-unfolding 3d-unfolding   (empty)
```

**Read-only verified three ways** — mode bits (`nd-unfolding` is `dr-xr-x---`), an independent
writable walk (**0**), and an **attempted write as this user that failed** with no residue.

**Correction to the stated framing, because it changes which tree the suites had to run in.**
`e93364d1` is **not itself an executable change** — it modified only `docs/orchestration/MANIFEST.tsv`.
Measured per commit: launcher and test bytes froze at **`60cf728d`**; the measurement instrument
froze at **`0b556379`**; `e93364d1`, `12f33039`, `c35bed58` and `14980486` are docs/manifest only. The
precondition you asked me to verify — *no executable or test bytes changed after `e93364d1`* — holds,
and holds more strongly than stated. Consequence: the suites and postconditions I ran at `14980486`
exercise the same executable bytes as `60cf728d`, and I ran the **doc-sensitive** postconditions
(`generate_manifest --check`, `verify_hash_bindings`, `live_doc_indexed`) at the **final** sha rather
than inheriting the packet's `e93364d1` figures — which matters, because the manifest row count moved
`427 → 428` between them.

### Postconditions

| check | candidate `14980486` | main `d3a63bbc` |
|---|---|---|
| `git status --porcelain` | **0** | **0** |
| `generate_manifest.py --check` | **rc=0**, rows=**428** | **rc=0**, rows=**440** |
| `verify_hash_bindings.py` | **rc=0**, `ALL BINDINGS INTACT` | **rc=0**, `ALL BINDINGS INTACT` |
| `live_doc_indexed.py` | **rc=0** | — |
| `generate_live_state.py --check-freshness` | — | **rc=0**, `FRESH` |

All statuses read **unpiped**. A-2(a)–(g) re-measured as a **postcondition after every other
observation**: all rc=0, digest `88656846…` **identical at both ends**.

**Hygiene.** Primary checkout `d3a63bbc` before and after, porcelain exactly the two pre-existing
untracked files (`PROJECT_STATE_PILOT_PROPOSAL.tmp.md`, `log_test.txt`), untouched. Three isolated
detached worktrees outside `.claude/worktrees/` (`g7-code` @ `14980486`, `g7-main` @ `d3a63bbc`,
`g7-base` @ `fabeedc2`), all porcelain **0**, all removed. Deployed tree unchanged and still
read-only; canonical unchanged at `b2d7d4ca` / 722 dirty. Cluster writes confined to `/tmp`.

**Instrument discipline.** `bash -c` for all multi-file work (zsh does not word-split unquoted
variables). No `$?` read after a pipe. `TMPDIR` explicit on every suite. Two of my own harness errors
are reported against me in §5.4.

---

## 1. The Gate-1 column, criterion by criterion

| # | verdict | first-hand basis |
|---|---|---|
| F-1(a) | PASS | A-2(a)–(g) each a separate observation, all rc=0, at start **and** as postcondition; 779 / `88656846…` identical at both ends; porcelain 0; read-only three ways incl. refused write; all eight preflight/gated/guard files IN the 779-entry manifest |
| F-2(a) | **PASS** | one byte-identical three-file gate in all eight, ending before the first source, no helper; every control exercised first-hand incl. a proven-fireable power arm (§2) |
| F-3(a) | PASS | non-comment `--allow` = **0** across all eight |
| F-4(a) | PASS | denominator **14** + the pinned-writer child, > 0, three ways: non-comment `--expect-root` 14, P-6 `--` targets 14, census `14 guarded` |
| F-5(a) | PASS | `test_source_manifest_constitution` **28**, `test_p4_ratchet_fail_closed` **30**, rc=0; fires-on-mismatch and silent-on-match both pinned |
| F-6(a) | PASS | `build_child_argv` byte-identical to the tree where I verified it; emits guard + mandatory inventory, fail-closed twice; `repo_origin_count` unconditional |
| F-7(a) | PASS | identity comparator + undeclared-pin-fails-closed, 30 arms; **13** census arms incl. fires-on-added-unguarded and fires-on-shrunk-set; census rc=0 |
| F-8(a) | PASS (flagged) | P-6 re-run by me at `14980486`, reproduces **exactly** (8 entrypoints / **14**); subprocess enumeration **1** child, WRAPPED; fifth blind spot published. Flag: P5-P6 doc still bound to `6113a34d` (§5.2) |
| F-9 | PASS | **re-run first-hand at `14980486`**; all six rows of §7.0.11 on the `guard_installed`/`checked`/`outcome` triple (§4.1) |
| F-10 | PASS | `test_n2_child_boundary` **7** arms rc=0 |
| F-11 | PASS | `test_n3_rooted_import_repair` **8** arms rc=0; all six B-1 prologues `__file__`-derived, no absolute fallback |
| F-12 | PASS | N-1's three restated clauses discharged first-hand; N-2/N-3 `__file__` anchors green |
| F-13 | PASS | refused-outside **and** not-refused-inside, plus `--allow`-cannot-launder |
| F-14 | PASS | `generate_manifest --check` **rc=0** in a clean worktree at the graded sha **and** on main; `SubstitutionFenceS1` **11** arms rc=0; `FAILOPEN_COUNT = 52` / `40bd83ca…`; `POSITIVE_CONTROLS` correct; guard `--pair` assertion retained; runbook + plan §C discharged (§3) |
| F-15 | PASS | `TMPDIR=/private/tmp python3 -m unittest test_mnv_guarded_run test_oi136_failopen_inventory_ratchet` → **`Ran 57 tests … OK`**, rc=0 unpiped; counts as measured: **50 and 7** |
| F-16 | PASS | `verify_hash_bindings.py` rc=0, `ALL BINDINGS INTACT`, run **after** all other observations, both trees |
| F-17(a) | **FAIL** | canonical M-1 reports **five** surviving literals where there are **seven**; the committed instrument prints `literal=-` for two files that carry an active `_ND` subpath literal feeding `insert(0,…)`, because it matches the root by exact equality — an undisclosed blind spot (§4.2) |
| F-18(a) | PASS | this document, clause by clause, by an eligible grader |

**TALLY: 17 PASS / 1 FAIL / 0 NOT-EVALUABLE.**

---

## 2. F-2(a) — PASS. The ruling is satisfied, and I proved the controls can fail.

### 2.1 The gate, on the deployed bytes

```bash
for _mnv_rel in lib/resume_guard.sh \
                nd-unfolding/lib_mnv_env_preflight.sh \
                nd-unfolding/lib_mnv_env_pathcheck.sh; do
  _mnv_head="$(git -C "$CODE_ROOT" rev-parse "HEAD:${_mnv_rel}" 2>/dev/null || true)"
  _mnv_work="$(git -C "$CODE_ROOT" hash-object "${CODE_ROOT}/${_mnv_rel}" 2>/dev/null || true)"
  [[ -z … ]] -> exit 3   # "A check that could not run is not a check that passed."
  [[ head != work ]] -> exit 3   # "It is SOURCED below. Refusing to execute unverified bytes."
done
```

* **One distinct digest across all eight.** Extracting the `for … done` block from each launcher and
  hashing it yields **1** distinct value (`480faeb987cb2352…` on my extraction span).
* **All three named, in all eight** — `resume_guard=1 preflight=1 pathcheck=1` for every launcher.
* **All three verified before ANY is sourced.** Gate spans and the first `source` of anything:
  `81-97/102`, `68-84/89`, `82-98/103`, `76-92/97`, `75-91/96`, `71-87/92`, `72-88/93`, `74-90/95`.
  Gate end **<** first source in all eight.
* **No sourced parity helper.** Lines sourced *above* the gate: **0** in all eight. A helper would
  itself execute unbound — `F-2(a)` one level down — and the suite pins that too.

### 2.2 The controls, exercised first-hand on a clone of the deployed bytes

Run from `/tmp` on `saul`, nothing on `pscratch` mutated. The mutation is a line that **writes a
marker file**, so it both breaks the blob and leaves physical evidence if the library was sourced
anyway.

| arm | result |
|---|---|
| **clean / silent** (A-2(g) applied) | **exit 0**, parity-FAIL messages **0**, markers **0**, `6 of 6 CURRENT`, source manifest identical |
| **mutation — `lib_mnv_env_preflight.sh`** | **exit 3**, `FAIL: nd-unfolding/lib_mnv_env_preflight.sh differs from HEAD`, markers **0** |
| **mutation — `lib_mnv_env_pathcheck.sh`** | **exit 3**, named, markers **0** |
| **mutation — `lib/resume_guard.sh`** | **exit 3**, named, markers **0** |
| **POWER / negative control** — same marker line, but **committed** so parity holds | parity-FAIL **0**, markers **1** |
| **missing / unhashable** (library deleted) | **exit 3**, `cannot compute git parity …` + *"A check that could not run is not a check that passed."* |
| **opposite direction** — mutate a tracked file the preamble never sources (`bootstrap_nd.py`) | gate FAIL messages **0** (it correctly leaves it alone); the **later** `srcman` gate refuses: `REFUSING: --require-clean … [' M nd-unfolding/bootstrap_nd.py']` |
| **all eight launchers, mutation** | exit **3**, mutated file **named**, markers **0**, in every one |

**The power arm is what makes the zeros evidence.** Markers = **1** when parity holds and **0** on
every refusal, from the *same* mechanism — so "markers 0" means the refusal genuinely preceded the
source, rather than meaning the marker could never have appeared. Without it every `markers=0` would
also be satisfied by an append that silently never happened.

**The suite agrees and pins the same directions**: `test_k0_launcher_two_roots` is **48 arms, rc=0**,
including a 10-arm class `EveryTrackedSourcedFileIsGitBoundBEFOREAnyOfThemIsSourced` whose members
are byte-identity-in-all-eight, covers-exactly-the-three-and-names-them, mutation-refused-by-name,
the unhashable/empty-string direction, no-launcher-sources-any-before-the-loop,
the-mutation-is-the-marker, a **power** arm, a **narrowing** arm ("a blanket *is the tree clean*
check would pass every arm above"), and a no-helper arm.

### 2.3 The other two F-2(a) obligations

* **Count 1 = 0.** `mnv_preflight_census.py` rc=0: `14 guarded + 16 declared-preflight +
  16 interpreter-probe + 0 unclassified = 46`. Ruling 21's boundary is untouched at 14 + 16, with the
  16 probes as the visible third category Joseph ratified on 2026-08-23.
* **Count 2 = 0.** Every executing tracked file is covered: the three sourced libraries by the
  pre-use git gate; `lib_member_resume.sh` by a `--pair` in all eight **plus** a canonicalised
  containment check before its source; `setup_salloc_env.sh` by the 14-member digest manifest,
  verified pre-source; and finalize's `_mr_rg` by a containment check at `:227-236` that canonicalises
  **both** sides against `${CODE_ROOT}/lib/resume_guard.sh` — whose bytes the early gate binds — before
  sourcing at `:237`.
* **Ordering, settled by running.** Activator **before** the first `python3` in all eight
  (`105/120`, `92/107`, `116/130`, `100/115`, `99/114`, `95/110`, `96/111`, `98/113`); parity-OK
  **before** the first science invocation in all eight (`179/264`… `309/377`). Zero launchers source
  the activator from `CODE_ROOT`.

---

## 3. F-14 — PASS, including the runbook and plan §C

* `generate_manifest.py --check` **rc=0** in a clean worktree at `14980486` (rows 428) **and** on
  main (rows 440). Measured in the graded tree, which is where round 5 got it wrong.
* `SubstitutionFenceS1` **11 arms rc=0**; `FAILOPEN_COUNT = 52`, `FAILOPEN_SHA256 = 40bd83ca…`;
  `POSITIVE_CONTROLS = (adopt_unified_5d.py, 3d-unfolding/unfold_3d_omnifold_unbinned.py)`; the
  `--pair "${GUARD}=…"` assertion retained.
* **Runbook and plan §C both discharge the third-root obligation.** The runbook's block exports all
  three roots plus `MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28`; plan §C `:436-443`
  does the same. I verified the two conda spellings are the **same directory** (`/global/homes` is a
  symlink to `/global/u2`; both `cd -P … && pwd -P` to `/global/u2/j/josephrb/.conda/envs/root_6_28`).
* **The activation source no longer points into `MNV_CODE_ROOT`.** Zero launchers do. The one grep hit
  for `${MNV_CODE_ROOT}/setup_salloc_env.sh` in plan §C is the **removal note** — *"THE SUBMITTING
  SHELL NO LONGER SOURCES THE ACTIVATOR, AND MUST NOT"* — not a live instruction.

### The matched-tree regression comparison, run by me

Both trees are worktrees at the two shas, same host, same interpreter, same `TMPDIR`:

| tree | result |
|---|---|
| candidate `14980486` | **9 failed, 2208 passed, 4 skipped** |
| baseline `fabeedc2` | **9 failed, 2198 passed, 4 skipped** |

```
$ comm -23 fail_cand fail_base    (empty)   # no new failure
$ comm -13 fail_cand fail_base    (empty)   # no accidental fix
FAILURE SETS IDENTICAL
```

**Zero regressions, zero accidental fixes, `+10 passed` = exactly the new parity arms** — reproducing
the packet's claim on an independent environment. My absolute count is 9, not the packet's 13, because
my interpreter and platform differ; the *comparison*, which is the load-bearing part, reproduces
exactly. One of the 9 is the macOS `/private/tmp`-symlink artifact I diagnosed in round 5.

---

## 4. The measurements that decided the verdict

### 4.1 F-9, re-run at the candidate sha

`mnv_guarded_run.py`, `mii_adopt_unified_5d_stamped.py`, `adopt_unified_5d.py` and
`lib_member_resume.sh` are **byte-identical** `fabeedc2 → 14980486` (`git diff --stat` empty), but I
re-ran the control rather than inherit it. Arm A, `A_EXIT=3` unpiped:
`outcome='refused:script-outside-expect-root'`, `guard_installed=False`, `checked=0`,
`checked_provenance='not-measured-no-guard-was-installed'`, `refusal_site='b4-script-containment'`,
`expect_root`=clean tree, `script_checkout_root`=canonical — all three named; `[remedyA]` and
`[adopt5d]` absent; `--out` fails `test -e`; witness directory empty before and after; 9.6 graded on
the triple, and reported-not-graded, the token occurs 0 times. Arm B (O-1 paired) reaches the marker,
`guard_installed=True`, `checked=9` — the arm **could** have succeeded. Arm C (U/U′, no record) named
`seed_offset_policy.__file__` under the canonical checkout.

### 4.2 F-17(a) — FAIL. What passes, and the one thing that does not.

**Most of it passes, and I verified each part twice where I could.**

**CANDIDATE (the tree that executes) — complete and correct.** The committed instrument at
`14980486`, and my own independent AST/substring instrument, agree:

```
--- M-1 (10 files)                                  <- TEN rows, unified_throw_cov.py restored
    unified_throw_cov.py          literal=_DATA_ROOT@69  insert=61  repo_mods_after=5
    unfold_nd_omnifold_unbinned.py literal=_DATA_ROOT@73 insert=77  repo_mods_after=4
    sweep_bank_5d.py              literal=_DATA_ROOT@59  insert=51  repo_mods_after=6
    adopt_unified_5d.py           literal=_REPO@35       insert=38  repo_mods_after=0   <- INERT, measured
--- M-2  importable=127 stdlib_collisions=0 py=3.11.14
--- M-3  rc=0, all_intact=True
--- M-4  head=14980486…, dirty=0
--- M-5  repo_assign=[], activator_from_code_root=[], activator_from_env_root=[all 8]
--- M-6  557 lines, inventory_write=[369], state='WRITTEN BUT DEFAULTED'
```

**The 3 `_DATA_ROOT` / 1 inert `_REPO` split is exactly right**, and I confirmed the candidate carries
**no** canonical *subpath* literal — a substring scan over all ten files returns exactly those four
lines. So the instrument's blind spot below does **not** touch the candidate. The refusal arm works:
`/usr/bin/python3` (3.6.15) → `REFUSING: this measurement needs CPython >= 3.10`, rc=1.

**Canonical M-3 — independently reproduced, exactly as the packet describes.** I ran
`verify_hash_bindings.py` on the canonical checkout myself; it took **~45 minutes** and returned
**rc=1**, `*** BINDINGS BROKEN ***`, with **exactly one** mismatch:

```
MISMATCH nd-unfolding/pet/train_fullevent_nominal.py
  want 66aa1f8f62087e6ef6ca79928aca954ed25aea1bb304d71e8dbf159ec417dadd
  got  91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc
  from nd-unfolding/pet/step1_iteration_dynamics/cold_fresh_split/slurm-56534116_2/STEP1_DYNAMICS.json
```

And I established it **is** the stale untracked PET receipt, rather than accepting that: the receipt
is **untracked** (`git ls-files --error-unmatch` → *did not match any file(s) known to git*), **exists
on canonical and not on the candidate**, and the bound script is **byte-identical** (`91144bee…`) at
the **same git blob** (`9719049c…`) on both trees. So it is a stale provenance receipt, not tree
corruption, and it **cannot reach the candidate**. Canonical M-4 (`722 = 718 ?? + 4 M`), M-5
(`8 of 8 REPO=`), M-6 (`281 lines, no inventory write at all`) all reproduce.

**THE DEFECT.** The filing's canonical M-1 states:

> **FIVE surviving literals, all `_REPO`, none `_DATA_ROOT`** — the unrepaired world:
> `unified_throw_cov.py:42`, `unified_throw_cov_5d.py:24`, `unfold_nd_omnifold_unbinned.py:47`,
> `sweep_bank_5d.py:32`, `adopt_unified_5d.py:35`.

There are **seven**, and the two omitted are **active** hazards of the most serious class:

```
canonical bootstrap_nd.py:10   _ND="/pscratch/…/MINERvA-OmniFold/nd-unfolding"
                        :11    if _ND not in sys.path: sys.path.insert(0,_ND)
                        :12-14 omnifold_nn_core, xsec_nd, seed_offset_policy      -> 3 repo modules
canonical seedscan_split.py:21 _ND = "/pscratch/…/MINERvA-OmniFold/nd-unfolding"
                         :23   sys.path.insert(0, _ND)
                         :24-27 omnifold_nn_core, xsec_nd, seed_offset_policy     -> 3 repo modules
```

So the canonical tree carries **six** active hardcoded-root import hazards plus one inert, not the
one the filing singles out as *"the hazardous one."*

**The cause is an undisclosed instrument blind spot, and it is not a prose slip.**
`measure_m1_m6.py` detects a literal with
`isinstance(v, ast.Constant) and v.value == CANONICAL_LITERAL` — **exact equality** against the
canonical *root*. `_ND` is the root **plus `/nd-unfolding`**, so the test cannot match it. The
instrument's own canonical output therefore prints:

```
nd-unfolding/bootstrap_nd.py      literal=-   insert=11  repo_mods_after=3
nd-unfolding/seedscan_split.py    literal=-   insert=23  repo_mods_after=3
```

**Two of ten rows are positively false for that tree** — and internally contradictory on their face,
since a rooted `insert` at `:11` with three repository modules after it on the *unrepaired* tree
cannot coexist with `literal=-`. The filing discloses two other instrument defects it found (the `m6`
substring bug, the pre-3.10 refusal) but not this one.

**Why this is F-17(a) and not a new criterion.** F-17(a) requires M-1…M-6 re-measured *"on
`MNV_CODE_ROOT` at the pinned sha **and on the canonical checkout** … and any difference from this
document reported as a finding."* M-1's specified content includes the *"carries the root literal"*
column per entrypoint. On the canonical checkout that column is wrong for two of the ten rows, and the
contract's own M-1 table records both as carrying the literal — so the filing silently contradicts the
contract on two rows and reports no difference. I am grading an obligation that already exists; I have
added nothing.

**Materiality, stated plainly because Joseph decides, not me.** This changes **no Gate-1 decision**.
The candidate is measured completely and correctly. The canonical tree is one from which nothing may
be executed or imported, and the filing says so correctly; adding two more hazards to a tree already
wholly off-limits alters no authorization. The error direction *understates* a hazard on the
data-role tree — it is not flattering to the candidate. **If the ruling is that an incomplete
enumeration of a tree nothing executes from is immaterial, `F-17(a)` becomes a PASS and Gate 1
passes on every measurement in this document.** That is a waiver on the facts, and it is Joseph's to
make. What I cannot do is record the enumeration as correct, because I measured it and it is not —
and it is the same defect class I failed `F-17(a)` on in round 6, moved from the candidate column to
the canonical column of the same sentence in the contract.

**The forward-looking cost, which is the part I would not waive silently.** `measure_m1_m6.py` is now
the *committed mechanism* for every future re-measurement, and F-17 is re-opened at every sha. A
literal detector that cannot see canonical subpaths will keep returning a clean, quiet undercount on
whichever tree still carries them — which is precisely the failure mode the instrument's own docstring
refuses 3.6.15 to avoid: *"a silent zero here is worse than the defect it is looking for."*

---

## 5. Findings recorded, not counted against Gate 1

Per the scope, these do not expand Gate 1 and are not repair authorizations.

1. **M-6's vacuity hole is open on the candidate, and no criterion requires it closed.** Measured
   first-hand: 557 lines, inventory write at `:369`, `"checked": (guard.checked if guard is not None
   else 0)`, state *WRITTEN BUT DEFAULTED*. I did **not** accept "out of scope" as the answer — I
   checked the rubric. F-5's `checked > 0` clause is its **post-rehearsal** half; F-4(a)'s
   anti-vacuity denominator is the bench count (14, satisfied); and §7.0.11 **already names this exact
   default** and prescribes the `guard_installed`/`checked_provenance`/`outcome` triple as its remedy —
   which is implemented and which I exercised in §4.1. The packet discloses the hole as open and
   unchanged; F-17(a)'s M-6 reporting obligation is discharged by that disclosure. **No existing
   criterion is breached, and I decline to create one.**
2. **F-8(a) flag.** P-6 and the subprocess enumeration reproduce exactly at `14980486` (14 / 8
   entrypoints; one child, wrapped), but the `P5-P6` document of record is still bound to `6113a34d`.
   I graded on content I measured. A stricter grader could call the filing half NOT-EVALUABLE and
   therefore a FAIL, reading **16/2**; Gate 1 fails either way.
3. **Canonical M-3's failing binding is real and unrepaired**, by design — no repair was authorized.
   Whether a historical run receipt should count as a live binding at all is the open question the
   filing raises; the checker already has a *"known pre-existing drift (submit-time provenance)"*
   allowlist that this one is not in.
4. **Two errors of mine, corrected against my own interest.** (a) My first pass ran all eight
   preambles without `MNV_LAUNCHER_DIR` and read `finalize`'s exit 2 as a ninth defect; it is required
   by A-5 and by the runbook I had already read, and with it set finalize exits 0 with `9 of 9
   CURRENT`. (b) My clean/silent arm first exited 3 because my *clone* was writable and
   `--require-readonly` correctly refused; with A-2(g) applied it exits 0. Neither was a defect in the
   candidate, and neither changed a grade.
5. **Carried forward, previously ratified by Joseph and not re-litigated here:** the 16
   interpreter-capability probes as a declared third category; `ROOT628_CONDA`'s declared system
   default as a recorded residual; the unreadable-member diagnostic wording as nonblocking.

---

## 6. The parts of this verdict most likely to be wrong

1. **Failing `F-17(a)` on a canonical-tree enumeration.** The strongest counter-argument is the one I
   made in §4.2 myself: it changes no decision, and the candidate is complete. I hold that the
   contract names both trees in one sentence and admits no partial credit — but a reasonable grader
   waives it, and Joseph is better placed than I am to weigh a reporting defect on a tree nothing
   executes from. **This single call is the difference between PASS and FAIL in this document.**
2. **Passing `F-2(a)`.** It rests on accepting the inline `for` loop as satisfying A-3 for three
   sourced libraries via pure git rather than via `verify_executing_copy_is_committed.py --pair`. That
   is the mechanism Joseph's own ruling and authorized repair item 1 prescribed ("no new helper or
   trust layer"), and I verified refusal precedes the source physically, not just textually. If the
   ruling had required literal `--pair` coverage, this would fail.
3. **Passing `F-8(a)`** where the artifacts were not re-published at the graded sha.
4. **My matched-tree suite counts (9/9) differ from the packet's (13/13).** I attribute that to
   platform and interpreter, and rest only on the *comparison*, which reproduced exactly. If the
   difference has another cause, my regression conclusion is weaker than I have stated.

---

## 7. What this verdict does and does not authorize

**Nothing.** §G is unchanged. The k=0 rehearsal is **not** launched. Gate 2 is not graded and cannot
be. `OI-136` is not closed. No member `k≠0`, no leg 6, no scientific verdict of any kind. This is a
**terminal handoff to Joseph**: I have implemented no repair, initiated none, requested no further
grader, and taken no action beyond grading.

## 8. Explicit confirmation of non-mutation

* **No Slurm job was submitted.** `squeue -u josephrb` shows exactly one job, `57275989`, submitted
  `2026-08-20T15:02:55` — three days before this session — `PENDING`. `sacct -S 2026-08-23T00:00`
  returns that same single row and nothing else.
* **No science was run**, no covariance constructed or adopted, no rehearsal started, no leg launched.
* **No scientific artifact** created, opened for write, moved, renamed or deleted. The negative
  controls used only nonexistent throwaway paths under `/tmp`; the witness directory was empty before
  and after.
* **No deployment changed.** `/pscratch/sd/j/josephrb/k0r2/clean` still `14980486`, porcelain **0**,
  **0** writable files, A-2(g) intact and demonstrated by a refused write with no residue. Canonical
  still `b2d7d4ca…` / 722 dirty, unchanged. All mutation controls ran on `/tmp` clones.
* **No repository edit, commit, push or merge.** Primary checkout still `d3a63bbc`, porcelain exactly
  the two pre-existing untracked files, untouched. All three detached worktrees porcelain **0** and
  removed.
* **`set -u` was neither added nor invoked.** Cluster writes confined to `/tmp`.

---

*Terminal Gate-1 regrade. PRE-SUBMISSION column only.*
**GATE 1 DOES NOT PASS. Failed criterion: `F-17(a)`.**
*Handed to Joseph. No repair implemented or initiated; no further grader requested.*
