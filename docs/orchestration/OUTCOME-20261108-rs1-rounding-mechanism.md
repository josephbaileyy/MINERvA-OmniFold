# OUTCOME 2026-11-08: RS1, the mechanism of the rounding instability. K1 and K5 are SUPPORTED

**Recorded by** the rounding-instability lane, a Claude session named `director-helper-3`, for the director. This is step
1 of the rounding-instability work (`DECISION-20261106-joseph-diagnoses-jinst-corrections.md` item 1.3).

**The design:** `RS1-DECLARATION.md`, bound by `RS1-BINDING-1.md`. **The code:** bound at M = `e306087e` by RS1-BINDING-2.
**The run:** completed under addendum A1, revision 2, at M_A1 = `1f747346`.

**The records**, in the receipt `fd/rounding-stability-20261106/receipts/full-a1/` (PR #913):
- `read/rs1_read.json`, sha256 `9938e1685018a1943125cd4414ea93d1cc5a0852e82234fe49d1678d89e8b9ef`. It was produced by the
  bound `rounding_mechanism_analyze.py read` at M on the run's 229 products (job 60982139, DONE 66/66; 20 tasks staged
  from the dry run and attempt 1, 46 run).
- `read/rs1_r0.json`, sha256 `724f0c3a7fc89f6f7f1ecc54d412a8c25e7c6b533f8f7d7b90d494dba6120652`.

Below, a number written `[key]` is read from `rs1_read.json` at that key path, unless `rs1_r0.json` is named.

**The order of steps was kept.** Step 2 (ENS1) was declared and bound before this read. Its addendum A1 was frozen at
#912 head `1ae4fcea` before this read too (the director's condition).

**The study:** pseudo-data only. No data was read, and R0 reads committed results only.

