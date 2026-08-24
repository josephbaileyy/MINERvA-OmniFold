# RECEIPT — F-8(a), F-9, F-12 and F-17(a) filed at the restored candidate `aa67c426`

**CITABLE FOR:** the four measurements below, taken 2026-08-24 against the deployed candidate
`/pscratch/sd/j/josephrb/k0r2/clean` at `aa67c426` and against the canonical checkout
`/pscratch/sd/j/josephrb/MINERvA-OmniFold`, with the commands and their full output.

**NOT CITABLE FOR:** a Gate-1 pass, and not for any `sbatch` authorization. **I am the builder. This
receipt produces evidence; it does not grade it.** F-18 separates those lanes and round 11's grader
declined to produce this capture for exactly that reason. Gate 1 stood at **14 PASS / 4 FAIL** when
this work began and only a fresh non-builder can move it.

**Authorization:** Joseph, 2026-08-24 — *"Close the remaining findings."* No new candidate sha was
required: all four are filing acts or a single cluster invocation, and none touches a tracked
`*.py`/`*.sh`, so the A-2(f) listing digest `fa3489e2…` is untouched and the docs-only invariant
holds.

---

## 1. F-8(a) — P-6's ENUMERATION RE-RUN, AND P-5's BLIND SPOTS

### 1.1 The population, named before the command

**The eight k=0 launchers**, all present at `aa67c426`: `sbatch_bootstrap_5d_gpu.sh`,
`sbatch_finalize_5d_bkgaware_gpu.sh`, `sbatch_seedscan_split_5d.sh`,
`sbatch_sweep_bank_5d_run_bkgaware_gpu.sh`, `sbatch_unfold_5d_detector_bkgaware_gpu.sh`,
`sbatch_uthrow_block_5d.sh`, `sbatch_uthrow_combine_5d_fast.sh`, `sbatch_uthrow_run_5d_fast.sh`.

**Stated because I got it wrong first:** `nd-unfolding/sbatch_*.sh` is **not** this set — the glob
matches the 4D, FPS and PET-era launchers too. A glob is not a population.

### 1.2 The command, verbatim from the contract, and its counts

```
$ grep -nE 'python[0-9]*\s|\.py' <each of the eight launchers>
   matching lines, comments INCLUDED : 171
   matching lines, comments filtered : 114
```

Comment filter: drop lines whose first non-space character is `#`.

**BOTH ALTERNATIVES OF THE PATTERN, separately, because the contract's regex is a disjunction and a
single total hides which half matched:**

```
python[0-9]*\s  alternative, comments filtered :  46 lines
\.py            alternative, comments filtered :  82 lines
either                                          : 114 lines   (46+82 > 114: they overlap)
```

**RAW AND COLLAPSED OUTPUT PUBLISHED SEPARATELY, because they differ by more than a factor of two and
a reader given only one of them gets the wrong number:**

```
.py-shaped tokens in the filtered lines, RAW              : 101
distinct tokens, NOT path-collapsed                       :  27   <- what a naive sort -u gives
distinct FILES after collapsing to basenames              :  12   <- the answer
```

The 27 is inflated by path-prefix duplicates of the *same file*: `adopt_unified_5d.py`,
`nd-unfolding/adopt_unified_5d.py` and `/nd-unfolding/adopt_unified_5d.py` are one file written three
ways, and the same triple occurs for eleven others. **27 is not a count of files and must not be
quoted as one.** Raised by the round-11 grader against its own instrument, which used the same
extraction.

### 1.3 Distinct `.py` basenames in the filtered set, with occurrence counts

```
  24  verify_executing_copy_is_committed.py     <- integrity tool
  24  mnv_source_manifest.py                    <- integrity tool
  16  mnv_guarded_run.py                        <- the guard
  10  unified_throw_cov_5d.py
   4  unfold_nd_omnifold_unbinned.py
   4  mii_adopt_unified_5d_stamped.py
   4  combine_cov_nd.py
   3  sweep_bank_5d.py
   3  seedscan_split.py
   3  bootstrap_nd.py
   3  analyze_universes_5d.py
   3  adopt_unified_5d.py
  -- 12 distinct
```

### 1.4 THE RECONCILIATION, which is the part the clause is actually about

**12 distinct, and the contract claims nine.** The difference is exactly the three integrity tools —
the two preflight tools and the guard — which are not science entrypoints. Removing them leaves
**nine**, and they are the same nine, name for name, as the M-1 table:

`unified_throw_cov_5d.py`, `unfold_nd_omnifold_unbinned.py`, `mii_adopt_unified_5d_stamped.py`,
`combine_cov_nd.py`, `sweep_bank_5d.py`, `seedscan_split.py`, `bootstrap_nd.py`,
`analyze_universes_5d.py`, `adopt_unified_5d.py`.

**`unified_throw_cov.py` is deliberately not in the nine** — it is imported, not launched, and M-1
carries it as a tenth row on that basis. It appears in none of the eight launchers.

**A null result from that grep would be evidence about the grep**, so: the grep is not null, it
returns 114 filtered lines, and its positive control is that it finds every one of the nine.

### 1.5 INVOCATIONS ARE A DIFFERENT CLASS FROM LINES, and both are stated

The counts in §1.3 are **line occurrences**. They are not invocation counts and must not be quoted as
such. Measured separately, in command position:

| class | count | how |
|---|---|---|
| guarded science invocations | **14** | `python3 "$GUARD"` in command position |
| `GUARD=` assignments | 8 | one per launcher — this is why the *line* count for the guard is 16, not 14 |
| preflight-tool invocations | **16** | `python3 "$SRCMAN"` / `"$PARITY"` in command position |

`14 + 16 = 30`, which is ruling 21's boundary reproduced independently at this sha.

**The tool that owns this census, run at the paperwork tip:**

```
$ python3 nd-unfolding/mnv_preflight_census.py
[preflight-census] 8 launcher(s): 14 guarded + 16 declared-preflight + 16 interpreter-probe
                   + 0 unclassified = 46 non-comment python3 invocation(s); 18 commented out
[preflight-census] OK: every python3 invocation is guarded or declared
rc=0
```

### 1.6 P-5 — THE BLIND SPOTS, IN MY OWN WORDS

The inventory cannot see four things, and none of them is closed here:

