# MSR C-ROUTE blind diagnostic 2: the rules, fixed before it runs (2026-11-23, tier3-design)

Diagnostic 1 (`../route-diag/`, PR #1263) found 21 failing C-ROUTE rows. All are `Z_well`, at the 2D vector ids
`2d#013–015` and `2d#030–047`. Its rule selected branch 2 (route bug), but κ₂(Wᵀ C W) = 539 there, so the solve cannot be
the cause. The director ruled (2026-11-23, option (i)): a second blind diagnostic against a high-precision reference,
under the same output rules. If C's formation is the cause, a fix to one route would hide an error in the other. This
README is committed **before** the diagnostic runs.

## The diagnostic

`nd-unfolding/msr/msr_route_diag2.py` imports msr_project.py unchanged: it asserts sha256 `ffb88e7b…`, as merged at
88994c9a. It reruns the controls and `readings()` on the committed products (`run-b/cluster/build`) and discards the
readings unwritten. It identifies vectors by the same call order as diagnostic 1, and keeps only these rows:
- **the 21 failing 2D Z_well rows**: `2d#013`, `2d#014`, `2d#015`, `2d#030` … `2d#047`;
- **3 passing 5D Z_well rows as controls**: `5d#001`, `5d#002`, `5d#003`.

The test checks this list against diagnostic 1's `diag.json`. The run refuses (rc 4) if any target row is not reached,
and refuses (rc 3) if any first-block control fails.

**The output holds only** these fields, per row:
- `stat` (always `Z_well`), `vector_id`, `build` (`full/numpy`, as in diagnostic 1);
- `kappa2_C`: κ₂ of C = J F⁺ Jᵀ, as the eigen route forms it in float64;
- `kappa2_CQ`: κ₂ of C_Q = B_Qᵀ C B_Q, the matrix the eigen route decomposes. It is computed as κ₂(wᵀ C w) with
  w = B_Q c and c orthogonal, which has the same spectrum;
- `rel_diff_drivers`: Z_well with numpy `eigh` vs scipy `evr`, as N-PREC compares it;
- `rel_diff_eigen_vs_ref`: the eigen route (`msr_project.z_well` on the full numpy decomposition) vs the reference;
- `rel_diff_indep_vs_ref`: the independent route (`route_independent`, the solve aᵀ(Wᵀ C W)⁻¹a) vs the same reference;
- `ref_partition_equal`: whether the reference's (n_well, dim U∞) equals the float64 decomposition's. This field is not
  in the director's list. It is added because a Z difference means nothing if the two sides partition differently;
  its use in the rule is stated below.

Each rel_diff is |a − b| / max(|a|, |b|, 1e-300). The output never writes a, b, a reference value, a label, a band, or
anything a reading is computed from. The writer (`Record`) refuses any other field, and `test_msr_route_diag2.py` fails
if one is written, or if any S_poor or Z_well value of the fixture's readings appears in the output.

**The reference** works at 50 significant digits in mpmath 1.3.0, from the same float64 inputs: R, t0, b and J, exactly
as `problem_2d` builds them. It follows the declared formulas (§3.3), with every step in mpmath:
- F = Rᵀ diag(1/μ) R over the reco cells with μ = R t0 + b > 0 (`did.fisher`'s definition);
- `eigsy` of F, the range cut λ > 1e-12·λ_max, and F⁺ on that range;
- C = J F⁺ Jᵀ, formed in mpmath;
- U∞ from the generalized eigenproblem M u = ρ² K u, with M = J V_N V_Nᵀ Jᵀ and K = J Jᵀ (via the Cholesky factor of K),
  and ρ > 1e-6;
- B_Q, the QR of the remaining directions; C_Q = B_Qᵀ C B_Q and its eigenpairs (s², c), w = B_Q c;
- the well block s ≤ 0.10, and Z = √Σ_well (w·β)²/s².

The cut values are read from msr_project's constants. The reference is computed **for 2D only**, as the director scoped
it. On the three 5D rows, both reference fields are NaN and `ref_partition_equal` is null; those rows carry κ₂ and the
driver difference only.

The tests check the reference against float64 `decompose` on small well-conditioned problems, to ≤ 1e-10 relative, with
and without a null direction, and check that the partitions agree. They also check that the Fisher matrix matches
`did.fisher`. A smoke run of the real 50-digit path on the test fixture's 224-cell 2D problem passed and took about
8 minutes.

## What follows, decided now, before anyone sees the output (the director's ruling)

Applied in code by `msr_route_diag2.branch()` over the 21 2D rows (tested in `test_msr_route_diag2.Rule`). A NaN or
infinite difference counts as a miss; "within" means rel_diff ≤ 1e-8.

0. **Precondition (my addition, for the director's confirmation):** if any 2D row has `ref_partition_equal` false, or
   the 21 rows are not exactly present, the outcome is **anything else**, and it goes to the director.
1. **The independent route is the defect:** the eigen route is within 1e-8 of the reference on all 21 rows, and the
   independent route is not (it misses on at least one).
   - Fix the independent route's formation as an executability fix, with tests against the mpmath reference.
   - Rerun once.
2. **C's float64 formation is the defect:** on at least one row, both routes miss the reference by more than 1e-8.
   - Fix the computation for both routes, e.g. by working in F's eigenbasis restricted to Q, without forming C. Add
     tests against the reference.
   - Check that 5D's rows stay within 1e-8 of a reference under the new formation, and add one 5D reference row if
     that is feasible.
   - Rerun once.
3. **Anything else** comes back to the director.

The diagnostic's output is committed as a diagnostic record (`route-diag2/diag.json`, with its run-env, stdout and
stderr), and then sent to the director. Any fix that follows means a new sha of msr_project.py, and that sha goes to
the director before anything runs.
<!-- absence-ok: a pre-declared rule for an unrun diagnostic; "never writes" states the script's own output contract -->
