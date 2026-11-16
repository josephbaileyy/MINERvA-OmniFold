# DECISION 2026-11-10 — Joseph: V-HALF-R's two-dimensional resolution rule for C6 and C7 is a 20 % share per row and column, with no exemption: structurally unresolvable rows count as failures

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **coverage-5b-audit** blocked V-HALF-R Amendment 1 (PR #1043 at `c76e2e3a`) on B1. A3.1's rule refuses joins that
  span a whole axis, but a near-strip (a strip missing one fine cell) passes it. Since Joseph removed C7's fixed q3 edge
  (`DECISION-20261110-joseph-vhalfr-a33-a82.md`), it is C7's only two-dimensional guarantee.
- **limitation-resolver** drafted three options as A3.4 (`v-half-r/AMENDMENT-1.md` at `1083258f`):
  - (i) a share per row and column;
  - (ii) a balanced 2×2 frame;
  - (iii) the current rule with disclosure.
  It recommended (i) at s = 0.2, with an exemption for rows where one fine cell exceeds 80 %.
- **An independent consult** at Joseph's request (codex-school `gpt-6.1-sol`, high;
  [`v-half-r/consult-sol-a34-20261110/`](state/2d-closeout/valid-region-20261107/v-half-r/consult-sol-a34-20261110/))
  recommended (i) at 0.2, but without the exemption:
  - rows that cannot meet the rule from the fine grid are structural failures;
  - the exemption would drop the guarantee where it is weakest, uncapped, and miss other impossible rows (for example
    19/62/19);
  - option (ii) is weaker, because balanced margins can leave the events in two opposite quadrants.

## Joseph's answers, verbatim

> Ask Sol first

(sha256 of the text plus a final newline begins `0d547a651426d1ce`), and then:

> (i) 20%, no exemption (Rec.)

(`1ceae2eb28ce6968`).

## What is decided

1. **C6 and C7's two-dimensional rule (A3.4) is option (i) at s = 0.2.** In the masked domain, every fine row and every
   fine column keeps at least two pieces, each holding at least 20 % of that row's or column's truth_sel.
   - **During merging,** a join is refused if it would push any touched row's or column's largest piece above 80 %. That
     veto is monotone.
   - **At the end,** the two-piece condition is checked as a final requirement.
2. **No exemption.** Before merging, the builder identifies every row or column that cannot meet the rule from the fine
   grid alone: one cell above 80 %, or a contiguous structure such as 19/62/19 that admits no two pieces of 20 % or more.
   Each is recorded as a structural failure of the requirement. A candidate with any such failure, or with a final
   two-piece failure, ends with no reportable binning, and that is its reported outcome.
3. **Every other requirement stands:**
   - min(purity, diagonal fraction) ≥ 0.5, as a final requirement;
   - support of at least 1000 in both specified populations;
   - the bin floor;
   - C6's fixed p∥ = 4.5 edge;
   - every share computed within the masked domain, with finite, nonnegative weights.
4. **0.2 is a stated convention, not a calibrated value.** The study is informed development, and the disclosure says
   so.
5. **The amendment** is revised for this and returns to coverage-5b-audit for the B1 and M1–M3 recheck, then to the
   director's binding.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the rule; the no-exemption ruling.
- **Not citable for:** any failure probability, or any V-HALF-R result.

Nothing is submitted, deposited or tagged.
