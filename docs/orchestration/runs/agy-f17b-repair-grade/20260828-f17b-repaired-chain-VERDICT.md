# GRADE 2026-08-28 — the repaired F-17(b) coupled chain, fresh independent full-chain grade

**CITABLE FOR:** whether the eight-file F-17(b) coupled chain, as it stands at commit `46691bbc`
(chain byte-identical at `6eb70aa3`), conforms to
`docs/orchestration/SPEC-20260825-f17b-tree-comparison-instrument.md`
(sha256 `22b73175f90fdc423a49072c380ae0854f6f717a7e0d62f8d2025bd27025a06c`, 12935 bytes), and whether
the four repair surfaces approved in `DECISION-20260828-joseph-f17b-four-surface-repair.md` are
implemented and covered by tests in both directions. Citable for the specific nonconformance N1 and
for the six recorded coverage gaps N2–N7.

**NOT CITABLE FOR:** any Gate-2 clause discharge; any F-number's verdict; the far-end evidence; a
readiness finding; authority to run `measure_k0_farend_f1b_f17b.sh`, submit a rehearsal, or launch
compute; adoption or quotation of any scalar-5D covariance. **This grade is fixtures-only.** I did
not run the far-end script, did not touch Slurm, did not read the frozen deploy tree, and wrote
nothing inside the repository.

**Even a FIT would have authorized only a PROPOSAL for a new forward-only rehearsal.** Gate 2
remains **FAIL**, readiness remains **NOT READY**, and no scalar-5D covariance is adopted. This
verdict changes none of that, and a NOT FIT changes none of it either.

---

F17B-REPAIRED-CHAIN: NOT FIT

The single independently sufficient basis is **N1**: the chain is wired to two mutually
incompatible schema revisions of `measure_m1_m6.py`, so at `46691bbc` it cannot produce an F-17(b)
comparison record for the run it exists to measure. This is a defect *introduced by the repair*,
and it is forced by the §7.0.19 freeze ordering rather than merely likely.

**The two SPEC bases on which the prior grade returned NOT FIT are genuinely repaired.** R3 and R6
are now conformant, and each has a test arm that dies under mutation. I confirm the prior grade's
diagnosis and I confirm the repair fixed what it set out to fix. N1 is a different defect, in a
place neither the proposal nor the decision looked.

---

## 1. Grader identity and non-involvement

- Grader role: fresh independent full-chain grader, commissioned per the "Validation and remaining
  gate" section of `DECISION-20260828-joseph-f17b-four-surface-repair.md`.
- I am **not** the implementer of `46691bbc` and **not** `agy-capacity-probe`. Eligible.
- Workspace: the shared checkout at `/Users/josephbailey/local-research/MINERvA-OmniFold`, read
  only, plus a `git archive HEAD` export to scratch for mutation work. I did not create a git
  worktree (that writes `.git/worktrees`), did not commit, push, stage, stash, or `git add`.
- Interpreter: `python3` 3.12.2 (Mac install). Target is 3.11.14 (Perlmutter). Local shell for my
  own tooling is zsh; the graded script targets bash, and I checked it with local `bash` 3.2.57.
- `git status --porcelain` at start and at end: the same two pre-existing untracked files,
  `HANDOFF-polish-categories-3-6-9.md` and `PROJECT_STATE_PILOT_PROPOSAL.tmp.md`. Neither is mine.
  **No repository file was created, edited, or deleted by this grade.**

### HEAD moved under me mid-grade — re-measured

I began at HEAD `46691bbc0f84b6b85eca5c6c2aced96572f115b1` and finished at
`6eb70aa3c9fe260fe8c3944a9f1ed8867c55e669`. The checkout is shared with peer sessions, so I
re-measured rather than assuming.

- `46691bbc` is still an ancestor of HEAD (`git merge-base --is-ancestor` → yes).
- The two intervening commits are `d5493bf5` ([state] LIVE-STATE prose correction) and `6eb70aa3`
  ([records] OI-160/OI-161). `git diff --stat 46691bbc HEAD` over all eight chain paths is
  **empty**: no chain file changed.
- All three decision-pinned digests re-measured **exact at both shas** (table below).

Every claim in this document is therefore bound to `46691bbc` and holds unchanged at `6eb70aa3`.

### Digest verification, with a negative control

Measured with `shasum -a 256` and `wc -c`:

| Artifact | Measured sha256 | Bytes | Pinned by the decision | Verdict |
|---|---|---|---|---|
| `docs/orchestration/measure_m1_m6.py` | `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51` | 14108 | same | EXACT |
| `docs/orchestration/compare_m1_m6.py` | `28490539b60c4a790f77b5dd1070dc7e9d192efabebee640662d9496cf465242` | 67440 | same | EXACT |
| `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775` | 16358 | same | EXACT |
| `docs/orchestration/SPEC-20260825-...md` | `22b73175f90fdc423a49072c380ae0854f6f717a7e0d62f8d2025bd27025a06c` | 12935 | (commission) | EXACT |

