# V-HALF-R builder: implementation notes (`vhr_binning.py`)

**By** the limitation-resolver lane, 2026-11-11, for coverage-5b-audit and the director's code binding. The code binding
cites these notes. They record how the builder reads V-HALF-R-BINDING-1 (DECLARATION.md together with AMENDMENT-1)
where the text leaves a choice. They change no rule.

## 1. The 80 % veto (AMENDMENT-1 A3.4 (2); DECISION-20261110-joseph-vhalfr-a34.md item 1)

**The reading, ruled by the director on 2026-11-11.** A join is refused if, for some row or column it touches, the
largest piece's share is at most 0.8 before the join and above 0.8 after it (`veto`, the condition
`before[0] <= VETO < after[0]`).

**Why a line already above 0.8 does not refuse joins.**
- Such a line has one fine cell holding more than 0.8 of its truth_sel. So no cut leaves 0.2 on each side, and A3.4 (1)
  records it as a structural failure. Its candidate then ends at T2 whatever the merge does (decision item 2).
- If that line refused every join through it, the merge would only print a distorted binning for a candidate that is
  already terminal.

**Monotonicity.**
- Let a line's denominator be its truth_sel total, which is fixed because Ω and the weights are fixed. Every cell weight
  is nonnegative: `check_weights` STOPs otherwise.
- A join of two rectangles either merges adjacent pieces within the lines it spans, or leaves each touched line's pieces
  unchanged. A merged piece's share is the sum of two nonnegative shares.
- So a line's largest-piece share never falls under any sequence of joins. Once a join is refused for crossing 0.8, no
  later join can make it acceptable.
- `test_largest_share_never_falls_under_joins` checks this on 30 random join sequences.

**What the veto does not guarantee.** Two pieces of at least 0.2 is a separate final requirement (A3.4 (3); `final_two_piece_failures`). A row
at 70/10/10/10 passes the veto and fails that check. Greedy construction under the veto does not ensure a passing
partition is reached (D:216-217; consult S3:7).

## 2. Lines with no signal (A3.4's definitions)

A row or column with zero truth_sel within Ω is listed in `empty_lines` and carries no requirement, because a share is
undefined there. Any line with nonzero truth_sel, however small, carries the full rule. coverage-5b-audit read this as
a definition, and it waives nothing else.

## 3. Flagged bins (A4.2, following `h2_definition.merge`)

A low bin with no allowed partner is flagged by its first index, and the loop skips flagged first indices, exactly as
`h2_definition.merge` does (`nd-unfolding/pv-ladder/h2_definition.py:90-117`). That has two consequences (audit w1):
- A union that takes a flagged bin as its partner keeps that first index. It inherits the flag and is never tested as
  low again during the merge.
- A flagged bin is not retried after its neighbours change shape.
<!-- absence-ok: these describe the merge algorithm's control flow, not a claim that a result does not exist -->
Either way, whatever remains low at the end is caught by the final requirement as T3: `outcome` evaluates every final
bin, regardless of flags.

## 4. Tie-breaks (A4.2)

- **Lows:** the key is (value, first index), where value is min(purity, diagonal fraction), or purity in the
  reproduction mode.
- **Partners:** the key is (−value of the union, axis, partner's first index).
- A grid bin's first index is the flat index of its lowest corner. A C0 bin's first index is its lowest H2 cell. Both
  match `h2_definition.merge`'s keys.

**Tests** (audit V3). `TieBreaks` covers:
- equal lows, where the lowest first index goes first;
- the lowest low going first;
- partner ties, settled by the lower axis, then the lower first index;
- value-0 ties on an empty-corner C6 and C8, where many bins have reco_all = 0. Those two are pinned by their fine-map
  sha256. The C6 pin equals coverage-5b-audit's head value.

## 5. Weights (A3.4)

`check_weights` STOPs on a negative or non-finite w_truth on any row a share counts (pass_truth, true fine cell in Ω).
It also STOPs on a non-finite w_reco on any counted pass_reco row, with the truth or the reco in Ω. The w_reco condition
is an addition that keeps the fractions finite.
- The first build's precondition check (`receipts/wtruth-20261111/`) covered w_truth only.
- The w_reco condition is checked by the builder itself, at the first build, before the reproduction or any candidate
  (audit w2).

## 6. The reproduction of R00–R15 (D:264; A4.5; audit M1 and V1)

`reproduce` runs at the first build, after the weight check and before any candidate is built.
- It runs `merge(..., mode="repro", tau=0.1)` with `Boxes` on the 32 H2 boxes, unmasked, on the pinned npz. That is
  `h2_definition.merge`'s rule exactly: only a supported bin can be low.
- The reported boxes are numbered in order, and unsupported boxes map to −1, as `h2_definition.fine_map` does.
- **The STOP.** The run STOPs, writing nothing, unless all four of these equal `h2_definition.json`'s: the reported
  boxes, the unreported boxes, the flags (`flagged_no_partner`), and the fine map's sha256 (`930326a3…`). τ must also
  be the record's 0.1.
- The result is written as `reproduction_R00-R15.json`.
- **Tests.** `test_repro_equals_h2_merge` compares the rule with `h2_definition.merge` on 40 random responses.
  `Reproduction` runs `reproduce` against a record that `h2_definition`'s own functions made from synthetic events,
  and checks that each mismatched field STOPs. `Main.test_failed_reproduction_writes_nothing` checks the STOP end to end.

## 7. Records (audit w4, w5, w7)

- Each record carries `inputs`: the npz and h2_definition sha256, the sha256 of `vhr_binning.py` and
  `s5p_stage1_inspect.py`, and the constants.
- Each candidate's `domain` names the region Ω leaves out, derived from the unreported H2 boxes: p_T < 0.7 GeV/c,
  q3 ≥ 2.0 GeV and W < 1.8 GeV (A2).
- Every record is serialized and checked before any file is written. A non-finite figure STOPs with nothing written.

## 8. C0's floors

C0's total floor of 8 is implied by its 4 bins on each side of p_∥ = 4.5. So the total check is kept but cannot fire
alone, and a mutant of it is equivalent (audit w6).

Nothing is submitted, deposited or tagged.
