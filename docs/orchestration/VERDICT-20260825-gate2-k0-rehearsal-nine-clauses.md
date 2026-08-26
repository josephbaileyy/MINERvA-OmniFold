# GATE-2 VERDICT — k=0 rehearsal `k0-aa67c426-20260824T145751Z`, nine clauses

**Recorded 2026-08-25/26 by an independent grading lane.** Graded against
`docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md`,
sha256 `8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378` at `main` = `e428a645`.

**This verdict is recorded AFTER 2026-08-24, so it grades NINE clauses** (§7.0.18): F-1(b), F-2(b),
F-3(b), F-4(b), F-5(b), F-7(b), F-8(b), F-17(b), F-18(b). **`F-6(b)` is not graded here — it moved to
the separate leg-6 completion gate, where it remains MANDATORY and is NOT waived, excused or
optional.**

---

## THE VERDICT, first

> ## GATE 2 DOES NOT PASS.
>
> **F-7(b) and F-8(b) have NO evidence of any kind — not weak evidence, none.** F-17(b) is
> partially discharged and its second obligation is not merely unperformed but currently
> **impossible**. §F's no-partial-credit rule applies over the nine, so any single miss is a FAIL of
> the gate. There are three.
>
> **The rehearsal's products therefore stay exactly where they land: not adopted, not consumed
> outside the seven rehearsal jobs, not quoted, and no further member is authorized** (§7.0.6).

## CITABLE FOR

- The per-clause dispositions in §1, each bound to a path and a digest I re-derived myself.
- That the seven jobs are terminal and clean, that the frozen deploy tree still satisfies A-2(a)–(g)
  at the far end, and that P-2 holds across all 374 inventory records — measurements filed here for
  the first time.
- The four defects in §3, three of which are **repairable in code and are not disclosures**.
- The list in §2 of the producing lane's claims that did **not** reproduce.

## NOT CITABLE FOR

- **Any PASS of Gate 2.** It does not pass.
- Authority to adopt, consume, or quote any run product; to submit leg 6; to submit any member
  k≠0; or to unfreeze `/pscratch/sd/j/josephrb/k0r2/clean`. This document authorizes **nothing**.
- F-6(b), which is out of scope here and unaffected.
- A claim that the 32 reported M-1…M-6 differences have been *explained*. F-17(b) obliges
  **reporting**, not resolution. They are reported and they remain unexplained.
- The three clauses in §1 marked **PASS (measured by the grader)**, if the campaign's reading of
  §7.0.10 requires a producing lane to file a measurement and a grader only to check it. **That
  reading is Joseph's to settle — see §4.**

## Eligibility (§7.0.10)

I did not build the run, the launchers, the guard, the ruler `measure_m1_m6.py`, the comparator
`compare_m1_m6.py`, the far-end script, or the F-17(b) record; and I did not write §7.0 of the
contract or the SPEC the comparator was built against. I am not the lane that filed `a3ed8631`.

---

## 1. The nine clauses

| clause | verdict |
|---|---|
| F-1(b) | **PASS** |
| F-2(b) | **PASS (measured by the grader; nothing was filed by a producing lane)** |
| F-3(b) | **PASS on substance by a STRONGER instrument; the clause's own instrument is VACUOUS here** |
| F-4(b) | **PASS** |
| F-5(b) | **PASS (measured by the grader; nothing was filed by a producing lane)** |
| F-7(b) | **NOT DISCHARGED — no pin recorded from this rehearsal exists** |
| F-8(b) | **NOT DISCHARGED — no run receipt for this rehearsal has been authored** |
| F-17(b) | **NOT DISCHARGED — half of the clause is performed; the other half is impossible, not pending** |
| F-18(b) | **PASS on delivery of this document** |

### F-1(b) — PASS

Requirement (§7.0.5): *"the same measurements repeated after the last leg; porcelain zero and the
manifest digest identical at both ends."*