1. **Namespace packages.** `spec.origin` is `None` for them and `find_spec` returns before
   `checkout_root_of` is reached, so a namespace portion resolving from the wrong checkout is **not
   refused**. `nd-unfolding/` and `2d-unfolding/` both contain `__init__.py`-less directories with
   ordinary-word names — `tests`, `products`, `mii`, `pet`, `uq`, `seedscan`. A regular module in any
   later `sys.path` entry outranks a namespace portion, so this is a **narrow** hole. It is still a
   hole and it is **not measured**.
2. **Modules already in `sys.modules`** when `install()` runs — the wrapper's own `argparse`, `os`,
   `pathlib`, `runpy`, `sys`. They were imported before the guard existed and are invisible to it.
3. **Anything in a further subprocess.** Enumerated below.
4. **The `.sh` route entirely** (B-5). Nothing in this receipt speaks to it.

### 1.7 The subprocess enumeration, with every child dispositioned

```
$ grep -n "subprocess\.\(run\|call\|Popen\)\|os\.system\|os\.exec" <the nine entrypoints>
mii_adopt_unified_5d_stamped.py:788:    rc = subprocess.call(argv_child)
  -- 1 matching line across all nine
```

| child | disposition |
|---|---|
| `mii_adopt_unified_5d_stamped.py:788` → `adopt_unified_5d.py` | **COVERED** — the child is *separately* wrapped, via `--guard-expect-root`/`--guard-inventory` on the `build_child_argv` template. Demonstrated live in §3.2's paired arm, whose record shows `checked=9` in the parent. |

**Every other entrypoint spawns nothing**, so there is no second child to wrap or to record as
uncovered. `unified_throw_cov.py` and `compare_unified_throw.py` were checked separately and also
return zero. **One child, covered; zero uncovered ACROSS THE ENTRYPOINT SET**, which is the population
P-5's command names.

> **⚠ SCOPE CORRECTED 2026-08-24 by the round-12 lane. The search was right; the SENTENCE was wider
> than the search.** As first written this said *"one child, covered; zero uncovered"* full stop, which
> reads as a statement about the whole import closure. It is not. A **closure-wide** search finds a
> second subprocess: **`nd-unfolding/seed_offset_policy.py:420`**, which is
> `subprocess.run(["git", "-C", repo_root, "ls-files", …])`. `seed_offset_policy.py` is a closure member,
> not an entrypoint, so it is outside P-5's stated population and outside what I searched.
>
> **It is harmless, and for a reason that is a measurement rather than a judgement: the child is `git`,
> not an interpreter.** A `git ls-files` subprocess cannot resolve a Python import, so the guard's
> subprocess blind spot — which is about *import* resolution in a child interpreter — does not reach
> it. Nothing changes in the disposition.
>
> **What was wrong was the claim's scope, and that is the exact error this campaign keeps making**:
> state the population beside the number, and scope the CLAIM to what was searched rather than widening
> the search until the sentence becomes true. Third form of it in this document alone — the census
> population, the P-6 raw-versus-collapsed count, and now this.

---

## 2. F-9 — N-1 PERFORMED, GRADED AGAINST §7.0.11's SIX ROWS

Run at **`/pscratch/sd/j/josephrb/k0r2/n1-20260824b`** — the second pass. The first pass
(`…-20260824`) is retained unaltered; it established the same six rows but **recorded no exit status
anywhere in its evidence directory**, which the round-11 grader found and which is a real gap: 9.1's
settlement column is *"the process's own status, captured unpiped"*, and a status that exists only in
a message is not an artifact. `status/EXIT-STATUSES.txt` now carries them, written by the shell that
ran the arms:

```
# N-1 arm exit statuses, written by the shell that ran them, unpiped (O-4)
# tree=/pscratch/sd/j/josephrb/k0r2/clean sha=aa67c426…  utc=2026-08-24T12:26:58Z
armN1=3        armU=1        armUp=1        armU_origin=0
``` The **real, unmodified**
`mii_adopt_unified_5d_stamped.py` from the canonical checkout, under the candidate's own
`mnv_guarded_run.py` — the tree that carries B-4 — with `--expect-root ${MNV_CODE_ROOT}`.
`--uthrow/--combined/--out` all throwaway. **No `--allow` on any arm.** Interpreter
`/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3` 3.11.14 with `ROOT 6.28/12`, from
`source ./setup_salloc_env.sh` — **not piped**, which is the trap that cost the first attempt in
August.

| # | requirement | measured | verdict |
|---|---|---|---|
| 9.1 | exit **3**, through B-4 | `rc=3`, captured into `RC_N1=$?` immediately, unpiped | **MET** |
| 9.2 | `outcome` exactly `refused:script-outside-expect-root`, verdict never empty/green | `outcome=refused:script-outside-expect-root`; verdict `REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT --expect-root; nothing was imported because nothing was run` | **MET** |
| 9.3 | names the script, the canonical root, the expected clean root | `script=…/MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py`; `script_checkout_root=/pscratch/sd/j/josephrb/MINERvA-OmniFold`; `expect_root=/pscratch/sd/j/josephrb/k0r2/clean` | **MET** |
| 9.4 | `checked == 0` **and** `guard_installed == false`, together | `checked=0`, `guard_installed=False` | **MET** |
| 9.5 | O-1…O-4, no child marker and no output | marker count **0**; `[adopt5d]` **0**; `--out` fails `test -e`; `witness_N1` `[]` before **and** after | **MET** |
| 9.6 | `seed_offset_policy` neither required nor expected — a consequence, not a string check | absent, and 9.4's triple is why: no guard, nothing imported. Read as a consequence; the token was not grepped for as a criterion | **MET** |

**The `checked=0` inversion applies and is deliberate.** Everywhere else an empty inspection set is
the vacuity trap; here a **non-zero** `checked` would mean containment did not fire first and the arm
was measuring something else.

### 2.1 The refused arm's full merged stream (O-3), which is the entire content

```
[oi136] SCRIPT OUTSIDE THE EXPECTED TREE -- REFUSING BEFORE THE FIRST IMPORT.
[oi136]   script        /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py
[oi136]   which is in   /pscratch/sd/j/josephrb/MINERvA-OmniFold
[oi136]   expected      /pscratch/sd/j/josephrb/k0r2/clean
[oi136] The file that EXECUTES is not the file that was approved. An entrypoint with
[oi136] no repository imports gives this guard nothing to resolve, so without this
[oi136] check it would have exited 0 while running the wrong tree's copy. --allow
[oi136] does not cover this: it declares an IMPORT tree, never an execution tree.

[oi136] inventory: checked=0 repo_origin_count=0 outside_expect_root=0
        verdict=REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT --expect-root;
        nothing was imported because nothing was run
```

