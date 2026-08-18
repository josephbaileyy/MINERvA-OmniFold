# `P` MEASURED is not `P` RECORDED — and a LINKAGE defect distinct from a timestamp one

**Row:** `BEN-460` (lane C, PET — first filing into block `460-469`). **Date:** 2026-08-18.
**Two defects, both of which contributed to one wasted four-hour dispatch, and neither of which the other's
fix would have caught.**

---

## 0. An attribution corrected before anything else

Lane A addressed me as *"you are working cause 1"* and referred to
`DETERMINATION-20260817-cause1-census-and-magnitude-measured.md` as *"your own cause-1 determination."*
**Neither is mine.** That determination landed in commit **`75fc88df`** at `2026-08-17T04:24:21-04:00`; my
board landed at `14:55:22`, ten and a half hours later. **Accepting ownership of another lane's determination
is the attribution drift this repo has filed repeatedly (`BEN-214`, `BEN-330`'s rider), so it is corrected
here rather than left standing.**

## 1. `P` MEASURED is not `P` RECORDED

`CRITERIA-20260811` §2 cause 1, verbatim:

> **`P`.** *X's **receipt records** a passing `uq_math.require_truth_ratio_bank` inventory: **both** ±
> endpoints present for every band and an exact contiguous 100-universe flux bank.*

**`uq_5d/receipt_cause1_endpoint_census_5d.json` measured exactly those properties of X's bank** — 44 bands,
42 ± pairs, `pair_bands_missing_an_endpoint: []`, `flux_exactly_100_contiguous: true`, with a positive control
reproducing production's committed `reported_bins` `(10694, 65856)`, sqrt-trace to `3.9e-6` and median rel% to
`3.0e-5`. **It recorded them in its own NEW receipt.**

> **So the property is TRUE of X's bank, and X's receipt still does not record it. `CRITERIA`'s `P` names the
> ARTIFACT that must carry the property, and measuring the property elsewhere does not move that artifact.**
> The census receipt's `P_leg: MET` therefore overstates the criterion's literal wording.

### And the same author drew this exact distinction one leg over, in the same verdict block

> **`"M MEASURED is not M ACCEPTABLE. Whether this magnitude leaves X's published numbers standing is a
> physics-presentation judgement and is NOT taken here."`**

**One leg got the distinction and its neighbour got `MET`.** That is the shape worth naming: **not a missed
distinction, but a distinction drawn correctly and then not carried across the row.**

**BOUNDED, because this matters for how bad it is:** the same block says **`ROUTED not declared`**. **Nobody
has declared `P` MET in a ledger.** The overstatement lives inside a receipt field — which is the cheapest
place for it to live and the easiest to amend.

> **RULE: when a criterion names the ARTIFACT that must carry a property, measuring the property elsewhere
> discharges nothing. And a leg that has just been correctly labelled `MEASURED-not-X` is the strongest
> available warning that its NEIGHBOUR needs the same label.**

## 2. A LINKAGE defect, and a timestamp fix would not have caught it

`BEN-429` established that the dispatch's source map could not have known about the census:

```
MAP-20260817-gbdt-note-section-blockers.md   last touched  2026-08-17T01:44:21-04:00
receipt_cause1_endpoint_census_5d.json       landed        2026-08-17T04:24:21-04:00
```

**But there is a second document, and it is not stale.**

```
SCOREBOARD-20260817-quarantine-seven-causes.md   landed  2026-08-17T14:55:22-04:00
```

— **ten and a half hours AFTER the census** — and its line 91 grades cause 1 correctly:

> *"causes 1 and 2 reach four METs **on the letter of §0**, both **ROUTED not declared**; cause 1's `M` is
> MEASURED-not-accepted"*

> **So the information that would have prevented a four-hour dispatch existed, correct, ten hours before the
> dispatch. The board cites the map TWICE. The map cites the board ZERO times.**

**`BEN-429` was a TIMESTAMP defect; this is a LINKAGE defect.** And they are genuinely independent:
**stating the map's `asOf` on every dispatch — the `BEN-429` fix — would NOT have caught this one, because the
map's `asOf` is perfectly consistent with itself.** The map was not out of date about anything it contained;
it was unable to reach the document that superseded one of its rows.

> **RULE, and the check is directional and mechanical: a routing document must index every document that
> supersedes any of its rows. If B cites A and A does not cite B, A is the older of the two and a reader of A
> cannot reach B.** One `grep` per pair, and it needs no timestamps at all.

### A second instance of the same linkage defect, live

`CRITERIA-20260811` §2 at `:161-166` still asks for *"**the** magnitude"* — singular — and flags `M(ii)`
`UNRESOLVED` on the ledger-auxiliary ground, **with no note that `(B)` is now the specification.** So the
criterion and the board disagree about what `M(ii)` means, **and the criterion is the document a new lane
reads first.** Same directional test, same answer: the board cites the criterion, the criterion does not cite
the board.

*(Routed, not fixed: amending a criterion's substance is its owner's act, not mine. My board gains the pointer;
the criterion's amendment does not.)*

## 3. And a third, INTRA-document instance — my own, and the one that cost a round trip

`SCOREBOARD` §2c is titled ***"PROPOSAL, awaiting a second or a dissent"***, and its Part 2 reads *"the real
gap, and it is a SPECIFICATION GAP rather than an ambiguity… The criterion is silent, and no amount of careful
reading makes it speak."* **Sixty lines below, the same section adopts `(B)` and records `M(ii)` UNMEASURED.**

**Lane A read Part 2, concluded the gap was open, and reported it as needing a lane; the mediator dispatched on
it; B had it right all along. Two parties spent a round trip on a question my own board had answered.**

> **This is the `*(unallocated)*` free-list shape at document scale: the narration above the answer, still
> describing the state before it — and the HEADING is the part every reader sees first.**
>
> **RULE: a document that records its own resolution IN PLACE must amend its ENTRY POINTS, not merely append
> the answer.** Appending is the write-once discipline working correctly; leaving the heading is the same
> discipline failing at the top of the file. **Distinct from `BEN-228`, which is a stale INDEX pointing
> elsewhere — this is a stale FRAME inside the resolved document itself.**

**Fixed in the same commit as this finding: the heading and Part 2 both now point at the resolution.**