**Negative control, because a digest check that reads no file prints MATCH forever.** A perturbed
copy of `measure_m1_m6.py` (one appended comment line) digested to
`0a528ddc90a3e41093898553620d0c3e9de5be8de90d580ea6aa16ab4c3c8891` — different, so the instrument
discriminates. An absent path (`/nonexistent/xyz.py`) produced `shasum: No such file or directory`
at rc 1, so absence is an error and not a silent match. **What this instrument cannot say:** nothing
about the file that will *execute* on the cluster; it reads only this checkout's bytes. That
distinction is the whole of N1.

The commission's brief mis-stated the SPEC path as `docs/orchestension/...`. The correct path is
`docs/orchestration/SPEC-20260825-f17b-tree-comparison-instrument.md`, and the digest and byte count
given match that file exactly, so the referent was unambiguous.

---

## 2. The file set I graded, and how I derived it

**I did not take the commission's enumeration.** I derived the set three ways and they agree.

1. **From the SPEC.** R1 names the input producer (`measure_m1_m6.py --json`). R4 requires the
   expected list be "an input file, not a literal in the code". R8 requires a documented exit
   vocabulary in the comparator. §6.3 requires, "for each of R1–R8, the arm that fires on bad input
   and the arm that stays silent on good input" — i.e. the test files are part of the deliverable,
   not adjuncts. R6 requires a durable record, which implies the publisher.
2. **From the shell's own wiring**, `measure_k0_farend_f1b_f17b.sh` at `ad1a8b64`: `:128` MEASURER,
   `:134` COMPARATOR, `:135` EXPECTED, `:136` PRESERVER. Four components plus the script = 5, plus
   the three test files = 8.
3. **From the prior verdict's digest table**, `runs/agy-capacity-probe/20260827-f17b-mechanism-VERDICT.md:14-49`,
   which pins **ten** artifacts. Two of those ten are the *yardsticks*, not chain members: the SPEC
   itself and `REVIEW-CONTRACT-20260822-k0-execution-integrity.md`. Removing them gives the same 8.

**The set is eight.** The commission's "eight-file coupled chain" is correct, and I reached it
independently.

