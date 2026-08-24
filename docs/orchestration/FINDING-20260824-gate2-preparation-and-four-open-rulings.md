# FINDING — Gate 2 prepared, and four questions about what Gate 2 MEANS that a lane may not answer

**Author:** the third grading lane (fresh non-builder; did not build the work, did not write §7.0, did
not write §7.0.17), briefed by the coordinating lane on 2026-08-24 while the k=0 rehearsal was in
flight. **Recorded by** the coordinating lane, which wrote §7.0.17 and is therefore ineligible under
§7.0.10 to grade against it.

**CITABLE FOR:** the Gate-2 clause list and its per-clause settling instrument; the state of the
rehearsal as measured 2026-08-24; four open questions that need a ruling before Gate 2 can be graded.

**NOT CITABLE FOR:** a Gate-2 verdict. **No clause below is graded.** Two clauses are blocked on the
far end by design and three are blocked on something else — see §2.

## 1. The clause list, derived rather than inherited

**Gate 2 = 10 clauses: F-1(b), F-2(b), F-3(b), F-4(b), F-5(b), F-6(b), F-7(b), F-8(b), F-17(b),
F-18(b).** Derived from the POST-REHEARSAL column of §7.0.5 by reading its class cells: 10 non-empty,
8 pure PRE-SUBMISSION (F-9…F-16), 0 pure POST-REHEARSAL, 8+10+0 = 18. **§7.0.5's own stated arithmetic
agrees exactly.** No other section creates a Gate-2 obligation: §7.0.7 lands on F-14/F-15
pre-submission, §7.0.13 on F-2(a)/F-4(a), and §7.0.12 and §7.0.17 on F-9/F-12, both pure
pre-submission.

**This confirms the `F-3(b)` omission independently.** `CATALOG.md` enumerated Gate 2's debt as
*"F-1(b), F-2(b), F-4(b)–F-8(b), F-17(b), F-18(b)"* — nine clauses, jumping F-2(b) to F-4(b). Two
lanes now derive ten. The router is annotated at `e1596f00`; **derive the list from §7.0.5, never from
a summary.**

## 2. Status per clause, and the distinction §7.0.8 forbids collapsing

§7.0.8: *"A NOT-EVALUABLE in the PRE-SUBMISSION column is a FAIL … a missing instrument is the defect
— not a reason to defer."* Applied to Gate 2, that makes **"the input has not landed" and "the
instrument does not exist" two different verdicts**, and they are separated here deliberately.

| clause | status | why |
|---|---|---|
| F-2(b), F-3(b), F-5(b) | **instrument armed, value awaits legs 2–5c** | ratchet and greps exercised now, with firing negative arms and silent-on-good positive arms |
| F-1(b), F-17(b) | **blocked on the far end BY DESIGN** | the both-ends re-measurement; this is what §7.0.6 names |
| F-4(b) | blocked on the far end **and ambiguous** | ruling 2 below |
| F-7(b) | set half armed; **exclusion half has no instrument** | ruling 3 below — a §7.0.8 FAIL surface, not a pending input |
| F-8(b) | input not landed (receipt not yet authored); **bench half filed** | not instrument-missing |
| F-6(b) | **structurally unsatisfiable in Gate 1's scope** | ruling 1 below |
| F-18(b) | structure ready; verdict awaits the other nine | — |

**Instruments verified present and non-vacuous, so Gate 2 is not tooling-blocked:**
`mnv_source_manifest.py`, `mnv_import_set_ratchet.py`, `mnv_preflight_census.py`,
`measure_m1_m6.py`, and the launchers' in-line `verify_executing_copy_is_committed.py` parity gate.
Each was run with a firing negative arm **and** a silent-on-good arm. Notably the ratchet's
anti-vacuity is **implemented, not argued**: an empty inventory directory returns **rc=2**, *"zero
inventory records … this is never a clean result."*

**Rehearsal state, measured 2026-08-24 (`squeue`/`sacct`, not a process list):** leg 1 `boot5dG`
100/100 COMPLETED; leg 2 `ssplit5d` 2 COMPLETED, `[3-24%24]` PENDING; leg 3 `det5dBKG` 8 COMPLETED /
8 RUNNING / `[16-18]` PENDING; legs 4, 5a, 5b, 5c PENDING. 110 inventory records so far, **all** with
`script_checkout_root` = the clean tree, `checked` 974–1164, **zero** with `checked == 0`, all with
`allow_is_empty=true`. `grep -rIl -- "--allow"` over 239 log files: **0 hits, and the same grep for
`oi136` hits 228 files**, so the null is about the world rather than about the search.

## 3. FOUR RULINGS NEEDED. A lane may not make any of these; they change what a gate means.