Re-derived by me on the frozen deploy tree `/pscratch/sd/j/josephrb/k0r2/clean`, today, i.e. after
the last leg ended (combine `57527875` End `2026-08-25T16:24:42`):

| A-2 | measured | value |
|---|---|---|
| a | `git rev-parse HEAD` | `aa67c426afaa9b6ca91c9996637a6bade950da9a`, and `symbolic-ref -q HEAD` rc=1 → **DETACHED**, so §7.0.19's freeze held |
| b | `git status --porcelain` line count | **0** (counted, not read from `$?` after a pipe) |
| c | `constitution.is_checkout` / `markers` | `true` / `["VALIDATION_LEDGER.md", "nd-unfolding"]` |
| d | `constitution.nested_checkouts` | `[]` |
| e | `constitution.enclosing_checkout` | `null` |
| f | `--compare --require-clean` | rc=0, `SOURCE MANIFEST IDENTICAL (782 files, fa3489e2…535420)` |
| g | `constitution.mode_writable` / `uid_writable` / `other_writable` | `[]` / `[]` / `[]` |

Baseline: `/pscratch/sd/j/josephrb/k0r2/declarations/aa67c426/source-manifest.json`, **file** sha256
`622ddc0ada33234d…`, **field** `listing_sha256` = `fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420`,
`file_count` 782. The producing lane flagged the file/field distinction and **did not conflate them**;
I confirm they are different objects with different values.

**I went past what was filed and tested A-2(f)'s comparator in the direction it acts**, because a
printed `rc=0` is a filter, not a test of the filter. Three mutated baselines in my own scratch, same
tool, same tree:

| mutation | rc | said `IDENTICAL` |
|---|---|---|
| one tracked file's `sha256` changed | **3** (`CHANGED`) | no |
| one file deleted from the baseline | **3** (`ADDED`) | no |
| one phantom file added to the baseline | **3** (`REMOVED`) | no |
| baseline unreadable | **2** (`COULD NOT LOOK`) | no |
| true baseline | **0** | yes |

Fires on bad in both directions, silent on good, and distinguishes "could not look" from "clean".
A-2(f) is a real check. **Defect D-1 (§3) is recorded against A-2(g), and it does not change this
PASS**, because ruling 22's attempted-write wording amended F-1(a); F-1(b) is "the same measurements
repeated", and they were.

### F-2(b) — PASS, measured by the grader

Requirement: *"P-2 holds across every inventory; every `--pair` CURRENT."*

Over **all 374** records in
`/pscratch/sd/j/josephrb/k0r2/runs/k0-aa67c426-20260824T145751Z/inv/*.jsonl` — not a sample:

| field | value | count |
|---|---|---|
| `outcome` | `ok` | 374/374 |
| `verdict` | `REPOSITORY-ORIGINS-INSPECTED` | 374/374 |
| `violation` | `null` | 374/374 |
| `guard_installed` | `true` | 374/374 |
| `expect_root` | `/pscratch/sd/j/josephrb/k0r2/clean` | 374/374 |
| `repo_origins_outside_expect_root` | `0` | 374/374 |
| `checked` | `> 0` (min 974, max 1164) | 374/374 |

`--pair`: **374 of 374** task `.out` files carry `6 of 6 CURRENT`. Zero occurrences of `STALE`,
`UNCOMMITTED`, `MISSING`, `DIVERGED` or `NOT CURRENT` anywhere in the 750-file log corpus, against
2992 occurrences of `CURRENT` on the same file set — so the null is scoped and covered.

The non-vacuity requirement of §7.0.8 is satisfied on its own terms: `checked` is not zero anywhere,
and its minimum is 974.

### F-3(b) — PASS on substance; the clause's instrument is vacuous

Requirement: *"grep the job stdout → zero `--allow`; publish the command."*

Published command, over the complete corpus (374 task `.out` + 374 task `.err` + 2 preflight `.out`):

