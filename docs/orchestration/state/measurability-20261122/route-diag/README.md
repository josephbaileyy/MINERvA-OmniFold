# MSR C-ROUTE blind diagnostic: the rules, fixed before it runs (2026-11-23, tier3-design)

The MSR rerun (`run-local-2/`, PR #1262) STOPped at C-ROUTE with `max_excess` 0.7114, after every other control passed.
The director ruled (2026-11-23, option (a)): first a blind diagnostic, and no bar change before it is known whether the
cause is conditioning or a bug. This README is committed **before** the diagnostic runs.

## The diagnostic

`nd-unfolding/msr/msr_route_diag.py` imports the merged msr_project.py unchanged: it asserts sha256 `ffb88e7b…`, as
merged at 88994c9a. It recomputes every C-ROUTE comparison on the committed products (`run-b/cluster/build`):
- S_poor and Z_well per bias vector;
- r_poor and r_well per oracle arm.

Each is compared against the eigen route. **The output holds only**, for each (statistic, vector id, build):
- `rel_diff` = |a − b| / max(|a|, |b|, 1e-300);
- `passes_current_bar` (a boolean; the current bar is |b − a| ≤ 1e-10 + 1e-8·|a|);
- `kappa2`, κ₂ of the matrix the independent route solves: Wᵀ C W for Z_well, and the well-constrained block W, which
  the QR projector factors, for S_poor and r;
- `ten_kappa_eps` = 10·κ₂·ε, with ε the float64 epsilon.

It never writes a, b, |a|, a label, a band, or anything a reading is computed from. The writer (`Record`) refuses any
other field, and `test_msr_route_diag.py` fails if one is written. The readings msr_project computes in memory along the
way are discarded unwritten.

Vector ids number the comparisons in the order `msr_project.readings()` makes them: `5d#nnn` and `2d#nnn` for the bias
vectors in that function's order (M1, then the secondary and printed sets), and `arm#1` (MO) and `arm#2` (OP) for M2.

## What follows, decided now, before anyone sees the output (the director's ruling)

Here a *failing comparison* is a row with `passes_current_bar = false`.

1. **Conditioning:** every failing comparison has `rel_diff ≤ ten_kappa_eps`.
   - **Amendment D** replaces C-ROUTE's bar with max(1e-10 + 1e-8·|a|, 10·κ₂·ε relative), on the A5 precedent.
   - It is recorded as made after a STOP and before any reading was seen.
   - The run is then repeated once at the merged commit.
2. **Route bug:** any failing comparison has `rel_diff ≥ 10 · ten_kappa_eps`.
   - It is treated as a bug in a route: an executability fix with tests, then the run repeated once.
3. **In between:** any other outcome goes back to the director. That means some failing comparison with
   `ten_kappa_eps < rel_diff < 10 · ten_kappa_eps`, and none at or above 10×.

The diagnostic's output is committed as a diagnostic record (`route-diag/diag.json`, with its run-env) and then sent to
the director.
<!-- absence-ok: a pre-declared rule for an unrun diagnostic; "never writes" states the script's own output contract -->
