# RECORD — OI-12 retired as fixed: `mat_gates`'s diagonal bound is relative (2026-10-29)

**By** the close-items session, as backlog candidate 2, on the director's order. Fixed at `c3aef8d5a`, on
`origin/main` `c9ee6fe2a`.

## OI-12 — retired, as fixed

**The row asked for** an absolute covariance-diagonal tolerance replaced with a relative check, plus a mutation test at
the real scale (`VALIDATOR-TOLERANCE-UNITS-20260808.md` §2).

**The change** (`nd-unfolding/p4_validate_active_lateral_fps.py`, `mat_gates`): `d >= -1e-30` now reads
`d >= -1e-12 * abs(ev[-1])`, in line 68's units. `diag_finite_nonneg` is gated in `main()` (`:129-131`), so this is a
gate, not only a recorded field.

**The severity stays LATENT**, as Joseph corrected it on 2026-08-08. For symmetric input min(diag) ≥ min(eigenvalue), so a
negative diagonal is already a negative eigenvalue, and the relative PSD check rejects it first. With the same threshold
the repaired bound is still subsumed. The fix is consistency, not the closing of a hole.

**The adopted FPS lateral is unaffected.** Its receipt (`active_universe_5d/fps/covariance/p4_summary_active_lateral_fps.json`)
records `min_over_max_eig = -3.87e-16`. Its smallest diagonal entry is therefore at least −3.87 × 10⁻¹⁶ λ_max, about 2,600×
inside the new bound, so its `diag_finite_nonneg: true` cannot change. Nothing is re-run.

**The mutation test** (`nd-unfolding/tests/test_mat_gates_relative_diagonal.py`, 10 tests) builds a 266-cell covariance
at the adopted receipt's own `sqrt_trace`:
- a −1 × 10⁻³¹ diagonal passes the old bound and fails the new one, and the PSD check also rejects it;
- the bound passes −1 × 10⁻¹³ λ_max and fails −2 × 10⁻¹² λ_max;
- the same matrices in O(1) units get the same verdicts.

Reverting the one line fails 3 of the 10 tests.

## The auditor's control, replaced

`docs/orchestration/audit_validator_tolerance_units.py` used the unrepaired `mat_gates` as its live positive control. It
refused to print once the repair landed, exiting 3 as its design intended. The control is now
`nd-unfolding/tests/fixtures/units_auditor_control/mat_gates_pre_oi12.py`: the pre-repair function, frozen verbatim
from `c9ee6fe2a` and matched by full path. The sweep must discover the fixture by its own walk.

`nd-unfolding/tests/test_validator_units_auditor.py` adds three checks:
- a tree without the fixture is refused (exit 3), and one with it passes;
- the live `mat_gates` is no longer flagged.

That suite also had a test that failed on `origin/main` before this change. `test_sweep_refuses_a_root_with_no_code`
used `docs/orchestration` as a root with no code, but that directory now holds 685 `.py` files, over the 200-file floor.
It now uses an empty directory, and the suite passes 10 of 10.

## Statements this makes historical

- **`VALIDATOR-TOLERANCE-UNITS-20260808.md`** (ARCHIVAL, not edited) describes `mat_gates` as unrepaired and as the live
  control (§1, §2, §4, §5). Both statements are true as of its date. Its 3-row table is a 2026-08-08 snapshot; the sweep
  prints 37 functions today.
- **`docs/known-issues/ISSUE-46-…`** says the `-1e-30` literal is unchanged. It gains a dated line pointing here.

## Dependency check

Search: `git grep -n -P "OI-12(?![0-9])"` over `KNOWN_ISSUES.md`, `docs/known-issues/`, the DECISION, RULING,
AUTHORIZATION and OPERATIVE records, `docs/analysis-note/` and `measurement-paper/` @ `c3aef8d5a`.

Result: 0 hits. Across the whole tree, the only hits are the register (`OPEN_ITEMS.md`, `work-items.tsv`), its
derived views, and this fix's own files.

No file pins `p4_validate_active_lateral_fps.py` by hash. Search: its git blob `d470c007` and its sha256 `95a86d61` over
the tree @ `c9ee6fe2a`, with 0 hits.