---

## 3. F-12(N-1) — THE NON-VACUITY ANCHOR, ALL THREE LIMBS

Each arm wrote its **own** inventory and its **own** capture file. That is structural, not care:
a single combined capture would put U′'s naming of `seed_offset_policy` into the same file as the
refused arm, which is the one way the token realistically appears beside a refusal.

### 3.1 (i) the fixture really is misplaced

From the refused arm's own record, on the path the guard **computed**, never the command line as
typed: `script_checkout_root = /pscratch/sd/j/josephrb/MINERvA-OmniFold` ≠
`expect_root = /pscratch/sd/j/josephrb/k0r2/clean`. **MET.**

### 3.2 (ii) the arm can succeed — the O-1 paired arm

Same real wrapper, same launch directory, `--expect-root` naming the canonical checkout it was
launched from. `--expect-root` is not `--allow`; `--allow` is empty on every arm.

```
rc=1
[remedyA] running the PINNED writer as a subprocess:      <- PRESENT (the O-1 discriminator)
expect_root          = /pscratch/sd/j/josephrb/MINERvA-OmniFold
script_checkout_root = /pscratch/sd/j/josephrb/MINERvA-OmniFold      (equal, as the arm requires)
guard_installed      = True
checked              = 9
verdict              = REPOSITORY-ORIGINS-INSPECTED
outcome              = child-systemexit: '[FAIL] the pinned writer exited 1; nothing is stamped…'
```

The arm reaches the marker and does not refuse, which is what (ii) asks. **MET — and see finding
F-2 below, because the exit code does not match the contract's table and I believe the table is the
part that is wrong.**

### 3.3 (iii) counterfactual origin — MY FIRST FILING CITED THE WRONG ARM

**The error, stated before the repair.** I filed this limb from `invUp/armUp.jsonl` and called it
*"the U′ record"*. It is not: it has `guard_installed=True`, `checked=9`,
`expect_root=/pscratch/…/MINERvA-OmniFold` and `refusal_site=None` — **that is the O-1 PAIRED arm**,
which §7.0.11's three-arm table marks *"may; not graded"* for this column, and §7.0.11 says the U/U′
arm *"discharges F-12(N-1)(iii) and nothing else."* Substituting the paired arm is exactly what the
table forbids. In the first pass `seed_offset_policy` appeared in **one artifact in the whole
directory**, and it was the wrong one. Found by the round-11 grader from per-file counts, not from my
summary.

**Why I made it:** the 2026-08-22 receipt uses that shape and calls its guarded arm "U′", reading the
contract's *"read it from an unguarded inventory run"* as satisfied by a guard that refuses nothing.
§7.0.11 supersedes that, and I inherited the older reading without re-checking it against the current
rubric — which is the same lane carrying a prior artifact's framing forward that §5's own findings
warn about.

**The repair, on the genuinely unguarded arm, with TWO instruments and NO code modified:**

*Instrument A — the real, unmodified binary under `python3 -v`*, which emits the resolved origin of
every import. No guard, no inventory, no edit:

```
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/__pycache__/seed_offset_policy.cpython-311.pyc
  matches /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/seed_offset_policy.py
```

*Instrument B — an independent direct probe*, same cwd, same resolution order, unguarded, `rc=0`:

```
U-ORIGIN /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/seed_offset_policy.py
```