| # | File | sha256 at `46691bbc` | Bytes | Changed by the repair? |
|---|---|---|---|---|
| 1 | `docs/orchestration/measure_m1_m6.py` | `ce52ff77…` | 14108 | **YES** (was `0fcd90f7…`, 13213) |
| 2 | `docs/orchestration/test_measure_m1_m6.py` | `1a9ef532…` | 9990 | **YES** (was `0cc38708…`) |
| 3 | `docs/orchestration/compare_m1_m6.py` | `28490539…` | 67440 | **YES** (was `5dc92487…`, 66599) |
| 4 | `docs/orchestration/test_compare_m1_m6.py` | `0977152e…` | 96872 | **YES** (was `762fac14…`) |
| 5 | `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | `ad1a8b64…` | 16358 | **YES** (was `c40e6b54…`, 15722) |
| 6 | `docs/orchestration/m1m6_expected_differences.json` | `2e5f3d52…` | 10393 | no — byte-identical to the prior grade |
| 7 | `docs/orchestration/preserve_f17b_record.py` | `ea2dea54…` | 2354 | no — byte-identical to the prior grade |
| 8 | `docs/orchestration/test_preserve_f17b_record.py` | `509646cf…` | 1786 | no — byte-identical to the prior grade |

Five of eight changed; three are byte-identical to what `agy-capacity-probe` graded, verified
against that verdict's own digest table. For those three I inherit its measurements and re-derived
the ones I cite (R4 exit 5, preserver clobber exit 13) rather than quoting them.

**MANIFEST coupling (F-14 / §7.0.7).** All eight paths have an exact-path row in
`docs/orchestration/MANIFEST.tsv` whose `lines` and `bytes` columns match the live files. Negative
control: a deliberately mis-spelled path returns no row, so the instrument can report absence.
**What this instrument cannot say:** `MANIFEST.tsv` has no digest column (header is
`path tracking class kind campaign event_date event_status canonical_successor read_policy consumer immutable inbound_count lines bytes`),
so it cannot detect a content change that preserves both line and byte counts. My first attempt at
this check reported all eight rows stale *including three known-unchanged controls* — a null result
across a control set, which meant my instrument was wrong, not the manifest.

**Suite count.** 84 (`test_compare_m1_m6.py`) + 13 (`test_measure_m1_m6.py`) + 3
(`test_preserve_f17b_record.py`) = **100, OK**, reproducing the implementer's count on local
Python 3.12.2. That is an implementation control and I treat it as one; the grade below rests on
mutation testing, not on the suite being green.

---

## 3. Per-SPEC-requirement table

Every row is measured at `compare_m1_m6.py` `28490539…` / `measure_m1_m6.py` `ce52ff77…` /
`measure_k0_farend_f1b_f17b.sh` `ad1a8b64…` unless stated. "Mutation-killed" means I edited a
scratch copy, re-ran the suites, and a named arm failed; "**mutation SURVIVED**" means all 100 tests
stayed green with the behaviour removed.

| ID | Verdict | Evidence (path:line + digest) | Test in both directions? |
|---|---|---|---|
| **R1** — consume `--json`, re-implement no measurement | **CONFORMANT** | `compare_m1_m6.py:130-135` (`28490539…`) imports only `argparse, datetime, hashlib, json, pathlib, sys`. `test_compare_m1_m6.py:181` asserts absence of `subprocess, ast, glob, os, re, fnmatch`; `:208-209` asserts absence of the call names. `datetime` predates the repair (file mtime field), so the repair added no measurement surface. | **YES** — bad: forbidden-import sweep; good: the suite's own green baseline. |
| **R2** — no defaults, fail closed on absence | **CONFORMANT** | Measured on fixtures: absent path → **4**; empty file → **4**; valid JSON missing `M-4` → **4**. All three distinct from the difference codes 0/10/20. `compare_m1_m6.py:210` `REQUIRED_KEYS`. | **YES** — three bad arms measured, good arm exit 0. |
| **R3** — identity per tree incl. detached-or-branch | **NOW CONFORMANT** (was the prior grade's independent basis) | Producer: `measure_m1_m6.py:177-187` `branch_or_detached()`, emitted at `:269, :272`. Consumer: `compare_m1_m6.py:430-441` validates, `:467` carries `doc["branch_or_detached"]` **without re-observing the tree**. Real fixture runs gave `{"state":"branch","name":"fixbranch"}` and `{"state":"detached","name":None}`. `record["input_schema_gaps"]` no longer contains the key. | **PARTLY** — carrying is mutation-killed (M5/M6), detached emission is mutation-killed (M7), non-branch-carrying-a-name is mutation-killed (M12). **Four sub-guards mutation SURVIVED** → N5. |
| **R4** — expected list is a declared input file; an unresolvable citation is a hard error | **CONFORMANT**, untouched by the repair | `m1m6_expected_differences.json` (`2e5f3d52…`) byte-identical to the prior grade. Measured: every citation quote replaced with a non-occurring string, list placed **inside** `--repo` → exit **5**, "entry E1-m4-behind-drift, field 'M-4.behind': the quote is not in docs/orchestration/MEASUREMENT-20260822-m1-m6-at-pinned-sha.md. An unresolved citation is a hard error". Control: unmodified list → exit **0**. | **YES.** My first attempt at this arm exited 5 for the *wrong reason* (list outside `--repo`); I re-ran it correctly rather than record the wrong proposition as a pass. |
| **R5** — refuse to infer global agreement at n ≥ 3 | **NOT MEASURED BY ME** — see §6 | `compare_m1_m6.py:944` emits `"global_agreement_inferred_from_pairs": False`, and the comparator's docstring states every comparison is over all n with tolerance as max−min over all n. | **NOT VERIFIED BY ME.** My three-input fixture was degenerate (I copied a dict without perturbing it), so I measured nothing. I do not record a pass. |
| **R6** — record what was compared, incl. each measurement's wall-clock | **NOW CONFORMANT** (was the prior grade's other independent basis) | Producer: `measure_m1_m6.py:172-174` `utc_now()`, `:268` `started_utc` taken **before** the M-1…M-6 work, `:275` `completed_utc` **after**. Consumer: `compare_m1_m6.py:416-429` validates format (`%Y-%m-%dT%H:%M:%SZ`) and ordering, `:461` carries it. Record also carries `instrument.self_sha256`, `instrument.version`, `expected_list.sha256`, per-input `sha256`/`bytes`/resolved path, and `generated_utc`. | **PARTLY** — required-key (M1), reversed-clock (M3) and carrying (M5) are mutation-killed. **The "real" property mutation SURVIVED** → N3. |
| **R7** — M-2 flagged distinctly, never absorbed into a summary count | **CONFORMANT** | Measured: `M-2.python` perturbed → exit **20** with a dedicated line `M-2 PERISHABILITY: DIFFERS  fields=['M-2.python']`, separate from the unexpected-field block. Identical inputs → `M-2 PERISHABILITY: IDENTICAL-ACROSS-ALL-INPUTS  fields=[]`. `PERISHABLE_ID = "M-2"` at `compare_m1_m6.py:211`. | **YES** — bad arm and silent arm both measured. |
| **R8** — exit codes a documented disjoint vocabulary | **CONFORMANT** | `compare_m1_m6.py:157-191`: `EXIT_VOCABULARY` + `check_vocabulary()`, which **raises at import** on a collapsed vocabulary (so the module is not importable rather than warning). `RESERVED_EXIT_CODES` reserves 1 (traceback) and 2 (argparse). `--help` prints "EXIT CODES ARE A DISJOINT VOCABULARY (R8) … 4 refusal: an input  5 refusal: the expected list  2 refusal: usage … 1 RESERVED AND NEVER A VERDICT". I measured the integers 0, 4, 5, 20. | **YES** for the codes I measured; I did not measure 10 (differences-all-expected). |

### The four decision surfaces, graded separately from R1–R8

Surfaces 3 and 4 answer the prior grade's **Item C** findings, which are chain-integrity findings
and **not** SPEC R1–R8 clauses. I keep them separate rather than reporting shell findings as SPEC
nonconformances.

| # | Surface | Implemented? | Test in both directions? |
|---|---|---|---|
| 1 | Real measurement wall-clock | YES — `measure_m1_m6.py:268,275`; `compare_m1_m6.py:416-429,461` | **NO.** N3. |
| 2 | Detached-or-branch identity | YES — `measure_m1_m6.py:177-187`; `compare_m1_m6.py:430-441,467` | Partly. N5. |
| 3 | Preserver digest bracket | YES — `measure_k0_farend_f1b_f17b.sh:221-230`, full 64-hex via `awk '{print $1}'` | **NO — the refusal action has no arm at all.** N2. |
| 4 | Immediate measurer short-circuit | YES — `measure_k0_farend_f1b_f17b.sh:174-179` | **YES** — mutation-killed (M15). |

Schema and instrument version move `1 → 2` at `compare_m1_m6.py:137,139`. Predecessor documents are
refused, not upgraded: `:209-210` plus `:416-441`, measured at exit 4. Both behaviours are correct;
the version bump itself is untested (N4).

**Scoped-out item, recorded and NOT graded as a nonconformance of this repair**, per the decision:
`compare_m1_m6.py:946` retains `input_schema_gaps.measuring_instrument_digest` —
"`measure_m1_m6.py --json` does not identify its own revision; `field_set_differs` is the only
visible symptom of two documents from different revisions". I record it here because **N1 is the
concrete harm that gap would have made visible as a finding**, and a future proposal should close
them together. N1 is not that gap and does not depend on it.

---

## 4. Nonconformances

### N1 — INDEPENDENTLY SUFFICIENT. The chain executes two mutually incompatible revisions of the measurer, and cannot complete.

The repair added producer-side fields to an instrument whose **executing copy lives inside a frozen
tree that cannot receive them**, and simultaneously made the consumer *require* those fields.

Chain of measured facts:

1. `measure_k0_farend_f1b_f17b.sh:128` (`ad1a8b64…`):
   `MEASURER="$CODE_ROOT/docs/orchestration/measure_m1_m6.py"`.
   The measurer is taken from **`CODE_ROOT`**, not from `TOOLS_ROOT`. Only the comparator (`:134`),
   expected list (`:135`) and preserver (`:136`) come from `TOOLS_ROOT`, and only `TOOLS_ROOT`
   (`:133`, `MNV_TOOLS_ROOT`) and the record path (`:139`) have environment overrides. **There is
   no override for `CODE_ROOT`.**
2. `:46` `CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean`, hardcoded; `:47`
   `WANT_SHA=aa67c426afaa9b6ca91c9996637a6bade950da9a`; `:71` prints "DETACHED (7.0.19 intact)".
   `CODE_ROOT` is the frozen deploy tree.
3. **The freeze ordering forces it.** SPEC §5: "The deployment is frozen at `aa67c426` until F-1(b)
   is filed (§7.0.19)." And §1 of this very script — `:64`, "### 1. F-1(b) — A-2(a)-(g) at the FAR
   END" — *is* the F-1(b) measurement. F-1(b) cannot be filed before the script runs, so the script
   necessarily runs while `CODE_ROOT` is at `aa67c426`. This is not "likely"; there is no ordering
   in which it is otherwise.
4. Measured on the git blob, without touching the frozen tree:
   `aa67c426:docs/orchestration/measure_m1_m6.py` = `0fcd90f7c92a7071208e62d09ebc38956f1a83b11af41a469b4886a6e6786d79`,
   **13213 bytes**, with **0** occurrences of `measurement_wall_clock` or `branch_or_detached`.
   Covering control: HEAD's `ce52ff77…` has **5**. Second, independent source for the same digest:
   the script's own comment at `:126` records "measured 2026-08-25: sha256 0fcd90f7...".
5. `:171` invokes **the same `$MEASURER`** for both trees, so *both* documents are predecessors —
   canonical as well as deploy.
6. **Fixture replay of the exact wiring.** I extracted the `aa67c426` blob to scratch (digest
   re-verified `0fcd90f7…`), ran it against two fixture git trees, and fed both outputs to the
   repaired comparator with the flags the shell uses at `:194-195`:

   ```
   keys emitted by the frozen measurer:
     ['M-1','M-2','M-3','M-4','M-5','M-6','label','tree']
   COMPARATOR EXIT = 4
   REFUSING (REFUSAL-INPUT): input 0 is missing measurement_wall_clock, branch_or_detached: …
     A document short of a measurement is a refusal, never a silent agreement on the rest.
   record file: No such file or directory
   ```

   The shell then refuses at `:212-219`: "comparator exit 4 is not a completed comparison; no
   durable record published", exit 4.

**Consequence.** At `46691bbc` the coupled chain runs both measurements — the script itself puts
the canonical pass at "42-47 min" (`:120`) — and then refuses, producing **no F-17(b) record at
all**. The prior grade's state was "completes, with two named schema gaps in the record". The repair
converted that into "cannot complete". The direction is fail-closed, which is the safe direction and
is to the repair's credit; but F-17(b) is now mechanically undischargeable by this instrument rather
than incompletely discharged.

**Why this was not caught.** `grep` over `PROPOSAL-20260828-f17b-four-surface-repair.md` and
`DECISION-20260828-joseph-f17b-four-surface-repair.md` for `CODE_ROOT`, `frozen`, `aa67c426`,
`MEASURER`, `predecessor` returns **zero hits in the decision** and one unrelated hit in the
proposal (`:84`, about the durable record's routes). Neither document asks which copy of the
measurer executes. No test covers it: the 100-test suite exercises the measurer via
`sys.executable` against `_HERE / "measure_m1_m6.py"` — i.e. always the repaired local copy, never
the `CODE_ROOT` copy the shell names.

**The file documented its own trap and the repair edited around it.** `measure_k0_farend_f1b_f17b.sh:125-127`,
unchanged by a commit that edited `:174-179` and `:221-230` of the same file:

> `# The RULER. measure_m1_m6.py is byte-identical in the frozen deploy and on main (measured`
> `# 2026-08-25: sha256 0fcd90f7...), so which copy is used does not change the numbers -- but it is`
> `# recorded anyway, because "identical today" is a measurement and not a property.`

