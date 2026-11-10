# BINDING 1: the confirming round's Tier 2 diagnostics, T2A and T2B (director, 2026-11-10)

**Binds** the two declarations below as merged in PR #1032 at **M_T2 = `3bb2a96c75728fd6b05edcca0b33e6e82c2ed91b`**.
The reviewed head was `b8494106`; each file is identical at both commits.

| file | sha256 (prefix) |
|---|---|
| [`T2A-COV2D-SPLIT-DECLARATION.md`](T2A-COV2D-SPLIT-DECLARATION.md) | `be83886d5256b625` |
| [`T2B-FD-GRADE-VARIANTS-DECLARATION.md`](T2B-FD-GRADE-VARIANTS-DECLARATION.md) | `52e2ba36dd8051c6` |

[`T2C-ENS1-DEFICIT-LICENCE-NOTE.md`](T2C-ENS1-DEFICIT-LICENCE-NOTE.md) (`1f49539a504d7c85`) is a note for Joseph, not a
declaration, and binds nothing. Joseph decided it in `DECISION-20261110-joseph-ens1-deficit-licence.md` (PR #1035).

**Under** `DECISION-20261110-joseph-confirm-round-scope.md` item 1: each Tier 2 diagnostic is declared before it is
computed and read once, under the director's binding, from existing products only.

## What the director checked

- **Each declaration implements the director's scoping rulings:**
  - T2A: fixed ranks 73 and 139 with C_T's own threshold counts beside them; S at ddof 0; C_T only; E as the grade
    used it.
  - T2B: M1 = (C_e + C_resp), M2 = stat only, M3 = stat + C_resp, all fractional, with N kept; the seed block stated
    as zero, which the lane verified (`s1_assembly.json` `relative_sigma.seed` is 0.0 on all 16 cells).
- **The licences are narrow.** Neither declaration can change a verdict, criterion, grade or covariance. Neither
  supports a cause, a coverage statement or a p-value reading. T2A borrows the published covariance's counts as ranks
  only.
- **The controls fail closed before any reading:**
  - T2A: A0 (the regenerated score equals the committed one field for field) through A4;
  - T2B: B0–B3, including the existing grade on all 16 records reproduced to 1e-12.
- **Inputs are named by path and sha256.** Neither declaration runs a Slurm job, writes to CFS, or reads a sealed file.

## Rulings

1. **T2A's capture** is one login-node connect at 0 node-h, from a wrapper built by the valid-region lane in the
   `ess_capture.py` pattern. Before the director's go:
   - its tool commit and tests are reviewed by the cov2d session, which owns `cov2d_readout.py`;
   - the wrapper, connect and launcher come to the director with their sha256s;
   - `cov2d_fence.sh` runs before the connect.
   The connect waits for Joseph's NERSC certificate if it has lapsed.
2. **T2A's local nulls** (four, 2,000,000 draws in about 205 dimensions) are drawn in chunks, so that no array exceeds
   a few hundred MB. The chunking must not change the draw sequence: it is the same generator and seed, consumed in
   order. A3 states the size it was checked at.
3. **T2B's fetch** is one ssh session into a new empty scratchpad directory, sha-checked, then read locally under
   `python -I` with `allow_pickle=False`. The fetch script comes to the director with its sha256 before it runs.
4. **Each result is read once,** by the director, from its committed record. It enters the paper only within its
   licence, through the paper lane and a meaning read.
5. **If a control fails,** that diagnostic is reported as not made, with the control's output, and nothing is
   repaired into it.

Nothing is submitted, deposited or tagged.