**The cost:** 4.0428 of the 8.0 CPU node-h cap. That is the dry run's 0.2622, attempt 1's 0.9778 (INVALID,
infrastructure; #901), A1 connect 1 at 0 (#905), and the resume's 2.8028.

## The gates

All pass, and the status is **READ** [`status`].
- **G1:** A0's float32 base and jitters 1–20 equal FD-STAB's control products bitwise, and every one is verified against
  FD-STAB's pinned SHA256SUMS [`G1`]: 21 of 21.
- **G2:** informativeness. No functional has zero spread under A0 [`G2.zero_spread_fraction` = 0.0].
- **G4:** S-all, with nothing swapped, reproduces A0 bitwise [`G4`]: 3 of 3.

## The readings (`RS1-DECLARATION.md` §5.2)

A candidate is read SUPPORTED or NOT SUPPORTED only if both functional sets give the same DEFINITE reading. M is an arm's
median spread ratio to A0, with a 90 % paired-bootstrap interval. The bands are R ≤ 0.10 < P < 0.70 ≤ C.

| candidate | the test | 153 functionals: M [interval] | 16 cells: M [interval] | reading |
|---|---|---|---|---|
| **K1**, ties through the bins | V, the tie-preserving jitter | 6.2 × 10⁻⁷ [5.8, 7.4 × 10⁻⁷] R | 1.07 × 10⁻⁶ [0.81, 1.26 × 10⁻⁶] R | **SUPPORTED** |
| K2, `max_bin` | B1023 | 0.950 [0.889, 1.03] C | 0.945 [0.795, 1.12] C | NOT SUPPORTED: the interval lies above 0.7 |
| K3, float32 against float64 | the two unjittered bases | D = 0 | D = 0 | NOT SUPPORTED: bitwise equal [`statistics.K3_bitwise_equal`] |
| K4, near-degenerate gains | P1 and P2, permuted rows | D_P = 4.1 × 10⁻¹¹ | D_P = 1.2 × 10⁻¹⁰ | NOT SUPPORTED: D_P ≤ 0.01 |
| **K5**, the refinement stage | S-ref, only the refinement jittered | 0.959 [0.888, 1.04] C | 0.890 [0.742, 1.09] C | **SUPPORTED** |
| K6, the W² clamp | none possible | — | — | NOT TESTABLE |

The table's sources:
- **M values:** `statistics.ratio.<arm>.functionals_153` and `.cells_16`.
- **K3:** `statistics.K3_D`.
- **K4:** `statistics.K4_D_P`.
- **The six readings:** `readings`.
- **The supported candidates** are `supported` = [K1, K5].

## What each reading licenses, as the declaration states it (§5.2)

**K1 SUPPORTED.** The record may say: *"on this pseudo-experiment, the perturbation reaches the estimator by breaking ties
among equal float32 values, which changes LightGBM's histogram bins; a perturbation that keeps the ties removes the
spread."* Measured, the tie-preserving jitter leaves a spread ratio of about 10⁻⁶ on both sets.
- It may **not** say that the data's spread has this cause.
- It may **not** say that ties are a defect of the inputs. Equal float32 values are what float32 storage of these
  kinematics produces (the A0 base's tie fractions are in `readouts.ties_float32_base`).

**K5 SUPPORTED.** The refinement is a **sufficient entry**. Jittering only the refinement's input carries the full spread,
with M_ref reading C on both sets.
- S-omni, which jitters only the OmniFold loop, reads C on the 153 functionals (0.947 [0.865, 0.992]). On the 16 cells
  it reads INCONCLUSIVE (0.857 [0.697, 1.03]).
- So the declaration's "either stage alone is a sufficient entry" (both C) is **not** established. Only the refinement's
  sufficiency is.
- Neither stage is "the" mechanism.

**K2, K3 and K4 NOT SUPPORTED.**
- Finer binning (B1023) does not reduce the spread, and coarser binning (B63) reads C on the functionals.
- The float32 and float64 bases are bitwise equal.
- Permuting the rows moves the result by about 10⁻¹⁰ of the jitter spread.
- K3's and K4's results re-confirm the s5e measurements on this input and estimator.

**K6 is NOT TESTABLE** (§3).

**Not a declared reading, and not claimed here:** that K1's ties act *at the refinement*. K1 and K5 are separate tests.
V jitters every coordinate for every consumer, and S-ref jitters with the protocol's tie-breaking jitter. Joining them
into one mechanism would need a test that was not declared.

## Predictions, stated before the run (§5.3), against the outcome

| the prediction | the outcome |
|---|---|
| K1 SUPPORTED; V bitwise equal to the float64 base for most fits, with any residual through the regressor's untrained rows | **SUPPORTED.** V is not bitwise equal: the dry-run tie read (#896) found differences up to 3 × 10⁻⁹ relative, from a leaf value onward in later fits. Its spread ratio is about 10⁻⁶. |
| K3 NOT SUPPORTED (bitwise equal) | **as predicted:** bitwise equal |
| K4 NOT SUPPORTED | **as predicted** |
| K2 and K5: no expectation | K2 NOT SUPPORTED; K5 SUPPORTED |

## Readouts, descriptive only (§6)

**The absolute spreads, in pseudo-data σ** [`readouts.absolute_median_spread_in_pseudo_sigma`]:
- A0: 0.595;
- V: 3.5 × 10⁻⁷;
- the axis arms (F_pt, F_pz, F_eavail, F_q3, F_W): 0.54–0.61;
- S-ref: 0.564; S-omni: 0.558; B63: 0.537; B1023: 0.605.

**Each single axis's jitter alone carries most of the spread.** Every F_k reads C on the functionals.

**A0's pair statistic over its 10 disjoint pairs** [`readouts.A0_pair_statistic_10_pairs`]: mean median 0.760 and mean
max 6.78. That reproduces FD-STAB's control at its 25 pairs (0.759 and 6.83, `fd_stab.json:6-7`).

**The spread grows over the five OmniFold iterations**, relative to iteration 1
[`readouts.per_iteration_spread_over_iteration_1`]: 1.00, 1.10, 1.22, 1.25 and 1.35.

**R0, the spread on the 16 reported cells in units of S1's statistical σ** (`rs1_r0.json`). A description only, read as
neither a pass nor a fail.
- **R0a** = (σ_J/f)/σ_S1,stat: median 0.512, range 0.385–0.819 [`R0a_summary`].
- **R0b** = (σ_J/f)/√(σ_S1² − (σ_J/f)²): median 0.596, range 0.418–1.426 [`R0b_summary`]. It is defined at all 16 cells
  [`R0b_undefined_cells` = []]. R0b assumes the two variances add (`assumption`).
- **The controls passed** [`controls`]: σ_J/f reproduces I0's printed (0.133, 0.055, 0.252) %, and C_e is S1's.
- **The inputs**, by digest [`inputs_sha256`]: `i0.json` `9a4142d3…`, `fd_data_product.json` `b79556f0…`,
  `s1_assembly.json` `81e5ef3f…`.

## A finding about reproducibility across a teardown crash

In attempt 1 (job 60972000, #901), task `rs1_V_02` wrote its four products with rc 0, then segfaulted in PyROOT during
interpreter teardown. Under A1, it was recomputed from scratch.
- **The four recomputed products are bitwise identical** to attempt 1's, in `xsec_flat` and `xtrue_flat`.
- The comparison record is on pscratch (sha256 `374969f2…`, receipt §"After the run").
- So the crash came after the products were complete, and did not touch them.
- **The teardown guard was not exercised by the resume.** None of the 46 tasks crashed at exit.

## CITABLE FOR

- **RS1's step-1 outcome on this pseudo-experiment:** K1 and K5 are SUPPORTED; K2, K3 and K4 are NOT SUPPORTED; K6 is NOT
  TESTABLE. Each statement may be made in the declaration's licensed wording above.
- **The readouts above,** as descriptions: the absolute spreads, the per-iteration growth, A0's pair statistic and R0's
  two ratios.
- **The V_02 bitwise reproduction** across a teardown crash.

## NOT CITABLE FOR

- **Any statement about the real data.** In particular, not that the data's rounding spread has K1's cause.
- **A remedy.** Step 2, ENS1, is declared separately and was frozen before this read. Nothing here selects or changes
  its design.
- **Ties as a defect of the inputs.**
- **K1 and K5 joined into one mechanism** ("ties at the refinement"). That is not a declared reading.
- **"Either stage alone suffices".** S-omni is INCONCLUSIVE on the 16 cells.
- **Any change to the reported estimator, to `OUTCOME-20261105-fd-stab-none-pass.md`, or to any wording on main**
  (§5.2: no outcome changes them).
- **R0 as a pass or a fail.**

Nothing is submitted, deposited or tagged.