```
grep -l -- '--allow' $RUN/log/*.out $RUN/log/*.err \
                     $RUN/log/uq_4d/*.out $RUN/log/uq_4d/*.err \
                     $RUN/log/uq_5d/*.out $RUN/log/uq_5d/*.err
```

Result: **0 files, 0 occurrences.** *And that result is worth nothing on its own*, which is the
finding. **These launchers never echo their argv.** Measured on the same 750 files:

| token | files | occurrences |
|---|---|---|
| `--allow` | 0 | 0 |
| `--expect-root` | 0 | 0 |
| `--inventory` | 0 | 0 |
| `--pair` | 0 | 0 |
| `allow` (bare substring) | 0 | 0 |

A `--allow` passed on a command line **would not appear in stdout**, so the zero is exactly what an
argv-free log returns whether or not the flag was passed. My first covering control — `mnv_guarded_run`
in 374 files — was itself misleading: that string appears only as a *path* inside a `CURRENT` parity
line, never as a command line. A control that matches a path does not prove a search can find a flag.

The clause's intent is nevertheless satisfied, by a **stronger** instrument the clause does not name:
the guard records its own parsed argv, and across all 374 records `allow` is `[]` and
`allow_is_empty` is `true`, 374/374. That is the guard's own view of what it was given, not a
launcher's self-report. **Defect D-2 (§3): the clause should be re-pointed at that field.** Changing
the clause is a contract amendment and is not mine to make.

### F-4(b) — PASS

Requirement: *"count of inventories == count of guarded processes."*

**374 == 374**, and both sides are established independently rather than one being read off the other:

- **Inventories = 374.** 374 files in `inv/`, all `.jsonl`, and **374 non-empty lines in total** — so
  records equal files here and "374 records" is exact, not an approximation from a file count.
- **Guarded processes = 374, from the scheduler and the logs, not from the inventories.**
  `sacct -X` over the seven jobs returns **374** rows (100 + 24 + 19 + 40 + 21 + 169 + 1), array
  indices contiguous with no gaps. Each of the 374 task `.out` files contains **exactly one**
  `mnv_guarded_run` invocation (histogram: `374 × 1`; the only two `.out` files with zero are the
  preflight `srcman.out` and `a2f.out`).
- **Bijection.** The 374 jobids embedded in the inventory filenames and the 374 `JobIDRaw` values
  from `sacct` are the **same set**: 0 filename ids absent from the `sacct` set, 0 `JobIDRaw` absent
  from the filenames. No record came from outside the seven jobs, and no task failed to emit one.
- Guarded scripts sum correctly: `sweep_bank_5d` 169, `bootstrap_nd` 100, `unified_throw_cov_5d` 62
  (40 run + 21 block + 1 combine), `seedscan_split` 24, `unfold_nd_omnifold_unbinned` 19 = **374**.

Non-vacuity holds: 374 > 0. The pinned-writer child is absent, consistent with
`finalize_submitted=NO` and with F-6(b) sitting at the leg-6 gate.

**The filed count is right; the filed JUSTIFICATION for it is wrong — see §2, finding (iii).**

### F-5(b) — PASS, measured by the grader

Requirement: *"P-2 holds for every real inventory: origins under the code root, sha256 matching the
manifest, `checked > 0`."*

All three, over all 374 records, checked against the 782-entry declared baseline:

- **origins under the code root:** every `script` and every entry of every `repo_origins` list
  resolves under `/pscratch/sd/j/josephrb/k0r2/clean`. `repo_origins_outside_expect_root` = 0 in
  374/374. `under_expect_root` false: **0** occurrences.
- **sha256 matching the manifest:** 0 `script_sha256` mismatches, 0 origin `sha256` mismatches, and
  0 paths absent from the manifest — across every origin of every record.
- **`checked > 0`:** 374/374, minimum 974.