That claim is **false at `46691bbc`**: main's copy is `ce52ff77…`/14108, the frozen deploy's is
`0fcd90f7…`/13213. The comment's own closing clause names precisely the failure that occurred.

**Note on the same file's `:129-132` rationale:** the comparator is deliberately *not* in the frozen
tree, "built after `aa67c426`, so it cannot be", and is invoked from a live checkout. The measurer's
two new fields were also built after `aa67c426` — the same reasoning applies to them and was not
applied.

Adjacent, and I flag it as **untested** rather than assert it: I did not read the canonical checkout
`CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold` (`:137`), so I cannot say what revision it carries.
It is moot — `$MEASURER` is the frozen copy for both trees — but if a future fix routes the measurer
through `TOOLS_ROOT`, the canonical side becomes a second surface to check.

### N2 — not independently sufficient. Surface 3's refusal action has no failing arm.

`test_measure_m1_m6.py:FarEndShellFailsClosedAroundTheRepairedSurfaces.test_preserver_digest_is_bracketed_across_its_own_invocation`
asserts only **substring index ordering** in the shell source: `PRESERVER_PRE=` < invocation <
`PRESERVER_POST=` < the `if` < the `prc` check. It never asserts that the mismatch branch *exits*.

Measured: replacing the drift branch's body
```
    echo "  REFUSE: the durable-record helper changed on disk across its own invocation."
    echo "          scratch output remains at $OUT for diagnosis."
    exit 13
```
with a bare `echo "  NOTE: ..."` — i.e. **downgrading the newly approved refusal to a warning that
lets publication stand** — leaves all **100 tests green**. The test asserts on the wrapper that
carries the guard, not on the payload. Contrast surface 4, whose test pins `exit "$rc"` literally
and dies under the equivalent mutation (M15).

