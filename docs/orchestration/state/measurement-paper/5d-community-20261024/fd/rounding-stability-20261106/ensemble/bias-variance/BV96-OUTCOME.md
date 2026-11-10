# BV96 OUTCOME: E₉₆'s bias–variance study stops before running. At generator-shape truths, an MSE comparison with configuration (e) cannot resolve E₉₆'s variance-only gain at affordable cost (2026-11-10)

**Written by** the `limitation-resolver` lane (a Claude session), at the director's request of 2026-11-10 (in
correspondence). It is a findings record of a planned study that was never run, so it needs no audit (the director's
ruling). Joseph's decision is recorded by the director in its own decision file. Citations are relative to this
directory unless stated.
<!-- absence-ok: states that this study's own plan was not executed (Joseph's decision of 2026-11-10), not that a result is absent elsewhere -->

**The design, as written:** `BV96-DECLARATION.md`, an archived design that never ran. It is kept as written, apart
from the corrections marked "Corrected", which come from the consult below.

**The records:**
- the power check's read of FD-STAB's 70 control products: `power/receipts-o1/` (the director's go at sha256
  `2f35f99f…`);
- the derived inputs: `power/bv96_power_inputs.json`;
- the declared simulation: `power/bv96_power_sim.py` and `bv96_power_sim.out.txt` (seed 20261110);
- the corrected M₈₀ table: `power/bv96_m80.py` and `bv96_m80.out.txt`;
- the independent review Joseph decided on: `consult-astra/` (codex-school2 gpt-6-astra, at #1017's `b738074e`).

## What was decided

- **BV96 stops as an MSE study, and nothing launches** (option (a)). Its 122 node-h expected, and its 175 node-h cap,
  are not spent.
- **A re-targeted, held-out bias comparison** (option (b)) is deferred to the follow-up paper's planning. There, the
  physics contrasts and the acceptable absolute bias get defined, together with V-HALF-R's minimum-cell basis.

## The findings

**1. The scale finding: at generator-shape truths, MSE is bias-dominated, and E₉₆'s variance-only gain cannot be
resolved at affordable M.**
- **On s5e's 153 functionals.** At F0b's 14 non-nominal, non-GiBUU truths, (e)'s noise-free bias in σ_rel units has a
  median |b_j| from 4.5 (W2) to 62 (A7 NuWro), against 0.46 at the nominal truth (`power/bv96_power_sim.out.txt`).
- **The gain.** If E₉₆ leaves the bias unchanged and removes F's rounding variance, it gains on average
  mean(sd51²) × 95/96 = **0.77077 σ_rel²** per functional (`bv96_m80.out.txt`; the consult's re-derivation gives the
  same, 0.770770).
- **Why it cannot be seen.** Write each error as a shared part b + s plus the rounding deviations u (of F) and v (of
  E₉₆). Then e_E² − e_F² = 2(b + s)(v − u) + v² − u². The gain is quadratic in the rounding scale, but the noise has a
  term linear in it and in the common bias. Pairing removes the statistical noise and cannot remove that cross-term.
  So the per-experiment SD of the paired difference is 4.1–54 at those truths, against 0.57 at the nominal truth.
- **The cost of seeing it.** Power 0.8 at a single truth needs about 310 (W2) to about 53,000 (A7 NuWro) experiments,
  with a median over the 14 of about 7,800. That is about 600 to 104,000 node-h per truth, at 97 unfolds per
  experiment and 0.020258 node-h per unfold (`bv96_m80.out.txt`).
- **On the 16 cells.** The same holds, as `BV96-DECLARATION.md` §1.1 argues from the records: F's per-cell rounding
  variance is 0.4–4.5 % of a cell's statistical variance (mean 2.0 %).

**2. The power planning.**
- The declared headline is the minimum over ρ ∈ {0, 0.5, 0.9} of the median, over truth pairs, of P(E₉₆ resolvably
  better at both truths).
- **The primary basis excludes the two GiBUU truths: 0.0007 at M = 30**, over the 105 pairs of the 15 non-GiBUU
  truths.
- With them it is 0.001 over 136 pairs, at every M in {20, 30, 40, 60}. P(E-better) at M = 30 is 1.000 at the nominal
  truth, and 0.015–0.12 at the 14 other non-GiBUU truths.
- **What 0.001 and 0.0007 are:** planning summaries under the model's assumptions, not measured powers at BV96's
  reserved truths. The assumptions:
  - one noise-free closure supplies each truth's bias;
  - one stability input supplies the rounding behaviour everywhere;
  - shared statistical fluctuations cancel exactly between estimators;
  - E₉₆'s residual is an independent rounding row over √96.
  The simulation also did not combine "E-better" with the absence of harm, so it is not the probability of the full
  PREFER_E96 verdict.

**3. The consult's corrections, adopted** (`consult-astra/answer.txt`, the director's ruling):
- **M₈₀ at the worst truth is about 52,000, not 28,000.** The consult gives about 52,200 at A7 NuWro, and
  `bv96_m80.py` gives 52,959, taking the larger SD over ρ. The first figure divided by each truth's noisy simulated
  gain, instead of the model's expected gain.
