# CENSUS 2026-09-02 — which leg-grade cells assert permanence, and which of them hide it

**CITABLE FOR:** the counts, the row table in §3, the exclusions in §4, and the structural observation
in §5.
**NOT CITABLE FOR** grading any leg, moving any cell, relabelling any token, changing §0's vocabulary,
or discharging anything. **This record measures text. It grades nothing.** Gate 2 remains **FAIL**.
CAND `1 of 7`, QUOTED `0 of 7`.

## 1. What this is, and why the framing matters

Joseph authorized it — *"yes do it"*, relayed by the `5d` lane, which dispatched the spec. **The relay
authorizes nothing that needed authorizing**: this is a read-only text survey of committed bytes, no
cluster compute, no cell moves.

**The framing inverts what this lane originally assumed.** This lane put enumeration to Joseph as the
**cost** of ruling for a fourth grading token; the `5d` lane put it as the **input** to that ruling, and
he took that. So the case for a fourth token is empirical — worth adding if a real population of cells
needs it, not worth it if the population is one. **This census is meant to decide the question, not to
follow it.**

**Disclosed leans, so a reader can discount both:** the `5d` lane leans AGAINST a fourth token; this
lane, after correcting itself once, leaned FOR one. **The result below cuts against this lane.**

## 2. THE COUNTS

| quantity | value |
|---|---|
| **denominator** — graded (cause × leg × artifact) cells | **46** (23 rows × 2 artifact columns) |
| **bucket (i)** — permanence asserted **and the cell carries it** | **1** |
| **bucket (ii)** — permanence asserted in the record, **cell reads bare** | **4** |
| cells in the permanence state at all | **5 of 46** |

Causes 5 and 7 collapse all four legs into a single row each, so 46 cells cover 7 causes rather than
7 × 4 × 2 = 56.

## 3. THE ROWS

**Bucket (i) — no harm; the cell communicates correctly.**

| document | line | cause | leg | column | token | verbatim |
|---|---|---|---|---|---|---|
| `SCOREBOARD-20260817` | `:78` | 4 | M | CAND | `OPEN` | *"**OPEN — AND IT CANNOT BECOME `MET`.**"* |

**This is the mandated positive control and the search returned it.** Had it not, the null would not be
reportable.

**Bucket (ii) — the decision-relevant population. All four are the QUOTED `P` leg.**

| document | line | cause | leg | column | token | verbatim |
|---|---|---|---|---|---|---|
| `SCOREBOARD-20260817` | `:68` | 2 | P | QUOTED | `OPEN` | *"**OPEN** — stamps `ABSENT`"* |
| `SCOREBOARD-20260817` | `:72` | 3 | P-i | QUOTED | `OPEN` | *"**OPEN**"* |
| `SCOREBOARD-20260817` | `:73` | 3 | P-ii | QUOTED | `OPEN` | *"**OPEN**"* |
| `SCOREBOARD-20260817` | `:77` | 4 | P | QUOTED | `OPEN` | *"**OPEN** — stamps `ABSENT`"* |

**Where the permanence is asserted for those four, verbatim:** `SCOREBOARD:5` and `:143` —
*"**THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION.**"* — and
`DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md` §2(b), *"unsatisfiable IN
PRINCIPLE … **This is permanent for X, not a gap awaiting work.**"*

> ⚠ **§2(b)'s STATED MECHANISM IS UNDER A STANDING FLAG** — it reaches that conclusion through a
> `git log -S` step refuted at `DECISION-20260902-two-lane-consensus-…` §4. Its substance survives on
> VL3–VL8. **Cite the conclusion, not the 36.5-hour reason.** The permanence claim itself is not
> disturbed; only one of its two supports is.

## 4. EXCLUDED, WITH REASONS — this is what makes it a census rather than a grep

- **`:64` cause 1 `P` QUOTED, bare `OPEN`.** Excluded because `SCOREBOARD:102-106` **explicitly carves
  cause 1 out**: *"§1's 'THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION' is sound for causes 2/3/4 and
  does not extend to cause 1."*
- **`:82` cause 6 `P` QUOTED, bare `OPEN`.** Excluded for the same reason: the permanence claim names
  causes 2/3/4 only.
- **`:73` cause 3 `P-ii` CAND** — contains *"value **CANNOT** be recorded on the dominant arm"*, but
  **names a remedy in the same cell** (*"remedy = a new write site"*), so it asserts difficulty, not
  permanence. **SEPARATELY FLAGGED, NOT RESOLVED: that premise was measured FALSE at HEAD** — four
  write sites exist. Not this census's to fix.
- **`:74` cause 3 `M` CAND** — *"**OPEN and NOT CURRENTLY MEASURABLE**"*. Explicitly temporary and
  costed at ~1 GPU-node-hour. **This is the census's best negative control: the board already
  distinguishes "not currently measurable" from "cannot become `MET`" in its own cell language.**
- **`:80` cause 5, `:85` cause 7** — `N/A ON ITS MERITS` and a third-artifact discharge. Inapplicability
  and scope, not permanence about a leg's measurability. Out of the spec's stated scope.

**Scope swept, so the null is covering.** Every document carrying per-leg grade cells was enumerated by
searching `docs/` for leg-column tables and for the grade vocabulary: the grade cells live in
`SCOREBOARD-20260817` (the artifact-separated board) and `CRITERIA-20260811` §3 (the older
mixed-artifact table, superseded for CAND). `docs/OPEN_ITEMS.md` and
`MAP-20260817-gbdt-note-section-blockers.md` were searched and hold **no per-leg grade cells** — one
token occurrence in the latter, in prose. The permanence-term list was run over all of them; **inside
the grade table itself only two rows match, `:73` and `:78`**, both accounted for above.

