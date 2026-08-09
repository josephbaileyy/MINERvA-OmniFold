# Repo-wide table: every validator that mixes absolute and relative tolerances

**Date:** 2026-08-08 · **Generator:** `docs/orchestration/audit_validator_tolerance_units.py` (AST-based,
307 `.py` files, live positive control) · **Ledger:** BEN-071 · **Commissioned by** Joseph, 2026-08-08:
*"read a validator's checks against each other before reading any against the physics … run it as an
exhaustive sweep rather than case by case … post the table; that artifact is worth more than the
individual fixes."*

## The result in one line

**307 files, 3 functions mix units, and exactly 1 matters.** The other 2 are false positives with a
shared cause that turns out to be the tool's real limitation, stated in §3.

## 1. The table

| file | function | ABSOLUTE checks | RELATIVE checks | verdict |
|---|---|---|---|---|
| `nd-unfolding/p4_validate_active_lateral_fps.py` | `mat_gates` | L70 `-1e-30` | L66 `/max(1e-300, max\|C\|)`, L68 `-1e-12·\|ev[-1]\|` | **REAL — latent, fix for consistency** |
| `3d-unfolding/genie/compare_3d_fullcov.py` | `main` | L162 `1e-30` | L138 `1e-12·lmax` | false positive — exact-equality epsilon |
| `nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py` | `test_math_contract` | L63 `1e-12`, L64 `1e-12` | L49 `-1e-9·ev[-1]` | false positive — synthetic O(1) data |

## 2. The one that is real, and its corrected severity

`mat_gates` computes the eigenvalues, uses them relatively twice, then checks the diagonal absolutely:

    L66   rel_asymmetry = max|C-C^T| / max(1e-300, max|C|)      RELATIVE
    L68   psd           = ev[0] >= -1e-12 * abs(ev[-1])          RELATIVE
    L70   diag          = np.all(d >= -1e-30)                    ABSOLUTE

**Severity: LATENT, not reachable at this scale — corrected by Joseph 2026-08-08, and my earlier report of
it as simply "still live" overstated it.** The adopted FPS lateral has `sqrt_trace = 8.10399e-39`, so
`trace ≈ 6.6e-77` over 266 bins and `|ev[-1]| ≈ 1e-77…1e-78`. Line 68's effective threshold is therefore
`~1e-89`, which sits **~59 orders below** line 70's `1e-30` — so the PSD check subsumes the diagonal check
entirely, and a negative diagonal forces a negative eigenvalue that line 68 catches first. **The
2026-08-07 FPS adoption is not compromised and should not be re-opened.** The defect becomes exploitable
only for `|ev[-1]|` above `~1e-18`.

Fix for consistency, mirroring line 68 (`-1e-12 * abs(ev[-1])`) or `p4_lib`'s repaired form
(`-psd_atol_ratio * denom`). Left to the owning lane; `p4_lib.py` was repaired in the P4 round with a
mutation test at the real 1e-79 scale, and this variant should land the same way rather than as a bare
one-liner from another lane.

## 3. Why the two false positives matter more than they look

Both are absolute-against-**O(1)** quantities, and that is the tool's boundary:

- `compare_3d_fullcov.py:162` — `abs(t - args.tol) < 1e-30` is an **exact-equality proxy** between two
  floats that should be bit-identical (a sweep entry versus the CLI value). An absolute epsilon is the
  correct construction here; a relative one would be wrong.
- `test_fps_corrected_uq.py:63-64` — a **synthetic** null test. Its inputs are
  `rng.normal(size=(12,285)) + 5.0`, so the covariance is O(1): measured `max|C| = 2.725`, diagonal median
  `0.855`. An absolute `1e-12` therefore sits 12 orders *below* the data, which is a correct margin. I
  initially read this as "65 orders too loose" by assuming the production 1e-77 covariance scale, and
  checking the actual inputs is what caught it.

**So mixed units is a SMELL, not a defect. The defect is mixed units where the data is far from O(1).**
The tool classifies units, which is mechanical; it cannot know the scale of the data flowing through,
which is not. That is the same distinction Joseph applied to line 70 — a defect in form is only a defect
in fact once you check reachability — and it is why this table carries a verdict column rather than just
a hit list.

## 4. Method, and what it deliberately excludes

Classification is on the **AST**, not by regex, because `-1e-9 * max(eig, 1.0)` and
`abs(a-b)/total < 1e-9` are similar characters in different shapes:

- **RELATIVE** — the literal is multiplied/divided by a non-literal, or the compared quantity is a
  quotient, or a name announces a ratio (`rel_`, `ratio`, `_over_`, `relerr`, …).
- **ABSOLUTE** — a bare literal against a raw quantity.
- **FLOOR** — the literal is an argument of `max()`/`min()` beside another expression
  (`max(1e-300, max|C|)`): a div-by-zero guard, counted as neither.

**Tolerance cut `|literal| ≤ 1e-2`,** which is the single judgement in the tool and is stated because of
it. It keeps real tolerances (1e-30, 1e-12, 5e-4) and excludes physics **bars** — `recovery >= 0.80`,
`floor/gap <= 0.10`, `residual/gap <= 0.20` — which are absolute *by specification* and would otherwise
flag every criterion function spuriously.

**Live positive control.** The sweep requires `p4_validate_active_lateral_fps.mat_gates` to be flagged
before it prints. Because that instance is unrepaired, this tool has a *real* control rather than only
synthetic ones — and when the fix lands, the control will fail loudly and force the table to be
regenerated rather than silently passing. `--min-files 200` fails closed on a sweep that examined nothing,
the mistake the sibling auditor shipped on its first run.

**Complementary, not overlapping.** `audit_gates_that_cannot_fail.py` finds absolute tolerances that are
scale-blind *on their own* (BEN-044's class, no neighbour needed). This tool finds *inconsistency between
neighbours* (BEN-070/071's class), which catches cases where every individual check looks defensible.
`p4_lib.py` pre-repair was found by both; `mat_gates` is found by both. The 3d-unfolding and uq_fps
functions are found only here, and both are benign — which is a fair statement of this tool's
signal-to-noise: 1 of 3.

## 5. Reproducing

    python3 docs/orchestration/audit_validator_tolerance_units.py            # detail
    python3 docs/orchestration/audit_validator_tolerance_units.py --markdown # the table above

Guarded by `nd-unfolding/tests/test_validator_units_auditor.py`, which requires the live control to be
found and the classifier to get all four categories right on constructed cases.
