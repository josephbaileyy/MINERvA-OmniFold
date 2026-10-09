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

## Ranked obstacles and dispositions

Ranked by their effect on estimator tracing, independent-validation design and supported
reproduction, and by the strength of the evidence. There are five, the maximum.

| # | Obstacle | Evidence | Disposition |
|---|---|---|---|
| O1 | The 2D reference sent readers to superseded uncertainty producers. Its rollup bullet named `sbatch_final_rollup_full.sh`, whose universe step reads the pre-fluxfix sweep. Its Fig. 6/7 path named that route's output directory. Its "Driver" was the interactive script. It never mentioned `VL170`, the replica record or `uq/rollup_vl170_adoption.sh` (0 hits). | rows N06, N07, N11; `rollup_vl170_adoption.sh:6-7`; `nav-before.txt` T1/T2 | **IMPLEMENTED** (I1 `abc1e6f7`, I3 `bd738973`). The reference has a producer table that says what each row reads and writes, that every row is a record of how a pinned product was made rather than a prospective command, and how each row guards against overwriting, and the old route is marked superseded. README routes there from "Where to start" and Setup step 6. |
| O2 | The reference's bootstrap item 4 told each replica to pass `--seed N`. Every band producer passes a fixed `--seed 1`, and the scaleup header records that varying both double-counted ML stochasticity. | row D05; six launchers measured; `scaleup.sh:18-19` | **IMPLEMENTED** (I2 `00803510`). **A's factual check: PENDING** (see "For A"). |
| O3 | The frozen central value's backend is labeled inconsistently. The status headline says "MEFHC 5-iter lgbm", but the launcher that writes the frozen path passes no `--estimator` (driver default `exact`). `final_rollup_full.sh` (c) comments "using the exact-GBT production CV here". | row D06 | **DEFERRED to A** (estimator identity) and to E (status routing). D wrote no backend label, so the producer table names the launcher and not a backend. Least costly resolution: read the backend from the product's own metadata or its run log. That is A's read-only check. |
| O4 | The 205-bin reported mask is computed four ways from four operands (`analyze_uq.py`: ensemble mean > 0; `analyze_universes.py`: CV > 0; `compare_to_paper_fullcov.py`: paper diagonal > 0; Fig. 6/7: central > 0). The comparison aligns the matrices by ordinal position and checks only the count. Today the cells coincide, so no number is wrong. A future ensemble with one zero-mean reported bin and one extra nonzero cell would misalign every element silently. The 3D analogue `build_bootstrap_cov_3d.py` already takes its mask from the CV, the same operand as its universe rollup. | row D01; `compare_to_paper_fullcov.py:148-159`; `build_bootstrap_cov_3d.py:11-13,84` | **DEFERRED patch design** (below). Two of the files are A's conditional paths and the third is a publication figure producer, so D edits none of them. |
| O5 | `3d-unfolding/genie/gen5d_*` and `run_gen5d_supplement.sh` are the s5p 5D predictor family, in a 3D directory beside 3D generator code. | row N14; `reproduction/s5p/scope.py` `PRODUCER_FILES` | **Routing IMPLEMENTED** in README (I3). **Move DEFERRED**, with a full design in `docs/POST_PUBLICATION_REORG_PLAN.md`, "Uncertainty preparation, lane D". The recommendation is not to move. |

Implemented improvements: three (I1, I2, I3), all documentation. **No source file was edited**,
so D's two-file structural allowance is unused and no ownership transfer happened.

### O4 deferred patch design (for A, or the publication owner for `compare_to_paper_fullcov.py`)

- **Change.** Make each covariance carry its reported-cell identity, not just its size.
  - `analyze_uq.py` and `analyze_universes.py` already write `hCov2D_reported`. Next to it, each
    writes a `TH2D`/`TH1D` mask of the 224-cell grid, or the flat indices.
  - `compare_to_paper_fullcov.py:load_omnifold_cov` refuses when the stored indices differ from the
    paper mask's `np.where(reported_mask)[0]`. If an input has no stored mask, it falls back to the
    current count check and prints a warning.
  - Alternatively, `analyze_uq.py` takes a `--cv` and builds its mask from the CV, as the 3D builder does.
- **Behavior contract.** On today's inputs the four masks coincide, so every output must be identical
  bit for bit: `hCov2D_reported`, `hCov_combined`, the χ² logs and the Fig. 6/7 summary. The only
  addition is the stored mask object.
- **Verification.**
  - Run the VL172 rollup's controls from `rollup_vl170_adoption.sh` on frozen inputs (Perlmutter,
    login-node-safe: about minutes of CPU, no training). Require numerically identical logs and
    covariance arrays, with a declared tolerance of 0 (same code path).
  - Add a synthetic negative control: shift one reported cell, which must be refused.
  - Run `test_bootstrap_completeness_ki84.py`.
  - Record the producer digest in `fig_arrays.npz.manifest.json`, and note that it changes.
- **Why deferred.**
  - The files belong to A (two) or are a publication input (one).
  - The required equivalence run needs the frozen ROOT inputs on Perlmutter, which this lane does not
    run.
  - The hazard is latent, not live.

## Before and after: the four navigation tasks

Logs: [`nav-before.txt`](nav-before.txt) (base docs) and [`nav-after.txt`](nav-after.txt) (head docs).
A reader starts from `README.md`.