`repo_origin_count` distribution: `{3: 124, 5: 19, 6: 169, 7: 62}` — never zero, so there is no
record on which the origin question went unasked.

This also closes the OI-136 hazard for this run specifically: `sys_path_final[0]` is the frozen
tree's `nd-unfolding` and no origin resolves outside it. That is the failure mode that made a
`5 of 5 CURRENT` true and blind on run 4, and it is measured absent here.

### F-7(b) — NOT DISCHARGED

Requirement: *"the sets are recorded from the rehearsal and pinned — see §7.0.9, the pin's first TEST
falls outside this gate."*

§7.0.9 disposes of F-7(b) by *recording and committing* the sets, and requires the reviewer to say in
those words that the pin is recorded and untested. **I cannot say it, because it is not recorded.**
No expected-set pin taken from this rehearsal exists anywhere in the repository, on any ref. The
far-end instrument does not produce one, and its own header records the adjacent gap as deferred
defect 4: *"F-7(b) has no exclusion instrument — nothing mechanically enforces the exclusion the
clause asserts, so it is satisfied by convention only."*

This is cheap to fix and it must not be graded as satisfied by convention. §7.0.9 lowered the bar to
recording; the bar was not met.

### F-8(b) — NOT DISCHARGED

Requirement: *"the receipt states the blind spots in the receipt's own words."*

**No run receipt for this rehearsal has been authored.** Every committed blind-spot document is
pre-submission (F-8(a)) material dated 2026-08-22/23. `RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md`
exists only on `github/build-k0-execution-integrity`, is not on `main`, covers the *(a)* halves, and
was committed **before** the far end. A receipt that predates the run cannot state the run's blind
spots.

### F-17(b) — NOT DISCHARGED

Requirement: *"re-measured **again after the path runs**; M-2's inventory claim over the untracked
set is the perishable one and is re-tested here."* The clause elsewhere (`:1471`) obliges that any
difference from `MEASUREMENT-20260822-m1-m6-at-pinned-sha.md` be reported as a finding.

**First half: PERFORMED, and I reproduced it independently.** Re-running the committed comparator over
the surviving scratch inputs gives, bit for bit, the filed numbers: 72 fields compared, 32 findings,
`n_expected` 0, `n_unexpected` 32, `n_unexpected_excluding_m2` 31, `n_m2_findings` 1, verdict
`DIFFERENCES-SOME-UNEXPECTED`, **exit 20**. Record
`docs/orchestration/state/f17b-k0-aa67c426-20260824T145751Z.json`, sha256
`9109f371f0db33eb575d426bf8b843dbd0b0d3e390c78cc0faba133a34fce24d`, **53226 bytes** — exactly as
claimed. Input digests in the record match the files on disk
(`501326a0de79aad5…`, `6564ada83a8ba1e9…`). M-2 is flagged separately and is not absorbed into a
summary count, as R7 requires. The 32 differences being unexplained does **not** fail this clause:
the obligation is reporting, and they are reported.

**Second half: NOT PERFORMED, AND CURRENTLY IMPOSSIBLE.** The comparator consumes
`measure_m1_m6.py --json`; the pre-submission column exists only as markdown prose, and no `--json`
document was ever filed at the near end. So the `:1471` comparison cannot be run at all. The
producing lane disclosed this in the instrument itself, and the prior instrument grade reached it
independently as its G-5. **This is the fourth instance in this contract of the shape it already
names twice: a control presenting as merely UNPERFORMED when it is IMPOSSIBLE.** §7.0.8 forbids
reading an impossibility as a deferral, which is why this is NOT DISCHARGED rather than deferred.

The clean repair is the one the prior grade named: emit `--json` alongside the human table at both
ends from here on. **The repair to refuse is back-filling the pre-submission column now** — a column
manufactured after the fact cannot falsify anything, and re-pointing a receipt-bound artifact to make
a check pass is forbidden outright (OI-123).

