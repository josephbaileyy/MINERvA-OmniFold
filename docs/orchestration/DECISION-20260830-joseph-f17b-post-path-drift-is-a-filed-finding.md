# DECISION 2026-08-30 — canonical drift during the run is a FILED FINDING, not a defect to design around

**CITABLE FOR:** the disposition of `OI-178` recorded below, and for the two corrections in §4.
**NOT CITABLE FOR** any gate movement, for the content of the `F-17(b)` finding itself, or for a
standing policy about future rehearsals. **Gate 2 remains FAIL**; nothing is adopted; leg 6 was not
submitted.

## 1. Authority

Joseph, 2026-08-30, choosing among four options for the post-path `F-17(b)` operand capture:

> *"Yes do option 1, filing the correction and settling OI-178"*

Option 1 as put to him was: **let the finding be filed** — allow the canonical checkout to move
during the run, let `canonical-pre` versus `canonical-post` report the difference, and retain it as a
finding rather than preventing, repointing, or suppressing it. The three options he declined were
re-freezing the canonical tree for the life of the run, repointing the `F-17(b)` canonical operand at
a quiescent stand-in tree, and adding `M-4.dirty` to the expected-differences file.

**The option text is this lane's drafting, ratified by him.** He did not type it into the repository.

## 2. What this rests on — measured, not recalled

The disposition is not a judgement call about tolerable risk. It follows from three artifacts that
already say so, read directly rather than from summary:

**`compare_m1_m6.py:141-145`** — the exit vocabulary distinguishes findings from refusals:
`EXIT_NO_DIFFERENCES = 0`, `EXIT_DIFFERENCES_ALL_EXPECTED = 10`,
`EXIT_DIFFERENCES_SOME_UNEXPECTED = 20`, `EXIT_REFUSAL_INPUT = 4`,
`EXIT_REFUSAL_EXPECTED_LIST = 5`.

**`PROPOSAL-20260830-forward-only-rehearsal.md` §3** — requires `canonical-pre` versus
`canonical-post` as an explicit **time** comparison, states that *"Exit 0, 10, or 20 is a completed
comparison with its findings retained"*, and makes `F-17(b)` not-discharged on exactly three
conditions: a missing dedicated `M-2` result, an input-schema gap, or a comparator refusal. An
unexpected difference is none of those.

**`m1m6_expected_differences.json`**, entry `E1-m4-behind-drift`, on the very field at issue:

> *"NOT `M-4.head` or `M-4.dirty`: those are the tree's identity, and a difference in them is the
> finding `F-17(b)` asks for."*

So a canonical `M-4.dirty` move of **726 → 725**, when the dashboard lane lands the `OI-175`
collector-output fix, yields **exit 20 with a retained finding, and `F-17(b)` still discharges.**

## 3. Why the other three were declined

Option 2 (re-freeze) is the only one that would actually make pre and post match, and only by
preventing the change entirely — quiescing later does not retroactively align an earlier capture. The
run is 374 tasks with 12-hour arms under throttles; that is a multi-day hold on another lane, and this
lane had already released it. Options 3 and 4 both degrade the instrument to protect the appearance of
a clean result: repointing measures a stand-in and calls it the subject, and suppressing `M-4.dirty`
silences the field the file itself names as the finding. **The instrument was built to notice this.
Preventing it from noticing is not a fix.**

## 4. Two corrections to this lane's own records

**(a) `CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md` (`dfcb4d8f`) overclaims a citation.**
Its `OI-178` routing says the three options *"and their trade-offs are set out in the freeze record's
own preamble."* They are not. `FREEZE-20260830-canonical-quiesce-k0-7ac0edec.md` names the three
options in a **single sentence** under `## Authority` and gives no trade-offs at all. A reader sent
there would find a list and no analysis. The trade-offs are in §3 above; this is their first written
form.

**(b) `OI-178` as filed overstates the severity.** It describes the collision as *"the same shape that
produced the round-1 BLOCK"* and calls the failure mode *"scheduled."* That framing is wrong.
`F-17(a)` carried a **currency** requirement — the operand had to describe its subject at `sbatch`
time — and violating it was a FAIL, which is what produced `GATE1-VERDICT-20260830`'s BLOCK at 722
against 726. `F-17(b)`'s canonical-pre-versus-post is a **time** comparison in which drift is the
subject of measurement, and its consequence is exit 20 with a retained finding. **Read `OI-178` as
describing a filed finding, not a block.** The error was this lane's; no grader applied it.

## 5. What is authorized, and what is not

**Authorized:** the canonical checkout may move for the remainder of this run; the dashboard lane's
release stands; the `F-17(b)` post-path capture proceeds against the canonical tree as it actually
stands at that time; any resulting `M-4` identity difference is filed as a finding.

**NOT authorized by this record:** converting that finding into an expected difference after it is
observed (`PROPOSAL` §3 forbids it and this record does not relax it); editing
`m1m6_expected_differences.json`; releasing the deployment tree, which stays frozen detached at
`7ac0edec` under `§7.0.19` for the life of the run; any gate movement; leg 6; family work; or a
standing policy for future rehearsals. **The grader still weighs the finding.** This record settles
how the capture is *taken*, not how it is *graded*.
