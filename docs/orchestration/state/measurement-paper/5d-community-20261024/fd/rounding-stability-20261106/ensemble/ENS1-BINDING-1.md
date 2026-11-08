# BINDING 1: ENS1, the ensemble-averaged estimator (RS1 step 2), its design (director, 2026-11-07)

**Binds the design of** [`ENS1-DECLARATION.md`](ENS1-DECLARATION.md), as merged in PR #887 (merge `e0b0ddfa`) at the
declaration head **D = `15305f2d9f976d1fdb8ab29830c3f6ff7a3a821e`**. The file's sha256 is
`e29877cd978d317038539d88de8d4bdc4741611f402171ddb3c9f2146b2e3589`, and the text is byte-identical to the audited head
`1bd885b3`. **No code is bound here.**

**Under:**
- `DECISION-20261106-joseph-diagnoses-jinst-corrections.md` item 1.3;
- `DECISION-20261106-joseph-plateau-next-work.md` item 1;
- the director's rulings on N = 96, P = 10 and a conditional stage 2.

**The order.** ENS1 was declared and bound before RS1's outcome was read. RS1's dry-run tie-invariance reading runs
only after this binding merges, and no one had seen it before then.

## What the director checked

**coverage-5b-audit's GO at `9db73df2`, and at `1bd885b3` after its text-only LOW-2 commit:**
- **ENS-1 is closed.** G0 uses F₆₄(x), F's float64 seed-0 base, with a test that refuses a float32 base.
- **ENS-2 is closed.** δ_k is the protocol's ±½, pinned in both directions with a ±¼ mutant.
- **The §11 answers are adopted:**
  - the N_PAIRS rebind is restored in a `finally`;
  - one determinism fit is compared bitwise;
  - stage 2 keeps its dry run.
- **LOW-2 is in:** E3 stops unless F₆₄(x)'s estimator code_sha256 entries equal FD-STAB's j1–j20.
- **The power simulation** (`ens_power_sim.py`, seed 20261107) reproduces exactly. At c = 0, P(pass) is about 0.97
  (Gaussian, ρ = 0) and about 0.99 (t3).

## Rulings

1. **The design is bound as declared at D:**
   - E₉₆ (96 fits at fixed internal jitters on y at full precision, edge-safe, seeds 10001–10096), with the three
     float32 traps closed;
   - stage 1's statistic, FD-STAB §4.3 with E₉₆ for F, P = 10, bars 0.3 / 1.0, and gate G0 on F₆₄(x);
   - ĉ as descriptive only, with its rule fixed in advance;
   - the projection gates.
2. **The price is bound:**
   - **stage 1:** 2,017 unfolds, 46.04 node-h expected, **cap 55.0**;
   - **stage 2:** 1,633 unfolds, 37.28 node-h expected, **cap 46.0**.

   The total is under half the group's remaining balance (1,774.4 node-h at RS1's dry run). `iris` is read before each
   launch.
3. **Stage 2 runs only on stage 1's STAB_PASS and the director's go.** If stage 1 fails, stage 2 doesn't run, and the
   record says so.
4. **Before anything runs:**
   - the code, with tests in each guard's direction;
   - a mutation receipt with REQUIRED mutants for every gate, reading and refusal, including the three float32 traps;
   - coverage-5b-audit's code GO;
   - binding 2 at the code's M.
5. **Whether a passing E₉₆ replaces the reported estimator is Joseph's decision.** Nothing here makes that change.

Nothing is submitted, deposited or tagged.