- **0.001 is a planning summary, not a measured power** (finding 2).
- **The finding concerns an equal-bias, variance-only gain.** A large bias change between the estimators could still
  be detectable. "NO_PREFERENCE whatever happens" overstated it.
- **The re-targeted comparison's precision,** if it is ever declared:
  - per functional, SE(δ̂_j) = sd_j·√((1 + 1/96)/30);
  - that is **0.107 σ_rel at the median functional and 0.462 at the worst**, with individual 95 % half-widths of about
    0.21 and 0.91;
  - so it does not resolve 0.1 σ_rel uniformly, as the lane first wrote, and simultaneous claims need more.
- **In the archived design** (each marked "Corrected" there):
  - the margin's and the guard's a-priori grounds read 0.05 σ_rel² and 0.25 of a variance as relative changes in MSE.
    They are absolute yardsticks, and at large bias MSE is dominated by b²;
  - normal critical values with standard errors estimated at M = 30 do not guarantee the stated familywise rates;
  - the direct mean of squares is ē² + (M − 1)s²/M, not ē² + s².

**4. The GiBUU use: a disclosed planning sensitivity input.**
- The simulation's inputs include FD-STAB's control closures at A7 GiBUU and Stage 0c GiBUU.
- FD-STAB §5.3 keeps those truths' bias magnitudes out of every criterion, and ENS1's outcome keeps them out of any use
  beyond "no worse".
- The consult judged this use scientifically defensible as a disclosed sensitivity analysis. It also noted that
  "planning only" is not a complete procedural defence, because the headline fed the rule that decides M.
- **The non-GiBUU figure, 0.0007, is the primary basis.** The conclusion does not depend on the GiBUU inputs. No
  broader licence for GiBUU magnitudes is inferred from this use.

## CITABLE FOR

- **The scale finding:** at generator-shape truths, (e)'s bias on s5e's 153 functionals is large in σ_rel units, so an
  MSE comparison with E₉₆ is bias-dominated. E₉₆'s equal-bias, variance-only gain (about 0.77 σ_rel² per functional)
  cannot be resolved at affordable M (finding 1). The 16-cell version follows from the declaration's §1.1.
- **The power planning,** as a planning summary under its stated assumptions (finding 2), and the costs of finding 1.

## NOT CITABLE FOR

- **Any preference between E₉₆ and (e),** in MSE, bias or variance. Nothing was run at BV96's truths.
  <!-- absence-ok: states that this study's own plan was not executed (Joseph's decision of 2026-11-10), not that a result is absent elsewhere -->
- **Any measurement claim,** any statement about the real data, or any coverage statement.
- **A measured power at R1 or R2.** The figures are planning summaries.
- **A reinterpretation of ENS1** (`docs/orchestration/OUTCOME-20261109-ens1-stab-pass-bias-worse.md`). Its STAB_PASS and
  its BIAS_WORSE at one truth stand.
- **Any use of the GiBUU truths' bias magnitudes** beyond the disclosed sensitivity input of finding 4.
- **A paper or note sentence.** Wording is Joseph's, through the PRD-referee read. Nothing here enters the methods
  paper (`DECISION-20261109-joseph-methods-baseline-and-plan.md` item 4).

## What it changes, and what stands

- **Unchanged:** the reported estimator, configuration (e); ENS1's outcome; FD-STAB's outcome; and the methods paper.
- **E₉₆'s demonstrated merit is stability,** which ENS1 measured on its declared input.
- **Whether E₉₆ advances toward a future measurement** is for the follow-up paper's planning, which defines the
  contrasts and acceptable absolute bias first. The consult's guidance for that is in `consult-astra/answer.txt`
  §2: absolute biases beside any shift, a non-inferiority margin with simultaneous bounds and an inconclusive outcome,
  a variance-reduction target, and what success would and would not justify.
- **The reserved truths stay unused:** GENIE v3.04.00 G18_02a_00_000 and G18_10a_02_11a (declaration §3), and the
  seeds of §4. The power check read only F0b's development truths.

Nothing is submitted, deposited or tagged.
