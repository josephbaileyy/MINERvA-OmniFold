# OUTCOME 2026-11-06 — REF-C2C1: c2 reads "differ" and "unresolved"; c1 reads "equivalent"

**Recorded by** the paper-tighten lane, as director.

**The record:** `state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/read-2/readout.json`, sha256
`0ee21301744cf04df4e1ebf7224692a00fba5188532b31af9d596be8ce69cf5a` (#844, head `98d178f9`).
- It was produced by the bound read at M' `af70e9c4` (`REF-C2C1-BINDING-2.md`, the binding of 2026-11-06).
- The read connect was `d37f6682`, launched from main's bytes and re-hashed on login04, at 0 node-h.
- The director read it from main. The lane did not open it.

## The readings, as the record states them

**Every control passes:**
- C-CELLS (205 cells);
- C-IN;
- C-PUB: χ² = 465.4152721915331 over 205, against the full-precision operand;
- C-CV (max_rel 9.2×10⁻¹²);
- C-REF;
- C-CPUS (64 CPUs; OMP/MKL/OPENBLAS 64/1/1);
- C-SET (only the four determinism keys differ);
- C-SIM (1.5×10⁻¹⁴);
- C-ROO (4.0×10⁻¹⁵).

D_E_R = 2.2703 over ndf 205.

**c2, a binned IBU on E_R's own inputs, at K = 10 (the primary; declaration §1.4).** It uses the 300 Q_R replicas
(C-DRAW passed) at rank 75.
- **C2-R1: `differ`.** T_δ = 382.8, against the leave-one-out null's q̂₉₅ = 123.6 and max̂ = 138.5.
  - The null is exact agreement, so "differ" says a difference between IBU and E_R is detectable at this noise. It
    does not say the difference is large (§1.4).
  - The Hartlap factor, 0.746, is read by nothing.
- **C2-R2: `unresolved`.**
  - The per-replica interval [ρ₀.₀₅, ρ₀.₉₅] = [0.701, 1.128] straddles the 0.75 boundary, so it lies inside no single
    class.
  - The point ρ = D_IBU/D_E_R = 1.027/2.270 = 0.452 is printed beside it, as §1.4 requires.
  - That point lies below the replica interval. The declaration reads the interval, not the point. Why the two
    differ is not tested here, and this record offers no mechanism. <!-- absence-ok: a scoping statement about an untested property, not a claim that a result does not exist -->
- **K = 5, reported identically and not primary.** C2-R1 is `differ`, with T_δ = 437.1 against max̂ = 140.7. ρ = 0.366, its
  interval is [0.470, 0.770], and C2-R2 is `unresolved`.
- **Printed and read by nothing:** D_IBU at each K is 3.95 (K = 1), 1.59 (2), 1.08 (3), 0.90 (4), 0.83 (5), 1.03 (10),
  1.52 (15) and 2.16 (20).

**c1, the joint-test estimator (e) on E_R's 2D inputs (§2.3).** It uses 50 paired replicas at rank 12.
- **C1-R1: `equivalent`.** T_ef = 13.87, against q̂₉₅ = 14.46 and max̂ = 20.34. **It sits 4 % under the q̂₉₅ bar**, so
  "equivalent" holds by a small margin. The Hartlap factor, 0.735, is read by nothing.
- **C1-R2 (descriptive):** D_(e) = 2.356, beside D_E_R = 2.270.

## What it licenses (REF-C2C1-DECLARATION.md §1.5 and §2.4)

**c2, unresolved** (`:208`).
- **It licenses** reporting ρ, its interval and T_δ, as measured.
- **It does not license** any of the table's other sentences:
  - neither "input side" nor "algorithm side";
  - no attribution, and no cause;
  - in particular, it does not narrow the paper's "the source of the shape difference has not been identified"
    (`:205`). That statement stands as it is.

**c1, equivalent** (`:268`).
- **It licenses** "the joint-test estimator, run on the 2D inputs, reproduces the 2D central value within its paired
  noise".
- **It does not license:**
  - combining the estimators' results;
  - any change to E_R or Q_R;
  - any statement that this analysis's intermediate stages equal the publication's.

**Both** (`:209`):
- the result goes to Joseph first, then to the paper lane through the PRD read, with no paper text before that;
- "c2 and c1 compare estimators on this analysis's inputs. Agreement between methods does not show that the upstream
  ingredients or intermediate stages equal MINERvA's, and a difference does not show that either method is correct."

**Admissibility (§3).**
- Neither IBU nor (e)-in-2D becomes a reported 2D estimator on this evidence.
- No follow-up run is made because of these outcomes unless a new declaration binds it.

**Not to be conflated with REF-G1's "differ"** (`OUTCOME-20261106-ref-g1-r1-differ.md`). That was IBU against (e) on the
16-cell 5D reporting grid. Here c1 compares (e) with E_R in 2D, and c2 compares IBU with E_R in 2D. These are three
different pairs, on different binnings.

## A correction to the director's C-PUB ruling

`REF-C2C1-BINDING-2.md` (the C-PUB section, #839) says "`tension_report.txt:14` names no path". That holds only for the
control's own line, `:115`. The declaration's §0 (`:33-34`) gives the full path:
`re2/run/partc_r2/partc-r2/receipts/figs/tension_report.txt:5, 14`. That file prints 465.4153, which is the value the
ruling used. The ruling's conclusion is unchanged. The citation was not ambiguous, only printed to four decimals.

## Where it goes

- **Joseph:** the result, under `:209`.
- **The publication-scope package** (OI-205; the Codex scope lane, #827): the 2D shape-difference row reads "c2
  unresolved, and C2-R1 differ; the limitation sentence stands. c1 equivalent at a 4 % margin."
- **REF-C2C1 stage 4,** the deletion of the staged copies under a B9-form ledger row, proceeds now that the read's
  receipt is merged.
- **Spend:** 11.0587 of 12.5 node-h. The reads cost 0.