`invU/` holds **0 entries**, which is what the three-arm table requires of this arm (*"no record
exists"*). Two instruments because the first reads a `.pyc` mapping and the second reads `__file__`
directly; they agree on the tree, which is the claim. **MET.**

**IT IS NOT the mechanism of the F-9 refusal** and cannot be cited for 9.1–9.5. Both halves stated
together, as ruling 20 requires.

### 3.4 TWO FIELDS THAT MAKE THE HARD DISTINCTIONS MECHANICAL

Not required by the clause, and worth naming because they replace an inference with a field:

- `refusal_site='b4-script-containment'` on the refused arm — the control names its *intended*
  refusal site, so it can notice if an earlier site starts short-circuiting it. `None` on the paired
  arm.
- `checked_provenance='not-measured-no-guard-was-installed'` vs `'measured-by-installed-guard'` —
  this makes §7.0.11's defaulted-zero-versus-measured-zero distinction a **field** rather than a
  reader's inference. A bare `checked=0` cannot say which world produced it; this can.

### 3.5 A CAUTION FOR A LATER READER, AND ONE OBSERVATION IN THE ARMS' FAVOUR

**O-3 interleaving.** In `armU.log` and `armUp.log` the child's traceback appears *before*
`[remedyA]`, because stdout and stderr interleave unbuffered into one file. **The causal order is the
reverse.** It does not affect grading — O-3 governs the exit-3 arms and `armN1` has no child — but the
order is misleading on its face.

**`armU` and `armUp` fail IDENTICALLY downstream** — same `TFile::ReadBuffer`, same traceback at
`adopt_unified_5d.py:88`, same `[FAIL]`. That is direct evidence for what F-12(N-1)(ii) exists to
establish: the difference between the refused arm and the others is **containment, not breakage**.
An exit 0 would have established this less directly than two identical downstream failures do.
Observed by the round-11 grader; I had not claimed it.

### 3.6 A LINE IN THE PAIRED-ARM CAPTURE THAT READS AS AN F-6(a) VIOLATION AND IS NOT

**Annotated because the artifact really does say it, which is what makes the false reading durable.**
`cap/armUp.log` prints:

```
[remedyA] running the PINNED writer as a subprocess: …/python3
  /pscratch/…/MINERvA-OmniFold/nd-unfolding/adopt_unified_5d.py --uthrow … --combined … --out …
```

**No guard, no `--expect-root`, no `--inventory`.** A later reader would reasonably conclude *"the
pinned-writer child runs unguarded in production"*. That is **false**, and the reason is that N-1
executes the **canonical** copy by design:

| tree | `mii_adopt_unified_5d_stamped.py` sha256 | `--guard-expect-root` | `CHILD_GUARD` |
|---|---|---|---|
| canonical checkout | `fc520bfd09a5…` | **0** | **0** |
| code root (`aa67c426`) | `e5bc51a4d482…` | **2** | **2** |

**The canonical copy has no child-guard routing at all**, so the bare child argv is a property of the
wrong-tree copy, not of the graded tree. The code-root copy additionally *refuses* rather than
defaulting — `:776-777` fails when neither `--guard-expect-root` nor `$MNV_CODE_ROOT` resolves,
because *"a default would be the hardcode wearing a flag, and an empty one would guard against
nothing."* **F-6(a) is unaffected and stands.**

This is the same discipline the rubric already imposes on F-9 — *"grade against the tree that carries
B-4, and say which one"* — applied to the paired arm, which had no equivalent sentence. Identified by
the round-11 grader, which chased it precisely because it appeared to contradict a clause it had been
passing since round 11.

**The cross-tree digest difference belongs in F-17(a)'s M-4 column too**: M-4 recorded four files as
digest-identical between canonical and `main`, and this wrapper now differs between canonical and the
**code root** because the code root carries this campaign's repairs. Expected drift — but it is
precisely the difference that makes the annotation above necessary, so it is reported rather than left
for the next lane to rediscover.

---

## 4. F-17(a) — M-1…M-6 RE-MEASURED ON BOTH TREES, WITH DIFFERENCES REPORTED AS FINDINGS

Instrument `docs/orchestration/measure_m1_m6.py`, interpreter 3.11.14, `--tree` given explicitly on
both runs because that tool takes no default *"deliberately"*. Baseline for comparison:
`MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md` as it stands at `aa67c426`.

**The canonical run took BETWEEN 42 AND 47 MINUTES.** Stated as a bracket because that is what was
measured: `ps -o etime` showed it alive at **41:55**, and at the next observation it was gone with its
output complete. **A first draft of this line said "43 minutes", which is a number I never measured** —
it sat inside the bracket and read as precise. Corrected on the same principle the rest of this receipt
applies to other people's figures.

The baseline records M-3 on that tree as *"roughly 30 minutes"*; the round-11 grader's attempt never
returned and it could not say why. **That is the why** — the full six-measure run on the canonical tree
exceeds the M-3 stage alone by enough to outlast a patient wait — and it is worth having on the record
as a duration rather than as an unexplained timeout.

**A defect in my own waiter, recorded because it is the day's recurring shape.** The wait script
printed `=== canonical run no longer in the process table ===` **unconditionally after its loop**,
including on the give-up path where it had just printed `WAITER GAVE UP; process may still be running`.
Two contradictory claims in consecutive lines, one of them asserting something the code had not
established. Harmless here — the run really had finished, and its capture agrees with §4.2 on every
value — but it is a message stating more than its own control flow supports, which is the same class as
a status that exists only in a message and a bar that reads as a measurement.

### 4.1 CANDIDATE — `/pscratch/sd/j/josephrb/k0r2/clean` at `aa67c426`

M-1, ten rows, **matches the filed baseline exactly — every literal, every insert line, every count**:

| entrypoint | literal | first insert | repo modules after |
|---|---|---|---|
| `bootstrap_nd.py` | — | :28 | 3 |
| `seedscan_split.py` | — | :37 | 3 |
| `unified_throw_cov.py` | `_DATA_ROOT` @:69 (exact) | :61 | 5 |
| `unified_throw_cov_5d.py` | — | :42 | 3 |
| `unfold_nd_omnifold_unbinned.py` | `_DATA_ROOT` @:73 (exact) | :77 | 4 |
| `sweep_bank_5d.py` | `_DATA_ROOT` @:59 (exact) | :51 | 6 |
| `combine_cov_nd.py` | — | none | 0 |
| `analyze_universes_5d.py` | — | none | 0 |
| `mii_adopt_unified_5d_stamped.py` | — | :149 | 2 |
| `adopt_unified_5d.py` | `_REPO` @:35 (exact) | :38 | **0** |

```
M-2  importable=127  stdlib_collisions=0  py=3.11.14
M-3  present=True  rc=0  all_intact=True
     -> 133 bindings resolved, 132 OK, 1 disclosed pre-existing drift, ALL BINDINGS INTACT
M-4  is_git=True  head=aa67c426…  dirty=0  untracked=0  modified=0
M-5  n=8  missing=[]  repo_assign=[]  activator_from_env_root=[all 8]
M-6  present=True  n_lines=557  WRITTEN BUT DEFAULTED
```

### 4.2 CANONICAL CHECKOUT — `/pscratch/sd/j/josephrb/MINERvA-OmniFold`

**Seven surviving literals, none `_DATA_ROOT`** — the unrepaired world, and it matches the baseline's
canonical table row for row including the two **subpath** forms that an exact-equality instrument
could not see and that round-7 `F-17(a)` was failed for missing:

| file | literal | form | insert | repo modules after |
|---|---|---|---|---|
| `bootstrap_nd.py` | `_ND` @:10 | **subpath** | :11 | 3 |
| `seedscan_split.py` | `_ND` @:21 | **subpath** | :23 | 3 |
| `unified_throw_cov.py` | `_REPO` @:42 | exact | :45 | 5 |
| `unified_throw_cov_5d.py` | `_REPO` @:24 | exact | :27 | 3 |
| `unfold_nd_omnifold_unbinned.py` | `_REPO` @:47 | exact | :52 | 4 |
| `sweep_bank_5d.py` | `_REPO` @:32 | exact | :35 | 6 |
| `adopt_unified_5d.py` | `_REPO` @:35 | exact | :38 | **0** |

```
M-2  importable=125  stdlib_collisions=0
M-3  present=True  rc=1  all_intact=FALSE
M-4  is_git=True  head=b2d7d4ca…  dirty=722  untracked=718  modified=4
M-5  n=8  repo_assign=[ALL EIGHT]  activator_from_code_root=[]  activator_from_env_root=[]
M-6  present=True  n_lines=281  NO INVENTORY WRITE
     -> "the guard counts but emits nothing; the vacuity question cannot even be asked of this tree"
```

### 4.3 THE DIFFERENCE TABLE — what F-17(a) actually asks for

| # | measure | candidate | canonical | difference from the FILED baseline |
|---|---|---|---|---|
| M-1 | literals | 4 (3 `_DATA_ROOT` + 1 inert `_REPO`) | 7 (5 exact + 2 subpath) | **none** — both tables reproduce row for row |
| M-2 | importable names | 127 | 125 | **none**; the 2 are the candidate's two new test files |
| M-3 | hash bindings | rc=0 INTACT | **rc=1 NOT intact** | **none** — the canonical failure is a stale untracked PET run receipt that cannot exist on the candidate |
| M-4 | git state | `aa67c426`, dirty 0 | `b2d7d4ca`, dirty **722** = 718 `??` + 4 ` M` | **DIFFERS: baseline recorded 721 = 717 + 4** |
| M-5 | `.sh` root assignment | **0 of 8** | **8 of 8** | **none**; reported both ways |
| M-6 | guard evidence | WRITTEN BUT DEFAULTED | NO INVENTORY WRITE | **none** |

**THE ONE DIFFERENCE, IDENTIFIED RATHER THAN LEFT AS A DELTA.** M-4's canonical untracked count moved
**717 → 718**. The single added path is `nd-unfolding/pet/log_fe_nominal_nominal.txt`, 51 B, mtime
**2026-08-24 04:50:08** — a PET lane's log. **It is not this work's**: the N-1 arms ran at 05:17 and
05:26, and zero `.pyc` anywhere under canonical is newer than 90 minutes (see FINDING 8). A live tree
that other lanes write to will keep doing this; the number is a snapshot, not an invariant.

### 4.4 TWO CROSS-TREE FACTS THAT BELONG HERE AND WOULD OTHERWISE BE REDISCOVERED

**M-4, wrapper digest.** `mii_adopt_unified_5d_stamped.py` differs between the trees —
canonical `fc520bfd09a5…` with `--guard-expect-root` and `CHILD_GUARD` counts of **0/0**, code root
`e5bc51a4d482…` with **2/2**. Expected drift, since the code root carries this campaign's repairs. It
is also exactly what makes §3.6's annotation necessary, so it is reported rather than assumed benign.

**M-2, shared scope with the closure index.** M-2's **127** importable names on the code root is the
*same population* as the narrow index of §6's closure (`nd-unfolding` + `2d-unfolding`), which also
gives 127 and which excludes `unbinned_unfolding/python`. That is a coincidence of construction, not
of arithmetic: **anyone widening one must widen the other**, or the two will silently disagree about
the same tree. Observed by the round-11 grader.

### 4.5 THE PERISHABLE PARTS, NAMED SO THEY ARE NOT INHERITED

- **M-4's canonical `dirty` count is falsified by any lane touching that tree**, and was, twice, in the
  two days between the baseline and this filing.
- **M-2's claim over the untracked set is the one the contract flags as perishable**, and it is
  re-tested here rather than carried.
- **M-1's ten rows are not eleven.** `compare_unified_throw.py` is absent from the instrument, is
  inside the import closure at depth 2, and is the file whose hardcode stopped legs 5a/5b. See
  FINDING 1 — the instrument fix needs a new candidate sha and is deferred, disclosed, and outside §F.

---

## 5. FINDINGS — reported as findings, which is what F-17(a) asks for, rather than repaired here

### FINDING 1 — M-1 IS A DEPTH-1 INSTRUMENT AND THE VIOLATION THAT STOPPED THE REHEARSAL WAS AT DEPTH 2

`docs/orchestration/measure_m1_m6.py`'s M-1 enumerates the **ten** files of the M-1 table.
`nd-unfolding/compare_unified_throw.py` is not one of them — `grep -c 'compare_unified_throw'` over
the instrument returns **0** — and that is the file whose hardcoded `sys.path.insert(0, …)` refused
legs 5a/5b at runtime and cost the k=0 rehearsal.

**Why it is invisible, stated as a mechanism.** M-1 walks the entrypoints and, for each, lists the
repository modules imported after the rooted insert. `unified_throw_cov.py`'s row **already names
`compare_unified_throw`** as one of its five. So the module is *named as an import* and never *given
its own row*, which is the only place its own insert would be inspected. The instrument stops at
depth 1; the violation was at depth 2.

**This is the second instance of the same shape, and the first was fixed by adding a row.** The
baseline filing calls `unified_throw_cov.py` *"the tenth row and the one that was missing"* — that
was a depth-1 omission, caught and repaired. `compare_unified_throw.py` is the eleventh row, one
level deeper, and still missing.

**Not repaired here, and the reason is structural rather than a choice.** `measure_m1_m6.py` is a
tracked `.py` inside the 782-file source manifest (89 of the 782 are under `docs/`). Editing it above
`aa67c426` changes the A-2(f) listing digest `fa3489e2…` and puts a `.py` into a range this whole
arrangement requires to be docs-only. **The binding constraint is the DIGEST, not the count** — a
modification is count-neutral, so the declaration's *"falsified by any add or removal, and by nothing
else"* clause would not fire while A-2(f) would. Closing it needs a new candidate sha. **No clause in
§F requires the instrument to be transitive**, so F-17(a) is dischargeable with this carried as a
disclosed finding — which is what the clause's own *"differences reported as findings"* provides for.

### FINDING 2 — §7.0.11's PAIRED-ARM CELL IS UNREACHABLE UNDER §5's OWN CONSTRAINT

The three-arm table requires the O-1 paired arm to exit **0** with `outcome=ok`. Measured: **exit 1**,
`outcome=child-systemexit`, marker present, `guard_installed=true`, `checked=9`,
`verdict=REPOSITORY-ORIGINS-INSPECTED`.

The cause is not the arm. N-1 **mandates** throwaway `--uthrow/--combined/--out` paths — *"never the
defaults; the defaults name real archive products"* — and a zero-byte throwaway makes the child fail
inside `TFile::ReadBuffer`, downstream of everything the arm establishes. **So exit 0 on that arm is
unreachable without feeding it real archive inputs, which §5 forbids.** The 2026-08-22 receipt
recorded the same `rc=1` on its unguarded arm and treated it as downstream.

F-12(N-1)(ii) asks whether the arm *"can succeed"* and names the `[remedyA]` marker as the
discriminator, which it reaches. I read the requirement as met and the table's `0`/`ok` cell as having
been measured on a fixture with valid inputs. **I did not manufacture valid ROOT inputs to force a
zero**, because that starts real adopt work on a path Joseph has prohibited. Whether the cell or the
arm is wrong is the grader's call, not mine.

### FINDING 3 — A CENSUS FIELD NAMED "invocations" COUNTS LINES

`mnv_preflight_census.py` reports `46 non-comment python3 invocation(s)`. The unit is **lines
carrying at least one invocation**. The probe failure branch —
`echo "[preflight]   $(command -v python3 …): $(python3 -V …)"` — carries **two** invocations and the
census counts it once (`per_launcher: 2`, not 3). A true invocation count is **≥54**, treating 54 as a
floor because the 16 probe lines were audited for multiplicity and the other 30 lines were not.
Nothing downstream breaks — ruling 21's boundary is about *which* invocations are guarded and the
classification is unaffected — but **46 must be quoted as lines, not invocations.** Found by the
round-11 grader against its own figure.

### FINDING 4 — A CORRECTED POPULATION PAIR, BECAUSE THE DIGITS WERE RIGHT AND THE SENTENCE WAS NOT

The claim in circulation was *"the preflight exclusion population Joseph ruled on at 30 is now 46."*
**That sentence names a quantity that never existed.** Ruling 21's 30 is `14 guarded + 16 excluded` —
the **total** non-comment population. The exclusion he ruled on was **16**. Correctly:

| | ruled on | now |
|---|---|---|
| TOTAL non-comment population | 30 | **46** |
| EXCLUDED subset | 16 | **32** (16 preflight + 16 interpreter-probe) |

This is the same defect class as the round-10 census headline — *"53 repository-wide on the deployed
candidate"* — where the digit was reproducible and the population sentence was false. **Two lanes made
it in the same session, in opposite directions.** My own contribution to the confusion was measuring
`python3 -c` only, which returns **8**, and offering a coincidental 46 in M-3's output (46 unpaired
receipt role keys denoting repo code) as a possible source. That hypothesis was wrong. The
`per_launcher: 2` declaration is the real explanation.