The shipped bytes are correct (`:226-230` does `exit 13`). This is a coverage defect, not a live
behavioural one — which is why it is not independently sufficient.

Two related observations on the same surface, neither sufficient:

- **The drift refusal fires after publication, and does not say so.** Order at `:221-234` is PRE →
  invoke → POST → print → `if PRE != POST → exit 13` → `if prc != 0`. A preserver swapped across
  its own invocation is now *detected* (which is what the prior grade asked for), but the durable
  record may already exist at `$DURABLE_RECORD`. The exit-13 message says only "scratch output
  remains at `$OUT` for diagnosis" — it does **not** name `$DURABLE_RECORD` as suspect, whereas the
  comparator's bracket at `:207-208` correctly says "Nothing published". Detection without
  containment is inherent to bracketing a side-effecting call; the silent message is not.
- **The dry run cannot exercise it at all.** The whole preserver block is inside
  `if [ "$MODE" = "--measure" ]` (`:211`), so `--dry-run` never reaches `:221`. Combined with the
  text-only test, surface 3 has **zero behavioural exercise anywhere** in the repository.

### N3 — not independently sufficient. Surface 1's "real" property has no failing arm.

Measured: changing `measure_m1_m6.py:275` from
`res["measurement_wall_clock"]["completed_utc"] = utc_now()` to `... = started_utc` — collapsing the
interval to a single stamp emitted twice, defeating the word "real" in the decision's surface-1
title — leaves all **100 tests green**. The only clock arm,
`test_measure_m1_m6.py:test_branch_and_measurement_interval_are_emitted`, asserts
`assertLessEqual(started, completed)`, which equality satisfies.

