# Lane D — repository comprehensibility: inventory and dispositions

Base `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c`, branch `prep/uncertainty-d-navigation-20261008`,
worktree `MINERvA-OmniFold-uncprep-d-20261008`. Plan: `docs/orchestration/PLAN-20261008-uncertainty-investigation-preparation.md`
(blob `fbbc0d65`). The measured graph is in [`dependencies.tsv`](dependencies.tsv). This record is
preparation evidence. It grants no compute and changes no gate, adoption or publication scope.

## Ownership (inventory commit)

**D writes only these paths:**

| Path | Status at inventory |
|---|---|
| `README.md` | D; planned edit (routing) |
| `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` | D; planned edit (routing and the bootstrap seed instruction, after A's factual check) |
| `docs/POST_PUBLICATION_REORG_PLAN.md` | D; planned edit (deferred-move designs) |
| `P/d/dependencies.tsv`, `P/d/disposition.md` | D |
| one existing workstream README | **none claimed.** If one is claimed later, it is named in this table in a commit before the edit |

**Source files.** D claims **none** of A's five conditional 2D paths and proposes **no transfer** at
this inventory:
`2d-unfolding/unfold_2d_omnifold_unbinned.py`, `2d-unfolding/uq/analyze_uq.py`,
`2d-unfolding/uq/analyze_universes.py`, `2d-unfolding/uq/rollup_vl170_adoption.sh`,
`2d-unfolding/tests/test_bootstrap_completeness_ki84.py`. All five stay released to A. D's
structural-code allowance (at most two non-frozen files) is unused. Any later use needs an exact
transfer recorded both here and in `P/a/verification.md`.

**Caller constraints for A** (measured, see `dependencies.tsv`):
- The driver has 47 importers (`import unfold_2d_omnifold_unbinned as u2d`). The most-used names are
  `PT_EDGES`, `PZ_EDGES`, `refine_stay_positive`, `MAX_MUON_THETA_RAD`, `get_pot_scales`,
  `in_truth_phase_space`, `load_flux_bins` and `TRACKER_FIDUCIAL_N_NUCLEONS`. A rename or a signature
  change to any of them reaches the 3D and N-D drivers, PET and one note figure script.
- The driver's rooted insert must stay inside `main()`, and `unbinned_unfolding/python/omnifold.py`
  must keep its digest (`test_oi136_rooted_insert_ratchet.py`). Its two current-bytes pins
  (`8ebe0277…`, in the negweight receipt and the Gate-2 launcher) are already broken by KI-84 and
  listed `KNOWN_PREEXISTING`; a further edit does not change that status and does not re-pin anything.
- `analyze_universes.py` is pinned only at revision `901f2c64` (`test_hash_bindings.py:701`), so an
  edit to its current bytes does not break that test.
- `compare_to_paper_fullcov.py` is not one of A's paths. It is a publication figure producer (its
  digest is recorded in `publication/release/figs/_data/fig_arrays.npz.manifest.json`).
- The reported-bin mask is computed four ways from four operands (row D01). A change to how
  `analyze_uq.py` or `analyze_universes.py` chooses reported bins reaches
  `compare_to_paper_fullcov.py`'s ordinal alignment, which checks only the count.

**Not D's:** A–C and E surfaces in the plan's writer table; `docs/analysis-note/`,
`publication/release/`, `docs/publication/corrections-20261008/`; `MANIFEST.tsv`,
`MANIFEST-overrides.tsv`, `CATALOG.md`; `AGENTS.md`; frozen receipts; generated views.

**Path recheck before the first edit** (2026-10-09T06:14Z): no other worktree's uncommitted edits or
live branch deltas touch D's three existing paths. E's dispatch snapshot found none, and
`git fetch origin` showed only `prep/uncertainty-e-20261008` among the lane branches. Older remote
branches differ from the base on `README.md` only because `main` moved past them; none is a live
edit.

## Supported entry points (2D, immediate)

See the `entry` rows E01–E06. Each is either a frozen reproduction (its outputs are pinned
products) or a prospective run, never both:

| Task | Entry point | Kind |
|---|---|---|
| Event loop and merge | `sbatch_evloop_array.sh` → `sbatch_hadd_MEFHC.sh` | prospective |
| Central value | `sbatch_unfold_2d_MEFHC.sh` → `unfold_2d_omnifold_unbinned.py` | frozen reproduction; the product's backend label is open (row D06, A) |
| Statistical replicas (VL170) | `state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh` | frozen reproduction (record) |
| Systematic universes | `sbatch_unfold_2d_MEFHC_5iter_universes_full{,_CV}.sh` | frozen reproduction |
| Active combined rollup (VL172) | `uq/rollup_vl170_adoption.sh` | frozen reproduction |
| Paper comparison | `compare_to_paper_fullcov.py` | deterministic re-evaluation |

## Preliminary obstacle list (to be ranked and disposed in the final commit)

1. The reference routes the combined rollup to `sbatch_final_rollup_full.sh`, whose universe step
   predates the quoted products. The active route is `uq/rollup_vl170_adoption.sh` (rows N06, N07).
2. The reference's bootstrap item 4 (`--seed N`) contradicts every producer (`--seed 1`) (row D05).
3. The frozen central value's backend is labeled inconsistently (row D06). This is A's question; D
   writes no label until A records one.
4. The reported-bin mask is defined four ways and aligned by ordinal position with only a count check
   (row D01).
5. `3d-unfolding/genie/gen5d_*` is the s5p 5D predictor family under a 3D directory (row N14).