### FINDING 5 — THE CANDIDATE BRANCH CARRIED A SUPERSEDED RUBRIC — **CLOSED, AND THIS ENTRY WAS STALE THE MOMENT IT WAS FILED**

> **⚠ THE TEXT BELOW WAS TRUE WHEN DRAFTED AND FALSE WHEN COMMITTED. FOURTH INSTANCE OF THIS CLASS IN
> THREE DAYS, AND THE WORST OF THE FOUR.** It says the branch's rubric *"is 575 lines (`cf53f587`)"*.
> At `30ec0707` — the commit that files this very receipt — that path is blob
> `e2b952075205a4383fcc99811692add83bce8ef9`, **1160 lines**, sha256 `e0fb342b…`. **The disposition
> the finding asks for was already actioned**: an independent non-builder lane synced it at
> `b2075558`, which `git merge-base --is-ancestor` confirms is an **ancestor of `30ec0707`**. So the
> finding is **CLOSED**, not wrong — but it was filed describing a world its own commit had already
> left.
>
> **The check that would have caught it is one command on one path**, and it names the answer:
> `git log --oneline 30ec0707 -- docs/orchestration/REVIEW-CONTRACT-…md` → `b2075558 Sync k=0 rubric
> on the build branch to main's copy, byte for byte`. **The correction was upstream in its own
> history.** The first three instances of this class needed a re-measurement on the cluster or a
> peer's grep; this one needed a `git log` on the path I was writing about.
>
> **And `CLAUDE.md:8` instructs exactly this** — *"before quoting, writing, computing, or deciding a
> gate, open the routed canonical artifact and re-measure volatile fields."* The rule was loaded into
> context for the whole session. **The mechanism is that I re-measure when I MEASURE and not when I
> FILE**: every number in §1–§4 was measured minutes before commit, and this one was drafted hours
> before it and never re-read against the tree. A receipt is committed at one instant and drafted over
> many, so **every factual sentence needs its truth checked at the commit, not at the keystroke.**
> Found by the round-11 grader.