| Task | Before (`f8e2bf85`) | After |
|---|---|---|
| T1 Find the adopted statistical producer | The README has no 2D uncertainty route. The reference's only "Driver" is `uq/run_bootstrap_interactive.sh`, which did not make the quoted replicas, and the reference never mentions `VL170`, KI-84 or the replica record (0 hits). Reachable only through `AGENTS.md` → `KNOWN_ISSUES.md` 84 → a receipt directory listing. | README "Where to start" row (line 30) → reference table row "Statistical replicas (`VL170`)" → `state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh` (`--seed 1`, `--bootstrap-seed N`) → `analyze_uq.py` in the rollup. Two hops, both named. |
| T2 Find the active combined rollup | The reference names `sbatch_final_rollup_full.sh` (superseded). Only the ledger and the plan mention `rollup_vl170_adoption.sh`. | Reference table "Combined rollup (`VL172`)" and the universe-workflow bullet both name `uq/rollup_vl170_adoption.sh`, with its inputs, outputs and digests file. README Setup step 6 points there. |
| T3 Find the supported import constraints | Reachable from README "Before changing the 2D driver" (one hop). The reference's driver contract does not mention the constraint (0 hits). | Unchanged in README. The reference's driver contract now opens with the constraint and routes to the ruling (`AUTHORIZATION-20260903-oi136-failopen-repair.md:41`, verified), the ratchet test and `mnv_guarded_run.py`. |
| T4 Recover a historical evidence path through the correct tag | Works through README → reorg plan or `CATALOG.md`, but README names only the 2026-08-20 tag. The A3 path tried at that tag fails (`rc=128`). | README names all three removal-boundary tags and how to pick one. `git show evidence/simplification-2026-10-07-fc97eaf9:nd-unfolding/pet/final_design/results/dev1/dev1-CS1-F0.posthoc.json` gives sha256 `d6d09e6f…`, equal to the external epoch's `a3-blobs.tsv`. The reference's archive citation `evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:441` resolves (Phase-16 heading). |

## Checks

All checks ran locally (macOS, Python 3.12.2), with `TMPDIR=/private/tmp/minerva-uncprep-d-20261008/tmp`
and a four-thread cap.

| Check | Result |
|---|---|
| pre-commit hook (shared `.githooks`) on each of D's commits | 13 checks passed, every commit |
| `python3 docs/orchestration/verify_hash_bindings.py` at D's head | rc 0, ALL BINDINGS INTACT ([`verify_hash_bindings.txt`](verify_hash_bindings.txt)) |
| `python3 -m pytest -q nd-unfolding/tests/test_hash_bindings.py` (inspected first: verifier subprocesses and synthetic temp repos only) | 33 passed, 0 skipped ([`test_hash_bindings.txt`](test_hash_bindings.txt)). It pins `2D_OMNIFOLD_REFERENCE.md` and `analyze_universes.py` at revision `901f2c64`, not at current bytes |
| Paths in D's added lines resolve | 68 resolved. The 26 unresolved occurrences are bare basenames of files named in full nearby, untracked cluster product directories (by design), two formulas, and the proposed destination `nd-unfolding/gen5d` ([`pathcheck.txt`](pathcheck.txt)) |
| `generate_manifest.py --check` | not run: already OUT OF DATE at the pin (E-C1). No lane regenerates it, and D's three paths are not in `MANIFEST.tsv` rows that D may touch |
| Code equivalence | not applicable: no source file changed |
| Document builds | not applicable: no `docs/analysis-note/` input changed |

The `final_rollup_full.sh`, rollup and driver statements in the reference were each checked against
the script text at the base (line citations in `dependencies.tsv`). No product was opened. The
products are on Perlmutter, and D read none of them.

## For A — factual-check requests (D remains the writer)

Please answer in `P/a/verification.md`. D's wording is on this branch.
1. **I2, bootstrap item 4** (`2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, "Bootstrap-replica workflow").
   Confirm that the `VL162` and `VL170` replicas used a fixed estimator seed `--seed 1` with varying
   `--bootstrap-seed N`. Confirm, or correct, the statement that the replicas' estimator seed differs
   from the matched universe CV's `--seed 42`, and that the central launcher passes neither flag.
2. **I1, the producer table** ("Which script produced the quoted 2D uncertainty"). Confirm that
   `uq/rollup_vl170_adoption.sh` is the actual active `VL172` rollup route, and that its ML covariance
   input came from step (a) of `final_rollup_full.sh`.
3. **O3.** Which backend produced `2d_crossSection_omnifold_MEFHC_5iter.root` (`142a45b0…`)? D will
   not write a label until A records one.

## For E

- Integrate commits `d126a115` (INVENTORY), `abc1e6f7`, `00803510`, `bd738973`, `3a95fc71` and this
  record's FREEZE commit. All are documentation. Nothing touches `MANIFEST*`, `CATALOG.md` or a hash-bound file.
- O3 needs a status-routing decision, after A's answer, about the 2D status headline's backend label.
- If A's check (above) is still pending at integration, I2's wording stands only on the launcher
  evidence D measured. E's reviewer should re-read the six launchers named in item 4.
- `README.md`'s shared-code row and the reference's producer table contain no numbers. They will need
  a refresh only if the rollup route changes.