### Ruling 1 — F-6(b) is unsatisfiable within the scope Gate 1 unlocks, so **Gate 2 cannot pass as written**

§7.0.6: a Gate-1 PASS *"unlocks exactly one thing: submission of the seven jobs of logical legs 1–5"*,
and leg 6 *"stays separately gated."* F-6(b) requires the B-2 pinned-writer child's record to be
present in the run's inventory. **Measured:** `adopt_unified_5d.py` and
`mii_adopt_unified_5d_stamped.py` appear in **exactly one** of the eight in-scope launchers —
`sbatch_finalize_5d_bkgaware_gpu.sh`, holding 5 of the 14 guarded invocations — and it was **not
submitted** (`finalize_submitted=NO`).

**Under §F's no-partial-credit rule, Gate 2 therefore FAILS on this rehearsal regardless of execution
quality.** This is §7.0.8's own shape at **gate** granularity rather than clause granularity, and
§7.0.8 forbids calling it a deferral. **Two dispositions, and the choice is Joseph's:** scope F-6(b)
out of Gate 2 and into a leg-6 gate, or define Gate 2 over the remaining nine. **Neither is a lane's
call, and neither should be settled by grading around it.**

### Ruling 2 — F-4(b)'s "count of guarded processes" has no stated population, and the two readings disagree

F-4(a) fixes the denominator at *"14 launcher-level science invocations plus the pinned-writer
child"* — a **per-launcher** count of 15. F-4(b) says *"count of inventories == count of guarded
processes"* — a **per-process** count, which is array-multiplied and which **excludes the 5 finalize
invocations that never run**. **Neither number appears in the contract.** Recommended settling form,
with the class named beside the number: inventories = one record per *process* (the launcher's own
comment says *"THE INVENTORY IS ONE FILE PER PROCESS, NOT ONE PER RUN"*); denominator = Σ over the
seven submitted jobids of (array cardinality from `scontrol`) × (guarded invocations in that launcher
from `mnv_preflight_census.py`).

**A live pooling hazard that would be a well-formed query over the wrong rows:** four run directories
exist under `runs/`; three hold **zero** `.jsonl`, and `sacct` shows a **superseded attempt-1 family**
(`57526062`–`57526066`) with 97 boot FAILED, 19 det FAILED, 2 CANCELLED. **A `runs/*/inv` glob would
silently pool them.** Scope `--inventory-dir` to the single attempt-2 path
`k0-aa67c426-20260824T145751Z`, which itself records `supersedes=…T143517Z (attempt 1, 0 products)`.

### Ruling 3 — F-7(b)'s exclusion half is not armed, and the instrument cannot express it

§7.0.15 requires the §7.0.13 preflight exclusion to be pinned **with** the import set *"so that the
exclusion cannot widen unnoticed."* **Measured:** the `--write-pins` artifact carries exactly two keys,
`{"entrypoints", "schema"}` — **no exclusion field of any kind** — and grepping the ratchet for
`exclusion|preflight|mnv_preflight` returns 0 lines. The exclusion lives in a separate, unbound file
(`nd-unfolding/mnv_preflight_exclusions.json`, sha256 `2d4ee2e9e604…`).

**So comparing two pin files across runs would not notice a widened exclusion — the guarantee §7.0.15
asks for does not exist.** Per §7.0.8 this is a **missing instrument, not a pending input**, and
therefore a Gate-2 FAIL surface unless the pin artifact is made to carry the exclusion digest before
the far end. **Filed as a repairable defect and NOT as a disclosure**, because writing it into a
caveat register would launder a fix into a caveat. It is a small change to the pin writer; it is
outside §6's authorized set, so it needs authorization rather than initiative.

### Ruling 4 — F-1(b)'s "the manifest digest" is not a well-defined quantity, and two files already disagree

Two A-2(f) manifests exist for `aa67c426`: the **declared** one (file sha256 `622ddc0ada33…`,
`built_at_utc 04:00:20Z`) and the **run's** `MNV_SOURCE_MANIFEST` (file sha256 `b46e4f576646…`,
`built_at_utc 14:57:52Z`). Their `diff` is **4 lines — the `built_at_utc` line only**;
`listing_sha256` (`fa3489e2…`), `file_count` (782) and `head` are identical.

**So a grader comparing *file* digests at the two ends sees a difference that carries no information,
and one comparing `listing_sha256` sees none. F-1(b) must name `listing_sha256`.** Second point, and
it is the sharper one: the run manifest was built at 14:57:52Z and submission was 14:58:01Z — **nine
seconds** — which is the state the launcher's own error text forbids (*"comparing against a manifest
generated now would compare the tree to itself"*). **F-1(b) should `--compare` against the
`declarations/aa67c426` baseline, not against the run's own copy.**