**A second reason this cannot be closed today.** The prior instrument grade
`GRADE-20260825-f17b-comparison-instrument-fitness.md` **has self-expired**: it states that its
verdict expires the moment any of three digests moves, and all three have. `compare_m1_m6.py` is
`bace69d2…` / 892 lines against the graded `422ed9e7…` / 782; the expected list is `56c2e0ef…` / 53
lines against `299c5799…` / 48; the suite is `88674d28…` / 1155 lines against `9b3ef0d4…` / 919. So
the instrument that produced the filed record **has never been graded**. I re-tested the two findings
that would have mattered most and both are now **FIXED**: a one-character citation quote is refused
at exit 5 with a ≤3-matching-line bound (was G-2), and a field absent from one side is no longer
suppressible by `may-differ` — injecting `M-4.behind` on the deploy side only yields 33 findings, 0
expected, exit 20 (was G-3). G-1 is fixed too: the suite's whitelist arm now calls
`cm.field_matches` instead of `fnmatch`. **What is not fixed is D-3 in §3.**

### F-18(b) — PASS on delivery

Requirement: *"a fresh non-builder records the POST-REHEARSAL verdict clause by clause."*

This document, by a lane that built none of the work under review and did not write §7.0. It grades
nine clauses individually, reaches FAIL on the gate, and contains no "all controls passed" summary —
which §7.0.10 makes a FAIL of F-18 in its own right. See §4 for the one eligibility question I cannot
settle for myself.

---

## 2. The producing lane's claims — what reproduced, and what did not

All eight claims in `a3ed8631` were re-derived from their stated operands rather than accepted.

**Reproduced exactly.** Seven jobs terminal: `sacct` over the seven returns **1122** rows, **all**
`COMPLETED`, **all** `0:0`; combine `57527875` `COMPLETED 0:0`. Covering control: `sacct -j 99999999`
returns **rc=0 with 0 rows**, so an empty answer here would have looked identical to a clean one —
my 1122 is non-empty, which is what makes it evidence. F-1(b)'s figures (`aa67c426`, DETACHED,
porcelain 0, four require-arms rc=0, `622ddc0a`, 782 files / `fa3489e2`). F-17(b)'s 72/32/exit-20 and
the record's digest and byte count. The canonical tree at `b2d7d4ca` with **dirty 742 = 718 untracked
+ 24 modified** — the status-code histogram is `718 ??`, `10 M`, `8 A`, `4 M`, `2 MM`, so the split is
right and the two populations really are different, as the commit says. The reflog: `b2d7d4ca` was
reached by `merge github/main: Fast-forward` at **2026-08-21 21:39:10 -0700** and there is no later
entry, so HEAD provably had that value at submission.

**Claim 6 holds, including its restraint.** The lane claimed HEAD-stability and explicitly declined
to claim working-tree stability. I looked for a place where the argument quietly widened from the
first to the second and **found none** — the commit message scopes it to HEAD, and the far-end M-1…M-6
column is measured on the tree as it is now, which is what F-17(b) asks for. The distinction is
correctly maintained.

**Did not reproduce, or overstated:**