**The finding as originally filed, retained verbatim:**

`docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md` is **575 lines**
(`cf53f587`) on `build-k0-execution-integrity` and **1160 lines** (`e2b95207`) on `main`. Rounds 10
and 11 were graded against `main`'s. The branch copy is missing §7.0.11, §7.0.12 and §7.0.13 — the
restatements F-9 and F-12 are now graded by.

**I am not syncing it.** A builder editing the contract it is graded against is a conflict of
interest even when the edit is a pure copy from `main`. Flagged for Joseph or a non-builder lane.

**DISPOSITION, added at the annotation above:** Joseph authorized delegation; an independent lane
landed it at `b2075558` with blob `e2b95207…` matching `main` exactly, verified on both the local ref
and origin, `--check` rc=0, no force-push, `d268a95b`/`35777aad`/`aa67c426` all still ancestors. That
lane also established the stronger non-destructiveness result my own `comm -23` set comparison could
not: the old copy is an exact **ordered subsequence** of the new one, 576/576 lines in order, **585
added, 0 deleted, 0 modified**. And it retired a caveat that headed both of the round-10 and round-11
verdicts — *"grade by digest, not by branch"* — so §7.0.11/12/13 are now present on the candidate
itself.

### FINDING 6 — `setup_salloc_env.sh` SOURCES TWO FILES THAT NO CONFORMING CLONE CAN CONTAIN, AND THE OBVIOUS FIX IS THE HAZARD

My own `cap/env.log` carries two errors that no previous filing has mentioned:

```
./setup_salloc_env.sh: line 18: /pscratch/…/k0r2/clean/unbinned_unfolding/build/setup.sh: No such file or directory
./setup_salloc_env.sh: line 21: /pscratch/…/k0r2/clean/MINERvA101/opt/bin/setup.sh: No such file or directory
```

`SCRIPT_DIR` derives from `BASH_SOURCE`, so sourced from the code root both paths resolve **into** the
code root. Measured: both files are **absent from the code root, present in canonical, and neither is
tracked** — `.gitignore` carries `unbinned_unfolding/**` and `MINERvA101/**` with narrow re-includes
that do not cover either `setup.sh`. **So no A-2-satisfying clone can ever contain them.** `source` of
a missing file warns and continues, and the launchers deliberately carry no `set -e`/`set -u`, so the
activation is **partial and fails silently**. conda still succeeds because `ROOT628_PREFIX` lives
under `$HOME`, independent of `SCRIPT_DIR` — which is why the N-1 child could `import ROOT` at all.

**THE TRAP, and it is why this is filed rather than fixed.** The canonical copy of
`unbinned_unfolding/build/setup.sh` hardcodes the canonical root into three variables:

```
export PATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build:${PATH}
export PYTHONPATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build:${PYTHONPATH}
export LD_LIBRARY_PATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build:${LD_LIBRARY_PATH}
```

**Copying that file into the code root — the first repair a reasonable person reaches for — would
install a canonical-root `PYTHONPATH` and `LD_LIBRARY_PATH` into the approved clean tree**, on the
`.sh`/environment side that B-5 says no Python guard reaches. **Do not copy it.** Derive the three
from `MNV_CODE_ROOT` or set them explicitly. Flagged by the round-11 grader.