Aggravating, and measured: real invocations against small fixture trees already emit
`started_utc == completed_utc` (`2026-08-28T13:59:07Z` for both), because `utc_now()` is
one-second precision. So in the fast case the emitted interval is *indistinguishable* from the
mutation. On the real trees the pass is minutes (`:120`, "42-47 min"), so an arm with an
artificially slowed measurement is entirely feasible and would fire.

The comparator's side of this guard is better: the opposite direction (`completed < started`) **is**
tested and mutation-killed.

### N4 — not independently sufficient. The mandated `1 → 2` version bump is untested.

Measured: reverting both `compare_m1_m6.py:137` to `"mnv_m1m6_comparison/1"` and `:139` to
`INSTRUMENT_VERSION = "1"` leaves all **100 tests green**. The only version assertion,
`test_compare_m1_m6.py:1421`, is `assertEqual(record["instrument"]["version"], cm.INSTRUMENT_VERSION)`
— the record echoing the module constant, a tautology that holds for any value.

The decision states the bump as an implemented behaviour, so it should have an arm. Mitigating, and
why this is not sufficient: I grepped the repository for `mnv_m1m6_comparison` and found exactly two
occurrences — `compare_m1_m6.py:137`, and `state/f17b-k0-aa67c426-20260824T145751Z.json:2` which
correctly still reads `/1` (the already-filed record, properly left identifying its own bytes).
`preserve_f17b_record.py` does not validate the schema string. So no live consumer reads it, and a
`/1` record is distinguishable from a `/2` one by field *shape* anyway (string sentinel vs. object).

### N5 — not independently sufficient. Four sub-guards on surface 2 are untested.

All four are **correct in the shipped bytes** and all four survive mutation with 100 tests green:

| Mutation | Guard neutralised | Suite |
|---|---|---|
| M4 | `compare_m1_m6.py:435` state enum `{branch, detached, not-a-git-checkout}` | green |
| M10 | `:430` `branch_or_detached` shape (exactly `{state, name}`) | green |
| M11 | `:438` the "a branch must carry a non-empty string name" half | green |
| M13 | `measure_m1_m6.py:186` the `not-a-git-checkout` state — **the third of the three states the decision names is never produced by any test** | green |

I verified the enum guard works behaviourally: `{"state":"garbage","name":null}` → exit **4**,
"invalid branch_or_detached state 'garbage'". And the clock format guard: an ISO offset
(`2026-08-28T10:00:00+00:00`) instead of `Z` → exit **4**. The same survival result holds for
`compare_m1_m6.py:416` (M9, clock shape). These are below the granularity the SPEC's own §4 controls
demand, which is why they are recorded rather than treated as sufficient.

### N6 — not independently sufficient. An undeclared stale pin in a live input file.

`m1m6_expected_differences.json:19` (`2e5f3d52…`) states its accepted-pattern grammar was
"transcribed … by RUNNING `bad_pattern` at `compare_m1_m6.py = 5dc92487` rather than by reading it."
`5dc92487…` is the **pre-repair** comparator. The decision's pin-supersession table
(`DECISION-20260828…:34-37`) lists two pin surfaces — §11 of `DECISION-20260825…` and
`receipts/RECEIPT-20260825-terminal-watch-f17b-durability.json`, both of which I verified — and does
**not** list this third one.

Severity is low and I say why: I read the full `46691bbc` diff of `compare_m1_m6.py` and it touches
only the docstring, `SCHEMA`/`INSTRUMENT_VERSION`, `REQUIRED_KEYS`/`IDENTITY_KEYS`, `load_document`,
`identity_of`, and `input_schema_gaps`. `bad_pattern` and `parse_pattern` are untouched, so the
transcription remains **accurate**; and the note's own text says "IF THE CODE AND THIS NOTE DISAGREE,
THE CODE GOVERNS AND THIS NOTE IS THE DEFECT". Unlike the many `5dc92487` references in
`GRADE-20260825-*.md`, `CATALOG.md` and prior verdicts — which correctly identify the bytes *they*
graded and must not be repointed — this one sits in a **live instrument input**.

### N7 — not independently sufficient. The bracket cannot distinguish "no movement" from "no measurement".

`measure_k0_farend_f1b_f17b.sh:221,224`: `PRESERVER_PRE=$(sha256sum "$PRESERVER" 2>/dev/null | awk '{print $1}')`.
If `sha256sum` were unavailable, PRE and POST are both empty, `empty != empty` is false, and the
bracket passes silently while the log prints `pre=   post=`. This is an empty-vs-empty comparison in
newly added code. It applies equally to the three pre-existing brackets at `:167,181,192,197,198`.
Not sufficient: `sha256sum` is used elsewhere in the same script (`:66,68`) and is coreutils-standard
on the target, and the *deletion* direction is caught by the `prc` arm.

