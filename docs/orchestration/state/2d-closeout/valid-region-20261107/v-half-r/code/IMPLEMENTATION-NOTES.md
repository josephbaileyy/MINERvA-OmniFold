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
`h2_definition.merge` does (`nd-unfolding/pv-ladder/h2_definition.py:90-117`). A flagged bin can still be taken as another bin's partner. Whatever remains low
at the end is caught by the final requirement as T3, because `outcome` evaluates every final bin regardless of flags.

## 4. Tie-breaks (A4.2)

- **Lows:** the key is (value, first index), where value is min(purity, diagonal fraction), or purity in the
  reproduction mode.
- **Partners:** the key is (−value of the union, axis, partner's first index).
- A grid bin's first index is the flat index of its lowest corner. A C0 bin's first index is its lowest H2 cell. Both
  match `h2_definition.merge`'s keys.

## 5. Weights (A3.4)

`check_weights` STOPs on a negative or non-finite w_truth on any row a share counts (pass_truth, true fine cell in Ω). It
also STOPs on a non-finite w_reco on any counted pass_reco row. The w_reco condition is an addition: it keeps the
fractions finite. The first build's precondition check passed on the pinned npz (`receipts/wtruth-20261111/`).

## 6. The reproduction mode (A4.5; audit M1)

`merge(..., mode="repro", tau=0.1)` with `Boxes` on the 32 H2 boxes is `h2_definition.merge`'s rule exactly: only a
supported bin can be low, and unsupported boxes are never merged.
`test_repro_equals_h2_merge` compares the two on 40 random responses with support failures, and the final boxes and
flags are identical. The real reproduction of R00–R15 (D:264) runs at the first build on the pinned npz, where the
fine map must equal h2_definition.json's `930326a3…`.

Nothing is submitted, deposited or tagged.