- **(i) "233 behind" is unreproducible as written.** A "behind" count is a two-sided comparison and
  the right-hand side is named only as *"main"*, which re-points. Measured: **233** against
  `30ede740` (main's tip at measurement time), **234** against `a3ed8631` itself, **238** against
  today's `main` = `e428a645`, and **230** against `github/main` as seen from inside the canonical
  tree. Four numbers for one phrase. The figure was true when written; it was not stated with its
  operand, so it cannot be checked without guessing. `b2d7d4ca` **is** an ancestor of `main` (rc=0),
  and that part is stable.
- **(ii) Claim 8 is overstated, and I can date the window.** The commit and the script's own comment
  say each tool is digested *"immediately before AND immediately after its own invocation"*. That is
  true of the ruler and **false of the comparator and the expected list**:
  `COMPARATOR_PRE`/`EXPECTED_PRE` are taken at `measure_k0_farend_f1b_f17b.sh:149-150`, **before** the
  two ruler invocations at `:152-158`, and the comparator does not run until `:162`. From the record's
  own mtimes that gap is **at least 44 min 48 s** — a lower bound, because `COMPARATOR_PRE` is taken
  before the deploy measurement finishes at `2026-08-25T23:46:05Z` and the comparator had not yet
  emitted the record at `2026-08-26T00:30:53Z`. A tight bracket strictly dominates a wide one: a swap that is reverted
  before `POST` is caught by a digest taken just before the call and missed by one taken 45 minutes
  earlier. The window is not hypothetical — a second run of the same script was executing
  **concurrently** from a *mutation-testing* worktree (`…/scratchpad/wt-mutate`) during it. I did not
  re-run the exit-13 positive control; I verified the refusal logic at `:172-178` by reading it, and
  the specific hole the comment claims to close is the one still open.
- **(iii) The F-4(b) exclusion justification is FALSE.** The commit says *"siblings excluded by name
  — one excluded sibling holds 298 jsonl, so a `runs/*/inv` glob would have inflated the count by
  80%."* The 298 is real and the arithmetic is right — `(374+298)/374` = **+79.7%**. **The operand is
  wrong.** Those 298 files live in
  `runs/k0-a54038b2-20260823T205254Z/guard-inventories/`, a **differently named** directory that a
  `runs/*/inv` glob cannot reach. Measured: `ls runs/*/inv/*.jsonl` returns **374**, of which
  **0** come from siblings. Of the three siblings, two have no `inv/` directory at all and the third
  (`k0-aa67c426-20260824T143517Z`) has an `inv/` that is **empty** — it is the superseded attempt 1,
  which `SUBMISSION.txt` records as *"cwd was the read-only code root; 0 products"*. So the
  exclusion-by-name prevented nothing, and the counterfactual it is offered as evidence for could not
  have happened. This is right arithmetic over the wrong object, and it is fail-safe only by luck:
  the filed 374 is correct.
- **(iv) A hypothesis of mine that was WRONG, recorded because a null result should be scoped.** The
  script counts the audited run with `find $RUN/inv -type f` (all files, one directory) and the
  siblings with `find $d -name '*.jsonl'` (one suffix, whole tree). Those are different populations
  and different filters, so I expected the 374 to be inflated by non-`jsonl` files. It is not: all
  374 entries are `.jsonl` and each holds exactly one record. **The asymmetry is real in the
  instrument and immaterial in the result.**

**Claim 7 — the challenge the producing lane set, answered in the direction it asked for.**

The premise reproduces completely. `M-4.behind` is absent from **both** documents (deploy `M-4` keys
and canonical `M-4` keys are both exactly `dirty, head, is_git, modified, untracked`);
`--upstream` defaults to `origin/main`; `rev-list --left-right --count origin/main...HEAD` returns
**rc=128** in both trees, because the frozen tree has **no remotes** and the canonical tree has
`analysis-note` and `github` but no `origin`. The whitelist's only entry is therefore dead, and
`expected_entries_unused: ["E1-m4-behind-drift"]` is reported in the record.

**The fail-safe argument is right about the dead direction and incomplete about the other one.** A
dead entry suppresses nothing — confirmed. But the guard that is supposed to make an over-broad entry
impossible is **fail-open**, which is D-3 below. So the correct statement is narrower than the one
filed: *this* whitelist suppressed nothing, and the reason is not that the guard would have stopped it.

---

## 3. Defects. Three of these are repairable in code and are NOT disclosures.

### D-3 (repairable, and the most consequential) — `bad_pattern` admits a pattern that whitelists an entire measurement

`compare_m1_m6.py:441`'s docstring: *"A whitelist that can swallow a whole measurement is not
reviewable."* The shipped expected-list's own notes claim the instrument *"refuses (exit 5) … any
pattern that is a bare measurement id or ends in a wildcard segment."*

**The pattern `M-1[*` — the documented per-file wildcard with the closing bracket omitted — is
ALLOWED, and it matches every M-1 field.** The breadth check is
`pattern.rsplit(".", 1)[-1] in ("*", "**")`, and a pattern containing no `.` has no last segment to
test, so the whole pattern is compared against `"*"` and passes. `field_matches` then splits on `*`
into `["M-1[", ""]`, and `endswith("")` is true of everything.

Measured end to end against the real far-end inputs, with one entry carrying one citation whose quote
is a genuine line of a genuine cited document:

| expected list | exit | `n_expected` | `n_unexpected` |
|---|---|---|---|
| shipped | 20 | 0 | 32 |
| one entry, `fields: ["M-1[*"]` | 20 | **19** | 13 |
| one entry, `fields: ["M-1[*].first_insert"]` | 20 | 6 | 26 |

**All 19 M-1 findings suppressed by a one-character malformation**, classified
`EXPECTED-BY-RULING`, with no warning and no refusal. It stayed at exit 20 here only because 13
non-M-1 findings survived; had the differences been confined to M-1 it would have produced
`DIFFERENCES-ALL-EXPECTED`. The deny-list arm
`test_an_OVER_BROAD_pattern_is_refused_so_the_list_cannot_swallow_a_measurement` tests
`("M-4", "M-4.*", "M-1[*].*", "*", "M-4behind", "behind")` and **does not include `M-1[*`** — it is
again a list of the spellings someone thought to type, which its sibling arm's docstring already
concedes is not the guard.

**Severity is bounded, and the bound must be stated with it.** The suite's behavioural pin
`test_ONLY_M4_BEHIND_IS_SUPPRESSIBLE_over_a_MEASURED_field_universe` is bound to the shipped
whitelist path, and it **works**: I added `M-1[*` to the shipped list and the suite went from **64
passing** to **4 failures**. So a widening of the shipped file is caught in pre-commit. What is not
caught is `--expected` pointed at any *other* in-tree file, which the pin does not cover. The far-end
script hardcodes the shipped path (`:116`), so **the filed F-17(b) record is not affected** — I
verified its `expected_list.sha256` is the shipped `56c2e0ef…`.

**Repair:** reject an unbalanced `[` and any pattern whose match set spans more than one field of a
measurement, and build the arm from the field universe rather than from remembered spellings. The
prior instrument grade did not reach this: it attributed the M-1 wildcard's survival entirely to the
suite's `fnmatch` blindness and never asked whether `bad_pattern` should admit the pattern at all.

### D-2 (repairable) — F-3(b)'s instrument cannot answer F-3(b)'s question

See §1. The clause greps stdout for a flag these launchers never print. Re-point the clause at the
guard's own `allow` / `allow_is_empty` inventory fields, which are a strictly better instrument, and
keep the stdout grep only if a launcher is made to echo its argv. Amending the clause is Joseph's.

### D-1 (repairable) — A-2(g) is a mode-bit check, not the attempted write ruling 22 defines

Ruling 22, §7.0.14: *"**'Verified' means an attempted write, as the job's own user, fails.** A
`chmod` that was issued is not evidence that a write is refused; that is the difference between a
filter and a test of the filter."* `--require-readonly` enforces `mode_writable`
(`os.stat` mode bits) and *reports but does not enforce* `uid_writable` (`os.access(W_OK)`). Neither
attempts a write. In fairness the tool's own docstring is explicit about this, and substantively the
frozen tree is clean on **both** definitions — `mode_writable`, `uid_writable` and `other_writable`
are all `[]` — with `uid_writable` being the closer of the two to the ruling's intent. So this does
not change F-1(b)'s PASS; it means A-2(g) has never been tested in the direction it acts. I did
**not** attempt a write, because the frozen tree is immutable.

### D-4 (not repairable by code) — the instrument that produced the record has never been graded

See F-17(b). The prior grade expired by its own terms when the digests moved. I re-tested its two
HIGH findings and both are fixed, and its G-1 is fixed; that is spot-checking, not a grade. Whoever
next needs F-17(b) closed should re-grade `bace69d2…` rather than cite the expired verdict.

---

## 4. For Joseph — three things a grader should not decide alone

1. **F-2(b), F-3(b) and F-5(b) had no filed evidence, and I both measured and graded them.** That is
   a narrower version of the §7.0.10 conflict this lane exists to avoid. The measurements are
   reproducible from the commands in §1 and I believe them. If the campaign's reading is that a
   producing lane must file and a grader must only check, **treat those three as NOT DISCHARGED** and
   have a producing lane re-file them; the gate fails either way, so nothing downstream turns on it.
2. **F-17(b)'s second half is impossible, not late.** The choices are to emit `--json` at both ends
   going forward and accept that this rehearsal cannot discharge `:1471`, or to amend the clause.
   **Back-filling the pre-submission column is the one option that should be refused.**
3. **D-3 is a live fail-open guard in a whitelist.** Fixing it touches a tracked `.py` and a tracked
   test. Whether that happens before or after the deployment freeze at `aa67c426` is lifted is a
   sequencing call, since §7.0.19 expires when F-1(b) is filed and F-1(b) now passes.

## 5. What I did not check

- I did not re-run the ruler on either tree; the two-tree comparison was reproduced from the
  surviving scratch inputs, whose digests I verified against the record.
- I did not re-run the exit-13 self-mutating-comparator positive control. §2(ii) is a reading of the
  script plus a re-derivation of the window from the record's mtimes, not a re-execution.
- I did not attempt a write anywhere under `/pscratch/sd/j/josephrb/k0r2/clean`.
- I did not grade F-6(b), F-9, F-12, or any Gate-1 clause.
- **I did not verify that the seven jobs are the only jobs that wrote into this run directory** beyond
  the filename/`JobIDRaw` bijection in §1. That bijection is strong evidence and is not a proof about
  processes that wrote nothing to `inv/`.

## 5a. An incidental finding, outside Gate 2 but measured on the way

`MANIFEST.tsv` was **already stale on `main`** before I touched anything. Measured in a clean
detached worktree at `e428a645` with none of my edits present:
`generate_manifest.py --check` → **rc=1, `OUT OF DATE`**, and regenerating there alone rewrites
**23 rows and drops 18**. This verdict's commit brings it current, so the drift in its diff is
pre-existing committed drift and not a peer's uncommitted work — I confirmed the only dirty paths
were my own four.

This is **not** a Gate-2 clause. It is, however, exactly the condition §7.0.7's first addition makes
an F-14 pre-submission requirement (*"`generate_manifest.py --check` exiting 0, measured in a clean
worktree"*), so the next lane that needs F-14 should know the check was failing on `main` today
rather than discover it under time pressure.

## 6. Provenance of the two comparison runs, checked because it invites suspicion

Two complete far-end comparisons exist in scratch, four minutes apart, and only one was filed. They
are substantively **identical**: same comparator digest `bace69d2…`, same expected-list digest
`56c2e0ef…`, same input digests, same 32 finding fields with byte-identical `sides`, same verdict and
same exit 20. A full leaf-level diff of the two records differs in **six** values only — two
timestamps, two input mtimes and two scratch paths, plus the earlier run's `expected_list.path`
pointing into a session-scoped mutation worktree rather than the durable checkout. **No result was
shopped**, and the filed record is the one whose operands are durable.

---

**Filed by an independent grading lane, 2026-08-25/26.** Every number above was re-derived from its
stated operands on the paths and digests named beside it. **Gate 2 does not pass, and nothing in this
document authorizes anything.**