Recorded for accuracy of the decision's own wording: surface 3 uses the **full 64-hex** digest, so
the decision's phrase "takes full sha256 values" is exactly right for the preserver — but the three
brackets beside it compare `cut -c1-12`, a 48-bit prefix. `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md:558-559`
already records that as a non-graded finding, so it is pre-existing and out of this repair's scope; I
note it only because a reader of the 2026-08-28 decision could over-read "full" as describing the
script.

---

## 5. What I could not test — untested items, not caveats that read like passes

1. **SPEC R5 at n ≥ 3.** My three-input fixture was degenerate: I built three documents intending
   pairwise-consistent-jointly-inconsistent and failed to perturb the values, so the run returned
   `NO-DIFFERENCES` and measured nothing about the requirement. **R5 is unverified by me.** The
   field `global_agreement_inferred_from_pairs: False` exists at `compare_m1_m6.py:944` and the
   implementer's suite covers it, but I do not convert someone else's green into my measurement.
2. **`measure_k0_farend_f1b_f17b.sh` was never executed** — prohibited by the decision, and I did
   not run it. Surfaces 3 and 4 were graded by reading the source, by mutation of the *tests*, and
   by `bash -n` (syntax only, no execution; exit 0 under local bash 3.2.57). I did not verify at
   runtime that `exit "$rc"` inside the `for` loop terminates the script — it is a plain loop, not a
   subshell or a pipeline, so it does; that is a reading, not a measurement.
3. **The frozen deploy tree on the cluster was not read**, per SPEC §5 ("Do not touch the frozen
   tree. You do not need to."). N1's frozen-side digest comes from the git blob at `aa67c426` plus
   the script's own `:126` record, which agree exactly. **Falsifier, stated so N1 can be attacked:**
   if `/pscratch/sd/j/josephrb/k0r2/clean/docs/orchestration/measure_m1_m6.py` is not `0fcd90f7…`
   at run time, N1's premise fails — but then `:70` would print `*** DIFFERS ***` and the §7.0.19
   freeze would already be broken, which is a larger finding, not a smaller one.
4. **Interpreter and shell mismatch.** The suites passed on local Python **3.12.2**; the target is
   **3.11.14**. I did not run them on 3.11.14, so I make no claim about 3.11 behaviour of
   `datetime.datetime.now(datetime.timezone.utc)` or `strptime`. Local bash is **3.2.57**;
   Perlmutter's is **4.4**. A 3.2 `bash -n` pass is the stricter check for old-syntax rejection but
   says nothing about 4.4-only semantics.
5. **Exit code 10** (differences-all-expected) was not measured by me; I measured 0, 4, 5, 20.
6. **The canonical checkout's revision** was not read (see N1's closing note).
7. **`generate_manifest.py --check` was not run.** I verified MANIFEST coupling by reading the
   `lines`/`bytes` columns instead, because a `--write`-capable generator can silently change rows
   and I am forbidden to write in the repo. My check cannot detect a byte-and-line-preserving
   content change.
8. **Byte-identity of the three unchanged chain files** rests on comparing my measurements to the
   prior verdict's digest table. If that table were itself wrong, three of my eight rows inherit the
   error; I did not independently re-derive them at the prior tip `7d13066e`.

---

## 6. Where I disagree with the commissioning session and with the prior verdict

### With the commissioning session

1. **Its framing treats the predecessor-refusal as purely a safety feature. It is also the mechanism
   of N1.** The brief instructed me: "Predecessor measurement documents lacking producer-captured
   identity fields must be REFUSED rather than silently upgraded — test that." I tested it and it
   works (exit 4, mutation-killed). But the brief, and the decision it relays, never ask **which
   documents this run can actually produce**. Under the §7.0.19 freeze the answer is: only
   predecessor documents. So the refusal that both documents present as the correct fail-closed
   behaviour is exactly what makes the chain unable to complete. I disagree with the framing, not the
   behaviour.
2. **"Grade against the SPEC" and "grade the four surfaces" are not the same instruction, and the
   brief conflates them.** Surfaces 1 and 2 map onto SPEC R6 and R3. Surfaces 3 and 4 map onto
   *nothing* in R1–R8 — they answer the prior grade's Item C, which are chain-integrity findings. I
   graded both and kept them in separate tables rather than reporting shell findings as SPEC
   nonconformances, which would have overstated the SPEC's reach.
3. **On the retractions it disclosed:** its self-reported errors (misattributed launcher refusals,
   the `--expected-ids` directory mis-scope, the digest check that read no files) are all in the
   OI-160 subject area and none of them touch this chain, so they did not propagate into what I
   graded. I verified the third class does not recur here by running an explicit negative control on
   my own digest instrument (§1). Its two commits that landed during my grade (`d5493bf5`,
   `6eb70aa3`) changed no chain file, and `d5493bf5`'s measured line citations —
   `compare_m1_m6.py:209`, validators at `:416-441`, `measure_m1_m6.py:268-275`, `:177` — agree
   exactly with mine.
