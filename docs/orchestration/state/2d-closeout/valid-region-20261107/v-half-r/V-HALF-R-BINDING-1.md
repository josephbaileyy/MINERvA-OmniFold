# BINDING 1: V-HALF-R, the declared rebinning and candidate-observable study, with Amendment 1 (director, 2026-11-11)

**Binds**, together:
- [`DECLARATION.md`](DECLARATION.md) (sha256 `bdf853073b4d79ca`), as merged in PR #1016 at
  **M_D = `d6f6427546430c6d72220e308e09dcc9d90849ef`**, byte-identical to its reviewed head `b7d7ac2dc`;
- [`AMENDMENT-1.md`](AMENDMENT-1.md) (`a8648b9fec2b6d13`), as merged in PR #1043 at
  **M_A1 = `bb3ad5f53e7a66e46dd7e582973dc9ff00e7b848`**, byte-identical to its audited head `9b6855e9`.

Where the two differ, **Amendment 1 governs**.

**Under** Joseph's decisions:
- `DECISION-20261110-joseph-vhalfr-choices.md`: C6 and C7 are required; the six design choices; three fixes;
- `DECISION-20261110-joseph-vhalfr-a33-a82.md`: no fixed C7 q3 edge; the three tilts confirm;
- `DECISION-20261110-joseph-vhalfr-a34.md`: the 2D rule, 20 % per row and column, no exemption.

The packet behind them is `CHOICES-FOR-JOSEPH-20261110.md`. The three independent consults are in `consult-sol-*`.

## What the director checked

- **coverage-5b-audit's GO** on Amendment 1 at `9b6855e9`:
  - B1 is resolved by A3.4. It implements decision A3.4's items 1–4: the structural check before merging is
    necessary, the 80 % veto is monotone, and the two-piece condition is final.
  - M1–M3 and v1–v5 stay resolved.
- **Each of Joseph's four decisions is implemented** as he decided it, and each consult is committed beside its
  decision.
- **Nothing has been computed.** The choices read only simulation, and no binning has been built.
  <!-- absence-ok: this binding's own scope, before any build -->

## Rulings

1. **Order.** The code (D §6, Amendment 1 A9) comes next, with tests and mutants. Then coverage-5b-audit audits it,
   and the director binds the code. **The study runs only after Tier 3 reports** and Joseph has decided whether the
   estimator changes. If it changes, F0b's and FD-PRR's products are remade for it before grading (A8.1).
2. **Precondition of the first build** (the audit's minor): w_truth in the pinned MC npz `07fccc1a` is confirmed finite
   and nonnegative wherever a share counts it. This is a read-only login check, with its script to the director
   first. If it fails, A3.4 STOPs, and C6 and C7 cannot be built.
3. **The required outcome.** If C6 or C7 ends with no reportable binning, that is the reported outcome, and a passing
   optional candidate does not replace it.
4. **Disclosure.** Amendment 1's disclosure prints wherever any candidate's result prints. It says the rules were set
   after the 16-cell V-HALF result and the referees' remark were known, and that 0.2 and 0.5 are conventions.
5. **The reserved-truth step** (A8.2) runs only after the development read is committed and its own addendum is
   bound. Seeds and experiment counts are fixed before any tilt is generated.
6. **The price** is set at the code binding. The cluster work runs as declared, with nothing written to CFS.

Nothing is submitted, deposited or tagged.
