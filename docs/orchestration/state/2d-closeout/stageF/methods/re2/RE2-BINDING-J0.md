# RE-2 binding, part A: the J0 pilot (2026-10-23)

**By** the paper-tighten lane, as director, under `AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2 and
DECISION-20261023 (second) item 1. **Binds** [`RE2-DECLARATION.md`](RE2-DECLARATION.md) as merged in PR #283
(`716dd17e`; the file's sha256 begins `3db6cc85810e0de5`), whose code commit is `668e9b44`.

## Rulings (as sent to the re-1 lane, 2026-10-23, and recorded here)

- **A1, the code path: accepted.** `re2_driver.py` is a `driver_p1.py` copy, changed only in blocks marked RE-2: the
  400/31 size and the refined three-stream background stream. It replaces the planned `re1_2d.py` extension, and the
  declaration names that change from the plan.
- **A2, tolerance: accepted.** The K1 and CHK checks pass at ≤ 1e-8 and report bitwise equality. Configuration (a)'s
  LightGBM mode is not deterministic, and the declaration says so.
- **A3, two parts: accepted.** Part B needs its own binding before any production job.
- **A4, the J0 grant: accepted.**
  - At most **10.5 CPU node-h**: two regular jobs with limits 5:55 and 4:15, on m3246, under the 2D closeout
    ceiling.
  - The limits come from class maxima × the measured packed slowdown of 1.81
    (`state/gpu-timing-20261023/REPORT.md`) × 1.06 × 1.25.
  - Stop and report if either job runs past 1.25× its projection.
  - Submit once only, with `re2_submit_j0.sh`, from a deploy at `668e9b44`.
- **A5, the rule for part B: accepted as written.**
- **A6, the registry: done in PR #283.**
  - ALIASES "refinement 400/31" is identifying = no.
  - UNRESOLVED-NAMES row 7 lists its three senses.
  - This binding also sets the e-R-joint-test alias "400-tree, 31-leaf Stay-Positive refinement"
    (`r12/REVIEW.md:48`) to identifying = no, because the phrase also describes `a-refined-400-31`. The (e) = R
    crosswalk still resolves through the identifying aliases "R = paper configuration (e)" and "configuration (e)".
- **A7: noted.**
  - At today's speed, part B's core looks like about 98 node-h (about 122 at worst), and about 117 (147) with the
    diagnostics.
  - That is above the 90 granted in principle, but inside the ceiling: 660.53 left before J0, from the plan's
    re-derivation.
  - The director grants part B from J0's measured units, in a fresh binding.

## Correction

The declaration cites the director's plan rulings as PR #277; they merged as **PR #278**. The wrong number came from
the director's own message. PR #277 is the IBU-1 report.

J0 may be submitted once this record is on `main`.