**DOES ANY k=0 ENTRYPOINT NEED IT? MEASURED: NO.** `unbinned_unfolding/build` provides exactly **one**
importable name, `libRooUnfold` (a `.so`), and **no** k=0 file imports it — checked by AST over all
nine entrypoints plus `unified_throw_cov.py` and `compare_unified_throw.py`. RooUnfold is the legacy
binned path, not OmniFold. Live (non-comment) references to `unbinned_unfolding` across the eight
launchers: **0**. The only references are **comments that already document the exclusion**, in the
launchers' own words: *"`.gitignore` excludes `unbinned_unfolding/**` and `MINERvA101/**`, so a clone
satisfying A-2 …"*.

**So the two errors are structural and expected, not a deployment defect** — and this belongs in
F-8(a)'s P-5 inventory as the first concrete instance of the *"`.sh` route entirely (B-5)"* hole,
which until now was named in the abstract. What is missing is not the file; it is that a documented
expectation prints as an error and therefore reads as a failure to anyone tailing a log.

### FINDING 7 — THE FIRST N-1 PASS FILED NO EXIT STATUS

Closed rather than merely reported, but recorded because the shape recurs: I had `rc=3`, `rc=1`,
`rc=1` in hand, quoted them in a message, and wrote **none of them into the evidence directory**. The
first pass held 4 logs, 2 `.jsonl` and 2 `.root` and nothing matching `rc=`/`exit_status`. A grader
could only *derive* rc=3 from `mnv_guarded_run.py:524` returning `VIOLATION_EXIT` after that banner —
a derivation from source, not a measurement of the run. **A number that exists only in a message is
not evidence**, and 9.1's settlement column asks for the process's own status.

*Pre-empting a false positive for the next reader:* `grep -c -- '--allow' cap/armN1.log` returns
**1**. That is the guard's own banner text — *"--allow does not cover this: it declares an IMPORT tree,
never an execution tree"* — not a flag. `allow=[]` and `allow_is_empty=True` on both records.

### FINDING 8 — MY UNGUARDED ARM RAN FROM THE CANONICAL CHECKOUT AND DID NOT MUTATE IT

Checked because `python3 -v` reported reading a `.pyc` **inside** the canonical tree, and CPython
writes bytecode beside sources by default. Measured after the arms: **0** `.pyc` files anywhere under
canonical newer than 90 minutes; the `seed_offset_policy` `.pyc` dates from **2026-08-20**, so it was
read, not written. Exactly **one** file under canonical changed in that window —
`nd-unfolding/pet/log_fe_nominal_nominal.txt`, 51 B at 04:50:08, a PET lane's log — and **my arms ran
at 05:17 and 05:26**, so it is not mine. Canonical `HEAD b2d7d4ca`, porcelain **722** against the
721 the August receipt recorded; the +1 is that PET log, not this work.

---

## 6. F-8(a) PART TWO — THE ENTRYPOINT-SET CLOSURE, PUBLISHED SO IT CAN BE FALSIFIED

The round-10 packet asserted *"2 in the static k=0 import closure (15 files)"*. **The 15 was never
published and was therefore unfalsifiable**, which is the defect P-6 exists to prevent. Measured on
the deployed candidate, from the nine M-1 entrypoints, resolving only repository-local modules under
`nd-unfolding/`, `2d-unfolding/`, `3d-unfolding/`, `unbinned_unfolding/python/` and `nd-unfolding/pet/`:

| pass | closure | hazards inside it |
|---|---|---|
| module-level imports only | **18** | **2** |
| any-depth imports | **20** | **2** |

**Not 15.** The two files the any-depth pass adds are `unbinned_unfolding/python/omnifold.py` and
`nd-unfolding/fps_unfold_complete.py`.

**The two hazards, and they are the same two in both passes:**
`nd-unfolding/adopt_unified_5d.py` and `2d-unfolding/unfold_2d_omnifold_unbinned.py`. Both are
already in the ratchet's 52-entry `KNOWN_UNREPAIRED` set; neither is presented here as repaired.

**`compare_unified_throw.py` is INSIDE the closure and is NOT a hazard**, which is the repair working:
it enters at depth 2 — entrypoint → `unified_throw_cov.py` → `compare_unified_throw.py` — and that
depth is exactly why FINDING 1's depth-1 instrument cannot see it.

### 6.1 RECONCILIATION with the independent figure, rather than adoption of it

The round-11 grader first measured **18 / 19 / 2** independently, against my **18 / 20 / 2**. It then
re-measured both ways and the gap resolved — **it was INDEX SCOPE, not depth**, and it has adopted 20:

```
index = nd-unfolding + 2d-unfolding             (127 names) : module-level 18 | any-depth 19
   any-depth adds: fps_unfold_complete.py
index = the same + unbinned_unfolding/python     (129 names) : module-level 18 | any-depth 20
   any-depth adds: fps_unfold_complete.py, unbinned_unfolding/python/omnifold.py
```

**Both scopes agree on 18 module-level and on exactly the same two hazards.** The narrow index cannot
admit `omnifold.py` at *any* depth, so the disagreement was never about transitivity. **Both scopes
are recorded here on purpose, so a 19-versus-20 cannot recur without someone naming which index
produced it** — this is the same discipline as stating the population beside a census count.

**An incidental agreement worth carrying into F-17(a):** the narrow index is **127 names, which is
exactly M-2's 127** on the code root. So M-2's population and the closure's narrow index share a
scope, and both exclude `unbinned_unfolding/python`. That is a coincidence of construction rather than
of arithmetic — and it means **anyone widening one must widen the other**, or the two will silently
disagree about the same tree.

### 6.2 MY FIRST CLOSURE INSTRUMENT WAS WRONG, IN A WAY THIS CAMPAIGN HAD ALREADY FIXED ONCE

My first pass reported **1** hazard, not 2. It missed `adopt_unified_5d.py`:

```python
_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"              # :35
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):    # :36
    if _p not in sys.path:
        sys.path.insert(0, _p)                                   # :38
```

My detector resolved rooted names through `ast.Assign` only, so the insert argument `_p` — **bound by a
`for` loop** — was invisible. **That is verbatim the defect the round-10 packet diagnosed and repaired
three weeks of work ago**, in its own words: *"The insert argument is `_p`, a loop variable bound from
an f-string mentioning `_REPO` — never the rooted name."* The repair there was dataflow to a fixpoint
over `ast.Assign` **and** `ast.For`. I wrote a third implementation of the rule and rebuilt the flaw,
hours after reading the paragraph describing it.

