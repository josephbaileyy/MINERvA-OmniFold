# r22 paper pass 3: report (2026-10-31)

**Under** STEP2-PAPER.md §6, committed before any text of this pass and accepted by the director.

**Result:**
- **Option B is made.** It was decided, not judged: Table IV is in two blocks, χ² and ndf print in separate columns,
  and the caption is Joseph's.
- **The three deferred gaps are not adopted.** NEW lost all four blind comparisons to BASE′, so the paper keeps their
  base text.
- **The paper's P1 is 3, 3, 3** (BASE′'s, the adopted paper's), as in passes 1 and 2.
- **The paper's register rounds stop** (STEP2-PLAN.md §5). This was the third round without movement, against a
  target of 3.667. The director takes this to Joseph.

Nothing is submitted, deposited or tagged.

## What was judged

**The two texts:**
- **BASE′** is the base `4121f185d60d` with change (i), Option B, only. It is commit `e10c4c08`
  (`docs/r22-paper-pass3-baseprime-20261031`).
- **NEW** is BASE′ with the three gaps, each in the independent review's narrowed form, and with the two-direction
  review's five fixes. It is commit `1405c8a3`. The gaps:
  - **paper-g-03:** the FROZEN coverage sentence joins the validation discussion, verbatim, in its original place
    (R3-5).
  - **paper-g-02:** five iterations are kept because none of the larger counts in the cited comparison reduced the
    residual proxy. The counts are in the note (R3-3).
  - **paper-g-06:** only the precision-target discussion leaves the paper, with each fact homed in `sec_5d.tex`. The
    envelope's size and meaning stay, as does the limitations' pointer to the target (R3-1, R3-2, R3-4).

**The rater copies** were cut from each committed tree immediately before the runs (`base-prime/`, `new/`; hold diff
PASS). `KEY-PROOF.txt` shows:
- Option B prints in both;
- each gap rewrite prints in NEW;
- each cut phrase is gone from NEW and still printed in BASE′.

**Checks before the runs (§6.3):**
- **Ledger** (`check_paper3.py --all-rows`, on NEW): 6 rows, 17 probes, 11 changed sentences, 0 failures. KEEP F109 is
  named; self-test PASS.
- **Held** (`check_held.py --fact-held`): 14 exact, 8 held for facts, and G1b:paper-s-05 exempt by its applied A1
  pair; 0 failures.
- **Option B's number probe** (`tools/check_table_macros.py`): 21 numbers, each its macro, in both BASE′ and NEW.
- **The two-direction review** (`review.md`): 5 findings, all fixed. Nothing was lost, weakened, added or beyond its
  narrowed form.
- **agy, on the final text** (`agy2/`, `agy-triage.md`): the control caught 3/3 and the identity fillers read SAME.
  Every DIFFERS is a declared change with its home.
- **Local CI:** 37 steps, 0 failed.

## The runs (`runs/`)

- **sol** (gpt-6.1-sol) ran on **codex-school**: `SOL_RX=sol`, recorded per run as `key=sol` in `status.tsv`. Its
  calls went one at a time, with nothing else on the account.
- **gemini** ran through agy, after sol.
- All 10 runs answered on the first attempt.

| run | outcome |
|---|---|
| P2 sol AB / BA | BASE′ in both orders (STRENGTH 1, 1) |
| P2 gemini AB / BA | BASE′ in both orders (STRENGTH 2, 2) |
| P1 NEW ×3 | 3, 3, 3 |
| P1 BASE′ ×3 | 3, 3, 3 |

**Adoption** (`runs/adoption.tsv`, `tools/adopt_step2p.py`, recomputed byte-identically from the committed `.txt`
copies): NEW won 0 of 4 P2 runs. sol did not flip, and NEW's P1 equals the base's, but the P2 rule fails. **NEW is not
adopted.**

**Why the raters preferred BASE′, in their own reasons:**
- **sol:** "A explains the iteration choice in direct sentences, avoiding B's cumbersome and repetitive 'counts
  compared and the comparison'". "B's heavily interrupted 'With the joint-test estimator, over the reporting
  definitions' construction". "B interrupts the phrase 'precision target … in two of the three tested reporting
  definitions' with a citation".
- **gemini:** the same "counts compared and the comparison". It prefers the precision target defined in the body of
  Sec. III A, not a reference that depends on a citation. It also prefers the base's separate coverage paragraph.

So the wording the review's fixes needed to keep each fact true, R3-1, R3-3 and R3-4, is the wording the raters
marked down.

## The adopted paper

The adopted paper is BASE′. `paper_body.tex` equals `e10c4c08`'s: the base with Option B.
- **Ledger:** `check_paper3.py`, which after a non-adoption checks Option B's row only, gives 1 row, 5 probes and 0
  failures.
- **Self-test:** PASS. Its KEEP plant now rewords a KEEP item itself, so it tests check 8 on this paper too, which
  rewords none.
- **Option B's probe:** PASS (above).
- **The score** for the stopping rule is BASE′'s P1 mean, 3.0. That is no movement from 3.0, so the paper's register
  rounds stop.

## Tools changed in this pass, before any run

- **`step2p_runs.sh`:** `SOL_RX`, `RATERS`/`JOBS` and `P1_OLD`. A stub test gave 8 sol runs, `key=sol`, at most 1
  concurrent.
- **`check_paper.py`:**
  - its self-test's abstract anchors are a module constant, which pass 3's wrapper sets;
  - its KEEP plant rewords a KEEP item;
  - Step 2's configuration still passes its self-test at `f47b1b4a`.
- **`pass3/check_paper3.py`:** pass 3's base and ledger, empty `PAIRS`, the adopted-row filter and `--all-rows`.
- **`tools/check_table_macros.py`:** the number probe.

**One process incident.** A `make_rater_copy.sh` build left symlinks inside the worktree, and the pre-commit hook's
`verify_hash_bindings.py` spun on them for 21 CPU-minutes. The build is now moved out after each copy, and the
verifier then ran in 9 s.