## 4. Two corrections to the record, one of them to this lane's own report

**(a) The lane's finding "§7.0.17 is not committed anywhere" was TRUE WHEN MEASURED AND IS NOW FALSE
— a timing artifact, and it is worth keeping rather than deleting.** The lane measured 19 refs and
found `grep -c '7.0.17'` = 0 on every one, with `main` at `27d5a7d4`. **That was correct: the
amendment was an unstaged working-tree modification when the lane started.** It landed at `e1596f00`
during the lane's run, and `main` now carries it (8 occurrences, contract sha256 `e34cdc76…`, 1293
lines). **The lane was right about the tree it measured and right to refuse to be bound by
uncommitted text** — `CLAUDE.md` says a result is live only once it lands in a commit. **The
transferable part is that a delegated measurement is bound to the sha it ran against, and a
long-running lane's "not present anywhere" can expire mid-run.** Bind a lane's finding to a sha, and
re-check any absence claim against `HEAD` before acting on it.

**(b) The divergence the coordinating lane recorded was real but mis-stated, and the lane found the
larger one.** `main` and `build-k0-execution-integrity` were byte-identical at `e0fb342b…` when the
lane looked; they diverge **now**, after `e1596f00`. **But the more important measurement is the
lane's:** `contract-f9-restatement` (`8e4878eb…`), `review-contract-k0-integrity` (`80402f75…`) and
`verify-k0-execution-integrity` (`504803c2…`) each carry **different contract bytes**. **That is a
three-way divergence nobody had named, and it is not the two-way one the brief described.** Grade
against path + digest + sha, and treat "the contract" as a definite description that re-points.

## 5. DISCLOSURE — two of my own commits are red on `generate_manifest.py --check`, and the fix is one line of procedure

**Stated here before anyone finds it.** `e1596f00` and `585b1f3a` each ADD a document and each carry a
`MANIFEST.tsv` row for that document reading **`tracking=intended`** — for a file the same commit
**commits**. So `--check` at those two shas returns **rc=1**, bracketed by green at `2e805d6f` and
`eb3a417e`. This is the exact pattern already recorded against `82727fe3`: a pushed commit red on
`--check` with green on both sides.

**Cause, measured rather than guessed.** `generate_manifest.py:92` computes the tracked set as
`git_lines("ls-files", "--", "docs/orchestration")`, and **`git ls-files` reads the INDEX.** So a file
that is written but not yet `git add`ed is `intended` at regeneration time and `tracked` the instant
the commit lands — the row is guaranteed stale for any newly-added file. **The second mechanism is
separate:** `MANIFEST.tsv` carries its own `bytes` cell, so writing it perturbs the value it reports
(98425 → 98424 in one observed pass).

**THE FIX, VERIFIED IN A THROWAWAY REPO RATHER THAN REASONED ABOUT: `git add` THE NEW FILE *BEFORE*
REGENERATING.** Measured on a scratch `git init`: a new file under `docs/orchestration` appears only
in `ls-files --others` before `git add`, and in **`ls-files`** immediately after `git add` — *before
any commit*. So the correct order is:

1. write the documents;
2. **`git add <every path, including the new ones>`**;
3. regenerate the manifest — it now sees the new file as `tracked`;
4. `git add docs/orchestration/MANIFEST.tsv`;
5. **bare `git commit`** — never a pathspec, because the generator reads working-tree bytes only
   (three `read_bytes()` calls, no `git show`/`cat-file`/`--cached`), so a pathspec-scoped commit can
   publish a row describing content the commit excludes while `--check` still passes;
6. re-run `--check` **after** `git commit` returns, and quote only that rc.

**This commit uses that order, so it is the control.** Step 6 is the only measurement whose rc may be
put in a commit message — which is the half I got wrong twice today, once in the commit immediately
after writing the rule down.

**Not repaired by rewriting history, deliberately.** `e1596f00` and `585b1f3a` are published on shared
`main` with another lane's commit (`c9f331f0`) interleaved between them, and graders' verdicts cite
shas by line. **A force-push would dangle those citations to fix a stale cell in a generated index.**
The rows are correct at `eb3a417e` and forward; the two shas are disclosed here instead.

## 6. What this lane did NOT do

No file was edited, no job launched or cancelled, nothing committed by it. The held scron
`57275989` (`Reason=user_env_retrieval_failed_requeued_held`, `Restarts=199`, unchanged) was
**flagged, not touched** — it is the supervision ticker, not a rehearsal leg.

**F-18 eligibility, stated so it can be checked:** this lane did not build the work, did not write
§7.0 or its split, and did not write §7.0.17. It remains eligible to record the Gate-2 verdict. **The
coordinating lane does not, and records neither the F-9/F-12 re-grade nor either Gate-2 verdict.**