**The fix was not to fix my detector.** It was to delete it and delegate the hazard test to the
instrument that owns the rule — `test_oi136_rooted_insert_ratchet.rooted_insert_files` — and intersect
its 52-file census with the closure. The same principle `mnv_source_manifest.py` states about hand
recipes applies to hand re-implementations: **a rule retyped is a second implementation of the rule**,
and it will drift toward the naive reading. The published 2 comes from the campaign's instrument, not
from mine.

### 6.3 A LOAD-BEARING `.gitignore` RE-INCLUDE, WITH ITS COUPLING UNRECORDED

The k=0 path **does** use `unbinned_unfolding/python`, and safely:
`unfold_nd_omnifold_unbinned.py:969` builds `_OF = f"{_REPO}/unbinned_unfolding/python"` from
`_REPO = str(Path(__file__).resolve().parents[1])` at `:63` — **derived**, so it resolves under the
code root, not the canonical tree.

That works only because `omnifold.py` is present in a conforming clone, and it is present only
because `.gitignore` re-includes it by name after excluding the tree:

```
71: unbinned_unfolding/**
75: !unbinned_unfolding/python/omnifold.py
76: !unbinned_unfolding/python/omnifold_old.py
```

**So line 75 is load-bearing for Gate 1**, and nothing says so where a reader would look. Tidying it as
*"why is one file re-included from an excluded tree?"* would make conforming clones stop containing
`omnifold.py`, and the k=0 path would break or fall back.

**One refinement, then a sharper reason than either of us first gave.** The claim that *nothing*
guards presence is too strong: `blob = (REPO / OMNIFOLD_HELPER).read_bytes()` is unguarded, so an
absent file raises `FileNotFoundError` and the suite goes non-zero — presence is guarded **as a side
effect**.

**But the read sits ABOVE the assertion, so an absence never reaches `assertEqual`.** The consequence
is specific and worse than "an exception rather than a diagnosis": the carefully written message on
that assertion — *"Do not update this constant to make the test pass — take the decision back to
him"* — is **on a branch that cannot fire when the file is missing.** Someone who tidies the
`.gitignore` re-include gets a bare `FileNotFoundError` and no hint that line 75 is load-bearing for
Gate 1. **The stakes are documented on the unreachable branch.** Identified by the round-11 grader,
and it is a one-line fix — test `.exists()` first with its own message. **Not made here:** the ratchet
is a tracked `.py` in the 782, so it needs a future candidate (FINDING 1).

### 6.4 THE UNGUARDED ARM'S TWO HALVES COME FROM ONE PROCESS, NOT TWO RUNS

Stated because it had to be inferred once already. `cap/armU.log` (stdout) and `cap/armU.verbose`
(stderr) are **two streams of a single invocation** of the real unmodified binary — the redirection is
`> armU.log 2> armU.verbose`. The stdout file shrank 1385 → 369 bytes between pass 1 and pass 2 with
the ROOT errors moving into `.verbose`, which is the signature of a stream split rather than a second
run. So §5.5's two halves — *reaches the `[remedyA]` marker* and *names the module's origin* — are
properties of **one** process: the marker in `armU.log`, the `SourceFileLoader` resolution at
`armU.verbose:274-276`.

### 6.5 THE `.pyc` RESULT IS CONTINGENT, AND MUST NOT BE FILED AS A GUARANTEE

FINDING 8 records that my unguarded run wrote no bytecode into the canonical checkout. **That held
only because the cache was already current for an unchanged source.** Had the source differed by one
byte, CPython would have written a fresh `.pyc` **into the tree this campaign treats as read-only** —
and `python3 -v` is precisely the instrument one reaches for while investigating a source that *has*
changed. Neither `PYTHONDONTWRITEBYTECODE` nor `-B` was set on this arm; it was unset, measured.
**Any future arm executing from the canonical checkout must set `PYTHONDONTWRITEBYTECODE=1` or pass
`-B`.** Filed as contingent, not as "canonical is safe from `-v`". Raised by the round-11 grader.

### FINDING 9 — `MANIFEST.tsv` IS INDEX-BLIND, SO "ONE COMMIT" NEEDS A SECOND HALF

`generate_manifest.py` reads **working-tree bytes and nothing else**. Verified by exhaustion: the only
reads in the file are `read_bytes()` at `:281`, `:345` and `:539` — **no `git show`, no `cat-file`, no
`--cached`, no `GIT_INDEX_FILE`**. There is no index or blob read anywhere.

**The consequence, which I had not drawn.** A partial commit — a staged subset, or
`git commit -- <pathspec>` — can publish a `MANIFEST.tsv` row describing **working-tree content that
is not in that commit**, and `--check` still passes, because *both sides of the check read that same
working tree*. The index never enters the comparison, so the check is structurally incapable of
noticing.

**So the forward rule from §6.6.2 is amended and this is its final form:** a docs edit and its
manifest regeneration are **ONE commit, and a WHOLE-FILE commit** — not pathspec-scoped, not partially
staged. Raised by the round-11 grader.

**And it lands on me.** Every commit I made today used `git commit -F - -- <explicit paths>`, which is
exactly the pathspec form. They were safe only because each pathspec happened to name every file
modified at that moment — `82727fe3` two docs, `d268a95b` one, `0c74ad01` and `35777aad` two each.
**That is circumstance, not method**, and it is the same shape as FINDING 8's `.pyc` result: the right
outcome from a protection that was not actually in place. This campaign has already been bitten twice
by pathspec scoping — *"the unit is the invocation, not the flag"* — and once by a hook seeing a
different index than the shell. Same family, third appearance.

### FINDING 10 — A `data = b""` THAT READS LIKE A BUG AND IS THE FIXPOINT SEED

Recorded because the next reader will stop on it. `generate_manifest.py:342-343`:

```python
if path == TARGET:
    data = b""
```

That is not a skipped file. It is the **seed** of the self-row fixpoint: `MANIFEST.tsv` carries a row
about itself, so its `lines`/`bytes` start at 0/0 and iteration fills them in until they describe the
file that contains them. It is why the self-row can be accurate at all, and why
`MANIFEST.tsv byte-count fixed point did not converge` is a reachable error rather than dead code.
Stated beside §6.6.2's fixpoint paragraph so `b""` is not read as the defect it resembles.