## 5. THE STRUCTURAL OBSERVATION, WHICH CHANGES WHAT THE NUMBER MEANS

**By the spec's own decision rule, `(ii) = 4` is "several" and the fourth token has an empirical case.**
This lane reports that plainly because it is the rule that was set in advance.

**But the four are not scattered — they are one column, governed by one statement, made twice and
prominently**, at `:5` in a warning box that precedes every cell and again at `:143`. So the harm is
**grep-scale, not read-scale**: a reader going top-to-bottom is not misled; a reader pulling a single
cell is.

That changes the remedy that fits. A fourth token would make those four cells self-describing — **but
so would a pointer in each cell**, at lower cost and without touching §0. Whereas `:78` is a
**single-cell fact with no column-level home**, and it is *already annotated*.

**So the population that a fourth token would help AND that nothing else already covers is 1 — and that
one is already handled.** This lane had argued FOR a fourth token and now reports a measurement that
cuts against its own position; the `5d` lane's lean is the one the number supports.

**This is a measurement and a structural reading, NOT a recommendation, and explicitly not a ruling.**
Whether "one column, one statement" is adequate governance is Joseph's call. **Neither lane may make the
token choice on cause 4's `M` in any case** — `BEN-381` bites, because both measured evidence bearing on
that leg.

## 6. A CORRECTION THIS CENSUS FORCES ON THIS LANE'S EARLIER NUMBER

This lane told Joseph the scheme *"declares three tokens and is running six"*. **The board runs seven
distinct forms:** `MET`, `OPEN`, `UNRESOLVED` (in `CRITERIA`), `PARTIAL`, `INAPPLICABLE`, `MEASURED` /
`MEASURED, not MET`, and `N/A`. Annotated variants (*"OPEN and NOT CURRENTLY MEASURABLE"*, *"OPEN — AND
IT CANNOT BECOME `MET`"*) are **not** counted as separate tokens; they are the annotation convention
working as intended.

> ### ⚠ AMENDED 2026-09-02, SAME DAY, after the `5d` lane verified this census against the bytes
>
> That lane independently re-derived the column mapping from the `:61` header before reading a row,
> confirmed all four bucket-(ii) rows, the positive control, both exclusions and the denominator of 46.
> **Two things came out of the verification. Neither changes §2's counts or §5's conclusion.**
>
> **A. AN OPEN SCOPE QUESTION — bucket (ii) was scoped to `P` legs, and that was a CHOICE.** The
> headline claim does not say `P`. `SCOREBOARD:5-8` reads: *"**THE QUOTED COLUMN CANNOT MOVE BY
> REMEDIATION** … X predates the stamping, so **'X gets replaced, not repaired.'** That is a structural
> fact about the deliverable, not a grading…"* — **an artifact-level mechanism, which on its own words is
> column-wide** and would also catch `:69` (cause 2 `M` QUOTED, bare `OPEN`) and `:78`'s QUOTED cell
> (cause 4 `M` QUOTED, bare `OPEN`), making the count **6**.
>
> **The counter is real, which is why this is a flag and not an erratum:** the claim's *evidence* is
> entirely stamp-specific — 4 keys against 13, every named stamp `ABSENT` — and stamps are the `P`
> criterion. *"Cannot move by remediation"* says the cell cannot be fixed by fixing the artifact; for `M`
> the question is whether a magnitude measurement can be **taken** on X's inputs, which is not obviously
> blocked by X being unrepairable. **`P`-only is defensible and may well be right.**
>
> **Resolving it means judging whether `M` is measurable on X, which is grading a cause-4 leg, so
> `BEN-381` bites both lanes exactly as it did on the cell.** Routed to a clean lane; resolved by
> neither. **Credited to the `5d` lane.**
>
> **It does not change §5's answer, and if anything strengthens it:** at 6 the hits are *more* uniformly
> one column under one statement, so *grep-scale not read-scale* holds harder. The decision-relevant
> number — cells a fourth token would uniquely help that nothing else already covers — **remains 1, and
> that one is already annotated.**
>
> **B. AN ATTRIBUTION DEFECT IN §4, THIS LANE'S OWN.** §4 says of `:73` that *"that premise was measured
> FALSE at HEAD"* **without saying by whom, and against a moving target.** Corrected:
>
> - **The measurement is the stale blocker sweep lane's, not this lane's.** Recorded at
>   `VALIDATION_LEDGER.md:756-758` under `BEN-381`, taken at HEAD **`32e403b8`**, naming four write
>   sites: `sweep_bank_5d.py:309-311`, `analyze_universes_5d.py:273-278`,
>   `unified_throw_cov.py:569-575`, `mii_adopt_unified_5d_stamped.py:168`, landed 2026-08-18…08-20.
> - **"at HEAD" was the wrong form** — a sha, never a moving ref. This lane relayed a dated claim as a
>   present-tense one.
> - **Spot-checked here rather than re-relayed:** `nd-unfolding/unified_throw_cov.py:569` at
>   **`bae4c6c1`** writes `ROOT.TParameter("int")("estimator_seed", …)`. So the premise *"the dominant
>   arm has nowhere to put a seed stamp"* is **still false at this sha**, on one of the four sites.
> - **`:73` therefore deserves its own route, not an exclusions footnote** — a live board asserts an
>   impossibility that is not true, and it is load-bearing for cause 3's `P-ii` remedy. The `5d` lane is
>   flagging it to Joseph by name. **Not fixed here; not this census's cell.**

## 7. What this record does not do

It grades nothing, moves no cell, relabels nothing, proposes no token for any specific cell, changes no
count, moves no gate, and authorizes no compute. It does not resolve `:73`'s false premise or the
`§2(b)` mechanism flag.