4. **I agree with it on one contested point:** it was right that the decision's four surfaces are
   implemented as described. My NOT FIT does not contradict that; it rests on a fifth thing nobody
   specified.

### With the prior `agy-capacity-probe` verdict

1. **I AGREE with both of its SPEC bases and confirm both are repaired.** Its §5 (symbolic-ref →
   R3) and §7 (timestamp → R6) were correct, and each is now conformant with a mutation-killed arm.
   Its Item C findings were also correct and both are now implemented. **This is a good prior
   grade** and I reached the same two SPEC conclusions independently before reading its supplement's
   numbers.
2. **I DISAGREE with the stated ground of its §4.** It concluded the measurer-failure gap was "a
   MISSING IMMEDIATE SHORT-CIRCUIT / WASTED WORK defect, NOT a fail-open chain", reasoning: "If the
   measurer fails, it produces empty or invalid JSON. The comparator then `exit 4` … The preserver is
   never called." The *conclusion* is right. The *ground* is narrower than it knew: it treated the
   comparator's exit-4 as a reliable backstop against a failed measurer, without asking whether
   exit-4 could also fire on a **successful** one. N1 shows it now does. The reasoning was sound
   about the case in front of it and blind to the adjacent case.
3. **I note an internal tension it did not reconcile.** Item D point 1 says the mechanism "**CAN**
   meet its clause with [symbolic-ref] absent"; its §5 calls the same absence "a **SPEC
   NONCONFORMANCE** and … a separate, independent NOT FIT basis". Both sentences are in one
   document. §5 (the later, prompted one) is the one I agree with; a reader quoting Item D alone
   would draw the opposite conclusion.
4. **On its recorded weakness** — the supplement abbreviates fixture paths as `/tmp/...`, so it is a
   grader output and not an exact replay receipt. I did not rely on it. I independently reproduced
   its B1 (identical inputs → **0**), B2-equivalent (unexpected field → **20**), B3 (M-2 → **20**
   with a distinct perishability line), B4 (absent input → **4**), B5 (unresolvable citation →
   **5**), and B6's clobber refusal (second publish to the same destination → **13**, `[Errno 17]
   File exists`). **All six exit codes reproduce**, on my own fixtures with full paths. Its numbers
   are trustworthy even though its receipt is not replayable.

---

## 7. What would change this verdict

N1 is the only independently sufficient basis, and it is a wiring defect, not a design one. The
narrowest fixes I can see — offered as observations for whoever writes the next proposal, not as
authorization:

- Route `MEASURER` through `TOOLS_ROOT` (as the comparator already is, for the reason stated at
  `:129-132`) while keeping `--tree "$CODE_ROOT"`, so the *ruler* is the repaired revision and the
  *measured tree* is still the frozen one. That is what "measure the frozen tree" requires; it does
  not require running the frozen tree's copy of the ruler. Then re-check `:125-127`'s comment.
- Or add a pre-flight arm that digests `$MEASURER`, compares it against the schema the comparator
  requires, and refuses **before** the 42-47 minute pass rather than after — which is the
  scoped-out `measuring_instrument_digest` gap, arriving as a shell precondition instead of a
  record field.
- N2–N7 are each cheap and none blocks: an arm asserting the drift branch exits; an arm with a
  slowed measurement asserting `completed > started`; literal assertions on `"…/2"` and `"2"`;
  arms for the state enum, the two shapes, the branch-name half, and a non-git fixture; a dated
  successor row for `m1m6_expected_differences.json:19`; and a `[ -n "$PRESERVER_PRE" ]` guard.

**Restating the ceiling, because a NOT FIT is sometimes read as the only thing a grade can move:**
nothing here discharges or advances any Gate-2 clause. Gate 2 remains **FAIL**, readiness remains
**NOT READY**, no scalar-5D covariance is adopted, no rehearsal is authorized, and no compute is
authorized. Had I returned FIT, that list would read identically except that a proposal for a new
forward-only rehearsal would have become writable.

---

## 8. Reachability

Completed: digest verification with negative control; independent derivation of the eight-file set;
MANIFEST coupling check with a control; all three suites run read-only (100 tests, OK); 15
mutations across the comparator, the measurer and the shell; 12 behavioural fixture probes; a
fixture replay of the frozen measurer into the repaired comparator; pin-supersession verification;
repository-wide stale-digest sweep; re-measurement after HEAD moved.

Not reached: SPEC R5 (§5 item 1); exit code 10; runtime execution of the far-end script; the cluster
paths; Python 3.11.14 and bash 4.4.

Prohibitions honoured: fixtures only; `measure_k0_farend_f1b_f17b.sh` never executed; no rehearsal,
no compute, no Slurm, no gate change; **nothing written inside the repository** — all scratch work,
including this verdict, under
`/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/722f92c5-be70-4eee-86d7-938026ec6cfd/scratchpad`;
no `git commit`, `push`, `add`, `stash`, worktree creation, or any other git mutation; the frozen
tree was not read; `$?` was never read after a pipe for any status I report.
