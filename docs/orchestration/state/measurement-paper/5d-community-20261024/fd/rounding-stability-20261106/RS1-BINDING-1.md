# BINDING 1: RS1, the rounding-instability mechanism study, its design (director, 2026-11-07)

**Binds the design of** [`RS1-DECLARATION.md`](RS1-DECLARATION.md), as merged in PR #867 (merge `de73f6c8`) at the
declaration head **D = `0d51e05456810dc568fb939eca1fb319acd7a3d4`** (the file's sha256 begins `dbfb0c941b2ad699`).
**No code is bound here.** The code is bound in binding 2, at its own M.

**Under:**
- `DECISION-20261106-joseph-diagnoses-jinst-corrections.md` item 1.3;
- `DECISION-20261106-joseph-plateau-next-work.md` item 1, at main `6d0aca7f`.

## What the director checked

**coverage-5b-audit's design GO at `0d51e054`**
(https://github.com/josephbaileyy/MINERvA-OmniFold/pull/867#issuecomment-6700940693):
- **E1 fixed,** with the stricter control the director accepted. The S arms are paired with A0's jitter, and gate G4
  requires S-all to equal A0 bitwise, so equivalence is an identity.
- **E2 fixed:** seed 0 is the step-free float64 copy, through main's float64 branch.
- **E3 as ruled:** 20 seeds. The declared power simulation (`power/rs1_power_sim.py`, output committed) gives 0.70–0.79
  DEFINITE C at M = 1, c = 0.8, and no wrong DEFINITE band.
- **The price arithmetic is checked,** and G1's 21 references are verified.

## Rulings

1. **The design is bound as declared at D:**
   - the arms K1–K5, with K6 (the W² clamp) declared NOT TESTABLE;
   - the gates G1 (A0 bitwise equal to FD-STAB's pinned controls) and G4;
   - the bands (0.10, 0.70) and the K2/K3/K4 thresholds, as declared;
   - the readings of §5 and §6;
   - R0's two ratios, as a description only.
2. **The price is bound:** 229 unfolds, 6.28 CPU node-h expected. **The cap is 8.0 node-h,** dry run and full run
   together, enforced by `--time` (0:45:00 dry, 7:15:00 full) on one node. `iris` is read before each launch.
3. **Before anything runs** (§8):
   - the code, with tests that fire in each guard's direction;
   - a mutation receipt with REQUIRED mutants for every gate, reading and refusal;
   - coverage-5b-audit's code GO;
   - binding 2 at the code's M.

   The bound modules are imported unchanged.
4. **Who runs it:** this lane, from a fresh clone at binding 2's M.
   - The dry run comes first.
   - Each connect's sha256 goes to the director before launch.
   - The cov2d squeue check is recorded, and ssh's rc is read unpiped.
   - Receipts go in as PRs.
5. **Step 2,** the ensemble-averaged estimator, is declared after binding 2 and before RS1's outcome is read (§11).
   Whether a passing variant replaces the reported estimator is Joseph's decision.

Nothing is submitted, deposited or tagged.
